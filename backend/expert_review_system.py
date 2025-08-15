"""
Expert Review Integration System (Simulated)
Automated expert routing, priority queuing, and review tracking
"""

import asyncio
import json
import logging
import hashlib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

import google.generativeai as genai
from groq import Groq
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI clients
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

class ExpertDomain(Enum):
    """Legal expert domains"""
    CONTRACT_LAW = "contract_law"
    CONSTITUTIONAL_LAW = "constitutional_law"
    EMPLOYMENT_LAW = "employment_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CORPORATE_LAW = "corporate_law"
    LITIGATION = "litigation"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    GENERAL_PRACTICE = "general_practice"

class ReviewPriority(Enum):
    """Review priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReviewStatus(Enum):
    """Review status options"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

@dataclass
class SimulatedExpert:
    """Simulated expert profile for review system"""
    expert_id: str
    name: str
    domain: ExpertDomain
    experience_years: int
    specializations: List[str]
    current_workload: int  # Number of pending reviews
    average_review_time: float  # Hours
    success_rate: float  # 0.0 to 1.0
    is_available: bool = True

@dataclass
class ExpertReviewRequest:
    """Expert review request structure"""
    review_id: str
    analysis_id: str
    legal_domain: str
    complexity_score: float
    priority: ReviewPriority
    validation_issues: List[str]
    content_summary: str
    requested_at: datetime
    estimated_completion: Optional[datetime] = None

@dataclass
class ExpertReviewResult:
    """Expert review result structure"""
    review_id: str
    expert_id: str
    expert_domain: str
    accuracy_assessment: float  # 0.0 to 1.0
    expert_corrections: List[Dict[str, Any]]
    expert_comments: str
    validation_outcome: str  # "approved", "needs_revision", "rejected"
    reviewed_at: datetime
    review_duration: float  # Hours

class ExpertReviewSystem:
    """Simulated expert review system with automated routing"""
    
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.simulated_experts = self._initialize_simulated_experts()
        
    async def initialize(self):
        """Initialize database connection"""
        try:
            mongo_url = os.environ.get('MONGO_URL')
            if not mongo_url:
                raise ValueError("MONGO_URL not found in environment variables")
            
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.db = self.mongo_client[os.environ.get('DB_NAME', 'legalmate')]
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            logger.info("✅ Expert Review System initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing expert review system: {e}")
            raise
    
    def _initialize_simulated_experts(self) -> List[SimulatedExpert]:
        """Initialize pool of simulated legal experts"""
        experts = [
            SimulatedExpert(
                expert_id="expert_contract_001",
                name="Dr. Sarah Johnson",
                domain=ExpertDomain.CONTRACT_LAW,
                experience_years=15,
                specializations=["Commercial Contracts", "Employment Agreements", "IP Licensing"],
                current_workload=3,
                average_review_time=4.5,
                success_rate=0.92
            ),
            SimulatedExpert(
                expert_id="expert_constitutional_001",
                name="Prof. Michael Chen",
                domain=ExpertDomain.CONSTITUTIONAL_LAW,
                experience_years=20,
                specializations=["Due Process", "Equal Protection", "First Amendment"],
                current_workload=2,
                average_review_time=6.0,
                success_rate=0.95
            ),
            SimulatedExpert(
                expert_id="expert_employment_001",
                name="Jessica Williams",
                domain=ExpertDomain.EMPLOYMENT_LAW,
                experience_years=12,
                specializations=["Discrimination", "Wrongful Termination", "Wage & Hour"],
                current_workload=4,
                average_review_time=3.5,
                success_rate=0.88
            ),
            SimulatedExpert(
                expert_id="expert_ip_001",
                name="David Rodriguez",
                domain=ExpertDomain.INTELLECTUAL_PROPERTY,
                experience_years=18,
                specializations=["Patents", "Trademarks", "Trade Secrets"],
                current_workload=1,
                average_review_time=5.0,
                success_rate=0.94
            ),
            SimulatedExpert(
                expert_id="expert_corporate_001",
                name="Emily Zhang",
                domain=ExpertDomain.CORPORATE_LAW,
                experience_years=14,
                specializations=["M&A", "Securities", "Corporate Governance"],
                current_workload=2,
                average_review_time=4.0,
                success_rate=0.90
            ),
            SimulatedExpert(
                expert_id="expert_litigation_001",
                name="Robert Martinez",
                domain=ExpertDomain.LITIGATION,
                experience_years=16,
                specializations=["Civil Litigation", "Business Disputes", "Appeals"],
                current_workload=3,
                average_review_time=5.5,
                success_rate=0.91
            ),
            SimulatedExpert(
                expert_id="expert_regulatory_001",
                name="Lisa Thompson",
                domain=ExpertDomain.REGULATORY_COMPLIANCE,
                experience_years=13,
                specializations=["Healthcare Compliance", "Financial Regulation", "Environmental Law"],
                current_workload=2,
                average_review_time=4.5,
                success_rate=0.89
            ),
            SimulatedExpert(
                expert_id="expert_general_001",
                name="James Wilson",
                domain=ExpertDomain.GENERAL_PRACTICE,
                experience_years=10,
                specializations=["General Practice", "Small Business Law", "Real Estate"],
                current_workload=5,
                average_review_time=3.0,
                success_rate=0.85
            )
        ]
        
        return experts
    
    async def request_expert_review(
        self, 
        analysis_id: str,
        content: str,
        legal_domain: str,
        validation_issues: List[str],
        complexity_score: float
    ) -> Dict[str, Any]:
        """Request expert review with automated routing"""
        
        try:
            # Generate review ID
            review_id = f"review_{analysis_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine priority based on complexity and issues
            priority = self._determine_priority(validation_issues, complexity_score)
            
            # Route to appropriate expert
            assigned_expert = await self._route_to_expert(legal_domain, priority, complexity_score)
            
            if not assigned_expert:
                return {
                    "success": False,
                    "error": "No available expert found for this domain",
                    "review_id": review_id
                }
            
            # Create review request
            review_request = ExpertReviewRequest(
                review_id=review_id,
                analysis_id=analysis_id,
                legal_domain=legal_domain,
                complexity_score=complexity_score,
                priority=priority,
                validation_issues=validation_issues,
                content_summary=content[:500],  # First 500 chars as summary
                requested_at=datetime.utcnow(),
                estimated_completion=datetime.utcnow() + timedelta(hours=assigned_expert.average_review_time)
            )
            
            # Store review request in database
            await self._store_review_request(review_request, assigned_expert)
            
            # Update expert workload
            assigned_expert.current_workload += 1
            
            logger.info(f"📋 Expert review requested: {review_id} assigned to {assigned_expert.name}")
            
            return {
                "success": True,
                "review_id": review_id,
                "assigned_expert": {
                    "expert_id": assigned_expert.expert_id,
                    "name": assigned_expert.name,
                    "domain": assigned_expert.domain.value,
                    "estimated_completion": review_request.estimated_completion.isoformat()
                },
                "priority": priority.value,
                "status": ReviewStatus.ASSIGNED.value
            }
            
        except Exception as e:
            logger.error(f"Error requesting expert review: {e}")
            return {
                "success": False,
                "error": str(e),
                "review_id": ""
            }
    
    async def simulate_expert_review_completion(self, review_id: str) -> ExpertReviewResult:
        """Simulate completion of expert review (for demonstration)"""
        
        try:
            # Retrieve review request from database
            review_doc = await self.db.expert_reviews.find_one({"review_id": review_id})
            
            if not review_doc:
                raise ValueError(f"Review {review_id} not found")
            
            # Find assigned expert
            assigned_expert = next(
                (expert for expert in self.simulated_experts 
                 if expert.expert_id == review_doc.get("assigned_expert_id")),
                None
            )
            
            if not assigned_expert:
                raise ValueError("Assigned expert not found")
            
            # Simulate expert review using AI
            expert_analysis = await self._simulate_expert_analysis(
                review_doc.get("content_summary", ""),
                review_doc.get("validation_issues", []),
                assigned_expert
            )
            
            # Create review result
            review_result = ExpertReviewResult(
                review_id=review_id,
                expert_id=assigned_expert.expert_id,
                expert_domain=assigned_expert.domain.value,
                accuracy_assessment=expert_analysis["accuracy_assessment"],
                expert_corrections=expert_analysis["corrections"],
                expert_comments=expert_analysis["comments"],
                validation_outcome=expert_analysis["outcome"],
                reviewed_at=datetime.utcnow(),
                review_duration=assigned_expert.average_review_time + (
                    -1 + 2 * hash(review_id) % 100 / 100  # Add some randomness
                )
            )
            
            # Update database with completed review
            await self._store_review_result(review_result)
            
            # Update expert workload
            assigned_expert.current_workload = max(0, assigned_expert.current_workload - 1)
            
            logger.info(f"✅ Expert review completed: {review_id} by {assigned_expert.name}")
            
            return review_result
            
        except Exception as e:
            logger.error(f"Error simulating expert review completion: {e}")
            raise
    
    async def get_review_status(self, review_id: str) -> Dict[str, Any]:
        """Get current status of expert review"""
        try:
            review_doc = await self.db.expert_reviews.find_one({"review_id": review_id})
            
            if not review_doc:
                return {"error": "Review not found", "status": "not_found"}
            
            return {
                "review_id": review_id,
                "status": review_doc.get("status", "unknown"),
                "assigned_expert": review_doc.get("assigned_expert_name", "Unknown"),
                "domain": review_doc.get("expert_domain", "Unknown"),
                "priority": review_doc.get("priority", "unknown"),
                "created_at": review_doc.get("created_at"),
                "estimated_completion": review_doc.get("estimated_completion"),
                "completed_at": review_doc.get("completed_at"),
                "accuracy_assessment": review_doc.get("accuracy_assessment"),
                "validation_outcome": review_doc.get("validation_outcome")
            }
            
        except Exception as e:
            logger.error(f"Error getting review status: {e}")
            return {"error": str(e), "status": "error"}
    
    async def get_pending_reviews(self, expert_domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of pending expert reviews"""
        try:
            filter_criteria = {"status": {"$in": ["pending", "assigned", "in_progress"]}}
            
            if expert_domain:
                filter_criteria["expert_domain"] = expert_domain
            
            cursor = self.db.expert_reviews.find(filter_criteria).sort("created_at", -1)
            reviews = await cursor.to_list(length=50)  # Limit to 50 reviews
            
            # Convert ObjectIds to strings
            for review in reviews:
                review["_id"] = str(review["_id"])
            
            return reviews
            
        except Exception as e:
            logger.error(f"Error getting pending reviews: {e}")
            return []
    
    def _determine_priority(self, validation_issues: List[str], complexity_score: float) -> ReviewPriority:
        """Determine review priority based on issues and complexity"""
        
        # Critical priority triggers
        critical_keywords = ["constitutional", "overturned", "precedent conflict", "authority conflict"]
        if any(keyword in " ".join(validation_issues).lower() for keyword in critical_keywords):
            return ReviewPriority.CRITICAL
        
        # High priority for complex cases or multiple issues
        if complexity_score > 0.8 or len(validation_issues) > 5:
            return ReviewPriority.HIGH
        
        # Medium priority for moderate complexity or some issues
        if complexity_score > 0.6 or len(validation_issues) > 2:
            return ReviewPriority.MEDIUM
        
        return ReviewPriority.LOW
    
    async def _route_to_expert(
        self, legal_domain: str, priority: ReviewPriority, complexity_score: float
    ) -> Optional[SimulatedExpert]:
        """Route review to most appropriate available expert"""
        
        # Map legal domain to expert domain
        domain_mapping = {
            "contract_law": ExpertDomain.CONTRACT_LAW,
            "constitutional_law": ExpertDomain.CONSTITUTIONAL_LAW,
            "employment_law": ExpertDomain.EMPLOYMENT_LAW,
            "intellectual_property": ExpertDomain.INTELLECTUAL_PROPERTY,
            "corporate_law": ExpertDomain.CORPORATE_LAW,
            "tort_law": ExpertDomain.LITIGATION,
            "general_law": ExpertDomain.GENERAL_PRACTICE
        }
        
        target_domain = domain_mapping.get(legal_domain, ExpertDomain.GENERAL_PRACTICE)
        
        # Find available experts in the domain
        available_experts = [
            expert for expert in self.simulated_experts
            if expert.domain == target_domain and expert.is_available and expert.current_workload < 8
        ]
        
        # If no domain-specific experts available, try general practice
        if not available_experts and target_domain != ExpertDomain.GENERAL_PRACTICE:
            available_experts = [
                expert for expert in self.simulated_experts
                if expert.domain == ExpertDomain.GENERAL_PRACTICE and expert.is_available and expert.current_workload < 8
            ]
        
        if not available_experts:
            return None
        
        # Select best expert based on criteria
        def expert_score(expert: SimulatedExpert) -> float:
            # Score based on success rate, workload, and experience
            workload_penalty = expert.current_workload * 0.1
            experience_bonus = min(expert.experience_years * 0.01, 0.15)
            success_bonus = expert.success_rate * 0.3
            
            return success_bonus + experience_bonus - workload_penalty
        
        # Sort experts by score and return the best one
        available_experts.sort(key=expert_score, reverse=True)
        return available_experts[0]
    
    async def _simulate_expert_analysis(
        self, content_summary: str, validation_issues: List[str], expert: SimulatedExpert
    ) -> Dict[str, Any]:
        """Simulate expert analysis using AI to generate realistic review"""
        
        try:
            # Use Gemini to simulate expert review
            expert_prompt = f"""
            You are {expert.name}, a legal expert with {expert.experience_years} years of experience 
            in {expert.domain.value} with specializations in: {', '.join(expert.specializations)}.
            
            Review this legal analysis and provide expert assessment:
            
            CONTENT SUMMARY: {content_summary}
            VALIDATION ISSUES IDENTIFIED: {validation_issues}
            
            As an expert, provide:
            1. Accuracy assessment (0.0-1.0 score)
            2. Specific corrections needed
            3. Expert comments on the analysis quality
            4. Overall validation outcome (approved/needs_revision/rejected)
            
            Provide JSON response:
            {{
                "accuracy_assessment": 0.0-1.0,
                "corrections": [
                    {{
                        "issue": "description of issue",
                        "correction": "how to fix it",
                        "severity": "low|medium|high"
                    }}
                ],
                "comments": "detailed expert comments",
                "outcome": "approved|needs_revision|rejected",
                "confidence": "expert confidence in assessment"
            }}
            
            Be thorough but realistic based on the expert's success rate of {expert.success_rate}.
            """
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(expert_prompt)
            
            # Parse response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback result
                result = {
                    "accuracy_assessment": expert.success_rate,
                    "corrections": [{"issue": "Analysis needs general improvement", "correction": "Review legal reasoning", "severity": "medium"}],
                    "comments": "Analysis requires some improvements but shows good understanding of legal principles.",
                    "outcome": "needs_revision",
                    "confidence": "high"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error simulating expert analysis: {e}")
            # Return default analysis
            return {
                "accuracy_assessment": 0.7,
                "corrections": [{"issue": "System error in analysis", "correction": "Manual review required", "severity": "high"}],
                "comments": "Expert review system encountered an error. Manual review recommended.",
                "outcome": "needs_revision",
                "confidence": "low"
            }
    
    async def _store_review_request(self, request: ExpertReviewRequest, expert: SimulatedExpert):
        """Store expert review request in database"""
        if self.db is None:
            return
        
        try:
            await self.db.expert_reviews.insert_one({
                "review_id": request.review_id,
                "analysis_id": request.analysis_id,
                "legal_domain": request.legal_domain,
                "complexity_score": request.complexity_score,
                "priority": request.priority.value,
                "validation_issues": request.validation_issues,
                "content_summary": request.content_summary,
                "requested_at": request.requested_at,
                "estimated_completion": request.estimated_completion,
                "assigned_expert_id": expert.expert_id,
                "assigned_expert_name": expert.name,
                "expert_domain": expert.domain.value,
                "status": ReviewStatus.ASSIGNED.value
            })
            
        except Exception as e:
            logger.error(f"Error storing review request: {e}")
    
    async def _store_review_result(self, result: ExpertReviewResult):
        """Store expert review result in database"""
        if not self.db:
            return
        
        try:
            await self.db.expert_reviews.update_one(
                {"review_id": result.review_id},
                {
                    "$set": {
                        "status": ReviewStatus.COMPLETED.value,
                        "accuracy_assessment": result.accuracy_assessment,
                        "expert_corrections": result.expert_corrections,
                        "expert_comments": result.expert_comments,
                        "validation_outcome": result.validation_outcome,
                        "completed_at": result.reviewed_at,
                        "review_duration": result.review_duration
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing review result: {e}")

# Global instance
_expert_review_system = None

async def get_expert_review_system():
    """Get global expert review system instance"""
    global _expert_review_system
    if _expert_review_system is None:
        _expert_review_system = ExpertReviewSystem()
        await _expert_review_system.initialize()
    return _expert_review_system