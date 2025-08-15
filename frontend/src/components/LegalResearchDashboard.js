import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { Search, BookOpen, Scale, FileText, Network, AlertCircle, BarChart3 } from 'lucide-react';
import axios from 'axios';

import PrecedentSearchPanel from './PrecedentSearchPanel';
import CitationNetworkVisualization from './CitationNetworkVisualization';
import ResearchMemoEditor from './ResearchMemoEditor';
import ArgumentBuilder from './ArgumentBuilder';
import MultiJurisdictionComparison from './MultiJurisdictionComparison';
import ResearchQualityIndicator from './ResearchQualityIndicator';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LegalResearchDashboard = ({ onBack }) => {
  const [activeTab, setActiveTab] = useState('search');
  const [researchQuery, setResearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [researchHistory, setResearchHistory] = useState([]);
  const [currentResearchId, setCurrentResearchId] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);

  useEffect(() => {
    loadDashboardStats();
    loadResearchHistory();
  }, []);

  const loadDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/legal-research-engine/stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  };

  const loadResearchHistory = async () => {
    try {
      const response = await axios.get(`${API}/legal-research-engine/research-queries`);
      setResearchHistory(response.data.queries || []);
    } catch (error) {
      console.error('Error loading research history:', error);
    }
  };

  const handleResearch = async () => {
    if (!researchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/research`, {
        query: researchQuery,
        research_type: 'comprehensive',
        jurisdiction: 'US',
        include_citations: true,
        include_precedents: true,
        max_results: 50
      });
      
      setSearchResults(response.data);
      setCurrentResearchId(response.data.research_id);
      
      // Refresh history
      await loadResearchHistory();
      
      // Switch to results tab
      setActiveTab('results');
      
    } catch (error) {
      console.error('Error performing research:', error);
      alert('Failed to perform research. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleQuickSearch = (query) => {
    setResearchQuery(query);
    handleResearch();
  };

  const ResearchInterface = React.useMemo(() => (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Legal Research Query
        </CardTitle>
        <CardDescription>
          Enter your legal research question or topic to begin comprehensive analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Textarea
            placeholder="e.g., What are the precedents for contract breach in employment termination cases?"
            value={researchQuery}
            onChange={(e) => setResearchQuery(e.target.value)}
            className="min-h-24"
          />
          <div className="flex gap-2">
            <Button 
              onClick={handleResearch}
              disabled={isSearching || !researchQuery.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isSearching ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                  Researching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Start Research
                </>
              )}
            </Button>
            <Button variant="outline" onClick={() => setResearchQuery('')}>
              Clear
            </Button>
          </div>
        </div>

        {/* Quick Search Suggestions */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Quick Research Topics:</h4>
          <div className="flex flex-wrap gap-2">
            {[
              'Contract liability precedents',
              'Employment law updates',
              'Intellectual property disputes',
              'Corporate governance standards',
              'Data privacy regulations'
            ].map((topic) => (
              <Badge
                key={topic}
                variant="outline"
                className="cursor-pointer hover:bg-blue-50"
                onClick={() => handleQuickSearch(topic)}
              >
                {topic}
              </Badge>
            ))}
          </div>
        </div>

        {/* Dashboard Stats */}
        {dashboardStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {dashboardStats.total_research_queries || 0}
              </div>
              <div className="text-sm text-gray-600">Total Queries</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {dashboardStats.active_research_sessions || 0}
              </div>
              <div className="text-sm text-gray-600">Active Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {dashboardStats.precedents_analyzed || 0}
              </div>
              <div className="text-sm text-gray-600">Precedents Analyzed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {dashboardStats.avg_quality_score || 0}%
              </div>
              <div className="text-sm text-gray-600">Quality Score</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  ), [researchQuery, isSearching, dashboardStats, handleResearch]);

  const ResearchResults = React.useMemo(() => {
    if (!searchResults) {
      return (
        <Card>
          <CardContent className="py-12 text-center">
            <Search className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No research results yet. Start a research query to see results here.</p>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Research Results</span>
              <Badge variant="outline">
                {searchResults.total_results || 0} Results
              </Badge>
            </CardTitle>
            <CardDescription>
              Query: "{searchResults.query}" | Research ID: {currentResearchId}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {searchResults.quality_score && (
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Research Quality Score</span>
                  <span className="text-sm">{searchResults.quality_score}%</span>
                </div>
                <Progress value={searchResults.quality_score} className="w-full" />
              </div>
            )}

            {searchResults.summary && (
              <Alert className="mb-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Summary:</strong> {searchResults.summary}
                </AlertDescription>
              </Alert>
            )}

            {/* Key Findings */}
            {searchResults.key_findings && searchResults.key_findings.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold">Key Findings:</h4>
                {searchResults.key_findings.map((finding, index) => (
                  <Card key={index} className="border-l-4 border-l-blue-500">
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium">{finding.title}</h5>
                          <p className="text-sm text-gray-600 mt-1">{finding.description}</p>
                          {finding.relevance_score && (
                            <Badge variant="outline" className="mt-2">
                              {finding.relevance_score}% Relevant
                            </Badge>
                          )}
                        </div>
                        {finding.citation && (
                          <Badge variant="secondary" className="ml-2">
                            {finding.citation}
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }, [searchResults, currentResearchId]);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Legal Research Dashboard</h1>
          <p className="text-gray-600">Comprehensive legal research powered by AI and extensive legal databases</p>
        </div>
        <Button variant="outline" onClick={onBack}>
          <Scale className="h-4 w-4 mr-2" />
          Back to Main
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="search">
            <Search className="h-4 w-4 mr-2" />
            Search
          </TabsTrigger>
          <TabsTrigger value="results">
            <FileText className="h-4 w-4 mr-2" />
            Results
          </TabsTrigger>
          <TabsTrigger value="precedents">
            <BookOpen className="h-4 w-4 mr-2" />
            Precedents
          </TabsTrigger>
          <TabsTrigger value="citations">
            <Network className="h-4 w-4 mr-2" />
            Citations
          </TabsTrigger>
          <TabsTrigger value="memo">
            <FileText className="h-4 w-4 mr-2" />
            Memo
          </TabsTrigger>
          <TabsTrigger value="arguments">
            <Scale className="h-4 w-4 mr-2" />
            Arguments
          </TabsTrigger>
          <TabsTrigger value="comparison">
            <BarChart3 className="h-4 w-4 mr-2" />
            Compare
          </TabsTrigger>
        </TabsList>

        <TabsContent value="search" className="mt-6">
          <ResearchInterface />
        </TabsContent>

        <TabsContent value="results" className="mt-6">
          <ResearchResults />
        </TabsContent>

        <TabsContent value="precedents" className="mt-6">
          <PrecedentSearchPanel 
            currentQuery={researchQuery}
            onResultsUpdate={(results) => console.log('Precedent results:', results)}
          />
        </TabsContent>

        <TabsContent value="citations" className="mt-6">
          <CitationNetworkVisualization 
            researchId={currentResearchId}
            searchResults={searchResults}
          />
        </TabsContent>

        <TabsContent value="memo" className="mt-6">
          <ResearchMemoEditor 
            researchData={searchResults}
            researchId={currentResearchId}
          />
        </TabsContent>

        <TabsContent value="arguments" className="mt-6">
          <ArgumentBuilder 
            researchData={searchResults}
            precedents={searchResults?.precedents || []}
          />
        </TabsContent>

        <TabsContent value="comparison" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MultiJurisdictionComparison 
              query={researchQuery}
              currentResults={searchResults}
            />
            <ResearchQualityIndicator 
              researchData={searchResults}
              qualityScore={searchResults?.quality_score}
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default LegalResearchDashboard;