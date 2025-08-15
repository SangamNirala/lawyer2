import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Globe, Scale, TrendingUp, AlertTriangle, FileText, Users } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MultiJurisdictionComparison = ({ query, currentResults }) => {
  const [selectedJurisdictions, setSelectedJurisdictions] = useState(['US', 'CA', 'UK', 'AU']);
  const [comparisonData, setComparisonData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeMetric, setActiveMetric] = useState('precedent_strength');
  const [recommendationEngine, setRecommendationEngine] = useState(null);
  const [availableJurisdictions] = useState([
    { code: 'US', name: 'United States', flag: '🇺🇸' },
    { code: 'CA', name: 'Canada', flag: '🇨🇦' },
    { code: 'UK', name: 'United Kingdom', flag: '🇬🇧' },
    { code: 'AU', name: 'Australia', flag: '🇦🇺' },
    { code: 'EU', name: 'European Union', flag: '🇪🇺' },
    { code: 'DE', name: 'Germany', flag: '🇩🇪' },
    { code: 'FR', name: 'France', flag: '🇫🇷' },
    { code: 'JP', name: 'Japan', flag: '🇯🇵' },
    { code: 'SG', name: 'Singapore', flag: '🇸🇬' },
    { code: 'IN', name: 'India', flag: '🇮🇳' }
  ]);

  useEffect(() => {
    if (query && selectedJurisdictions.length > 1) {
      performComparison();
    }
  }, [query, selectedJurisdictions]);

  const performComparison = async () => {
    if (!query) return;

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/multi-jurisdiction-search`, {
        query: query,
        jurisdictions: selectedJurisdictions,
        include_comparison_analysis: true,
        include_recommendations: true,
        comparison_metrics: ['precedent_strength', 'legal_certainty', 'enforcement_ease', 'cost_efficiency']
      });

      setComparisonData(response.data);
      if (response.data.recommendation_engine) {
        setRecommendationEngine(response.data.recommendation_engine);
      }

    } catch (error) {
      console.error('Error performing multi-jurisdiction comparison:', error);
      alert('Failed to perform comparison. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const addJurisdiction = (jurisdictionCode) => {
    if (!selectedJurisdictions.includes(jurisdictionCode)) {
      setSelectedJurisdictions([...selectedJurisdictions, jurisdictionCode]);
    }
  };

  const removeJurisdiction = (jurisdictionCode) => {
    if (selectedJurisdictions.length > 2) {
      setSelectedJurisdictions(selectedJurisdictions.filter(j => j !== jurisdictionCode));
    }
  };

  const getJurisdictionName = (code) => {
    const jurisdiction = availableJurisdictions.find(j => j.code === code);
    return jurisdiction ? `${jurisdiction.flag} ${jurisdiction.name}` : code;
  };

  const getJurisdictionColor = (code, index) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16', '#f97316'];
    return colors[index % colors.length];
  };

  const ComparisonChart = () => {
    if (!comparisonData || !comparisonData.jurisdiction_analysis) return null;

    const chartData = selectedJurisdictions.map((jurisdiction, index) => {
      const analysis = comparisonData.jurisdiction_analysis[jurisdiction];
      return {
        jurisdiction: getJurisdictionName(jurisdiction),
        precedent_strength: analysis?.precedent_strength || 0,
        legal_certainty: analysis?.legal_certainty || 0,
        enforcement_ease: analysis?.enforcement_ease || 0,
        cost_efficiency: analysis?.cost_efficiency || 0,
        overall_score: analysis?.overall_score || 0
      };
    });

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['precedent_strength', 'legal_certainty', 'enforcement_ease', 'cost_efficiency'].map((metric) => (
            <Button
              key={metric}
              variant={activeMetric === metric ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveMetric(metric)}
              className="justify-start"
            >
              {metric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </Button>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>
              {activeMetric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="jurisdiction" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar 
                  dataKey={activeMetric} 
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Radar Chart for Overall Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Multi-Dimensional Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={chartData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="jurisdiction" />
                <PolarRadiusAxis domain={[0, 100]} />
                <Radar 
                  name="Overall Score" 
                  dataKey="overall_score" 
                  stroke="#3b82f6" 
                  fill="#3b82f6" 
                  fillOpacity={0.1} 
                />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    );
  };

  const JurisdictionCard = ({ jurisdiction, analysis, index }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <span>{getJurisdictionName(jurisdiction)}</span>
            <Badge 
              variant="outline" 
              style={{ 
                borderColor: getJurisdictionColor(jurisdiction, index),
                color: getJurisdictionColor(jurisdiction, index)
              }}
            >
              Rank #{analysis.rank || index + 1}
            </Badge>
          </CardTitle>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => removeJurisdiction(jurisdiction)}
            disabled={selectedJurisdictions.length <= 2}
          >
            Remove
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">Overall Score</span>
              <span className="text-sm">{analysis.overall_score || 0}%</span>
            </div>
            <Progress value={analysis.overall_score || 0} className="w-full" />
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-gray-600">Precedent Strength</div>
              <div className="font-medium">{analysis.precedent_strength || 0}%</div>
            </div>
            <div>
              <div className="text-gray-600">Legal Certainty</div>
              <div className="font-medium">{analysis.legal_certainty || 0}%</div>
            </div>
            <div>
              <div className="text-gray-600">Enforcement Ease</div>
              <div className="font-medium">{analysis.enforcement_ease || 0}%</div>
            </div>
            <div>
              <div className="text-gray-600">Cost Efficiency</div>
              <div className="font-medium">{analysis.cost_efficiency || 0}%</div>
            </div>
          </div>
        </div>

        {analysis.key_differences && analysis.key_differences.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Key Differences:</h4>
            <ul className="space-y-1">
              {analysis.key_differences.slice(0, 3).map((diff, idx) => (
                <li key={idx} className="text-xs text-gray-700 pl-2 border-l-2 border-blue-200">
                  {diff}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis.notable_cases && analysis.notable_cases.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Notable Cases:</h4>
            <div className="space-y-1">
              {analysis.notable_cases.slice(0, 2).map((case_info, idx) => (
                <div key={idx} className="text-xs bg-gray-50 p-2 rounded">
                  <div className="font-medium">{case_info.case_name}</div>
                  <div className="text-gray-600">{case_info.summary}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );

  const RecommendationPanel = () => {
    if (!recommendationEngine) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            AI Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {recommendationEngine.best_jurisdiction && (
            <Alert>
              <TrendingUp className="h-4 w-4" />
              <AlertDescription>
                <strong>Recommended Jurisdiction:</strong> {getJurisdictionName(recommendationEngine.best_jurisdiction.code)}
                <br />
                <span className="text-sm text-gray-600">
                  {recommendationEngine.best_jurisdiction.reason}
                </span>
              </AlertDescription>
            </Alert>
          )}

          {recommendationEngine.risk_factors && recommendationEngine.risk_factors.length > 0 && (
            <div>
              <h4 className="font-medium flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4" />
                Risk Factors to Consider
              </h4>
              <div className="space-y-2">
                {recommendationEngine.risk_factors.map((risk, index) => (
                  <div key={index} className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <div className="font-medium text-orange-800">{risk.jurisdiction}</div>
                    <div className="text-sm text-orange-700">{risk.risk}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {recommendationEngine.strategic_considerations && (
            <div>
              <h4 className="font-medium flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4" />
                Strategic Considerations
              </h4>
              <ul className="space-y-1">
                {recommendationEngine.strategic_considerations.map((consideration, index) => (
                  <li key={index} className="text-sm text-gray-700 pl-3 border-l-2 border-blue-200">
                    {consideration}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Multi-Jurisdiction Comparison
              </CardTitle>
              <CardDescription>
                Compare legal positions across different jurisdictions
              </CardDescription>
            </div>
            <Button 
              onClick={performComparison}
              disabled={isLoading || selectedJurisdictions.length < 2}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                  Comparing...
                </>
              ) : (
                <>
                  <Scale className="h-4 w-4 mr-2" />
                  Compare
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Jurisdiction Selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium">Selected Jurisdictions ({selectedJurisdictions.length})</h4>
              <Select onValueChange={addJurisdiction}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Add jurisdiction..." />
                </SelectTrigger>
                <SelectContent>
                  {availableJurisdictions
                    .filter(j => !selectedJurisdictions.includes(j.code))
                    .map((jurisdiction) => (
                      <SelectItem key={jurisdiction.code} value={jurisdiction.code}>
                        {jurisdiction.flag} {jurisdiction.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-wrap gap-2">
              {selectedJurisdictions.map((jurisdiction, index) => (
                <Badge 
                  key={jurisdiction}
                  variant="outline"
                  className="flex items-center gap-1"
                  style={{ 
                    borderColor: getJurisdictionColor(jurisdiction, index),
                    color: getJurisdictionColor(jurisdiction, index)
                  }}
                >
                  {getJurisdictionName(jurisdiction)}
                  {selectedJurisdictions.length > 2 && (
                    <button 
                      onClick={() => removeJurisdiction(jurisdiction)}
                      className="ml-1 hover:bg-gray-200 rounded-full p-0.5"
                    >
                      ✕
                    </button>
                  )}
                </Badge>
              ))}
            </div>
          </div>

          {query && (
            <Alert>
              <FileText className="h-4 w-4" />
              <AlertDescription>
                Comparing: "{query}" across {selectedJurisdictions.length} jurisdictions
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {comparisonData && (
        <Tabs defaultValue="analysis" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="analysis">
              <Users className="h-4 w-4 mr-2" />
              Analysis
            </TabsTrigger>
            <TabsTrigger value="comparison">
              <BarChart className="h-4 w-4 mr-2" />
              Charts
            </TabsTrigger>
            <TabsTrigger value="recommendations">
              <TrendingUp className="h-4 w-4 mr-2" />
              Recommendations
            </TabsTrigger>
          </TabsList>

          <TabsContent value="analysis" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {selectedJurisdictions.map((jurisdiction, index) => {
                const analysis = comparisonData.jurisdiction_analysis?.[jurisdiction];
                return analysis ? (
                  <JurisdictionCard
                    key={jurisdiction}
                    jurisdiction={jurisdiction}
                    analysis={analysis}
                    index={index}
                  />
                ) : null;
              })}
            </div>
          </TabsContent>

          <TabsContent value="comparison" className="mt-6">
            <ComparisonChart />
          </TabsContent>

          <TabsContent value="recommendations" className="mt-6">
            <RecommendationPanel />
          </TabsContent>
        </Tabs>
      )}

      {!query && (
        <Alert>
          <Globe className="h-4 w-4" />
          <AlertDescription>
            Start a research query to enable multi-jurisdiction comparison analysis.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default MultiJurisdictionComparison;