import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Network, Maximize2, Minimize2, RefreshCw, Download, Info } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CitationNetworkVisualization = ({ researchId, searchResults }) => {
  const svgRef = useRef();
  const [citationData, setCitationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [networkStats, setNetworkStats] = useState(null);
  const [viewMode, setViewMode] = useState('authority'); // authority, temporal, subject
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  useEffect(() => {
    if (researchId || searchResults) {
      loadCitationNetwork();
    }
  }, [researchId, searchResults, viewMode]);

  const loadCitationNetwork = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/citation-analysis`, {
        research_id: researchId,
        search_results: searchResults,
        analysis_type: 'network_visualization',
        include_authority_scores: true,
        include_temporal_analysis: true,
        max_nodes: 100
      });
      
      setCitationData(response.data);
      setNetworkStats(response.data.network_stats);
      
      // Render the network
      renderNetwork(response.data);
      
    } catch (error) {
      console.error('Error loading citation network:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderNetwork = (data) => {
    if (!data || !data.nodes || !data.links) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = isFullscreen ? window.innerWidth - 100 : 800;
    const height = isFullscreen ? window.innerHeight - 200 : 500;

    svg.attr('width', width).attr('height', height);

    // Create zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
        setZoomLevel(event.transform.k);
      });

    svg.call(zoom);

    const container = svg.append('g');

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => getNodeRadius(d) + 5));

    // Create links
    const links = container.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', d => getLinkColor(d))
      .attr('stroke-width', d => Math.sqrt(d.citation_count || 1) * 2)
      .attr('stroke-opacity', 0.6);

    // Create nodes
    const nodes = container.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', d => getNodeRadius(d))
      .attr('fill', d => getNodeColor(d))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .call(d3.drag()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded))
      .on('click', (event, d) => {
        setSelectedNode(d);
        highlightConnectedNodes(d);
      })
      .on('mouseover', (event, d) => {
        showTooltip(event, d);
      })
      .on('mouseout', hideTooltip);

    // Add labels
    const labels = container.append('g')
      .attr('class', 'labels')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .text(d => truncateText(d.case_name || d.title, 20))
      .attr('font-size', '10px')
      .attr('fill', '#333')
      .attr('text-anchor', 'middle')
      .attr('dy', d => getNodeRadius(d) + 15)
      .style('pointer-events', 'none');

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      nodes
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      labels
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    // Drag functions
    function dragStarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragEnded(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  const getNodeRadius = (node) => {
    switch (viewMode) {
      case 'authority':
        return Math.max(8, Math.min(30, (node.authority_score || 0) * 30));
      case 'temporal':
        const age = new Date().getFullYear() - (node.year || new Date().getFullYear());
        return Math.max(8, Math.min(30, 30 - (age * 0.5)));
      default:
        return 15;
    }
  };

  const getNodeColor = (node) => {
    switch (viewMode) {
      case 'authority':
        const score = node.authority_score || 0;
        return score > 0.8 ? '#dc2626' : score > 0.6 ? '#f59e0b' : score > 0.4 ? '#10b981' : '#6b7280';
      case 'temporal':
        const year = node.year || new Date().getFullYear();
        const age = new Date().getFullYear() - year;
        return age < 5 ? '#3b82f6' : age < 15 ? '#10b981' : age < 30 ? '#f59e0b' : '#6b7280';
      case 'subject':
        const subjects = {
          'Contract Law': '#3b82f6',
          'Employment Law': '#10b981',
          'Corporate Law': '#f59e0b',
          'IP Law': '#8b5cf6',
          'default': '#6b7280'
        };
        return subjects[node.legal_domain] || subjects.default;
      default:
        return '#6b7280';
    }
  };

  const getLinkColor = (link) => {
    const strength = link.citation_strength || 0;
    return strength > 0.7 ? '#dc2626' : strength > 0.4 ? '#f59e0b' : '#94a3b8';
  };

  const truncateText = (text, maxLength) => {
    return text && text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const highlightConnectedNodes = (targetNode) => {
    const svg = d3.select(svgRef.current);
    
    // Reset all nodes
    svg.selectAll('circle').attr('opacity', 0.3);
    svg.selectAll('line').attr('opacity', 0.1);
    
    // Highlight selected node
    svg.selectAll('circle')
      .filter(d => d.id === targetNode.id)
      .attr('opacity', 1)
      .attr('stroke-width', 4);
    
    // Highlight connected nodes and links
    if (citationData && citationData.links) {
      const connectedNodeIds = new Set();
      citationData.links.forEach(link => {
        if (link.source.id === targetNode.id || link.target.id === targetNode.id) {
          connectedNodeIds.add(link.source.id);
          connectedNodeIds.add(link.target.id);
          
          // Highlight link
          svg.selectAll('line')
            .filter(d => (d.source.id === link.source.id && d.target.id === link.target.id))
            .attr('opacity', 0.8);
        }
      });
      
      // Highlight connected nodes
      svg.selectAll('circle')
        .filter(d => connectedNodeIds.has(d.id))
        .attr('opacity', 1);
    }
  };

  const resetHighlights = () => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('circle').attr('opacity', 1).attr('stroke-width', 2);
    svg.selectAll('line').attr('opacity', 0.6);
    setSelectedNode(null);
  };

  const showTooltip = (event, node) => {
    // Create tooltip element
    const tooltip = d3.select('body').append('div')
      .attr('class', 'citation-tooltip')
      .style('position', 'absolute')
      .style('padding', '10px')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('border-radius', '5px')
      .style('pointer-events', 'none')
      .style('font-size', '12px')
      .style('z-index', '1000')
      .html(`
        <strong>${node.case_name || node.title}</strong><br/>
        Authority: ${((node.authority_score || 0) * 100).toFixed(0)}%<br/>
        Year: ${node.year || 'N/A'}<br/>
        Citations: ${node.citation_count || 0}
      `);
    
    // Position tooltip
    tooltip
      .style('left', (event.pageX + 10) + 'px')
      .style('top', (event.pageY - 10) + 'px');
  };

  const hideTooltip = () => {
    d3.selectAll('.citation-tooltip').remove();
  };

  const downloadNetwork = () => {
    const svg = svgRef.current;
    const serializer = new XMLSerializer();
    const source = serializer.serializeToString(svg);
    
    const blob = new Blob([source], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'citation-network.svg';
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                Citation Network Visualization
              </CardTitle>
              <CardDescription>
                Interactive network showing case relationships and citation patterns
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Select value={viewMode} onValueChange={setViewMode}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="authority">Authority View</SelectItem>
                  <SelectItem value="temporal">Temporal View</SelectItem>
                  <SelectItem value="subject">Subject View</SelectItem>
                </SelectContent>
              </Select>
              <Button size="sm" variant="outline" onClick={loadCitationNetwork}>
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button size="sm" variant="outline" onClick={downloadNetwork}>
                <Download className="h-4 w-4" />
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => setIsFullscreen(!isFullscreen)}
              >
                {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Network Stats */}
          {networkStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{networkStats.total_nodes || 0}</div>
                <div className="text-sm text-gray-600">Nodes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{networkStats.total_links || 0}</div>
                <div className="text-sm text-gray-600">Connections</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {networkStats.avg_authority_score || 0}%
                </div>
                <div className="text-sm text-gray-600">Avg Authority</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {networkStats.network_density || 0}%
                </div>
                <div className="text-sm text-gray-600">Density</div>
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-red-600"></div>
                  <span>High Authority</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
                  <span>Medium Authority</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-green-600"></div>
                  <span>Low Authority</span>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                Zoom: {Math.round(zoomLevel * 100)}%
              </div>
            </div>
          </div>

          {/* SVG Container */}
          <div className={`border rounded-lg ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}>
            {isLoading ? (
              <div className="flex items-center justify-center h-96">
                <div className="animate-spin h-8 w-8 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                <span className="ml-2">Loading citation network...</span>
              </div>
            ) : (
              <svg ref={svgRef} className="w-full"></svg>
            )}
          </div>

          {/* Control Buttons */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center space-x-2">
              <Button size="sm" variant="outline" onClick={resetHighlights}>
                Reset View
              </Button>
              <Button size="sm" variant="outline" onClick={() => setZoomLevel(1)}>
                Reset Zoom
              </Button>
            </div>
            {selectedNode && (
              <Badge variant="outline">
                Selected: {selectedNode.case_name || selectedNode.title}
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Selected Node Details */}
      {selectedNode && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Info className="h-4 w-4" />
              Case Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <h4 className="font-semibold">{selectedNode.case_name || selectedNode.title}</h4>
                <p className="text-sm text-gray-600">{selectedNode.court} | {selectedNode.year}</p>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Authority Score</div>
                  <div className="font-medium">{((selectedNode.authority_score || 0) * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Citations</div>
                  <div className="font-medium">{selectedNode.citation_count || 0}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Legal Domain</div>
                  <div className="font-medium">{selectedNode.legal_domain || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Jurisdiction</div>
                  <div className="font-medium">{selectedNode.jurisdiction || 'N/A'}</div>
                </div>
              </div>

              {selectedNode.summary && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Summary</div>
                  <p className="text-sm">{selectedNode.summary}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {!citationData && !isLoading && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Start a research query to generate citation network visualization.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default CitationNetworkVisualization;