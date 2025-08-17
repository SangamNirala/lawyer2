import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { OptimizedImage } from './MobilePerformanceOptimizer';
import { 
  Shield, 
  Zap, 
  Users, 
  Sparkles, 
  Clock,
  Wand2,
  MessageSquare,
  Scale,
  Mic,
  Search,
  FileText,
  BarChart3,
  Bot
} from 'lucide-react';

const MobileOptimizedHero = ({ 
  onNavigate, 
  useEnhancedWizard, 
  complianceMode,
  setShowAttorneyDashboard 
}) => {
  // Primary action buttons (most important features)
  const primaryActions = [
    {
      id: 'smart-wizard',
      label: 'Smart Contract Wizard',
      icon: Sparkles,
      gradient: 'from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700',
      badge: { text: 'NEW', className: 'bg-yellow-400 text-yellow-900' },
      action: () => onNavigate('enhanced-wizard')
    },
    {
      id: 'plain-english',
      label: 'Plain English Creator',
      icon: MessageSquare,
      gradient: 'from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700',
      badge: { text: 'AI-POWERED', className: 'bg-green-400 text-green-900' },
      action: () => onNavigate('plain-english')
    }
  ];

  // Secondary action buttons
  const secondaryActions = [
    {
      id: 'legal-qa',
      label: 'Legal Q&A',
      icon: Scale,
      gradient: 'from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700',
      badge: { text: 'RAG-POWERED', className: 'bg-purple-400 text-purple-900' },
      action: () => onNavigate('legal-qa')
    },
    {
      id: 'voice-agent',
      label: 'AI Voice Agent',
      icon: Mic,
      gradient: 'from-indigo-600 to-cyan-600 hover:from-indigo-700 hover:to-cyan-700',
      badge: { text: 'VOICE-POWERED', className: 'bg-cyan-400 text-cyan-900' },
      action: () => onNavigate('voice-agent')
    },
    {
      id: 'ai-agent-hub',
      label: 'AI Agent Hub',
      icon: Bot,
      gradient: 'from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700',
      badge: { text: 'PHASE 1.3', className: 'bg-teal-400 text-teal-900' },
      action: () => onNavigate('ai-agent-hub')
    },
    {
      id: 'litigation-analytics',
      label: 'Litigation Analytics',
      icon: Scale,
      gradient: 'from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700',
      badge: { text: 'PREMIUM', className: 'bg-red-400 text-red-900' },
      action: () => onNavigate('litigation-analytics')
    },
    {
      id: 'attorney-dashboard',
      label: 'Attorney Dashboard',
      icon: Shield,
      gradient: 'from-orange-600 to-yellow-600 hover:from-orange-700 hover:to-yellow-700',
      badge: { text: 'COMPLIANCE', className: 'bg-orange-400 text-orange-900' },
      action: () => setShowAttorneyDashboard && setShowAttorneyDashboard(true)
    }
  ];

  // Tertiary actions (classic features)
  const tertiaryActions = [
    {
      id: 'legal-research',
      label: 'Legal Research',
      icon: Search,
      variant: 'outline',
      action: () => onNavigate('legal-research')
    },
    {
      id: 'classic-mode',
      label: 'Classic Mode',
      icon: FileText,
      variant: 'outline',
      action: () => onNavigate('classic-mode')
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      variant: 'outline',
      action: () => onNavigate('analytics')
    }
  ];

  const features = [
    {
      icon: Shield,
      text: 'Legally Compliant',
      color: 'text-green-400'
    },
    {
      icon: Zap,
      text: 'AI-Powered',
      color: 'text-yellow-400'
    },
    {
      icon: Users,
      text: 'Multi-Jurisdiction',
      color: 'text-blue-400'
    },
    {
      icon: Sparkles,
      text: 'Smart Suggestions',
      color: 'text-purple-400'
    },
    {
      icon: Clock,
      text: 'Quick Setup',
      color: 'text-orange-400'
    }
  ];

  return (
    <div className="relative bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="absolute inset-0 bg-black/20"></div>
      
      {/* Mobile-First Hero Content */}
      <div className="relative px-4 py-8 sm:px-6 lg:py-16 lg:px-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Logo and Title - Mobile Optimized */}
          <div className="text-center mb-8 lg:mb-12">
            <div className="mb-4 lg:mb-6">
              <OptimizedImage 
                src="https://images.unsplash.com/photo-1599840448769-f4ac7aac8d8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxsZWdhbCUyMHRlY2hub2xvZ3l8ZW58MHx8fGJsdWV8MTc1MzgzNzA1NHww&ixlib=rb-4.1.0&q=85"
                alt="LegalMate AI"
                className="w-20 h-12 sm:w-24 sm:h-16 lg:w-32 lg:h-20 mx-auto rounded-lg shadow-2xl object-cover"
                lazy={true}
              />
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-3 lg:mb-4">
              LegalMate AI
            </h1>
            <p className="text-base sm:text-lg lg:text-xl text-blue-100 mb-6 lg:mb-8 max-w-3xl mx-auto px-2">
              Generate professional, jurisdiction-specific legal contracts in minutes using advanced AI. 
              Perfect for freelancers, agencies, and small businesses.
            </p>
          </div>

          {/* Primary Actions - Mobile Stack, Desktop Grid */}
          <div className="mb-6 lg:mb-8">
            <div className="space-y-3 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-4 lg:flex lg:justify-center lg:space-x-4 max-w-4xl mx-auto">
              {primaryActions.map((action) => {
                const Icon = action.icon;
                return (
                  <Button
                    key={action.id}
                    onClick={action.action}
                    className={`w-full sm:w-auto bg-gradient-to-r ${action.gradient} text-white px-6 py-4 sm:px-8 text-base sm:text-lg font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 min-h-[56px]`}
                  >
                    <Icon className="h-5 w-5 mr-2 flex-shrink-0" />
                    <span className="truncate">{action.label}</span>
                    {action.badge && (
                      <Badge variant="secondary" className={`ml-2 text-xs ${action.badge.className} hidden sm:inline-flex`}>
                        {action.badge.text}
                      </Badge>
                    )}
                  </Button>
                );
              })}
            </div>
          </div>

          {/* Secondary Actions - Mobile Responsive */}
          <div className="mb-6 lg:mb-8">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-5xl mx-auto">
              {secondaryActions.map((action) => {
                const Icon = action.icon;
                return (
                  <Button
                    key={action.id}
                    onClick={action.action}
                    className={`bg-gradient-to-r ${action.gradient} text-white px-4 py-3 sm:px-6 sm:py-4 text-sm sm:text-base font-semibold rounded-lg transition-all duration-300 transform hover:scale-105 min-h-[52px]`}
                  >
                    <Icon className="h-4 w-4 sm:h-5 sm:w-5 mr-2 flex-shrink-0" />
                    <span className="truncate">{action.label}</span>
                    {action.badge && (
                      <Badge variant="secondary" className={`ml-2 text-xs ${action.badge.className} hidden lg:inline-flex`}>
                        {action.badge.text}
                      </Badge>
                    )}
                  </Button>
                );
              })}
            </div>
          </div>

          {/* Tertiary Actions - Compact Mobile Layout */}
          <div className="mb-8 lg:mb-12">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3 max-w-3xl mx-auto">
              {tertiaryActions.map((action) => {
                const Icon = action.icon;
                return (
                  <Button
                    key={action.id}
                    onClick={action.action}
                    variant="outline"
                    className="border-white/30 text-white hover:bg-white/10 px-3 py-2 sm:px-4 sm:py-3 text-xs sm:text-sm font-medium rounded-lg min-h-[44px]"
                  >
                    <Icon className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 flex-shrink-0" />
                    <span className="truncate">{action.label}</span>
                  </Button>
                );
              })}
            </div>
          </div>
          
          {/* Feature Highlights - Mobile Responsive */}
          <div className="flex flex-wrap justify-center gap-3 sm:gap-4 text-xs sm:text-sm">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="flex items-center space-x-1 sm:space-x-2 px-2">
                  <Icon className={`h-3 w-3 sm:h-4 sm:w-4 lg:h-5 lg:w-5 ${feature.color} flex-shrink-0`} />
                  <span className="whitespace-nowrap">{feature.text}</span>
                </div>
              );
            })}
          </div>
          
          {/* Enhanced Wizard Features - Mobile Optimized */}
          {useEnhancedWizard && (
            <div className="mt-6 lg:mt-8 bg-white/10 backdrop-blur-sm rounded-lg p-4 sm:p-6 max-w-3xl mx-auto">
              <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4 text-center">Enhanced Features</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 text-xs sm:text-sm">
                <div className="text-center">
                  <Wand2 className="h-6 w-6 sm:h-8 sm:w-8 mx-auto mb-2 text-purple-300" />
                  <div className="font-medium">Smart Auto-Fill</div>
                  <div className="text-blue-200 text-xs">Profile-based suggestions</div>
                </div>
                <div className="text-center">
                  <Clock className="h-6 w-6 sm:h-8 sm:w-8 mx-auto mb-2 text-orange-300" />
                  <div className="font-medium">Time Estimate</div>
                  <div className="text-blue-200 text-xs">Know exactly how long it takes</div>
                </div>
                <div className="text-center">
                  <Sparkles className="h-6 w-6 sm:h-8 sm:w-8 mx-auto mb-2 text-yellow-300" />
                  <div className="font-medium">Industry Specific</div>
                  <div className="text-blue-200 text-xs">Tailored recommendations</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MobileOptimizedHero;