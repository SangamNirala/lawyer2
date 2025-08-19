#!/usr/bin/env python3
"""
Focused Re-test for Compliance Gap Analysis Endpoint
Re-testing the POST /api/ai-agents/contract-negotiation/compliance-gap-analysis endpoint
that failed in the previous test due to ObjectId serialization issues.

SPECIFIC TEST FOCUS:
- POST /api/ai-agents/contract-negotiation/compliance-gap-analysis endpoint only
- Use session_id from previous successful compliance assessment: "test-session-regulatory-001"
- Verify the endpoint now returns 200 OK instead of HTTP 500
- Confirm detailed gap analysis, remediation roadmap, and cost estimates are working
- Validate response structure includes analysis_id, detailed_gaps, remediation_roadmap
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
BACKEND_URL = "https://clever-jepsen.preview.emergentagent.com/api"
TEST_SESSION_ID = "test-session-regulatory-001"

class ComplianceGapAnalysisRetest:
    def __init__(self):
        self.session = None
        self.results = []
        
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
        print("🔧 Test session initialized for Compliance Gap Analysis re-test")
        
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
        
    async def test_compliance_gap_analysis_focused(self):
        """
        Focused test for POST /api/ai-agents/contract-negotiation/compliance-gap-analysis
        Using exact payload from review request to verify ObjectId serialization fix
        """
        test_name = "Compliance Gap Analysis - ObjectId Serialization Fix Verification"
        start_time = time.time()
        
        try:
            # Use exact payload from review request
            payload = {
                "session_id": TEST_SESSION_ID
            }
            
            print(f"🧪 Testing with payload: {json.dumps(payload, indent=2)}")
            print(f"🎯 Target endpoint: {BACKEND_URL}/ai-agents/contract-negotiation/compliance-gap-analysis")
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/compliance-gap-analysis",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                print(f"📡 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📄 Response received: {len(str(data))} characters")
                    
                    # Validate response structure as specified in review request
                    required_fields = [
                        "analysis_id", 
                        "detailed_gaps", 
                        "remediation_roadmap"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_result(test_name, False, response_time, 
                                      f"Missing required fields from review request: {missing_fields}")
                        return
                    
                    # Additional validation for expected fields
                    expected_fields = [
                        "session_id", "total_gaps", "critical_gaps", "high_priority_gaps",
                        "estimated_timeline", "estimated_cost_range"
                    ]
                    
                    # Validate session_id matches
                    if data.get("session_id") != TEST_SESSION_ID:
                        self.log_result(test_name, False, response_time,
                                      f"Session ID mismatch: expected {TEST_SESSION_ID}, got {data.get('session_id')}")
                        return
                    
                    # Validate analysis_id is a proper UUID string (not ObjectId)
                    analysis_id = data.get("analysis_id")
                    if not analysis_id or not isinstance(analysis_id, str):
                        self.log_result(test_name, False, response_time,
                                      f"Invalid analysis_id: {analysis_id} (should be UUID string)")
                        return
                    
                    # Try to parse as UUID to ensure it's not an ObjectId
                    try:
                        uuid.UUID(analysis_id)
                        print(f"✅ analysis_id is valid UUID: {analysis_id}")
                    except ValueError:
                        self.log_result(test_name, False, response_time,
                                      f"analysis_id is not a valid UUID: {analysis_id}")
                        return
                    
                    # Validate detailed_gaps structure
                    detailed_gaps = data.get("detailed_gaps", [])
                    if not isinstance(detailed_gaps, list):
                        self.log_result(test_name, False, response_time,
                                      f"detailed_gaps should be a list, got: {type(detailed_gaps)}")
                        return
                    
                    # Validate remediation_roadmap structure
                    remediation_roadmap = data.get("remediation_roadmap", {})
                    if not isinstance(remediation_roadmap, dict):
                        self.log_result(test_name, False, response_time,
                                      f"remediation_roadmap should be a dict, got: {type(remediation_roadmap)}")
                        return
                    
                    # Validate cost estimates and timeline projections
                    estimated_cost_range = data.get("estimated_cost_range", {})
                    estimated_timeline = data.get("estimated_timeline", {})
                    
                    if not estimated_cost_range:
                        self.log_result(test_name, False, response_time,
                                      "Missing cost estimates")
                        return
                    
                    if not estimated_timeline:
                        self.log_result(test_name, False, response_time,
                                      "Missing timeline projections")
                        return
                    
                    # Extract key metrics for reporting
                    total_gaps = data.get("total_gaps", 0)
                    critical_gaps = data.get("critical_gaps", 0)
                    high_priority_gaps = data.get("high_priority_gaps", 0)
                    
                    # Success - all validations passed
                    self.log_result(test_name, True, response_time,
                                  f"✅ ObjectId serialization fix VERIFIED! Analysis: {total_gaps} total gaps, "
                                  f"{critical_gaps} critical, {high_priority_gaps} high priority. "
                                  f"Response includes analysis_id (UUID), detailed_gaps ({len(detailed_gaps)} items), "
                                  f"remediation_roadmap, cost estimates, and timeline projections.")
                    
                    # Print detailed response structure for verification
                    print(f"📊 DETAILED RESPONSE STRUCTURE:")
                    print(f"   • analysis_id: {analysis_id} (UUID format)")
                    print(f"   • session_id: {data.get('session_id')}")
                    print(f"   • total_gaps: {total_gaps}")
                    print(f"   • critical_gaps: {critical_gaps}")
                    print(f"   • high_priority_gaps: {high_priority_gaps}")
                    print(f"   • detailed_gaps: {len(detailed_gaps)} items")
                    print(f"   • remediation_roadmap: {len(remediation_roadmap)} sections")
                    print(f"   • estimated_cost_range: {estimated_cost_range}")
                    print(f"   • estimated_timeline: {estimated_timeline}")
                    
                elif response.status == 500:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"❌ STILL FAILING with HTTP 500 - ObjectId serialization issue NOT fixed: {error_text}")
                    print(f"🚨 ERROR DETAILS: {error_text}")
                    
                else:
                    error_text = await response.text()
                    self.log_result(test_name, False, response_time,
                                  f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.log_result(test_name, False, response_time, f"Exception: {str(e)}")
            print(f"🚨 EXCEPTION DETAILS: {str(e)}")
            
    async def run_focused_retest(self):
        """Run the focused re-test for compliance gap analysis"""
        print("🎯 Starting Focused Re-test: Compliance Gap Analysis ObjectId Serialization Fix")
        print("=" * 90)
        print(f"📋 Test Scope: POST /api/ai-agents/contract-negotiation/compliance-gap-analysis")
        print(f"🔑 Session ID: {TEST_SESSION_ID}")
        print(f"🎯 Expected: HTTP 200 OK (previously HTTP 500)")
        print(f"✅ Verify: analysis_id, detailed_gaps, remediation_roadmap in response")
        print("=" * 90)
        
        await self.setup()
        
        try:
            await self.test_compliance_gap_analysis_focused()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("\n" + "=" * 90)
        print("🎯 COMPLIANCE GAP ANALYSIS RE-TEST SUMMARY")
        print("=" * 90)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if passed_tests > 0:
            print("\n🎉 SUCCESS DETAILS:")
            for result in self.results:
                if result["success"]:
                    print(f"  ✅ {result['test']}")
                    print(f"      Response Time: {result['response_time']:.3f}s")
                    print(f"      Details: {result['details']}")
        
        if failed_tests > 0:
            print("\n❌ FAILURE DETAILS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}")
                    print(f"      Response Time: {result['response_time']:.3f}s")
                    print(f"      Error: {result['details']}")
        
        # Final verdict
        if success_rate == 100:
            print("\n🎉 COMPLIANCE GAP ANALYSIS ENDPOINT FULLY FIXED!")
            print("✅ ObjectId serialization issue resolved")
            print("✅ HTTP 200 OK response confirmed")
            print("✅ All required response fields present")
            print("✅ Step 2 Regulatory Compliance Focus can now achieve 100% success rate (8/8 endpoints)")
        else:
            print("\n🚨 COMPLIANCE GAP ANALYSIS ENDPOINT STILL HAS ISSUES!")
            print("❌ ObjectId serialization fix incomplete")
            print("❌ Step 2 Regulatory Compliance Focus remains at 87.5% success rate (7/8 endpoints)")
        
        return success_rate == 100

async def main():
    """Main test execution"""
    test_suite = ComplianceGapAnalysisRetest()
    success = await test_suite.run_focused_retest()
    
    if success:
        print("\n🎉 COMPLIANCE GAP ANALYSIS RE-TEST PASSED!")
        exit(0)
    else:
        print("\n🚨 COMPLIANCE GAP ANALYSIS RE-TEST FAILED!")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())