"""
Context-Aware AI Agents Module

Specialized AI assistants that provide domain-specific expertise with full context awareness.
Each agent maintains conversation history, understands current case/contract context,
and provides intelligent recommendations based on their specialization.

Agents:
- Contract Negotiation Agent
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
    """Specialized agent for contract negotiation assistance"""
    
    def __init__(self, db_connection):
        super().__init__(AgentType.CONTRACT_NEGOTIATION, db_connection)
        self.specialization = "contract negotiation and deal structuring"

    async def _generate_specialized_response(self, message: str, context: AgentContext) -> AgentResponse:
        """Generate contract negotiation specific response"""
        try:
            # Check if this is a simple greeting or short query
            simple_patterns = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 
                             'good evening', 'thanks', 'thank you', 'bye', 'goodbye',
                             'what can you do', 'help', 'how are you']
            
            message_lower = message.lower().strip()
            is_simple = (any(pattern in message_lower for pattern in simple_patterns) or 
                        len(message_lower) < 20)
            
            if is_simple:
                # Provide brief greeting response
                brief_responses = [
                    "Hello! I'm here to help you with contract negotiation strategies. What contract terms would you like to discuss?",
                    "Hi! I specialize in deal structuring and negotiation tactics. How can I assist you with your contract today?",
                    "Welcome! I can help you optimize contract terms and develop negotiation strategies. What's your contract situation?"
                ]
                
                content = brief_responses[0]  # Use first one for consistency
                
                return AgentResponse(
                    response_id=str(uuid.uuid4()),
                    agent_type=self.agent_type,
                    content=content,
                    recommendations=[],
                    action_items=[],
                    confidence_score=0.95,
                    follow_up_questions=[
                        "What type of contract are you working on?",
                        "Are there specific terms you'd like to negotiate?",
                        "What's your main concern with the current agreement?"
                    ]
                )
            
            context_summary = self._build_context_summary(context)
            
            prompt = f"""
            You are a specialized Contract Negotiation AI Agent with expertise in deal structuring, 
            risk mitigation, and strategic negotiation tactics. You have deep knowledge of contract law,
            commercial terms, and negotiation psychology.

            CURRENT CONTEXT:
            {context_summary}

            SPECIALIZATION FOCUS:
            - Contract term optimization
            - Risk allocation strategies  
            - Negotiation tactics and positioning
            - Deal structure recommendations
            - Clause analysis and alternatives
            - Commercial term benchmarking

            USER MESSAGE: {message}

            Provide expert guidance on contract negotiation including:
            1. Specific recommendations for the current situation
            2. Risk assessment of proposed terms
            3. Alternative clause suggestions
            4. Strategic negotiation positioning
            5. Action items for moving forward
            6. Potential counteroffers or responses

            Focus on practical, actionable advice that considers both legal and business implications.
            Keep your response concise but comprehensive, focusing on the most important points.
            """

            ai_response = await self._get_ai_response(prompt)
            
            # Parse response for structured elements
            recommendations = self._extract_recommendations(ai_response)
            action_items = self._extract_action_items(ai_response)
            confidence_score = self._calculate_confidence(ai_response, context)
            
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                content=ai_response,
                recommendations=recommendations,
                action_items=action_items,
                confidence_score=confidence_score,
                follow_up_questions=[
                    "Would you like me to analyze specific contract clauses?",
                    "Do you need help with negotiation strategy for upcoming discussions?",
                    "Should I review the risk allocation in these terms?"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Contract negotiation response failed: {e}")
            raise

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
            context_summary = self._build_context_summary(context)
            
            prompt = f"""
            You are a specialized Litigation Strategy AI Agent with expertise in case management,
            legal tactics, discovery strategy, and trial preparation. You understand procedural rules,
            evidence standards, and strategic litigation planning.

            CURRENT CONTEXT:
            {context_summary}

            SPECIALIZATION FOCUS:
            - Case strategy development
            - Discovery planning and management
            - Motion practice strategy
            - Settlement vs. trial analysis
            - Evidence evaluation and presentation
            - Risk assessment and mitigation
            - Timeline and resource planning

            USER MESSAGE: {message}

            Provide expert litigation guidance including:
            1. Strategic recommendations for case positioning
            2. Discovery strategy and priorities
            3. Motion practice opportunities
            4. Settlement leverage analysis
            5. Risk factors and mitigation strategies
            6. Timeline and milestone planning

            Consider procedural requirements, evidence standards, and practical litigation realities.
            """

            ai_response = await self._get_ai_response(prompt)
            
            # Parse response for litigation-specific elements
            recommendations = self._extract_litigation_recommendations(ai_response)
            action_items = self._extract_litigation_actions(ai_response)
            priority_alerts = self._extract_priority_alerts(ai_response)
            confidence_score = self._calculate_litigation_confidence(ai_response, context)
            
            return AgentResponse(
                response_id=str(uuid.uuid4()),
                agent_type=self.agent_type,
                content=ai_response,
                recommendations=recommendations,
                action_items=action_items,
                confidence_score=confidence_score,
                priority_alerts=priority_alerts,
                follow_up_questions=[
                    "Do you need help with discovery strategy planning?",
                    "Should I analyze potential motions for this case?",
                    "Would you like a settlement vs. trial analysis?",
                    "Do you need timeline planning for key milestones?"
                ]
            )
            
        except Exception as e:
            logger.error(f"❌ Litigation strategy response failed: {e}")
            raise

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