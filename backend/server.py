from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import os
import logging
from dataclasses import asdict

# Existing imports and initializations above ...

# ================================
# ADVANCED LEGAL RESEARCH ENGINE API ENDPOINTS
# ================================

# Initialize Advanced Legal Research Engine components
try:
    from advanced_legal_research_engine import get_research_engine
    from precedent_matching_system import get_precedent_matcher
    from citation_network_analyzer import CitationNetworkAnalyzer
    from research_memo_generator import ResearchMemoGenerator
    from legal_argument_structurer import LegalArgumentStructurer
    from multi_jurisdiction_search import MultiJurisdictionSearch
    from research_quality_scorer import get_quality_scorer
    ADVANCED_RESEARCH_ENGINE_AVAILABLE = True
    logger.info("✅ Advanced Legal Research Engine modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Advanced Legal Research Engine not fully available: {e}")
    ADVANCED_RESEARCH_ENGINE_AVAILABLE = False

# ... existing models above ...

@api_router.post("/legal-research-engine/research", response_model=ResearchResultResponse)
async def coordinate_legal_research(request: ResearchQueryRequest):
    """
    Main Advanced Legal Research Engine endpoint - coordinates comprehensive research
    across all components (precedent matching, citation analysis, memo generation, etc.)
    """
    try:
        if not ADVANCED_RESEARCH_ENGINE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Advanced Legal Research Engine not available")
        
        logger.info(f"🔍 Starting comprehensive legal research: {request.research_type}")
        
        # Get the research engine
        engine = await get_research_engine()
        
        # Create research query from request
        from advanced_legal_research_engine import ResearchQuery, ResearchType, ResearchPriority
        
        research_query = ResearchQuery(
            query_text=request.query_text,
            research_type=ResearchType(request.research_type),
            jurisdiction=request.jurisdiction,
            legal_domain=request.legal_domain,
            priority=ResearchPriority(request.priority),
            court_level=request.court_level,
            date_range=request.date_range,
            case_type=request.case_type,
            legal_issues=request.legal_issues,
            max_results=request.max_results,
            min_confidence=request.min_confidence,
            include_analysis=request.include_analysis,
            cache_results=request.cache_results,
            user_context=request.user_context
        )
        
        # Execute comprehensive research
        result = await engine.coordinate_research(research_query)
        
        # Store research session in database - convert enums to strings for serialization
        def serialize_enums(obj):
            """Recursively convert enum objects to strings for MongoDB serialization"""
            if isinstance(obj, dict):
                return {key: serialize_enums(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [serialize_enums(item) for item in obj]
            elif hasattr(obj, '__dict__') and hasattr(obj, 'value'):
                # This is an enum, return its value
                return obj.value
            elif hasattr(obj, '__dict__'):
                # This is a dataclass or similar object, convert to dict and recurse
                return serialize_enums(asdict(obj))
            else:
                return obj
        
        research_doc = serialize_enums(asdict(result))
        research_doc["_id"] = result.id
        await db.legal_research_queries.insert_one(research_doc)
        
        logger.info(f"✅ Research completed: {result.sources_count} sources, confidence: {result.confidence_score:.2f}")
        
        # Convert result to response format
        precedent_matches = []
        for match in result.precedent_matches:
            if isinstance(match, dict):
                # Convert dict to PrecedentMatchResponse format
                precedent_matches.append(PrecedentMatchResponse(
                    case_id=match.get("case_id", ""),
                    case_title=match.get("case_title", ""),
                    citation=match.get("citation", ""),
                    court=match.get("court", ""),
                    jurisdiction=match.get("jurisdiction", ""),
                    decision_date=match.get("decision_date"),
                    case_summary=match.get("case_summary", ""),
                    legal_issues=match.get("legal_issues", []),
                    holdings=match.get("holdings", []),
                    key_facts=match.get("key_facts", []),
                    similarity_scores=SimilarityScoreResponse(
                        factual_similarity=match.get("similarity_scores", {}).get("factual_similarity", 0.0),
                        legal_similarity=match.get("similarity_scores", {}).get("legal_similarity", 0.0),
                        procedural_similarity=match.get("similarity_scores", {}).get("procedural_similarity", 0.0),
                        jurisdictional_similarity=match.get("similarity_scores", {}).get("jurisdictional_similarity", 0.0),
                        temporal_similarity=match.get("similarity_scores", {}).get("temporal_similarity", 0.0),
                        overall_similarity=match.get("similarity_scores", {}).get("overall_similarity", 0.0),
                        confidence_score=match.get("similarity_scores", {}).get("confidence_score", 0.0)
                    ),
                    match_type=match.get("match_type", "moderately_similar"),
                    relevance_score=match.get("relevance_score", 0.0),
                    extracted_principles=[],
                    citation_count=match.get("citation_count", 0),
                    authority_score=match.get("authority_score", 0.0),
                    match_reasoning=match.get("match_reasoning", ""),
                    distinguishing_factors=match.get("distinguishing_factors", []),
                    supporting_quotes=match.get("supporting_quotes", []),
                    created_at=match.get("created_at", datetime.utcnow())
                ))
        
        return ResearchResultResponse(
            id=result.id,
            query_id=result.query_id,
            research_type=result.research_type.value,
            results=result.results,
            precedent_matches=precedent_matches,
            citation_network=result.citation_network,
            generated_memo=result.generated_memo,
            legal_arguments=result.legal_arguments,
            confidence_score=result.confidence_score,
            completeness_score=result.completeness_score,
            authority_score=result.authority_score,
            processing_time=result.processing_time,
            models_used=result.models_used,
            sources_count=result.sources_count,
            status=result.status.value,
            created_at=result.created_at,
            updated_at=result.updated_at,
            expires_at=result.expires_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in comprehensive legal research: {e}")
        raise HTTPException(status_code=500, detail=f"Error conducting research: {str(e)}")

@api_router.post("/legal-research-engine/precedent-search", response_model=List[PrecedentMatchResponse])
async def search_precedents(request: PrecedentSearchRequest):
    """AI-powered precedent matching with multi-dimensional similarity analysis"""
    try:
        if not ADVANCED_RESEARCH_ENGINE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Precedent matching system not available")
        
        logger.info("🔍 Starting precedent search...")
        
        # Get precedent matcher
        matcher = await get_precedent_matcher()
        
        # Execute precedent search
        matches = await matcher.find_similar_cases(
            query_case=request.query_case,
            filters=request.filters
        )
        
        # Convert to response format
        response_matches = []
        for match in matches:
            response_matches.append(PrecedentMatchResponse(
                case_id=match.case_id,
                case_title=match.case_title,
                citation=match.citation,
                court=match.court,
                jurisdiction=match.jurisdiction,
                decision_date=match.decision_date,
                case_summary=match.case_summary,
                legal_issues=match.legal_issues,
                holdings=match.holdings,
                key_facts=match.key_facts,
                similarity_scores=SimilarityScoreResponse(
                    factual_similarity=match.similarity_scores.factual_similarity,
                    legal_similarity=match.similarity_scores.legal_similarity,
                    procedural_similarity=match.similarity_scores.procedural_similarity,
                    jurisdictional_similarity=match.similarity_scores.jurisdictional_similarity,
                    temporal_similarity=match.similarity_scores.temporal_similarity,
                    overall_similarity=match.similarity_scores.overall_similarity,
                    confidence_score=match.similarity_scores.confidence_score
                ),
                match_type=match.match_type.value,
                relevance_score=match.relevance_score,
                extracted_principles=[
                    LegalPrincipleResponse(
                        id=principle.id,
                        principle_text=principle.principle_text,
                        legal_domain=principle.legal_domain,
                        authority_level=(principle.authority_level.value if hasattr(principle.authority_level, 'value') else str(principle.authority_level)),
                        jurisdiction=principle.jurisdiction,
                        source_case=(getattr(principle, 'source_case_id', '') or ''),
                        confidence_score=principle.confidence_score,
                        supporting_citations=principle.supporting_citations,
                        created_at=principle.created_at
                    ) for principle in match.extracted_principles
                ],
                citation_count=match.citation_count,
                authority_score=match.authority_score,
                match_reasoning=match.match_reasoning,
                distinguishing_factors=match.distinguishing_factors,
                supporting_quotes=match.supporting_quotes,
                created_at=match.created_at
            ))
        
        logger.info(f"✅ Found {len(response_matches)} precedent matches")
        return response_matches
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in precedent search: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching precedents: {str(e)}")

# ... rest of file remains unchanged ...