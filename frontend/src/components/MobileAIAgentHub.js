import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { Alert, AlertDescription } from './ui/alert';
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
  ArrowLeft,
  Settings
} from 'lucide-react';

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

const MobileAIAgentHub = ({
  agents,
  activeAgent,
  setActiveAgent,
  sessions,
  setSessions,
  currentMessage,
  setCurrentMessage,
  isLoading,
  setIsLoading,
  agentStats,
  sendMessage,
  handleKeyPress,
  clearSession,
  loadAgentStatistics
}) => {
  const [showAgentSelector, setShowAgentSelector] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [sessions]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const getCurrentSession = (agentType) => {
    return sessions[agentType] || { messages: [], sessionId: null };
  };

  const renderMessage = (message) => {
    const isUser = message.type === 'user';
    const isError = message.type === 'error';

    return (
      <div key={message.id} className={`mb-4 px-4 ${isUser ? 'text-right' : 'text-left'}`}>
        <div className={`inline-block max-w-[85%] ${
          isUser 
            ? 'bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-3' 
            : isError 
              ? 'bg-red-50 text-red-800 border border-red-200 rounded-2xl rounded-bl-md px-4 py-3'
              : 'bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm'
        }`}>
          {!isUser && !isError && (
            <div className="flex items-center mb-2">
              <Bot className="w-4 h-4 mr-2 text-gray-500" />
              <span className="font-semibold text-sm text-gray-700">
                {agents[activeAgent].name}
              </span>
            </div>
          )}
          
          <div 
            className={`whitespace-pre-wrap break-words leading-relaxed text-sm ${
              isUser ? 'text-white' : 'text-gray-800'
            }`}
            dangerouslySetInnerHTML={{
              __html: renderMarkdown(message.content || '')
            }}
          />
          
          {/* Mobile-optimized confidence score */}
          {message.confidence_score && (
            <div className="mt-2 flex items-center">
              <span className="text-xs opacity-75 mr-2">Confidence:</span>
              <div className="flex-1 max-w-16">
                <Progress value={message.confidence_score * 100} className="h-1" />
              </div>
              <span className="text-xs ml-2 opacity-75">
                {Math.round(message.confidence_score * 100)}%
              </span>
            </div>
          )}
          
          {/* Compact recommendations for mobile */}
          {message.recommendations && message.recommendations.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-100">
              <div className="text-xs font-semibold mb-2 text-gray-700">Recommendations:</div>
              <div className="text-xs space-y-1">
                {message.recommendations.slice(0, 3).map((rec, index) => (
                  <div key={index} className="flex items-start">
                    <CheckCircle className="w-3 h-3 mr-1 mt-0.5 text-green-500 flex-shrink-0" />
                    <span 
                      className="text-gray-700"
                      dangerouslySetInnerHTML={{
                        __html: renderMarkdown(rec)
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Compact action items for mobile */}
          {message.action_items && message.action_items.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-100">
              <div className="text-xs font-semibold mb-2 text-gray-700">Action Items:</div>
              <div className="space-y-1">
                {message.action_items.slice(0, 2).map((item, index) => (
                  <div key={index} className="flex items-start text-xs">
                    <Badge 
                      variant={item.priority === 'high' || item.priority === 'urgent' ? 'destructive' : 'secondary'}
                      className="mr-2 text-xs flex-shrink-0"
                    >
                      {item.priority}
                    </Badge>
                    <span 
                      className="text-gray-700"
                      dangerouslySetInnerHTML={{
                        __html: renderMarkdown(item.description || item)
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Priority alerts */}
          {message.priority_alerts && message.priority_alerts.length > 0 && (
            <div className="mt-3">
              <Alert className="border-orange-200 bg-orange-50 p-2">
                <AlertCircle className="h-3 w-3" />
                <AlertDescription className="text-xs">
                  {message.priority_alerts.map((alert, index) => (
                    <div key={index} dangerouslySetInnerHTML={{
                      __html: renderMarkdown(alert.message || alert)
                    }} />
                  ))}
                </AlertDescription>
              </Alert>
            </div>
          )}
          
          {/* Follow-up questions - Mobile optimized */}
          {message.follow_up_questions && message.follow_up_questions.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-100">
              <div className="text-xs font-semibold mb-2 text-gray-700">Follow-up:</div>
              <div className="space-y-1">
                {message.follow_up_questions.slice(0, 2).map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="w-full text-xs h-auto py-2 px-2 whitespace-normal text-left justify-start"
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
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    );
  };

  const currentSession = getCurrentSession(activeAgent);
  const currentAgent = agents[activeAgent];

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Mobile Header */}
      <div className="bg-white border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sheet open={showAgentSelector} onOpenChange={setShowAgentSelector}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" className="p-0">
                  <div className={`p-2 rounded-lg ${currentAgent.color} mr-3`}>
                    <currentAgent.icon className="w-5 h-5 text-white" />
                  </div>
                </Button>
              </SheetTrigger>
              <SheetContent side="bottom" className="h-[70vh]">
                <SheetHeader>
                  <SheetTitle>Choose AI Agent</SheetTitle>
                  <SheetDescription>
                    Select a specialized AI assistant
                  </SheetDescription>
                </SheetHeader>
                
                {/* Agent Statistics - Mobile */}
                {agentStats && (
                  <div className="grid grid-cols-2 gap-3 mt-4 mb-6">
                    <div className="bg-blue-50 p-3 rounded-lg text-center">
                      <div className="text-lg font-bold text-blue-600">{agentStats.total_agents}</div>
                      <div className="text-xs text-blue-500">Agents</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg text-center">
                      <div className="text-lg font-bold text-green-600">
                        {Object.values(agentStats.conversation_counts || {}).reduce((a, b) => a + b, 0)}
                      </div>
                      <div className="text-xs text-green-500">Conversations</div>
                    </div>
                  </div>
                )}

                {/* Agent Selection */}
                <div className="space-y-3 max-h-[45vh] overflow-y-auto">
                  {Object.entries(agents).map(([agentType, agent]) => {
                    const Icon = agent.icon;
                    const isActive = activeAgent === agentType;
                    const session = getCurrentSession(agentType);
                    
                    return (
                      <div
                        key={agentType}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          isActive 
                            ? 'border-blue-500 bg-blue-50' 
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                        onClick={() => {
                          setActiveAgent(agentType);
                          setShowAgentSelector(false);
                        }}
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
                            
                            {session.messages.length > 0 && (
                              <div className="mt-2 flex items-center text-xs text-gray-500">
                                <Clock className="w-3 h-3 mr-1" />
                                {session.messages.length} messages
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </SheetContent>
            </Sheet>
            
            <div>
              <h1 className="text-lg font-bold text-gray-900 truncate">
                {currentAgent.name}
              </h1>
              <p className="text-xs text-gray-500 truncate">
                {currentAgent.description}
              </p>
            </div>
          </div>
          
          <Button 
            variant="ghost" 
            size="sm"
            onClick={clearSession}
            className="p-2"
          >
            <MessageCircle className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto pb-4">
          {currentSession.messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8 px-4">
              <div className={`w-16 h-16 mx-auto mb-4 ${currentAgent.color} rounded-2xl flex items-center justify-center`}>
                <currentAgent.icon className="w-8 h-8 text-white" />
              </div>
              <p className="text-lg font-semibold mb-2">
                {currentAgent.name}
              </p>
              <p className="text-sm mb-6">
                {currentAgent.description}
              </p>
              
              <div className="space-y-2">
                <p className="text-sm font-semibold">Try asking about:</p>
                {currentAgent.capabilities.slice(0, 3).map((capability, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="block mx-auto text-xs bg-gray-100"
                    onClick={() => setCurrentMessage(`Help me with ${capability.toLowerCase()}`)}
                  >
                    {capability}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div className="pt-2">
              {currentSession.messages.map(renderMessage)}
              {isLoading && (
                <div className="text-left mb-4 px-4">
                  <div className="inline-block bg-gray-100 p-3 rounded-2xl rounded-bl-md">
                    <div className="flex items-center">
                      <Loader2 className="w-4 h-4 mr-2 animate-spin text-gray-500" />
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
        </div>
      </div>

      {/* Mobile Input Area - Fixed at Bottom */}
      <div className="bg-white border-t px-4 py-3 safe-area-inset-bottom">
        <div className="flex items-end space-x-2">
          <Input
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder={`Ask ${currentAgent.name} for help...`}
            className="flex-1 border-gray-300 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[44px]"
            disabled={isLoading}
            style={{ minHeight: '44px' }}
          />
          <Button
            onClick={sendMessage}
            disabled={!currentMessage.trim() || isLoading}
            className="bg-blue-600 text-white rounded-2xl min-h-[44px] min-w-[44px] hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center p-0"
            style={{ minHeight: '44px', minWidth: '44px' }}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
        
        <div className="text-xs text-gray-500 mt-2 text-center">
          Specialized AI assistant for {currentAgent.description.toLowerCase()}
        </div>
      </div>
    </div>
  );
};

export default MobileAIAgentHub;