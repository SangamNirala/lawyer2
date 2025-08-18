import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { 
  TrendingUp, 
  BarChart3, 
  Target, 
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Activity
} from 'lucide-react';

const StrategyDashboard = ({ isCollapsed, onToggle }) => {
  const [analytics, setAnalytics] = useState(null);
  const [abTests, setAbTests] = useState(null);
  const [predictorHealth, setPredictorHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [analyticsRes, abTestsRes, healthRes] = await Promise.all([
        fetch(`${backendUrl}/api/ai-agents/contract-negotiation/analytics/overview`),
        fetch(`${backendUrl}/api/ai-agents/contract-negotiation/analytics/ab-tests`),
        fetch(`${backendUrl}/api/ai-agents/contract-negotiation/predictor/health`)
      ]);
      
      if (analyticsRes.ok) {
        const analyticsData = await analyticsRes.json();
        setAnalytics(analyticsData);
      }
      
      if (abTestsRes.ok) {
        const abTestsData = await abTestsRes.json();
        setAbTests(abTestsData);
      }
      
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setPredictorHealth(healthData);
      }
      
      setLastRefresh(new Date());
    } catch (err) {
      setError(`Analytics fetch failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format = 'csv') => {
    try {
      const response = await fetch(`${backendUrl}/api/ai-agents/contract-negotiation/analytics/export?format=${format}`);
      
      if (!response.ok) {
        throw new Error(`Export failed: ${response.status}`);
      }
      
      if (format === 'csv') {
        const csvContent = await response.text();
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `strategy_analytics_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        const jsonData = await response.json();
        const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `strategy_analytics_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    // Auto-refresh every 2 minutes
    const interval = setInterval(fetchAnalytics, 120000);
    return () => clearInterval(interval);
  }, []);

  const AcceptanceChart = ({ data }) => {
    if (!data || data.length === 0) {
      return <div className="text-gray-500 text-sm">No acceptance data available</div>;
    }

    const maxRate = Math.max(...data.map(d => d.acceptance_rate));
    
    return (
      <div className="space-y-2">
        {data.slice(-7).map((item, index) => (
          <div key={index} className="flex items-center justify-between">
            <span className="text-xs text-gray-600 w-20">{item.date}</span>
            <div className="flex-1 mx-2">
              <div className="bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(item.acceptance_rate / maxRate) * 100}%` }}
                />
              </div>
            </div>
            <span className="text-xs text-gray-800 w-12 text-right">
              {(item.acceptance_rate * 100).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    );
  };

  const ScenarioPerformanceChart = ({ data }) => {
    if (!data || data.length === 0) {
      return <div className="text-gray-500 text-sm">No scenario data available</div>;
    }

    return (
      <div className="space-y-3">
        {data.map((scenario, index) => (
          <div key={index} className="border rounded-lg p-3">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h4 className="font-medium text-sm">{scenario.scenario}</h4>
                <p className="text-xs text-gray-500">{scenario.total_uses} uses</p>
              </div>
              <Badge 
                variant={scenario.acceptance_rate > 0.6 ? "default" : scenario.acceptance_rate > 0.4 ? "secondary" : "destructive"}
                className="text-xs"
              >
                {(scenario.acceptance_rate * 100).toFixed(1)}%
              </Badge>
            </div>
            <Progress 
              value={scenario.acceptance_rate * 100} 
              className="h-2 mb-1"
            />
            <div className="text-xs text-gray-500">
              Avg response: {Math.round(scenario.avg_response_time)}s
            </div>
          </div>
        ))}
      </div>
    );
  };

  const RiskRewardScatter = ({ correlationData }) => {
    if (!correlationData || correlationData.length === 0) {
      return <div className="text-gray-500 text-sm">No correlation data available</div>;
    }

    return (
      <div className="space-y-2">
        <div className="text-xs text-gray-600 mb-2">Leverage Score vs Acceptance Rate</div>
        {correlationData.map((point, index) => (
          <div key={index} className="flex items-center justify-between py-1">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span className="text-xs">Leverage {point._id}/10</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                <div 
                  className="bg-green-500 h-1.5 rounded-full"
                  style={{ width: `${point.acceptance_rate * 100}%` }}
                />
              </div>
              <span className="text-xs w-8">{(point.acceptance_rate * 100).toFixed(0)}%</span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (isCollapsed) {
    return (
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Strategy Analytics</span>
            </CardTitle>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onToggle}
              className="h-6 w-6 p-0"
            >
              <TrendingUp className="h-3 w-3" />
            </Button>
          </div>
          <CardDescription className="text-xs">
            Real-time negotiation intelligence
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="border-l-4 border-l-blue-500">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Strategy Analytics Dashboard</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchAnalytics}
              disabled={loading}
            >
              <RefreshCw className={`h-3 w-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onToggle}
            >
              Collapse
            </Button>
          </div>
        </div>
        <CardDescription>
          Phase 4 Advanced Intelligence: Real-time analytics and predictive modeling
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Predictor Health Status */}
        {predictorHealth && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-sm mb-3 flex items-center">
              <Activity className="h-4 w-4 mr-2" />
              AI Predictor Health
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">
                  {predictorHealth.status === 'ok' ? 
                    <CheckCircle className="h-5 w-5 mx-auto" /> : 
                    <AlertCircle className="h-5 w-5 mx-auto" />
                  }
                </div>
                <div className="text-xs text-gray-600">Status</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold">{predictorHealth.total_feedback_events}</div>
                <div className="text-xs text-gray-600">Feedback Events</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold">{predictorHealth.sessions_trained}</div>
                <div className="text-xs text-gray-600">Trained Sessions</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold">{predictorHealth.model_version}</div>
                <div className="text-xs text-gray-600">Model Version</div>
              </div>
            </div>
          </div>
        )}

        {/* Key Metrics Overview */}
        {analytics?.overall_stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="p-4">
              <div className="text-2xl font-bold text-blue-600">
                {(analytics.overall_stats.overall_acceptance_rate * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-600">Overall Acceptance Rate</div>
            </Card>
            <Card className="p-4">
              <div className="text-2xl font-bold text-green-600">
                {analytics.overall_stats.total_events}
              </div>
              <div className="text-xs text-gray-600">Total Events</div>
            </Card>
            <Card className="p-4">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(analytics.overall_stats.avg_response_time)}s
              </div>
              <div className="text-xs text-gray-600">Avg Response Time</div>
            </Card>
            <Card className="p-4">
              <div className="text-2xl font-bold text-orange-600">
                {analytics.overall_stats.total_sessions}
              </div>
              <div className="text-xs text-gray-600">Active Sessions</div>
            </Card>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6">
          {/* Acceptance Rate Trends */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center">
                <TrendingUp className="h-4 w-4 mr-2" />
                Acceptance Rate Over Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                </div>
              ) : (
                <AcceptanceChart data={analytics?.acceptance_rate_over_time} />
              )}
            </CardContent>
          </Card>

          {/* Scenario Performance */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm flex items-center">
                <Target className="h-4 w-4 mr-2" />
                Scenario Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                </div>
              ) : (
                <ScenarioPerformanceChart data={analytics?.scenario_performance} />
              )}
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* A/B Test Results */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">A/B Test Results</CardTitle>
            </CardHeader>
            <CardContent>
              {abTests?.running_tests?.length > 0 ? (
                <div className="space-y-3">
                  {abTests.running_tests.map((test, index) => (
                    <div key={index} className="border rounded p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-medium text-sm">{test._id}</span>
                        <Badge variant={test.statistical_power === 'high' ? 'default' : 'secondary'}>
                          {test.statistical_power} power
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        Success Rate: {(test.success_rate * 100).toFixed(1)}% ({test.total_tests} tests)
                      </div>
                      {test.confidence_interval && (
                        <div className="text-xs text-gray-500">
                          95% CI: [{(test.confidence_interval[0] * 100).toFixed(1)}%, {(test.confidence_interval[1] * 100).toFixed(1)}%]
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-sm">No A/B tests running</div>
              )}
            </CardContent>
          </Card>

          {/* Risk-Reward Analysis */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Risk-Reward Correlation</CardTitle>
            </CardHeader>
            <CardContent>
              <RiskRewardScatter correlationData={analytics?.leverage_vs_acceptance} />
            </CardContent>
          </Card>
        </div>

        {/* Top Recommendations */}
        {analytics?.top_recommendations?.length > 0 && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Top Strategic Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {analytics.top_recommendations.slice(0, 5).map((rec, index) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <span className="text-sm flex-1">{rec.recommendation}</span>
                    <Badge variant="outline" className="ml-2">
                      {rec.frequency}x
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Export Actions */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-xs text-gray-500">
            Last updated: {lastRefresh?.toLocaleTimeString()}
          </div>
          <div className="flex space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => exportData('csv')}
            >
              <Download className="h-3 w-3 mr-1" />
              Export CSV
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => exportData('json')}
            >
              <Download className="h-3 w-3 mr-1" />
              Export JSON
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StrategyDashboard;