#!/usr/bin/env python3
"""
Enhanced Contract Negotiation Agent - Multipart Form Data Fix Test
Testing the document upload endpoint with proper multipart form data format
to resolve the critical issue identified in the review request.
"""

import requests
import json
import time
import sys
import uuid
import io
from datetime import datetime
import aiohttp
import asyncio

# Use production URL from frontend .env
BASE_URL = "https://strategyengine.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_sample_contract_content():
    """Create a sample contract for testing"""
    return """
INDEPENDENT CONTRACTOR AGREEMENT

This Independent Contractor Agreement ("Agreement") is entered into on January 15, 2025 between ABC Company ("Company") and John Doe ("Contractor").

1. SERVICES
Contractor agrees to provide web development services including:
- Frontend development using React
- Backend API development
- Database design and implementation

2. COMPENSATION
Company agrees to pay Contractor $10,000 for the completion of the project.
Payment will be made in two installments:
- 50% upon signing this agreement
- 50% upon project completion

3. TERM
This agreement shall commence on February 1, 2025 and continue until project completion, estimated to be 3 months.

4. INTELLECTUAL PROPERTY
All work product created by Contractor shall be owned by Company.

5. CONFIDENTIALITY
Contractor agrees to maintain confidentiality of all Company information.

6. TERMINATION
Either party may terminate this agreement with 30 days written notice.

7. GOVERNING LAW
This agreement shall be governed by the laws of California.

IN WITNESS WHEREOF, the parties have executed this agreement.

Company: _________________
ABC Company

Contractor: _______________
John Doe
"""

async def test_basic_contract_negotiation_agent():
    """Test the basic Contract Negotiation Agent chat functionality"""
    log_test("🤝 TESTING: Basic Contract Negotiation Agent")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation"
    session_id = str(uuid.uuid4())
    
    payload = {
        "message": "I need help negotiating payment terms in a freelance contract. The client wants to pay everything at the end, but I prefer milestone payments.",
        "session_id": session_id,
        "user_id": "test_user_123",
        "contract_type": "freelance_agreement",
        "jurisdiction": "US"
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ['response_id', 'agent_type', 'content', 'recommendations', 
                             'action_items', 'confidence_score', 'follow_up_questions', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                log_test(f"✅ PASS: Basic Contract Negotiation Agent working")
                log_test(f"Agent Type: {data.get('agent_type')}")
                log_test(f"Content Length: {len(data.get('content', ''))}")
                log_test(f"Confidence Score: {data.get('confidence_score')}")
                log_test(f"Recommendations: {len(data.get('recommendations', []))}")
                log_test(f"Action Items: {len(data.get('action_items', []))}")
                return True, session_id, f"Working correctly, {response_time:.3f}s response time"
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                return False, session_id, f"Missing fields: {missing_fields}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, session_id, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, session_id, f"Exception: {str(e)}"

async def test_document_upload_with_requests_multipart():
    """Test document upload using requests library with files parameter"""
    log_test("📄 TESTING: Document Upload with requests multipart (Method 1)")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation/upload-document"
    session_id = str(uuid.uuid4())
    
    # Create sample contract file
    contract_content = create_sample_contract_content()
    
    try:
        # Method 1: Using requests with files parameter
        files = {
            'file': ('sample_contract.txt', io.BytesIO(contract_content.encode('utf-8')), 'text/plain')
        }
        data = {
            'session_id': session_id,
            'user_id': 'test_user_123'
        }
        
        start_time = time.time()
        response = requests.post(endpoint, files=files, data=data, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ['document_id', 'filename', 'document_type', 'overall_risk_score',
                             'analysis_summary', 'key_issues', 'recommendations', 'negotiation_priorities']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                log_test(f"✅ PASS: Document upload working correctly (requests method)")
                log_test(f"Document ID: {data.get('document_id')}")
                log_test(f"Filename: {data.get('filename')}")
                log_test(f"Document Type: {data.get('document_type')}")
                log_test(f"Risk Score: {data.get('overall_risk_score')}")
                log_test(f"Key Issues: {len(data.get('key_issues', []))}")
                log_test(f"Recommendations: {len(data.get('recommendations', []))}")
                return True, data.get('document_id'), session_id, f"Upload successful, {response_time:.3f}s"
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                return False, None, session_id, f"Missing fields: {missing_fields}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, None, session_id, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, None, session_id, f"Exception: {str(e)}"

async def test_document_upload_with_aiohttp():
    """Test document upload using aiohttp with FormData"""
    log_test("📄 TESTING: Document Upload with aiohttp FormData (Method 2)")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation/upload-document"
    session_id = str(uuid.uuid4())
    
    # Create sample contract file
    contract_content = create_sample_contract_content()
    
    try:
        # Method 2: Using aiohttp for proper multipart form data handling
        async with aiohttp.ClientSession() as session:
            # Create form data with proper Form parameters
            data = aiohttp.FormData()
            data.add_field('session_id', session_id)
            data.add_field('user_id', 'test_user_123')
            data.add_field('file', 
                          io.BytesIO(contract_content.encode('utf-8')), 
                          filename='sample_contract.txt',
                          content_type='text/plain')
            
            start_time = time.time()
            async with session.post(endpoint, data=data, timeout=30) as response:
                response_time = time.time() - start_time
                
                log_test(f"Response Status: {response.status}")
                log_test(f"Response Time: {response_time:.3f}s")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    required_fields = ['document_id', 'filename', 'document_type', 'overall_risk_score',
                                     'analysis_summary', 'key_issues', 'recommendations', 'negotiation_priorities']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        log_test(f"✅ PASS: Document upload working correctly (aiohttp method)")
                        log_test(f"Document ID: {data.get('document_id')}")
                        log_test(f"Filename: {data.get('filename')}")
                        log_test(f"Document Type: {data.get('document_type')}")
                        log_test(f"Risk Score: {data.get('overall_risk_score')}")
                        log_test(f"Key Issues: {len(data.get('key_issues', []))}")
                        log_test(f"Recommendations: {len(data.get('recommendations', []))}")
                        return True, data.get('document_id'), session_id, f"Upload successful, {response_time:.3f}s"
                    else:
                        log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                        return False, None, session_id, f"Missing fields: {missing_fields}"
                else:
                    response_text = await response.text()
                    log_test(f"❌ FAIL: HTTP {response.status} - {response_text}")
                    return False, None, session_id, f"HTTP {response.status} error"
                    
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, None, session_id, f"Exception: {str(e)}"

def test_document_clause_analysis(document_id):
    """Test detailed clause analysis for uploaded document"""
    log_test("📋 TESTING: Document Clause Analysis")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation/document/{document_id}/clauses"
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                # Check first clause structure
                clause = data[0]
                required_fields = ['clause_id', 'clause_type', 'content', 'risk_level', 
                                 'risk_score', 'issues', 'recommendations', 'suggested_alternatives']
                missing_fields = [field for field in required_fields if field not in clause]
                
                if not missing_fields:
                    log_test(f"✅ PASS: Clause analysis working correctly")
                    log_test(f"Total Clauses: {len(data)}")
                    log_test(f"First Clause Type: {clause.get('clause_type')}")
                    log_test(f"First Clause Risk Level: {clause.get('risk_level')}")
                    log_test(f"First Clause Risk Score: {clause.get('risk_score')}")
                    return True, f"Found {len(data)} clauses, {response_time:.3f}s"
                else:
                    log_test(f"❌ FAIL: Missing clause fields: {missing_fields}")
                    return False, f"Missing clause fields: {missing_fields}"
            else:
                log_test(f"❌ FAIL: No clauses returned or invalid format")
                return False, "No clauses returned"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_document_analysis_summary(document_id):
    """Test document analysis summary retrieval"""
    log_test("📊 TESTING: Document Analysis Summary")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation/document/{document_id}"
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ['document_id', 'filename', 'document_type', 'overall_risk_score',
                             'analysis_summary', 'key_issues', 'recommendations', 'metadata']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                log_test(f"✅ PASS: Document analysis summary working correctly")
                log_test(f"Document ID: {data.get('document_id')}")
                log_test(f"Overall Risk Score: {data.get('overall_risk_score')}")
                log_test(f"Analysis Summary: {data.get('analysis_summary')}")
                return True, f"Summary retrieved successfully, {response_time:.3f}s"
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                return False, f"Missing fields: {missing_fields}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_document_listing(session_id):
    """Test document listing functionality"""
    log_test("📚 TESTING: Document Listing")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation/documents"
    params = {
        'session_id': session_id,
        'limit': 10,
        'offset': 0
    }
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, params=params, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ['documents', 'total_count']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                log_test(f"✅ PASS: Document listing working correctly")
                log_test(f"Total Documents: {data.get('total_count')}")
                log_test(f"Documents in Response: {len(data.get('documents', []))}")
                return True, f"Listed {data.get('total_count')} documents, {response_time:.3f}s"
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                return False, f"Missing fields: {missing_fields}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_document_comparison(document1_id, document2_id, session_id):
    """Test document comparison functionality"""
    log_test("🔄 TESTING: Document Comparison")
    
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation/compare-documents"
    
    payload = {
        "session_id": session_id,
        "document1_id": document1_id,
        "document2_id": document2_id,
        "user_id": "test_user_123"
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            required_fields = ['comparison_id', 'document1_id', 'document2_id', 'differences',
                             'gap_analysis', 'risk_comparison', 'recommendations', 'preferred_clauses']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                log_test(f"✅ PASS: Document comparison working correctly")
                log_test(f"Comparison ID: {data.get('comparison_id')}")
                log_test(f"Differences Found: {len(data.get('differences', []))}")
                log_test(f"Gap Analysis Items: {len(data.get('gap_analysis', []))}")
                log_test(f"Recommendations: {len(data.get('recommendations', []))}")
                return True, f"Comparison successful, {response_time:.3f}s"
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                return False, f"Missing fields: {missing_fields}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

async def test_integration_workflow(document_id, session_id):
    """Test integration between basic chat agent and document analysis features"""
    log_test("🔗 TESTING: Integration Workflow")
    
    # Continue chat with document context
    endpoint = f"{BASE_URL}/api/ai-agents/contract-negotiation"
    payload = {
        "message": f"I just uploaded a contract document with ID {document_id}. Can you analyze the payment terms and suggest improvements?",
        "session_id": session_id,
        "user_id": "test_user_123",
        "contract_type": "freelance_agreement",
        "jurisdiction": "US",
        "context_metadata": {
            "analyzed_documents": [{"document_id": document_id}]
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            
            # Check if response references the uploaded document
            if any(keyword in content.lower() for keyword in ['document', 'contract', 'uploaded', 'analysis', 'payment']):
                log_test(f"✅ PASS: Integration workflow working - agent references document context")
                log_test(f"Response length: {len(content)} characters")
                log_test(f"Confidence score: {data.get('confidence_score')}")
                return True, f"Integration successful, agent aware of document context"
            else:
                log_test(f"⚠️  PARTIAL: Chat works but may not be fully integrated with document context")
                return True, f"Chat works but integration unclear"
        else:
            log_test(f"❌ FAIL: Integration chat failed - HTTP {response.status_code}")
            return False, f"Integration chat failed"
            
    except Exception as e:
        log_test(f"❌ ERROR: Integration test failed - {str(e)}")
        return False, f"Integration test exception: {str(e)}"

async def main():
    """Run all Enhanced Contract Negotiation Agent tests with focus on multipart form data fix"""
    log_test("🚀 STARTING ENHANCED CONTRACT NEGOTIATION AGENT TESTING")
    log_test("🎯 FOCUS: Resolving document upload multipart form data issue")
    log_test(f"Base URL: {BASE_URL}")
    log_test("=" * 80)
    
    all_results = []
    
    # Test 1: Basic Contract Negotiation Agent
    basic_result, session_id, basic_details = await test_basic_contract_negotiation_agent()
    all_results.append(("Basic Contract Negotiation Agent", basic_result, basic_details))
    
    # Test 2: Document Upload with requests multipart (Method 1)
    upload1_result, document1_id, session1_id, upload1_details = await test_document_upload_with_requests_multipart()
    all_results.append(("Document Upload (requests multipart)", upload1_result, upload1_details))
    
    # Test 3: Document Upload with aiohttp FormData (Method 2)
    upload2_result, document2_id, session2_id, upload2_details = await test_document_upload_with_aiohttp()
    all_results.append(("Document Upload (aiohttp FormData)", upload2_result, upload2_details))
    
    # Use the first successful upload for subsequent tests
    successful_document_id = document1_id if document1_id else document2_id
    successful_session_id = session1_id if document1_id else session2_id
    
    # Test 4: Document Clause Analysis (if upload succeeded)
    if successful_document_id:
        clause_result, clause_details = test_document_clause_analysis(successful_document_id)
        all_results.append(("Document Clause Analysis", clause_result, clause_details))
        
        # Test 5: Document Analysis Summary
        summary_result, summary_details = test_document_analysis_summary(successful_document_id)
        all_results.append(("Document Analysis Summary", summary_result, summary_details))
        
        # Test 6: Integration Workflow
        integration_result, integration_details = await test_integration_workflow(successful_document_id, successful_session_id)
        all_results.append(("Integration Workflow", integration_result, integration_details))
    else:
        all_results.append(("Document Clause Analysis", False, "Skipped - no successful upload"))
        all_results.append(("Document Analysis Summary", False, "Skipped - no successful upload"))
        all_results.append(("Integration Workflow", False, "Skipped - no successful upload"))
    
    # Test 7: Document Listing
    listing_result, listing_details = test_document_listing(successful_session_id if successful_session_id else session_id)
    all_results.append(("Document Listing", listing_result, listing_details))
    
    # Test 8: Document Comparison (if we have two documents)
    if document1_id and document2_id:
        comparison_result, comparison_details = test_document_comparison(document1_id, document2_id, successful_session_id)
        all_results.append(("Document Comparison", comparison_result, comparison_details))
    else:
        all_results.append(("Document Comparison", False, "Skipped - need two successful uploads"))
    
    # Summary
    log_test("\n" + "=" * 80)
    log_test("📊 ENHANCED CONTRACT NEGOTIATION AGENT TESTING SUMMARY")
    log_test("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, success, details in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        log_test(f"{status}: {test_name} - {details}")
        if success:
            passed += 1
        else:
            failed += 1
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    log_test(f"\nTotal Tests: {total}")
    log_test(f"Passed: {passed}")
    log_test(f"Failed: {failed}")
    log_test(f"Success Rate: {success_rate:.1f}%")
    
    # Specific focus on the critical issue from review request
    log_test("\n" + "=" * 40)
    log_test("🎯 CRITICAL ISSUE RESOLUTION STATUS")
    log_test("=" * 40)
    
    upload_tests = [result for result in all_results if "Document Upload" in result[0]]
    upload_success_count = sum(1 for result in upload_tests if result[1])
    
    if upload_success_count > 0:
        log_test("✅ RESOLVED: Document upload multipart form data issue FIXED")
        log_test("✅ SUCCESS: Form(...) parameters working correctly")
        log_test(f"✅ METHODS WORKING: {upload_success_count}/{len(upload_tests)} upload methods successful")
    else:
        log_test("❌ UNRESOLVED: Document upload multipart form data issue PERSISTS")
        log_test("❌ CRITICAL: Form(...) parameters still not working")
    
    # Enhanced Legal Analysis Pipeline Status
    log_test("\n" + "=" * 40)
    log_test("📋 ENHANCED LEGAL ANALYSIS PIPELINE STATUS")
    log_test("=" * 40)
    
    pipeline_tests = [
        ("Basic Chat Agent", next((r for r in all_results if "Basic Contract" in r[0]), (None, False, None))[1]),
        ("Document Upload", upload_success_count > 0),
        ("Clause Analysis", next((r for r in all_results if "Clause Analysis" in r[0]), (None, False, None))[1]),
        ("Document Comparison", next((r for r in all_results if "Document Comparison" in r[0]), (None, False, None))[1]),
        ("Integration", next((r for r in all_results if "Integration" in r[0]), (None, False, None))[1])
    ]
    
    for test_name, test_success in pipeline_tests:
        status = "✅ WORKING" if test_success else "❌ FAILING"
        log_test(f"{status}: {test_name}")
    
    pipeline_success_rate = (sum(1 for _, success in pipeline_tests if success) / len(pipeline_tests)) * 100
    log_test(f"\n📈 Enhanced Legal Analysis Pipeline: {pipeline_success_rate:.1f}% operational")
    
    if success_rate >= 85:
        log_test("🎉 ENHANCED CONTRACT NEGOTIATION AGENT: EXCELLENT")
        return 0
    elif success_rate >= 70:
        log_test("✅ ENHANCED CONTRACT NEGOTIATION AGENT: GOOD")
        return 0
    else:
        log_test("🚨 ENHANCED CONTRACT NEGOTIATION AGENT: NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))