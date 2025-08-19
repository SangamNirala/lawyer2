#!/usr/bin/env python3
"""
FOCUSED LEGAL RESEARCH ENGINE VERIFICATION TEST
===============================================

Tests the exact 8 Legal Research Engine endpoints mentioned in the review request:

PREVIOUSLY FAILING (4 endpoints):
1. POST /api/legal-research-engine/generate-memo (previously: generate_basic_memo method missing)
2. POST /api/legal-research-engine/structure-arguments (previously: LegalPosition enum validation error) 
3. POST /api/legal-research-engine/quality-assessment (previously: QualityLevel enum serialization error)
4. POST /api/legal-research-engine/multi-jurisdiction-search (previously: timeout >15s)

PREVIOUSLY WORKING (4 endpoints):
5. GET /api/legal-research-engine/stats
6. POST /api/legal-research-engine/research  
7. GET /api/legal-research-engine/research-queries
8. GET /api/legal-research-engine/research-memos

Expected outcome: 100% success rate (8/8 endpoints working) with all timeout issues resolved
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://risk-ai-negotiator.preview.emergentagent.com/api"

def test_endpoint_with_monitoring(method: str, endpoint: str, data: dict = None, timeout: float = 15.0):
    """Test endpoint with detailed monitoring"""
    start_time = time.time()
    
    try:
        url = f"{BACKEND_URL}{endpoint}"
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        response_time = time.time() - start_time
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"   Response Size: {len(json.dumps(response_data))} bytes")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "data": response_data,
                    "error": None
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "data": None,
                    "error": "Invalid JSON response"
                }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "response_time": response_time,
                "data": None,
                "error": response.text[:500]
            }
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "response_time": response_time,
            "data": None,
            "error": f"TIMEOUT after {response_time:.1f}s"
        }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "response_time": response_time,
            "data": None,
            "error": str(e)
        }

def main():
    print("🎯 FOCUSED LEGAL RESEARCH ENGINE VERIFICATION TEST")
    print("=" * 80)
    print("Testing the exact 8 endpoints mentioned in review request")
    print("Expected: 100% success rate (8/8 endpoints working)")
    print("Previous: 50% success rate (4/8 endpoints working)")
    print("=" * 80)
    
    test_start_time = time.time()
    results = []
    
    # Test 1: GET /api/legal-research-engine/stats (PREVIOUSLY WORKING)
    print("\n🔍 TEST 1/8: GET /api/legal-research-engine/stats")
    print("   Status: PREVIOUSLY WORKING")
    print("   Expected: Should work (regression check)")
    result = test_endpoint_with_monitoring("GET", "/legal-research-engine/stats")
    results.append(("GET /api/legal-research-engine/stats", "PREVIOUSLY WORKING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 2: POST /api/legal-research-engine/research (PREVIOUSLY WORKING)
    print("\n🔍 TEST 2/8: POST /api/legal-research-engine/research")
    print("   Status: PREVIOUSLY WORKING")
    print("   Expected: Should work (regression check)")
    test_data = {
        "query_text": "Contract breach remedies in commercial agreements",
        "research_type": "comprehensive",
        "jurisdiction": "US",
        "legal_domain": "contract_law",
        "priority": "high",
        "max_results": 10,
        "min_confidence": 0.7,
        "include_analysis": True,
        "cache_results": True
    }
    result = test_endpoint_with_monitoring("POST", "/legal-research-engine/research", test_data)
    results.append(("POST /api/legal-research-engine/research", "PREVIOUSLY WORKING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 3: GET /api/legal-research-engine/research-queries (PREVIOUSLY WORKING)
    print("\n🔍 TEST 3/8: GET /api/legal-research-engine/research-queries")
    print("   Status: PREVIOUSLY WORKING")
    print("   Expected: Should work (regression check)")
    result = test_endpoint_with_monitoring("GET", "/legal-research-engine/research-queries")
    results.append(("GET /api/legal-research-engine/research-queries", "PREVIOUSLY WORKING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 4: GET /api/legal-research-engine/research-memos (PREVIOUSLY WORKING)
    print("\n🔍 TEST 4/8: GET /api/legal-research-engine/research-memos")
    print("   Status: PREVIOUSLY WORKING")
    print("   Expected: Should work (regression check)")
    result = test_endpoint_with_monitoring("GET", "/legal-research-engine/research-memos")
    results.append(("GET /api/legal-research-engine/research-memos", "PREVIOUSLY WORKING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 5: POST /api/legal-research-engine/generate-memo (PREVIOUSLY FAILING)
    print("\n🔍 TEST 5/8: POST /api/legal-research-engine/generate-memo")
    print("   Status: PREVIOUSLY FAILING")
    print("   Previous Issue: generate_basic_memo method missing")
    print("   Expected: Should now work if method implemented")
    test_data = {
        "memo_data": {
            "research_query": "Employment contract termination clauses",
            "legal_issues": ["wrongful termination", "severance pay", "non-compete"],
            "jurisdiction": "California",
            "case_facts": "Employee terminated after 5 years, no cause given",
            "client_position": "seeking severance and challenging non-compete"
        },
        "memo_type": "comprehensive",
        "format_style": "professional"
    }
    result = test_endpoint_with_monitoring("POST", "/legal-research-engine/generate-memo", test_data)
    results.append(("POST /api/legal-research-engine/generate-memo", "PREVIOUSLY FAILING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 6: POST /api/legal-research-engine/structure-arguments (PREVIOUSLY FAILING)
    print("\n🔍 TEST 6/8: POST /api/legal-research-engine/structure-arguments")
    print("   Status: PREVIOUSLY FAILING")
    print("   Previous Issue: LegalPosition enum validation error")
    print("   Expected: Should now work if enum serialization fixed")
    test_data = {
        "argument_data": {
            "legal_question": "Is the non-compete clause enforceable?",
            "case_facts": ["Employee worked in tech industry", "Non-compete covers entire state", "Duration is 2 years"],
            "legal_position": "plaintiff",
            "jurisdiction": "California",
            "supporting_evidence": ["Industry practice", "Overbroad geographic scope"]
        },
        "argument_strength": "strong",
        "include_counterarguments": True
    }
    result = test_endpoint_with_monitoring("POST", "/legal-research-engine/structure-arguments", test_data)
    results.append(("POST /api/legal-research-engine/structure-arguments", "PREVIOUSLY FAILING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 7: POST /api/legal-research-engine/quality-assessment (PREVIOUSLY FAILING)
    print("\n🔍 TEST 7/8: POST /api/legal-research-engine/quality-assessment")
    print("   Status: PREVIOUSLY FAILING")
    print("   Previous Issue: QualityLevel enum serialization error")
    print("   Expected: Should now work if enum serialization fixed")
    test_data = {
        "research_data": {
            "research_id": "test_research_001",
            "sources": [
                {"type": "case_law", "citation": "Smith v. Jones", "authority": "high"},
                {"type": "statute", "citation": "Cal. Bus. & Prof. Code § 16600", "authority": "primary"}
            ],
            "analysis_content": "The non-compete clause analysis shows...",
            "quality_level": "comprehensive",
            "completeness_score": 0.85,
            "authority_score": 0.90
        }
    }
    result = test_endpoint_with_monitoring("POST", "/legal-research-engine/quality-assessment", test_data)
    results.append(("POST /api/legal-research-engine/quality-assessment", "PREVIOUSLY FAILING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Test 8: POST /api/legal-research-engine/multi-jurisdiction-search (PREVIOUSLY FAILING)
    print("\n🔍 TEST 8/8: POST /api/legal-research-engine/multi-jurisdiction-search")
    print("   Status: PREVIOUSLY FAILING")
    print("   Previous Issue: timeout >15s")
    print("   Expected: Should now work within <15s if timeout issues fixed")
    test_data = {
        "query": "Employment non-compete enforceability",
        "jurisdictions": ["US", "CA", "UK", "AU"],
        "legal_domain": "employment_law",
        "comparison_mode": True
    }
    result = test_endpoint_with_monitoring("POST", "/legal-research-engine/multi-jurisdiction-search", test_data)
    results.append(("POST /api/legal-research-engine/multi-jurisdiction-search", "PREVIOUSLY FAILING", result))
    print(f"   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    
    # Generate comprehensive report
    total_test_time = time.time() - test_start_time
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE VERIFICATION RESULTS")
    print("=" * 80)
    
    working_count = sum(1 for _, _, result in results if result['success'])
    success_rate = (working_count / len(results)) * 100
    
    print(f"📈 SUCCESS RATE: {success_rate:.1f}% ({working_count}/{len(results)} endpoints working)")
    print(f"⏱️ TOTAL TEST TIME: {total_test_time:.2f} seconds")
    print(f"🎯 TARGET: 100% (8/8 endpoints working)")
    print(f"📊 PREVIOUS: 50% (4/8 endpoints working)")
    
    if success_rate > 50:
        improvement = success_rate - 50
        print(f"📈 IMPROVEMENT: +{improvement:.1f}% from previous test")
    
    print("\n" + "=" * 80)
    print("📋 DETAILED RESULTS BY CATEGORY")
    print("=" * 80)
    
    # Previously working endpoints (regression check)
    print("\n✅ PREVIOUSLY WORKING ENDPOINTS (Regression Check):")
    previously_working = [r for r in results if r[1] == "PREVIOUSLY WORKING"]
    for endpoint, status, result in previously_working:
        icon = "✅" if result['success'] else "❌"
        print(f"   {icon} {endpoint} - {result['response_time']:.3f}s")
        if not result['success']:
            print(f"      ERROR: {result['error']}")
    
    # Previously failing endpoints (fix verification)
    print("\n🔧 PREVIOUSLY FAILING ENDPOINTS (Fix Verification):")
    previously_failing = [r for r in results if r[1] == "PREVIOUSLY FAILING"]
    for endpoint, status, result in previously_failing:
        icon = "✅" if result['success'] else "❌"
        print(f"   {icon} {endpoint} - {result['response_time']:.3f}s")
        if not result['success']:
            print(f"      ERROR: {result['error']}")
    
    print("\n" + "=" * 80)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 80)
    
    if success_rate == 100:
        print("🎉 OUTSTANDING SUCCESS: All 8 endpoints working!")
        print("✅ TARGET ACHIEVED: 100% success rate as requested")
        print("✅ TIMEOUT ISSUES RESOLVED: All endpoints respond within acceptable time")
        print("✅ SERIALIZATION ISSUES RESOLVED: All enum handling working correctly")
        print("✅ IMPLEMENTATION ISSUES RESOLVED: All missing methods implemented")
    elif success_rate >= 75:
        print("✅ SIGNIFICANT IMPROVEMENT: Most endpoints working")
        print("⚠️ TARGET PARTIALLY ACHIEVED: Some issues remain")
        failing_count = len(results) - working_count
        print(f"🔧 REMAINING ISSUES: {failing_count} endpoints still need fixes")
    elif success_rate > 50:
        print("⚠️ PARTIAL IMPROVEMENT: Some progress made")
        print("❌ TARGET NOT ACHIEVED: Significant issues remain")
    else:
        print("❌ NO IMPROVEMENT: Success rate same as previous test")
        print("❌ TARGET NOT ACHIEVED: Critical issues persist")
    
    # Specific issue analysis
    timeout_issues = [r for r in results if not r[2]['success'] and 'TIMEOUT' in str(r[2]['error'])]
    if timeout_issues:
        print(f"\n⏰ TIMEOUT ISSUES: {len(timeout_issues)} endpoints still timing out")
        for endpoint, _, result in timeout_issues:
            print(f"   • {endpoint} - {result['response_time']:.1f}s")
    
    error_issues = [r for r in results if not r[2]['success'] and 'TIMEOUT' not in str(r[2]['error'])]
    if error_issues:
        print(f"\n💥 IMPLEMENTATION ISSUES: {len(error_issues)} endpoints with errors")
        for endpoint, _, result in error_issues:
            print(f"   • {endpoint} - {result['error'][:100]}...")
    
    print(f"\n🏁 VERIFICATION COMPLETE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()