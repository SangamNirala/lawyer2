#!/usr/bin/env python3
"""
Legal Research Engine Quick Testing - Individual Endpoint Verification
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://litigation-buttons.preview.emergentagent.com/api"

def test_endpoint(endpoint_path, method="GET", data=None, timeout=10):
    """Test a single endpoint with timeout"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    url = f"{BACKEND_URL}{endpoint_path}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = session.get(url, timeout=timeout)
        else:
            response = session.post(url, json=data, timeout=timeout)
            
        response_time = time.time() - start_time
        
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'response_time': response_time,
            'response_data': response.json() if response.status_code == 200 else response.text,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'status_code': None,
            'response_time': 0,
            'response_data': None,
            'error': str(e)
        }

def main():
    print("🎯 LEGAL RESEARCH ENGINE QUICK TESTING")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Test data for endpoints
    test_cases = [
        {
            'name': 'Stats Endpoint',
            'path': '/legal-research-engine/stats',
            'method': 'GET',
            'data': None
        },
        {
            'name': 'Research Endpoint',
            'path': '/legal-research-engine/research',
            'method': 'POST',
            'data': {
                "query_text": "Contract breach remedies",
                "research_type": "comprehensive",
                "jurisdiction": "US",
                "legal_domain": "contract_law",
                "priority": "medium"
            }
        },
        {
            'name': 'Precedent Search',
            'path': '/legal-research-engine/precedent-search',
            'method': 'POST',
            'data': {
                "query_case": {
                    "case_title": "Contract Breach Case",
                    "facts": "Breach of contract with damages",
                    "jurisdiction": "US"
                },
                "max_results": 10
            }
        },
        {
            'name': 'Citation Analysis',
            'path': '/legal-research-engine/citation-analysis',
            'method': 'POST',
            'data': {
                "cases": [
                    {
                        "case_id": "case_001",
                        "title": "Smith v. Jones",
                        "citation": "123 F.3d 456",
                        "jurisdiction": "US"
                    }
                ],
                "depth": 2
            }
        },
        {
            'name': 'Memo Generation',
            'path': '/legal-research-engine/generate-memo',
            'method': 'POST',
            'data': {
                "memo_data": {
                    "research_query": "Contract breach analysis",
                    "case_facts": "Commercial contract breach",
                    "jurisdiction": "US"
                },
                "memo_type": "comprehensive",
                "format_style": "professional"
            }
        },
        {
            'name': 'Structure Arguments',
            'path': '/legal-research-engine/structure-arguments',
            'method': 'POST',
            'data': {
                "argument_data": {
                    "legal_question": "Contract breach remedies",
                    "case_facts": "Commercial dispute",
                    "jurisdiction": "US"
                },
                "argument_strength": "strong"
            }
        },
        {
            'name': 'Multi-Jurisdiction Search',
            'path': '/legal-research-engine/multi-jurisdiction-search',
            'method': 'POST',
            'data': {
                "query": "Contract breach remedies",
                "jurisdictions": ["US", "UK"],
                "legal_domain": "contract_law"
            }
        },
        {
            'name': 'Quality Assessment',
            'path': '/legal-research-engine/quality-assessment',
            'method': 'POST',
            'data': {
                "research_data": {
                    "research_id": "test_001",
                    "query": "Contract analysis",
                    "results": [{"case_title": "Test Case"}]
                }
            }
        }
    ]
    
    results = []
    working_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 TEST {i}: {test_case['name']}")
        print("-" * 40)
        
        result = test_endpoint(
            test_case['path'], 
            test_case['method'], 
            test_case['data'],
            timeout=15
        )
        
        results.append({
            'name': test_case['name'],
            'path': test_case['path'],
            **result
        })
        
        if result['success']:
            working_count += 1
            print(f"✅ WORKING - Status: {result['status_code']}, Time: {result['response_time']:.3f}s")
            
            # Show key response data
            if isinstance(result['response_data'], dict):
                keys = list(result['response_data'].keys())[:5]  # First 5 keys
                print(f"   Response keys: {keys}")
        else:
            print(f"❌ FAILED - Status: {result['status_code']}")
            if result['error']:
                print(f"   Error: {result['error']}")
            else:
                print(f"   Response: {str(result['response_data'])[:200]}...")
    
    # Summary
    total_endpoints = len(test_cases)
    success_rate = (working_count / total_endpoints) * 100
    
    print("\n" + "=" * 60)
    print("🎯 TESTING SUMMARY")
    print("=" * 60)
    print(f"Total Endpoints: {total_endpoints}")
    print(f"Working: {working_count}")
    print(f"Failed: {total_endpoints - working_count}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n📊 COMPARISON:")
    print(f"Previous Success Rate: 50-62.5% (4-5/8 endpoints)")
    print(f"Current Success Rate: {success_rate:.1f}% ({working_count}/8 endpoints)")
    
    if success_rate > 62.5:
        improvement = success_rate - 62.5
        print(f"✅ IMPROVEMENT: +{improvement:.1f}% success rate increase")
    elif success_rate >= 50:
        print(f"✅ MAINTAINED: Success rate within expected range")
    else:
        decline = 50 - success_rate
        print(f"❌ DECLINE: -{decline:.1f}% success rate decrease")
    
    print(f"\n📋 ENDPOINT RESULTS:")
    for result in results:
        status = "✅ WORKING" if result['success'] else "❌ FAILED"
        print(f"{status} {result['name']} ({result['path']})")
    
    return success_rate >= 75.0

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 TESTING COMPLETED SUCCESSFULLY - TARGET SUCCESS RATE ACHIEVED")
    else:
        print("\n⚠️ TESTING COMPLETED - SUCCESS RATE BELOW TARGET")