#!/usr/bin/env python3
"""
Phase 2A Backend Testing Script
Tests the Legal Research Engine backend functionality as specified in the review request.
"""

import requests
import time
import json
import sys
from datetime import datetime

# Backend URL
BACKEND_URL = "https://7505fd5e-29e4-43b6-a4da-c5add39ca139.preview.emergentagent.com/api"
LOCAL_BACKEND_URL = "http://localhost:8001/api"

# Choose which backend to test
BACKEND = BACKEND_URL  # Using correct external backend URL for testing

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(test_name, success, details="", response_time=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    time_info = f" ({response_time:.3f}s)" if response_time else ""
    print(f"{status} {test_name}{time_info}")
    if details:
        print(f"    Details: {details}")

def test_server_stats():
    """Test A) Server stats check: GET /api/legal-research-engine/stats"""
    print_header("TEST A: Server Stats Check")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND}/legal-research-engine/stats", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = ["status", "precedent_matching_stats"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print_result("Server Stats API", False, 
                           f"Missing required fields: {missing_fields}", response_time)
                return False
            
            # Check if operational
            operational = data.get("status") == "operational"
            has_stats = "precedent_matching_stats" in data
            
            if operational and has_stats:
                print_result("Server Stats API", True, 
                           f"Status: {data['status']}, ML Models loaded: {data.get('ml_models', {}).get('sentence_transformer_loaded', False)}", 
                           response_time)
                print(f"    Stats: {json.dumps(data['precedent_matching_stats'], indent=4)}")
                return True
            else:
                print_result("Server Stats API", False, 
                           f"Status: {data.get('status')}, Stats present: {has_stats}", response_time)
                return False
        else:
            print_result("Server Stats API", False, 
                        f"HTTP {response.status_code}: {response.text}", response_time)
            return False
            
    except Exception as e:
        print_result("Server Stats API", False, f"Exception: {str(e)}")
        return False

def test_background_enrichment():
    """Test B) Background enrichment trigger: POST /api/legal-research-engine/refresh-courtlistener"""
    print_header("TEST B: Background Enrichment Trigger")
    
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND}/legal-research-engine/refresh-courtlistener", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for expected response format
            if data.get("status") == "started":
                print_result("Background Enrichment Trigger", True, 
                           f"Message: {data.get('message')}", response_time)
                return True
            else:
                print_result("Background Enrichment Trigger", False, 
                           f"Unexpected status: {data.get('status')}", response_time)
                return False
        else:
            print_result("Background Enrichment Trigger", False, 
                        f"HTTP {response.status_code}: {response.text}", response_time)
            return False
            
    except Exception as e:
        print_result("Background Enrichment Trigger", False, f"Exception: {str(e)}")
        return False

def test_precedent_search_performance():
    """Test C) Immediate precedent search performance test with specific query case"""
    print_header("TEST C: Precedent Search Performance Test")
    
    test_query = "constitutional rights due process equal protection"
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND}/legal-research-engine/search-precedents",
            json={"query": test_query, "limit": 10},
            headers={"Content-Type": "application/json"},
            timeout=5  # 5 second timeout for performance requirement
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check response format
            required_fields = ["results", "query", "total_results", "search_time"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print_result("Precedent Search Performance", False, 
                           f"Missing required fields: {missing_fields}", response_time)
                return response_time
            
            # Check performance requirement (< 2 seconds)
            performance_ok = response_time < 2.0
            search_time = data.get("search_time", 0)
            
            status_msg = f"Query: '{test_query}', Results: {data['total_results']}, Search time: {search_time:.4f}s"
            
            if performance_ok:
                print_result("Precedent Search Performance", True, status_msg, response_time)
            else:
                print_result("Precedent Search Performance", False, 
                           f"PERFORMANCE ISSUE: {status_msg} (exceeded 2s limit)", response_time)
            
            return response_time
        else:
            print_result("Precedent Search Performance", False, 
                        f"HTTP {response.status_code}: {response.text}", response_time)
            return response_time
            
    except requests.exceptions.Timeout:
        print_result("Precedent Search Performance", False, 
                    "TIMEOUT: Request exceeded 5 seconds", 5.0)
        return 5.0
    except Exception as e:
        print_result("Precedent Search Performance", False, f"Exception: {str(e)}")
        return None

def test_precedent_search_after_delay():
    """Test D) Follow-up precedent search after 5 seconds to verify performance"""
    print_header("TEST D: Follow-up Precedent Search After 5 Seconds")
    
    print("Waiting 5 seconds before follow-up search...")
    time.sleep(5)
    
    test_query = "contract law breach damages"
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BACKEND}/legal-research-engine/search-precedents",
            json={"query": test_query, "limit": 10},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check performance requirement (< 2 seconds)
            performance_ok = response_time < 2.0
            search_time = data.get("search_time", 0)
            
            status_msg = f"Query: '{test_query}', Results: {data['total_results']}, Search time: {search_time:.4f}s"
            
            if performance_ok:
                print_result("Follow-up Precedent Search", True, status_msg, response_time)
            else:
                print_result("Follow-up Precedent Search", False, 
                           f"PERFORMANCE ISSUE: {status_msg} (exceeded 2s limit)", response_time)
            
            return response_time
        else:
            print_result("Follow-up Precedent Search", False, 
                        f"HTTP {response.status_code}: {response.text}", response_time)
            return response_time
            
    except requests.exceptions.Timeout:
        print_result("Follow-up Precedent Search", False, 
                    "TIMEOUT: Request exceeded 5 seconds", 5.0)
        return 5.0
    except Exception as e:
        print_result("Follow-up Precedent Search", False, f"Exception: {str(e)}")
        return None

def run_phase2a_tests():
    """Run all Phase 2A tests"""
    print_header("PHASE 2A BACKEND TESTING - LEGAL RESEARCH ENGINE")
    print(f"Backend URL: {BACKEND}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test A: Server stats
    results['server_stats'] = test_server_stats()
    
    # Test B: Background enrichment
    results['background_enrichment'] = test_background_enrichment()
    
    # Test C: Precedent search performance
    search_time_1 = test_precedent_search_performance()
    results['precedent_search_1'] = search_time_1 is not None and search_time_1 < 2.0
    
    # Test D: Follow-up precedent search
    search_time_2 = test_precedent_search_after_delay()
    results['precedent_search_2'] = search_time_2 is not None and search_time_2 < 2.0
    
    # Summary
    print_header("PHASE 2A TEST RESULTS SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if search_time_1 is not None and search_time_2 is not None:
        print(f"\nPerformance Analysis:")
        print(f"  First search time: {search_time_1:.4f}s")
        print(f"  Second search time: {search_time_2:.4f}s")
        if search_time_1 < 2.0 and search_time_2 < 2.0:
            print("  ✅ Both searches meet performance requirement (< 2 seconds)")
        else:
            print("  ❌ Performance requirement not met")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")
    
    # Return overall success
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_phase2a_tests()
    sys.exit(0 if success else 1)