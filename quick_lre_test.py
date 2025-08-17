#!/usr/bin/env python3
"""
Quick Legal Research Engine Test
Testing endpoints with short timeouts to identify working vs problematic ones
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://mobile-input-test.preview.emergentagent.com/api"

def quick_test(method, endpoint, data=None, timeout=10):
    """Quick test with short timeout"""
    url = f"{BACKEND_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        response_time = time.time() - start_time
        return response.status_code, response_time, "SUCCESS"
        
    except requests.exceptions.Timeout:
        return None, timeout, "TIMEOUT"
    except Exception as e:
        return None, time.time() - start_time, f"ERROR: {str(e)}"

def main():
    print("🚀 QUICK LEGAL RESEARCH ENGINE TEST")
    print("=" * 50)
    
    tests = [
        ("GET", "/legal-research-engine/stats", None),
        ("POST", "/legal-research-engine/precedent-search", {
            "query_case": {"case_title": "Test", "legal_issues": ["contract"], "jurisdiction": "US"},
            "max_results": 5
        }),
        ("POST", "/legal-research-engine/citation-analysis", {
            "cases": [{"case_id": "test", "case_title": "Test v. Case", "citation": "123 F.3d 456"}],
            "depth": 1
        }),
        ("POST", "/legal-research-engine/structure-arguments", {
            "argument_data": {"legal_question": "Contract breach remedies?", "jurisdiction": "US"},
            "argument_strength": "strong"
        }),
        ("POST", "/legal-research-engine/multi-jurisdiction-search", {
            "query": "Contract breach",
            "jurisdictions": ["US", "UK"],
            "legal_domain": "contract_law"
        }),
        ("POST", "/legal-research-engine/quality-assessment", {
            "research_data": {"query": "test", "results": ["result1"], "sources": ["source1"]}
        }),
        ("POST", "/legal-research-engine/research", {
            "query_text": "Contract breach",
            "research_type": "comprehensive",
            "jurisdiction": "US"
        }),
        ("POST", "/legal-research-engine/generate-memo", {
            "memo_data": {"research_query": "Contract analysis", "jurisdiction": "US"},
            "memo_type": "brief"
        }),
        ("GET", "/legal-research-engine/research-queries", None),
        ("GET", "/legal-research-engine/research-memos", None)
    ]
    
    results = []
    working_count = 0
    
    for method, endpoint, data in tests:
        print(f"Testing {method} {endpoint}...", end=" ")
        status, time_taken, result = quick_test(method, endpoint, data, timeout=15)
        
        if result == "SUCCESS" and status == 200:
            print(f"✅ {status} ({time_taken:.2f}s)")
            working_count += 1
        elif result == "SUCCESS":
            print(f"⚠️ {status} ({time_taken:.2f}s)")
        elif result == "TIMEOUT":
            print(f"❌ TIMEOUT ({time_taken:.1f}s)")
        else:
            print(f"❌ {result} ({time_taken:.2f}s)")
        
        results.append((endpoint, status, time_taken, result))
    
    print()
    print(f"Summary: {working_count}/{len(tests)} endpoints working (200 OK)")
    print(f"Success Rate: {(working_count/len(tests))*100:.1f}%")
    
    return results

if __name__ == "__main__":
    main()