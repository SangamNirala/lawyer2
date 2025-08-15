import React, { useState, useCallback, useRef } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Scale, Plus, Trash2, Move, Eye, Save, Download, Lightbulb } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Drag and Drop Item Types
const ItemTypes = {
  PRECEDENT: 'precedent',
  ARGUMENT: 'argument',
  EVIDENCE: 'evidence'
};

// Draggable Precedent Card
const PrecedentCard = ({ precedent, index }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.PRECEDENT,
    item: { type: ItemTypes.PRECEDENT, precedent, index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <div
      ref={drag}
      className={`p-3 border rounded-lg cursor-move transition-all ${
        isDragging ? 'opacity-50 scale-95' : 'hover:shadow-md'
      }`}
    >
      <div className="space-y-2">
        <h4 className="font-semibold text-sm">{precedent.case_name}</h4>
        <p className="text-xs text-gray-600">{precedent.court} | {precedent.date}</p>
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-xs">
            {precedent.relevance_score || 0}% Match
          </Badge>
          {precedent.precedent_strength && (
            <Badge variant="secondary" className="text-xs">
              Strength: {precedent.precedent_strength}/10
            </Badge>
          )}
        </div>
        {precedent.key_principle && (
          <p className="text-xs text-blue-700 bg-blue-50 p-2 rounded">
            {precedent.key_principle}
          </p>
        )}
      </div>
    </div>
  );
};

// Draggable Argument Component
const ArgumentComponent = ({ argument, index, onUpdate, onDelete, moveArgument }) => {
  const ref = useRef(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(argument.content);

  const [{ handlerId }, drop] = useDrop({
    accept: [ItemTypes.ARGUMENT, ItemTypes.PRECEDENT],
    collect(monitor) {
      return {
        handlerId: monitor.getHandlerId(),
      };
    },
    hover(item, monitor) {
      if (!ref.current) {
        return;
      }
      
      if (item.type === ItemTypes.ARGUMENT) {
        const dragIndex = item.index;
        const hoverIndex = index;

        if (dragIndex === hoverIndex) {
          return;
        }

        const hoverBoundingRect = ref.current?.getBoundingClientRect();
        const hoverMiddleY = (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;
        const clientOffset = monitor.getClientOffset();
        const hoverClientY = clientOffset.y - hoverBoundingRect.top;

        if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) {
          return;
        }
        if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) {
          return;
        }

        moveArgument(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    drop(item) {
      if (item.type === ItemTypes.PRECEDENT) {
        const newSupport = {
          id: Date.now(),
          type: 'precedent',
          case_name: item.precedent.case_name,
          citation: item.precedent.citation,
          relevance_score: item.precedent.relevance_score,
          key_principle: item.precedent.key_principle
        };
        
        const updatedArgument = {
          ...argument,
          supporting_evidence: [...(argument.supporting_evidence || []), newSupport]
        };
        
        onUpdate(index, updatedArgument);
      }
    },
  });

  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.ARGUMENT,
    item: () => {
      return { id: argument.id, index, type: ItemTypes.ARGUMENT };
    },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  drag(drop(ref));

  const handleSave = () => {
    onUpdate(index, { ...argument, content: editContent });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditContent(argument.content);
    setIsEditing(false);
  };

  const removeSupport = (supportIndex) => {
    const updatedSupporting = argument.supporting_evidence.filter((_, idx) => idx !== supportIndex);
    onUpdate(index, { ...argument, supporting_evidence: updatedSupporting });
  };

  return (
    <div
      ref={ref}
      data-handler-id={handlerId}
      className={`transition-all ${isDragging ? 'opacity-50' : ''}`}
    >
      <Card className="hover:shadow-md">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Move className="h-4 w-4 text-gray-400 cursor-move" />
              <Badge variant="outline">Argument {index + 1}</Badge>
              {argument.strength_score && (
                <Badge variant={
                  argument.strength_score >= 8 ? 'default' : 
                  argument.strength_score >= 6 ? 'secondary' : 'outline'
                }>
                  {argument.strength_score}/10
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-1">
              <Button 
                size="sm" 
                variant="ghost"
                onClick={() => setIsEditing(!isEditing)}
              >
                Edit
              </Button>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={() => onDelete(index)}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {isEditing ? (
            <div className="space-y-3">
              <Textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                placeholder="Enter your legal argument..."
                className="min-h-24"
              />
              <div className="flex items-center space-x-2">
                <Button size="sm" onClick={handleSave}>Save</Button>
                <Button size="sm" variant="outline" onClick={handleCancel}>Cancel</Button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm leading-relaxed">{argument.content}</p>
              
              {/* Supporting Evidence */}
              {argument.supporting_evidence && argument.supporting_evidence.length > 0 && (
                <div className="space-y-2">
                  <h5 className="text-sm font-medium text-gray-700">Supporting Evidence:</h5>
                  <div className="space-y-2">
                    {argument.supporting_evidence.map((support, supportIndex) => (
                      <div key={support.id} className="flex items-center justify-between p-2 bg-blue-50 rounded text-xs">
                        <div className="flex-1">
                          <div className="font-medium">{support.case_name}</div>
                          {support.key_principle && (
                            <div className="text-gray-600 mt-1">{support.key_principle}</div>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          {support.relevance_score && (
                            <Badge variant="outline" className="text-xs">
                              {support.relevance_score}%
                            </Badge>
                          )}
                          <Button 
                            size="sm" 
                            variant="ghost"
                            onClick={() => removeSupport(supportIndex)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Drop Zone for Precedents */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center text-sm text-gray-500 hover:border-blue-400 hover:bg-blue-50 transition-colors">
                Drop precedents here to add supporting evidence
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const ArgumentBuilder = ({ researchData, precedents = [] }) => {
  const [argumentsList, setArgumentsList] = useState([]);
  const [newArgumentContent, setNewArgumentContent] = useState('');
  const [argumentTitle, setArgumentTitle] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState('builder');
  const [argumentAnalysis, setArgumentAnalysis] = useState(null);

  const addArgument = () => {
    if (!newArgumentContent.trim()) return;

    const newArgument = {
      id: Date.now(),
      content: newArgumentContent,
      supporting_evidence: [],
      strength_score: null,
      created_at: new Date().toISOString()
    };

    setArgumentsList([...argumentsList, newArgument]);
    setNewArgumentContent('');
  };

  const updateArgument = (index, updatedArgument) => {
    const updatedArguments = argumentsList.map((arg, idx) => 
      idx === index ? updatedArgument : arg
    );
    setArgumentsList(updatedArguments);
  };

  const deleteArgument = (index) => {
    setArgumentsList(argumentsList.filter((_, idx) => idx !== index));
  };

  const moveArgument = useCallback((dragIndex, hoverIndex) => {
    setArgumentsList((prevArguments) => {
      const newArguments = [...prevArguments];
      const draggedArgument = newArguments[dragIndex];
      newArguments.splice(dragIndex, 1);
      newArguments.splice(hoverIndex, 0, draggedArgument);
      return newArguments;
    });
  }, []);

  const generateArgumentStructure = async () => {
    if (!researchData && precedents.length === 0) {
      alert('No research data available for argument generation.');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/structure-arguments`, {
        research_data: researchData,
        precedents: precedents,
        argument_style: 'comprehensive',
        include_counter_arguments: true,
        include_strength_analysis: true
      });

      if (response.data.structured_arguments) {
        setArgumentsList(response.data.structured_arguments.map((arg, index) => ({
          id: Date.now() + index,
          content: arg.argument,
          supporting_evidence: arg.supporting_precedents || [],
          strength_score: arg.strength_score,
          created_at: new Date().toISOString()
        })));
      }

      if (response.data.argument_analysis) {
        setArgumentAnalysis(response.data.argument_analysis);
      }

    } catch (error) {
      console.error('Error generating argument structure:', error);
      alert('Failed to generate argument structure. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const saveArgumentStructure = async () => {
    if (argumentsList.length === 0) {
      alert('No arguments to save.');
      return;
    }

    try {
      const response = await axios.post(`${API}/legal-research-engine/save-argument-structure`, {
        title: argumentTitle || `Argument Structure - ${new Date().toLocaleDateString()}`,
        arguments: argumentsList,
        analysis: argumentAnalysis
      });

      alert('Argument structure saved successfully!');
    } catch (error) {
      console.error('Error saving argument structure:', error);
      alert('Failed to save argument structure. Please try again.');
    }
  };

  const exportArguments = () => {
    const exportData = {
      title: argumentTitle || `Argument Structure - ${new Date().toLocaleDateString()}`,
      created_at: new Date().toISOString(),
      arguments: arguments,
      analysis: argumentAnalysis
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `argument-structure-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const ArgumentPreview = () => (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold">
          {argumentTitle || 'Legal Argument Structure'}
        </h2>
        <p className="text-gray-600">Generated on {new Date().toLocaleDateString()}</p>
      </div>

      {arguments.map((argument, index) => (
        <div key={argument.id} className="space-y-3">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-semibold">Argument {index + 1}</h3>
            {argument.strength_score && (
              <Badge variant="outline">
                Strength: {argument.strength_score}/10
              </Badge>
            )}
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="leading-relaxed">{argument.content}</p>
          </div>

          {argument.supporting_evidence && argument.supporting_evidence.length > 0 && (
            <div className="ml-4">
              <h4 className="font-medium text-gray-700 mb-2">Supporting Evidence:</h4>
              <ul className="space-y-2">
                {argument.supporting_evidence.map((support, supportIndex) => (
                  <li key={support.id} className="text-sm">
                    <span className="font-medium">{support.case_name}</span>
                    {support.citation && (
                      <span className="text-gray-600"> - {support.citation}</span>
                    )}
                    {support.key_principle && (
                      <div className="text-gray-700 mt-1 ml-4 italic">
                        "{support.key_principle}"
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}

      {argumentAnalysis && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold mb-2">Argument Analysis</h3>
          <div className="space-y-2 text-sm">
            {argumentAnalysis.overall_strength && (
              <div>
                <span className="font-medium">Overall Strength:</span> {argumentAnalysis.overall_strength}/10
              </div>
            )}
            {argumentAnalysis.recommendations && (
              <div>
                <span className="font-medium">Recommendations:</span>
                <ul className="mt-1 ml-4 list-disc">
                  {argumentAnalysis.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Scale className="h-5 w-5" />
                  Legal Argument Builder
                </CardTitle>
                <CardDescription>
                  Drag and drop interface for constructing legal arguments with precedent support
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Button 
                  onClick={generateArgumentStructure}
                  disabled={isGenerating}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Lightbulb className="h-4 w-4 mr-2" />
                      AI Generate
                    </>
                  )}
                </Button>
                <Button variant="outline" onClick={saveArgumentStructure}>
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </Button>
                <Button variant="outline" onClick={exportArguments}>
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                placeholder="Argument structure title..."
                value={argumentTitle}
                onChange={(e) => setArgumentTitle(e.target.value)}
              />
              
              <div className="flex gap-4">
                <Textarea
                  placeholder="Add a new argument..."
                  value={newArgumentContent}
                  onChange={(e) => setNewArgumentContent(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={addArgument}
                  disabled={!newArgumentContent.trim()}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Argument
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="builder">
              <Scale className="h-4 w-4 mr-2" />
              Builder
            </TabsTrigger>
            <TabsTrigger value="preview">
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </TabsTrigger>
          </TabsList>

          <TabsContent value="builder" className="mt-6">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Precedents Panel */}
              <div>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Available Precedents</CardTitle>
                    <CardDescription className="text-sm">
                      Drag precedents to arguments for support
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {precedents.length > 0 ? (
                        precedents.map((precedent, index) => (
                          <PrecedentCard 
                            key={index} 
                            precedent={precedent} 
                            index={index} 
                          />
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-500 text-sm">
                          <Scale className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                          No precedents available. Run a precedent search first.
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Arguments Panel */}
              <div className="lg:col-span-3">
                <div className="space-y-4">
                  {arguments.length > 0 ? (
                    arguments.map((argument, index) => (
                      <ArgumentComponent
                        key={argument.id}
                        argument={argument}
                        index={index}
                        onUpdate={updateArgument}
                        onDelete={deleteArgument}
                        moveArgument={moveArgument}
                      />
                    ))
                  ) : (
                    <Card>
                      <CardContent className="py-12 text-center">
                        <Scale className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                        <p className="text-gray-600">No arguments yet. Add your first argument above.</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="preview" className="mt-6">
            <Card>
              <CardContent className="p-8">
                {arguments.length > 0 ? (
                  <ArgumentPreview />
                ) : (
                  <div className="text-center py-12">
                    <Scale className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No arguments to preview. Build your argument structure first.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {!researchData && precedents.length === 0 && (
          <Alert>
            <Scale className="h-4 w-4" />
            <AlertDescription>
              Start a research query and precedent search to enable AI-powered argument generation.
            </AlertDescription>
          </Alert>
        )}
      </div>
    </DndProvider>
  );
};

export default ArgumentBuilder;