import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Play, Pause, RotateCcw, Settings, Activity, MessageCircle, Bot, User, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import MobileVoiceAgent from './MobileVoiceAgent';

const VoiceAgent = ({ onClose }) => {
  // Voice states
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentSpeech, setCurrentSpeech] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  
  // Voice settings
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [speechRate, setSpeechRate] = useState(1.0);
  const [speechPitch, setSpeechPitch] = useState(1.0);
  const [voiceVolume, setVoiceVolume] = useState(0.8);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [autoListen, setAutoListen] = useState(true);
  
  // Legal Q&A settings
  const [sessionId, setSessionId] = useState(null);
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('US');
  const [selectedDomain, setSelectedDomain] = useState('all_domains');
  
  // Enhanced conversation states
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [conversationContext, setConversationContext] = useState([]);
  const [suggestedFollowUps, setSuggestedFollowUps] = useState([]);
  const [isInterrupted, setIsInterrupted] = useState(false);
  const [conversationSummary, setConversationSummary] = useState('');
  const [lastUserIntent, setLastUserIntent] = useState('');
  
  // Enhanced error handling and retry logic
  const [retryCount, setRetryCount] = useState(0);
  const [isInitializing, setIsInitializing] = useState(false);
  const [recognitionState, setRecognitionState] = useState('idle'); // 'idle', 'starting', 'active', 'stopping', 'error'
  
  // Refs
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const conversationEndRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const restartTimeoutRef = useRef(null);
  const interruptTimeoutRef = useRef(null);
  const currentUtteranceRef = useRef(null);
  
  // Mobile detection
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768); // md breakpoint
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const jurisdictions = [
    { value: 'US', label: 'United States' },
    { value: 'UK', label: 'United Kingdom' },
    { value: 'CA', label: 'Canada' },
    { value: 'AU', label: 'Australia' },
    { value: 'EU', label: 'European Union' },
    { value: 'IN', label: 'India' }
  ];

  const legalDomains = [
    { value: 'all_domains', label: 'All Legal Domains' },
    { value: 'contract_law', label: 'Contract Law' },
    { value: 'employment_labor_law', label: 'Employment & Labor Law' },
    { value: 'intellectual_property', label: 'Intellectual Property' },
    { value: 'corporate_regulatory', label: 'Corporate & Regulatory' },
    { value: 'civil_criminal_procedure', label: 'Civil & Criminal Procedure' },
    { value: 'constitutional_law', label: 'Constitutional Law' },
    { value: 'taxation_financial', label: 'Taxation & Financial' },
    { value: 'real_estate_law', label: 'Real Estate Law' },
    { value: 'family_law', label: 'Family Law' },
    { value: 'immigration_law', label: 'Immigration Law' }
  ];

  const sampleQuestions = [
    "What are the key elements of a valid contract?",
    "How does employment at-will doctrine work?", 
    "What is the difference between copyright and trademark?",
    "What are the requirements for forming an LLC?",
    "How do non-compete agreements work in different states?",
    "What are the legal requirements for terminating an employee?",
    "Can you explain breach of contract remedies?",
    "What is intellectual property infringement?",
    "How do I protect my business from liability?",
    "What are the basics of employment discrimination law?"
  ];

  // Generate contextual follow-up suggestions
  const generateFollowUpSuggestions = (lastResponse, userQuestion) => {
    const suggestions = [];
    
    // Contract law follow-ups
    if (lastResponse.toLowerCase().includes('contract') || userQuestion.toLowerCase().includes('contract')) {
      suggestions.push("What happens if a contract is breached?");
      suggestions.push("Can you explain contract modification?");
      suggestions.push("What makes a contract void?");
    }
    
    // Employment law follow-ups
    if (lastResponse.toLowerCase().includes('employment') || userQuestion.toLowerCase().includes('employee')) {
      suggestions.push("What are wrongful termination laws?");
      suggestions.push("Can you explain workplace discrimination?");
      suggestions.push("What are employee rights regarding wages?");
    }
    
    // IP law follow-ups
    if (lastResponse.toLowerCase().includes('intellectual property') || lastResponse.toLowerCase().includes('copyright') || lastResponse.toLowerCase().includes('trademark')) {
      suggestions.push("How do I file for trademark protection?");
      suggestions.push("What is fair use in copyright law?");
      suggestions.push("Can you explain patent basics?");
    }
    
    // Business law follow-ups
    if (lastResponse.toLowerCase().includes('llc') || lastResponse.toLowerCase().includes('corporation') || userQuestion.toLowerCase().includes('business')) {
      suggestions.push("What are the tax implications of an LLC?");
      suggestions.push("How do I maintain corporate compliance?");
      suggestions.push("What are the differences between LLC and corporation?");
    }
    
    // Generic follow-ups if no specific category matched
    if (suggestions.length === 0) {
      suggestions.push("Can you provide more details?");
      suggestions.push("What are the practical implications?");
      suggestions.push("Are there any exceptions to this rule?");
    }
    
    return suggestions.slice(0, 3); // Return max 3 suggestions
  };

  // Enhanced cleanup utility
  const cleanupReferences = () => {
    // Clear all timeouts
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    if (interruptTimeoutRef.current) {
      clearTimeout(interruptTimeoutRef.current);
      interruptTimeoutRef.current = null;
    }
    
    // Stop speech synthesis safely
    if (synthRef.current) {
      try {
        synthRef.current.cancel();
        if (currentUtteranceRef.current) {
          currentUtteranceRef.current = null;
        }
      } catch (error) {
        console.warn('Error during speech synthesis cleanup:', error);
      }
    }
    
    // Stop recognition safely
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      } catch (error) {
        console.warn('Error during recognition cleanup:', error);
      }
    }
    
    setRecognitionState('idle');
    setIsListening(false);
    setIsSpeaking(false);
    setIsUserSpeaking(false);
    setInterimTranscript('');
  };

  // Initialize voice capabilities and session
  useEffect(() => {
    initializeVoiceCapabilities();
    initializeSession();
    
    return cleanupReferences;
  }, []);

  // Scroll to bottom when conversation updates
  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  // Categorize speech recognition errors
  const categorizeError = (error) => {
    const fatalErrors = ['not-allowed', 'audio-capture', 'service-not-allowed'];
    const retryableErrors = ['aborted', 'network', 'no-speech'];
    
    if (fatalErrors.includes(error)) {
      return 'fatal';
    } else if (retryableErrors.includes(error)) {
      return 'retryable';
    }
    return 'unknown';
  };

  // Calculate retry delay with exponential backoff
  const getRetryDelay = (attempt) => {
    return Math.min(1000 * Math.pow(2, attempt), 10000); // Max 10 seconds
  };

  const initializeVoiceCapabilities = () => {
    if (isInitializing) return;
    
    setIsInitializing(true);
    
    try {
      // Check for Web Speech API support
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        setVoiceError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
        setIsInitializing(false);
        return;
      }

      if (!('speechSynthesis' in window)) {
        setVoiceError('Speech synthesis not supported in this browser.');
        setIsInitializing(false);
        return;
      }

      // Initialize Speech Recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.maxAlternatives = 1;

      // Set up recognition event handlers with improved logic and detailed logging
      recognitionRef.current.onstart = () => {
        console.log('🎤 ✅ Speech recognition started successfully');
        console.log('🎤 Recognition state changing from', recognitionState, 'to active');
        setRecognitionState('active');
        setIsListening(true);
        setVoiceError(null);
        setRetryCount(0); // Reset retry count on successful start
      };

      recognitionRef.current.onresult = (event) => {
        console.log('🎤 📝 Speech recognition result received:', event);
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          const confidence = event.results[i][0].confidence;
          console.log(`🎤 Result ${i}:`, {
            transcript: transcript,
            confidence: confidence,
            isFinal: event.results[i].isFinal
          });
          
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        // Update interim transcript for live feedback
        setInterimTranscript(interimTranscript);
        setTranscript(finalTranscript + interimTranscript);
        
        console.log('🎤 📝 Transcripts updated:', {
          interim: interimTranscript,
          final: finalTranscript,
          combined: finalTranscript + interimTranscript
        });
        
        // Detect if user is actively speaking
        const hasInterimText = interimTranscript.trim().length > 0;
        setIsUserSpeaking(hasInterimText || finalTranscript.trim().length > 0);
        
        if (hasInterimText || finalTranscript.trim().length > 0) {
          console.log('🎤 👤 User is speaking detected');
        }
        
        // If user starts speaking while AI is speaking, interrupt
        if (hasInterimText && isSpeaking) {
          console.log('🎤 ✋ User interruption detected, stopping AI speech');
          setIsInterrupted(true);
          stopSpeaking();
        }

        // Process final transcript
        if (finalTranscript.trim()) {
          console.log('🎤 ✅ Processing final transcript:', finalTranscript.trim());
          setInterimTranscript(''); // Clear interim when we have final
          setIsUserSpeaking(false);
          processVoiceInput(finalTranscript.trim());
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('🎤 ❌ Speech recognition error:', event.error);
        console.error('🎤 ❌ Error details:', {
          error: event.error,
          message: event.message,
          timeStamp: event.timeStamp,
          type: event.type
        });
        
        const errorCategory = categorizeError(event.error);
        console.log('🎤 📊 Error category:', errorCategory);
        
        setRecognitionState('error');
        setIsListening(false);
        
        // Enhanced error messages based on specific error types
        let errorMessage = '';
        
        if (event.error === 'not-allowed') {
          errorMessage = '❌ Microphone access denied. Please click the microphone icon in your browser address bar and allow microphone access, then try again.';
          setAutoListen(false);
        } else if (event.error === 'audio-capture') {
          errorMessage = '❌ No microphone detected or microphone is not working. Please connect a working microphone and try again.';
          setAutoListen(false);
        } else if (event.error === 'service-not-allowed') {
          errorMessage = '❌ Speech recognition service is not allowed. Please check your browser settings and try again.';
          setAutoListen(false);
        } else if (event.error === 'network') {
          errorMessage = '⚠️ Network error occurred. Please check your internet connection and try again.';
        } else if (event.error === 'no-speech') {
          errorMessage = '⚠️ No speech detected. Please speak clearly into your microphone.';
        } else if (event.error === 'aborted') {
          errorMessage = '⚠️ Speech recognition was interrupted. Click "Start Listening" to try again.';
        } else if (errorCategory === 'fatal') {
          errorMessage = `❌ Speech recognition error: ${event.error}. Please check your microphone permissions and reload the page.`;
          setAutoListen(false);
          setRetryCount(0);
        } else if (errorCategory === 'retryable' && retryCount < 5) {
          errorMessage = `⚠️ Temporary issue: ${event.error}. Retrying automatically...`;
          console.log('🎤 🔄 Attempting automatic retry for retryable error');
          handleRetryableError();
          return; // Don't set error message yet
        } else {
          errorMessage = `❌ Speech recognition error: ${event.error}. Try clicking the "Retry" button or reload the page.`;
          setAutoListen(false);
          setRetryCount(0);
        }
        
        setVoiceError(errorMessage);
      };

      recognitionRef.current.onend = () => {
        console.log('🎤 🛑 Speech recognition ended');
        console.log('🎤 📊 Recognition end state:', {
          autoListen,
          isProcessing,
          isSpeaking,
          voiceError,
          isInterrupted,
          recognitionState,
          retryCount
        });
        
        setRecognitionState('idle');
        setIsListening(false);
        setIsUserSpeaking(false);
        setInterimTranscript('');
        
        // Only auto-restart if conditions are met and we're not in an error state
        if (autoListen && 
            !isProcessing && 
            !isSpeaking && 
            !voiceError && 
            !isInterrupted &&
            recognitionState !== 'error' &&
            retryCount < 3) {
          
          console.log('🎤 🔄 Auto-restart conditions met, scheduling restart...');
          
          // Clear any existing restart timeout
          if (restartTimeoutRef.current) {
            clearTimeout(restartTimeoutRef.current);
          }
          
          // Delayed restart to prevent rapid cycling
          restartTimeoutRef.current = setTimeout(() => {
            if (autoListen && !isProcessing && !isSpeaking && !voiceError && !isInterrupted) {
              console.log('🎤 🔄 Auto-restarting speech recognition...');
              startListening();
            } else {
              console.log('🎤 🚫 Auto-restart cancelled due to changed conditions');
            }
          }, 1500); // Increased delay to prevent loops
        } else {
          console.log('🎤 🚫 Auto-restart conditions not met');
        }
        
        // Reset interruption flag after a delay
        if (isInterrupted) {
          setTimeout(() => {
            console.log('🎤 🔄 Resetting interruption flag');
            setIsInterrupted(false);
          }, 2000);
        }
      };

      recognitionRef.current.onspeechstart = () => {
        console.log('🎤 🗣️ Speech started (user began speaking)');
      };

      recognitionRef.current.onspeechend = () => {
        console.log('🎤 🔇 Speech ended (user stopped speaking)');
      };

      recognitionRef.current.onsoundstart = () => {
        console.log('🎤 🔊 Sound detected');
      };

      recognitionRef.current.onsoundend = () => {
        console.log('🎤 🔇 Sound ended');
      };

      recognitionRef.current.onaudiostart = () => {
        console.log('🎤 🎵 Audio capture started');
      };

      recognitionRef.current.onaudioend = () => {
        console.log('🎤 🔇 Audio capture ended');
      };

      recognitionRef.current.onnomatch = () => {
        console.log('🎤 ❓ No speech match found');
      };

      // Initialize Speech Synthesis
      synthRef.current = window.speechSynthesis;
      
      // Load voices with multiple attempts
      loadVoices();
      
      if (synthRef.current.onvoiceschanged !== undefined) {
        synthRef.current.onvoiceschanged = loadVoices;
      }
      
      setTimeout(() => {
        loadVoices();
        setIsInitializing(false);
        console.log('Voice capabilities initialized successfully');
      }, 200);

    } catch (error) {
      console.error('Error initializing voice capabilities:', error);
      setVoiceError('Failed to initialize voice capabilities. Please reload the page.');
      setIsInitializing(false);
    }
  };

  // Handle retryable errors with exponential backoff
  const handleRetryableError = () => {
    const delay = getRetryDelay(retryCount);
    
    setRetryCount(prev => prev + 1);
    
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
    }
    
    retryTimeoutRef.current = setTimeout(() => {
      if (autoListen && !isProcessing && !isSpeaking && retryCount < 5) {
        console.log(`Retrying speech recognition (attempt ${retryCount + 1})`);
        startListening();
      }
    }, delay);
  };

  const loadVoices = () => {
    const voices = synthRef.current.getVoices();
    const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
    setAvailableVoices(englishVoices);
    
    // Set default voice with better selection criteria
    if (!selectedVoice && englishVoices.length > 0) {
      // Try to find a good female voice first
      let preferredVoice = englishVoices.find(voice => 
        voice.lang === 'en-US' && 
        (voice.name.toLowerCase().includes('female') || voice.name.toLowerCase().includes('samantha') || voice.name.toLowerCase().includes('karen'))
      );
      
      // If no female voice, try any US English voice
      if (!preferredVoice) {
        preferredVoice = englishVoices.find(voice => voice.lang === 'en-US');
      }
      
      // If no US voice, pick the first English voice
      if (!preferredVoice) {
        preferredVoice = englishVoices[0];
      }
      
      setSelectedVoice(preferredVoice);
      console.log('Selected voice:', preferredVoice?.name);
    }
  };

  const initializeSession = () => {
    const newSessionId = 'voice_session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    // Add welcome message
    const welcomeMessage = {
      id: Date.now(),
      type: 'assistant',
      content: 'Hello! I\'m your AI legal assistant. You can ask me any legal questions using your voice. I have access to over 25,000 legal documents and can help with contracts, employment law, intellectual property, and much more. How can I help you today?',
      timestamp: new Date().toISOString(),
      confidence: null
    };
    
    setConversation([welcomeMessage]);
    
    // Ensure voices are loaded and speak the welcome message
    const speakWelcome = () => {
      if (synthRef.current && selectedVoice) {
        speakText(welcomeMessage.content);
      } else {
        // If voices aren't ready yet, try again in a moment
        setTimeout(() => {
          loadVoices();
          if (synthRef.current && selectedVoice) {
            speakText(welcomeMessage.content);
          }
        }, 500);
      }
    };
    
    // Speak the welcome message after a short delay
    setTimeout(speakWelcome, 800);
  };

  // Enhanced microphone permissions and capabilities check
  const checkMicrophonePermissions = async () => {
    console.log('=== ENHANCED MICROPHONE CHECK STARTED ===');
    
    try {
      // First, check basic Web Speech API support
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        setVoiceError('❌ Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
        return false;
      }

      // Check if we're in a secure context (required for microphone access)
      if (!window.isSecureContext) {
        setVoiceError('❌ Voice recognition requires HTTPS. Please access this page via HTTPS.');
        return false;
      }

      // Check if MediaDevices API is available
      if (!('mediaDevices' in navigator) || !('getUserMedia' in navigator.mediaDevices)) {
        console.log('⚠️ MediaDevices API not available, but speech recognition might still work');
        // Don't fail here - speech recognition might work without explicit media device access
      }

      let permissionGranted = false;
      let microphoneAvailable = false;

      // Check permissions if available
      if ('permissions' in navigator) {
        try {
          const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
          console.log('🔐 Microphone permission status:', permissionStatus.state);
          
          if (permissionStatus.state === 'denied') {
            setVoiceError('❌ Microphone access denied. Please click the microphone icon in your browser address bar and allow microphone access, then reload the page.');
            return false;
          } else if (permissionStatus.state === 'granted') {
            permissionGranted = true;
            console.log('✅ Microphone permission already granted');
          } else {
            console.log('⏳ Microphone permission will be requested when needed');
          }
        } catch (permError) {
          console.log('⚠️ Could not check permissions API, proceeding with speech recognition test');
        }
      }

      // Try to detect microphone availability (but don't fail if not available)
      if ('mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices) {
        try {
          console.log('🎤 Testing microphone access with getUserMedia...');
          
          // First, try to enumerate devices to see if microphones are available
          if ('enumerateDevices' in navigator.mediaDevices) {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const audioInputs = devices.filter(device => device.kind === 'audioinput');
            console.log('🎤 Audio input devices found:', audioInputs.length);
            
            if (audioInputs.length > 0) {
              microphoneAvailable = true;
              console.log('✅ Microphone devices detected');
            } else {
              console.log('⚠️ No microphone devices detected, but speech recognition might still work');
            }
          }

          // Try getUserMedia with a short timeout
          const getUserMediaPromise = navigator.mediaDevices.getUserMedia({ 
            audio: { 
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true 
            } 
          });

          // Add timeout to prevent hanging - increase timeout for permission dialog
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('getUserMedia timeout')), 10000);
          });

          try {
            const stream = await Promise.race([getUserMediaPromise, timeoutPromise]);
            console.log('✅ Microphone access verified successfully');
            console.log('🎤 Microphone stream details:', {
              active: stream.active,
              tracks: stream.getAudioTracks().length,
              trackSettings: stream.getAudioTracks()[0]?.getSettings()
            });
            
            // Stop the stream immediately as we just needed to verify access
            stream.getTracks().forEach(track => {
              console.log('🛑 Stopping microphone track:', track.label);
              track.stop();
            });
            
            microphoneAvailable = true;
            permissionGranted = true;
            
          } catch (mediaError) {
            console.log('⚠️ getUserMedia test failed:', mediaError.name, mediaError.message);
            
            // Don't set error for common cases - let speech recognition handle it
            if (mediaError.name === 'NotAllowedError' || mediaError.name === 'PermissionDeniedError') {
              console.log('⚠️ Microphone permission not granted, will request when starting speech recognition');
            } else if (mediaError.name === 'NotFoundError') {
              console.log('⚠️ No microphone found, but speech recognition might still work');
            } else if (mediaError.message === 'getUserMedia timeout') {
              console.log('⚠️ getUserMedia timed out, but speech recognition might still work');
            } else {
              console.log('⚠️ getUserMedia failed, but attempting speech recognition anyway');
            }
          }
        } catch (deviceError) {
          console.log('⚠️ Device enumeration failed:', deviceError);
        }
      }

      // Final decision logic
      console.log('📊 Microphone check results:', {
        permissionGranted,
        microphoneAvailable,
        webSpeechSupported: true,
        secureContext: window.isSecureContext
      });

      // Always allow proceeding to speech recognition - let it handle microphone access
      console.log('✅ Proceeding with speech recognition (microphone access will be handled by browser)');
      return true;

    } catch (error) {
      console.error('❌ Error during microphone check:', error);
      
      // Don't fail completely - let speech recognition try
      console.log('⚠️ Microphone check had errors, but allowing speech recognition to try');
      return true;
      
    } finally {
      console.log('=== ENHANCED MICROPHONE CHECK COMPLETED ===');
    }
  };

  const startListening = async () => {
    console.log('🎤 🚀 === ENHANCED START LISTENING FUNCTION CALLED ===');
    
    // Prevent multiple simultaneous start attempts
    if (recognitionState === 'starting' || recognitionState === 'active' || isProcessing || isSpeaking || isInitializing) {
      console.log('🎤 🚫 Start listening blocked:', { 
        recognitionState, 
        isProcessing, 
        isSpeaking, 
        isInitializing 
      });
      return;
    }

    if (!recognitionRef.current) {
      console.warn('🎤 ❌ Recognition not initialized');
      setVoiceError('❌ Voice recognition not properly initialized. Please reload the page.');
      return;
    }

    // Enhanced microphone permissions check (non-blocking)
    console.log('🎤 🔍 Checking microphone capabilities before starting...');
    const canProceed = await checkMicrophonePermissions();
    if (!canProceed) {
      console.log('🎤 ❌ Cannot proceed with speech recognition');
      return;
    }

    try {
      console.log('🎤 ⏳ Setting recognition state to starting...');
      setRecognitionState('starting');
      setTranscript('');
      setVoiceError(null);
      
      console.log('🎤 🔧 Configuring speech recognition...');
      console.log('🎤 📊 Recognition configuration:', {
        continuous: recognitionRef.current.continuous,
        interimResults: recognitionRef.current.interimResults,
        lang: recognitionRef.current.lang,
        maxAlternatives: recognitionRef.current.maxAlternatives
      });
      
      console.log('🎤 🎯 Attempting to start speech recognition...');
      
      // Enhanced error handling for speech recognition start
      const startSpeechRecognition = () => {
        return new Promise((resolve, reject) => {
          if (!recognitionRef.current) {
            reject(new Error('Recognition object not available'));
            return;
          }

          // Set up one-time event listeners for start result
          const onStart = () => {
            console.log('🎤 ✅ Speech recognition started successfully');
            if (recognitionRef.current) {
              recognitionRef.current.removeEventListener('error', onError);
            }
            // Update state on successful start
            setRecognitionState('active');
            setIsListening(true);
            resolve();
          };

          const onError = (event) => {
            console.error('🎤 ❌ Speech recognition start error:', event.error);
            if (recognitionRef.current) {
              recognitionRef.current.removeEventListener('start', onStart);
            }
            
            // Handle specific errors during start
            if (event.error === 'not-allowed') {
              reject(new Error('Microphone permission denied. Please allow microphone access and try again.'));
            } else if (event.error === 'audio-capture') {
              reject(new Error('No microphone detected. Please connect a microphone and try again.'));
            } else if (event.error === 'service-not-allowed') {
              reject(new Error('Speech recognition service not allowed. Please check your browser settings.'));
            } else if (event.error === 'network') {
              reject(new Error('Network error. Please check your internet connection and try again.'));
            } else {
              reject(new Error(`Speech recognition error: ${event.error}. Please try again.`));
            }
          };

          // Add temporary event listeners
          recognitionRef.current.addEventListener('start', onStart, { once: true });
          recognitionRef.current.addEventListener('error', onError, { once: true });

          try {
            console.log('🎤 ▶️ Calling recognition.start()...');
            recognitionRef.current.start();
          } catch (startError) {
            // Remove event listeners on synchronous error
            if (recognitionRef.current) {
              recognitionRef.current.removeEventListener('start', onStart);
              recognitionRef.current.removeEventListener('error', onError);
            }
            
            if (startError.message && startError.message.includes('already started')) {
              console.log('🎤 ℹ️ Recognition already running, updating state');
              setRecognitionState('active');
              setIsListening(true);
              resolve();
            } else {
              console.error('🎤 ❌ Synchronous start error:', startError);
              reject(startError);
            }
          }
        });
      };

      // Try to start with timeout and better state checking
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Speech recognition start timeout')), 8000);
      });

      // Remove delay and use direct state management to prevent race conditions
      try {
        // Use current state directly instead of closure
        const currentState = recognitionRef.current ? 'ready' : 'not_ready';
        
        if (currentState === 'not_ready') {
          throw new Error('Recognition object not available during start');
        }
        
        await Promise.race([startSpeechRecognition(), timeoutPromise]);
        console.log('🎤 ✅ Speech recognition start completed successfully');
        
      } catch (error) {
        console.error('🎤 ❌ Error starting speech recognition:', error);
        
        // Set appropriate error message based on error type
        let errorMessage = '❌ Could not start voice recognition. ';
        
        if (error.message.includes('permission') || error.message.includes('not-allowed')) {
          errorMessage = '❌ Microphone permission denied. Please allow microphone access in your browser and try again.';
        } else if (error.message.includes('microphone') || error.message.includes('audio-capture')) {
          errorMessage = '❌ No microphone detected. Please connect a microphone and try again.';
        } else if (error.message.includes('timeout')) {
          errorMessage = '❌ Speech recognition start timed out. Please check your microphone and try again.';
        } else if (error.message.includes('network')) {
          errorMessage = '❌ Network error. Please check your internet connection and try again.';
        } else if (error.message.includes('state changed') || error.message.includes('Recognition state')) {
          errorMessage = '❌ Voice recognition startup interrupted. Please try clicking "Start Listening" again.';
        } else {
          errorMessage += error.message || 'Please try again or reload the page.';
        }
        
        setVoiceError(errorMessage);
        setRecognitionState('error');
        setIsListening(false);
      }
      
    } catch (error) {
      console.error('🎤 ❌ Outer error in startListening:', error);
      
      // Handle any uncaught errors
      let errorMessage = '❌ Could not start voice recognition. ';
      
      if (error.message.includes('permission') || error.message.includes('not-allowed')) {
        errorMessage = '❌ Microphone permission denied. Please allow microphone access in your browser and try again.';
      } else if (error.message.includes('microphone') || error.message.includes('audio-capture')) {
        errorMessage = '❌ No microphone detected. Please connect a microphone and try again.';
      } else if (error.message.includes('timeout')) {
        errorMessage = '❌ Speech recognition start timed out. Please check your microphone and try again.';
      } else if (error.message.includes('network')) {
        errorMessage = '❌ Network error. Please check your internet connection and try again.';
      } else {
        errorMessage += error.message || 'Please try again or reload the page.';
      }
      
      setVoiceError(errorMessage);
      setRecognitionState('error');
      setIsListening(false);
    }
    
    console.log('🎤 🏁 === ENHANCED START LISTENING FUNCTION COMPLETED ===');
  };

  const stopListening = () => {
    if (recognitionRef.current && (recognitionState === 'active' || recognitionState === 'starting')) {
      try {
        setRecognitionState('stopping');
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Error stopping speech recognition:', error);
        setRecognitionState('idle');
        setIsListening(false);
      }
    }
    
    // Clear any pending restart
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
  };

  const speakText = (text) => {
    if (!synthRef.current) {
      console.warn('Speech synthesis not available');
      return;
    }

    if (!selectedVoice) {
      console.warn('No voice selected, loading voices...');
      loadVoices();
      setTimeout(() => {
        if (selectedVoice) {
          speakText(text);
        }
      }, 500);
      return;
    }

    // Stop any ongoing speech
    stopSpeaking();
    setIsInterrupted(false);

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = speechRate;
    utterance.pitch = speechPitch;
    utterance.volume = voiceVolume;
    
    // Store reference for interruption capability
    currentUtteranceRef.current = utterance;

    utterance.onstart = () => {
      console.log('Started speaking:', text.substring(0, 50) + '...');
      setIsSpeaking(true);
      setCurrentSpeech(text);
      // Stop listening while speaking to prevent feedback
      if (recognitionState === 'active') {
        stopListening();
      }
    };

    utterance.onend = () => {
      console.log('Finished speaking');
      setIsSpeaking(false);
      setCurrentSpeech('');
      currentUtteranceRef.current = null;
      
      // Resume listening after speaking if auto-listen is enabled and not interrupted
      if (autoListen && !isProcessing && !voiceError && !isInterrupted) {
        setTimeout(() => {
          if (!isInterrupted) {
            startListening();
          }
        }, 800);
      }
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      setIsSpeaking(false);
      setCurrentSpeech('');
      currentUtteranceRef.current = null;
      setVoiceError(`Speech error: ${event.error}`);
    };

    // Enable interruption detection
    utterance.onboundary = (event) => {
      // Check for interruption every word boundary
      if (isInterrupted && currentUtteranceRef.current) {
        synthRef.current.cancel();
        return;
      }
    };

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
      setCurrentSpeech('');
      if (currentUtteranceRef.current) {
        currentUtteranceRef.current = null;
      }
    }
  };

  const processVoiceInput = async (input) => {
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    setTranscript('');
    setInterimTranscript('');
    setIsUserSpeaking(false);
    setLastUserIntent(input);

    // Add user message to conversation
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setConversation(prev => [...prev, userMessage]);
    
    // Update conversation context
    setConversationContext(prev => [...prev, { role: 'user', content: input }]);

    try {
      // Call the legal Q&A API with enhanced parameters
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/legal-qa/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: input,
          session_id: sessionId,
          jurisdiction: selectedJurisdiction,
          legal_domain: selectedDomain === 'all_domains' ? null : selectedDomain,
          is_voice: true,
          conversation_context: conversationContext.slice(-4) // Last 4 exchanges for context
        })
      });

      if (response.ok) {
        const result = await response.json();
        
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: result.answer,
          timestamp: new Date().toISOString(),
          confidence: result.confidence,
          sources: result.sources || []
        };

        setConversation(prev => [...prev, assistantMessage]);
        
        // Update conversation context
        setConversationContext(prev => [...prev, { role: 'assistant', content: result.answer }]);
        
        // Generate contextual follow-up suggestions
        const followUps = generateFollowUpSuggestions(result.answer, input);
        setSuggestedFollowUps(followUps);
        
        // Update conversation summary
        updateConversationSummary(input, result.answer);

        // Speak the response with enhanced naturalness
        const enhancedResponse = enhanceResponseForSpeech(result.answer);
        speakText(enhancedResponse);
        
      } else {
        throw new Error('Failed to get response from legal assistant');
      }
    } catch (error) {
      console.error('Error processing voice input:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'I apologize, but I encountered an error processing your question. Could you please rephrase or try again?',
        timestamp: new Date().toISOString()
      };

      setConversation(prev => [...prev, errorMessage]);
      speakText(errorMessage.content);
    } finally {
      setIsProcessing(false);
    }
  };

  // Enhance response text for more natural speech
  const enhanceResponseForSpeech = (text) => {
    // Replace symbols that shouldn't be pronounced
    let enhancedText = text
      // Handle asterisks and stars
      .replace(/\*/g, '') // Remove asterisks entirely
      .replace(/★|⭐/g, '') // Remove star symbols
      
      // Handle other common symbols
      .replace(/#/g, 'hashtag ') // Hash/pound sign
      .replace(/@/g, 'at ') // At symbol
      .replace(/&/g, 'and ') // Ampersand
      .replace(/%/g, 'percent ') // Percent sign
      .replace(/\$/g, 'dollar ') // Dollar sign
      .replace(/€/g, 'euro ') // Euro sign
      .replace(/£/g, 'pound ') // Pound sign
      .replace(/\+/g, 'plus ') // Plus sign
      .replace(/=/g, 'equals ') // Equals sign
      .replace(/</g, 'less than ') // Less than
      .replace(/>/g, 'greater than ') // Greater than
      .replace(/\|/g, ' ') // Pipe symbol - just remove
      .replace(/~/g, ' ') // Tilde - just remove
      .replace(/`/g, ' ') // Backtick - just remove
      .replace(/\^/g, ' ') // Caret - just remove
      .replace(/_/g, ' ') // Underscore - replace with space
      
      // Handle brackets and parentheses more naturally
      .replace(/\[/g, ' ') // Opening square bracket - remove
      .replace(/\]/g, ' ') // Closing square bracket - remove
      .replace(/\{/g, ' ') // Opening curly brace - remove
      .replace(/\}/g, ' ') // Closing curly brace - remove
      
      // Handle quotation marks
      .replace(/"/g, '') // Remove double quotes
      .replace(/'/g, '') // Remove single quotes
      .replace(/`/g, '') // Remove backticks
      
      // Handle multiple punctuation marks
      .replace(/\.{2,}/g, '. ') // Multiple periods
      .replace(/\?{2,}/g, '? ') // Multiple question marks
      .replace(/!{2,}/g, '! ') // Multiple exclamation marks
      
      // Add natural pauses and improve flow for speech
      .replace(/\n\n/g, '. ') // Replace paragraph breaks with pauses
      .replace(/\n/g, ', ') // Replace line breaks with commas
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/([.!?])\s*([A-Z])/g, '$1 $2') // Ensure proper spacing after sentences
      .trim();
    
    // Final cleanup - remove any remaining problematic characters
    enhancedText = enhancedText
      .replace(/[^\w\s.,!?;:()\-]/g, ' ') // Remove any remaining special characters
      .replace(/\s+/g, ' ') // Final whitespace normalization
      .trim();
    
    return enhancedText;
  };

  // Update conversation summary
  const updateConversationSummary = (question, answer) => {
    const topics = [];
    
    // Extract key legal topics from the conversation
    const legalKeywords = {
      'contract': 'Contract Law',
      'employment': 'Employment Law', 
      'intellectual property': 'IP Law',
      'trademark': 'Trademark Law',
      'copyright': 'Copyright Law',
      'llc': 'Business Formation',
      'corporation': 'Corporate Law',
      'liability': 'Liability Issues',
      'breach': 'Contract Breach',
      'termination': 'Employment Termination'
    };
    
    const combined = (question + ' ' + answer).toLowerCase();
    Object.entries(legalKeywords).forEach(([keyword, topic]) => {
      if (combined.includes(keyword) && !topics.includes(topic)) {
        topics.push(topic);
      }
    });
    
    if (topics.length > 0) {
      setConversationSummary(`Discussed: ${topics.join(', ')}`);
    }
  };

  const handleSampleQuestion = (question) => {
    processVoiceInput(question);
  };

  const resetConversation = () => {
    setConversation([]);
    setConversationContext([]);
    setSuggestedFollowUps([]);
    setConversationSummary('');
    setTranscript('');
    setInterimTranscript('');
    setIsUserSpeaking(false);
    setIsInterrupted(false);
    setRetryCount(0);
    setVoiceError(null);
    setLastUserIntent('');
    stopSpeaking();
    stopListening();
    
    // Clear all timeouts
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    if (interruptTimeoutRef.current) {
      clearTimeout(interruptTimeoutRef.current);
      interruptTimeoutRef.current = null;
    }
    
    // Reinitialize session
    setTimeout(() => {
      initializeSession();
    }, 500);
  };

  const toggleAutoListen = () => {
    const newAutoListen = !autoListen;
    setAutoListen(newAutoListen);
    
    if (newAutoListen && recognitionState === 'idle' && !isProcessing && !isSpeaking) {
      setTimeout(() => {
        startListening();
      }, 500);
    } else if (!newAutoListen) {
      stopListening();
      // Clear retry attempts when auto-listen is disabled
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
      setRetryCount(0);
    }
  };

  // Enhanced retry function with better diagnostics
  const handleRetry = async () => {
    console.log('Starting enhanced retry process...');
    setVoiceError(null);
    setRetryCount(0);
    setRecognitionState('idle');
    
    // Clear all timeouts
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    
    // Clean up existing recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
        recognitionRef.current = null;
      } catch (error) {
        console.warn('Error cleaning up recognition:', error);
      }
    }
    
    // Run diagnostics
    console.log('Running voice system diagnostics...');
    
    // Check browser support
    const hasWebSpeech = ('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window);
    const hasSpeechSynthesis = ('speechSynthesis' in window);
    
    console.log('Browser capabilities:', {
      webSpeech: hasWebSpeech,
      speechSynthesis: hasSpeechSynthesis,
      userAgent: navigator.userAgent
    });
    
    if (!hasWebSpeech) {
      setVoiceError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }
    
    // Check microphone permissions
    const hasPermission = await checkMicrophonePermissions();
    if (!hasPermission) {
      console.log('Microphone permission check failed during retry');
      return;
    }
    
    // Reinitialize if needed
    try {
      setIsInitializing(true);
      console.log('Reinitializing voice capabilities...');
      
      setTimeout(() => {
        initializeVoiceCapabilities();
        
        setTimeout(() => {
          setAutoListen(true);
          if (!isProcessing && !isSpeaking) {
            console.log('Attempting to start listening after reinitialization...');
            startListening();
          }
        }, 1000);
      }, 500);
      
    } catch (error) {
      console.error('Error during retry:', error);
      setVoiceError('Failed to reinitialize voice system. Please reload the page.');
      setIsInitializing(false);
    }
  };

  // If mobile, use mobile-optimized component
  if (isMobile) {
    return (
      <MobileVoiceAgent
        onClose={onClose}
        // Voice states
        isListening={isListening}
        setIsListening={setIsListening}
        isSpeaking={isSpeaking}
        setIsSpeaking={setIsSpeaking}
        transcript={transcript}
        setTranscript={setTranscript}
        currentSpeech={currentSpeech}
        setCurrentSpeech={setCurrentSpeech}
        conversation={conversation}
        setConversation={setConversation}
        isProcessing={isProcessing}
        setIsProcessing={setIsProcessing}
        voiceError={voiceError}
        setVoiceError={setVoiceError}
        // Voice settings
        selectedVoice={selectedVoice}
        setSelectedVoice={setSelectedVoice}
        speechRate={speechRate}
        setSpeechRate={setSpeechRate}
        speechPitch={speechPitch}
        setSpeechPitch={setSpeechPitch}
        voiceVolume={voiceVolume}
        setVoiceVolume={setVoiceVolume}
        availableVoices={availableVoices}
        setAvailableVoices={setAvailableVoices}
        autoListen={autoListen}
        setAutoListen={setAutoListen}
        // Legal Q&A settings
        sessionId={sessionId}
        setSessionId={setSessionId}
        selectedJurisdiction={selectedJurisdiction}
        setSelectedJurisdiction={setSelectedJurisdiction}
        selectedDomain={selectedDomain}
        setSelectedDomain={setSelectedDomain}
        // Enhanced states
        interimTranscript={interimTranscript}
        setInterimTranscript={setInterimTranscript}
        isUserSpeaking={isUserSpeaking}
        setIsUserSpeaking={setIsUserSpeaking}
        conversationContext={conversationContext}
        setConversationContext={setConversationContext}
        suggestedFollowUps={suggestedFollowUps}
        setSuggestedFollowUps={setSuggestedFollowUps}
        isInterrupted={isInterrupted}
        setIsInterrupted={setIsInterrupted}
        conversationSummary={conversationSummary}
        setConversationSummary={setConversationSummary}
        lastUserIntent={lastUserIntent}
        setLastUserIntent={setLastUserIntent}
        // Enhanced error handling
        retryCount={retryCount}
        setRetryCount={setRetryCount}
        isInitializing={isInitializing}
        setIsInitializing={setIsInitializing}
        recognitionState={recognitionState}
        setRecognitionState={setRecognitionState}
        // Functions
        initializeVoiceCapabilities={initializeVoiceCapabilities}
        startListening={startListening}
        stopListening={stopListening}
        processVoiceInput={processVoiceInput}
        stopSpeaking={stopSpeaking}
        resetConversation={resetConversation}
        handleRetry={handleRetry}
        jurisdictions={jurisdictions}
        legalDomains={legalDomains}
        sampleQuestions={sampleQuestions}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl h-[90vh] flex flex-col bg-white"
            style={{ zIndex: 9999 }}>
        <CardHeader className="flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="h-6 w-6 text-purple-600" />
              <div>
                <CardTitle className="text-xl">AI Voice Legal Assistant</CardTitle>
                <CardDescription>Ask legal questions using your voice</CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="p-2"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {voiceError && (
            <Alert className="mt-4">
              <AlertDescription className="flex items-center justify-between">
                <span>{voiceError}</span>
                {voiceError.includes('❌') && (
                  <Button
                    onClick={() => {
                      console.log('🔄 Force refresh requested by user');
                      window.location.reload();
                    }}
                    variant="outline"
                    size="sm"
                    className="ml-2"
                  >
                    🔄 Refresh Page
                  </Button>
                )}
              </AlertDescription>
            </Alert>
          )}
        </CardHeader>

        <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden">
          {/* Voice Controls */}
          <div className="flex-shrink-0 grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Voice Controls</h4>
              <div className="flex space-x-2">
                <Button
                  onClick={recognitionState === 'active' ? stopListening : startListening}
                  disabled={isProcessing || isInitializing || isSpeaking || recognitionState === 'starting' || recognitionState === 'stopping'}
                  className={`flex items-center space-x-2 ${
                    recognitionState === 'active' ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                  size="sm"
                >
                  {recognitionState === 'active' ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  <span>
                    {recognitionState === 'active' ? 'Stop' : 
                     recognitionState === 'starting' ? 'Starting...' :
                     recognitionState === 'stopping' ? 'Stopping...' : 
                     'Start'} Listening
                  </span>
                </Button>
                
                <Button
                  onClick={isSpeaking ? stopSpeaking : () => {}}
                  disabled={!isSpeaking}
                  variant={isSpeaking ? "destructive" : "outline"}
                  size="sm"
                >
                  {isSpeaking ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                  <span className="ml-1">{isSpeaking ? 'Stop' : 'Speak'}</span>
                </Button>

                <Button
                  onClick={resetConversation}
                  variant="outline"
                  size="sm"
                  disabled={isProcessing || isInitializing}
                >
                  <RotateCcw className="h-4 w-4" />
                  <span className="ml-1">Reset</span>
                </Button>

                <Button
                  onClick={async () => {
                    console.log('=== VOICE SYSTEM DIAGNOSTIC TEST ===');
                    
                    // Log current state
                    console.log('Current state:', {
                      recognitionState,
                      isListening,
                      isSpeaking,
                      isProcessing,
                      isInitializing,
                      autoListen,
                      retryCount,
                      voiceError
                    });
                    
                    // Test microphone permissions
                    const hasPermission = await checkMicrophonePermissions();
                    console.log('Microphone permission check result:', hasPermission);
                    
                    // Test browser support
                    const hasWebSpeech = ('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window);
                    const hasSpeechSynthesis = ('speechSynthesis' in window);
                    console.log('Browser support:', { webSpeech: hasWebSpeech, speechSynthesis: hasSpeechSynthesis });
                    
                    // Test recognition object
                    console.log('Recognition object exists:', !!recognitionRef.current);
                    
                    // Test speech synthesis
                    if (selectedVoice) {
                      console.log('Testing speech synthesis...');
                      speakText('Voice system diagnostic test complete. Check the console for detailed results.');
                    }
                    
                    console.log('=== END DIAGNOSTIC TEST ===');
                  }}
                  variant="outline"
                  size="sm"
                  disabled={isInitializing}
                  className="bg-blue-50 hover:bg-blue-100"
                >
                  <Settings className="h-4 w-4" />
                  <span className="ml-1">Test</span>
                </Button>

                {voiceError && (
                  <Button
                    onClick={handleRetry}
                    variant="outline"
                    size="sm"
                    className="bg-yellow-100 hover:bg-yellow-200"
                    disabled={isInitializing}
                  >
                    <Settings className="h-4 w-4" />
                    <span className="ml-1">{isInitializing ? 'Initializing...' : 'Retry'}</span>
                  </Button>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="autoListen"
                  checked={autoListen}
                  onChange={toggleAutoListen}
                  disabled={isInitializing}
                  className="rounded"
                />
                <label htmlFor="autoListen" className="text-sm">Auto-listen after speaking</label>
                {retryCount > 0 && (
                  <span className="text-xs text-yellow-600">
                    (Retry {retryCount}/5)
                  </span>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold text-sm">Settings</h4>
              <div className="grid grid-cols-1 gap-2">
                <div className="flex space-x-2">
                  <Select value={selectedJurisdiction} onValueChange={setSelectedJurisdiction}>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {jurisdictions.map((jurisdiction) => (
                        <SelectItem key={jurisdiction.value} value={jurisdiction.value}>
                          {jurisdiction.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <Select value={selectedDomain} onValueChange={setSelectedDomain}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Legal Domain" />
                    </SelectTrigger>
                    <SelectContent>
                      {legalDomains.map((domain) => (
                        <SelectItem key={domain.value} value={domain.value}>
                          {domain.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                {/* Voice Selection */}
                <div className="flex space-x-2">
                  <Select 
                    value={selectedVoice?.name || ''} 
                    onValueChange={(voiceName) => {
                      const voice = availableVoices.find(v => v.name === voiceName);
                      if (voice) {
                        setSelectedVoice(voice);
                        console.log('Voice changed to:', voice.name);
                      }
                    }}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Voice" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableVoices.map((voice) => (
                        <SelectItem key={voice.name} value={voice.name}>
                          {voice.name} ({voice.lang})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  {/* Voice Test Button */}
                <Button
                  onClick={async () => {
                    console.log('🎤 🧪 === ENHANCED MICROPHONE TEST STARTED ===');
                    
                    try {
                      setVoiceError('🔍 Running comprehensive microphone and speech recognition test...');
                      
                      // Test 1: Check browser support
                      const hasWebSpeech = ('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window);
                      const hasSpeechSynthesis = ('speechSynthesis' in window);
                      const hasMediaDevices = ('mediaDevices' in navigator);
                      
                      console.log('🧪 Browser Support Test:', {
                        webSpeech: hasWebSpeech,
                        speechSynthesis: hasSpeechSynthesis,
                        mediaDevices: hasMediaDevices,
                        isSecureContext: window.isSecureContext,
                        protocol: window.location.protocol,
                        userAgent: navigator.userAgent
                      });
                      
                      let testResults = [];
                      
                      if (!hasWebSpeech) {
                        setVoiceError('❌ Browser does not support speech recognition. Please use Chrome, Edge, or Safari.');
                        return;
                      }
                      testResults.push('✅ Web Speech API supported');
                      
                      if (!window.isSecureContext) {
                        setVoiceError('❌ Speech recognition requires HTTPS. Please access this page via HTTPS.');
                        return;
                      }
                      testResults.push('✅ Secure context (HTTPS)');
                      
                      // Test 2: Check device enumeration (non-blocking)
                      setVoiceError('🔍 Checking for audio devices...');
                      let microphoneDevicesFound = 0;
                      
                      if (hasMediaDevices && 'enumerateDevices' in navigator.mediaDevices) {
                        try {
                          const devices = await navigator.mediaDevices.enumerateDevices();
                          const audioInputs = devices.filter(device => device.kind === 'audioinput');
                          microphoneDevicesFound = audioInputs.length;
                          
                          console.log('🧪 Device Enumeration:', {
                            totalDevices: devices.length,
                            audioInputs: audioInputs.length,
                            devices: audioInputs.map(d => ({ id: d.deviceId, label: d.label || 'Unknown Device' }))
                          });
                          
                          if (microphoneDevicesFound > 0) {
                            testResults.push(`✅ ${microphoneDevicesFound} microphone device(s) detected`);
                          } else {
                            testResults.push('⚠️ No microphone devices detected (may still work)');
                          }
                        } catch (enumError) {
                          console.log('⚠️ Device enumeration failed:', enumError);
                          testResults.push('⚠️ Could not enumerate devices (may still work)');
                        }
                      }
                      
                      // Test 3: Try getUserMedia (non-blocking - don't fail if it doesn't work)
                      setVoiceError('🎤 Testing microphone access...');
                      let getUserMediaWorked = false;
                      
                      if (hasMediaDevices && 'getUserMedia' in navigator.mediaDevices) {
                        try {
                          const getUserMediaPromise = navigator.mediaDevices.getUserMedia({ 
                            audio: { 
                              echoCancellation: true,
                              noiseSuppression: true,
                              autoGainControl: true 
                            } 
                          });
                          
                          const timeoutPromise = new Promise((_, reject) => {
                            setTimeout(() => reject(new Error('getUserMedia timeout')), 3000);
                          });
                          
                          const stream = await Promise.race([getUserMediaPromise, timeoutPromise]);
                          
                          console.log('🧪 getUserMedia Success:', {
                            active: stream.active,
                            id: stream.id,
                            tracks: stream.getAudioTracks().map(track => ({
                              id: track.id,
                              kind: track.kind,
                              label: track.label,
                              enabled: track.enabled,
                              muted: track.muted,
                              readyState: track.readyState,
                              settings: track.getSettings()
                            }))
                          });
                          
                          // Stop the stream immediately
                          stream.getTracks().forEach(track => track.stop());
                          getUserMediaWorked = true;
                          testResults.push('✅ Microphone access granted');
                          
                        } catch (mediaError) {
                          console.log('⚠️ getUserMedia failed (this is OK):', mediaError.name, mediaError.message);
                          
                          if (mediaError.name === 'NotAllowedError') {
                            testResults.push('⚠️ Microphone permission not granted (will be requested when needed)');
                          } else if (mediaError.name === 'NotFoundError') {
                            testResults.push('⚠️ No microphone detected (speech recognition may still work)');
                          } else if (mediaError.message === 'getUserMedia timeout') {
                            testResults.push('⚠️ Microphone access timed out (speech recognition may still work)');
                          } else {
                            testResults.push('⚠️ Microphone test inconclusive (speech recognition may still work)');
                          }
                        }
                      }
                      
                      // Test 4: Speech Recognition initialization test (this is the important one)
                      setVoiceError('🔧 Testing speech recognition initialization...');
                      
                      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                      const testRecognition = new SpeechRecognition();
                      
                      console.log('🧪 Speech Recognition Test:', {
                        constructor: testRecognition.constructor.name,
                        continuous: testRecognition.continuous,
                        interimResults: testRecognition.interimResults,
                        lang: testRecognition.lang,
                        maxAlternatives: testRecognition.maxAlternatives
                      });
                      
                      testResults.push('✅ Speech Recognition object created successfully');
                      
                      // Test 5: Try a quick recognition start/stop test
                      setVoiceError('🎯 Testing speech recognition start/stop...');
                      
                      const recognitionTest = await new Promise((resolve) => {
                        let testTimeout;
                        let resolved = false;
                        
                        const resolveOnce = (result) => {
                          if (!resolved) {
                            resolved = true;
                            if (testTimeout) clearTimeout(testTimeout);
                            resolve(result);
                          }
                        };
                        
                        testRecognition.onstart = () => {
                          console.log('🧪 ✅ Test recognition started successfully');
                          setTimeout(() => {
                            try {
                              testRecognition.stop();
                            } catch (e) {
                              console.log('🧪 Note: stop() called but recognition may have already ended');
                            }
                          }, 1000);
                        };
                        
                        testRecognition.onend = () => {
                          console.log('🧪 ✅ Test recognition ended successfully');
                          resolveOnce({ success: true, message: 'Speech recognition start/stop test passed' });
                        };
                        
                        testRecognition.onerror = (event) => {
                          console.log('🧪 ⚠️ Test recognition error (this might be expected):', event.error);
                          if (event.error === 'not-allowed') {
                            resolveOnce({ success: false, message: 'Microphone permission denied (will be requested when user starts listening)', warning: true });
                          } else if (event.error === 'audio-capture') {
                            resolveOnce({ success: false, message: 'No microphone detected (users with microphones should be able to use this)', warning: true });
                          } else if (event.error === 'service-not-allowed') {
                            resolveOnce({ success: false, message: 'Speech recognition service not allowed', error: true });
                          } else {
                            resolveOnce({ success: false, message: `Speech recognition error: ${event.error}`, warning: true });
                          }
                        };
                        
                        // Set timeout for the test
                        testTimeout = setTimeout(() => {
                          resolveOnce({ success: false, message: 'Speech recognition test timed out', warning: true });
                        }, 5000);
                        
                        try {
                          testRecognition.start();
                        } catch (error) {
                          console.log('🧪 ⚠️ Test recognition start error:', error);
                          resolveOnce({ success: false, message: `Could not start test: ${error.message}`, warning: true });
                        }
                      });
                      
                      if (recognitionTest.success) {
                        testResults.push('✅ Speech recognition start/stop test passed');
                      } else if (recognitionTest.warning) {
                        testResults.push(`⚠️ ${recognitionTest.message}`);
                      } else {
                        testResults.push(`❌ ${recognitionTest.message}`);
                      }
                      
                      // Final assessment
                      const criticalErrors = testResults.filter(r => r.startsWith('❌')).length;
                      const warnings = testResults.filter(r => r.startsWith('⚠️')).length;
                      const successes = testResults.filter(r => r.startsWith('✅')).length;
                      
                      console.log('🧪 Test Results Summary:', {
                        successes,
                        warnings, 
                        criticalErrors,
                        results: testResults
                      });
                      
                      let finalMessage = '';
                      if (criticalErrors === 0) {
                        if (warnings === 0) {
                          finalMessage = '✅ All tests passed! Voice recognition should work perfectly.';
                        } else {
                          finalMessage = `✅ Basic functionality works! (${warnings} minor issues detected - voice recognition should still work for users with microphones)`;
                        }
                      } else {
                        finalMessage = `❌ Found ${criticalErrors} critical issue(s). Voice recognition may not work properly.`;
                      }
                      
                      finalMessage += `\n\nTest Results:\n${testResults.join('\n')}`;
                      setVoiceError(finalMessage);
                      
                    } catch (error) {
                      console.error('🧪 ❌ Microphone test error:', error);
                      setVoiceError(`❌ Test failed: ${error.message}. Check console for details.`);
                    } finally {
                      console.log('🧪 🏁 === ENHANCED MICROPHONE TEST COMPLETED ===');
                    }
                  }}
                  variant="outline"
                  size="sm"
                  disabled={isInitializing}
                  className="bg-green-50 hover:bg-green-100"
                >
                  <Mic className="h-4 w-4" />
                  <span className="ml-1">Mic Test+</span>
                </Button>
                </div>
                
                {/* Voice Speed Control */}
                <div className="flex items-center space-x-2">
                  <label className="text-xs text-gray-600 w-16">Speed:</label>
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={speechRate}
                    onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-xs text-gray-600 w-8">{speechRate.toFixed(1)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Status Indicators */}
          <div className="flex-shrink-0 space-y-2">
            {/* Main Status Bar */}
            <div className="flex items-center space-x-4 p-2 bg-white border rounded-lg">
              <div className="flex items-center space-x-2">
                <Activity className={`h-4 w-4 ${
                  recognitionState === 'active' ? 'text-green-500 animate-pulse' : 
                  recognitionState === 'starting' ? 'text-yellow-500 animate-pulse' :
                  recognitionState === 'stopping' ? 'text-orange-500 animate-pulse' :
                  'text-gray-400'
                }`} />
                <span className="text-sm">
                  {recognitionState === 'active' ? 'Listening...' :
                   recognitionState === 'starting' ? 'Starting...' :
                   recognitionState === 'stopping' ? 'Stopping...' :
                   recognitionState === 'error' ? 'Error' :
                   'Not listening'}
                </span>
                {isUserSpeaking && (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                    Speaking
                  </span>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <Volume2 className={`h-4 w-4 ${isSpeaking ? 'text-blue-500 animate-pulse' : 'text-gray-400'}`} />
                <span className="text-sm">{isSpeaking ? 'AI Speaking...' : 'Silent'}</span>
                {selectedVoice && !isSpeaking && (
                  <span className="text-xs text-gray-500">({selectedVoice.name.split(' ')[0]})</span>
                )}
                {isInterrupted && (
                  <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full">
                    Interrupted
                  </span>
                )}
              </div>

              {isProcessing && (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                  <span className="text-sm">Processing...</span>
                </div>
              )}

              {isInitializing && (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-sm">Initializing...</span>
                </div>
              )}
            </div>

            {/* Live Transcript Display */}
            {(transcript || interimTranscript) && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="text-sm text-blue-800">
                  <span className="font-medium">Live Transcript:</span>
                  <div className="mt-1">
                    {transcript && <span className="text-blue-900">{transcript}</span>}
                    {interimTranscript && (
                      <span className="text-blue-600 italic opacity-70">
                        {transcript && ' '}{interimTranscript}
                        <span className="animate-pulse">|</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Conversation Summary */}
            {conversationSummary && (
              <div className="p-2 bg-purple-50 border border-purple-200 rounded-lg">
                <div className="text-sm text-purple-800">
                  <span className="font-medium">Session Summary:</span> {conversationSummary}
                </div>
              </div>
            )}
          </div>

          {/* Enhanced Conversation Area */}
          <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-4">
            {conversation.map((message, index) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className={`flex-shrink-0 ${
                  message.type === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : message.type === 'error'
                    ? 'bg-red-600 text-white'
                    : 'bg-purple-600 text-white'
                } rounded-full p-2`}>
                  {message.type === 'user' ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>

                <div className={`flex-1 ${
                  message.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  <div className={`inline-block p-3 rounded-lg max-w-xs md:max-w-md lg:max-w-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.type === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-white shadow-sm border'
                  }`}>
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    
                    {/* Enhanced message metadata */}
                    <div className="mt-2 flex items-center justify-between">
                      {message.confidence && (
                        <Badge variant="outline" className="text-xs">
                          Confidence: {Math.round(message.confidence * 100)}%
                        </Badge>
                      )}
                      
                      {message.type === 'assistant' && (
                        <div className="flex items-center space-x-1">
                          {isSpeaking && index === conversation.length - 1 && (
                            <Button
                              onClick={() => {
                                setIsInterrupted(true);
                                stopSpeaking();
                              }}
                              variant="ghost"
                              size="sm"
                              className="text-xs h-6 px-2 hover:bg-gray-100"
                            >
                              ✋ Stop
                            </Button>
                          )}
                          
                          {!isSpeaking && (
                            <Button
                              onClick={() => speakText(message.content)}
                              variant="ghost"
                              size="sm"
                              className="text-xs h-6 px-2 hover:bg-gray-100"
                              disabled={isProcessing}
                            >
                              🔊 Repeat
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500 mt-1 flex items-center justify-between">
                    <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                    
                    {/* Context indicator for follow-up questions */}
                    {message.type === 'user' && index > 0 && (
                      <span className="bg-gray-200 text-gray-600 px-2 py-1 rounded-full text-xs">
                        Follow-up
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Processing indicator */}
            {isProcessing && (
              <div className="flex items-center justify-center p-4">
                <div className="flex items-center space-x-2 text-purple-600">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={conversationEndRef} />
          </div>

          {/* Enhanced Sample Questions and Follow-ups */}
          <div className="flex-shrink-0 space-y-3">
            {/* Follow-up Suggestions */}
            {suggestedFollowUps.length > 0 && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-sm text-green-800 mb-2">💡 Follow-up Questions:</h4>
                <div className="flex flex-wrap gap-2">
                  {suggestedFollowUps.map((question, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => processVoiceInput(question)}
                      disabled={isProcessing || isSpeaking}
                      className="text-xs bg-white hover:bg-green-50 border-green-300 text-green-700"
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Sample Questions */}
            <div className="p-3 bg-white border rounded-lg">
              <h4 className="font-semibold text-sm mb-2">
                {conversation.length > 1 ? '🎯 More Questions:' : '🎯 Try asking:'}
              </h4>
              <div className="flex flex-wrap gap-2">
                {sampleQuestions.slice(0, 3).map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => processVoiceInput(question)}
                    disabled={isProcessing || isSpeaking}
                    className="text-xs"
                  >
                    {question}
                  </Button>
                ))}
              </div>
              
              {/* Interrupt Button */}
              {isSpeaking && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <Button
                    onClick={() => {
                      setIsInterrupted(true);
                      stopSpeaking();
                    }}
                    variant="outline"
                    size="sm"
                    className="text-xs bg-orange-50 hover:bg-orange-100 border-orange-300 text-orange-700"
                  >
                    ✋ Interrupt & Ask New Question
                  </Button>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VoiceAgent;