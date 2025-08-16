import React, { useState } from 'react';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { Badge } from './ui/badge';
import { 
  Menu, 
  X, 
  Sparkles, 
  MessageSquare, 
  Scale, 
  Mic, 
  Search, 
  FileText, 
  BarChart3, 
  Bot,
  Home,
  Settings,
  User,
  Shield
} from 'lucide-react';

const ResponsiveHeader = ({ 
  onNavigate, 
  currentView, 
  complianceMode,
  setShowAttorneyDashboard 
}) => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const navigationItems = [
    {
      id: 'home',
      label: 'Home',
      icon: Home,
      action: () => onNavigate('home'),
      badge: null
    },
    {
      id: 'smart-wizard',
      label: 'Smart Contract Wizard',
      icon: Sparkles,
      action: () => onNavigate('enhanced-wizard', true), // Enable mobile detection
      badge: { text: 'NEW', variant: 'secondary', className: 'bg-yellow-400 text-yellow-900' }
    },
    {
      id: 'plain-english',
      label: 'Plain English Creator',
      icon: MessageSquare,
      action: () => onNavigate('plain-english'),
      badge: { text: 'AI-POWERED', variant: 'secondary', className: 'bg-green-400 text-green-900' }
    },
    {
      id: 'legal-qa',
      label: 'Legal Q&A Assistant',
      icon: Scale,
      action: () => onNavigate('legal-qa'),
      badge: { text: 'RAG-POWERED', variant: 'secondary', className: 'bg-purple-400 text-purple-900' }
    },
    {
      id: 'voice-agent',
      label: 'AI Voice Agent',
      icon: Mic,
      action: () => onNavigate('voice-agent'),
      badge: { text: 'VOICE-POWERED', variant: 'secondary', className: 'bg-cyan-400 text-cyan-900' }
    },
    {
      id: 'legal-research',
      label: 'Legal Research',
      icon: Search,
      action: () => onNavigate('legal-research'),
      badge: { text: 'AI-POWERED', variant: 'secondary', className: 'bg-emerald-400 text-emerald-900' }
    },
    {
      id: 'classic-mode',
      label: 'Classic Mode',
      icon: FileText,
      action: () => onNavigate('classic-mode'),
      badge: null
    },
    {
      id: 'analytics',
      label: 'Analytics Dashboard',
      icon: BarChart3,
      action: () => onNavigate('analytics', true), // Enable mobile detection
      badge: { text: 'NEW', variant: 'secondary', className: 'bg-green-400 text-green-900' }
    },
    {
      id: 'litigation-analytics',
      label: 'Litigation Analytics',
      icon: Scale,
      action: () => onNavigate('litigation-analytics'),
      badge: { text: 'PREMIUM', variant: 'secondary', className: 'bg-red-400 text-red-900' }
    },
    {
      id: 'ai-agent-hub',
      label: 'AI Agent Hub',
      icon: Bot,
      action: () => onNavigate('ai-agent-hub'),
      badge: { text: 'PHASE 1.3', variant: 'secondary', className: 'bg-teal-400 text-teal-900' }
    },
    {
      id: 'attorney-dashboard',
      label: 'Attorney Dashboard',
      icon: Shield,
      action: () => setShowAttorneyDashboard(true),
      badge: { text: 'COMPLIANCE', variant: 'secondary', className: 'bg-orange-400 text-orange-900' }
    }
  ];

  const handleItemClick = (item) => {
    item.action();
    setIsDrawerOpen(false);
  };

  return (
    <>
      {/* Mobile & Tablet Header */}
      <div className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b lg:hidden">
        <div className="flex items-center justify-between p-4">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <img 
              src="https://images.unsplash.com/photo-1599840448769-f4ac7aac8d8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxsZWdhbCUyMHRlY2hub2xvZ3l8ZW58MHx8fGJsdWV8MTc1MzgzNzA1NHww&ixlib=rb-4.1.0&q=85"
              alt="LegalMate AI"
              className="w-8 h-8 rounded-lg object-cover"
            />
            <h1 className="text-lg font-bold text-gray-900">LegalMate AI</h1>
          </div>
          
          {/* Hamburger Menu */}
          <Sheet open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="p-2">
                <Menu className="h-6 w-6" />
                <span className="sr-only">Open menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[400px]">
              <SheetHeader>
                <SheetTitle className="flex items-center space-x-2 text-left">
                  <img 
                    src="https://images.unsplash.com/photo-1599840448769-f4ac7aac8d8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxsZWdhbCUyMHRlY2hub2xvZ3l8ZW58MHx8fGJsdWV8MTc1MzgzNzA1NHww&ixlib=rb-4.1.0&q=85"
                    alt="LegalMate AI"
                    className="w-6 h-6 rounded object-cover"
                  />
                  <span>LegalMate AI</span>
                </SheetTitle>
                <SheetDescription>
                  AI-Powered Legal Platform
                </SheetDescription>
              </SheetHeader>
              
              {/* Navigation Items */}
              <div className="mt-6 space-y-2">
                {navigationItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentView === item.id;
                  
                  return (
                    <Button
                      key={item.id}
                      variant={isActive ? "secondary" : "ghost"}
                      className={`w-full justify-start h-12 px-3 ${
                        isActive ? 'bg-blue-100 text-blue-900 border border-blue-200' : 'hover:bg-gray-100'
                      }`}
                      onClick={() => handleItemClick(item)}
                    >
                      <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
                      <span className="flex-1 text-left truncate">{item.label}</span>
                      {item.badge && (
                        <Badge 
                          variant={item.badge.variant}
                          className={`ml-2 text-xs flex-shrink-0 ${item.badge.className}`}
                        >
                          {item.badge.text}
                        </Badge>
                      )}
                    </Button>
                  );
                })}
              </div>
              
              {/* Compliance Status */}
              {complianceMode && (
                <div className="mt-6 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <div className="flex items-center space-x-2 text-orange-800">
                    <Shield className="h-4 w-4" />
                    <span className="text-sm font-medium">Compliance Mode Active</span>
                  </div>
                  <p className="text-xs text-orange-600 mt-1">
                    Attorney supervision enabled for legal compliance
                  </p>
                </div>
              )}
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Desktop Header - Hidden on Mobile */}
      <div className="hidden lg:block">
        {/* Desktop header content can go here if needed */}
      </div>
    </>
  );
};

const BottomNavigation = ({ onNavigate, currentView }) => {
  const bottomNavItems = [
    {
      id: 'home',
      label: 'Home',
      icon: Home,
      action: () => onNavigate('home')
    },
    {
      id: 'legal-qa',
      label: 'Chat',
      icon: MessageSquare,
      action: () => onNavigate('legal-qa', true) // Enable mobile detection
    },
    {
      id: 'search',
      label: 'Research',
      icon: Search,
      action: () => onNavigate('legal-research')
    },
    {
      id: 'ai-agent-hub',
      label: 'Agents',
      icon: Bot,
      action: () => onNavigate('ai-agent-hub')
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      action: () => onNavigate('analytics', true) // Enable mobile detection
    }
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t lg:hidden">
      <div className="flex items-center justify-around py-2 px-2">
        {bottomNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <Button
              key={item.id}
              variant="ghost"
              size="sm"
              className={`flex flex-col items-center justify-center p-2 h-14 w-full max-w-[80px] ${
                isActive 
                  ? 'text-blue-600 bg-blue-50' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
              onClick={item.action}
            >
              <Icon className={`h-5 w-5 mb-1 ${isActive ? 'text-blue-600' : ''}`} />
              <span className={`text-xs truncate ${isActive ? 'text-blue-600 font-medium' : ''}`}>
                {item.label}
              </span>
            </Button>
          );
        })}
      </div>
      {/* Safe area padding for devices with home indicators */}
      <div className="h-safe-area-inset-bottom bg-white"></div>
    </div>
  );
};

export { ResponsiveHeader, BottomNavigation };