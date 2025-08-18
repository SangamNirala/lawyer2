#!/usr/bin/env python3
"""
Alternative Legal Research Endpoints Testing
Testing the working legal research endpoints that are available:

1. POST /api/legal-research/search - Legal case search
2. POST /api/legal-research/precedent-analysis - Precedent analysis
3. GET /api/legal-research/results - Get research results
4. GET /api/legal-research/precedent-analyses - Get precedent analyses
5. POST /api/legal-research/contract-insight - Contract legal insights
"""

import requests
import json
import time
import sys
from datetime import datetime

# Use production URL from frontend .env
BASE_URL = "https://strat-engine-ai.preview.emergentagent.com"

class AlternativeLegalResearchTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.timeout = 30
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
    
    def test_legal_case_search(self) -> bool:
        """Test POST /api/legal-research/search - Legal case search"""
        print("\n🎯 TEST 1: Legal Case Search Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research/search"
        
        # Realistic legal case search request
        payload = {
            "query": "contract breach damages software licensing",
            "jurisdiction": "US",
            "case_type": "commercial",
            "date_range": {"start": "2015-01-01", "end": "2024-01-01"},
            "max_results": 10
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Legal Search Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for expected fields
                expected_fields = ['id', 'query', 'cases', 'total_found']
                present_fields = [field for field in expected_fields if field in data]
                
                if len(present_fields) >= 2:
                    self.log_test("Legal Case Search", True, f"Search response contains {len(present_fields)} expected fields: {present_fields}", response_time)
                    return True
                else:
                    self.log_test("Legal Case Search", False, f"Missing critical fields, only found: {present_fields}", response_time)
                    return False
            else:
                self.log_test("Legal Case Search", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Legal Case Search", False, f"Exception: {str(e)}")
            return False
    
    def test_precedent_analysis(self) -> bool:
        """Test POST /api/legal-research/precedent-analysis - Precedent analysis"""
        print("\n🎯 TEST 2: Precedent Analysis Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research/precedent-analysis"
        
        # Realistic precedent analysis request
        payload = {
            "contract_content": "This Software License Agreement is entered into between TechCorp Inc. and Client Company for the licensing of proprietary software with user limitations of 100 concurrent users.",
            "contract_type": "software_license",
            "jurisdiction": "US",
            "analysis_depth": "standard"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Precedent Analysis Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for expected fields
                expected_fields = ['id', 'contract_content', 'similar_cases', 'legal_principles']
                present_fields = [field for field in expected_fields if field in data]
                
                if len(present_fields) >= 2:
                    self.log_test("Precedent Analysis", True, f"Analysis response contains {len(present_fields)} expected fields: {present_fields}", response_time)
                    return True
                else:
                    self.log_test("Precedent Analysis", False, f"Missing critical fields, only found: {present_fields}", response_time)
                    return False
            else:
                self.log_test("Precedent Analysis", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Precedent Analysis", False, f"Exception: {str(e)}")
            return False
    
    def test_get_research_results(self) -> bool:
        """Test GET /api/legal-research/results - Get research results"""
        print("\n🎯 TEST 3: Get Research Results Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research/results"
        
        try:
            start_time = time.time()
            response = self.session.get(endpoint)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Research Results Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for expected fields
                if 'results' in data and 'count' in data:
                    results_count = data.get('count', 0)
                    self.log_test("Get Research Results", True, f"Retrieved {results_count} research results", response_time)
                    return True
                else:
                    self.log_test("Get Research Results", False, f"Missing expected fields (results, count)", response_time)
                    return False
            else:
                self.log_test("Get Research Results", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Get Research Results", False, f"Exception: {str(e)}")
            return False
    
    def test_get_precedent_analyses(self) -> bool:
        """Test GET /api/legal-research/precedent-analyses - Get precedent analyses"""
        print("\n🎯 TEST 4: Get Precedent Analyses Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research/precedent-analyses"
        
        try:
            start_time = time.time()
            response = self.session.get(endpoint)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Precedent Analyses Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check for expected fields
                if 'analyses' in data and 'count' in data:
                    analyses_count = data.get('count', 0)
                    self.log_test("Get Precedent Analyses", True, f"Retrieved {analyses_count} precedent analyses", response_time)
                    return True
                else:
                    self.log_test("Get Precedent Analyses", False, f"Missing expected fields (analyses, count)", response_time)
                    return False
            else:
                self.log_test("Get Precedent Analyses", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Get Precedent Analyses", False, f"Exception: {str(e)}")
            return False
    
    def test_contract_insights(self) -> bool:
        """Test POST /api/legal-research/contract-insight - Contract legal insights"""
        print("\n🎯 TEST 5: Contract Legal Insights Endpoint")
        print("=" * 60)
        
        endpoint = f"{BASE_URL}/api/legal-research/contract-insight"
        
        # Realistic contract insights request
        payload = {
            "contract_content": "This Non-Disclosure Agreement is entered into between Company A and Company B for the protection of confidential information during business negotiations.",
            "contract_type": "NDA",
            "jurisdiction": "US"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=payload)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Contract Insights Response: {json.dumps(data, indent=2)[:500]}...")
                
                # Check if we got some insights back
                if isinstance(data, dict) and len(data) > 0:
                    self.log_test("Contract Legal Insights", True, f"Generated legal insights for contract", response_time)
                    return True
                else:
                    self.log_test("Contract Legal Insights", False, f"Empty or invalid insights response", response_time)
                    return False
            else:
                self.log_test("Contract Legal Insights", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Contract Legal Insights", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all alternative legal research endpoint tests"""
        print("🎯 ALTERNATIVE LEGAL RESEARCH ENDPOINTS TESTING")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("Testing 5 alternative legal research endpoints")
        print("=" * 80)
        
        # Execute all tests
        test_results = []
        test_results.append(("Legal Case Search", self.test_legal_case_search()))
        test_results.append(("Precedent Analysis", self.test_precedent_analysis()))
        test_results.append(("Get Research Results", self.test_get_research_results()))
        test_results.append(("Get Precedent Analyses", self.test_get_precedent_analyses()))
        test_results.append(("Contract Legal Insights", self.test_contract_insights()))
        
        # Calculate results
        total_tests = len(test_results)
        passed_tests = sum(1 for _, success in test_results if success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 ALTERNATIVE LEGAL RESEARCH TESTING SUMMARY")
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
        
        return success_rate >= 50  # 50% success rate for overall pass

def main():
    """Main execution function"""
    tester = AlternativeLegalResearchTest()
    
    try:
        overall_success = tester.run_comprehensive_test()
        
        if overall_success:
            print("\n🎉 ALTERNATIVE LEGAL RESEARCH TESTING COMPLETED SUCCESSFULLY")
            print("✅ Alternative legal research endpoints are available for Dashboard integration")
            sys.exit(0)
        else:
            print("\n❌ ALTERNATIVE LEGAL RESEARCH TESTING FAILED")
            print("⚠️  Limited legal research functionality available")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()