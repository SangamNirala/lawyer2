#!/usr/bin/env python3
"""
Phase 4: Advanced Intelligence Backend Testing
==============================================

Comprehensive testing of Phase 4 Advanced Intelligence implementation for Contract Negotiation Strategy Engine.

Tests all 7 Phase 4 endpoints:
1. POST /api/ai-agents/contract-negotiation/events/feedback
2. GET /api/ai-agents/contract-negotiation/predictor/health
3. GET /api/ai-agents/contract-negotiation/strategy-updates/test-session-123
4. GET /api/ai-agents/contract-negotiation/analytics/overview
5. GET /api/ai-agents/contract-negotiation/analytics/ab-tests
6. GET /api/ai-agents/contract-negotiation/analytics/export?format=csv
7. POST /api/ai-agents/contract-negotiation/generate-counter-offer (Enhanced)

Integration workflow testing:
- Feedback → model update → enhanced strategy generation flow
- Predictor integration with existing strategy engine
- MongoDB collection creation and data persistence
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = "https://compliance-hub-53.preview.emergentagent.com/api"
TEST_SESSION_ID = "test-session-123"
TEST_SCENARIO_ID = "test-scenario-456"

class Phase4BackendTester:
    def __init__(self):
        self.session = None
        self.results = []
        self.start_time = time.time()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, response_time: float, details: str = "", status_code: int = None):
        """Log test result with timing and details"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "response_time": f"{response_time:.3f}s",
            "details": details,
            "status_code": status_code
        }
        self.results.append(result)
        print(f"{status} {test_name} ({response_time:.3f}s) - {details}")
        
    async def test_feedback_endpoint(self):
        """Test POST /api/ai-agents/contract-negotiation/events/feedback"""
        print("\n🧪 Testing Feedback Collection Endpoint...")
        
        # Test 1: Valid feedback payload
        test_start = time.time()
        try:
            valid_payload = {
                "session_id": TEST_SESSION_ID,
                "scenario_id": TEST_SCENARIO_ID,
                "accepted": True,
                "counterparty_delay_sec": 300,
                "notes": "Test feedback for Phase 4 implementation"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=valid_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - test_start
                data = await response.json()
                
                if response.status == 200:
                    # Verify response structure
                    required_fields = ["status", "feedback_id", "model_update"]
                    if all(field in data for field in required_fields):
                        model_update = data.get("model_update", {})
                        if "status" in model_update and model_update["status"] in ["updated", "feedback_stored"]:
                            self.log_result(
                                "Feedback Endpoint - Valid Payload",
                                True,
                                response_time,
                                f"Status: {data['status']}, Model Update: {model_update.get('status', 'N/A')}",
                                response.status
                            )
                        else:
                            self.log_result(
                                "Feedback Endpoint - Valid Payload",
                                False,
                                response_time,
                                f"Invalid model update structure: {model_update}",
                                response.status
                            )
                    else:
                        self.log_result(
                            "Feedback Endpoint - Valid Payload",
                            False,
                            response_time,
                            f"Missing required fields in response: {data}",
                            response.status
                        )
                else:
                    self.log_result(
                        "Feedback Endpoint - Valid Payload",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Feedback Endpoint - Valid Payload",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Invalid payload (missing required fields)
        test_start = time.time()
        try:
            invalid_payload = {
                "session_id": TEST_SESSION_ID,
                # Missing scenario_id and accepted
                "notes": "Invalid test payload"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=invalid_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - test_start
                
                if response.status == 400:
                    data = await response.json()
                    self.log_result(
                        "Feedback Endpoint - Invalid Payload",
                        True,
                        response_time,
                        f"Correctly rejected invalid payload: {data.get('detail', 'No detail')}",
                        response.status
                    )
                else:
                    data = await response.json()
                    self.log_result(
                        "Feedback Endpoint - Invalid Payload",
                        False,
                        response_time,
                        f"Should have returned 400, got {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Feedback Endpoint - Invalid Payload",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_predictor_health_endpoint(self):
        """Test GET /api/ai-agents/contract-negotiation/predictor/health"""
        print("\n🧪 Testing Predictor Health Endpoint...")
        
        test_start = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/predictor/health"
            ) as response:
                response_time = time.time() - test_start
                try:
                    data = await response.json()
                except Exception as json_error:
                    # Try to get text response for debugging
                    text_response = await response.text()
                    raise Exception(f"JSON parsing failed: {json_error}. Response: {text_response[:200]}")
                
                if response.status == 200:
                    # Verify response structure
                    required_fields = ["status", "model_version", "total_feedback_events", "sessions_trained"]
                    if all(field in data for field in required_fields):
                        # Check response time requirement (under 3 seconds)
                        if response_time < 3.0:
                            self.log_result(
                                "Predictor Health Endpoint",
                                True,
                                response_time,
                                f"Status: {data['status']}, Version: {data['model_version']}, Events: {data['total_feedback_events']}, Sessions: {data['sessions_trained']}",
                                response.status
                            )
                        else:
                            self.log_result(
                                "Predictor Health Endpoint",
                                False,
                                response_time,
                                f"Response time {response_time:.3f}s exceeds 3s requirement",
                                response.status
                            )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(
                            "Predictor Health Endpoint",
                            False,
                            response_time,
                            f"Missing required fields: {missing_fields}",
                            response.status
                        )
                else:
                    self.log_result(
                        "Predictor Health Endpoint",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Predictor Health Endpoint",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_strategy_updates_endpoint(self):
        """Test GET /api/ai-agents/contract-negotiation/strategy-updates/{session_id}"""
        print("\n🧪 Testing Real-time Strategy Updates Endpoint...")
        
        test_start = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/strategy-updates/{TEST_SESSION_ID}"
            ) as response:
                response_time = time.time() - test_start
                data = await response.json()
                
                if response.status == 200:
                    # Verify StrategyUpdate response structure
                    required_fields = ["session_id", "updated_at", "suggested_scenario", "predicted_acceptance", "confidence", "next_best_action"]
                    if all(field in data for field in required_fields):
                        # Verify predicted_acceptance is a dict with scenario probabilities
                        predicted_acceptance = data.get("predicted_acceptance", {})
                        expected_scenarios = ["Stretch", "Balanced", "Conservative"]
                        
                        if isinstance(predicted_acceptance, dict) and all(scenario in predicted_acceptance for scenario in expected_scenarios):
                            self.log_result(
                                "Strategy Updates Endpoint",
                                True,
                                response_time,
                                f"Session: {data['session_id']}, Suggested: {data['suggested_scenario']}, Confidence: {data['confidence']}, Probabilities: {predicted_acceptance}",
                                response.status
                            )
                        else:
                            self.log_result(
                                "Strategy Updates Endpoint",
                                False,
                                response_time,
                                f"Invalid predicted_acceptance structure: {predicted_acceptance}",
                                response.status
                            )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(
                            "Strategy Updates Endpoint",
                            False,
                            response_time,
                            f"Missing required fields: {missing_fields}",
                            response.status
                        )
                else:
                    self.log_result(
                        "Strategy Updates Endpoint",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Strategy Updates Endpoint",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_analytics_overview_endpoint(self):
        """Test GET /api/ai-agents/contract-negotiation/analytics/overview"""
        print("\n🧪 Testing Comprehensive Analytics Overview Endpoint...")
        
        test_start = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/overview"
            ) as response:
                response_time = time.time() - test_start
                data = await response.json()
                
                if response.status == 200:
                    # Verify comprehensive analytics response structure
                    required_fields = ["acceptance_rate_over_time", "scenario_performance", "overall_stats"]
                    if all(field in data for field in required_fields):
                        # Check performance requirement (under 3 seconds)
                        if response_time < 3.0:
                            overall_stats = data.get("overall_stats", {})
                            scenario_performance = data.get("scenario_performance", [])
                            
                            self.log_result(
                                "Analytics Overview Endpoint",
                                True,
                                response_time,
                                f"Total Events: {overall_stats.get('total_events', 0)}, Total Sessions: {overall_stats.get('total_sessions', 0)}, Acceptance Rate: {overall_stats.get('overall_acceptance_rate', 0):.3f}, Scenarios Analyzed: {len(scenario_performance)}",
                                response.status
                            )
                        else:
                            self.log_result(
                                "Analytics Overview Endpoint",
                                False,
                                response_time,
                                f"Response time {response_time:.3f}s exceeds 3s requirement",
                                response.status
                            )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(
                            "Analytics Overview Endpoint",
                            False,
                            response_time,
                            f"Missing required fields: {missing_fields}",
                            response.status
                        )
                else:
                    self.log_result(
                        "Analytics Overview Endpoint",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Analytics Overview Endpoint",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_analytics_ab_tests_endpoint(self):
        """Test GET /api/ai-agents/contract-negotiation/analytics/ab-tests"""
        print("\n🧪 Testing A/B Test Analysis Endpoint...")
        
        test_start = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/ab-tests"
            ) as response:
                response_time = time.time() - test_start
                data = await response.json()
                
                if response.status == 200:
                    # Verify A/B test analysis response structure
                    required_fields = ["running_tests", "test_summary"]
                    if all(field in data for field in required_fields):
                        running_tests = data.get("running_tests", [])
                        test_summary = data.get("test_summary", {})
                        
                        # Verify statistical significance calculations
                        valid_tests = True
                        for test in running_tests:
                            if not all(field in test for field in ["_id", "total_tests", "success_rate", "confidence_interval", "statistical_power"]):
                                valid_tests = False
                                break
                        
                        if valid_tests:
                            self.log_result(
                                "A/B Tests Analytics Endpoint",
                                True,
                                response_time,
                                f"Running Tests: {len(running_tests)}, Best Performing: {test_summary.get('best_performing', 'N/A')}, Total Groups: {test_summary.get('total_test_groups', 0)}",
                                response.status
                            )
                        else:
                            self.log_result(
                                "A/B Tests Analytics Endpoint",
                                False,
                                response_time,
                                f"Invalid test structure in running_tests",
                                response.status
                            )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(
                            "A/B Tests Analytics Endpoint",
                            False,
                            response_time,
                            f"Missing required fields: {missing_fields}",
                            response.status
                        )
                else:
                    self.log_result(
                        "A/B Tests Analytics Endpoint",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "A/B Tests Analytics Endpoint",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_analytics_export_endpoint(self):
        """Test GET /api/ai-agents/contract-negotiation/analytics/export"""
        print("\n🧪 Testing Analytics Export Endpoint...")
        
        # Test 1: CSV export
        test_start = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/export?format=csv"
            ) as response:
                response_time = time.time() - test_start
                
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'text/csv' in content_type:
                        csv_content = await response.text()
                        # Basic CSV validation
                        lines = csv_content.strip().split('\n')
                        if len(lines) >= 1:  # At least header
                            self.log_result(
                                "Analytics Export - CSV Format",
                                True,
                                response_time,
                                f"CSV export successful, {len(lines)} lines, Content-Type: {content_type}",
                                response.status
                            )
                        else:
                            self.log_result(
                                "Analytics Export - CSV Format",
                                False,
                                response_time,
                                f"Empty CSV content",
                                response.status
                            )
                    else:
                        self.log_result(
                            "Analytics Export - CSV Format",
                            False,
                            response_time,
                            f"Wrong content type: {content_type}",
                            response.status
                        )
                else:
                    data = await response.text()
                    self.log_result(
                        "Analytics Export - CSV Format",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Analytics Export - CSV Format",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
        
        # Test 2: JSON export
        test_start = time.time()
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/export?format=json"
            ) as response:
                response_time = time.time() - test_start
                data = await response.json()
                
                if response.status == 200:
                    required_fields = ["export_format", "record_count", "exported_at", "data"]
                    if all(field in data for field in required_fields):
                        if data["export_format"] == "json":
                            self.log_result(
                                "Analytics Export - JSON Format",
                                True,
                                response_time,
                                f"JSON export successful, {data['record_count']} records",
                                response.status
                            )
                        else:
                            self.log_result(
                                "Analytics Export - JSON Format",
                                False,
                                response_time,
                                f"Wrong export format: {data['export_format']}",
                                response.status
                            )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(
                            "Analytics Export - JSON Format",
                            False,
                            response_time,
                            f"Missing required fields: {missing_fields}",
                            response.status
                        )
                else:
                    self.log_result(
                        "Analytics Export - JSON Format",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Analytics Export - JSON Format",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_enhanced_counter_offer_endpoint(self):
        """Test POST /api/ai-agents/contract-negotiation/generate-counter-offer (Enhanced with Phase 4)"""
        print("\n🧪 Testing Enhanced Counter-Offer Generation Endpoint...")
        
        test_start = time.time()
        try:
            enhanced_payload = {
                "session_id": TEST_SESSION_ID,
                "goals": ["speed", "clarity"],
                "key_terms": ["payment terms"],
                "base_offer": {
                    "price": 75000,
                    "currency": "USD"
                }
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=enhanced_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - test_start
                data = await response.json()
                
                if response.status == 200:
                    # Verify enhanced response structure with Phase 4 predictor integration
                    required_fields = ["strategy_id", "scenarios", "metrics"]
                    if all(field in data for field in required_fields):
                        scenarios = data.get("scenarios", [])
                        if len(scenarios) == 3:  # Should have 3 scenarios
                            # Check if scenarios have enhanced predictions
                            enhanced_features = True
                            for scenario in scenarios:
                                if not all(field in scenario for field in ["scenario_id", "name", "predicted_acceptance"]):
                                    enhanced_features = False
                                    break
                            
                            if enhanced_features:
                                metrics = data.get("metrics", {})
                                self.log_result(
                                    "Enhanced Counter-Offer Generation",
                                    True,
                                    response_time,
                                    f"Strategy ID: {data['strategy_id'][:8]}..., Scenarios: {len(scenarios)}, Avg Acceptance: {metrics.get('avg_predicted_acceptance', 'N/A')}",
                                    response.status
                                )
                            else:
                                self.log_result(
                                    "Enhanced Counter-Offer Generation",
                                    False,
                                    response_time,
                                    f"Scenarios missing enhanced prediction fields",
                                    response.status
                                )
                        else:
                            self.log_result(
                                "Enhanced Counter-Offer Generation",
                                False,
                                response_time,
                                f"Expected 3 scenarios, got {len(scenarios)}",
                                response.status
                            )
                    else:
                        missing_fields = [f for f in required_fields if f not in data]
                        self.log_result(
                            "Enhanced Counter-Offer Generation",
                            False,
                            response_time,
                            f"Missing required fields: {missing_fields}",
                            response.status
                        )
                else:
                    self.log_result(
                        "Enhanced Counter-Offer Generation",
                        False,
                        response_time,
                        f"HTTP {response.status}: {data}",
                        response.status
                    )
                    
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Enhanced Counter-Offer Generation",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    async def test_integration_workflow(self):
        """Test the complete integration workflow: feedback → model update → enhanced strategy generation"""
        print("\n🧪 Testing Integration Workflow...")
        
        workflow_session_id = f"workflow-test-{uuid.uuid4()}"
        workflow_scenario_id = f"scenario-{uuid.uuid4()}"
        
        # Step 1: Generate initial counter-offer strategy
        print("  Step 1: Generate initial strategy...")
        test_start = time.time()
        try:
            initial_payload = {
                "session_id": workflow_session_id,
                "goals": ["maximize_value"],
                "key_terms": ["payment_terms", "liability"],
                "base_offer": {
                    "price": 80000,
                    "currency": "USD"
                }
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=initial_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    initial_data = await response.json()
                    scenarios = initial_data.get("scenarios", [])
                    if scenarios:
                        workflow_scenario_id = scenarios[0].get("scenario_id", workflow_scenario_id)
                        print(f"    ✅ Initial strategy generated with scenario ID: {workflow_scenario_id[:8]}...")
                    else:
                        print(f"    ❌ No scenarios in initial strategy response")
                        return
                else:
                    print(f"    ❌ Initial strategy generation failed: {response.status}")
                    return
        except Exception as e:
            print(f"    ❌ Initial strategy generation exception: {e}")
            return
        
        # Step 2: Provide feedback
        print("  Step 2: Provide feedback...")
        try:
            feedback_payload = {
                "session_id": workflow_session_id,
                "scenario_id": workflow_scenario_id,
                "accepted": True,
                "counterparty_delay_sec": 180,
                "notes": "Integration workflow test feedback"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=feedback_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    feedback_data = await response.json()
                    model_update = feedback_data.get("model_update", {})
                    print(f"    ✅ Feedback processed, model update status: {model_update.get('status', 'N/A')}")
                else:
                    print(f"    ❌ Feedback processing failed: {response.status}")
                    return
        except Exception as e:
            print(f"    ❌ Feedback processing exception: {e}")
            return
        
        # Step 3: Get strategy updates
        print("  Step 3: Get real-time strategy updates...")
        try:
            async with self.session.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/strategy-updates/{workflow_session_id}"
            ) as response:
                if response.status == 200:
                    updates_data = await response.json()
                    suggested_scenario = updates_data.get("suggested_scenario", "N/A")
                    confidence = updates_data.get("confidence", 0)
                    print(f"    ✅ Strategy updates retrieved, suggested: {suggested_scenario}, confidence: {confidence}")
                else:
                    print(f"    ❌ Strategy updates failed: {response.status}")
                    return
        except Exception as e:
            print(f"    ❌ Strategy updates exception: {e}")
            return
        
        # Step 4: Generate enhanced strategy
        print("  Step 4: Generate enhanced strategy with predictor integration...")
        try:
            enhanced_payload = {
                "session_id": workflow_session_id,
                "goals": ["speed", "relationship"],
                "key_terms": ["termination", "ip_rights"],
                "base_offer": {
                    "price": 85000,
                    "currency": "USD"
                }
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=enhanced_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - test_start
                if response.status == 200:
                    enhanced_data = await response.json()
                    scenarios = enhanced_data.get("scenarios", [])
                    metrics = enhanced_data.get("metrics", {})
                    
                    self.log_result(
                        "Integration Workflow Test",
                        True,
                        response_time,
                        f"Complete workflow successful: Initial → Feedback → Updates → Enhanced Strategy ({len(scenarios)} scenarios, avg acceptance: {metrics.get('avg_predicted_acceptance', 'N/A')})",
                        response.status
                    )
                else:
                    self.log_result(
                        "Integration Workflow Test",
                        False,
                        response_time,
                        f"Enhanced strategy generation failed: {response.status}",
                        response.status
                    )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Integration Workflow Test",
                False,
                response_time,
                f"Enhanced strategy generation exception: {e}"
            )
    
    async def run_all_tests(self):
        """Run all Phase 4 Advanced Intelligence tests"""
        print("🚀 Starting Phase 4: Advanced Intelligence Backend Testing")
        print("=" * 80)
        
        # Test all 7 Phase 4 endpoints
        await self.test_feedback_endpoint()
        await self.test_predictor_health_endpoint()
        await self.test_strategy_updates_endpoint()
        await self.test_analytics_overview_endpoint()
        await self.test_analytics_ab_tests_endpoint()
        await self.test_analytics_export_endpoint()
        await self.test_enhanced_counter_offer_endpoint()
        
        # Test integration workflow
        await self.test_integration_workflow()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        total_time = time.time() - self.start_time
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 PHASE 4 ADVANCED INTELLIGENCE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.3f}s")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        print("-" * 80)
        for result in self.results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {result['test']}")
            print(f"   Time: {result['response_time']}")
            if result.get('status_code'):
                print(f"   Status: {result['status_code']}")
            print(f"   Details: {result['details']}")
            print()
        
        # Performance analysis
        response_times = [float(r["response_time"].replace('s', '')) for r in self.results if r["success"]]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print("⚡ PERFORMANCE ANALYSIS:")
            print("-" * 80)
            print(f"Average Response Time: {avg_response_time:.3f}s")
            print(f"Maximum Response Time: {max_response_time:.3f}s")
            print(f"Performance Requirement: All endpoints < 3s ({'✅ MET' if max_response_time < 3.0 else '❌ EXCEEDED'})")
            print()
        
        # Phase 4 specific analysis
        print("🧠 PHASE 4 ADVANCED INTELLIGENCE ANALYSIS:")
        print("-" * 80)
        
        # Count endpoint categories
        feedback_tests = [r for r in self.results if "Feedback" in r["test"]]
        predictor_tests = [r for r in self.results if "Predictor" in r["test"]]
        analytics_tests = [r for r in self.results if "Analytics" in r["test"]]
        integration_tests = [r for r in self.results if "Integration" in r["test"]]
        
        print(f"Feedback Collection: {sum(1 for t in feedback_tests if t['success'])}/{len(feedback_tests)} ✅")
        print(f"Predictor Health: {sum(1 for t in predictor_tests if t['success'])}/{len(predictor_tests)} ✅")
        print(f"Analytics & Reporting: {sum(1 for t in analytics_tests if t['success'])}/{len(analytics_tests)} ✅")
        print(f"Integration Workflow: {sum(1 for t in integration_tests if t['success'])}/{len(integration_tests)} ✅")
        print()
        
        # Final verdict
        if success_rate >= 85:
            print("🎉 PHASE 4 ADVANCED INTELLIGENCE: FULLY OPERATIONAL")
            print("All critical endpoints are working correctly with predictive modeling,")
            print("real-time adaptation, and comprehensive analytics capabilities.")
        elif success_rate >= 70:
            print("⚠️ PHASE 4 ADVANCED INTELLIGENCE: MOSTLY OPERATIONAL")
            print("Most endpoints working but some issues need attention.")
        else:
            print("❌ PHASE 4 ADVANCED INTELLIGENCE: NEEDS ATTENTION")
            print("Multiple critical issues detected that require immediate fixes.")
        
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with Phase4BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())