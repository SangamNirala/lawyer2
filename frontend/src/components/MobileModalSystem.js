import React, { useState, useEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { Drawer, DrawerClose, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle, DrawerTrigger } from './ui/drawer';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  X, 
  ChevronDown, 
  Check, 
  AlertCircle, 
  Info, 
  Settings, 
  Share2, 
  Download,
  Star,
  Heart,
  MessageSquare,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Clock
} from 'lucide-react';

// Enhanced Mobile Modal with gesture support
const MobileModal = ({ 
  isOpen, 
  onClose, 
  title, 
  description, 
  children, 
  size = 'default', // 'small', 'default', 'large', 'fullscreen'
  position = 'center', // 'center', 'bottom'
  hasHandle = false,
  closable = true,
  overlay = true
}) => {
  const [startY, setStartY] = useState(0);
  const [currentY, setCurrentY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  // Handle touch events for swipe-to-close
  const handleTouchStart = (e) => {
    if (position !== 'bottom') return;
    setStartY(e.touches[0].clientY);
    setIsDragging(true);
  };

  const handleTouchMove = (e) => {
    if (!isDragging || position !== 'bottom') return;
    const currentY = e.touches[0].clientY;
    const diff = currentY - startY;
    
    if (diff > 0) {
      setCurrentY(diff);
    }
  };

  const handleTouchEnd = () => {
    if (!isDragging || position !== 'bottom') return;
    
    if (currentY > 100) {
      onClose();
    } else {
      setCurrentY(0);
    }
    
    setIsDragging(false);
  };

  const modalSizes = {
    small: 'max-w-sm',
    default: 'max-w-md', 
    large: 'max-w-lg',
    fullscreen: 'w-full h-full max-w-none'
  };

  const modalPositions = {
    center: 'items-center justify-center',
    bottom: 'items-end justify-center'
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 flex ${modalPositions[position]} p-4`}>
      {/* Overlay */}
      {overlay && (
        <div 
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={closable ? onClose : undefined}
        />
      )}
      
      {/* Modal Content */}
      <div 
        className={`relative bg-white rounded-t-2xl shadow-2xl w-full ${modalSizes[size]} 
          ${position === 'bottom' ? 'rounded-b-none' : 'rounded-2xl'}
          transition-transform duration-300 ease-out`}
        style={{
          transform: `translateY(${currentY}px)`
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Handle for bottom sheets */}
        {hasHandle && position === 'bottom' && (
          <div className="flex justify-center pt-3 pb-2">
            <div className="w-10 h-1 bg-gray-300 rounded-full" />
          </div>
        )}
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex-1">
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
          </div>
          {closable && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="ml-2 h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        
        {/* Content */}
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

// Mobile Bottom Sheet Component
const MobileBottomSheet = ({ 
  isOpen, 
  onClose, 
  title, 
  description,
  children,
  snapPoints = ['25%', '50%', '90%'], // Height percentages
  initialSnap = 1,
  hasHandle = true
}) => {
  const [currentSnap, setCurrentSnap] = useState(initialSnap);
  const [startY, setStartY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const handleTouchStart = (e) => {
    setStartY(e.touches[0].clientY);
    setIsDragging(true);
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    const currentY = e.touches[0].clientY;
    const diff = startY - currentY; // Negative for down swipe, positive for up
    
    // Handle snapping logic here
    if (Math.abs(diff) > 50) {
      if (diff > 0 && currentSnap < snapPoints.length - 1) {
        setCurrentSnap(currentSnap + 1);
      } else if (diff < 0 && currentSnap > 0) {
        setCurrentSnap(currentSnap - 1);
      } else if (diff < 0 && currentSnap === 0) {
        onClose();
      }
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Overlay */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Bottom Sheet */}
      <div 
        className="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl shadow-2xl transition-all duration-300 ease-out"
        style={{ height: snapPoints[currentSnap] }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Handle */}
        {hasHandle && (
          <div className="flex justify-center pt-3 pb-2">
            <div className="w-10 h-1 bg-gray-300 rounded-full cursor-grab" />
          </div>
        )}
        
        {/* Header */}
        <div className="px-4 pb-2">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {description && <p className="text-sm text-gray-600">{description}</p>}
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto px-4 pb-4">
          {children}
        </div>
        
        {/* Snap Indicators */}
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2 space-y-2">
          {snapPoints.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSnap(index)}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === currentSnap ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

// Action Sheet Component for mobile-friendly menus
const MobileActionSheet = ({ 
  isOpen, 
  onClose, 
  title,
  actions = [],
  destructiveIndex = -1
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div 
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />
      
      <div className="absolute bottom-0 left-0 right-0 p-4">
        {/* Actions Container */}
        <div className="bg-white rounded-2xl overflow-hidden mb-3">
          {title && (
            <div className="px-4 py-3 border-b bg-gray-50">
              <p className="text-sm font-medium text-gray-600 text-center">{title}</p>
            </div>
          )}
          
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={() => {
                action.onPress();
                onClose();
              }}
              className={`w-full px-4 py-3 text-left border-b border-gray-100 last:border-b-0
                ${index === destructiveIndex 
                  ? 'text-red-600 font-medium' 
                  : 'text-gray-900'
                } hover:bg-gray-50 transition-colors`}
            >
              <div className="flex items-center">
                {action.icon && (
                  <action.icon className={`h-5 w-5 mr-3 ${
                    index === destructiveIndex ? 'text-red-600' : 'text-gray-400'
                  }`} />
                )}
                <span className="text-base">{action.title}</span>
              </div>
            </button>
          ))}
        </div>
        
        {/* Cancel Button */}
        <button
          onClick={onClose}
          className="w-full bg-white rounded-2xl px-4 py-3 text-base font-semibold text-blue-600 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

// Mobile-Optimized Confirmation Dialog
const MobileConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message = "Are you sure you want to proceed?",
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default" // 'default', 'destructive'
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      
      <div className="relative bg-white rounded-2xl w-full max-w-sm p-6 text-center">
        <div className="mb-4">
          {variant === 'destructive' ? (
            <AlertCircle className="h-12 w-12 text-red-600 mx-auto mb-3" />
          ) : (
            <Info className="h-12 w-12 text-blue-600 mx-auto mb-3" />
          )}
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600">{message}</p>
        </div>
        
        <div className="space-y-3">
          <Button
            onClick={onConfirm}
            className={`w-full h-12 text-base font-semibold ${
              variant === 'destructive'
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {confirmText}
          </Button>
          <Button
            variant="outline"
            onClick={onClose}
            className="w-full h-12 text-base"
          >
            {cancelText}
          </Button>
        </div>
      </div>
    </div>
  );
};

// Mobile Loading Modal with progress
const MobileLoadingModal = ({
  isOpen,
  title = "Loading...",
  message = "Please wait while we process your request",
  progress = -1, // -1 for indeterminate, 0-100 for determinate
  canCancel = false,
  onCancel
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      
      <div className="relative bg-white rounded-2xl w-full max-w-sm p-6 text-center">
        <div className="mb-6">
          {progress === -1 ? (
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          ) : (
            <div className="relative w-16 h-16 mx-auto mb-4">
              <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="3"
                />
                <path
                  d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="3"
                  strokeDasharray={`${progress}, 100`}
                  className="transition-all duration-300 ease-in-out"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-sm font-bold text-gray-700">{progress}%</span>
              </div>
            </div>
          )}
          
          <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
          <p className="text-sm text-gray-600">{message}</p>
        </div>
        
        {canCancel && (
          <Button
            variant="outline"
            onClick={onCancel}
            className="w-full h-12 text-base"
          >
            Cancel
          </Button>
        )}
      </div>
    </div>
  );
};

// Success/Error Toast Modal for mobile
const MobileToastModal = ({
  isOpen,
  onClose,
  type = 'success', // 'success', 'error', 'warning', 'info'
  title,
  message,
  duration = 3000,
  actions = []
}) => {
  useEffect(() => {
    if (isOpen && duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [isOpen, duration, onClose]);

  if (!isOpen) return null;

  const typeStyles = {
    success: { bg: 'bg-green-600', icon: Check, color: 'text-green-600' },
    error: { bg: 'bg-red-600', icon: AlertCircle, color: 'text-red-600' },
    warning: { bg: 'bg-orange-600', icon: AlertCircle, color: 'text-orange-600' },
    info: { bg: 'bg-blue-600', icon: Info, color: 'text-blue-600' }
  };

  const style = typeStyles[type];
  const IconComponent = style.icon;

  return (
    <div className="fixed top-4 left-4 right-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl border border-gray-200 p-4">
        <div className="flex items-start">
          <div className={`p-2 rounded-full ${style.bg} mr-3`}>
            <IconComponent className="h-5 w-5 text-white" />
          </div>
          
          <div className="flex-1">
            {title && <h4 className="text-sm font-semibold text-gray-900 mb-1">{title}</h4>}
            {message && <p className="text-sm text-gray-600">{message}</p>}
            
            {actions.length > 0 && (
              <div className="flex space-x-2 mt-3">
                {actions.map((action, index) => (
                  <Button
                    key={index}
                    size="sm"
                    variant={action.variant || "outline"}
                    onClick={action.onPress}
                    className="text-xs"
                  >
                    {action.title}
                  </Button>
                ))}
              </div>
            )}
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="ml-2 h-6 w-6 p-0"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
        
        {/* Progress bar for duration */}
        {duration > 0 && (
          <div className="mt-3 h-1 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full ${style.bg} transition-all ease-linear`}
              style={{ 
                animation: `shrink ${duration}ms linear`,
                width: '100%'
              }}
            />
          </div>
        )}
      </div>
      
      <style jsx>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
};

// Contact/Communication Modal for mobile
const MobileCommunicationModal = ({
  isOpen,
  onClose,
  contact = {
    name: "John Doe",
    role: "Legal Consultant", 
    email: "john@example.com",
    phone: "+1 (555) 123-4567",
    location: "New York, NY"
  }
}) => {
  const communicationActions = [
    {
      title: "Call",
      icon: Phone,
      onPress: () => window.open(`tel:${contact.phone}`),
      color: "bg-green-600"
    },
    {
      title: "Email", 
      icon: Mail,
      onPress: () => window.open(`mailto:${contact.email}`),
      color: "bg-blue-600"
    },
    {
      title: "Message",
      icon: MessageSquare,
      onPress: () => console.log("Open messaging"),
      color: "bg-purple-600"
    }
  ];

  return (
    <MobileBottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title="Contact Information"
      initialSnap={1}
      snapPoints={['40%', '60%']}
    >
      <div className="space-y-6">
        {/* Contact Info */}
        <div className="text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-2xl font-bold text-white">
              {contact.name.split(' ').map(n => n[0]).join('')}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{contact.name}</h3>
          <p className="text-sm text-gray-600">{contact.role}</p>
        </div>

        {/* Contact Details */}
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <Mail className="h-5 w-5 text-gray-400 mr-3" />
            <span className="text-sm text-gray-900">{contact.email}</span>
          </div>
          
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <Phone className="h-5 w-5 text-gray-400 mr-3" />
            <span className="text-sm text-gray-900">{contact.phone}</span>
          </div>
          
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <MapPin className="h-5 w-5 text-gray-400 mr-3" />
            <span className="text-sm text-gray-900">{contact.location}</span>
          </div>
        </div>

        {/* Communication Actions */}
        <div className="grid grid-cols-3 gap-3">
          {communicationActions.map((action, index) => (
            <button
              key={index}
              onClick={action.onPress}
              className={`flex flex-col items-center p-4 rounded-xl ${action.color} text-white hover:opacity-90 transition-opacity`}
            >
              <action.icon className="h-6 w-6 mb-2" />
              <span className="text-xs font-medium">{action.title}</span>
            </button>
          ))}
        </div>
      </div>
    </MobileBottomSheet>
  );
};

export {
  MobileModal,
  MobileBottomSheet, 
  MobileActionSheet,
  MobileConfirmDialog,
  MobileLoadingModal,
  MobileToastModal,
  MobileCommunicationModal
};