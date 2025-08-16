import React, { useState, useEffect, useRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Settings, 
  ChevronDown, 
  Scale, 
  Search, 
  FileText, 
  AlertCircle, 
  CheckCircle, 
  Loader2, 
  ExternalLink, 
  Shield,
  Menu,
  X,
  Lightbulb,
  Clock
} from 'lucide-react';

const MobileLegalQA = ({ 
  messages, 
  currentQuestion, 
  isLoading, 
  selectedJurisdiction, 
  selectedDomain, 
  communicationMode,
  handleSubmit,
  handleSampleQuestion,
  setCurrentQuestion,
  setSelectedJurisdiction,
  setSelectedDomain,
  setCommunicationMode,
  formatConfidence,
  convertMarkdownToHtml,
  shouldShowMetadata,
  sampleQuestions,
  getCurrentSampleQuestions,
  communicationModes,
  legalDomains,
  jurisdictions,
  ragStats,
  knowledgeBaseStats
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showSamples, setShowSamples] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const renderMessage = (message) => {
    switch (message.type) {
      case 'user':
        return (
          <div key={message.id} className="flex justify-end mb-3 px-4">
            <div className="flex items-end space-x-2 max-w-[85%]">
              <div className="bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-3">
                <p className="text-sm leading-relaxed">{message.content}</p>
              </div>
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-blue-600" />
              </div>
            </div>
          </div>
        );

      case 'assistant':
        const confidenceInfo = formatConfidence(message.confidence);
        const shouldShowMeta = shouldShowMetadata(message);
        const formattedContent = convertMarkdownToHtml(message.content);
        
        return (
          <div key={message.id} className="flex justify-start mb-4 px-4">
            <div className="flex items-start space-x-3 max-w-[90%]">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Scale className="w-4 h-4 text-purple-600" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
                {/* Communication Mode Indicator - Mobile Optimized */}
                {message.communicationMode && message.communicationMode !== 'general_consumer' && (
                  <div className="flex items-center mb-2 pb-2 border-b border-gray-100">
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      message.communicationMode === 'legal_professional' ? 'bg-blue-100 text-blue-700' :
                      message.communicationMode === 'business_executive' ? 'bg-green-100 text-green-700' :
                      message.communicationMode === 'academic_student' ? 'bg-indigo-100 text-indigo-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {message.communicationMode.replace('_', ' ')}
                    </div>
                  </div>
                )}

                <div className="prose prose-sm max-w-none">
                  <div 
                    className="text-gray-800 leading-relaxed text-sm"
                    dangerouslySetInnerHTML={{ __html: formattedContent }}
                  />
                </div>

                {/* Follow-up Suggestions - Mobile Optimized */}
                {message.adaptiveResponse && message.adaptiveResponse.follow_up_suggestions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <h4 className="text-xs font-medium text-gray-700 mb-2">Follow-up:</h4>
                    <div className="space-y-1">
                      {message.adaptiveResponse.follow_up_suggestions.slice(0, 2).map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleSampleQuestion(suggestion)}
                          className="block w-full text-left text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 p-2 rounded transition-colors"
                          disabled={isLoading}
                        >
                          💡 {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Compact Metadata for Mobile */}
                {shouldShowMeta && (
                  <div className="mt-3 pt-2 border-t border-gray-100">
                    <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <CheckCircle className="w-3 h-3" />
                        <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${confidenceInfo.bg} ${confidenceInfo.color}`}>
                          {Math.round(message.confidence * 100)}%
                        </span>
                      </div>
                      {message.retrievedDocuments > 0 && (
                        <div className="flex items-center space-x-1">
                          <FileText className="w-3 h-3" />
                          <span>{message.retrievedDocuments} sources</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Compact Sources for Mobile */}
                {shouldShowMeta && message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-gray-100">
                    <div className="text-xs font-medium text-gray-700 mb-2 flex items-center">
                      <FileText className="w-3 h-3 mr-1" />
                      Sources ({message.sources.length})
                    </div>
                    <div className="space-y-1">
                      {message.sources.slice(0, 2).map((source, index) => (
                        <div key={index} className="bg-gray-50 rounded p-2 text-xs">
                          <div className="font-medium text-gray-800 truncate">{source.title}</div>
                          <div className="text-gray-600 mt-1 flex flex-wrap gap-1">
                            {source.jurisdiction && (
                              <span className="inline-block bg-blue-100 text-blue-800 px-1 py-0.5 rounded text-xs">
                                {source.jurisdiction}
                              </span>
                            )}
                            {source.legal_domain && (
                              <span className="inline-block bg-green-100 text-green-800 px-1 py-0.5 rounded text-xs">
                                {source.legal_domain.replace('_', ' ')}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        );

      case 'system':
        return (
          <div key={message.id} className="flex justify-center mb-3 px-4">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2 max-w-[90%]">
              <p className="text-xs text-yellow-800 text-center">{message.content}</p>
            </div>
          </div>
        );

      case 'error':
        return (
          <div key={message.id} className="flex justify-start mb-3 px-4">
            <div className="flex items-start space-x-2 max-w-[90%]">
              <div className="flex-shrink-0 w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-4 h-4 text-red-600" />
              </div>
              <div className="bg-red-50 border border-red-200 text-red-800 rounded-2xl rounded-bl-md px-3 py-2">
                <p className="text-xs">{message.content}</p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Mobile Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-purple-100 p-2 rounded-full">
            <Scale className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">Legal Q&A</h1>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              {ragStats && (
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span>Active</span>
                </div>
              )}
              {knowledgeBaseStats && (
                <span>{knowledgeBaseStats.total_documents} docs</span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Sample Questions Sheet */}
          <Sheet open={showSamples} onOpenChange={setShowSamples}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="p-2">
                <Lightbulb className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="bottom" className="h-[60vh]">
              <SheetHeader>
                <SheetTitle>Sample Questions</SheetTitle>
                <SheetDescription>
                  {communicationMode === 'auto_detect' ? 'General' : communicationMode.replace('_', ' ')} mode
                </SheetDescription>
              </SheetHeader>
              <div className="mt-4 space-y-2 max-h-[40vh] overflow-y-auto">
                {getCurrentSampleQuestions().map((question, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      handleSampleQuestion(question);
                      setShowSamples(false);
                    }}
                    className="w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 p-3 rounded-lg border transition-colors"
                    disabled={isLoading}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </SheetContent>
          </Sheet>

          {/* Settings Sheet */}
          <Sheet open={showSettings} onOpenChange={setShowSettings}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="p-2">
                <Settings className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px]">
              <SheetHeader>
                <SheetTitle>Chat Settings</SheetTitle>
                <SheetDescription>
                  Customize your legal Q&A experience
                </SheetDescription>
              </SheetHeader>
              
              <div className="mt-6 space-y-6">
                {/* Communication Mode */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Communication Mode
                  </label>
                  <div className="space-y-2">
                    {communicationModes.map((mode) => {
                      const IconComponent = mode.icon;
                      const isActive = communicationMode === mode.id;
                      
                      return (
                        <button
                          key={mode.id}
                          onClick={() => setCommunicationMode(mode.id)}
                          className={`w-full flex items-start space-x-3 p-3 rounded-lg border transition-all ${
                            isActive 
                              ? mode.color + ' shadow-sm' 
                              : 'bg-white border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <IconComponent className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <div className="text-left">
                            <div className="text-sm font-medium">{mode.label}</div>
                            <div className="text-xs text-gray-500 mt-1">{mode.description}</div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Jurisdiction */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Jurisdiction
                  </label>
                  <select
                    value={selectedJurisdiction}
                    onChange={(e) => setSelectedJurisdiction(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {jurisdictions.map(jurisdiction => (
                      <option key={jurisdiction.value} value={jurisdiction.value}>
                        {jurisdiction.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Legal Domain */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Legal Domain
                  </label>
                  <select
                    value={selectedDomain}
                    onChange={(e) => setSelectedDomain(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Domains</option>
                    {legalDomains.map(domain => (
                      <option key={domain.value} value={domain.value}>
                        {domain.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Messages Area - Mobile Optimized */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto pb-4">
          {messages.map(renderMessage)}
          {isLoading && (
            <div className="flex justify-start px-4 mb-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                  <Scale className="w-4 h-4 text-purple-600" />
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex items-center space-x-2 text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Analyzing legal sources...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Mobile Input Area - Fixed at Bottom */}
      <div className="bg-white border-t px-4 py-3 safe-area-inset-bottom">
        <form onSubmit={handleSubmit} className="flex items-end space-x-2">
          <div className="flex-1">
            <Input
              type="text"
              value={currentQuestion}
              onChange={(e) => setCurrentQuestion(e.target.value)}
              placeholder="Ask a legal question..."
              className="border-gray-300 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[44px]"
              disabled={isLoading}
              style={{ minHeight: '44px' }}
            />
          </div>
          <Button
            type="submit"
            disabled={isLoading || !currentQuestion.trim()}
            className="bg-blue-600 text-white rounded-2xl min-h-[44px] min-w-[44px] hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center p-0"
            style={{ minHeight: '44px', minWidth: '44px' }}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </form>
        
        <div className="flex items-center justify-center space-x-4 mt-2 pt-2 border-t border-gray-100">
          <div className="flex items-center space-x-1 text-xs text-green-600">
            <Shield className="w-3 h-3" />
            <span>95% Accuracy</span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-blue-600">
            <CheckCircle className="w-3 h-3" />
            <span>Expert Validated</span>
          </div>
          <div className="flex items-center space-x-1 text-xs text-purple-600">
            <FileText className="w-3 h-3" />
            <span>25K+ Sources</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileLegalQA;