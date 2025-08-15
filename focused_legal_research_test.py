#!/usr/bin/env python3
"""
Focused Legal Research Engine Testing
Testing the 8 specific endpoints mentioned in the review request that were previously failing with 503 errors.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://legal-timeout-fix.preview.emergentagent.com"

def log_test(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_endpoint(endpoint_name, method, url, payload=None, timeout=30):
    """Generic endpoint testing function"""
    log_test(f"Testing {method} {endpoint_name}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=payload, timeout=timeout)
        
        response_time = time.time() - start_time
        
        log_test(f"Status: {response.status_code}, Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            log_test("✅ SUCCESS: Endpoint working")
            return True, f"Working, {response_time:.3f}s"
        elif response.status_code == 503:
            log_test("❌ FAIL: Still returning 503 Service Unavailable")
            return False, "503 Service Unavailable"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code}")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        log_test("❌ TIMEOUT: Request timed out")
        return False, "Timeout"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Error: {str(e)}"

def main():
    log_test("🚀 FOCUSED LEGAL RESEARCH ENGINE TESTING")
    log_test(f"Base URL: {BASE_URL}")
    log_test("Testing 8 endpoints that were previously failing with 503 errors")
    log_test("=" * 70)
    
    results = []
    
    # 1. GET /api/legal-research-engine/stats (was already working)
    success, msg = test_endpoint(
        "/api/legal-research-engine/stats",
        "GET",
        f"{BASE_URL}/api/legal-research-engine/stats"
    )
    results.append(("Stats", success, msg))
    
    # 2. POST /api/legal-research-engine/research
    research_payload = {
        "query_text": "contract breach remedies",
        "research_type": "comprehensive",
        "jurisdiction": "US",
        "legal_domain": "contract_law"
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/research",
        "POST", 
        f"{BASE_URL}/api/legal-research-engine/research",
        research_payload
    )
    results.append(("Research", success, msg))
    
    # 3. POST /api/legal-research-engine/precedent-search
    precedent_payload = {
        "query_case": {
            "case_facts": "Contract breach case",
            "legal_issues": ["breach of contract"],
            "jurisdiction": "US"
        },
        "max_results": 5
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/precedent-search",
        "POST",
        f"{BASE_URL}/api/legal-research-engine/precedent-search", 
        precedent_payload
    )
    results.append(("Precedent Search", success, msg))
    
    # 4. POST /api/legal-research-engine/citation-analysis
    citation_payload = {
        "cases": [
            {
                "case_id": "test_1",
                "citation": "123 F.3d 456",
                "title": "Test Case"
            }
        ],
        "depth": 1
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/citation-analysis",
        "POST",
        f"{BASE_URL}/api/legal-research-engine/citation-analysis",
        citation_payload
    )
    results.append(("Citation Analysis", success, msg))
    
    # 5. POST /api/legal-research-engine/generate-memo
    memo_payload = {
        "memo_data": {
            "research_query": "Contract breach analysis",
            "legal_issues": ["breach of contract"],
            "jurisdiction": "US"
        },
        "memo_type": "brief"
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/generate-memo",
        "POST",
        f"{BASE_URL}/api/legal-research-engine/generate-memo",
        memo_payload
    )
    results.append(("Generate Memo", success, msg))
    
    # 6. POST /api/legal-research-engine/structure-arguments
    arguments_payload = {
        "argument_data": {
            "legal_question": "What remedies are available for contract breach?",
            "case_facts": "Breach of contract case",
            "jurisdiction": "US"
        },
        "argument_strength": "strong"
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/structure-arguments",
        "POST",
        f"{BASE_URL}/api/legal-research-engine/structure-arguments",
        arguments_payload
    )
    results.append(("Structure Arguments", success, msg))
    
    # 7. POST /api/legal-research-engine/multi-jurisdiction-search
    multi_jurisdiction_payload = {
        "query": "contract breach remedies",
        "jurisdictions": ["US", "UK"],
        "legal_domain": "contract_law"
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/multi-jurisdiction-search",
        "POST",
        f"{BASE_URL}/api/legal-research-engine/multi-jurisdiction-search",
        multi_jurisdiction_payload
    )
    results.append(("Multi-Jurisdiction Search", success, msg))
    
    # 8. POST /api/legal-research-engine/quality-assessment
    quality_payload = {
        "research_data": {
            "research_id": "test_123",
            "query": "contract breach",
            "results": [],
            "sources_count": 5
        }
    }
    success, msg = test_endpoint(
        "/api/legal-research-engine/quality-assessment",
        "POST",
        f"{BASE_URL}/api/legal-research-engine/quality-assessment",
        quality_payload
    )
    results.append(("Quality Assessment", success, msg))
    
    # Summary
    log_test("\n" + "=" * 70)
    log_test("🎯 TESTING SUMMARY")
    log_test("=" * 70)
    
    working_count = 0
    for endpoint, success, message in results:
        status = "✅ WORKING" if success else "❌ FAILING"
        log_test(f"{status}: {endpoint} - {message}")
        if success:
            working_count += 1
    
    success_rate = (working_count / len(results)) * 100
    log_test(f"\n🎯 SUCCESS RATE: {working_count}/{len(results)} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        log_test("🎉 EXCELLENT: All Legal Research Engine endpoints working!")
    elif success_rate >= 87.5:
        log_test("✅ GREAT: Most endpoints working, significant improvement!")
    elif success_rate >= 50:
        log_test("⚠️ PARTIAL: Some improvement, but issues remain")
    else:
        log_test("❌ CRITICAL: Most endpoints still failing")
    
    return results

if __name__ == "__main__":
    main()