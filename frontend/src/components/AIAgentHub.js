import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Progress } from './ui/progress';
import { 
  MessageCircle, 
  Bot, 
  Briefcase, 
  Scale, 
  Shield, 
  Phone,
  Send,
  Loader2,
  CheckCircle,
  AlertCircle,
  Clock,
  Users,
  TrendingUp,
  FileText,
  Upload
} from 'lucide-react';
import MobileAIAgentHub from './MobileAIAgentHub';
import EnhancedContractAnalysis from './EnhancedContractAnalysis';

// Simple markdown renderer for basic formatting
const renderMarkdown = (text) => {
  if (!text) return text;
  
  return text
    // Bold text **bold** -> <strong>
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic text *italic* -> <em>
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Simple bullet points
    .replace(/^- (.*$)/gim, '• $1')
    // Numbered lists (basic)
    .replace(/^\d+\.\s/gim, '• ');
};

// Check if message is a simple greeting or short query
const isSimpleQuery = (message) => {
  const simple = message.toLowerCase().trim();
  const simplePatterns = [
    'hi', 'hello', 'hey', 'good morning', 'good afternoon', 
    'good evening', 'thanks', 'thank you', 'bye', 'goodbye',
    'what can you do', 'help', 'how are you'
  ];
  
  return simplePatterns.some(pattern => 
    simple === pattern || simple.startsWith(pattern + ' ') || simple.endsWith(' ' + pattern)
  ) || simple.length < 20;
};

const AIAgentHub = () => {
  const [activeAgent, setActiveAgent] = useState('contract-negotiation');
  const [sessions, setSessions] = useState({});
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agentStats, setAgentStats] = useState(null);
  const [isMobile, setIsMobile] = useState(false);
  const [showEnhancedAnalysis, setShowEnhancedAnalysis] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768); // md breakpoint
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const agents = {
    'contract-negotiation': {
      name: 'Contract Negotiation Agent',
      icon: Briefcase,
      color: 'bg-blue-500',
      description: 'Expert in deal structuring, risk allocation, and negotiation tactics with advanced document analysis',
      capabilities: [
        'Contract term optimization',
        'Document upload & analysis',
        'Risk allocation strategies',
        'Contract comparison',
        'Negotiation positioning',
        'Deal structure recommendations'
      ],
      enhanced_features: [
        'AI-powered document analysis',
        'Clause-by-clause risk assessment',
        'Side-by-side contract comparison',
        'Automated compliance checking'
      ]
    },
    'litigation-strategy': {
      name: 'Litigation Strategy Agent',
      icon: Scale,
      color: 'bg-purple-500',
      description: 'Specialized in case management and strategic litigation planning',
      capabilities: [
        'Case strategy development',
        'Discovery planning',
        'Motion practice strategy',
        'Settlement vs. trial analysis'
      ]
    },
    'compliance-monitoring': {
      name: 'Compliance Monitoring Agent',
      icon: Shield,
      color: 'bg-green-500',
      description: 'Regulatory compliance and risk assessment expert',
      capabilities: [
        'Regulatory compliance analysis',
        'Risk assessment & monitoring',
        'Policy recommendations',
        'Violation prevention'
      ]
    },
    'client-communication': {
      name: 'Client Communication Agent',
      icon: Phone,
      color: 'bg-orange-500',
      description: 'Professional communication and relationship management specialist',
      capabilities: [
        'Communication drafting',
        'Expectation management',
        'Relationship building',
        'Service delivery optimization'
      ]
    }
  };

  useEffect(() => {
    loadAgentStatistics();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [sessions]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadAgentStatistics = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-agents/statistics`);
      if (response.ok) {
        const stats = await response.json();
        setAgentStats(stats);
      }
    } catch (error) {
      console.error('Failed to load agent statistics:', error);
    }
  };

  const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const getCurrentSession = (agentType) => {
    if (!sessions[agentType]) {
      const sessionId = generateSessionId();
      setSessions(prev => ({
        ...prev,
        [agentType]: {
          sessionId,
          messages: [],
          context: {
            sessionId,
            case_id: null,
            contract_id: null,
            jurisdiction: null,
            case_type: null,
            contract_type: null
          }
        }
      }));
      return { sessionId, messages: [], context: { sessionId } };
    }
    return sessions[agentType];
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const session = getCurrentSession(activeAgent);
    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    // Add user message immediately
    setSessions(prev => ({
      ...prev,
      [activeAgent]: {
        ...prev[activeAgent],
        messages: [...(prev[activeAgent]?.messages || []), newMessage]
      }
    }));

    const messageToSend = currentMessage;
    setCurrentMessage('');
    setIsLoading(true);

    try {
      // Check if it's a simple query and provide appropriate response length guidance
      const isSimple = isSimpleQuery(messageToSend);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-agents/${activeAgent}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageToSend,
          session_id: session.sessionId,
          response_length: isSimple ? 'brief' : 'detailed',
          query_context: isSimple ? 'greeting_or_simple' : 'detailed_inquiry',
          ...session.context
        }),
      });

      if (!response.ok) {
        throw new Error(`Agent request failed: ${response.status}`);
      }

      let agentResponse = await response.json();
      
      // If backend doesn't support length adjustment, do it on frontend for simple queries
      if (isSimple && agentResponse.content && agentResponse.content.length > 200) {
        const greetingResponses = {
          'contract-negotiation': 'Hello! I\'m here to help you with contract negotiation strategies. What contract terms would you like to discuss?',
          'litigation-strategy': 'Hi! I can help you develop effective litigation strategies. What case are you working on?',
          'compliance-monitoring': 'Hello! I specialize in regulatory compliance and risk assessment. How can I assist you today?',
          'client-communication': 'Hi! I can help you craft professional client communications. What type of message do you need help with?'
        };
        
        if (greetingResponses[activeAgent]) {
          agentResponse.content = greetingResponses[activeAgent];
          agentResponse.confidence_score = 0.95;
          agentResponse.recommendations = [];
          agentResponse.action_items = [];
          agentResponse.follow_up_questions = [
            'What specific area would you like help with?',
            'Do you have a particular case or contract in mind?'
          ];
        }
      }

      // Add agent response
      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: agentResponse.content,
        recommendations: agentResponse.recommendations || [],
        action_items: agentResponse.action_items || [],
        confidence_score: agentResponse.confidence_score,
        follow_up_questions: agentResponse.follow_up_questions || [],
        priority_alerts: agentResponse.priority_alerts || [],
        timestamp: new Date()
      };

      setSessions(prev => ({
        ...prev,
        [activeAgent]: {
          ...prev[activeAgent],
          messages: [...prev[activeAgent].messages, agentMessage]
        }
      }));

      // Refresh statistics
      loadAgentStatistics();

    } catch (error) {
      console.error('Error sending message to agent:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };

      setSessions(prev => ({
        ...prev,
        [activeAgent]: {
          ...prev[activeAgent],
          messages: [...prev[activeAgent].messages, errorMessage]
        }
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearSession = () => {
    setSessions(prev => ({
      ...prev,
      [activeAgent]: {
        ...prev[activeAgent],
        messages: []
      }
    }));
  };

  const renderMessage = (message) => {
    const isUser = message.type === 'user';
    const isError = message.type === 'error';

    return (
      <div key={message.id} className={`mb-6 ${isUser ? 'text-right' : 'text-left'}`}>
        <div className={`inline-block max-w-[85%] p-4 rounded-lg ${
          isUser 
            ? 'bg-blue-500 text-white ml-auto' 
            : isError 
              ? 'bg-red-100 text-red-800 border border-red-200'
              : 'bg-gray-100 text-gray-800'
        }`}>
          {!isUser && !isError && (
            <div className="flex items-center mb-3">
              <Bot className="w-4 h-4 mr-2" />
              <span className="font-semibold text-sm">
                {agents[activeAgent].name}
              </span>
            </div>
          )}
          
          <div 
            className="whitespace-pre-wrap break-words leading-relaxed"
            dangerouslySetInnerHTML={{
              __html: renderMarkdown(message.content || '')
            }}
          />
          
          {message.confidence_score && (
            <div className="mt-3 flex items-center">
              <span className="text-xs opacity-75 mr-2">Confidence:</span>
              <Progress value={message.confidence_score * 100} className="w-20 h-2" />
              <span className="text-xs ml-2 opacity-75">
                {Math.round(message.confidence_score * 100)}%
              </span>
            </div>
          )}
          
          {message.recommendations && message.recommendations.length > 0 && (
            <div className="mt-4">
              <div className="text-sm font-semibold mb-2">Recommendations:</div>
              <div className="text-sm space-y-1">
                {message.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start">
                    <CheckCircle className="w-3 h-3 mr-2 mt-0.5 text-green-500 flex-shrink-0" />
                    <span 
                      dangerouslySetInnerHTML={{
                        __html: renderMarkdown(rec)
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {message.action_items && message.action_items.length > 0 && (
            <div className="mt-4">
              <div className="text-sm font-semibold mb-2">Action Items:</div>
              <div className="space-y-2">
                {message.action_items.map((item, index) => (
                  <div key={index} className="flex items-start text-sm">
                    <Badge 
                      variant={item.priority === 'high' ? 'destructive' : 
                              item.priority === 'urgent' ? 'destructive' : 'secondary'}
                      className="mr-2 text-xs flex-shrink-0"
                    >
                      {item.priority}
                    </Badge>
                    <span 
                      dangerouslySetInnerHTML={{
                        __html: renderMarkdown(item.description || item)
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {message.priority_alerts && message.priority_alerts.length > 0 && (
            <div className="mt-4">
              <Alert className="border-orange-200 bg-orange-50">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {message.priority_alerts.map((alert, index) => (
                    <div key={index} dangerouslySetInnerHTML={{
                      __html: renderMarkdown(alert.message || alert)
                    }} />
                  ))}
                </AlertDescription>
              </Alert>
            </div>
          )}
          
          {message.follow_up_questions && message.follow_up_questions.length > 0 && (
            <div className="mt-4">
              <div className="text-sm font-semibold mb-2">Follow-up Questions:</div>
              <div className="flex flex-wrap gap-2">
                {message.follow_up_questions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs h-auto py-1.5 px-3 whitespace-normal text-left"
                    onClick={() => setCurrentMessage(question)}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className="text-xs text-gray-500 mt-1">
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    );
  };

  const currentSession = getCurrentSession(activeAgent);
  const currentAgent = agents[activeAgent];

  // If mobile, use mobile-optimized component
  if (isMobile) {
    return (
      <MobileAIAgentHub
        agents={agents}
        activeAgent={activeAgent}
        setActiveAgent={setActiveAgent}
        sessions={sessions}
        setSessions={setSessions}
        currentMessage={currentMessage}
        setCurrentMessage={setCurrentMessage}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
        agentStats={agentStats}
        sendMessage={sendMessage}
        handleKeyPress={handleKeyPress}
        clearSession={clearSession}
        loadAgentStatistics={loadAgentStatistics}
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Context-Aware AI Agents
        </h1>
        <p className="text-gray-600">
          Specialized AI assistants that provide domain-specific expertise with full context awareness
        </p>
      </div>

      {/* Agent Statistics */}
      {agentStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <Users className="w-8 h-8 text-blue-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold">{agentStats.total_agents}</div>
                  <div className="text-sm text-gray-500">Active Agents</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <MessageCircle className="w-8 h-8 text-green-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold">
                    {Object.values(agentStats.conversation_counts || {}).reduce((a, b) => a + b, 0)}
                  </div>
                  <div className="text-sm text-gray-500">Total Conversations</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <TrendingUp className="w-8 h-8 text-purple-500 mr-3" />
                <div>
                  <div className="text-2xl font-bold">
                    {Object.values(agentStats.session_counts || {}).reduce((a, b) => a + b, 0)}
                  </div>
                  <div className="text-sm text-gray-500">Active Sessions</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center">
                <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
                <div>
                  <div className="text-2xl font-bold">{agentStats.system_status}</div>
                  <div className="text-sm text-gray-500">System Status</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Selection Panel */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Available Agents</CardTitle>
              <CardDescription>
                Choose a specialized AI agent for your needs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(agents).map(([agentType, agent]) => {
                  const Icon = agent.icon;
                  const isActive = activeAgent === agentType;
                  
                  return (
                    <div
                      key={agentType}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        isActive 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                      onClick={() => setActiveAgent(agentType)}
                    >
                      <div className="flex items-start">
                        <div className={`p-2 rounded-lg ${agent.color} mr-3`}>
                          <Icon className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-sm">{agent.name}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            {agent.description}
                          </div>
                          <div className="mt-2">
                            {agent.capabilities.map((capability, index) => (
                              <Badge key={index} variant="secondary" className="mr-1 mb-1 text-xs">
                                {capability}
                              </Badge>
                            ))}
                          </div>
                          
                          {/* Enhanced features for contract negotiation agent */}
                          {agentType === 'contract-negotiation' && agent.enhanced_features && (
                            <div className="mt-3 pt-2 border-t border-gray-200">
                              <div className="text-xs font-semibold text-blue-600 mb-1">Enhanced Features:</div>
                              <div className="space-y-1">
                                {agent.enhanced_features.map((feature, index) => (
                                  <div key={index} className="flex items-center text-xs text-gray-600">
                                    <FileText className="w-3 h-3 mr-1 text-blue-500" />
                                    {feature}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {currentSession.messages.length > 0 && (
                        <div className="mt-2 flex items-center text-xs text-gray-500">
                          <Clock className="w-3 h-3 mr-1" />
                          {currentSession.messages.length} messages
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <Card className="h-[700px] flex flex-col">
            <CardHeader className="pb-3 flex-shrink-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg ${currentAgent.color} mr-3`}>
                    <currentAgent.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{currentAgent.name}</CardTitle>
                    <CardDescription>{currentAgent.description}</CardDescription>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {activeAgent === 'contract-negotiation' && (
                    <div className="hidden lg:block ml-2">
                      <CounterOfferGenerator 
                        sessionId={getCurrentSession(activeAgent).sessionId}
                        goals={[]}
                        keyTerms={[]}
                        baseOffer={null}
                      />
                    </div>
                  )}

                  {activeAgent === 'contract-negotiation' && (
                    <>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setShowEnhancedAnalysis(true)}
                        className="flex items-center space-x-1"
                      >
                        <Upload className="w-4 h-4" />
                        <span>Analyze Document</span>
                      </Button>
                    </>
                  )}
                  
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={clearSession}
                  >
                    Clear Chat
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col p-0 min-h-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-hidden">
                <ScrollArea className="h-full p-4">
                  {currentSession.messages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-8">
                      <currentAgent.icon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p className="text-lg font-semibold mb-2">
                        Welcome to {currentAgent.name}
                      </p>
                      <p className="text-sm">
                        Start a conversation to get expert assistance with {currentAgent.description.toLowerCase()}
                      </p>
                      
                      <div className="mt-6 space-y-2">
                        <p className="text-sm font-semibold">Try asking about:</p>
                        {currentAgent.capabilities.map((capability, index) => (
                          <Button
                            key={index}
                            variant="ghost"
                            size="sm"
                            className="block mx-auto text-xs"
                            onClick={() => setCurrentMessage(`Help me with ${capability.toLowerCase()}`)}
                          >
                            {capability}
                          </Button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {currentSession.messages.map(renderMessage)}
                      {isLoading && (
                        <div className="text-left mb-4">
                          <div className="inline-block bg-gray-100 p-3 rounded-lg">
                            <div className="flex items-center">
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              <span className="text-sm text-gray-600">
                                {currentAgent.name} is thinking...
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </ScrollArea>
              </div>
              
              {/* Input Area */}
              <div className="border-t p-4 flex-shrink-0">
                <div className="flex space-x-2">
                  <Textarea
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={`Ask ${currentAgent.name} for expert assistance...`}
                    className="flex-1 min-h-[40px] max-h-32 resize-none"
                    rows={2}
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={!currentMessage.trim() || isLoading}
                    className="self-end"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                
                <div className="text-xs text-gray-500 mt-2">
                  Press Enter to send, Shift+Enter for new line
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Enhanced Contract Analysis Modal */}
      {showEnhancedAnalysis && (
        <EnhancedContractAnalysis
          sessionId={getCurrentSession(activeAgent).sessionId}
          isVisible={showEnhancedAnalysis}
          onClose={() => setShowEnhancedAnalysis(false)}
        />
      )}
    </div>
  );
};

export default AIAgentHub;