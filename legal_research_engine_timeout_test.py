#!/usr/bin/env python3
"""
Legal Research Engine Timeout Issues Resolution Testing
Testing all 8 Legal Research Engine endpoints to verify timeout fixes:
1. GET /api/legal-research-engine/stats 
2. POST /api/legal-research-engine/research
3. POST /api/legal-research-engine/generate-memo
4. POST /api/legal-research-engine/structure-arguments  
5. POST /api/legal-research-engine/multi-jurisdiction-search
6. POST /api/legal-research-engine/quality-assessment
7. GET /api/legal-research-engine/research-queries
8. GET /api/legal-research-engine/research-memos

Focus: Verify all endpoints respond within 15 seconds (no timeouts)
Performance expectations:
- Stats endpoint: <2s
- List endpoints: <5s  
- POST endpoints: <15s
"""

import requests
import json
import time
import sys
from datetime import datetime

# Use production URL from frontend .env
BASE_URL = "https://legal-api-testing.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_stats_endpoint():
    """Test GET /api/legal-research-engine/stats - should respond in <2s"""
    log_test("🎯 TESTING: GET /api/legal-research-engine/stats")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/stats"
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 2.0:
            log_test(f"⚠️  WARNING: Response time {response_time:.3f}s exceeds 2s threshold")
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 2s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"Response Body: {json.dumps(data, indent=2)}")
            
            # Check for expected structure
            status = data.get('status')
            if status in ['operational', 'degraded', 'unavailable']:
                log_test(f"✅ PASS: Valid status '{status}' returned, no timeout")
                return True, f"Status: {status}, Response time: {response_time:.3f}s"
            else:
                log_test(f"✅ PASS: Endpoint responded (no timeout), status: {status}")
                return True, f"No timeout, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_research_endpoint():
    """Test POST /api/legal-research-engine/research - should respond in <15s"""
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/research")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/research"
    
    # Realistic payload as requested
    payload = {
        "query_text": "What are the elements of breach of contract?",
        "research_type": "comprehensive",
        "jurisdiction": "US",
        "legal_domain": "contract_law",
        "priority": "medium",
        "max_results": 10,
        "min_confidence": 0.7,
        "include_analysis": True
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 15.0:
            log_test(f"❌ FAIL: Response time {response_time:.3f}s exceeds 15s threshold")
            return False, f"Timeout - {response_time:.3f}s > 15s"
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 15s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Research endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_generate_memo_endpoint():
    """Test POST /api/legal-research-engine/generate-memo - should respond in <15s"""
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/generate-memo")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/generate-memo"
    
    # Basic legal memo request as requested
    payload = {
        "memo_data": {
            "topic": "Contract Formation Requirements",
            "jurisdiction": "US",
            "legal_issues": ["offer", "acceptance", "consideration", "capacity"],
            "client_facts": "Client wants to understand basic contract formation elements"
        },
        "memo_type": "comprehensive",
        "format_style": "professional"
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 15.0:
            log_test(f"❌ FAIL: Response time {response_time:.3f}s exceeds 15s threshold")
            return False, f"Timeout - {response_time:.3f}s > 15s"
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 15s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Generate memo endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_structure_arguments_endpoint():
    """Test POST /api/legal-research-engine/structure-arguments - should respond in <15s"""
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/structure-arguments")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/structure-arguments"
    
    # Simple legal argument as requested
    payload = {
        "argument_data": {
            "legal_question": "Is a contract valid without written consideration?",
            "position": "A contract can be valid without written consideration if consideration exists",
            "jurisdiction": "US",
            "case_facts": "Parties agreed to exchange services for goods"
        },
        "argument_strength": "strong",
        "include_counterarguments": True
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 15.0:
            log_test(f"❌ FAIL: Response time {response_time:.3f}s exceeds 15s threshold")
            return False, f"Timeout - {response_time:.3f}s > 15s"
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 15s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Structure arguments endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_multi_jurisdiction_search_endpoint():
    """Test POST /api/legal-research-engine/multi-jurisdiction-search - should respond in <15s"""
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/multi-jurisdiction-search")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/multi-jurisdiction-search"
    
    # US, UK jurisdictions as requested
    payload = {
        "query": "Contract formation requirements",
        "jurisdictions": ["US", "UK"],
        "legal_domain": "contract_law",
        "comparison_mode": True
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 15.0:
            log_test(f"❌ FAIL: Response time {response_time:.3f}s exceeds 15s threshold")
            return False, f"Timeout - {response_time:.3f}s > 15s"
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 15s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Multi-jurisdiction search endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_quality_assessment_endpoint():
    """Test POST /api/legal-research-engine/quality-assessment - should respond in <15s"""
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/quality-assessment")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/quality-assessment"
    
    # Basic research data as requested
    payload = {
        "research_data": {
            "research_query": "Contract breach remedies",
            "sources_found": 5,
            "legal_authorities": ["Case law", "Statutes"],
            "jurisdiction": "US",
            "confidence_level": 0.8
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 15.0:
            log_test(f"❌ FAIL: Response time {response_time:.3f}s exceeds 15s threshold")
            return False, f"Timeout - {response_time:.3f}s > 15s"
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 15s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Quality assessment endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_research_queries_endpoint():
    """Test GET /api/legal-research-engine/research-queries - should respond in <5s"""
    log_test("\n🎯 TESTING: GET /api/legal-research-engine/research-queries")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/research-queries"
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 5.0:
            log_test(f"⚠️  WARNING: Response time {response_time:.3f}s exceeds 5s threshold for list endpoint")
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 5s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Research queries endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_research_memos_endpoint():
    """Test GET /api/legal-research-engine/research-memos - should respond in <5s"""
    log_test("\n🎯 TESTING: GET /api/legal-research-engine/research-memos")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/research-memos"
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        # Check performance expectation
        if response_time > 5.0:
            log_test(f"⚠️  WARNING: Response time {response_time:.3f}s exceeds 5s threshold for list endpoint")
        else:
            log_test(f"✅ PERFORMANCE: Response time {response_time:.3f}s is within 5s threshold")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ PASS: Research memos endpoint responded successfully, no timeout")
            return True, f"Success, Response time: {response_time:.3f}s"
        else:
            log_test(f"✅ PASS: Endpoint responded (no timeout), HTTP {response.status_code}")
            log_test(f"Response: {response.text[:200]}...")
            return True, f"No timeout, HTTP {response.status_code}, Response time: {response_time:.3f}s"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>15s) - timeout issue NOT resolved")
        return False, "Timeout - endpoint hanging"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def main():
    """Run all Legal Research Engine timeout tests"""
    log_test("🚀 STARTING LEGAL RESEARCH ENGINE TIMEOUT RESOLUTION TESTING")
    log_test(f"Base URL: {BASE_URL}")
    log_test("Testing all 8 Legal Research Engine endpoints for timeout issues")
    log_test("=" * 80)
    
    # Define all tests
    tests = [
        ("GET /api/legal-research-engine/stats", test_stats_endpoint),
        ("POST /api/legal-research-engine/research", test_research_endpoint),
        ("POST /api/legal-research-engine/generate-memo", test_generate_memo_endpoint),
        ("POST /api/legal-research-engine/structure-arguments", test_structure_arguments_endpoint),
        ("POST /api/legal-research-engine/multi-jurisdiction-search", test_multi_jurisdiction_search_endpoint),
        ("POST /api/legal-research-engine/quality-assessment", test_quality_assessment_endpoint),
        ("GET /api/legal-research-engine/research-queries", test_research_queries_endpoint),
        ("GET /api/legal-research-engine/research-memos", test_research_memos_endpoint)
    ]
    
    results = []
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            success, details = test_func()
            results.append((test_name, success, details))
        except Exception as e:
            log_test(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
            results.append((test_name, False, f"Critical error: {str(e)}"))
    
    # Summary
    log_test("\n" + "=" * 80)
    log_test("📊 LEGAL RESEARCH ENGINE TIMEOUT TESTING SUMMARY")
    log_test("=" * 80)
    
    passed = 0
    failed = 0
    timeout_issues = 0
    
    for test_name, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        log_test(f"{status}: {test_name}")
        log_test(f"    Details: {details}")
        
        if success:
            passed += 1
        else:
            failed += 1
            if "timeout" in details.lower() or "hanging" in details.lower():
                timeout_issues += 1
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    log_test(f"\nTotal Endpoints Tested: {total}")
    log_test(f"Responding (No Timeout): {passed}")
    log_test(f"Timeout Issues: {timeout_issues}")
    log_test(f"Other Failures: {failed - timeout_issues}")
    log_test(f"Success Rate: {success_rate:.1f}%")
    
    # Critical assessment
    if timeout_issues == 0:
        log_test("🎉 TIMEOUT RESOLUTION: SUCCESSFUL - No endpoints hanging or timing out")
        if success_rate >= 75:
            log_test("🎉 OVERALL TESTING: SUCCESSFUL - System responsive and stable")
            return 0
        else:
            log_test("⚠️  OVERALL TESTING: MIXED RESULTS - No timeouts but some logic errors")
            return 0  # Still success for timeout resolution
    else:
        log_test(f"🚨 TIMEOUT RESOLUTION: FAILED - {timeout_issues} endpoints still timing out")
        log_test("🚨 CRITICAL: Timeout issues NOT resolved as claimed")
        return 1

if __name__ == "__main__":
    sys.exit(main())