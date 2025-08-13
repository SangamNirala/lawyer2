from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import time
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
import aiohttp
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="Legal Research Engine API",
    description="Comprehensive legal research platform powered by CourtListener",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for ML models and indices
sentence_model = None
faiss_index = None
case_embeddings = {}
precedent_matching_stats = {
    "total_cases": 0,
    "indexed_cases": 0,
    "last_update": None,
    "average_search_time": 0.0,
    "total_searches": 0
}

# Initialize ML models and FAISS index
async def initialize_ml_models():
    """Initialize sentence transformer and FAISS index"""
    global sentence_model, faiss_index
    
    try:
        logger.info("Initializing sentence transformer model...")
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index (768 dimensions for all-MiniLM-L6-v2)
        faiss_index = faiss.IndexFlatIP(384)  # Inner product for cosine similarity
        
        # Load existing embeddings if available
        await load_existing_embeddings()
        
        logger.info("ML models initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing ML models: {e}")

async def load_existing_embeddings():
    """Load existing case embeddings from database"""
    global faiss_index, case_embeddings, precedent_matching_stats
    
    try:
        # Load cases from database
        cases_cursor = db.legal_cases.find(
            {"processing_status": "enriched"},
            {"_id": 1, "case_name": 1, "full_text": 1, "embeddings": 1}
        )
        
        cases = await cases_cursor.to_list(length=1000)  # Load first 1000 cases
        
        embeddings_list = []
        case_ids = []
        
        for case in cases:
            case_id = str(case["_id"])
            case_text = case.get("full_text", case.get("case_name", ""))
            
            # Generate embedding if not exists
            if "embeddings" not in case or case["embeddings"] is None:
                if case_text:
                    embedding = sentence_model.encode([case_text])[0]
                    # Store embedding back to database
                    await db.legal_cases.update_one(
                        {"_id": case["_id"]},
                        {"$set": {"embeddings": embedding.tolist()}}
                    )
                else:
                    continue
            else:
                embedding = np.array(case["embeddings"])
            
            embeddings_list.append(embedding)
            case_ids.append(case_id)
            case_embeddings[case_id] = {
                "case_name": case["case_name"],
                "embedding": embedding
            }
        
        if embeddings_list:
            # Add to FAISS index
            embeddings_matrix = np.vstack(embeddings_list).astype('float32')
            faiss.normalize_L2(embeddings_matrix)  # Normalize for cosine similarity
            faiss_index.add(embeddings_matrix)
            
            precedent_matching_stats["total_cases"] = len(cases)
            precedent_matching_stats["indexed_cases"] = len(embeddings_list)
            precedent_matching_stats["last_update"] = datetime.utcnow().isoformat()
            
            logger.info(f"Loaded {len(embeddings_list)} case embeddings into FAISS index")
        
    except Exception as e:
        logger.error(f"Error loading existing embeddings: {e}")

# CourtListener API client
class CourtListenerClient:
    def __init__(self):
        self.api_key = os.environ.get('COURTLISTENER_API_KEY', 'demo_key')
        self.base_url = "https://www.courtlistener.com/api/rest/v3"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': f'Token {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'LegalResearchEngine/1.0'
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_opinions(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for legal opinions"""
        params = {
            'q': query,
            'format': 'json',
            'limit': limit
        }
        
        try:
            async with self.session.get(f"{self.base_url}/search/", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"results": [], "count": 0}
        except Exception as e:
            logger.error(f"Error searching opinions: {e}")
            return {"results": [], "count": 0}

# Background task for CourtListener data enrichment
async def background_courtlistener_sync():
    """Background task to sync data from CourtListener"""
    logger.info("Starting background CourtListener sync")
    
    try:
        async with CourtListenerClient() as client:
            # Search for recent cases (last 30 days)
            recent_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Sample queries for different legal areas
            queries = [
                "constitutional law",
                "contract law", 
                "tort law",
                "civil rights",
                "criminal law"
            ]
            
            total_processed = 0
            
            for query in queries:
                try:
                    results = await client.search_opinions(query, limit=50)
                    opinions = results.get('results', [])
                    
                    for opinion in opinions:
                        await process_and_store_case(opinion)
                        total_processed += 1
                        
                        # Rate limiting
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error processing query '{query}': {e}")
                    continue
            
            logger.info(f"Background sync completed. Processed {total_processed} cases")
            
            # Update embeddings after sync
            await load_existing_embeddings()
            
    except Exception as e:
        logger.error(f"Error in background sync: {e}")

async def process_and_store_case(opinion_data: Dict[str, Any]):
    """Process and store a legal case from CourtListener"""
    try:
        cluster_data = opinion_data.get('cluster', {})
        
        # Create case document
        case_doc = {
            "courtlistener_id": opinion_data.get('id'),
            "cluster_id": cluster_data.get('id'),
            "case_name": cluster_data.get('case_name', ''),
            "court": {
                "id": cluster_data.get('court_id', ''),
                "name": cluster_data.get('court', {}).get('full_name', ''),
                "jurisdiction": cluster_data.get('court', {}).get('jurisdiction', '')
            },
            "date_filed": cluster_data.get('date_filed'),
            "date_decided": cluster_data.get('date_decided'),
            "full_text": opinion_data.get('plain_text', '')[:10000],  # Limit text length
            "summary": cluster_data.get('summary', ''),
            "citations": [],
            "legal_areas": [],
            "key_terms": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "processing_status": "pending"
        }
        
        # Check if case already exists
        existing_case = await db.legal_cases.find_one({
            "courtlistener_id": case_doc["courtlistener_id"]
        })
        
        if not existing_case:
            # Insert new case
            result = await db.legal_cases.insert_one(case_doc)
            logger.debug(f"Inserted new case: {case_doc['case_name']}")
            
            # Generate embedding and enrich data
            await enrich_case_data(str(result.inserted_id), case_doc)
    
    except Exception as e:
        logger.error(f"Error processing case: {e}")

async def enrich_case_data(case_id: str, case_data: Dict[str, Any]):
    """Enrich case data with embeddings and analysis"""
    try:
        if not sentence_model:
            return
        
        # Generate text for embedding
        text_for_embedding = f"{case_data['case_name']} {case_data.get('summary', '')} {case_data.get('full_text', '')}"
        
        if text_for_embedding.strip():
            # Generate embedding
            embedding = sentence_model.encode([text_for_embedding])[0]
            
            # Extract key terms (simplified)
            key_terms = extract_key_terms(text_for_embedding)
            
            # Classify legal areas (simplified)
            legal_areas = classify_legal_areas(text_for_embedding)
            
            # Update case in database
            await db.legal_cases.update_one(
                {"_id": case_id},
                {
                    "$set": {
                        "embeddings": embedding.tolist(),
                        "key_terms": key_terms,
                        "legal_areas": legal_areas,
                        "processing_status": "enriched",
                        "last_processed": datetime.utcnow()
                    }
                }
            )
            
            logger.debug(f"Enriched case: {case_id}")
    
    except Exception as e:
        logger.error(f"Error enriching case {case_id}: {e}")

def extract_key_terms(text: str) -> List[str]:
    """Extract key legal terms from text"""
    import re
    
    legal_patterns = [
        r'\b(?:constitutional|constitution|amendment|due process|equal protection)\b',
        r'\b(?:contract|agreement|breach|consideration|damages)\b',
        r'\b(?:negligence|liability|tort|injury)\b',
        r'\b(?:criminal|defendant|prosecution|sentence)\b'
    ]
    
    terms = set()
    for pattern in legal_patterns:
        matches = re.findall(pattern, text.lower())
        terms.update(matches)
    
    return list(terms)[:10]

def classify_legal_areas(text: str) -> List[str]:
    """Classify text into legal areas"""
    text_lower = text.lower()
    areas = []
    
    area_keywords = {
        "constitutional_law": ["constitutional", "amendment", "due process"],
        "contract_law": ["contract", "agreement", "breach"],
        "tort_law": ["negligence", "liability", "injury"],
        "criminal_law": ["criminal", "defendant", "prosecution"]
    }
    
    for area, keywords in area_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            areas.append(area)
    
    return areas

# Precedent search function
async def search_precedents(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for legal precedents using vector similarity"""
    global sentence_model, faiss_index, case_embeddings, precedent_matching_stats
    
    start_time = time.time()
    
    try:
        if not sentence_model or not faiss_index or faiss_index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = sentence_model.encode([query])
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search similar cases
        scores, indices = faiss_index.search(query_embedding, min(limit, faiss_index.ntotal))
        
        results = []
        case_ids = list(case_embeddings.keys())
        
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(case_ids):
                case_id = case_ids[idx]
                case_info = case_embeddings[case_id]
                
                # Get full case data from database
                case_data = await db.legal_cases.find_one({"_id": case_id})
                
                if case_data:
                    results.append({
                        "case_id": case_id,
                        "case_name": case_info["case_name"],
                        "similarity_score": float(score),
                        "court": case_data.get("court", {}),
                        "date_decided": case_data.get("date_decided"),
                        "summary": case_data.get("summary", "")[:500],
                        "legal_areas": case_data.get("legal_areas", []),
                        "key_terms": case_data.get("key_terms", [])
                    })
        
        # Update stats
        search_time = time.time() - start_time
        precedent_matching_stats["total_searches"] += 1
        current_avg = precedent_matching_stats["average_search_time"]
        total_searches = precedent_matching_stats["total_searches"]
        precedent_matching_stats["average_search_time"] = (
            (current_avg * (total_searches - 1) + search_time) / total_searches
        )
        
        return results
    
    except Exception as e:
        logger.error(f"Error searching precedents: {e}")
        return []

# API Models
class PrecedentSearchRequest(BaseModel):
    query: str = Field(..., description="Legal query for precedent search")
    limit: int = Field(default=10, ge=1, le=50, description="Number of results to return")

class PrecedentSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int
    search_time: float

# API Endpoints

@api_router.get("/legal-research-engine/stats")
async def get_legal_research_stats():
    """Get legal research engine operational status and stats"""
    try:
        # Get database stats
        total_cases = await db.legal_cases.count_documents({})
        enriched_cases = await db.legal_cases.count_documents({"processing_status": "enriched"})
        
        # Update stats
        precedent_matching_stats["total_cases"] = total_cases
        precedent_matching_stats["indexed_cases"] = enriched_cases
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "database_stats": {
                "total_cases": total_cases,
                "enriched_cases": enriched_cases,
                "pending_cases": total_cases - enriched_cases
            },
            "precedent_matching_stats": precedent_matching_stats,
            "ml_models": {
                "sentence_transformer_loaded": sentence_model is not None,
                "faiss_index_size": faiss_index.ntotal if faiss_index else 0
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving stats")

@api_router.post("/legal-research-engine/refresh-courtlistener")
async def refresh_courtlistener_data(background_tasks: BackgroundTasks):
    """Trigger background enrichment from CourtListener"""
    try:
        # Add background task
        background_tasks.add_task(background_courtlistener_sync)
        
        return {
            "status": "started",
            "message": "Background CourtListener sync initiated",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting background sync: {e}")
        raise HTTPException(status_code=500, detail="Error starting background sync")

@api_router.post("/legal-research-engine/search-precedents", response_model=PrecedentSearchResponse)
async def search_legal_precedents(request: PrecedentSearchRequest):
    """Search for legal precedents using AI-powered similarity matching"""
    try:
        start_time = time.time()
        
        results = await search_precedents(request.query, request.limit)
        
        search_time = time.time() - start_time
        
        return PrecedentSearchResponse(
            results=results,
            query=request.query,
            total_results=len(results),
            search_time=search_time
        )
    
    except Exception as e:
        logger.error(f"Error in precedent search: {e}")
        raise HTTPException(status_code=500, detail="Error performing precedent search")

# Legacy endpoints (keeping for compatibility)
@api_router.get("/")
async def root():
    return {"message": "Legal Research Engine API", "version": "1.0.0"}

@api_router.post("/status")
async def create_status_check(client_name: str):
    status_dict = {"client_name": client_name, "timestamp": datetime.utcnow()}
    status_obj = {**status_dict, "id": str(uuid.uuid4())}
    await db.status_checks.insert_one(status_obj)
    return status_obj

@api_router.get("/status")
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Legal Research Engine API")
    
    # Initialize ML models
    await initialize_ml_models()
    
    logger.info("Legal Research Engine API started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()