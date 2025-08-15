#!/usr/bin/env python3
"""
Focused Legal Research Engine Testing
Testing the 8 specific endpoints mentioned in the review request with 30-second timeouts.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "https://lawtech-testing.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_endpoint(name, method, endpoint, payload=None, timeout=30):
    """Generic endpoint testing function"""
    log_test(f"🎯 TESTING: {name}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        start_time = time.time()
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=payload, timeout=timeout)
        
        response_time = time.time() - start_time
        
        log_test(f"Status: {response.status_code}, Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            log_test(f"✅ {name}: WORKING")
            return True
        elif response.status_code == 503:
            log_test(f"❌ {name}: Service Unavailable (503)")
            log_test(f"Response: {response.text[:100]}")
            return False
        else:
            log_test(f"❌ {name}: Status {response.status_code}")
            log_test(f"Response: {response.text[:100]}")
            return False
            
    except requests.exceptions.Timeout:
        log_test(f"❌ {name}: TIMEOUT (>{timeout}s)")
        return False
    except Exception as e:
        log_test(f"❌ {name}: ERROR - {str(e)}")
        return False

def main():
    """Test all 8 Legal Research Engine endpoints"""
    log_test("🚀 LEGAL RESEARCH ENGINE ENDPOINT TESTING")
    log_test(f"Base URL: {BASE_URL}")
    log_test("=" * 60)
    
    results = []
    
    # 1. Stats Endpoint
    results.append(test_endpoint(
        "Legal Research Engine Stats",
        "GET",
        "/api/legal-research-engine/stats"
    ))
    
    # 2. Main Research Endpoint
    results.append(test_endpoint(
        "Main Research Endpoint",
        "POST",
        "/api/legal-research-engine/research",
        {
            "query_text": "contract breach liability",
            "research_type": "comprehensive",
            "jurisdiction": "US",
            "legal_domain": "contract_law"
        }
    ))
    
    # 3. Precedent Search Endpoint
    results.append(test_endpoint(
        "Precedent Search Endpoint",
        "POST",
        "/api/legal-research-engine/precedent-search",
        {
            "query_case": {
                "case_facts": "Contract breach involving delivery of goods",
                "legal_issues": ["breach of contract", "damages"],
                "jurisdiction": "US"
            },
            "max_results": 10
        }
    ))
    
    # 4. Citation Analysis Endpoint
    results.append(test_endpoint(
        "Citation Analysis Endpoint",
        "POST",
        "/api/legal-research-engine/citation-analysis",
        {
            "cases": [
                {
                    "case_id": "test_case_1",
                    "citation": "123 F.3d 456 (9th Cir. 2020)",
                    "title": "Test Contract Case"
                }
            ],
            "depth": 2
        }
    ))
    
    # 5. Generate Memo Endpoint
    results.append(test_endpoint(
        "Generate Memo Endpoint",
        "POST",
        "/api/legal-research-engine/generate-memo",
        {
            "memo_data": {
                "research_query": "contract breach liability analysis",
                "legal_issues": ["breach of contract", "damages"],
                "jurisdiction": "US"
            },
            "memo_type": "comprehensive"
        }
    ))
    
    # 6. Structure Arguments Endpoint
    results.append(test_endpoint(
        "Structure Arguments Endpoint",
        "POST",
        "/api/legal-research-engine/structure-arguments",
        {
            "argument_data": {
                "legal_question": "What remedies are available for breach of contract?",
                "case_facts": "Supplier failed to deliver goods",
                "jurisdiction": "US"
            },
            "argument_strength": "strong"
        }
    ))
    
    # 7. Multi-Jurisdiction Search Endpoint
    results.append(test_endpoint(
        "Multi-Jurisdiction Search Endpoint",
        "POST",
        "/api/legal-research-engine/multi-jurisdiction-search",
        {
            "query": "contract breach liability",
            "jurisdictions": ["US", "UK", "CA", "AU"],
            "legal_domain": "contract_law"
        }
    ))
    
    # 8. Quality Assessment Endpoint
    results.append(test_endpoint(
        "Quality Assessment Endpoint",
        "POST",
        "/api/legal-research-engine/quality-assessment",
        {
            "research_data": {
                "research_query": "contract breach liability",
                "results": [
                    {
                        "case_title": "Test Contract Case",
                        "citation": "123 F.3d 456",
                        "relevance_score": 0.85
                    }
                ],
                "jurisdiction": "US"
            }
        }
    ))
    
    # Summary
    working_count = sum(results)
    total_count = len(results)
    success_rate = (working_count / total_count) * 100
    
    log_test("\n" + "=" * 60)
    log_test("📊 LEGAL RESEARCH ENGINE TEST SUMMARY")
    log_test("=" * 60)
    log_test(f"Working Endpoints: {working_count}/{total_count}")
    log_test(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate > 12.5:
        log_test("🎉 IMPROVEMENT: Success rate increased from previous 12.5%")
    else:
        log_test("⚠️  NO IMPROVEMENT: Success rate still at or below 12.5%")
    
    endpoint_names = [
        "Stats", "Research", "Precedent Search", "Citation Analysis",
        "Generate Memo", "Structure Arguments", "Multi-Jurisdiction", "Quality Assessment"
    ]
    
    log_test("\nDetailed Results:")
    for i, (name, result) in enumerate(zip(endpoint_names, results)):
        status = "✅ WORKING" if result else "❌ FAILING"
        log_test(f"{i+1}. {name}: {status}")
    
    log_test("=" * 60)
    
    return working_count, total_count

if __name__ == "__main__":
    working, total = main()
    sys.exit(0)