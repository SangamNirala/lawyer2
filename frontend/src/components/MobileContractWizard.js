import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { Drawer, DrawerClose, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle, DrawerTrigger } from './ui/drawer';
import { 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  Target,
  Clock,
  User,
  Building,
  FileText,
  CheckCircle,
  Settings,
  X,
  Lightbulb,
  AlertCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const MobileContractWizard = ({ 
  contractTypes, 
  jurisdictions, 
  onContractGenerated,
  onBack 
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(20);
  const [estimatedTime, setEstimatedTime] = useState('8-12 minutes');
  
  // Form data for each step - mobile-optimized structure
  const [stepData, setStepData] = useState({
    step1: { 
      contract_type: '', 
      industry: '', 
      jurisdiction: 'US',
      urgency: 'normal' // Add urgency for mobile workflow
    },
    step2: { 
      party1_name: '', 
      party1_email: '', 
      party1_address: '',
      party1_phone: '', // Mobile-specific field
      party2_name: '', 
      party2_email: '', 
      party2_address: '',
      party2_phone: '' // Mobile-specific field
    },
    step3: { 
      payment_amount: '', // More specific than payment_terms
      payment_schedule: '', 
      project_duration: '', 
      deliverables: '', 
      liability_cap: ''
    },
    step4: { 
      confidentiality: false, 
      non_compete: false, 
      special_terms: '', 
      execution_date: '',
      include_signatures: true // Mobile-optimized feature
    },
    step5: { 
      review_complete: false, 
      legal_review: false,
      notification_email: '' // Mobile workflow enhancement
    }
  });

  // Mobile-specific state
  const [showHelp, setShowHelp] = useState(false);
  const [currentFieldHelp, setCurrentFieldHelp] = useState('');
  const [touchFeedback, setTouchFeedback] = useState(null);
  
  // Swipe gesture state
  const [swipeStartX, setSwipeStartX] = useState(0);
  const [swipeStartY, setSwipeStartY] = useState(0);
  const [isSwipeEnabled, setIsSwipeEnabled] = useState(true);

  useEffect(() => {
    // Update progress based on current step
    const progressMap = { 1: 20, 2: 40, 3: 60, 4: 80, 5: 100 };
    setProgress(progressMap[currentStep] || 0);
    
    // Update estimated time
    const timeMap = { 
      1: '6-8 minutes', 
      2: '4-6 minutes', 
      3: '3-5 minutes', 
      4: '2-3 minutes', 
      5: '1-2 minutes' 
    };
    setEstimatedTime(timeMap[currentStep] || '1-2 minutes');
  }, [currentStep]);

  const updateStepData = useCallback((step, field, value) => {
    setStepData(prev => ({
      ...prev,
      [step]: {
        ...prev[step],
        [field]: value
      }
    }));
  }, []);

  // Swipe gesture handlers - Updated to prevent interference with input fields
  const handleTouchStart = useCallback((e) => {
    if (!isSwipeEnabled) return;
    
    // Ignore touch events on input fields, textareas, and select elements
    const target = e.target;
    if (target && (
      target.tagName === 'INPUT' || 
      target.tagName === 'TEXTAREA' || 
      target.tagName === 'SELECT' ||
      target.closest('input') ||
      target.closest('textarea') ||
      target.closest('select') ||
      target.closest('[role="combobox"]') ||
      target.closest('.select-trigger')
    )) {
      return;
    }
    
    setSwipeStartX(e.touches[0].clientX);
    setSwipeStartY(e.touches[0].clientY);
  }, [isSwipeEnabled]);

  const handleTouchEnd = useCallback((e) => {
    if (!isSwipeEnabled) return;
    
    // Ignore touch events on input fields, textareas, and select elements
    const target = e.target;
    if (target && (
      target.tagName === 'INPUT' || 
      target.tagName === 'TEXTAREA' || 
      target.tagName === 'SELECT' ||
      target.closest('input') ||
      target.closest('textarea') ||
      target.closest('select') ||
      target.closest('[role="combobox"]') ||
      target.closest('.select-trigger')
    )) {
      return;
    }
    
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const deltaX = endX - swipeStartX;
    const deltaY = endY - swipeStartY;
    
    // Check if horizontal swipe is more dominant than vertical
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
      if (deltaX > 0 && currentStep > 1) {
        // Swipe right - previous step
        setCurrentStep(prev => prev - 1);
        setTouchFeedback({ type: 'success', message: 'Previous step' });
        setTimeout(() => setTouchFeedback(null), 1500);
      } else if (deltaX < 0 && currentStep < 5) {
        // Swipe left - next step (only if current step is valid)
        if (isStepValid(currentStep)) {
          setCurrentStep(prev => prev + 1);
          setTouchFeedback({ type: 'success', message: 'Next step' });
          setTimeout(() => setTouchFeedback(null), 1500);
        } else {
          setTouchFeedback({ type: 'error', message: 'Please complete required fields' });
          setTimeout(() => setTouchFeedback(null), 2500);
        }
      }
    }
  }, [isSwipeEnabled, swipeStartX, swipeStartY, currentStep]);

  // Simple validation for swipe navigation
  const isStepValid = (step) => {
    switch (step) {
      case 1:
        return stepData.step1.contract_type && stepData.step1.jurisdiction;
      case 2:
        return stepData.step2.party1_name && stepData.step2.party2_name;
      case 3:
        return stepData.step3.payment_amount;
      case 4:
        return true; // Optional step
      default:
        return true;
    }
  };

  const nextStep = () => {
    if (currentStep < 5) {
      setCurrentStep(currentStep + 1);
    } else {
      generateContract();
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const generateContract = async () => {
    setIsLoading(true);
    try {
      const contractData = {
        contract_type: stepData.step1.contract_type,
        jurisdiction: stepData.step1.jurisdiction,
        parties: {
          party1_name: stepData.step2.party1_name,
          party1_email: stepData.step2.party1_email,
          party1_address: stepData.step2.party1_address,
          party1_phone: stepData.step2.party1_phone,
          party2_name: stepData.step2.party2_name,
          party2_email: stepData.step2.party2_email,
          party2_address: stepData.step2.party2_address,
          party2_phone: stepData.step2.party2_phone,
        },
        terms: {
          payment_amount: stepData.step3.payment_amount,
          payment_schedule: stepData.step3.payment_schedule,
          project_duration: stepData.step3.project_duration,
          deliverables: stepData.step3.deliverables,
          liability_cap: stepData.step3.liability_cap,
        },
        special_clauses: stepData.step4.special_terms ? [stepData.step4.special_terms] : [],
        execution_date: stepData.step4.execution_date,
        mobile_optimized: true // Flag for mobile-generated contracts
      };

      const response = await axios.post(`${API}/generate-contract`, contractData);
      onContractGenerated(response.data);
    } catch (error) {
      console.error('Error generating contract:', error);
      setTouchFeedback({ type: 'error', message: 'Failed to generate contract. Please try again.' });
      setTimeout(() => setTouchFeedback(null), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  // Mobile Header with step indicator
  const MobileHeader = () => (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 sticky top-0 z-50">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={currentStep === 1 ? onBack : prevStep}
            className="text-white hover:bg-white/20 p-2 min-h-[44px] min-w-[44px]"
          >
            {currentStep === 1 ? <X className="h-5 w-5" /> : <ArrowLeft className="h-5 w-5" />}
          </Button>
          <div>
            <h1 className="text-lg font-bold">Contract Wizard</h1>
            <p className="text-sm opacity-90">Step {currentStep} of 5</p>
          </div>
        </div>
        
        <Sheet open={showHelp} onOpenChange={setShowHelp}>
          <SheetTrigger asChild>
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-white hover:bg-white/20 p-2 min-h-[44px] min-w-[44px]"
            >
              <Lightbulb className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="bottom" className="h-[60vh]">
            <SheetHeader>
              <SheetTitle>Step {currentStep} Help</SheetTitle>
              <SheetDescription>
                {getStepHelp()}
              </SheetDescription>
            </SheetHeader>
            <div className="mt-4">
              <div className="space-y-3">
                {getStepTips().map((tip, index) => (
                  <div key={index} className="flex items-start space-x-2 p-3 bg-blue-50 rounded-lg">
                    <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{tip}</span>
                  </div>
                ))}
              </div>
            </div>
          </SheetContent>
        </Sheet>
      </div>
      
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs">
          <span>Progress</span>
          <span>{estimatedTime} remaining</span>
        </div>
        <Progress value={progress} className="h-2 bg-white/20" />
      </div>
    </div>
  );

  // Step 1: Contract Type & Basic Info - Mobile Optimized
  const Step1ContractType = () => (
    <div className="space-y-6 p-4">
      <div className="text-center mb-6">
        <Target className="h-12 w-12 mx-auto mb-3 text-blue-600" />
        <h2 className="text-xl font-bold mb-2">Contract Details</h2>
        <p className="text-gray-600 text-sm">Tell us what kind of contract you need</p>
      </div>

      <div className="space-y-6">
        <div>
          <Label htmlFor="contract_type" className="text-base font-medium mb-3 block">
            Contract Type *
          </Label>
          <Select 
            value={stepData.step1.contract_type} 
            onValueChange={(value) => updateStepData('step1', 'contract_type', value)}
          >
            <SelectTrigger className="h-12 text-base">
              <SelectValue placeholder="Choose your contract type" />
            </SelectTrigger>
            <SelectContent>
              {contractTypes.map((type) => (
                <SelectItem key={type.id} value={type.id} className="p-4">
                  <div className="flex flex-col items-start">
                    <span className="font-medium">{type.name}</span>
                    <span className="text-xs text-gray-500">{type.description}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="industry" className="text-base font-medium mb-3 block">
            Industry (Optional)
          </Label>
          <Select 
            value={stepData.step1.industry} 
            onValueChange={(value) => updateStepData('step1', 'industry', value)}
          >
            <SelectTrigger className="h-12 text-base">
              <SelectValue placeholder="Select your industry" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="technology">Technology & Software</SelectItem>
              <SelectItem value="healthcare">Healthcare & Medical</SelectItem>
              <SelectItem value="finance">Finance & Banking</SelectItem>
              <SelectItem value="marketing">Marketing & Advertising</SelectItem>
              <SelectItem value="consulting">Consulting & Professional</SelectItem>
              <SelectItem value="real_estate">Real Estate & Property</SelectItem>
              <SelectItem value="manufacturing">Manufacturing & Production</SelectItem>
              <SelectItem value="creative">Creative & Design</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="jurisdiction" className="text-base font-medium mb-3 block">
            Jurisdiction *
          </Label>
          <Select 
            value={stepData.step1.jurisdiction} 
            onValueChange={(value) => updateStepData('step1', 'jurisdiction', value)}
          >
            <SelectTrigger className="h-12 text-base">
              <SelectValue placeholder="Select jurisdiction" />
            </SelectTrigger>
            <SelectContent>
              {jurisdictions.filter(j => j.supported).map((jurisdiction) => (
                <SelectItem key={jurisdiction.code} value={jurisdiction.code} className="p-4">
                  <div className="flex flex-col items-start">
                    <span className="font-medium">{jurisdiction.name}</span>
                    <span className="text-xs text-gray-500">Legal framework: {jurisdiction.legal_system}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="urgency" className="text-base font-medium mb-3 block">
            Timeline Urgency
          </Label>
          <Select 
            value={stepData.step1.urgency} 
            onValueChange={(value) => updateStepData('step1', 'urgency', value)}
          >
            <SelectTrigger className="h-12 text-base">
              <SelectValue placeholder="How urgent is this?" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low - No rush (1-2 weeks)</SelectItem>
              <SelectItem value="normal">Normal - Soon (3-7 days)</SelectItem>
              <SelectItem value="high">High - ASAP (1-3 days)</SelectItem>
              <SelectItem value="urgent">Urgent - Today</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  // Step 2: Party Information - Mobile Optimized Vertical Layout
  const Step2PartyInfo = () => (
    <div className="space-y-6 p-4">
      <div className="text-center mb-6">
        <User className="h-12 w-12 mx-auto mb-3 text-blue-600" />
        <h2 className="text-xl font-bold mb-2">Party Information</h2>
        <p className="text-gray-600 text-sm">Who are the parties in this contract?</p>
      </div>

      {/* Party 1 - Your Information */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center">
            <User className="h-4 w-4 mr-2" />
            Your Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="party1_name" className="text-sm font-medium mb-2 block">
              Name/Company Name *
            </Label>
            <Input
              key="party1_name_input"
              id="party1_name"
              value={stepData.step2.party1_name}
              onChange={(e) => updateStepData('step2', 'party1_name', e.target.value)}
              placeholder="Your name or company name"
              className="h-12 text-base"
              autoComplete="name"
            />
          </div>
          
          <div>
            <Label htmlFor="party1_email" className="text-sm font-medium mb-2 block">
              Email Address
            </Label>
            <Input
              key="party1_email_input"
              id="party1_email"
              type="email"
              value={stepData.step2.party1_email}
              onChange={(e) => updateStepData('step2', 'party1_email', e.target.value)}
              placeholder="your@email.com"
              className="h-12 text-base"
              autoComplete="email"
            />
          </div>

          <div>
            <Label htmlFor="party1_phone" className="text-sm font-medium mb-2 block">
              Phone Number
            </Label>
            <Input
              id="party1_phone"
              type="tel"
              value={stepData.step2.party1_phone}
              onChange={(e) => updateStepData('step2', 'party1_phone', e.target.value)}
              placeholder="+1 (555) 123-4567"
              className="h-12 text-base"
            />
          </div>

          <div>
            <Label htmlFor="party1_address" className="text-sm font-medium mb-2 block">
              Address
            </Label>
            <Textarea
              id="party1_address"
              value={stepData.step2.party1_address}
              onChange={(e) => updateStepData('step2', 'party1_address', e.target.value)}
              placeholder="Full address including city, state, and zip"
              rows={3}
              className="text-base resize-none"
            />
          </div>
        </CardContent>
      </Card>

      {/* Party 2 - Other Party Information */}
      <Card className="border-l-4 border-l-green-500">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center">
            <Building className="h-4 w-4 mr-2" />
            Other Party Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="party2_name" className="text-sm font-medium mb-2 block">
              Name/Company Name *
            </Label>
            <Input
              id="party2_name"
              value={stepData.step2.party2_name}
              onChange={(e) => updateStepData('step2', 'party2_name', e.target.value)}
              placeholder="Other party name or company"
              className="h-12 text-base"
            />
          </div>
          
          <div>
            <Label htmlFor="party2_email" className="text-sm font-medium mb-2 block">
              Email Address
            </Label>
            <Input
              id="party2_email"
              type="email"
              value={stepData.step2.party2_email}
              onChange={(e) => updateStepData('step2', 'party2_email', e.target.value)}
              placeholder="other@email.com"
              className="h-12 text-base"
            />
          </div>

          <div>
            <Label htmlFor="party2_phone" className="text-sm font-medium mb-2 block">
              Phone Number
            </Label>
            <Input
              id="party2_phone"
              type="tel"
              value={stepData.step2.party2_phone}
              onChange={(e) => updateStepData('step2', 'party2_phone', e.target.value)}
              placeholder="+1 (555) 987-6543"
              className="h-12 text-base"
            />
          </div>

          <div>
            <Label htmlFor="party2_address" className="text-sm font-medium mb-2 block">
              Address
            </Label>
            <Textarea
              id="party2_address"
              value={stepData.step2.party2_address}
              onChange={(e) => updateStepData('step2', 'party2_address', e.target.value)}
              placeholder="Full address including city, state, and zip"
              rows={3}
              className="text-base resize-none"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // Step 3: Terms & Conditions - Mobile Optimized
  const Step3Terms = () => (
    <div className="space-y-6 p-4">
      <div className="text-center mb-6">
        <FileText className="h-12 w-12 mx-auto mb-3 text-blue-600" />
        <h2 className="text-xl font-bold mb-2">Terms & Conditions</h2>
        <p className="text-gray-600 text-sm">Define the key terms of your agreement</p>
      </div>

      <div className="space-y-6">
        <div>
          <Label htmlFor="payment_amount" className="text-base font-medium mb-3 block">
            Payment Amount *
          </Label>
          <Input
            id="payment_amount"
            value={stepData.step3.payment_amount}
            onChange={(e) => updateStepData('step3', 'payment_amount', e.target.value)}
            placeholder="e.g., $5,000, €3,500, £2,800"
            className="h-12 text-base"
          />
        </div>

        <div>
          <Label htmlFor="payment_schedule" className="text-base font-medium mb-3 block">
            Payment Schedule *
          </Label>
          <Select 
            value={stepData.step3.payment_schedule} 
            onValueChange={(value) => updateStepData('step3', 'payment_schedule', value)}
          >
            <SelectTrigger className="h-12 text-base">
              <SelectValue placeholder="How will payment be made?" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="full_upfront">Full payment upfront</SelectItem>
              <SelectItem value="50_50">50% upfront, 50% on completion</SelectItem>
              <SelectItem value="30_70">30% upfront, 70% on completion</SelectItem>
              <SelectItem value="milestone">Milestone-based payments</SelectItem>
              <SelectItem value="monthly">Monthly payments</SelectItem>
              <SelectItem value="net_30">Net 30 days after invoice</SelectItem>
              <SelectItem value="net_15">Net 15 days after invoice</SelectItem>
              <SelectItem value="custom">Custom schedule</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="project_duration" className="text-base font-medium mb-3 block">
            Project Duration
          </Label>
          <Input
            id="project_duration"
            value={stepData.step3.project_duration}
            onChange={(e) => updateStepData('step3', 'project_duration', e.target.value)}
            placeholder="e.g., 3 months, 6 weeks, 12 days"
            className="h-12 text-base"
          />
        </div>

        <div>
          <Label htmlFor="deliverables" className="text-base font-medium mb-3 block">
            Deliverables & Scope
          </Label>
          <Textarea
            id="deliverables"
            value={stepData.step3.deliverables}
            onChange={(e) => updateStepData('step3', 'deliverables', e.target.value)}
            placeholder="Describe what will be delivered, services provided, or work completed..."
            rows={4}
            className="text-base resize-none"
          />
        </div>

        <div>
          <Label htmlFor="liability_cap" className="text-base font-medium mb-3 block">
            Liability Cap (Optional)
          </Label>
          <Select 
            value={stepData.step3.liability_cap} 
            onValueChange={(value) => updateStepData('step3', 'liability_cap', value)}
          >
            <SelectTrigger className="h-12 text-base">
              <SelectValue placeholder="Choose liability limit" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="project_value">Project value amount</SelectItem>
              <SelectItem value="500">$500</SelectItem>
              <SelectItem value="1000">$1,000</SelectItem>
              <SelectItem value="5000">$5,000</SelectItem>
              <SelectItem value="10000">$10,000</SelectItem>
              <SelectItem value="unlimited">Unlimited</SelectItem>
              <SelectItem value="custom">Custom amount</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  // Step 4: Special Clauses - Mobile Optimized
  const Step4SpecialClauses = () => (
    <div className="space-y-6 p-4">
      <div className="text-center mb-6">
        <Sparkles className="h-12 w-12 mx-auto mb-3 text-blue-600" />
        <h2 className="text-xl font-bold mb-2">Special Clauses</h2>
        <p className="text-gray-600 text-sm">Add protection and special requirements</p>
      </div>

      <div className="space-y-6">
        {/* Toggle Switches - Mobile Optimized */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Protection Clauses</CardTitle>
            <CardDescription className="text-sm">Add common legal protections</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <Label htmlFor="confidentiality" className="text-sm font-medium">
                  Confidentiality Agreement
                </Label>
                <p className="text-xs text-gray-600 mt-1">
                  Protect sensitive information and trade secrets
                </p>
              </div>
              <Switch
                id="confidentiality"
                checked={stepData.step4.confidentiality}
                onCheckedChange={(checked) => updateStepData('step4', 'confidentiality', checked)}
                className="ml-3"
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <Label htmlFor="non_compete" className="text-sm font-medium">
                  Non-Compete Clause
                </Label>
                <p className="text-xs text-gray-600 mt-1">
                  Prevent competition during contract period
                </p>
              </div>
              <Switch
                id="non_compete"
                checked={stepData.step4.non_compete}
                onCheckedChange={(checked) => updateStepData('step4', 'non_compete', checked)}
                className="ml-3"
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <Label htmlFor="include_signatures" className="text-sm font-medium">
                  Digital Signature Fields
                </Label>
                <p className="text-xs text-gray-600 mt-1">
                  Include signature areas for both parties
                </p>
              </div>
              <Switch
                id="include_signatures"
                checked={stepData.step4.include_signatures}
                onCheckedChange={(checked) => updateStepData('step4', 'include_signatures', checked)}
                className="ml-3"
              />
            </div>
          </CardContent>
        </Card>

        <div>
          <Label htmlFor="execution_date" className="text-base font-medium mb-3 block">
            Contract Start Date
          </Label>
          <Input
            id="execution_date"
            type="date"
            value={stepData.step4.execution_date}
            onChange={(e) => updateStepData('step4', 'execution_date', e.target.value)}
            className="h-12 text-base"
          />
        </div>

        <div>
          <Label htmlFor="special_terms" className="text-base font-medium mb-3 block">
            Additional Terms (Optional)
          </Label>
          <Textarea
            id="special_terms"
            value={stepData.step4.special_terms}
            onChange={(e) => updateStepData('step4', 'special_terms', e.target.value)}
            placeholder="Any additional terms, conditions, or special requirements..."
            rows={4}
            className="text-base resize-none"
          />
        </div>
      </div>
    </div>
  );

  // Step 5: Review & Generate - Mobile Optimized
  const Step5Review = () => (
    <div className="space-y-6 p-4">
      <div className="text-center mb-6">
        <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-600" />
        <h2 className="text-xl font-bold mb-2">Review & Generate</h2>
        <p className="text-gray-600 text-sm">Review your contract details before generating</p>
      </div>

      {/* Contract Summary - Mobile Optimized */}
      <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-base text-blue-800">Contract Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b border-blue-200 last:border-b-0">
            <span className="text-sm font-medium text-gray-700">Type:</span>
            <span className="text-sm text-blue-800">
              {contractTypes.find(t => t.id === stepData.step1.contract_type)?.name}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-blue-200 last:border-b-0">
            <span className="text-sm font-medium text-gray-700">Jurisdiction:</span>
            <span className="text-sm text-blue-800">{stepData.step1.jurisdiction}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-blue-200 last:border-b-0">
            <span className="text-sm font-medium text-gray-700">Parties:</span>
            <span className="text-sm text-blue-800 text-right">
              {stepData.step2.party1_name} ↔ {stepData.step2.party2_name}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-blue-200 last:border-b-0">
            <span className="text-sm font-medium text-gray-700">Payment:</span>
            <span className="text-sm text-blue-800">{stepData.step3.payment_amount}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-sm font-medium text-gray-700">Schedule:</span>
            <span className="text-sm text-blue-800">{stepData.step3.payment_schedule}</span>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Delivery Options</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="notification_email" className="text-sm font-medium mb-2 block">
              Email for Contract Delivery (Optional)
            </Label>
            <Input
              id="notification_email"
              type="email"
              value={stepData.step5.notification_email}
              onChange={(e) => updateStepData('step5', 'notification_email', e.target.value)}
              placeholder="Send completed contract to this email"
              className="h-12 text-base"
            />
          </div>
        </CardContent>
      </Card>

      {/* Final Confirmations */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
            <Switch
              id="review_complete"
              checked={stepData.step5.review_complete}
              onCheckedChange={(checked) => updateStepData('step5', 'review_complete', checked)}
            />
            <div className="flex-1">
              <Label htmlFor="review_complete" className="text-sm font-medium">
                I have reviewed all details and confirm they are correct
              </Label>
              <p className="text-xs text-gray-600 mt-1">
                Please double-check all information before generating
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
            <Switch
              id="legal_review"
              checked={stepData.step5.legal_review}
              onCheckedChange={(checked) => updateStepData('step5', 'legal_review', checked)}
            />
            <div className="flex-1">
              <Label htmlFor="legal_review" className="text-sm font-medium">
                This contract will be reviewed by legal counsel
              </Label>
              <p className="text-xs text-gray-600 mt-1">
                Recommended for high-value or complex agreements
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {!stepData.step5.review_complete && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-amber-800">
              Please confirm you have reviewed all contract details before generating the final document.
            </p>
          </div>
        </div>
      )}
    </div>
  );

  // Helper functions for mobile help system
  const getStepHelp = () => {
    const helpTexts = {
      1: "Choose the type of contract that best matches your needs. This determines the legal framework and required clauses.",
      2: "Provide accurate contact information for both parties. This ensures proper legal identification and communication.",
      3: "Define clear payment terms and project scope. Be specific about deliverables to avoid disputes later.",
      4: "Consider adding protection clauses based on your business needs. These help safeguard your interests.",
      5: "Review all information carefully. Once generated, the contract should be ready for legal review and signing."
    };
    return helpTexts[currentStep] || "";
  };

  const getStepTips = () => {
    const tipsByStep = {
      1: [
        "Choose the contract type that most closely matches your situation",
        "Industry selection helps customize legal language",
        "Jurisdiction affects which laws apply to your contract"
      ],
      2: [
        "Include full legal names for individuals or companies",
        "Provide complete addresses for proper legal notice",
        "Phone numbers help with quick communication"
      ],
      3: [
        "Be specific about payment amounts and currency",
        "Clear deliverables prevent scope creep",
        "Consider liability caps for risk management"
      ],
      4: [
        "Confidentiality clauses protect sensitive information",
        "Non-compete clauses may not be enforceable in all jurisdictions",
        "Set realistic start dates for the contract"
      ],
      5: [
        "Review all details carefully before generating",
        "Consider having contracts reviewed by legal counsel",
        "Keep copies of all generated contracts for your records"
      ]
    };
    return tipsByStep[currentStep] || [];
  };

  // Validation functions - mobile optimized
  const isCurrentStepValid = () => {
    switch (currentStep) {
      case 1: 
        return stepData.step1.contract_type && stepData.step1.jurisdiction;
      case 2: 
        return stepData.step2.party1_name && stepData.step2.party2_name;
      case 3: 
        return stepData.step3.payment_amount && stepData.step3.payment_schedule;
      case 4: 
        return true; // All optional
      case 5: 
        return stepData.step5.review_complete;
      default: 
        return false;
    }
  };

  // Touch feedback component
  const TouchFeedback = () => {
    if (!touchFeedback) return null;
    
    return (
      <div className={`fixed top-4 left-4 right-4 z-50 p-3 rounded-lg shadow-lg ${
        touchFeedback.type === 'error' ? 'bg-red-500' : 'bg-green-500'
      } text-white text-sm`}>
        {touchFeedback.message}
      </div>
    );
  };

  // Mobile Navigation Footer
  const MobileNavigation = () => (
    <div className="sticky bottom-0 bg-white border-t p-4 safe-area-inset-bottom">
      <div className="flex space-x-3">
        {currentStep > 1 && (
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={isLoading}
            className="flex-1 h-12 text-base"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>
        )}
        
        <Button
          onClick={nextStep}
          disabled={isLoading || !isCurrentStepValid()}
          className={`h-12 text-base font-semibold ${currentStep === 1 ? 'flex-1' : 'flex-1'} 
            ${isCurrentStepValid() 
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700' 
              : 'bg-gray-300'
            } text-white`}
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
              Generating...
            </>
          ) : currentStep === 5 ? (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Contract
            </>
          ) : (
            <>
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </>
          )}
        </Button>
      </div>
      
      {!isCurrentStepValid() && (
        <p className="text-xs text-gray-500 mt-2 text-center">
          Please complete required fields to continue
        </p>
      )}
    </div>
  );

  return (
    <div 
      className="min-h-screen bg-gray-50 flex flex-col"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <TouchFeedback />
      <MobileHeader />
      
      <div className="flex-1 overflow-y-auto">
        <div className="px-2 pb-2 text-center text-xs text-gray-500">
          💡 Tip: Swipe left/right to navigate between steps
        </div>
        {currentStep === 1 && <Step1ContractType />}
        {currentStep === 2 && <Step2PartyInfo />}
        {currentStep === 3 && <Step3Terms />}
        {currentStep === 4 && <Step4SpecialClauses />}
        {currentStep === 5 && <Step5Review />}
      </div>
      
      <MobileNavigation />
    </div>
  );
};

export default MobileContractWizard;