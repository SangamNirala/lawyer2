#!/usr/bin/env python3
"""
Simple Phase 4 Advanced Intelligence Backend Test
=================================================

Quick verification of Phase 4 endpoints using requests library.
"""

import requests
import json
import time
import uuid

# Configuration
BACKEND_URL = "https://clever-jepsen.preview.emergentagent.com/api"
TEST_SESSION_ID = "test-session-123"
TEST_SCENARIO_ID = "test-scenario-456"

def test_endpoint(name, method, url, payload=None, expected_status=200):
    """Test a single endpoint"""
    print(f"\n🧪 Testing {name}...")
    start_time = time.time()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        response_time = time.time() - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Time: {response_time:.3f}s")
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                print(f"✅ {name} - SUCCESS")
                return True
            except:
                print(f"   Response: {response.text[:200]}...")
                print(f"✅ {name} - SUCCESS (non-JSON)")
                return True
        else:
            print(f"   Error: {response.text[:200]}...")
            print(f"❌ {name} - FAILED")
            return False
            
    except Exception as e:
        response_time = time.time() - start_time
        print(f"   Time: {response_time:.3f}s")
        print(f"   Exception: {str(e)}")
        print(f"❌ {name} - FAILED")
        return False

def main():
    """Run all Phase 4 tests"""
    print("🚀 Phase 4 Advanced Intelligence - Simple Backend Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Predictor Health
    results.append(test_endpoint(
        "Predictor Health",
        "GET",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/predictor/health"
    ))
    
    # Test 2: Strategy Updates
    results.append(test_endpoint(
        "Strategy Updates",
        "GET", 
        f"{BACKEND_URL}/ai-agents/contract-negotiation/strategy-updates/{TEST_SESSION_ID}"
    ))
    
    # Test 3: Analytics Overview
    results.append(test_endpoint(
        "Analytics Overview",
        "GET",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/overview"
    ))
    
    # Test 4: A/B Tests Analytics
    results.append(test_endpoint(
        "A/B Tests Analytics",
        "GET",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/ab-tests"
    ))
    
    # Test 5: Analytics Export CSV
    results.append(test_endpoint(
        "Analytics Export CSV",
        "GET",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/export?format=csv"
    ))
    
    # Test 6: Analytics Export JSON
    results.append(test_endpoint(
        "Analytics Export JSON",
        "GET",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/export?format=json"
    ))
    
    # Test 7: Feedback Endpoint
    feedback_payload = {
        "session_id": TEST_SESSION_ID,
        "scenario_id": TEST_SCENARIO_ID,
        "accepted": True,
        "counterparty_delay_sec": 300,
        "notes": "Test feedback"
    }
    results.append(test_endpoint(
        "Feedback Collection",
        "POST",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
        feedback_payload
    ))
    
    # Test 8: Enhanced Counter-Offer Generation
    counter_offer_payload = {
        "session_id": TEST_SESSION_ID,
        "goals": ["speed", "clarity"],
        "key_terms": ["payment terms"],
        "base_offer": {
            "price": 75000,
            "currency": "USD"
        }
    }
    results.append(test_endpoint(
        "Enhanced Counter-Offer Generation",
        "POST",
        f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
        counter_offer_payload
    ))
    
    # Summary
    total_tests = len(results)
    passed_tests = sum(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 85:
        print("\n🎉 Phase 4 Advanced Intelligence: FULLY OPERATIONAL")
    elif success_rate >= 70:
        print("\n⚠️ Phase 4 Advanced Intelligence: MOSTLY OPERATIONAL")
    else:
        print("\n❌ Phase 4 Advanced Intelligence: NEEDS ATTENTION")

if __name__ == "__main__":
    main()