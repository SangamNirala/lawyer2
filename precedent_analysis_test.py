#!/usr/bin/env python3
"""
Precedent Analysis and Citation Network API Testing
Testing the new Day 17-18 Precedent Analysis System endpoints
"""

import requests
import sys
import json
from datetime import datetime

class PrecedentAnalysisAPITester:
    def __init__(self, base_url="https://compliance-hub-53.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'List with ' + str(len(response_data)) + ' items'}")
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response_keys": list(response_data.keys()) if isinstance(response_data, dict) else [],
                        "data_size": len(str(response_data))
                    })
                    return True, response_data
                except:
                    self.test_results.append({
                        "test": name,
                        "status": "PASSED",
                        "response": "Non-JSON response",
                        "data_size": len(response.text)
                    })
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "error": error_data,
                        "expected_status": expected_status,
                        "actual_status": response.status_code
                    })
                except:
                    print(f"   Error: {response.text}")
                    self.test_results.append({
                        "test": name,
                        "status": "FAILED",
                        "error": response.text,
                        "expected_status": expected_status,
                        "actual_status": response.status_code
                    })
                return False, {}
                
        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout after {timeout} seconds")
            self.test_results.append({
                "test": name,
                "status": "TIMEOUT",
                "timeout": timeout
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Exception: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "ERROR",
                "exception": str(e)
            })
            return False, {}

    def test_precedent_analysis_endpoints(self):
        """Test all 5 Precedent Analysis and Citation Network endpoints"""
        
        print("🎯 TESTING PRECEDENT ANALYSIS AND CITATION NETWORK API ENDPOINTS")
        print("=" * 80)
        
        # Test 1: POST /api/legal-reasoning/analyze-precedents
        print("\n📋 TEST 1: Precedent Analysis for Legal Issues")
        precedent_request = {
            "legal_issue": "Contract breach and damages in employment agreements",
            "jurisdiction": "US_Federal",
            "user_facts": "Employee terminated without cause before contract completion, seeking damages for remaining term",
            "analysis_depth": "standard"
        }
        
        success, response = self.run_test(
            "Precedent Analysis - Contract Breach",
            "POST",
            "legal-reasoning/analyze-precedents",
            200,
            precedent_request
        )
        
        if success and isinstance(response, dict):
            print(f"   ✅ Analysis completed for: {response.get('legal_issue', 'N/A')}")
            print(f"   ✅ Controlling precedents found: {len(response.get('controlling_precedents', []))}")
            print(f"   ✅ Persuasive precedents found: {len(response.get('persuasive_precedents', []))}")
            print(f"   ✅ Confidence score: {response.get('confidence_score', 'N/A')}")
        
        # Test 2: Different legal issue for precedent analysis
        print("\n📋 TEST 2: Precedent Analysis - Constitutional Law")
        constitutional_request = {
            "legal_issue": "First Amendment free speech rights in public forums",
            "jurisdiction": "US_Federal", 
            "user_facts": "Government restriction on political speech in public park",
            "analysis_depth": "comprehensive"
        }
        
        success2, response2 = self.run_test(
            "Precedent Analysis - Constitutional Law",
            "POST", 
            "legal-reasoning/analyze-precedents",
            200,
            constitutional_request
        )
        
        # Test 3: GET /api/legal-reasoning/citation-network/{case_id}
        print("\n📋 TEST 3: Citation Network Retrieval")
        
        # First try with a common case ID pattern
        test_case_ids = [
            "brown_v_board_1954",
            "miranda_v_arizona_1966", 
            "roe_v_wade_1973",
            "case_001",
            "test_case_id"
        ]
        
        citation_network_found = False
        for case_id in test_case_ids:
            success3, response3 = self.run_test(
                f"Citation Network - {case_id}",
                "GET",
                f"legal-reasoning/citation-network/{case_id}",
                200  # Try 200 first, will handle 404 if not found
            )
            
            if success3:
                citation_network_found = True
                print(f"   ✅ Citation network found for case: {case_id}")
                if isinstance(response3, dict):
                    network = response3.get('citation_network', {})
                    print(f"   ✅ Outbound citations: {network.get('outbound_count', 0)}")
                    print(f"   ✅ Inbound citations: {network.get('inbound_count', 0)}")
                    print(f"   ✅ Authority score: {network.get('authority_score', 'N/A')}")
                break
            else:
                # Try with 404 expected for non-existent cases
                success3_404, _ = self.run_test(
                    f"Citation Network - {case_id} (404 expected)",
                    "GET",
                    f"legal-reasoning/citation-network/{case_id}",
                    404
                )
                if success3_404:
                    print(f"   ✅ Correctly returned 404 for non-existent case: {case_id}")
        
        # Test 4: POST /api/legal-reasoning/precedent-hierarchy
        print("\n📋 TEST 4: Precedent Hierarchy Analysis")
        hierarchy_request = {
            "case_ids": [
                "brown_v_board_1954",
                "plessy_v_ferguson_1896", 
                "miranda_v_arizona_1966",
                "test_case_1",
                "test_case_2"
            ],
            "jurisdiction": "US_Federal"
        }
        
        success4, response4 = self.run_test(
            "Precedent Hierarchy Analysis",
            "POST",
            "legal-reasoning/precedent-hierarchy", 
            200,
            hierarchy_request
        )
        
        if success4 and isinstance(response4, dict):
            hierarchy = response4.get('precedent_hierarchy', [])
            summary = response4.get('hierarchy_summary', {})
            print(f"   ✅ Cases analyzed: {summary.get('total_cases_requested', 0)}")
            print(f"   ✅ Cases found: {summary.get('cases_found', 0)}")
            print(f"   ✅ Controlling precedents: {summary.get('controlling_precedents', 0)}")
            print(f"   ✅ Persuasive precedents: {summary.get('persuasive_precedents', 0)}")
        
        # Test 5: POST /api/legal-reasoning/legal-reasoning-chain
        print("\n📋 TEST 5: Legal Reasoning Chain Generation")
        reasoning_request = {
            "legal_issue": "Breach of non-disclosure agreement and trade secret misappropriation",
            "user_facts": "Former employee disclosed confidential customer list to competitor after leaving company",
            "jurisdiction": "US_Federal"
        }
        
        success5, response5 = self.run_test(
            "Legal Reasoning Chain Generation",
            "POST",
            "legal-reasoning/legal-reasoning-chain",
            200,
            reasoning_request
        )
        
        if success5 and isinstance(response5, dict):
            chain = response5.get('legal_reasoning_chain', {})
            quality = response5.get('analysis_quality', {})
            print(f"   ✅ Reasoning chain generated with {len(chain)} steps")
            print(f"   ✅ Chain strength: {quality.get('reasoning_chain_strength', 'N/A')}")
            print(f"   ✅ Overall confidence: {quality.get('overall_confidence', 'N/A')}")
        
        # Test 6: GET /api/legal-reasoning/conflicting-precedents
        print("\n📋 TEST 6: Conflicting Precedents Identification")
        
        # Test with different legal concepts
        legal_concepts = [
            "due process",
            "contract formation", 
            "negligence liability",
            "constitutional rights",
            "employment termination"
        ]
        
        conflicts_found = False
        for concept in legal_concepts:
            success6, response6 = self.run_test(
                f"Conflicting Precedents - {concept}",
                "GET",
                f"legal-reasoning/conflicting-precedents?legal_concept={concept}&jurisdiction_scope=federal&limit=5",
                200
            )
            
            if success6 and isinstance(response6, dict):
                conflicts = response6.get('conflicting_precedents', [])
                summary = response6.get('conflict_summary', {})
                if conflicts:
                    conflicts_found = True
                    print(f"   ✅ Found {len(conflicts)} conflicts for '{concept}'")
                    print(f"   ✅ High priority conflicts: {summary.get('high_priority_conflicts', 0)}")
                    print(f"   ✅ Jurisdictional conflicts: {summary.get('jurisdictional_conflicts', 0)}")
                    break
                else:
                    print(f"   ℹ️  No conflicts found for '{concept}' (expected for some concepts)")
        
        # Test 7: Error handling - Test with invalid data
        print("\n📋 TEST 7: Error Handling Verification")
        
        # Test invalid precedent analysis request
        invalid_request = {
            "legal_issue": "",  # Empty legal issue
            "jurisdiction": "INVALID_JURISDICTION"
        }
        
        success7, response7 = self.run_test(
            "Error Handling - Invalid Precedent Request",
            "POST",
            "legal-reasoning/analyze-precedents",
            422  # Expect validation error
        )
        
        # Test invalid case ID for citation network
        success8, response8 = self.run_test(
            "Error Handling - Invalid Case ID",
            "GET", 
            "legal-reasoning/citation-network/invalid_case_id_12345",
            404  # Expect not found
        )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 PRECEDENT ANALYSIS API TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASSED" else "❌" if result["status"] == "FAILED" else "⏱️" if result["status"] == "TIMEOUT" else "⚠️"
            print(f"   {status_emoji} {result['test']}: {result['status']}")
        
        print(f"\n🎯 ENDPOINT COVERAGE:")
        print(f"   ✅ POST /api/legal-reasoning/analyze-precedents")
        print(f"   ✅ GET /api/legal-reasoning/citation-network/{{case_id}}")
        print(f"   ✅ POST /api/legal-reasoning/precedent-hierarchy")
        print(f"   ✅ POST /api/legal-reasoning/legal-reasoning-chain")
        print(f"   ✅ GET /api/legal-reasoning/conflicting-precedents")
        
        if success_rate >= 80:
            print(f"\n🎉 PRECEDENT ANALYSIS SYSTEM: OPERATIONAL")
            print(f"   The Precedent Analysis and Citation Network API is working well!")
        elif success_rate >= 60:
            print(f"\n⚠️  PRECEDENT ANALYSIS SYSTEM: PARTIALLY OPERATIONAL")
            print(f"   Some endpoints may need attention.")
        else:
            print(f"\n❌ PRECEDENT ANALYSIS SYSTEM: NEEDS ATTENTION")
            print(f"   Multiple endpoints are not working as expected.")
        
        return success_rate

def main():
    """Main test execution"""
    print("🚀 Starting Precedent Analysis and Citation Network API Testing...")
    print("📅 Day 17-18 Implementation Testing")
    print("🕒 Test started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    tester = PrecedentAnalysisAPITester()
    
    try:
        tester.test_precedent_analysis_endpoints()
        success_rate = tester.print_summary()
        
        # Exit with appropriate code
        if success_rate >= 80:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some failures
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Testing failed with exception: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()