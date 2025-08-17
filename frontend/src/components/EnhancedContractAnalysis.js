import React, { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { 
  Upload, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Download, 
  Eye,
  Compare,
  BarChart3,
  Shield,
  Clock,
  Users,
  MapPin,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

const EnhancedContractAnalysis = ({ sessionId, isVisible, onClose }) => {
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isComparing, setIsComparing] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const fileInputRef = useRef(null);

  if (!isVisible) return null;

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a PDF, DOCX, or TXT file');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    setIsUploading(true);
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', sessionId);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-agents/contract-negotiation/upload-document`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const analysisResult = await response.json();
      
      setUploadedDocuments(prev => [...prev, analysisResult]);
      setSelectedDocument(analysisResult);
      setActiveTab('analysis');
      
    } catch (error) {
      console.error('Document upload failed:', error);
      alert(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
      setIsAnalyzing(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleCompareDocuments = async () => {
    if (selectedDocuments.length !== 2) {
      alert('Please select exactly 2 documents to compare');
      return;
    }

    setIsComparing(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ai-agents/contract-negotiation/compare-documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          document1_id: selectedDocuments[0],
          document2_id: selectedDocuments[1]
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Comparison failed');
      }

      const comparisonData = await response.json();
      setComparisonResults(comparisonData);
      setActiveTab('comparison');
      
    } catch (error) {
      console.error('Document comparison failed:', error);
      alert(`Comparison failed: ${error.message}`);
    } finally {
      setIsComparing(false);
    }
  };

  const getRiskLevelColor = (riskScore) => {
    if (riskScore >= 0.8) return 'bg-red-500';
    if (riskScore >= 0.6) return 'bg-orange-500';
    if (riskScore >= 0.4) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getRiskLevelText = (riskScore) => {
    if (riskScore >= 0.8) return 'Critical';
    if (riskScore >= 0.6) return 'High';
    if (riskScore >= 0.4) return 'Medium';
    return 'Low';
  };

  const handleDocumentSelection = (documentId) => {
    setSelectedDocuments(prev => {
      if (prev.includes(documentId)) {
        return prev.filter(id => id !== documentId);
      } else if (prev.length < 2) {
        return [...prev, documentId];
      } else {
        return [prev[1], documentId]; // Replace first with new selection
      }
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-2">
            <FileText className="h-6 w-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Enhanced Contract Analysis</h2>
          </div>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="w-full justify-start p-6 pb-2">
              <TabsTrigger value="upload" className="flex items-center space-x-2">
                <Upload className="h-4 w-4" />
                <span>Upload & Analyze</span>
              </TabsTrigger>
              <TabsTrigger value="analysis" disabled={!selectedDocument} className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>Analysis Results</span>
              </TabsTrigger>
              <TabsTrigger value="comparison" className="flex items-center space-x-2">
                <Compare className="h-4 w-4" />
                <span>Document Comparison</span>
              </TabsTrigger>
            </TabsList>

            {/* Upload Tab */}
            <TabsContent value="upload" className="flex-1 p-6">
              <div className="space-y-6">
                {/* Upload Area */}
                <Card>
                  <CardHeader>
                    <CardTitle>Upload Contract Document</CardTitle>
                    <CardDescription>
                      Upload PDF, DOCX, or TXT files for comprehensive AI-powered analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                      <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                      <p className="text-lg font-medium text-gray-900 mb-2">
                        Drop your contract here or click to browse
                      </p>
                      <p className="text-sm text-gray-500 mb-4">
                        Supports PDF, DOCX, TXT files up to 10MB
                      </p>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.docx,.txt"
                        onChange={handleFileUpload}
                        className="hidden"
                        disabled={isUploading}
                      />
                      <Button 
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        {isUploading ? 'Uploading...' : 'Choose File'}
                      </Button>
                    </div>
                    
                    {isAnalyzing && (
                      <div className="mt-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                          <span className="text-sm text-gray-600">Analyzing document...</span>
                        </div>
                        <Progress value={45} className="w-full" />
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Uploaded Documents List */}
                {uploadedDocuments.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Analyzed Documents</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {uploadedDocuments.map((doc) => (
                          <div key={doc.document_id} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center space-x-3">
                              <FileText className="h-5 w-5 text-blue-600" />
                              <div>
                                <p className="font-medium">{doc.filename}</p>
                                <p className="text-sm text-gray-500">
                                  {doc.document_type} • Risk Score: {(doc.overall_risk_score * 100).toFixed(0)}%
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge variant={doc.overall_risk_score >= 0.6 ? "destructive" : "default"}>
                                {getRiskLevelText(doc.overall_risk_score)}
                              </Badge>
                              <Button 
                                size="sm" 
                                onClick={() => setSelectedDocument(doc)}
                                variant="outline"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>

            {/* Analysis Results Tab */}
            <TabsContent value="analysis" className="flex-1 p-6">
              {selectedDocument && (
                <ScrollArea className="h-full">
                  <div className="space-y-6">
                    {/* Document Overview */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <span>{selectedDocument.filename}</span>
                          <Badge 
                            variant={selectedDocument.overall_risk_score >= 0.6 ? "destructive" : "default"}
                            className="text-lg px-3 py-1"
                          >
                            {getRiskLevelText(selectedDocument.overall_risk_score)} Risk
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">{selectedDocument.analysis_summary.total_clauses}</div>
                            <div className="text-sm text-gray-500">Total Clauses</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-red-600">{selectedDocument.analysis_summary.high_risk_clauses}</div>
                            <div className="text-sm text-gray-500">High Risk</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-600">{selectedDocument.analysis_summary.word_count}</div>
                            <div className="text-sm text-gray-500">Words</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">{selectedDocument.recommendations.length}</div>
                            <div className="text-sm text-gray-500">Recommendations</div>
                          </div>
                        </div>

                        {/* Risk Score Visualization */}
                        <div className="mb-6">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">Overall Risk Score</span>
                            <span className="text-sm text-gray-500">{(selectedDocument.overall_risk_score * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3">
                            <div 
                              className={`h-3 rounded-full ${getRiskLevelColor(selectedDocument.overall_risk_score)}`}
                              style={{ width: `${selectedDocument.overall_risk_score * 100}%` }}
                            ></div>
                          </div>
                        </div>

                        {/* Document Metadata */}
                        {selectedDocument.analysis_summary.parties.length > 0 && (
                          <div className="flex items-center space-x-4 text-sm text-gray-600">
                            <div className="flex items-center space-x-1">
                              <Users className="h-4 w-4" />
                              <span>Parties: {selectedDocument.analysis_summary.parties.slice(0, 2).join(', ')}</span>
                            </div>
                            {selectedDocument.analysis_summary.jurisdiction && (
                              <div className="flex items-center space-x-1">
                                <MapPin className="h-4 w-4" />
                                <span>Jurisdiction: {selectedDocument.analysis_summary.jurisdiction}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Key Issues */}
                    {selectedDocument.key_issues.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <AlertTriangle className="h-5 w-5 text-red-600" />
                            <span>Key Issues Identified</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {selectedDocument.key_issues.slice(0, 5).map((issue, index) => (
                              <Alert key={index} variant="destructive">
                                <AlertTriangle className="h-4 w-4" />
                                <AlertDescription>{issue}</AlertDescription>
                              </Alert>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Recommendations */}
                    {selectedDocument.recommendations.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                            <span>Recommendations</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            {selectedDocument.recommendations.map((recommendation, index) => (
                              <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                                <span className="text-sm">{recommendation}</span>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Negotiation Priorities */}
                    {selectedDocument.negotiation_priorities.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <TrendingUp className="h-5 w-5 text-blue-600" />
                            <span>Negotiation Priorities</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {selectedDocument.negotiation_priorities.map((priority, index) => (
                              <div key={index} className="flex items-center space-x-3 p-2">
                                <Badge variant="outline" className="text-xs">
                                  Priority {index + 1}
                                </Badge>
                                <span className="text-sm">{priority}</span>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Missing Clauses */}
                    {selectedDocument.missing_clauses.length > 0 && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <Minus className="h-5 w-5 text-orange-600" />
                            <span>Missing Clauses</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            {selectedDocument.missing_clauses.map((clause, index) => (
                              <Alert key={index} variant="warning">
                                <AlertTriangle className="h-4 w-4" />
                                <AlertDescription>Consider adding: {clause}</AlertDescription>
                              </Alert>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                </ScrollArea>
              )}
            </TabsContent>

            {/* Comparison Tab */}
            <TabsContent value="comparison" className="flex-1 p-6">
              <div className="space-y-6">
                {/* Document Selection for Comparison */}
                <Card>
                  <CardHeader>
                    <CardTitle>Select Documents to Compare</CardTitle>
                    <CardDescription>
                      Choose exactly 2 documents for side-by-side analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4">
                      {uploadedDocuments.map((doc) => (
                        <div key={doc.document_id} 
                             className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                               selectedDocuments.includes(doc.document_id) 
                                 ? 'border-blue-500 bg-blue-50' 
                                 : 'border-gray-200 hover:border-gray-300'
                             }`}
                             onClick={() => handleDocumentSelection(doc.document_id)}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <input 
                                type="checkbox" 
                                checked={selectedDocuments.includes(doc.document_id)}
                                onChange={() => handleDocumentSelection(doc.document_id)}
                                className="rounded"
                              />
                              <FileText className="h-5 w-5 text-blue-600" />
                              <div>
                                <p className="font-medium">{doc.filename}</p>
                                <p className="text-sm text-gray-500">Risk Score: {(doc.overall_risk_score * 100).toFixed(0)}%</p>
                              </div>
                            </div>
                            <Badge variant={doc.overall_risk_score >= 0.6 ? "destructive" : "default"}>
                              {getRiskLevelText(doc.overall_risk_score)}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <Button 
                      onClick={handleCompareDocuments}
                      disabled={selectedDocuments.length !== 2 || isComparing}
                      className="w-full"
                    >
                      {isComparing ? 'Comparing...' : `Compare Documents (${selectedDocuments.length}/2 selected)`}
                    </Button>
                  </CardContent>
                </Card>

                {/* Comparison Results */}
                {comparisonResults && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Comparison Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ScrollArea className="h-96">
                        <div className="space-y-4">
                          {/* Recommendations */}
                          {comparisonResults.recommendations.length > 0 && (
                            <div>
                              <h4 className="font-medium mb-2">Key Recommendations</h4>
                              {comparisonResults.recommendations.map((rec, index) => (
                                <Alert key={index} className="mb-2">
                                  <CheckCircle className="h-4 w-4" />
                                  <AlertDescription>{rec}</AlertDescription>
                                </Alert>
                              ))}
                            </div>
                          )}

                          {/* Gap Analysis */}
                          {comparisonResults.gap_analysis.length > 0 && (
                            <div>
                              <h4 className="font-medium mb-2">Gap Analysis</h4>
                              {comparisonResults.gap_analysis.map((gap, index) => (
                                <Alert key={index} variant="warning" className="mb-2">
                                  <AlertTriangle className="h-4 w-4" />
                                  <AlertDescription>{gap}</AlertDescription>
                                </Alert>
                              ))}
                            </div>
                          )}

                          {/* Differences */}
                          {comparisonResults.differences.length > 0 && (
                            <div>
                              <h4 className="font-medium mb-2">Key Differences</h4>
                              {comparisonResults.differences.map((diff, index) => (
                                <div key={index} className="border rounded-lg p-3 mb-2">
                                  <h5 className="font-medium capitalize">{diff.section?.replace('_', ' ')}</h5>
                                  <p className="text-sm text-gray-600 mt-1">{diff.recommendation}</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </ScrollArea>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default EnhancedContractAnalysis;