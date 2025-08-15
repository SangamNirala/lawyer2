#!/usr/bin/env python3
"""
Phase 2A Focused Backend Testing
Testing specific issues mentioned in review request:
1. Legal QA is_voice_session boolean validation
2. Legal Research Engine stats timeout/warmup
3. Regression checks
"""

import requests
import json
import time
import sys
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://legal-timeout-fix.preview.emergentagent.com/api"

def test_legal_qa_is_voice_session_validation():
    """Test POST /api/legal-qa/ask for is_voice_session Pydantic boolean validation"""
    print("=" * 80)
    print("TESTING: Legal QA is_voice_session Boolean Validation")
    print("=" * 80)
    
    results = []
    
    # Test 1: is_voice: false with session_id
    print("\n1. Testing is_voice: false with session_id")
    test_data = {
        "question": "What is consideration in contract law?",
        "session_id": "abc123",
        "is_voice": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/legal-qa/ask", json=test_data, timeout=30)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check is_voice_session field
            is_voice_session = data.get('is_voice_session')
            print(f"is_voice_session value: {is_voice_session} (type: {type(is_voice_session)})")
            
            if isinstance(is_voice_session, bool) and is_voice_session == False:
                print("✅ PASS: is_voice_session is strictly boolean false")
                results.append(("Test 1 - is_voice false", True, f"is_voice_session correctly set to {is_voice_session}"))
            else:
                print(f"❌ FAIL: is_voice_session should be boolean false, got {is_voice_session} ({type(is_voice_session)})")
                results.append(("Test 1 - is_voice false", False, f"Expected boolean false, got {is_voice_session} ({type(is_voice_session)})"))
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            results.append(("Test 1 - is_voice false", False, f"HTTP {response.status_code}: {response.text[:200]}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append(("Test 1 - is_voice false", False, f"Exception: {str(e)}"))
    
    # Test 2: is_voice: true without session_id
    print("\n2. Testing is_voice: true without session_id")
    test_data = {
        "question": "Explain promissory estoppel.",
        "is_voice": True
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/legal-qa/ask", json=test_data, timeout=30)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check is_voice_session field and session_id generation
            is_voice_session = data.get('is_voice_session')
            session_id = data.get('session_id')
            
            print(f"is_voice_session value: {is_voice_session} (type: {type(is_voice_session)})")
            print(f"session_id value: {session_id}")
            
            if isinstance(is_voice_session, bool) and is_voice_session == True:
                if session_id and session_id.startswith("voice_session_"):
                    print("✅ PASS: is_voice_session is boolean true and session_id generated correctly")
                    results.append(("Test 2 - is_voice true", True, f"is_voice_session: {is_voice_session}, session_id: {session_id}"))
                else:
                    print(f"❌ FAIL: session_id should start with 'voice_session_', got {session_id}")
                    results.append(("Test 2 - is_voice true", False, f"Invalid session_id: {session_id}"))
            else:
                print(f"❌ FAIL: is_voice_session should be boolean true, got {is_voice_session} ({type(is_voice_session)})")
                results.append(("Test 2 - is_voice true", False, f"Expected boolean true, got {is_voice_session} ({type(is_voice_session)})"))
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            results.append(("Test 2 - is_voice true", False, f"HTTP {response.status_code}: {response.text[:200]}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append(("Test 2 - is_voice true", False, f"Exception: {str(e)}"))
    
    # Test 3: is_voice: false with voice_session_id (should detect as voice)
    print("\n3. Testing is_voice: false with voice_session_id (should detect as voice)")
    test_data = {
        "question": "What are remedies for breach?",
        "session_id": "voice_session_1234567890_1234",
        "is_voice": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/legal-qa/ask", json=test_data, timeout=30)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check is_voice_session field - should be true due to session_id detection
            is_voice_session = data.get('is_voice_session')
            print(f"is_voice_session value: {is_voice_session} (type: {type(is_voice_session)})")
            
            if isinstance(is_voice_session, bool) and is_voice_session == True:
                print("✅ PASS: is_voice_session correctly detected as true from session_id")
                results.append(("Test 3 - voice session detection", True, f"is_voice_session correctly detected: {is_voice_session}"))
            else:
                print(f"❌ FAIL: is_voice_session should be boolean true (detected from session_id), got {is_voice_session} ({type(is_voice_session)})")
                results.append(("Test 3 - voice session detection", False, f"Expected boolean true, got {is_voice_session} ({type(is_voice_session)})"))
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            results.append(("Test 3 - voice session detection", False, f"HTTP {response.status_code}: {response.text[:200]}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append(("Test 3 - voice session detection", False, f"Exception: {str(e)}"))
    
    return results

def test_legal_research_engine_stats():
    """Test GET /api/legal-research-engine/stats for timeout/warmup issues"""
    print("=" * 80)
    print("TESTING: Legal Research Engine Stats Timeout/Warmup")
    print("=" * 80)
    
    results = []
    
    print("\n1. Testing GET /api/legal-research-engine/stats")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/legal-research-engine/stats", timeout=2.5)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            status = data.get('status')
            print(f"Status: {status}")
            
            if status == "operational":
                # Check for precedence_matching_stats
                if 'precedence_matching_stats' in data:
                    print("✅ PASS: Status operational with precedence_matching_stats present")
                    results.append(("Legal Research Engine Stats", True, f"Operational status with stats, response time: {response_time:.3f}s"))
                else:
                    print("❌ FAIL: precedence_matching_stats missing from operational response")
                    results.append(("Legal Research Engine Stats", False, "precedence_matching_stats missing"))
            elif status == "degraded":
                message = data.get('message', '')
                if "warmup in progress" in message.lower():
                    print("✅ PASS: Status degraded with warmup message")
                    results.append(("Legal Research Engine Stats", True, f"Degraded status (warmup), response time: {response_time:.3f}s"))
                else:
                    print(f"❌ FAIL: Unexpected degraded message: {message}")
                    results.append(("Legal Research Engine Stats", False, f"Unexpected degraded message: {message}"))
            elif status == "unavailable":
                message = data.get('message', '')
                if "not available" in message.lower():
                    print("✅ PASS: Status unavailable with appropriate message")
                    results.append(("Legal Research Engine Stats", True, f"Unavailable status, response time: {response_time:.3f}s"))
                else:
                    print(f"❌ FAIL: Unexpected unavailable message: {message}")
                    results.append(("Legal Research Engine Stats", False, f"Unexpected unavailable message: {message}"))
            else:
                print(f"❌ FAIL: Unexpected status: {status}")
                results.append(("Legal Research Engine Stats", False, f"Unexpected status: {status}"))
                
            # Check response time
            if response_time < 2.5:
                print(f"✅ PASS: Response time {response_time:.3f}s < 2.5s threshold")
            else:
                print(f"❌ FAIL: Response time {response_time:.3f}s >= 2.5s threshold")
                
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            results.append(("Legal Research Engine Stats", False, f"HTTP {response.status_code}: {response.text[:200]}"))
            
    except requests.exceptions.Timeout:
        print("❌ FAIL: Request timed out (>2.5s)")
        results.append(("Legal Research Engine Stats", False, "Request timed out (>2.5s)"))
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append(("Legal Research Engine Stats", False, f"Exception: {str(e)}"))
    
    return results

def test_regression_checks():
    """Test regression checks for other legal endpoints"""
    print("=" * 80)
    print("TESTING: Regression Checks")
    print("=" * 80)
    
    results = []
    
    # Test 1: GET /api/legal-qa/stats
    print("\n1. Testing GET /api/legal-qa/stats")
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/legal-qa/stats", timeout=10)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print("✅ PASS: Legal QA stats endpoint working")
            results.append(("Legal QA Stats", True, f"Working, response time: {response_time:.3f}s"))
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            results.append(("Legal QA Stats", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append(("Legal QA Stats", False, f"Exception: {str(e)}"))
    
    # Test 2: GET /api/legal-qa/knowledge-base/stats
    print("\n2. Testing GET /api/legal-qa/knowledge-base/stats")
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/legal-qa/knowledge-base/stats", timeout=10)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            print("✅ PASS: Legal QA knowledge base stats endpoint working")
            results.append(("Legal QA Knowledge Base Stats", True, f"Working, response time: {response_time:.3f}s"))
        else:
            print(f"❌ FAIL: Expected 200, got {response.status_code}")
            results.append(("Legal QA Knowledge Base Stats", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        results.append(("Legal QA Knowledge Base Stats", False, f"Exception: {str(e)}"))
    
    return results

def main():
    """Run all Phase 2A focused tests"""
    print("🎯 PHASE 2A FOCUSED BACKEND TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = []
    
    # Run all test suites
    all_results.extend(test_legal_qa_is_voice_session_validation())
    all_results.extend(test_legal_research_engine_stats())
    all_results.extend(test_regression_checks())
    
    # Summary
    print("\n" + "=" * 80)
    print("PHASE 2A FOCUSED TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, success, details in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not success:
            print(f"   Details: {details}")
    
    # Return success rate for external use
    return success_rate >= 80.0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)