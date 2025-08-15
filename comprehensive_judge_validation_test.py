#!/usr/bin/env python3
"""
Comprehensive Judge Validation System Testing
===========================================

This script tests the comprehensive judge validation system that addresses concerns about 
fake/non-existent judges returning results. Tests validation response types, sources,
and distinguishes between fake and real judges.

SPECIFIC TESTING REQUIREMENTS:
1. Individual Judge Analysis with Validation (/api/litigation/judge-insights/{judge_name})
2. Judge Comparison with Validation (/api/litigation/judge-comparison) 
3. Validation Response Types (NO_INFORMATION_FOUND, HIGH_CONFIDENCE, MODERATE_CONFIDENCE, LOW_CONFIDENCE_ESTIMATED)
4. Validation Sources and reference links
5. Error handling with fake judges vs real judges
6. Test fake judges like "ZZZ Fictional Judge" vs realistic names like "John Smith"
7. Verify validation response structures with is_verified, validation_sources, validation_summary, reference_links
8. Test jurisdiction parameters (US, India, international)
9. Test error handling for empty judge names or special characters
"""

import requests
import json
import sys
import time
from urllib.parse import quote
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://testing-fixes.preview.emergentagent.com/api"

class ComprehensiveJudgeValidationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print("🎯 COMPREHENSIVE JUDGE VALIDATION SYSTEM TESTING INITIATED")
        print(f"📡 Backend URL: {BACKEND_URL}")
        print("=" * 80)

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results for tracking"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} | {test_name}")
        if details:
            print(f"     Details: {details}")
        if not success and response_data:
            print(f"     Response: {str(response_data)[:200]}...")
        print()

    def test_fake_vs_real_judges_individual(self):
        """Test individual judge analysis with fake vs realistic judges"""
        print("🎭 TESTING FAKE VS REAL JUDGES - INDIVIDUAL ANALYSIS")
        print("-" * 60)
        
        # Test cases with clearly fake judges vs realistic names
        test_cases = [
            {
                "name": "ZZZ Fictional Judge",
                "type": "fake",
                "expected_verified": False,
                "description": "Obviously fake judge name with ZZZ prefix"
            },
            {
                "name": "Judge Unicorn Rainbow",
                "type": "fake", 
                "expected_verified": False,
                "description": "Fictional judge with impossible name"
            },
            {
                "name": "XYZ NonExistent Judge",
                "type": "fake",
                "expected_verified": False,
                "description": "Clearly fabricated judge name"
            },
            {
                "name": "John Smith",
                "type": "realistic",
                "expected_verified": None,  # Could be true or false depending on actual existence
                "description": "Common realistic judge name"
            },
            {
                "name": "Sarah Martinez",
                "type": "realistic",
                "expected_verified": None,
                "description": "Realistic Hispanic judge name"
            },
            {
                "name": "Robert Johnson",
                "type": "realistic",
                "expected_verified": None,
                "description": "Common realistic judge name"
            }
        ]
        
        for test_case in test_cases:
            judge_name = test_case["name"]
            judge_type = test_case["type"]
            expected_verified = test_case["expected_verified"]
            description = test_case["description"]
            
            try:
                encoded_judge_name = quote(judge_name)
                url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check validation fields
                    is_verified = data.get('is_verified', False)
                    validation_sources = data.get('validation_sources', [])
                    validation_summary = data.get('validation_summary', '')
                    reference_links = data.get('reference_links', [])
                    confidence_score = data.get('confidence_score', 0)
                    
                    # For fake judges, expect is_verified = False, low confidence, limited sources
                    if judge_type == "fake":
                        if not is_verified and confidence_score < 0.5:
                            self.log_test_result(
                                f"Fake Judge Detection - {judge_name}",
                                True,
                                f"✅ Correctly identified as unverified (is_verified: {is_verified}, confidence: {confidence_score:.2f})"
                            )
                        else:
                            self.log_test_result(
                                f"Fake Judge Detection - {judge_name}",
                                False,
                                f"❌ Fake judge marked as verified (is_verified: {is_verified}, confidence: {confidence_score:.2f})"
                            )
                    else:  # realistic judges
                        # For realistic judges, check that validation system is working
                        validation_working = all([
                            isinstance(is_verified, bool),
                            isinstance(validation_sources, list),
                            isinstance(validation_summary, str),
                            isinstance(reference_links, list),
                            isinstance(confidence_score, (int, float))
                        ])
                        
                        if validation_working:
                            self.log_test_result(
                                f"Realistic Judge Validation - {judge_name}",
                                True,
                                f"✅ Validation system working (is_verified: {is_verified}, confidence: {confidence_score:.2f}, sources: {len(validation_sources)})"
                            )
                        else:
                            self.log_test_result(
                                f"Realistic Judge Validation - {judge_name}",
                                False,
                                f"❌ Validation system not working properly"
                            )
                    
                    # Test validation response structure for all judges
                    required_validation_fields = ['is_verified', 'validation_sources', 'validation_summary', 'reference_links']
                    missing_fields = [field for field in required_validation_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_test_result(
                            f"Validation Fields Structure - {judge_name}",
                            True,
                            f"✅ All validation fields present: {required_validation_fields}"
                        )
                    else:
                        self.log_test_result(
                            f"Validation Fields Structure - {judge_name}",
                            False,
                            f"❌ Missing validation fields: {missing_fields}"
                        )
                        
                else:
                    self.log_test_result(
                        f"API Response - {judge_name}",
                        False,
                        f"❌ HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Request Exception - {judge_name}",
                    False,
                    f"❌ Exception: {str(e)}"
                )

    def test_fake_vs_real_judges_comparison(self):
        """Test judge comparison with mixed fake and real judges"""
        print("🎭 TESTING FAKE VS REAL JUDGES - COMPARISON")
        print("-" * 60)
        
        test_cases = [
            {
                "judge_names": ["ZZZ Fictional Judge", "ABC Fake Judge"],
                "description": "Two obviously fake judges",
                "expected_behavior": "Should return validation warnings or no information found"
            },
            {
                "judge_names": ["John Smith", "Sarah Martinez"],
                "description": "Two realistic judge names",
                "expected_behavior": "Should work with appropriate validation information"
            },
            {
                "judge_names": ["ZZZ Fictional Judge", "John Smith"],
                "description": "Mixed fake and realistic judge",
                "expected_behavior": "Should handle mixed validation states properly"
            },
            {
                "judge_names": ["Judge Unicorn Rainbow", "XYZ NonExistent Judge", "John Smith"],
                "description": "Two fake judges and one realistic",
                "expected_behavior": "Should provide validation details for each judge"
            }
        ]
        
        for test_case in test_cases:
            judge_names = test_case["judge_names"]
            description = test_case["description"]
            expected_behavior = test_case["expected_behavior"]
            
            try:
                url = f"{BACKEND_URL}/litigation/judge-comparison"
                payload = {
                    "judge_names": judge_names,
                    "case_type": "civil",
                    "jurisdiction": "US"
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if validation_info exists
                    if 'validation_info' in data:
                        validation_info = data['validation_info']
                        
                        # Check validation_info structure
                        required_validation_keys = [
                            'verified_judges', 'estimated_judges', 'judges_with_no_information',
                            'verification_details', 'judges_not_found'
                        ]
                        
                        missing_keys = [key for key in required_validation_keys if key not in validation_info]
                        
                        if not missing_keys:
                            self.log_test_result(
                                f"Validation Info Structure - {', '.join(judge_names[:2])}...",
                                True,
                                f"✅ All validation info keys present: verified={validation_info.get('verified_judges', 0)}, estimated={validation_info.get('estimated_judges', 0)}, not_found={validation_info.get('judges_with_no_information', 0)}"
                            )
                        else:
                            self.log_test_result(
                                f"Validation Info Structure - {', '.join(judge_names[:2])}...",
                                False,
                                f"❌ Missing validation info keys: {missing_keys}"
                            )
                        
                        # Check verification_details for each judge
                        verification_details = validation_info.get('verification_details', [])
                        
                        for detail in verification_details:
                            judge_name = detail.get('judge_name', 'Unknown')
                            is_verified = detail.get('is_verified', False)
                            confidence_score = detail.get('confidence_score', 0)
                            validation_summary = detail.get('validation_summary', '')
                            reference_links = detail.get('reference_links', [])
                            
                            # Check if this is a fake judge (contains ZZZ, ABC, Unicorn, etc.)
                            is_fake_judge = any(fake_indicator in judge_name for fake_indicator in ['ZZZ', 'ABC', 'Unicorn', 'XYZ', 'Fictional'])
                            
                            if is_fake_judge:
                                if not is_verified and confidence_score < 0.5:
                                    self.log_test_result(
                                        f"Fake Judge in Comparison - {judge_name}",
                                        True,
                                        f"✅ Correctly identified as unverified (confidence: {confidence_score:.2f})"
                                    )
                                else:
                                    self.log_test_result(
                                        f"Fake Judge in Comparison - {judge_name}",
                                        False,
                                        f"❌ Fake judge incorrectly verified (is_verified: {is_verified}, confidence: {confidence_score:.2f})"
                                    )
                            else:
                                # For realistic judges, just verify validation structure exists
                                validation_structure_ok = all([
                                    isinstance(is_verified, bool),
                                    isinstance(confidence_score, (int, float)),
                                    isinstance(validation_summary, str),
                                    isinstance(reference_links, list)
                                ])
                                
                                if validation_structure_ok:
                                    self.log_test_result(
                                        f"Realistic Judge in Comparison - {judge_name}",
                                        True,
                                        f"✅ Validation structure correct (is_verified: {is_verified}, confidence: {confidence_score:.2f})"
                                    )
                                else:
                                    self.log_test_result(
                                        f"Realistic Judge in Comparison - {judge_name}",
                                        False,
                                        f"❌ Invalid validation structure"
                                    )
                    else:
                        self.log_test_result(
                            f"Validation Info Missing - {', '.join(judge_names[:2])}...",
                            False,
                            f"❌ No validation_info section in response"
                        )
                        
                elif response.status_code == 400:
                    # Check if this is expected for all-fake judges
                    all_fake = all(any(fake_indicator in name for fake_indicator in ['ZZZ', 'ABC', 'Unicorn', 'XYZ', 'Fictional']) for name in judge_names)
                    
                    if all_fake:
                        self.log_test_result(
                            f"All Fake Judges Handling - {', '.join(judge_names[:2])}...",
                            True,
                            f"✅ Correctly returned 400 for all fake judges"
                        )
                    else:
                        self.log_test_result(
                            f"Mixed Judges HTTP 400 - {', '.join(judge_names[:2])}...",
                            False,
                            f"❌ Unexpected 400 response for mixed/realistic judges"
                        )
                else:
                    self.log_test_result(
                        f"HTTP Response - {', '.join(judge_names[:2])}...",
                        False,
                        f"❌ HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Comparison Request Exception - {', '.join(judge_names[:2])}...",
                    False,
                    f"❌ Exception: {str(e)}"
                )

    def test_validation_response_types(self):
        """Test different validation response types and confidence levels"""
        print("📊 TESTING VALIDATION RESPONSE TYPES")
        print("-" * 60)
        
        # Test judges designed to trigger different validation responses
        test_cases = [
            {
                "name": "ZZZ Fictional Judge",
                "expected_type": "NO_INFORMATION_FOUND or LOW_CONFIDENCE_ESTIMATED",
                "description": "Should trigger low confidence or no information response"
            },
            {
                "name": "John Smith",
                "expected_type": "HIGH_CONFIDENCE, MODERATE_CONFIDENCE, or LOW_CONFIDENCE_ESTIMATED",
                "description": "Common name might have various confidence levels"
            },
            {
                "name": "",
                "expected_type": "ERROR",
                "description": "Empty name should trigger error handling"
            }
        ]
        
        for test_case in test_cases:
            judge_name = test_case["name"]
            expected_type = test_case["expected_type"]
            description = test_case["description"]
            
            if judge_name == "":
                # Test empty judge name (should return 404)
                try:
                    url = f"{BACKEND_URL}/litigation/judge-insights/"
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 404:
                        self.log_test_result(
                            "Empty Judge Name Error Handling",
                            True,
                            f"✅ Correctly returned 404 for empty judge name"
                        )
                    else:
                        self.log_test_result(
                            "Empty Judge Name Error Handling",
                            False,
                            f"❌ Expected 404, got {response.status_code}"
                        )
                except Exception as e:
                    self.log_test_result(
                        "Empty Judge Name Exception",
                        False,
                        f"❌ Exception: {str(e)}"
                    )
            else:
                # Test normal judge names for validation types
                try:
                    encoded_judge_name = quote(judge_name)
                    url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
                    
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        confidence_score = data.get('confidence_score', 0)
                        is_verified = data.get('is_verified', False)
                        validation_summary = data.get('validation_summary', '')
                        validation_sources = data.get('validation_sources', [])
                        
                        # Categorize response based on confidence and verification
                        if confidence_score >= 0.8 and is_verified:
                            response_type = "HIGH_CONFIDENCE"
                        elif confidence_score >= 0.5 and is_verified:
                            response_type = "MODERATE_CONFIDENCE"  
                        elif confidence_score > 0:
                            response_type = "LOW_CONFIDENCE_ESTIMATED"
                        else:
                            response_type = "NO_INFORMATION_FOUND"
                        
                        # Check if validation summary provides useful information
                        has_useful_summary = len(validation_summary) > 0
                        has_sources = len(validation_sources) > 0
                        
                        self.log_test_result(
                            f"Validation Response Type - {judge_name}",
                            True,
                            f"✅ Response type: {response_type} (confidence: {confidence_score:.2f}, verified: {is_verified}, sources: {len(validation_sources)}, summary: {has_useful_summary})"
                        )
                        
                        # Test validation response structure completeness
                        validation_complete = all([
                            isinstance(is_verified, bool),
                            isinstance(validation_sources, list),
                            isinstance(validation_summary, str),
                            isinstance(data.get('reference_links', []), list)
                        ])
                        
                        if validation_complete:
                            self.log_test_result(
                                f"Validation Structure Complete - {judge_name}",
                                True,
                                f"✅ All validation fields properly structured"
                            )
                        else:
                            self.log_test_result(
                                f"Validation Structure Complete - {judge_name}",
                                False,
                                f"❌ Some validation fields improperly structured"
                            )
                    else:
                        self.log_test_result(
                            f"Validation Response HTTP - {judge_name}",
                            False,
                            f"❌ HTTP {response.status_code}: {response.text[:100]}"
                        )
                        
                except Exception as e:
                    self.log_test_result(
                        f"Validation Response Exception - {judge_name}",
                        False,
                        f"❌ Exception: {str(e)}"
                    )

    def test_validation_sources_and_links(self):
        """Test validation sources and reference links structure"""
        print("🔗 TESTING VALIDATION SOURCES AND REFERENCE LINKS")
        print("-" * 60)
        
        test_judges = ["John Smith", "Sarah Martinez", "ZZZ Fictional Judge"]
        
        for judge_name in test_judges:
            try:
                encoded_judge_name = quote(judge_name)
                url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    validation_sources = data.get('validation_sources', [])
                    reference_links = data.get('reference_links', [])
                    
                    # Test validation_sources structure
                    if isinstance(validation_sources, list):
                        sources_ok = all(isinstance(source, str) for source in validation_sources)
                        if sources_ok:
                            self.log_test_result(
                                f"Validation Sources Structure - {judge_name}",
                                True,
                                f"✅ validation_sources is array of strings ({len(validation_sources)} sources)"
                            )
                        else:
                            self.log_test_result(
                                f"Validation Sources Structure - {judge_name}",
                                False,
                                f"❌ validation_sources contains non-string elements"
                            )
                    else:
                        self.log_test_result(
                            f"Validation Sources Structure - {judge_name}",
                            False,
                            f"❌ validation_sources is not an array"
                        )
                    
                    # Test reference_links structure
                    if isinstance(reference_links, list):
                        links_structure_ok = True
                        for i, link in enumerate(reference_links):
                            if not isinstance(link, dict):
                                links_structure_ok = False
                                break
                            if 'name' not in link or 'url' not in link:
                                links_structure_ok = False
                                break
                            if not isinstance(link['name'], str) or not isinstance(link['url'], str):
                                links_structure_ok = False
                                break
                        
                        if links_structure_ok:
                            self.log_test_result(
                                f"Reference Links Structure - {judge_name}",
                                True,
                                f"✅ reference_links properly structured ({len(reference_links)} links)"
                            )
                            
                            # Test a few sample links for basic URL format
                            for i, link in enumerate(reference_links[:3]):  # Test first 3 links
                                url_str = link['url']
                                name_str = link['name']
                                
                                if url_str.startswith(('http://', 'https://')) and len(name_str) > 0:
                                    self.log_test_result(
                                        f"Reference Link Format {i} - {judge_name}",
                                        True,
                                        f"✅ Link {i}: {name_str[:30]}... -> {url_str[:50]}..."
                                    )
                                else:
                                    self.log_test_result(
                                        f"Reference Link Format {i} - {judge_name}",
                                        False,
                                        f"❌ Invalid link format: name='{name_str}', url='{url_str}'"
                                    )
                        else:
                            self.log_test_result(
                                f"Reference Links Structure - {judge_name}",
                                False,
                                f"❌ reference_links has invalid structure"
                            )
                    else:
                        self.log_test_result(
                            f"Reference Links Structure - {judge_name}",
                            False,
                            f"❌ reference_links is not an array"
                        )
                        
                else:
                    self.log_test_result(
                        f"Sources/Links HTTP Response - {judge_name}",
                        False,
                        f"❌ HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Sources/Links Exception - {judge_name}",
                    False,
                    f"❌ Exception: {str(e)}"
                )

    def test_jurisdiction_parameters(self):
        """Test validation with different jurisdiction parameters"""
        print("🌍 TESTING JURISDICTION PARAMETERS")
        print("-" * 60)
        
        test_cases = [
            {
                "judge_name": "John Smith",
                "url_params": "?jurisdiction=US",
                "description": "US jurisdiction parameter"
            },
            {
                "judge_name": "Rajesh Sharma", 
                "url_params": "?jurisdiction=India",
                "description": "India jurisdiction parameter"
            },
            {
                "judge_name": "Sarah Martinez",
                "url_params": "?jurisdiction=international",
                "description": "International jurisdiction parameter"
            },
            {
                "judge_name": "John Smith",
                "url_params": "",
                "description": "No jurisdiction parameter (default)"
            }
        ]
        
        for test_case in test_cases:
            judge_name = test_case["judge_name"]
            url_params = test_case["url_params"]
            description = test_case["description"]
            
            try:
                encoded_judge_name = quote(judge_name)
                url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}{url_params}"
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check basic validation fields are present
                    validation_fields = ['is_verified', 'validation_sources', 'validation_summary', 'reference_links']
                    all_fields_present = all(field in data for field in validation_fields)
                    
                    if all_fields_present:
                        confidence_score = data.get('confidence_score', 0)
                        is_verified = data.get('is_verified', False)
                        
                        self.log_test_result(
                            f"Jurisdiction Parameter - {description}",
                            True,
                            f"✅ Validation working with jurisdiction (confidence: {confidence_score:.2f}, verified: {is_verified})"
                        )
                    else:
                        missing_fields = [field for field in validation_fields if field not in data]
                        self.log_test_result(
                            f"Jurisdiction Parameter - {description}",
                            False,
                            f"❌ Missing validation fields: {missing_fields}"
                        )
                else:
                    self.log_test_result(
                        f"Jurisdiction HTTP - {description}",
                        False,
                        f"❌ HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Jurisdiction Exception - {description}",
                    False,
                    f"❌ Exception: {str(e)}"
                )

    def test_special_characters_and_edge_cases(self):
        """Test error handling for special characters and edge cases"""
        print("🔤 TESTING SPECIAL CHARACTERS AND EDGE CASES")
        print("-" * 60)
        
        test_cases = [
            {
                "name": "Judge O'Connor",
                "description": "Apostrophe in name",
                "expected_success": True
            },
            {
                "name": "Judge María González",
                "description": "Accented characters", 
                "expected_success": True
            },
            {
                "name": "Judge Smith-Johnson",
                "description": "Hyphenated name",
                "expected_success": True
            },
            {
                "name": "Judge 123",
                "description": "Numbers in name",
                "expected_success": True  # Should work but might have low validation
            },
            {
                "name": "Judge @#$%",
                "description": "Special symbols",
                "expected_success": True  # Should work but might have low validation
            },
            {
                "name": "a" * 200,
                "description": "Very long name",
                "expected_success": False  # Might cause errors
            }
        ]
        
        for test_case in test_cases:
            judge_name = test_case["name"]
            description = test_case["description"]
            expected_success = test_case["expected_success"]
            
            try:
                encoded_judge_name = quote(judge_name)
                url = f"{BACKEND_URL}/litigation/judge-insights/{encoded_judge_name}"
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if validation fields are present and properly structured
                    validation_ok = all([
                        isinstance(data.get('is_verified'), bool),
                        isinstance(data.get('validation_sources'), list),
                        isinstance(data.get('validation_summary'), str),
                        isinstance(data.get('reference_links'), list)
                    ])
                    
                    if validation_ok:
                        self.log_test_result(
                            f"Special Characters - {description}",
                            expected_success,
                            f"✅ Handled special characters correctly (confidence: {data.get('confidence_score', 0):.2f})"
                        )
                    else:
                        self.log_test_result(
                            f"Special Characters - {description}",
                            False,
                            f"❌ Validation structure broken with special characters"
                        )
                        
                elif response.status_code in [400, 422]:
                    if not expected_success:
                        self.log_test_result(
                            f"Special Characters Error - {description}",
                            True,
                            f"✅ Correctly rejected invalid input with {response.status_code}"
                        )
                    else:
                        self.log_test_result(
                            f"Special Characters Error - {description}",
                            False,
                            f"❌ Unexpected rejection of valid input: {response.status_code}"
                        )
                else:
                    self.log_test_result(
                        f"Special Characters HTTP - {description}",
                        False,
                        f"❌ HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                if not expected_success:
                    self.log_test_result(
                        f"Special Characters Exception - {description}",
                        True,
                        f"✅ Expected exception occurred: {str(e)[:100]}"
                    )
                else:
                    self.log_test_result(
                        f"Special Characters Exception - {description}",
                        False,
                        f"❌ Unexpected exception: {str(e)[:100]}"
                    )

    def run_comprehensive_tests(self):
        """Run all comprehensive judge validation tests"""
        print("🚀 STARTING COMPREHENSIVE JUDGE VALIDATION TESTING")
        print("=" * 80)
        
        # Run all test suites
        self.test_fake_vs_real_judges_individual()
        self.test_fake_vs_real_judges_comparison() 
        self.test_validation_response_types()
        self.test_validation_sources_and_links()
        self.test_jurisdiction_parameters()
        self.test_special_characters_and_edge_cases()
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("📋 COMPREHENSIVE JUDGE VALIDATION TEST REPORT")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by test category
        category_results = {}
        for result in self.test_results:
            category = result["test_name"].split(" - ")[0]
            if category not in category_results:
                category_results[category] = {"passed": 0, "total": 0}
            category_results[category]["total"] += 1
            if result["success"]:
                category_results[category]["passed"] += 1
        
        print("📈 CATEGORY-SPECIFIC RESULTS:")
        for category, stats in category_results.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 75 else "❌"
            print(f"   {status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        print()
        
        # Show failed tests
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests[:10]:  # Show first 10 failed tests
                print(f"   • {test['test_name']}: {test['details']}")
            if len(failed_tests) > 10:
                print(f"   ... and {len(failed_tests) - 10} more failed tests")
            print()
        
        # Key validation findings
        print("🔍 KEY VALIDATION FINDINGS:")
        
        # Count fake judge detection results
        fake_judge_tests = [r for r in self.test_results if "Fake Judge" in r["test_name"]]
        fake_detection_success = [r for r in fake_judge_tests if r["success"]]
        
        if fake_judge_tests:
            fake_detection_rate = (len(fake_detection_success) / len(fake_judge_tests) * 100)
            print(f"   🎭 Fake Judge Detection: {len(fake_detection_success)}/{len(fake_judge_tests)} ({fake_detection_rate:.1f}%)")
        
        # Count validation structure tests
        validation_structure_tests = [r for r in self.test_results if "Validation" in r["test_name"] and "Structure" in r["test_name"]]
        validation_structure_success = [r for r in validation_structure_tests if r["success"]]
        
        if validation_structure_tests:
            structure_rate = (len(validation_structure_success) / len(validation_structure_tests) * 100)
            print(f"   🔧 Validation Structure: {len(validation_structure_success)}/{len(validation_structure_tests)} ({structure_rate:.1f}%)")
        
        # Count jurisdiction tests
        jurisdiction_tests = [r for r in self.test_results if "Jurisdiction" in r["test_name"]]
        jurisdiction_success = [r for r in jurisdiction_tests if r["success"]]
        
        if jurisdiction_tests:
            jurisdiction_rate = (len(jurisdiction_success) / len(jurisdiction_tests) * 100)
            print(f"   🌍 Jurisdiction Support: {len(jurisdiction_success)}/{len(jurisdiction_tests)} ({jurisdiction_rate:.1f}%)")
        
        print()
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Comprehensive judge validation system is working excellently!")
            print("   ✅ Fake judges are properly detected and handled")
            print("   ✅ Validation response types are working correctly")
            print("   ✅ Validation sources and reference links are properly structured")
            print("   ✅ Jurisdiction parameters are supported")
            print("   ✅ Error handling for edge cases is robust")
        elif success_rate >= 75:
            print("✅ GOOD: Judge validation system is working well with minor issues.")
            print("   ℹ️ Most validation functionality is operational")
            print("   ⚠️ Some edge cases or specific features may need attention")
        elif success_rate >= 60:
            print("⚠️ MODERATE: Judge validation system has significant issues requiring attention.")
            print("   ⚠️ Core validation functionality may be working but with notable problems")
            print("   🔧 Several fixes needed for full reliability")
        else:
            print("❌ CRITICAL: Judge validation system is not working properly.")
            print("   ❌ Major validation functionality is broken or missing")
            print("   🚨 Immediate attention required to fix validation system")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "category_results": category_results,
            "failed_tests": failed_tests,
            "test_results": self.test_results
        }

def main():
    """Main testing function"""
    tester = ComprehensiveJudgeValidationTester()
    results = tester.run_comprehensive_tests()
    
    # Return results for potential integration with other systems
    return results

if __name__ == "__main__":
    main()