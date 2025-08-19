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
BACKEND_URL = "https://risk-ai-negotiator.preview.emergentagent.com/api"
TIMEOUT = 15  # 15 seconds timeout for this specific test

class CounterOfferFocusedTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
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

    async def test_counter_offer_generation_detailed(self) -> bool:
        """Test POST /api/ai-agents/contract-negotiation/generate-counter-offer with exact payload from review request"""
        test_name = "Counter-Offer Generation with New Fields Validation"
        
        # Exact payload from review request
        payload = {
            "session_id": str(uuid.uuid4()),
            "goals": ["clarity", "speed"],
            "key_terms": ["payment terms", "ip"],
            "base_offer": {
                "price": 80000,
                "currency": "USD",
                "term_months": 12,
                "payment_terms": "Net 30"
            }
        }
        
        print(f"\n🎯 Testing Counter-Offer Generation Endpoint")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        try:
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/generate-counter-offer",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"\n📊 Response Status: 200 OK")
                    print(f"⏱️  Response Time: {response_time:.3f}s")
                    
                    # Validate top-level required fields
                    required_top_level_fields = ['strategy_id', 'scenarios', 'anchor_strategy', 'sequencing_plan', 'metrics']
                    missing_top_level = [field for field in required_top_level_fields if field not in data]
                    
                    if missing_top_level:
                        error_msg = f"Missing top-level required fields: {missing_top_level}"
                        print(f"❌ {error_msg}")
                        self.log_result(test_name, False, None, error_msg, response_time)
                        return False
                    
                    print(f"✅ All top-level fields present: {required_top_level_fields}")
                    
                    # Validate scenarios array
                    scenarios = data.get('scenarios', [])
                    if len(scenarios) != 3:
                        error_msg = f"Expected exactly 3 scenarios, got {len(scenarios)}"
                        print(f"❌ {error_msg}")
                        self.log_result(test_name, False, None, error_msg, response_time)
                        return False
                    
                    print(f"✅ Scenarios array has exactly 3 items")
                    
                    # Validate each scenario structure
                    scenario_required_fields = [
                        'scenario_id', 'name', 'predicted_acceptance', 'sequence_order', 
                        'target_price', 'price_impact', 'risk_adjusted_value', 'tactic', 
                        'narrative', 'dependencies', 'anchor_rationale'
                    ]
                    
                    for i, scenario in enumerate(scenarios):
                        missing_scenario_fields = [field for field in scenario_required_fields if field not in scenario]
                        if missing_scenario_fields:
                            error_msg = f"Scenario {i+1} missing fields: {missing_scenario_fields}"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate predicted_acceptance is between 0-1
                        predicted_acceptance = scenario.get('predicted_acceptance')
                        if not isinstance(predicted_acceptance, (int, float)) or not (0 <= predicted_acceptance <= 1):
                            error_msg = f"Scenario {i+1} predicted_acceptance {predicted_acceptance} not in range 0-1"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate target_price is a number
                        target_price = scenario.get('target_price')
                        if not isinstance(target_price, (int, float)):
                            error_msg = f"Scenario {i+1} target_price {target_price} is not a number"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate price_impact is a number
                        price_impact = scenario.get('price_impact')
                        if not isinstance(price_impact, (int, float)):
                            error_msg = f"Scenario {i+1} price_impact {price_impact} is not a number"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate risk_adjusted_value is a number
                        risk_adjusted_value = scenario.get('risk_adjusted_value')
                        if not isinstance(risk_adjusted_value, (int, float)):
                            error_msg = f"Scenario {i+1} risk_adjusted_value {risk_adjusted_value} is not a number"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate tactic is a string
                        tactic = scenario.get('tactic')
                        if not isinstance(tactic, str):
                            error_msg = f"Scenario {i+1} tactic {tactic} is not a string"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate narrative is a string
                        narrative = scenario.get('narrative')
                        if not isinstance(narrative, str):
                            error_msg = f"Scenario {i+1} narrative is not a string"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate dependencies is an array
                        dependencies = scenario.get('dependencies')
                        if not isinstance(dependencies, list):
                            error_msg = f"Scenario {i+1} dependencies is not an array"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                        
                        # Validate anchor_rationale is a string
                        anchor_rationale = scenario.get('anchor_rationale')
                        if not isinstance(anchor_rationale, str):
                            error_msg = f"Scenario {i+1} anchor_rationale is not a string"
                            print(f"❌ {error_msg}")
                            self.log_result(test_name, False, None, error_msg, response_time)
                            return False
                    
                    print(f"✅ All 3 scenarios have correct structure and field types")
                    
                    # Validate metrics structure
                    metrics = data.get('metrics', {})
                    metrics_required_fields = ['avg_predicted_acceptance', 'stretch_anchor', 'balanced_target', 'conservative_target']
                    missing_metrics_fields = [field for field in metrics_required_fields if field not in metrics]
                    
                    if missing_metrics_fields:
                        error_msg = f"Metrics missing fields: {missing_metrics_fields}"
                        print(f"❌ {error_msg}")
                        self.log_result(test_name, False, None, error_msg, response_time)
                        return False
                    
                    print(f"✅ Metrics object has all required fields: {metrics_required_fields}")
                    
                    # Validate sequencing_plan is an array
                    sequencing_plan = data.get('sequencing_plan')
                    if not isinstance(sequencing_plan, list):
                        error_msg = f"sequencing_plan is not an array, got {type(sequencing_plan)}"
                        print(f"❌ {error_msg}")
                        self.log_result(test_name, False, None, error_msg, response_time)
                        return False
                    
                    print(f"✅ sequencing_plan is an array with {len(sequencing_plan)} items")
                    
                    # Print example response snippet as requested
                    print(f"\n📋 EXAMPLE RESPONSE SNIPPET:")
                    example_response = {
                        "strategy_id": data.get('strategy_id'),
                        "scenarios": [
                            {
                                "scenario_id": scenarios[0].get('scenario_id'),
                                "name": scenarios[0].get('name'),
                                "predicted_acceptance": scenarios[0].get('predicted_acceptance'),
                                "sequence_order": scenarios[0].get('sequence_order'),
                                "target_price": scenarios[0].get('target_price'),
                                "price_impact": scenarios[0].get('price_impact'),
                                "risk_adjusted_value": scenarios[0].get('risk_adjusted_value'),
                                "tactic": scenarios[0].get('tactic'),
                                "narrative": scenarios[0].get('narrative')[:100] + "..." if len(scenarios[0].get('narrative', '')) > 100 else scenarios[0].get('narrative'),
                                "dependencies": scenarios[0].get('dependencies'),
                                "anchor_rationale": scenarios[0].get('anchor_rationale')[:100] + "..." if len(scenarios[0].get('anchor_rationale', '')) > 100 else scenarios[0].get('anchor_rationale')
                            }
                        ],
                        "anchor_strategy": data.get('anchor_strategy'),
                        "sequencing_plan": data.get('sequencing_plan'),
                        "metrics": data.get('metrics')
                    }
                    print(json.dumps(example_response, indent=2))
                    
                    # Check for any deviations
                    deviations = []
                    
                    # Check if all scenarios have unique scenario_ids
                    scenario_ids = [s.get('scenario_id') for s in scenarios]
                    if len(set(scenario_ids)) != len(scenario_ids):
                        deviations.append("Some scenarios have duplicate scenario_ids")
                    
                    # Check if sequence_order values are reasonable
                    sequence_orders = [s.get('sequence_order') for s in scenarios]
                    if not all(isinstance(order, int) and order > 0 for order in sequence_orders):
                        deviations.append("Some sequence_order values are not positive integers")
                    
                    if deviations:
                        print(f"\n⚠️  DEVIATIONS NOTED:")
                        for deviation in deviations:
                            print(f"   - {deviation}")
                    else:
                        print(f"\n✅ NO DEVIATIONS - All fields match expected structure perfectly")
                    
                    self.log_result(test_name, True, data, None, response_time)
                    return True
                else:
                    error_text = await response.text()
                    error_msg = f"HTTP {response.status}: {error_text}"
                    print(f"❌ {error_msg}")
                    self.log_result(test_name, False, None, error_msg, response_time)
                    return False
                    
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            error_msg = f"Timeout after {TIMEOUT}s"
            print(f"❌ {error_msg}")
            self.log_result(test_name, False, None, error_msg, response_time)
            return False
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            print(f"❌ {error_msg}")
            self.log_result(test_name, False, None, error_msg, response_time)
            return False

    async def run_focused_test(self):
        """Run the focused counter-offer generation test"""
        print("🚀 STARTING FOCUSED COUNTER-OFFER GENERATION TEST")
        print("=" * 60)
        
        success = await self.test_counter_offer_generation_detailed()
        
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
        if success:
            print("✅ Counter-Offer Generation Endpoint: WORKING")
            print("✅ All required fields present and correctly typed")
            print("✅ Response structure matches specification exactly")
        else:
            print("❌ Counter-Offer Generation Endpoint: FAILED")
            print("❌ See detailed error messages above")
        
        return success

async def main():
    """Main test execution"""
    async with CounterOfferFocusedTester() as tester:
        success = await tester.run_focused_test()
        return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)