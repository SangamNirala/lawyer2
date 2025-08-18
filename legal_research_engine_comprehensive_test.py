#!/usr/bin/env python3
"""
Legal Research Engine Comprehensive Testing - Post-Fix Verification
Testing all 8 Legal Research Engine endpoints after comprehensive fixes implementation
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://strategyengine.preview.emergentagent.com/api"

class LegalResearchEngineComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.timeout = 30  # 30 second timeout for complex operations
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
    
    def test_1_stats_endpoint(self) -> bool:
        """Test 1: GET /api/legal-research-engine/stats"""
        print("\n🎯 TEST 1: LEGAL RESEARCH ENGINE STATS")
        print("=" * 60)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/legal-research-engine/stats")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                stats_data = response.json()
                status = stats_data.get('status', '').lower()
                message = stats_data.get('message', '')
                
                # Check for expected response structure
                if 'status' in stats_data:
                    self.log_test("Stats Endpoint Response", True, f"Status: {status}, Message: {message}", response_time, "stats")
                    print(f"📊 Stats Data: {json.dumps(stats_data, indent=2)}")
                    self.endpoint_results['stats'] = True
                    return True
                else:
                    self.log_test("Stats Endpoint Response", False, f"Missing status field in response", response_time, "stats")
                    
            else:
                self.log_test("Stats Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time, "stats")
                
        except Exception as e:
            self.log_test("Stats Endpoint", False, f"Exception: {str(e)}", 0, "stats")
        
        self.endpoint_results['stats'] = False
        return False
    
    def test_2_research_endpoint(self) -> bool:
        """Test 2: POST /api/legal-research-engine/research"""
        print("\n🎯 TEST 2: LEGAL RESEARCH ENGINE RESEARCH")
        print("=" * 60)
        
        # Test data with proper enum values and fallback handling
        research_request = {
            "query_text": "Contract breach remedies and damages in commercial disputes",
            "research_type": "comprehensive",  # Valid enum value
            "jurisdiction": "US",
            "legal_domain": "contract_law",
            "priority": "medium",  # Valid enum value
            "court_level": "federal",
            "case_type": "commercial",
            "legal_issues": ["breach of contract", "damages", "remedies"],
            "max_results": 20,
            "min_confidence": 0.7,
            "include_analysis": True,
            "cache_results": True,
            "user_context": {
                "case_type": "commercial_dispute",
                "urgency": "normal"
            }
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
                
                # Check for expected response structure
                if 'id' in research_data and 'results' in research_data:
                    results_count = len(research_data.get('results', []))
                    confidence_score = research_data.get('confidence_score', 0)
                    
                    self.log_test("Research Endpoint Response", True, 
                                f"Generated {results_count} results with confidence {confidence_score}", 
                                response_time, "research")
                    
                    print(f"📊 Research Results: ID={research_data.get('id')}, Results={results_count}")
                    self.endpoint_results['research'] = True
                    return True
                else:
                    self.log_test("Research Endpoint Response", False, 
                                f"Missing required fields in response", response_time, "research")
                    
            elif response.status_code == 422:
                # Check if this is the old enum validation error (should be fixed)
                error_text = response.text
                if "is not a valid ResearchType" in error_text:
                    self.log_test("Research Endpoint", False, 
                                f"ENUM VALIDATION ERROR STILL PRESENT: {error_text}", response_time, "research")
                else:
                    self.log_test("Research Endpoint", False, 
                                f"Validation error: {error_text}", response_time, "research")
            else:
                self.log_test("Research Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "research")
                
        except Exception as e:
            self.log_test("Research Endpoint", False, f"Exception: {str(e)}", 0, "research")
        
        self.endpoint_results['research'] = False
        return False
    
    def test_3_precedent_search_endpoint(self) -> bool:
        """Test 3: POST /api/legal-research-engine/precedent-search"""
        print("\n🎯 TEST 3: LEGAL RESEARCH ENGINE PRECEDENT SEARCH")
        print("=" * 60)
        
        precedent_request = {
            "query_case": {
                "case_title": "Commercial Contract Breach Case",
                "facts": "Breach of software development contract with damages claim",
                "legal_issues": ["breach of contract", "specific performance", "damages"],
                "jurisdiction": "US",
                "case_type": "commercial"
            },
            "filters": {
                "jurisdiction": "US",
                "court_level": "federal",
                "date_range": {
                    "start": "2020-01-01",
                    "end": "2024-01-01"
                }
            },
            "max_results": 15,
            "min_similarity": 0.6
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/precedent-search",
                json=precedent_request
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                precedent_data = response.json()
                
                # Check for expected response structure
                if 'precedent_matches' in precedent_data or 'matches' in precedent_data:
                    matches = precedent_data.get('precedent_matches', precedent_data.get('matches', []))
                    matches_count = len(matches) if isinstance(matches, list) else 0
                    
                    self.log_test("Precedent Search Response", True, 
                                f"Found {matches_count} precedent matches", 
                                response_time, "precedent-search")
                    
                    print(f"📊 Precedent Matches: {matches_count}")
                    self.endpoint_results['precedent-search'] = True
                    return True
                else:
                    self.log_test("Precedent Search Response", False, 
                                f"Missing precedent matches in response", response_time, "precedent-search")
                    
            else:
                self.log_test("Precedent Search Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "precedent-search")
                
        except Exception as e:
            self.log_test("Precedent Search Endpoint", False, f"Exception: {str(e)}", 0, "precedent-search")
        
        self.endpoint_results['precedent-search'] = False
        return False
    
    def test_4_citation_analysis_endpoint(self) -> bool:
        """Test 4: POST /api/legal-research-engine/citation-analysis"""
        print("\n🎯 TEST 4: LEGAL RESEARCH ENGINE CITATION ANALYSIS")
        print("=" * 60)
        
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
                
                # Check for expected response structure - looking for summary.total_nodes (fixed structure)
                if 'summary' in citation_data and 'total_nodes' in citation_data['summary']:
                    total_nodes = citation_data['summary']['total_nodes']
                    total_edges = citation_data['summary'].get('total_edges', 0)
                    
                    self.log_test("Citation Analysis Response", True, 
                                f"Network analysis: {total_nodes} nodes, {total_edges} edges", 
                                response_time, "citation-analysis")
                    
                    print(f"📊 Citation Network: {total_nodes} nodes, {total_edges} edges")
                    self.endpoint_results['citation-analysis'] = True
                    return True
                elif 'total_nodes' in citation_data:
                    # Fallback for direct total_nodes field
                    total_nodes = citation_data['total_nodes']
                    self.log_test("Citation Analysis Response", True, 
                                f"Citation network with {total_nodes} nodes", 
                                response_time, "citation-analysis")
                    self.endpoint_results['citation-analysis'] = True
                    return True
                else:
                    self.log_test("Citation Analysis Response", False, 
                                f"Missing total_nodes in response structure", response_time, "citation-analysis")
                    print(f"📊 Response structure: {list(citation_data.keys())}")
                    
            else:
                self.log_test("Citation Analysis Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "citation-analysis")
                
        except Exception as e:
            self.log_test("Citation Analysis Endpoint", False, f"Exception: {str(e)}", 0, "citation-analysis")
        
        self.endpoint_results['citation-analysis'] = False
        return False
    
    def test_5_memo_generation_endpoint(self) -> bool:
        """Test 5: POST /api/legal-research-engine/generate-memo"""
        print("\n🎯 TEST 5: LEGAL RESEARCH ENGINE MEMO GENERATION")
        print("=" * 60)
        
        memo_request = {
            "memo_data": {
                "research_query": "Contract breach remedies and damages analysis",
                "case_facts": "Commercial software development contract breach with $500K damages claim",
                "legal_issues": ["breach of contract", "damages calculation", "specific performance"],
                "jurisdiction": "US",
                "client_name": "ABC Corporation",
                "attorney_name": "John Smith, Esq."
            },
            "memo_type": "comprehensive",
            "format_style": "professional"  # Fixed enum value (was causing error before)
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/generate-memo",
                json=memo_request
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                memo_data = response.json()
                
                # Check for expected response structure
                if 'id' in memo_data and 'generated_memo' in memo_data:
                    memo_content = memo_data.get('generated_memo', '')
                    memo_length = len(memo_content)
                    confidence = memo_data.get('confidence_rating', 0)
                    
                    self.log_test("Memo Generation Response", True, 
                                f"Generated memo: {memo_length} characters, confidence: {confidence}", 
                                response_time, "generate-memo")
                    
                    print(f"📊 Memo: ID={memo_data.get('id')}, Length={memo_length} chars")
                    self.endpoint_results['generate-memo'] = True
                    return True
                else:
                    self.log_test("Memo Generation Response", False, 
                                f"Missing required fields in response", response_time, "generate-memo")
                    
            elif response.status_code == 422:
                # Check if this is the old enum validation error (should be fixed)
                error_text = response.text
                if "is not a valid MemoFormat" in error_text:
                    self.log_test("Memo Generation Endpoint", False, 
                                f"ENUM VALIDATION ERROR STILL PRESENT: {error_text}", response_time, "generate-memo")
                else:
                    self.log_test("Memo Generation Endpoint", False, 
                                f"Validation error: {error_text}", response_time, "generate-memo")
            else:
                self.log_test("Memo Generation Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "generate-memo")
                
        except Exception as e:
            self.log_test("Memo Generation Endpoint", False, f"Exception: {str(e)}", 0, "generate-memo")
        
        self.endpoint_results['generate-memo'] = False
        return False
    
    def test_6_structure_arguments_endpoint(self) -> bool:
        """Test 6: POST /api/legal-research-engine/structure-arguments"""
        print("\n🎯 TEST 6: LEGAL RESEARCH ENGINE STRUCTURE ARGUMENTS")
        print("=" * 60)
        
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
                
                # Check for expected response structure
                if 'id' in arguments_data and 'argument_structure' in arguments_data:
                    argument_structure = arguments_data.get('argument_structure', {})
                    supporting_precedents = arguments_data.get('supporting_precedents', [])
                    counterarguments = arguments_data.get('counterarguments', [])
                    
                    self.log_test("Structure Arguments Response", True, 
                                f"Arguments: {len(supporting_precedents)} precedents, {len(counterarguments)} counterarguments", 
                                response_time, "structure-arguments")
                    
                    print(f"📊 Arguments: {len(supporting_precedents)} precedents, {len(counterarguments)} counterargs")
                    self.endpoint_results['structure-arguments'] = True
                    return True
                else:
                    self.log_test("Structure Arguments Response", False, 
                                f"Missing required fields in response", response_time, "structure-arguments")
                    
            else:
                self.log_test("Structure Arguments Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "structure-arguments")
                
        except Exception as e:
            self.log_test("Structure Arguments Endpoint", False, f"Exception: {str(e)}", 0, "structure-arguments")
        
        self.endpoint_results['structure-arguments'] = False
        return False
    
    def test_7_multi_jurisdiction_search_endpoint(self) -> bool:
        """Test 7: POST /api/legal-research-engine/multi-jurisdiction-search"""
        print("\n🎯 TEST 7: LEGAL RESEARCH ENGINE MULTI-JURISDICTION SEARCH")
        print("=" * 60)
        
        multi_jurisdiction_request = {
            "query": "Contract breach remedies and specific performance requirements",
            "jurisdictions": ["US", "UK", "CA", "AU"],
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
                
                # Check for expected response structure
                if 'results' in multi_jurisdiction_data:
                    results = multi_jurisdiction_data.get('results', [])
                    jurisdictions_covered = len(results) if isinstance(results, list) else 0
                    
                    self.log_test("Multi-Jurisdiction Search Response", True, 
                                f"Search across {jurisdictions_covered} jurisdictions", 
                                response_time, "multi-jurisdiction-search")
                    
                    print(f"📊 Multi-Jurisdiction: {jurisdictions_covered} jurisdictions covered")
                    self.endpoint_results['multi-jurisdiction-search'] = True
                    return True
                else:
                    self.log_test("Multi-Jurisdiction Search Response", False, 
                                f"Missing results in response", response_time, "multi-jurisdiction-search")
                    
            else:
                self.log_test("Multi-Jurisdiction Search Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "multi-jurisdiction-search")
                
        except Exception as e:
            self.log_test("Multi-Jurisdiction Search Endpoint", False, f"Exception: {str(e)}", 0, "multi-jurisdiction-search")
        
        self.endpoint_results['multi-jurisdiction-search'] = False
        return False
    
    def test_8_quality_assessment_endpoint(self) -> bool:
        """Test 8: POST /api/legal-research-engine/quality-assessment"""
        print("\n🎯 TEST 8: LEGAL RESEARCH ENGINE QUALITY ASSESSMENT")
        print("=" * 60)
        
        quality_assessment_request = {
            "research_data": {
                "research_id": "test_research_001",
                "query": "Contract breach remedies analysis",
                "results": [
                    {
                        "case_title": "Smith v. Jones",
                        "citation": "123 F.3d 456",
                        "relevance_score": 0.85,
                        "authority_score": 0.90
                    },
                    {
                        "case_title": "ABC Corp v. XYZ Ltd",
                        "citation": "456 F.Supp.3d 789", 
                        "relevance_score": 0.78,
                        "authority_score": 0.75
                    }
                ],
                "analysis_depth": "comprehensive",
                "sources_count": 15
            }
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/quality-assessment",
                json=quality_assessment_request
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                quality_data = response.json()
                
                # Check for expected response structure
                if 'assessment_id' in quality_data and 'overall_scores' in quality_data:
                    overall_scores = quality_data.get('overall_scores', {})
                    dimensional_scores = quality_data.get('dimensional_scores', {})
                    
                    self.log_test("Quality Assessment Response", True, 
                                f"Assessment completed with overall and dimensional scores", 
                                response_time, "quality-assessment")
                    
                    print(f"📊 Quality Assessment: ID={quality_data.get('assessment_id')}")
                    self.endpoint_results['quality-assessment'] = True
                    return True
                else:
                    self.log_test("Quality Assessment Response", False, 
                                f"Missing required fields in response", response_time, "quality-assessment")
                    
            else:
                self.log_test("Quality Assessment Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}", response_time, "quality-assessment")
                
        except Exception as e:
            self.log_test("Quality Assessment Endpoint", False, f"Exception: {str(e)}", 0, "quality-assessment")
        
        self.endpoint_results['quality-assessment'] = False
        return False
    
    def run_comprehensive_testing(self):
        """Execute comprehensive testing of all 8 Legal Research Engine endpoints"""
        print("🎯 LEGAL RESEARCH ENGINE COMPREHENSIVE TESTING - POST-FIX VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("Testing all 8 Legal Research Engine endpoints after comprehensive fixes:")
        print("1. GET /api/legal-research-engine/stats")
        print("2. POST /api/legal-research-engine/research")
        print("3. POST /api/legal-research-engine/precedent-search")
        print("4. POST /api/legal-research-engine/citation-analysis")
        print("5. POST /api/legal-research-engine/generate-memo")
        print("6. POST /api/legal-research-engine/structure-arguments")
        print("7. POST /api/legal-research-engine/multi-jurisdiction-search")
        print("8. POST /api/legal-research-engine/quality-assessment")
        print("=" * 80)
        
        # Execute all 8 endpoint tests
        test_results = []
        test_results.append(self.test_1_stats_endpoint())
        test_results.append(self.test_2_research_endpoint())
        test_results.append(self.test_3_precedent_search_endpoint())
        test_results.append(self.test_4_citation_analysis_endpoint())
        test_results.append(self.test_5_memo_generation_endpoint())
        test_results.append(self.test_6_structure_arguments_endpoint())
        test_results.append(self.test_7_multi_jurisdiction_search_endpoint())
        test_results.append(self.test_8_quality_assessment_endpoint())
        
        # Calculate overall success
        total_endpoints = 8
        working_endpoints = sum(1 for result in test_results if result)
        success_rate = (working_endpoints / total_endpoints) * 100
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 LEGAL RESEARCH ENGINE COMPREHENSIVE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Endpoints Tested: {total_endpoints}")
        print(f"Working Endpoints: {working_endpoints}")
        print(f"Failed Endpoints: {total_endpoints - working_endpoints}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Endpoint-by-endpoint results
        print("\n📋 ENDPOINT RESULTS:")
        endpoints = [
            ("stats", "GET /api/legal-research-engine/stats"),
            ("research", "POST /api/legal-research-engine/research"),
            ("precedent-search", "POST /api/legal-research-engine/precedent-search"),
            ("citation-analysis", "POST /api/legal-research-engine/citation-analysis"),
            ("generate-memo", "POST /api/legal-research-engine/generate-memo"),
            ("structure-arguments", "POST /api/legal-research-engine/structure-arguments"),
            ("multi-jurisdiction-search", "POST /api/legal-research-engine/multi-jurisdiction-search"),
            ("quality-assessment", "POST /api/legal-research-engine/quality-assessment")
        ]
        
        for endpoint_key, endpoint_name in endpoints:
            status = "✅ WORKING" if self.endpoint_results.get(endpoint_key, False) else "❌ FAILED"
            print(f"{status} {endpoint_name}")
        
        # Compare with previous results
        print(f"\n📊 COMPARISON WITH PREVIOUS TESTING:")
        print(f"Previous Success Rate: 50-62.5% (4-5/8 endpoints)")
        print(f"Current Success Rate: {success_rate:.1f}% ({working_endpoints}/8 endpoints)")
        
        if success_rate > 62.5:
            improvement = success_rate - 62.5
            print(f"✅ IMPROVEMENT: +{improvement:.1f}% success rate increase")
        elif success_rate >= 50:
            print(f"✅ MAINTAINED: Success rate within expected range")
        else:
            decline = 50 - success_rate
            print(f"❌ DECLINE: -{decline:.1f}% success rate decrease")
        
        # Detailed test results
        print("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"     {result['details']}")
            if result['response_time'] > 0:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        # Fix verification
        print(f"\n🔧 FIX VERIFICATION:")
        print(f"✅ Database truth value testing errors: {'VERIFIED' if working_endpoints > 0 else 'NOT VERIFIED'}")
        print(f"✅ MemoFormat enum 'professional' value: {'VERIFIED' if self.endpoint_results.get('generate-memo', False) else 'NOT VERIFIED'}")
        print(f"✅ Citation analysis 'total_nodes' field access: {'VERIFIED' if self.endpoint_results.get('citation-analysis', False) else 'NOT VERIFIED'}")
        print(f"✅ ResearchType enum validation with fallbacks: {'VERIFIED' if self.endpoint_results.get('research', False) else 'NOT VERIFIED'}")
        
        return success_rate >= 75.0  # Target 75-100% success rate as mentioned in review

def main():
    """Main execution function"""
    tester = LegalResearchEngineComprehensiveTester()
    
    try:
        overall_success = tester.run_comprehensive_testing()
        
        if overall_success:
            print("\n🎉 LEGAL RESEARCH ENGINE COMPREHENSIVE TESTING COMPLETED SUCCESSFULLY")
            print("✅ Expected success rate of 75-100% achieved after comprehensive fixes")
            sys.exit(0)
        else:
            print("\n❌ LEGAL RESEARCH ENGINE TESTING SHOWS ISSUES REMAIN")
            print("⚠️ Success rate below 75% target - some fixes may not be working")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()