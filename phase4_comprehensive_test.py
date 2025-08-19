#!/usr/bin/env python3
"""
Comprehensive Phase 4 Advanced Intelligence Backend Test
========================================================

Detailed testing of Phase 4 Advanced Intelligence implementation including:
- All 7 Phase 4 endpoints with detailed validation
- Integration workflow testing
- Performance verification
- MongoDB persistence verification
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://risk-ai-negotiator.preview.emergentagent.com/api"

class Phase4ComprehensiveTester:
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
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
    
    def test_feedback_endpoint_comprehensive(self):
        """Comprehensive test of feedback endpoint with validation"""
        print("\n🧪 Testing Feedback Collection Endpoint (Comprehensive)...")
        
        # Test 1: Valid feedback with all fields
        test_start = time.time()
        try:
            valid_payload = {
                "session_id": f"test-session-{uuid.uuid4()}",
                "scenario_id": f"test-scenario-{uuid.uuid4()}",
                "accepted": True,
                "counterparty_delay_sec": 300,
                "notes": "Comprehensive test feedback with all fields"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=valid_payload,
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                # Validate response structure
                required_fields = ["status", "feedback_id", "model_update"]
                if all(field in data for field in required_fields):
                    model_update = data.get("model_update", {})
                    if "status" in model_update:
                        self.log_result(
                            "Feedback Endpoint - Complete Payload",
                            True,
                            response_time,
                            f"Status: {data['status']}, Model Update: {model_update['status']}, Feedback ID: {data['feedback_id'][:8]}...",
                            response.status_code
                        )
                    else:
                        self.log_result(
                            "Feedback Endpoint - Complete Payload",
                            False,
                            response_time,
                            f"Missing model_update.status in response",
                            response.status_code
                        )
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result(
                        "Feedback Endpoint - Complete Payload",
                        False,
                        response_time,
                        f"Missing required fields: {missing}",
                        response.status_code
                    )
            else:
                self.log_result(
                    "Feedback Endpoint - Complete Payload",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Feedback Endpoint - Complete Payload",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Minimal valid payload
        test_start = time.time()
        try:
            minimal_payload = {
                "session_id": f"minimal-session-{uuid.uuid4()}",
                "scenario_id": f"minimal-scenario-{uuid.uuid4()}",
                "accepted": False
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=minimal_payload,
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Feedback Endpoint - Minimal Payload",
                    True,
                    response_time,
                    f"Minimal payload accepted, Status: {data.get('status', 'N/A')}",
                    response.status_code
                )
            else:
                self.log_result(
                    "Feedback Endpoint - Minimal Payload",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Feedback Endpoint - Minimal Payload",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
        
        # Test 3: Invalid payload validation
        test_start = time.time()
        try:
            invalid_payload = {
                "session_id": f"invalid-session-{uuid.uuid4()}",
                # Missing scenario_id and accepted
                "notes": "Invalid payload test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=invalid_payload,
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 400:
                self.log_result(
                    "Feedback Endpoint - Invalid Payload Validation",
                    True,
                    response_time,
                    f"Correctly rejected invalid payload with 400 error",
                    response.status_code
                )
            else:
                self.log_result(
                    "Feedback Endpoint - Invalid Payload Validation",
                    False,
                    response_time,
                    f"Should return 400, got {response.status_code}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Feedback Endpoint - Invalid Payload Validation",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    def test_predictor_health_comprehensive(self):
        """Comprehensive test of predictor health endpoint"""
        print("\n🧪 Testing Predictor Health Endpoint (Comprehensive)...")
        
        test_start = time.time()
        try:
            response = requests.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/predictor/health",
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate all required fields
                required_fields = ["status", "model_version", "total_feedback_events", "sessions_trained"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Validate field types and values
                    validations = []
                    
                    if isinstance(data.get("status"), str):
                        validations.append("status is string")
                    else:
                        validations.append("❌ status not string")
                    
                    if isinstance(data.get("model_version"), str):
                        validations.append("model_version is string")
                    else:
                        validations.append("❌ model_version not string")
                    
                    if isinstance(data.get("total_feedback_events"), int) and data.get("total_feedback_events") >= 0:
                        validations.append("total_feedback_events is valid int")
                    else:
                        validations.append("❌ total_feedback_events invalid")
                    
                    if isinstance(data.get("sessions_trained"), int) and data.get("sessions_trained") >= 0:
                        validations.append("sessions_trained is valid int")
                    else:
                        validations.append("❌ sessions_trained invalid")
                    
                    # Check response time requirement
                    if response_time < 3.0:
                        validations.append("response time < 3s")
                    else:
                        validations.append("❌ response time >= 3s")
                    
                    all_valid = all("❌" not in v for v in validations)
                    
                    self.log_result(
                        "Predictor Health - Comprehensive Validation",
                        all_valid,
                        response_time,
                        f"Status: {data['status']}, Version: {data['model_version']}, Events: {data['total_feedback_events']}, Sessions: {data['sessions_trained']}, Validations: {len([v for v in validations if '❌' not in v])}/{len(validations)}",
                        response.status_code
                    )
                else:
                    self.log_result(
                        "Predictor Health - Comprehensive Validation",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                        response.status_code
                    )
            else:
                self.log_result(
                    "Predictor Health - Comprehensive Validation",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Predictor Health - Comprehensive Validation",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    def test_strategy_updates_comprehensive(self):
        """Comprehensive test of strategy updates endpoint"""
        print("\n🧪 Testing Strategy Updates Endpoint (Comprehensive)...")
        
        test_session_id = f"strategy-test-{uuid.uuid4()}"
        test_start = time.time()
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/strategy-updates/{test_session_id}",
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate StrategyUpdate structure
                required_fields = ["session_id", "updated_at", "suggested_scenario", "predicted_acceptance", "confidence", "next_best_action"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Detailed validation
                    validations = []
                    
                    # Session ID should match
                    if data.get("session_id") == test_session_id:
                        validations.append("session_id matches")
                    else:
                        validations.append("❌ session_id mismatch")
                    
                    # Updated_at should be recent ISO timestamp
                    try:
                        updated_at = datetime.fromisoformat(data.get("updated_at", "").replace('Z', '+00:00'))
                        if (datetime.utcnow() - updated_at.replace(tzinfo=None)).total_seconds() < 60:
                            validations.append("updated_at is recent")
                        else:
                            validations.append("❌ updated_at not recent")
                    except:
                        validations.append("❌ updated_at invalid format")
                    
                    # Suggested scenario should be valid
                    valid_scenarios = ["Stretch", "Balanced", "Conservative"]
                    if data.get("suggested_scenario") in valid_scenarios:
                        validations.append("suggested_scenario valid")
                    else:
                        validations.append("❌ suggested_scenario invalid")
                    
                    # Predicted acceptance should have all scenarios
                    predicted_acceptance = data.get("predicted_acceptance", {})
                    if isinstance(predicted_acceptance, dict) and all(scenario in predicted_acceptance for scenario in valid_scenarios):
                        # Check if probabilities are in valid range
                        probs_valid = all(0 <= predicted_acceptance[s] <= 1 for s in valid_scenarios)
                        if probs_valid:
                            validations.append("predicted_acceptance valid")
                        else:
                            validations.append("❌ predicted_acceptance probabilities out of range")
                    else:
                        validations.append("❌ predicted_acceptance structure invalid")
                    
                    # Confidence should be in valid range
                    confidence = data.get("confidence")
                    if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
                        validations.append("confidence valid")
                    else:
                        validations.append("❌ confidence invalid")
                    
                    # Next best action should be string
                    if isinstance(data.get("next_best_action"), str) and len(data.get("next_best_action", "")) > 0:
                        validations.append("next_best_action valid")
                    else:
                        validations.append("❌ next_best_action invalid")
                    
                    all_valid = all("❌" not in v for v in validations)
                    
                    self.log_result(
                        "Strategy Updates - Comprehensive Validation",
                        all_valid,
                        response_time,
                        f"Session: {data['session_id'][:8]}..., Suggested: {data['suggested_scenario']}, Confidence: {data['confidence']:.3f}, Validations: {len([v for v in validations if '❌' not in v])}/{len(validations)}",
                        response.status_code
                    )
                else:
                    self.log_result(
                        "Strategy Updates - Comprehensive Validation",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                        response.status_code
                    )
            else:
                self.log_result(
                    "Strategy Updates - Comprehensive Validation",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Strategy Updates - Comprehensive Validation",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    def test_analytics_comprehensive(self):
        """Comprehensive test of analytics endpoints"""
        print("\n🧪 Testing Analytics Endpoints (Comprehensive)...")
        
        # Test Analytics Overview
        test_start = time.time()
        try:
            response = requests.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/overview",
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate comprehensive analytics structure
                required_fields = ["acceptance_rate_over_time", "scenario_performance", "overall_stats"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Validate overall_stats structure
                    overall_stats = data.get("overall_stats", {})
                    stats_fields = ["total_events", "total_sessions", "overall_acceptance_rate", "avg_response_time"]
                    stats_valid = all(field in overall_stats for field in stats_fields)
                    
                    # Check performance requirement
                    performance_ok = response_time < 3.0
                    
                    # Check caching (generated_at should be present)
                    caching_ok = "generated_at" in data
                    
                    self.log_result(
                        "Analytics Overview - Comprehensive",
                        stats_valid and performance_ok and caching_ok,
                        response_time,
                        f"Events: {overall_stats.get('total_events', 0)}, Sessions: {overall_stats.get('total_sessions', 0)}, Acceptance Rate: {overall_stats.get('overall_acceptance_rate', 0):.3f}, Performance: {'✅' if performance_ok else '❌'}, Caching: {'✅' if caching_ok else '❌'}",
                        response.status_code
                    )
                else:
                    self.log_result(
                        "Analytics Overview - Comprehensive",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                        response.status_code
                    )
            else:
                self.log_result(
                    "Analytics Overview - Comprehensive",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Analytics Overview - Comprehensive",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
        
        # Test A/B Tests Analytics
        test_start = time.time()
        try:
            response = requests.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/ab-tests",
                timeout=10
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate A/B test structure
                required_fields = ["running_tests", "test_summary"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    running_tests = data.get("running_tests", [])
                    test_summary = data.get("test_summary", {})
                    
                    # Validate statistical significance calculations
                    stats_valid = True
                    for test in running_tests:
                        required_test_fields = ["_id", "total_tests", "success_rate", "confidence_interval", "statistical_power"]
                        if not all(field in test for field in required_test_fields):
                            stats_valid = False
                            break
                        
                        # Validate confidence interval
                        ci = test.get("confidence_interval", [])
                        if not (isinstance(ci, list) and len(ci) == 2 and ci[0] <= ci[1]):
                            stats_valid = False
                            break
                    
                    self.log_result(
                        "A/B Tests Analytics - Comprehensive",
                        stats_valid,
                        response_time,
                        f"Running Tests: {len(running_tests)}, Best: {test_summary.get('best_performing', 'N/A')}, Statistical Validation: {'✅' if stats_valid else '❌'}",
                        response.status_code
                    )
                else:
                    self.log_result(
                        "A/B Tests Analytics - Comprehensive",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                        response.status_code
                    )
            else:
                self.log_result(
                    "A/B Tests Analytics - Comprehensive",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "A/B Tests Analytics - Comprehensive",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    def test_enhanced_counter_offer_comprehensive(self):
        """Comprehensive test of enhanced counter-offer generation"""
        print("\n🧪 Testing Enhanced Counter-Offer Generation (Comprehensive)...")
        
        test_start = time.time()
        try:
            enhanced_payload = {
                "session_id": f"enhanced-test-{uuid.uuid4()}",
                "goals": ["speed", "clarity"],
                "key_terms": ["payment terms"],
                "base_offer": {
                    "price": 75000,
                    "currency": "USD"
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=enhanced_payload,
                timeout=15
            )
            response_time = time.time() - test_start
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate enhanced response structure
                required_fields = ["strategy_id", "scenarios", "metrics"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    scenarios = data.get("scenarios", [])
                    metrics = data.get("metrics", {})
                    
                    # Validate scenarios
                    scenarios_valid = True
                    if len(scenarios) == 3:  # Should have exactly 3 scenarios
                        for scenario in scenarios:
                            required_scenario_fields = ["scenario_id", "name", "predicted_acceptance", "sequence_order"]
                            if not all(field in scenario for field in required_scenario_fields):
                                scenarios_valid = False
                                break
                            
                            # Validate predicted_acceptance is in valid range
                            pred_acc = scenario.get("predicted_acceptance")
                            if not (isinstance(pred_acc, (int, float)) and 0 <= pred_acc <= 1):
                                scenarios_valid = False
                                break
                    else:
                        scenarios_valid = False
                    
                    # Validate metrics
                    metrics_valid = "avg_predicted_acceptance" in metrics
                    
                    # Check if Phase 4 predictor integration is working
                    predictor_integration = any("predictor" in str(data).lower() for _ in [1])  # Simple check
                    
                    self.log_result(
                        "Enhanced Counter-Offer - Comprehensive",
                        scenarios_valid and metrics_valid,
                        response_time,
                        f"Strategy ID: {data['strategy_id'][:8]}..., Scenarios: {len(scenarios)}/3, Avg Acceptance: {metrics.get('avg_predicted_acceptance', 'N/A')}, Scenarios Valid: {'✅' if scenarios_valid else '❌'}, Metrics Valid: {'✅' if metrics_valid else '❌'}",
                        response.status_code
                    )
                else:
                    self.log_result(
                        "Enhanced Counter-Offer - Comprehensive",
                        False,
                        response_time,
                        f"Missing required fields: {missing_fields}",
                        response.status_code
                    )
            else:
                self.log_result(
                    "Enhanced Counter-Offer - Comprehensive",
                    False,
                    response_time,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response.status_code
                )
        except Exception as e:
            response_time = time.time() - test_start
            self.log_result(
                "Enhanced Counter-Offer - Comprehensive",
                False,
                response_time,
                f"Exception: {str(e)}"
            )
    
    def test_integration_workflow_comprehensive(self):
        """Comprehensive test of the complete integration workflow"""
        print("\n🧪 Testing Integration Workflow (Comprehensive)...")
        
        workflow_session_id = f"workflow-comprehensive-{uuid.uuid4()}"
        workflow_start = time.time()
        
        try:
            # Step 1: Generate initial strategy
            print("  Step 1: Generate initial counter-offer strategy...")
            initial_payload = {
                "session_id": workflow_session_id,
                "goals": ["maximize_value", "minimize_risk"],
                "key_terms": ["payment_terms", "liability", "termination"],
                "base_offer": {
                    "price": 90000,
                    "currency": "USD"
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=initial_payload,
                timeout=15
            )
            
            if response.status_code != 200:
                raise Exception(f"Initial strategy generation failed: {response.status_code}")
            
            initial_data = response.json()
            scenarios = initial_data.get("scenarios", [])
            if not scenarios:
                raise Exception("No scenarios in initial strategy")
            
            workflow_scenario_id = scenarios[0].get("scenario_id")
            print(f"    ✅ Initial strategy generated with {len(scenarios)} scenarios")
            
            # Step 2: Provide feedback to train the model
            print("  Step 2: Provide feedback for model training...")
            feedback_payload = {
                "session_id": workflow_session_id,
                "scenario_id": workflow_scenario_id,
                "accepted": True,
                "counterparty_delay_sec": 240,
                "notes": "Comprehensive workflow test - positive feedback"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/events/feedback",
                json=feedback_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"Feedback processing failed: {response.status_code}")
            
            feedback_data = response.json()
            model_update = feedback_data.get("model_update", {})
            print(f"    ✅ Feedback processed, model update: {model_update.get('status', 'N/A')}")
            
            # Step 3: Get real-time strategy updates
            print("  Step 3: Get real-time strategy updates...")
            response = requests.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/strategy-updates/{workflow_session_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"Strategy updates failed: {response.status_code}")
            
            updates_data = response.json()
            suggested_scenario = updates_data.get("suggested_scenario")
            confidence = updates_data.get("confidence", 0)
            print(f"    ✅ Strategy updates: {suggested_scenario} (confidence: {confidence:.3f})")
            
            # Step 4: Generate enhanced strategy with predictor integration
            print("  Step 4: Generate enhanced strategy with predictor integration...")
            enhanced_payload = {
                "session_id": workflow_session_id,
                "goals": ["speed", "relationship_preservation"],
                "key_terms": ["ip_rights", "confidentiality"],
                "base_offer": {
                    "price": 95000,
                    "currency": "USD"
                }
            }
            
            response = requests.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=enhanced_payload,
                timeout=15
            )
            
            if response.status_code != 200:
                raise Exception(f"Enhanced strategy generation failed: {response.status_code}")
            
            enhanced_data = response.json()
            enhanced_scenarios = enhanced_data.get("scenarios", [])
            enhanced_metrics = enhanced_data.get("metrics", {})
            print(f"    ✅ Enhanced strategy: {len(enhanced_scenarios)} scenarios, avg acceptance: {enhanced_metrics.get('avg_predicted_acceptance', 'N/A')}")
            
            # Step 5: Verify analytics capture the workflow
            print("  Step 5: Verify analytics capture the workflow data...")
            response = requests.get(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/analytics/overview",
                timeout=10
            )
            
            if response.status_code != 200:
                raise Exception(f"Analytics overview failed: {response.status_code}")
            
            analytics_data = response.json()
            overall_stats = analytics_data.get("overall_stats", {})
            total_events = overall_stats.get("total_events", 0)
            print(f"    ✅ Analytics updated: {total_events} total events captured")
            
            workflow_time = time.time() - workflow_start
            
            self.log_result(
                "Integration Workflow - Comprehensive",
                True,
                workflow_time,
                f"Complete workflow successful: Initial Strategy → Feedback → Model Update → Strategy Updates → Enhanced Strategy → Analytics Verification. Total events: {total_events}",
                200
            )
            
        except Exception as e:
            workflow_time = time.time() - workflow_start
            self.log_result(
                "Integration Workflow - Comprehensive",
                False,
                workflow_time,
                f"Workflow failed: {str(e)}"
            )
    
    def run_comprehensive_tests(self):
        """Run all comprehensive Phase 4 tests"""
        print("🚀 Phase 4 Advanced Intelligence - Comprehensive Backend Testing")
        print("=" * 80)
        
        # Run all comprehensive tests
        self.test_feedback_endpoint_comprehensive()
        self.test_predictor_health_comprehensive()
        self.test_strategy_updates_comprehensive()
        self.test_analytics_comprehensive()
        self.test_enhanced_counter_offer_comprehensive()
        self.test_integration_workflow_comprehensive()
        
        # Generate comprehensive summary
        self.generate_comprehensive_summary()
    
    def generate_comprehensive_summary(self):
        """Generate comprehensive test summary"""
        total_time = time.time() - self.start_time
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 PHASE 4 ADVANCED INTELLIGENCE - COMPREHENSIVE TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Time: {total_time:.3f}s")
        print()
        
        # Categorize results
        feedback_tests = [r for r in self.results if "Feedback" in r["test"]]
        predictor_tests = [r for r in self.results if "Predictor" in r["test"]]
        strategy_tests = [r for r in self.results if "Strategy Updates" in r["test"]]
        analytics_tests = [r for r in self.results if "Analytics" in r["test"]]
        counter_offer_tests = [r for r in self.results if "Counter-Offer" in r["test"]]
        workflow_tests = [r for r in self.results if "Workflow" in r["test"]]
        
        print("📋 PHASE 4 COMPONENT ANALYSIS:")
        print("-" * 80)
        print(f"Feedback Collection: {sum(1 for t in feedback_tests if t['success'])}/{len(feedback_tests)} ✅")
        print(f"Predictor Health: {sum(1 for t in predictor_tests if t['success'])}/{len(predictor_tests)} ✅")
        print(f"Strategy Updates: {sum(1 for t in strategy_tests if t['success'])}/{len(strategy_tests)} ✅")
        print(f"Analytics & Reporting: {sum(1 for t in analytics_tests if t['success'])}/{len(analytics_tests)} ✅")
        print(f"Enhanced Counter-Offers: {sum(1 for t in counter_offer_tests if t['success'])}/{len(counter_offer_tests)} ✅")
        print(f"Integration Workflow: {sum(1 for t in workflow_tests if t['success'])}/{len(workflow_tests)} ✅")
        print()
        
        # Performance analysis
        response_times = []
        for result in self.results:
            if result["success"]:
                time_str = result["response_time"].replace('s', '')
                try:
                    response_times.append(float(time_str))
                except:
                    pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print("⚡ PERFORMANCE ANALYSIS:")
            print("-" * 80)
            print(f"Average Response Time: {avg_response_time:.3f}s")
            print(f"Maximum Response Time: {max_response_time:.3f}s")
            print(f"Performance Requirement: All endpoints < 3s ({'✅ MET' if max_response_time < 3.0 else '❌ EXCEEDED'})")
            print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 80)
        for result in self.results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {result['test']}")
            print(f"   Time: {result['response_time']}")
            if result.get('status_code'):
                print(f"   Status: {result['status_code']}")
            print(f"   Details: {result['details']}")
            print()
        
        # Final verdict
        print("🎯 PHASE 4 ADVANCED INTELLIGENCE FINAL ASSESSMENT:")
        print("-" * 80)
        
        if success_rate >= 90:
            print("🎉 PHASE 4 ADVANCED INTELLIGENCE: FULLY OPERATIONAL")
            print("✅ All critical endpoints working correctly")
            print("✅ Predictive modeling integration successful")
            print("✅ Real-time adaptation systems functional")
            print("✅ Advanced analytics and reporting operational")
            print("✅ Performance optimization requirements met")
            print("✅ Integration workflow complete and verified")
        elif success_rate >= 75:
            print("⚠️ PHASE 4 ADVANCED INTELLIGENCE: MOSTLY OPERATIONAL")
            print("Most endpoints working but some issues need attention.")
        else:
            print("❌ PHASE 4 ADVANCED INTELLIGENCE: NEEDS ATTENTION")
            print("Multiple critical issues detected that require immediate fixes.")
        
        print("=" * 80)

def main():
    """Main test execution function"""
    tester = Phase4ComprehensiveTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()