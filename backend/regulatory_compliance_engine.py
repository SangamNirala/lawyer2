"""
Regulatory Compliance Engine - Step 2 Implementation
Enhanced Contract Negotiation Agent - Regulatory Compliance Focus

Provides specialized compliance analysis for:
- GDPR (data protection)
- SOX (financial controls) 
- HIPAA (healthcare)
- Industry-specific regulations

Integrates with existing risk assessment system while maintaining modularity.
"""

import os
import uuid
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
import re
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
# Regulatory Compliance Models
# ==========================

class RegulatoryFramework(str, Enum):
    GDPR = "gdpr"                    # General Data Protection Regulation (EU)
    SOX = "sox"                      # Sarbanes-Oxley Act (US Financial)
    HIPAA = "hipaa"                  # Health Insurance Portability and Accountability Act (US Healthcare)
    CCPA = "ccpa"                    # California Consumer Privacy Act
    PCI_DSS = "pci_dss"             # Payment Card Industry Data Security Standard
    ISO_27001 = "iso_27001"          # Information Security Management
    FTC_ACT = "ftc_act"             # Federal Trade Commission Act
    GLBA = "glba"                    # Gramm-Leach-Bliley Act (Financial)

class IndustryType(str, Enum):
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    TECHNOLOGY = "technology"        # SaaS/Tech
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    GOVERNMENT = "government"

class ComplianceRiskLevel(str, Enum):
    COMPLIANT = "compliant"          # 0-2: Meets regulatory requirements
    LOW_RISK = "low_risk"            # 2-4: Minor compliance gaps
    MODERATE_RISK = "moderate_risk"  # 4-6: Some compliance issues
    HIGH_RISK = "high_risk"          # 6-8: Significant compliance gaps
    CRITICAL = "critical"            # 8-10: Major regulatory violations

class ComplianceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    framework: RegulatoryFramework
    requirement_code: str            # e.g., "GDPR Art. 6", "SOX 302", "HIPAA 164.308"
    title: str
    description: str
    applicability_conditions: List[str] = Field(default_factory=list)
    compliance_indicators: List[str] = Field(default_factory=list)
    violation_indicators: List[str] = Field(default_factory=list)
    penalty_severity: str = "medium"  # low, medium, high, critical
    remediation_actions: List[str] = Field(default_factory=list)

class ComplianceGap(BaseModel):
    gap_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requirement: ComplianceRequirement
    gap_description: str
    risk_score: float = Field(ge=0, le=10)
    impact_areas: List[str] = Field(default_factory=list)
    recommended_clauses: List[str] = Field(default_factory=list)
    remediation_timeline: str = "30_days"  # immediate, 30_days, 90_days, ongoing
    business_impact: str = "medium"        # low, medium, high, critical

class IndustryComplianceProfile(BaseModel):
    industry: IndustryType
    applicable_frameworks: List[RegulatoryFramework]
    mandatory_requirements: List[str] = Field(default_factory=list)
    optional_requirements: List[str] = Field(default_factory=list)
    industry_specific_clauses: List[str] = Field(default_factory=list)
    common_violations: List[str] = Field(default_factory=list)

# ==========================
# Input/Output Models  
# ==========================

class RegulatoryComplianceInput(BaseModel):
    session_id: str
    contract_text: Optional[str] = None
    document_id: Optional[str] = None
    target_frameworks: List[RegulatoryFramework] = Field(default_factory=list)
    industry_type: Optional[IndustryType] = None
    jurisdiction: str = "US"             # US, EU, UK, CA, AU
    business_context: Optional[Dict[str, Any]] = None
    data_processing_activities: List[str] = Field(default_factory=list)  # For GDPR
    financial_reporting: bool = False     # For SOX
    health_data_involved: bool = False    # For HIPAA

class RegulatoryComplianceResult(BaseModel):
    compliance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Overall Compliance Assessment
    overall_compliance_score: float = Field(ge=0, le=10)
    compliance_level: ComplianceRiskLevel
    confidence_score: float = Field(ge=0, le=1)
    
    # Framework-Specific Analysis
    framework_assessments: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Identified Gaps and Issues
    compliance_gaps: List[ComplianceGap] = Field(default_factory=list)
    high_priority_violations: List[str] = Field(default_factory=list)
    
    # Recommendations
    required_clauses: List[str] = Field(default_factory=list)
    suggested_amendments: List[Dict[str, str]] = Field(default_factory=list)
    compliance_checklist: List[str] = Field(default_factory=list)
    
    # Industry-Specific Insights
    industry_profile: Optional[IndustryComplianceProfile] = None
    industry_recommendations: List[str] = Field(default_factory=list)

# ==========================
# Regulatory Compliance Engine
# ==========================

class RegulatoryComplianceEngine:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._gemini_initialized = False
        self._groq_client = None
        self._maybe_init_ai()
        self._init_compliance_frameworks()

    def _maybe_init_ai(self):
        """Initialize AI clients opportunistically"""
        try:
            gem_key = os.environ.get("GEMINI_API_KEY")
            if gem_key and genai:
                genai.configure(api_key=gem_key)
                self._gemini_initialized = True
                logger.info("✅ RegulatoryEngine: Gemini ready")
        except Exception as e:
            logger.warning(f"⚠️ RegulatoryEngine: Gemini init failed: {e}")
            self._gemini_initialized = False

        try:
            groq_key = os.environ.get("GROQ_API_KEY") 
            if groq_key and Groq:
                self._groq_client = Groq(api_key=groq_key)
                logger.info("✅ RegulatoryEngine: Groq ready")
        except Exception as e:
            logger.warning(f"⚠️ RegulatoryEngine: Groq init failed: {e}")
            self._groq_client = None

    def _init_compliance_frameworks(self):
        """Initialize compliance framework knowledge base"""
        self.frameworks = {
            RegulatoryFramework.GDPR: self._init_gdpr_framework(),
            RegulatoryFramework.SOX: self._init_sox_framework(),
            RegulatoryFramework.HIPAA: self._init_hipaa_framework(),
            RegulatoryFramework.CCPA: self._init_ccpa_framework(),
            RegulatoryFramework.PCI_DSS: self._init_pci_framework(),
        }
        
        self.industry_profiles = {
            IndustryType.HEALTHCARE: self._init_healthcare_profile(),
            IndustryType.FINANCE: self._init_finance_profile(),
            IndustryType.TECHNOLOGY: self._init_technology_profile(),
        }

    def _init_gdpr_framework(self) -> List[ComplianceRequirement]:
        """Initialize GDPR compliance requirements"""
        return [
            ComplianceRequirement(
                framework=RegulatoryFramework.GDPR,
                requirement_code="GDPR Art. 6",
                title="Lawful Basis for Processing",
                description="Processing must have a lawful basis under Article 6",
                compliance_indicators=["consent", "contract necessity", "legitimate interest", "legal obligation"],
                violation_indicators=["no lawful basis", "unclear legal basis", "invalid consent"],
                penalty_severity="critical",
                remediation_actions=["Add lawful basis clause", "Implement consent mechanism", "Document legitimate interest assessment"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.GDPR,
                requirement_code="GDPR Art. 7",
                title="Conditions for Consent",
                description="Consent must be freely given, specific, informed and unambiguous",
                compliance_indicators=["clear consent language", "withdraw consent option", "separate consent"],
                violation_indicators=["forced consent", "bundled consent", "unclear consent"],
                penalty_severity="high",
                remediation_actions=["Revise consent language", "Add withdrawal mechanism", "Separate consent from other terms"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.GDPR,
                requirement_code="GDPR Art. 28",
                title="Data Processing Agreement",
                description="Data processing by third parties requires appropriate safeguards",
                compliance_indicators=["DPA clause", "processor obligations", "security measures"],
                violation_indicators=["no DPA", "insufficient processor controls", "unclear data handling"],
                penalty_severity="high",
                remediation_actions=["Add DPA clause", "Define processor obligations", "Include security requirements"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.GDPR,
                requirement_code="GDPR Art. 32",
                title="Security of Processing",
                description="Appropriate technical and organizational measures for data security",
                compliance_indicators=["encryption", "access controls", "security measures", "breach procedures"],
                violation_indicators=["no security measures", "weak security", "no breach procedures"],
                penalty_severity="high",
                remediation_actions=["Add security clause", "Define technical measures", "Include breach notification procedures"]
            )
        ]

    def _init_sox_framework(self) -> List[ComplianceRequirement]:
        """Initialize SOX compliance requirements"""
        return [
            ComplianceRequirement(
                framework=RegulatoryFramework.SOX,
                requirement_code="SOX 302",
                title="Corporate Responsibility for Financial Reports",
                description="CEO and CFO certification of financial statements accuracy",
                compliance_indicators=["financial reporting controls", "certification process", "accuracy statements"],
                violation_indicators=["no financial controls", "inadequate reporting", "false certifications"],
                penalty_severity="critical",
                remediation_actions=["Implement financial controls", "Add certification procedures", "Enhance reporting accuracy"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.SOX,
                requirement_code="SOX 404",
                title="Management Assessment of Internal Controls",
                description="Annual assessment of internal control over financial reporting",
                compliance_indicators=["internal control assessment", "management testing", "control documentation"],
                violation_indicators=["no control assessment", "inadequate testing", "poor documentation"],
                penalty_severity="high",
                remediation_actions=["Establish control framework", "Implement testing procedures", "Document controls"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.SOX,
                requirement_code="SOX 409",
                title="Real-time Disclosure",
                description="Rapid disclosure of material changes in financial condition",
                compliance_indicators=["disclosure procedures", "timely reporting", "material event identification"],
                violation_indicators=["delayed disclosure", "inadequate procedures", "missed material events"],
                penalty_severity="medium",
                remediation_actions=["Implement disclosure procedures", "Define material events", "Establish reporting timeline"]
            )
        ]

    def _init_hipaa_framework(self) -> List[ComplianceRequirement]:
        """Initialize HIPAA compliance requirements"""
        return [
            ComplianceRequirement(
                framework=RegulatoryFramework.HIPAA,
                requirement_code="HIPAA 164.308",
                title="Administrative Safeguards",
                description="Administrative actions to protect electronic PHI",
                compliance_indicators=["security officer", "workforce training", "access procedures", "contingency plan"],
                violation_indicators=["no security officer", "untrained workforce", "inadequate access controls"],
                penalty_severity="high",
                remediation_actions=["Designate security officer", "Implement training program", "Establish access procedures"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.HIPAA,
                requirement_code="HIPAA 164.310",
                title="Physical Safeguards",
                description="Physical protection of electronic information systems and equipment",
                compliance_indicators=["facility access controls", "workstation controls", "device controls"],
                violation_indicators=["unrestricted facility access", "unsecured workstations", "uncontrolled devices"],
                penalty_severity="medium",
                remediation_actions=["Implement facility controls", "Secure workstations", "Control device access"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.HIPAA,
                requirement_code="HIPAA 164.312",
                title="Technical Safeguards",
                description="Technology controls to protect and control access to electronic PHI",
                compliance_indicators=["access controls", "audit controls", "integrity controls", "encryption"],
                violation_indicators=["no access controls", "no audit logs", "unencrypted data"],
                penalty_severity="high",
                remediation_actions=["Implement access controls", "Enable audit logging", "Encrypt sensitive data"]
            ),
            ComplianceRequirement(
                framework=RegulatoryFramework.HIPAA,
                requirement_code="HIPAA 164.502",
                title="Uses and Disclosures of PHI",
                description="Permitted uses and disclosures of protected health information",
                compliance_indicators=["minimum necessary", "business associate agreement", "patient authorization"],
                violation_indicators=["excessive disclosure", "no BAA", "unauthorized use"],
                penalty_severity="critical",
                remediation_actions=["Implement minimum necessary", "Execute BAA", "Obtain patient authorization"]
            )
        ]

    def _init_ccpa_framework(self) -> List[ComplianceRequirement]:
        """Initialize CCPA compliance requirements"""
        return [
            ComplianceRequirement(
                framework=RegulatoryFramework.CCPA,
                requirement_code="CCPA 1798.100",
                title="Right to Know",
                description="Consumer right to know what personal information is collected and used",
                compliance_indicators=["privacy notice", "collection disclosure", "use disclosure"],
                violation_indicators=["no privacy notice", "unclear collection", "hidden use"],
                penalty_severity="medium",
                remediation_actions=["Create privacy notice", "Disclose collection practices", "Explain use purposes"]
            )
        ]

    def _init_pci_framework(self) -> List[ComplianceRequirement]:
        """Initialize PCI DSS compliance requirements"""
        return [
            ComplianceRequirement(
                framework=RegulatoryFramework.PCI_DSS,
                requirement_code="PCI DSS 3.4",
                title="Protect Stored Cardholder Data",
                description="Render PAN unreadable wherever it is stored",
                compliance_indicators=["encryption", "tokenization", "truncation", "hashing"],
                violation_indicators=["plaintext storage", "weak encryption", "inadequate protection"],
                penalty_severity="critical",
                remediation_actions=["Encrypt cardholder data", "Implement tokenization", "Use strong cryptography"]
            )
        ]

    def _init_healthcare_profile(self) -> IndustryComplianceProfile:
        """Initialize healthcare industry compliance profile"""
        return IndustryComplianceProfile(
            industry=IndustryType.HEALTHCARE,
            applicable_frameworks=[RegulatoryFramework.HIPAA, RegulatoryFramework.GDPR],
            mandatory_requirements=["Business Associate Agreement", "PHI safeguards", "Breach notification"],
            optional_requirements=["Additional state privacy laws", "International data transfers"],
            industry_specific_clauses=[
                "Protected Health Information (PHI) handling",
                "Business Associate Agreement (BAA)",
                "Breach notification procedures",
                "Patient consent and authorization",
                "Minimum necessary standard"
            ],
            common_violations=[
                "Missing Business Associate Agreement",
                "Inadequate PHI encryption",
                "Lack of breach notification procedures",
                "Insufficient access controls",
                "No employee training requirements"
            ]
        )

    def _init_finance_profile(self) -> IndustryComplianceProfile:
        """Initialize finance industry compliance profile"""
        return IndustryComplianceProfile(
            industry=IndustryType.FINANCE,
            applicable_frameworks=[RegulatoryFramework.SOX, RegulatoryFramework.GLBA, RegulatoryFramework.GDPR],
            mandatory_requirements=["Internal controls", "Financial reporting accuracy", "Customer privacy"],
            optional_requirements=["International compliance", "Sector-specific regulations"],
            industry_specific_clauses=[
                "Financial reporting controls",
                "Internal control certification",
                "Customer financial information protection",
                "Audit and examination rights",
                "Regulatory reporting obligations"
            ],
            common_violations=[
                "Inadequate internal controls",
                "Missing financial certifications", 
                "Insufficient customer data protection",
                "Lack of audit provisions",
                "No regulatory reporting clauses"
            ]
        )

    def _init_technology_profile(self) -> IndustryComplianceProfile:
        """Initialize technology/SaaS industry compliance profile"""
        return IndustryComplianceProfile(
            industry=IndustryType.TECHNOLOGY,
            applicable_frameworks=[RegulatoryFramework.GDPR, RegulatoryFramework.CCPA, RegulatoryFramework.ISO_27001],
            mandatory_requirements=["Data processing agreements", "Privacy policies", "Security measures"],
            optional_requirements=["Industry certifications", "International compliance frameworks"],
            industry_specific_clauses=[
                "Data Processing Agreement (DPA)",
                "Service Level Agreements (SLA)",
                "Data portability and deletion",
                "Subprocessor agreements",
                "Security incident notifications"
            ],
            common_violations=[
                "Missing or inadequate DPA",
                "Unclear data retention policies",
                "Insufficient security measures",
                "No subprocessor provisions",
                "Inadequate breach notification"
            ]
        )

    async def initialize_collections(self):
        """Initialize MongoDB collections for compliance tracking"""
        try:
            # Compliance assessments collection
            await self.db.compliance_assessments.create_index([("session_id", 1), ("created_at", -1)])
            await self.db.compliance_assessments.create_index([("compliance_id", 1)], unique=True)
            
            # Compliance gaps collection  
            await self.db.compliance_gaps.create_index([("session_id", 1), ("framework", 1)])
            await self.db.compliance_gaps.create_index([("risk_score", -1)])
            
            # Framework requirements collection
            await self.db.compliance_requirements.create_index([("framework", 1), ("requirement_code", 1)])
            
            logger.info("✅ RegulatoryEngine: collections initialized")
        except Exception as e:
            logger.error(f"❌ RegulatoryEngine: init collections error: {e}")

    async def assess_regulatory_compliance(self, input_data: RegulatoryComplianceInput) -> RegulatoryComplianceResult:
        """
        Main compliance assessment function
        
        Analyzes contract for regulatory compliance across specified frameworks
        and industry requirements.
        """
        try:
            logger.info(f"🛡️ Starting regulatory compliance assessment for session: {input_data.session_id}")
            
            # Determine applicable frameworks
            target_frameworks = input_data.target_frameworks
            if input_data.industry_type and not target_frameworks:
                # Auto-detect frameworks based on industry
                profile = self.industry_profiles.get(input_data.industry_type)
                if profile:
                    target_frameworks = profile.applicable_frameworks
            
            # Get contract text
            contract_text = await self._get_contract_text(input_data)
            
            # Assess each framework
            framework_assessments = {}
            all_gaps = []
            
            for framework in target_frameworks:
                assessment = await self._assess_framework_compliance(
                    framework, contract_text, input_data
                )
                framework_assessments[framework.value] = assessment
                all_gaps.extend(assessment.get("gaps", []))
            
            # Calculate overall compliance score
            overall_score, compliance_level = self._calculate_overall_compliance(framework_assessments)
            
            # Get industry-specific recommendations
            industry_profile = None
            industry_recommendations = []
            if input_data.industry_type:
                industry_profile = self.industry_profiles.get(input_data.industry_type)
                industry_recommendations = await self._get_industry_recommendations(
                    input_data.industry_type, all_gaps, contract_text
                )
            
            # Generate compliance result
            result = RegulatoryComplianceResult(
                session_id=input_data.session_id,
                overall_compliance_score=overall_score,
                compliance_level=compliance_level,
                confidence_score=0.85,  # Base confidence
                framework_assessments=framework_assessments,
                compliance_gaps=all_gaps,
                high_priority_violations=self._identify_high_priority_violations(all_gaps),
                required_clauses=self._generate_required_clauses(all_gaps),
                suggested_amendments=self._generate_suggested_amendments(all_gaps),
                compliance_checklist=self._generate_compliance_checklist(target_frameworks),
                industry_profile=industry_profile,
                industry_recommendations=industry_recommendations
            )
            
            # Store result in database
            await self.db.compliance_assessments.insert_one(result.model_dump())
            
            logger.info(f"✅ Compliance assessment completed: {overall_score}/10 ({compliance_level.value})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Compliance assessment error: {e}")
            raise

    async def _get_contract_text(self, input_data: RegulatoryComplianceInput) -> str:
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
            
        return "Sample contract for compliance analysis purposes."

    async def _assess_framework_compliance(
        self, framework: RegulatoryFramework, contract_text: str, input_data: RegulatoryComplianceInput
    ) -> Dict[str, Any]:
        """Assess compliance for a specific regulatory framework"""
        
        requirements = self.frameworks.get(framework, [])
        gaps = []
        compliant_requirements = []
        
        for req in requirements:
            is_compliant, gap = await self._check_requirement_compliance(req, contract_text, input_data)
            if is_compliant:
                compliant_requirements.append(req.requirement_code)
            else:
                gaps.append(gap)
        
        # Calculate framework-specific score
        total_requirements = len(requirements)
        compliant_count = len(compliant_requirements)
        compliance_percentage = (compliant_count / total_requirements * 100) if total_requirements > 0 else 100
        
        # Convert percentage to risk score (inverted)
        risk_score = max(0, 10 - (compliance_percentage / 10))
        
        return {
            "framework": framework.value,
            "total_requirements": total_requirements,
            "compliant_requirements": compliant_count,
            "compliance_percentage": compliance_percentage,
            "risk_score": round(risk_score, 2),
            "gaps": gaps,
            "compliant_items": compliant_requirements,
            "assessment_details": await self._get_framework_assessment_details(framework, contract_text)
        }

    async def _check_requirement_compliance(
        self, requirement: ComplianceRequirement, contract_text: str, input_data: RegulatoryComplianceInput
    ) -> Tuple[bool, Optional[ComplianceGap]]:
        """Check if contract meets specific compliance requirement"""
        
        contract_lower = contract_text.lower()
        
        # Check for compliance indicators
        compliance_indicators_found = 0
        for indicator in requirement.compliance_indicators:
            if indicator.lower() in contract_lower:
                compliance_indicators_found += 1
        
        # Check for violation indicators
        violation_indicators_found = 0
        for violation in requirement.violation_indicators:
            if violation.lower() in contract_lower:
                violation_indicators_found += 1
        
        # Determine compliance status
        compliance_threshold = len(requirement.compliance_indicators) * 0.5  # At least 50% indicators
        
        is_compliant = (
            compliance_indicators_found >= compliance_threshold and 
            violation_indicators_found == 0
        )
        
        if not is_compliant:
            # Calculate risk score for the gap
            gap_risk_score = min(10, (violation_indicators_found * 3) + 
                                   (max(0, len(requirement.compliance_indicators) - compliance_indicators_found) * 2))
            
            gap = ComplianceGap(
                requirement=requirement,
                gap_description=f"Contract lacks sufficient compliance with {requirement.title}",
                risk_score=gap_risk_score,
                impact_areas=[requirement.framework.value, requirement.requirement_code],
                recommended_clauses=requirement.remediation_actions,
                remediation_timeline="30_days" if requirement.penalty_severity in ["high", "critical"] else "90_days",
                business_impact=requirement.penalty_severity
            )
            return False, gap
        
        return True, None

    async def _get_framework_assessment_details(self, framework: RegulatoryFramework, contract_text: str) -> Dict[str, Any]:
        """Get detailed assessment for specific framework using AI"""
        
        prompt = f"""
        Analyze the following contract for {framework.value.upper()} compliance:
        
        Contract Text: {contract_text[:2000]}...
        
        Provide specific analysis of:
        1. Key compliance issues identified
        2. Missing required clauses
        3. Recommended improvements
        4. Compliance score (0-10)
        
        Keep response concise and actionable.
        """
        
        ai_analysis = await self._get_ai_insight(prompt)
        
        return {
            "ai_analysis": ai_analysis,
            "key_findings": await self._extract_key_findings(framework, contract_text),
            "missing_clauses": await self._identify_missing_clauses(framework, contract_text),
            "recommendations": await self._generate_framework_recommendations(framework, contract_text)
        }

    async def _extract_key_findings(self, framework: RegulatoryFramework, contract_text: str) -> List[str]:
        """Extract key compliance findings for framework"""
        findings = []
        
        if framework == RegulatoryFramework.GDPR:
            if "consent" not in contract_text.lower():
                findings.append("No explicit consent mechanism found")
            if "data processing" not in contract_text.lower():
                findings.append("Data processing terms not clearly defined")
            if "data subject rights" not in contract_text.lower():
                findings.append("Data subject rights not addressed")
        
        elif framework == RegulatoryFramework.HIPAA:
            if "protected health information" not in contract_text.lower() and "phi" not in contract_text.lower():
                findings.append("PHI handling not explicitly addressed")
            if "business associate" not in contract_text.lower():
                findings.append("Business Associate Agreement terms missing")
        
        elif framework == RegulatoryFramework.SOX:
            if "financial reporting" not in contract_text.lower():
                findings.append("Financial reporting controls not specified")
            if "internal control" not in contract_text.lower():
                findings.append("Internal control requirements not addressed")
        
        return findings[:5]  # Limit to top 5 findings

    async def _identify_missing_clauses(self, framework: RegulatoryFramework, contract_text: str) -> List[str]:
        """Identify missing regulatory clauses"""
        missing_clauses = []
        
        if framework == RegulatoryFramework.GDPR:
            gdpr_clauses = [
                "Data Processing Agreement (DPA)",
                "Lawful basis for processing",
                "Data subject rights (access, rectification, erasure)",
                "Data breach notification procedures",
                "International data transfer safeguards"
            ]
            for clause in gdpr_clauses:
                if not self._clause_present(clause, contract_text):
                    missing_clauses.append(clause)
        
        elif framework == RegulatoryFramework.HIPAA:
            hipaa_clauses = [
                "Business Associate Agreement",
                "PHI safeguard requirements",
                "Minimum necessary standard",
                "Security incident notification",
                "Return or destruction of PHI"
            ]
            for clause in hipaa_clauses:
                if not self._clause_present(clause, contract_text):
                    missing_clauses.append(clause)
        
        elif framework == RegulatoryFramework.SOX:
            sox_clauses = [
                "Internal control certification",
                "Financial reporting accuracy",
                "Audit and examination rights",
                "Regulatory compliance reporting",
                "Management certification procedures"
            ]
            for clause in sox_clauses:
                if not self._clause_present(clause, contract_text):
                    missing_clauses.append(clause)
        
        return missing_clauses

    def _clause_present(self, clause: str, contract_text: str) -> bool:
        """Check if clause is present in contract text"""
        # Simple keyword matching - could be enhanced with NLP
        keywords = clause.lower().split()
        contract_lower = contract_text.lower()
        
        # Check if at least 50% of keywords are present
        found_keywords = sum(1 for keyword in keywords if keyword in contract_lower)
        return found_keywords >= len(keywords) * 0.5

    async def _generate_framework_recommendations(self, framework: RegulatoryFramework, contract_text: str) -> List[str]:
        """Generate framework-specific recommendations"""
        recommendations = []
        
        if framework == RegulatoryFramework.GDPR:
            recommendations = [
                "Include explicit consent mechanism for personal data processing",
                "Add data subject rights clause (access, rectification, erasure, portability)",
                "Define lawful basis for each type of data processing",
                "Include data breach notification procedures (72-hour rule)",
                "Add Data Processing Agreement (DPA) for third-party processors"
            ]
        
        elif framework == RegulatoryFramework.HIPAA:
            recommendations = [
                "Execute comprehensive Business Associate Agreement (BAA)",
                "Include PHI safeguard requirements (administrative, physical, technical)",
                "Define minimum necessary standard for PHI access",
                "Add security incident notification procedures",
                "Include PHI return or destruction provisions upon contract termination"
            ]
        
        elif framework == RegulatoryFramework.SOX:
            recommendations = [
                "Include internal control certification requirements",
                "Add financial reporting accuracy and timeliness provisions",
                "Define audit and examination rights for regulatory compliance",
                "Include management certification procedures",
                "Add regulatory reporting and disclosure obligations"
            ]
        
        return recommendations[:5]  # Limit to top 5 recommendations

    def _calculate_overall_compliance(self, framework_assessments: Dict[str, Dict[str, Any]]) -> Tuple[float, ComplianceRiskLevel]:
        """Calculate overall compliance score across all frameworks"""
        
        if not framework_assessments:
            return 5.0, ComplianceRiskLevel.MODERATE_RISK
        
        # Calculate weighted average of framework scores
        total_score = 0
        total_weight = 0
        
        for framework, assessment in framework_assessments.items():
            risk_score = assessment.get("risk_score", 5.0)
            # Convert risk score to compliance score (inverted)
            compliance_score = 10 - risk_score
            
            # Weight frameworks based on criticality
            weight = 1.0
            if framework in ["gdpr", "hipaa", "sox"]:  # High-impact frameworks
                weight = 1.5
            
            total_score += compliance_score * weight
            total_weight += weight
        
        overall_score = total_score / total_weight if total_weight > 0 else 5.0
        
        # Determine compliance level
        if overall_score >= 8:
            level = ComplianceRiskLevel.COMPLIANT
        elif overall_score >= 6:
            level = ComplianceRiskLevel.LOW_RISK
        elif overall_score >= 4:
            level = ComplianceRiskLevel.MODERATE_RISK
        elif overall_score >= 2:
            level = ComplianceRiskLevel.HIGH_RISK
        else:
            level = ComplianceRiskLevel.CRITICAL
        
        return round(overall_score, 2), level

    def _identify_high_priority_violations(self, gaps: List[ComplianceGap]) -> List[str]:
        """Identify high-priority compliance violations"""
        high_priority = []
        
        for gap in gaps:
            if (gap.risk_score >= 7.0 or 
                gap.business_impact in ["high", "critical"] or
                gap.requirement.penalty_severity in ["high", "critical"]):
                
                violation_desc = f"{gap.requirement.framework.value.upper()} - {gap.requirement.title}: {gap.gap_description}"
                high_priority.append(violation_desc)
        
        return high_priority[:10]  # Limit to top 10

    def _generate_required_clauses(self, gaps: List[ComplianceGap]) -> List[str]:
        """Generate list of required clauses to address compliance gaps"""
        required_clauses = []
        
        for gap in gaps:
            for clause in gap.recommended_clauses:
                if clause not in required_clauses:
                    required_clauses.append(clause)
        
        return required_clauses[:15]  # Limit to top 15

    def _generate_suggested_amendments(self, gaps: List[ComplianceGap]) -> List[Dict[str, str]]:
        """Generate suggested contract amendments"""
        amendments = []
        
        for gap in gaps[:5]:  # Top 5 gaps
            amendment = {
                "section": f"{gap.requirement.framework.value.upper()} Compliance",
                "current": "Missing or insufficient compliance provision",
                "suggested": f"Add clause addressing: {gap.requirement.title}",
                "rationale": gap.gap_description,
                "priority": gap.business_impact
            }
            amendments.append(amendment)
        
        return amendments

    def _generate_compliance_checklist(self, frameworks: List[RegulatoryFramework]) -> List[str]:
        """Generate compliance checklist for frameworks"""
        checklist = []
        
        for framework in frameworks:
            if framework == RegulatoryFramework.GDPR:
                checklist.extend([
                    "✓ Identify lawful basis for data processing",
                    "✓ Implement data subject rights procedures", 
                    "✓ Execute Data Processing Agreements with processors",
                    "✓ Establish data breach notification procedures",
                    "✓ Document legitimate interest assessments"
                ])
            
            elif framework == RegulatoryFramework.HIPAA:
                checklist.extend([
                    "✓ Execute Business Associate Agreement",
                    "✓ Implement administrative safeguards",
                    "✓ Establish physical safeguards",
                    "✓ Deploy technical safeguards",
                    "✓ Define minimum necessary policies"
                ])
            
            elif framework == RegulatoryFramework.SOX:
                checklist.extend([
                    "✓ Design internal control framework",
                    "✓ Implement management testing procedures",
                    "✓ Establish certification processes",
                    "✓ Define financial reporting controls",
                    "✓ Document control assessments"
                ])
        
        return list(set(checklist))[:20]  # Remove duplicates, limit to 20

    async def _get_industry_recommendations(
        self, industry: IndustryType, gaps: List[ComplianceGap], contract_text: str
    ) -> List[str]:
        """Generate industry-specific compliance recommendations"""
        
        profile = self.industry_profiles.get(industry)
        if not profile:
            return []
        
        recommendations = []
        
        # Add industry-specific clause recommendations
        for clause in profile.industry_specific_clauses:
            if not self._clause_present(clause, contract_text):
                recommendations.append(f"Add industry-standard clause: {clause}")
        
        # Add recommendations based on common violations
        gap_areas = [gap.requirement.framework.value for gap in gaps]
        for violation in profile.common_violations:
            relevant = any(framework.value in violation.lower() for framework in profile.applicable_frameworks
                          if framework.value in gap_areas)
            if relevant:
                recommendations.append(f"Address common industry violation: {violation}")
        
        return recommendations[:8]  # Limit to top 8

    async def _get_ai_insight(self, prompt: str) -> Optional[str]:
        """Get AI insight for compliance analysis"""
        try:
            if self._gemini_initialized and genai:
                resp = await self._run_in_thread(genai.GenerativeModel('gemini-1.5-pro').generate_content, prompt)
                if getattr(resp, 'text', None):
                    return str(resp.text)[:800]
        except Exception as e:
            logger.debug(f"Gemini insight failed: {e}")
        
        try:
            if self._groq_client:
                comp = await self._run_in_thread(self._groq_client.chat.completions.create,
                                                model="llama-3.3-70b-versatile", 
                                                messages=[{"role": "user", "content": prompt}],
                                                temperature=0.1,
                                                max_tokens=400)
                content = comp.choices[0].message.content if comp and comp.choices else None
                if content:
                    return str(content)[:800]
        except Exception as e:
            logger.debug(f"Groq insight failed: {e}")
        
        return None

    async def _run_in_thread(self, fn, *args, **kwargs):
        """Run function in thread pool"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))

# Global engine instance
_regulatory_engine = None

async def get_regulatory_compliance_engine(db: AsyncIOMotorDatabase) -> RegulatoryComplianceEngine:
    """Get global regulatory compliance engine instance"""
    global _regulatory_engine
    if _regulatory_engine is None:
        _regulatory_engine = RegulatoryComplianceEngine(db)
        await _regulatory_engine.initialize_collections()
    return _regulatory_engine