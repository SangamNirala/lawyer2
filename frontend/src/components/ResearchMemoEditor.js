import React, { useState, useEffect, useRef } from 'react';
import { Editor } from '@monaco-editor/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { FileText, Save, Download, Wand2, Eye, RefreshCw, Copy, Check } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ResearchMemoEditor = ({ researchData, researchId }) => {
  const [memoContent, setMemoContent] = useState('');
  const [memoTitle, setMemoTitle] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [memoTemplate, setMemoTemplate] = useState('comprehensive');
  const [savedMemos, setSavedMemos] = useState([]);
  const [activeTab, setActiveTab] = useState('editor');
  const [wordCount, setWordCount] = useState(0);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [copied, setCopied] = useState(false);
  const editorRef = useRef(null);

  useEffect(() => {
    if (researchData) {
      setMemoTitle(`Research Memo - ${new Date().toLocaleDateString()}`);
    }
    loadSavedMemos();
  }, [researchData]);

  useEffect(() => {
    // Update word count
    const words = memoContent.trim().split(/\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [memoContent]);

  const loadSavedMemos = async () => {
    try {
      const response = await axios.get(`${API}/legal-research-engine/research-memos`);
      setSavedMemos(response.data.memos || []);
    } catch (error) {
      console.error('Error loading saved memos:', error);
    }
  };

  const generateMemo = async () => {
    if (!researchData && !researchId) {
      alert('No research data available for memo generation.');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/generate-memo`, {
        research_id: researchId,
        research_data: researchData,
        memo_template: memoTemplate,
        include_citations: true,
        include_analysis: true,
        include_recommendations: true
      });

      setMemoContent(response.data.memo_content || response.data.content);
      if (response.data.suggested_title) {
        setMemoTitle(response.data.suggested_title);
      }
      
      // Generate AI suggestions for improvements
      if (response.data.ai_suggestions) {
        setAiSuggestions(response.data.ai_suggestions);
      }

    } catch (error) {
      console.error('Error generating memo:', error);
      alert('Failed to generate memo. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const saveMemo = async () => {
    if (!memoContent.trim() || !memoTitle.trim()) {
      alert('Please provide both title and content for the memo.');
      return;
    }

    setIsSaving(true);
    try {
      const response = await axios.post(`${API}/legal-research-engine/save-memo`, {
        title: memoTitle,
        content: memoContent,
        research_id: researchId,
        template_type: memoTemplate,
        word_count: wordCount
      });

      alert('Memo saved successfully!');
      await loadSavedMemos();

    } catch (error) {
      console.error('Error saving memo:', error);
      alert('Failed to save memo. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const downloadMemo = () => {
    const blob = new Blob([memoContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${memoTitle.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(memoContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const insertAiSuggestion = (suggestion) => {
    const editor = editorRef.current;
    if (editor) {
      const position = editor.getPosition();
      editor.executeEdits('', [{
        range: new window.monaco.Range(position.lineNumber, position.column, position.lineNumber, position.column),
        text: `\n\n${suggestion}\n\n`
      }]);
    }
  };

  const loadMemo = (memo) => {
    setMemoTitle(memo.title);
    setMemoContent(memo.content);
    setMemoTemplate(memo.template_type || 'comprehensive');
    setActiveTab('editor');
  };

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    
    // Configure editor options
    editor.updateOptions({
      minimap: { enabled: false },
      wordWrap: 'on',
      lineNumbers: 'on',
      fontSize: 14,
      fontFamily: 'SF Mono, Monaco, Menlo, Consolas, monospace'
    });

    // Add custom legal document snippets
    monaco.languages.registerCompletionItemProvider('plaintext', {
      provideCompletionItems: () => {
        return {
          suggestions: [
            {
              label: 'memo-header',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'MEMORANDUM\n\nTO: ${1:Recipient}\nFROM: ${2:Attorney}\nDATE: ${3:Date}\nRE: ${4:Subject}\n\n',
              documentation: 'Legal memo header template'
            },
            {
              label: 'issue-section',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'ISSUE\n\n${1:Legal issue statement}\n\n',
              documentation: 'Issue section template'
            },
            {
              label: 'conclusion-section',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: 'CONCLUSION\n\n${1:Brief conclusion}\n\n',
              documentation: 'Conclusion section template'
            }
          ]
        };
      }
    });
  };

  const MemoPreview = () => (
    <div className="prose max-w-none">
      <div className="bg-white p-8 border rounded-lg shadow-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold">{memoTitle}</h1>
          <div className="text-sm text-gray-600 mt-2">
            Generated on {new Date().toLocaleDateString()}
          </div>
        </div>
        <div className="whitespace-pre-wrap font-mono text-sm">
          {memoContent}
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Research Memo Editor
              </CardTitle>
              <CardDescription>
                AI-powered legal memo generation and editing with live preview
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <span>{wordCount} words</span>
              {memoContent && <Badge variant="outline">Draft</Badge>}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Memo Title and Template Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Memo Title</label>
              <Input
                placeholder="Enter memo title..."
                value={memoTitle}
                onChange={(e) => setMemoTitle(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Template</label>
              <Select value={memoTemplate} onValueChange={setMemoTemplate}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="comprehensive">Comprehensive Analysis</SelectItem>
                  <SelectItem value="brief">Brief Summary</SelectItem>
                  <SelectItem value="client-advisory">Client Advisory</SelectItem>
                  <SelectItem value="case-analysis">Case Analysis</SelectItem>
                  <SelectItem value="regulatory">Regulatory Update</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <Button 
              onClick={generateMemo}
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
                  <Wand2 className="h-4 w-4 mr-2" />
                  Generate Memo
                </>
              )}
            </Button>
            <Button 
              variant="outline" 
              onClick={saveMemo}
              disabled={isSaving || !memoContent.trim()}
            >
              {isSaving ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-gray-600 border-t-transparent rounded-full mr-2" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save
                </>
              )}
            </Button>
            <Button 
              variant="outline" 
              onClick={downloadMemo}
              disabled={!memoContent.trim()}
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button 
              variant="outline" 
              onClick={copyToClipboard}
              disabled={!memoContent.trim()}
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="editor">
            <FileText className="h-4 w-4 mr-2" />
            Editor
          </TabsTrigger>
          <TabsTrigger value="preview">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </TabsTrigger>
          <TabsTrigger value="saved">
            <Save className="h-4 w-4 mr-2" />
            Saved Memos ({savedMemos.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="editor" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <div className="border rounded-lg overflow-hidden">
                <Editor
                  height="500px"
                  defaultLanguage="plaintext"
                  value={memoContent}
                  onChange={(value) => setMemoContent(value || '')}
                  onMount={handleEditorDidMount}
                  options={{
                    minimap: { enabled: false },
                    wordWrap: 'on',
                    lineNumbers: 'on',
                    fontSize: 14,
                    fontFamily: 'SF Mono, Monaco, Menlo, Consolas, monospace',
                    padding: { top: 16, bottom: 16 }
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          {aiSuggestions.length > 0 && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wand2 className="h-4 w-4" />
                  AI Suggestions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {aiSuggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <p className="text-sm">{suggestion}</p>
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => insertAiSuggestion(suggestion)}
                      >
                        Insert
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="preview" className="mt-4">
          <Card>
            <CardContent className="p-6">
              {memoContent ? (
                <MemoPreview />
              ) : (
                <div className="text-center py-12">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No content to preview. Start writing or generate a memo.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="saved" className="mt-4">
          <div className="space-y-4">
            {savedMemos.length > 0 ? (
              savedMemos.map((memo) => (
                <Card key={memo.id} className="cursor-pointer hover:shadow-md transition-shadow">
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold">{memo.title}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <span>{new Date(memo.created_at).toLocaleDateString()}</span>
                          <span>{memo.word_count} words</span>
                          <Badge variant="outline">{memo.template_type}</Badge>
                        </div>
                      </div>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => loadMemo(memo)}
                      >
                        Load
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No saved memos yet. Generate and save your first memo.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {!researchData && !researchId && (
        <Alert>
          <FileText className="h-4 w-4" />
          <AlertDescription>
            Start a research query to enable AI-powered memo generation with relevant legal analysis.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default ResearchMemoEditor;