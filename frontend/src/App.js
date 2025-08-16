import React, { useState, useEffect, useCallback, memo } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Calendar as CalendarComponent } from './components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './components/ui/popover';
import EnhancedContractWizard from './components/EnhancedContractWizard';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import PlainEnglishContractCreator from './components/PlainEnglishContractCreator';
import LegalQuestionAnswering from './components/LegalQuestionAnswering';
import VoiceAgent from './components/VoiceAgent';
import LitigationAnalytics from './components/LitigationAnalytics';
import LegalResearchDashboard from './components/LegalResearchDashboard';
import ResizeObserverErrorBoundary from './components/ResizeObserverErrorBoundary';
// Compliance System Components
import AttorneyDashboard from './components/AttorneyDashboard';
import { AttorneySupervisionNotice, ComplianceModeIndicator, LegalDisclaimerFooter } from './components/ComplianceNotices';
import ConsentManager from './components/ConsentManager';
import AIAgentHub from './components/AIAgentHub';
// Mobile Responsive Components
import { ResponsiveHeader, BottomNavigation } from './components/ResponsiveNavigation';
import MobileOptimizedHero from './components/MobileOptimizedHero';
import MobileContractWizard from './components/MobileContractWizard';
import MobileAnalyticsDashboard from './components/MobileAnalyticsDashboard';
import { 
  MobileModal, 
  MobileBottomSheet, 
  MobileActionSheet,
  MobileConfirmDialog,
  MobileLoadingModal,
  MobileToastModal 
} from './components/MobileModalSystem';
import { usePerformanceMonitor, MobilePerformanceDashboard } from './components/MobilePerformanceOptimizer';
import { FileText, Zap, Shield, Users, CheckCircle, AlertTriangle, Download, Eye, Calendar, Sparkles, Wand2, Clock, BarChart3, MessageSquare, Scale, Mic, Search, Bot } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Move PartiesStep outside the App component to prevent re-creation
const PartiesStep = ({ contractData, updateParties, setCurrentStep }) => (
  <Card className="w-full max-w-2xl mx-auto">
    <CardHeader>
      <CardTitle className="text-2xl">Party Information</CardTitle>
      <CardDescription>Enter details about the parties involved</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="party1_name">Party 1 Name</Label>
          <Input 
            id="party1_name"
            placeholder="Company or Individual Name"
            value={contractData.parties.party1_name || ''}
            onChange={(e) => updateParties('party1_name', e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="party1_type">Party 1 Type</Label>
          <Select value={contractData.parties.party1_type || ''} onValueChange={(value) => 
            updateParties('party1_type', value)
          }>
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="individual">Individual</SelectItem>
              <SelectItem value="company">Company</SelectItem>
              <SelectItem value="llc">LLC</SelectItem>
              <SelectItem value="corporation">Corporation</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label htmlFor="party2_name">Party 2 Name</Label>
          <Input 
            id="party2_name"
            placeholder="Company or Individual Name"
            value={contractData.parties.party2_name || ''}
            onChange={(e) => updateParties('party2_name', e.target.value)}
          />
        </div>
        <div>
          <Label htmlFor="party2_type">Party 2 Type</Label>
          <Select value={contractData.parties.party2_type || ''} onValueChange={(value) => 
            updateParties('party2_type', value)
          }>
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="individual">Individual</SelectItem>
              <SelectItem value="company">Company</SelectItem>
              <SelectItem value="llc">LLC</SelectItem>
              <SelectItem value="corporation">Corporation</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex gap-4 mt-6">
        <Button variant="outline" onClick={() => setCurrentStep(1)}>
          Back
        </Button>
        <Button 
          onClick={() => setCurrentStep(3)} 
          disabled={!contractData.parties.party1_name || !contractData.parties.party2_name}
          className="flex-1"
        >
          Next: Terms & Conditions
        </Button>
      </div>
    </CardContent>
  </Card>
);

// Move TermsStep outside the App component to prevent re-creation
const TermsStep = ({ contractData, contractTypes, updateTerms, setContractData, generateContract, isGenerating, setCurrentStep }) => (
  <Card className="w-full max-w-2xl mx-auto">
    <CardHeader>
      <CardTitle className="text-2xl">Terms & Conditions</CardTitle>
      <CardDescription>Specify the key terms of your contract</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      {contractData.contract_type === 'NDA' && (
        <>
          <div>
            <Label htmlFor="purpose">Purpose of Disclosure</Label>
            <Textarea
              id="purpose"
              placeholder="Describe why confidential information will be shared..."
              value={contractData.terms.purpose || ''}
              onChange={(e) => updateTerms('purpose', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="duration">Agreement Duration</Label>
            <Select value={contractData.terms.duration || ''} onValueChange={(value) => 
              updateTerms('duration', value)
            }>
              <SelectTrigger>
                <SelectValue placeholder="Select duration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1_year">1 Year</SelectItem>
                <SelectItem value="2_years">2 Years</SelectItem>
                <SelectItem value="3_years">3 Years</SelectItem>
                <SelectItem value="5_years">5 Years</SelectItem>
                <SelectItem value="indefinite">Indefinite</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </>
      )}

      {contractData.contract_type === 'freelance_agreement' && (
        <>
          <div>
            <Label htmlFor="scope">Scope of Work</Label>
            <Textarea
              id="scope"
              placeholder="Describe the services to be provided..."
              value={contractData.terms.scope || ''}
              onChange={(e) => updateTerms('scope', e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="payment_amount">Payment Amount</Label>
              <Input
                id="payment_amount"
                placeholder="$5,000"
                value={contractData.terms.payment_amount || ''}
                onChange={(e) => updateTerms('payment_amount', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="payment_terms">Payment Terms</Label>
              <Select value={contractData.terms.payment_terms || ''} onValueChange={(value) => 
                updateTerms('payment_terms', value)
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Select terms" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="upfront">100% Upfront</SelectItem>
                  <SelectItem value="milestone">Milestone-based</SelectItem>
                  <SelectItem value="net30">Net 30 Days</SelectItem>
                  <SelectItem value="net15">Net 15 Days</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </>
      )}

      {contractData.contract_type === 'partnership_agreement' && (
        <>
          <div>
            <Label htmlFor="business_purpose">Business Purpose</Label>
            <Textarea
              id="business_purpose"
              placeholder="Describe the purpose of the partnership..."
              value={contractData.terms.business_purpose || ''}
              onChange={(e) => updateTerms('business_purpose', e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="profit_split">Profit Split (%)</Label>
              <Input
                id="profit_split"
                placeholder="50/50"
                value={contractData.terms.profit_split || ''}
                onChange={(e) => updateTerms('profit_split', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="capital_contribution">Capital Contribution</Label>
              <Input
                id="capital_contribution"
                placeholder="$10,000 each"
                value={contractData.terms.capital_contribution || ''}
                onChange={(e) => updateTerms('capital_contribution', e.target.value)}
              />
            </div>
          </div>
        </>
      )}

      <div>
        <Label htmlFor="execution_date">Select Date of Execution:</Label>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={`w-full justify-start text-left font-normal ${
                !contractData.execution_date && "text-muted-foreground"
              }`}
            >
              <Calendar className="mr-2 h-4 w-4" />
              {contractData.execution_date ? (
                new Date(contractData.execution_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })
              ) : (
                <span>Pick a date</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0">
            <CalendarComponent
              mode="single"
              selected={contractData.execution_date ? new Date(contractData.execution_date) : undefined}
              onSelect={(date) => setContractData(prev => ({ 
                ...prev, 
                execution_date: date ? date.toISOString() : null
              }))}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      <div>
        <Label htmlFor="special_clauses">Special Clauses (Optional)</Label>
        <Textarea
          id="special_clauses"
          placeholder="Any additional clauses or terms..."
          value={contractData.special_clauses.join('\n')}
          onChange={(e) => setContractData(prev => ({ 
            ...prev, 
            special_clauses: e.target.value.split('\n').filter(c => c.trim())
          }))}
        />
      </div>

      <div className="flex gap-4 mt-6">
        <Button variant="outline" onClick={() => setCurrentStep(2)}>
          Back
        </Button>
        <Button 
          onClick={generateContract} 
          disabled={isGenerating}
          className="flex-1 bg-blue-600 hover:bg-blue-700"
        >
          {isGenerating ? (
            <>
              <Zap className="mr-2 h-4 w-4 animate-spin" />
              Generating Contract...
            </>
          ) : (
            <>
              <FileText className="mr-2 h-4 w-4" />
              Generate Contract
            </>
          )}
        </Button>
      </div>
    </CardContent>
  </Card>
);

function App() {
  const [contractTypes, setContractTypes] = useState([]);
  const [jurisdictions, setJurisdictions] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [contractData, setContractData] = useState({
    contract_type: '',
    jurisdiction: 'US',
    parties: {},
    terms: {},
    special_clauses: [],
    execution_date: null
  });
  const [generatedContract, setGeneratedContract] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [contracts, setContracts] = useState([]);
  const [useEnhancedWizard, setUseEnhancedWizard] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showPlainEnglishCreator, setShowPlainEnglishCreator] = useState(false);
  const [showLegalQA, setShowLegalQA] = useState(false);
  const [showVoiceAgent, setShowVoiceAgent] = useState(false);
  const [showLitigationAnalytics, setShowLitigationAnalytics] = useState(false);
  const [showLegalResearch, setShowLegalResearch] = useState(false);
  const [showAIAgentHub, setShowAIAgentHub] = useState(false);
  
  // Compliance System State
  const [showAttorneyDashboard, setShowAttorneyDashboard] = useState(false);
  const [complianceMode, setComplianceMode] = useState(true);
  const [showConsentManager, setShowConsentManager] = useState(false);
  const [clientConsent, setClientConsent] = useState(false);
  const [consentJustProvided, setConsentJustProvided] = useState(false);
  const [clientId] = useState(() => localStorage.getItem('client_id') || `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [currentReviewId, setCurrentReviewId] = useState(null);
  const [complianceStatus, setComplianceStatus] = useState(null);

  // Mobile Navigation State
  const [currentView, setCurrentView] = useState('home');

  // Mobile-specific State
  const [useMobileWizard, setUseMobileWizard] = useState(false);
  const [useMobileAnalytics, setUseMobileAnalytics] = useState(false);
  const [useMobileLegalQA, setUseMobileLegalQA] = useState(false);
  const [useMobileVoiceAgent, setUseMobileVoiceAgent] = useState(false);
  const [useMobileAIAgentHub, setUseMobileAIAgentHub] = useState(false);
  const [showMobileModal, setShowMobileModal] = useState(false);
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);
  const [mobileToast, setMobileToast] = useState(null);
  
  // Performance monitoring
  const performanceMetrics = usePerformanceMonitor();

  // Navigation handler for mobile responsive navigation
  const handleNavigation = (view, isMobile = false) => {
    // Reset all view states
    setUseEnhancedWizard(false);
    setShowAnalytics(false);
    setShowPlainEnglishCreator(false);
    setShowLegalQA(false);
    setShowVoiceAgent(false);
    setShowLitigationAnalytics(false);
    setShowLegalResearch(false);
    setShowAIAgentHub(false);
    
    // Reset mobile states
    setUseMobileWizard(false);
    setUseMobileAnalytics(false);
    setUseMobileLegalQA(false);
    setUseMobileVoiceAgent(false);
    setUseMobileAIAgentHub(false);
    
    // Set current view for navigation state
    setCurrentView(view);
    
    // Handle specific view logic with mobile optimization
    switch(view) {
      case 'home':
        // Already reset all states above
        break;
      case 'enhanced-wizard':
        if (isMobile && window.innerWidth <= 768) {
          setUseMobileWizard(true);
        } else {
          setUseEnhancedWizard(true);
        }
        break;
      case 'mobile-wizard':
        setUseMobileWizard(true);
        break;
      case 'plain-english':
        setShowPlainEnglishCreator(true);
        break;
      case 'legal-qa':
        setShowLegalQA(true);
        break;
      case 'voice-agent':
        setShowVoiceAgent(true);
        break;
      case 'legal-research':
        setShowLegalResearch(true);
        break;
      case 'ai-agent-hub':
        setShowAIAgentHub(true);
        break;
      case 'analytics':
        if (isMobile && window.innerWidth <= 768) {
          setUseMobileAnalytics(true);
        } else {
          setShowAnalytics(true);
        }
        break;
      case 'mobile-analytics':
        setUseMobileAnalytics(true);
        break;
      case 'litigation-analytics':
        setShowLitigationAnalytics(true);
        break;
      case 'performance-monitor':
        setShowPerformanceMonitor(true);
        break;
      case 'classic-mode':
        setCurrentStep(1);
        break;
      default:
        break;
    }
  };

  useEffect(() => {
    loadContractTypes();
    loadJurisdictions();
    loadContracts();
    checkComplianceStatus();
    
    // Save client ID to localStorage for persistence
    localStorage.setItem('client_id', clientId);
  }, [clientId]);

  // Simplified ResizeObserver console error suppression
  useEffect(() => {
    // Suppress ResizeObserver console warnings
    const originalConsoleError = console.error;
    const originalConsoleWarn = console.warn;
    
    console.error = (...args) => {
      const message = args.join(' ');
      if (message.includes('ResizeObserver') || 
          message.includes('loop completed') ||
          message.includes('undelivered notifications')) {
        return; // Suppress ResizeObserver warnings
      }
      originalConsoleError.apply(console, args);
    };

    console.warn = (...args) => {
      const message = args.join(' ');
      if (message.includes('ResizeObserver') || 
          message.includes('loop completed') ||
          message.includes('undelivered notifications')) {
        return; // Suppress ResizeObserver warnings
      }
      originalConsoleWarn.apply(console, args);
    };

    // Additional global error handler for runtime errors
    const handleGlobalError = (event) => {
      if (event.message && event.message.includes('ResizeObserver')) {
        event.stopImmediatePropagation();
        event.preventDefault();
        return false;
      }
    };

    window.addEventListener('error', handleGlobalError);

    return () => {
      // Restore original console methods on cleanup
      console.error = originalConsoleError;
      console.warn = originalConsoleWarn;
      window.removeEventListener('error', handleGlobalError);
    };
  }, []);

  const loadContractTypes = async () => {
    try {
      const response = await axios.get(`${API}/contract-types`);
      setContractTypes(response.data.types);
    } catch (error) {
      console.error('Error loading contract types:', error);
    }
  };

  const loadJurisdictions = async () => {
    try {
      const response = await axios.get(`${API}/jurisdictions`);
      setJurisdictions(response.data.jurisdictions);
    } catch (error) {
      console.error('Error loading jurisdictions:', error);
    }
  };

  const loadContracts = async () => {
    try {
      const response = await axios.get(`${API}/contracts`);
      setContracts(response.data);
    } catch (error) {
      console.error('Error loading contracts:', error);
    }
  };

  const updateParties = (field, value) => {
    setContractData(prev => ({
      ...prev,
      parties: { ...prev.parties, [field]: value }
    }));
  };

  const updateTerms = (field, value) => {
    setContractData(prev => ({
      ...prev,
      terms: { ...prev.terms, [field]: value }
    }));
  };

  // Mobile toast helper
  const showMobileToast = (type, title, message, duration = 3000) => {
    setMobileToast({ type, title, message, duration });
  };

  const generateContract = async () => {
    console.log('🔄 Starting generateContract function...');
    console.log('🔍 Current state - isGenerating:', isGenerating, 'consentJustProvided:', consentJustProvided);
    
    setIsGenerating(true);
    try {
      // Always show consent manager in compliance mode - unless consent was just provided
      if (complianceMode && !consentJustProvided) {
        console.log('🔒 Showing consent manager...');
        setShowConsentManager(true);
        // Keep isGenerating true and return - don't call finally block
        return;
      }
      
      // Reset the consent flag after successful consent check
      if (consentJustProvided) {
        console.log('✅ Consent was just provided, continuing with generation...');
        setConsentJustProvided(false);
      }

      console.log('🔄 Calling contract generation API...');
      console.log('📋 Contract data:', contractData);
      console.log('👤 Client ID:', clientId);

      // Use compliant contract generation endpoint
      const endpoint = complianceMode ? '/generate-contract-compliant' : '/generate-contract';
      const fullUrl = `${API}${endpoint}`;
      console.log('🌐 API URL:', fullUrl);

      const requestData = {
        ...contractData,
        client_id: clientId
      };
      console.log('📤 Request data:', requestData);

      const response = await axios.post(fullUrl, requestData);
      console.log('✅ Contract generation API call successful');
      console.log('📥 Full response:', response.data);
      
      setGeneratedContract(response.data);
      
      // Enhanced review ID extraction with more debugging
      console.log('🔍 Checking for review ID in suggestions...');
      const suggestions = response.data.suggestions;
      console.log('📝 Suggestions array:', suggestions);
      console.log('📝 Suggestions type:', typeof suggestions);
      console.log('📝 Is array?', Array.isArray(suggestions));
      
      if (suggestions && Array.isArray(suggestions)) {
        console.log('🔍 Searching through suggestions for review ID...');
        
        let reviewIdFound = null;
        for (let i = 0; i < suggestions.length; i++) {
          const suggestion = suggestions[i];
          console.log(`📝 Suggestion ${i}:`, suggestion);
          
          // Multiple patterns to catch review ID
          if (suggestion && (
            suggestion.includes('review (ID:') || 
            suggestion.includes('review ID:') ||
            suggestion.includes('ID:')
          )) {
            console.log('🎯 Found potential review ID match:', suggestion);
            
            // Try multiple regex patterns
            const patterns = [
              /review \(ID:\s*([^)]+)\)/i,
              /review ID:\s*([^)]+)/i,
              /ID:\s*([^)\s,]+)/i
            ];
            
            for (const pattern of patterns) {
              const match = suggestion.match(pattern);
              if (match && match[1]) {
                reviewIdFound = match[1].trim();
                console.log('✅ Successfully extracted review ID:', reviewIdFound);
                break;
              }
            }
            
            if (reviewIdFound) break;
          }
        }
        
        if (reviewIdFound) {
          console.log('🎉 Setting currentReviewId to:', reviewIdFound);
          setCurrentReviewId(reviewIdFound);
          
          // Additional verification - check if the review ID is valid
          setTimeout(async () => {
            try {
              const statusResponse = await axios.get(`${API}/api/attorney/review/status/${reviewIdFound}`);
              console.log('✅ Review status verification successful:', statusResponse.data);
            } catch (statusError) {
              console.error('❌ Review status verification failed:', statusError);
            }
          }, 2000);
          
        } else {
          console.log('❌ Could not extract review ID from suggestions');
          console.log('📝 Available suggestions for debugging:', suggestions);
        }
      } else {
        console.log('❌ No suggestions array found in response');
        console.log('📊 Response structure:', Object.keys(response.data));
      }
      
      console.log('🔄 Moving to step 4 (Contract Result)...');
      setCurrentStep(4);
      
      console.log('📚 Loading contracts...');
      await loadContracts();
      
      console.log('✅ Contract generation completed successfully');
      
    } catch (error) {
      console.error('❌ Error in generateContract:', error);
      console.error('❌ Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config
      });
      
      // More detailed error message
      let errorMessage = 'Failed to generate contract. ';
      if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage += error.response.data.message;  
      } else if (error.message) {
        errorMessage += error.message;
      }
      
      alert(errorMessage);
      
      // Reset state on error
      setCurrentStep(3); // Go back to terms step
    } finally {
      // Only set isGenerating to false if we're not showing consent manager
      if (!showConsentManager) {
        console.log('🏁 Ending generateContract function, setting isGenerating to false');
        setIsGenerating(false);
      } else {
        console.log('🔒 Keeping isGenerating true - consent manager is shown');
      }
    }
  };

  // Compliance System Functions
  const checkComplianceStatus = async () => {
    try {
      const response = await axios.get(`${API}/compliance/status`);
      setComplianceStatus(response.data);
      setComplianceMode(response.data.compliance_mode);
    } catch (error) {
      console.error('Error checking compliance status:', error);
      // Default to compliance mode if check fails
      setComplianceMode(true);
    }
  };

  const checkExistingClientConsent = async () => {
    try {
      const response = await axios.get(`${API}/api/client/consent/check/${clientId}`);
      const hasConsent = response.data.has_consent;
      setClientConsent(hasConsent);
    } catch (error) {
      console.error('Failed to check existing client consent:', error);
      // Default to no consent if check fails
      setClientConsent(false);
    }
  };

  const handleConsentGiven = (consentGiven) => {
    console.log('✅ Consent given callback triggered:', consentGiven);
    console.log('🔍 Current isGenerating state:', isGenerating);
    
    setClientConsent(consentGiven);
    setShowConsentManager(false);
    setConsentJustProvided(true); // Flag that consent was just provided
    
    if (consentGiven) {
      console.log('🔄 Resuming contract generation after consent...');
      // Resume contract generation immediately - no delay needed
      generateContract();
    }
  };

  const handleConsentDeclined = () => {
    console.log('❌ Consent declined');
    setShowConsentManager(false);
    setIsGenerating(false); // Make sure to reset the generating state when consent is declined
    alert('Consent is required to use legal services. Please provide consent to continue.');
  };

  const handleReviewStatusChange = (newStatus) => {
    // Handle review status changes (e.g., show notifications)
    if (newStatus.status === 'approved') {
      alert('Great! Your document has been approved by an attorney.');
    } else if (newStatus.status === 'rejected') {
      alert('Your document requires revision. Please check the attorney feedback.');
    }
  };

  const ContractTypeStep = () => (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Choose Contract Type</CardTitle>
        <CardDescription>Select the type of legal document you need</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4">
          {contractTypes.map((type) => (
            <Card 
              key={type.id}
              className={`cursor-pointer transition-all hover:shadow-md ${
                contractData.contract_type === type.id ? 'ring-2 ring-blue-500 bg-blue-50' : ''
              }`}
              onClick={() => setContractData(prev => ({ ...prev, contract_type: type.id }))}
            >
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{type.name}</h3>
                    <p className="text-gray-600 mt-1">{type.description}</p>
                  </div>
                  <Badge variant={type.complexity === 'Simple' ? 'secondary' : 
                                type.complexity === 'Medium' ? 'default' : 'destructive'}>
                    {type.complexity}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {contractData.contract_type && (
          <div className="mt-6">
            <Label htmlFor="jurisdiction">Jurisdiction</Label>
            <Select value={contractData.jurisdiction} onValueChange={(value) => 
              setContractData(prev => ({ ...prev, jurisdiction: value }))
            }>
              <SelectTrigger>
                <SelectValue placeholder="Select jurisdiction" />
              </SelectTrigger>
              <SelectContent>
                {jurisdictions.filter(j => j.supported).map((jurisdiction) => (
                  <SelectItem key={jurisdiction.code} value={jurisdiction.code}>
                    {jurisdiction.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <Button 
          onClick={() => setCurrentStep(2)} 
          disabled={!contractData.contract_type}
          className="w-full mt-6"
        >
          Next: Party Information
        </Button>
      </CardContent>
    </Card>
  );

  // Remove the old TermsStep definition - it's now defined outside App component

  const ContractResult = () => {
    const [editedContent, setEditedContent] = useState('');
    const [hasEdits, setHasEdits] = useState(false);
    const [activeTab, setActiveTab] = useState('edit');
    const [firstPartySignature, setFirstPartySignature] = useState(null);
    const [secondPartySignature, setSecondPartySignature] = useState(null);
    const [uploadingSignature, setUploadingSignature] = useState(null);

    // Initialize edited content when component mounts
    useEffect(() => {
      if (generatedContract?.contract?.content && !editedContent) {
        setEditedContent(generatedContract.contract.content);
        // Load existing signatures
        loadExistingSignatures();
      }
    }, [generatedContract, editedContent]);

    const loadExistingSignatures = async () => {
      if (!generatedContract?.contract?.id) return;
      
      try {
        const response = await axios.get(`${API}/contracts/${generatedContract.contract.id}/signatures`);
        const { first_party_signature, second_party_signature } = response.data;
        
        if (first_party_signature) {
          setFirstPartySignature(`data:image/png;base64,${first_party_signature}`);
        }
        if (second_party_signature) {
          setSecondPartySignature(`data:image/png;base64,${second_party_signature}`);
        }
      } catch (error) {
        console.error('Error loading existing signatures:', error);
      }
    };

    const handleContentChange = (value) => {
      setEditedContent(value);
      setHasEdits(value !== generatedContract.contract.content);
    };

    const handleConfirmEdit = () => {
      setActiveTab('preview');
    };

    // Signature upload handlers
    const handleSignatureUpload = async (partyType, file) => {
      try {
        setUploadingSignature(partyType);
        
        // Validate file type
        if (!['image/png', 'image/jpg', 'image/jpeg'].includes(file.type)) {
          alert('Please upload a PNG, JPG, or JPEG image file.');
          return;
        }
        
        // Validate file size (1MB limit)
        if (file.size > 1024 * 1024) {
          alert('File size must be less than 1MB.');
          return;
        }
        
        // Convert to base64
        const reader = new FileReader();
        reader.onload = async (e) => {
          const base64Data = e.target.result.split(',')[1]; // Remove data URL prefix
          
          try {
            // Upload signature to backend
            const response = await axios.post(`${API}/contracts/${generatedContract.contract.id}/upload-signature`, {
              contract_id: generatedContract.contract.id,
              party_type: partyType,
              signature_image: base64Data
            });
            
            // Update local state
            if (partyType === 'first_party') {
              setFirstPartySignature(e.target.result);
            } else {
              setSecondPartySignature(e.target.result);
            }
            
            // Update contract content with signature
            updateContractWithSignature(partyType, e.target.result);
            
            alert(`${partyType === 'first_party' ? 'First' : 'Second'} party signature uploaded successfully!`);
          } catch (error) {
            console.error('Error uploading signature:', error);
            alert('Error uploading signature. Please try again.');
          } finally {
            setUploadingSignature(null);
          }
        };
        
        reader.readAsDataURL(file);
      } catch (error) {
        console.error('Error processing signature:', error);
        alert('Error processing signature. Please try again.');
        setUploadingSignature(null);
      }
    };

    const updateContractWithSignature = (partyType, signatureDataUrl) => {
      const placeholder = partyType === 'first_party' 
        ? '[First Party Signature Placeholder]' 
        : '[Second Party Signature Placeholder]';
      
      // Replace placeholder with signature indicator in content
      const updatedContent = editedContent.replace(
        placeholder,
        `[${partyType === 'first_party' ? 'First' : 'Second'} Party Signature Uploaded]`
      );
      
      setEditedContent(updatedContent);
      setHasEdits(true);
    };

    const triggerFileUpload = (partyType) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/png,image/jpg,image/jpeg';
      input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
          handleSignatureUpload(partyType, file);
        }
      };
      input.click();
    };

    const downloadPDF = async (contentToDownload) => {
      if (!generatedContract?.contract?.id) {
        alert('No contract available for download');
        return;
      }

      try {
        // If we have edited content, we need to send it to the backend for PDF generation
        if (contentToDownload && contentToDownload !== generatedContract.contract.content) {
          // Create a temporary contract with the edited content for download
          const editedContractData = {
            ...generatedContract.contract,
            content: contentToDownload,
            first_party_signature: firstPartySignature ? firstPartySignature.split(',')[1] : null,
            second_party_signature: secondPartySignature ? secondPartySignature.split(',')[1] : null
          };
          
          const response = await axios.post(`${API}/contracts/download-pdf-edited`, {
            contract: editedContractData
          }, {
            responseType: 'blob'
          });
          
          // Create blob link to download
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `contract_${generatedContract.contract.id}_edited.pdf`);
          
          // Append to body, click and remove
          document.body.appendChild(link);
          link.click();
          link.remove();
          
          // Clean up the URL
          window.URL.revokeObjectURL(url);
        } else {
          // Use original PDF download endpoint
          const response = await axios.get(`${API}/contracts/${generatedContract.contract.id}/download-pdf`, {
            responseType: 'blob'
          });
          
          // Create blob link to download
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', `contract_${generatedContract.contract.id}.pdf`);
          
          // Append to body, click and remove
          document.body.appendChild(link);
          link.click();
          link.remove();
          
          // Clean up the URL
          window.URL.revokeObjectURL(url);
        }
      } catch (error) {
        console.error('Error downloading PDF:', error);
        alert('Failed to download PDF. Please try again.');
      }
    };

    const currentContent = editedContent || generatedContract.contract.content;

    return (
      <div className="w-full max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">Contract Generated Successfully</CardTitle>
                <CardDescription>
                  Your {contractTypes.find(t => t.id === generatedContract.contract.contract_type)?.name} is ready
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant={generatedContract.contract.compliance_score > 80 ? 'default' : 'secondary'}>
                  {generatedContract.contract.compliance_score.toFixed(0)}% Compliance
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Progress value={generatedContract.contract.compliance_score} className="w-full" />
              
              {generatedContract.warnings?.length > 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Warnings:</strong> {generatedContract.warnings.join(', ')}
                  </AlertDescription>
                </Alert>
              )}

              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="edit">
                    <FileText className="mr-2 h-4 w-4" />
                    Edit
                  </TabsTrigger>
                  <TabsTrigger value="preview">
                    <Eye className="mr-2 h-4 w-4" />
                    Preview
                  </TabsTrigger>
                  <TabsTrigger value="clauses">
                    <FileText className="mr-2 h-4 w-4" />
                    Clauses ({generatedContract.contract.clauses.length})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="edit" className="mt-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <Textarea
                          value={editedContent}
                          onChange={(e) => handleContentChange(e.target.value)}
                          className="min-h-96 font-mono text-sm"
                          placeholder="Edit your contract content here..."
                        />
                        
                        {/* Signature Upload Section */}
                        <div className="border-t pt-4">
                          <h3 className="text-lg font-semibold mb-4">Digital Signatures</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* First Party Signature */}
                            <div className="space-y-2">
                              <Button
                                onClick={() => triggerFileUpload('first_party')}
                                disabled={uploadingSignature === 'first_party'}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                                variant="outline"
                              >
                                {uploadingSignature === 'first_party' ? (
                                  'Uploading...'
                                ) : (
                                  <>
                                    <FileText className="mr-2 h-4 w-4" />
                                    Add Signature of First Party
                                  </>
                                )}
                              </Button>
                              {firstPartySignature && (
                                <div className="mt-2 p-2 border rounded">
                                  <p className="text-sm text-green-600 mb-2">✓ First Party signature uploaded</p>
                                  <img 
                                    src={firstPartySignature} 
                                    alt="First Party Signature" 
                                    className="max-w-full h-auto max-h-20 border"
                                    style={{ maxWidth: '300px' }}
                                  />
                                </div>
                              )}
                            </div>
                            
                            {/* Second Party Signature */}
                            <div className="space-y-2">
                              <Button
                                onClick={() => triggerFileUpload('second_party')}
                                disabled={uploadingSignature === 'second_party'}
                                className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                                variant="outline"
                              >
                                {uploadingSignature === 'second_party' ? (
                                  'Uploading...'
                                ) : (
                                  <>
                                    <FileText className="mr-2 h-4 w-4" />
                                    Add Signature of Second Party
                                  </>
                                )}
                              </Button>
                              {secondPartySignature && (
                                <div className="mt-2 p-2 border rounded">
                                  <p className="text-sm text-green-600 mb-2">✓ Second Party signature uploaded</p>
                                  <img 
                                    src={secondPartySignature} 
                                    alt="Second Party Signature" 
                                    className="max-w-full h-auto max-h-20 border"
                                    style={{ maxWidth: '300px' }}
                                  />
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex justify-end">
                          <Button
                            onClick={handleConfirmEdit}
                            disabled={!hasEdits}
                            className={`${
                              hasEdits 
                                ? 'bg-green-600 hover:bg-green-700 text-white' 
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            }`}
                          >
                            Confirm
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="preview" className="mt-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="max-h-96 overflow-y-auto bg-gray-50 p-4 rounded border">
                        <div className="text-sm font-mono whitespace-pre-wrap">
                          {currentContent.split('\n').map((line, index) => {
                            // Check if line contains signature placeholders
                            if (line.includes('[First Party Signature Placeholder]') || line.includes('[First Party Signature Uploaded]')) {
                              return (
                                <div key={index} className="my-4">
                                  {firstPartySignature ? (
                                    <img 
                                      src={firstPartySignature} 
                                      alt="First Party Signature" 
                                      className="max-w-full h-auto max-h-16 mb-2"
                                      style={{ maxWidth: '300px' }}
                                    />
                                  ) : (
                                    <div className="h-16 border-b-2 border-gray-400 mb-2" style={{ width: '300px' }}>
                                      <span className="text-gray-500 text-xs">[First Party Signature Area]</span>
                                    </div>
                                  )}
                                </div>
                              );
                            }
                            if (line.includes('[Second Party Signature Placeholder]') || line.includes('[Second Party Signature Uploaded]')) {
                              return (
                                <div key={index} className="my-4">
                                  {secondPartySignature ? (
                                    <img 
                                      src={secondPartySignature} 
                                      alt="Second Party Signature" 
                                      className="max-w-full h-auto max-h-16 mb-2"
                                      style={{ maxWidth: '300px' }}
                                    />
                                  ) : (
                                    <div className="h-16 border-b-2 border-gray-400 mb-2" style={{ width: '300px' }}>
                                      <span className="text-gray-500 text-xs">[Second Party Signature Area]</span>
                                    </div>
                                  )}
                                </div>
                              );
                            }
                            return <div key={index}>{line}</div>;
                          })}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="clauses" className="mt-4">
                  <div className="space-y-3">
                    {generatedContract.contract.clauses.map((clause, index) => (
                      <Card key={index}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-semibold text-sm">{clause.title}</h4>
                              <p className="text-sm text-gray-600 mt-1">{clause.content}</p>
                            </div>
                            <Badge variant="outline" className="ml-2">
                              {clause.type}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>
              </Tabs>

              <div className="flex gap-4 mt-6">
                <Button 
                  onClick={() => {
                    setCurrentStep(1);
                    setGeneratedContract(null);
                    setContractData({
                      contract_type: '',
                      jurisdiction: 'US',
                      parties: {},
                      terms: {},
                      special_clauses: [],
                      execution_date: null
                    });
                  }}
                  variant="outline"
                  className="flex-1"
                >
                  Create New Contract
                </Button>
                <Button 
                  onClick={() => downloadPDF(currentContent)}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download PDF
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const Hero = () => (
    <MobileOptimizedHero 
      onNavigate={handleNavigation}
      useEnhancedWizard={useEnhancedWizard}
      complianceMode={complianceMode}
    />
  );

  const ContractLibrary = () => (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">Your Contract Library</CardTitle>
        <CardDescription>Previously generated contracts</CardDescription>
      </CardHeader>
      <CardContent>
        {contracts.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">No contracts generated yet. Create your first contract above!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {contracts.slice(0, 5).map((contract) => (
              <Card key={contract.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">
                        {contractTypes.find(t => t.id === contract.contract_type)?.name || contract.contract_type}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {new Date(contract.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{contract.jurisdiction}</Badge>
                      <Badge variant={contract.compliance_score > 80 ? 'default' : 'secondary'}>
                        {contract.compliance_score.toFixed(0)}%
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Responsive Header - Mobile/Tablet Navigation */}
      <ResponsiveHeader 
        onNavigate={handleNavigation}
        currentView={currentView}
        complianceMode={complianceMode}
        setShowAttorneyDashboard={setShowAttorneyDashboard}
      />
      
      {/* Hero Section - Mobile Optimized */}
      <Hero />
      
      {/* Compliance System Components */}
      <ComplianceModeIndicator 
        complianceMode={complianceMode}
        attorneySupervisionRequired={complianceStatus?.attorney_supervision_required}
      />
      
      {/* Attorney Dashboard Modal */}
      {showAttorneyDashboard && (
        <AttorneyDashboard onClose={() => setShowAttorneyDashboard(false)} />
      )}
      
      {/* Consent Manager Modal */}
      {showConsentManager && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-auto">
            <div className="p-6">
              <ConsentManager
                clientId={clientId}
                onConsentGiven={handleConsentGiven}
                onConsentDeclined={handleConsentDeclined}
              />
            </div>
          </div>
        </div>
      )}
      
      {/* Main Content Area - Mobile Responsive */}
      <div className="py-6 px-4 sm:py-8 sm:px-6 lg:py-12 lg:px-8 pb-20 lg:pb-8">
        <div className="max-w-6xl mx-auto">
          {/* Attorney Supervision Notice */}
          {complianceMode && (
            <AttorneySupervisionNotice 
              isVisible={true}
              showDetails={false}
            />
          )}
          
          {/* Debug info for development */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mb-4 p-3 bg-gray-100 rounded text-xs">
              <strong>Debug Info:</strong>
              <div>Current View: {currentView}</div>
              <div>Current Step: {currentStep}</div>
              <div>Current Review ID: {currentReviewId || 'None'}</div>
              <div>Is Generating: {isGenerating ? 'Yes' : 'No'}</div>
              <div>Generated Contract: {generatedContract ? 'Yes' : 'No'}</div>
              <div>Compliance Mode: {complianceMode ? 'Yes' : 'No'}</div>
            </div>
          )}
          
          {/* Plain English Creator */}
          {showPlainEnglishCreator && !showAnalytics && !useEnhancedWizard && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && (
            <PlainEnglishContractCreator
              contractTypes={contractTypes}
              jurisdictions={jurisdictions}
              onBack={() => handleNavigation('home')}
            />
          )}
          
          {/* Analytics Dashboard */}
          {showAnalytics && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && (
            <AnalyticsDashboard onBack={() => handleNavigation('home')} />
          )}
          
          {/* Litigation Analytics */}
          {showLitigationAnalytics && !showAnalytics && !showLegalQA && !showVoiceAgent && !useEnhancedWizard && !showPlainEnglishCreator && !showLegalResearch && !showAIAgentHub && (
            <LitigationAnalytics onBack={() => handleNavigation('home')} />
          )}
          
          {/* Enhanced Contract Wizard */}
          {useEnhancedWizard && !showAnalytics && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && !useMobileWizard && !useMobileAnalytics && (
            <ResizeObserverErrorBoundary>
              <EnhancedContractWizard
                contractTypes={contractTypes}
                jurisdictions={jurisdictions}
                onContractGenerated={(contract) => {
                  setGeneratedContract(contract);
                  setCurrentStep(4);
                  setUseEnhancedWizard(false);
                  loadContracts();
                  showMobileToast('success', 'Contract Generated', 'Your contract has been created successfully!');
                }}
                onBack={() => handleNavigation('home')}
              />
            </ResizeObserverErrorBoundary>
          )}
          
          {/* Mobile Contract Wizard */}
          {useMobileWizard && !showAnalytics && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && !useMobileAnalytics && (
            <MobileContractWizard
              contractTypes={contractTypes}
              jurisdictions={jurisdictions}
              onContractGenerated={(contract) => {
                setGeneratedContract(contract);
                setCurrentStep(4);
                setUseMobileWizard(false);
                loadContracts();
                showMobileToast('success', 'Contract Generated', 'Your mobile-optimized contract has been created!');
              }}
              onBack={() => handleNavigation('home')}
            />
          )}

          {/* Mobile Analytics Dashboard */}
          {useMobileAnalytics && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && !useMobileWizard && (
            <MobileAnalyticsDashboard onBack={() => handleNavigation('home')} />
          )}
          
          {/* Legal Question Answering */}
          {showLegalQA && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && (
            <LegalQuestionAnswering />
          )}
          
          {/* Voice Agent */}
          {showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && (
            <VoiceAgent onClose={() => handleNavigation('home')} />
          )}
          
          {/* AI Agent Hub */}
          {showAIAgentHub && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && (
            <AIAgentHub />
          )}
          
          {/* Legal Research Dashboard */}
          {showLegalResearch && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showAIAgentHub && (
            <LegalResearchDashboard />
          )}
          
          {/* Classic Mode Contract Wizard */}
          {!useEnhancedWizard && !showAnalytics && !showPlainEnglishCreator && !showLegalQA && !showVoiceAgent && !showLitigationAnalytics && !showLegalResearch && !showAIAgentHub && !useMobileWizard && !useMobileAnalytics && (
            <>
              {currentStep === 1 && <ContractTypeStep />}
              {currentStep === 2 && (
                <PartiesStep 
                  contractData={contractData} 
                  updateParties={updateParties} 
                  setCurrentStep={setCurrentStep} 
                />
              )}
              {currentStep === 3 && (
                <TermsStep 
                  contractData={contractData} 
                  contractTypes={contractTypes}
                  updateTerms={updateTerms} 
                  setContractData={setContractData}
                  generateContract={generateContract} 
                  isGenerating={isGenerating} 
                  setCurrentStep={setCurrentStep}
                />
              )}
              {currentStep === 4 && generatedContract && <ContractResult />}
              
              {/* Contract Library - Show when on step 1 */}
              {currentStep === 1 && (
                <div className="mt-8">
                  <ContractLibrary />
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Bottom Navigation - Mobile Only */}
      <BottomNavigation 
        onNavigate={handleNavigation}
        currentView={currentView}
      />

      {/* Legal Disclaimer Footer - Mobile Responsive */}
      <div className="pb-20 lg:pb-0">
        <LegalDisclaimerFooter />
      </div>

      {/* Mobile Performance Monitor */}
      {showPerformanceMonitor && (
        <MobilePerformanceDashboard 
          onClose={() => setShowPerformanceMonitor(false)} 
        />
      )}

      {/* Mobile Toast Notifications */}
      {mobileToast && (
        <MobileToastModal
          isOpen={!!mobileToast}
          onClose={() => setMobileToast(null)}
          type={mobileToast.type}
          title={mobileToast.title}
          message={mobileToast.message}
          duration={mobileToast.duration}
        />
      )}
    </div>
  );
}

export default App;