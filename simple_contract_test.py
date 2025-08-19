#!/usr/bin/env python3
"""
Simple Contract Generation Test
Test basic contract generation with minimal data to isolate the issue
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://sector-insight.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_simple_contract_generation():
    """Test with minimal contract data"""
    log_test("🎯 TESTING: Simple Contract Generation")
    
    endpoint = f"{BASE_URL}/api/generate-contract"
    
    # Very simple payload
    payload = {
        "contract_type": "NDA",
        "parties": {
            "party1_name": "John Smith",
            "party2_name": "ABC Company"
        },
        "terms": {
            "duration": "2 years"
        },
        "jurisdiction": "US"
    }
    
    log_test("Testing: Minimal NDA Contract")
    log_test(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ SUCCESS: Contract generated successfully")
            log_test(f"Contract ID: {data['contract']['id']}")
            log_test(f"Content Length: {len(data['contract']['content'])} characters")
            return True
        else:
            log_test(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_detail = response.json()
                log_test(f"Error Detail: {error_detail}")
            except:
                log_test(f"Response Text: {response.text[:500]}")
            return False
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_simple_contract_generation()