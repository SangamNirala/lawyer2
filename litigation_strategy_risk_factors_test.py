#!/usr/bin/env python3
"""
Litigation Strategy Risk Factors Testing
========================================

Focused testing of the litigation strategy recommendations endpoint specifically 
for the risk factors issue reported by the user.

USER REPORTED ISSUE:
- Risk Factors shows "Risk analysis in progress..." which means the risk_factors array is empty
- Other sections (Strategic Advantages, Action Plan) work fine
- Need to debug why _identify_risk_factors method isn't generating factors

TEST FOCUS:
1. Test with exact user parameters
2. Debug empty risk_factors array
3. Test with different evidence_strength and case_complexity values
4. Check for errors in strategy optimization process
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://lawcite-network.preview.emergentagent.com/api"

def test_litigation_strategy_risk_factors():
    """Test litigation strategy endpoint with exact user parameters focusing on risk factors"""
    print("🎯 TESTING LITIGATION STRATEGY RISK FACTORS - USER REPORTED ISSUE")
    print("=" * 80)
    
    test_results = []
    
    # Exact parameters from user's case
    user_case_data = {
        "case_type": "civil",
        "jurisdiction": "california",
        "court_level": "district",
        "judge_name": "Judge Sarah Martinez",
        "case_value": 750000,
        "client_budget": 150000,
        "witness_count": 4,
        "opposing_counsel": "Smith & Associates",
        "evidence_strength": 7.0,
        "case_complexity": 0.65,
        "case_facts": "The plaintiff, a technology startup, alleges that the defendant, a hardware supplier, failed to deliver specialized components critical for a product launch despite an executed supply contract. The components were delayed by three months, causing the plaintiff to miss a major trade show and lose potential contracts worth over $750,000. The defendant claims the delay was due to unforeseeable shipping disruptions and force majeure provisions in the contract. Key issues include contract interpretation, applicability of force majeure clauses, and damages calculation.",
        "timeline_constraints": "Plaintiff seeks expedited proceedings to minimize ongoing business losses and maintain investor confidence, requesting trial within 12 months."
    }
    
    print(f"\n📋 Test Case: User's Exact Parameters")
    print(f"Case Type: {user_case_data['case_type']}")
    print(f"Jurisdiction: {user_case_data['jurisdiction']}")
    print(f"Court Level: {user_case_data['court_level']}")
    print(f"Judge: {user_case_data['judge_name']}")
    print(f"Case Value: ${user_case_data['case_value']:,}")
    print(f"Client Budget: ${user_case_data['client_budget']:,}")
    print(f"Evidence Strength: {user_case_data['evidence_strength']}/10")
    print(f"Case Complexity: {user_case_data['case_complexity']}")
    print(f"Witness Count: {user_case_data['witness_count']}")
    print(f"Opposing Counsel: {user_case_data['opposing_counsel']}")
    print(f"Timeline Constraints: {user_case_data['timeline_constraints']}")
    
    try:
        url = f"{BACKEND_URL}/litigation/strategy-recommendations"
        print(f"\nRequest URL: {url}")
        
        response = requests.post(url, json=user_case_data, timeout=120)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Focus on risk_factors analysis
            print("\n🔍 RISK FACTORS ANALYSIS:")
            print("=" * 50)
            
            risk_factors = data.get('risk_factors', [])
            print(f"Risk Factors Count: {len(risk_factors)}")
            
            if len(risk_factors) == 0:
                print("❌ CRITICAL ISSUE: risk_factors array is EMPTY")
                print("🚨 This confirms the user's reported issue!")
                print("🔧 The _identify_risk_factors method is not generating any factors")
                test_results.append(False)
                
                # Debug information
                print("\n🔍 DEBUG INFORMATION:")
                print(f"Evidence Strength: {user_case_data['evidence_strength']} (normalized: {user_case_data['evidence_strength']/10.0})")
                print(f"Case Complexity: {user_case_data['case_complexity']}")
                print(f"Case Value: ${user_case_data['case_value']:,}")
                print(f"Timeline Constraints Present: {'timeline_constraints' in user_case_data}")
                
                # Check what should trigger risk factors based on the logic
                evidence_normalized = user_case_data['evidence_strength'] / 10.0
                complexity = user_case_data['case_complexity']
                case_value = user_case_data['case_value']
                
                print(f"\n🧮 EXPECTED RISK FACTOR TRIGGERS:")
                if evidence_normalized < 0.4:
                    print("✅ Should trigger: Weak evidence risk")
                elif evidence_normalized < 0.6:
                    print("✅ Should trigger: Moderate evidence risk")
                else:
                    print("❌ Evidence strength too high to trigger risk (7.0/10 = 0.7)")
                
                if complexity > 0.8:
                    print("✅ Should trigger: High complexity risk")
                elif complexity > 0.6:
                    print("✅ Should trigger: Complex case factors risk")
                else:
                    print("❌ Complexity not high enough to trigger risk (0.65)")
                
                if case_value > 5000000:
                    print("✅ Should trigger: Very high value risk")
                elif case_value > 1000000:
                    print("❌ Case value not high enough for major risk ($750,000)")
                else:
                    print("❌ Case value too low to trigger risk")
                
                if user_case_data.get('timeline_constraints'):
                    print("✅ Should trigger: Timeline constraints risk")
                else:
                    print("❌ No timeline constraints to trigger risk")
                
            else:
                print("✅ Risk factors are present!")
                print(f"Risk Factors ({len(risk_factors)}):")
                for i, factor in enumerate(risk_factors, 1):
                    print(f"  {i}. {factor}")
                test_results.append(True)
            
            # Check other sections to confirm they work
            print(f"\n📊 OTHER SECTIONS STATUS:")
            strategic_recommendations = data.get('strategic_recommendations', [])
            ai_strategic_summary = data.get('ai_strategic_summary', '')
            
            print(f"Strategic Recommendations: {len(strategic_recommendations)} items")
            print(f"AI Strategic Summary: {len(ai_strategic_summary)} characters")
            
            if len(strategic_recommendations) > 0:
                print("✅ Strategic Advantages/Action Plan working (as user reported)")
                test_results.append(True)
            else:
                print("❌ Strategic recommendations also empty")
                test_results.append(False)
            
            if len(ai_strategic_summary) > 50:
                print("✅ AI Strategic Summary working")
                test_results.append(True)
            else:
                print("❌ AI Strategic Summary minimal or empty")
                test_results.append(False)
                
        elif response.status_code == 404:
            print("❌ Endpoint not found - litigation strategy endpoint may not be implemented")
            test_results.append(False)
            
        elif response.status_code == 500:
            print("❌ Internal server error")
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

def test_different_evidence_strength_values():
    """Test with different evidence_strength values to see if any generate risk factors"""
    print("\n🧪 TESTING DIFFERENT EVIDENCE STRENGTH VALUES")
    print("=" * 80)
    
    test_results = []
    
    # Base case data
    base_case = {
        "case_type": "civil",
        "jurisdiction": "california",
        "court_level": "district",
        "judge_name": "Judge Sarah Martinez",
        "case_value": 750000,
        "client_budget": 150000,
        "witness_count": 4,
        "opposing_counsel": "Smith & Associates",
        "case_complexity": 0.65,
        "case_facts": "Contract dispute with evidence issues",
        "timeline_constraints": "Expedited proceedings requested"
    }
    
    # Test different evidence strength values
    evidence_values = [2.0, 4.0, 6.0, 8.0, 10.0]
    
    for evidence_strength in evidence_values:
        print(f"\n📋 Testing Evidence Strength: {evidence_strength}/10 (normalized: {evidence_strength/10.0})")
        
        test_case = base_case.copy()
        test_case['evidence_strength'] = evidence_strength
        
        try:
            url = f"{BACKEND_URL}/litigation/strategy-recommendations"
            response = requests.post(url, json=test_case, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                risk_factors = data.get('risk_factors', [])
                
                print(f"  Risk Factors Count: {len(risk_factors)}")
                
                if len(risk_factors) > 0:
                    print("  ✅ Risk factors generated!")
                    for i, factor in enumerate(risk_factors[:2], 1):  # Show first 2
                        print(f"    {i}. {factor[:80]}...")
                    test_results.append(True)
                else:
                    print("  ❌ No risk factors generated")
                    test_results.append(False)
                    
            else:
                print(f"  ❌ Request failed with status {response.status_code}")
                test_results.append(False)
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            test_results.append(False)
    
    return test_results

def test_different_case_complexity_values():
    """Test with different case_complexity values to see if any generate risk factors"""
    print("\n🧪 TESTING DIFFERENT CASE COMPLEXITY VALUES")
    print("=" * 80)
    
    test_results = []
    
    # Base case data
    base_case = {
        "case_type": "civil",
        "jurisdiction": "california",
        "court_level": "district",
        "judge_name": "Judge Sarah Martinez",
        "case_value": 750000,
        "client_budget": 150000,
        "witness_count": 4,
        "opposing_counsel": "Smith & Associates",
        "evidence_strength": 7.0,
        "case_facts": "Contract dispute with complexity issues",
        "timeline_constraints": "Expedited proceedings requested"
    }
    
    # Test different complexity values
    complexity_values = [0.3, 0.5, 0.7, 0.85, 0.95]
    
    for complexity in complexity_values:
        print(f"\n📋 Testing Case Complexity: {complexity}")
        
        test_case = base_case.copy()
        test_case['case_complexity'] = complexity
        
        try:
            url = f"{BACKEND_URL}/litigation/strategy-recommendations"
            response = requests.post(url, json=test_case, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                risk_factors = data.get('risk_factors', [])
                
                print(f"  Risk Factors Count: {len(risk_factors)}")
                
                if len(risk_factors) > 0:
                    print("  ✅ Risk factors generated!")
                    for i, factor in enumerate(risk_factors[:2], 1):  # Show first 2
                        print(f"    {i}. {factor[:80]}...")
                    test_results.append(True)
                else:
                    print("  ❌ No risk factors generated")
                    test_results.append(False)
                    
            else:
                print(f"  ❌ Request failed with status {response.status_code}")
                test_results.append(False)
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            test_results.append(False)
    
    return test_results

def test_high_value_case_for_risk_factors():
    """Test with high case value to trigger value-based risk factors"""
    print("\n💰 TESTING HIGH VALUE CASE FOR RISK FACTORS")
    print("=" * 80)
    
    test_results = []
    
    # High value case that should trigger risk factors
    high_value_case = {
        "case_type": "civil",
        "jurisdiction": "california",
        "court_level": "district",
        "judge_name": "Judge Sarah Martinez",
        "case_value": 6000000,  # High value to trigger risk
        "client_budget": 500000,
        "witness_count": 4,
        "opposing_counsel": "Smith & Associates",
        "evidence_strength": 3.0,  # Low evidence to trigger risk
        "case_complexity": 0.85,  # High complexity to trigger risk
        "case_facts": "High-stakes contract dispute with weak evidence and high complexity",
        "timeline_constraints": "Expedited proceedings requested"
    }
    
    print(f"\n📋 High Value Test Case:")
    print(f"Case Value: ${high_value_case['case_value']:,} (should trigger value risk)")
    print(f"Evidence Strength: {high_value_case['evidence_strength']}/10 (should trigger evidence risk)")
    print(f"Case Complexity: {high_value_case['case_complexity']} (should trigger complexity risk)")
    print(f"Timeline Constraints: Present (should trigger timeline risk)")
    
    try:
        url = f"{BACKEND_URL}/litigation/strategy-recommendations"
        response = requests.post(url, json=high_value_case, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            risk_factors = data.get('risk_factors', [])
            
            print(f"\n🔍 RISK FACTORS ANALYSIS:")
            print(f"Risk Factors Count: {len(risk_factors)}")
            
            if len(risk_factors) > 0:
                print("✅ Risk factors generated with high-risk parameters!")
                print("Risk Factors:")
                for i, factor in enumerate(risk_factors, 1):
                    print(f"  {i}. {factor}")
                test_results.append(True)
                
                # Check if expected risk types are present
                risk_text = ' '.join(risk_factors).lower()
                expected_risks = [
                    ('evidence', 'weak evidence'),
                    ('complexity', 'complex'),
                    ('value', 'high.*value'),
                    ('timeline', 'timeline')
                ]
                
                print(f"\n🔍 EXPECTED RISK TYPES CHECK:")
                for risk_type, pattern in expected_risks:
                    if pattern in risk_text:
                        print(f"  ✅ {risk_type.title()} risk detected")
                    else:
                        print(f"  ❌ {risk_type.title()} risk NOT detected")
                        
            else:
                print("❌ CRITICAL: Even with high-risk parameters, no risk factors generated!")
                print("🚨 This indicates a fundamental issue with the _identify_risk_factors method")
                test_results.append(False)
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        test_results.append(False)
    
    return test_results

def main():
    """Main test execution function"""
    print("🎯 LITIGATION STRATEGY RISK FACTORS TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 FOCUS: Debugging empty risk_factors array in litigation strategy endpoint")
    print("USER ISSUE: Risk Factors shows 'Risk analysis in progress...' (empty array)")
    print("=" * 80)
    
    all_results = []
    
    # Test 1: User's exact parameters
    print("\n" + "🎯" * 25 + " TEST 1 " + "🎯" * 25)
    user_results = test_litigation_strategy_risk_factors()
    all_results.extend(user_results)
    
    # Test 2: Different evidence strength values
    print("\n" + "🧪" * 25 + " TEST 2 " + "🧪" * 25)
    evidence_results = test_different_evidence_strength_values()
    all_results.extend(evidence_results)
    
    # Test 3: Different case complexity values
    print("\n" + "🧪" * 25 + " TEST 3 " + "🧪" * 25)
    complexity_results = test_different_case_complexity_values()
    all_results.extend(complexity_results)
    
    # Test 4: High value case with multiple risk triggers
    print("\n" + "💰" * 25 + " TEST 4 " + "💰" * 25)
    high_value_results = test_high_value_case_for_risk_factors()
    all_results.extend(high_value_results)
    
    # Final Results Summary
    print("\n" + "=" * 80)
    print("🎯 RISK FACTORS TEST RESULTS SUMMARY")
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
    print(f"  User's Exact Parameters: {sum(user_results)}/{len(user_results)} passed")
    print(f"  Evidence Strength Variations: {sum(evidence_results)}/{len(evidence_results)} passed")
    print(f"  Case Complexity Variations: {sum(complexity_results)}/{len(complexity_results)} passed")
    print(f"  High Value Risk Triggers: {sum(high_value_results)}/{len(high_value_results)} passed")
    
    print(f"\n🕒 Test Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Risk Factors Issue Assessment
    print(f"\n🔍 RISK FACTORS ISSUE ASSESSMENT:")
    
    if success_rate >= 80:
        print("✅ RISK FACTORS WORKING: Litigation strategy generating risk factors correctly!")
        print("✅ User's issue may be resolved or was a temporary problem")
        issue_status = "RESOLVED"
    elif success_rate >= 50:
        print("⚠️ RISK FACTORS PARTIALLY WORKING: Some scenarios generate risk factors")
        print("🔧 May need parameter adjustments or logic refinement")
        issue_status = "PARTIALLY_RESOLVED"
    else:
        print("❌ RISK FACTORS NOT WORKING: Confirming user's reported issue")
        print("🚨 _identify_risk_factors method has fundamental problems")
        print("🔧 Requires immediate debugging and fixes")
        issue_status = "CONFIRMED_ISSUE"
    
    print(f"\n🎯 DEBUGGING RECOMMENDATIONS:")
    debug_recommendations = [
        "🔍 Check if _identify_risk_factors method is being called properly",
        "🔍 Verify evidence_strength normalization (divide by 10.0)",
        "🔍 Confirm case_complexity and case_value parameter handling",
        "🔍 Check if analyses parameter contains expected settlement_analysis data",
        "🔍 Verify timeline_constraints parameter is being processed",
        "🔍 Test with extreme values to isolate threshold issues"
    ]
    
    for recommendation in debug_recommendations:
        print(recommendation)
    
    print(f"\n📊 ISSUE STATUS: {issue_status}")
    print("=" * 80)
    
    return success_rate >= 50

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)