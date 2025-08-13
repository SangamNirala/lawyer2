"""
Advanced AI-Powered Precedent Matching System - Enhanced Implementation

This module implements comprehensive AI-powered precedent matching capabilities using semantic
similarity, multi-dimensional case analysis, and advanced legal principle extraction as specified
in the Advanced Legal Research & Precedent Analysis Engine requirements.

Key Features:
- 6-dimensional similarity analysis (factual, legal, procedural, jurisdictional, temporal, authority)
- AI-powered legal principle extraction using Gemini AI
- Advanced similarity algorithms with confidence scoring
- Integration with CourtListener data and legal knowledge base
- Real-time precedent validation and authority assessment
- PageRank-style authority calculation for legal precedents
"""

import asyncio
import json
import logging
import numpy as np
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

import google.generativeai as genai
from groq import Groq
import httpx
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Import embeddings with fallbacks
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

import re
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityDimension(Enum):
    """Dimensions for comprehensive case similarity analysis"""
    FACTUAL = "factual"
    LEGAL = "legal" 
    PROCEDURAL = "procedural"
    JURISDICTIONAL = "jurisdictional"
    TEMPORAL = "temporal"
    AUTHORITY = "authority"


class MatchType(Enum):
    """Types of precedent matches with detailed classification"""
    IDENTICAL = "identical"
    HIGHLY_SIMILAR = "highly_similar"
    MODERATELY_SIMILAR = "moderately_similar"
    DISTINGUISHABLE = "distinguishable"
    ANALOGOUS = "analogous"
    CONTRARY = "contrary"


class AuthorityLevel(Enum):
    """Legal authority levels for precedent ranking"""
    SUPREME_COURT = "supreme_court"
    APPELLATE_COURT = "appellate_court"
    TRIAL_COURT = "trial_court"
    ADMINISTRATIVE = "administrative"
    INTERNATIONAL = "international"


@dataclass
class LegalPrinciple:
    """Enhanced legal principle with comprehensive metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    principle_text: str = ""
    legal_domain: str = ""
    authority_level: AuthorityLevel = AuthorityLevel.TRIAL_COURT
    jurisdiction: str = ""
    source_case_id: str = ""
    confidence_score: float = 0.0
    precedential_value: str = "medium"
    supporting_citations: List[str] = field(default_factory=list)
    related_principles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    ai_analysis: str = ""


@dataclass
class SimilarityScore:
    """Multi-dimensional similarity score with AI confidence assessment"""
    factual_similarity: float = 0.0
    legal_similarity: float = 0.0
    procedural_similarity: float = 0.0
    jurisdictional_similarity: float = 0.0
    temporal_similarity: float = 0.0
    authority_similarity: float = 0.0
    overall_similarity: float = 0.0
    confidence_score: float = 0.0
    ai_confidence: float = 0.0
    
    def calculate_overall(self, weights: Dict[str, float] = None) -> float:
        """Calculate weighted overall similarity score with enhanced dimensions"""
        if weights is None:
            # Enhanced 6-dimensional weighting as specified
            weights = {
                'factual': 0.30,      # Semantic embedding similarity 
                'legal': 0.25,        # Legal issue categorization matching
                'jurisdictional': 0.20, # Jurisdictional hierarchy consideration
                'temporal': 0.15,     # Temporal relevance scoring
                'authority': 0.10,    # Authority weight calculation
                'procedural': 0.0     # Included in other dimensions
            }
        
        overall = (
            self.factual_similarity * weights.get('factual', 0.0) +
            self.legal_similarity * weights.get('legal', 0.0) +
            self.procedural_similarity * weights.get('procedural', 0.0) +
            self.jurisdictional_similarity * weights.get('jurisdictional', 0.0) +
            self.temporal_similarity * weights.get('temporal', 0.0) +
            self.authority_similarity * weights.get('authority', 0.0)
        )
        
        self.overall_similarity = min(max(overall, 0.0), 1.0)
        return self.overall_similarity


@dataclass
class PrecedentMatch:
    """Comprehensive precedent match result with AI analysis"""
    case_id: str = ""
    case_title: str = ""
    citation: str = ""
    court: str = ""
    jurisdiction: str = ""
    decision_date: Optional[datetime] = None
    
    # Enhanced case content
    case_summary: str = ""
    legal_issues: List[str] = field(default_factory=list)
    holdings: List[str] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    outcome: str = ""
    
    # Advanced similarity analysis
    similarity_scores: SimilarityScore = field(default_factory=SimilarityScore)
    match_type: MatchType = MatchType.MODERATELY_SIMILAR
    relevance_score: float = 0.0
    
    # AI-powered legal principles
    extracted_principles: List[LegalPrinciple] = field(default_factory=list)
    
    # Enhanced authority and citation metrics
    citation_count: int = 0
    authority_score: float = 0.0
    pagerank_score: float = 0.0
    influence_score: float = 0.0
    
    # Advanced match analysis
    match_reasoning: str = ""
    distinguishing_factors: List[str] = field(default_factory=list)
    supporting_quotes: List[str] = field(default_factory=list)
    outcome_prediction: str = ""
    ai_analysis: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    confidence_intervals: Dict[str, float] = field(default_factory=dict)


class SimilarityCalculator:
    """Advanced algorithms for legal case similarity calculation"""
    
    def __init__(self, embeddings_model=None, ai_client=None):
        self.embeddings_model = embeddings_model
        self.ai_client = ai_client
        self.similarity_cache = {}
        
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Enhanced semantic similarity using legal embeddings"""
        try:
            if not self.embeddings_model or not text1 or not text2:
                return 0.0
            
            # Use existing embedding model for semantic similarity
            embeddings = self.embeddings_model.encode([text1[:2000], text2[:2000]])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"❌ Error calculating semantic similarity: {e}")
            return 0.0
    
    async def calculate_legal_issue_similarity(self, case1: Dict, case2: Dict) -> float:
        """AI-powered legal issue alignment scoring with Gemini analysis"""
        try:
            issues1 = case1.get("legal_issues", [])
            issues2 = case2.get("legal_issues", [])
            
            if not issues1 or not issues2:
                # Fallback to AI-powered content analysis
                return await self._ai_analyze_legal_similarity(
                    case1.get("content", ""), 
                    case2.get("content", "")
                )
            
            # Enhanced Jaccard similarity with legal concept weighting
            issues1_set = set([issue.lower().strip() for issue in issues1])
            issues2_set = set([issue.lower().strip() for issue in issues2])
            
            if not issues1_set or not issues2_set:
                return 0.0
            
            # Calculate weighted intersection based on legal domain importance
            intersection = len(issues1_set & issues2_set)
            union = len(issues1_set | issues2_set)
            
            base_similarity = intersection / union if union > 0 else 0.0
            
            # Apply legal domain weighting
            domain_weight = await self._calculate_domain_importance_weight(issues1_set, issues2_set)
            
            return min(1.0, base_similarity * domain_weight)
            
        except Exception as e:
            logger.error(f"❌ Error calculating legal issue similarity: {e}")
            return 0.0
    
    async def _ai_analyze_legal_similarity(self, content1: str, content2: str) -> float:
        """Use Gemini AI to analyze legal similarity when structured data unavailable"""
        try:
            if not self.ai_client or not content1 or not content2:
                return 0.0
            
            prompt = f"""
            As a legal expert, analyze the similarity between these two legal cases based on their legal issues and holdings:
            
            Case 1:
            {content1[:1000]}
            
            Case 2:
            {content2[:1000]}
            
            Provide a legal similarity score from 0.0 to 1.0 based on:
            1. Similar legal principles applied
            2. Comparable legal issues addressed
            3. Related holdings and outcomes
            4. Common legal doctrines
            
            Respond with just a decimal number between 0.0 and 1.0.
            """
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            # Extract similarity score from response  
            score_text = response.text.strip()
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))
            except ValueError:
                logger.warning(f"⚠️ Could not parse AI similarity score: {score_text}")
                return 0.5
                
        except Exception as e:
            logger.error(f"❌ Error in AI legal similarity analysis: {e}")
            return 0.0
    
    async def _calculate_domain_importance_weight(self, issues1_set: set, issues2_set: set) -> float:
        """Calculate domain importance weighting for legal issues"""
        try:
            # Define high-importance legal domains
            high_importance_domains = {
                'constitutional', 'contract', 'tort', 'criminal', 'employment',
                'intellectual_property', 'securities', 'antitrust', 'environmental'
            }
            
            # Check if any issues relate to high-importance domains
            all_issues = issues1_set | issues2_set
            high_importance_count = sum(1 for issue in all_issues 
                                     if any(domain in issue.lower() for domain in high_importance_domains))
            
            if high_importance_count > 0:
                return 1.2  # Boost for high-importance domains
            else:
                return 1.0  # Standard weighting
                
        except Exception:
            return 1.0
    
    async def calculate_jurisdictional_weight(self, case: Dict, target_jurisdiction: str) -> float:
        """Enhanced jurisdictional hierarchy and relevance weighting"""
        try:
            case_jurisdiction = case.get("jurisdiction", "").lower()
            target_jurisdiction = target_jurisdiction.lower()
            
            if not case_jurisdiction:
                return 0.5  # Unknown jurisdiction gets neutral weight
            
            # Exact match gets highest weight
            if case_jurisdiction == target_jurisdiction:
                return 1.0
            
            # Hierarchical relationships
            jurisdiction_hierarchy = {
                'us_supreme': 1.0,
                'us_federal': 0.9,
                'us_state': 0.7,
                'us': 0.6,
                'international': 0.4
            }
            
            case_weight = jurisdiction_hierarchy.get(case_jurisdiction, 0.3)
            target_weight = jurisdiction_hierarchy.get(target_jurisdiction, 0.3)
            
            # Calculate relative jurisdictional relevance
            return min(1.0, (case_weight + target_weight) / 2.0)
            
        except Exception as e:
            logger.error(f"❌ Error calculating jurisdictional weight: {e}")
            return 0.5
    
    async def calculate_temporal_relevance(self, case_date: str, legal_domain: str) -> float:
        """Enhanced temporal relevance with domain-specific decay functions"""
        try:
            if not case_date:
                return 0.5  # Unknown date gets neutral relevance
            
            # Parse case date
            case_datetime = self._parse_date(case_date)
            if not case_datetime:
                return 0.5
            
            # Calculate years since decision
            years_ago = (datetime.utcnow() - case_datetime).days / 365.0
            
            # Domain-specific decay rates
            domain_decay_rates = {
                'technology': 0.15,      # Fast decay for tech law
                'constitutional': 0.02,  # Slow decay for constitutional law
                'contract': 0.05,        # Moderate decay for contract law
                'tort': 0.04,           # Moderate decay for tort law
                'criminal': 0.06,       # Moderate-fast decay for criminal law
                'employment': 0.08,     # Faster decay for employment law
                'securities': 0.10,     # Fast decay for securities law
                'default': 0.06         # Default decay rate
            }
            
            decay_rate = domain_decay_rates.get(legal_domain.lower(), domain_decay_rates['default'])
            
            # Calculate temporal relevance using exponential decay
            relevance = np.exp(-decay_rate * years_ago)
            
            return max(0.1, min(1.0, relevance))  # Minimum 0.1 relevance for very old cases
            
        except Exception as e:
            logger.error(f"❌ Error calculating temporal relevance: {e}")
            return 0.5
    
    async def calculate_authority_weight(self, case: Dict) -> float:
        """Enhanced authority scoring based on court level and citation patterns"""
        try:
            court = case.get("court", "").lower()
            citation_count = case.get("citation_count", 0)
            
            # Court hierarchy weights
            court_weights = {
                'supreme': 1.0,
                'appellate': 0.8,
                'circuit': 0.8,
                'district': 0.6, 
                'trial': 0.6,
                'administrative': 0.4
            }
            
            # Determine court weight
            court_weight = 0.5  # Default
            for court_type, weight in court_weights.items():
                if court_type in court:
                    court_weight = weight
                    break
            
            # Citation count influence (normalized)
            citation_influence = min(0.5, citation_count / 100.0)
            
            # Combined authority weight
            authority_weight = (court_weight * 0.7) + (citation_influence * 0.3)
            
            return min(1.0, authority_weight)
            
        except Exception as e:
            logger.error(f"❌ Error calculating authority weight: {e}")
            return 0.5
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Enhanced date parsing with multiple format support"""
        try:
            # Common date formats in legal data
            formats = [
                "%Y-%m-%d", 
                "%Y-%m-%dT%H:%M:%S", 
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%m/%d/%Y",
                "%B %d, %Y",
                "%Y"
            ]
            
            for fmt in formats:
                try:
                    if fmt == "%Y":
                        # Year only - assume January 1st
                        year = int(date_str)
                        return datetime(year, 1, 1)
                    else:
                        return datetime.strptime(date_str[:len(fmt.replace('%f', '123456'))], fmt)
                except (ValueError, TypeError):
                    continue
            
            return None
            
        except Exception:
            return None


class PrecedentMatchingSystem:
    """
    Advanced AI-powered precedent matching system with comprehensive similarity analysis.
    
    This system provides enterprise-grade precedent analysis with 6-dimensional
    similarity scoring, AI-powered legal principle extraction, and authority assessment.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Enhanced Precedent Matching System"""
        self.config = config or {}
        
        # API Configuration
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        self.courtlistener_api_key = os.environ.get('COURTLISTENER_API_KEY')
        
        # MongoDB Configuration  
        self.mongo_url = os.environ.get('MONGO_URL')
        self.db_name = os.environ.get('DB_NAME', 'legal_research_db')
        
        # Initialize clients
        self.db_client = None
        self.db = None
        self.groq_client = None
        self.courtlistener_client = None
        
        # Enhanced embeddings model
        self.embeddings_model = None
        self.embedding_dimension = 384
        
        # FAISS index for enhanced similarity search
        self.faiss_index = None
        self.case_metadata = {}
        self.case_id_mapping = {}
        
        # Advanced similarity calculator
        self.similarity_calculator = None
        
        # Caching systems
        self.similarity_cache = {}
        self.principle_cache = {}
        self.authority_cache = {}
        
        # Performance metrics
        self.performance_metrics = {
            "total_matches": 0,
            "average_match_time": 0.0,
            "cache_hits": 0,
            "ai_principle_extractions": 0,
            "authority_calculations": 0
        }
        
        logger.info("🔍 Enhanced Precedent Matching System initialized")
    
    async def initialize(self):
        """Initialize all enhanced system components"""
        try:
            logger.info("🚀 Initializing Enhanced Precedent Matching System...")
            
            # Initialize AI clients
            if self.gemini_api_key:
                genai.configure(api_key=self.gemini_api_key)
                logger.info("✅ Gemini AI client initialized")
            
            if self.groq_api_key:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Groq AI client initialized")
            
            # Initialize CourtListener client
            # Support unauthenticated mode if key is missing (lower rate limits)
            headers = {"User-Agent": "LegalMateAI/precedent-matching"}
            if self.courtlistener_api_key:
                headers["Authorization"] = f"Token {self.courtlistener_api_key}"
            self.courtlistener_client = httpx.AsyncClient(
                base_url="https://www.courtlistener.com/api/rest/v3",
                headers=headers,
                timeout=30.0
            )
            logger.info("✅ CourtListener client initialized (auth: %s)" % ("yes" if self.courtlistener_api_key else "no"))
            
            # Initialize MongoDB connection
            if self.mongo_url:
                self.db_client = AsyncIOMotorClient(self.mongo_url)
                self.db = self.db_client[self.db_name]
                logger.info("✅ MongoDB connection established")
            
            # Initialize enhanced embeddings model
            await self._initialize_embeddings()
            
            # Initialize enhanced FAISS index
            await self._initialize_faiss_index()
            
            # Initialize similarity calculator
            self.similarity_calculator = SimilarityCalculator(
                embeddings_model=self.embeddings_model,
                ai_client=self.gemini_api_key
            )
            
            # Load enhanced case database quickly (KB + DB only)
            await self._load_case_database_base()

            # Start background enrichment from CourtListener if enabled
            enrich_on_start = os.environ.get('COURTLISTENER_ENRICH_ON_START', 'true').lower() in ('1','true','yes')
            if enrich_on_start:
                asyncio.create_task(self._background_enrich_courtlistener())
                logger.info("🧵 Started background CourtListener enrichment task")
            else:
                logger.info("⏭️ Skipping automatic CourtListener enrichment on start (config)")
            
            logger.info("🎉 Enhanced Precedent Matching System fully initialized!")
            
        except Exception as e:
            logger.error(f"❌ Error initializing enhanced precedent matching system: {e}")
            raise
    
    async def _initialize_embeddings(self):
        """Initialize enhanced embeddings model for legal semantic similarity"""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.warning("⚠️ Sentence transformers not available, using fallback")
                return
            
            logger.info("🔤 Loading enhanced legal embeddings model...")
            # Use optimized model for legal text analysis
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dimension = 384
            
            logger.info("✅ Enhanced embeddings model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing enhanced embeddings: {e}")
            self.embeddings_model = None
    
    async def _initialize_faiss_index(self):
        """Initialize enhanced FAISS index for high-performance similarity search"""
        try:
            if not FAISS_AVAILABLE:
                logger.warning("⚠️ FAISS not available for similarity indexing")
                return
                
            logger.info("📊 Initializing enhanced FAISS index for case similarity...")
            
            # Create enhanced FAISS index with better performance
            self.faiss_index = faiss.IndexFlatIP(self.embedding_dimension)
            
            logger.info("✅ Enhanced FAISS index initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing enhanced FAISS index: {e}")
            self.faiss_index = None
    
    async def _load_case_database(self):
        """Load and index comprehensive case database"""
        try:
            logger.info("📚 Loading comprehensive case database...")
            
            # Load from legal knowledge base
            knowledge_base_path = "/app/legal_knowledge_base.json"
            if os.path.exists(knowledge_base_path):
                with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                    cases = json.load(f)
                
                await self._process_cases_for_enhanced_indexing(cases)
                logger.info(f"✅ Loaded {len(cases)} cases into enhanced precedent database")
            else:
                logger.warning("⚠️ Legal knowledge base not found, loading from CourtListener...")
                await self._load_courtlistener_cases()
            
            # Load additional cases from database if available
            await self._load_database_cases()
            
            # Always attempt to enrich with recent CourtListener opinions if allowed
            await self._load_courtlistener_cases(max_cases=200)
            
        except Exception as e:
            logger.error(f"❌ Error loading comprehensive case database: {e}")
    
    async def _process_cases_for_enhanced_indexing(self, cases: List[Dict]):
        """Process cases with enhanced embeddings and metadata extraction"""
        try:
            if not self.embeddings_model or not FAISS_AVAILABLE:
                logger.warning("⚠️ Enhanced indexing not available")
                return
            
            logger.info("🔍 Processing cases for enhanced embeddings indexing...")
            
            case_texts = []
            case_ids = []
            
            for i, case in enumerate(cases):
                # Enhanced text combination for better embeddings
                case_text_parts = []
                if case.get('title'):
                    case_text_parts.append(f"Title: {case['title']}")
                if case.get('content'):
                    case_text_parts.append(f"Content: {case['content'][:1500]}")
                if case.get('legal_domain'):
                    case_text_parts.append(f"Domain: {case['legal_domain']}")
                if case.get('jurisdiction'):
                    case_text_parts.append(f"Jurisdiction: {case['jurisdiction']}")
                
                case_text = " | ".join(case_text_parts)
                
                if case_text.strip():
                    case_texts.append(case_text)
                    case_id = case.get('id', f'case_{i}')
                    case_ids.append(case_id)
                    
                    # Store enhanced case metadata
                    enhanced_metadata = case.copy()
                    enhanced_metadata.update({
                        'indexed_at': datetime.utcnow().isoformat(),
                        'embedding_text': case_text[:500]  # Store snippet for debugging
                    })
                    self.case_metadata[case_id] = enhanced_metadata
                    self.case_id_mapping[len(case_ids) - 1] = case_id
            
            if case_texts and self.faiss_index:
                # Generate enhanced embeddings
                logger.info("🧠 Generating enhanced semantic embeddings...")
                embeddings = self.embeddings_model.encode(
                    case_texts, 
                    convert_to_numpy=True,
                    show_progress_bar=True,
                    batch_size=32
                )
                
                # Normalize for cosine similarity
                faiss.normalize_L2(embeddings)
                
                # Add to enhanced FAISS index
                self.faiss_index.add(embeddings)
                
                logger.info(f"✅ Enhanced indexing completed - {len(case_texts)} cases indexed")
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced case processing: {e}")
    
    async def _load_database_cases(self):
        """Load additional cases from MongoDB database"""
        try:
            if not self.db:
                return
                
            logger.info("💾 Loading additional cases from database...")
            
            # Load cases from legal_research_queries collection
            cursor = self.db.legal_research_queries.find({
                "results": {"$exists": True, "$ne": []}
            }).limit(1000)
            
            additional_cases = []
            async for query_doc in cursor:
                for result in query_doc.get('results', []):
                    if result.get('result_type') == 'case' and result.get('content_summary'):
                        case_data = {
                            'id': result.get('result_id', str(uuid.uuid4())),
                            'title': result.get('content_summary', '')[:100] + "...",
                            'content': result.get('content_summary', ''),
                            'jurisdiction': query_doc.get('jurisdiction', 'US'),
                            'legal_domain': query_doc.get('legal_domain', 'general'),
                            'source': 'database',
                            'relevance_score': result.get('relevance_score', 0.0)
                        }
                        additional_cases.append(case_data)
            
            if additional_cases:
                await self._process_cases_for_enhanced_indexing(additional_cases)
                logger.info(f"✅ Loaded {len(additional_cases)} additional cases from database")
            
        except Exception as e:
            logger.error(f"❌ Error loading database cases: {e}")
    
    async def _load_courtlistener_cases(self, years_back: int = 5, max_cases: int = 150):
        """Fetch recent opinions from CourtListener and index them.
        Works with or without API key (lower rate limits without key).
        """
        try:
            if not self.courtlistener_client:
                # As a fallback, create a client without auth
                self.courtlistener_client = httpx.AsyncClient(
                    base_url="https://www.courtlistener.com/api/rest/v3",
                    headers={"User-Agent": "LegalMateAI/precedent-matching"},
                    timeout=30.0
                )
            
            start_date = (datetime.utcnow() - timedelta(days=365 * years_back)).strftime('%Y-%m-%d')
            params = {
                'filed_after': start_date,
                'order_by': '-date_filed',
                'type': 'opinion',
                'page_size': 50,
                'format': 'json'
            }
            
            collected = 0
            next_url = '/search/'
            cases: List[Dict[str, Any]] = []
            
            while next_url and collected < max_cases:
                try:
                    resp = await self.courtlistener_client.get(next_url, params=params if next_url == '/search/' else None)
                    if resp.status_code != 200:
                        logger.warning(f"CourtListener request failed: {resp.status_code} {resp.text[:200]}")
                        break
                    data = resp.json()
                except Exception as e:
                    logger.error(f"Error fetching CourtListener data: {e}")
                    break
                
                for result in data.get('results', []):
                    if collected >= max_cases:
                        break
                    try:
                        case_id = str(result.get('id', ''))
                        title = result.get('caseName', '') or result.get('caseNameFull', '') or result.get('caseNameShort', '')
                        date_filed = result.get('dateFiled') or result.get('date_filed')
                        citation = None
                        cites = result.get('citations') or []
                        if isinstance(cites, list) and cites:
                            citation = cites[0].get('cite')
                        absolute_url = result.get('absolute_url') or result.get('absoluteUrl')
                        court = result.get('court', '')
                        jurisdiction = 'US'
                        
                        # Fetch opinion text where possible
                        content = await self._fetch_courtlistener_opinion_text(result)
                        if not content:
                            # Fallback to snippet
                            content = result.get('snippet', '') or ''
                        
                        if not title and not content:
                            continue
                        
                        case_obj = {
                            'id': f"cl_{case_id}",
                            'title': title or (absolute_url or 'CourtListener Opinion'),
                            'content': content[:8000],
                            'jurisdiction': jurisdiction,
                            'court': court,
                            'citation': citation or '',
                            'date_filed': date_filed or '',
                            'source': 'courtlistener',
                            'source_url': f"https://www.courtlistener.com{absolute_url}" if absolute_url else '',
                            'citation_count': result.get('citeCount', 0) or result.get('citation_count', 0),
                            'legal_domain': 'general'
                        }
                        cases.append(case_obj)
                        collected += 1
                    except Exception as e:
                        logger.warning(f"Error parsing CourtListener result: {e}")
                        continue
                
                next_url = data.get('next')
                # Respect rate limits
                await asyncio.sleep(0.2 if self.courtlistener_api_key else 0.6)
            
            if cases:
                await self._process_cases_for_enhanced_indexing(cases)
                logger.info(f"✅ Indexed {len(cases)} CourtListener opinions")
            else:
                logger.info("ℹ️ No CourtListener opinions fetched")
        except Exception as e:
            logger.error(f"❌ Error loading CourtListener cases: {e}")
    
    async def _fetch_courtlistener_opinion_text(self, result: Dict[str, Any]) -> str:
        """Attempt to retrieve full opinion text for a search result."""
        try:
            # If opinions endpoint id available, try fetching
            opinion_id = result.get('id')
            if opinion_id is not None:
                url = f"/opinions/{opinion_id}/"
                try:
                    resp = await self.courtlistener_client.get(url, params={'format': 'json'})
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data.get('plain_text') or data.get('html') or ''
                        if text:
                            # Strip HTML if needed
                            return text if isinstance(text, str) else ''
                except Exception:
                    pass
            
            # Try to follow absolute_url if present (as a last resort skip due to HTML)
            snippet = result.get('snippet', '') or ''
            return snippet
        except Exception:
            return ""
    
    async def find_similar_cases(self, query_case: Dict[str, Any], 
                               filters: Dict[str, Any] = None) -> List[PrecedentMatch]:
        """
        Find similar cases using comprehensive 6-dimensional similarity analysis.
        Implements the enhanced similarity matching as specified in requirements.
        
        Args:
            query_case: Case to find precedents for with facts, legal_issues, etc.
            filters: Enhanced filters for jurisdiction, date range, court level, etc.
            
        Returns:
            List[PrecedentMatch]: Ranked list of similar cases with comprehensive analysis
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Finding similar cases with enhanced 6-dimensional analysis...")
            
            # Extract enhanced query information
            query_facts = query_case.get("facts", "")
            query_issues = query_case.get("legal_issues", [])
            query_jurisdiction = query_case.get("jurisdiction", "US")
            query_legal_domain = query_case.get("legal_domain", "general")
            
            # Apply enhanced filters
            filters = filters or {}
            max_results = filters.get("max_results", 20)
            min_similarity = filters.get("min_similarity", 0.6)
            
            # Perform enhanced semantic similarity search
            similar_cases = await self._enhanced_semantic_similarity_search(
                query_text=query_facts,
                query_issues=query_issues,
                max_results=max_results * 3  # Get more candidates for filtering
            )
            
            # Perform comprehensive 6-dimensional similarity analysis
            precedent_matches = []
            
            for case_data in similar_cases:
                match = await self._comprehensive_case_similarity_analysis(
                    query_case=query_case,
                    candidate_case=case_data,
                    filters=filters
                )
                
                if match and match.similarity_scores.overall_similarity >= min_similarity:
                    precedent_matches.append(match)
            
            # Enhanced ranking with multiple factors
            precedent_matches = await self._rank_precedent_matches(precedent_matches, query_case)
            
            # Limit to requested number of results
            precedent_matches = precedent_matches[:max_results]
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, len(precedent_matches))
            
            logger.info(f"✅ Enhanced precedent search completed - {len(precedent_matches)} matches in {processing_time:.2f}s")
            
            return precedent_matches
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced precedent search: {e}")
            raise
    
    async def _enhanced_semantic_similarity_search(self, query_text: str, query_issues: List[str], max_results: int = 50) -> List[Dict]:
        """Enhanced semantic similarity search with legal issue weighting"""
        try:
            if not self.embeddings_model or not self.faiss_index:
                logger.warning("⚠️ Enhanced embeddings or FAISS index not available")
                return []
            
            # Create enhanced query text combining facts and legal issues
            enhanced_query_parts = []
            if query_text:
                enhanced_query_parts.append(f"Facts: {query_text}")
            if query_issues:
                enhanced_query_parts.append(f"Legal Issues: {' | '.join(query_issues)}")
            
            enhanced_query_text = " | ".join(enhanced_query_parts)
            
            # Generate enhanced query embedding
            query_embedding = self.embeddings_model.encode([enhanced_query_text], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Enhanced FAISS search
            similarities, indices = self.faiss_index.search(query_embedding, max_results)
            
            # Retrieve enhanced case metadata
            similar_cases = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx < len(self.case_id_mapping) and similarity > 0.0:
                    case_id = self.case_id_mapping[idx]
                    case_data = self.case_metadata[case_id].copy()
                    case_data['semantic_similarity'] = float(similarity)
                    case_data['search_rank'] = len(similar_cases) + 1
                    similar_cases.append(case_data)
            
            return similar_cases
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced semantic similarity search: {e}")
            return []
    
    async def _comprehensive_case_similarity_analysis(self, query_case: Dict, candidate_case: Dict, 
                                                    filters: Dict = None) -> Optional[PrecedentMatch]:
        """Comprehensive 6-dimensional similarity analysis as specified"""
        try:
            # Perform enhanced 6-dimensional similarity analysis
            similarity_scores = await self.analyze_case_similarity(query_case, candidate_case)
            
            # Apply enhanced filters
            if not await self._apply_enhanced_filters(candidate_case, filters):
                return None
            
            # Create comprehensive precedent match
            match = PrecedentMatch(
                case_id=candidate_case.get("id", ""),
                case_title=candidate_case.get("title", ""),
                citation=candidate_case.get("citation", ""),
                court=candidate_case.get("court", ""),
                jurisdiction=candidate_case.get("jurisdiction", ""),
                case_summary=candidate_case.get("content", "")[:500],
                similarity_scores=similarity_scores
            )
            
            # Parse decision date
            if candidate_case.get("date_filed"):
                match.decision_date = self._parse_date(candidate_case["date_filed"])
            
            # Determine enhanced match type
            match.match_type = self._determine_enhanced_match_type(similarity_scores.overall_similarity)
            
            # Calculate enhanced relevance score
            match.relevance_score = await self._calculate_enhanced_relevance_score(
                similarity_scores, 
                candidate_case
            )
            
            # Extract legal principles using AI
            match.extracted_principles = await self.extract_legal_principles(
                candidate_case.get("content", "")
            )
            
            # Generate AI-powered match reasoning
            match.match_reasoning = await self._generate_ai_match_reasoning(
                query_case, candidate_case, similarity_scores
            )
            
            # Identify distinguishing factors
            match.distinguishing_factors = await self._identify_distinguishing_factors(
                query_case, candidate_case
            )
            
            # Calculate authority metrics
            await self._calculate_authority_metrics(match, candidate_case)
            
            # Generate AI analysis
            match.ai_analysis = await self._generate_comprehensive_ai_analysis(
                query_case, candidate_case, similarity_scores
            )
            
            return match
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive case similarity analysis: {e}")
            return None
    
    async def analyze_case_similarity(self, case1: Dict, case2: Dict) -> SimilarityScore:
        """
        Enhanced multi-dimensional similarity analysis between two cases.
        Implements the 6-dimensional analysis as specified in requirements.
        
        Args:
            case1: First case for comparison
            case2: Second case for comparison
            
        Returns:
            SimilarityScore: Comprehensive 6-dimensional similarity analysis
        """
        try:
            logger.info("🔍 Performing comprehensive 6-dimensional similarity analysis...")
            
            similarity = SimilarityScore()
            
            # 1. Factual similarity (30% weight) - Semantic embedding similarity
            similarity.factual_similarity = await self.similarity_calculator.calculate_semantic_similarity(
                case1.get("facts", case1.get("content", "")),
                case2.get("facts", case2.get("content", ""))
            )
            
            # 2. Legal similarity (25% weight) - Legal issue categorization matching
            similarity.legal_similarity = await self.similarity_calculator.calculate_legal_issue_similarity(
                case1, case2
            )
            
            # 3. Jurisdictional similarity (20% weight) - Jurisdictional hierarchy consideration
            similarity.jurisdictional_similarity = await self.similarity_calculator.calculate_jurisdictional_weight(
                case2, case1.get("jurisdiction", "US")
            )
            
            # 4. Temporal similarity (15% weight) - Temporal relevance scoring
            similarity.temporal_similarity = await self.similarity_calculator.calculate_temporal_relevance(
                case2.get("date_filed", ""), 
                case1.get("legal_domain", "general")
            )
            
            # 5. Authority similarity (10% weight) - Authority weight calculation
            similarity.authority_similarity = await self.similarity_calculator.calculate_authority_weight(case2)
            
            # 6. Procedural similarity - Included in overall calculation
            similarity.procedural_similarity = await self._calculate_procedural_similarity(case1, case2)
            
            # Calculate weighted overall similarity
            similarity.calculate_overall()
            
            # Calculate comprehensive confidence score
            similarity.confidence_score = await self._calculate_enhanced_confidence_score(case1, case2, similarity)
            
            # AI confidence assessment
            similarity.ai_confidence = await self._calculate_ai_confidence_assessment(case1, case2, similarity)
            
            logger.info(f"✅ 6-dimensional similarity analysis completed - Overall: {similarity.overall_similarity:.3f}")
            
            return similarity
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive similarity analysis: {e}")
            return SimilarityScore()
    
    async def _calculate_procedural_similarity(self, case1: Dict, case2: Dict) -> float:
        """Enhanced procedural similarity calculation"""
        try:
            court1 = case1.get("court", "").lower()
            court2 = case2.get("court", "").lower()
            
            case_type1 = case1.get("case_type", "").lower() 
            case_type2 = case2.get("case_type", "").lower()
            
            similarity_score = 0.0
            
            # Enhanced court level similarity
            if court1 and court2:
                if court1 == court2:
                    similarity_score += 0.6
                elif self._same_court_level(court1, court2):
                    similarity_score += 0.4
                elif self._compatible_court_levels(court1, court2):
                    similarity_score += 0.2
            
            # Enhanced case type similarity
            if case_type1 and case_type2:
                if case_type1 == case_type2:
                    similarity_score += 0.4
                elif self._similar_case_type(case_type1, case_type2):
                    similarity_score += 0.3
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"❌ Error calculating procedural similarity: {e}")
            return 0.0
    
    async def _calculate_enhanced_confidence_score(self, case1: Dict, case2: Dict, similarity: SimilarityScore) -> float:
        """Enhanced confidence scoring based on data completeness and quality"""
        try:
            completeness_score = 0.0
            
            # Enhanced data completeness check
            essential_fields = ["title", "content", "jurisdiction", "court"]
            optional_fields = ["legal_domain", "date_filed", "citation", "legal_issues"]
            
            for field in essential_fields:
                if case1.get(field) and case2.get(field):
                    completeness_score += 0.20  # 80% for essential fields
            
            for field in optional_fields:
                if case1.get(field) and case2.get(field):
                    completeness_score += 0.05  # 20% for optional fields
            
            # Quality assessment based on content length and structure
            content1_quality = min(1.0, len(case1.get("content", "")) / 1000.0)
            content2_quality = min(1.0, len(case2.get("content", "")) / 1000.0)
            content_quality = (content1_quality + content2_quality) / 2.0
            
            # Similarity variance assessment
            similarities = [
                similarity.factual_similarity,
                similarity.legal_similarity,
                similarity.procedural_similarity,
                similarity.jurisdictional_similarity,
                similarity.temporal_similarity,
                similarity.authority_similarity
            ]
            
            similarity_variance = np.var(similarities)
            variance_factor = min(1.0, 1.0 - similarity_variance)  # Lower variance = higher confidence
            
            # Combined confidence score
            confidence = (completeness_score * 0.4) + (content_quality * 0.3) + (variance_factor * 0.3)
            
            return min(1.0, max(0.1, confidence))
            
        except Exception as e:
            logger.error(f"❌ Error calculating enhanced confidence score: {e}")
            return 0.5
    
    async def _calculate_ai_confidence_assessment(self, case1: Dict, case2: Dict, similarity: SimilarityScore) -> float:
        """AI-powered confidence assessment using Gemini"""
        try:
            if not self.gemini_api_key:
                return similarity.confidence_score
            
            prompt = f"""
            As a legal expert, assess the confidence level of this case similarity analysis:
            
            Case 1: {case1.get('title', 'Unknown')[:200]}
            Case 2: {case2.get('title', 'Unknown')[:200]}
            
            Similarity Scores:
            - Factual: {similarity.factual_similarity:.3f}
            - Legal: {similarity.legal_similarity:.3f}
            - Jurisdictional: {similarity.jurisdictional_similarity:.3f}
            - Temporal: {similarity.temporal_similarity:.3f}
            - Authority: {similarity.authority_similarity:.3f}
            - Overall: {similarity.overall_similarity:.3f}
            
            Rate the confidence of this similarity analysis from 0.0 to 1.0 based on:
            1. Consistency of similarity scores across dimensions
            2. Availability and quality of case information
            3. Logical coherence of the similarity assessment
            
            Respond with just a decimal number between 0.0 and 1.0.
            """
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            try:
                ai_confidence = float(response.text.strip())
                return max(0.0, min(1.0, ai_confidence))
            except ValueError:
                return similarity.confidence_score
                
        except Exception as e:
            logger.error(f"❌ Error in AI confidence assessment: {e}")
            return similarity.confidence_score
    
    async def extract_legal_principles(self, case_content: str) -> List[LegalPrinciple]:
        """
        Enhanced AI-powered legal principle extraction using Gemini.
        Implements comprehensive principle extraction as specified.
        
        Args:
            case_content: Full text of the legal case
            
        Returns:
            List[LegalPrinciple]: Extracted legal principles with enhanced metadata
        """
        try:
            logger.info("🧠 Extracting legal principles using enhanced AI analysis...")
            
            if not case_content or len(case_content.strip()) < 100:
                return []
            
            # Check enhanced cache first
            content_hash = hash(case_content[:2000])
            if content_hash in self.principle_cache:
                self.performance_metrics["cache_hits"] += 1
                return self.principle_cache[content_hash]
            
            # Enhanced principle extraction using Gemini
            principles = await self._extract_principles_with_enhanced_gemini(case_content)
            
            # Cache results
            self.principle_cache[content_hash] = principles
            self.performance_metrics["ai_principle_extractions"] += 1
            
            logger.info(f"✅ Extracted {len(principles)} legal principles with enhanced analysis")
            
            return principles
            
        except Exception as e:
            logger.error(f"❌ Error extracting legal principles: {e}")
            return []
    
    async def _extract_principles_with_enhanced_gemini(self, case_content: str) -> List[LegalPrinciple]:
        """Enhanced legal principle extraction using Gemini AI"""
        try:
            prompt = f"""
            Analyze this legal case content and extract the key legal principles with comprehensive metadata:

            {case_content[:3000]}

            Extract and analyze:
            1. Core legal principles established or applied
            2. Rules of law stated by the court
            3. Legal tests or standards articulated
            4. Precedential value and authority level
            5. Related legal doctrines and principles

            Format your response as JSON with this structure:
            {{
                "principles": [
                    {{
                        "principle_text": "The specific legal principle or rule",
                        "legal_domain": "contract_law|tort_law|constitutional_law|criminal_law|employment_law|intellectual_property|etc",
                        "authority_level": "supreme_court|appellate_court|trial_court|administrative",
                        "precedential_value": "high|medium|low",
                        "confidence_score": 0.0-1.0,
                        "supporting_citations": ["relevant citation text"],
                        "related_principles": ["related principle descriptions"],
                        "ai_analysis": "Brief analysis of the principle's significance"
                    }}
                ]
            }}
            
            Focus on principles that have clear precedential value and legal significance.
            """
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            # Parse enhanced JSON response
            try:
                response_data = json.loads(response.text.strip())
                principles = []
                
                for principle_data in response_data.get("principles", []):
                    # Map authority level string to enum
                    authority_mapping = {
                        "supreme_court": AuthorityLevel.SUPREME_COURT,
                        "appellate_court": AuthorityLevel.APPELLATE_COURT,
                        "trial_court": AuthorityLevel.TRIAL_COURT,
                        "administrative": AuthorityLevel.ADMINISTRATIVE
                    }
                    
                    principle = LegalPrinciple(
                        principle_text=principle_data.get("principle_text", ""),
                        legal_domain=principle_data.get("legal_domain", "general"),
                        authority_level=authority_mapping.get(
                            principle_data.get("authority_level", "trial_court"),
                            AuthorityLevel.TRIAL_COURT
                        ),
                        confidence_score=principle_data.get("confidence_score", 0.7),
                        precedential_value=principle_data.get("precedential_value", "medium"),
                        supporting_citations=principle_data.get("supporting_citations", []),
                        related_principles=principle_data.get("related_principles", []),
                        ai_analysis=principle_data.get("ai_analysis", "")
                    )
                    principles.append(principle)
                
                return principles
                
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Could not parse AI response for principle extraction")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced Gemini principle extraction: {e}")
            return []
    
    async def auto_validate_precedent_relevance(self, precedents: List[PrecedentMatch]) -> Dict[str, Any]:
        """
        AI-powered precedent validation and relevance assessment.
        Implements comprehensive validation as specified.
        
        Args:
            precedents: List of precedent matches to validate
            
        Returns:
            Dict: Validation results with quality metrics and recommendations
        """
        try:
            logger.info(f"🎯 Validating relevance of {len(precedents)} precedents...")
            
            validation_results = {
                "total_precedents": len(precedents),
                "high_relevance": [],
                "medium_relevance": [],
                "low_relevance": [],
                "quality_issues": [],
                "recommendations": [],
                "overall_quality_score": 0.0
            }
            
            for precedent in precedents:
                # Relevance scoring using multi-factor analysis
                relevance_assessment = await self._assess_precedent_relevance(precedent)
                
                # Quality assessment based on court hierarchy and citations
                quality_assessment = await self._assess_precedent_quality(precedent)
                
                # Temporal currency validation
                currency_assessment = await self._assess_precedent_currency(precedent)
                
                # Combine assessments
                overall_score = (
                    relevance_assessment * 0.5 +
                    quality_assessment * 0.3 +
                    currency_assessment * 0.2
                )
                
                precedent.relevance_score = overall_score
                
                # Categorize by relevance
                if overall_score >= 0.8:
                    validation_results["high_relevance"].append(precedent)
                elif overall_score >= 0.6:
                    validation_results["medium_relevance"].append(precedent)
                else:
                    validation_results["low_relevance"].append(precedent)
                    validation_results["quality_issues"].append({
                        "case_id": precedent.case_id,
                        "issue": "Low relevance score",
                        "score": overall_score
                    })
            
            # Calculate overall quality score
            if precedents:
                validation_results["overall_quality_score"] = sum(
                    p.relevance_score for p in precedents
                ) / len(precedents)
            
            # Generate recommendations
            validation_results["recommendations"] = await self._generate_validation_recommendations(
                validation_results
            )
            
            logger.info(f"✅ Precedent validation completed - Overall quality: {validation_results['overall_quality_score']:.3f}")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Error in precedent validation: {e}")
            raise
    
    async def _assess_precedent_relevance(self, precedent: PrecedentMatch) -> float:
        """Assess precedent relevance using multi-factor analysis"""
        try:
            factors = []
            
            # Similarity score factor
            factors.append(precedent.similarity_scores.overall_similarity * 0.4)
            
            # Authority factor
            factors.append(precedent.authority_score * 0.3)
            
            # Recency factor
            if precedent.decision_date:
                years_ago = (datetime.utcnow() - precedent.decision_date).days / 365.0
                recency_score = max(0.1, 1.0 - (years_ago * 0.05))  # 5% decay per year
                factors.append(recency_score * 0.2)
            else:
                factors.append(0.5 * 0.2)  # Neutral score for unknown date
            
            # Legal principle relevance
            principle_score = len(precedent.extracted_principles) / 5.0  # Normalize to max 5 principles
            factors.append(min(1.0, principle_score) * 0.1)
            
            return sum(factors)
            
        except Exception:
            return 0.5
    
    async def _assess_precedent_quality(self, precedent: PrecedentMatch) -> float:
        """Assess precedent quality based on court hierarchy and citations"""
        try:
            quality_score = 0.0
            
            # Court hierarchy assessment
            court = precedent.court.lower()
            if "supreme" in court:
                quality_score += 0.5
            elif "appellate" in court or "circuit" in court:
                quality_score += 0.4
            elif "district" in court or "trial" in court:
                quality_score += 0.3
            else:
                quality_score += 0.2
            
            # Citation count assessment
            citation_score = min(0.3, precedent.citation_count / 100.0)
            quality_score += citation_score
            
            # Content quality assessment
            content_length = len(precedent.case_summary)
            content_score = min(0.2, content_length / 1000.0)
            quality_score += content_score
            
            return min(1.0, quality_score)
            
        except Exception:
            return 0.5
    
    async def _assess_precedent_currency(self, precedent: PrecedentMatch) -> float:
        """Assess temporal currency and precedent status"""
        try:
            if not precedent.decision_date:
                return 0.5  # Neutral for unknown date
            
            years_ago = (datetime.utcnow() - precedent.decision_date).days / 365.0
            
            # Base currency score with exponential decay
            base_score = np.exp(-0.05 * years_ago)  # 5% annual decay
            
            # Adjust for legal domain
            domain_factors = {
                'technology': 0.8,      # Faster decay for tech law
                'constitutional': 1.2,  # Slower decay for constitutional law
                'contract': 1.0,        # Standard decay
                'tort': 1.0,           # Standard decay
                'criminal': 0.9,       # Moderate decay
                'employment': 0.85     # Faster decay for employment law
            }
            
            # Extract legal domain from extracted principles
            domain_factor = 1.0
            for principle in precedent.extracted_principles:
                domain = principle.legal_domain.replace('_law', '')
                if domain in domain_factors:
                    domain_factor = domain_factors[domain]
                    break
            
            currency_score = base_score * domain_factor
            
            return max(0.1, min(1.0, currency_score))
            
        except Exception:
            return 0.5
    
    async def _generate_validation_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate validation recommendations based on assessment results"""
        try:
            recommendations = []
            
            high_count = len(validation_results["high_relevance"])
            medium_count = len(validation_results["medium_relevance"])
            low_count = len(validation_results["low_relevance"])
            total_count = validation_results["total_precedents"]
            
            if total_count == 0:
                recommendations.append("No precedents found. Consider broadening search criteria.")
                return recommendations
            
            # Quality distribution recommendations
            high_ratio = high_count / total_count
            if high_ratio < 0.3:
                recommendations.append("Consider refining search criteria to find more highly relevant precedents.")
            
            if low_count > total_count * 0.4:
                recommendations.append("Many precedents have low relevance scores. Consider narrowing jurisdiction or legal domain filters.")
            
            # Quality issue recommendations
            if validation_results["quality_issues"]:
                recommendations.append(f"Found {len(validation_results['quality_issues'])} precedents with quality issues. Review these carefully.")
            
            # Overall quality recommendations
            overall_quality = validation_results["overall_quality_score"]
            if overall_quality < 0.6:
                recommendations.append("Overall precedent quality is below optimal. Consider additional search terms or alternative legal databases.")
            elif overall_quality > 0.8:
                recommendations.append("Excellent precedent quality detected. These results provide strong legal support.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating validation recommendations: {e}")
            return ["Unable to generate recommendations due to analysis error."]
    
    # Additional helper methods for enhanced functionality
    
    async def _apply_enhanced_filters(self, candidate_case: Dict, filters: Dict) -> bool:
        """Apply enhanced filtering logic"""
        try:
            if not filters:
                return True
            
            # Jurisdiction filter
            jurisdiction = filters.get("jurisdiction")
            if jurisdiction and candidate_case.get("jurisdiction") != jurisdiction:
                # Allow hierarchical jurisdiction matching
                if not self._is_compatible_jurisdiction(candidate_case.get("jurisdiction", ""), jurisdiction):
                    return False
            
            # Date range filter
            date_range = filters.get("date_range")
            if date_range:
                case_date = candidate_case.get("date_filed")
                if not self._date_in_enhanced_range(case_date, date_range):
                    return False
            
            # Court level filter
            court_level = filters.get("court_level")
            if court_level:
                case_court = candidate_case.get("court", "").lower()
                if not self._matches_court_level(case_court, court_level):
                    return False
            
            # Legal domain filter
            legal_domain = filters.get("legal_domain")
            if legal_domain and legal_domain != "general":
                case_domain = candidate_case.get("legal_domain", "")
                if not self._matches_legal_domain(case_domain, legal_domain):
                    return False
            
            return True
            
        except Exception:
            return True  # Default to include if filter evaluation fails
    
    def _is_compatible_jurisdiction(self, case_jurisdiction: str, target_jurisdiction: str) -> bool:
        """Check if jurisdictions are compatible (hierarchical matching)"""
        try:
            case_j = case_jurisdiction.lower()
            target_j = target_jurisdiction.lower()
            
            if case_j == target_j:
                return True
            
            # Hierarchical compatibility
            if target_j == "us" and any(prefix in case_j for prefix in ["us_", "federal"]):
                return True
            
            if "federal" in target_j and "us_federal" in case_j:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _date_in_enhanced_range(self, date_str: str, date_range: Dict) -> bool:
        """Enhanced date range checking"""
        try:
            if not date_str:
                return True  # Include if date unknown
            
            case_date = self._parse_date(date_str)
            if not case_date:
                return True
            
            start_str = date_range.get("start")
            end_str = date_range.get("end")
            
            if start_str:
                start_date = self._parse_date(start_str)
                if start_date and case_date < start_date:
                    return False
            
            if end_str:
                end_date = self._parse_date(end_str)
                if end_date and case_date > end_date:
                    return False
            
            return True
            
        except Exception:
            return True
    
    def _matches_court_level(self, case_court: str, target_level: str) -> bool:
        """Check if case court matches target level"""
        try:
            target_level = target_level.lower()
            
            level_keywords = {
                'supreme': ['supreme'],
                'appellate': ['appellate', 'appeal', 'circuit'],
                'trial': ['district', 'trial', 'superior'],
                'federal': ['federal', 'circuit', 'district'],
                'state': ['state', 'superior', 'county']
            }
            
            if target_level in level_keywords:
                return any(keyword in case_court for keyword in level_keywords[target_level])
            
            return True
            
        except Exception:
            return True
    
    def _matches_legal_domain(self, case_domain: str, target_domain: str) -> bool:
        """Check if case legal domain matches target"""
        try:
            if not case_domain:
                return True  # Include if domain unknown
            
            return case_domain.lower() == target_domain.lower()
            
        except Exception:
            return True
    
    def _determine_enhanced_match_type(self, similarity_score: float) -> MatchType:
        """Enhanced match type determination"""
        if similarity_score >= 0.95:
            return MatchType.IDENTICAL
        elif similarity_score >= 0.85:
            return MatchType.HIGHLY_SIMILAR
        elif similarity_score >= 0.70:
            return MatchType.MODERATELY_SIMILAR
        elif similarity_score >= 0.55:
            return MatchType.ANALOGOUS
        elif similarity_score >= 0.30:
            return MatchType.DISTINGUISHABLE
        else:
            return MatchType.CONTRARY
    
    async def _calculate_enhanced_relevance_score(self, similarity: SimilarityScore, candidate_case: Dict) -> float:
        """Enhanced relevance scoring with multiple factors"""
        try:
            # Base score from similarity
            relevance = similarity.overall_similarity * 0.6
            
            # Authority bonus
            authority_bonus = candidate_case.get("authority_score", 0.0) * 0.15
            relevance += authority_bonus
            
            # Citation count bonus
            citation_count = candidate_case.get("citation_count", 0)
            citation_bonus = min(0.15, (citation_count / 100.0) * 0.15)
            relevance += citation_bonus
            
            # Confidence factor
            confidence_factor = similarity.confidence_score
            relevance *= (0.7 + confidence_factor * 0.3)  # Scale between 0.7 and 1.0
            
            # Recency bonus for recent cases
            if candidate_case.get("date_filed"):
                case_date = self._parse_date(candidate_case["date_filed"])
                if case_date:
                    years_ago = (datetime.utcnow() - case_date).days / 365.0
                    if years_ago <= 5:
                        recency_bonus = (5 - years_ago) / 50.0  # Up to 0.1 bonus
                        relevance += recency_bonus
            
            return min(1.0, max(0.0, relevance))
            
        except Exception:
            return similarity.overall_similarity
    
    async def _rank_precedent_matches(self, matches: List[PrecedentMatch], query_case: Dict) -> List[PrecedentMatch]:
        """Enhanced ranking algorithm for precedent matches"""
        try:
            # Multi-factor ranking
            for match in matches:
                ranking_score = 0.0
                
                # Primary factors
                ranking_score += match.relevance_score * 0.4
                ranking_score += match.similarity_scores.overall_similarity * 0.3
                ranking_score += match.authority_score * 0.2
                
                # Secondary factors
                if match.extracted_principles:
                    principle_bonus = min(0.05, len(match.extracted_principles) / 100.0)
                    ranking_score += principle_bonus
                
                if match.similarity_scores.confidence_score > 0.8:
                    ranking_score += 0.05  # High confidence bonus
                
                match.relevance_score = ranking_score
            
            # Sort by enhanced ranking score
            matches.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error ranking precedent matches: {e}")
            return matches
    
    async def _generate_ai_match_reasoning(self, query_case: Dict, candidate_case: Dict, similarity: SimilarityScore) -> str:
        """Generate AI-powered match reasoning"""
        try:
            if not self.gemini_api_key:
                return f"Match based on {similarity.overall_similarity:.1%} overall similarity"
            
            prompt = f"""
            Explain why this legal case is a relevant precedent match:
            
            Query Case: {query_case.get('facts', '')[:300]}
            Precedent Case: {candidate_case.get('title', '')} - {candidate_case.get('content', '')[:300]}
            
            Similarity Scores:
            - Overall: {similarity.overall_similarity:.1%}
            - Factual: {similarity.factual_similarity:.1%}
            - Legal: {similarity.legal_similarity:.1%}
            
            Provide a concise explanation (2-3 sentences) of why this precedent is relevant.
            """
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            return response.text.strip()[:500]  # Limit length
            
        except Exception as e:
            logger.error(f"❌ Error generating AI match reasoning: {e}")
            return f"Match based on {similarity.overall_similarity:.1%} overall similarity across multiple dimensions"
    
    async def _identify_distinguishing_factors(self, query_case: Dict, candidate_case: Dict) -> List[str]:
        """Identify distinguishing factors between cases"""
        try:
            factors = []
            
            # Jurisdictional differences
            query_jurisdiction = query_case.get("jurisdiction", "")
            candidate_jurisdiction = candidate_case.get("jurisdiction", "")
            if query_jurisdiction != candidate_jurisdiction:
                factors.append(f"Different jurisdictions: {query_jurisdiction} vs {candidate_jurisdiction}")
            
            # Court level differences
            query_court = query_case.get("court", "")
            candidate_court = candidate_case.get("court", "")
            if query_court and candidate_court and not self._same_court_level(query_court, candidate_court):
                factors.append(f"Different court levels: {self._get_court_level(query_court)} vs {self._get_court_level(candidate_court)}")
            
            # Temporal differences
            if candidate_case.get("date_filed"):
                case_date = self._parse_date(candidate_case["date_filed"])
                if case_date:
                    years_ago = (datetime.utcnow() - case_date).days / 365.0
                    if years_ago > 10:
                        factors.append(f"Case is {years_ago:.0f} years old")
            
            return factors
            
        except Exception:
            return []
    
    async def _calculate_authority_metrics(self, match: PrecedentMatch, candidate_case: Dict):
        """Calculate comprehensive authority metrics"""
        try:
            # Basic authority score
            match.authority_score = await self.similarity_calculator.calculate_authority_weight(candidate_case)
            
            # PageRank-style scoring (simplified)
            citation_count = candidate_case.get("citation_count", 0)
            court_weight = self._get_court_authority_weight(candidate_case.get("court", ""))
            
            match.pagerank_score = (citation_count * 0.7 + court_weight * 0.3) / 100.0
            match.pagerank_score = min(1.0, match.pagerank_score)
            
            # Influence score based on citations and temporal factors
            if candidate_case.get("date_filed"):
                case_date = self._parse_date(candidate_case["date_filed"])
                if case_date:
                    years_ago = (datetime.utcnow() - case_date).days / 365.0
                    temporal_factor = max(0.1, 1.0 - (years_ago * 0.02))  # 2% decay per year
                    match.influence_score = match.pagerank_score * temporal_factor
                else:
                    match.influence_score = match.pagerank_score * 0.5
            else:
                match.influence_score = match.pagerank_score * 0.5
            
        except Exception as e:
            logger.error(f"❌ Error calculating authority metrics: {e}")
    
    def _get_court_authority_weight(self, court: str) -> float:
        """Get authority weight based on court hierarchy"""
        try:
            court_lower = court.lower()
            
            if "supreme" in court_lower:
                return 100.0
            elif "appellate" in court_lower or "circuit" in court_lower:
                return 80.0
            elif "district" in court_lower or "trial" in court_lower:
                return 60.0
            elif "administrative" in court_lower:
                return 40.0
            else:
                return 50.0
                
        except Exception:
            return 50.0
    
    async def _generate_comprehensive_ai_analysis(self, query_case: Dict, candidate_case: Dict, similarity: SimilarityScore) -> str:
        """Generate comprehensive AI analysis of the case match"""
        try:
            if not self.gemini_api_key:
                return "AI analysis not available"
            
            prompt = f"""
            Provide a comprehensive legal analysis of this precedent match:
            
            Query: {query_case.get('facts', '')[:500]}
            Precedent: {candidate_case.get('title', '')} - {candidate_case.get('content', '')[:500]}
            
            Similarity Analysis:
            - Overall: {similarity.overall_similarity:.1%}
            - Factual: {similarity.factual_similarity:.1%}
            - Legal: {similarity.legal_similarity:.1%}
            - Jurisdictional: {similarity.jurisdictional_similarity:.1%}
            - Temporal: {similarity.temporal_similarity:.1%}
            - Authority: {similarity.authority_similarity:.1%}
            
            Provide analysis covering:
            1. Key legal similarities and differences
            2. Precedential value and authority
            3. Applicability to the query scenario
            4. Potential limitations or distinguishing factors
            
            Keep response to 3-4 sentences.
            """
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await asyncio.to_thread(model.generate_content, prompt)
            
            return response.text.strip()[:800]  # Limit length
            
        except Exception as e:
            logger.error(f"❌ Error generating comprehensive AI analysis: {e}")
            return "Comprehensive AI analysis not available"
    
    # Utility methods
    
    def _same_court_level(self, court1: str, court2: str) -> bool:
        """Check if courts are at the same level"""
        level1 = self._get_court_level(court1)
        level2 = self._get_court_level(court2) 
        return level1 == level2
    
    def _get_court_level(self, court: str) -> str:
        """Determine court level from court name"""
        court_lower = court.lower()
        
        if any(keyword in court_lower for keyword in ["supreme", "highest"]):
            return "supreme"
        elif any(keyword in court_lower for keyword in ["appellate", "appeal", "circuit"]):
            return "appellate"
        elif any(keyword in court_lower for keyword in ["district", "trial", "superior"]):
            return "trial"
        else:
            return "unknown"
    
    def _compatible_court_levels(self, court1: str, court2: str) -> bool:
        """Check if court levels are compatible for precedent purposes"""
        level1 = self._get_court_level(court1)
        level2 = self._get_court_level(court2)
        
        # Supreme court decisions are precedential for all lower courts
        if level1 == "supreme" or level2 == "supreme":
            return True
        
        # Appellate decisions are precedential for trial courts
        if (level1 == "appellate" and level2 == "trial") or (level1 == "trial" and level2 == "appellate"):
            return True
        
        return level1 == level2
    
    def _similar_case_type(self, type1: str, type2: str) -> bool:
        """Check if case types are similar"""
        civil_types = ["civil", "contract", "tort", "property", "employment"]
        criminal_types = ["criminal", "felony", "misdemeanor"]
        
        if any(t in type1 for t in civil_types) and any(t in type2 for t in civil_types):
            return True
        if any(t in type1 for t in criminal_types) and any(t in type2 for t in criminal_types):
            return True
        
        return False
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Enhanced date parsing with multiple format support"""
        try:
            # Common date formats in legal data
            formats = [
                "%Y-%m-%d", 
                "%Y-%m-%dT%H:%M:%S", 
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%m/%d/%Y",
                "%B %d, %Y",
                "%Y"
            ]
            
            for fmt in formats:
                try:
                    if fmt == "%Y":
                        year = int(date_str)
                        return datetime(year, 1, 1)
                    else:
                        return datetime.strptime(date_str[:len(fmt.replace('%f', '123456'))], fmt)
                except (ValueError, TypeError):
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _update_performance_metrics(self, processing_time: float, matches_found: int):
        """Update comprehensive performance metrics"""
        try:
            self.performance_metrics["total_matches"] += matches_found
            
            # Update average processing time
            current_avg = self.performance_metrics["average_match_time"]
            total_searches = self.performance_metrics.get("total_searches", 0) + 1
            
            new_avg = ((current_avg * (total_searches - 1)) + processing_time) / total_searches
            self.performance_metrics["average_match_time"] = new_avg
            self.performance_metrics["total_searches"] = total_searches
            
        except Exception as e:
            logger.error(f"❌ Error updating performance metrics: {e}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = {
                "system_status": "operational",
                "performance_metrics": self.performance_metrics,
                "cache_stats": {
                    "similarity_cache_size": len(self.similarity_cache),
                    "principle_cache_size": len(self.principle_cache),
                    "authority_cache_size": len(self.authority_cache)
                },
                "database_stats": {
                    "case_metadata_count": len(self.case_metadata),
                    "faiss_index_available": self.faiss_index is not None,
                    "embeddings_model_available": self.embeddings_model is not None
                },
                "ai_clients": {
                    "gemini_available": self.gemini_api_key is not None,
                    "groq_available": self.groq_client is not None,
                    "courtlistener_available": self.courtlistener_client is not None
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting system stats: {e}")
            return {"error": str(e)}


# Global instance
_precedent_matcher = None

async def get_precedent_matcher() -> PrecedentMatchingSystem:
    """Get initialized precedent matching system"""
    global _precedent_matcher
    
    if _precedent_matcher is None:
        _precedent_matcher = PrecedentMatchingSystem()
        await _precedent_matcher.initialize()
    
    return _precedent_matcher


if __name__ == "__main__":
    # Test the enhanced precedent matching system
    async def test_precedent_matcher():
        matcher = await get_precedent_matcher()
        
        # Test query
        query_case = {
            "facts": "Breach of contract case where vendor failed to deliver goods on time",
            "legal_issues": ["breach of contract", "damages", "specific performance"],
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }
        
        filters = {
            "max_results": 10,
            "min_similarity": 0.6,
            "jurisdiction": "US"
        }
        
        matches = await matcher.find_similar_cases(query_case, filters)
        print(f"Found {len(matches)} precedent matches")
        
        for match in matches[:3]:
            print(f"- {match.case_title}: {match.similarity_scores.overall_similarity:.1%} similarity")
    
    asyncio.run(test_precedent_matcher())