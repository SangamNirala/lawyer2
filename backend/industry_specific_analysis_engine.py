"""
Industry-Specific Analysis Engine - Step 3 Implementation
Enhanced Contract Negotiation Agent - Industry-Specific Analysis

Provides specialized contract analysis for:
- Healthcare contracts (medical services, BAAs, telemedicine, pharmaceutical)
- Financial services (investment, loan, banking, fintech partnerships)
- Technology/SaaS (software licenses, data processing, API, cloud services)
- Manufacturing (supply chain, distribution, OEM, quality assurance)

Features per industry:
- Industry-specific clauses and templates
- Risk factors and mitigation strategies
- Negotiation strategies and tactics
- Compliance requirements
- Market benchmarks and standards
- Common pitfalls and best practices
"""

import os
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
import json

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

# Optional AI clients (opportunistic)
try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    from groq import Groq
except Exception:
    Groq = None

logger = logging.getLogger(__name__)

# ==========================
# Industry-Specific Models
# ==========================

class IndustryType(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"

class ContractCategory(str, Enum):
    # Healthcare
    MEDICAL_SERVICES = "medical_services"
    BUSINESS_ASSOCIATE_AGREEMENT = "business_associate_agreement"
    TELEMEDICINE = "telemedicine"
    PHARMACEUTICAL = "pharmaceutical"
    MEDICAL_DEVICE = "medical_device"
    
    # Financial
    INVESTMENT_AGREEMENT = "investment_agreement"
    LOAN_CONTRACT = "loan_contract"
    BANKING_SERVICES = "banking_services"
    FINTECH_PARTNERSHIP = "fintech_partnership"
    PAYMENT_PROCESSING = "payment_processing"
    INSURANCE = "insurance"
    
    # Technology
    SOFTWARE_LICENSE = "software_license"
    DATA_PROCESSING_AGREEMENT = "data_processing_agreement"
    API_AGREEMENT = "api_agreement"
    CLOUD_SERVICES = "cloud_services"
    AI_ML_CONTRACT = "ai_ml_contract"
    SaaS_AGREEMENT = "saas_agreement"
    
    # Manufacturing
    SUPPLY_CHAIN = "supply_chain"
    DISTRIBUTION_AGREEMENT = "distribution_agreement"
    OEM_AGREEMENT = "oem_agreement"
    QUALITY_ASSURANCE = "quality_assurance"
    MANUFACTURING_SERVICES = "manufacturing_services"
    PROCUREMENT = "procurement"

class RiskCategory(str, Enum):
    REGULATORY = "regulatory"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    LEGAL = "legal"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"
    MARKET = "market"

class NegotiationTactic(str, Enum):
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    DEFENSIVE = "defensive"
    VALUE_BASED = "value_based"
    RELATIONSHIP_FOCUSED = "relationship_focused"
    TECHNICAL_FOCUSED = "technical_focused"

# ==========================
# Data Models
# ==========================

class IndustryClause(BaseModel):
    clause_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    template_text: str
    mandatory: bool = False
    industry_standard: bool = True
    risk_mitigation: List[str] = Field(default_factory=list)
    negotiation_priority: str = "medium"  # low, medium, high, critical
    alternatives: List[str] = Field(default_factory=list)

class IndustryRisk(BaseModel):
    risk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    risk_name: str
    description: str
    category: RiskCategory
    likelihood: str = "medium"  # low, medium, high
    impact: str = "medium"     # low, medium, high
    mitigation_strategies: List[str] = Field(default_factory=list)
    contractual_protections: List[str] = Field(default_factory=list)
    industry_examples: List[str] = Field(default_factory=list)

class NegotiationStrategy(BaseModel):
    strategy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    strategy_name: str
    description: str
    tactic: NegotiationTactic
    use_cases: List[str] = Field(default_factory=list)
    key_talking_points: List[str] = Field(default_factory=list)
    concession_framework: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)

class IndustryBenchmark(BaseModel):
    benchmark_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str
    industry_average: str
    percentile_25: Optional[str] = None
    percentile_75: Optional[str] = None
    best_practice: str
    data_source: str = "Industry Analysis"
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class IndustryProfile(BaseModel):
    industry: IndustryType
    supported_contract_types: List[ContractCategory]
    mandatory_clauses: List[IndustryClause] = Field(default_factory=list)
    recommended_clauses: List[IndustryClause] = Field(default_factory=list)
    common_risks: List[IndustryRisk] = Field(default_factory=list)
    negotiation_strategies: List[NegotiationStrategy] = Field(default_factory=list)
    compliance_frameworks: List[str] = Field(default_factory=list)
    market_benchmarks: List[IndustryBenchmark] = Field(default_factory=list)
    common_pitfalls: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)

# ==========================
# Input/Output Models
# ==========================

class IndustryAnalysisInput(BaseModel):
    session_id: str
    industry: IndustryType
    contract_category: ContractCategory
    contract_text: Optional[str] = None
    document_id: Optional[str] = None
    contract_value: Optional[float] = None
    contract_duration_months: Optional[int] = None
    jurisdiction: str = "US"
    counterparty_size: str = "medium"  # small, medium, large, enterprise
    relationship_type: str = "new"     # new, existing, strategic
    negotiation_position: str = "balanced"  # strong, balanced, weak
    priority_objectives: List[str] = Field(default_factory=list)

class IndustryAnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Industry Analysis
    industry: IndustryType
    contract_category: ContractCategory
    industry_profile: IndustryProfile
    
    # Contract Assessment
    contract_completeness_score: float = Field(ge=0, le=10)
    industry_alignment_score: float = Field(ge=0, le=10)
    risk_assessment_score: float = Field(ge=0, le=10)
    
    # Findings and Recommendations
    missing_industry_clauses: List[IndustryClause] = Field(default_factory=list)
    identified_risks: List[IndustryRisk] = Field(default_factory=list)
    recommended_strategies: List[NegotiationStrategy] = Field(default_factory=list)
    
    # Benchmarking
    market_benchmarks: List[IndustryBenchmark] = Field(default_factory=list)
    competitive_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Actionable Insights
    priority_amendments: List[Dict[str, str]] = Field(default_factory=list)
    negotiation_roadmap: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_checklist: List[str] = Field(default_factory=list)
    
    # AI-Enhanced Insights
    ai_analysis: Optional[str] = None
    industry_trends: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)

# ==========================
# Industry-Specific Analysis Engine
# ==========================

class IndustrySpecificAnalysisEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._gemini_initialized = False
        self._groq_client = None
        self._maybe_init_ai()
        self._init_industry_profiles()

    def _maybe_init_ai(self):
        """Initialize AI clients opportunistically"""
        try:
            gem_key = os.environ.get("GEMINI_API_KEY")
            if gem_key and genai:
                genai.configure(api_key=gem_key)
                self._gemini_initialized = True
                logger.info("✅ IndustryEngine: Gemini ready")
        except Exception as e:
            logger.warning(f"⚠️ IndustryEngine: Gemini init failed: {e}")
            self._gemini_initialized = False

        try:
            groq_key = os.environ.get("GROQ_API_KEY") 
            if groq_key and Groq:
                self._groq_client = Groq(api_key=groq_key)
                logger.info("✅ IndustryEngine: Groq ready")
        except Exception as e:
            logger.warning(f"⚠️ IndustryEngine: Groq init failed: {e}")
            self._groq_client = None

    def _init_industry_profiles(self):
        """Initialize industry-specific profiles and knowledge base"""
        self.industry_profiles = {
            IndustryType.HEALTHCARE: self._init_healthcare_profile(),
            IndustryType.FINANCIAL: self._init_financial_profile(),
            IndustryType.TECHNOLOGY: self._init_technology_profile(),
            IndustryType.MANUFACTURING: self._init_manufacturing_profile(),
        }

    def _init_healthcare_profile(self) -> IndustryProfile:
        """Initialize Healthcare industry profile"""
        
        # Healthcare-specific mandatory clauses
        mandatory_clauses = [
            IndustryClause(
                title="HIPAA Compliance",
                description="Ensures compliance with Health Insurance Portability and Accountability Act",
                template_text="Provider shall comply with all applicable provisions of HIPAA and implement appropriate safeguards for PHI.",
                mandatory=True,
                risk_mitigation=["Data breach prevention", "Regulatory compliance", "Patient privacy protection"],
                negotiation_priority="critical",
                alternatives=["Enhanced BAA terms", "Additional security measures"]
            ),
            IndustryClause(
                title="Professional Liability Coverage",
                description="Required malpractice insurance coverage",
                template_text="Provider shall maintain professional liability insurance with minimum coverage of $[X] per occurrence.",
                mandatory=True,
                risk_mitigation=["Financial protection", "Risk transfer"],
                negotiation_priority="high"
            ),
            IndustryClause(
                title="Patient Consent and Authorization",
                description="Proper patient consent procedures",
                template_text="All medical services require informed patient consent in accordance with applicable medical ethics standards.",
                mandatory=True,
                risk_mitigation=["Legal compliance", "Patient rights protection"],
                negotiation_priority="critical"
            )
        ]
        
        # Healthcare-specific recommended clauses
        recommended_clauses = [
            IndustryClause(
                title="Quality Assurance Standards",
                description="Healthcare quality metrics and compliance",
                template_text="Services shall meet industry-standard quality metrics including [specific quality indicators].",
                mandatory=False,
                risk_mitigation=["Quality control", "Patient safety"],
                negotiation_priority="medium"
            ),
            IndustryClause(
                title="Emergency Response Procedures",
                description="Protocols for medical emergencies",
                template_text="Provider shall maintain 24/7 emergency response capabilities and escalation procedures.",
                mandatory=False,
                risk_mitigation=["Patient safety", "Continuity of care"],
                negotiation_priority="medium"
            )
        ]
        
        # Healthcare-specific risks
        common_risks = [
            IndustryRisk(
                risk_name="HIPAA Violation",
                description="Breach of patient privacy regulations",
                category=RiskCategory.REGULATORY,
                likelihood="medium",
                impact="high",
                mitigation_strategies=["Comprehensive BAA", "Regular compliance audits", "Staff training"],
                contractual_protections=["Indemnification clauses", "Insurance requirements", "Audit rights"],
                industry_examples=["PHI data breaches", "Unauthorized access", "Inadequate safeguards"]
            ),
            IndustryRisk(
                risk_name="Medical Malpractice",
                description="Professional liability exposure",
                category=RiskCategory.LEGAL,
                likelihood="medium",
                impact="high",
                mitigation_strategies=["Professional liability insurance", "Quality protocols", "Peer review"],
                contractual_protections=["Insurance requirements", "Indemnification", "Standard of care definitions"],
                industry_examples=["Misdiagnosis", "Treatment errors", "Delayed care"]
            ),
            IndustryRisk(
                risk_name="Regulatory Changes",
                description="Evolving healthcare regulations",
                category=RiskCategory.REGULATORY,
                likelihood="high",
                impact="medium",
                mitigation_strategies=["Regulatory monitoring", "Flexible compliance framework", "Legal counsel"],
                contractual_protections=["Change in law clauses", "Compliance obligations", "Termination rights"],
                industry_examples=["CMS rule changes", "State licensing requirements", "Quality reporting mandates"]
            )
        ]
        
        # Healthcare negotiation strategies
        negotiation_strategies = [
            NegotiationStrategy(
                strategy_name="Patient Safety First",
                description="Prioritize patient safety in all negotiations",
                tactic=NegotiationTactic.COLLABORATIVE,
                use_cases=["Medical service agreements", "Provider contracts"],
                key_talking_points=["Patient outcomes", "Quality metrics", "Safety protocols"],
                concession_framework=["Non-negotiable: patient safety", "Flexible: administrative terms"],
                success_metrics=["Reduced liability", "Improved outcomes", "Regulatory compliance"]
            ),
            NegotiationStrategy(
                strategy_name="Value-Based Care",
                description="Focus on outcomes rather than volume",
                tactic=NegotiationTactic.VALUE_BASED,
                use_cases=["Provider contracts", "Insurance agreements"],
                key_talking_points=["Quality metrics", "Cost effectiveness", "Patient outcomes"],
                concession_framework=["Trade volume for quality incentives", "Risk-sharing arrangements"],
                success_metrics=["Improved patient outcomes", "Cost savings", "Quality bonuses"]
            )
        ]
        
        return IndustryProfile(
            industry=IndustryType.HEALTHCARE,
            supported_contract_types=[
                ContractCategory.MEDICAL_SERVICES,
                ContractCategory.BUSINESS_ASSOCIATE_AGREEMENT,
                ContractCategory.TELEMEDICINE,
                ContractCategory.PHARMACEUTICAL,
                ContractCategory.MEDICAL_DEVICE
            ],
            mandatory_clauses=mandatory_clauses,
            recommended_clauses=recommended_clauses,
            common_risks=common_risks,
            negotiation_strategies=negotiation_strategies,
            compliance_frameworks=["HIPAA", "FDA", "CMS", "Joint Commission", "State Medical Boards"],
            common_pitfalls=[
                "Inadequate HIPAA compliance provisions",
                "Insufficient professional liability coverage",
                "Unclear scope of medical services",
                "Missing emergency response procedures",
                "Inadequate quality assurance measures"
            ],
            best_practices=[
                "Comprehensive Business Associate Agreements",
                "Regular compliance audits and training",
                "Clear quality metrics and reporting",
                "24/7 emergency response capabilities",
                "Continuous professional development"
            ]
        )

    def _init_financial_profile(self) -> IndustryProfile:
        """Initialize Financial services industry profile"""
        
        # Financial-specific mandatory clauses
        mandatory_clauses = [
            IndustryClause(
                title="Regulatory Compliance",
                description="Compliance with financial services regulations",
                template_text="Provider shall comply with all applicable financial regulations including SEC, FINRA, and banking laws.",
                mandatory=True,
                risk_mitigation=["Regulatory compliance", "Penalty avoidance"],
                negotiation_priority="critical"
            ),
            IndustryClause(
                title="Anti-Money Laundering (AML)",
                description="AML and Know Your Customer requirements",
                template_text="Provider shall maintain AML compliance program and conduct appropriate due diligence.",
                mandatory=True,
                risk_mitigation=["Criminal liability prevention", "Regulatory compliance"],
                negotiation_priority="critical"
            ),
            IndustryClause(
                title="Data Security and Privacy",
                description="Financial data protection requirements",
                template_text="Provider shall implement bank-grade security measures for financial data protection.",
                mandatory=True,
                risk_mitigation=["Data breach prevention", "Customer privacy"],
                negotiation_priority="high"
            )
        ]
        
        # Financial-specific risks
        common_risks = [
            IndustryRisk(
                risk_name="Regulatory Penalties",
                description="Fines and sanctions from regulators",
                category=RiskCategory.REGULATORY,
                likelihood="medium",
                impact="high",
                mitigation_strategies=["Compliance monitoring", "Regular audits", "Legal review"],
                contractual_protections=["Regulatory compliance clauses", "Indemnification"],
                industry_examples=["SEC fines", "FINRA sanctions", "Banking penalties"]
            ),
            IndustryRisk(
                risk_name="Market Risk",
                description="Financial market volatility impact",
                category=RiskCategory.MARKET,
                likelihood="high",
                impact="medium",
                mitigation_strategies=["Hedging strategies", "Diversification", "Risk limits"],
                contractual_protections=["Market disruption clauses", "Force majeure", "Pricing adjustments"],
                industry_examples=["Interest rate changes", "Market crashes", "Currency fluctuations"]
            )
        ]
        
        # Financial negotiation strategies
        negotiation_strategies = [
            NegotiationStrategy(
                strategy_name="Risk-Adjusted Pricing",
                description="Pricing based on risk assessment",
                tactic=NegotiationTactic.VALUE_BASED,
                use_cases=["Loan agreements", "Investment contracts"],
                key_talking_points=["Risk assessment", "Market conditions", "Regulatory requirements"],
                concession_framework=["Risk-based pricing adjustments", "Performance incentives"],
                success_metrics=["Risk-adjusted returns", "Regulatory compliance", "Client satisfaction"]
            )
        ]
        
        return IndustryProfile(
            industry=IndustryType.FINANCIAL,
            supported_contract_types=[
                ContractCategory.INVESTMENT_AGREEMENT,
                ContractCategory.LOAN_CONTRACT,
                ContractCategory.BANKING_SERVICES,
                ContractCategory.FINTECH_PARTNERSHIP,
                ContractCategory.PAYMENT_PROCESSING,
                ContractCategory.INSURANCE
            ],
            mandatory_clauses=mandatory_clauses,
            recommended_clauses=[],
            common_risks=common_risks,
            negotiation_strategies=negotiation_strategies,
            compliance_frameworks=["SEC", "FINRA", "FDIC", "OCC", "CFPB", "SOX", "Basel III"],
            common_pitfalls=[
                "Inadequate regulatory compliance provisions",
                "Insufficient AML/KYC procedures",
                "Weak data security measures",
                "Missing risk management frameworks",
                "Inadequate capital requirements"
            ],
            best_practices=[
                "Comprehensive compliance monitoring",
                "Regular regulatory updates training",
                "Robust risk management systems",
                "Strong data security protocols",
                "Clear audit trails and documentation"
            ]
        )

    def _init_technology_profile(self) -> IndustryProfile:
        """Initialize Technology/SaaS industry profile"""
        
        # Technology-specific mandatory clauses
        mandatory_clauses = [
            IndustryClause(
                title="Data Processing Agreement",
                description="GDPR and data privacy compliance",
                template_text="Provider shall execute comprehensive DPA covering data processing, security, and privacy obligations.",
                mandatory=True,
                risk_mitigation=["Data privacy compliance", "Regulatory compliance"],
                negotiation_priority="critical"
            ),
            IndustryClause(
                title="Service Level Agreement",
                description="Uptime and performance guarantees",
                template_text="Provider shall maintain [X]% uptime with performance benchmarks and remedies for non-compliance.",
                mandatory=True,
                risk_mitigation=["Service reliability", "Business continuity"],
                negotiation_priority="high"
            ),
            IndustryClause(
                title="Intellectual Property Rights",
                description="IP ownership and licensing terms",
                template_text="Clear definition of IP ownership, licensing rights, and restrictions on use.",
                mandatory=True,
                risk_mitigation=["IP disputes", "Licensing clarity"],
                negotiation_priority="high"
            )
        ]
        
        # Technology-specific risks
        common_risks = [
            IndustryRisk(
                risk_name="Data Breach",
                description="Cybersecurity incidents and data exposure",
                category=RiskCategory.TECHNICAL,
                likelihood="medium",
                impact="high",
                mitigation_strategies=["Security audits", "Encryption", "Access controls"],
                contractual_protections=["Security requirements", "Breach notification", "Liability limits"],
                industry_examples=["Ransomware attacks", "Data theft", "System compromises"]
            ),
            IndustryRisk(
                risk_name="Technology Obsolescence",
                description="Platform or technology becoming outdated",
                category=RiskCategory.TECHNICAL,
                likelihood="medium",
                impact="medium",
                mitigation_strategies=["Regular updates", "Migration planning", "Flexible architecture"],
                contractual_protections=["Update obligations", "Migration assistance", "Termination rights"],
                industry_examples=["Legacy system issues", "Platform deprecation", "Version conflicts"]
            )
        ]
        
        # Technology negotiation strategies
        negotiation_strategies = [
            NegotiationStrategy(
                strategy_name="Agile Partnership",
                description="Flexible, iterative approach to technology contracts",
                tactic=NegotiationTactic.COLLABORATIVE,
                use_cases=["Software development", "SaaS agreements"],
                key_talking_points=["Flexibility", "Iterative development", "Continuous improvement"],
                concession_framework=["Scope adjustments", "Timeline flexibility", "Performance incentives"],
                success_metrics=["Time to market", "User satisfaction", "Technical performance"]
            )
        ]
        
        return IndustryProfile(
            industry=IndustryType.TECHNOLOGY,
            supported_contract_types=[
                ContractCategory.SOFTWARE_LICENSE,
                ContractCategory.DATA_PROCESSING_AGREEMENT,
                ContractCategory.API_AGREEMENT,
                ContractCategory.CLOUD_SERVICES,
                ContractCategory.AI_ML_CONTRACT,
                ContractCategory.SaaS_AGREEMENT
            ],
            mandatory_clauses=mandatory_clauses,
            recommended_clauses=[],
            common_risks=common_risks,
            negotiation_strategies=negotiation_strategies,
            compliance_frameworks=["GDPR", "CCPA", "SOC 2", "ISO 27001", "PCI DSS"],
            common_pitfalls=[
                "Inadequate data protection provisions",
                "Unclear IP ownership terms",
                "Insufficient SLA definitions",
                "Missing security requirements",
                "Inadequate termination procedures"
            ],
            best_practices=[
                "Comprehensive data processing agreements",
                "Clear IP ownership and licensing",
                "Detailed SLAs with measurable metrics",
                "Robust security and compliance frameworks",
                "Flexible scaling and termination provisions"
            ]
        )

    def _init_manufacturing_profile(self) -> IndustryProfile:
        """Initialize Manufacturing industry profile"""
        
        # Manufacturing-specific mandatory clauses
        mandatory_clauses = [
            IndustryClause(
                title="Quality Specifications",
                description="Product quality standards and testing requirements",
                template_text="Products shall meet specified quality standards with testing and certification requirements.",
                mandatory=True,
                risk_mitigation=["Quality control", "Defect prevention"],
                negotiation_priority="high"
            ),
            IndustryClause(
                title="Supply Chain Security",
                description="Supply chain integrity and security measures",
                template_text="Supplier shall maintain secure supply chain with verified sourcing and chain of custody.",
                mandatory=True,
                risk_mitigation=["Supply chain risks", "Security breaches"],
                negotiation_priority="high"
            ),
            IndustryClause(
                title="Environmental Compliance",
                description="Environmental regulations and sustainability",
                template_text="Operations shall comply with environmental regulations and sustainability standards.",
                mandatory=True,
                risk_mitigation=["Environmental liability", "Regulatory compliance"],
                negotiation_priority="medium"
            )
        ]
        
        # Manufacturing-specific risks
        common_risks = [
            IndustryRisk(
                risk_name="Supply Chain Disruption",
                description="Interruption in supply chain or materials",
                category=RiskCategory.OPERATIONAL,
                likelihood="medium",
                impact="high",
                mitigation_strategies=["Supplier diversification", "Inventory buffers", "Contingency planning"],
                contractual_protections=["Force majeure clauses", "Alternative suppliers", "Risk sharing"],
                industry_examples=["Natural disasters", "Supplier failures", "Transportation issues"]
            ),
            IndustryRisk(
                risk_name="Product Liability",
                description="Defective products causing harm or damage",
                category=RiskCategory.LEGAL,
                likelihood="low",
                impact="high",
                mitigation_strategies=["Quality control", "Testing protocols", "Insurance coverage"],
                contractual_protections=["Indemnification", "Insurance requirements", "Warranty limitations"],
                industry_examples=["Product recalls", "Safety incidents", "Performance failures"]
            )
        ]
        
        # Manufacturing negotiation strategies
        negotiation_strategies = [
            NegotiationStrategy(
                strategy_name="Total Cost of Ownership",
                description="Focus on long-term costs rather than unit prices",
                tactic=NegotiationTactic.VALUE_BASED,
                use_cases=["Procurement contracts", "OEM agreements"],
                key_talking_points=["Total cost", "Quality benefits", "Long-term partnership"],
                concession_framework=["Price vs. quality trade-offs", "Volume commitments", "Partnership benefits"],
                success_metrics=["Total cost reduction", "Quality improvements", "Supply reliability"]
            )
        ]
        
        return IndustryProfile(
            industry=IndustryType.MANUFACTURING,
            supported_contract_types=[
                ContractCategory.SUPPLY_CHAIN,
                ContractCategory.DISTRIBUTION_AGREEMENT,
                ContractCategory.OEM_AGREEMENT,
                ContractCategory.QUALITY_ASSURANCE,
                ContractCategory.MANUFACTURING_SERVICES,
                ContractCategory.PROCUREMENT
            ],
            mandatory_clauses=mandatory_clauses,
            recommended_clauses=[],
            common_risks=common_risks,
            negotiation_strategies=negotiation_strategies,
            compliance_frameworks=["ISO 9001", "ISO 14001", "OSHA", "EPA", "FDA (if applicable)"],
            common_pitfalls=[
                "Inadequate quality specifications",
                "Insufficient supply chain security",
                "Missing environmental compliance",
                "Weak intellectual property protection",
                "Inadequate risk allocation"
            ],
            best_practices=[
                "Comprehensive quality management systems",
                "Robust supply chain risk management",
                "Strong environmental compliance programs",
                "Clear IP ownership and protection",
                "Balanced risk sharing arrangements"
            ]
        )

    async def initialize_collections(self):
        """Initialize MongoDB collections for industry analysis tracking"""
        try:
            # Industry analyses collection
            await self.db.industry_analyses.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.industry_analyses.create_index([("analysis_id", 1)], unique=True)
            await self.db.industry_analyses.create_index([("industry", 1), ("contract_category", 1)])
            
            # Industry benchmarks collection
            await self.db.industry_benchmarks.create_index([("industry", 1), ("metric_name", 1)])
            
            # Industry templates collection
            await self.db.industry_templates.create_index([("industry", 1), ("contract_category", 1)])
            
            logger.info("✅ IndustryEngine: collections initialized")
        except Exception as e:
            logger.error(f"❌ IndustryEngine: init collections error: {e}")

    async def analyze_industry_contract(self, input_data: IndustryAnalysisInput) -> IndustryAnalysisResult:
        """
        Main industry-specific contract analysis function
        
        Analyzes contract for industry-specific requirements, risks, and opportunities
        """
        try:
            logger.info(f"🏭 Starting industry analysis for {input_data.industry.value} - {input_data.contract_category.value}")
            
            # Get industry profile
            industry_profile = self.industry_profiles.get(input_data.industry)
            if not industry_profile:
                raise ValueError(f"Unsupported industry: {input_data.industry}")
            
            # Get contract text
            contract_text = await self._get_contract_text(input_data)
            
            # Analyze contract completeness
            completeness_score = await self._assess_contract_completeness(
                contract_text, industry_profile, input_data.contract_category
            )
            
            # Assess industry alignment
            alignment_score = await self._assess_industry_alignment(
                contract_text, industry_profile, input_data
            )
            
            # Perform risk assessment
            risk_score, identified_risks = await self._assess_industry_risks(
                contract_text, industry_profile, input_data
            )
            
            # Identify missing clauses
            missing_clauses = await self._identify_missing_clauses(
                contract_text, industry_profile, input_data.contract_category
            )
            
            # Recommend negotiation strategies
            recommended_strategies = await self._recommend_negotiation_strategies(
                industry_profile, input_data
            )
            
            # Get market benchmarks
            market_benchmarks = await self._get_market_benchmarks(
                input_data.industry, input_data.contract_category
            )
            
            # Perform competitive analysis
            competitive_analysis = await self._perform_competitive_analysis(
                input_data, contract_text
            )
            
            # Generate priority amendments
            priority_amendments = await self._generate_priority_amendments(
                missing_clauses, identified_risks
            )
            
            # Create negotiation roadmap
            negotiation_roadmap = await self._create_negotiation_roadmap(
                recommended_strategies, input_data
            )
            
            # Generate compliance checklist
            compliance_checklist = await self._generate_compliance_checklist(
                industry_profile, input_data.contract_category
            )
            
            # Get AI-enhanced insights
            ai_analysis = await self._get_ai_analysis(
                input_data, contract_text, industry_profile
            )
            
            # Get industry trends
            industry_trends = await self._get_industry_trends(input_data.industry)
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                input_data, completeness_score, alignment_score, risk_score
            )
            
            # Create analysis result
            result = IndustryAnalysisResult(
                session_id=input_data.session_id,
                industry=input_data.industry,
                contract_category=input_data.contract_category,
                industry_profile=industry_profile,
                contract_completeness_score=completeness_score,
                industry_alignment_score=alignment_score,
                risk_assessment_score=risk_score,
                missing_industry_clauses=missing_clauses,
                identified_risks=identified_risks,
                recommended_strategies=recommended_strategies,
                market_benchmarks=market_benchmarks,
                competitive_analysis=competitive_analysis,
                priority_amendments=priority_amendments,
                negotiation_roadmap=negotiation_roadmap,
                compliance_checklist=compliance_checklist,
                ai_analysis=ai_analysis,
                industry_trends=industry_trends,
                strategic_recommendations=strategic_recommendations
            )
            
            # Store result in database
            await self.db.industry_analyses.insert_one(result.model_dump())
            
            logger.info(f"✅ Industry analysis completed: {completeness_score:.1f}/10 completeness, {alignment_score:.1f}/10 alignment")
            return result
            
        except Exception as e:
            logger.error(f"❌ Industry analysis error: {e}")
            raise

    async def _get_contract_text(self, input_data: IndustryAnalysisInput) -> str:
        """Get contract text from input or database"""
        if input_data.contract_text:
            return input_data.contract_text
        
        if input_data.document_id:
            # Try to get from uploaded documents
            doc = await self.db.legal_documents.find_one({"document_id": input_data.document_id})
            if doc and "content" in doc:
                return doc["content"]
        
        # Fallback: get from latest negotiation session
        session_doc = await self.db.negotiation_sessions.find_one({"session_id": input_data.session_id})
        if session_doc and "contract_text" in session_doc:
            return session_doc["contract_text"]
            
        return f"Sample {input_data.contract_category.value} contract for {input_data.industry.value} industry analysis."

    async def _assess_contract_completeness(
        self, contract_text: str, industry_profile: IndustryProfile, contract_category: ContractCategory
    ) -> float:
        """Assess how complete the contract is for the industry"""
        
        contract_lower = contract_text.lower()
        total_clauses = len(industry_profile.mandatory_clauses) + len(industry_profile.recommended_clauses)
        
        if total_clauses == 0:
            return 8.0  # Default score if no specific clauses defined
        
        found_clauses = 0
        
        # Check mandatory clauses (weighted more heavily)
        for clause in industry_profile.mandatory_clauses:
            if self._clause_present_in_contract(clause.title, contract_text):
                found_clauses += 2  # Double weight for mandatory
        
        # Check recommended clauses
        for clause in industry_profile.recommended_clauses:
            if self._clause_present_in_contract(clause.title, contract_text):
                found_clauses += 1
        
        # Calculate score (out of 10)
        max_possible = len(industry_profile.mandatory_clauses) * 2 + len(industry_profile.recommended_clauses)
        score = (found_clauses / max_possible * 10) if max_possible > 0 else 8.0
        
        return min(10.0, max(0.0, score))

    async def _assess_industry_alignment(
        self, contract_text: str, industry_profile: IndustryProfile, input_data: IndustryAnalysisInput
    ) -> float:
        """Assess how well the contract aligns with industry standards"""
        
        alignment_factors = []
        
        # Check for industry-specific terminology
        industry_terms = self._get_industry_terms(input_data.industry)
        found_terms = sum(1 for term in industry_terms if term.lower() in contract_text.lower())
        term_score = (found_terms / len(industry_terms)) * 2.5 if industry_terms else 2.5
        alignment_factors.append(term_score)
        
        # Check compliance framework references
        frameworks = industry_profile.compliance_frameworks
        found_frameworks = sum(1 for framework in frameworks if framework.lower() in contract_text.lower())
        framework_score = (found_frameworks / len(frameworks)) * 2.5 if frameworks else 2.5
        alignment_factors.append(framework_score)
        
        # Check for industry best practices
        best_practices = industry_profile.best_practices
        found_practices = 0
        for practice in best_practices:
            # Simple keyword matching for best practices
            practice_keywords = practice.lower().split()
            if any(keyword in contract_text.lower() for keyword in practice_keywords):
                found_practices += 1
        practice_score = (found_practices / len(best_practices)) * 2.5 if best_practices else 2.5
        alignment_factors.append(practice_score)
        
        # Check for common pitfall avoidance
        pitfalls = industry_profile.common_pitfalls
        avoided_pitfalls = 0
        for pitfall in pitfalls:
            # If contract addresses the pitfall area, it's good
            pitfall_keywords = pitfall.lower().split()
            if any(keyword in contract_text.lower() for keyword in pitfall_keywords):
                avoided_pitfalls += 1
        pitfall_score = (avoided_pitfalls / len(pitfalls)) * 2.5 if pitfalls else 2.5
        alignment_factors.append(pitfall_score)
        
        # Calculate overall alignment score
        total_score = sum(alignment_factors)
        return min(10.0, max(0.0, total_score))

    async def _assess_industry_risks(
        self, contract_text: str, industry_profile: IndustryProfile, input_data: IndustryAnalysisInput
    ) -> Tuple[float, List[IndustryRisk]]:
        """Assess industry-specific risks in the contract"""
        
        identified_risks = []
        total_risk_score = 0
        
        for risk in industry_profile.common_risks:
            # Check if risk is adequately addressed in contract
            risk_addressed = False
            
            # Check for contractual protections
            for protection in risk.contractual_protections:
                if self._clause_present_in_contract(protection, contract_text):
                    risk_addressed = True
                    break
            
            if not risk_addressed:
                # Risk is not adequately addressed
                identified_risks.append(risk)
                
                # Calculate risk score based on likelihood and impact
                likelihood_score = {"low": 1, "medium": 2, "high": 3}.get(risk.likelihood, 2)
                impact_score = {"low": 1, "medium": 2, "high": 3}.get(risk.impact, 2)
                risk_score = likelihood_score * impact_score
                total_risk_score += risk_score
        
        # Convert to score out of 10 (lower is better for risk)
        max_possible_risk = len(industry_profile.common_risks) * 9  # 3 * 3 = max risk per item
        if max_possible_risk > 0:
            risk_percentage = total_risk_score / max_possible_risk
            risk_assessment_score = 10 - (risk_percentage * 10)  # Invert so higher is better
        else:
            risk_assessment_score = 8.0
        
        return max(0.0, min(10.0, risk_assessment_score)), identified_risks

    async def _identify_missing_clauses(
        self, contract_text: str, industry_profile: IndustryProfile, contract_category: ContractCategory
    ) -> List[IndustryClause]:
        """Identify missing industry-specific clauses"""
        
        missing_clauses = []
        
        # Check mandatory clauses
        for clause in industry_profile.mandatory_clauses:
            if not self._clause_present_in_contract(clause.title, contract_text):
                missing_clauses.append(clause)
        
        # Check recommended clauses based on contract category
        for clause in industry_profile.recommended_clauses:
            if not self._clause_present_in_contract(clause.title, contract_text):
                # Add if high priority or relevant to contract category
                if clause.negotiation_priority in ["high", "critical"]:
                    missing_clauses.append(clause)
        
        return missing_clauses

    async def _recommend_negotiation_strategies(
        self, industry_profile: IndustryProfile, input_data: IndustryAnalysisInput
    ) -> List[NegotiationStrategy]:
        """Recommend negotiation strategies based on industry and situation"""
        
        recommended_strategies = []
        
        # Select strategies based on negotiation position and relationship
        for strategy in industry_profile.negotiation_strategies:
            # Match strategy to situation
            if input_data.negotiation_position == "strong" and strategy.tactic in [
                NegotiationTactic.COMPETITIVE, NegotiationTactic.VALUE_BASED
            ]:
                recommended_strategies.append(strategy)
            elif input_data.negotiation_position == "weak" and strategy.tactic in [
                NegotiationTactic.COLLABORATIVE, NegotiationTactic.RELATIONSHIP_FOCUSED
            ]:
                recommended_strategies.append(strategy)
            elif input_data.negotiation_position == "balanced":
                recommended_strategies.append(strategy)  # Include all for balanced position
        
        # If no specific strategies matched, include collaborative approach
        if not recommended_strategies and industry_profile.negotiation_strategies:
            recommended_strategies = [industry_profile.negotiation_strategies[0]]
        
        return recommended_strategies

    async def _get_market_benchmarks(
        self, industry: IndustryType, contract_category: ContractCategory
    ) -> List[IndustryBenchmark]:
        """Get market benchmarks for industry and contract type"""
        
        # Default benchmarks by industry
        benchmarks = []
        
        if industry == IndustryType.HEALTHCARE:
            benchmarks = [
                IndustryBenchmark(
                    metric_name="Professional Liability Coverage",
                    industry_average="$1M-$3M per occurrence",
                    percentile_25="$1M",
                    percentile_75="$5M",
                    best_practice="$3M+ with umbrella coverage"
                ),
                IndustryBenchmark(
                    metric_name="Contract Term Length",
                    industry_average="2-3 years",
                    percentile_25="1 year",
                    percentile_75="5 years",
                    best_practice="3 years with renewal options"
                )
            ]
        elif industry == IndustryType.FINANCIAL:
            benchmarks = [
                IndustryBenchmark(
                    metric_name="Regulatory Capital Requirements",
                    industry_average="8-12% Tier 1 capital ratio",
                    percentile_25="8%",
                    percentile_75="15%",
                    best_practice="12%+ for stability"
                ),
                IndustryBenchmark(
                    metric_name="AML Compliance Investment",
                    industry_average="0.5-1.5% of revenue",
                    percentile_25="0.3%",
                    percentile_75="2%",
                    best_practice="1%+ with continuous monitoring"
                )
            ]
        elif industry == IndustryType.TECHNOLOGY:
            benchmarks = [
                IndustryBenchmark(
                    metric_name="SLA Uptime Guarantee",
                    industry_average="99.5-99.9%",
                    percentile_25="99%",
                    percentile_75="99.95%",
                    best_practice="99.9%+ with penalties"
                ),
                IndustryBenchmark(
                    metric_name="Data Retention Period",
                    industry_average="3-7 years",
                    percentile_25="1 year",
                    percentile_75="10 years",
                    best_practice="Follow legal requirements + business needs"
                )
            ]
        elif industry == IndustryType.MANUFACTURING:
            benchmarks = [
                IndustryBenchmark(
                    metric_name="Quality Standards Compliance",
                    industry_average="ISO 9001 or equivalent",
                    best_practice="Multiple certifications (ISO 9001, 14001, etc.)"
                ),
                IndustryBenchmark(
                    metric_name="Supplier Payment Terms",
                    industry_average="Net 30-60 days",
                    percentile_25="Net 30",
                    percentile_75="Net 90",
                    best_practice="Net 45 with early payment discounts"
                )
            ]
        
        return benchmarks

    async def _perform_competitive_analysis(
        self, input_data: IndustryAnalysisInput, contract_text: str
    ) -> Dict[str, Any]:
        """Perform competitive analysis for the industry"""
        
        analysis = {
            "market_position": self._assess_market_position(input_data),
            "competitive_advantages": self._identify_competitive_advantages(input_data),
            "market_trends": await self._get_industry_trends(input_data.industry),
            "pricing_insights": self._get_pricing_insights(input_data),
            "negotiation_leverage": self._assess_negotiation_leverage(input_data)
        }
        
        return analysis

    def _assess_market_position(self, input_data: IndustryAnalysisInput) -> str:
        """Assess market position based on input parameters"""
        
        if input_data.counterparty_size == "enterprise" and input_data.relationship_type == "strategic":
            return "strong"
        elif input_data.counterparty_size == "small" and input_data.contract_value and input_data.contract_value > 100000:
            return "strong"
        elif input_data.negotiation_position == "strong":
            return "strong"
        elif input_data.negotiation_position == "weak":
            return "weak"
        else:
            return "balanced"

    def _identify_competitive_advantages(self, input_data: IndustryAnalysisInput) -> List[str]:
        """Identify competitive advantages based on industry and situation"""
        
        advantages = []
        
        if input_data.industry == IndustryType.HEALTHCARE:
            advantages = [
                "Specialized medical expertise",
                "Regulatory compliance experience", 
                "Patient safety focus",
                "Quality outcome metrics"
            ]
        elif input_data.industry == IndustryType.FINANCIAL:
            advantages = [
                "Regulatory expertise",
                "Risk management capabilities",
                "Market knowledge",
                "Compliance infrastructure"
            ]
        elif input_data.industry == IndustryType.TECHNOLOGY:
            advantages = [
                "Technical innovation",
                "Scalability capabilities",
                "Security expertise",
                "Integration capabilities"
            ]
        elif input_data.industry == IndustryType.MANUFACTURING:
            advantages = [
                "Production efficiency",
                "Quality control systems",
                "Supply chain expertise",
                "Cost optimization"
            ]
        
        return advantages

    def _get_pricing_insights(self, input_data: IndustryAnalysisInput) -> Dict[str, Any]:
        """Get pricing insights for the industry"""
        
        insights = {
            "pricing_model": "value-based",
            "market_rate_range": "competitive",
            "cost_drivers": [],
            "negotiation_flexibility": "medium"
        }
        
        if input_data.industry == IndustryType.HEALTHCARE:
            insights.update({
                "pricing_model": "outcome-based",
                "cost_drivers": ["compliance costs", "insurance requirements", "quality metrics"],
                "negotiation_flexibility": "low"  # Due to regulatory constraints
            })
        elif input_data.industry == IndustryType.FINANCIAL:
            insights.update({
                "pricing_model": "risk-adjusted",
                "cost_drivers": ["regulatory compliance", "capital requirements", "risk assessment"],
                "negotiation_flexibility": "medium"
            })
        elif input_data.industry == IndustryType.TECHNOLOGY:
            insights.update({
                "pricing_model": "subscription/usage-based",
                "cost_drivers": ["development costs", "infrastructure", "support"],
                "negotiation_flexibility": "high"
            })
        elif input_data.industry == IndustryType.MANUFACTURING:
            insights.update({
                "pricing_model": "cost-plus or fixed-price",
                "cost_drivers": ["materials", "labor", "quality standards", "compliance"],
                "negotiation_flexibility": "medium"
            })
        
        return insights

    def _assess_negotiation_leverage(self, input_data: IndustryAnalysisInput) -> Dict[str, Any]:
        """Assess negotiation leverage factors"""
        
        leverage = {
            "overall_position": input_data.negotiation_position,
            "leverage_factors": [],
            "constraints": [],
            "opportunities": []
        }
        
        # Add industry-specific leverage factors
        if input_data.contract_value and input_data.contract_value > 1000000:
            leverage["leverage_factors"].append("High contract value")
        
        if input_data.relationship_type == "strategic":
            leverage["leverage_factors"].append("Strategic partnership potential")
        
        if input_data.counterparty_size == "large" or input_data.counterparty_size == "enterprise":
            leverage["constraints"].append("Large counterparty negotiation power")
        else:
            leverage["opportunities"].append("Smaller counterparty flexibility")
        
        return leverage

    async def _generate_priority_amendments(
        self, missing_clauses: List[IndustryClause], identified_risks: List[IndustryRisk]
    ) -> List[Dict[str, str]]:
        """Generate priority contract amendments"""
        
        amendments = []
        
        # Add amendments for missing critical clauses
        for clause in missing_clauses:
            if clause.negotiation_priority in ["critical", "high"]:
                amendment = {
                    "section": clause.title,
                    "priority": clause.negotiation_priority,
                    "suggested_text": clause.template_text,
                    "rationale": clause.description,
                    "risk_mitigation": ", ".join(clause.risk_mitigation)
                }
                amendments.append(amendment)
        
        # Add amendments for high-impact risks
        for risk in identified_risks:
            if risk.impact == "high":
                for protection in risk.contractual_protections[:2]:  # Top 2 protections
                    amendment = {
                        "section": f"{risk.risk_name} Protection",
                        "priority": "high" if risk.impact == "high" else "medium",
                        "suggested_text": f"Add contractual protection for {protection}",
                        "rationale": f"Mitigate {risk.risk_name}: {risk.description}",
                        "risk_mitigation": protection
                    }
                    amendments.append(amendment)
        
        return amendments[:10]  # Limit to top 10 amendments

    async def _create_negotiation_roadmap(
        self, recommended_strategies: List[NegotiationStrategy], input_data: IndustryAnalysisInput
    ) -> List[Dict[str, Any]]:
        """Create negotiation roadmap with phases and tactics"""
        
        roadmap = []
        
        # Phase 1: Preparation
        roadmap.append({
            "phase": 1,
            "title": "Preparation and Analysis",
            "timeline": "1-2 weeks before negotiation",
            "objectives": [
                "Complete industry analysis",
                "Identify key priorities and constraints",
                "Prepare fallback positions",
                "Research counterparty background"
            ],
            "deliverables": ["Negotiation strategy document", "Risk assessment", "Market benchmarks"]
        })
        
        # Phase 2: Opening Strategy
        if recommended_strategies:
            primary_strategy = recommended_strategies[0]
            roadmap.append({
                "phase": 2,
                "title": f"Opening Strategy: {primary_strategy.strategy_name}",
                "timeline": "Initial negotiation rounds",
                "objectives": primary_strategy.key_talking_points,
                "tactics": primary_strategy.tactic.value,
                "success_metrics": primary_strategy.success_metrics
            })
        
        # Phase 3: Core Negotiations
        roadmap.append({
            "phase": 3,
            "title": "Core Term Negotiations",
            "timeline": "Main negotiation phase",
            "objectives": [
                "Address mandatory industry clauses",
                "Negotiate commercial terms",
                "Resolve risk allocation",
                "Finalize compliance requirements"
            ],
            "focus_areas": input_data.priority_objectives if input_data.priority_objectives else [
                "Price and payment terms", "Risk allocation", "Performance standards"
            ]
        })
        
        # Phase 4: Final Agreement
        roadmap.append({
            "phase": 4,
            "title": "Final Agreement and Closure",
            "timeline": "Final negotiation rounds",
            "objectives": [
                "Resolve remaining open issues",
                "Finalize contract language",
                "Obtain necessary approvals",
                "Execute final agreement"
            ],
            "deliverables": ["Executed contract", "Implementation plan", "Governance framework"]
        })
        
        return roadmap

    async def _generate_compliance_checklist(
        self, industry_profile: IndustryProfile, contract_category: ContractCategory
    ) -> List[str]:
        """Generate industry-specific compliance checklist"""
        
        checklist = []
        
        # Add framework-specific items
        for framework in industry_profile.compliance_frameworks:
            checklist.append(f"✓ Verify {framework} compliance requirements")
        
        # Add mandatory clause items
        for clause in industry_profile.mandatory_clauses:
            checklist.append(f"✓ Include {clause.title}")
        
        # Add industry-specific items
        if industry_profile.industry == IndustryType.HEALTHCARE:
            checklist.extend([
                "✓ Execute Business Associate Agreement if applicable",
                "✓ Verify professional liability insurance coverage",
                "✓ Confirm HIPAA compliance training requirements",
                "✓ Establish patient consent procedures"
            ])
        elif industry_profile.industry == IndustryType.FINANCIAL:
            checklist.extend([
                "✓ Confirm regulatory registration and licensing",
                "✓ Verify AML/KYC compliance procedures",
                "✓ Establish capital adequacy requirements",
                "✓ Implement risk management frameworks"
            ])
        elif industry_profile.industry == IndustryType.TECHNOLOGY:
            checklist.extend([
                "✓ Execute comprehensive Data Processing Agreement",
                "✓ Define Service Level Agreements and penalties",
                "✓ Clarify intellectual property ownership",
                "✓ Establish security and privacy controls"
            ])
        elif industry_profile.industry == IndustryType.MANUFACTURING:
            checklist.extend([
                "✓ Define quality standards and testing procedures",
                "✓ Establish supply chain security requirements",
                "✓ Confirm environmental compliance obligations",
                "✓ Verify insurance and indemnification coverage"
            ])
        
        return list(set(checklist))[:20]  # Remove duplicates, limit to 20

    async def _get_ai_analysis(
        self, input_data: IndustryAnalysisInput, contract_text: str, industry_profile: IndustryProfile
    ) -> Optional[str]:
        """Get AI-enhanced analysis of industry-specific contract"""
        
        prompt = f"""
        Analyze this {input_data.industry.value} industry {input_data.contract_category.value} contract:
        
        Contract Text: {contract_text[:2000]}...
        
        Industry Context:
        - Contract Category: {input_data.contract_category.value}
        - Contract Value: ${input_data.contract_value:,.0f}" if input_data.contract_value else "Not specified"
        - Counterparty Size: {input_data.counterparty_size}
        - Relationship: {input_data.relationship_type}
        - Negotiation Position: {input_data.negotiation_position}
        
        Provide industry-specific analysis covering:
        1. Key strengths and weaknesses from industry perspective
        2. Critical missing elements for this industry
        3. Industry-specific risks and opportunities
        4. Negotiation recommendations based on market position
        5. Compliance and regulatory considerations
        
        Keep response focused and actionable (max 500 words).
        """
        
        return await self._get_ai_insight(prompt)

    async def _get_industry_trends(self, industry: IndustryType) -> List[str]:
        """Get current industry trends affecting contracts"""
        
        trends = []
        
        if industry == IndustryType.HEALTHCARE:
            trends = [
                "Increased focus on value-based care contracts",
                "Stricter data privacy and cybersecurity requirements",
                "Growth in telemedicine and remote care agreements",
                "Enhanced patient outcome measurement and reporting",
                "Consolidation driving larger, more complex contracts"
            ]
        elif industry == IndustryType.FINANCIAL:
            trends = [
                "Increased regulatory scrutiny and compliance costs",
                "Digital transformation and fintech partnerships",
                "Enhanced ESG (Environmental, Social, Governance) requirements",
                "Real-time payments and instant settlement systems",
                "Cryptocurrency and digital asset regulations"
            ]
        elif industry == IndustryType.TECHNOLOGY:
            trends = [
                "AI and machine learning integration requirements",
                "Stricter data privacy regulations (GDPR, CCPA)",
                "Cloud-first and hybrid infrastructure models",
                "Increased cybersecurity and breach notification requirements",
                "API-first and microservices architectures"
            ]
        elif industry == IndustryType.MANUFACTURING:
            trends = [
                "Supply chain resilience and diversification",
                "Sustainability and environmental compliance focus",
                "Industry 4.0 and IoT integration",
                "Reshoring and nearshoring manufacturing",
                "Circular economy and waste reduction initiatives"
            ]
        
        return trends

    async def _generate_strategic_recommendations(
        self, input_data: IndustryAnalysisInput, completeness_score: float, 
        alignment_score: float, risk_score: float
    ) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        
        recommendations = []
        
        # Score-based recommendations
        if completeness_score < 7.0:
            recommendations.append("Priority: Address missing mandatory industry clauses to improve contract completeness")
        
        if alignment_score < 6.0:
            recommendations.append("Focus: Improve industry alignment by incorporating standard terms and practices")
        
        if risk_score < 7.0:
            recommendations.append("Critical: Implement additional risk mitigation measures for identified industry risks")
        
        # Industry-specific recommendations
        if input_data.industry == IndustryType.HEALTHCARE:
            recommendations.extend([
                "Ensure comprehensive HIPAA compliance and Business Associate Agreement terms",
                "Consider value-based care metrics and outcome-based pricing models"
            ])
        elif input_data.industry == IndustryType.FINANCIAL:
            recommendations.extend([
                "Implement robust regulatory compliance and change management provisions",
                "Consider ESG factors and sustainable finance requirements"
            ])
        elif input_data.industry == IndustryType.TECHNOLOGY:
            recommendations.extend([
                "Prioritize data privacy, security, and AI governance frameworks",
                "Ensure scalability and flexibility for rapid technology changes"
            ])
        elif input_data.industry == IndustryType.MANUFACTURING:
            recommendations.extend([
                "Focus on supply chain resilience and sustainability requirements",
                "Implement comprehensive quality assurance and environmental compliance"
            ])
        
        # Position-based recommendations
        if input_data.negotiation_position == "strong":
            recommendations.append("Leverage strong position to secure favorable terms and comprehensive protections")
        elif input_data.negotiation_position == "weak":
            recommendations.append("Focus on collaborative approach and relationship-building for long-term success")
        
        return recommendations[:8]  # Limit to top 8 recommendations

    def _clause_present_in_contract(self, clause_title: str, contract_text: str) -> bool:
        """Check if clause is present in contract text"""
        # Simple keyword matching - could be enhanced with NLP
        keywords = clause_title.lower().split()
        contract_lower = contract_text.lower()
        
        # Check if at least 50% of keywords are present
        found_keywords = sum(1 for keyword in keywords if keyword in contract_lower)
        return found_keywords >= len(keywords) * 0.5

    def _get_industry_terms(self, industry: IndustryType) -> List[str]:
        """Get industry-specific terminology"""
        
        terms_by_industry = {
            IndustryType.HEALTHCARE: [
                "HIPAA", "PHI", "BAA", "medical", "patient", "healthcare", "clinical",
                "FDA", "quality assurance", "malpractice", "license"
            ],
            IndustryType.FINANCIAL: [
                "regulatory", "compliance", "AML", "KYC", "capital", "risk", "SEC",
                "FINRA", "banking", "investment", "fiduciary", "audit"
            ],
            IndustryType.TECHNOLOGY: [
                "software", "SaaS", "API", "cloud", "data", "security", "privacy",
                "IP", "license", "SLA", "uptime", "scalability"
            ],
            IndustryType.MANUFACTURING: [
                "quality", "ISO", "supply chain", "manufacturing", "production",
                "materials", "testing", "compliance", "environmental", "safety"
            ]
        }
        
        return terms_by_industry.get(industry, [])

    async def _get_ai_insight(self, prompt: str) -> Optional[str]:
        """Get AI insight for industry analysis"""
        try:
            if self._gemini_initialized and genai:
                resp = await self._run_in_thread(genai.GenerativeModel('gemini-1.5-pro').generate_content, prompt)
                if getattr(resp, 'text', None):
                    return str(resp.text)[:1000]
        except Exception as e:
            logger.debug(f"Gemini insight failed: {e}")
        
        try:
            if self._groq_client:
                comp = await self._run_in_thread(self._groq_client.chat.completions.create,
                                                model="llama-3.3-70b-versatile", 
                                                messages=[{"role": "user", "content": prompt}],
                                                temperature=0.1,
                                                max_tokens=500)
                content = comp.choices[0].message.content if comp and comp.choices else None
                if content:
                    return str(content)[:1000]
        except Exception as e:
            logger.debug(f"Groq insight failed: {e}")
        
        return None

    async def _run_in_thread(self, fn, *args, **kwargs):
        """Run function in thread pool"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

# Global engine instance
_industry_engine = None

async def get_industry_analysis_engine(db: AsyncIOMotorDatabase) -> IndustrySpecificAnalysisEngine:
    """Get global industry analysis engine instance"""
    global _industry_engine
    if _industry_engine is None:
        _industry_engine = IndustrySpecificAnalysisEngine(db)
        await _industry_engine.initialize_collections()
    return _industry_engine