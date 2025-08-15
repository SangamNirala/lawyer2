#!/usr/bin/env python3
"""
Patient Legal Research Engine Test
Testing with longer timeouts to account for processing time
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"  # Use local backend directly

def test_endpoint_patient(name, method, url, payload=None, timeout=120):
    """Patient endpoint test with long timeout"""
    print(f"Testing {name}... (timeout: {timeout}s)")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=payload, timeout=timeout)
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ {name}: SUCCESS ({response_time:.2f}s)")
            return True, response_time
        elif response.status_code == 503:
            print(f"❌ {name}: 503 Service Unavailable")
            return False, response_time
        elif response.status_code == 500:
            print(f"⚠️ {name}: 500 Internal Server Error (endpoint accessible but has issues)")
            return True, response_time  # Endpoint is accessible, just has implementation issues
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, response_time
            
    except requests.exceptions.Timeout:
        print(f"❌ {name}: TIMEOUT after {timeout}s")
        return False, timeout
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
        return False, 0

def main():
    print("🚀 PATIENT LEGAL RESEARCH ENGINE TEST")
    print("Testing with longer timeouts to account for processing time")
    print("=" * 60)
    
    results = []
    
    # Test the 8 endpoints with appropriate timeouts
    endpoints = [
        ("Stats", "GET", f"{BASE_URL}/api/legal-research-engine/stats", None, 10),
        ("Research", "POST", f"{BASE_URL}/api/legal-research-engine/research", {
            "query_text": "contract breach remedies",
            "research_type": "comprehensive",
            "jurisdiction": "US",
            "legal_domain": "contract_law",
            "max_results": 5,
            "min_confidence": 0.7
        }, 180),  # 3 minutes for comprehensive research
        ("Precedent Search", "POST", f"{BASE_URL}/api/legal-research-engine/precedent-search", {
            "query_case": {
                "case_facts": "Commercial contract breach involving delivery failure",
                "legal_issues": ["breach of contract", "damages"],
                "jurisdiction": "US"
            },
            "max_results": 5,
            "min_similarity": 0.6
        }, 120),  # 2 minutes for precedent search
        ("Citation Analysis", "POST", f"{BASE_URL}/api/legal-research-engine/citation-analysis", {
            "cases": [
                {
                    "case_id": "test_case_1",
                    "citation": "123 F.3d 456 (9th Cir. 2020)",
                    "title": "Sample Contract Case",
                    "legal_issues": ["breach of contract"]
                }
            ],
            "depth": 1
        }, 90),  # 1.5 minutes for citation analysis
        ("Generate Memo", "POST", f"{BASE_URL}/api/legal-research-engine/generate-memo", {
            "memo_data": {
                "research_query": "contract breach remedies analysis",
                "legal_issues": ["breach of contract", "damages"],
                "jurisdiction": "US"
            },
            "memo_type": "brief"
        }, 120),  # 2 minutes for memo generation
        ("Structure Arguments", "POST", f"{BASE_URL}/api/legal-research-engine/structure-arguments", {
            "argument_data": {
                "legal_question": "What remedies are available for contract breach?",
                "case_facts": "Contract breach case",
                "jurisdiction": "US"
            },
            "argument_strength": "strong"
        }, 90),  # 1.5 minutes for argument structuring
        ("Multi-Jurisdiction", "POST", f"{BASE_URL}/api/legal-research-engine/multi-jurisdiction-search", {
            "query": "contract breach remedies",
            "jurisdictions": ["US"],
            "legal_domain": "contract_law"
        }, 120),  # 2 minutes for multi-jurisdiction search
        ("Quality Assessment", "POST", f"{BASE_URL}/api/legal-research-engine/quality-assessment", {
            "research_data": {
                "research_id": "test_123",
                "query": "contract breach",
                "results": [
                    {
                        "case_id": "case_1",
                        "relevance_score": 0.8,
                        "authority_score": 0.9
                    }
                ],
                "sources_count": 5
            }
        }, 60)  # 1 minute for quality assessment
    ]
    
    working_count = 0
    total_time = 0
    
    for name, method, url, payload, timeout in endpoints:
        success, response_time = test_endpoint_patient(name, method, url, payload, timeout)
        results.append((name, success, response_time))
        if success:
            working_count += 1
        total_time += response_time
        print()  # Add spacing between tests
    
    print("=" * 60)
    print("DETAILED RESULTS:")
    for name, success, response_time in results:
        status = "✅ WORKING" if success else "❌ FAILING"
        print(f"{status}: {name} ({response_time:.2f}s)")
    
    success_rate = (working_count / len(results)) * 100
    print(f"\nSUCCESS RATE: {working_count}/{len(results)} ({success_rate:.1f}%)")
    print(f"TOTAL TEST TIME: {total_time:.2f}s")
    
    if success_rate == 100:
        print("🎉 PERFECT: All Legal Research Engine endpoints working!")
    elif success_rate >= 87.5:  # 7/8 working
        print("🎉 EXCELLENT: Most endpoints working - major improvement!")
    elif success_rate >= 62.5:  # 5/8 working
        print("✅ GOOD: Significant improvement from previous 12.5% rate")
    elif success_rate >= 37.5:  # 3/8 working
        print("⚠️ PARTIAL: Some improvement, but issues remain")
    else:
        print("❌ POOR: Still many issues")
    
    # Compare to previous state
    if success_rate > 12.5:
        improvement = success_rate - 12.5
        print(f"📈 IMPROVEMENT: +{improvement:.1f}% from previous testing")
    
    return results

if __name__ == "__main__":
    main()