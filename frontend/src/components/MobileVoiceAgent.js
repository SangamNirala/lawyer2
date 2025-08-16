import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Play, 
  Pause, 
  RotateCcw, 
  Settings, 
  Activity, 
  MessageCircle, 
  Bot, 
  User, 
  X,
  Phone,
  PhoneOff,
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';

const MobileVoiceAgent = ({ 
  onClose,
  // Voice states
  isListening,
  setIsListening,
  isSpeaking,
  setIsSpeaking,
  transcript,
  setTranscript,
  currentSpeech,
  setCurrentSpeech,
  conversation,
  setConversation,
  isProcessing,
  setIsProcessing,
  voiceError,
  setVoiceError,
  // Voice settings
  selectedVoice,
  setSelectedVoice,
  speechRate,
  setSpeechRate,
  speechPitch,
  setSpeechPitch,
  voiceVolume,
  setVoiceVolume,
  availableVoices,
  setAvailableVoices,
  autoListen,
  setAutoListen,
  // Legal Q&A settings
  sessionId,
  setSessionId,
  selectedJurisdiction,
  setSelectedJurisdiction,
  selectedDomain,
  setSelectedDomain,
  // Enhanced states
  interimTranscript,
  setInterimTranscript,
  isUserSpeaking,
  setIsUserSpeaking,
  conversationContext,
  setConversationContext,
  suggestedFollowUps,
  setSuggestedFollowUps,
  isInterrupted,
  setIsInterrupted,
  conversationSummary,
  setConversationSummary,
  lastUserIntent,
  setLastUserIntent,
  // Enhanced error handling
  retryCount,
  setRetryCount,
  isInitializing,
  setIsInitializing,
  recognitionState,
  setRecognitionState,
  // Functions
  initializeVoiceAgent,
  startListening,
  stopListening,
  sendVoiceMessage,
  interruptSpeech,
  clearConversation,
  restartRecognition,
  jurisdictions,
  legalDomains,
  sampleQuestions
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showSamples, setShowSamples] = useState(false);
  const conversationEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const scrollToBottom = () => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
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
                Voice Assistant
              </span>
            </div>
          )}
          
          <div className={`whitespace-pre-wrap break-words leading-relaxed text-sm ${
            isUser ? 'text-white' : 'text-gray-800'
          }`}>
            {message.content}
          </div>
          
          {/* Voice-specific indicators */}
          {message.confidence && (
            <div className="mt-2 flex items-center text-xs opacity-75">
              <CheckCircle className="w-3 h-3 mr-1" />
              <span>{Math.round(message.confidence * 100)}% confidence</span>
            </div>
          )}
          
          {message.response_time && (
            <div className="mt-1 flex items-center text-xs opacity-75">
              <Activity className="w-3 h-3 mr-1" />
              <span>{message.response_time}ms response</span>
            </div>
          )}
        </div>
        
        <div className="text-xs text-gray-500 mt-1">
          {message.timestamp && new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    );
  };

  const getConnectionStatus = () => {
    if (voiceError) return { status: 'error', color: 'bg-red-500', text: 'Error' };
    if (isInitializing) return { status: 'connecting', color: 'bg-yellow-500', text: 'Connecting' };
    if (recognitionState === 'active') return { status: 'connected', color: 'bg-green-500', text: 'Connected' };
    return { status: 'idle', color: 'bg-gray-500', text: 'Idle' };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-t-3xl w-full h-full max-w-md mx-auto overflow-hidden flex flex-col">
        {/* Mobile Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-white/20 p-2 rounded-full">
                <Mic className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-lg font-bold">AI Voice Agent</h1>
                <div className="flex items-center space-x-2 text-sm opacity-90">
                  <div className={`w-2 h-2 rounded-full ${connectionStatus.color}`}></div>
                  <span>{connectionStatus.text}</span>
                  {sessionId && (
                    <span className="text-xs opacity-75">• Session Active</span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Settings */}
              <Sheet open={showSettings} onOpenChange={setShowSettings}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="sm" className="text-white p-2">
                    <Settings className="w-5 h-5" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-[300px]">
                  <SheetHeader>
                    <SheetTitle>Voice Settings</SheetTitle>
                    <SheetDescription>
                      Customize your voice assistant experience
                    </SheetDescription>
                  </SheetHeader>
                  
                  <div className="mt-6 space-y-6">
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
                        {legalDomains.map(domain => (
                          <option key={domain.value} value={domain.value}>
                            {domain.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Voice Settings */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Speech Rate
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2.0"
                        step="0.1"
                        value={speechRate}
                        onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="text-xs text-gray-500 mt-1">{speechRate}x speed</div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Volume
                      </label>
                      <input
                        type="range"
                        min="0.1"
                        max="1.0"
                        step="0.1"
                        value={voiceVolume}
                        onChange={(e) => setVoiceVolume(parseFloat(e.target.value))}
                        className="w-full"
                      />
                      <div className="text-xs text-gray-500 mt-1">{Math.round(voiceVolume * 100)}%</div>
                    </div>

                    {/* Auto Listen Toggle */}
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium text-gray-700">
                        Auto Listen After Response
                      </label>
                      <Button
                        variant={autoListen ? "default" : "outline"}
                        size="sm"
                        onClick={() => setAutoListen(!autoListen)}
                      >
                        {autoListen ? 'On' : 'Off'}
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>

              {/* Close */}
              <Button variant="ghost" size="sm" className="text-white p-2" onClick={onClose}>
                <X className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Voice Status Bar */}
        <div className="bg-gray-50 px-4 py-2 border-b">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              {isListening && (
                <div className="flex items-center space-x-1 text-green-600">
                  <Activity className="w-4 h-4 animate-pulse" />
                  <span>Listening...</span>
                </div>
              )}
              {isSpeaking && (
                <div className="flex items-center space-x-1 text-blue-600">
                  <Volume2 className="w-4 h-4 animate-pulse" />
                  <span>Speaking...</span>
                </div>
              )}
              {isProcessing && (
                <div className="flex items-center space-x-1 text-purple-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </div>
              )}
              {!isListening && !isSpeaking && !isProcessing && (
                <div className="flex items-center space-x-1 text-gray-500">
                  <Mic className="w-4 h-4" />
                  <span>Ready to listen</span>
                </div>
              )}
            </div>
            
            <div className="text-xs text-gray-500">
              {conversation.length} messages
            </div>
          </div>
          
          {/* Live Transcript */}
          {(transcript || interimTranscript) && (
            <div className="mt-2 p-2 bg-white rounded-lg border">
              <div className="text-xs text-gray-500 mb-1">Live Transcript:</div>
              <div className="text-sm">
                {transcript}
                {interimTranscript && (
                  <span className="text-gray-400 italic">{interimTranscript}</span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto pb-4">
            {conversation.length === 0 ? (
              <div className="text-center text-gray-500 mt-8 px-4">
                <div className="w-16 h-16 mx-auto mb-4 bg-purple-100 rounded-full flex items-center justify-center">
                  <Mic className="w-8 h-8 text-purple-600" />
                </div>
                <p className="text-lg font-semibold mb-2">
                  Voice Legal Assistant
                </p>
                <p className="text-sm mb-6">
                  Speak naturally to get legal information and guidance
                </p>
                
                <div className="space-y-2">
                  <p className="text-sm font-semibold">Try saying:</p>
                  {sampleQuestions.slice(0, 3).map((question, index) => (
                    <div key={index} className="text-xs bg-gray-100 p-2 rounded-lg">
                      "{question}"
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="pt-2">
                {conversation.map(renderMessage)}
                <div ref={conversationEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Voice Controls - Fixed at Bottom */}
        <div className="bg-white border-t px-6 py-4 safe-area-inset-bottom">
          {/* Error Display */}
          {voiceError && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-sm text-red-800">
                {voiceError}
              </AlertDescription>
            </Alert>
          )}

          {/* Main Voice Controls */}
          <div className="flex items-center justify-center space-x-4 mb-4">
            {/* Listen/Stop Button */}
            <Button
              onClick={isListening ? stopListening : startListening}
              disabled={isInitializing || recognitionState === 'starting'}
              className={`w-16 h-16 rounded-full transition-all duration-200 ${
                isListening 
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                  : 'bg-blue-600 hover:bg-blue-700'
              } text-white`}
            >
              {isListening ? (
                <MicOff className="w-8 h-8" />
              ) : (
                <Mic className="w-8 h-8" />
              )}
            </Button>

            {/* Interrupt/Stop Speaking */}
            {isSpeaking && (
              <Button
                onClick={interruptSpeech}
                className="w-12 h-12 rounded-full bg-orange-500 hover:bg-orange-600 text-white"
              >
                <Pause className="w-6 h-6" />
              </Button>
            )}

            {/* Clear Conversation */}
            <Button
              onClick={clearConversation}
              variant="outline"
              className="w-12 h-12 rounded-full"
              disabled={conversation.length === 0}
            >
              <RotateCcw className="w-6 h-6" />
            </Button>
          </div>

          {/* Status and Instructions */}
          <div className="text-center">
            <div className="text-sm font-medium text-gray-700 mb-1">
              {isListening ? 'Tap to stop listening' : 'Tap to start voice conversation'}
            </div>
            <div className="text-xs text-gray-500">
              {isListening ? 'Speak your legal question naturally' : 'Voice-powered legal assistance'}
            </div>
          </div>

          {/* Follow-up Suggestions */}
          {suggestedFollowUps.length > 0 && !isListening && !isSpeaking && (
            <div className="mt-4 pt-3 border-t border-gray-100">
              <div className="text-xs font-medium text-gray-700 mb-2">Suggested follow-ups:</div>
              <div className="flex flex-wrap gap-2">
                {suggestedFollowUps.slice(0, 2).map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs h-auto py-1 px-2 whitespace-normal text-left"
                    onClick={() => {
                      setTranscript(suggestion);
                      sendVoiceMessage(suggestion);
                    }}
                  >
                    "{suggestion}"
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MobileVoiceAgent;