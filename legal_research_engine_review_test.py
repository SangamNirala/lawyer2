#!/usr/bin/env python3
"""
Legal Research Engine (LRE) Review Test Suite
Testing all endpoints mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://strategyengine.preview.emergentagent.com/api"

def test_endpoint(method, endpoint, data=None, timeout=30):
    """Test a single endpoint with timeout and error handling"""
    url = f"{BACKEND_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        response_time = time.time() - start_time
        
        return {
            "success": True,
            "status_code": response.status_code,
            "response_time": response_time,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "TIMEOUT",
            "response_time": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": time.time() - start_time
        }

def main():
    print("🎯 LEGAL RESEARCH ENGINE (LRE) REVIEW TEST SUITE")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().isoformat()}")
    print()
    
    # Test data for different endpoints
    test_cases = [
        {
            "name": "LRE Stats",
            "method": "GET",
            "endpoint": "/legal-research-engine/stats",
            "data": None,
            "expected_fields": ["status", "message"]
        },
        {
            "name": "LRE Research (Valid Type)",
            "method": "POST", 
            "endpoint": "/legal-research-engine/research",
            "data": {
                "query_text": "Contract breach remedies",
                "research_type": "comprehensive",
                "jurisdiction": "US",
                "legal_domain": "contract_law"
            },
            "expected_fields": ["id", "results"]
        },
        {
            "name": "LRE Research (Invalid Type Fallback)",
            "method": "POST",
            "endpoint": "/legal-research-engine/research", 
            "data": {
                "query_text": "Contract breach remedies",
                "research_type": "invalid_type",
                "jurisdiction": "US",
                "legal_domain": "contract_law"
            },
            "expected_fields": ["id", "results"]
        },
        {
            "name": "LRE Precedent Search",
            "method": "POST",
            "endpoint": "/legal-research-engine/precedent-search",
            "data": {
                "query_case": {
                    "case_title": "Contract Dispute",
                    "legal_issues": ["breach of contract", "damages"],
                    "jurisdiction": "US"
                },
                "max_results": 10
            },
            "expected_fields": ["precedent_matches"]
        },
        {
            "name": "LRE Citation Analysis",
            "method": "POST",
            "endpoint": "/legal-research-engine/citation-analysis",
            "data": {
                "cases": [
                    {
                        "case_id": "test_case_1",
                        "case_title": "Test v. Case",
                        "citation": "123 F.3d 456 (2023)"
                    }
                ],
                "depth": 2
            },
            "expected_fields": ["summary", "authority_ranking"]
        },
        {
            "name": "LRE Generate Memo",
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
            "expected_fields": ["id", "generated_memo"]
        },
        {
            "name": "LRE Structure Arguments",
            "method": "POST",
            "endpoint": "/legal-research-engine/structure-arguments",
            "data": {
                "argument_data": {
                    "legal_question": "What are the remedies for breach of contract?",
                    "case_facts": ["Contract signed", "Performance failed", "Damages incurred"],
                    "jurisdiction": "US"
                },
                "argument_strength": "strong"
            },
            "expected_fields": ["id", "argument_structure"]
        },
        {
            "name": "LRE Multi-Jurisdiction Search",
            "method": "POST",
            "endpoint": "/legal-research-engine/multi-jurisdiction-search",
            "data": {
                "query": "Breach of contract specific performance",
                "jurisdictions": ["US", "UK", "CA"],
                "legal_domain": "contract_law",
                "comparison_mode": True
            },
            "expected_fields": ["query", "jurisdictions_searched", "results"]
        },
        {
            "name": "LRE Quality Assessment",
            "method": "POST",
            "endpoint": "/legal-research-engine/quality-assessment",
            "data": {
                "research_data": {
                    "query": "Contract analysis",
                    "results": ["Result 1", "Result 2"],
                    "sources": ["Source 1", "Source 2"]
                }
            },
            "expected_fields": ["assessment_id", "overall_scores"]
        }
    ]
    
    # Additional smoke tests for GET endpoints
    smoke_tests = [
        {
            "name": "LRE Research Queries (Smoke)",
            "method": "GET",
            "endpoint": "/legal-research-engine/research-queries",
            "data": None
        },
        {
            "name": "LRE Research Memos (Smoke)",
            "method": "GET", 
            "endpoint": "/legal-research-engine/research-memos",
            "data": None
        }
    ]
    
    results = []
    total_tests = len(test_cases) + len(smoke_tests)
    passed_tests = 0
    
    # Run main test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"🎯 TEST {i}/{total_tests}: {test_case['name']}")
        print("=" * 60)
        
        result = test_endpoint(
            test_case["method"],
            test_case["endpoint"], 
            test_case["data"],
            timeout=45  # Longer timeout for complex operations
        )
        
        if result["success"]:
            status_icon = "✅" if result["status_code"] == 200 else "⚠️"
            print(f"{status_icon} Status: {result['status_code']} | Time: {result['response_time']:.3f}s")
            
            # Validate expected fields for 200 responses
            if result["status_code"] == 200 and "expected_fields" in test_case:
                response_data = result["response"]
                missing_fields = []
                for field in test_case["expected_fields"]:
                    if field not in response_data:
                        # Check nested fields like summary.total_nodes
                        if "." in field:
                            parts = field.split(".")
                            current = response_data
                            found = True
                            for part in parts:
                                if isinstance(current, dict) and part in current:
                                    current = current[part]
                                else:
                                    found = False
                                    break
                            if not found:
                                missing_fields.append(field)
                        else:
                            missing_fields.append(field)
                
                if missing_fields:
                    print(f"⚠️ Missing expected fields: {missing_fields}")
                else:
                    print("✅ All expected fields present")
            
            if result["status_code"] == 200:
                passed_tests += 1
                
        else:
            print(f"❌ Error: {result['error']} | Time: {result['response_time']:.3f}s")
        
        results.append({
            "test": test_case["name"],
            "endpoint": test_case["endpoint"],
            "method": test_case["method"],
            "result": result
        })
        print()
    
    # Run smoke tests
    for i, test_case in enumerate(smoke_tests, len(test_cases) + 1):
        print(f"🎯 TEST {i}/{total_tests}: {test_case['name']}")
        print("=" * 60)
        
        result = test_endpoint(
            test_case["method"],
            test_case["endpoint"],
            test_case["data"],
            timeout=15  # Shorter timeout for smoke tests
        )
        
        if result["success"]:
            status_icon = "✅" if result["status_code"] == 200 else "⚠️"
            print(f"{status_icon} Status: {result['status_code']} | Time: {result['response_time']:.3f}s")
            if result["status_code"] == 200:
                passed_tests += 1
        else:
            print(f"❌ Error: {result['error']} | Time: {result['response_time']:.3f}s")
        
        results.append({
            "test": test_case["name"],
            "endpoint": test_case["endpoint"], 
            "method": test_case["method"],
            "result": result
        })
        print()
    
    # Summary
    print("🎯 LEGAL RESEARCH ENGINE TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed (200 OK): {passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    # Detailed results
    print("📊 DETAILED RESULTS:")
    print("-" * 80)
    for result in results:
        test_result = result["result"]
        if test_result["success"]:
            status = f"{test_result['status_code']} ({test_result['response_time']:.3f}s)"
            icon = "✅" if test_result["status_code"] == 200 else "⚠️"
        else:
            status = f"ERROR: {test_result['error']}"
            icon = "❌"
        
        print(f"{icon} {result['method']} {result['endpoint']}")
        print(f"   {result['test']}: {status}")
    
    print()
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    # Return results for further processing
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "results": results
    }

if __name__ == "__main__":
    main()