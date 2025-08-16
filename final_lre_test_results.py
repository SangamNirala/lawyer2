#!/usr/bin/env python3
"""
Final Legal Research Engine Test Results
Comprehensive testing of all LRE endpoints with detailed analysis
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://mobile-test-complete.preview.emergentagent.com/api"

def test_endpoint_with_retry(method, endpoint, data=None, timeout=30, retries=2):
    """Test endpoint with retry logic"""
    url = f"{BACKEND_URL}{endpoint}"
    
    for attempt in range(retries + 1):
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response": response_data,
                    "attempt": attempt + 1
                }
            else:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response": response.text,
                    "attempt": attempt + 1
                }
                
        except requests.exceptions.Timeout:
            if attempt == retries:
                return {
                    "success": False,
                    "error": "TIMEOUT",
                    "response_time": timeout,
                    "attempt": attempt + 1
                }
            time.sleep(2)  # Wait before retry
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "attempt": attempt + 1
            }
    
    return {"success": False, "error": "Unknown", "response_time": 0, "attempt": retries + 1}

def validate_response_structure(response_data, expected_fields):
    """Validate response structure against expected fields"""
    if not isinstance(response_data, dict):
        return {"valid": False, "missing": expected_fields, "present": []}
    
    missing = []
    present = []
    
    for field in expected_fields:
        if "." in field:  # Handle nested fields
            parts = field.split(".")
            current = response_data
            found = True
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    found = False
                    break
            if found:
                present.append(field)
            else:
                missing.append(field)
        else:
            if field in response_data:
                present.append(field)
            else:
                missing.append(field)
    
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "present": present
    }

def main():
    print("🎯 FINAL LEGAL RESEARCH ENGINE TEST RESULTS")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().isoformat()}")
    print()
    
    # Define all test cases from the review request
    test_cases = [
        {
            "name": "GET /api/legal-research-engine/stats",
            "method": "GET",
            "endpoint": "/legal-research-engine/stats",
            "data": None,
            "timeout": 10,
            "expected_fields": ["status", "engine_stats", "system_health"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/research (valid research_type)",
            "method": "POST",
            "endpoint": "/legal-research-engine/research",
            "data": {
                "query_text": "Contract breach remedies analysis",
                "research_type": "comprehensive",
                "jurisdiction": "US",
                "legal_domain": "contract_law"
            },
            "timeout": 60,
            "expected_fields": ["id", "results", "confidence_score"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/research (invalid research_type fallback)",
            "method": "POST",
            "endpoint": "/legal-research-engine/research",
            "data": {
                "query_text": "Contract breach analysis",
                "research_type": "invalid_type_should_fallback",
                "jurisdiction": "US",
                "legal_domain": "contract_law"
            },
            "timeout": 60,
            "expected_fields": ["id", "results"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/precedent-search",
            "method": "POST",
            "endpoint": "/legal-research-engine/precedent-search",
            "data": {
                "query_case": {
                    "case_title": "Contract Breach Analysis",
                    "legal_issues": ["breach of contract", "damages"],
                    "jurisdiction": "US"
                },
                "max_results": 10
            },
            "timeout": 20,
            "expected_fields": ["precedent_matches"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/citation-analysis",
            "method": "POST",
            "endpoint": "/legal-research-engine/citation-analysis",
            "data": {
                "cases": [
                    {
                        "case_id": "test_case_1",
                        "case_title": "Smith v. Jones",
                        "citation": "123 F.3d 456 (2023)"
                    }
                ],
                "depth": 2
            },
            "timeout": 25,
            "expected_fields": ["summary", "authority_ranking", "summary.total_nodes"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/generate-memo",
            "method": "POST",
            "endpoint": "/legal-research-engine/generate-memo",
            "data": {
                "memo_data": {
                    "research_query": "Contract breach analysis",
                    "legal_issues": ["breach", "damages"],
                    "jurisdiction": "US"
                },
                "memo_type": "comprehensive"
            },
            "timeout": 60,
            "expected_fields": ["id", "generated_memo"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/structure-arguments",
            "method": "POST",
            "endpoint": "/legal-research-engine/structure-arguments",
            "data": {
                "argument_data": {
                    "legal_question": "What are the remedies for breach of contract?",
                    "jurisdiction": "US"
                },
                "argument_strength": "strong"
            },
            "timeout": 45,
            "expected_fields": ["id", "argument_structure"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/multi-jurisdiction-search",
            "method": "POST",
            "endpoint": "/legal-research-engine/multi-jurisdiction-search",
            "data": {
                "query": "Breach of contract specific performance",
                "jurisdictions": ["US", "UK", "CA"],
                "legal_domain": "contract_law",
                "comparison_mode": True
            },
            "timeout": 45,
            "expected_fields": ["query", "jurisdictions_searched", "results", "total_results"],
            "priority": "HIGH"
        },
        {
            "name": "POST /api/legal-research-engine/quality-assessment",
            "method": "POST",
            "endpoint": "/legal-research-engine/quality-assessment",
            "data": {
                "research_data": {
                    "query": "Contract analysis",
                    "results": ["Result 1", "Result 2"],
                    "sources": ["Source 1", "Source 2"]
                }
            },
            "timeout": 30,
            "expected_fields": ["assessment_id", "overall_scores"],
            "priority": "HIGH"
        },
        {
            "name": "GET /api/legal-research-engine/research-queries (smoke)",
            "method": "GET",
            "endpoint": "/legal-research-engine/research-queries",
            "data": None,
            "timeout": 15,
            "expected_fields": None,
            "priority": "MEDIUM"
        },
        {
            "name": "GET /api/legal-research-engine/research-memos (smoke)",
            "method": "GET",
            "endpoint": "/legal-research-engine/research-memos",
            "data": None,
            "timeout": 15,
            "expected_fields": None,
            "priority": "MEDIUM"
        }
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    high_priority_passed = 0
    high_priority_total = sum(1 for tc in test_cases if tc.get("priority") == "HIGH")
    
    # Run all tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"🎯 TEST {i}/{total_tests}: {test_case['name']}")
        print(f"Priority: {test_case.get('priority', 'MEDIUM')} | Timeout: {test_case['timeout']}s")
        print("-" * 60)
        
        result = test_endpoint_with_retry(
            test_case["method"],
            test_case["endpoint"],
            test_case["data"],
            test_case["timeout"],
            retries=1
        )
        
        test_passed = False
        
        if result["success"]:
            if result["status_code"] == 200:
                print(f"✅ SUCCESS: {result['status_code']} | Time: {result['response_time']:.3f}s | Attempt: {result['attempt']}")
                test_passed = True
                passed_tests += 1
                if test_case.get("priority") == "HIGH":
                    high_priority_passed += 1
                
                # Validate expected fields
                if test_case["expected_fields"]:
                    validation = validate_response_structure(result["response"], test_case["expected_fields"])
                    if validation["valid"]:
                        print(f"✅ Schema Validation: All {len(validation['present'])} expected fields present")
                        if "summary.total_nodes" in validation["present"]:
                            total_nodes = result["response"].get("summary", {}).get("total_nodes", "N/A")
                            print(f"   ✅ summary.total_nodes: {total_nodes}")
                        if "authority_ranking" in validation["present"]:
                            auth_ranking = result["response"].get("authority_ranking", [])
                            print(f"   ✅ authority_ranking: {len(auth_ranking)} items")
                    else:
                        print(f"⚠️ Schema Validation: Missing {len(validation['missing'])} fields: {validation['missing']}")
                        print(f"   Present: {validation['present']}")
                
            elif result["status_code"] == 503:
                print(f"⚠️ SERVICE UNAVAILABLE: {result['status_code']} | Time: {result['response_time']:.3f}s")
                print("   Engine unavailable by design - this is acceptable behavior")
            else:
                print(f"⚠️ NON-200 RESPONSE: {result['status_code']} | Time: {result['response_time']:.3f}s")
        else:
            print(f"❌ FAILED: {result['error']} | Time: {result['response_time']:.3f}s | Attempt: {result['attempt']}")
        
        results.append({
            "test": test_case["name"],
            "endpoint": test_case["endpoint"],
            "method": test_case["method"],
            "priority": test_case.get("priority", "MEDIUM"),
            "result": result,
            "passed": test_passed
        })
        print()
    
    # Final Summary
    print("🎯 FINAL LEGAL RESEARCH ENGINE TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed (200 OK): {passed_tests}")
    print(f"Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"High Priority Tests: {high_priority_passed}/{high_priority_total} passed ({(high_priority_passed/high_priority_total)*100:.1f}%)")
    print()
    
    # Categorize results
    working = [r for r in results if r["passed"]]
    failing = [r for r in results if not r["passed"]]
    
    print("📊 ENDPOINT STATUS BREAKDOWN:")
    print("-" * 80)
    
    if working:
        print(f"✅ WORKING ENDPOINTS ({len(working)}):")
        for result in working:
            test_result = result["result"]
            priority_icon = "🔥" if result["priority"] == "HIGH" else "📋"
            print(f"   {priority_icon} {result['method']} {result['endpoint']}")
            print(f"      Response Time: {test_result['response_time']:.3f}s | Status: {test_result['status_code']}")
    
    if failing:
        print(f"\n❌ FAILING ENDPOINTS ({len(failing)}):")
        for result in failing:
            test_result = result["result"]
            priority_icon = "🔥" if result["priority"] == "HIGH" else "📋"
            error_info = test_result.get('error', f"Status {test_result.get('status_code', 'Unknown')}")
            print(f"   {priority_icon} {result['method']} {result['endpoint']}")
            print(f"      Error: {error_info} | Time: {test_result['response_time']:.3f}s")
    
    # Response time analysis for working endpoints
    if working:
        response_times = [r["result"]["response_time"] for r in working]
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n📈 PERFORMANCE METRICS (Working Endpoints):")
        print(f"   Average Response Time: {avg_time:.3f}s")
        print(f"   Fastest Response: {min_time:.3f}s")
        print(f"   Slowest Response: {max_time:.3f}s")
    
    print()
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    # Return comprehensive results
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "overall_success_rate": (passed_tests/total_tests)*100,
        "high_priority_passed": high_priority_passed,
        "high_priority_total": high_priority_total,
        "high_priority_success_rate": (high_priority_passed/high_priority_total)*100,
        "working_endpoints": len(working),
        "failing_endpoints": len(failing),
        "results": results
    }

if __name__ == "__main__":
    main()