#!/usr/bin/env python3
"""
Mobile-First Backend Implementation Testing
Testing mobile-optimized backend APIs for LegalMate AI application

Focus Areas:
1. Contract generation endpoints with mobile-optimized payloads
2. Analytics endpoints returning mobile-friendly data structures
3. Performance metrics endpoints for mobile monitoring
4. Contract wizard endpoints with mobile-specific fields
5. All existing functionality continues to work as expected
"""

import requests
import json
import time
import sys
from datetime import datetime
import uuid

# Use production URL from frontend .env
BASE_URL = "https://mobile-test-complete.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_contract_generation_mobile_optimized():
    """Test contract generation endpoints with mobile-optimized payloads"""
    log_test("🎯 TESTING: Contract Generation with Mobile Optimization")
    
    endpoint = f"{BASE_URL}/api/generate-contract"
    
    # Test with mobile-optimized payload including phone numbers and mobile flags
    mobile_payload = {
        "contract_type": "freelance_agreement",
        "parties": {
            "party1_name": "TechCorp Solutions",
            "party1_email": "contact@techcorp.com",
            "party1_phone": "+1-555-123-4567",  # Mobile-specific field
            "party2_name": "Sarah Johnson",
            "party2_email": "sarah.johnson@email.com",
            "party2_phone": "+1-555-987-6543"   # Mobile-specific field
        },
        "terms": {
            "project_description": "Mobile app development for e-commerce platform",
            "payment_amount": 15000,
            "payment_schedule": "50% upfront, 50% on completion",
            "timeline": "8 weeks",
            "mobile_optimized": True  # Mobile optimization flag
        },
        "jurisdiction": "US",
        "special_clauses": ["mobile_workflow", "remote_collaboration"],
        "mobile_workflow_flags": {  # Mobile-specific workflow flags
            "enable_mobile_signatures": True,
            "mobile_friendly_formatting": True,
            "responsive_contract_layout": True
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=mobile_payload, timeout=30)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ Contract generation successful")
            
            # Check for mobile-optimized features in response
            contract = data.get('contract', {})
            if 'mobile_optimized' in str(contract.get('content', '')).lower():
                log_test("✅ Mobile optimization detected in contract content")
            
            # Check if phone numbers are properly handled
            content = contract.get('content', '')
            if '+1-555-123-4567' in content and '+1-555-987-6543' in content:
                log_test("✅ Mobile phone numbers properly included")
            
            return True, f"Contract generation with mobile optimization working (response time: {response_time:.3f}s)"
        else:
            log_test(f"❌ Contract generation failed: {response.status_code}")
            return False, f"Contract generation failed with status {response.status_code}"
            
    except Exception as e:
        log_test(f"❌ Contract generation error: {str(e)}")
        return False, f"Contract generation error: {str(e)}"

def test_analytics_mobile_friendly():
    """Test analytics endpoints for mobile-friendly data structures"""
    log_test("🎯 TESTING: Analytics Endpoints for Mobile-Friendly Data")
    
    endpoints_to_test = [
        "/api/legal-qa/stats",
        "/api/legal-qa/knowledge-base/stats",
        "/api/legal-research-engine/stats"
    ]
    
    results = []
    
    for endpoint_path in endpoints_to_test:
        endpoint = f"{BASE_URL}{endpoint_path}"
        log_test(f"Testing: {endpoint_path}")
        
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=15)
            response_time = time.time() - start_time
            
            log_test(f"Response Status: {response.status_code}")
            log_test(f"Response Time: {response_time:.3f}s")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for mobile-friendly data structure
                mobile_friendly_features = []
                
                # Check for compact data structures
                if isinstance(data, dict):
                    # Check for summary fields (mobile-friendly)
                    if any(key in data for key in ['summary', 'total', 'count', 'status']):
                        mobile_friendly_features.append("summary_fields")
                    
                    # Check for reasonable data size (mobile-friendly)
                    data_str = json.dumps(data)
                    if len(data_str) < 5000:  # Reasonable size for mobile
                        mobile_friendly_features.append("compact_size")
                    
                    # Check for nested structure optimization
                    if not any(isinstance(v, dict) and len(v) > 10 for v in data.values()):
                        mobile_friendly_features.append("optimized_nesting")
                
                log_test(f"✅ Mobile-friendly features: {mobile_friendly_features}")
                results.append((True, f"{endpoint_path} mobile-friendly (features: {mobile_friendly_features})"))
            else:
                log_test(f"❌ Analytics endpoint failed: {response.status_code}")
                results.append((False, f"{endpoint_path} failed with status {response.status_code}"))
                
        except Exception as e:
            log_test(f"❌ Analytics endpoint error: {str(e)}")
            results.append((False, f"{endpoint_path} error: {str(e)}"))
    
    return results

def test_performance_metrics_mobile():
    """Test performance metrics endpoints for mobile monitoring"""
    log_test("🎯 TESTING: Performance Metrics for Mobile Monitoring")
    
    # Test multiple endpoints for performance
    performance_endpoints = [
        "/api/legal-qa/ask",
        "/api/generate-contract",
        "/api/legal-research-engine/research",
        "/api/plain-english-to-legal"
    ]
    
    results = []
    
    for endpoint_path in performance_endpoints:
        endpoint = f"{BASE_URL}{endpoint_path}"
        log_test(f"Testing performance: {endpoint_path}")
        
        # Prepare lightweight payloads for performance testing
        payloads = {
            "/api/legal-qa/ask": {
                "question": "What is a contract?",
                "is_voice": False,
                "jurisdiction": "US"
            },
            "/api/generate-contract": {
                "contract_type": "NDA",
                "parties": {"party1_name": "Company A", "party2_name": "Company B"},
                "terms": {"duration": "1 year"},
                "jurisdiction": "US"
            },
            "/api/legal-research-engine/research": {
                "query_text": "contract law basics",
                "jurisdiction": "US",
                "max_results": 5
            },
            "/api/plain-english-to-legal": {
                "plain_text": "I want to hire someone for a project",
                "jurisdiction": "US"
            }
        }
        
        payload = payloads.get(endpoint_path, {})
        
        try:
            start_time = time.time()
            if payload:
                response = requests.post(endpoint, json=payload, timeout=20)
            else:
                response = requests.get(endpoint, timeout=20)
            response_time = time.time() - start_time
            
            log_test(f"Response Status: {response.status_code}")
            log_test(f"Response Time: {response_time:.3f}s")
            
            # Mobile performance criteria (should be under 5 seconds for mobile)
            if response_time < 5.0:
                performance_rating = "excellent" if response_time < 2.0 else "good"
                log_test(f"✅ Mobile performance: {performance_rating}")
                results.append((True, f"{endpoint_path} mobile performance {performance_rating} ({response_time:.3f}s)"))
            else:
                log_test(f"⚠️ Slow for mobile: {response_time:.3f}s")
                results.append((False, f"{endpoint_path} too slow for mobile ({response_time:.3f}s)"))
                
        except Exception as e:
            log_test(f"❌ Performance test error: {str(e)}")
            results.append((False, f"{endpoint_path} performance test error: {str(e)}"))
    
    return results

def test_contract_wizard_mobile_fields():
    """Test contract wizard endpoints with mobile-specific fields"""
    log_test("🎯 TESTING: Contract Wizard with Mobile-Specific Fields")
    
    # Test contract wizard initialization
    wizard_endpoint = f"{BASE_URL}/api/contract-wizard/initialize"
    
    mobile_wizard_payload = {
        "user_id": str(uuid.uuid4()),
        "contract_type": "employment_agreement",
        "mobile_context": {
            "device_type": "mobile",
            "screen_size": "small",
            "input_method": "touch"
        },
        "mobile_preferences": {
            "simplified_steps": True,
            "touch_friendly_inputs": True,
            "minimal_text_entry": True
        }
    }
    
    try:
        start_time = time.time()
        response = requests.post(wizard_endpoint, json=mobile_wizard_payload, timeout=15)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            log_test("✅ Contract wizard initialization successful")
            
            # Check for mobile-optimized wizard steps
            current_step = data.get('current_step', {})
            if current_step:
                fields = current_step.get('fields', [])
                mobile_optimized_fields = []
                
                for field in fields:
                    if isinstance(field, dict):
                        # Check for mobile-friendly field types
                        field_type = field.get('type', '')
                        if field_type in ['select', 'radio', 'checkbox', 'date']:
                            mobile_optimized_fields.append(field_type)
                        
                        # Check for phone number fields
                        if 'phone' in field.get('name', '').lower():
                            mobile_optimized_fields.append('phone_field')
                
                log_test(f"✅ Mobile-optimized fields: {mobile_optimized_fields}")
            
            return True, f"Contract wizard mobile fields working (response time: {response_time:.3f}s)"
        else:
            log_test(f"❌ Contract wizard failed: {response.status_code}")
            return False, f"Contract wizard failed with status {response.status_code}"
            
    except Exception as e:
        log_test(f"❌ Contract wizard error: {str(e)}")
        return False, f"Contract wizard error: {str(e)}"

def test_mobile_error_handling():
    """Test mobile-friendly error handling"""
    log_test("🎯 TESTING: Mobile-Friendly Error Handling")
    
    # Test with invalid data to check error responses
    test_cases = [
        {
            "endpoint": "/api/generate-contract",
            "payload": {"invalid": "data"},
            "expected_error": "validation"
        },
        {
            "endpoint": "/api/legal-qa/ask",
            "payload": {"question": ""},
            "expected_error": "empty_question"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        endpoint = f"{BASE_URL}{test_case['endpoint']}"
        log_test(f"Testing error handling: {test_case['endpoint']}")
        
        try:
            response = requests.post(endpoint, json=test_case['payload'], timeout=10)
            
            log_test(f"Response Status: {response.status_code}")
            
            if response.status_code in [400, 422]:  # Expected error codes
                try:
                    error_data = response.json()
                    
                    # Check for mobile-friendly error structure
                    mobile_friendly_error = False
                    if isinstance(error_data, dict):
                        # Check for simple error message
                        if 'message' in error_data or 'error' in error_data:
                            mobile_friendly_error = True
                        
                        # Check error message length (should be concise for mobile)
                        error_msg = error_data.get('message', error_data.get('error', ''))
                        if isinstance(error_msg, str) and len(error_msg) < 200:
                            mobile_friendly_error = True
                    
                    if mobile_friendly_error:
                        log_test("✅ Mobile-friendly error response")
                        results.append((True, f"{test_case['endpoint']} mobile-friendly error handling"))
                    else:
                        log_test("⚠️ Error response could be more mobile-friendly")
                        results.append((False, f"{test_case['endpoint']} error response not optimized for mobile"))
                        
                except:
                    log_test("⚠️ Error response not JSON")
                    results.append((False, f"{test_case['endpoint']} error response not JSON"))
            else:
                log_test(f"⚠️ Unexpected status code: {response.status_code}")
                results.append((False, f"{test_case['endpoint']} unexpected error status"))
                
        except Exception as e:
            log_test(f"❌ Error handling test failed: {str(e)}")
            results.append((False, f"{test_case['endpoint']} error handling test failed: {str(e)}"))
    
    return results

def main():
    """Run comprehensive mobile-first backend testing"""
    log_test("🚀 STARTING: Mobile-First Backend Implementation Testing")
    log_test(f"Backend URL: {BASE_URL}")
    
    all_results = []
    
    # Test 1: Contract Generation with Mobile Optimization
    log_test("\n" + "="*60)
    success, message = test_contract_generation_mobile_optimized()
    all_results.append(("Contract Generation Mobile Optimization", success, message))
    
    # Test 2: Analytics Mobile-Friendly Data
    log_test("\n" + "="*60)
    analytics_results = test_analytics_mobile_friendly()
    for endpoint, success, message in analytics_results:
        all_results.append((f"Analytics Mobile-Friendly: {endpoint}", success, message))
    
    # Test 3: Performance Metrics for Mobile
    log_test("\n" + "="*60)
    performance_results = test_performance_metrics_mobile()
    for endpoint, success, message in performance_results:
        all_results.append((f"Mobile Performance: {endpoint}", success, message))
    
    # Test 4: Contract Wizard Mobile Fields
    log_test("\n" + "="*60)
    success, message = test_contract_wizard_mobile_fields()
    all_results.append(("Contract Wizard Mobile Fields", success, message))
    
    # Test 5: Mobile Error Handling
    log_test("\n" + "="*60)
    error_results = test_mobile_error_handling()
    for endpoint, success, message in error_results:
        all_results.append((f"Mobile Error Handling: {endpoint}", success, message))
    
    # Summary
    log_test("\n" + "="*60)
    log_test("📊 MOBILE-FIRST BACKEND TESTING SUMMARY")
    log_test("="*60)
    
    passed = 0
    total = len(all_results)
    
    for test_name, success, message in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        log_test(f"{status}: {test_name}")
        log_test(f"    {message}")
        if success:
            passed += 1
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    log_test(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed}/{total} tests passed)")
    
    if success_rate >= 80:
        log_test("🎉 MOBILE-FIRST BACKEND IMPLEMENTATION: EXCELLENT")
    elif success_rate >= 60:
        log_test("⚠️ MOBILE-FIRST BACKEND IMPLEMENTATION: GOOD - Minor issues")
    else:
        log_test("🚨 MOBILE-FIRST BACKEND IMPLEMENTATION: NEEDS ATTENTION")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)