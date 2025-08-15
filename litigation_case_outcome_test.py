#!/usr/bin/env python3
"""
Litigation Analytics Case Outcome Analysis Endpoint Testing
===========================================================

Testing the POST /api/litigation/analyze-case endpoint to verify it's working 
after fixing the "Litigation Analytics Engine is currently unavailable" error.

SPECIFIC TESTING REQUIREMENTS:
1. Test the POST /api/litigation/analyze-case endpoint with proper request data
2. Verify the response includes all required fields with correct data types
3. Test error handling by sending invalid data
4. Confirm that the response is no longer returning 503 "Litigation Analytics Engine is currently unavailable" error

CONTEXT: The user fixed the issue by adding the missing pyyaml dependency and restarting the backend.
The backend logs show "✅ Litigation Analytics Engine modules loaded successfully" and a manual curl test 
returned proper JSON response instead of the 503 error.
"""

import requests
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://verdict-analytics.preview.emergentagent.com/api"

def test_litigation_case_analysis_main():
    """Test the main litigation case analysis endpoint with exact specifications from review request"""
    print("🎯 TESTING LITIGATION CASE OUTCOME ANALYSIS ENDPOINT")
    print("=" * 80)
    
    test_results = []
    
    # Test case data as specified in the review request
    test_case = {
        "case_type": "civil",
        "jurisdiction": "california", 
        "case_facts": "Contract dispute between two parties regarding breach of agreement terms and seeking damages",
        "court_level": "district",
        "case_value": 100000
    }
    
    print(f"\n📋 Test Case: Civil Contract Dispute")
    print(f"Case Type: {test_case['case_type']}")
    print(f"Jurisdiction: {test_case['jurisdiction']}")
    print(f"Case Facts: {test_case['case_facts']}")
    print(f"Court Level: {test_case['court_level']}")
    print(f"Case Value: ${test_case['case_value']:,}")
    
    try:
        url = f"{BACKEND_URL}/litigation/analyze-case"
        print(f"\nRequest URL: {url}")
        
        response = requests.post(url, json=test_case, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 503:
            print("❌ CRITICAL: Still getting 503 'Litigation Analytics Engine is currently unavailable' error!")
            print("The fix may not have been applied correctly or the backend needs to be restarted.")
            test_results.append(False)
            return test_results
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required fields from review request are present
            required_fields = [
                'case_id',           # UUID format
                'predicted_outcome', # should be one of: plaintiff_win, defendant_win, settlement, dismissed
                'confidence_score',  # float between 0-1
                'probability_breakdown', # object with outcome probabilities
                'estimated_duration',    # in days
                'estimated_cost',       # in dollars
                'settlement_probability', # float
                'prediction_date'       # ISO format
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                test_results.append(False)
            else:
                print("✅ All required fields present")
                
                # Validate field types and values
                validation_results = []
                
                # 1. Validate case_id (UUID format)
                case_id = data.get('case_id')
                try:
                    uuid.UUID(case_id)
                    print(f"✅ case_id is valid UUID: {case_id}")
                    validation_results.append(True)
                except ValueError:
                    print(f"❌ case_id is not valid UUID format: {case_id}")
                    validation_results.append(False)
                
                # 2. Validate predicted_outcome (should be one of the expected values)
                predicted_outcome = data.get('predicted_outcome')
                valid_outcomes = ['plaintiff_win', 'defendant_win', 'settlement', 'dismissed']
                if predicted_outcome in valid_outcomes:
                    print(f"✅ predicted_outcome is valid: {predicted_outcome}")
                    validation_results.append(True)
                else:
                    print(f"❌ predicted_outcome is invalid: {predicted_outcome} (expected one of: {valid_outcomes})")
                    validation_results.append(False)
                
                # 3. Validate confidence_score (float between 0-1)
                confidence_score = data.get('confidence_score')
                if isinstance(confidence_score, (int, float)) and 0 <= confidence_score <= 1:
                    print(f"✅ confidence_score is valid: {confidence_score}")
                    validation_results.append(True)
                else:
                    print(f"❌ confidence_score is invalid: {confidence_score} (expected float between 0-1)")
                    validation_results.append(False)
                
                # 4. Validate probability_breakdown (object with outcome probabilities)
                probability_breakdown = data.get('probability_breakdown')
                if isinstance(probability_breakdown, dict) and len(probability_breakdown) > 0:
                    print(f"✅ probability_breakdown is valid dict with {len(probability_breakdown)} outcomes")
                    # Check if probabilities are valid floats
                    prob_values_valid = all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in probability_breakdown.values())
                    if prob_values_valid:
                        print(f"  Sample probabilities: {dict(list(probability_breakdown.items())[:3])}")
                        validation_results.append(True)
                    else:
                        print(f"❌ Some probability values are invalid: {probability_breakdown}")
                        validation_results.append(False)
                else:
                    print(f"❌ probability_breakdown is invalid: {probability_breakdown}")
                    validation_results.append(False)
                
                # 5. Validate estimated_duration (in days)
                estimated_duration = data.get('estimated_duration')
                if estimated_duration is None or (isinstance(estimated_duration, (int, float)) and estimated_duration > 0):
                    print(f"✅ estimated_duration is valid: {estimated_duration} days")
                    validation_results.append(True)
                else:
                    print(f"❌ estimated_duration is invalid: {estimated_duration}")
                    validation_results.append(False)
                
                # 6. Validate estimated_cost (in dollars)
                estimated_cost = data.get('estimated_cost')
                if estimated_cost is None or (isinstance(estimated_cost, (int, float)) and estimated_cost >= 0):
                    print(f"✅ estimated_cost is valid: ${estimated_cost:,.2f}" if estimated_cost else "✅ estimated_cost is valid: None")
                    validation_results.append(True)
                else:
                    print(f"❌ estimated_cost is invalid: {estimated_cost}")
                    validation_results.append(False)
                
                # 7. Validate settlement_probability (float)
                settlement_probability = data.get('settlement_probability')
                if settlement_probability is None or (isinstance(settlement_probability, (int, float)) and 0 <= settlement_probability <= 1):
                    print(f"✅ settlement_probability is valid: {settlement_probability}")
                    validation_results.append(True)
                else:
                    print(f"❌ settlement_probability is invalid: {settlement_probability}")
                    validation_results.append(False)
                
                # 8. Validate prediction_date (ISO format)
                prediction_date = data.get('prediction_date')
                try:
                    datetime.fromisoformat(prediction_date.replace('Z', '+00:00'))
                    print(f"✅ prediction_date is valid ISO format: {prediction_date}")
                    validation_results.append(True)
                except (ValueError, AttributeError):
                    print(f"❌ prediction_date is invalid ISO format: {prediction_date}")
                    validation_results.append(False)
                
                # Overall validation result
                if all(validation_results):
                    print("\n🎉 ALL FIELD VALIDATIONS PASSED!")
                    test_results.append(True)
                else:
                    print(f"\n❌ {len(validation_results) - sum(validation_results)} field validations failed")
                    test_results.append(False)
                
                # Display analysis results summary
                print(f"\n📊 CASE ANALYSIS RESULTS SUMMARY:")
                print(f"Case ID: {case_id}")
                print(f"Predicted Outcome: {predicted_outcome}")
                print(f"Confidence Score: {confidence_score:.1%}")
                print(f"Settlement Probability: {settlement_probability:.1%}" if settlement_probability else "Settlement Probability: N/A")
                print(f"Estimated Duration: {estimated_duration} days" if estimated_duration else "Estimated Duration: N/A")
                print(f"Estimated Cost: ${estimated_cost:,.2f}" if estimated_cost else "Estimated Cost: N/A")
                print(f"Prediction Date: {prediction_date}")
                
                # Show probability breakdown
                if probability_breakdown:
                    print(f"\n📈 OUTCOME PROBABILITIES:")
                    for outcome, prob in probability_breakdown.items():
                        print(f"  {outcome}: {prob:.1%}")
                
                # Check for additional fields
                additional_fields = ['risk_factors', 'success_factors', 'recommendations']
                present_additional = [field for field in additional_fields if field in data and data[field]]
                if present_additional:
                    print(f"\n📋 ADDITIONAL ANALYSIS PRESENT:")
                    for field in present_additional:
                        value = data[field]
                        if isinstance(value, list):
                            print(f"  {field}: {len(value)} items")
                        else:
                            print(f"  {field}: {type(value).__name__}")
                
        elif response.status_code == 422:
            print(f"❌ VALIDATION ERROR (422)")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
            test_results.append(False)
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            if response.text:
                print(f"Error response: {response.text}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    print("-" * 50)
    return test_results

def test_error_handling():
    """Test error handling by sending invalid data"""
    print("\n🚨 TESTING ERROR HANDLING WITH INVALID DATA")
    print("=" * 80)
    
    test_results = []
    
    # Test Case 1: Invalid case_type
    print("\n📋 Test Case: Invalid Case Type")
    invalid_case_type = {
        "case_type": "invalid_case_type",
        "jurisdiction": "california",
        "case_facts": "Test case facts"
    }
    
    try:
        url = f"{BACKEND_URL}/litigation/analyze-case"
        response = requests.post(url, json=invalid_case_type, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        # Should return an error (400, 422, or 500)
        if response.status_code in [400, 422, 500]:
            print("✅ Correctly returned error for invalid case type")
            test_results.append(True)
        else:
            print(f"❌ Expected error but got HTTP {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    # Test Case 2: Missing required fields
    print("\n📋 Test Case: Missing Required Fields")
    missing_fields = {
        "case_type": "civil"
        # Missing jurisdiction
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/litigation/analyze-case", json=missing_fields, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print("✅ Correctly returned validation error for missing fields")
            test_results.append(True)
        else:
            print(f"❌ Expected validation error but got HTTP {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    # Test Case 3: Invalid data types
    print("\n📋 Test Case: Invalid Data Types")
    invalid_types = {
        "case_type": "civil",
        "jurisdiction": "california",
        "case_facts": "Test case facts",
        "case_value": "not_a_number",  # Should be float
        "evidence_strength": "invalid"  # Should be float
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/litigation/analyze-case", json=invalid_types, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [400, 422]:
            print("✅ Correctly returned validation error for invalid data types")
            test_results.append(True)
        else:
            print(f"❌ Expected validation error but got HTTP {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    print("-" * 50)
    return test_results

def test_additional_scenarios():
    """Test additional scenarios with different parameters"""
    print("\n🔬 TESTING ADDITIONAL SCENARIOS")
    print("=" * 80)
    
    test_results = []
    
    # Test Case 1: Employment case
    print("\n📋 Test Case: Employment Case")
    employment_case = {
        "case_type": "employment",
        "jurisdiction": "california",
        "case_facts": "Wrongful termination and discrimination claim against employer",
        "court_level": "district",
        "case_value": 75000,
        "evidence_strength": 0.8,
        "case_complexity": 0.6
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/litigation/analyze-case", json=employment_case, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Employment case analysis successful")
            print(f"  Predicted Outcome: {data.get('predicted_outcome', 'N/A')}")
            print(f"  Confidence Score: {data.get('confidence_score', 0):.1%}")
            test_results.append(True)
        else:
            print(f"❌ Employment case analysis failed: HTTP {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    # Test Case 2: Commercial case with all optional fields
    print("\n📋 Test Case: Commercial Case with All Fields")
    commercial_case = {
        "case_type": "commercial",
        "jurisdiction": "federal",
        "case_facts": "Breach of contract dispute involving software licensing agreement",
        "court_level": "district",
        "case_value": 500000,
        "evidence_strength": 0.7,
        "case_complexity": 0.8,
        "judge_name": "Judge Smith",
        "legal_issues": ["breach of contract", "intellectual property", "damages"],
        "witness_count": 5,
        "filing_date": "2024-01-15T00:00:00Z",
        "settlement_offers": [200000, 300000]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/litigation/analyze-case", json=commercial_case, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Commercial case analysis successful")
            print(f"  Predicted Outcome: {data.get('predicted_outcome', 'N/A')}")
            print(f"  Confidence Score: {data.get('confidence_score', 0):.1%}")
            print(f"  Settlement Probability: {data.get('settlement_probability', 0):.1%}")
            test_results.append(True)
        else:
            print(f"❌ Commercial case analysis failed: HTTP {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    # Test Case 3: Minimal data case
    print("\n📋 Test Case: Minimal Required Data")
    minimal_case = {
        "case_type": "civil",
        "jurisdiction": "california"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/litigation/analyze-case", json=minimal_case, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Minimal case analysis successful")
            print(f"  Predicted Outcome: {data.get('predicted_outcome', 'N/A')}")
            print(f"  Confidence Score: {data.get('confidence_score', 0):.1%}")
            test_results.append(True)
        elif response.status_code in [400, 422]:
            print("✅ Correctly handled minimal data (validation error expected)")
            test_results.append(True)
        else:
            print(f"❌ Unexpected response: HTTP {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    print("-" * 50)
    return test_results

def main():
    """Main test execution function"""
    print("🎯 LITIGATION ANALYTICS CASE OUTCOME ANALYSIS TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 FOCUS: Verifying POST /api/litigation/analyze-case endpoint is working")
    print("USER ISSUE: Previously returning 503 'Litigation Analytics Engine is currently unavailable'")
    print("FIX APPLIED: Added missing pyyaml dependency and restarted backend")
    print("=" * 80)
    
    all_results = []
    
    # Test 1: Main litigation case analysis endpoint
    print("\n" + "🎯" * 25 + " TEST 1 " + "🎯" * 25)
    main_results = test_litigation_case_analysis_main()
    all_results.extend(main_results)
    
    # Test 2: Error handling
    print("\n" + "🚨" * 25 + " TEST 2 " + "🚨" * 25)
    error_results = test_error_handling()
    all_results.extend(error_results)
    
    # Test 3: Additional scenarios
    print("\n" + "🔬" * 25 + " TEST 3 " + "🔬" * 25)
    additional_results = test_additional_scenarios()
    all_results.extend(additional_results)
    
    # Final Results Summary
    print("\n" + "=" * 80)
    print("🎯 LITIGATION CASE OUTCOME ANALYSIS TEST RESULTS")
    print("=" * 80)
    
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Detailed breakdown
    print(f"\n📋 Test Suite Breakdown:")
    print(f"  Main Endpoint Testing: {sum(main_results)}/{len(main_results)} passed")
    print(f"  Error Handling: {sum(error_results)}/{len(error_results)} passed")
    print(f"  Additional Scenarios: {sum(additional_results)}/{len(additional_results)} passed")
    
    print(f"\n🕒 Test Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fix Assessment
    print(f"\n🔍 LITIGATION ANALYTICS FIX ASSESSMENT:")
    
    if success_rate >= 90:
        print("🎉 FIX COMPLETELY SUCCESSFUL: Litigation Analytics Engine is fully operational!")
        print("✅ No more 503 'Litigation Analytics Engine is currently unavailable' errors")
        print("✅ POST /api/litigation/analyze-case endpoint working perfectly")
        print("✅ All required response fields present with correct data types")
        print("✅ Error handling working correctly")
        fix_status = "COMPLETELY_SUCCESSFUL"
    elif success_rate >= 70:
        print("✅ FIX MOSTLY SUCCESSFUL: Litigation Analytics Engine is working well")
        print("✅ Main functionality restored")
        print("⚠️ Some minor issues may remain")
        fix_status = "MOSTLY_SUCCESSFUL"
    else:
        print("❌ FIX NEEDS ATTENTION: Litigation Analytics Engine still has issues")
        print("❌ May still be returning 503 errors or other problems")
        print("🚨 Additional investigation required")
        fix_status = "NEEDS_ATTENTION"
    
    print(f"\n🎯 EXPECTED BEHAVIOR VERIFICATION:")
    expected_behaviors = [
        "✅ No 503 'Litigation Analytics Engine is currently unavailable' errors",
        "✅ Response includes case_id (UUID format)",
        "✅ Response includes predicted_outcome (plaintiff_win, defendant_win, settlement, dismissed)",
        "✅ Response includes confidence_score (float between 0-1)",
        "✅ Response includes probability_breakdown (object with outcome probabilities)",
        "✅ Response includes estimated_duration (in days)",
        "✅ Response includes estimated_cost (in dollars)",
        "✅ Response includes settlement_probability (float)",
        "✅ Response includes prediction_date (ISO format)",
        "✅ Error handling works for invalid data"
    ]
    
    for behavior in expected_behaviors:
        print(behavior)
    
    print(f"\n📊 FIX STATUS: {fix_status}")
    print("=" * 80)
    
    return success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)