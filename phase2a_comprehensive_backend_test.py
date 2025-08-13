#!/usr/bin/env python3
"""
Phase 2A Backend Fixes Comprehensive Testing
============================================

This script tests all Phase 2A backend fixes as specified in the review request:

CRITICAL TEST SCENARIOS:
A) LEGAL QA VOICE SESSION ID SCENARIOS (3 scenarios)
B) STATS ENDPOINTS FIELD MAPPING VERIFICATION (2 endpoints)  
C) LEGAL RESEARCH ENGINE REGRESSION CHECK (1 endpoint)

Total: 6 test scenarios for 100% success rate verification
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"

def log_test(message, level="INFO"):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_legal_qa_voice_session_scenarios():
    """
    Test all 3 Legal QA Voice Session ID scenarios that were failing
    """
    log_test("=" * 80)
    log_test("TESTING LEGAL QA VOICE SESSION ID SCENARIOS")
    log_test("=" * 80)
    
    results = []
    
    # Scenario 1: is_voice: false, no voice_session_id
    log_test("SCENARIO 1: is_voice: false, no voice_session_id")
    log_test("Expected: is_voice_session: false (boolean), voice_session_id: null")
    
    try:
        payload = {
            "question": "What are the key elements of a valid contract?",
            "is_voice": False,
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }
        
        response = requests.post(f"{BACKEND_URL}/legal-qa/ask", json=payload, timeout=30)
        log_test(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            is_voice_session = data.get('is_voice_session')
            voice_session_id = data.get('voice_session_id')
            
            log_test(f"is_voice_session: {is_voice_session} (type: {type(is_voice_session)})")
            log_test(f"voice_session_id: {voice_session_id}")
            
            # Verify boolean false (not string/empty)
            if is_voice_session is False and voice_session_id is None:
                log_test("✅ SCENARIO 1 PASSED: Correct boolean false and null voice_session_id")
                results.append(("Scenario 1", True, "is_voice: false returns boolean false, voice_session_id: null"))
            else:
                log_test(f"❌ SCENARIO 1 FAILED: Expected boolean false and null, got {is_voice_session} and {voice_session_id}")
                results.append(("Scenario 1", False, f"Expected boolean false/null, got {is_voice_session}/{voice_session_id}"))
        else:
            log_test(f"❌ SCENARIO 1 FAILED: HTTP {response.status_code} - {response.text}")
            results.append(("Scenario 1", False, f"HTTP {response.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ SCENARIO 1 ERROR: {str(e)}")
        results.append(("Scenario 1", False, f"Exception: {str(e)}"))
    
    log_test("-" * 60)
    
    # Scenario 2: is_voice: true, no voice_session_id
    log_test("SCENARIO 2: is_voice: true, no voice_session_id")
    log_test("Expected: is_voice_session: true (boolean), voice_session_id: generated (starts with 'voice_session_')")
    
    try:
        payload = {
            "question": "Explain the statute of limitations for contract disputes",
            "is_voice": True,
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }
        
        response = requests.post(f"{BACKEND_URL}/legal-qa/ask", json=payload, timeout=30)
        log_test(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            is_voice_session = data.get('is_voice_session')
            voice_session_id = data.get('voice_session_id')
            
            log_test(f"is_voice_session: {is_voice_session} (type: {type(is_voice_session)})")
            log_test(f"voice_session_id: {voice_session_id}")
            
            # Verify boolean true and generated voice_session_id
            if (is_voice_session is True and 
                voice_session_id is not None and 
                isinstance(voice_session_id, str) and 
                voice_session_id.startswith('voice_session_')):
                log_test("✅ SCENARIO 2 PASSED: Correct boolean true and generated voice_session_id")
                results.append(("Scenario 2", True, f"is_voice: true returns boolean true, voice_session_id: {voice_session_id}"))
            else:
                log_test(f"❌ SCENARIO 2 FAILED: Expected boolean true and voice_session_* ID, got {is_voice_session} and {voice_session_id}")
                results.append(("Scenario 2", False, f"Expected boolean true/voice_session_*, got {is_voice_session}/{voice_session_id}"))
        else:
            log_test(f"❌ SCENARIO 2 FAILED: HTTP {response.status_code} - {response.text}")
            results.append(("Scenario 2", False, f"HTTP {response.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ SCENARIO 2 ERROR: {str(e)}")
        results.append(("Scenario 2", False, f"Exception: {str(e)}"))
    
    log_test("-" * 60)
    
    # Scenario 3: voice_session_id provided, is_voice: false (override test)
    log_test("SCENARIO 3: voice_session_id: 'test_voice_123', is_voice: false")
    log_test("Expected: is_voice_session: true (override), voice_session_id: 'test_voice_123'")
    
    try:
        payload = {
            "question": "What is the difference between express and implied contracts?",
            "is_voice": False,  # This should be overridden
            "voice_session_id": "test_voice_123",
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }
        
        response = requests.post(f"{BACKEND_URL}/legal-qa/ask", json=payload, timeout=30)
        log_test(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            is_voice_session = data.get('is_voice_session')
            voice_session_id = data.get('voice_session_id')
            
            log_test(f"is_voice_session: {is_voice_session} (type: {type(is_voice_session)})")
            log_test(f"voice_session_id: {voice_session_id}")
            
            # Verify override works: is_voice_session should be true regardless of is_voice flag
            if (is_voice_session is True and voice_session_id == "test_voice_123"):
                log_test("✅ SCENARIO 3 PASSED: Override works correctly - is_voice_session: true despite is_voice: false")
                results.append(("Scenario 3", True, "voice_session_id override works correctly"))
            else:
                log_test(f"❌ SCENARIO 3 FAILED: Override failed, got {is_voice_session} and {voice_session_id}")
                results.append(("Scenario 3", False, f"Override failed: {is_voice_session}/{voice_session_id}"))
        else:
            log_test(f"❌ SCENARIO 3 FAILED: HTTP {response.status_code} - {response.text}")
            results.append(("Scenario 3", False, f"HTTP {response.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ SCENARIO 3 ERROR: {str(e)}")
        results.append(("Scenario 3", False, f"Exception: {str(e)}"))
    
    return results

def test_stats_endpoints_field_mapping():
    """
    Test Stats Endpoints Field Mapping Verification
    """
    log_test("=" * 80)
    log_test("TESTING STATS ENDPOINTS FIELD MAPPING VERIFICATION")
    log_test("=" * 80)
    
    results = []
    
    # Test 4: Legal QA Stats
    log_test("TEST 4: Legal QA Stats - GET /api/legal-qa/stats")
    log_test("Expected: Should include both 'indexed_documents' AND 'total_documents' fields")
    
    try:
        response = requests.get(f"{BACKEND_URL}/legal-qa/stats", timeout=15)
        log_test(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Response keys: {list(data.keys())}")
            
            indexed_documents = data.get('indexed_documents')
            total_documents = data.get('total_documents')
            
            log_test(f"indexed_documents: {indexed_documents}")
            log_test(f"total_documents: {total_documents}")
            
            if indexed_documents is not None and total_documents is not None:
                if indexed_documents == total_documents:
                    log_test("✅ TEST 4 PASSED: Both fields present with same values")
                    results.append(("Legal QA Stats", True, f"Both fields present: indexed_documents={indexed_documents}, total_documents={total_documents}"))
                else:
                    log_test(f"⚠️ TEST 4 WARNING: Fields present but different values: {indexed_documents} vs {total_documents}")
                    results.append(("Legal QA Stats", True, f"Both fields present but different values: {indexed_documents} vs {total_documents}"))
            else:
                log_test(f"❌ TEST 4 FAILED: Missing fields - indexed_documents: {indexed_documents}, total_documents: {total_documents}")
                results.append(("Legal QA Stats", False, f"Missing fields: indexed_documents={indexed_documents}, total_documents={total_documents}"))
        else:
            log_test(f"❌ TEST 4 FAILED: HTTP {response.status_code} - {response.text}")
            results.append(("Legal QA Stats", False, f"HTTP {response.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ TEST 4 ERROR: {str(e)}")
        results.append(("Legal QA Stats", False, f"Exception: {str(e)}"))
    
    log_test("-" * 60)
    
    # Test 5: Knowledge Base Stats
    log_test("TEST 5: Knowledge Base Stats - GET /api/legal-qa/knowledge-base/stats")
    log_test("Expected: Should include both 'by_jurisdiction' + 'jurisdictions' AND 'by_legal_domain' + 'legal_domains'")
    
    try:
        response = requests.get(f"{BACKEND_URL}/legal-qa/knowledge-base/stats", timeout=15)
        log_test(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Response keys: {list(data.keys())}")
            
            by_jurisdiction = data.get('by_jurisdiction')
            jurisdictions = data.get('jurisdictions')
            by_legal_domain = data.get('by_legal_domain')
            legal_domains = data.get('legal_domains')
            
            log_test(f"by_jurisdiction: {by_jurisdiction}")
            log_test(f"jurisdictions: {jurisdictions}")
            log_test(f"by_legal_domain: {by_legal_domain}")
            log_test(f"legal_domains: {legal_domains}")
            
            # Check if both original and alias fields are present
            jurisdiction_check = by_jurisdiction is not None and jurisdictions is not None
            domain_check = by_legal_domain is not None and legal_domains is not None
            
            if jurisdiction_check and domain_check:
                log_test("✅ TEST 5 PASSED: All alias fields present")
                results.append(("Knowledge Base Stats", True, "All alias fields present: by_jurisdiction/jurisdictions and by_legal_domain/legal_domains"))
            else:
                missing_fields = []
                if not jurisdiction_check:
                    missing_fields.append("jurisdiction fields")
                if not domain_check:
                    missing_fields.append("domain fields")
                log_test(f"❌ TEST 5 FAILED: Missing {', '.join(missing_fields)}")
                results.append(("Knowledge Base Stats", False, f"Missing {', '.join(missing_fields)}"))
        else:
            log_test(f"❌ TEST 5 FAILED: HTTP {response.status_code} - {response.text}")
            results.append(("Knowledge Base Stats", False, f"HTTP {response.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ TEST 5 ERROR: {str(e)}")
        results.append(("Knowledge Base Stats", False, f"Exception: {str(e)}"))
    
    return results

def test_legal_research_engine_regression():
    """
    Test Legal Research Engine Regression Check
    """
    log_test("=" * 80)
    log_test("TESTING LEGAL RESEARCH ENGINE REGRESSION CHECK")
    log_test("=" * 80)
    
    results = []
    
    # Test 6: Legal Research Engine Stats
    log_test("TEST 6: Legal Research Engine Stats - GET /api/legal-research-engine/stats")
    log_test("Expected: Should respond quickly (< 2s) with 'operational' or 'unavailable' status")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/legal-research-engine/stats", timeout=5)
        response_time = time.time() - start_time
        
        log_test(f"Status Code: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Response: {json.dumps(data, indent=2)}")
            
            status = data.get('status', 'unknown')
            log_test(f"Status: {status}")
            
            # Check response time and status
            if response_time < 2.0:
                if status in ['operational', 'unavailable']:
                    log_test(f"✅ TEST 6 PASSED: Quick response ({response_time:.3f}s) with valid status '{status}'")
                    results.append(("Legal Research Engine Stats", True, f"Quick response ({response_time:.3f}s) with status '{status}'"))
                else:
                    log_test(f"⚠️ TEST 6 WARNING: Quick response but unexpected status '{status}'")
                    results.append(("Legal Research Engine Stats", True, f"Quick response ({response_time:.3f}s) but unexpected status '{status}'"))
            else:
                log_test(f"❌ TEST 6 FAILED: Response too slow ({response_time:.3f}s)")
                results.append(("Legal Research Engine Stats", False, f"Response too slow ({response_time:.3f}s)"))
        else:
            log_test(f"❌ TEST 6 FAILED: HTTP {response.status_code} - {response.text}")
            results.append(("Legal Research Engine Stats", False, f"HTTP {response.status_code} error"))
            
    except requests.exceptions.Timeout:
        log_test("❌ TEST 6 FAILED: Request timed out (> 5s)")
        results.append(("Legal Research Engine Stats", False, "Request timed out"))
    except Exception as e:
        log_test(f"❌ TEST 6 ERROR: {str(e)}")
        results.append(("Legal Research Engine Stats", False, f"Exception: {str(e)}"))
    
    return results

def main():
    """
    Execute comprehensive Phase 2A backend testing
    """
    log_test("🎯 PHASE 2A BACKEND FIXES COMPREHENSIVE TESTING STARTED")
    log_test(f"Backend URL: {BACKEND_URL}")
    log_test(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # Execute all test scenarios
    voice_results = test_legal_qa_voice_session_scenarios()
    all_results.extend(voice_results)
    
    stats_results = test_stats_endpoints_field_mapping()
    all_results.extend(stats_results)
    
    regression_results = test_legal_research_engine_regression()
    all_results.extend(regression_results)
    
    # Calculate success rate
    total_tests = len(all_results)
    passed_tests = sum(1 for _, passed, _ in all_results if passed)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    log_test("=" * 80)
    log_test("PHASE 2A COMPREHENSIVE TEST RESULTS SUMMARY")
    log_test("=" * 80)
    
    for test_name, passed, details in all_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        log_test(f"{status}: {test_name} - {details}")
    
    log_test("-" * 80)
    log_test(f"SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100.0:
        log_test("🎉 ALL PHASE 2A FIXES WORKING PERFECTLY!")
        log_test("✅ Voice session scenarios: All 3 working correctly")
        log_test("✅ Stats field mapping: Both endpoints have alias fields")
        log_test("✅ Legal Research Engine: No hanging/timeout issues")
    else:
        log_test("🚨 SOME PHASE 2A FIXES STILL HAVE ISSUES")
        failed_tests = [name for name, passed, _ in all_results if not passed]
        log_test(f"❌ Failed tests: {', '.join(failed_tests)}")
    
    log_test("🎯 PHASE 2A BACKEND TESTING COMPLETED")
    
    return success_rate, all_results

if __name__ == "__main__":
    success_rate, results = main()
    
    # Exit with appropriate code
    if success_rate == 100.0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Some tests failed