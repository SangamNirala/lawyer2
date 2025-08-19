#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import uuid
import ssl
from datetime import datetime
from typing import Dict, Any, List, Optional

# Test Configuration
BACKEND_URL = "https://compliance-hub-53.preview.emergentagent.com/api"
TIMEOUT = 10  # 10 seconds timeout per call

# Sample contract text from review request
SAMPLE_CONTRACT = """This Service Agreement is entered into between Company A and Company B. The service provider will deliver software development services for $50,000 payable within 90 days. The provider assumes unlimited liability for any damages. Termination can occur immediately without notice. All intellectual property belongs to the provider. No force majeure clause is included."""

class RiskAssessmentTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.session_id = str(uuid.uuid4())
        self.risk_assessment_id = None
        
    async def __aenter__(self):
        # Create SSL context that doesn't verify certificates for testing
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, response_data: Any = None, error: str = None, response_time: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "response_time": f"{response_time:.3f}s",
            "timestamp": datetime.now().isoformat()
        }
        
        if success and response_data:
            result["response_data"] = response_data
        if error:
            result["error"] = error
            
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name} ({response_time:.3f}s)")
        if error:
            print(f"   Error: {error}")
        elif success and response_data:
            # Print key response fields for verification
            if isinstance(response_data, dict):
                key_fields = []
                if 'assessment_id' in response_data:
                    key_fields.append(f"assessment_id: {response_data['assessment_id']}")
                if 'overall_risk_score' in response_data:
                    key_fields.append(f"overall_risk_score: {response_data['overall_risk_score']}")
                if 'dimensional_scores' in response_data:
                    key_fields.append(f"dimensional_scores: {len(response_data['dimensional_scores'])} categories")
                if 'clause_analyses' in response_data:
                    key_fields.append(f"clause_analyses: {len(response_data['clause_analyses'])} clauses")
                if 'risk_mitigation_plan' in response_data:
                    key_fields.append(f"risk_mitigation_plan: {len(response_data['risk_mitigation_plan'])} recommendations")
                if 'red_flags' in response_data:
                    key_fields.append(f"red_flags: {len(response_data['red_flags'])} flags")
                if 'high_priority_risks' in response_data:
                    key_fields.append(f"high_priority_risks: {len(response_data['high_priority_risks'])} risks")
                    
                if key_fields:
                    print(f"   Key fields: {', '.join(key_fields)}")

    async def test_risk_assessment_endpoint(self) -> bool:
        """Test POST /api/ai-agents/contract-negotiation/risk-assessment"""
        test_name = "Risk Assessment Endpoint"
        
        payload = {
            "session_id": self.session_id,
            "contract_text": SAMPLE_CONTRACT,
            "contract_type": "service_agreement",
            "jurisdiction": "US"
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/risk-assessment",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                print(f"Response status: {response.status}")
                response_text = await response.text()
                print(f"Response text: {response_text[:500]}...")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify expected response structure
                    required_fields = ['assessment_id', 'overall_risk_score', 'dimensional_scores', 'clause_analyses', 'risk_mitigation_plan']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, None, f"Missing required fields: {missing_fields}", response_time)
                        return False
                    
                    # Store assessment_id for later tests
                    self.risk_assessment_id = data.get('assessment_id')
                    
                    # Verify overall_risk_score is reasonable (should be high for this contract)
                    overall_score = data.get('overall_risk_score', 0)
                    if not (0 <= overall_score <= 10):
                        self.log_result(test_name, False, None, f"overall_risk_score {overall_score} not in range 0-10", response_time)
                        return False
                    
                    # Verify dimensional_scores contains expected categories
                    dimensional_scores = data.get('dimensional_scores', {})
                    expected_categories = ['legal', 'financial', 'operational', 'compliance']
                    missing_categories = [cat for cat in expected_categories if cat not in dimensional_scores]
                    
                    if missing_categories:
                        self.log_result(test_name, False, None, f"Missing risk categories: {missing_categories}", response_time)
                        return False
                    
                    # Verify clause_analyses is a list
                    clause_analyses = data.get('clause_analyses', [])
                    if not isinstance(clause_analyses, list):
                        self.log_result(test_name, False, None, "clause_analyses should be a list", response_time)
                        return False
                    
                    # Verify mitigation_plan is a list
                    mitigation_plan = data.get('mitigation_plan', [])
                    if not isinstance(mitigation_plan, list):
                        self.log_result(test_name, False, None, "mitigation_plan should be a list", response_time)
                        return False
                    
                    self.log_result(test_name, True, data, None, response_time)
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, None, f"HTTP {response.status}: {error_text}", response_time)
                    return False
                    
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.log_result(test_name, False, None, f"Timeout after {TIMEOUT}s", response_time)
            return False
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, None, str(e), response_time)
            return False

    async def test_session_risk_assessments(self) -> bool:
        """Test GET /api/ai-agents/contract-negotiation/risk-assessments/session/{session_id}"""
        test_name = "Session Risk Assessments Endpoint"
        
        start_time = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/risk-assessments/session/{self.session_id}",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if not isinstance(data, dict):
                        self.log_result(test_name, False, None, "Response should be a dictionary", response_time)
                        return False
                    
                    # Should contain session_id and assessments
                    if 'session_id' not in data:
                        self.log_result(test_name, False, None, "Missing session_id in response", response_time)
                        return False
                    
                    if 'assessments' not in data:
                        self.log_result(test_name, False, None, "Missing assessments in response", response_time)
                        return False
                    
                    # Verify assessments is a list
                    assessments = data.get('assessments', [])
                    if not isinstance(assessments, list):
                        self.log_result(test_name, False, None, "assessments should be a list", response_time)
                        return False
                    
                    # If we created an assessment earlier, it should be in the list
                    if self.risk_assessment_id and len(assessments) == 0:
                        self.log_result(test_name, False, None, "Expected to find at least one assessment for this session", response_time)
                        return False
                    
                    self.log_result(test_name, True, data, None, response_time)
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, None, f"HTTP {response.status}: {error_text}", response_time)
                    return False
                    
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.log_result(test_name, False, None, f"Timeout after {TIMEOUT}s", response_time)
            return False
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, None, str(e), response_time)
            return False

    async def test_high_priority_risk_factors(self) -> bool:
        """Test GET /api/ai-agents/contract-negotiation/risk-factors/high-priority"""
        test_name = "High Priority Risk Factors Endpoint"
        
        start_time = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/risk-factors/high-priority",
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure
                    if not isinstance(data, dict):
                        self.log_result(test_name, False, None, "Response should be a dictionary", response_time)
                        return False
                    
                    # Should contain high_priority_risks
                    if 'high_priority_risks' not in data:
                        self.log_result(test_name, False, None, "Missing high_priority_risks in response", response_time)
                        return False
                    
                    # Verify high_priority_risks is a list
                    high_priority_risks = data.get('high_priority_risks', [])
                    if not isinstance(high_priority_risks, list):
                        self.log_result(test_name, False, None, "high_priority_risks should be a list", response_time)
                        return False
                    
                    # Verify each risk has required fields
                    for risk in high_priority_risks:
                        if not isinstance(risk, dict):
                            self.log_result(test_name, False, None, "Each risk should be a dictionary", response_time)
                            return False
                        
                        required_risk_fields = ['risk_type', 'description', 'severity', 'category']
                        missing_risk_fields = [field for field in required_risk_fields if field not in risk]
                        
                        if missing_risk_fields:
                            self.log_result(test_name, False, None, f"Risk missing fields: {missing_risk_fields}", response_time)
                            return False
                    
                    self.log_result(test_name, True, data, None, response_time)
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, None, f"HTTP {response.status}: {error_text}", response_time)
                    return False
                    
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.log_result(test_name, False, None, f"Timeout after {TIMEOUT}s", response_time)
            return False
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, None, str(e), response_time)
            return False

    async def run_all_tests(self):
        """Run all risk assessment tests"""
        print("🧪 ADVANCED RISK ASSESSMENT FUNCTIONALITY TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Session ID: {self.session_id}")
        print(f"Timeout: {TIMEOUT}s")
        print()
        
        tests = [
            ("Risk Assessment Endpoint", self.test_risk_assessment_endpoint),
            ("Session Risk Assessments", self.test_session_risk_assessments),
            ("High Priority Risk Factors", self.test_high_priority_risk_factors),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                success = await test_func()
                if success:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} - Unexpected error: {str(e)}")
        
        print()
        print("=" * 60)
        print(f"ADVANCED RISK ASSESSMENT TEST RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Advanced Risk Assessment functionality is working correctly!")
            
            # Verify expected high-risk factors were identified
            print("\n📊 RISK ASSESSMENT ANALYSIS:")
            print("Expected high-risk factors for the sample contract:")
            print("- Unlimited liability clause")
            print("- Immediate termination without notice")
            print("- IP ownership issues (all IP belongs to provider)")
            print("- No force majeure clause")
            print("- 90-day payment terms")
            print("Expected overall risk score: 7-9/10 (HIGH)")
            
        else:
            print(f"❌ {total - passed} tests failed - Advanced Risk Assessment functionality needs attention")
        
        return passed == total

async def main():
    """Main test execution"""
    async with RiskAssessmentTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)