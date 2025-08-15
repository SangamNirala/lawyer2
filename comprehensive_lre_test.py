#!/usr/bin/env python3
"""
Comprehensive Legal Research Engine Test
Testing all endpoints with appropriate timeouts and validation
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://legal-api-debug-1.preview.emergentagent.com/api"

def test_endpoint_detailed(method, endpoint, data=None, timeout=30, expected_fields=None):
    """Detailed endpoint test with validation"""
    url = f"{BACKEND_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        response_time = time.time() - start_time
        
        result = {
            "success": True,
            "status_code": response.status_code,
            "response_time": response_time,
            "timeout_used": timeout
        }
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                result["response"] = response.json()
                result["response_size"] = len(json.dumps(result["response"]))
            except:
                result["response"] = response.text
                result["response_size"] = len(response.text)
        else:
            result["response"] = response.text
            result["response_size"] = len(response.text)
        
        # Validate expected fields
        if response.status_code == 200 and expected_fields and isinstance(result["response"], dict):
            missing_fields = []
            present_fields = []
            
            for field in expected_fields:
                if "." in field:  # Handle nested fields like summary.total_nodes
                    parts = field.split(".")
                    current = result["response"]
                    found = True
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            found = False
                            break
                    if found:
                        present_fields.append(field)
                    else:
                        missing_fields.append(field)
                else:
                    if field in result["response"]:
                        present_fields.append(field)
                    else:
                        missing_fields.append(field)
            
            result["field_validation"] = {
                "expected": expected_fields,
                "present": present_fields,
                "missing": missing_fields,
                "validation_passed": len(missing_fields) == 0
            }
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "TIMEOUT",
            "response_time": timeout,
            "timeout_used": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": time.time() - start_time,
            "timeout_used": timeout
        }

def main():
    print("🎯 COMPREHENSIVE LEGAL RESEARCH ENGINE TEST SUITE")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().isoformat()}")
    print()
    
    # Test cases with appropriate timeouts and validation
    test_cases = [
        {
            "name": "LRE Stats",
            "method": "GET",
            "endpoint": "/legal-research-engine/stats",
            "data": None,
            "timeout": 10,
            "expected_fields": ["status", "engine_stats", "system_health"]
        },
        {
            "name": "LRE Precedent Search",
            "method": "POST",
            "endpoint": "/legal-research-engine/precedent-search",
            "data": {
                "query_case": {
                    "case_title": "Contract Breach Analysis",
                    "legal_issues": ["breach of contract", "specific performance", "damages"],
                    "jurisdiction": "US",
                    "case_facts": ["Written contract executed", "Performance deadline missed", "Monetary damages claimed"]
                },
                "max_results": 10,
                "min_similarity": 0.6
            },
            "timeout": 15,
            "expected_fields": ["precedent_matches", "query_id", "processing_time"]
        },
        {
            "name": "LRE Citation Analysis",
            "method": "POST",
            "endpoint": "/legal-research-engine/citation-analysis",
            "data": {
                "cases": [
                    {
                        "case_id": "test_case_1",
                        "case_title": "Smith v. Jones Contract Dispute",
                        "citation": "123 F.3d 456 (9th Cir. 2023)",
                        "court": "9th Circuit Court of Appeals",
                        "jurisdiction": "US"
                    },
                    {
                        "case_id": "test_case_2", 
                        "case_title": "Brown v. Davis Breach Analysis",
                        "citation": "456 F.Supp.3d 789 (S.D.N.Y. 2023)",
                        "court": "Southern District of New York",
                        "jurisdiction": "US"
                    }
                ],
                "depth": 2,
                "jurisdiction_filter": "US"
            },
            "timeout": 20,
            "expected_fields": ["summary", "authority_ranking", "summary.total_nodes"]
        },
        {
            "name": "LRE Research (Valid Type)",
            "method": "POST",
            "endpoint": "/legal-research-engine/research",
            "data": {
                "query_text": "Contract breach remedies and specific performance analysis",
                "research_type": "comprehensive",
                "jurisdiction": "US",
                "legal_domain": "contract_law",
                "priority": "high",
                "max_results": 20,
                "include_analysis": True
            },
            "timeout": 60,
            "expected_fields": ["id", "results", "confidence_score"]
        },
        {
            "name": "LRE Research (Invalid Type Fallback)",
            "method": "POST",
            "endpoint": "/legal-research-engine/research",
            "data": {
                "query_text": "Contract breach analysis",
                "research_type": "invalid_research_type",
                "jurisdiction": "US",
                "legal_domain": "contract_law"
            },
            "timeout": 60,
            "expected_fields": ["id", "results"]
        },
        {
            "name": "LRE Structure Arguments",
            "method": "POST",
            "endpoint": "/legal-research-engine/structure-arguments",
            "data": {
                "argument_data": {
                    "legal_question": "What are the available remedies for material breach of contract when specific performance is sought?",
                    "case_facts": [
                        "Written contract for unique services",
                        "Material breach by defendant",
                        "Plaintiff seeks specific performance",
                        "Monetary damages insufficient"
                    ],
                    "jurisdiction": "US",
                    "legal_domain": "contract_law"
                },
                "argument_strength": "strong",
                "include_counterarguments": True
            },
            "timeout": 45,
            "expected_fields": ["id", "legal_question", "argument_structure"]
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
            "timeout": 45,
            "expected_fields": ["query", "jurisdictions_searched", "results", "total_results"]
        },
        {
            "name": "LRE Generate Memo",
            "method": "POST",
            "endpoint": "/legal-research-engine/generate-memo",
            "data": {
                "memo_data": {
                    "research_query": "Contract breach remedies analysis",
                    "legal_issues": ["breach of contract", "specific performance", "damages"],
                    "jurisdiction": "US",
                    "case_facts": ["Contract executed", "Performance failed", "Damages sought"],
                    "client_objectives": ["Obtain specific performance", "Recover damages"]
                },
                "memo_type": "comprehensive",
                "format_style": "professional"
            },
            "timeout": 60,
            "expected_fields": ["id", "generated_memo", "memo_structure"]
        },
        {
            "name": "LRE Quality Assessment",
            "method": "POST",
            "endpoint": "/legal-research-engine/quality-assessment",
            "data": {
                "research_data": {
                    "query": "Contract breach analysis",
                    "results": [
                        {"case_title": "Smith v. Jones", "relevance": 0.9},
                        {"case_title": "Brown v. Davis", "relevance": 0.8}
                    ],
                    "sources": [
                        {"source": "Federal Courts", "authority": "high"},
                        {"source": "State Courts", "authority": "medium"}
                    ],
                    "legal_domain": "contract_law",
                    "jurisdiction": "US"
                }
            },
            "timeout": 30,
            "expected_fields": ["assessment_id", "overall_scores", "quality_insights"]
        }
    ]
    
    # Smoke tests for GET endpoints
    smoke_tests = [
        {
            "name": "LRE Research Queries (Smoke)",
            "method": "GET",
            "endpoint": "/legal-research-engine/research-queries",
            "data": None,
            "timeout": 15,
            "expected_fields": None
        },
        {
            "name": "LRE Research Memos (Smoke)",
            "method": "GET",
            "endpoint": "/legal-research-engine/research-memos",
            "data": None,
            "timeout": 15,
            "expected_fields": None
        }
    ]
    
    all_tests = test_cases + smoke_tests
    results = []
    passed_tests = 0
    total_tests = len(all_tests)
    
    # Run all tests
    for i, test_case in enumerate(all_tests, 1):
        print(f"🎯 TEST {i}/{total_tests}: {test_case['name']}")
        print("=" * 60)
        
        result = test_endpoint_detailed(
            test_case["method"],
            test_case["endpoint"],
            test_case["data"],
            test_case["timeout"],
            test_case.get("expected_fields")
        )
        
        if result["success"]:
            if result["status_code"] == 200:
                print(f"✅ SUCCESS: {result['status_code']} | Time: {result['response_time']:.3f}s | Size: {result.get('response_size', 0)} bytes")
                passed_tests += 1
                
                # Field validation results
                if "field_validation" in result:
                    validation = result["field_validation"]
                    if validation["validation_passed"]:
                        print(f"✅ Field Validation: All {len(validation['present'])} expected fields present")
                    else:
                        print(f"⚠️ Field Validation: Missing {len(validation['missing'])} fields: {validation['missing']}")
                        print(f"   Present fields: {validation['present']}")
                
            elif result["status_code"] == 503:
                print(f"⚠️ SERVICE UNAVAILABLE: {result['status_code']} | Time: {result['response_time']:.3f}s")
                print("   Engine may be warming up or temporarily unavailable")
            else:
                print(f"⚠️ NON-200 RESPONSE: {result['status_code']} | Time: {result['response_time']:.3f}s")
        else:
            print(f"❌ FAILED: {result['error']} | Time: {result['response_time']:.3f}s | Timeout: {result['timeout_used']}s")
        
        results.append({
            "test": test_case["name"],
            "endpoint": test_case["endpoint"],
            "method": test_case["method"],
            "result": result
        })
        print()
    
    # Summary
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed (200 OK): {passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    # Categorize results
    working_endpoints = []
    timeout_endpoints = []
    error_endpoints = []
    unavailable_endpoints = []
    
    for result in results:
        test_result = result["result"]
        if test_result["success"] and test_result["status_code"] == 200:
            working_endpoints.append(result)
        elif test_result["success"] and test_result["status_code"] == 503:
            unavailable_endpoints.append(result)
        elif not test_result["success"] and test_result["error"] == "TIMEOUT":
            timeout_endpoints.append(result)
        else:
            error_endpoints.append(result)
    
    print("📊 ENDPOINT STATUS BREAKDOWN:")
    print("-" * 80)
    
    if working_endpoints:
        print(f"✅ WORKING ENDPOINTS ({len(working_endpoints)}):")
        for result in working_endpoints:
            test_result = result["result"]
            print(f"   {result['method']} {result['endpoint']} - {test_result['response_time']:.3f}s")
    
    if unavailable_endpoints:
        print(f"\n⚠️ UNAVAILABLE ENDPOINTS ({len(unavailable_endpoints)}):")
        for result in unavailable_endpoints:
            print(f"   {result['method']} {result['endpoint']} - Service Unavailable")
    
    if timeout_endpoints:
        print(f"\n❌ TIMEOUT ENDPOINTS ({len(timeout_endpoints)}):")
        for result in timeout_endpoints:
            test_result = result["result"]
            print(f"   {result['method']} {result['endpoint']} - Timeout after {test_result['timeout_used']}s")
    
    if error_endpoints:
        print(f"\n❌ ERROR ENDPOINTS ({len(error_endpoints)}):")
        for result in error_endpoints:
            test_result = result["result"]
            print(f"   {result['method']} {result['endpoint']} - {test_result['error']}")
    
    print()
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": (passed_tests/total_tests)*100,
        "working_endpoints": len(working_endpoints),
        "timeout_endpoints": len(timeout_endpoints),
        "error_endpoints": len(error_endpoints),
        "unavailable_endpoints": len(unavailable_endpoints),
        "results": results
    }

if __name__ == "__main__":
    main()