#!/usr/bin/env python3
"""
Enhanced Contract Negotiation Agent with Legal Analysis Testing Suite

This comprehensive test suite validates:
1. Basic Contract Negotiation Agent functionality
2. Enhanced Legal Analysis endpoints (document upload, analysis, comparison)
3. Integration testing with AI models and database
4. Response validation against Pydantic schemas
5. Error handling and edge cases

Test Coverage:
- POST /api/ai-agents/contract-negotiation (basic agent)
- POST /api/ai-agents/contract-negotiation/upload-document (file upload)
- GET /api/ai-agents/contract-negotiation/documents (document listing)
- GET /api/ai-agents/contract-negotiation/document/{document_id} (analysis retrieval)
- GET /api/ai-agents/contract-negotiation/document/{document_id}/clauses (clause analysis)
- POST /api/ai-agents/contract-negotiation/compare-documents (document comparison)
"""

import asyncio
import aiohttp
import json
import time
import uuid
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedContractNegotiationTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://risk-ai-negotiator.preview.emergentagent.com/api"
        self.session = None
        self.test_results = []
        self.test_session_id = str(uuid.uuid4())
        self.test_user_id = str(uuid.uuid4())
        
        # Test data for comprehensive testing
        self.test_documents = {}
        self.uploaded_document_ids = []
        
    async def setup_session(self):
        """Initialize HTTP session with proper headers"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test_result(self, test_name: str, success: bool, details: str, response_time: float = 0.0):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        logger.info(f"{status} {test_name}: {details} ({response_time:.3f}s)")
        
    async def test_basic_contract_negotiation_agent(self):
        """Test 1: Basic Contract Negotiation Agent functionality"""
        test_name = "Basic Contract Negotiation Agent"
        start_time = time.time()
        
        try:
            # Test various message types for contract negotiation
            test_scenarios = [
                {
                    "message": "I need help negotiating payment terms in a software licensing agreement",
                    "expected_keywords": ["payment", "terms", "software", "licensing"]
                },
                {
                    "message": "What are the key risk factors I should consider in this partnership agreement?",
                    "expected_keywords": ["risk", "partnership", "agreement"]
                },
                {
                    "message": "Help me structure a better liability clause for my service contract",
                    "expected_keywords": ["liability", "clause", "service", "contract"]
                }
            ]
            
            for i, scenario in enumerate(test_scenarios):
                payload = {
                    "message": scenario["message"],
                    "session_id": f"{self.test_session_id}_scenario_{i}",
                    "user_id": self.test_user_id,
                    "jurisdiction": "US"
                }
                
                async with self.session.post(f"{self.base_url}/ai-agents/contract-negotiation", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        required_fields = ['response_id', 'agent_type', 'content', 'recommendations', 
                                         'action_items', 'confidence_score', 'follow_up_questions', 'timestamp']
                        
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            self.log_test_result(f"{test_name} - Scenario {i+1} Structure", False, 
                                               f"Missing fields: {missing_fields}", response_time)
                            continue
                            
                        # Validate agent type
                        if data.get('agent_type') != 'contract_negotiation':
                            self.log_test_result(f"{test_name} - Scenario {i+1} Agent Type", False, 
                                               f"Wrong agent type: {data.get('agent_type')}", response_time)
                            continue
                            
                        # Validate confidence score range
                        confidence = data.get('confidence_score', 0)
                        if not (0.0 <= confidence <= 1.0):
                            self.log_test_result(f"{test_name} - Scenario {i+1} Confidence", False, 
                                               f"Invalid confidence score: {confidence}", response_time)
                            continue
                            
                        # Check for meaningful content
                        content = data.get('content', '')
                        if len(content) < 50:
                            self.log_test_result(f"{test_name} - Scenario {i+1} Content", False, 
                                               f"Content too short: {len(content)} chars", response_time)
                            continue
                            
                        # Check for meaningful guidance (recommendations, action items, or follow-up questions)
                        recommendations = data.get('recommendations', [])
                        action_items = data.get('action_items', [])
                        follow_up_questions = data.get('follow_up_questions', [])
                        
                        # Agent should provide at least some form of guidance
                        if not recommendations and not action_items and not follow_up_questions:
                            self.log_test_result(f"{test_name} - Scenario {i+1} Guidance", False, 
                                               f"No guidance provided (no recommendations, action items, or follow-up questions)", response_time)
                            continue
                            
                        self.log_test_result(f"{test_name} - Scenario {i+1}", True, 
                                           f"Agent responded with {len(content)} chars, confidence: {confidence:.3f}", 
                                           response_time)
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"{test_name} - Scenario {i+1}", False, 
                                           f"HTTP {response.status}: {error_text}", response_time)
                        
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {str(e)}", response_time)
            
    async def test_document_upload_and_analysis(self):
        """Test 2: Document Upload and Analysis functionality"""
        test_name = "Document Upload and Analysis"
        start_time = time.time()
        
        try:
            # Create test contract documents
            test_contracts = [
                {
                    "filename": "test_nda.txt",
                    "content": """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into on [DATE] between Company A and Company B.

1. CONFIDENTIAL INFORMATION
The parties acknowledge that confidential information may be disclosed during business discussions.

2. OBLIGATIONS
The receiving party agrees to:
- Keep all confidential information strictly confidential
- Not disclose to third parties without written consent
- Use information solely for evaluation purposes

3. TERM
This agreement shall remain in effect for 2 years from the date of execution.

4. GOVERNING LAW
This agreement shall be governed by the laws of California.

SIGNATURES:
Company A: _________________
Company B: _________________""",
                    "document_type": "nda"
                },
                {
                    "filename": "test_service_agreement.txt", 
                    "content": """SERVICE AGREEMENT

This Service Agreement is between Service Provider and Client for web development services.

1. SCOPE OF WORK
Provider will develop a custom e-commerce website with the following features:
- Product catalog management
- Shopping cart functionality
- Payment processing integration
- User account management

2. PAYMENT TERMS
Total project cost: $15,000
Payment schedule:
- 50% upfront upon signing
- 25% at milestone completion
- 25% upon final delivery

3. TIMELINE
Project duration: 12 weeks from start date
Key milestones:
- Week 4: Design approval
- Week 8: Development completion
- Week 12: Testing and launch

4. INTELLECTUAL PROPERTY
All custom code and designs become property of Client upon final payment.

5. LIABILITY
Provider's liability is limited to the total contract amount.

SIGNATURES:
Provider: _________________
Client: _________________""",
                    "document_type": "service_agreement"
                }
            ]
            
            for contract in test_contracts:
                # Prepare multipart form data properly
                data = aiohttp.FormData()
                data.add_field('session_id', self.test_session_id)
                data.add_field('user_id', self.test_user_id)
                
                # Create a proper file-like object
                file_content = contract["content"].encode('utf-8')
                data.add_field('file', 
                             io.BytesIO(file_content), 
                             filename=contract["filename"],
                             content_type='text/plain')
                
                # Update session headers for multipart form data
                headers = {'Accept': 'application/json'}
                
                async with self.session.post(f"{self.base_url}/ai-agents/contract-negotiation/upload-document", 
                                           data=data, headers=headers) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Validate response structure
                        required_fields = ['document_id', 'filename', 'document_type', 'overall_risk_score',
                                         'analysis_summary', 'key_issues', 'recommendations', 
                                         'negotiation_priorities', 'missing_clauses', 'metadata']
                        
                        missing_fields = [field for field in required_fields if field not in result]
                        if missing_fields:
                            self.log_test_result(f"{test_name} - {contract['filename']} Structure", False, 
                                               f"Missing fields: {missing_fields}", response_time)
                            continue
                            
                        # Validate risk score
                        risk_score = result.get('overall_risk_score', -1)
                        if not (0.0 <= risk_score <= 100.0):
                            self.log_test_result(f"{test_name} - {contract['filename']} Risk Score", False, 
                                               f"Invalid risk score: {risk_score}", response_time)
                            continue
                            
                        # Store document ID for later tests
                        document_id = result.get('document_id')
                        if document_id:
                            self.uploaded_document_ids.append(document_id)
                            self.test_documents[document_id] = {
                                'filename': contract['filename'],
                                'type': contract['document_type'],
                                'analysis': result
                            }
                            
                        # Validate analysis content
                        key_issues = result.get('key_issues', [])
                        recommendations = result.get('recommendations', [])
                        if not key_issues or not recommendations:
                            self.log_test_result(f"{test_name} - {contract['filename']} Analysis", False, 
                                               f"Missing analysis content", response_time)
                            continue
                            
                        self.log_test_result(f"{test_name} - {contract['filename']}", True, 
                                           f"Document analyzed, risk score: {risk_score:.1f}, {len(key_issues)} issues found", 
                                           response_time)
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"{test_name} - {contract['filename']}", False, 
                                           f"HTTP {response.status}: {error_text}", response_time)
                        
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {str(e)}", response_time)
            
    async def test_document_listing(self):
        """Test 3: Document Listing functionality"""
        test_name = "Document Listing"
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}/ai-agents/contract-negotiation/documents") as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    if 'documents' not in data or 'total_count' not in data:
                        self.log_test_result(test_name, False, 
                                           f"Missing required fields in response", response_time)
                        return
                        
                    documents = data.get('documents', [])
                    total_count = data.get('total_count', 0)
                    
                    # Check if our uploaded documents are listed
                    found_documents = 0
                    for doc_id in self.uploaded_document_ids:
                        for doc in documents:
                            if doc.get('document_id') == doc_id:
                                found_documents += 1
                                break
                                
                    if found_documents == len(self.uploaded_document_ids):
                        self.log_test_result(test_name, True, 
                                           f"Found {found_documents}/{len(self.uploaded_document_ids)} uploaded documents, total: {total_count}", 
                                           response_time)
                    else:
                        self.log_test_result(test_name, False, 
                                           f"Only found {found_documents}/{len(self.uploaded_document_ids)} uploaded documents", 
                                           response_time)
                else:
                    error_text = await response.text()
                    self.log_test_result(test_name, False, 
                                       f"HTTP {response.status}: {error_text}", response_time)
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {str(e)}", response_time)
            
    async def test_document_analysis_retrieval(self):
        """Test 4: Document Analysis Retrieval"""
        test_name = "Document Analysis Retrieval"
        
        if not self.uploaded_document_ids:
            self.log_test_result(test_name, False, "No uploaded documents to test", 0.0)
            return
            
        for document_id in self.uploaded_document_ids:
            start_time = time.time()
            
            try:
                async with self.session.get(f"{self.base_url}/ai-agents/contract-negotiation/document/{document_id}") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure matches DocumentAnalysisResponse
                        required_fields = ['document_id', 'filename', 'document_type', 'overall_risk_score',
                                         'analysis_summary', 'key_issues', 'recommendations', 
                                         'negotiation_priorities', 'missing_clauses', 'metadata']
                        
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                               f"Missing fields: {missing_fields}", response_time)
                            continue
                            
                        # Validate document ID matches
                        if data.get('document_id') != document_id:
                            self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                               f"Document ID mismatch", response_time)
                            continue
                            
                        filename = data.get('filename', 'unknown')
                        risk_score = data.get('overall_risk_score', 0)
                        
                        self.log_test_result(f"{test_name} - {filename}", True, 
                                           f"Retrieved analysis for {filename}, risk: {risk_score:.1f}", 
                                           response_time)
                    elif response.status == 404:
                        self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                           f"Document not found", response_time)
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                           f"HTTP {response.status}: {error_text}", response_time)
                        
            except Exception as e:
                response_time = time.time() - start_time
                self.log_test_result(f"{test_name} - {document_id[:8]}", False, f"Exception: {str(e)}", response_time)
                
    async def test_clause_analysis(self):
        """Test 5: Detailed Clause Analysis"""
        test_name = "Clause Analysis"
        
        if not self.uploaded_document_ids:
            self.log_test_result(test_name, False, "No uploaded documents to test", 0.0)
            return
            
        for document_id in self.uploaded_document_ids:
            start_time = time.time()
            
            try:
                async with self.session.get(f"{self.base_url}/ai-agents/contract-negotiation/document/{document_id}/clauses") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Should return a list of clause analyses
                        if not isinstance(data, list):
                            self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                               f"Expected list, got {type(data)}", response_time)
                            continue
                            
                        if len(data) == 0:
                            self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                               f"No clauses found in analysis", response_time)
                            continue
                            
                        # Validate clause structure
                        valid_clauses = 0
                        for clause in data:
                            required_fields = ['clause_id', 'clause_type', 'content', 'risk_level', 
                                             'risk_score', 'issues', 'recommendations', 'suggested_alternatives']
                            
                            if all(field in clause for field in required_fields):
                                # Validate risk score
                                risk_score = clause.get('risk_score', -1)
                                if 0.0 <= risk_score <= 100.0:
                                    valid_clauses += 1
                                    
                        filename = self.test_documents.get(document_id, {}).get('filename', 'unknown')
                        
                        if valid_clauses == len(data):
                            self.log_test_result(f"{test_name} - {filename}", True, 
                                               f"Retrieved {len(data)} valid clause analyses", 
                                               response_time)
                        else:
                            self.log_test_result(f"{test_name} - {filename}", False, 
                                               f"Only {valid_clauses}/{len(data)} clauses valid", 
                                               response_time)
                    elif response.status == 404:
                        self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                           f"Document analysis not found", response_time)
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"{test_name} - {document_id[:8]}", False, 
                                           f"HTTP {response.status}: {error_text}", response_time)
                        
            except Exception as e:
                response_time = time.time() - start_time
                self.log_test_result(f"{test_name} - {document_id[:8]}", False, f"Exception: {str(e)}", response_time)
                
    async def test_document_comparison(self):
        """Test 6: Document Comparison functionality"""
        test_name = "Document Comparison"
        
        if len(self.uploaded_document_ids) < 2:
            self.log_test_result(test_name, False, "Need at least 2 documents for comparison", 0.0)
            return
            
        start_time = time.time()
        
        try:
            # Compare first two uploaded documents
            doc1_id = self.uploaded_document_ids[0]
            doc2_id = self.uploaded_document_ids[1]
            
            payload = {
                "session_id": self.test_session_id,
                "document1_id": doc1_id,
                "document2_id": doc2_id,
                "user_id": self.test_user_id
            }
            
            async with self.session.post(f"{self.base_url}/ai-agents/contract-negotiation/compare-documents", 
                                       json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ['comparison_id', 'document1_id', 'document2_id', 'differences',
                                     'gap_analysis', 'risk_comparison', 'recommendations', 'preferred_clauses']
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test_result(test_name, False, 
                                           f"Missing fields: {missing_fields}", response_time)
                        return
                        
                    # Validate document IDs match
                    if data.get('document1_id') != doc1_id or data.get('document2_id') != doc2_id:
                        self.log_test_result(test_name, False, 
                                           f"Document ID mismatch in response", response_time)
                        return
                        
                    # Check for meaningful comparison content
                    differences = data.get('differences', [])
                    gap_analysis = data.get('gap_analysis', [])
                    recommendations = data.get('recommendations', [])
                    
                    if not differences and not gap_analysis:
                        self.log_test_result(test_name, False, 
                                           f"No differences or gap analysis found", response_time)
                        return
                        
                    doc1_name = self.test_documents.get(doc1_id, {}).get('filename', 'doc1')
                    doc2_name = self.test_documents.get(doc2_id, {}).get('filename', 'doc2')
                    
                    self.log_test_result(test_name, True, 
                                       f"Compared {doc1_name} vs {doc2_name}: {len(differences)} differences, {len(recommendations)} recommendations", 
                                       response_time)
                else:
                    error_text = await response.text()
                    self.log_test_result(test_name, False, 
                                       f"HTTP {response.status}: {error_text}", response_time)
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {str(e)}", response_time)
            
    async def test_integration_with_chat_agent(self):
        """Test 7: Integration - Enhanced agent provides document analysis guidance in chat"""
        test_name = "Integration with Chat Agent"
        
        if not self.uploaded_document_ids:
            self.log_test_result(test_name, False, "No uploaded documents to reference", 0.0)
            return
            
        start_time = time.time()
        
        try:
            # Test chat messages that reference uploaded documents
            document_id = self.uploaded_document_ids[0]
            filename = self.test_documents.get(document_id, {}).get('filename', 'test document')
            
            test_messages = [
                f"I just uploaded a document ({filename}). Can you help me understand the key risks?",
                f"Based on the document analysis for {filename}, what should I negotiate first?",
                "What are the most important clauses I should focus on in my uploaded contracts?"
            ]
            
            for i, message in enumerate(test_messages):
                payload = {
                    "message": message,
                    "session_id": f"{self.test_session_id}_integration_{i}",
                    "user_id": self.test_user_id,
                    "jurisdiction": "US"
                }
                
                async with self.session.post(f"{self.base_url}/ai-agents/contract-negotiation", json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        content = data.get('content', '')
                        recommendations = data.get('recommendations', [])
                        
                        # Check if response shows awareness of document analysis capabilities
                        analysis_keywords = ['analysis', 'document', 'risk', 'clause', 'upload', 'review']
                        keyword_found = any(keyword in content.lower() for keyword in analysis_keywords)
                        
                        if keyword_found and len(recommendations) > 0:
                            self.log_test_result(f"{test_name} - Message {i+1}", True, 
                                               f"Agent provided document-aware guidance with {len(recommendations)} recommendations", 
                                               response_time)
                        else:
                            self.log_test_result(f"{test_name} - Message {i+1}", False, 
                                               f"Agent response lacks document analysis awareness", 
                                               response_time)
                    else:
                        error_text = await response.text()
                        self.log_test_result(f"{test_name} - Message {i+1}", False, 
                                           f"HTTP {response.status}: {error_text}", response_time)
                        
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {str(e)}", response_time)
            
    async def test_error_handling(self):
        """Test 8: Error Handling for invalid inputs"""
        test_name = "Error Handling"
        
        error_tests = [
            {
                "name": "Invalid File Upload - No File",
                "endpoint": "/ai-agents/contract-negotiation/upload-document",
                "method": "POST",
                "data": {"session_id": self.test_session_id},
                "expected_status": 422  # Changed from 400 to 422 for validation errors
            },
            {
                "name": "Invalid Document ID - Analysis Retrieval",
                "endpoint": "/ai-agents/contract-negotiation/document/invalid-doc-id",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "Invalid Document ID - Clause Analysis",
                "endpoint": "/ai-agents/contract-negotiation/document/invalid-doc-id/clauses",
                "method": "GET", 
                "expected_status": 404
            },
            {
                "name": "Invalid Comparison Request - Missing Document IDs",
                "endpoint": "/ai-agents/contract-negotiation/compare-documents",
                "method": "POST",
                "data": {"session_id": self.test_session_id},
                "expected_status": 422
            }
        ]
        
        for test_case in error_tests:
            start_time = time.time()
            
            try:
                url = f"{self.base_url}{test_case['endpoint']}"
                
                if test_case['method'] == 'POST':
                    if 'upload-document' in test_case['endpoint']:
                        # Test file upload without file
                        data = aiohttp.FormData()
                        data.add_field('session_id', self.test_session_id)
                        async with self.session.post(url, data=data) as response:
                            response_time = time.time() - start_time
                            
                            if response.status == test_case['expected_status']:
                                self.log_test_result(f"{test_name} - {test_case['name']}", True, 
                                                   f"Correctly returned HTTP {response.status}", response_time)
                            else:
                                self.log_test_result(f"{test_name} - {test_case['name']}", False, 
                                                   f"Expected {test_case['expected_status']}, got {response.status}", response_time)
                    else:
                        # Regular POST request
                        async with self.session.post(url, json=test_case.get('data', {})) as response:
                            response_time = time.time() - start_time
                            
                            if response.status == test_case['expected_status']:
                                self.log_test_result(f"{test_name} - {test_case['name']}", True, 
                                                   f"Correctly returned HTTP {response.status}", response_time)
                            else:
                                self.log_test_result(f"{test_name} - {test_case['name']}", False, 
                                                   f"Expected {test_case['expected_status']}, got {response.status}", response_time)
                else:
                    # GET request
                    async with self.session.get(url) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == test_case['expected_status']:
                            self.log_test_result(f"{test_name} - {test_case['name']}", True, 
                                               f"Correctly returned HTTP {response.status}", response_time)
                        else:
                            self.log_test_result(f"{test_name} - {test_case['name']}", False, 
                                               f"Expected {test_case['expected_status']}, got {response.status}", response_time)
                            
            except Exception as e:
                response_time = time.time() - start_time
                self.log_test_result(f"{test_name} - {test_case['name']}", False, f"Exception: {str(e)}", response_time)
                
    async def run_comprehensive_tests(self):
        """Run all comprehensive tests for Enhanced Contract Negotiation Agent"""
        logger.info("🚀 Starting Enhanced Contract Negotiation Agent Testing Suite")
        logger.info(f"📍 Testing against: {self.base_url}")
        
        await self.setup_session()
        
        try:
            # Run all test suites in order
            await self.test_basic_contract_negotiation_agent()
            await self.test_document_upload_and_analysis()
            await self.test_document_listing()
            await self.test_document_analysis_retrieval()
            await self.test_clause_analysis()
            await self.test_document_comparison()
            await self.test_integration_with_chat_agent()
            await self.test_error_handling()
            
        finally:
            await self.cleanup_session()
            
        # Generate comprehensive test report
        return self.generate_test_report()
        
    def generate_test_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("\n" + "="*80)
        logger.info("📊 ENHANCED CONTRACT NEGOTIATION AGENT TEST REPORT")
        logger.info("="*80)
        logger.info(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        
        if failed_tests > 0:
            logger.info("\n🔍 FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"❌ {result['test_name']}: {result['details']}")
                    
        logger.info("\n📋 TEST CATEGORIES SUMMARY:")
        
        # Group results by test category
        categories = {}
        for result in self.test_results:
            category = result['test_name'].split(' - ')[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if result['success']:
                categories[category]['passed'] += 1
                
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 50 else "❌"
            logger.info(f"{status} {category}: {success_rate:.1f}% ({stats['passed']}/{stats['total']})")
            
        # Performance summary
        avg_response_time = sum(r['response_time'] for r in self.test_results) / len(self.test_results)
        logger.info(f"\n⚡ Average Response Time: {avg_response_time:.3f}s")
        
        logger.info("="*80)
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'categories': categories,
            'avg_response_time': avg_response_time,
            'test_results': self.test_results
        }

async def main():
    """Main test execution function"""
    tester = EnhancedContractNegotiationTester()
    return await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())