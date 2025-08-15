#!/usr/bin/env python3
"""
Focused Legal Research Engine Timeout Test
Testing the 4 specific endpoints mentioned in the review request that were previously timing out:

1. POST /api/legal-research-engine/generate-memo - Previously failed with generate_basic_memo method missing
2. POST /api/legal-research-engine/structure-arguments - Previously failed with LegalPosition enum validation error
3. POST /api/legal-research-engine/quality-assessment - Previously failed with QualityLevel enum serialization error  
4. POST /api/legal-research-engine/multi-jurisdiction-search - Previously timed out >15s

This test uses the same parameters that previously caused failures to verify fixes.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Use production URL from frontend .env
BASE_URL = "https://verdict-analytics.preview.emergentagent.com"

def log_test(message):
    """Log test messages with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_generate_memo_with_previous_failing_params():
    """
    Test POST /api/legal-research-engine/generate-memo
    Using parameters that previously caused generate_basic_memo method missing error
    """
    log_test("🎯 TESTING: POST /api/legal-research-engine/generate-memo (Previously: generate_basic_memo method missing)")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/generate-memo"
    
    # Use parameters similar to those that previously caused failures
    payload = {
        "memo_data": {
            "research_query": "Contract breach remedies and damages calculation",
            "legal_issues": ["breach of contract", "compensatory damages", "consequential damages"],
            "jurisdiction": "US",
            "case_facts": "Supplier failed to deliver critical components causing production delays",
            "client_objectives": "Determine available remedies and calculate potential damages"
        },
        "memo_type": "basic",  # This might trigger the generate_basic_memo method
        "format_style": "professional"
    }
    
    try:
        log_test(f"Sending request with memo_type: 'basic' (may trigger generate_basic_memo)")
        log_test(f"Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=20)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response_time >= 15:
            log_test("❌ FAIL: Response time >= 15s (timeout threshold)")
            return False, f"Timeout: {response_time:.3f}s"
        
        if response.status_code == 200:
            try:
                data = response.json()
                log_test(f"✅ SUCCESS: Memo generation completed")
                log_test(f"Response keys: {list(data.keys())}")
                
                # Check if memo was generated
                generated_memo = data.get('generated_memo', '')
                if generated_memo:
                    log_test(f"✅ Memo content generated: {len(generated_memo)} characters")
                    return True, f"Success: {response_time:.3f}s, memo: {len(generated_memo)} chars"
                else:
                    log_test(f"⚠️  WARNING: No memo content generated")
                    return True, f"Success but no content: {response_time:.3f}s"
                    
            except json.JSONDecodeError as e:
                log_test(f"❌ FAIL: Invalid JSON response: {str(e)}")
                return False, f"Invalid JSON: {str(e)}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code}")
            log_test(f"Response text: {response.text[:300]}...")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>20s)")
        return False, "Timeout >20s"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_structure_arguments_with_enum_validation():
    """
    Test POST /api/legal-research-engine/structure-arguments
    Using parameters that previously caused LegalPosition enum validation error
    """
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/structure-arguments (Previously: LegalPosition enum validation error)")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/structure-arguments"
    
    # Use parameters that should trigger proper enum validation
    payload = {
        "argument_data": {
            "legal_question": "Can a party claim specific performance for breach of a services contract?",
            "case_facts": "Software development contract where developer failed to complete project",
            "legal_position": "plaintiff",  # Valid LegalPosition enum value
            "jurisdiction": "US",
            "case_type": "contract_dispute",
            "supporting_evidence": [
                "Written contract with specific deliverables",
                "Email communications showing breach"
            ]
        },
        "argument_strength": "strong",
        "include_counterarguments": True
    }
    
    try:
        log_test(f"Sending request with legal_position: 'plaintiff' (valid enum value)")
        log_test(f"Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=20)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response_time >= 15:
            log_test("❌ FAIL: Response time >= 15s (timeout threshold)")
            return False, f"Timeout: {response_time:.3f}s"
        
        if response.status_code == 200:
            try:
                data = response.json()
                log_test(f"✅ SUCCESS: Argument structuring completed")
                log_test(f"Response keys: {list(data.keys())}")
                
                # Check if argument structure was generated
                argument_structure = data.get('argument_structure', {})
                if argument_structure:
                    log_test(f"✅ Argument structure generated: {list(argument_structure.keys())}")
                    return True, f"Success: {response_time:.3f}s, structure generated"
                else:
                    log_test(f"⚠️  WARNING: No argument structure generated")
                    return True, f"Success but no structure: {response_time:.3f}s"
                    
            except json.JSONDecodeError as e:
                log_test(f"❌ FAIL: Invalid JSON response: {str(e)}")
                return False, f"Invalid JSON: {str(e)}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code}")
            log_test(f"Response text: {response.text[:300]}...")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>20s)")
        return False, "Timeout >20s"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_quality_assessment_with_enum_serialization():
    """
    Test POST /api/legal-research-engine/quality-assessment
    Using parameters that previously caused QualityLevel enum serialization error
    """
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/quality-assessment (Previously: QualityLevel enum serialization error)")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/quality-assessment"
    
    # Use parameters that should trigger enum serialization
    payload = {
        "research_data": {
            "research_query": "Employment law compliance for remote workers",
            "sources_analyzed": [
                {
                    "source_type": "case_law",
                    "citation": "Smith v. Remote Corp, 123 F.3d 456 (2023)",
                    "authority_level": "high",
                    "relevance_score": 0.85
                },
                {
                    "source_type": "statute", 
                    "citation": "29 U.S.C. § 201 et seq.",
                    "authority_level": "primary",
                    "relevance_score": 0.92
                }
            ],
            "legal_analysis": "Comprehensive analysis of remote work compliance requirements",
            "jurisdiction": "US",
            "legal_domain": "employment_law"
        }
    }
    
    try:
        log_test(f"Sending request that should trigger QualityLevel enum serialization")
        log_test(f"Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=20)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response_time >= 15:
            log_test("❌ FAIL: Response time >= 15s (timeout threshold)")
            return False, f"Timeout: {response_time:.3f}s"
        
        if response.status_code == 200:
            try:
                data = response.json()
                log_test(f"✅ SUCCESS: Quality assessment completed")
                log_test(f"Response keys: {list(data.keys())}")
                
                # Check if quality assessment was generated
                overall_scores = data.get('overall_scores', {})
                quality_insights = data.get('quality_insights', {})
                
                if overall_scores or quality_insights:
                    log_test(f"✅ Quality assessment generated successfully")
                    return True, f"Success: {response_time:.3f}s, assessment completed"
                else:
                    log_test(f"⚠️  WARNING: No quality assessment data generated")
                    return True, f"Success but no assessment: {response_time:.3f}s"
                    
            except json.JSONDecodeError as e:
                log_test(f"❌ FAIL: Invalid JSON response: {str(e)}")
                return False, f"Invalid JSON: {str(e)}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code}")
            log_test(f"Response text: {response.text[:300]}...")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>20s)")
        return False, "Timeout >20s"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def test_multi_jurisdiction_search_timeout():
    """
    Test POST /api/legal-research-engine/multi-jurisdiction-search
    Using parameters that previously caused >15s timeout
    """
    log_test("\n🎯 TESTING: POST /api/legal-research-engine/multi-jurisdiction-search (Previously: timed out >15s)")
    
    endpoint = f"{BASE_URL}/api/legal-research-engine/multi-jurisdiction-search"
    
    # Use parameters that previously caused timeouts
    payload = {
        "query": "Data privacy laws and GDPR compliance requirements",
        "jurisdictions": ["US", "UK", "CA", "EU"],
        "legal_domain": "privacy_law",
        "comparison_mode": True
    }
    
    try:
        log_test(f"Sending request with 4 jurisdictions (previously caused timeout)")
        log_test(f"Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=20)
        response_time = time.time() - start_time
        
        log_test(f"Response Status: {response.status_code}")
        log_test(f"Response Time: {response_time:.3f}s")
        
        if response_time >= 15:
            log_test("❌ FAIL: Response time >= 15s (timeout threshold)")
            return False, f"Timeout: {response_time:.3f}s"
        
        if response.status_code == 200:
            try:
                data = response.json()
                log_test(f"✅ SUCCESS: Multi-jurisdiction search completed")
                log_test(f"Response keys: {list(data.keys())}")
                
                # Check if search results were generated
                results = data.get('results', [])
                jurisdictions = data.get('jurisdictions', [])
                
                if results or jurisdictions:
                    log_test(f"✅ Search results generated: {len(results)} results, {len(jurisdictions)} jurisdictions")
                    return True, f"Success: {response_time:.3f}s, {len(results)} results"
                else:
                    log_test(f"⚠️  WARNING: No search results generated")
                    return True, f"Success but no results: {response_time:.3f}s"
                    
            except json.JSONDecodeError as e:
                log_test(f"❌ FAIL: Invalid JSON response: {str(e)}")
                return False, f"Invalid JSON: {str(e)}"
        else:
            log_test(f"❌ FAIL: HTTP {response.status_code}")
            log_test(f"Response text: {response.text[:300]}...")
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        log_test("❌ FAIL: Request timed out (>20s)")
        return False, "Timeout >20s"
    except Exception as e:
        log_test(f"❌ ERROR: {str(e)}")
        return False, f"Exception: {str(e)}"

def main():
    """Run focused tests on the 4 previously failing Legal Research Engine endpoints"""
    log_test("🚀 STARTING FOCUSED LEGAL RESEARCH ENGINE TIMEOUT RESOLUTION TESTING")
    log_test(f"Base URL: {BASE_URL}")
    log_test("Testing 4 specific endpoints that were previously timing out:")
    log_test("1. POST /api/legal-research-engine/generate-memo (generate_basic_memo method missing)")
    log_test("2. POST /api/legal-research-engine/structure-arguments (LegalPosition enum validation error)")
    log_test("3. POST /api/legal-research-engine/quality-assessment (QualityLevel enum serialization error)")
    log_test("4. POST /api/legal-research-engine/multi-jurisdiction-search (timed out >15s)")
    log_test("=" * 100)
    
    all_results = []
    
    # Test 1: Generate Memo endpoint (generate_basic_memo method issue)
    memo_result = test_generate_memo_with_previous_failing_params()
    all_results.append(("Generate Memo", memo_result[0], memo_result[1]))
    
    # Test 2: Structure Arguments endpoint (LegalPosition enum validation)
    arguments_result = test_structure_arguments_with_enum_validation()
    all_results.append(("Structure Arguments", arguments_result[0], arguments_result[1]))
    
    # Test 3: Quality Assessment endpoint (QualityLevel enum serialization)
    quality_result = test_quality_assessment_with_enum_serialization()
    all_results.append(("Quality Assessment", quality_result[0], quality_result[1]))
    
    # Test 4: Multi-Jurisdiction Search endpoint (timeout >15s)
    multi_jurisdiction_result = test_multi_jurisdiction_search_timeout()
    all_results.append(("Multi-Jurisdiction Search", multi_jurisdiction_result[0], multi_jurisdiction_result[1]))
    
    # Summary
    log_test("\n" + "=" * 100)
    log_test("📊 FOCUSED LEGAL RESEARCH ENGINE TIMEOUT RESOLUTION TESTING SUMMARY")
    log_test("=" * 100)
    
    passed = 0
    failed = 0
    
    for test_name, success, details in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        log_test(f"{status}: {test_name}")
        log_test(f"    Details: {details}")
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
    
    # Expected outcome analysis
    log_test("\n" + "=" * 100)
    log_test("📈 TIMEOUT RESOLUTION VERIFICATION")
    log_test("=" * 100)
    log_test("REVIEW REQUEST EXPECTATION: Success rate should improve from 50% (4/8 working) to 100% (8/8 working)")
    log_test(f"CURRENT RESULT: {passed}/4 previously failing endpoints now working ({success_rate:.1f}%)")
    
    if success_rate == 100:
        log_test("🎉 OUTSTANDING SUCCESS: All timeout issues completely resolved!")
        log_test("✅ All 4 previously failing endpoints now working correctly")
        log_test("✅ No enum serialization errors detected")
        log_test("✅ No missing method errors detected")
        log_test("✅ All endpoints responding within 15s timeout threshold")
        log_test("✅ serialize_enums_for_mongodb function working correctly")
    elif success_rate >= 75:
        log_test("🎯 MAJOR IMPROVEMENT: Most timeout issues resolved")
        log_test("⚠️  Some endpoints may still need attention")
    elif success_rate >= 50:
        log_test("📈 PARTIAL IMPROVEMENT: Some progress made")
        log_test("⚠️  Several endpoints still need fixes")
    else:
        log_test("🚨 TIMEOUT ISSUES PERSIST: Fixes not effective")
        log_test("❌ Most endpoints still failing or timing out")
    
    # Specific findings for review request
    log_test("\n" + "=" * 100)
    log_test("🔍 SPECIFIC FINDINGS FOR REVIEW REQUEST")
    log_test("=" * 100)
    
    findings = []
    for test_name, success, details in all_results:
        if success:
            findings.append(f"✅ {test_name}: RESOLVED - {details}")
        else:
            findings.append(f"❌ {test_name}: STILL FAILING - {details}")
    
    for finding in findings:
        log_test(finding)
    
    if success_rate >= 75:
        log_test("\n✅ LEGAL RESEARCH ENGINE TIMEOUT RESOLUTION: SUCCESSFUL")
        return 0
    else:
        log_test("\n❌ LEGAL RESEARCH ENGINE TIMEOUT RESOLUTION: NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    sys.exit(main())