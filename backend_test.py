#!/usr/bin/env python3
"""
Backend Testing Suite for Step 2 Regulatory Compliance Focus
Enhanced Contract Negotiation Agent - Regulatory Compliance Testing

Tests all 6 regulatory compliance endpoints:
1. POST /api/ai-agents/contract-negotiation/regulatory-compliance
2. GET /api/ai-agents/contract-negotiation/regulatory-compliance/{compliance_id}
3. GET /api/ai-agents/contract-negotiation/regulatory-compliance/session/{session_id}
4. GET /api/ai-agents/contract-negotiation/regulatory-frameworks
5. POST /api/ai-agents/contract-negotiation/compliance-gap-analysis
6. GET /api/ai-agents/contract-negotiation/industry-compliance/{industry_type}
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BACKEND_URL = "https://compliance-hub-53.preview.emergentagent.com/api"
TEST_SESSION_ID = "test-session-regulatory-001"

class RegulatoryComplianceTestSuite:
    def __init__(self):
        self.session = None
        self.results = []
        self.compliance_id = None
        
    async def setup(self):
        """Setup test session"""
        import ssl
        # Create SSL context that doesn't verify certificates for testing
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"Content-Type": "application/json"},
            connector=connector
        )
        print("🔧 Test session initialized")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("🧹 Test session cleaned up")
        
    def log_result(self, test_name: str, success: bool, response_time: float, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "response_time": response_time,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.results.append(result)
        print(f"{status} {test_name} ({response_time:.3f}s) - {details}")
        
    async def test_regulatory_compliance_assessment(self):
        """Test POST /api/ai-agents/contract-negotiation/regulatory-compliance"""
        test_name = "Regulatory Compliance Assessment"
        start_time = time.time()
        
        try:
            # Test payload from review request
            payload = {
                "session_id": TEST_SESSION_ID,
                "contract_text": "This service agreement governs the relationship between parties for software development services. Payment terms are Net 30 days. The contractor will provide web development services for $50,000. Data processing activities include customer information handling.",
                "target_frameworks": ["gdpr", "hipaa"],
                "industry_type": "healthcare",
                "jurisdiction": "US",
                "data_processing_activities": ["customer_data", "health_information"],
                "health_data_involved": True
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/regulatory-compliance",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = [
                        "compliance_id", "session_id", "overall_compliance_score",
                        "compliance_level", "framework_assessments", "compliance_gaps"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_result(test_name, False, response_time, 
                                      f"Missing required fields: {missing_fields}")
                        return
                    
                    # Store compliance_id for later tests
                    self.compliance_id = data["compliance_id"]
                    
                    # Validate framework assessments
                    framework_assessments = data.get("framework_assessments", {})
                    expected_frameworks = ["gdpr", "hipaa"]
                    
                    for framework in expected_frameworks:
                        if framework not in framework_assessments:
                            self.log_result(test_name, False, response_time,
                                          f"Missing framework assessment: {framework}")
                            return
                    
                    # Validate compliance score range
                    score = data.get("overall_compliance_score", 0)
                    if not (0 <= score <= 10):
                        self.log_result(test_name, False, response_time,
                                      f"Invalid compliance score: {score} (should be 0-10)")
                        return
                    
                    self.log_result(test_name, True, response_time,
                                  f"Score: {score}/10, Level: {data.get('compliance_level')}, "
                                  f"Frameworks: {list(framework_assessments.keys())}")
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, response_time, f"Exception: {str(e)}")
            
    async def test_get_compliance_assessment(self):
        """Test GET /api/ai-agents/contract-negotiation/regulatory-compliance/{compliance_id}"""
        test_name = "Get Compliance Assessment"
        start_time = time.time()
        
        if not self.compliance_id:
            self.log_result(test_name, False, 0, "No compliance_id available from previous test")
            return
            
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/regulatory-compliance/{self.compliance_id}"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate that we get the same compliance assessment
                    if data.get("compliance_id") != self.compliance_id:
                        self.log_result(test_name, False, response_time,
                                      f"Compliance ID mismatch: expected {self.compliance_id}, got {data.get('compliance_id')}")
                        return
                    
                    # Validate required fields
                    required_fields = ["compliance_id", "session_id", "overall_compliance_score"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, response_time,
                                      f"Missing required fields: {missing_fields}")
                        return
                    
                    self.log_result(test_name, True, response_time,
                                  f"Retrieved assessment: {data.get('compliance_id')}")
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, response_time, f"Exception: {str(e)}")
            
    async def test_get_session_compliance_history(self):
        """Test GET /api/ai-agents/contract-negotiation/regulatory-compliance/session/{session_id}"""
        test_name = "Get Session Compliance History"
        start_time = time.time()
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/regulatory-compliance/session/{TEST_SESSION_ID}"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["session_id", "assessments", "total_count"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, response_time,
                                      f"Missing required fields: {missing_fields}")
                        return
                    
                    # Validate session_id matches
                    if data.get("session_id") != TEST_SESSION_ID:
                        self.log_result(test_name, False, response_time,
                                      f"Session ID mismatch: expected {TEST_SESSION_ID}, got {data.get('session_id')}")
                        return
                    
                    assessments = data.get("assessments", [])
                    total_count = data.get("total_count", 0)
                    
                    self.log_result(test_name, True, response_time,
                                  f"Found {total_count} assessments, frameworks: {data.get('frameworks_analyzed', [])}")
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, response_time, f"Exception: {str(e)}")
            
    async def test_get_regulatory_frameworks(self):
        """Test GET /api/ai-agents/contract-negotiation/regulatory-frameworks"""
        test_name = "Get Regulatory Frameworks"
        start_time = time.time()
        
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/regulatory-frameworks"
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["supported_frameworks", "industry_mappings", "total_frameworks"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, response_time,
                                      f"Missing required fields: {missing_fields}")
                        return
                    
                    # Validate expected frameworks
                    supported_frameworks = data.get("supported_frameworks", {})
                    expected_frameworks = ["gdpr", "sox", "hipaa", "ccpa", "pci_dss"]
                    
                    missing_frameworks = [fw for fw in expected_frameworks if fw not in supported_frameworks]
                    if missing_frameworks:
                        self.log_result(test_name, False, response_time,
                                      f"Missing expected frameworks: {missing_frameworks}")
                        return
                    
                    # Validate framework details
                    for framework_key, framework_data in supported_frameworks.items():
                        required_fw_fields = ["name", "jurisdiction", "industry", "key_areas"]
                        missing_fw_fields = [field for field in required_fw_fields if field not in framework_data]
                        
                        if missing_fw_fields:
                            self.log_result(test_name, False, response_time,
                                          f"Framework {framework_key} missing fields: {missing_fw_fields}")
                            return
                    
                    total_frameworks = data.get("total_frameworks", 0)
                    industry_mappings = data.get("industry_mappings", {})
                    
                    self.log_result(test_name, True, response_time,
                                  f"Found {total_frameworks} frameworks, {len(industry_mappings)} industry mappings")
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, response_time, f"Exception: {str(e)}")
            
    async def test_compliance_gap_analysis(self):
        """Test POST /api/ai-agents/contract-negotiation/compliance-gap-analysis"""
        test_name = "Compliance Gap Analysis"
        start_time = time.time()
        
        try:
            payload = {
                "session_id": TEST_SESSION_ID,
                "compliance_id": self.compliance_id,
                "target_frameworks": ["gdpr", "hipaa"]
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/compliance-gap-analysis",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = [
                        "analysis_id", "session_id", "total_gaps", "detailed_gaps",
                        "remediation_roadmap", "estimated_timeline", "estimated_cost_range"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_result(test_name, False, response_time,
                                      f"Missing required fields: {missing_fields}")
                        return
                    
                    # Validate session_id matches
                    if data.get("session_id") != TEST_SESSION_ID:
                        self.log_result(test_name, False, response_time,
                                      f"Session ID mismatch: expected {TEST_SESSION_ID}, got {data.get('session_id')}")
                        return
                    
                    total_gaps = data.get("total_gaps", 0)
                    critical_gaps = data.get("critical_gaps", 0)
                    high_priority_gaps = data.get("high_priority_gaps", 0)
                    
                    self.log_result(test_name, True, response_time,
                                  f"Analysis: {total_gaps} total gaps, {critical_gaps} critical, {high_priority_gaps} high priority")
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, response_time, f"Exception: {str(e)}")
            
    async def test_industry_compliance_requirements(self):
        """Test GET /api/ai-agents/contract-negotiation/industry-compliance/{industry_type}"""
        test_name = "Industry Compliance Requirements"
        
        # Test all three industry types
        industries = ["healthcare", "finance", "technology"]
        
        for industry in industries:
            start_time = time.time()
            
            try:
                async with self.session.get(
                    f"{BACKEND_URL}/ai-agents/contract-negotiation/industry-compliance/{industry}"
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        required_fields = [
                            "industry", "profile", "applicable_frameworks",
                            "compliance_checklist", "common_violations"
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            self.log_result(f"{test_name} ({industry})", False, response_time,
                                          f"Missing required fields: {missing_fields}")
                            continue
                        
                        # Validate industry matches
                        if data.get("industry") != industry:
                            self.log_result(f"{test_name} ({industry})", False, response_time,
                                          f"Industry mismatch: expected {industry}, got {data.get('industry')}")
                            continue
                        
                        # Validate applicable frameworks
                        applicable_frameworks = data.get("applicable_frameworks", {})
                        mandatory_frameworks = applicable_frameworks.get("mandatory", [])
                        
                        if not mandatory_frameworks:
                            self.log_result(f"{test_name} ({industry})", False, response_time,
                                          "No mandatory frameworks found")
                            continue
                        
                        profile = data.get("profile", {})
                        checklist = data.get("compliance_checklist", [])
                        violations = data.get("common_violations", [])
                        
                        self.log_result(f"{test_name} ({industry})", True, response_time,
                                      f"Frameworks: {mandatory_frameworks}, Checklist: {len(checklist)} items, "
                                      f"Violations: {len(violations)} items")
                    else:
                        error_text = await response.text()
                        self.log_result(f"{test_name} ({industry})", False, response_time,
                                      f"HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                response_time = time.time() - start_time
                self.log_result(f"{test_name} ({industry})", False, response_time, f"Exception: {str(e)}")
                
    async def run_all_tests(self):
        """Run all regulatory compliance tests"""
        print("🛡️ Starting Step 2 Regulatory Compliance Focus Testing")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Test all 6 endpoints in sequence
            await self.test_regulatory_compliance_assessment()
            await self.test_get_compliance_assessment()
            await self.test_get_session_compliance_history()
            await self.test_get_regulatory_frameworks()
            await self.test_compliance_gap_analysis()
            await self.test_industry_compliance_requirements()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("\n" + "=" * 80)
        print("🛡️ REGULATORY COMPLIANCE TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n🔍 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']} ({result['response_time']:.3f}s)")
            if result["details"]:
                print(f"      {result['details']}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

async def main():
    """Main test execution"""
    test_suite = RegulatoryComplianceTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n🎉 REGULATORY COMPLIANCE TESTING COMPLETED SUCCESSFULLY!")
        exit(0)
    else:
        print("\n🚨 REGULATORY COMPLIANCE TESTING FAILED!")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())