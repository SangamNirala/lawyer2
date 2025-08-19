import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Progress } from './ui/progress';
import { 
  AlertTriangle, 
  Shield, 
  AlertCircle, 
  CheckCircle, 
  X,
  FileText,
  Upload,
  BarChart3,
  Target,
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
  Eye,
  RefreshCw,
  Download,
  Plus,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Lightbulb,
  Warning
} from 'lucide-react';

// Risk level color mapping
const getRiskColor = (level) => {
  const colors = {
    very_low: 'text-green-600 bg-green-100 border-green-200',
    low: 'text-green-700 bg-green-50 border-green-300', 
    medium: 'text-yellow-700 bg-yellow-50 border-yellow-300',
    high: 'text-orange-700 bg-orange-50 border-orange-300',
    very_high: 'text-red-700 bg-red-50 border-red-300'
  };
  return colors[level] || colors.medium;
};

// Risk level display names
const getRiskLevelName = (level) => {
  const names = {
    very_low: 'Very Low',
    low: 'Low',
    medium: 'Medium', 
    high: 'High',
    very_high: 'Very High'
  };
  return names[level] || 'Medium';
};

// Category icons
const getCategoryIcon = (category) => {
  const icons = {
    legal: Shield,
    financial: BarChart3,
    operational: Target,
    compliance: CheckCircle
  };
  return icons[category] || Shield;
};

const RiskAssessmentDashboard = ({ 
  sessionId, 
  isVisible = true, 
  onClose,
  contractText = null,
  documentId = null 
}) => {
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [assessmentHistory, setAssessmentHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [contractInput, setContractInput] = useState('');
  const [contractType, setContractType] = useState('general');
  const [riskTolerance, setRiskTolerance] = useState('medium');
  const [expandedClauses, setExpandedClauses] = useState(new Set());
  const [expandedRisks, setExpandedRisks] = useState(new Set());
  const [showCreateAssessment, setShowCreateAssessment] = useState(true);

  // Load assessment history on component mount
  useEffect(() => {
    if (sessionId) {
      loadAssessmentHistory();
    }
  }, [sessionId]);

  // Auto-populate contract text if provided
  useEffect(() => {
    if (contractText) {
      setContractInput(contractText);
      setShowCreateAssessment(false);
    }
  }, [contractText]);

  const loadAssessmentHistory = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/ai-agents/contract-negotiation/risk-assessments/session/${sessionId}?limit=10`
      );
      
      if (response.ok) {
        const data = await response.json();
        setAssessmentHistory(data.assessments || []);
        
        // Auto-load latest assessment if available
        if (data.latest_assessment && !assessment) {
          setAssessment(data.latest_assessment);
          setShowCreateAssessment(false);
        }
      }
    } catch (error) {
      console.error('Failed to load assessment history:', error);
    }
  };

  const runRiskAssessment = async () => {
    if (!contractInput.trim() && !documentId) {
      setError('Please provide contract text or select a document');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        session_id: sessionId,
        contract_text: contractInput.trim() || null,
        document_id: documentId || null,
        contract_type: contractType,
        assessment_focus: ['legal', 'financial', 'operational', 'compliance'],
        risk_tolerance: riskTolerance,
        business_context: {
          urgency: 'medium',
          relationship_importance: 'high'
        }
      };

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/ai-agents/contract-negotiation/risk-assessment`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Assessment failed');
      }

      const assessmentResult = await response.json();
      setAssessment(assessmentResult);
      setShowCreateAssessment(false);
      
      // Refresh history
      await loadAssessmentHistory();
      
    } catch (error) {
      console.error('Risk assessment failed:', error);
      setError(error.message || 'Risk assessment failed');
    } finally {
      setLoading(false);
    }
  };

  const toggleClauseExpansion = (clauseId) => {
    const newExpanded = new Set(expandedClauses);
    if (newExpanded.has(clauseId)) {
      newExpanded.delete(clauseId);
    } else {
      newExpanded.add(clauseId);
    }
    setExpandedClauses(newExpanded);
  };

  const toggleRiskExpansion = (riskId) => {
    const newExpanded = new Set(expandedRisks);
    if (newExpanded.has(riskId)) {
      newExpanded.delete(riskId);
    } else {
      newExpanded.add(riskId);
    }
    setExpandedRisks(newExpanded);
  };

  // Calculate risk distribution for visualization
  const riskDistribution = useMemo(() => {
    if (!assessment?.dimensional_scores) return null;

    const scores = assessment.dimensional_scores;
    const categories = Object.keys(scores);
    
    return {
      categories: categories.map(cat => ({
        name: cat.charAt(0).toUpperCase() + cat.slice(1),
        key: cat,
        score: scores[cat].score,
        level: scores[cat].mitigation_priority,
        confidence: scores[cat].confidence,
        factors: scores[cat].key_factors.length
      })),
      overall: {
        score: assessment.overall_risk_score,
        level: assessment.risk_level,
        confidence: assessment.confidence_score
      }
    };
  }, [assessment]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b bg-gradient-to-r from-red-50 to-orange-50">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg mr-3">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Advanced Risk Assessment
              </h2>
              <p className="text-sm text-gray-600">
                Multi-dimensional automated contract risk analysis
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowCreateAssessment(!showCreateAssessment)}
            >
              {showCreateAssessment ? 'Hide Form' : 'New Assessment'}
            </Button>
            {onClose && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-100px)]">
          {/* Error Display */}
          {error && (
            <Alert className="mb-6 border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertTitle className="text-red-800">Assessment Error</AlertTitle>
              <AlertDescription className="text-red-700">{error}</AlertDescription>
            </Alert>
          )}

          {/* Create New Assessment Form */}
          {showCreateAssessment && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Plus className="w-5 h-5 mr-2" />
                  Create Risk Assessment
                </CardTitle>
                <CardDescription>
                  Analyze contract text or document for comprehensive risk evaluation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Contract Type</label>
                    <select
                      value={contractType}
                      onChange={(e) => setContractType(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="general">General Contract</option>
                      <option value="employment">Employment Agreement</option>
                      <option value="service">Service Agreement</option>
                      <option value="nda">Non-Disclosure Agreement</option>
                      <option value="partnership">Partnership Agreement</option>
                      <option value="licensing">Licensing Agreement</option>
                      <option value="supply">Supply Agreement</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Risk Tolerance</label>
                    <select
                      value={riskTolerance}
                      onChange={(e) => setRiskTolerance(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="conservative">Conservative</option>
                      <option value="medium">Medium</option>
                      <option value="aggressive">Aggressive</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Contract Text</label>
                  <Textarea
                    value={contractInput}
                    onChange={(e) => setContractInput(e.target.value)}
                    placeholder="Paste your contract text here for comprehensive risk analysis..."
                    rows={6}
                    className="w-full"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    Alternatively, you can analyze a previously uploaded document
                  </div>
                </div>

                <Button
                  onClick={runRiskAssessment}
                  disabled={loading || (!contractInput.trim() && !documentId)}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing Contract...
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4 mr-2" />
                      Run Risk Assessment
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Assessment Results */}
          {assessment && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="dimensions">Dimensions</TabsTrigger>
                <TabsTrigger value="clauses">Clause Analysis</TabsTrigger>
                <TabsTrigger value="mitigation">Mitigation Plan</TabsTrigger>
                <TabsTrigger value="history">History</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  {/* Overall Risk Score */}
                  <Card className={`border-2 ${getRiskColor(assessment.risk_level)}`}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <AlertTriangle className="w-8 h-8 text-current" />
                        <Badge variant="outline" className="text-current border-current">
                          {getRiskLevelName(assessment.risk_level)}
                        </Badge>
                      </div>
                      <div className="text-2xl font-bold">{assessment.overall_risk_score}/10</div>
                      <div className="text-sm opacity-80">Overall Risk Score</div>
                      <Progress 
                        value={assessment.overall_risk_score * 10} 
                        className="mt-2 h-2" 
                      />
                    </CardContent>
                  </Card>

                  {/* Confidence Score */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Target className="w-8 h-8 text-blue-500" />
                        <Badge variant="outline">
                          {(assessment.confidence_score * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <div className="text-2xl font-bold">
                        {(assessment.confidence_score * 100).toFixed(0)}%
                      </div>
                      <div className="text-sm text-gray-500">Analysis Confidence</div>
                      <Progress 
                        value={assessment.confidence_score * 100} 
                        className="mt-2 h-2" 
                      />
                    </CardContent>
                  </Card>

                  {/* High Priority Risks */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Warning className="w-8 h-8 text-orange-500" />
                        <Badge variant="destructive">
                          {assessment.high_priority_risks?.length || 0}
                        </Badge>
                      </div>
                      <div className="text-2xl font-bold">
                        {assessment.high_priority_risks?.length || 0}
                      </div>
                      <div className="text-sm text-gray-500">Critical Issues</div>
                    </CardContent>
                  </Card>

                  {/* Processing Time */}
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Clock className="w-8 h-8 text-green-500" />
                        <Badge variant="outline">
                          {assessment.processing_time_seconds?.toFixed(1)}s
                        </Badge>
                      </div>
                      <div className="text-2xl font-bold">
                        {assessment.processing_time_seconds?.toFixed(1)}s
                      </div>
                      <div className="text-sm text-gray-500">Analysis Time</div>
                    </CardContent>
                  </Card>
                </div>

                {/* Red Flags Alert */}
                {assessment.red_flags?.length > 0 && (
                  <Alert className="mb-6 border-red-200 bg-red-50">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <AlertTitle className="text-red-800">Critical Red Flags</AlertTitle>
                    <AlertDescription className="text-red-700">
                      <div className="mt-2 space-y-1">
                        {assessment.red_flags.map((flag, index) => (
                          <div key={index} className="flex items-start">
                            <div className="w-2 h-2 bg-red-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                            <span>{flag}</span>
                          </div>
                        ))}
                      </div>
                    </AlertDescription>
                  </Alert>
                )}

                {/* Dimensional Risk Breakdown */}
                {riskDistribution && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Risk Dimension Breakdown</CardTitle>
                      <CardDescription>
                        Risk analysis across legal, financial, operational, and compliance dimensions
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {riskDistribution.categories.map((category) => {
                          const Icon = getCategoryIcon(category.key);
                          const riskLevel = category.score >= 8 ? 'very_high' : 
                                          category.score >= 6 ? 'high' : 
                                          category.score >= 4 ? 'medium' : 
                                          category.score >= 2 ? 'low' : 'very_low';
                          
                          return (
                            <div key={category.key} className="flex items-center justify-between p-3 border rounded-lg">
                              <div className="flex items-center">
                                <Icon className="w-5 h-5 mr-3 text-gray-600" />
                                <div>
                                  <div className="font-medium">{category.name} Risk</div>
                                  <div className="text-sm text-gray-500">
                                    {category.factors} risk factors identified
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <div className="text-right">
                                  <div className="font-bold text-lg">
                                    {category.score.toFixed(1)}/10
                                  </div>
                                  <Badge className={getRiskColor(riskLevel)}>
                                    {getRiskLevelName(riskLevel)}
                                  </Badge>
                                </div>
                                <Progress
                                  value={category.score * 10}
                                  className="w-24 h-2"
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Dimensions Tab */}
              <TabsContent value="dimensions">
                <div className="space-y-6">
                  {assessment.dimensional_scores && Object.entries(assessment.dimensional_scores).map(([categoryKey, scoreData]) => {
                    const Icon = getCategoryIcon(categoryKey);
                    const riskLevel = scoreData.score >= 8 ? 'very_high' : 
                                    scoreData.score >= 6 ? 'high' : 
                                    scoreData.score >= 4 ? 'medium' : 
                                    scoreData.score >= 2 ? 'low' : 'very_low';
                    
                    return (
                      <Card key={categoryKey} className={`border-l-4 ${getRiskColor(riskLevel).split(' ')[2]}`}>
                        <CardHeader>
                          <CardTitle className="flex items-center">
                            <Icon className="w-5 h-5 mr-2" />
                            {categoryKey.charAt(0).toUpperCase() + categoryKey.slice(1)} Risk Analysis
                          </CardTitle>
                          <CardDescription>
                            Detailed analysis of {categoryKey} risk factors and impact assessment
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div className="text-center p-4 bg-gray-50 rounded-lg">
                              <div className="text-2xl font-bold text-gray-900">
                                {scoreData.score.toFixed(1)}/10
                              </div>
                              <div className="text-sm text-gray-500">Risk Score</div>
                            </div>
                            <div className="text-center p-4 bg-blue-50 rounded-lg">
                              <div className="text-2xl font-bold text-blue-600">
                                {(scoreData.confidence * 100).toFixed(0)}%
                              </div>
                              <div className="text-sm text-gray-500">Confidence</div>
                            </div>
                            <div className="text-center p-4 rounded-lg" 
                                 style={{background: `linear-gradient(135deg, ${getRiskColor(riskLevel).includes('red') ? '#fee2e2' : getRiskColor(riskLevel).includes('orange') ? '#fed7aa' : getRiskColor(riskLevel).includes('yellow') ? '#fef3c7' : '#dcfce7'})`}}>
                              <Badge className={getRiskColor(riskLevel)}>
                                {scoreData.mitigation_priority.toUpperCase()}
                              </Badge>
                              <div className="text-sm text-gray-500 mt-1">Priority Level</div>
                            </div>
                          </div>

                          {scoreData.key_factors?.length > 0 && (
                            <div className="mb-4">
                              <h4 className="font-semibold mb-2">Key Risk Factors:</h4>
                              <div className="space-y-2">
                                {scoreData.key_factors.map((factor, index) => (
                                  <div key={index} className="flex items-start p-2 bg-gray-50 rounded">
                                    <div className="w-2 h-2 bg-orange-400 rounded-full mt-2 mr-2 flex-shrink-0" />
                                    <span className="text-sm">{factor}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {scoreData.impact_areas?.length > 0 && (
                            <div>
                              <h4 className="font-semibold mb-2">Impact Areas:</h4>
                              <div className="flex flex-wrap gap-2">
                                {scoreData.impact_areas.map((area, index) => (
                                  <Badge key={index} variant="secondary">
                                    {area}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>

              {/* Clause Analysis Tab */}
              <TabsContent value="clauses">
                <div className="space-y-4">
                  {assessment.clause_analyses?.map((clause) => {
                    const isExpanded = expandedClauses.has(clause.clause_id);
                    const riskLevel = clause.overall_clause_risk >= 8 ? 'very_high' : 
                                    clause.overall_clause_risk >= 6 ? 'high' : 
                                    clause.overall_clause_risk >= 4 ? 'medium' : 
                                    clause.overall_clause_risk >= 2 ? 'low' : 'very_low';
                    
                    return (
                      <Card key={clause.clause_id} className={`border-l-4 ${getRiskColor(riskLevel).split(' ')[2]}`}>
                        <CardHeader className="cursor-pointer" onClick={() => toggleClauseExpansion(clause.clause_id)}>
                          <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center text-base">
                              <FileText className="w-4 h-4 mr-2" />
                              {clause.clause_type.replace('_', ' ').toUpperCase()} Clause
                            </CardTitle>
                            <div className="flex items-center space-x-2">
                              <Badge className={getRiskColor(riskLevel)}>
                                Risk: {clause.overall_clause_risk.toFixed(1)}/10
                              </Badge>
                              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            </div>
                          </div>
                          <CardDescription>
                            Primary risk category: {clause.primary_risk_category.toUpperCase()}
                            {clause.risk_factors?.length > 0 && ` • ${clause.risk_factors.length} risk factors identified`}
                          </CardDescription>
                        </CardHeader>
                        
                        {isExpanded && (
                          <CardContent>
                            {/* Clause Text */}
                            <div className="mb-4">
                              <h4 className="font-semibold mb-2">Clause Text:</h4>
                              <div className="p-3 bg-gray-50 rounded border text-sm">
                                {clause.clause_text}
                              </div>
                            </div>

                            {/* Risk Factors */}
                            {clause.risk_factors?.length > 0 && (
                              <div className="mb-4">
                                <h4 className="font-semibold mb-2">Risk Factors:</h4>
                                <div className="space-y-3">
                                  {clause.risk_factors.map((risk) => {
                                    const riskExpanded = expandedRisks.has(risk.factor_id);
                                    const factorRiskLevel = risk.risk_score >= 8 ? 'very_high' : 
                                                          risk.risk_score >= 6 ? 'high' : 
                                                          risk.risk_score >= 4 ? 'medium' : 
                                                          risk.risk_score >= 2 ? 'low' : 'very_low';

                                    return (
                                      <div key={risk.factor_id} className="border rounded p-3">
                                        <div 
                                          className="flex items-center justify-between cursor-pointer"
                                          onClick={() => toggleRiskExpansion(risk.factor_id)}
                                        >
                                          <div className="flex items-center">
                                            <div className={`p-1 rounded mr-2 ${getRiskColor(factorRiskLevel)}`}>
                                              <AlertCircle className="w-3 h-3" />
                                            </div>
                                            <span className="text-sm font-medium">{risk.description}</span>
                                          </div>
                                          <div className="flex items-center space-x-2">
                                            <Badge variant="outline" className="text-xs">
                                              {risk.risk_score.toFixed(1)}/10
                                            </Badge>
                                            {riskExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                          </div>
                                        </div>
                                        
                                        {riskExpanded && (
                                          <div className="mt-3 pl-6 space-y-2">
                                            <div className="grid grid-cols-2 gap-4 text-xs">
                                              <div>
                                                <span className="font-medium">Impact:</span> {risk.impact_score}/10
                                              </div>
                                              <div>
                                                <span className="font-medium">Probability:</span> {risk.probability_score}/10
                                              </div>
                                            </div>
                                            {risk.mitigation_suggestions?.length > 0 && (
                                              <div>
                                                <div className="font-medium text-xs mb-1">Mitigation Suggestions:</div>
                                                <div className="space-y-1">
                                                  {risk.mitigation_suggestions.map((suggestion, index) => (
                                                    <div key={index} className="flex items-start text-xs">
                                                      <Lightbulb className="w-3 h-3 mr-1 text-yellow-500 mt-0.5 flex-shrink-0" />
                                                      <span>{suggestion}</span>
                                                    </div>
                                                  ))}
                                                </div>
                                              </div>
                                            )}
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}

                            {/* Recommendations */}
                            {clause.recommendations?.length > 0 && (
                              <div className="mb-4">
                                <h4 className="font-semibold mb-2">Recommendations:</h4>
                                <div className="space-y-2">
                                  {clause.recommendations.map((rec, index) => (
                                    <div key={index} className="flex items-start p-2 bg-blue-50 rounded">
                                      <CheckCircle className="w-4 h-4 mr-2 text-blue-500 mt-0.5 flex-shrink-0" />
                                      <span className="text-sm">{rec}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Alternative Language */}
                            {clause.alternative_language && (
                              <div>
                                <h4 className="font-semibold mb-2">Suggested Alternative Language:</h4>
                                <div className="p-3 bg-green-50 border border-green-200 rounded text-sm">
                                  {clause.alternative_language}
                                </div>
                              </div>
                            )}
                          </CardContent>
                        )}
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>

              {/* Mitigation Plan Tab */}
              <TabsContent value="mitigation">
                <div className="space-y-6">
                  {/* Negotiation Priorities */}
                  {assessment.negotiation_priorities?.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <Target className="w-5 h-5 mr-2" />
                          Negotiation Priorities
                        </CardTitle>
                        <CardDescription>
                          Key areas to focus on during contract negotiations
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {assessment.negotiation_priorities.map((priority, index) => (
                            <div key={index} className="flex items-start p-3 border rounded-lg">
                              <div className="flex items-center justify-center w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full mr-3 mt-0.5">
                                {index + 1}
                              </div>
                              <span className="text-sm">{priority}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Risk Mitigation Plan */}
                  {assessment.risk_mitigation_plan?.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center">
                          <Shield className="w-5 h-5 mr-2" />
                          Risk Mitigation Action Plan
                        </CardTitle>
                        <CardDescription>
                          Structured plan for addressing identified risks
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {assessment.risk_mitigation_plan.map((item, index) => (
                            <div key={index} className="border rounded-lg p-4">
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex items-start">
                                  <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-3 text-white text-sm font-bold ${
                                    item.timeline === 'immediate' ? 'bg-red-500' : 
                                    item.timeline === 'short_term' ? 'bg-orange-500' : 'bg-blue-500'
                                  }`}>
                                    {item.priority || index + 1}
                                  </div>
                                  <div>
                                    <div className="font-semibold">{item.risk_description}</div>
                                    <div className="text-sm text-gray-500">
                                      Category: {item.category?.toUpperCase()} • 
                                      Risk Score: {item.risk_score?.toFixed(1)}/10 • 
                                      Timeline: {item.timeline?.replace('_', ' ').toUpperCase()}
                                    </div>
                                  </div>
                                </div>
                                <Badge variant={
                                  item.timeline === 'immediate' ? 'destructive' : 
                                  item.timeline === 'short_term' ? 'secondary' : 'outline'
                                }>
                                  {item.timeline?.replace('_', ' ').toUpperCase()}
                                </Badge>
                              </div>
                              
                              {item.mitigation_actions?.length > 0 && (
                                <div className="mb-3">
                                  <div className="font-medium text-sm mb-2">Mitigation Actions:</div>
                                  <div className="space-y-1">
                                    {item.mitigation_actions.map((action, actionIndex) => (
                                      <div key={actionIndex} className="flex items-start text-sm">
                                        <CheckCircle className="w-4 h-4 mr-2 text-green-500 mt-0.5 flex-shrink-0" />
                                        <span>{action}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}

                              <div className="flex items-center justify-between text-xs text-gray-500">
                                <span>Responsible: {item.responsible_party?.replace('_', ' ').toUpperCase()}</span>
                                {item.success_metrics?.length > 0 && (
                                  <span>Success Metric: {item.success_metrics[0]}</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* History Tab */}
              <TabsContent value="history">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Clock className="w-5 h-5 mr-2" />
                      Assessment History
                    </CardTitle>
                    <CardDescription>
                      Previous risk assessments for this session
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {assessmentHistory.length > 0 ? (
                      <div className="space-y-3">
                        {assessmentHistory.map((hist, index) => {
                          const histRiskLevel = hist.risk_level;
                          return (
                            <div key={hist.assessment_id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                              <div className="flex items-center">
                                <div className={`p-2 rounded mr-3 ${getRiskColor(histRiskLevel)}`}>
                                  <AlertTriangle className="w-4 h-4" />
                                </div>
                                <div>
                                  <div className="font-medium">
                                    Risk Assessment #{assessmentHistory.length - index}
                                  </div>
                                  <div className="text-sm text-gray-500">
                                    {new Date(hist.created_at).toLocaleString()} • 
                                    Contract: {hist.contract_type}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center space-x-3">
                                <div className="text-right">
                                  <div className="font-bold">{hist.overall_risk_score}/10</div>
                                  <Badge className={getRiskColor(histRiskLevel)}>
                                    {getRiskLevelName(histRiskLevel)}
                                  </Badge>
                                </div>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => setAssessment(hist)}
                                >
                                  <Eye className="w-3 h-3 mr-1" />
                                  View
                                </Button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="text-center text-gray-500 py-8">
                        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p>No previous assessments found for this session</p>
                        <p className="text-sm">Create your first assessment to see history here</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          )}

          {/* No Assessment State */}
          {!assessment && !showCreateAssessment && (
            <Card>
              <CardContent className="text-center py-12">
                <AlertTriangle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-semibold mb-2">No Risk Assessment Available</h3>
                <p className="text-gray-500 mb-4">
                  Create a new risk assessment to analyze contract risks and get mitigation recommendations
                </p>
                <Button onClick={() => setShowCreateAssessment(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Risk Assessment
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentDashboard;