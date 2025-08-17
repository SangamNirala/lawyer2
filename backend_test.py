#!/usr/bin/env python3
"""
Phase 2A Focused Backend Testing
Testing specific scenarios as requested in review:
1. POST /api/legal-qa/ask - three scenarios validating is_voice_session strict boolean
2. GET /api/legal-research-engine/stats - response time and structure 
3. GET /api/legal-qa/stats and GET /api/legal-qa/knowledge-base/stats - regression testing
"""

import requests
import json
import time
import sys
from datetime import datetime

# Use production URL from frontend .env
BASE_URL = "https://contract-genius-7.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_legal_qa_is_voice_session_validation():
    """
    Test POST /api/legal-qa/ask with three scenarios for is_voice_session validation
    Scenario 1: is_voice: false returns boolean false
    Scenario 2: is_voice: true returns boolean true with generated voice_session_id
    Scenario 3: voice_session_id detection overrides is_voice: false to return boolean true
    """
    log_test("🎯 TESTING: POST /api/legal-qa/ask - is_voice_session Pydantic validation")
    
    endpoint = f"{BASE_URL}/api/legal-qa/ask"
    results = []
    
    # Scenario 1: is_voice: false should return boolean false
    log_test("Scenario 1: Testing is_voice: false")
    payload1 = {
        "question": "What are the key elements of a valid contract?",
        "is_voice": False,
        "jurisdiction": "US",
        "legal_domain": "contract_law"
    }
    
    try:
        start_time = time.time()
        response1 = requests.post(endpoint, json=payload1, timeout=30)
        response_time1 = time.time() - start_time
        
        log_test(f"Response Status: {response1.status_code}")
        log_test(f"Response Time: {response_time1:.3f}s")
        
        if response1.status_code == 200:
            data1 = response1.json()
            is_voice_session = data1.get('is_voice_session')
            log_test(f"is_voice_session value: {is_voice_session} (type: {type(is_voice_session)})")
            
            if isinstance(is_voice_session, bool) and is_voice_session == False:
                log_test("✅ PASS: is_voice_session correctly returned as boolean false")
                results.append(("Scenario 1", True, f"Boolean false returned correctly: {is_voice_session}"))
            else:
                log_test(f"❌ FAIL: Expected boolean false, got {is_voice_session} ({type(is_voice_session)})")
                results.append(("Scenario 1", False, f"Expected boolean false, got {is_voice_session} ({type(is_voice_session)})"))
        else:
            log_test(f"❌ FAIL: HTTP {response1.status_code} - {response1.text}")
            results.append(("Scenario 1", False, f"HTTP {response1.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ ERROR: Scenario 1 failed - {str(e)}")
        results.append(("Scenario 1", False, f"Exception: {str(e)}"))
    
    # Scenario 2: is_voice: true should return boolean true with voice_session_id
    log_test("\nScenario 2: Testing is_voice: true")
    payload2 = {
        "question": "What are the requirements for a non-disclosure agreement?",
        "is_voice": True,
        "jurisdiction": "US",
        "legal_domain": "contract_law"
    }
    
    try:
        start_time = time.time()
        response2 = requests.post(endpoint, json=payload2, timeout=30)
        response_time2 = time.time() - start_time
        
        log_test(f"Response Status: {response2.status_code}")
        log_test(f"Response Time: {response_time2:.3f}s")
        
        if response2.status_code == 200:
            data2 = response2.json()
            is_voice_session = data2.get('is_voice_session')
            voice_session_id = data2.get('voice_session_id')
            
            log_test(f"is_voice_session value: {is_voice_session} (type: {type(is_voice_session)})")
            log_test(f"voice_session_id: {voice_session_id}")
            
            if isinstance(is_voice_session, bool) and is_voice_session == True and voice_session_id:
                log_test("✅ PASS: is_voice_session correctly returned as boolean true with voice_session_id")
                results.append(("Scenario 2", True, f"Boolean true with voice_session_id: {voice_session_id}"))
            else:
                log_test(f"❌ FAIL: Expected boolean true with voice_session_id, got is_voice_session={is_voice_session}, voice_session_id={voice_session_id}")
                results.append(("Scenario 2", False, f"Expected boolean true with voice_session_id"))
        else:
            log_test(f"❌ FAIL: HTTP {response2.status_code} - {response2.text}")
            results.append(("Scenario 2", False, f"HTTP {response2.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ ERROR: Scenario 2 failed - {str(e)}")
        results.append(("Scenario 2", False, f"Exception: {str(e)}"))
    
    # Scenario 3: voice_session_id detection should override is_voice: false
    log_test("\nScenario 3: Testing voice_session_id detection override")
    payload3 = {
        "question": "What are the elements of employment law compliance?",
        "is_voice": False,
        "voice_session_id": "voice_session_test_12345",
        "jurisdiction": "US",
        "legal_domain": "employment_law"
    }
    
    try:
        start_time = time.time()
        response3 = requests.post(endpoint, json=payload3, timeout=30)
        response_time3 = time.time() - start_time
        
        log_test(f"Response Status: {response3.status_code}")
        log_test(f"Response Time: {response_time3:.3f}s")
        
        if response3.status_code == 200:
            data3 = response3.json()
            is_voice_session = data3.get('is_voice_session')
            returned_voice_session_id = data3.get('voice_session_id')
            
            log_test(f"is_voice_session value: {is_voice_session} (type: {type(is_voice_session)})")
            log_test(f"voice_session_id: {returned_voice_session_id}")
            
            if isinstance(is_voice_session, bool) and is_voice_session == True:
                log_test("✅ PASS: voice_session_id correctly overrode is_voice: false to return boolean true")
                results.append(("Scenario 3", True, f"Override successful, returned boolean true"))
            else:
                log_test(f"❌ FAIL: Expected boolean true due to voice_session_id override, got {is_voice_session}")
                results.append(("Scenario 3", False, f"Override failed, got {is_voice_session}"))
        else:
            log_test(f"❌ FAIL: HTTP {response3.status_code} - {response3.text}")
            results.append(("Scenario 3", False, f"HTTP {response3.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ ERROR: Scenario 3 failed - {str(e)}")
        results.append(("Scenario 3", False, f"Exception: {str(e)}"))
    
    return results

def test_legal_research_engine_stats():
    """
    Test GET /api/legal-research-engine/stats for response time and structure
    Should return operational/degraded/unavailable status within reasonable time
    """
    log_test("\n🎯 TESTING: GET /api/legal-research-engine/stats - response time and structure")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/stats"
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=5)  # 5 second timeout to test for hanging
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response_time > 2.5:
            log_test(f"⚠️  WARNING: Response time {response_time:.3f}s exceeds 2.5s threshold")
        else:
            log_test(f"✅ GOOD: Response time {response_time:.3f}s is within acceptable range")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Response Body: {json.dumps(data, indent=2)}")
            
            # Check for expected structure
            status = data.get('status')
            message = data.get('message')
            
            if status in ['operational', 'degraded', 'unavailable']:
                log_test(f"✅ PASS: Valid status '{status}' returned")
                return True, f"Status: {status}, Response time: {response_time:.3f}s"
            else:
                log_test(f"❌ FAIL: Invalid status '{status}', expected operational/degraded/unavailable")
                return False, f"Invalid status: {status}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code} error"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>5s) - endpoint may be hanging")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_legal_qa_stats_regression():
    """
    Test GET /api/legal-qa/stats and GET /api/legal-qa/knowledge-base/stats for regression
    Ensure these endpoints still work correctly after Phase 2A changes
    """
    log_test("\n🎯 TESTING: Legal QA Stats Regression Testing")
    
    results = []
    
    # Test /api/legal-qa/stats
    log_test("Testing GET /api/legal-qa/stats")
    endpoint1 = f"{BASE_URL}/api/legal-qa/stats"
    
    try:
        start_time = time.time()
        response1 = requests.get(endpoint1, timeout=10)
        response_time1 = time.time() - start_time
        
        log_test(f"Response Status: {response1.status_code}")
        log_test(f"Response Time: {response_time1:.3f}s")
        
        if response1.status_code == 200:
            data1 = response1.json()
            log_test(f"Response Body: {json.dumps(data1, indent=2)}")
            
            # Check for expected fields
            expected_fields = ['vector_db', 'embeddings_model', 'total_documents']
            missing_fields = [field for field in expected_fields if field not in data1]
            
            if not missing_fields:
                log_test("✅ PASS: /api/legal-qa/stats working correctly")
                results.append(("legal-qa/stats", True, f"All expected fields present, {response_time1:.3f}s"))
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                results.append(("legal-qa/stats", False, f"Missing fields: {missing_fields}"))
        else:
            log_test(f"❌ FAIL: HTTP {response1.status_code} - {response1.text}")
            results.append(("legal-qa/stats", False, f"HTTP {response1.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        results.append(("legal-qa/stats", False, f"Exception: {str(e)}"))
    
    # Test /api/legal-qa/knowledge-base/stats
    log_test("\nTesting GET /api/legal-qa/knowledge-base/stats")
    endpoint2 = f"{BASE_URL}/api/legal-qa/knowledge-base/stats"
    
    try:
        start_time = time.time()
        response2 = requests.get(endpoint2, timeout=10)
        response_time2 = time.time() - start_time
        
        log_test(f"Response Status: {response2.status_code}")
        log_test(f"Response Time: {response_time2:.3f}s")
        
        if response2.status_code == 200:
            data2 = response2.json()
            log_test(f"Response Body: {json.dumps(data2, indent=2)}")
            
            # Check for expected fields
            expected_fields = ['total_documents', 'jurisdictions', 'legal_domains']
            missing_fields = [field for field in expected_fields if field not in data2]
            
            if not missing_fields:
                log_test("✅ PASS: /api/legal-qa/knowledge-base/stats working correctly")
                results.append(("knowledge-base/stats", True, f"All expected fields present, {response_time2:.3f}s"))
            else:
                log_test(f"❌ FAIL: Missing fields: {missing_fields}")
                results.append(("knowledge-base/stats", False, f"Missing fields: {missing_fields}"))
        else:
            log_test(f"❌ FAIL: HTTP {response2.status_code} - {response2.text}")
            results.append(("knowledge-base/stats", False, f"HTTP {response2.status_code} error"))
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        results.append(("knowledge-base/stats", False, f"Exception: {str(e)}"))
    
    return results

def main():
    """Run all Phase 2A focused backend tests"""
    log_test("🚀 STARTING PHASE 2A FOCUSED BACKEND TESTING")
    log_test(f"Base URL: {BASE_URL}")
    log_test("=" * 80)
    
    all_results = []
    
    # Test 1: Legal QA is_voice_session validation
    voice_session_results = test_legal_qa_is_voice_session_validation()
    all_results.extend(voice_session_results)
    
    # Test 2: Legal Research Engine stats
    research_engine_result = test_legal_research_engine_stats()
    all_results.append(("Legal Research Engine Stats", research_engine_result[0], research_engine_result[1]))
    
    # Test 3: Legal QA stats regression
    regression_results = test_legal_qa_stats_regression()
    all_results.extend(regression_results)
    
    # Summary
    log_test("\n" + "=" * 80)
    log_test("📊 PHASE 2A TESTING SUMMARY")
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
    
    if success_rate >= 80:
        log_test("🎉 PHASE 2A TESTING: SUCCESSFUL")
        return 0
    else:
        log_test("🚨 PHASE 2A TESTING: NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(main())