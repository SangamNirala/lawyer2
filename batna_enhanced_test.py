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
BACKEND_URL = "https://strat-engine-ai.preview.emergentagent.com/api"
TIMEOUT = 10  # 10 seconds timeout as requested

class BATNAEnhancedTester:
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
        elif success and response_data:
            # Print key response fields for verification
            if isinstance(response_data, dict):
                key_fields = []
                if 'batna_id' in response_data:
                    key_fields.append(f"batna_id: {response_data['batna_id']}")
                if 'alternatives' in response_data:
                    key_fields.append(f"alternatives: {len(response_data['alternatives'])} items")
                if 'recommended_walkaway_point' in response_data:
                    key_fields.append(f"walkaway_point: {response_data['recommended_walkaway_point']}")
                if 'decision_notes' in response_data:
                    key_fields.append(f"decision_notes: {len(response_data['decision_notes'])} items")
                if 'decision_tree' in response_data:
                    key_fields.append(f"decision_tree: {response_data['decision_tree'].get('name', 'N/A')}")
                if 'metrics' in response_data:
                    metrics = response_data['metrics']
                    key_fields.append(f"metrics: best_score={metrics.get('best_score', 'N/A')}")
                    
                if key_fields:
                    print(f"   Key fields: {', '.join(key_fields)}")

    async def test_batna_enhanced_endpoint(self) -> bool:
        """Test POST /api/ai-agents/contract-negotiation/batna-analysis with enhanced requirements"""
        test_name = "BATNA Enhanced Endpoint"
        
        # Exact payload from review request
        payload = {
            "session_id": str(uuid.uuid4()),
            "base_offer": {
                "price": 90000,
                "currency": "USD",
                "term_months": 12,
                "payment_terms": "Net 30"
            }
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                f"{BACKEND_URL}/ai-agents/contract-negotiation/batna-analysis",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify expected response structure from review request
                    required_fields = ['batna_id', 'alternatives', 'recommended_walkaway_point', 'decision_notes', 'decision_tree', 'metrics']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_result(test_name, False, None, f"Missing required fields: {missing_fields}", response_time)
                        return False
                    
                    # Verify alternatives array has exactly 3 items
                    alternatives = data.get('alternatives', [])
                    if len(alternatives) != 3:
                        self.log_result(test_name, False, None, f"Expected 3 alternatives, got {len(alternatives)}", response_time)
                        return False
                    
                    # Verify each alternative has required fields
                    alternative_required_fields = [
                        'alt_id', 'name', 'description', 'expected_value', 'risk', 
                        'time_cost_months', 'score', 'roi', 'risk_adjusted_value', 
                        'relationship_impact', 'scenarios'
                    ]
                    
                    for i, alt in enumerate(alternatives):
                        missing_alt_fields = [field for field in alternative_required_fields if field not in alt]
                        if missing_alt_fields:
                            self.log_result(test_name, False, None, f"Alternative {i+1} missing fields: {missing_alt_fields}", response_time)
                            return False
                        
                        # Verify risk is 0-1
                        if not (0 <= alt.get('risk', -1) <= 1):
                            self.log_result(test_name, False, None, f"Alternative {i+1} risk {alt.get('risk')} not in range 0-1", response_time)
                            return False
                        
                        # Verify score is 0-1
                        if not (0 <= alt.get('score', -1) <= 1):
                            self.log_result(test_name, False, None, f"Alternative {i+1} score {alt.get('score')} not in range 0-1", response_time)
                            return False
                        
                        # Verify relationship_impact is -1 to 1
                        if not (-1 <= alt.get('relationship_impact', -2) <= 1):
                            self.log_result(test_name, False, None, f"Alternative {i+1} relationship_impact {alt.get('relationship_impact')} not in range -1 to 1", response_time)
                            return False
                        
                        # Verify scenarios has best, likely, worst
                        scenarios = alt.get('scenarios', {})
                        scenario_keys = ['best', 'likely', 'worst']
                        missing_scenarios = [key for key in scenario_keys if key not in scenarios]
                        if missing_scenarios:
                            self.log_result(test_name, False, None, f"Alternative {i+1} missing scenarios: {missing_scenarios}", response_time)
                            return False
                        
                        # Verify each scenario has value and prob
                        for scenario_name, scenario_data in scenarios.items():
                            if scenario_name in scenario_keys:
                                if 'value' not in scenario_data or 'prob' not in scenario_data:
                                    self.log_result(test_name, False, None, f"Alternative {i+1} scenario {scenario_name} missing value or prob", response_time)
                                    return False
                    
                    # Verify recommended_walkaway_point is a number
                    walkaway_point = data.get('recommended_walkaway_point')
                    if not isinstance(walkaway_point, (int, float)):
                        self.log_result(test_name, False, None, f"recommended_walkaway_point should be number, got {type(walkaway_point)}", response_time)
                        return False
                    
                    # Verify decision_notes is an array
                    decision_notes = data.get('decision_notes', [])
                    if not isinstance(decision_notes, list):
                        self.log_result(test_name, False, None, f"decision_notes should be array, got {type(decision_notes)}", response_time)
                        return False
                    
                    # Verify decision_tree has name and children
                    decision_tree = data.get('decision_tree', {})
                    if 'name' not in decision_tree or 'children' not in decision_tree:
                        self.log_result(test_name, False, None, "decision_tree missing name or children", response_time)
                        return False
                    
                    # Verify metrics has required fields
                    metrics = data.get('metrics', {})
                    metrics_required_fields = ['best_alternative', 'best_score', 'avg_risk', 'avg_roi']
                    missing_metrics_fields = [field for field in metrics_required_fields if field not in metrics]
                    if missing_metrics_fields:
                        self.log_result(test_name, False, None, f"metrics missing fields: {missing_metrics_fields}", response_time)
                        return False
                    
                    # Create response snippet for reporting
                    response_snippet = {
                        "status": response.status,
                        "batna_id": data.get('batna_id'),
                        "alternatives_count": len(alternatives),
                        "sample_alternative": {
                            "alt_id": alternatives[0].get('alt_id'),
                            "name": alternatives[0].get('name'),
                            "expected_value": alternatives[0].get('expected_value'),
                            "risk": alternatives[0].get('risk'),
                            "score": alternatives[0].get('score'),
                            "scenarios_keys": list(alternatives[0].get('scenarios', {}).keys())
                        } if alternatives else None,
                        "recommended_walkaway_point": walkaway_point,
                        "decision_notes_count": len(decision_notes),
                        "decision_tree_name": decision_tree.get('name'),
                        "metrics": {
                            "best_alternative": metrics.get('best_alternative'),
                            "best_score": metrics.get('best_score'),
                            "avg_risk": metrics.get('avg_risk'),
                            "avg_roi": metrics.get('avg_roi')
                        }
                    }
                    
                    self.log_result(test_name, True, response_snippet, None, response_time)
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
        """Run all BATNA enhanced tests"""
        print("🎯 BATNA Enhanced Endpoint Testing Started")
        print("=" * 60)
        
        success_count = 0
        total_tests = 1
        
        # Test BATNA enhanced endpoint
        if await self.test_batna_enhanced_endpoint():
            success_count += 1
        
        print("\n" + "=" * 60)
        print(f"📊 BATNA Enhanced Testing Summary:")
        print(f"✅ Successful: {success_count}/{total_tests}")
        print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
        print(f"📈 Success Rate: {(success_count/total_tests)*100:.1f}%")
        
        if success_count == total_tests:
            print("🎉 All BATNA enhanced tests passed!")
        else:
            print("⚠️  Some tests failed - check details above")
        
        return success_count == total_tests

async def main():
    """Main test execution"""
    async with BATNAEnhancedTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)