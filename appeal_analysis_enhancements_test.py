#!/usr/bin/env python3
"""
Appeal Analysis Enhancements Testing - TASK 2 & TASK 3 VERIFICATION
==================================================================

Comprehensive testing of the newly implemented TASK 2 and TASK 3 enhancements 
to the Appeal Probability Analysis system:

TASK 2 - EVIDENCE/COMPLEXITY CORRELATION FIX:
- AI-powered parameter extraction system using Gemini/Groq
- _enhance_case_parameters_from_narrative() method
- Intelligent evidence strength (0-10) and complexity (0-100%) extraction
- Auto-correlation with case narrative analysis

TASK 3 - COST ESTIMATION & RISK THRESHOLD FIXES:
- Redesigned _estimate_appeal_costs() with tiered base costs ($20k-$150k)
- 25% case value cap to prevent unreasonable costs
- Fixed frontend risk thresholds: <25% Low, <50% Moderate, <75% High, ≥75% Very High

SPECIFIC TEST SCENARIOS:
1. Evidence/complexity correlation with detailed case facts
2. Cost estimation fixes for various case values ($100k, $250k, $1M, $10M)
3. User-reported scenario: $250k case should show ~$30k (12%) not $97.5k (39%)
4. Parameter enhancement verification with rich vs minimal case facts
5. AI fallback behavior when services fail
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://casesearch-fix.preview.emergentagent.com/api"

def test_evidence_complexity_correlation():
    """Test TASK 2: Evidence/complexity correlation with AI parameter extraction"""
    print("🧠 TESTING TASK 2: EVIDENCE/COMPLEXITY CORRELATION FIX")
    print("=" * 70)
    
    test_results = []
    
    # Test Case 1: Rich case narrative - should extract intelligent parameters
    print(f"\n📋 Test Case 1: Rich Case Narrative - AI Parameter Extraction")
    
    rich_narrative_case = {
        "case_type": "civil",
        "jurisdiction": "federal",
        "case_value": 250000,
        "judge_name": "Judge Rebecca Morgan",
        "case_facts": """This is a complex breach of contract case involving medical equipment delivery. 
        The plaintiff, a medical supply company, contracted with defendant hospital to deliver 
        specialized MRI equipment worth $250,000. The contract included specific delivery deadlines 
        and installation requirements. However, supply chain issues caused significant delays, 
        and when the equipment finally arrived, it was damaged during transport. The hospital 
        refused delivery and terminated the contract, claiming breach of delivery terms. 
        
        Evidence includes: signed purchase agreement with clear delivery terms, email 
        correspondence showing supply chain disruptions, shipping manifests documenting 
        damage, expert testimony on equipment condition, and witness statements from 
        installation technicians. The case involves complex questions about force majeure 
        clauses, risk of loss provisions, and damages calculation including lost profits 
        and replacement costs. Multiple parties are involved including the manufacturer, 
        shipping company, and insurance carriers.""",
        # Don't provide evidence_strength or case_complexity - let AI extract them
    }
    
    print(f"Case Facts Length: {len(rich_narrative_case['case_facts'])} characters")
    print(f"Case Value: ${rich_narrative_case['case_value']:,}")
    print(f"Evidence Strength: Not provided (AI should extract)")
    print(f"Case Complexity: Not provided (AI should extract)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/litigation/appeal-analysis",
            json=rich_narrative_case,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Appeal analysis with rich narrative working")
            
            # Check if AI extracted parameters are reasonable for this case
            appeal_prob = data.get('appeal_probability', 0)
            appeal_cost = data.get('appeal_cost_estimate', 0)
            
            print(f"📊 Appeal Probability: {appeal_prob:.1%}")
            print(f"📊 Appeal Cost Estimate: ${appeal_cost:,.2f}")
            
            # For this complex case with mixed evidence, expect moderate appeal probability
            if 0.25 <= appeal_prob <= 0.75:
                print("✅ AI extracted reasonable appeal probability for complex case")
                ai_extraction_success = True
            else:
                print(f"❌ Appeal probability {appeal_prob:.1%} seems unreasonable for this case complexity")
                ai_extraction_success = False
            
            # Check cost estimation (TASK 3) - $250k case should be around $30k (12%), not $97.5k (39%)
            expected_cost_range = (20000, 40000)  # $20k-$40k for $250k case
            if expected_cost_range[0] <= appeal_cost <= expected_cost_range[1]:
                print(f"✅ Cost estimate ${appeal_cost:,.2f} is reasonable ({appeal_cost/rich_narrative_case['case_value']*100:.1f}% of case value)")
                cost_estimation_success = True
            else:
                print(f"❌ Cost estimate ${appeal_cost:,.2f} is unreasonable ({appeal_cost/rich_narrative_case['case_value']*100:.1f}% of case value)")
                cost_estimation_success = False
            
            test_results.append(("Rich Narrative AI Extraction", ai_extraction_success, f"Appeal: {appeal_prob:.1%}"))
            test_results.append(("Cost Estimation Fix", cost_estimation_success, f"Cost: ${appeal_cost:,.2f} ({appeal_cost/rich_narrative_case['case_value']*100:.1f}%)"))
            
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            test_results.append(("Rich Narrative AI Extraction", False, f"HTTP {response.status_code}"))
            test_results.append(("Cost Estimation Fix", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Rich Narrative AI Extraction", False, str(e)))
        test_results.append(("Cost Estimation Fix", False, str(e)))
    
    # Test Case 2: Minimal case facts - should use provided or default values
    print(f"\n📋 Test Case 2: Minimal Case Facts - Fallback Behavior")
    
    minimal_case = {
        "case_type": "civil",
        "jurisdiction": "california",
        "case_value": 250000,
        "evidence_strength": 7,  # Explicitly provided
        "case_complexity": 0.65,  # Explicitly provided
        "case_facts": "Contract dispute"  # Minimal facts
    }
    
    print(f"Case Facts: '{minimal_case['case_facts']}'")
    print(f"Evidence Strength: {minimal_case['evidence_strength']}/10 (provided)")
    print(f"Case Complexity: {minimal_case['case_complexity']*100:.0f}% (provided)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/litigation/appeal-analysis",
            json=minimal_case,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Appeal analysis with minimal facts working")
            
            appeal_prob = data.get('appeal_probability', 0)
            appeal_cost = data.get('appeal_cost_estimate', 0)
            
            print(f"📊 Appeal Probability: {appeal_prob:.1%}")
            print(f"📊 Appeal Cost Estimate: ${appeal_cost:,.2f}")
            
            # Should use provided parameters or reasonable defaults
            if 0.1 <= appeal_prob <= 0.9:
                print("✅ Minimal facts case shows reasonable appeal probability")
                test_results.append(("Minimal Facts Fallback", True, f"Appeal: {appeal_prob:.1%}"))
            else:
                print(f"❌ Appeal probability {appeal_prob:.1%} unreasonable for minimal facts")
                test_results.append(("Minimal Facts Fallback", False, f"Appeal: {appeal_prob:.1%}"))
                
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            test_results.append(("Minimal Facts Fallback", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Minimal Facts Fallback", False, str(e)))
    
    return test_results

def test_cost_estimation_fixes():
    """Test TASK 3: Cost estimation fixes for various case values"""
    print("\n💰 TESTING TASK 3: COST ESTIMATION & RISK THRESHOLD FIXES")
    print("=" * 70)
    
    test_results = []
    
    # Test different case values to verify tiered cost structure
    test_cases = [
        {"value": 100000, "expected_range": (20000, 35000), "description": "$100k case"},
        {"value": 250000, "expected_range": (25000, 45000), "description": "$250k case (user reported)"},
        {"value": 1000000, "expected_range": (50000, 80000), "description": "$1M case"},
        {"value": 10000000, "expected_range": (120000, 200000), "description": "$10M case"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        
        case_data = {
            "case_type": "commercial",
            "jurisdiction": "federal",
            "case_value": test_case["value"],
            "evidence_strength": 6,  # Keep constant for comparison
            "case_complexity": 0.6,
            "case_facts": f"Commercial dispute involving ${test_case['value']:,}"
        }
        
        print(f"Case Value: ${case_data['case_value']:,}")
        print(f"Expected Cost Range: ${test_case['expected_range'][0]:,} - ${test_case['expected_range'][1]:,}")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/litigation/appeal-analysis",
                json=case_data,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                appeal_cost = data.get('appeal_cost_estimate', 0)
                cost_percentage = (appeal_cost / case_data['case_value']) * 100
                
                print(f"📊 Actual Appeal Cost: ${appeal_cost:,.2f}")
                print(f"📊 Percentage of Case Value: {cost_percentage:.1f}%")
                
                # Check if cost is within expected range
                if test_case['expected_range'][0] <= appeal_cost <= test_case['expected_range'][1]:
                    print(f"✅ Cost estimate within expected range")
                    cost_range_success = True
                else:
                    print(f"❌ Cost estimate outside expected range")
                    cost_range_success = False
                
                # Check 25% cap (TASK 3 requirement)
                if cost_percentage <= 25:
                    print(f"✅ Cost under 25% cap ({cost_percentage:.1f}%)")
                    cap_success = True
                else:
                    print(f"❌ Cost exceeds 25% cap ({cost_percentage:.1f}%)")
                    cap_success = False
                
                test_results.append((f"Cost Range {test_case['description']}", cost_range_success, f"${appeal_cost:,.2f}"))
                test_results.append((f"25% Cap {test_case['description']}", cap_success, f"{cost_percentage:.1f}%"))
                
                # Special check for user-reported $250k case
                if case_data['case_value'] == 250000:
                    if cost_percentage <= 15:  # Should be around 12%, definitely under 15%
                        print(f"✅ USER ISSUE RESOLVED: $250k case shows {cost_percentage:.1f}% (not 39%)")
                        test_results.append(("User $250k Issue Fix", True, f"{cost_percentage:.1f}% of case value"))
                    else:
                        print(f"❌ USER ISSUE NOT RESOLVED: $250k case still shows {cost_percentage:.1f}%")
                        test_results.append(("User $250k Issue Fix", False, f"{cost_percentage:.1f}% of case value"))
                
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                test_results.append((f"Cost Test {test_case['description']}", False, f"HTTP {response.status_code}"))
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            test_results.append((f"Cost Test {test_case['description']}", False, str(e)))
    
    return test_results

def test_user_reported_scenario():
    """Test the exact user-reported scenario that had issues"""
    print("\n🎯 TESTING USER-REPORTED SCENARIO")
    print("=" * 70)
    
    test_results = []
    
    # Exact scenario from user report
    user_case = {
        "case_type": "civil",
        "jurisdiction": "federal",  # or california
        "case_value": 250000,
        "judge_name": "Judge Rebecca Morgan",
        "case_facts": """Breach of contract case involving medical equipment delivery. 
        The contract was for specialized medical equipment worth $250,000. Supply chain 
        issues caused delivery delays, and the equipment was damaged during transport. 
        The buyer refused delivery and terminated the contract. The case involves 
        complex questions about delivery terms, force majeure clauses, and damages 
        including lost profits and replacement costs.""",
        # Let AI extract evidence_strength and case_complexity
    }
    
    print(f"\n📋 User-Reported Scenario Test")
    print(f"Case Type: {user_case['case_type']}")
    print(f"Jurisdiction: {user_case['jurisdiction']}")
    print(f"Case Value: ${user_case['case_value']:,}")
    print(f"Judge: {user_case['judge_name']}")
    print(f"Case Facts: {len(user_case['case_facts'])} characters")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/litigation/appeal-analysis",
            json=user_case,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: User scenario analysis working")
            
            appeal_prob = data.get('appeal_probability', 0)
            appeal_cost = data.get('appeal_cost_estimate', 0)
            cost_percentage = (appeal_cost / user_case['case_value']) * 100
            
            print(f"📊 Appeal Probability: {appeal_prob:.1%}")
            print(f"📊 Appeal Cost Estimate: ${appeal_cost:,.2f}")
            print(f"📊 Cost Percentage: {cost_percentage:.1f}%")
            
            # Check if AI analysis is working (not fallback)
            if 'appeal_factors' in data and len(data.get('appeal_factors', [])) > 0:
                print(f"✅ AI analysis generated {len(data['appeal_factors'])} appeal factors")
                ai_working = True
            else:
                print("❌ AI analysis not generating appeal factors")
                ai_working = False
            
            # Check evidence/complexity extraction
            if 0.2 <= appeal_prob <= 0.8:  # Reasonable range for this case
                print("✅ Evidence/complexity correlation working - reasonable appeal probability")
                correlation_working = True
            else:
                print(f"❌ Appeal probability {appeal_prob:.1%} seems unreasonable")
                correlation_working = False
            
            # Check cost estimation fix
            if cost_percentage <= 15:  # Should be around 12%
                print(f"✅ Cost estimation fixed - {cost_percentage:.1f}% is reasonable")
                cost_fixed = True
            else:
                print(f"❌ Cost estimation still high - {cost_percentage:.1f}%")
                cost_fixed = False
            
            # Check risk threshold (frontend fix verification through backend)
            risk_level = "Low" if appeal_prob < 0.25 else "Moderate" if appeal_prob < 0.50 else "High" if appeal_prob < 0.75 else "Very High"
            print(f"📊 Risk Level: {risk_level} (based on {appeal_prob:.1%})")
            
            test_results.append(("User Scenario AI Analysis", ai_working, f"{len(data.get('appeal_factors', []))} factors"))
            test_results.append(("User Scenario Correlation", correlation_working, f"Appeal: {appeal_prob:.1%}"))
            test_results.append(("User Scenario Cost Fix", cost_fixed, f"Cost: {cost_percentage:.1f}%"))
            
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            test_results.append(("User Scenario", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("User Scenario", False, str(e)))
    
    return test_results

def test_parameter_enhancement_comparison():
    """Test parameter enhancement with rich vs minimal case facts"""
    print("\n🔍 TESTING PARAMETER ENHANCEMENT VERIFICATION")
    print("=" * 70)
    
    test_results = []
    
    # Test same case with rich vs minimal facts to see AI enhancement difference
    base_case = {
        "case_type": "commercial",
        "jurisdiction": "california",
        "case_value": 500000,
    }
    
    # Rich facts version
    rich_case = {
        **base_case,
        "case_facts": """Complex commercial litigation involving breach of a software licensing 
        agreement. The plaintiff software company licensed proprietary enterprise software to 
        defendant corporation for $500,000. The agreement included specific usage restrictions, 
        update requirements, and termination clauses. However, the defendant allegedly exceeded 
        the licensed user count, failed to implement required security updates, and shared 
        proprietary code with third parties in violation of the agreement.
        
        Evidence includes: detailed licensing agreement with clear usage terms, server logs 
        showing unauthorized access patterns, email communications discussing code sharing, 
        expert testimony on software usage analytics, and witness statements from IT personnel. 
        The case involves complex technical issues about software licensing, intellectual 
        property rights, and damages calculation including lost licensing revenue and 
        development costs. Multiple technical experts and substantial discovery are required."""
    }
    
    # Minimal facts version
    minimal_case = {
        **base_case,
        "case_facts": "Software licensing dispute",
        "evidence_strength": 5,  # Explicitly provided
        "case_complexity": 0.5   # Explicitly provided
    }
    
    print(f"\n📋 Test 1: Rich Case Facts (AI Enhancement)")
    print(f"Case Facts Length: {len(rich_case['case_facts'])} characters")
    
    try:
        rich_response = requests.post(
            f"{BACKEND_URL}/litigation/appeal-analysis",
            json=rich_case,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if rich_response.status_code == 200:
            rich_data = rich_response.json()
            rich_appeal_prob = rich_data.get('appeal_probability', 0)
            rich_factors = len(rich_data.get('appeal_factors', []))
            
            print(f"📊 Rich Facts Appeal Probability: {rich_appeal_prob:.1%}")
            print(f"📊 Rich Facts Appeal Factors: {rich_factors}")
            
            print(f"\n📋 Test 2: Minimal Case Facts (Fallback)")
            print(f"Case Facts: '{minimal_case['case_facts']}'")
            print(f"Provided Evidence: {minimal_case['evidence_strength']}/10")
            print(f"Provided Complexity: {minimal_case['case_complexity']*100:.0f}%")
            
            minimal_response = requests.post(
                f"{BACKEND_URL}/litigation/appeal-analysis",
                json=minimal_case,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if minimal_response.status_code == 200:
                minimal_data = minimal_response.json()
                minimal_appeal_prob = minimal_data.get('appeal_probability', 0)
                minimal_factors = len(minimal_data.get('appeal_factors', []))
                
                print(f"📊 Minimal Facts Appeal Probability: {minimal_appeal_prob:.1%}")
                print(f"📊 Minimal Facts Appeal Factors: {minimal_factors}")
                
                # Compare results
                print(f"\n🔍 COMPARISON ANALYSIS:")
                prob_difference = abs(rich_appeal_prob - minimal_appeal_prob)
                factor_difference = abs(rich_factors - minimal_factors)
                
                print(f"Appeal Probability Difference: {prob_difference:.1%}")
                print(f"Appeal Factors Difference: {factor_difference}")
                
                # AI enhancement should show some difference in analysis
                if prob_difference > 0.05 or factor_difference > 0:  # At least 5% difference or different factor count
                    print("✅ AI enhancement shows meaningful difference between rich and minimal facts")
                    enhancement_working = True
                else:
                    print("❌ AI enhancement not showing significant difference")
                    enhancement_working = False
                
                # Rich facts should generally produce more detailed analysis
                if rich_factors >= minimal_factors:
                    print("✅ Rich facts produce equal or more detailed factor analysis")
                    detail_enhancement = True
                else:
                    print("❌ Rich facts produce less detailed analysis than minimal facts")
                    detail_enhancement = False
                
                test_results.append(("AI Enhancement Difference", enhancement_working, f"Prob diff: {prob_difference:.1%}"))
                test_results.append(("Rich Facts Detail", detail_enhancement, f"Rich: {rich_factors}, Minimal: {minimal_factors}"))
                
            else:
                print(f"❌ Minimal case failed: {minimal_response.status_code}")
                test_results.append(("Parameter Enhancement Comparison", False, "Minimal case failed"))
                
        else:
            print(f"❌ Rich case failed: {rich_response.status_code}")
            test_results.append(("Parameter Enhancement Comparison", False, "Rich case failed"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("Parameter Enhancement Comparison", False, str(e)))
    
    return test_results

def test_ai_fallback_behavior():
    """Test fallback behavior when AI services fail"""
    print("\n🛡️ TESTING AI FALLBACK BEHAVIOR")
    print("=" * 70)
    
    test_results = []
    
    # Test with case that should work even if AI enhancement fails
    fallback_case = {
        "case_type": "employment",
        "jurisdiction": "texas",
        "case_value": 150000,
        "evidence_strength": 8,  # Explicitly provided
        "case_complexity": 0.3,  # Explicitly provided
        "case_facts": "Employment termination case with strong documentation and clear liability"
    }
    
    print(f"\n📋 Testing Fallback Behavior")
    print(f"Case Type: {fallback_case['case_type']}")
    print(f"Case Value: ${fallback_case['case_value']:,}")
    print(f"Evidence Strength: {fallback_case['evidence_strength']}/10 (provided)")
    print(f"Case Complexity: {fallback_case['case_complexity']*100:.0f}% (provided)")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/litigation/appeal-analysis",
            json=fallback_case,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            appeal_prob = data.get('appeal_probability', 0)
            appeal_cost = data.get('appeal_cost_estimate', 0)
            
            print(f"📊 Appeal Probability: {appeal_prob:.1%}")
            print(f"📊 Appeal Cost Estimate: ${appeal_cost:,.2f}")
            
            # Should work even if AI enhancement fails
            if 0.05 <= appeal_prob <= 0.95:
                print("✅ Fallback behavior working - reasonable appeal probability")
                fallback_success = True
            else:
                print(f"❌ Fallback behavior failed - unreasonable appeal probability")
                fallback_success = False
            
            # Cost should still be reasonable
            cost_percentage = (appeal_cost / fallback_case['case_value']) * 100
            if cost_percentage <= 25:
                print(f"✅ Cost estimation working in fallback mode ({cost_percentage:.1f}%)")
                cost_fallback_success = True
            else:
                print(f"❌ Cost estimation failed in fallback mode ({cost_percentage:.1f}%)")
                cost_fallback_success = False
            
            test_results.append(("AI Fallback Probability", fallback_success, f"Appeal: {appeal_prob:.1%}"))
            test_results.append(("AI Fallback Cost", cost_fallback_success, f"Cost: {cost_percentage:.1f}%"))
            
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            test_results.append(("AI Fallback Behavior", False, f"HTTP {response.status_code}"))
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        test_results.append(("AI Fallback Behavior", False, str(e)))
    
    return test_results

def print_comprehensive_summary(all_results: List[tuple]):
    """Print comprehensive test summary for TASK 2 & TASK 3"""
    print("\n" + "=" * 80)
    print("🎯 APPEAL ANALYSIS ENHANCEMENTS TESTING SUMMARY")
    print("=" * 80)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, passed, _ in all_results if passed)
    failed_tests = total_tests - passed_tests
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Categorize results by enhancement
    task2_results = [r for r in all_results if any(keyword in r[0] for keyword in ['AI', 'Extraction', 'Correlation', 'Enhancement', 'Rich', 'Minimal'])]
    task3_results = [r for r in all_results if any(keyword in r[0] for keyword in ['Cost', 'Cap', '$250k', 'User'])]
    
    print(f"\n📋 ENHANCEMENT BREAKDOWN:")
    if task2_results:
        task2_passed = sum(1 for _, passed, _ in task2_results if passed)
        print(f"TASK 2 (Evidence/Complexity Correlation): {task2_passed}/{len(task2_results)} passed")
    
    if task3_results:
        task3_passed = sum(1 for _, passed, _ in task3_results if passed)
        print(f"TASK 3 (Cost Estimation Fixes): {task3_passed}/{len(task3_results)} passed")
    
    print(f"\n🔍 DETAILED RESULTS:")
    for test_name, passed, details in all_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name} - {details}")
    
    print(f"\n🎯 KEY FINDINGS:")
    
    # Check specific user issues
    user_issue_tests = [r for r in all_results if 'User' in r[0] or '$250k' in r[0]]
    if user_issue_tests:
        user_passed = sum(1 for _, passed, _ in user_issue_tests if passed)
        if user_passed == len(user_issue_tests):
            print("✅ USER-REPORTED ISSUES COMPLETELY RESOLVED")
        elif user_passed > 0:
            print("⚠️ USER-REPORTED ISSUES PARTIALLY RESOLVED")
        else:
            print("❌ USER-REPORTED ISSUES NOT RESOLVED")
    
    # Check AI enhancement
    ai_tests = [r for r in all_results if 'AI' in r[0] or 'Enhancement' in r[0]]
    if ai_tests:
        ai_passed = sum(1 for _, passed, _ in ai_tests if passed)
        if ai_passed >= len(ai_tests) * 0.8:
            print("✅ AI-POWERED PARAMETER EXTRACTION WORKING WELL")
        else:
            print("⚠️ AI-POWERED PARAMETER EXTRACTION NEEDS ATTENTION")
    
    # Check cost estimation
    cost_tests = [r for r in all_results if 'Cost' in r[0]]
    if cost_tests:
        cost_passed = sum(1 for _, passed, _ in cost_tests if passed)
        if cost_passed >= len(cost_tests) * 0.8:
            print("✅ COST ESTIMATION FIXES WORKING WELL")
        else:
            print("⚠️ COST ESTIMATION FIXES NEED ATTENTION")
    
    print(f"\n📊 ENHANCEMENT STATUS:")
    if success_rate >= 85:
        print("🎉 OUTSTANDING: Both TASK 2 and TASK 3 enhancements working excellently!")
        status = "OUTSTANDING"
    elif success_rate >= 70:
        print("✅ GOOD: Most enhancements working well with minor issues")
        status = "GOOD"
    elif success_rate >= 50:
        print("⚠️ PARTIAL: Some enhancements working but significant issues remain")
        status = "PARTIAL"
    else:
        print("❌ NEEDS WORK: Major issues with enhancements")
        status = "NEEDS_WORK"
    
    return status

def main():
    """Run comprehensive TASK 2 & TASK 3 enhancement testing"""
    print("🚀 STARTING APPEAL ANALYSIS ENHANCEMENTS TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 TESTING FOCUS:")
    print("TASK 2: Evidence/Complexity Correlation Fix - AI parameter extraction")
    print("TASK 3: Cost Estimation & Risk Threshold Fixes - Tiered costs with 25% cap")
    print("=" * 80)
    
    all_results = []
    
    try:
        # Test 1: Evidence/Complexity Correlation (TASK 2)
        print("\n" + "🧠" * 25 + " TASK 2 TESTING " + "🧠" * 25)
        task2_results = test_evidence_complexity_correlation()
        all_results.extend(task2_results)
        
        # Test 2: Cost Estimation Fixes (TASK 3)
        print("\n" + "💰" * 25 + " TASK 3 TESTING " + "💰" * 25)
        task3_results = test_cost_estimation_fixes()
        all_results.extend(task3_results)
        
        # Test 3: User-Reported Scenario
        print("\n" + "🎯" * 25 + " USER SCENARIO " + "🎯" * 25)
        user_results = test_user_reported_scenario()
        all_results.extend(user_results)
        
        # Test 4: Parameter Enhancement Comparison
        print("\n" + "🔍" * 25 + " ENHANCEMENT COMPARISON " + "🔍" * 25)
        comparison_results = test_parameter_enhancement_comparison()
        all_results.extend(comparison_results)
        
        # Test 5: AI Fallback Behavior
        print("\n" + "🛡️" * 25 + " FALLBACK TESTING " + "🛡️" * 25)
        fallback_results = test_ai_fallback_behavior()
        all_results.extend(fallback_results)
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        all_results.append(("Testing Framework", False, str(e)))
    
    # Print comprehensive summary
    status = print_comprehensive_summary(all_results)
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return success for external monitoring
    return status in ["OUTSTANDING", "GOOD"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)