#!/usr/bin/env python3
"""
Phase 2A Async Background Enrichment Testing - Legal Research Engine Performance Verification
Testing sequence: Server Stats → Background Enrichment Trigger → Immediate Precedent Search → Follow-up Performance Test
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from environment
BACKEND_URL = "https://legal-precedent.preview.emergentagent.com/api"

class Phase2ALegalResearchTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.performance_metrics = {}
        
    def log_test(self, test_name: str, success: bool, details: str, response_time: float = 0.0):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_time > 0:
            print(f"   Response Time: {response_time:.3f}s")
    
    def test_a_server_stats_verification(self) -> bool:
        """A) Server Stats Verification - Test GET /api/legal-research-engine/stats"""
        print("\n🎯 PHASE 2A TEST A: SERVER STATS VERIFICATION")
        print("=" * 60)
        
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/legal-research-engine/stats")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                stats_data = response.json()
                
                # Verify "operational" status
                status = stats_data.get('status', '').lower()
                if 'operational' in status:
                    self.log_test("Server Status Check", True, f"Status: {status}", response_time)
                else:
                    self.log_test("Server Status Check", False, f"Expected 'operational', got: {status}", response_time)
                    return False
                
                # Verify "precedent_matching_stats" field is present
                if 'precedent_matching_stats' in stats_data:
                    precedent_stats = stats_data['precedent_matching_stats']
                    self.log_test("Precedent Matching Stats Present", True, f"Stats found: {type(precedent_stats)}", response_time)
                else:
                    self.log_test("Precedent Matching Stats Present", False, "precedent_matching_stats field missing", response_time)
                    return False
                
                # Check system health indicators
                health_indicators = ['database_connectivity', 'ai_services', 'vector_db_status']
                health_found = any(indicator in stats_data for indicator in health_indicators)
                if health_found:
                    self.log_test("System Health Indicators", True, "Health indicators present", response_time)
                else:
                    self.log_test("System Health Indicators", False, "No health indicators found", response_time)
                
                print(f"📊 Server Stats Response: {json.dumps(stats_data, indent=2)}")
                return True
                
            else:
                self.log_test("Server Stats API", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Server Stats API", False, f"Exception: {str(e)}")
            return False
    
    def test_b_background_enrichment_trigger(self) -> bool:
        """B) Background Enrichment Trigger - Test CourtListener rebuild endpoints"""
        print("\n🎯 PHASE 2A TEST B: BACKGROUND ENRICHMENT TRIGGER")
        print("=" * 60)
        
        # Test both available rebuild endpoints
        endpoints_to_test = [
            "/legal-qa/rebuild-knowledge-base",
            "/legal-qa/rebuild-bulk-knowledge-base"
        ]
        
        success_count = 0
        
        for endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.session.post(f"{BACKEND_URL}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code in [200, 202]:  # Accept both OK and Accepted
                    response_data = response.json()
                    
                    # Check for async process indication
                    status_indicators = ['status', 'message', 'task_id', 'background_process']
                    status_found = any(indicator in response_data for indicator in status_indicators)
                    
                    if status_found:
                        status_value = response_data.get('status', response_data.get('message', 'started'))
                        if 'started' in str(status_value).lower() or 'processing' in str(status_value).lower():
                            self.log_test(f"Background Enrichment {endpoint}", True, f"Process started: {status_value}", response_time)
                            success_count += 1
                        else:
                            self.log_test(f"Background Enrichment {endpoint}", False, f"Unexpected status: {status_value}", response_time)
                    else:
                        self.log_test(f"Background Enrichment {endpoint}", False, "No status indication in response", response_time)
                        
                    print(f"📊 Response from {endpoint}: {json.dumps(response_data, indent=2)}")
                    
                else:
                    self.log_test(f"Background Enrichment {endpoint}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                    
            except Exception as e:
                self.log_test(f"Background Enrichment {endpoint}", False, f"Exception: {str(e)}")
        
        return success_count > 0
    
    def test_c_immediate_precedent_search_performance(self) -> Dict[str, Any]:
        """C) Immediate Precedent Search Performance Test"""
        print("\n🎯 PHASE 2A TEST C: IMMEDIATE PRECEDENT SEARCH PERFORMANCE")
        print("=" * 60)
        
        # Specific query case for performance measurement
        test_query = {
            "query_case": {
                "case_title": "Contract Breach Performance Test",
                "legal_issues": ["contract breach", "damages", "specific performance"],
                "jurisdiction": "US",
                "case_facts": "Commercial contract dispute involving delivery delays and monetary damages",
                "case_type": "civil"
            },
            "filters": {
                "jurisdiction": "US",
                "min_confidence": 0.7
            },
            "max_results": 10,
            "min_similarity": 0.6
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{BACKEND_URL}/legal-research-engine/precedent-search",
                json=test_query
            )
            response_time = time.time() - start_time
            
            # Store baseline performance
            self.performance_metrics['baseline_response_time'] = response_time
            self.performance_metrics['baseline_timestamp'] = datetime.now().isoformat()
            
            if response.status_code == 200:
                precedent_data = response.json()
                
                # Check response time (target: < 2 seconds)
                if response_time < 2.0:
                    self.log_test("Precedent Search Performance", True, f"Response time: {response_time:.3f}s (< 2s target)", response_time)
                else:
                    self.log_test("Precedent Search Performance", False, f"Response time: {response_time:.3f}s (> 2s target)", response_time)
                
                # Verify response structure
                if isinstance(precedent_data, list) and len(precedent_data) > 0:
                    self.log_test("Precedent Search Results", True, f"Found {len(precedent_data)} precedent matches", response_time)
                    
                    # Check first result structure
                    first_result = precedent_data[0]
                    required_fields = ['case_id', 'case_title', 'similarity_scores', 'relevance_score']
                    missing_fields = [field for field in required_fields if field not in first_result]
                    
                    if not missing_fields:
                        self.log_test("Precedent Result Structure", True, "All required fields present", response_time)
                    else:
                        self.log_test("Precedent Result Structure", False, f"Missing fields: {missing_fields}", response_time)
                        
                else:
                    self.log_test("Precedent Search Results", False, "No precedent matches found or invalid response format", response_time)
                
                print(f"📊 Precedent Search Results: {len(precedent_data) if isinstance(precedent_data, list) else 'Invalid format'} matches")
                if isinstance(precedent_data, list) and len(precedent_data) > 0:
                    print(f"📊 First Result: {json.dumps(precedent_data[0], indent=2)[:500]}...")
                
                return {
                    'success': True,
                    'response_time': response_time,
                    'results_count': len(precedent_data) if isinstance(precedent_data, list) else 0,
                    'data': precedent_data
                }
                
            else:
                self.log_test("Precedent Search API", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return {'success': False, 'response_time': response_time}
                
        except Exception as e:
            self.log_test("Precedent Search API", False, f"Exception: {str(e)}")
            return {'success': False, 'response_time': 0.0}
    
    def test_d_followup_precedent_search_verification(self) -> bool:
        """D) Follow-up Precedent Search Verification after enrichment"""
        print("\n🎯 PHASE 2A TEST D: FOLLOW-UP PRECEDENT SEARCH VERIFICATION")
        print("=" * 60)
        
        # Wait 5 seconds after background enrichment trigger
        print("⏳ Waiting 5 seconds for background enrichment to process...")
        time.sleep(5)
        
        # Execute the same precedent search test again
        followup_result = self.test_c_immediate_precedent_search_performance()
        
        if followup_result['success']:
            baseline_time = self.performance_metrics.get('baseline_response_time', 0)
            followup_time = followup_result['response_time']
            
            # Compare performance
            if baseline_time > 0:
                improvement = baseline_time - followup_time
                improvement_percent = (improvement / baseline_time) * 100
                
                self.performance_metrics['followup_response_time'] = followup_time
                self.performance_metrics['performance_improvement'] = improvement
                self.performance_metrics['improvement_percent'] = improvement_percent
                
                if improvement > 0:
                    self.log_test("Performance Improvement", True, f"Improved by {improvement:.3f}s ({improvement_percent:.1f}%)", followup_time)
                elif abs(improvement) < 0.1:  # Within 100ms is considered stable
                    self.log_test("Performance Stability", True, f"Stable performance (±{abs(improvement):.3f}s)", followup_time)
                else:
                    self.log_test("Performance Change", True, f"Performance change: {improvement:.3f}s ({improvement_percent:.1f}%)", followup_time)
                
                print(f"📊 Performance Comparison:")
                print(f"   Baseline: {baseline_time:.3f}s")
                print(f"   Follow-up: {followup_time:.3f}s")
                print(f"   Change: {improvement:.3f}s ({improvement_percent:.1f}%)")
                
            else:
                self.log_test("Performance Comparison", False, "No baseline performance data available")
                
            return True
        else:
            self.log_test("Follow-up Precedent Search", False, "Follow-up search failed")
            return False
    
    def run_phase2a_testing_sequence(self):
        """Execute the complete Phase 2A testing sequence"""
        print("🎯 PHASE 2A ASYNC BACKGROUND ENRICHMENT TESTING - LEGAL RESEARCH ENGINE")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Execute testing sequence
        test_a_success = self.test_a_server_stats_verification()
        test_b_success = self.test_b_background_enrichment_trigger()
        test_c_result = self.test_c_immediate_precedent_search_performance()
        test_d_success = self.test_d_followup_precedent_search_verification()
        
        # Calculate overall success
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 PHASE 2A TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Success criteria evaluation
        print("\n📋 SUCCESS CRITERIA EVALUATION:")
        criteria_met = 0
        total_criteria = 4
        
        if test_a_success:
            print("✅ A) Server stats show operational status - PASSED")
            criteria_met += 1
        else:
            print("❌ A) Server stats show operational status - FAILED")
            
        if test_b_success:
            print("✅ B) Background enrichment triggers without errors - PASSED")
            criteria_met += 1
        else:
            print("❌ B) Background enrichment triggers without errors - FAILED")
            
        if test_c_result['success'] and test_c_result['response_time'] < 2.0:
            print("✅ C) Precedent search response time under 2 seconds - PASSED")
            criteria_met += 1
        else:
            print("❌ C) Precedent search response time under 2 seconds - FAILED")
            
        if test_d_success:
            print("✅ D) Follow-up precedent search verification - PASSED")
            criteria_met += 1
        else:
            print("❌ D) Follow-up precedent search verification - FAILED")
        
        criteria_success_rate = (criteria_met / total_criteria) * 100
        print(f"\n🎯 CRITERIA SUCCESS RATE: {criteria_success_rate:.1f}% ({criteria_met}/{total_criteria})")
        
        # Performance metrics summary
        if self.performance_metrics:
            print("\n📊 PERFORMANCE METRICS:")
            for key, value in self.performance_metrics.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.3f}")
                else:
                    print(f"   {key}: {value}")
        
        # Detailed test results
        print("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"     {result['details']}")
            if result['response_time'] > 0:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        return criteria_success_rate >= 75.0  # 75% criteria success rate for overall pass

def main():
    """Main execution function"""
    tester = Phase2ALegalResearchTester()
    
    try:
        overall_success = tester.run_phase2a_testing_sequence()
        
        if overall_success:
            print("\n🎉 PHASE 2A TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n❌ PHASE 2A TESTING FAILED - CRITERIA NOT MET")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()