#!/usr/bin/env python3

import requests
import json
import time

# Use internal backend URL
BASE_URL = "http://localhost:8001"

def test_stats():
    """Test the stats endpoint"""
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/legal-research-engine/stats", timeout=10)
        response_time = time.time() - start_time
        
        print(f"Stats endpoint: {response.status_code} ({response_time:.3f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"  - Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"  - Error: {response.text}")
            return False
    except Exception as e:
        print(f"Stats endpoint: ERROR - {e}")
        return False

def test_research():
    """Test the research endpoint"""
    try:
        start_time = time.time()
        payload = {
            "query_text": "Contract breach remedies",
            "research_type": "comprehensive",
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }
        response = requests.post(f"{BASE_URL}/api/legal-research-engine/research", 
                               json=payload, timeout=20)
        response_time = time.time() - start_time
        
        print(f"Research endpoint: {response.status_code} ({response_time:.3f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"  - ID: {data.get('id', 'missing')}")
            print(f"  - Status: {data.get('status', 'missing')}")
            print(f"  - Results count: {len(data.get('results', []))}")
            return True
        else:
            print(f"  - Error: {response.text}")
            return False
    except Exception as e:
        print(f"Research endpoint: ERROR - {e}")
        return False

def test_generate_memo():
    """Test the generate memo endpoint"""
    try:
        start_time = time.time()
        payload = {
            "memo_data": {
                "research_query": "Contract breach analysis",
                "legal_issues": ["breach of contract", "damages"],
                "jurisdiction": "US"
            },
            "memo_type": "comprehensive"
        }
        response = requests.post(f"{BASE_URL}/api/legal-research-engine/generate-memo", 
                               json=payload, timeout=20)
        response_time = time.time() - start_time
        
        print(f"Generate Memo endpoint: {response.status_code} ({response_time:.3f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"  - ID: {data.get('id', 'missing')}")
            print(f"  - Has memo: {'generated_memo' in data}")
            print(f"  - Has structure: {'memo_structure' in data}")
            return True
        else:
            print(f"  - Error: {response.text}")
            return False
    except Exception as e:
        print(f"Generate Memo endpoint: ERROR - {e}")
        return False

if __name__ == "__main__":
    print("🚀 QUICK INTERNAL LEGAL RESEARCH ENGINE TEST")
    print("=" * 50)
    
    results = []
    results.append(test_stats())
    results.append(test_research())
    results.append(test_generate_memo())
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    print(f"SUCCESS RATE: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")