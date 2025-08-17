#!/usr/bin/env python3
"""
Legal Research Engine Comprehensive Backend Testing
Testing all 8 Legal Research Engine endpoints for Legal Research Dashboard integration:

1. GET /api/legal-research-engine/stats - Dashboard statistics
2. POST /api/legal-research-engine/research - Main research endpoint 
3. POST /api/legal-research-engine/precedent-search - Precedent search functionality
4. POST /api/legal-research-engine/citation-analysis - Citation network analysis
5. POST /api/legal-research-engine/generate-memo - Research memo generation
6. POST /api/legal-research-engine/structure-arguments - Argument structuring
7. POST /api/legal-research-engine/multi-jurisdiction-search - Multi-jurisdiction comparison
8. POST /api/legal-research-engine/quality-assessment - Research quality assessment
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Use production URL from frontend .env
BASE_URL = "https://mobile-input-test.preview.emergentagent.com"

class LegalResearchEngineTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.timeout = 30  # 30 second timeout for research operations
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str, response_time: float = 0.0):
        """Log test results with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"[{timestamp}] {status}: {test_name}")
        print(f"           Details: {details}")
        if response_time > 0:
            print(f"           Response Time: {response_time:.3f}s")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': timestamp
        })
        
    def test_1_stats_endpoint(self) -> bool:
        """Test GET /api/legal-research-engine/stats - Dashboard statistics"""
        print("\n🎯 TEST 1: Legal Research Engine Stats Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/stats"
        
        try:
            start_time = time.time()
            response = self.session.get(endpoint)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Stats Response: {json.dumps(data, indent=2)}")
                
                # Check for expected dashboard statistics fields
                expected_fields = ['status', 'message']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if not missing_fields:
                    status = data.get('status', '').lower()
                    if status in ['operational', 'degraded', 'unavailable']:
                        self.log_test("Stats Endpoint Structure", True, f"Valid status: {status}, all expected fields present", response_time)
                        return True
                    else:
                        self.log_test("Stats Endpoint Structure", False, f"Invalid status: {status}", response_time)
                        return False
                else:
                    self.log_test("Stats Endpoint Structure", False, f"Missing fields: {missing_fields}", response_time)
                    return False
            else:
                self.log_test("Stats Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Stats Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_2_research_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/research - Main research endpoint"""
        print("\n🎯 TEST 2: Main Research Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/research"
        
        # Realistic legal research query
        payload = {
            "query_text": "Contract breach remedies and damages in commercial disputes involving software licensing agreements",
            "research_type": "comprehensive",
            "jurisdiction": "US",
            "legal_domain": "contract_law",
            "priority": "high",
            "court_level": "federal",
            "case_type": "commercial",
            "legal_issues": ["breach of contract", "damages", "software licensing"],
            "max_results": 20,
            "min_confidence": 0.7,
            "include_analysis": True,
            "cache_results": True,
            "user_context": {
                "case_type": "commercial_dispute",
                "industry": "technology"
            }
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Research Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for expected research result fields
                expected_fields = ['id', 'query_id', 'research_type', 'results']
                present_fields = [field for field in expected_fields if field in data]
                
                if len(present_fields) >= 2:  # At least 2 expected fields present
                    self.log_test("Research Endpoint Structure", True, f"Research response contains {len(present_fields)} expected fields: {present_fields}", response_time)
                    return True
                else:
                    self.log_test("Research Endpoint Structure", False, f"Missing critical fields, only found: {present_fields}", response_time)
                    return False
            else:
                self.log_test("Research Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Research Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_3_precedent_search_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/precedent-search - Precedent search functionality"""
        print("\n🎯 TEST 3: Precedent Search Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/precedent-search"
        
        # Realistic precedent search query
        payload = {
            "query_case": {
                "case_facts": "Software company breached licensing agreement by exceeding user limits",
                "legal_issues": ["breach of contract", "licensing violations"],
                "jurisdiction": "US",
                "case_type": "commercial",
                "industry": "technology"
            },
            "filters": {
                "jurisdiction": "US",
                "court_level": "federal",
                "date_range": {"start": "2015-01-01", "end": "2024-01-01"}
            },
            "max_results": 15,
            "min_similarity": 0.6
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Precedent Search Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for precedent search result structure
                if isinstance(data, dict) and ('precedent_matches' in data or 'results' in data or 'matches' in data):
                    self.log_test("Precedent Search Structure", True, f"Valid precedent search response structure", response_time)
                    return True
                elif isinstance(data, list):
                    self.log_test("Precedent Search Structure", True, f"Precedent search returned {len(data)} results", response_time)
                    return True
                else:
                    self.log_test("Precedent Search Structure", False, f"Unexpected response structure: {type(data)}", response_time)
                    return False
            else:
                self.log_test("Precedent Search Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Precedent Search Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_4_citation_analysis_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/citation-analysis - Citation network analysis"""
        print("\n🎯 TEST 4: Citation Analysis Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/citation-analysis"
        
        # Realistic citation analysis request
        payload = {
            "cases": [
                {
                    "case_id": "case_001",
                    "citation": "Smith v. Tech Corp, 123 F.3d 456 (9th Cir. 2020)",
                    "court": "9th Circuit Court of Appeals",
                    "jurisdiction": "US"
                },
                {
                    "case_id": "case_002", 
                    "citation": "Johnson v. Software Inc, 456 F.Supp.2d 789 (N.D. Cal. 2019)",
                    "court": "Northern District of California",
                    "jurisdiction": "US"
                }
            ],
            "depth": 2,
            "jurisdiction_filter": "US"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Citation Analysis Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for citation network analysis structure
                expected_fields = ['network_id', 'total_nodes', 'total_edges']
                present_fields = [field for field in expected_fields if field in data]
                
                if present_fields or 'citation_network' in data or 'analysis' in data:
                    self.log_test("Citation Analysis Structure", True, f"Valid citation analysis response", response_time)
                    return True
                else:
                    self.log_test("Citation Analysis Structure", False, f"Missing expected citation analysis fields", response_time)
                    return False
            else:
                self.log_test("Citation Analysis Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Citation Analysis Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_5_generate_memo_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/generate-memo - Research memo generation"""
        print("\n🎯 TEST 5: Generate Memo Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/generate-memo"
        
        # Realistic memo generation request
        payload = {
            "memo_data": {
                "research_query": "Analysis of contract breach remedies in software licensing disputes",
                "case_facts": "Client's software licensing agreement was breached when licensee exceeded user limits",
                "legal_issues": ["breach of contract", "damages calculation", "injunctive relief"],
                "jurisdiction": "US",
                "client_name": "TechCorp Solutions",
                "attorney_name": "Jane Smith, Esq."
            },
            "memo_type": "comprehensive",
            "format_style": "professional"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Memo Generation Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for memo generation structure
                expected_fields = ['id', 'generated_memo', 'memo_structure']
                present_fields = [field for field in expected_fields if field in data]
                
                if len(present_fields) >= 1:
                    self.log_test("Memo Generation Structure", True, f"Valid memo response with fields: {present_fields}", response_time)
                    return True
                else:
                    self.log_test("Memo Generation Structure", False, f"Missing expected memo fields", response_time)
                    return False
            else:
                self.log_test("Generate Memo Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Generate Memo Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_6_structure_arguments_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/structure-arguments - Argument structuring"""
        print("\n🎯 TEST 6: Structure Arguments Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/structure-arguments"
        
        # Realistic argument structuring request
        payload = {
            "argument_data": {
                "legal_question": "What are the strongest arguments for damages in a software licensing breach case?",
                "case_facts": "Defendant exceeded licensed user limits by 300%, causing plaintiff financial harm",
                "legal_theory": "breach of contract",
                "jurisdiction": "US",
                "opposing_arguments": ["damages are speculative", "breach was minor"]
            },
            "argument_strength": "strong",
            "include_counterarguments": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Argument Structure Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for argument structure
                expected_fields = ['id', 'argument_structure', 'supporting_precedents']
                present_fields = [field for field in expected_fields if field in data]
                
                if present_fields or 'arguments' in data or 'structure' in data:
                    self.log_test("Argument Structure", True, f"Valid argument structuring response", response_time)
                    return True
                else:
                    self.log_test("Argument Structure", False, f"Missing expected argument structure fields", response_time)
                    return False
            else:
                self.log_test("Structure Arguments Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Structure Arguments Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_7_multi_jurisdiction_search_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/multi-jurisdiction-search - Multi-jurisdiction comparison"""
        print("\n🎯 TEST 7: Multi-Jurisdiction Search Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/multi-jurisdiction-search"
        
        # Realistic multi-jurisdiction search request
        payload = {
            "query": "Software licensing agreement enforceability and breach remedies",
            "jurisdictions": ["US", "UK", "CA", "AU"],
            "legal_domain": "contract_law",
            "comparison_mode": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Multi-Jurisdiction Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for multi-jurisdiction structure
                if isinstance(data, dict) and ('jurisdictions' in data or 'comparison' in data or 'results' in data):
                    self.log_test("Multi-Jurisdiction Structure", True, f"Valid multi-jurisdiction response", response_time)
                    return True
                elif isinstance(data, list):
                    self.log_test("Multi-Jurisdiction Structure", True, f"Multi-jurisdiction returned {len(data)} results", response_time)
                    return True
                else:
                    self.log_test("Multi-Jurisdiction Structure", False, f"Unexpected response structure", response_time)
                    return False
            else:
                self.log_test("Multi-Jurisdiction Search Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Multi-Jurisdiction Search Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_8_quality_assessment_endpoint(self) -> bool:
        """Test POST /api/legal-research-engine/quality-assessment - Research quality assessment"""
        print("\n🎯 TEST 8: Quality Assessment Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research-engine/quality-assessment"
        
        # Realistic quality assessment request
        payload = {
            "research_data": {
                "research_id": "research_12345",
                "query": "Contract breach damages analysis",
                "results_count": 15,
                "sources": ["case_law", "statutes", "secondary_sources"],
                "jurisdiction": "US",
                "legal_domain": "contract_law",
                "confidence_scores": [0.85, 0.78, 0.92, 0.67, 0.89],
                "authority_levels": ["high", "medium", "high", "low", "high"]
            }
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Quality Assessment Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for quality assessment structure
                expected_fields = ['assessment_id', 'overall_scores', 'quality_insights']
                present_fields = [field for field in expected_fields if field in data]
                
                if present_fields or 'quality' in data or 'assessment' in data or 'scores' in data:
                    self.log_test("Quality Assessment Structure", True, f"Valid quality assessment response", response_time)
                    return True
                else:
                    self.log_test("Quality Assessment Structure", False, f"Missing expected quality assessment fields", response_time)
                    return False
            else:
                self.log_test("Quality Assessment Endpoint", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Quality Assessment Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all Legal Research Engine endpoint tests"""
        print("🎯 LEGAL RESEARCH ENGINE COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("Testing 8 Legal Research Engine endpoints for Dashboard integration")
        print("=" * 80)
        
        # Execute all tests
        test_results = []
        test_results.append(("Stats Endpoint", self.test_1_stats_endpoint()))
        test_results.append(("Research Endpoint", self.test_2_research_endpoint()))
        test_results.append(("Precedent Search", self.test_3_precedent_search_endpoint()))
        test_results.append(("Citation Analysis", self.test_4_citation_analysis_endpoint()))
        test_results.append(("Generate Memo", self.test_5_generate_memo_endpoint()))
        test_results.append(("Structure Arguments", self.test_6_structure_arguments_endpoint()))
        test_results.append(("Multi-Jurisdiction Search", self.test_7_multi_jurisdiction_search_endpoint()))
        test_results.append(("Quality Assessment", self.test_8_quality_assessment_endpoint()))
        
        # Calculate results
        total_tests = len(test_results)
        passed_tests = sum(1 for _, success in test_results if success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 LEGAL RESEARCH ENGINE TESTING SUMMARY")
        print("=" * 80)
        
        for test_name, success in test_results:
            status = "✅ WORKING" if success else "❌ FAILING"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal Endpoints Tested: {total_tests}")
        print(f"Working Endpoints: {passed_tests}")
        print(f"Failing Endpoints: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"     {result['details']}")
            if result['response_time'] > 0:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        # Frontend integration assessment
        print(f"\n🎯 FRONTEND INTEGRATION ASSESSMENT:")
        if success_rate >= 80:
            print("✅ EXCELLENT: Legal Research Dashboard can integrate with most endpoints")
        elif success_rate >= 60:
            print("⚠️  GOOD: Legal Research Dashboard can integrate with majority of endpoints")
        elif success_rate >= 40:
            print("⚠️  PARTIAL: Legal Research Dashboard has limited integration capability")
        else:
            print("❌ POOR: Legal Research Dashboard integration will be severely limited")
        
        return success_rate >= 50  # 50% success rate for overall pass

def main():
    """Main execution function"""
    tester = LegalResearchEngineTest()
    
    try:
        overall_success = tester.run_comprehensive_test()
        
        if overall_success:
            print("\n🎉 LEGAL RESEARCH ENGINE TESTING COMPLETED SUCCESSFULLY")
            print("✅ Legal Research Dashboard integration is viable")
            sys.exit(0)
        else:
            print("\n❌ LEGAL RESEARCH ENGINE TESTING FAILED")
            print("⚠️  Legal Research Dashboard integration may have limitations")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()