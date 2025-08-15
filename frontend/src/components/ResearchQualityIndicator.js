import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadialBarChart, RadialBar, PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import { 
  Award, TrendingUp, AlertCircle, CheckCircle, 
  Target, Zap, BarChart3, Info, Star 
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ResearchQualityIndicator = ({ researchData, qualityScore }) => {
  const [qualityMetrics, setQualityMetrics] = useState(null);
  const [qualityBreakdown, setQualityBreakdown] = useState(null);
  const [improvementSuggestions, setImprovementSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [qualityTrend, setQualityTrend] = useState(null);

  useEffect(() => {
    if (researchData) {
      assessResearchQuality();
    }
  }, [researchData]);

  const assessResearchQuality = async () => {
    if (!researchData) return;

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/quality-assessment`, {
        research_data: researchData,
        assessment_type: 'comprehensive',
        include_improvement_suggestions: true,
        include_benchmarking: true
      });

      setQualityMetrics(response.data.quality_metrics);
      setQualityBreakdown(response.data.quality_breakdown);
      setImprovementSuggestions(response.data.improvement_suggestions || []);
      setQualityTrend(response.data.quality_trend);

    } catch (error) {
      console.error('Error assessing research quality:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getQualityColor = (score) => {
    if (score >= 90) return '#22c55e'; // green
    if (score >= 80) return '#3b82f6'; // blue
    if (score >= 70) return '#f59e0b'; // yellow
    if (score >= 60) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const getQualityBadge = (score) => {
    if (score >= 90) return { variant: 'default', label: 'Excellent', icon: Award };
    if (score >= 80) return { variant: 'secondary', label: 'Good', icon: CheckCircle };
    if (score >= 70) return { variant: 'outline', label: 'Fair', icon: Target };
    if (score >= 60) return { variant: 'destructive', label: 'Poor', icon: AlertCircle };
    return { variant: 'destructive', label: 'Very Poor', icon: AlertCircle };
  };

  const QualityOverview = () => {
    const overallScore = qualityScore || qualityMetrics?.overall_score || 0;
    const badge = getQualityBadge(overallScore);
    const IconComponent = badge.icon;

    const radialData = [
      {
        name: 'Quality Score',
        value: overallScore,
        fill: getQualityColor(overallScore)
      }
    ];

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Research Quality Score
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold" style={{ color: getQualityColor(overallScore) }}>
                {overallScore}%
              </div>
              <Badge variant={badge.variant} className="mt-2">
                <IconComponent className="h-3 w-3 mr-1" />
                {badge.label}
              </Badge>
            </div>
            <div className="w-32 h-32">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart 
                  cx="50%" 
                  cy="50%" 
                  innerRadius="60%" 
                  outerRadius="90%" 
                  data={radialData}
                  startAngle={90}
                  endAngle={-270}
                >
                  <RadialBar 
                    dataKey="value" 
                    cornerRadius={10} 
                    fill={getQualityColor(overallScore)}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <Progress value={overallScore} className="w-full" />

          {qualityMetrics && (
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-gray-600">Source Credibility</div>
                <div className="font-medium">{qualityMetrics.source_credibility || 0}%</div>
              </div>
              <div>
                <div className="text-gray-600">Citation Strength</div>
                <div className="font-medium">{qualityMetrics.citation_strength || 0}%</div>
              </div>
              <div>
                <div className="text-gray-600">Content Depth</div>
                <div className="font-medium">{qualityMetrics.content_depth || 0}%</div>
              </div>
              <div>
                <div className="text-gray-600">Relevance Score</div>
                <div className="font-medium">{qualityMetrics.relevance_score || 0}%</div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  const QualityBreakdownChart = () => {
    if (!qualityBreakdown) return null;

    const breakdownData = Object.entries(qualityBreakdown).map(([key, value]) => ({
      name: key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      score: value.score || 0,
      weight: value.weight || 1,
      benchmark: value.benchmark || 75
    }));

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Quality Breakdown
          </CardTitle>
          <CardDescription>
            Detailed analysis of research quality components
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={breakdownData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  `${value}%`,
                  name === 'score' ? 'Current Score' : name === 'benchmark' ? 'Industry Benchmark' : name
                ]}
              />
              <Bar dataKey="score" fill="#3b82f6" name="Current Score" radius={[4, 4, 0, 0]} />
              <Bar dataKey="benchmark" fill="#94a3b8" name="Benchmark" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const QualityTrendChart = () => {
    if (!qualityTrend || !qualityTrend.historical_scores) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Quality Trend
          </CardTitle>
          <CardDescription>
            Research quality improvement over time
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={qualityTrend.historical_scores}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const ImprovementSuggestions = () => {
    if (improvementSuggestions.length === 0) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Improvement Suggestions
          </CardTitle>
          <CardDescription>
            AI-powered recommendations to enhance research quality
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {improvementSuggestions.map((suggestion, index) => (
              <div key={index} className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline">
                        {suggestion.category || 'General'}
                      </Badge>
                      {suggestion.priority && (
                        <Badge variant={
                          suggestion.priority === 'high' ? 'destructive' :
                          suggestion.priority === 'medium' ? 'default' : 'secondary'
                        }>
                          {suggestion.priority} priority
                        </Badge>
                      )}
                    </div>
                    <h4 className="font-medium mb-1">{suggestion.title}</h4>
                    <p className="text-sm text-gray-600">{suggestion.description}</p>
                    {suggestion.expected_improvement && (
                      <div className="mt-2 text-xs text-green-600">
                        Expected improvement: +{suggestion.expected_improvement}%
                      </div>
                    )}
                  </div>
                  {suggestion.impact_score && (
                    <div className="text-right">
                      <div className="text-sm font-medium">Impact</div>
                      <div className="text-lg font-bold text-blue-600">
                        {suggestion.impact_score}/10
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  const QualityInsights = () => {
    if (!qualityMetrics) return null;

    const insights = [
      {
        icon: CheckCircle,
        label: 'Sources Verified',
        value: qualityMetrics.verified_sources || 0,
        color: '#22c55e'
      },
      {
        icon: Star,
        label: 'Primary Sources',
        value: qualityMetrics.primary_sources || 0,
        color: '#3b82f6'
      },
      {
        icon: Target,
        label: 'Citation Accuracy',
        value: `${qualityMetrics.citation_accuracy || 0}%`,
        color: '#f59e0b'
      },
      {
        icon: TrendingUp,
        label: 'Recency Score',
        value: `${qualityMetrics.recency_score || 0}%`,
        color: '#8b5cf6'
      }
    ];

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {insights.map((insight, index) => {
          const IconComponent = insight.icon;
          return (
            <Card key={index}>
              <CardContent className="pt-4">
                <div className="flex items-center space-x-2">
                  <IconComponent 
                    className="h-4 w-4" 
                    style={{ color: insight.color }}
                  />
                  <div className="text-xs text-gray-600">{insight.label}</div>
                </div>
                <div className="text-xl font-bold mt-1" style={{ color: insight.color }}>
                  {insight.value}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin h-8 w-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Assessing research quality...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <QualityOverview />
      
      {qualityMetrics && <QualityInsights />}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QualityBreakdownChart />
        <QualityTrendChart />
      </div>
      
      <ImprovementSuggestions />

      {!researchData && !qualityScore && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Start a research query to enable quality assessment and improvement recommendations.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default ResearchQualityIndicator;