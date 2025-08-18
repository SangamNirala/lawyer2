#!/usr/bin/env python3
"""
Attorney Authentication System Testing
Testing the attorney authentication system with focus on demo account login issue.

Test Plan:
1. Test Attorney Login Endpoint with demo credentials
2. Check if Demo Account Exists in database
3. Create Demo Account if missing
4. Test Complete Login Flow
5. Test Token Validation
"""

import requests
import json
import time
import sys
from datetime import datetime
import jwt

# Use production URL from frontend .env
BASE_URL = "https://strat-engine-ai.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_attorney_login_with_demo_credentials():
    """
    Test POST /api/attorney/login with demo credentials:
    - Email: demo@attorney.com
    - Password: demo123
    """
    log_test("🎯 TESTING: POST /api/attorney/login with demo credentials")
    
    endpoint = f"{BASE_URL}/api/attorney/login"
    demo_credentials = {
        "email": "demo@attorney.com",
        "password": "demo123"
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=demo_credentials, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ SUCCESS: Demo attorney login successful")
            log_test(f"Response: {json.dumps(data, indent=2)}")
            
            # Check for required fields
            required_fields = ['token', 'attorney', 'expires_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                log_test("✅ All required fields present in response")
                return True, data, "Login successful with all required fields"
            else:
                log_test(f"⚠️  Missing fields: {missing_fields}")
                return True, data, f"Login successful but missing fields: {missing_fields}"
                
        elif response.status_code == 401:
            log_test("❌ FAIL: Invalid credentials - Demo account may not exist")
            return False, None, "Invalid credentials - Demo account missing"
        elif response.status_code == 503:
            log_test("❌ FAIL: Compliance system not available")
            return False, None, "Compliance system not available"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, None, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, None, f"Exception: {str(e)}"

def create_demo_attorney_account():
    """
    Create demo attorney account using POST /api/attorney/create with demo data:
    - Email: demo@attorney.com
    - Password: demo123
    - First Name: Demo
    - Last Name: Attorney
    - Bar Number: DEMO123
    - Role: supervising_attorney
    - Jurisdiction: US
    """
    log_test("🎯 CREATING: Demo attorney account")
    
    endpoint = f"{BASE_URL}/api/attorney/create"
    demo_attorney_data = {
        "email": "demo@attorney.com",
        "first_name": "Demo",
        "last_name": "Attorney",
        "bar_number": "DEMO123",
        "jurisdiction": "US",
        "role": "supervising_attorney",
        "specializations": ["contract_law", "business_law", "general_practice"],
        "years_experience": 5,
        "password": "demo123"
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=demo_attorney_data, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ SUCCESS: Demo attorney account created")
            log_test(f"Response: {json.dumps(data, indent=2)}")
            return True, data, "Demo attorney account created successfully"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, None, f"HTTP {response.status_code} error: {response.text}"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, None, f"Exception: {str(e)}"

def create_demo_attorney_using_dedicated_endpoint():
    """
    Alternative method: Create demo attorney using dedicated endpoint
    POST /api/attorney/create-demo-attorney
    """
    log_test("🎯 CREATING: Demo attorney using dedicated endpoint")
    
    endpoint = f"{BASE_URL}/api/attorney/create-demo-attorney"
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ SUCCESS: Demo attorney created via dedicated endpoint")
            log_test(f"Response: {json.dumps(data, indent=2)}")
            return True, data, "Demo attorney created via dedicated endpoint"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, None, f"HTTP {response.status_code} error: {response.text}"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, None, f"Exception: {str(e)}"

def test_jwt_token_validation(token):
    """
    Test JWT token validation by decoding and checking structure
    """
    log_test("🎯 TESTING: JWT token validation")
    
    try:
        # Decode token without verification to check structure
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        log_test(f"Token payload: {json.dumps(decoded_token, indent=2)}")
        
        # Check for required claims
        required_claims = ['attorney_id', 'email', 'role', 'exp']
        missing_claims = [claim for claim in required_claims if claim not in decoded_token]
        
        if not missing_claims:
            log_test("✅ JWT token has all required claims")
            
            # Check expiration
            exp_timestamp = decoded_token.get('exp')
            current_timestamp = time.time()
            
            if exp_timestamp > current_timestamp:
                log_test(f"✅ Token is valid (expires at {datetime.fromtimestamp(exp_timestamp)})")
                return True, "JWT token is valid with all required claims"
            else:
                log_test(f"❌ Token is expired (expired at {datetime.fromtimestamp(exp_timestamp)})")
                return False, "JWT token is expired"
        else:
            log_test(f"❌ Missing claims in JWT token: {missing_claims}")
            return False, f"Missing claims: {missing_claims}"
            
    except jwt.InvalidTokenError as e:
        log_test(f"❌ Invalid JWT token: {str(e)}")
        return False, f"Invalid JWT token: {str(e)}"
    except Exception as e:
        log_test(f"❌ Error validating token: {str(e)}")
        return False, f"Token validation error: {str(e)}"

def test_attorney_profile_with_token(attorney_id, token):
    """
    Test attorney profile endpoint with JWT token
    """
    log_test(f"🎯 TESTING: GET /api/attorney/profile/{attorney_id} with JWT token")
    
    endpoint = f"{BASE_URL}/api/attorney/profile/{attorney_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.get(endpoint, headers=headers, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test(f"✅ SUCCESS: Attorney profile retrieved")
            log_test(f"Profile data: {json.dumps(data, indent=2)}")
            return True, "Attorney profile retrieved successfully"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code} error"
            
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def main():
    """Run comprehensive attorney authentication testing"""
    log_test("🚀 STARTING ATTORNEY AUTHENTICATION SYSTEM TESTING")
    log_test(f"Base URL: {BASE_URL}")
    log_test("=" * 80)
    
    results = []
    
    # Step 1: Test attorney login with demo credentials
    log_test("\n📋 STEP 1: Testing attorney login with demo credentials")
    login_success, login_data, login_message = test_attorney_login_with_demo_credentials()
    results.append(("Demo Attorney Login", login_success, login_message))
    
    # If login failed, try to create demo account
    if not login_success and "Demo account missing" in login_message:
        log_test("\n📋 STEP 2: Demo account missing - attempting to create")
        
        # Try dedicated endpoint first
        create_success, create_data, create_message = create_demo_attorney_using_dedicated_endpoint()
        results.append(("Create Demo Attorney (Dedicated)", create_success, create_message))
        
        # If dedicated endpoint failed, try regular create endpoint
        if not create_success:
            log_test("\n📋 STEP 2b: Trying regular create attorney endpoint")
            create_success, create_data, create_message = create_demo_attorney_account()
            results.append(("Create Demo Attorney (Regular)", create_success, create_message))
        
        # If account creation succeeded, try login again
        if create_success:
            log_test("\n📋 STEP 3: Retrying login after account creation")
            login_success, login_data, login_message = test_attorney_login_with_demo_credentials()
            results.append(("Demo Attorney Login (Retry)", login_success, login_message))
    
    # If we have successful login, test token validation and profile access
    if login_success and login_data:
        token = login_data.get('token')
        attorney_data = login_data.get('attorney', {})
        attorney_id = attorney_data.get('id') or attorney_data.get('attorney_id')
        
        if token:
            log_test("\n📋 STEP 4: Testing JWT token validation")
            token_valid, token_message = test_jwt_token_validation(token)
            results.append(("JWT Token Validation", token_valid, token_message))
            
            if attorney_id:
                log_test("\n📋 STEP 5: Testing attorney profile access with token")
                profile_success, profile_message = test_attorney_profile_with_token(attorney_id, token)
                results.append(("Attorney Profile Access", profile_success, profile_message))
            else:
                log_test("⚠️  No attorney_id found in login response - skipping profile test")
                results.append(("Attorney Profile Access", False, "No attorney_id in login response"))
        else:
            log_test("⚠️  No token found in login response - skipping token validation")
            results.append(("JWT Token Validation", False, "No token in login response"))
    
    # Summary
    log_test("\n" + "=" * 80)
    log_test("📊 ATTORNEY AUTHENTICATION TESTING SUMMARY")
    log_test("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        log_test(f"{status}: {test_name} - {details}")
        if success:
            passed += 1
        else:
            failed += 1
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    log_test(f"\nTotal Tests: {total}")
    log_test(f"Passed: {passed}")
    log_test(f"Failed: {failed}")
    log_test(f"Success Rate: {success_rate:.1f}%")
    
    # Determine overall result
    if login_success:
        log_test("🎉 ATTORNEY AUTHENTICATION: WORKING")
        log_test("✅ Demo account login issue has been resolved")
        return 0
    else:
        log_test("🚨 ATTORNEY AUTHENTICATION: NEEDS ATTENTION")
        log_test("❌ Demo account login issue persists")
        return 1

if __name__ == "__main__":
    sys.exit(main())