import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  BarChart, Bar, PieChart, Pie, Cell, Area, AreaChart
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Clock, 
  Users, 
  Shield, 
  BarChart3, 
  Activity, 
  Target,
  ArrowLeft,
  RefreshCw,
  Download,
  Settings,
  Eye,
  AlertCircle,
  CheckCircle,
  Zap,
  FileText,
  Brain,
  Gauge
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mobile-optimized color schemes
const MOBILE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

// Mobile-optimized Metric Card
const MobileMetricCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  color = "blue", 
  trend, 
  subtitle, 
  loading = false,
  size = "normal" 
}) => (
  <Card className={`relative overflow-hidden transition-all duration-300 ${
    size === "large" ? "col-span-2" : ""
  }`}>
    <CardContent className="p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-medium text-gray-600 mb-1">{title}</p>
          <div className="flex items-baseline space-x-2">
            <p className={`font-bold text-gray-900 ${
              size === "large" ? "text-2xl" : "text-xl"
            }`}>
              {loading ? (
                <div className="animate-pulse bg-gray-200 h-6 w-16 rounded"></div>
              ) : (
                value
              )}
            </p>
            {change !== undefined && (
              <div className={`flex items-center text-xs ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {change >= 0 ? (
                  <TrendingUp className="h-3 w-3 mr-1" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1" />
                )}
                {Math.abs(change)}%
              </div>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2">
              <Badge 
                variant="outline" 
                className={`text-xs ${
                  trend === 'up' ? 'border-green-500 text-green-700' : 
                  trend === 'down' ? 'border-red-500 text-red-700' : 
                  'border-gray-500 text-gray-700'
                }`}
              >
                {trend === 'up' ? '↗ Up' : trend === 'down' ? '↘ Down' : '→ Stable'}
              </Badge>
            </div>
          )}
        </div>
        <div className={`p-2 rounded-lg bg-${color}-100`}>
          <Icon className={`h-5 w-5 text-${color}-600`} />
        </div>
      </div>
    </CardContent>
    <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-${color}-400 to-${color}-600`}></div>
  </Card>
);

// Mobile Chart Component with responsive sizing
const MobileChart = ({ title, children, height = 200 }) => (
  <Card>
    <CardHeader className="pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
    </CardHeader>
    <CardContent className="pt-2">
      <ResponsiveContainer width="100%" height={height}>
        {children}
      </ResponsiveContainer>
    </CardContent>
  </Card>
);

// Mobile Performance Indicator
const MobilePerformanceRing = ({ value, label, color = "blue" }) => (
  <div className="flex flex-col items-center p-3">
    <div className="relative w-16 h-16">
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
          stroke={color === "blue" ? "#3B82F6" : color === "green" ? "#10B981" : "#F59E0B"}
          strokeWidth="3"
          strokeDasharray={`${value}, 100`}
          className="transition-all duration-300 ease-in-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-xs font-bold text-gray-700">{value}%</span>
      </div>
    </div>
    <p className="text-xs text-gray-600 mt-2 text-center">{label}</p>
  </div>
);

const MobileAnalyticsDashboard = ({ onBack }) => {
  // State management
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [costAnalysis, setCostAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      
      const [dashboardRes, performanceRes, costRes] = await Promise.all([
        axios.get(`${API}/analytics/dashboard`).catch(() => ({ data: generateMockDashboardData() })),
        axios.get(`${API}/analytics/performance-metrics`).catch(() => ({ data: generateMockPerformanceData() })),
        axios.get(`${API}/analytics/cost-analysis`).catch(() => ({ data: generateMockCostData() }))
      ]);
      
      setDashboardData(dashboardRes.data);
      setPerformanceMetrics(performanceRes.data);
      setCostAnalysis(costRes.data);
      
    } catch (error) {
      console.error('Error loading analytics data:', error);
      // Load mock data as fallback
      setDashboardData(generateMockDashboardData());
      setPerformanceMetrics(generateMockPerformanceData());
      setCostAnalysis(generateMockCostData());
    } finally {
      setLoading(false);
    }
  };

  // Mock data generators for development/fallback
  const generateMockDashboardData = () => ({
    total_contracts: 156,
    active_contracts: 89,
    contracts_this_month: 23,
    success_rate: 94.2,
    avg_completion_time: 4.5,
    revenue_this_month: 45680,
    client_satisfaction: 4.8,
    recent_activity: Array.from({ length: 7 }, (_, i) => ({
      date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      contracts: Math.floor(Math.random() * 10) + 5,
      revenue: Math.floor(Math.random() * 5000) + 2000
    })).reverse()
  });

  const generateMockPerformanceData = () => ({
    success_rate: 94.2,
    average_completion_time: 4.5,
    client_satisfaction: 4.8,
    renewal_rate: 87.5,
    efficiency_improvement: 23.8,
    performance_trends: Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      success_rate: 90 + Math.random() * 10,
      completion_time: 3 + Math.random() * 4
    })).reverse()
  });

  const generateMockCostData = () => ({
    total_savings: 28450,
    time_saved_hours: 234,
    cost_per_contract_traditional: 850,
    cost_per_contract_automation: 125,
    roi: 3.2,
    savings_percentage: 85.3
  });

  const refreshData = async () => {
    setRefreshing(true);
    await loadAnalyticsData();
    setRefreshing(false);
  };

  // Mobile Header
  const MobileHeader = () => (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 sticky top-0 z-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onBack}
            className="text-white hover:bg-white/20 p-2 min-h-[44px] min-w-[44px]"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-lg font-bold">Analytics</h1>
            <p className="text-sm opacity-90">Performance Dashboard</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={refreshData}
            disabled={refreshing}
            className="text-white hover:bg-white/20 p-2 min-h-[44px] min-w-[44px]"
          >
            <RefreshCw className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          
          <Sheet open={showSettings} onOpenChange={setShowSettings}>
            <SheetTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-white hover:bg-white/20 p-2 min-h-[44px] min-w-[44px]"
              >
                <Settings className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px]">
              <SheetHeader>
                <SheetTitle>Analytics Settings</SheetTitle>
                <SheetDescription>
                  Customize your analytics view
                </SheetDescription>
              </SheetHeader>
              
              <div className="mt-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time Range
                  </label>
                  <Select value={timeRange} onValueChange={setTimeRange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7d">Last 7 days</SelectItem>
                      <SelectItem value="30d">Last 30 days</SelectItem>
                      <SelectItem value="90d">Last 3 months</SelectItem>
                      <SelectItem value="1y">Last year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Auto Refresh</span>
                  <Button variant="outline" size="sm">
                    Enable
                  </Button>
                </div>
                
                <div>
                  <Button className="w-full" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export Data
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </div>
  );

  // Overview Tab - Mobile Optimized
  const OverviewTab = () => (
    <div className="space-y-4 p-4">
      {/* Key Metrics Grid - Mobile 2x2 Layout */}
      <div className="grid grid-cols-2 gap-3">
        <MobileMetricCard
          title="Total Contracts"
          value={dashboardData?.total_contracts || 0}
          change={12.5}
          icon={FileText}
          color="blue"
          trend="up"
          loading={loading}
        />
        <MobileMetricCard
          title="Success Rate"
          value={`${dashboardData?.success_rate || 0}%`}
          change={2.3}
          icon={CheckCircle}
          color="green"
          trend="up"
          loading={loading}
        />
        <MobileMetricCard
          title="This Month"
          value={dashboardData?.contracts_this_month || 0}
          subtitle="New contracts"
          icon={TrendingUp}
          color="purple"
          loading={loading}
        />
        <MobileMetricCard
          title="Avg Time"
          value={`${dashboardData?.avg_completion_time || 0}d`}
          change={-8.2}
          icon={Clock}
          color="orange"
          trend="down"
          loading={loading}
        />
      </div>

      {/* Revenue Card - Full Width */}
      <MobileMetricCard
        title="Revenue This Month"
        value={`$${(dashboardData?.revenue_this_month || 0).toLocaleString()}`}
        change={15.3}
        icon={DollarSign}
        color="green"
        trend="up"
        size="large"
        loading={loading}
      />

      {/* Performance Rings */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Performance Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2">
            <MobilePerformanceRing 
              value={Math.round(dashboardData?.success_rate || 0)} 
              label="Success Rate"
              color="green"
            />
            <MobilePerformanceRing 
              value={Math.round((dashboardData?.client_satisfaction || 0) * 20)} 
              label="Satisfaction"
              color="blue"
            />
            <MobilePerformanceRing 
              value={Math.round(performanceMetrics?.renewal_rate || 0)} 
              label="Renewal Rate"
              color="purple"
            />
          </div>
        </CardContent>
      </Card>

      {/* Activity Trend - Mobile Optimized Chart */}
      <MobileChart title="Recent Activity" height={180}>
        <AreaChart data={dashboardData?.recent_activity || []}>
          <XAxis 
            dataKey="date" 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => new Date(value).getDate().toString()}
          />
          <YAxis hide />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px'
            }}
            formatter={(value, name) => [
              name === 'contracts' ? `${value} contracts` : `$${value}`,
              name === 'contracts' ? 'Contracts' : 'Revenue'
            ]}
          />
          <Area 
            type="monotone" 
            dataKey="contracts" 
            stroke="#3B82F6" 
            fill="#3B82F6" 
            fillOpacity={0.3}
            strokeWidth={2}
          />
        </AreaChart>
      </MobileChart>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Active</p>
              <p className="text-lg font-bold">{dashboardData?.active_contracts || 0}</p>
            </div>
            <Activity className="h-5 w-5 text-blue-600" />
          </div>
        </Card>
        
        <Card className="p-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-600">Satisfaction</p>
              <p className="text-lg font-bold">{dashboardData?.client_satisfaction || 0}/5</p>
            </div>
            <Users className="h-5 w-5 text-green-600" />
          </div>
        </Card>
      </div>
    </div>
  );

  // Performance Tab - Mobile Optimized
  const PerformanceTab = () => (
    <div className="space-y-4 p-4">
      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-2 gap-3">
        <MobileMetricCard
          title="Success Rate"
          value={`${performanceMetrics?.success_rate || 0}%`}
          icon={Target}
          color="green"
          loading={loading}
        />
        <MobileMetricCard
          title="Completion Time"
          value={`${performanceMetrics?.average_completion_time || 0}d`}
          icon={Clock}
          color="blue"
          loading={loading}
        />
      </div>

      {/* Performance Trends Chart */}
      <MobileChart title="Success Rate Trend" height={200}>
        <LineChart data={performanceMetrics?.performance_trends || []}>
          <XAxis 
            dataKey="date" 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10 }}
            tickFormatter={(value) => new Date(value).getDate().toString()}
          />
          <YAxis 
            domain={['dataMin - 5', 'dataMax + 5']}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10 }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="success_rate" 
            stroke="#10B981" 
            strokeWidth={3}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </MobileChart>

      {/* Performance Breakdown */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Performance Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span>Contract Success Rate</span>
              <span>{performanceMetrics?.success_rate || 0}%</span>
            </div>
            <Progress value={performanceMetrics?.success_rate || 0} className="h-2" />
          </div>
          
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span>Renewal Rate</span>
              <span>{performanceMetrics?.renewal_rate || 0}%</span>
            </div>
            <Progress value={performanceMetrics?.renewal_rate || 0} className="h-2" />
          </div>
          
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span>Client Satisfaction</span>
              <span>{((performanceMetrics?.client_satisfaction || 0) * 20)}%</span>
            </div>
            <Progress value={(performanceMetrics?.client_satisfaction || 0) * 20} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Efficiency Metrics */}
      <div className="grid grid-cols-1 gap-3">
        <MobileMetricCard
          title="Efficiency Improvement"
          value={`${performanceMetrics?.efficiency_improvement || 0}%`}
          change={5.2}
          icon={Zap}
          color="purple"
          trend="up"
          size="large"
          loading={loading}
        />
      </div>
    </div>
  );

  // Cost Analysis Tab - Mobile Optimized
  const CostAnalysisTab = () => (
    <div className="space-y-4 p-4">
      {/* Cost Savings Metrics */}
      <div className="grid grid-cols-2 gap-3">
        <MobileMetricCard
          title="Total Savings"
          value={`$${(costAnalysis?.total_savings || 0).toLocaleString()}`}
          icon={DollarSign}
          color="green"
          loading={loading}
        />
        <MobileMetricCard
          title="Time Saved"
          value={`${costAnalysis?.time_saved_hours || 0}h`}
          icon={Clock}
          color="blue"
          loading={loading}
        />
      </div>

      {/* ROI Card */}
      <Card className="bg-gradient-to-br from-green-50 to-blue-50 border-green-200">
        <CardContent className="p-4">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
              <span className="text-sm font-medium text-green-800">Return on Investment</span>
            </div>
            <div className="text-3xl font-bold text-green-600">
              {costAnalysis?.roi || 0}x
            </div>
            <p className="text-xs text-green-700 mt-1">
              {costAnalysis?.savings_percentage || 0}% cost reduction
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Cost Comparison */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Cost Comparison</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
            <span className="text-xs font-medium">Traditional Method</span>
            <span className="text-sm font-bold text-red-600">
              ${costAnalysis?.cost_per_contract_traditional || 0}
            </span>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
            <span className="text-xs font-medium">Automated Method</span>
            <span className="text-sm font-bold text-green-600">
              ${costAnalysis?.cost_per_contract_automation || 0}
            </span>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border-2 border-blue-200">
            <span className="text-xs font-medium">Savings per Contract</span>
            <span className="text-sm font-bold text-blue-600">
              ${(costAnalysis?.cost_per_contract_traditional || 0) - (costAnalysis?.cost_per_contract_automation || 0)}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Savings Breakdown Chart */}
      <MobileChart title="Savings Distribution" height={200}>
        <PieChart>
          <Pie
            data={[
              { name: 'Legal Fees', value: 45, fill: '#3B82F6' },
              { name: 'Time Savings', value: 35, fill: '#10B981' },
              { name: 'Admin Costs', value: 20, fill: '#F59E0B' }
            ]}
            cx="50%"
            cy="50%"
            innerRadius={30}
            outerRadius={70}
            paddingAngle={5}
            dataKey="value"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            labelLine={false}
            fontSize={10}
          >
            {[1, 2, 3].map((entry, index) => (
              <Cell key={`cell-${index}`} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '11px'
            }}
          />
        </PieChart>
      </MobileChart>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <MobileHeader />
      
      <div className="flex-1">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          {/* Mobile Tab Navigation */}
          <div className="bg-white border-b px-4 pt-3">
            <TabsList className="grid w-full grid-cols-3 h-10">
              <TabsTrigger value="overview" className="text-xs">Overview</TabsTrigger>
              <TabsTrigger value="performance" className="text-xs">Performance</TabsTrigger>
              <TabsTrigger value="costs" className="text-xs">Costs</TabsTrigger>
            </TabsList>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto pb-20">
            <TabsContent value="overview" className="mt-0">
              <OverviewTab />
            </TabsContent>
            
            <TabsContent value="performance" className="mt-0">
              <PerformanceTab />
            </TabsContent>
            
            <TabsContent value="costs" className="mt-0">
              <CostAnalysisTab />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
};

export default MobileAnalyticsDashboard;