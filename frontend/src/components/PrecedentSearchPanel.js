import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import { Search, BookOpen, Filter, Star, Calendar, Scale, ExternalLink } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PrecedentSearchPanel = ({ currentQuery, onResultsUpdate }) => {
  const [searchQuery, setSearchQuery] = useState(currentQuery || '');
  const [precedentResults, setPrecedentResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [filters, setFilters] = useState({
    jurisdiction: 'all',
    court_level: 'all',
    date_range: 'all',
    legal_domain: 'all',
    precedent_strength: 'all'
  });
  const [searchSuggestions, setSearchSuggestions] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [searchMetrics, setSearchMetrics] = useState(null);

  useEffect(() => {
    if (currentQuery) {
      setSearchQuery(currentQuery);
      handlePrecedentSearch();
    }
  }, [currentQuery]);

  const handlePrecedentSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/precedent-search`, {
        query: searchQuery,
        filters: filters,
        include_analytics: true,
        max_results: 50,
        include_summaries: true
      });
      
      setPrecedentResults(response.data.precedents || []);
      setTotalResults(response.data.total_count || 0);
      setSearchMetrics(response.data.search_metrics);
      
      // Generate search suggestions
      if (response.data.suggestions) {
        setSearchSuggestions(response.data.suggestions);
      }
      
      if (onResultsUpdate) {
        onResultsUpdate(response.data);
      }
      
    } catch (error) {
      console.error('Error searching precedents:', error);
      alert('Failed to search precedents. Please try again.');
    } finally {
      setIsSearching(false);
    }
  }, [searchQuery, filters, onResultsUpdate]);

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      jurisdiction: 'all',
      court_level: 'all',
      date_range: 'all',
      legal_domain: 'all',
      precedent_strength: 'all'
    });
  };

  const PrecedentCard = ({ precedent, index }) => (
    <Card key={index} className="hover:shadow-md transition-shadow">
      <CardContent className="pt-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="font-semibold text-lg">{precedent.case_name}</h4>
              <p className="text-sm text-gray-600">{precedent.court} | {precedent.date}</p>
            </div>
            <div className="flex items-center space-x-2">
              {precedent.precedent_strength && (
                <Badge variant={
                  precedent.precedent_strength >= 8 ? 'default' : 
                  precedent.precedent_strength >= 6 ? 'secondary' : 'outline'
                }>
                  <Star className="h-3 w-3 mr-1" />
                  {precedent.precedent_strength}/10
                </Badge>
              )}
              {precedent.relevance_score && (
                <Badge variant="outline">
                  {precedent.relevance_score}% Match
                </Badge>
              )}
            </div>
          </div>

          {precedent.summary && (
            <p className="text-sm">{precedent.summary}</p>
          )}

          {precedent.key_holdings && precedent.key_holdings.length > 0 && (
            <div>
              <h5 className="text-sm font-medium mb-2">Key Holdings:</h5>
              <div className="space-y-1">
                {precedent.key_holdings.slice(0, 3).map((holding, idx) => (
                  <div key={idx} className="text-sm text-gray-700 pl-3 border-l-2 border-blue-200">
                    {holding}
                  </div>
                ))}
              </div>
            </div>
          )}

          {precedent.legal_principles && precedent.legal_principles.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {precedent.legal_principles.slice(0, 4).map((principle, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {principle}
                </Badge>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>{precedent.citation}</span>
              {precedent.jurisdiction && <span>{precedent.jurisdiction}</span>}
            </div>
            <div className="flex items-center space-x-2">
              <Button size="sm" variant="outline">
                <BookOpen className="h-3 w-3 mr-1" />
                Read Full
              </Button>
              <Button size="sm" variant="ghost">
                <ExternalLink className="h-3 w-3 mr-1" />
                Source
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Search Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Precedent Search
          </CardTitle>
          <CardDescription>
            Search for relevant legal precedents and case law
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter legal issue, case name, or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handlePrecedentSearch()}
              className="flex-1"
            />
            <Button 
              onClick={handlePrecedentSearch}
              disabled={isSearching || !searchQuery.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {isSearching ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </>
              )}
            </Button>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="text-xs font-medium mb-1 block">Jurisdiction</label>
              <Select value={filters.jurisdiction} onValueChange={(value) => handleFilterChange('jurisdiction', value)}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Jurisdictions</SelectItem>
                  <SelectItem value="federal">Federal</SelectItem>
                  <SelectItem value="california">California</SelectItem>
                  <SelectItem value="new-york">New York</SelectItem>
                  <SelectItem value="texas">Texas</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-xs font-medium mb-1 block">Court Level</label>
              <Select value={filters.court_level} onValueChange={(value) => handleFilterChange('court_level', value)}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Courts</SelectItem>
                  <SelectItem value="supreme">Supreme Court</SelectItem>
                  <SelectItem value="appellate">Appellate</SelectItem>
                  <SelectItem value="district">District</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-xs font-medium mb-1 block">Date Range</label>
              <Select value={filters.date_range} onValueChange={(value) => handleFilterChange('date_range', value)}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Dates</SelectItem>
                  <SelectItem value="recent">Last 5 Years</SelectItem>
                  <SelectItem value="decade">Last 10 Years</SelectItem>
                  <SelectItem value="classic">Before 2000</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-xs font-medium mb-1 block">Legal Domain</label>
              <Select value={filters.legal_domain} onValueChange={(value) => handleFilterChange('legal_domain', value)}>
                <SelectTrigger className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Domains</SelectItem>
                  <SelectItem value="contract">Contract Law</SelectItem>
                  <SelectItem value="employment">Employment</SelectItem>
                  <SelectItem value="corporate">Corporate</SelectItem>
                  <SelectItem value="intellectual">IP Law</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button size="sm" variant="outline" onClick={clearFilters}>
                <Filter className="h-3 w-3 mr-1" />
                Clear
              </Button>
            </div>
          </div>

          {/* Search Suggestions */}
          {searchSuggestions.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Suggested Searches:</h4>
              <div className="flex flex-wrap gap-2">
                {searchSuggestions.map((suggestion, index) => (
                  <Badge
                    key={index}
                    variant="outline"
                    className="cursor-pointer hover:bg-blue-50"
                    onClick={() => setSearchQuery(suggestion)}
                  >
                    {suggestion}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search Metrics */}
      {searchMetrics && (
        <Card>
          <CardContent className="pt-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-xl font-bold text-blue-600">{totalResults}</div>
                <div className="text-xs text-gray-600">Total Results</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-green-600">
                  {searchMetrics.avg_relevance || 0}%
                </div>
                <div className="text-xs text-gray-600">Avg Relevance</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-purple-600">
                  {searchMetrics.search_time || 0}s
                </div>
                <div className="text-xs text-gray-600">Search Time</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-bold text-orange-600">
                  {searchMetrics.confidence_score || 0}%
                </div>
                <div className="text-xs text-gray-600">Confidence</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      <div className="space-y-4">
        {precedentResults.length > 0 ? (
          <>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                Precedent Results ({precedentResults.length})
              </h3>
              <Badge variant="outline">
                Sorted by Relevance
              </Badge>
            </div>
            {precedentResults.map((precedent, index) => (
              <PrecedentCard key={index} precedent={precedent} index={index} />
            ))}
          </>
        ) : (
          !isSearching && searchQuery && (
            <Card>
              <CardContent className="py-12 text-center">
                <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">No precedents found for your search query.</p>
                <p className="text-sm text-gray-500 mt-2">Try adjusting your search terms or filters.</p>
              </CardContent>
            </Card>
          )
        )}
      </div>
    </div>
  );
};

export default PrecedentSearchPanel;