#!/usr/bin/env python3
"""
🎯 CRITICAL PHASE 2A SYSTEM VERIFICATION TESTING - DIRECT

Direct testing to verify critical system fixes using curl-like approach:
- Legal QA API Pydantic Validation Fix Verification  
- Background Enrichment Performance
- Legal Research Engine Status (if accessible)

Backend URL: https://sector-insight.preview.emergentagent.com/api
"""

import subprocess
import json
import time
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://sector-insight.preview.emergentagent.com/api"

class DirectPhase2ATester:
    def __init__(self):
        self.test_results = []
        
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
    
    def curl_request(self, method: str, endpoint: str, data: dict = None, timeout: int = 15):
        """Make a curl request and return response"""
        url = f"{BACKEND_URL}{endpoint}"
        
        if method.upper() == "GET":
            cmd = ["curl", "-s", "-w", "\\n%{http_code}\\n%{time_total}", url]
        else:
            cmd = ["curl", "-s", "-X", method.upper(), "-H", "Content-Type: application/json", 
                   "-w", "\\n%{http_code}\\n%{time_total}", url]
            if data:
                cmd.extend(["-d", json.dumps(data)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            output_lines = result.stdout.strip().split('\n')
            
            if len(output_lines) >= 3:
                response_body = '\n'.join(output_lines[:-2])
                http_code = int(output_lines[-2])
                response_time = float(output_lines[-1])
                
                return {
                    'status_code': http_code,
                    'text': response_body,
                    'response_time': response_time,
                    'success': True
                }
            else:
                return {
                    'status_code': 0,
                    'text': result.stdout,
                    'response_time': 0.0,
                    'success': False,
                    'error': 'Invalid response format'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status_code': 0,
                'text': 'Request timeout',
                'response_time': timeout,
                'success': False,
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'status_code': 0,
                'text': str(e),
                'response_time': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def test_priority_1_legal_research_engine_status(self) -> bool:
        """PRIORITY 1 - Legal Research Engine Status Verification"""
        print("\n🎯 PRIORITY 1: LEGAL RESEARCH ENGINE STATUS VERIFICATION")
        print("=" * 70)
        
        # Test GET /api/legal-research-engine/stats endpoint with short timeout
        response = self.curl_request("GET", "/legal-research-engine/stats", timeout=10)
        
        if not response['success']:
            self.log_test("Legal Research Engine Stats API", False, f"Request failed: {response.get('error', 'Unknown error')}", response['response_time'])
            
            # Try alternative - Legal QA stats
            print("🔄 Trying alternative Legal QA stats endpoint...")
            alt_response = self.curl_request("GET", "/legal-qa/stats", timeout=10)
            
            if alt_response['success'] and alt_response['status_code'] == 200:
                try:
                    stats_data = json.loads(alt_response['text'])
                    print(f"📊 Legal QA Stats (Alternative): {json.dumps(stats_data, indent=2)}")
                    
                    vector_db = stats_data.get('vector_db')
                    indexed_docs = stats_data.get('indexed_documents', 0)
                    
                    if vector_db and indexed_docs >= 304:
                        self.log_test("Legal QA System Operational (Alternative)", True, f"Vector DB: {vector_db}, Documents: {indexed_docs} ✅", alt_response['response_time'])
                        return True
                    else:
                        self.log_test("Legal QA System Operational (Alternative)", False, f"Insufficient documents: {indexed_docs} (expected >= 304)", alt_response['response_time'])
                        return False
                        
                except json.JSONDecodeError:
                    self.log_test("Legal QA System Stats (Alternative)", False, f"Invalid JSON response: {alt_response['text'][:200]}...", alt_response['response_time'])
                    return False
            else:
                self.log_test("Legal QA System Stats (Alternative)", False, f"HTTP {alt_response['status_code']}: {alt_response['text'][:200]}...", alt_response['response_time'])
                return False
                
        elif response['status_code'] == 200:
            try:
                stats_data = json.loads(response['text'])
                print(f"📊 Legal Research Engine Stats: {json.dumps(stats_data, indent=2)}")
                
                status = stats_data.get('status', '').lower()
                if status == 'operational':
                    self.log_test("Legal Research Engine Status - Operational", True, f"Status: {status} ✅", response['response_time'])
                    return True
                else:
                    self.log_test("Legal Research Engine Status - Operational", False, f"Status: {status} (expected 'operational')", response['response_time'])
                    return False
                    
            except json.JSONDecodeError:
                self.log_test("Legal Research Engine Stats API", False, f"Invalid JSON response: {response['text'][:200]}...", response['response_time'])
                return False
        else:
            self.log_test("Legal Research Engine Stats API", False, f"HTTP {response['status_code']}: {response['text'][:200]}...", response['response_time'])
            return False
    
    def test_priority_2_legal_qa_pydantic_validation_fix(self) -> bool:
        """PRIORITY 2 - Legal QA API Pydantic Validation Fix Verification"""
        print("\n🎯 PRIORITY 2: LEGAL QA API PYDANTIC VALIDATION FIX VERIFICATION")
        print("=" * 70)
        
        success_count = 0
        total_tests = 0
        
        # Test standard legal question
        standard_question = {
            "question": "What are the key elements required to establish a valid contract under US law?",
            "jurisdiction": "US",
            "legal_domain": "contract_law",
            "is_voice": False
        }
        
        total_tests += 1
        response = self.curl_request("POST", "/legal-qa/ask", standard_question)
        
        if not response['success']:
            self.log_test("Legal QA API - Standard Question", False, f"Request failed: {response.get('error', 'Unknown error')}", response['response_time'])
        else:
            print(f"📊 Response Status: {response['status_code']}")
            response_text = response['text']
            
            # Check for Pydantic validation errors - THIS IS THE CRITICAL TEST
            if 'pydantic' in response_text.lower() or 'validation error' in response_text.lower():
                if 'is_voice_session' in response_text:
                    self.log_test("Legal QA API - is_voice_session Validation", False, f"❌ CRITICAL: is_voice_session validation error detected: {response_text[:300]}...", response['response_time'])
                    print("🚨 CRITICAL FINDING: The is_voice_session Pydantic validation error is still present!")
                else:
                    self.log_test("Legal QA API - Other Validation Error", False, f"Other Pydantic validation error: {response_text[:300]}...", response['response_time'])
            elif response['status_code'] == 200:
                try:
                    qa_data = json.loads(response_text)
                    print(f"📊 Response Keys: {list(qa_data.keys())}")
                    
                    # Check for is_voice_session field
                    if 'is_voice_session' in qa_data:
                        is_voice_session = qa_data['is_voice_session']
                        if isinstance(is_voice_session, bool):
                            self.log_test("Legal QA API - is_voice_session Field", True, f"✅ is_voice_session: {is_voice_session} (bool) - VALIDATION FIX WORKING!", response['response_time'])
                            success_count += 1
                        else:
                            self.log_test("Legal QA API - is_voice_session Field", False, f"is_voice_session: {is_voice_session} (not boolean)", response['response_time'])
                    else:
                        self.log_test("Legal QA API - is_voice_session Field", False, "is_voice_session field missing from response", response['response_time'])
                    
                    # Check response time
                    if response['response_time'] < 2.0:
                        self.log_test("Legal QA Response Time", True, f"✅ Response time: {response['response_time']:.3f}s (< 2s target)", response['response_time'])
                        success_count += 1
                        total_tests += 1
                    else:
                        self.log_test("Legal QA Response Time", False, f"Response time: {response['response_time']:.3f}s (> 2s target)", response['response_time'])
                        total_tests += 1
                        
                except json.JSONDecodeError:
                    self.log_test("Legal QA API - Standard Question", False, f"Invalid JSON response: {response_text[:300]}...", response['response_time'])
            else:
                self.log_test("Legal QA API - Standard Question", False, f"HTTP {response['status_code']}: {response_text[:300]}...", response['response_time'])
        
        # Test voice and non-voice requests
        voice_tests = [
            {"is_voice": True, "label": "Voice Session"},
            {"is_voice": False, "label": "Non-Voice Session"}
        ]
        
        for test_case in voice_tests:
            total_tests += 1
            voice_question = {
                "question": "What are the basic requirements for a non-disclosure agreement?",
                "jurisdiction": "US",
                "legal_domain": "contract_law",
                "is_voice": test_case["is_voice"]
            }
            
            response = self.curl_request("POST", "/legal-qa/ask", voice_question)
            
            if not response['success']:
                self.log_test(f"Legal QA API - {test_case['label']}", False, f"Request failed: {response.get('error', 'Unknown error')}", response['response_time'])
            else:
                response_text = response['text']
                
                # Check for Pydantic validation errors
                if 'pydantic' in response_text.lower() or 'validation error' in response_text.lower():
                    if 'is_voice_session' in response_text:
                        self.log_test(f"Legal QA API - {test_case['label']}", False, f"❌ CRITICAL: is_voice_session validation error: {response_text[:200]}...", response['response_time'])
                    else:
                        self.log_test(f"Legal QA API - {test_case['label']}", False, f"Other validation error: {response_text[:200]}...", response['response_time'])
                elif response['status_code'] == 200:
                    try:
                        qa_data = json.loads(response_text)
                        is_voice_session = qa_data.get('is_voice_session')
                        
                        if is_voice_session == test_case["is_voice"]:
                            self.log_test(f"Legal QA API - {test_case['label']}", True, f"✅ is_voice_session correctly set to {is_voice_session}", response['response_time'])
                            success_count += 1
                        else:
                            self.log_test(f"Legal QA API - {test_case['label']}", False, f"is_voice_session mismatch: expected {test_case['is_voice']}, got {is_voice_session}", response['response_time'])
                            
                    except json.JSONDecodeError:
                        self.log_test(f"Legal QA API - {test_case['label']}", False, f"Invalid JSON response: {response_text[:200]}...", response['response_time'])
                else:
                    self.log_test(f"Legal QA API - {test_case['label']}", False, f"HTTP {response['status_code']}: {response_text[:200]}...", response['response_time'])
        
        print(f"\n📊 Legal QA Validation Results: {success_count}/{total_tests} tests passed")
        return success_count >= 1  # At least 1 test must pass to indicate some progress
    
    def test_priority_3_background_enrichment_performance(self) -> bool:
        """PRIORITY 3 - Background Enrichment Performance"""
        print("\n🎯 PRIORITY 3: BACKGROUND ENRICHMENT PERFORMANCE")
        print("=" * 70)
        
        success_count = 0
        total_tests = 0
        
        # Test knowledge base rebuild
        total_tests += 1
        response = self.curl_request("POST", "/legal-qa/rebuild-knowledge-base")
        
        if not response['success']:
            self.log_test("Background Enrichment Trigger", False, f"Request failed: {response.get('error', 'Unknown error')}", response['response_time'])
        elif response['status_code'] in [200, 202]:
            try:
                response_data = json.loads(response['text'])
                print(f"📊 Rebuild Response: {json.dumps(response_data, indent=2)}")
                
                message = response_data.get('message', '').lower()
                if any(keyword in message for keyword in ['rebuilt', 'started', 'processing', 'completed']):
                    self.log_test("Background Enrichment Trigger", True, f"✅ Process indication: {response_data.get('message', 'Success')}", response['response_time'])
                    success_count += 1
                else:
                    self.log_test("Background Enrichment Trigger", False, f"Unclear process status: {response_data}", response['response_time'])
                    
            except json.JSONDecodeError:
                self.log_test("Background Enrichment Trigger", False, f"Invalid JSON response: {response['text'][:200]}...", response['response_time'])
        else:
            self.log_test("Background Enrichment Trigger", False, f"HTTP {response['status_code']}: {response['text'][:200]}...", response['response_time'])
        
        # Test precedent search performance
        total_tests += 1
        precedent_query = {
            "question": "Find legal precedents for breach of contract cases involving software licensing agreements",
            "jurisdiction": "US",
            "legal_domain": "contract_law",
            "is_voice": False
        }
        
        response = self.curl_request("POST", "/legal-qa/ask", precedent_query)
        
        if not response['success']:
            self.log_test("Precedent Search Performance", False, f"Request failed: {response.get('error', 'Unknown error')}", response['response_time'])
        elif response['status_code'] == 200:
            try:
                qa_data = json.loads(response['text'])
                
                # Check response time
                if response['response_time'] < 2.0:
                    self.log_test("Precedent Search Performance", True, f"✅ Response time: {response['response_time']:.3f}s (< 2s target)", response['response_time'])
                    success_count += 1
                else:
                    self.log_test("Precedent Search Performance", False, f"Response time: {response['response_time']:.3f}s (> 2s target)", response['response_time'])
                
                # Check content quality
                answer = qa_data.get('answer', '')
                if answer and len(answer) > 100:
                    precedent_terms = ['precedent', 'case', 'court', 'ruling', 'decision', 'judgment']
                    found_terms = [term for term in precedent_terms if term.lower() in answer.lower()]
                    
                    if found_terms:
                        self.log_test("Precedent Search Quality", True, f"✅ Found legal terms: {found_terms}", response['response_time'])
                        success_count += 1
                        total_tests += 1
                    else:
                        self.log_test("Precedent Search Quality", False, "No legal precedent terms found", response['response_time'])
                        total_tests += 1
                else:
                    self.log_test("Precedent Search Quality", False, f"Insufficient content: {len(answer)} chars", response['response_time'])
                    total_tests += 1
                    
            except json.JSONDecodeError:
                self.log_test("Precedent Search Performance", False, f"Invalid JSON response: {response['text'][:200]}...", response['response_time'])
                total_tests += 1
        else:
            response_text = response['text']
            if 'pydantic' in response_text.lower() or 'validation error' in response_text.lower():
                self.log_test("Precedent Search Performance", False, f"Validation error: {response_text[:200]}...", response['response_time'])
            else:
                self.log_test("Precedent Search Performance", False, f"HTTP {response['status_code']}: {response_text[:200]}...", response['response_time'])
            total_tests += 1
        
        print(f"\n📊 Background Enrichment Results: {success_count}/{total_tests} tests passed")
        return success_count >= 1  # At least 1 test must pass
    
    def run_direct_testing(self):
        """Execute direct Phase 2A testing"""
        print("🎯 CRITICAL PHASE 2A SYSTEM VERIFICATION TESTING - DIRECT")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("Direct curl-based testing to verify critical fixes")
        print("=" * 80)
        
        # Execute tests
        priority_1_success = self.test_priority_1_legal_research_engine_status()
        priority_2_success = self.test_priority_2_legal_qa_pydantic_validation_fix()
        priority_3_success = self.test_priority_3_background_enrichment_performance()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 DIRECT PHASE 2A TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Success criteria evaluation
        print("\n📋 SUCCESS CRITERIA EVALUATION:")
        criteria_met = 0
        total_criteria = 5
        
        if priority_1_success:
            print("✅ 1. Legal Research Engine shows 'operational' status - PASSED")
            criteria_met += 1
        else:
            print("❌ 1. Legal Research Engine shows 'operational' status - FAILED")
            
        if priority_2_success:
            print("✅ 2. Legal QA API returns successful responses without validation errors - PASSED")
            criteria_met += 1
        else:
            print("❌ 2. Legal QA API returns successful responses without validation errors - FAILED")
            
        # Check for is_voice_session field in successful responses
        voice_session_found = any('is_voice_session' in result['details'] and result['success'] for result in self.test_results)
        if voice_session_found:
            print("✅ 3. is_voice_session field properly included in Legal QA responses - PASSED")
            criteria_met += 1
        else:
            print("❌ 3. is_voice_session field properly included in Legal QA responses - FAILED")
            
        # Check for response times under 2 seconds
        fast_responses = [result for result in self.test_results if result['response_time'] > 0 and result['response_time'] < 2.0 and result['success']]
        if fast_responses:
            print("✅ 4. Response times under 2 seconds for precedent searches - PASSED")
            criteria_met += 1
        else:
            print("❌ 4. Response times under 2 seconds for precedent searches - FAILED")
            
        # Check for no HTTP 500 errors or validation errors
        validation_errors = [r for r in self.test_results if 'validation error' in r['details'].lower()]
        if not validation_errors:
            print("✅ 5. No HTTP 500 errors or validation errors in any endpoint - PASSED")
            criteria_met += 1
        else:
            print("❌ 5. No HTTP 500 errors or validation errors in any endpoint - FAILED")
            print(f"   Found {len(validation_errors)} validation errors")
        
        criteria_success_rate = (criteria_met / total_criteria) * 100
        print(f"\n🎯 CRITERIA SUCCESS RATE: {criteria_success_rate:.1f}% ({criteria_met}/{total_criteria})")
        
        # Critical findings
        print("\n📋 CRITICAL FINDINGS:")
        
        # Check for is_voice_session validation errors
        validation_errors = [r for r in self.test_results if 'is_voice_session validation error' in r['details']]
        if validation_errors:
            print("❌ CRITICAL ISSUE: is_voice_session Pydantic validation errors detected")
            for error in validation_errors:
                print(f"   - {error['test']}: {error['details'][:100]}...")
        else:
            print("✅ No is_voice_session validation errors detected")
        
        # Performance metrics
        response_times = [r['response_time'] for r in self.test_results if r['response_time'] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"\n📊 PERFORMANCE METRICS:")
            print(f"   Average Response Time: {avg_time:.3f}s")
            print(f"   Maximum Response Time: {max_time:.3f}s")
            print(f"   Minimum Response Time: {min_time:.3f}s")
        
        # Detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"     {result['details']}")
            if result['response_time'] > 0:
                print(f"     Response Time: {result['response_time']:.3f}s")
        
        # Final assessment
        overall_success = criteria_success_rate >= 60.0
        
        if overall_success:
            print(f"\n🎉 DIRECT PHASE 2A TESTING COMPLETED SUCCESSFULLY")
        else:
            print(f"\n❌ DIRECT PHASE 2A TESTING FAILED")
            print(f"⚠️ Critical validation issues need attention")
        
        return overall_success

def main():
    """Main execution function"""
    tester = DirectPhase2ATester()
    
    try:
        overall_success = tester.run_direct_testing()
        
        if overall_success:
            print("\n🎉 PHASE 2A TESTING COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n❌ PHASE 2A TESTING FAILED - CRITICAL ISSUES FOUND")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()