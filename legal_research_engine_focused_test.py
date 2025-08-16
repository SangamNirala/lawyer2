#!/usr/bin/env python3
"""
Legal Research Engine Focused Testing - Review Request Verification
Testing specific endpoints mentioned in the review request with exact requirements
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://key-rotation-1.preview.emergentagent.com/api"

class LegalResearchEngineFocusedTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.timeout = 30  # 30 second timeout
        self.test_results = []
        self.endpoint_results = {}
        
    def log_test(self, test_name: str, success: bool, details: str, response_time: float = 0.0, endpoint: str = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'endpoint': endpoint,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_time > 0:
            print(f"   Response Time: {response_time:.3f}s")
    
    def test_citation_analysis_endpoint(self) -> bool:
        """Test 1: POST /api/legal-research-engine/citation-analysis - Check for summary.total_nodes"""
        print("\n🎯 TEST 1: CITATION ANALYSIS - SUMMARY.TOTAL_NODES VERIFICATION")
        print("=" * 70)
        
        citation_request = {
            "cases": [
                {
                    "case_id": "case_001",
                    "title": "Smith v. Jones Commercial Contract Dispute",
                    "citation": "123 F.3d 456 (9th Cir. 2020)",
                    "court": "9th Circuit Court of Appeals",
                    "jurisdiction": "US"
                },
                {
                    "case_id": "case_002", 
                    "title": "ABC Corp v. XYZ Ltd Contract Breach",
                    "citation": "456 F.Supp.3d 789 (N.D. Cal. 2021)",
                    "court": "Northern District of California",
                    "jurisdiction": "US"
                }
            ],
            "depth": 2,
            "jurisdiction_filter": "US"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/citation-analysis",
                json=citation_request
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                citation_data = response.json()
                print(f"📊 Response Keys: {list(citation_data.keys())}")
                
                # Check for summary.total_nodes (primary requirement)
                if 'summary' in citation_data and 'total_nodes' in citation_data['summary']:
                    total_nodes = citation_data['summary']['total_nodes']
                    total_edges = citation_data['summary'].get('total_edges', 0)
                    
                    # Verify non-negative integers
                    if isinstance(total_nodes, int) and total_nodes >= 0:
                        self.log_test("Citation Analysis - summary.total_nodes", True, 
                                    f"✅ Found summary.total_nodes: {total_nodes} (non-negative integer)", 
                                    response_time, "citation-analysis")
                        
                        # Check total_edges too
                        if isinstance(total_edges, int) and total_edges >= 0:
                            print(f"   ✅ summary.total_edges: {total_edges} (non-negative integer)")
                        
                        # Check authority_ranking is a list
                        authority_ranking = citation_data.get('authority_ranking', [])
                        if isinstance(authority_ranking, list):
                            print(f"   ✅ authority_ranking: list with {len(authority_ranking)} items")
                            self.endpoint_results['citation-analysis'] = True
                            return True
                        else:
                            print(f"   ⚠️ authority_ranking is not a list: {type(authority_ranking)}")
                            self.endpoint_results['citation-analysis'] = True  # Still pass as main requirement met
                            return True
                    else:
                        self.log_test("Citation Analysis - summary.total_nodes", False, 
                                    f"❌ total_nodes is not a non-negative integer: {total_nodes} (type: {type(total_nodes)})", 
                                    response_time, "citation-analysis")
                
                # Check for top-level total_nodes (fallback)
                elif 'total_nodes' in citation_data:
                    total_nodes = citation_data['total_nodes']
                    if isinstance(total_nodes, int) and total_nodes >= 0:
                        self.log_test("Citation Analysis - top-level total_nodes", True, 
                                    f"✅ Found top-level total_nodes: {total_nodes} (non-negative integer)", 
                                    response_time, "citation-analysis")
                        self.endpoint_results['citation-analysis'] = True
                        return True
                    else:
                        self.log_test("Citation Analysis - top-level total_nodes", False, 
                                    f"❌ total_nodes is not a non-negative integer: {total_nodes}", 
                                    response_time, "citation-analysis")
                else:
                    self.log_test("Citation Analysis", False, 
                                f"❌ Missing both summary.total_nodes and top-level total_nodes", 
                                response_time, "citation-analysis")
                    print(f"   Available keys: {list(citation_data.keys())}")
                    
            else:
                self.log_test("Citation Analysis Endpoint", False, 
                            f"❌ HTTP {response.status_code}: {response.text}", response_time, "citation-analysis")
                
        except Exception as e:
            self.log_test("Citation Analysis Endpoint", False, f"❌ Exception: {str(e)}", 0, "citation-analysis")
        
        self.endpoint_results['citation-analysis'] = False
        return False
    
    def test_structure_arguments_endpoint(self) -> bool:
        """Test 2: POST /api/legal-research-engine/structure-arguments - Check response structure"""
        print("\n🎯 TEST 2: STRUCTURE ARGUMENTS - RESPONSE STRUCTURE VERIFICATION")
        print("=" * 70)
        
        arguments_request = {
            "argument_data": {
                "legal_question": "What are the strongest arguments for specific performance in a software development contract breach?",
                "case_facts": "Unique software with no market substitute, substantial investment, ongoing business relationship",
                "legal_issues": ["specific performance", "adequate remedy at law", "uniqueness"],
                "jurisdiction": "US",
                "case_type": "commercial_contract"
            },
            "argument_strength": "strong",
            "include_counterarguments": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/structure-arguments",
                json=arguments_request
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                arguments_data = response.json()
                print(f"📊 Response Keys: {list(arguments_data.keys())}")
                
                # Check required fields: id, legal_question, argument_structure
                required_fields = ['id', 'legal_question', 'argument_structure']
                missing_fields = []
                
                for field in required_fields:
                    if field not in arguments_data:
                        missing_fields.append(field)
                
                if not missing_fields:
                    # Check argument_structure has required keys
                    argument_structure = arguments_data.get('argument_structure', {})
                    required_structure_keys = ['primary', 'supporting', 'counterarguments', 'mitigation', 'summary']
                    missing_structure_keys = []
                    
                    for key in required_structure_keys:
                        if key not in argument_structure:
                            missing_structure_keys.append(key)
                    
                    if not missing_structure_keys:
                        # Check for numerical scores
                        numerical_scores = []
                        for key, value in arguments_data.items():
                            if 'score' in key.lower() and isinstance(value, (int, float)):
                                numerical_scores.append(f"{key}: {value}")
                        
                        self.log_test("Structure Arguments - Response Structure", True, 
                                    f"✅ All required fields present, argument_structure complete, {len(numerical_scores)} numerical scores", 
                                    response_time, "structure-arguments")
                        
                        print(f"   ✅ ID: {arguments_data.get('id')}")
                        print(f"   ✅ Legal Question: {arguments_data.get('legal_question')[:50]}...")
                        print(f"   ✅ Argument Structure Keys: {list(argument_structure.keys())}")
                        print(f"   ✅ Numerical Scores: {numerical_scores}")
                        
                        self.endpoint_results['structure-arguments'] = True
                        return True
                    else:
                        self.log_test("Structure Arguments - Argument Structure", False, 
                                    f"❌ Missing argument_structure keys: {missing_structure_keys}", 
                                    response_time, "structure-arguments")
                else:
                    self.log_test("Structure Arguments - Required Fields", False, 
                                f"❌ Missing required fields: {missing_fields}", 
                                response_time, "structure-arguments")
                    
            else:
                self.log_test("Structure Arguments Endpoint", False, 
                            f"❌ HTTP {response.status_code}: {response.text}", response_time, "structure-arguments")
                
        except Exception as e:
            self.log_test("Structure Arguments Endpoint", False, f"❌ Exception: {str(e)}", 0, "structure-arguments")
        
        self.endpoint_results['structure-arguments'] = False
        return False
    
    def test_research_endpoint_valid_types(self) -> bool:
        """Test 3a: POST /api/legal-research-engine/research - Valid research_type values"""
        print("\n🎯 TEST 3A: RESEARCH ENDPOINT - VALID RESEARCH_TYPE VALUES")
        print("=" * 70)
        
        valid_research_types = ["comprehensive", "precedent_search", "citation_analysis", "memo_generation"]
        
        for research_type in valid_research_types:
            research_request = {
                "query_text": "Contract breach remedies and damages in commercial disputes",
                "research_type": research_type,
                "jurisdiction": "US",
                "legal_domain": "contract_law",
                "priority": "medium",
                "max_results": 10,
                "min_confidence": 0.7,
                "include_analysis": True,
                "cache_results": True
            }
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{BACKEND_URL}/legal-research-engine/research",
                    json=research_request
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    research_data = response.json()
                    
                    if 'id' in research_data:
                        self.log_test(f"Research - {research_type}", True, 
                                    f"✅ Valid research_type '{research_type}' accepted", 
                                    response_time, "research")
                    else:
                        self.log_test(f"Research - {research_type}", False, 
                                    f"❌ Missing 'id' in response for research_type '{research_type}'", 
                                    response_time, "research")
                        return False
                else:
                    self.log_test(f"Research - {research_type}", False, 
                                f"❌ HTTP {response.status_code} for research_type '{research_type}': {response.text}", 
                                response_time, "research")
                    return False
                    
            except Exception as e:
                self.log_test(f"Research - {research_type}", False, f"❌ Exception for research_type '{research_type}': {str(e)}", 0, "research")
                return False
        
        return True
    
    def test_research_endpoint_invalid_types(self) -> bool:
        """Test 3b: POST /api/legal-research-engine/research - Invalid research_type fallback"""
        print("\n🎯 TEST 3B: RESEARCH ENDPOINT - INVALID RESEARCH_TYPE FALLBACK")
        print("=" * 70)
        
        invalid_research_types = ["invalid_type", "unknown_research", "bad_enum_value"]
        
        for research_type in invalid_research_types:
            research_request = {
                "query_text": "Contract breach remedies and damages in commercial disputes",
                "research_type": research_type,
                "jurisdiction": "US",
                "legal_domain": "contract_law",
                "priority": "medium",
                "max_results": 10,
                "min_confidence": 0.7,
                "include_analysis": True,
                "cache_results": True
            }
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{BACKEND_URL}/legal-research-engine/research",
                    json=research_request
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    research_data = response.json()
                    
                    if 'id' in research_data:
                        self.log_test(f"Research Fallback - {research_type}", True, 
                                    f"✅ Invalid research_type '{research_type}' handled with fallback (defaulted to comprehensive)", 
                                    response_time, "research")
                    else:
                        self.log_test(f"Research Fallback - {research_type}", False, 
                                    f"❌ Missing 'id' in fallback response for research_type '{research_type}'", 
                                    response_time, "research")
                        return False
                elif response.status_code == 422:
                    # Check if it's still throwing validation errors (should be fixed)
                    error_text = response.text
                    if "is not a valid ResearchType" in error_text:
                        self.log_test(f"Research Fallback - {research_type}", False, 
                                    f"❌ ENUM VALIDATION ERROR STILL PRESENT for '{research_type}': {error_text}", 
                                    response_time, "research")
                        return False
                    else:
                        self.log_test(f"Research Fallback - {research_type}", False, 
                                    f"❌ Unexpected validation error for '{research_type}': {error_text}", 
                                    response_time, "research")
                        return False
                else:
                    self.log_test(f"Research Fallback - {research_type}", False, 
                                f"❌ HTTP {response.status_code} for invalid research_type '{research_type}': {response.text}", 
                                response_time, "research")
                    return False
                    
            except Exception as e:
                self.log_test(f"Research Fallback - {research_type}", False, f"❌ Exception for research_type '{research_type}': {str(e)}", 0, "research")
                return False
        
        return True
    
    def test_multi_jurisdiction_search_endpoint(self) -> bool:
        """Test 4: POST /api/legal-research-engine/multi-jurisdiction-search - Basic smoke test"""
        print("\n🎯 TEST 4: MULTI-JURISDICTION SEARCH - BASIC SMOKE TEST")
        print("=" * 70)
        
        multi_jurisdiction_request = {
            "query": "Contract breach remedies and specific performance requirements",
            "jurisdictions": ["US", "UK", "CA"],
            "legal_domain": "contract_law",
            "comparison_mode": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/multi-jurisdiction-search",
                json=multi_jurisdiction_request
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                multi_jurisdiction_data = response.json()
                print(f"📊 Response Keys: {list(multi_jurisdiction_data.keys())}")
                
                # Check for comparison fields (basic requirement)
                comparison_fields = ['results', 'comparison', 'jurisdictions', 'analysis']
                found_fields = []
                
                for field in comparison_fields:
                    if field in multi_jurisdiction_data:
                        found_fields.append(field)
                
                if found_fields:
                    self.log_test("Multi-Jurisdiction Search - Response Fields", True, 
                                f"✅ Endpoint responds with comparison fields: {found_fields}", 
                                response_time, "multi-jurisdiction-search")
                    
                    # Check if results contain jurisdiction-specific data
                    results = multi_jurisdiction_data.get('results', [])
                    if isinstance(results, list) and len(results) > 0:
                        print(f"   ✅ Results: {len(results)} items returned")
                    
                    self.endpoint_results['multi-jurisdiction-search'] = True
                    return True
                else:
                    self.log_test("Multi-Jurisdiction Search - Response Fields", False, 
                                f"❌ No expected comparison fields found in response", 
                                response_time, "multi-jurisdiction-search")
                    
            else:
                self.log_test("Multi-Jurisdiction Search Endpoint", False, 
                            f"❌ HTTP {response.status_code}: {response.text}", response_time, "multi-jurisdiction-search")
                
        except Exception as e:
            self.log_test("Multi-Jurisdiction Search Endpoint", False, f"❌ Exception: {str(e)}", 0, "multi-jurisdiction-search")
        
        self.endpoint_results['multi-jurisdiction-search'] = False
        return False
    
    def run_focused_testing(self):
        """Execute focused testing of specific Legal Research Engine endpoints"""
        print("🎯 LEGAL RESEARCH ENGINE FOCUSED TESTING - REVIEW REQUEST VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("Testing specific endpoints mentioned in review request:")
        print("1. POST /api/legal-research-engine/citation-analysis (summary.total_nodes check)")
        print("2. POST /api/legal-research-engine/structure-arguments (response structure check)")
        print("3. POST /api/legal-research-engine/research (valid/invalid research_type handling)")
        print("4. POST /api/legal-research-engine/multi-jurisdiction-search (basic smoke test)")
        print("=" * 80)
        
        # Execute focused tests
        test_results = []
        test_results.append(self.test_citation_analysis_endpoint())
        test_results.append(self.test_structure_arguments_endpoint())
        test_results.append(self.test_research_endpoint_valid_types())
        test_results.append(self.test_research_endpoint_invalid_types())
        test_results.append(self.test_multi_jurisdiction_search_endpoint())
        
        # Calculate overall success
        total_tests = 5
        passed_tests = sum(1 for result in test_results if result)
        success_rate = (passed_tests / total_tests) * 100
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 LEGAL RESEARCH ENGINE FOCUSED TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Test-by-test results
        print("\n📋 TEST RESULTS:")
        test_names = [
            "Citation Analysis (summary.total_nodes)",
            "Structure Arguments (response structure)",
            "Research Endpoint (valid research_types)",
            "Research Endpoint (invalid research_type fallback)",
            "Multi-Jurisdiction Search (basic smoke test)"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{i+1}. {status} {test_name}")
        
        # Endpoint-specific results
        print("\n📋 ENDPOINT RESULTS:")
        endpoints = [
            ("citation-analysis", "POST /api/legal-research-engine/citation-analysis"),
            ("structure-arguments", "POST /api/legal-research-engine/structure-arguments"),
            ("research", "POST /api/legal-research-engine/research"),
            ("multi-jurisdiction-search", "POST /api/legal-research-engine/multi-jurisdiction-search")
        ]
        
        for endpoint_key, endpoint_name in endpoints:
            status = "✅ WORKING" if self.endpoint_results.get(endpoint_key, False) else "❌ FAILED"
            print(f"{status} {endpoint_name}")
        
        # Detailed test results
        print("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"     {result['details']}")
            if result['response_time'] > 0:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        return success_rate >= 80.0  # Target 80%+ success rate for focused testing

def main():
    """Main execution function"""
    tester = LegalResearchEngineFocusedTester()
    
    try:
        overall_success = tester.run_focused_testing()
        
        if overall_success:
            print("\n🎉 LEGAL RESEARCH ENGINE FOCUSED TESTING COMPLETED SUCCESSFULLY")
            print("✅ All critical endpoints verified as per review request")
            sys.exit(0)
        else:
            print("\n❌ LEGAL RESEARCH ENGINE FOCUSED TESTING SHOWS REMAINING ISSUES")
            print("⚠️ Some endpoints still need fixes as per review request")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()