#!/usr/bin/env python3
"""
Smart Contract Wizard Backend Testing
Testing contract wizard API endpoints to ensure mobile wizard component integration works correctly.
Focus areas:
1. Contract wizard initialization endpoint
2. Field suggestions endpoint  
3. Contract generation with wizard data
4. Party information and contract terms processing
5. No regressions in existing contract generation functionality
"""

import requests
import json
import time
import sys
from datetime import datetime
import uuid

# Use production URL from frontend .env
BASE_URL = "https://strat-engine-ai.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_contract_wizard_initialization():
    """Test POST /api/contract-wizard/initialize endpoint"""
    log_test("🎯 TESTING: POST /api/contract-wizard/initialize - Contract Wizard Initialization")
    
    endpoint = f"{BASE_URL}/api/contract-wizard/initialize"
    
    # Test different contract types that mobile wizard supports
    test_cases = [
        {
            "name": "NDA Contract Initialization",
            "payload": {
                "contract_type": "NDA",
                "current_step": 1,
                "partial_data": {}
            }
        },
        {
            "name": "Employment Agreement Initialization", 
            "payload": {
                "contract_type": "employment_agreement",
                "current_step": 1,
                "partial_data": {}
            }
        },
        {
            "name": "Freelance Agreement Initialization",
            "payload": {
                "contract_type": "freelance_agreement", 
                "current_step": 2,
                "partial_data": {
                    "contract_type": "freelance_agreement",
                    "jurisdiction": "US"
                }
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        log_test(f"Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(endpoint, json=test_case['payload'], timeout=15)
            response_time = time.time() - start_time
            
            log_test(f"Response Status: {response.status_code}")
            log_test(f"Response Time: {response_time:.3f}s")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['current_step', 'suggestions', 'progress', 'estimated_completion_time']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    log_test(f"✅ {test_case['name']}: SUCCESS")
                    log_test(f"   - Current Step: {data['current_step']['step_number']}")
                    log_test(f"   - Step Title: {data['current_step']['title']}")
                    log_test(f"   - Suggestions Count: {len(data['suggestions'])}")
                    log_test(f"   - Progress: {data['progress']}")
                    log_test(f"   - Estimated Time: {data['estimated_completion_time']}")
                    
                    # Validate current_step structure
                    step = data['current_step']
                    step_fields = ['step_number', 'title', 'description', 'fields']
                    step_missing = [field for field in step_fields if field not in step]
                    
                    if not step_missing:
                        log_test(f"   - Step Fields Count: {len(step['fields'])}")
                        results.append({"test": test_case['name'], "status": "PASS", "response_time": response_time})
                    else:
                        log_test(f"❌ {test_case['name']}: Missing step fields: {step_missing}")
                        results.append({"test": test_case['name'], "status": "FAIL", "error": f"Missing step fields: {step_missing}"})
                else:
                    log_test(f"❌ {test_case['name']}: Missing required fields: {missing_fields}")
                    results.append({"test": test_case['name'], "status": "FAIL", "error": f"Missing fields: {missing_fields}"})
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text[:200]}"
                
                log_test(f"❌ {test_case['name']}: {error_msg}")
                results.append({"test": test_case['name'], "status": "FAIL", "error": error_msg})
                
        except requests.exceptions.Timeout:
            log_test(f"❌ {test_case['name']}: TIMEOUT (>15s)")
            results.append({"test": test_case['name'], "status": "FAIL", "error": "Timeout"})
        except Exception as e:
            log_test(f"❌ {test_case['name']}: ERROR - {str(e)}")
            results.append({"test": test_case['name'], "status": "FAIL", "error": str(e)})
    
    return results

def test_contract_wizard_field_suggestions():
    """Test POST /api/contract-wizard/suggestions endpoint"""
    log_test("🎯 TESTING: POST /api/contract-wizard/suggestions - Field Suggestions")
    
    endpoint = f"{BASE_URL}/api/contract-wizard/suggestions"
    
    # Test field suggestions for different contract types and fields
    test_cases = [
        {
            "name": "NDA Party Name Suggestions",
            "payload": {
                "contract_type": "NDA",
                "field_name": "party1_name",
                "context": {"step": 2}
            }
        },
        {
            "name": "Employment Payment Terms Suggestions",
            "payload": {
                "contract_type": "employment_agreement",
                "field_name": "payment_terms", 
                "context": {"step": 3, "industry": "technology"}
            }
        },
        {
            "name": "Freelance Deliverables Suggestions",
            "payload": {
                "contract_type": "freelance_agreement",
                "field_name": "deliverables",
                "context": {"step": 3, "project_type": "web_development"}
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        log_test(f"Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(endpoint, json=test_case['payload'], timeout=10)
            response_time = time.time() - start_time
            
            log_test(f"Response Status: {response.status_code}")
            log_test(f"Response Time: {response_time:.3f}s")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'suggestions' in data:
                    suggestions = data['suggestions']
                    log_test(f"✅ {test_case['name']}: SUCCESS")
                    log_test(f"   - Suggestions Count: {len(suggestions)}")
                    
                    # Validate suggestion structure
                    if suggestions:
                        first_suggestion = suggestions[0]
                        required_fields = ['field_name', 'suggested_value', 'confidence', 'reasoning', 'source']
                        missing_fields = [field for field in required_fields if field not in first_suggestion]
                        
                        if not missing_fields:
                            log_test(f"   - First Suggestion: {first_suggestion['suggested_value']}")
                            log_test(f"   - Confidence: {first_suggestion['confidence']}")
                            log_test(f"   - Source: {first_suggestion['source']}")
                            results.append({"test": test_case['name'], "status": "PASS", "response_time": response_time})
                        else:
                            log_test(f"❌ {test_case['name']}: Missing suggestion fields: {missing_fields}")
                            results.append({"test": test_case['name'], "status": "FAIL", "error": f"Missing suggestion fields: {missing_fields}"})
                    else:
                        log_test(f"✅ {test_case['name']}: SUCCESS (No suggestions available)")
                        results.append({"test": test_case['name'], "status": "PASS", "response_time": response_time})
                else:
                    log_test(f"❌ {test_case['name']}: Missing 'suggestions' field in response")
                    results.append({"test": test_case['name'], "status": "FAIL", "error": "Missing suggestions field"})
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text[:200]}"
                
                log_test(f"❌ {test_case['name']}: {error_msg}")
                results.append({"test": test_case['name'], "status": "FAIL", "error": error_msg})
                
        except requests.exceptions.Timeout:
            log_test(f"❌ {test_case['name']}: TIMEOUT (>10s)")
            results.append({"test": test_case['name'], "status": "FAIL", "error": "Timeout"})
        except Exception as e:
            log_test(f"❌ {test_case['name']}: ERROR - {str(e)}")
            results.append({"test": test_case['name'], "status": "FAIL", "error": str(e)})
    
    return results

def test_contract_generation_with_wizard_data():
    """Test POST /api/generate-contract with data from mobile wizard"""
    log_test("🎯 TESTING: POST /api/generate-contract - Contract Generation with Wizard Data")
    
    endpoint = f"{BASE_URL}/api/generate-contract"
    
    # Test contract generation with realistic wizard data
    test_cases = [
        {
            "name": "NDA Generation from Mobile Wizard",
            "payload": {
                "contract_type": "NDA",
                "parties": {
                    "party1_name": "TechCorp Solutions",
                    "party1_email": "legal@techcorp.com",
                    "party1_address": "123 Innovation Drive, San Francisco, CA 94105",
                    "party2_name": "Creative Agency LLC", 
                    "party2_email": "contracts@creativeagency.com",
                    "party2_address": "456 Design Street, New York, NY 10001"
                },
                "terms": {
                    "confidentiality_period": "3 years",
                    "permitted_disclosures": "Legal compliance only",
                    "return_materials": "Within 30 days of termination"
                },
                "jurisdiction": "US",
                "special_clauses": ["mutual_confidentiality", "no_solicitation"],
                "execution_date": "2024-12-20"
            }
        },
        {
            "name": "Freelance Agreement from Mobile Wizard",
            "payload": {
                "contract_type": "freelance_agreement",
                "parties": {
                    "party1_name": "Digital Marketing Pro",
                    "party1_email": "sarah@digitalmarketingpro.com", 
                    "party1_address": "789 Freelancer Ave, Austin, TX 78701",
                    "party2_name": "StartupCo Inc",
                    "party2_email": "hiring@startupco.com",
                    "party2_address": "321 Startup Blvd, Seattle, WA 98101"
                },
                "terms": {
                    "project_scope": "Social media marketing campaign for Q1 2025",
                    "payment_amount": "$5,000",
                    "payment_terms": "50% upfront, 50% upon completion",
                    "project_duration": "3 months",
                    "deliverables": "Monthly reports, content calendar, ad campaigns"
                },
                "jurisdiction": "US",
                "special_clauses": ["intellectual_property_rights", "revision_policy"]
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        log_test(f"Testing: {test_case['name']}")
        
        try:
            start_time = time.time()
            response = requests.post(endpoint, json=test_case['payload'], timeout=30)
            response_time = time.time() - start_time
            
            log_test(f"Response Status: {response.status_code}")
            log_test(f"Response Time: {response_time:.3f}s")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'contract' in data:
                    contract = data['contract']
                    required_fields = ['id', 'contract_type', 'jurisdiction', 'content', 'clauses', 'compliance_score']
                    missing_fields = [field for field in required_fields if field not in contract]
                    
                    if not missing_fields:
                        log_test(f"✅ {test_case['name']}: SUCCESS")
                        log_test(f"   - Contract ID: {contract['id']}")
                        log_test(f"   - Contract Type: {contract['contract_type']}")
                        log_test(f"   - Jurisdiction: {contract['jurisdiction']}")
                        log_test(f"   - Content Length: {len(contract['content'])} characters")
                        log_test(f"   - Clauses Count: {len(contract['clauses'])}")
                        log_test(f"   - Compliance Score: {contract['compliance_score']}")
                        
                        # Validate party information is included in content
                        content = contract['content']
                        parties = test_case['payload']['parties']
                        
                        party_checks = []
                        if parties.get('party1_name') in content:
                            party_checks.append("Party 1 name found")
                        if parties.get('party2_name') in content:
                            party_checks.append("Party 2 name found")
                        
                        log_test(f"   - Party Information: {', '.join(party_checks) if party_checks else 'Not found'}")
                        
                        # Check for execution date if provided
                        if test_case['payload'].get('execution_date'):
                            if '[Date of Execution]' in content or test_case['payload']['execution_date'] in content:
                                log_test(f"   - Execution Date: Properly handled")
                            else:
                                log_test(f"   - Execution Date: Not found in content")
                        
                        results.append({"test": test_case['name'], "status": "PASS", "response_time": response_time})
                    else:
                        log_test(f"❌ {test_case['name']}: Missing contract fields: {missing_fields}")
                        results.append({"test": test_case['name'], "status": "FAIL", "error": f"Missing contract fields: {missing_fields}"})
                else:
                    log_test(f"❌ {test_case['name']}: Missing 'contract' field in response")
                    results.append({"test": test_case['name'], "status": "FAIL", "error": "Missing contract field"})
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text[:200]}"
                
                log_test(f"❌ {test_case['name']}: {error_msg}")
                results.append({"test": test_case['name'], "status": "FAIL", "error": error_msg})
                
        except requests.exceptions.Timeout:
            log_test(f"❌ {test_case['name']}: TIMEOUT (>30s)")
            results.append({"test": test_case['name'], "status": "FAIL", "error": "Timeout"})
        except Exception as e:
            log_test(f"❌ {test_case['name']}: ERROR - {str(e)}")
            results.append({"test": test_case['name'], "status": "FAIL", "error": str(e)})
    
    return results

def test_contract_retrieval_endpoints():
    """Test contract retrieval endpoints to ensure no regressions"""
    log_test("🎯 TESTING: Contract Retrieval Endpoints - Regression Testing")
    
    results = []
    
    # Test GET /api/contracts endpoint
    log_test("Testing: GET /api/contracts - List all contracts")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/contracts", timeout=10)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            contracts = response.json()
            log_test(f"✅ GET /api/contracts: SUCCESS")
            log_test(f"   - Contracts Count: {len(contracts)}")
            
            if contracts:
                # Validate first contract structure
                first_contract = contracts[0]
                required_fields = ['id', 'contract_type', 'jurisdiction', 'content']
                missing_fields = [field for field in required_fields if field not in first_contract]
                
                if not missing_fields:
                    log_test(f"   - Contract Structure: Valid")
                    results.append({"test": "GET /api/contracts", "status": "PASS", "response_time": response_time})
                else:
                    log_test(f"   - Contract Structure: Missing fields {missing_fields}")
                    results.append({"test": "GET /api/contracts", "status": "FAIL", "error": f"Missing fields: {missing_fields}"})
            else:
                log_test(f"   - No contracts found (empty database)")
                results.append({"test": "GET /api/contracts", "status": "PASS", "response_time": response_time})
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            log_test(f"❌ GET /api/contracts: {error_msg}")
            results.append({"test": "GET /api/contracts", "status": "FAIL", "error": error_msg})
            
    except Exception as e:
        log_test(f"❌ GET /api/contracts: ERROR - {str(e)}")
        results.append({"test": "GET /api/contracts", "status": "FAIL", "error": str(e)})
    
    return results

def test_party_information_processing():
    """Test that party information from mobile wizard is properly processed"""
    log_test("🎯 TESTING: Party Information Processing - Mobile Wizard Integration")
    
    endpoint = f"{BASE_URL}/api/generate-contract"
    
    # Test with comprehensive party information
    payload = {
        "contract_type": "consulting_agreement",
        "parties": {
            "party1_name": "Alexandra Johnson",
            "party1_email": "alex@consultingpro.com",
            "party1_address": "1234 Professional Way, Suite 100, Denver, CO 80202",
            "party1_phone": "+1 (555) 123-4567",
            "party2_name": "InnovateTech Solutions LLC",
            "party2_email": "contracts@innovatetech.com", 
            "party2_address": "5678 Technology Drive, Building B, Portland, OR 97201",
            "party2_phone": "+1 (555) 987-6543"
        },
        "terms": {
            "consulting_services": "Strategic business consulting and market analysis",
            "payment_rate": "$150 per hour",
            "payment_terms": "Net 15 days",
            "project_duration": "6 months",
            "work_location": "Remote with monthly on-site meetings"
        },
        "jurisdiction": "US",
        "special_clauses": ["confidentiality", "intellectual_property"]
    }
    
    log_test("Testing: Comprehensive Party Information Processing")
    
    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=25)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            contract = data['contract']
            content = contract['content']
            
            # Check if all party information is properly included
            party_info_checks = {
                "Party 1 Name": payload['parties']['party1_name'] in content,
                "Party 1 Email": payload['parties']['party1_email'] in content,
                "Party 2 Name": payload['parties']['party2_name'] in content,
                "Party 2 Email": payload['parties']['party2_email'] in content,
                "Party 1 Address": any(part in content for part in payload['parties']['party1_address'].split(', ')),
                "Party 2 Address": any(part in content for part in payload['parties']['party2_address'].split(', '))
            }
            
            # Check if contract terms are included
            terms_checks = {
                "Consulting Services": payload['terms']['consulting_services'] in content,
                "Payment Rate": payload['terms']['payment_rate'] in content,
                "Payment Terms": payload['terms']['payment_terms'] in content,
                "Project Duration": payload['terms']['project_duration'] in content
            }
            
            passed_party_checks = sum(party_info_checks.values())
            passed_terms_checks = sum(terms_checks.values())
            
            log_test(f"✅ Party Information Processing: SUCCESS")
            log_test(f"   - Party Information Included: {passed_party_checks}/6 checks passed")
            log_test(f"   - Contract Terms Included: {passed_terms_checks}/4 checks passed")
            
            for check, passed in party_info_checks.items():
                log_test(f"   - {check}: {'✓' if passed else '✗'}")
            
            for check, passed in terms_checks.items():
                log_test(f"   - {check}: {'✓' if passed else '✗'}")
            
            # Consider test passed if most information is included
            if passed_party_checks >= 4 and passed_terms_checks >= 3:
                return [{"test": "Party Information Processing", "status": "PASS", "response_time": response_time}]
            else:
                return [{"test": "Party Information Processing", "status": "FAIL", "error": "Insufficient party/terms information included"}]
        else:
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            log_test(f"❌ Party Information Processing: {error_msg}")
            return [{"test": "Party Information Processing", "status": "FAIL", "error": error_msg}]
            
    except Exception as e:
        log_test(f"❌ Party Information Processing: ERROR - {str(e)}")
        return [{"test": "Party Information Processing", "status": "FAIL", "error": str(e)}]

def main():
    """Run all Smart Contract Wizard backend tests"""
    log_test("🚀 STARTING: Smart Contract Wizard Backend Testing")
    log_test(f"Backend URL: {BASE_URL}")
    
    all_results = []
    
    # Test 1: Contract Wizard Initialization
    log_test("\n" + "="*60)
    initialization_results = test_contract_wizard_initialization()
    all_results.extend(initialization_results)
    
    # Test 2: Field Suggestions
    log_test("\n" + "="*60)
    suggestions_results = test_contract_wizard_field_suggestions()
    all_results.extend(suggestions_results)
    
    # Test 3: Contract Generation with Wizard Data
    log_test("\n" + "="*60)
    generation_results = test_contract_generation_with_wizard_data()
    all_results.extend(generation_results)
    
    # Test 4: Contract Retrieval (Regression Testing)
    log_test("\n" + "="*60)
    retrieval_results = test_contract_retrieval_endpoints()
    all_results.extend(retrieval_results)
    
    # Test 5: Party Information Processing
    log_test("\n" + "="*60)
    party_results = test_party_information_processing()
    all_results.extend(party_results)
    
    # Summary
    log_test("\n" + "="*60)
    log_test("📊 SMART CONTRACT WIZARD BACKEND TEST SUMMARY")
    log_test("="*60)
    
    passed_tests = [r for r in all_results if r['status'] == 'PASS']
    failed_tests = [r for r in all_results if r['status'] == 'FAIL']
    
    log_test(f"Total Tests: {len(all_results)}")
    log_test(f"Passed: {len(passed_tests)}")
    log_test(f"Failed: {len(failed_tests)}")
    log_test(f"Success Rate: {len(passed_tests)/len(all_results)*100:.1f}%")
    
    if passed_tests:
        log_test("\n✅ PASSED TESTS:")
        for test in passed_tests:
            response_time = test.get('response_time', 0)
            log_test(f"   - {test['test']} ({response_time:.3f}s)")
    
    if failed_tests:
        log_test("\n❌ FAILED TESTS:")
        for test in failed_tests:
            log_test(f"   - {test['test']}: {test['error']}")
    
    # Overall assessment
    success_rate = len(passed_tests) / len(all_results) * 100
    
    if success_rate >= 90:
        log_test("\n🎉 EXCELLENT: Smart Contract Wizard backend is working excellently!")
    elif success_rate >= 75:
        log_test("\n✅ GOOD: Smart Contract Wizard backend is working well with minor issues.")
    elif success_rate >= 50:
        log_test("\n⚠️ MODERATE: Smart Contract Wizard backend has some issues that need attention.")
    else:
        log_test("\n🚨 CRITICAL: Smart Contract Wizard backend has significant issues requiring immediate attention.")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)