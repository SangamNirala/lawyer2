#!/usr/bin/env python3
"""
Multi-Jurisdiction Search Endpoint Test
Re-testing the server-side normalization fix for multi-jurisdiction search endpoint
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://legal-api-debug-1.preview.emergentagent.com/api"

def test_multi_jurisdiction_search():
    """Test the multi-jurisdiction search endpoint with exact payload from review request"""
    
    print("🎯 MULTI-JURISDICTION SEARCH ENDPOINT TEST")
    print("=" * 60)
    
    # Exact payload from review request
    test_payload = {
        "query": "Breach of contract specific performance",
        "jurisdictions": ["US", "UK", "CA"],
        "legal_domain": "contract_law",
        "comparison_mode": True
    }
    
    endpoint = f"{BACKEND_URL}/legal-research-engine/multi-jurisdiction-search"
    
    print(f"Testing endpoint: {endpoint}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print()
    
    try:
        start_time = time.time()
        
        # Make the POST request
        response = requests.post(
            endpoint,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("✅ SUCCESS: Received 200 OK response")
                
                # Check expected JSON structure
                expected_keys = [
                    "query", 
                    "jurisdictions_searched", 
                    "results", 
                    "comparison_analysis", 
                    "jurisdiction_recommendations", 
                    "total_results", 
                    "search_timestamp"
                ]
                
                print("\n📋 RESPONSE STRUCTURE VALIDATION:")
                all_keys_present = True
                
                for key in expected_keys:
                    if key in response_data:
                        value = response_data[key]
                        value_type = type(value).__name__
                        
                        if key == "jurisdictions_searched":
                            if isinstance(value, list):
                                print(f"✅ {key}: {value_type} - {value}")
                            else:
                                print(f"❌ {key}: Expected array, got {value_type}")
                                all_keys_present = False
                        elif key == "results":
                            if isinstance(value, list):
                                print(f"✅ {key}: {value_type} with {len(value)} items")
                            else:
                                print(f"❌ {key}: Expected array, got {value_type}")
                                all_keys_present = False
                        elif key == "comparison_analysis":
                            if isinstance(value, dict):
                                print(f"✅ {key}: {value_type} with {len(value)} properties")
                            else:
                                print(f"❌ {key}: Expected object, got {value_type}")
                                all_keys_present = False
                        elif key == "jurisdiction_recommendations":
                            if isinstance(value, list):
                                print(f"✅ {key}: {value_type} with {len(value)} items")
                            else:
                                print(f"❌ {key}: Expected array, got {value_type}")
                                all_keys_present = False
                        elif key == "total_results":
                            if isinstance(value, int):
                                print(f"✅ {key}: {value_type} - {value}")
                            else:
                                print(f"❌ {key}: Expected int, got {value_type}")
                                all_keys_present = False
                        elif key == "search_timestamp":
                            if isinstance(value, (str, int, float)):
                                print(f"✅ {key}: {value_type} - {value}")
                            else:
                                print(f"❌ {key}: Expected string or timestamp, got {value_type}")
                                all_keys_present = False
                        else:
                            print(f"✅ {key}: {value_type}")
                    else:
                        print(f"❌ {key}: MISSING")
                        all_keys_present = False
                
                print(f"\n📊 RESPONSE DATA SAMPLE:")
                print(f"Query: {response_data.get('query', 'N/A')}")
                print(f"Jurisdictions Searched: {response_data.get('jurisdictions_searched', 'N/A')}")
                print(f"Total Results: {response_data.get('total_results', 'N/A')}")
                
                if all_keys_present:
                    print("\n🎉 PASS: All expected keys present with correct types")
                    return True, "Multi-jurisdiction search endpoint working correctly with proper response structure"
                else:
                    print("\n❌ FAIL: Missing or incorrect response structure")
                    return False, "Response structure validation failed - missing or incorrect keys"
                    
            except json.JSONDecodeError as e:
                print(f"❌ FAIL: Invalid JSON response - {e}")
                print(f"Raw response: {response.text[:500]}...")
                return False, f"Invalid JSON response: {e}"
                
        else:
            print(f"❌ FAIL: Expected 200 OK, got {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
                return False, f"HTTP {response.status_code}: {error_data.get('detail', response.text)}"
            except:
                print(f"Raw error response: {response.text}")
                return False, f"HTTP {response.status_code}: {response.text}"
                
    except requests.exceptions.Timeout:
        print("❌ FAIL: Request timeout (30s)")
        return False, "Request timeout after 30 seconds"
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAIL: Connection error - {e}")
        return False, f"Connection error: {e}"
        
    except Exception as e:
        print(f"❌ FAIL: Unexpected error - {e}")
        return False, f"Unexpected error: {e}"

def main():
    """Main test execution"""
    print("🚀 STARTING MULTI-JURISDICTION SEARCH ENDPOINT TEST")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    success, message = test_multi_jurisdiction_search()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST RESULT: PASS")
        print(f"✅ {message}")
    else:
        print("❌ TEST RESULT: FAIL")
        print(f"❌ {message}")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")
    
    return success, message

if __name__ == "__main__":
    main()