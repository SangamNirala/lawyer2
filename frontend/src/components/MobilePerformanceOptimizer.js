import React, { useState, useEffect, useMemo, useCallback, lazy, Suspense } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Gauge, 
  Smartphone, 
  Wifi, 
  Battery, 
  Zap, 
  Eye, 
  Clock,
  Cpu,
  MemoryStick,
  HardDrive,
  Activity,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

// Performance monitoring hook
const usePerformanceMonitor = () => {
  const [metrics, setMetrics] = useState({
    loadTime: 0,
    renderTime: 0,
    memoryUsage: 0,
    networkStatus: 'unknown',
    batteryLevel: 100,
    deviceType: 'unknown'
  });

  useEffect(() => {
    // Monitor page load performance
    const measureLoadTime = () => {
      if (performance && performance.timing) {
        const { navigationStart, loadEventEnd } = performance.timing;
        const loadTime = loadEventEnd - navigationStart;
        setMetrics(prev => ({ ...prev, loadTime }));
      }
    };

    // Monitor network status
    const updateNetworkStatus = () => {
      if ('connection' in navigator) {
        const connection = navigator.connection;
        setMetrics(prev => ({
          ...prev,
          networkStatus: connection.effectiveType || 'unknown',
          downlink: connection.downlink
        }));
      }
    };

    // Monitor battery level
    const updateBatteryInfo = async () => {
      if ('getBattery' in navigator) {
        try {
          const battery = await navigator.getBattery();
          setMetrics(prev => ({
            ...prev,
            batteryLevel: Math.round(battery.level * 100),
            charging: battery.charging
          }));
        } catch (error) {
          console.log('Battery API not available');
        }
      }
    };

    // Detect device type
    const detectDeviceType = () => {
      const userAgent = navigator.userAgent.toLowerCase();
      let deviceType = 'desktop';
      
      if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)) {
        deviceType = 'mobile';
      } else if (/tablet|ipad/i.test(userAgent)) {
        deviceType = 'tablet';
      }
      
      setMetrics(prev => ({ ...prev, deviceType }));
    };

    // Monitor memory usage (if available)
    const updateMemoryUsage = () => {
      if ('memory' in performance) {
        const memory = performance.memory;
        setMetrics(prev => ({
          ...prev,
          memoryUsage: Math.round((memory.usedJSHeapSize / memory.totalJSHeapSize) * 100)
        }));
      }
    };

    measureLoadTime();
    updateNetworkStatus();
    updateBatteryInfo();
    detectDeviceType();
    updateMemoryUsage();

    // Update memory usage periodically
    const memoryInterval = setInterval(updateMemoryUsage, 10000);

    // Listen for network changes
    if ('connection' in navigator) {
      navigator.connection.addEventListener('change', updateNetworkStatus);
    }

    return () => {
      clearInterval(memoryInterval);
      if ('connection' in navigator) {
        navigator.connection.removeEventListener('change', updateNetworkStatus);
      }
    };
  }, []);

  return metrics;
};

// Image optimization hook for mobile
const useOptimizedImage = (src, options = {}) => {
  const {
    quality = 80,
    format = 'webp',
    lazy = true,
    placeholder = true
  } = options;

  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const optimizedSrc = useMemo(() => {
    if (!src) return '';
    
    // If it's already optimized or a data URL, return as-is
    if (src.startsWith('data:') || src.includes('q=') || src.includes('f=')) {
      return src;
    }

    // For Unsplash images, add optimization parameters
    if (src.includes('unsplash.com')) {
      const url = new URL(src);
      url.searchParams.set('q', quality);
      url.searchParams.set('f', format);
      url.searchParams.set('auto', 'format');
      return url.toString();
    }

    return src;
  }, [src, quality, format]);

  const handleLoad = useCallback(() => {
    setLoaded(true);
    setError(false);
  }, []);

  const handleError = useCallback(() => {
    setError(true);
    setLoaded(false);
  }, []);

  return {
    src: optimizedSrc,
    loaded,
    error,
    onLoad: handleLoad,
    onError: handleError
  };
};

// Virtual scrolling hook for large lists
const useVirtualScrolling = (items = [], containerHeight = 400, itemHeight = 50) => {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );

  const visibleItems = items.slice(visibleStart, visibleEnd);

  const totalHeight = items.length * itemHeight;
  const offsetY = visibleStart * itemHeight;

  const handleScroll = useCallback((e) => {
    setScrollTop(e.target.scrollTop);
  }, []);

  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    visibleStart,
    visibleEnd
  };
};

// Debounced input hook
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Intersection Observer hook for lazy loading
const useIntersectionObserver = (options = {}) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [ref, setRef] = useState(null);

  const {
    threshold = 0.1,
    rootMargin = '50px',
    triggerOnce = true
  } = options;

  useEffect(() => {
    if (!ref) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsIntersecting(true);
          if (triggerOnce) {
            observer.disconnect();
          }
        } else if (!triggerOnce) {
          setIsIntersecting(false);
        }
      },
      { threshold, rootMargin }
    );

    observer.observe(ref);

    return () => observer.disconnect();
  }, [ref, threshold, rootMargin, triggerOnce]);

  return [setRef, isIntersecting];
};

// Optimized Image component
const OptimizedImage = ({ 
  src, 
  alt, 
  className, 
  lazy = true, 
  quality = 80,
  placeholder = true,
  ...props 
}) => {
  const { src: optimizedSrc, loaded, error, onLoad, onError } = useOptimizedImage(src, { quality });
  const [ref, isIntersecting] = useIntersectionObserver();
  
  const shouldLoad = !lazy || isIntersecting;

  return (
    <div ref={lazy ? ref : null} className={`relative ${className || ''}`}>
      {shouldLoad && (
        <img
          src={optimizedSrc}
          alt={alt}
          onLoad={onLoad}
          onError={onError}
          className={`transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
          {...props}
        />
      )}
      
      {/* Placeholder */}
      {placeholder && !loaded && !error && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
      
      {/* Error state */}
      {error && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <span className="text-gray-400 text-sm">Failed to load</span>
        </div>
      )}
    </div>
  );
};

// Virtual List component
const VirtualList = ({ 
  items, 
  renderItem, 
  itemHeight = 60, 
  height = 400,
  className = ''
}) => {
  const { visibleItems, totalHeight, offsetY, handleScroll } = useVirtualScrolling(
    items,
    height,
    itemHeight
  );

  return (
    <div 
      className={`overflow-auto ${className}`}
      style={{ height }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div key={index} style={{ height: itemHeight }}>
              {renderItem(item, index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Performance Dashboard component
const MobilePerformanceDashboard = ({ onClose }) => {
  const metrics = usePerformanceMonitor();
  const [showDetails, setShowDetails] = useState(false);

  const getPerformanceScore = () => {
    let score = 100;
    
    if (metrics.loadTime > 3000) score -= 20;
    if (metrics.memoryUsage > 80) score -= 15;
    if (metrics.networkStatus === '2g') score -= 25;
    if (metrics.batteryLevel < 20) score -= 10;
    
    return Math.max(0, score);
  };

  const performanceScore = getPerformanceScore();

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getNetworkIcon = (status) => {
    switch (status) {
      case '4g':
      case '5g':
        return <Wifi className="h-4 w-4 text-green-600" />;
      case '3g':
        return <Wifi className="h-4 w-4 text-yellow-600" />;
      case '2g':
      case 'slow-2g':
        return <Wifi className="h-4 w-4 text-red-600" />;
      default:
        return <Wifi className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold">Performance Monitor</h1>
            <p className="text-sm opacity-90">Mobile Optimization Status</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-white hover:bg-white/20"
          >
            ×
          </Button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Performance Score */}
        <Card className="bg-gradient-to-br from-blue-50 to-green-50">
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center mb-4">
              <div className="relative">
                <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="2"
                  />
                  <path
                    d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                    fill="none"
                    stroke={performanceScore >= 80 ? "#10B981" : performanceScore >= 60 ? "#F59E0B" : "#EF4444"}
                    strokeWidth="2"
                    strokeDasharray={`${performanceScore}, 100`}
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-2xl font-bold ${getScoreColor(performanceScore)}`}>
                    {performanceScore}
                  </span>
                </div>
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Performance Score</h3>
            <p className="text-sm text-gray-600">
              {performanceScore >= 80 ? 'Excellent' : performanceScore >= 60 ? 'Good' : 'Needs Improvement'}
            </p>
          </CardContent>
        </Card>

        {/* Quick Metrics */}
        <div className="grid grid-cols-2 gap-3">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600">Load Time</p>
                  <p className="text-lg font-bold">
                    {(metrics.loadTime / 1000).toFixed(1)}s
                  </p>
                </div>
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600">Memory</p>
                  <p className="text-lg font-bold">{metrics.memoryUsage}%</p>
                </div>
                <MemoryStick className="h-6 w-6 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Device Info */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Device Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Smartphone className="h-4 w-4 text-gray-600 mr-2" />
                <span className="text-sm">Device Type</span>
              </div>
              <Badge variant="outline" className="capitalize">
                {metrics.deviceType}
              </Badge>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {getNetworkIcon(metrics.networkStatus)}
                <span className="text-sm ml-2">Network</span>
              </div>
              <Badge variant="outline" className="uppercase">
                {metrics.networkStatus}
              </Badge>
            </div>

            {metrics.batteryLevel !== undefined && (
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Battery className="h-4 w-4 text-gray-600 mr-2" />
                  <span className="text-sm">Battery</span>
                </div>
                <Badge variant="outline">
                  {metrics.batteryLevel}%
                </Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detailed Metrics */}
        {showDetails && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Detailed Performance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Memory Usage</span>
                  <span>{metrics.memoryUsage}%</span>
                </div>
                <Progress 
                  value={metrics.memoryUsage} 
                  className="h-2"
                />
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Load Performance</span>
                  <span>{metrics.loadTime < 3000 ? 'Good' : 'Poor'}</span>
                </div>
                <Progress 
                  value={metrics.loadTime < 3000 ? 85 : 45} 
                  className="h-2"
                />
              </div>

              {metrics.downlink && (
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Network Speed</span>
                    <span>{metrics.downlink} Mbps</span>
                  </div>
                  <Progress 
                    value={Math.min(metrics.downlink * 10, 100)} 
                    className="h-2"
                  />
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Optimization Tips */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Optimization Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {performanceScore < 80 && (
                <>
                  {metrics.loadTime > 3000 && (
                    <div className="flex items-start space-x-2 text-sm">
                      <AlertTriangle className="h-4 w-4 text-orange-500 mt-0.5" />
                      <span>Consider enabling lazy loading for images</span>
                    </div>
                  )}
                  
                  {metrics.memoryUsage > 80 && (
                    <div className="flex items-start space-x-2 text-sm">
                      <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5" />
                      <span>High memory usage detected - close unused tabs</span>
                    </div>
                  )}
                  
                  {metrics.networkStatus === '2g' && (
                    <div className="flex items-start space-x-2 text-sm">
                      <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5" />
                      <span>Slow network - consider offline mode</span>
                    </div>
                  )}
                </>
              )}
              
              {performanceScore >= 80 && (
                <div className="flex items-start space-x-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                  <span>Your app is well optimized for mobile!</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="space-y-3">
          <Button
            variant="outline"
            onClick={() => setShowDetails(!showDetails)}
            className="w-full"
          >
            {showDetails ? 'Hide' : 'Show'} Detailed Metrics
          </Button>
          
          <Button
            onClick={onClose}
            className="w-full"
          >
            Close Monitor
          </Button>
        </div>
      </div>
    </div>
  );
};

// Performance optimization utilities
const PerformanceUtils = {
  // Preload critical resources
  preloadResource: (href, as = 'script', crossorigin = false) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = href;
    link.as = as;
    if (crossorigin) link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  },

  // Lazy load non-critical CSS
  loadCSS: (href) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    document.head.appendChild(link);
  },

  // Measure performance
  measurePerformance: (name, fn) => {
    if (!performance.mark) return fn();
    
    const startMark = `${name}-start`;
    const endMark = `${name}-end`;
    
    performance.mark(startMark);
    const result = fn();
    performance.mark(endMark);
    performance.measure(name, startMark, endMark);
    
    return result;
  },

  // Check if device has low-end capabilities
  isLowEndDevice: () => {
    const memory = navigator.deviceMemory;
    const cores = navigator.hardwareConcurrency;
    
    return (memory && memory < 4) || (cores && cores < 4);
  },

  // Reduce motion for accessibility and performance
  prefersReducedMotion: () => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
};

export {
  usePerformanceMonitor,
  useOptimizedImage,
  useVirtualScrolling,
  useDebounce,
  useIntersectionObserver,
  OptimizedImage,
  VirtualList,
  MobilePerformanceDashboard,
  PerformanceUtils
};