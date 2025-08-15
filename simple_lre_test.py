#!/usr/bin/env python3

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

def test_endpoint(name, method, endpoint, payload=None, timeout=15):
    """Test a single endpoint with timeout"""
    print(f"Testing {name}...", end=" ", flush=True)
    
    try:
        start_time = time.time()
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=payload, timeout=timeout)
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ SUCCESS ({response_time:.2f}s)")
            try:
                data = response.json()
                if 'id' in data:
                    print(f"   - ID: {data['id']}")
                if 'status' in data:
                    print(f"   - Status: {data['status']}")
                if 'results' in data:
                    print(f"   - Results: {len(data['results'])} items")
                if 'processing_time' in data:
                    print(f"   - Processing time: {data['processing_time']}")
            except:
                pass
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   - Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   - Error: {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("🚀 SIMPLE LEGAL RESEARCH ENGINE TEST")
    print("=" * 60)
    
    tests = [
        ("Stats", "GET", "/api/legal-research-engine/stats", None, 10),
        ("Research", "POST", "/api/legal-research-engine/research", {
            "query_text": "Contract breach remedies",
            "research_type": "comprehensive",
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }, 20),
        ("Generate Memo", "POST", "/api/legal-research-engine/generate-memo", {
            "memo_data": {
                "research_query": "Contract breach analysis",
                "legal_issues": ["breach of contract", "damages"],
                "jurisdiction": "US"
            },
            "memo_type": "comprehensive"
        }, 20),
        ("Structure Arguments", "POST", "/api/legal-research-engine/structure-arguments", {
            "argument_data": {
                "legal_question": "What are the remedies for breach of contract?",
                "case_facts": ["Contract signed", "Performance not delivered"],
                "jurisdiction": "US"
            }
        }, 20),
        ("Multi-Jurisdiction Search", "POST", "/api/legal-research-engine/multi-jurisdiction-search", {
            "query": "Breach of contract specific performance",
            "jurisdictions": ["US", "UK", "CA"],
            "legal_domain": "contract_law",
            "comparison_mode": True
        }, 20),
        ("Quality Assessment", "POST", "/api/legal-research-engine/quality-assessment", {
            "research_data": {
                "query": "Contract analysis",
                "results": ["Result 1", "Result 2"],
                "sources": ["Source 1", "Source 2"]
            }
        }, 15),
        ("Research Queries List", "GET", "/api/legal-research-engine/research-queries", None, 10),
        ("Research Memos List", "GET", "/api/legal-research-engine/research-memos", None, 10)
    ]
    
    results = []
    for name, method, endpoint, payload, timeout in tests:
        success = test_endpoint(name, method, endpoint, payload, timeout)
        results.append((name, success))
        print()  # Add spacing between tests
    
    print("=" * 60)
    print("SUMMARY:")
    success_count = 0
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if success:
            success_count += 1
    
    total_count = len(results)
    print(f"\nSUCCESS RATE: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

if __name__ == "__main__":
    main()