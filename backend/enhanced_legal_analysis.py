"""
Enhanced Legal Analysis Module for Contract Negotiation

This module provides sophisticated document analysis capabilities including:
- Document upload and processing (PDF, DOCX, TXT)
- Clause-by-clause analysis and risk assessment
- Contract comparison and gap analysis
- Intelligent recommendations and risk scoring
"""

import os
import logging
import asyncio
import re
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import magic
import fitz  # PyMuPDF for PDF processing
from docx import Document
import google.generativeai as genai
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    CONTRACT = "contract"
    AGREEMENT = "agreement"
    AMENDMENT = "amendment"
    ADDENDUM = "addendum"
    NDA = "nda"
    UNKNOWN = "unknown"

class ClauseType(Enum):
    PAYMENT_TERMS = "payment_terms"
    LIABILITY = "liability"
    TERMINATION = "termination"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    FORCE_MAJEURE = "force_majeure"
    DISPUTE_RESOLUTION = "dispute_resolution"
    GOVERNING_LAW = "governing_law"
    WARRANTIES = "warranties"
    INDEMNIFICATION = "indemnification"
    SERVICE_LEVEL = "service_level"
    SCOPE_OF_WORK = "scope_of_work"
    DELIVERABLES = "deliverables"
    TIMELINE = "timeline"
    GENERAL = "general"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DocumentMetadata:
    """Metadata for analyzed documents"""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    processing_timestamp: Optional[datetime] = None
    document_type: DocumentType = DocumentType.UNKNOWN
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    parties: List[str] = field(default_factory=list)
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    jurisdiction: Optional[str] = None

@dataclass
class ClauseAnalysis:
    """Analysis results for individual contract clauses"""
    clause_id: str
    clause_type: ClauseType
    content: str
    risk_level: RiskLevel
    risk_score: float  # 0.0 to 1.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    market_standard_comparison: Optional[str] = None
    suggested_alternatives: List[str] = field(default_factory=list)
    legal_precedents: List[str] = field(default_factory=list)
    compliance_notes: List[str] = field(default_factory=list)

@dataclass
class DocumentAnalysisResult:
    """Complete analysis results for a document"""
    document_id: str
    metadata: DocumentMetadata
    extracted_text: str
    clause_analyses: List[ClauseAnalysis] = field(default_factory=list)
    overall_risk_score: float = 0.0
    key_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    negotiation_priorities: List[str] = field(default_factory=list)
    missing_clauses: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContractComparison:
    """Results from comparing two contracts"""
    comparison_id: str
    document1_id: str
    document2_id: str
    differences: List[Dict[str, Any]] = field(default_factory=list)
    gap_analysis: List[str] = field(default_factory=list)
    risk_comparison: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    preferred_clauses: List[Dict[str, Any]] = field(default_factory=list)
    comparison_timestamp: datetime = field(default_factory=datetime.utcnow)

class EnhancedLegalAnalyzer:
    """Enhanced legal document analyzer for contract negotiation"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize AI clients
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        
        # Configure Gemini
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                logger.info("✅ Enhanced Legal Analyzer: Gemini AI initialized")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced Legal Analyzer: Failed to initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Configure Groq
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Enhanced Legal Analyzer: Groq AI initialized")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced Legal Analyzer: Failed to initialize Groq: {e}")
                self.groq_client = None
        else:
            self.groq_client = None
        
        logger.info("🔍 Enhanced Legal Analyzer initialized")

    async def process_document(self, file_content: bytes, filename: str, content_type: str) -> DocumentAnalysisResult:
        """Process uploaded document and perform comprehensive analysis"""
        try:
            logger.info(f"📄 Processing document: {filename}")
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Create metadata
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                file_type=content_type,
                file_size=len(file_content),
                upload_timestamp=datetime.utcnow()
            )
            
            # Extract text from document
            extracted_text = await self._extract_text(file_content, content_type)
            if not extracted_text:
                raise ValueError("Could not extract text from document")
            
            # Update metadata with document analysis
            metadata.word_count = len(extracted_text.split())
            metadata.document_type = self._detect_document_type(extracted_text)
            metadata.parties = self._extract_parties(extracted_text)
            metadata.effective_date = self._extract_date(extracted_text, "effective")
            metadata.expiration_date = self._extract_date(extracted_text, "expiration")
            metadata.jurisdiction = self._extract_jurisdiction(extracted_text)
            metadata.processing_timestamp = datetime.utcnow()
            
            # Perform clause-by-clause analysis
            clause_analyses = await self._analyze_clauses(extracted_text, document_id)
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk(clause_analyses)
            
            # Generate document-level recommendations
            key_issues, recommendations, negotiation_priorities, missing_clauses = await self._generate_document_recommendations(
                extracted_text, clause_analyses, metadata
            )
            
            # Create analysis result
            analysis_result = DocumentAnalysisResult(
                document_id=document_id,
                metadata=metadata,
                extracted_text=extracted_text,
                clause_analyses=clause_analyses,
                overall_risk_score=overall_risk_score,
                key_issues=key_issues,
                recommendations=recommendations,
                negotiation_priorities=negotiation_priorities,
                missing_clauses=missing_clauses
            )
            
            # Store in database
            await self._store_analysis_result(analysis_result)
            
            logger.info(f"✅ Document analysis completed: {filename}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            raise

    async def _extract_text(self, file_content: bytes, content_type: str) -> str:
        """Extract text from various document formats"""
        try:
            if content_type == 'application/pdf':
                return self._extract_pdf_text(file_content)
            elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                 'application/msword']:
                return self._extract_docx_text(file_content)
            elif content_type.startswith('text/'):
                return file_content.decode('utf-8')
            else:
                # Try to detect content type using magic
                file_type = magic.from_buffer(file_content, mime=True)
                if file_type == 'application/pdf':
                    return self._extract_pdf_text(file_content)
                elif 'word' in file_type.lower():
                    return self._extract_docx_text(file_content)
                else:
                    # Fallback to text
                    return file_content.decode('utf-8', errors='ignore')
                    
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {e}")
            raise

    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            # Extract text
            doc = fitz.open(temp_file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # Clean up
            os.unlink(temp_file_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"❌ PDF text extraction failed: {e}")
            raise

    def _extract_docx_text(self, docx_content: bytes) -> str:
        """Extract text from DOCX using python-docx"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(docx_content)
                temp_file_path = temp_file.name
            
            # Extract text
            doc = Document(temp_file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Clean up
            os.unlink(temp_file_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"❌ DOCX text extraction failed: {e}")
            raise

    def _detect_document_type(self, text: str) -> DocumentType:
        """Detect document type based on content analysis"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['non-disclosure', 'nda', 'confidentiality agreement']):
            return DocumentType.NDA
        elif any(term in text_lower for term in ['amendment', 'amend', 'modify']):
            return DocumentType.AMENDMENT
        elif any(term in text_lower for term in ['addendum', 'supplement']):
            return DocumentType.ADDENDUM
        elif any(term in text_lower for term in ['contract', 'agreement']):
            if 'service' in text_lower or 'consulting' in text_lower:
                return DocumentType.CONTRACT
            else:
                return DocumentType.AGREEMENT
        else:
            return DocumentType.UNKNOWN

    def _extract_parties(self, text: str) -> List[str]:
        """Extract party names from contract text"""
        parties = []
        
        # Common patterns for party identification
        patterns = [
            r'between\s+([^,]+?)\s+(?:and|&)\s+([^,]+?)(?:\s|,|$)',
            r'party\s+(?:of\s+the\s+)?first\s+part[:\s]+([^,\n]+)',
            r'party\s+(?:of\s+the\s+)?second\s+part[:\s]+([^,\n]+)',
            r'contractor[:\s]+([^,\n]+)',
            r'client[:\s]+([^,\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                for group in match.groups():
                    if group:
                        party = group.strip().strip('"\'()[]{}')
                        if len(party) > 3 and party not in parties:
                            parties.append(party)
        
        return parties[:10]  # Limit to 10 parties

    def _extract_date(self, text: str, date_type: str) -> Optional[str]:
        """Extract specific dates from contract text"""
        patterns = {
            'effective': [
                rf'effective\s+date[:\s]+([^,\n]+)',
                rf'commencing\s+on[:\s]+([^,\n]+)',
                rf'beginning[:\s]+([^,\n]+)'
            ],
            'expiration': [
                rf'expir(?:ation|es?)\s+(?:date)?[:\s]+([^,\n]+)',
                rf'terminat(?:ion|es?)\s+(?:date)?[:\s]+([^,\n]+)',
                rf'end(?:ing)?\s+(?:date)?[:\s]+([^,\n]+)'
            ]
        }
        
        for pattern in patterns.get(date_type, []):
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                date_str = match.group(1).strip()
                # Basic date format cleaning
                date_str = re.sub(r'[^\w\s,/-]', '', date_str)
                return date_str[:50]  # Limit length
        
        return None

    def _extract_jurisdiction(self, text: str) -> Optional[str]:
        """Extract jurisdiction information from contract text"""
        patterns = [
            r'governed\s+by\s+(?:the\s+)?laws?\s+of\s+([^,\n]+)',
            r'jurisdiction\s+of\s+([^,\n]+)',
            r'courts?\s+of\s+([^,\n]+)',
            r'state\s+of\s+([^,\n]+)(?:\s+law)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                jurisdiction = match.group(1).strip()
                # Clean up common suffixes
                jurisdiction = re.sub(r'\s+shall\s+have.*$', '', jurisdiction, flags=re.IGNORECASE)
                return jurisdiction[:100]  # Limit length
        
        return None

    async def _analyze_clauses(self, text: str, document_id: str) -> List[ClauseAnalysis]:
        """Perform detailed clause-by-clause analysis"""
        try:
            logger.info(f"🔍 Analyzing clauses for document {document_id}")
            
            # Split document into clauses
            clauses = self._split_into_clauses(text)
            
            clause_analyses = []
            for i, clause_text in enumerate(clauses):
                if len(clause_text.strip()) < 50:  # Skip very short clauses
                    continue
                
                # Analyze individual clause
                clause_analysis = await self._analyze_individual_clause(
                    clause_text, f"{document_id}_clause_{i}", document_id
                )
                if clause_analysis:
                    clause_analyses.append(clause_analysis)
            
            logger.info(f"✅ Analyzed {len(clause_analyses)} clauses")
            return clause_analyses
            
        except Exception as e:
            logger.error(f"❌ Clause analysis failed: {e}")
            return []

    def _split_into_clauses(self, text: str) -> List[str]:
        """Split document text into individual clauses"""
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text)
        
        # Split by common clause delimiters
        clause_patterns = [
            r'\n\s*\d+\.\s+',  # Numbered clauses
            r'\n\s*\([a-z]\)\s+',  # Letter sub-clauses
            r'\n\s*[A-Z][A-Z\s]{2,}:',  # All caps headers
            r'\n\s*Section\s+\d+',  # Section headers
            r'\n\s*Article\s+\d+',  # Article headers
        ]
        
        # Split text into potential clauses
        clauses = [text]  # Start with full text
        
        for pattern in clause_patterns:
            new_clauses = []
            for clause in clauses:
                splits = re.split(pattern, clause)
                new_clauses.extend([s.strip() for s in splits if s.strip()])
            clauses = new_clauses
        
        # Filter out very short or empty clauses
        filtered_clauses = []
        for clause in clauses:
            if len(clause.strip()) >= 100:  # Minimum clause length
                filtered_clauses.append(clause.strip())
        
        return filtered_clauses[:50]  # Limit to 50 clauses for performance

    async def _analyze_individual_clause(self, clause_text: str, clause_id: str, document_id: str) -> Optional[ClauseAnalysis]:
        """Analyze individual clause for risks and recommendations"""
        try:
            # Determine clause type
            clause_type = self._classify_clause_type(clause_text)
            
            # Generate AI analysis
            analysis_prompt = f"""
            You are an expert contract attorney analyzing the following contract clause. Provide a detailed legal analysis.

            CLAUSE TEXT:
            {clause_text}

            ANALYSIS REQUIREMENTS:
            1. Risk Assessment (0.0 to 1.0 scale where 1.0 is highest risk)
            2. Specific legal issues or concerns
            3. Recommendations for improvement
            4. Market standard comparison
            5. Alternative clause suggestions
            6. Compliance considerations

            Respond in JSON format:
            {{
                "risk_score": 0.0-1.0,
                "risk_level": "low|medium|high|critical",
                "issues": ["issue1", "issue2"],
                "recommendations": ["recommendation1", "recommendation2"],
                "market_standard_comparison": "comparison text",
                "suggested_alternatives": ["alternative1", "alternative2"],
                "compliance_notes": ["note1", "note2"]
            }}
            """
            
            ai_response = await self._get_ai_analysis(analysis_prompt)
            
            if ai_response:
                try:
                    analysis_data = json.loads(ai_response)
                    
                    return ClauseAnalysis(
                        clause_id=clause_id,
                        clause_type=clause_type,
                        content=clause_text,
                        risk_level=RiskLevel(analysis_data.get('risk_level', 'medium')),
                        risk_score=float(analysis_data.get('risk_score', 0.5)),
                        issues=analysis_data.get('issues', []),
                        recommendations=analysis_data.get('recommendations', []),
                        market_standard_comparison=analysis_data.get('market_standard_comparison'),
                        suggested_alternatives=analysis_data.get('suggested_alternatives', []),
                        compliance_notes=analysis_data.get('compliance_notes', [])
                    )
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"⚠️ Failed to parse AI analysis response: {e}")
                    # Return basic analysis
                    return ClauseAnalysis(
                        clause_id=clause_id,
                        clause_type=clause_type,
                        content=clause_text,
                        risk_level=RiskLevel.MEDIUM,
                        risk_score=0.5,
                        issues=["Analysis parsing failed - manual review recommended"],
                        recommendations=["Review this clause manually for potential risks"]
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Individual clause analysis failed: {e}")
            return None

    def _classify_clause_type(self, clause_text: str) -> ClauseType:
        """Classify clause type based on content"""
        text_lower = clause_text.lower()
        
        # Define keyword patterns for each clause type
        clause_patterns = {
            ClauseType.PAYMENT_TERMS: ['payment', 'invoice', 'billing', 'fee', 'cost', 'price', 'compensation'],
            ClauseType.LIABILITY: ['liability', 'liable', 'damages', 'limitation', 'exclude', 'disclaim'],
            ClauseType.TERMINATION: ['termination', 'terminate', 'end', 'expire', 'breach', 'default'],
            ClauseType.INTELLECTUAL_PROPERTY: ['intellectual property', 'ip', 'copyright', 'patent', 'trademark', 'proprietary'],
            ClauseType.CONFIDENTIALITY: ['confidential', 'non-disclosure', 'proprietary information', 'trade secret'],
            ClauseType.FORCE_MAJEURE: ['force majeure', 'act of god', 'unforeseeable', 'beyond control'],
            ClauseType.DISPUTE_RESOLUTION: ['dispute', 'arbitration', 'mediation', 'litigation', 'court', 'resolution'],
            ClauseType.GOVERNING_LAW: ['governing law', 'jurisdiction', 'applicable law', 'laws of'],
            ClauseType.WARRANTIES: ['warranty', 'warrant', 'represent', 'guarantee', 'assure'],
            ClauseType.INDEMNIFICATION: ['indemnif', 'hold harmless', 'defend', 'reimburse'],
            ClauseType.SERVICE_LEVEL: ['service level', 'performance standard', 'uptime', 'availability'],
            ClauseType.SCOPE_OF_WORK: ['scope', 'work', 'services', 'deliverable', 'perform'],
            ClauseType.DELIVERABLES: ['deliverable', 'output', 'result', 'product', 'milestone'],
            ClauseType.TIMELINE: ['timeline', 'schedule', 'deadline', 'completion', 'delivery date']
        }
        
        # Score each clause type
        scores = {}
        for clause_type, keywords in clause_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[clause_type] = score
        
        # Return clause type with highest score, or GENERAL if no match
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        else:
            return ClauseType.GENERAL

    async def _get_ai_analysis(self, prompt: str) -> Optional[str]:
        """Get AI analysis using available models"""
        try:
            if self.gemini_model:
                try:
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        prompt
                    )
                    return response.text
                except Exception as e:
                    logger.warning(f"⚠️ Gemini analysis failed: {e}, trying Groq")
            
            if self.groq_client:
                response = await asyncio.to_thread(
                    self.groq_client.chat.completions.create,
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            logger.warning("⚠️ No AI models available for analysis")
            return None
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return None

    def _calculate_overall_risk(self, clause_analyses: List[ClauseAnalysis]) -> float:
        """Calculate overall document risk score"""
        if not clause_analyses:
            return 0.5
        
        # Weight different clause types differently
        clause_weights = {
            ClauseType.LIABILITY: 3.0,
            ClauseType.TERMINATION: 2.5,
            ClauseType.PAYMENT_TERMS: 2.0,
            ClauseType.INTELLECTUAL_PROPERTY: 2.0,
            ClauseType.INDEMNIFICATION: 2.5,
            ClauseType.DISPUTE_RESOLUTION: 1.5,
            ClauseType.CONFIDENTIALITY: 1.5,
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for analysis in clause_analyses:
            weight = clause_weights.get(analysis.clause_type, 1.0)
            total_weighted_score += analysis.risk_score * weight
            total_weight += weight
        
        return min(1.0, total_weighted_score / total_weight if total_weight > 0 else 0.5)

    async def _generate_document_recommendations(self, text: str, clause_analyses: List[ClauseAnalysis], 
                                               metadata: DocumentMetadata) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Generate comprehensive document-level recommendations"""
        try:
            # Collect high-risk issues
            key_issues = []
            high_risk_clauses = [c for c in clause_analyses if c.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
            
            for clause in high_risk_clauses:
                key_issues.extend(clause.issues[:2])  # Top 2 issues per high-risk clause
            
            # Generate AI-powered recommendations
            recommendations_prompt = f"""
            You are a senior contract attorney providing strategic recommendations for this {metadata.document_type.value}.

            DOCUMENT SUMMARY:
            - Type: {metadata.document_type.value}
            - Parties: {', '.join(metadata.parties[:3])}
            - Jurisdiction: {metadata.jurisdiction or 'Not specified'}
            - High-risk clauses: {len(high_risk_clauses)}

            HIGH-RISK ISSUES IDENTIFIED:
            {chr(10).join(f"- {issue}" for issue in key_issues[:10])}

            PROVIDE:
            1. Top recommendations for reducing contract risk
            2. Negotiation priorities (what to focus on first)
            3. Missing clauses that should be added

            Respond in JSON format:
            {{
                "recommendations": ["recommendation1", "recommendation2"],
                "negotiation_priorities": ["priority1", "priority2"],
                "missing_clauses": ["missing1", "missing2"]
            }}
            """
            
            ai_response = await self._get_ai_analysis(recommendations_prompt)
            
            recommendations = []
            negotiation_priorities = []
            missing_clauses = []
            
            if ai_response:
                try:
                    data = json.loads(ai_response)
                    recommendations = data.get('recommendations', [])
                    negotiation_priorities = data.get('negotiation_priorities', [])
                    missing_clauses = data.get('missing_clauses', [])
                except (json.JSONDecodeError, KeyError):
                    logger.warning("⚠️ Failed to parse recommendations response")
            
            # Add fallback recommendations if AI failed
            if not recommendations:
                recommendations = [
                    "Review high-risk clauses identified in the analysis",
                    "Consider strengthening liability limitations",
                    "Ensure termination procedures are clearly defined"
                ]
            
            if not negotiation_priorities:
                negotiation_priorities = [
                    "Focus on liability and indemnification terms",
                    "Clarify payment terms and schedules",
                    "Negotiate favorable termination conditions"
                ]
            
            if not missing_clauses:
                missing_clauses = [
                    "Force majeure clause",
                    "Dispute resolution mechanism",
                    "Governing law specification"
                ]
            
            return key_issues[:10], recommendations[:8], negotiation_priorities[:6], missing_clauses[:5]
            
        except Exception as e:
            logger.error(f"❌ Document recommendations generation failed: {e}")
            return [], [], [], []

    async def _store_analysis_result(self, analysis_result: DocumentAnalysisResult):
        """Store analysis result in database"""
        try:
            # Convert dataclasses to dict for storage
            analysis_doc = {
                'document_id': analysis_result.document_id,
                'metadata': {
                    'document_id': analysis_result.metadata.document_id,
                    'filename': analysis_result.metadata.filename,
                    'file_type': analysis_result.metadata.file_type,
                    'file_size': analysis_result.metadata.file_size,
                    'upload_timestamp': analysis_result.metadata.upload_timestamp,
                    'processing_timestamp': analysis_result.metadata.processing_timestamp,
                    'document_type': analysis_result.metadata.document_type.value,
                    'page_count': analysis_result.metadata.page_count,
                    'word_count': analysis_result.metadata.word_count,
                    'parties': analysis_result.metadata.parties,
                    'effective_date': analysis_result.metadata.effective_date,
                    'expiration_date': analysis_result.metadata.expiration_date,
                    'jurisdiction': analysis_result.metadata.jurisdiction
                },
                'extracted_text': analysis_result.extracted_text,
                'clause_analyses': [
                    {
                        'clause_id': clause.clause_id,
                        'clause_type': clause.clause_type.value,
                        'content': clause.content,
                        'risk_level': clause.risk_level.value,
                        'risk_score': clause.risk_score,
                        'issues': clause.issues,
                        'recommendations': clause.recommendations,
                        'market_standard_comparison': clause.market_standard_comparison,
                        'suggested_alternatives': clause.suggested_alternatives,
                        'legal_precedents': clause.legal_precedents,
                        'compliance_notes': clause.compliance_notes
                    }
                    for clause in analysis_result.clause_analyses
                ],
                'overall_risk_score': analysis_result.overall_risk_score,
                'key_issues': analysis_result.key_issues,
                'recommendations': analysis_result.recommendations,
                'negotiation_priorities': analysis_result.negotiation_priorities,
                'missing_clauses': analysis_result.missing_clauses,
                'analysis_timestamp': analysis_result.analysis_timestamp
            }
            
            await self.db.document_analyses.update_one(
                {'document_id': analysis_result.document_id},
                {'$set': analysis_doc},
                upsert=True
            )
            
            logger.info(f"✅ Analysis result stored for document {analysis_result.document_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store analysis result: {e}")

    async def compare_contracts(self, document1_id: str, document2_id: str) -> ContractComparison:
        """Compare two contracts and provide detailed analysis"""
        try:
            logger.info(f"🔄 Comparing contracts {document1_id} and {document2_id}")
            
            # Retrieve both documents
            doc1_result = await self.db.document_analyses.find_one({'document_id': document1_id})
            doc2_result = await self.db.document_analyses.find_one({'document_id': document2_id})
            
            if not doc1_result or not doc2_result:
                raise ValueError("One or both documents not found")
            
            # Generate comparison analysis
            comparison_prompt = f"""
            You are a contract attorney comparing two contracts. Provide a detailed comparison analysis.

            CONTRACT 1 SUMMARY:
            - Type: {doc1_result['metadata']['document_type']}
            - Risk Score: {doc1_result['overall_risk_score']:.2f}
            - Key Issues: {', '.join(doc1_result['key_issues'][:3])}

            CONTRACT 2 SUMMARY:
            - Type: {doc2_result['metadata']['document_type']}
            - Risk Score: {doc2_result['overall_risk_score']:.2f}
            - Key Issues: {', '.join(doc2_result['key_issues'][:3])}

            PROVIDE COMPARISON IN JSON FORMAT:
            {{
                "differences": [
                    {{"section": "payment_terms", "contract1": "description", "contract2": "description", "recommendation": "text"}},
                    {{"section": "liability", "contract1": "description", "contract2": "description", "recommendation": "text"}}
                ],
                "gap_analysis": ["gap1", "gap2"],
                "risk_comparison": {{"contract1_advantages": ["adv1"], "contract2_advantages": ["adv1"], "overall_assessment": "text"}},
                "recommendations": ["rec1", "rec2"],
                "preferred_clauses": [{{"clause_type": "liability", "preferred_contract": "contract1", "reason": "explanation"}}]
            }}
            """
            
            ai_response = await self._get_ai_analysis(comparison_prompt)
            
            comparison_id = str(uuid.uuid4())
            
            # Parse AI response
            differences = []
            gap_analysis = []
            risk_comparison = {}
            recommendations = []
            preferred_clauses = []
            
            if ai_response:
                try:
                    data = json.loads(ai_response)
                    differences = data.get('differences', [])
                    gap_analysis = data.get('gap_analysis', [])
                    risk_comparison = data.get('risk_comparison', {})
                    recommendations = data.get('recommendations', [])
                    preferred_clauses = data.get('preferred_clauses', [])
                except (json.JSONDecodeError, KeyError):
                    logger.warning("⚠️ Failed to parse comparison response")
            
            # Create comparison result
            comparison = ContractComparison(
                comparison_id=comparison_id,
                document1_id=document1_id,
                document2_id=document2_id,
                differences=differences,
                gap_analysis=gap_analysis,
                risk_comparison=risk_comparison,
                recommendations=recommendations,
                preferred_clauses=preferred_clauses
            )
            
            # Store comparison result
            await self._store_comparison_result(comparison)
            
            logger.info(f"✅ Contract comparison completed: {comparison_id}")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Contract comparison failed: {e}")
            raise

    async def _store_comparison_result(self, comparison: ContractComparison):
        """Store contract comparison result"""
        try:
            comparison_doc = {
                'comparison_id': comparison.comparison_id,
                'document1_id': comparison.document1_id,
                'document2_id': comparison.document2_id,
                'differences': comparison.differences,
                'gap_analysis': comparison.gap_analysis,
                'risk_comparison': comparison.risk_comparison,
                'recommendations': comparison.recommendations,
                'preferred_clauses': comparison.preferred_clauses,
                'comparison_timestamp': comparison.comparison_timestamp
            }
            
            await self.db.contract_comparisons.update_one(
                {'comparison_id': comparison.comparison_id},
                {'$set': comparison_doc},
                upsert=True
            )
            
            logger.info(f"✅ Comparison result stored: {comparison.comparison_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store comparison result: {e}")

    async def get_document_analysis(self, document_id: str) -> Optional[DocumentAnalysisResult]:
        """Retrieve stored document analysis"""
        try:
            doc = await self.db.document_analyses.find_one({'document_id': document_id})
            if not doc:
                return None
            
            # Convert back to dataclass
            metadata = DocumentMetadata(
                document_id=doc['metadata']['document_id'],
                filename=doc['metadata']['filename'],
                file_type=doc['metadata']['file_type'],
                file_size=doc['metadata']['file_size'],
                upload_timestamp=doc['metadata']['upload_timestamp'],
                processing_timestamp=doc['metadata'].get('processing_timestamp'),
                document_type=DocumentType(doc['metadata']['document_type']),
                page_count=doc['metadata'].get('page_count'),
                word_count=doc['metadata'].get('word_count'),
                parties=doc['metadata'].get('parties', []),
                effective_date=doc['metadata'].get('effective_date'),
                expiration_date=doc['metadata'].get('expiration_date'),
                jurisdiction=doc['metadata'].get('jurisdiction')
            )
            
            clause_analyses = [
                ClauseAnalysis(
                    clause_id=clause['clause_id'],
                    clause_type=ClauseType(clause['clause_type']),
                    content=clause['content'],
                    risk_level=RiskLevel(clause['risk_level']),
                    risk_score=clause['risk_score'],
                    issues=clause['issues'],
                    recommendations=clause['recommendations'],
                    market_standard_comparison=clause.get('market_standard_comparison'),
                    suggested_alternatives=clause.get('suggested_alternatives', []),
                    legal_precedents=clause.get('legal_precedents', []),
                    compliance_notes=clause.get('compliance_notes', [])
                )
                for clause in doc['clause_analyses']
            ]
            
            return DocumentAnalysisResult(
                document_id=doc['document_id'],
                metadata=metadata,
                extracted_text=doc['extracted_text'],
                clause_analyses=clause_analyses,
                overall_risk_score=doc['overall_risk_score'],
                key_issues=doc['key_issues'],
                recommendations=doc['recommendations'],
                negotiation_priorities=doc['negotiation_priorities'],
                missing_clauses=doc['missing_clauses'],
                analysis_timestamp=doc['analysis_timestamp']
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve document analysis: {e}")
            return None

    async def initialize_database_collections(self):
        """Initialize database collections for document analysis"""
        try:
            # Create indexes for optimal performance
            await self.db.document_analyses.create_index([('document_id', 1)], unique=True)
            await self.db.document_analyses.create_index([('analysis_timestamp', -1)])
            await self.db.document_analyses.create_index([('metadata.document_type', 1)])
            await self.db.document_analyses.create_index([('overall_risk_score', -1)])
            
            await self.db.contract_comparisons.create_index([('comparison_id', 1)], unique=True)
            await self.db.contract_comparisons.create_index([('comparison_timestamp', -1)])
            await self.db.contract_comparisons.create_index([('document1_id', 1)])
            await self.db.contract_comparisons.create_index([('document2_id', 1)])
            
            logger.info("✅ Enhanced Legal Analysis database collections initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database collections: {e}")


# Global analyzer instance
_legal_analyzer = None

async def get_legal_analyzer(db_connection) -> EnhancedLegalAnalyzer:
    """Get or create enhanced legal analyzer instance"""
    global _legal_analyzer
    
    if _legal_analyzer is None:
        _legal_analyzer = EnhancedLegalAnalyzer(db_connection)
        await _legal_analyzer.initialize_database_collections()
        logger.info("🚀 Enhanced Legal Analyzer instance created and initialized")
    
    return _legal_analyzer