"""
Advanced Risk Assessment Engine - Phase 1
Automated risk scoring system for contract negotiation with multi-dimensional analysis.

Risk Dimensions:
1. Legal Risk - Contract terms, liability exposure, enforceability
2. Financial Risk - Payment terms, penalties, cost implications  
3. Operational Risk - Performance requirements, delivery risks
4. Compliance Risk - Regulatory violations, policy adherence

Features:
- Automated clause-by-clause risk scoring
- Multi-dimensional risk analysis
- Risk aggregation and weighting
- Mitigation recommendations
- Risk trend analysis
"""

import os
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import re
import json

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import google.generativeai as genai
from groq import Groq

logger = logging.getLogger(__name__)

# ==========================
# Risk Assessment Models
# ==========================

class RiskLevel(str, Enum):
    VERY_LOW = "very_low"      # 0-2
    LOW = "low"                # 2-4  
    MEDIUM = "medium"          # 4-6
    HIGH = "high"              # 6-8
    VERY_HIGH = "very_high"    # 8-10

class RiskCategory(str, Enum):
    LEGAL = "legal"
    FINANCIAL = "financial"  
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"

class ClauseType(str, Enum):
    PAYMENT_TERMS = "payment_terms"
    LIABILITY = "liability"
    TERMINATION = "termination"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    PERFORMANCE = "performance"
    DISPUTE_RESOLUTION = "dispute_resolution"
    GOVERNING_LAW = "governing_law"
    FORCE_MAJEURE = "force_majeure"
    INDEMNIFICATION = "indemnification"
    DATA_PROTECTION = "data_protection"
    WARRANTIES = "warranties"

class RiskFactor(BaseModel):
    factor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: RiskCategory
    description: str
    impact_score: float = Field(ge=0, le=10)  # 0-10 scale
    probability_score: float = Field(ge=0, le=10)  # 0-10 scale
    risk_score: float = Field(ge=0, le=10)  # Calculated: (impact * probability) / 10
    severity: RiskLevel
    clause_references: List[str] = Field(default_factory=list)
    mitigation_suggestions: List[str] = Field(default_factory=list)

class ClauseRiskAnalysis(BaseModel):
    clause_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    clause_type: ClauseType
    clause_text: str
    risk_factors: List[RiskFactor] = Field(default_factory=list)
    overall_clause_risk: float = Field(ge=0, le=10)
    primary_risk_category: RiskCategory
    recommendations: List[str] = Field(default_factory=list)
    alternative_language: Optional[str] = None

class DimensionalRiskScore(BaseModel):
    category: RiskCategory
    score: float = Field(ge=0, le=10)
    confidence: float = Field(ge=0, le=1)
    key_factors: List[str] = Field(default_factory=list)
    impact_areas: List[str] = Field(default_factory=list)
    mitigation_priority: str = "medium"  # low, medium, high, critical

class RiskAssessmentInput(BaseModel):
    session_id: str
    contract_text: Optional[str] = None
    document_id: Optional[str] = None
    contract_type: Optional[str] = "general"
    assessment_focus: List[RiskCategory] = Field(default_factory=lambda: list(RiskCategory))
    risk_tolerance: str = "medium"  # conservative, medium, aggressive
    business_context: Optional[Dict[str, Any]] = None

class ComprehensiveRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Overall Risk Metrics
    overall_risk_score: float = Field(ge=0, le=10)
    risk_level: RiskLevel
    confidence_score: float = Field(ge=0, le=1)
    
    # Dimensional Analysis
    dimensional_scores: Dict[str, DimensionalRiskScore]
    
    # Detailed Analysis
    clause_analyses: List[ClauseRiskAnalysis] = Field(default_factory=list)
    high_priority_risks: List[RiskFactor] = Field(default_factory=list)
    
    # Recommendations
    risk_mitigation_plan: List[Dict[str, Any]] = Field(default_factory=list)
    negotiation_priorities: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    
    # Metadata
    contract_type: str = "general"
    assessment_methodology: str = "ai_enhanced_scoring"
    processing_time_seconds: Optional[float] = None

# ==========================
# Risk Assessment Engine
# ==========================

class AdvancedRiskAssessmentEngine:
    """
    Advanced Risk Assessment Engine for contract analysis
    Provides multi-dimensional automated risk scoring
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # AI Configuration
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.groq_api_key = os.environ.get('GROQ_API_KEY') 
        self.emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Risk assessment parameters
        self.risk_weights = {
            RiskCategory.LEGAL: 0.3,
            RiskCategory.FINANCIAL: 0.25,
            RiskCategory.OPERATIONAL: 0.25,
            RiskCategory.COMPLIANCE: 0.2
        }
        
        # Clause pattern library for automated detection
        self.clause_patterns = self._init_clause_patterns()
        
        # Risk scoring matrices
        self.risk_matrices = self._init_risk_matrices()
        
    def _init_ai_clients(self):
        """Initialize AI clients for risk analysis"""
        self.gemini_model = None
        self.groq_client = None
        
        # Try Emergent LLM Key first if available
        if self.emergent_llm_key:
            try:
                from emergentintegrations import LLMClient
                self.llm_client = LLMClient(api_key=self.emergent_llm_key)
                logger.info("✅ Risk Engine: Emergent LLM initialized")
            except Exception as e:
                logger.warning(f"⚠️ Risk Engine: Emergent LLM failed: {e}")
                self.llm_client = None
        
        # Fallback to Gemini
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                logger.info("✅ Risk Engine: Gemini AI initialized")
            except Exception as e:
                logger.warning(f"⚠️ Risk Engine: Gemini failed: {e}")
                
        # Fallback to Groq
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Risk Engine: Groq AI initialized")
            except Exception as e:
                logger.warning(f"⚠️ Risk Engine: Groq failed: {e}")
    
    def _init_clause_patterns(self) -> Dict[ClauseType, List[str]]:
        """Initialize regex patterns for clause detection"""
        return {
            ClauseType.PAYMENT_TERMS: [
                r"payment.*(?:due|terms|schedule)",
                r"net \d+ days?",
                r"invoice.*(?:due|payment)",
                r"late.*(?:fee|penalty|charge)"
            ],
            ClauseType.LIABILITY: [
                r"liabilit(?:y|ies)",
                r"damages?.*(?:limit|cap|exclude)",
                r"consequential.*damages?",
                r"punitive.*damages?",
                r"limitation.*liabilit"
            ],
            ClauseType.TERMINATION: [
                r"terminat(?:e|ion)",
                r"end.*(?:agreement|contract)",
                r"breach.*(?:cure|notice)",
                r"notice.*terminat"
            ],
            ClauseType.INTELLECTUAL_PROPERTY: [
                r"intellectual.*property",
                r"copyright",
                r"trademark",
                r"patent",
                r"proprietary.*(?:information|rights)"
            ],
            ClauseType.CONFIDENTIALITY: [
                r"confidential(?:ity)?",
                r"non.?disclosure",
                r"proprietary.*information",
                r"trade.*secret"
            ],
            ClauseType.PERFORMANCE: [
                r"performance.*(?:standard|requirement|obligation)",
                r"service.*level.*agreement",
                r"SLA",
                r"deliverable"
            ],
            ClauseType.DATA_PROTECTION: [
                r"data.*(?:protection|privacy)",
                r"GDPR",
                r"personal.*(?:data|information)",
                r"privacy.*polic"
            ]
        }
    
    def _init_risk_matrices(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk scoring matrices for different factors"""
        return {
            "legal_factors": {
                "vague_termination": {"impact": 7, "probability": 6},
                "unlimited_liability": {"impact": 9, "probability": 4},
                "weak_ip_protection": {"impact": 8, "probability": 5},
                "ambiguous_performance": {"impact": 6, "probability": 7},
                "unfavorable_jurisdiction": {"impact": 5, "probability": 8}
            },
            "financial_factors": {
                "extended_payment_terms": {"impact": 6, "probability": 5},
                "high_late_fees": {"impact": 7, "probability": 4},
                "no_payment_protection": {"impact": 8, "probability": 3},
                "currency_exposure": {"impact": 5, "probability": 6},
                "uncapped_penalties": {"impact": 9, "probability": 3}
            },
            "operational_factors": {
                "unrealistic_deadlines": {"impact": 7, "probability": 7},
                "inadequate_resources": {"impact": 8, "probability": 5},
                "scope_creep_risk": {"impact": 6, "probability": 8},
                "dependency_risks": {"impact": 7, "probability": 6},
                "quality_standards_unclear": {"impact": 5, "probability": 7}
            },
            "compliance_factors": {
                "data_protection_gaps": {"impact": 8, "probability": 6},
                "regulatory_non_compliance": {"impact": 9, "probability": 4},
                "audit_requirements_missing": {"impact": 6, "probability": 5},
                "reporting_obligations_unclear": {"impact": 5, "probability": 7},
                "certification_requirements": {"impact": 7, "probability": 4}
            }
        }

    async def initialize_collections(self):
        """Initialize MongoDB collections for risk assessments"""
        try:
            # Risk assessments
            await self.db.risk_assessments.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.risk_assessments.create_index([("overall_risk_score", -1)])
            await self.db.risk_assessments.create_index([("risk_level", 1)])
            
            # Risk factors
            await self.db.risk_factors.create_index([("assessment_id", 1)])
            await self.db.risk_factors.create_index([("category", 1), ("risk_score", -1)])
            
            # Risk mitigation tracking
            await self.db.risk_mitigations.create_index([("session_id", 1)])
            await self.db.risk_mitigations.create_index([("status", 1)])
            
            logger.info("✅ Risk Assessment Engine: Collections initialized")
        except Exception as e:
            logger.error(f"❌ Risk Assessment Engine init error: {e}")

    async def assess_contract_risk(self, input_data: RiskAssessmentInput) -> ComprehensiveRiskAssessment:
        """
        Main entry point for comprehensive contract risk assessment
        """
        start_time = datetime.utcnow()
        logger.info(f"🔍 Starting risk assessment for session: {input_data.session_id}")
        
        try:
            # Get contract text
            contract_text = await self._get_contract_text(input_data)
            if not contract_text:
                raise ValueError("No contract text available for analysis")
            
            # Extract and analyze clauses
            clauses = await self._extract_clauses(contract_text)
            clause_analyses = await self._analyze_clauses(clauses, input_data.contract_type)
            
            # Calculate dimensional risk scores
            dimensional_scores = await self._calculate_dimensional_risks(clause_analyses, contract_text, input_data)
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk(dimensional_scores)
            risk_level = self._determine_risk_level(overall_risk_score)
            
            # Identify high-priority risks
            high_priority_risks = self._identify_high_priority_risks(clause_analyses)
            
            # Generate mitigation plan
            mitigation_plan = await self._generate_mitigation_plan(dimensional_scores, high_priority_risks, input_data)
            
            # Generate negotiation priorities
            negotiation_priorities = self._generate_negotiation_priorities(dimensional_scores, high_priority_risks)
            
            # Identify red flags
            red_flags = self._identify_red_flags(clause_analyses, dimensional_scores)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(clause_analyses, dimensional_scores)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create comprehensive assessment
            assessment = ComprehensiveRiskAssessment(
                session_id=input_data.session_id,
                overall_risk_score=round(overall_risk_score, 2),
                risk_level=risk_level,
                confidence_score=round(confidence_score, 2),
                dimensional_scores={cat.value: score for cat, score in dimensional_scores.items()},
                clause_analyses=clause_analyses,
                high_priority_risks=high_priority_risks,
                risk_mitigation_plan=mitigation_plan,
                negotiation_priorities=negotiation_priorities,
                red_flags=red_flags,
                contract_type=input_data.contract_type or "general",
                processing_time_seconds=round(processing_time, 2)
            )
            
            # Store assessment
            await self._store_assessment(assessment)
            
            logger.info(f"✅ Risk assessment completed: {assessment.assessment_id} (Risk: {risk_level.value}, Score: {overall_risk_score:.2f})")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {e}")
            raise

    async def _get_contract_text(self, input_data: RiskAssessmentInput) -> Optional[str]:
        """Get contract text from input or document ID"""
        if input_data.contract_text:
            return input_data.contract_text
        
        if input_data.document_id:
            try:
                # Try to get from document analysis
                doc = await self.db.document_analyses.find_one({"document_id": input_data.document_id})
                if doc and doc.get("extracted_text"):
                    return doc["extracted_text"]
                
                # Try to get from uploaded documents
                doc = await self.db.uploaded_documents.find_one({"document_id": input_data.document_id})
                if doc and doc.get("content"):
                    return doc["content"]
            except Exception as e:
                logger.warning(f"⚠️ Failed to retrieve document {input_data.document_id}: {e}")
        
        return None

    async def _extract_clauses(self, contract_text: str) -> List[Dict[str, Any]]:
        """Extract and categorize contract clauses"""
        clauses = []
        
        # Split contract into sections/paragraphs
        sections = self._split_into_sections(contract_text)
        
        for i, section in enumerate(sections):
            if len(section.strip()) < 50:  # Skip very short sections
                continue
                
            clause_type = self._classify_clause(section)
            clauses.append({
                "clause_id": str(uuid.uuid4()),
                "clause_type": clause_type,
                "text": section.strip(),
                "position": i,
                "word_count": len(section.split())
            })
        
        return clauses

    def _split_into_sections(self, text: str) -> List[str]:
        """Split contract text into logical sections"""
        # Split on common section delimiters
        sections = re.split(r'\n\s*\n|\n\d+\.|\n[A-Z]+\.|Article\s+\d+|Section\s+\d+', text)
        return [s.strip() for s in sections if s.strip()]

    def _classify_clause(self, clause_text: str) -> ClauseType:
        """Classify clause type using pattern matching"""
        clause_lower = clause_text.lower()
        
        for clause_type, patterns in self.clause_patterns.items():
            for pattern in patterns:
                if re.search(pattern, clause_lower):
                    return clause_type
        
        return ClauseType.PERFORMANCE  # Default fallback

    async def _analyze_clauses(self, clauses: List[Dict[str, Any]], contract_type: str) -> List[ClauseRiskAnalysis]:
        """Analyze risk factors for each clause"""
        analyses = []
        
        for clause in clauses:
            try:
                analysis = await self._analyze_single_clause(clause, contract_type)
                analyses.append(analysis)
            except Exception as e:
                logger.warning(f"⚠️ Failed to analyze clause {clause['clause_id']}: {e}")
        
        return analyses

    async def _analyze_single_clause(self, clause: Dict[str, Any], contract_type: str) -> ClauseRiskAnalysis:
        """Analyze a single clause for risk factors"""
        clause_type = clause["clause_type"]
        clause_text = clause["text"]
        
        # Identify risk factors using AI and pattern matching
        risk_factors = await self._identify_clause_risk_factors(clause_text, clause_type, contract_type)
        
        # Calculate overall clause risk
        if risk_factors:
            overall_risk = sum(rf.risk_score for rf in risk_factors) / len(risk_factors)
        else:
            overall_risk = 3.0  # Default medium-low risk
        
        # Determine primary risk category
        primary_category = self._determine_primary_risk_category(risk_factors, clause_type)
        
        # Generate recommendations
        recommendations = await self._generate_clause_recommendations(clause_text, clause_type, risk_factors)
        
        # Generate alternative language if high risk
        alternative_language = None
        if overall_risk >= 6.0:
            alternative_language = await self._generate_alternative_language(clause_text, clause_type)
        
        return ClauseRiskAnalysis(
            clause_id=clause["clause_id"],
            clause_type=clause_type,
            clause_text=clause_text,
            risk_factors=risk_factors,
            overall_clause_risk=round(overall_risk, 2),
            primary_risk_category=primary_category,
            recommendations=recommendations,
            alternative_language=alternative_language
        )

    async def _identify_clause_risk_factors(self, clause_text: str, clause_type: ClauseType, contract_type: str) -> List[RiskFactor]:
        """Identify risk factors in a clause using AI analysis"""
        try:
            prompt = f"""
            Analyze this contract clause for risk factors across these dimensions:
            1. Legal Risk - enforceability, ambiguity, unfavorable terms
            2. Financial Risk - cost implications, payment risks, penalties  
            3. Operational Risk - performance issues, delivery risks
            4. Compliance Risk - regulatory violations, policy gaps
            
            Clause Type: {clause_type.value}
            Contract Type: {contract_type}
            
            Clause Text: "{clause_text}"
            
            For each significant risk factor found, provide:
            - Risk category (legal/financial/operational/compliance)
            - Description of the risk
            - Impact score (1-10, where 10 is highest impact)
            - Probability score (1-10, where 10 is most likely)
            - Specific mitigation suggestions
            
            Focus on concrete, actionable risks. Return in JSON format:
            [
                {{
                    "category": "legal|financial|operational|compliance",
                    "description": "Clear description of the risk",
                    "impact_score": 7,
                    "probability_score": 5,
                    "mitigation_suggestions": ["Suggestion 1", "Suggestion 2"]
                }}
            ]
            """
            
            ai_response = await self._get_ai_response(prompt)
            
            # Parse AI response
            risk_factors = []
            try:
                factors_data = json.loads(ai_response)
                
                for factor_data in factors_data:
                    impact = float(factor_data.get("impact_score", 5))
                    probability = float(factor_data.get("probability_score", 5))
                    risk_score = (impact * probability) / 10
                    
                    risk_factor = RiskFactor(
                        category=RiskCategory(factor_data["category"]),
                        description=factor_data["description"],
                        impact_score=impact,
                        probability_score=probability,
                        risk_score=risk_score,
                        severity=self._determine_risk_level(risk_score),
                        clause_references=[clause_text[:100] + "..."],
                        mitigation_suggestions=factor_data.get("mitigation_suggestions", [])
                    )
                    risk_factors.append(risk_factor)
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"⚠️ Failed to parse AI risk analysis: {e}")
                # Fallback to pattern-based analysis
                risk_factors = self._pattern_based_risk_analysis(clause_text, clause_type)
            
            return risk_factors
            
        except Exception as e:
            logger.warning(f"⚠️ Risk factor identification failed: {e}")
            return self._pattern_based_risk_analysis(clause_text, clause_type)

    def _pattern_based_risk_analysis(self, clause_text: str, clause_type: ClauseType) -> List[RiskFactor]:
        """Fallback pattern-based risk analysis when AI is unavailable"""
        risk_factors = []
        clause_lower = clause_text.lower()
        
        # High-risk patterns
        high_risk_patterns = {
            "unlimited liability": {"category": RiskCategory.LEGAL, "impact": 9, "prob": 4},
            "no cure period": {"category": RiskCategory.LEGAL, "impact": 7, "prob": 6},
            "immediate termination": {"category": RiskCategory.OPERATIONAL, "impact": 8, "prob": 5},
            "all damages": {"category": RiskCategory.FINANCIAL, "impact": 8, "prob": 4},
            "personal guarantee": {"category": RiskCategory.FINANCIAL, "impact": 9, "prob": 3},
            "indefinite term": {"category": RiskCategory.LEGAL, "impact": 6, "prob": 7},
            "exclusive jurisdiction": {"category": RiskCategory.LEGAL, "impact": 5, "prob": 8}
        }
        
        for pattern, risk_data in high_risk_patterns.items():
            if pattern in clause_lower:
                risk_score = (risk_data["impact"] * risk_data["prob"]) / 10
                
                risk_factor = RiskFactor(
                    category=risk_data["category"],
                    description=f"Clause contains {pattern} which creates significant risk",
                    impact_score=risk_data["impact"],
                    probability_score=risk_data["prob"],
                    risk_score=risk_score,
                    severity=self._determine_risk_level(risk_score),
                    clause_references=[clause_text[:100] + "..."],
                    mitigation_suggestions=[f"Consider negotiating modification to {pattern} clause"]
                )
                risk_factors.append(risk_factor)
        
        return risk_factors

    def _determine_primary_risk_category(self, risk_factors: List[RiskFactor], clause_type: ClauseType) -> RiskCategory:
        """Determine the primary risk category for a clause"""
        if not risk_factors:
            # Default based on clause type
            clause_category_map = {
                ClauseType.PAYMENT_TERMS: RiskCategory.FINANCIAL,
                ClauseType.LIABILITY: RiskCategory.LEGAL,
                ClauseType.PERFORMANCE: RiskCategory.OPERATIONAL,
                ClauseType.DATA_PROTECTION: RiskCategory.COMPLIANCE
            }
            return clause_category_map.get(clause_type, RiskCategory.LEGAL)
        
        # Find category with highest total risk score
        category_scores = {}
        for rf in risk_factors:
            if rf.category not in category_scores:
                category_scores[rf.category] = 0
            category_scores[rf.category] += rf.risk_score
        
        return max(category_scores, key=category_scores.get)

    async def _calculate_dimensional_risks(self, clause_analyses: List[ClauseRiskAnalysis], 
                                         contract_text: str, input_data: RiskAssessmentInput) -> Dict[RiskCategory, DimensionalRiskScore]:
        """Calculate risk scores for each dimension"""
        dimensional_scores = {}
        
        for category in RiskCategory:
            # Collect all risk factors for this category
            category_risks = []
            for analysis in clause_analyses:
                category_risks.extend([rf for rf in analysis.risk_factors if rf.category == category])
            
            if category_risks:
                # Calculate weighted average risk score
                total_weight = sum(rf.risk_score * (rf.impact_score / 10) for rf in category_risks)
                total_factors = len(category_risks)
                avg_score = total_weight / total_factors if total_factors > 0 else 3.0
                
                # Calculate confidence based on number of factors and AI availability
                confidence = min(0.95, 0.6 + (total_factors * 0.1))
                
                # Extract key factors and impact areas
                key_factors = [rf.description for rf in sorted(category_risks, key=lambda x: x.risk_score, reverse=True)[:3]]
                impact_areas = list(set([rf.description.split()[0] for rf in category_risks]))
                
                # Determine mitigation priority
                max_risk = max(rf.risk_score for rf in category_risks)
                if max_risk >= 8:
                    priority = "critical"
                elif max_risk >= 6:
                    priority = "high"
                elif max_risk >= 4:
                    priority = "medium"
                else:
                    priority = "low"
            else:
                # No specific risks found, use baseline score
                avg_score = 2.5
                confidence = 0.4
                key_factors = [f"No significant {category.value} risks identified"]
                impact_areas = []
                priority = "low"
            
            dimensional_scores[category] = DimensionalRiskScore(
                category=category,
                score=round(avg_score, 2),
                confidence=round(confidence, 2),
                key_factors=key_factors,
                impact_areas=impact_areas[:5],  # Top 5 impact areas
                mitigation_priority=priority
            )
        
        return dimensional_scores

    def _calculate_overall_risk(self, dimensional_scores: Dict[RiskCategory, DimensionalRiskScore]) -> float:
        """Calculate overall weighted risk score"""
        weighted_sum = 0
        total_weight = 0
        
        for category, score_obj in dimensional_scores.items():
            weight = self.risk_weights.get(category, 0.25)
            confidence_adjusted_score = score_obj.score * score_obj.confidence
            weighted_sum += confidence_adjusted_score * weight
            total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 3.0
        return round(overall_score, 2)

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from numerical score"""
        if risk_score <= 2:
            return RiskLevel.VERY_LOW
        elif risk_score <= 4:
            return RiskLevel.LOW
        elif risk_score <= 6:
            return RiskLevel.MEDIUM
        elif risk_score <= 8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    def _identify_high_priority_risks(self, clause_analyses: List[ClauseRiskAnalysis]) -> List[RiskFactor]:
        """Identify high-priority risks requiring immediate attention"""
        all_risks = []
        for analysis in clause_analyses:
            all_risks.extend(analysis.risk_factors)
        
        # Sort by risk score and filter high-priority
        high_priority = [rf for rf in all_risks if rf.risk_score >= 6.0]
        high_priority.sort(key=lambda x: x.risk_score, reverse=True)
        
        return high_priority[:10]  # Top 10 high-priority risks

    async def _generate_mitigation_plan(self, dimensional_scores: Dict[RiskCategory, DimensionalRiskScore], 
                                      high_priority_risks: List[RiskFactor], 
                                      input_data: RiskAssessmentInput) -> List[Dict[str, Any]]:
        """Generate comprehensive risk mitigation plan"""
        mitigation_plan = []
        
        # Address high-priority risks first
        for i, risk in enumerate(high_priority_risks[:5]):  # Top 5 risks
            plan_item = {
                "priority": i + 1,
                "risk_id": risk.factor_id,
                "risk_description": risk.description,
                "category": risk.category.value,
                "risk_score": risk.risk_score,
                "mitigation_actions": risk.mitigation_suggestions[:3],  # Top 3 suggestions
                "timeline": "immediate" if risk.risk_score >= 8 else "short_term",
                "responsible_party": "legal_team" if risk.category == RiskCategory.LEGAL else "business_team",
                "success_metrics": [f"Reduce {risk.category.value} risk score below 4.0"]
            }
            mitigation_plan.append(plan_item)
        
        # Add dimensional mitigation strategies
        for category, dim_score in dimensional_scores.items():
            if dim_score.mitigation_priority in ["high", "critical"]:
                plan_item = {
                    "priority": len(mitigation_plan) + 1,
                    "risk_id": f"dimensional_{category.value}",
                    "risk_description": f"Overall {category.value} risk management",
                    "category": category.value,
                    "risk_score": dim_score.score,
                    "mitigation_actions": [
                        f"Comprehensive review of all {category.value} related clauses",
                        f"Implement {category.value} risk monitoring procedures",
                        f"Negotiate improved {category.value} protections"
                    ],
                    "timeline": "medium_term",
                    "responsible_party": "cross_functional_team",
                    "success_metrics": [f"Achieve {category.value} risk score below 4.0"]
                }
                mitigation_plan.append(plan_item)
        
        return mitigation_plan

    def _generate_negotiation_priorities(self, dimensional_scores: Dict[RiskCategory, DimensionalRiskScore], 
                                       high_priority_risks: List[RiskFactor]) -> List[str]:
        """Generate prioritized list of negotiation points"""
        priorities = []
        
        # Add high-impact risk areas
        for risk in high_priority_risks[:3]:
            if risk.risk_score >= 7:
                priorities.append(f"Address {risk.category.value} risk: {risk.description}")
        
        # Add dimensional priorities based on scores
        sorted_dimensions = sorted(dimensional_scores.items(), key=lambda x: x[1].score, reverse=True)
        
        for category, score in sorted_dimensions:
            if score.score >= 6 and score.mitigation_priority in ["high", "critical"]:
                priorities.append(f"Strengthen {category.value} protections (Current risk: {score.score}/10)")
        
        # Add standard negotiation priorities
        standard_priorities = [
            "Review and cap liability exposure",
            "Clarify performance standards and deliverables", 
            "Ensure adequate termination rights",
            "Protect intellectual property rights",
            "Include compliance and audit provisions"
        ]
        
        # Merge and deduplicate
        all_priorities = priorities + [p for p in standard_priorities if p not in priorities]
        
        return all_priorities[:8]  # Top 8 priorities

    def _identify_red_flags(self, clause_analyses: List[ClauseRiskAnalysis], 
                           dimensional_scores: Dict[RiskCategory, DimensionalRiskScore]) -> List[str]:
        """Identify critical red flags requiring immediate attention"""
        red_flags = []
        
        # Critical risk factors
        for analysis in clause_analyses:
            for risk in analysis.risk_factors:
                if risk.risk_score >= 8:
                    red_flags.append(f"CRITICAL: {risk.description} (Risk Score: {risk.risk_score:.1f})")
        
        # Dimensional red flags
        for category, score in dimensional_scores.items():
            if score.score >= 8:
                red_flags.append(f"HIGH {category.value.upper()} RISK: Score {score.score}/10 requires immediate attention")
        
        # Pattern-based red flags
        critical_patterns = [
            "No liability limitations found",
            "Unlimited indemnification obligations", 
            "Immediate termination without cure period",
            "Personal guarantees required",
            "Exclusive jurisdiction in unfavorable location"
        ]
        
        # Add pattern-based flags if relevant
        for analysis in clause_analyses:
            clause_text = analysis.clause_text.lower()
            for pattern in critical_patterns:
                if any(keyword in clause_text for keyword in pattern.lower().split()):
                    if pattern not in red_flags:
                        red_flags.append(pattern)
        
        return red_flags[:10]  # Top 10 red flags

    def _calculate_confidence_score(self, clause_analyses: List[ClauseRiskAnalysis], 
                                   dimensional_scores: Dict[RiskCategory, DimensionalRiskScore]) -> float:
        """Calculate overall confidence in the risk assessment"""
        factors = []
        
        # AI availability factor
        if hasattr(self, 'llm_client') and self.llm_client:
            ai_factor = 0.9
        elif self.gemini_model:
            ai_factor = 0.85
        elif self.groq_client:
            ai_factor = 0.8
        else:
            ai_factor = 0.6  # Pattern-based only
        
        factors.append(ai_factor)
        
        # Analysis completeness factor
        if clause_analyses:
            completeness = min(0.95, 0.5 + (len(clause_analyses) * 0.05))
            factors.append(completeness)
        else:
            factors.append(0.3)
        
        # Dimensional coverage factor
        avg_dim_confidence = sum(score.confidence for score in dimensional_scores.values()) / len(dimensional_scores)
        factors.append(avg_dim_confidence)
        
        # Calculate weighted average
        return sum(factors) / len(factors)

    async def _generate_clause_recommendations(self, clause_text: str, clause_type: ClauseType, 
                                             risk_factors: List[RiskFactor]) -> List[str]:
        """Generate specific recommendations for improving a clause"""
        recommendations = []
        
        # Extract suggestions from risk factors
        for risk in risk_factors:
            recommendations.extend(risk.mitigation_suggestions)
        
        # Add clause-type specific recommendations
        type_specific = {
            ClauseType.LIABILITY: [
                "Consider adding liability caps",
                "Exclude consequential damages",
                "Include mutual indemnification"
            ],
            ClauseType.PAYMENT_TERMS: [
                "Clarify payment schedule milestones",
                "Include early payment discounts",
                "Add late payment penalties"
            ],
            ClauseType.TERMINATION: [
                "Include cure periods for breaches",
                "Clarify termination for convenience",
                "Define post-termination obligations"
            ]
        }
        
        if clause_type in type_specific:
            recommendations.extend(type_specific[clause_type])
        
        # Remove duplicates and limit
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:5]

    async def _generate_alternative_language(self, clause_text: str, clause_type: ClauseType) -> Optional[str]:
        """Generate alternative clause language for high-risk clauses"""
        try:
            prompt = f"""
            The following {clause_type.value} clause has been identified as high-risk. 
            Please provide alternative language that reduces risk while maintaining the core business intent:
            
            Original Clause: "{clause_text}"
            
            Provide improved language that:
            1. Reduces legal and financial risk
            2. Maintains business functionality  
            3. Uses clear, unambiguous terms
            4. Follows standard contract practices
            
            Return only the improved clause text, not explanations.
            """
            
            alternative = await self._get_ai_response(prompt)
            return alternative.strip() if alternative else None
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to generate alternative language: {e}")
            return None

    async def _get_ai_response(self, prompt: str) -> str:
        """Get AI response using available models with fallback chain"""
        try:
            # Try Emergent LLM first
            if hasattr(self, 'llm_client') and self.llm_client:
                try:
                    response = await asyncio.to_thread(
                        self.llm_client.generate,
                        prompt=prompt,
                        model="gpt-4o",
                        max_tokens=2000,
                        temperature=0.1
                    )
                    return response.get('content', '')
                except Exception as e:
                    logger.warning(f"⚠️ Emergent LLM failed: {e}, trying Gemini")
            
            # Try Gemini
            if self.gemini_model:
                try:
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        prompt
                    )
                    return response.text
                except Exception as e:
                    logger.warning(f"⚠️ Gemini failed: {e}, trying Groq")
            
            # Try Groq
            if self.groq_client:
                response = await asyncio.to_thread(
                    self.groq_client.chat.completions.create,
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            raise Exception("No AI models available")
            
        except Exception as e:
            logger.error(f"❌ AI response failed: {e}")
            return "AI analysis temporarily unavailable. Please review manually."

    async def _store_assessment(self, assessment: ComprehensiveRiskAssessment):
        """Store risk assessment in database"""
        try:
            assessment_doc = assessment.model_dump()
            await self.db.risk_assessments.insert_one(assessment_doc)
            
            # Store individual risk factors for easier querying
            for clause_analysis in assessment.clause_analyses:
                for risk_factor in clause_analysis.risk_factors:
                    risk_doc = risk_factor.model_dump()
                    risk_doc["assessment_id"] = assessment.assessment_id
                    risk_doc["clause_id"] = clause_analysis.clause_id
                    await self.db.risk_factors.insert_one(risk_doc)
            
            logger.info(f"✅ Risk assessment stored: {assessment.assessment_id}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to store risk assessment: {e}")

# ==========================
# Global Instance Management
# ==========================

_risk_engine: Optional[AdvancedRiskAssessmentEngine] = None

async def get_risk_assessment_engine(db: AsyncIOMotorDatabase) -> AdvancedRiskAssessmentEngine:
    """Get or create risk assessment engine instance"""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = AdvancedRiskAssessmentEngine(db)
        await _risk_engine.initialize_collections()
        logger.info("🚀 Advanced Risk Assessment Engine initialized")
    return _risk_engine