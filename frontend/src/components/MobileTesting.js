import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Smartphone, 
  Tablet, 
  Monitor,
  Wifi,
  Battery,
  Eye,
  Clock,
  Zap,
  Target,
  Activity,
  Gauge
} from 'lucide-react';

// Mobile Testing Suite Component
const MobileTesting = ({ onClose }) => {
  const [testResults, setTestResults] = useState({});
  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState('');
  const [overallScore, setOverallScore] = useState(0);

  const testSuites = {
    'Touch Targets': {
      description: 'Verify all interactive elements meet 44px minimum touch target requirement',
      tests: [
        'Button minimum size check',
        'Link minimum size check', 
        'Input field minimum size check',
        'Navigation item spacing',
        'Modal close button accessibility'
      ]
    },
    'Responsive Design': {
      description: 'Test component behavior across different screen sizes',
      tests: [
        'Mobile layout (320px-768px)',
        'Tablet layout (768px-1024px)',
        'Desktop layout (1024px+)',
        'Orientation change handling',
        'Safe area handling (iOS notch)'
      ]
    },
    'Performance': {
      description: 'Mobile performance and optimization tests',
      tests: [
        'Initial load time',
        'Image lazy loading',
        'Virtual scrolling efficiency',
        'Memory usage optimization',
        'Bundle size analysis'
      ]
    },
    'Navigation': {
      description: 'Mobile navigation and routing tests',
      tests: [
        'Hamburger menu functionality',
        'Bottom navigation visibility',
        'Swipe gestures support',
        'Back button behavior',
        'Deep link handling'
      ]
    },
    'Modals & Sheets': {
      description: 'Mobile modal system functionality',
      tests: [
        'Bottom sheet swipe gestures',
        'Modal backdrop dismissal',
        'Keyboard avoidance',
        'Action sheet functionality',
        'Toast notifications'
      ]
    },
    'Analytics Dashboard': {
      description: 'Mobile analytics dashboard tests',
      tests: [
        'Chart responsiveness',
        'Touch interactions on graphs',
        'Data table scrolling',
        'Metric card layout',
        'Export functionality'
      ]
    },
    'Contract Wizard': {
      description: 'Mobile contract wizard optimization',
      tests: [
        'Form field stacking',
        'Progress indicator visibility',
        'Input validation feedback',
        'Step navigation',
        'Help system accessibility'
      ]
    },
    'Accessibility': {
      description: 'Mobile accessibility compliance tests',
      tests: [
        'Screen reader compatibility',
        'High contrast mode support',
        'Reduced motion preferences',
        'Voice over navigation',
        'Keyboard navigation fallback'
      ]
    }
  };

  // Mock test runner
  const runTestSuite = async (suiteName, tests) => {
    const results = {};
    
    for (const test of tests) {
      setCurrentTest(`${suiteName}: ${test}`);
      
      // Simulate test execution
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Mock results - randomize for demo
      const success = Math.random() > 0.2; // 80% success rate
      const duration = Math.random() * 500 + 100;
      
      results[test] = {
        status: success ? 'pass' : 'fail',
        duration: Math.round(duration),
        details: success ? 'Test completed successfully' : 'Test failed - needs optimization'
      };
    }
    
    return results;
  };

  // Run all tests
  const runAllTests = async () => {
    setIsRunning(true);
    setTestResults({});
    
    const allResults = {};
    let totalScore = 0;
    let totalTests = 0;
    
    for (const [suiteName, suite] of Object.entries(testSuites)) {
      const suiteResults = await runTestSuite(suiteName, suite.tests);
      allResults[suiteName] = {
        ...suite,
        results: suiteResults
      };
      
      // Calculate suite score
      const passed = Object.values(suiteResults).filter(r => r.status === 'pass').length;
      const suiteScore = (passed / suite.tests.length) * 100;
      allResults[suiteName].score = Math.round(suiteScore);
      
      totalScore += suiteScore;
      totalTests += suite.tests.length;
    }
    
    setTestResults(allResults);
    setOverallScore(Math.round(totalScore / Object.keys(testSuites).length));
    setIsRunning(false);
    setCurrentTest('');
  };

  // Test result component
  const TestResult = ({ test, result }) => {
    const getIcon = () => {
      switch (result.status) {
        case 'pass':
          return <CheckCircle className="h-4 w-4 text-green-600" />;
        case 'fail':
          return <XCircle className="h-4 w-4 text-red-600" />;
        case 'warning':
          return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
        default:
          return <Activity className="h-4 w-4 text-gray-400" />;
      }
    };

    return (
      <div className="flex items-center justify-between p-2 border-b border-gray-100 last:border-b-0">
        <div className="flex items-center space-x-2">
          {getIcon()}
          <span className="text-sm">{test}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-500">{result.duration}ms</span>
          <Badge 
            variant={result.status === 'pass' ? 'default' : result.status === 'fail' ? 'destructive' : 'secondary'}
            className="text-xs"
          >
            {result.status.toUpperCase()}
          </Badge>
        </div>
      </div>
    );
  };

  // Test suite card
  const TestSuiteCard = ({ suiteName, suite }) => (
    <Card className="mb-4">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base">{suiteName}</CardTitle>
            <CardDescription className="text-sm">{suite.description}</CardDescription>
          </div>
          {suite.score !== undefined && (
            <div className="text-right">
              <div className={`text-2xl font-bold ${
                suite.score >= 80 ? 'text-green-600' : 
                suite.score >= 60 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {suite.score}%
              </div>
              <div className="text-xs text-gray-500">Score</div>
            </div>
          )}
        </div>
        {suite.score !== undefined && (
          <Progress value={suite.score} className="h-2 mt-2" />
        )}
      </CardHeader>
      <CardContent>
        {suite.results && (
          <div className="space-y-1">
            {Object.entries(suite.results).map(([test, result]) => (
              <TestResult key={test} test={test} result={result} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );

  // Device simulation controls
  const DeviceSimulator = () => {
    const [selectedDevice, setSelectedDevice] = useState('mobile');
    
    const devices = {
      mobile: { width: 375, height: 667, name: 'iPhone SE', icon: Smartphone },
      tablet: { width: 768, height: 1024, name: 'iPad', icon: Tablet },
      desktop: { width: 1440, height: 900, name: 'Desktop', icon: Monitor }
    };

    return (
      <Card className="mb-4">
        <CardHeader>
          <CardTitle className="text-base">Device Simulation</CardTitle>
          <CardDescription>Test across different device types</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2">
            {Object.entries(devices).map(([key, device]) => {
              const IconComponent = device.icon;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedDevice(key)}
                  className={`p-3 rounded-lg border transition-colors ${
                    selectedDevice === key 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <IconComponent className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                  <div className="text-xs font-medium">{device.name}</div>
                  <div className="text-xs text-gray-500">
                    {device.width} × {device.height}
                  </div>
                </button>
              );
            })}
          </div>
          
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium mb-2">Current Viewport</div>
            <div className="text-xs text-gray-600">
              Width: {window.innerWidth}px, Height: {window.innerHeight}px
            </div>
            <div className="text-xs text-gray-600">
              Device Pixel Ratio: {window.devicePixelRatio}
            </div>
            <div className="text-xs text-gray-600">
              Touch Support: {window.navigator.maxTouchPoints > 0 ? 'Yes' : 'No'}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="fixed inset-0 z-50 bg-white overflow-y-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 sticky top-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold">Mobile Testing Suite</h1>
            <p className="text-sm opacity-90">Cross-device validation & optimization</p>
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

      <div className="p-4">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tests">Test Results</TabsTrigger>
            <TabsTrigger value="devices">Devices</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            {/* Overall Score */}
            <Card className="bg-gradient-to-br from-blue-50 to-purple-50">
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
                        stroke={overallScore >= 80 ? "#10B981" : overallScore >= 60 ? "#F59E0B" : "#EF4444"}
                        strokeWidth="2"
                        strokeDasharray={`${overallScore}, 100`}
                        className="transition-all duration-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl font-bold text-gray-900">{overallScore}</span>
                    </div>
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Mobile Optimization Score
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  {overallScore >= 80 ? 'Excellent mobile optimization!' : 
                   overallScore >= 60 ? 'Good, with room for improvement' : 
                   'Needs significant mobile optimization'}
                </p>
                
                <Button 
                  onClick={runAllTests}
                  disabled={isRunning}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                >
                  {isRunning ? (
                    <>
                      <Activity className="h-4 w-4 mr-2 animate-spin" />
                      Running Tests...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Run All Tests
                    </>
                  )}
                </Button>

                {isRunning && currentTest && (
                  <div className="mt-4 p-3 bg-white rounded-lg">
                    <div className="text-sm font-medium">Currently Testing:</div>
                    <div className="text-sm text-gray-600">{currentTest}</div>
                    <Progress value={Math.random() * 100} className="h-1 mt-2" />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Test Suites</p>
                      <p className="text-2xl font-bold">{Object.keys(testSuites).length}</p>
                    </div>
                    <Target className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Tests</p>
                      <p className="text-2xl font-bold">
                        {Object.values(testSuites).reduce((sum, suite) => sum + suite.tests.length, 0)}
                      </p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Test Categories Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Test Categories</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(testSuites).map(([name, suite]) => (
                    <div key={name} className="flex items-center justify-between p-2 border rounded-lg">
                      <div>
                        <span className="font-medium text-sm">{name}</span>
                        <p className="text-xs text-gray-600">{suite.tests.length} tests</p>
                      </div>
                      {testResults[name] && (
                        <Badge 
                          variant={testResults[name].score >= 80 ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {testResults[name].score}%
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="tests" className="space-y-4">
            {Object.keys(testResults).length === 0 ? (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  No test results available. Run the test suite to see detailed results.
                </AlertDescription>
              </Alert>
            ) : (
              Object.entries(testResults).map(([suiteName, suite]) => (
                <TestSuiteCard key={suiteName} suiteName={suiteName} suite={suite} />
              ))
            )}
          </TabsContent>

          <TabsContent value="devices" className="space-y-4">
            <DeviceSimulator />
            
            {/* Network conditions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Network Conditions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Connection Type</span>
                    <Badge variant="outline">
                      {navigator.connection?.effectiveType || 'Unknown'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Downlink Speed</span>
                    <span className="text-sm text-gray-600">
                      {navigator.connection?.downlink || 'Unknown'} Mbps
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Online Status</span>
                    <Badge variant={navigator.onLine ? 'default' : 'destructive'}>
                      {navigator.onLine ? 'Online' : 'Offline'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Performance monitoring */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Memory Usage</span>
                    <span className="text-sm text-gray-600">
                      {performance.memory ? 
                        `${Math.round((performance.memory.usedJSHeapSize / performance.memory.totalJSHeapSize) * 100)}%` : 
                        'Not Available'
                      }
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Hardware Concurrency</span>
                    <span className="text-sm text-gray-600">
                      {navigator.hardwareConcurrency || 'Unknown'} cores
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Device Memory</span>
                    <span className="text-sm text-gray-600">
                      {navigator.deviceMemory || 'Unknown'} GB
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MobileTesting;