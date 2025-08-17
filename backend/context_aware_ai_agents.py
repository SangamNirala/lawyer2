"""
Context-Aware AI Agents Module

Specialized AI assistants that provide domain-specific expertise with full context awareness.
Each agent maintains conversation history, understands current case/contract context,
and provides intelligent recommendations based on their specialization.

Agents:
- Contract Negotiation Agent (Enhanced with Legal Analysis)
- Litigation Strategy Agent  
- Compliance Monitoring Agent
- Client Communication Agent
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import google.generativeai as genai
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

# Import enhanced legal analysis
from enhanced_legal_analysis import get_legal_analyzer, DocumentAnalysisResult, ContractComparison

logger = logging.getLogger(__name__)

class AgentType(Enum):
    CONTRACT_NEGOTIATION = "contract_negotiation"
    LITIGATION_STRATEGY = "litigation_strategy"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    CLIENT_COMMUNICATION = "client_communication"

class MessageType(Enum):
    USER_QUERY = "user_query"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_UPDATE = "system_update"
    CONTEXT_UPDATE = "context_update"

class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class AgentMessage:
    """Message structure for agent conversations"""
    message_id: str
    session_id: str
    agent_type: AgentType
    message_type: MessageType
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: PriorityLevel = PriorityLevel.MEDIUM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentContext:
    """Context information for AI agents"""
    session_id: str
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    contract_id: Optional[str] = None
    jurisdiction: Optional[str] = None
    case_type: Optional[str] = None
    contract_type: Optional[str] = None
    current_phase: Optional[str] = None
    key_facts: List[str] = field(default_factory=list)
    relevant_documents: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[AgentMessage] = field(default_factory=list)
    context_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResponse:
    """Structured response from AI agents"""
    response_id: str
    agent_type: AgentType
    content: str
    recommendations: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    context_updates: Dict[str, Any] = field(default_factory=dict)
    follow_up_questions: List[str] = field(default_factory=list)
    priority_alerts: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class BaseAIAgent:
    """Base class for all context-aware AI agents"""
    
    def __init__(self, agent_type: AgentType, db_connection):
        self.agent_type = agent_type
        self.db = db_connection
        self.session_contexts: Dict[str, AgentContext] = {}
        
        # Initialize AI clients
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY')
        self.groq_api_key = os.environ.get('GROQ_API_KEY')
        
        # Configure Gemini
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                logger.info(f"✅ {self.agent_type.value} agent: Gemini AI initialized")
            except Exception as e:
                logger.warning(f"⚠️ {self.agent_type.value} agent: Failed to initialize Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        # Configure Groq
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info(f"✅ {self.agent_type.value} agent: Groq AI initialized")
            except Exception as e:
                logger.warning(f"⚠️ {self.agent_type.value} agent: Failed to initialize Groq: {e}")
                self.groq_client = None
        else:
            self.groq_client = None
        
        logger.info(f"🤖 {self.agent_type.value.replace('_', ' ').title()} Agent initialized")

    async def process_message(self, message: str, context: AgentContext) -> AgentResponse:
        """Process a message with full context awareness"""
        try:
            logger.info(f"🔄 {self.agent_type.value} agent processing message in session {context.session_id}")
            
            # Update context with new message
            user_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                session_id=context.session_id,
                agent_type=self.agent_type,
                message_type=MessageType.USER_QUERY,
                content=message,
                context=context.context_metadata
            )
            context.conversation_history.append(user_message)
            
            # Store updated context
            self.session_contexts[context.session_id] = context
            
            # Generate specialized response
            response = await self._generate_specialized_response(message, context)
            
            # Create agent message for history
            agent_message = AgentMessage(
                message_id=response.response_id,
                session_id=context.session_id,
                agent_type=self.agent_type,
                message_type=MessageType.AGENT_RESPONSE,
                content=response.content,
                context=response.context_updates
            )
            context.conversation_history.append(agent_message)
            
            # Store conversation in database
            await self._store_conversation(context)
            
            logger.info(f"✅ {self.agent_type.value} agent response generated with {response.confidence_score:.1%} confidence")
            return response
            
        except Exception as e:
            logger.error(f"❌ {self.agent_type.value} agent failed to process message: {e}")
            raise

    async def _generate_specialized_response(self, message: str, context: AgentContext) -> AgentResponse:
        """Generate response using agent's specialization - to be overridden by subclasses"""
        raise NotImplementedError("Subclasses must implement _generate_specialized_response")

    async def _get_ai_response(self, prompt: str, use_gemini: bool = True) -> str:
        """Get AI response using available models"""
        try:
            if use_gemini and self.gemini_model:
                try:
                    response = await asyncio.to_thread(
                        self.gemini_model.generate_content,
                        prompt
                    )
                    return response.text
                except Exception as e:
                    logger.warning(f"⚠️ Gemini failed: {e}, trying Groq")
            
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
            logger.error(f"❌ AI response generation failed: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again shortly."

    def _build_context_summary(self, context: AgentContext) -> str:
        """Build context summary for AI prompts"""
        summary = f"Session ID: {context.session_id}\n"
        
        if context.case_id:
            summary += f"Case ID: {context.case_id}\n"
        if context.contract_id:
            summary += f"Contract ID: {context.contract_id}\n"
        if context.jurisdiction:
            summary += f"Jurisdiction: {context.jurisdiction}\n"
        if context.case_type:
            summary += f"Case Type: {context.case_type}\n"
        if context.contract_type:
            summary += f"Contract Type: {context.contract_type}\n"
        if context.current_phase:
            summary += f"Current Phase: {context.current_phase}\n"
        
        if context.key_facts:
            summary += f"Key Facts:\n"
            for fact in context.key_facts:
                summary += f"- {fact}\n"
        
        if context.conversation_history:
            summary += f"\nRecent Conversation:\n"
            for msg in context.conversation_history[-5:]:  # Last 5 messages
                role = "User" if msg.message_type == MessageType.USER_QUERY else "Agent"
                summary += f"{role}: {msg.content[:200]}...\n"
        
        return summary

    async def _store_conversation(self, context: AgentContext):
        """Store conversation in database"""
        try:
            conversation_doc = {
                "session_id": context.session_id,
                "agent_type": self.agent_type.value,
                "user_id": context.user_id,
                "case_id": context.case_id,
                "contract_id": context.contract_id,
                "conversation_history": [
                    {
                        "message_id": msg.message_id,
                        "message_type": msg.message_type.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "context": msg.context,
                        "priority": msg.priority.value
                    }
                    for msg in context.conversation_history
                ],
                "context_metadata": context.context_metadata,
                "last_updated": datetime.utcnow()
            }
            
            await self.db.ai_agent_conversations.update_one(
                {"session_id": context.session_id, "agent_type": self.agent_type.value},
                {"$set": conversation_doc},
                upsert=True
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to store conversation: {e}")

    async def get_session_context(self, session_id: str) -> Optional[AgentContext]:
        """Retrieve session context from memory or database"""
        if session_id in self.session_contexts:
            return self.session_contexts[session_id]
        
        try:
            # Load from database
            conversation = await self.db.ai_agent_conversations.find_one({
                "session_id": session_id,
                "agent_type": self.agent_type.value
            })
            
            if conversation:
                context = AgentContext(session_id=session_id)
                context.user_id = conversation.get('user_id')
                context.case_id = conversation.get('case_id')
                context.contract_id = conversation.get('contract_id')
                context.context_metadata = conversation.get('context_metadata', {})
                
                # Rebuild conversation history
                for msg_data in conversation.get('conversation_history', []):
                    message = AgentMessage(
                        message_id=msg_data['message_id'],
                        session_id=session_id,
                        agent_type=self.agent_type,
                        message_type=MessageType(msg_data['message_type']),
                        content=msg_data['content'],
                        context=msg_data.get('context', {}),
                        priority=PriorityLevel(msg_data.get('priority', 'medium')),
                        timestamp=msg_data['timestamp']
                    )
                    context.conversation_history.append(message)
                
                self.session_contexts[session_id] = context
                return context
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to load session context: {e}")
        
        return None

    def create_session_context(self, session_id: str, **kwargs) -> AgentContext:
        """Create new session context"""
        context = AgentContext(session_id=session_id, **kwargs)
        self.session_contexts[session_id] = context
        return context


class ContractNegotiationAgent(BaseAIAgent):
    """Enhanced Contract Negotiation Agent with Legal Analysis capabilities"""
    
    def __init__(self, db_connection):
        super().__init__(AgentType.CONTRACT_NEGOTIATION, db_connection)
        self.specialization = "contract negotiation and deal structuring with advanced legal analysis"
        self.legal_analyzer = None

    async def get_legal_analyzer(self):
        """Get legal analyzer instance"""
        if self.legal_analyzer is None:
            self.legal_analyzer = await get_legal_analyzer(self.db)
        return self.legal_analyzer

    async def analyze_document(self, file_content: bytes, filename: str, content_type: str, session_id: str) -> DocumentAnalysisResult:
        """Analyze uploaded contract document"""
        try:
            logger.info(f"🔍 Contract Agent analyzing document: {filename}")
            analyzer = await self.get_legal_analyzer()
            
            # Process document
            analysis_result = await analyzer.process_document(file_content, filename, content_type)
            
            # Store document reference in session context
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                if not hasattr(context, 'analyzed_documents'):
                    context.analyzed_documents = []
                context.analyzed_documents.append({
                    'document_id': analysis_result.document_id,
                    'filename': filename,
                    'analysis_timestamp': analysis_result.analysis_timestamp,
                    'risk_score': analysis_result.overall_risk_score
                })
            
            logger.info(f"✅ Document analysis completed: {analysis_result.document_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Document analysis failed: {e}")
            raise

    async def compare_documents(self, document1_id: str, document2_id: str, session_id: str) -> ContractComparison:
        """Compare two contract documents"""
        try:
            logger.info(f"🔄 Contract Agent comparing documents: {document1_id} vs {document2_id}")
            analyzer = await self.get_legal_analyzer()
            
            comparison_result = await analyzer.compare_contracts(document1_id, document2_id)
            
            # Store comparison reference in session context
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                if not hasattr(context, 'document_comparisons'):
                    context.document_comparisons = []
                context.document_comparisons.append({
                    'comparison_id': comparison_result.comparison_id,
                    'document1_id': document1_id,
                    'document2_id': document2_id,
                    'comparison_timestamp': comparison_result.comparison_timestamp
                })
            
            logger.info(f"✅ Document comparison completed: {comparison_result.comparison_id}")
            return comparison_result
            
        except Exception as e:
            logger.error(f"❌ Document comparison failed: {e}")
            raise

    async def get_document_analysis(self, document_id: str) -> Optional[DocumentAnalysisResult]:
        """Retrieve document analysis results"""
        try:
            analyzer = await self.get_legal_analyzer()
            return await analyzer.get_document_analysis(document_id)
        except Exception as e:
            logger.error(f"❌ Failed to retrieve document analysis: {e}")
            return None

    async def _generate_specialized_response(self, message: str, context: AgentContext) -> AgentResponse:
        """Generate enhanced contract negotiation response with legal analysis integration"""
        try:
            # Get conversation history for context awareness
            conversation_history = context.conversation_history[-4:] if context.conversation_history else []
            
            # Check for document analysis commands
            if any(keyword in message.lower() for keyword in ['analyze', 'upload', 'document', 'contract review']):
                return await self._handle_document_analysis_request(message, context)
            
            # Check for comparison commands
            if any(keyword in message.lower() for keyword in ['compare', 'comparison', 'versus', 'vs']):
                return await self._handle_comparison_request(message, context)
            
            # Check if this is a simple query but make it context-aware
            simple_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 
                             'good evening', 'thanks', 'thank you', 'bye', 'goodbye',
                             'what can you do', 'help', 'how are you', 'how can you help',
                             'what do you know', 'what are you', 'tell me about']
            
            message_lower = message.lower().strip()
            is_simple = (any(pattern in message_lower for pattern in simple_patterns) or 
                        len(message_lower) < 25)
            
            # Check if we've already introduced ourselves in this conversation
            already_introduced = any(
                msg.message_type == MessageType.AGENT_RESPONSE and 
                ("I'm here to help you with contract negotiation" in str(msg.content) or 
                 "I specialize in" in str(msg.content))
                for msg in conversation_history
            )
            
            if is_simple:
                if not already_introduced:
                    # First interaction - proper introduction with enhanced capabilities
                    if 'hi' in message_lower or 'hello' in message_lower:
                        content = """Hello! I'm your Enhanced Contract Negotiation Agent. I specialize in deal structuring, risk assessment, and negotiation tactics with advanced legal document analysis capabilities. 

I can help you with:
• Document upload and clause-by-clause analysis
• Contract risk assessment and recommendations
• Side-by-side contract comparisons
• Negotiation strategy development
• Legal compliance checking"""
                        follow_ups = [
                            "Would you like to upload a contract for analysis?",
                            "Do you have contracts you'd like me to compare?",
                            "Are you preparing for specific negotiations?"
                        ]
                    elif 'help' in message_lower or 'what can you do' in message_lower:
                        content = """I'm an expert in contract negotiation with advanced legal analysis capabilities. I can:

🔍 **Document Analysis:**
• Upload and analyze contracts (PDF, Word, text)
• Clause-by-clause risk assessment
• Identify missing or problematic terms

📊 **Contract Comparison:**
• Side-by-side contract analysis
• Gap analysis and risk comparison
• Preferred clause recommendations

💡 **Negotiation Strategy:**
• Deal structuring and positioning
• Risk allocation strategies
• Market standard comparisons"""
                        follow_ups = [
                            "What's your current contract situation?",
                            "Would you like to analyze a specific document?",
                            "Are there particular terms giving you trouble?"
                        ]
                    elif 'what do you know' in message_lower or 'tell me about' in message_lower:
                        content = """I have comprehensive expertise in contract law and negotiation, enhanced with AI-powered document analysis:

**Legal Analysis:**
• Automated clause identification and categorization
• Risk scoring for individual contract terms
• Compliance checking and legal precedent analysis
• Market standard comparisons

**Negotiation Intelligence:**
• Payment terms and liability optimization
• Termination and IP protection strategies
• Dispute resolution and governing law advice
• Strategic positioning and leverage analysis"""
                        follow_ups = [
                            "Which area interests you most?",
                            "Do you have a contract clause you'd like me to review?",
                            "What industry are you working in?"
                        ]
                    else:
                        content = """Great to connect! I'm here to help you navigate contract negotiations with confidence and advanced legal analysis. Whether you're reviewing terms, comparing agreements, or developing strategies, I'll provide expert guidance with AI-powered insights."""
                        follow_ups = [
                            "What's your main contract concern?",
                            "Would you like to upload a document for analysis?",
                            "Are you in active negotiations?"
                        ]
                else:
                    # Continuing conversation - more contextual responses
                    if 'help' in message_lower:
                        content = """I can dive deeper into any specific contract issues you're facing. My enhanced capabilities include:

• **Document Analysis:** Upload contracts for automated clause analysis
• **Risk Assessment:** Detailed scoring and recommendations
• **Contract Comparison:** Side-by-side analysis with gap identification
• **Strategic Guidance:** Negotiation positioning and tactics

What would be most helpful for your situation?"""
                        follow_ups = [
                            "Do you have a contract to analyze?",
                            "Would you like to compare multiple agreements?",
                            "What's the most challenging part of your negotiation?"
                        ]
                    elif 'what do you know' in message_lower:
                        content = """Beyond basic contract advice, I offer advanced AI-powered analysis:

• **Automated Risk Scoring:** Each clause analyzed for potential issues
• **Intelligent Recommendations:** Market-standard alternatives and improvements
• **Comprehensive Comparisons:** Gap analysis between multiple contracts
• **Strategic Intelligence:** Leverage assessment and negotiation priorities

I can help transform complex legal documents into clear, actionable insights."""
                        follow_ups = [
                            "Are you looking for document analysis capabilities?",
                            "Do you need help with contract comparison?",
                            "Would you like strategies for difficult negotiations?"
                        ]
                    elif any(word in message_lower for word in ['thanks', 'thank you']):
                        content = """You're very welcome! I'm here whenever you need advanced contract analysis or negotiation support. Feel free to upload documents for analysis or ask about any specific terms, strategies, or challenges."""
                        follow_ups = [
                            "Is there a contract you'd like me to analyze?",
                            "Do you have other negotiation questions?",
                            "Would you like tips for your next contract review?"
                        ]
                    else:
                        content = """Absolutely! Let's focus on what matters most for your contract situation. I can provide targeted advice, document analysis, or strategic guidance once I understand your specific needs."""
                        follow_ups = [
                            "What's your biggest contract challenge right now?",
                            "Would document analysis be helpful?",
                            "What would success look like for this negotiation?"
                        ]
                
                return AgentResponse(
                    response_id=str(uuid.uuid4()),
                    agent_type=self.agent_type,
                    content=content,
                    recommendations=[],
                    action_items=[],
                    confidence_score=0.95,
                    follow_up_questions=follow_ups
                )
            
            # For detailed queries, build enhanced context-aware prompt
            context_summary = self._build_enhanced_context_summary(context)
            
            # Include recent conversation context
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n\nRECENT CONVERSATION:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages
                    role = "User" if msg.message_type == MessageType.USER_QUERY else "Assistant"
                    conversation_context += f"{role}: {str(msg.content)[:200]}...\n"
            
            prompt = f"""
            You are an Enhanced Contract Negotiation AI Agent with advanced legal analysis capabilities. 
            You combine expert knowledge of contract law, negotiation tactics, and AI-powered document analysis.

            CURRENT CONTEXT:
            {context_summary}
            {conversation_context}

            ENHANCED CAPABILITIES:
            - Advanced document analysis and clause identification
            - Risk assessment with automated scoring
            - Contract comparison and gap analysis  
            - Market standard benchmarking
            - Legal compliance checking
            - Strategic negotiation positioning

            SPECIALIZATION FOCUS:
            - Contract term optimization with AI insights
            - Risk allocation strategies based on analysis
            - Negotiation tactics and positioning with leverage assessment
            - Deal structure recommendations with precedent analysis
            - Clause analysis and intelligent alternatives
            - Commercial term benchmarking with market data

            USER MESSAGE: {message}

            Provide expert guidance that builds on our conversation and leverages advanced analysis capabilities. 
            Be conversational, insightful, and practical. Offer specific recommendations, risk assessments, 
            and actionable next steps. Mention document analysis capabilities when relevant.
            Keep responses focused and valuable - aim for 200-400 words unless the query requires more detail.
            """

            ai_response = await self._get_ai_response(prompt)
            
            # Parse response for structured elements
            recommendations = self._extract_recommendations(ai_response)
            action_items = self._extract_action_items(ai_response)
            confidence_score = self._calculate_confidence(ai_response, context)
            
            # Generate contextual follow-up questions based on the response content
            contextual_follow_ups = self._generate_enhanced_follow_ups(message, ai_response, context)
            
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                content=ai_response,
                recommendations=recommendations,
                action_items=action_items,
                confidence_score=confidence_score,
                follow_up_questions=contextual_follow_ups
            )
            
        except Exception as e:
            logger.error(f"❌ Enhanced contract negotiation response failed: {e}")
            raise

    async def _handle_document_analysis_request(self, message: str, context: AgentContext) -> AgentResponse:
        """Handle requests for document analysis"""
        content = """📄 **Document Analysis Ready**

I can analyze your contract documents to provide:

🔍 **Comprehensive Analysis:**
• Clause-by-clause risk assessment
• Automated issue identification
• Legal compliance checking
• Market standard comparisons

📊 **Detailed Reports:**
• Overall risk scoring
• Specific recommendations for each clause
• Missing clause identification
• Negotiation priority guidance

**To get started:** Upload your contract document (PDF, Word, or text format) and I'll provide a complete analysis with actionable insights.

Would you like to upload a document now, or do you have questions about the analysis process?"""

        follow_ups = [
            "What type of contract would you like to analyze?",
            "Do you have specific concerns about certain clauses?",
            "Would you like to know more about the analysis features?"
        ]

        return AgentResponse(
            response_id=str(uuid.uuid4()),
            agent_type=self.agent_type,
            content=content,
            recommendations=[
                "Upload contract documents in PDF, Word, or text format",
                "Focus on high-risk clauses identified in the analysis",
                "Use analysis results to prioritize negotiation points"
            ],
            action_items=[
                {
                    'description': 'Prepare contract documents for upload and analysis',
                    'priority': 'medium',
                    'category': 'document_analysis'
                }
            ],
            confidence_score=0.95,
            follow_up_questions=follow_ups
        )

    async def _handle_comparison_request(self, message: str, context: AgentContext) -> AgentResponse:
        """Handle requests for contract comparison"""
        # Check if user has analyzed documents
        analyzed_docs = getattr(context, 'analyzed_documents', [])
        
        if len(analyzed_docs) >= 2:
            content = f"""📊 **Contract Comparison Available**

I can compare your analyzed documents:

**Available Documents:**
{chr(10).join(f"• {doc['filename']} (Risk Score: {doc['risk_score']:.2f})" for doc in analyzed_docs[:5])}

🔍 **Comparison Features:**
• Side-by-side clause analysis
• Gap identification and risk assessment
• Preferred clause recommendations
• Detailed difference explanations

Would you like me to compare specific documents? Just let me know which ones."""

            follow_ups = [
                "Which documents would you like me to compare?",
                "Are you looking for specific clause comparisons?",
                "Do you need help choosing the better contract?"
            ]
        else:
            content = """📊 **Contract Comparison Service**

I can provide detailed side-by-side contract comparisons including:

🔍 **Comprehensive Analysis:**
• Clause-by-clause comparison
• Risk differential assessment
• Gap analysis and missing terms
• Preferred clause recommendations

**To compare contracts:** First upload and analyze at least two contract documents, then I can provide detailed comparisons with specific recommendations.

Would you like to upload documents for analysis first?"""

            follow_ups = [
                "Would you like to upload contracts for analysis?",
                "What types of contracts do you need to compare?",
                "Do you have specific comparison criteria in mind?"
            ]

        return AgentResponse(
            response_id=str(uuid.uuid4()),
            agent_type=self.agent_type,
            content=content,
            recommendations=[
                "Upload multiple contracts for comprehensive comparison",
                "Focus on high-risk differences identified in comparisons",
                "Use comparison results to negotiate better terms"
            ],
            action_items=[
                {
                    'description': 'Prepare multiple contract documents for comparison analysis',
                    'priority': 'medium',
                    'category': 'contract_comparison'
                }
            ],
            confidence_score=0.95,
            follow_up_questions=follow_ups
        )

    def _build_enhanced_context_summary(self, context: AgentContext) -> str:
        """Build enhanced context summary including document analysis history"""
        summary = self._build_context_summary(context)
        
        # Add document analysis information
        analyzed_docs = getattr(context, 'analyzed_documents', [])
        if analyzed_docs:
            summary += f"\nANALYZED DOCUMENTS:\n"
            for doc in analyzed_docs[-3:]:  # Last 3 documents
                summary += f"- {doc['filename']} (Risk: {doc['risk_score']:.2f})\n"
        
        # Add comparison information  
        comparisons = getattr(context, 'document_comparisons', [])
        if comparisons:
            summary += f"\nRECENT COMPARISONS: {len(comparisons)} completed\n"
        
        return summary

    def _generate_enhanced_follow_ups(self, user_message: str, ai_response: str, context: AgentContext) -> List[str]:
        """Generate enhanced contextual follow-up questions including document analysis options"""
        message_lower = user_message.lower()
        response_lower = ai_response.lower() if ai_response else ""
        
        # Check if user has analyzed documents
        analyzed_docs = getattr(context, 'analyzed_documents', [])
        has_documents = len(analyzed_docs) > 0
        
        # Document analysis related follow-ups
        if any(term in message_lower for term in ['document', 'contract', 'analyze', 'upload']):
            if has_documents:
                return [
                    "Would you like to analyze additional documents?",
                    "Should I compare this with your other contracts?",
                    "Do you need help with specific clauses from the analysis?"
                ]
            else:
                return [
                    "Would you like to upload a contract for analysis?",
                    "What type of document analysis would be most helpful?",
                    "Do you have contracts ready for review?"
                ]
        
        # Standard topic-based follow-ups with enhanced options
        if any(term in message_lower for term in ['payment', 'money', 'fee', 'cost']):
            base_follow_ups = [
                "Would you like me to review specific payment terms?",
                "Should we discuss payment security mechanisms?",
                "Are there milestone-based payment options to consider?"
            ]
            if has_documents:
                base_follow_ups.append("Should I analyze payment clauses in your uploaded contracts?")
            return base_follow_ups
            
        elif any(term in message_lower for term in ['risk', 'liability', 'insurance']):
            base_follow_ups = [
                "Should we explore liability cap strategies?",
                "Would indemnification clauses be relevant here?",
                "Are there specific risks you're most concerned about?"
            ]
            if has_documents:
                base_follow_ups.append("Would you like detailed risk analysis of your contracts?")
            return base_follow_ups
            
        elif any(term in message_lower for term in ['termination', 'end', 'cancel', 'exit']):
            base_follow_ups = [
                "Do you need help with termination notice periods?",
                "Should we discuss post-termination obligations?",
                "Are there specific exit scenarios to plan for?"
            ]
            if has_documents:
                base_follow_ups.append("Should I review termination clauses in your contracts?")
            return base_follow_ups
            
        else:
            # General contextual follow-ups based on conversation stage and available features
            conversation_length = len(context.conversation_history) if context.conversation_history else 0
            
            if conversation_length < 4:
                base_follow_ups = [
                    "What's the most important outcome for this negotiation?",
                    "Are there any deal-breaker terms we should address?",
                    "Would document analysis help with your contract review?"
                ]
            else:
                base_follow_ups = [
                    "Should we explore alternative approaches to this?",
                    "Are there other contract areas you'd like to optimize?",
                    "What would make this negotiation successful for you?"
                ]
            
            # Add document-specific options based on context
            if has_documents and len(analyzed_docs) >= 2:
                base_follow_ups.append("Would you like me to compare your analyzed contracts?")
            elif not has_documents:
                base_follow_ups.append("Would contract document analysis be helpful?")
            
            return base_follow_ups

    def _generate_contextual_follow_ups(self, user_message: str, ai_response: str, context: AgentContext) -> List[str]:
        """Generate contextual follow-up questions based on the conversation"""
        message_lower = user_message.lower()
        response_lower = ai_response.lower() if ai_response else ""
        
        # Analyze the topics discussed to generate relevant follow-ups
        if any(term in message_lower for term in ['payment', 'money', 'fee', 'cost']):
            return [
                "Would you like me to review specific payment terms?",
                "Should we discuss payment security mechanisms?",
                "Are there milestone-based payment options to consider?"
            ]
        elif any(term in message_lower for term in ['risk', 'liability', 'insurance']):
            return [
                "Should we explore liability cap strategies?",
                "Would indemnification clauses be relevant here?",
                "Are there specific risks you're most concerned about?"
            ]
        elif any(term in message_lower for term in ['termination', 'end', 'cancel', 'exit']):
            return [
                "Do you need help with termination notice periods?",
                "Should we discuss post-termination obligations?",
                "Are there specific exit scenarios to plan for?"
            ]
        elif any(term in message_lower for term in ['ip', 'intellectual property', 'ownership']):
            return [
                "Should we clarify IP ownership and licensing terms?",
                "Are there work-for-hire provisions to review?",
                "Do you need protection for existing IP?"
            ]
        elif any(term in message_lower for term in ['service', 'performance', 'delivery']):
            return [
                "Should we define service level agreements?",
                "Are there performance metrics to establish?",
                "Would delivery milestones be beneficial?"
            ]
        else:
            # General contextual follow-ups based on conversation stage
            conversation_length = len(context.conversation_history) if context.conversation_history else 0
            if conversation_length < 4:
                return [
                    "What's the most important outcome for this negotiation?",
                    "Are there any deal-breaker terms we should address?",
                    "Would you like me to analyze specific contract language?"
                ]
            else:
                return [
                    "Should we explore alternative approaches to this?",
                    "Are there other contract areas you'd like to optimize?",
                    "What would make this negotiation successful for you?"
                ]

    def _extract_recommendations(self, response_text: str) -> List[str]:
        """Extract specific recommendations from AI response"""
        recommendations = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('•') or line.startswith('-') or line.startswith('*') or
                'recommend' in line.lower() or 'suggest' in line.lower() or
                'consider' in line.lower()):
                if len(line) > 20:  # Filter out short lines
                    cleaned = line.lstrip('•-*').strip()
                    if cleaned and len(cleaned) > 10:
                        recommendations.append(cleaned)
        
        return recommendations[:5]  # Top 5 recommendations

    def _extract_action_items(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract actionable items from AI response"""
        action_items = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if ('action' in line.lower() or 'next step' in line.lower() or
                'should' in line.lower() or 'need to' in line.lower()):
                if len(line) > 20:
                    action_items.append({
                        'description': line.lstrip('•-*').strip(),
                        'priority': 'medium',
                        'category': 'negotiation'
                    })
        
        return action_items[:3]  # Top 3 action items

    def _calculate_confidence(self, response_text: str, context: AgentContext) -> float:
        """Calculate confidence score based on response quality and context"""
        base_confidence = 0.75
        
        # Increase confidence based on context richness
        if context.contract_type:
            base_confidence += 0.05
        if context.key_facts:
            base_confidence += 0.05
        if len(context.conversation_history) > 2:
            base_confidence += 0.05
        
        # Response quality indicators
        if len(response_text) > 500:  # Detailed response
            base_confidence += 0.05
        if 'risk' in response_text.lower():
            base_confidence += 0.03
        if 'recommend' in response_text.lower():
            base_confidence += 0.03
        
        return min(0.95, base_confidence)


class LitigationStrategyAgent(BaseAIAgent):
    """Specialized agent for litigation strategy and case management"""
    
    def __init__(self, db_connection):
        super().__init__(AgentType.LITIGATION_STRATEGY, db_connection)
        self.specialization = "litigation strategy and case management"

    async def _generate_specialized_response(self, message: str, context: AgentContext) -> AgentResponse:
        """Generate litigation strategy specific response"""
        try:
            # Get conversation history for context awareness
            conversation_history = context.conversation_history[-4:] if context.conversation_history else []
            
            # Check if this is a simple query but make it context-aware
            simple_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 
                             'good evening', 'thanks', 'thank you', 'bye', 'goodbye',
                             'what can you do', 'help', 'how are you', 'how can you help',
                             'what do you know', 'what are you', 'tell me about']
            
            message_lower = message.lower().strip()
            is_simple = (any(pattern in message_lower for pattern in simple_patterns) or 
                        len(message_lower) < 25)
            
            # Check if we've already introduced ourselves in this conversation
            already_introduced = any(
                msg.message_type == MessageType.AGENT_RESPONSE and 
                ("I'm your Litigation Strategy Agent" in str(msg.content) or 
                 "I specialize in case management" in str(msg.content))
                for msg in conversation_history
            )
            
            if is_simple:
                if not already_introduced:
                    # First interaction - proper introduction
                    if 'hi' in message_lower or 'hello' in message_lower:
                        content = "Hello! I'm your Litigation Strategy Agent. I specialize in case management, discovery planning, and trial strategy. I can help you develop winning litigation approaches and navigate complex legal proceedings."
                        follow_ups = [
                            "What type of case are you working on?",
                            "Are you in the early stages of litigation?",
                            "Do you need help with case strategy?"
                        ]
                    elif 'help' in message_lower or 'what can you do' in message_lower:
                        content = "I'm an expert in litigation strategy with deep knowledge in discovery planning, motion practice, settlement analysis, and trial preparation. I can help you develop case strategies, assess risks, and plan your litigation approach."
                        follow_ups = [
                            "What's your current litigation situation?",
                            "Are there specific strategic challenges you're facing?",
                            "Would you like help with discovery planning?"
                        ]
                    elif 'what do you know' in message_lower or 'tell me about' in message_lower:
                        content = "I have expertise in all phases of litigation: case assessment, discovery strategy, motion practice, settlement negotiations, trial preparation, and appellate considerations. I stay current with procedural rules and strategic best practices."
                        follow_ups = [
                            "Which litigation phase are you focusing on?",
                            "Do you have a case you'd like me to analyze?",
                            "What practice area is your case in?"
                        ]
                    else:
                        content = "Great to connect! I'm here to help you develop effective litigation strategies. Whether you're planning discovery, preparing motions, or evaluating settlement, I'll provide strategic guidance."
                        follow_ups = [
                            "What's your main litigation challenge?",
                            "Are you actively in litigation?",
                            "Would you like help with case planning?"
                        ]
                else:
                    # Continuing conversation - more contextual responses
                    if 'help' in message_lower:
                        content = "I can dive deeper into any specific litigation challenges you're facing. Whether it's discovery disputes, motion strategy, settlement leverage, or trial preparation - let me know what's most pressing."
                        follow_ups = [
                            "What's the most critical issue in your case?",
                            "Are you dealing with discovery challenges?",
                            "Do you need help with motion strategy?"
                        ]
                    elif 'what do you know' in message_lower:
                        content = "Beyond the fundamentals, I can help with advanced litigation tactics like creating discovery leverage, developing motion sequences, building settlement pressure, and identifying case-winning strategies. What interests you most?"
                        follow_ups = [
                            "Are you looking for advanced strategic approaches?",
                            "Do you need help with case positioning?",
                            "Would you like tactics for difficult opponents?"
                        ]
                    elif any(word in message_lower for word in ['thanks', 'thank you']):
                        content = "You're very welcome! I'm here whenever you need litigation strategy support. Feel free to discuss any case challenges, procedural questions, or strategic decisions."
                        follow_ups = [
                            "Is there anything else about your case I can help with?",
                            "Do you have other litigation questions?",
                            "Would you like tips for your next case milestone?"
                        ]
                    else:
                        content = "Absolutely! Let's focus on what's most important for your case. I can provide targeted strategy once I understand your specific litigation challenges."
                        follow_ups = [
                            "What's your biggest case challenge right now?",
                            "Are you dealing with difficult procedural issues?",
                            "What would success look like in this litigation?"
                        ]
                
                return AgentResponse(
                    response_id=str(uuid.uuid4()),
                    agent_type=self.agent_type,
                    content=content,
                    recommendations=[],
                    action_items=[],
                    confidence_score=0.95,
                    follow_up_questions=follow_ups
                )
            
            # For detailed queries, build context-aware prompt
            context_summary = self._build_context_summary(context)
            
            # Include recent conversation context
            conversation_context = ""
            if conversation_history:
                conversation_context = "\n\nRECENT CONVERSATION:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages
                    role = "User" if msg.message_type == MessageType.USER_QUERY else "Assistant"
                    conversation_context += f"{role}: {str(msg.content)[:200]}...\n"
            
            prompt = f"""
            You are a specialized Litigation Strategy AI Agent with expertise in case management,
            legal tactics, discovery strategy, and trial preparation. You understand procedural rules,
            evidence standards, and strategic litigation planning.

            CURRENT CONTEXT:
            {context_summary}
            {conversation_context}

            SPECIALIZATION FOCUS:
            - Case strategy development
            - Discovery planning and management
            - Motion practice strategy
            - Settlement vs. trial analysis
            - Evidence evaluation and presentation
            - Risk assessment and mitigation
            - Timeline and resource planning

            USER MESSAGE: {message}

            Provide expert litigation guidance that builds on our conversation. Be strategic, practical, and insightful.
            Focus on actionable recommendations and consider procedural requirements and litigation realities.
            Keep responses focused and valuable - aim for 200-400 words unless more detail is needed.
            """

            ai_response = await self._get_ai_response(prompt)
            
            # Parse response for litigation-specific elements
            recommendations = self._extract_litigation_recommendations(ai_response)
            action_items = self._extract_litigation_actions(ai_response)
            priority_alerts = self._extract_priority_alerts(ai_response)
            confidence_score = self._calculate_litigation_confidence(ai_response, context)
            
            # Generate contextual follow-ups
            contextual_follow_ups = self._generate_litigation_follow_ups(message, ai_response, context)
            
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                content=ai_response,
                recommendations=recommendations,
                action_items=action_items,
                confidence_score=confidence_score,
                priority_alerts=priority_alerts,
                follow_up_questions=contextual_follow_ups
            )
            
        except Exception as e:
            logger.error(f"❌ Litigation strategy response failed: {e}")
            raise

    def _generate_litigation_follow_ups(self, user_message: str, ai_response: str, context: AgentContext) -> List[str]:
        """Generate contextual follow-up questions for litigation strategy"""
        message_lower = user_message.lower()
        
        if any(term in message_lower for term in ['discovery', 'documents', 'interrogatories', 'depositions']):
            return [
                "Should we discuss discovery scheduling and priorities?",
                "Do you need help with discovery dispute strategy?",
                "Would you like templates for discovery requests?"
            ]
        elif any(term in message_lower for term in ['motion', 'summary judgment', 'dismiss']):
            return [
                "Should we explore other motion opportunities?",
                "Do you need help with motion timing strategy?",
                "Would you like to discuss opposition strategies?"
            ]
        elif any(term in message_lower for term in ['settlement', 'negotiate', 'mediation']):
            return [
                "Should we analyze your settlement leverage?",
                "Do you need help with negotiation strategy?",
                "Would you like to discuss mediation preparation?"
            ]
        elif any(term in message_lower for term in ['trial', 'jury', 'evidence']):
            return [
                "Should we discuss trial preparation strategy?",
                "Do you need help with evidence presentation?",
                "Would you like jury selection insights?"
            ]
        else:
            conversation_length = len(context.conversation_history) if context.conversation_history else 0
            if conversation_length < 4:
                return [
                    "What's your primary goal for this litigation?",
                    "Are there critical deadlines we should plan around?",
                    "Would you like me to assess your case strengths?"
                ]
            else:
                return [
                    "Should we explore alternative strategic approaches?",
                    "Are there other case aspects you'd like to discuss?",
                    "What would make this litigation most successful?"
                ]

    def _extract_litigation_recommendations(self, response_text: str) -> List[str]:
        """Extract litigation-specific recommendations"""
        recommendations = []
        litigation_keywords = ['discovery', 'motion', 'deposition', 'evidence', 'settlement', 'trial']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in litigation_keywords):
                if len(line) > 30 and ('recommend' in line.lower() or 
                                       'consider' in line.lower() or
                                       'should' in line.lower()):
                    cleaned = line.lstrip('•-*').strip()
                    if cleaned:
                        recommendations.append(cleaned)
        
        return recommendations[:5]

    def _extract_litigation_actions(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract litigation-specific action items"""
        action_items = []
        action_keywords = ['file', 'serve', 'request', 'schedule', 'prepare', 'review']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in action_keywords):
                if len(line) > 20:
                    # Determine priority based on keywords
                    priority = 'medium'
                    if any(urgent in line.lower() for urgent in ['urgent', 'deadline', 'asap']):
                        priority = 'high'
                    elif any(routine in line.lower() for routine in ['review', 'consider']):
                        priority = 'low'
                    
                    action_items.append({
                        'description': line.lstrip('•-*').strip(),
                        'priority': priority,
                        'category': 'litigation',
                        'type': 'legal_action'
                    })
        
        return action_items[:4]

    def _extract_priority_alerts(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract priority alerts from litigation analysis"""
        alerts = []
        alert_keywords = ['deadline', 'statute of limitations', 'urgent', 'time-sensitive', 'critical']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in alert_keywords):
                if len(line) > 20:
                    alerts.append({
                        'message': line.lstrip('•-*').strip(),
                        'priority': 'high',
                        'type': 'deadline_alert'
                    })
        
        return alerts[:3]

    def _calculate_litigation_confidence(self, response_text: str, context: AgentContext) -> float:
        """Calculate confidence for litigation advice"""
        base_confidence = 0.70
        
        # Context factors
        if context.case_type:
            base_confidence += 0.08
        if context.jurisdiction:
            base_confidence += 0.05
        if context.key_facts:
            base_confidence += 0.07
        
        # Response quality indicators
        litigation_terms = ['discovery', 'motion', 'evidence', 'precedent', 'procedure']
        term_count = sum(1 for term in litigation_terms if term in response_text.lower())
        base_confidence += min(0.10, term_count * 0.02)
        
        return min(0.92, base_confidence)


class ComplianceMonitoringAgent(BaseAIAgent):
    """Specialized agent for compliance monitoring and regulatory oversight"""
    
    def __init__(self, db_connection):
        super().__init__(AgentType.COMPLIANCE_MONITORING, db_connection)
        self.specialization = "compliance monitoring and regulatory analysis"

    async def _generate_specialized_response(self, message: str, context: AgentContext) -> AgentResponse:
        """Generate compliance monitoring specific response"""
        try:
            context_summary = self._build_context_summary(context)
            
            prompt = f"""
            You are a specialized Compliance Monitoring AI Agent with expertise in regulatory
            requirements, industry standards, and compliance risk assessment. You monitor
            for potential violations and provide proactive compliance guidance.

            CURRENT CONTEXT:
            {context_summary}

            SPECIALIZATION FOCUS:
            - Regulatory compliance analysis
            - Industry standard adherence
            - Risk assessment and monitoring
            - Compliance policy recommendations
            - Violation detection and prevention
            - Documentation requirements
            - Training and awareness programs

            USER MESSAGE: {message}

            Provide expert compliance guidance including:
            1. Regulatory requirement analysis
            2. Compliance risk assessment
            3. Policy and procedure recommendations
            4. Documentation and record-keeping guidance
            5. Training recommendations
            6. Monitoring and audit strategies

            Consider current regulations, industry best practices, and emerging compliance trends.
            """

            ai_response = await self._get_ai_response(prompt)
            
            # Parse response for compliance-specific elements
            recommendations = self._extract_compliance_recommendations(ai_response)
            action_items = self._extract_compliance_actions(ai_response)
            priority_alerts = self._extract_compliance_alerts(ai_response)
            confidence_score = self._calculate_compliance_confidence(ai_response, context)
            
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                content=ai_response,
                recommendations=recommendations,
                action_items=action_items,
                confidence_score=confidence_score,
                priority_alerts=priority_alerts,
                follow_up_questions=[
                    "Do you need a compliance risk assessment for this area?",
                    "Should I review current policies for regulatory alignment?",
                    "Would you like monitoring recommendations for this compliance area?",
                    "Do you need documentation templates for compliance tracking?"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Compliance monitoring response failed: {e}")
            raise

    def _extract_compliance_recommendations(self, response_text: str) -> List[str]:
        """Extract compliance-specific recommendations"""
        recommendations = []
        compliance_keywords = ['policy', 'procedure', 'regulation', 'standard', 'requirement', 'audit']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in compliance_keywords):
                if len(line) > 25 and ('recommend' in line.lower() or 
                                       'should' in line.lower() or
                                       'must' in line.lower() or
                                       'ensure' in line.lower()):
                    cleaned = line.lstrip('•-*').strip()
                    if cleaned:
                        recommendations.append(cleaned)
        
        return recommendations[:5]

    def _extract_compliance_actions(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract compliance-specific action items"""
        action_items = []
        action_keywords = ['implement', 'update', 'review', 'document', 'train', 'monitor']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in action_keywords):
                if len(line) > 20:
                    # Determine priority based on compliance urgency
                    priority = 'medium'
                    if any(urgent in line.lower() for urgent in ['immediate', 'critical', 'violation']):
                        priority = 'urgent'
                    elif any(high in line.lower() for high in ['required', 'must', 'mandatory']):
                        priority = 'high'
                    
                    action_items.append({
                        'description': line.lstrip('•-*').strip(),
                        'priority': priority,
                        'category': 'compliance',
                        'type': 'compliance_action'
                    })
        
        return action_items[:4]

    def _extract_compliance_alerts(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract compliance alerts and warnings"""
        alerts = []
        alert_keywords = ['violation', 'non-compliance', 'risk', 'warning', 'critical', 'mandatory']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in alert_keywords):
                if len(line) > 20:
                    # Determine alert level
                    alert_level = 'medium'
                    if any(critical in line.lower() for critical in ['critical', 'violation', 'mandatory']):
                        alert_level = 'urgent'
                    
                    alerts.append({
                        'message': line.lstrip('•-*').strip(),
                        'priority': alert_level,
                        'type': 'compliance_alert'
                    })
        
        return alerts[:3]

    def _calculate_compliance_confidence(self, response_text: str, context: AgentContext) -> float:
        """Calculate confidence for compliance advice"""
        base_confidence = 0.75
        
        # Context factors
        if context.jurisdiction:
            base_confidence += 0.08
        if context.contract_type or context.case_type:
            base_confidence += 0.05
        
        # Response quality indicators
        compliance_terms = ['regulation', 'compliance', 'policy', 'requirement', 'standard']
        term_count = sum(1 for term in compliance_terms if term in response_text.lower())
        base_confidence += min(0.10, term_count * 0.02)
        
        return min(0.90, base_confidence)


class ClientCommunicationAgent(BaseAIAgent):
    """Specialized agent for client communication and relationship management"""
    
    def __init__(self, db_connection):
        super().__init__(AgentType.CLIENT_COMMUNICATION, db_connection)
        self.specialization = "client communication and relationship management"

    async def _generate_specialized_response(self, message: str, context: AgentContext) -> AgentResponse:
        """Generate client communication specific response"""
        try:
            context_summary = self._build_context_summary(context)
            
            prompt = f"""
            You are a specialized Client Communication AI Agent with expertise in client relations,
            professional communication, expectation management, and service delivery. You help
            craft appropriate communications and manage client relationships effectively.

            CURRENT CONTEXT:
            {context_summary}

            SPECIALIZATION FOCUS:
            - Professional communication drafting
            - Client expectation management
            - Relationship building strategies
            - Service delivery optimization
            - Conflict resolution and difficult conversations
            - Progress updates and status reporting
            - Fee discussions and billing communications

            USER MESSAGE: {message}

            Provide expert client communication guidance including:
            1. Communication strategy recommendations
            2. Message drafting assistance
            3. Tone and approach suggestions
            4. Expectation management strategies
            5. Relationship building opportunities
            6. Follow-up and engagement planning

            Consider client personality, relationship history, and communication preferences.
            Maintain professionalism while building strong client relationships.
            """

            ai_response = await self._get_ai_response(prompt)
            
            # Parse response for communication-specific elements
            recommendations = self._extract_communication_recommendations(ai_response)
            action_items = self._extract_communication_actions(ai_response)
            confidence_score = self._calculate_communication_confidence(ai_response, context)
            
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                content=ai_response,
                recommendations=recommendations,
                action_items=action_items,
                confidence_score=confidence_score,
                follow_up_questions=[
                    "Would you like help drafting a specific client communication?",
                    "Do you need strategies for managing client expectations?",
                    "Should I suggest approaches for difficult client conversations?",
                    "Would you like recommendations for client engagement activities?"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Client communication response failed: {e}")
            raise

    def _extract_communication_recommendations(self, response_text: str) -> List[str]:
        """Extract communication-specific recommendations"""
        recommendations = []
        communication_keywords = ['communicate', 'explain', 'update', 'inform', 'discuss', 'clarify']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in communication_keywords):
                if len(line) > 25 and ('recommend' in line.lower() or 
                                       'suggest' in line.lower() or
                                       'consider' in line.lower() or
                                       'should' in line.lower()):
                    cleaned = line.lstrip('•-*').strip()
                    if cleaned:
                        recommendations.append(cleaned)
        
        return recommendations[:5]

    def _extract_communication_actions(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract communication-specific action items"""
        action_items = []
        action_keywords = ['call', 'email', 'schedule', 'send', 'follow up', 'meet']
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in action_keywords):
                if len(line) > 20:
                    # Determine priority based on communication urgency
                    priority = 'medium'
                    if any(urgent in line.lower() for urgent in ['urgent', 'asap', 'immediate']):
                        priority = 'high'
                    elif any(routine in line.lower() for routine in ['follow up', 'update']):
                        priority = 'low'
                    
                    action_items.append({
                        'description': line.lstrip('•-*').strip(),
                        'priority': priority,
                        'category': 'client_communication',
                        'type': 'communication_action'
                    })
        
        return action_items[:4]

    def _calculate_communication_confidence(self, response_text: str, context: AgentContext) -> float:
        """Calculate confidence for communication advice"""
        base_confidence = 0.80  # Higher base confidence for communication
        
        # Context factors
        if len(context.conversation_history) > 3:  # More context available
            base_confidence += 0.05
        if context.key_facts:
            base_confidence += 0.05
        
        # Response quality indicators
        communication_terms = ['tone', 'approach', 'relationship', 'expectation', 'professional']
        term_count = sum(1 for term in communication_terms if term in response_text.lower())
        base_confidence += min(0.08, term_count * 0.015)
        
        return min(0.92, base_confidence)


class AIAgentManager:
    """Manager class for coordinating all AI agents"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
        # Initialize all specialized agents
        self.agents = {
            AgentType.CONTRACT_NEGOTIATION: ContractNegotiationAgent(db_connection),
            AgentType.LITIGATION_STRATEGY: LitigationStrategyAgent(db_connection),
            AgentType.COMPLIANCE_MONITORING: ComplianceMonitoringAgent(db_connection),
            AgentType.CLIENT_COMMUNICATION: ClientCommunicationAgent(db_connection)
        }
        
        logger.info("🤖 AI Agent Manager initialized with all specialized agents")

    async def process_message(self, agent_type: AgentType, message: str, 
                            session_id: str, **context_params) -> AgentResponse:
        """Process message with appropriate specialized agent"""
        try:
            agent = self.agents[agent_type]
            
            # Get or create session context
            context = await agent.get_session_context(session_id)
            if not context:
                context = agent.create_session_context(session_id, **context_params)
            else:
                # Update context with new parameters
                for key, value in context_params.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
            
            # Process message with specialized agent
            response = await agent.process_message(message, context)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Agent manager failed to process message: {e}")
            raise

    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics for all agents"""
        try:
            stats = {
                "total_agents": len(self.agents),
                "agent_types": [agent_type.value for agent_type in self.agents.keys()],
                "session_counts": {},
                "conversation_counts": {}
            }
            
            # Get session and conversation counts for each agent type
            for agent_type in self.agents.keys():
                session_count = len(self.agents[agent_type].session_contexts)
                
                conversation_count = await self.db.ai_agent_conversations.count_documents({
                    "agent_type": agent_type.value
                })
                
                stats["session_counts"][agent_type.value] = session_count
                stats["conversation_counts"][agent_type.value] = conversation_count
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get agent statistics: {e}")
            return {}

    async def initialize_database_collections(self):
        """Initialize database collections for AI agents"""
        try:
            # Create indexes for optimal performance
            await self.db.ai_agent_conversations.create_index([
                ("session_id", 1), ("agent_type", 1)
            ], unique=True)
            
            await self.db.ai_agent_conversations.create_index([("last_updated", -1)])
            await self.db.ai_agent_conversations.create_index([("user_id", 1)])
            await self.db.ai_agent_conversations.create_index([("case_id", 1)])
            await self.db.ai_agent_conversations.create_index([("contract_id", 1)])
            
            logger.info("✅ AI Agent database collections initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI agent collections: {e}")
            raise


# Global agent manager instance
_agent_manager = None

async def get_ai_agent_manager(db_connection) -> AIAgentManager:
    """Get or create AI agent manager instance"""
    global _agent_manager
    
    if _agent_manager is None:
        _agent_manager = AIAgentManager(db_connection)
        await _agent_manager.initialize_database_collections()
        logger.info("🚀 AI Agent Manager instance created and initialized")
    
    return _agent_manager