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
BACKEND_URL = "https://strategyengine.preview.emergentagent.com/api"
TIMEOUT = 10  # 10 seconds timeout as requested

class BATNADetailedTester:
    def __init__(self):
        self.session = None
        
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

    async def test_batna_detailed_response(self) -> bool:
        """Test POST /api/ai-agents/contract-negotiation/batna-analysis with detailed response analysis"""
        test_name = "BATNA Enhanced Endpoint - Detailed Response Analysis"
        
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
                    
                    print(f"✅ {test_name} ({response_time:.3f}s)")
                    print(f"📊 Response Status: {response.status}")
                    print(f"⏱️  Response Time: {response_time:.3f}s (under {TIMEOUT}s timeout)")
                    print("\n🔍 DETAILED RESPONSE ANALYSIS:")
                    print("=" * 50)
                    
                    # Print main fields
                    print(f"🆔 BATNA ID: {data.get('batna_id', 'MISSING')}")
                    print(f"💰 Recommended Walkaway Point: {data.get('recommended_walkaway_point', 'MISSING')}")
                    
                    # Analyze alternatives
                    alternatives = data.get('alternatives', [])
                    print(f"\n📋 ALTERNATIVES ({len(alternatives)}/3 expected):")
                    for i, alt in enumerate(alternatives, 1):
                        print(f"  Alternative {i}:")
                        print(f"    🆔 ID: {alt.get('alt_id', 'MISSING')}")
                        print(f"    📝 Name: {alt.get('name', 'MISSING')}")
                        print(f"    📄 Description: {alt.get('description', 'MISSING')[:50]}...")
                        print(f"    💵 Expected Value: {alt.get('expected_value', 'MISSING')}")
                        print(f"    ⚠️  Risk: {alt.get('risk', 'MISSING')} (0-1 range)")
                        print(f"    ⏳ Time Cost (months): {alt.get('time_cost_months', 'MISSING')}")
                        print(f"    📊 Score: {alt.get('score', 'MISSING')} (0-1 range)")
                        print(f"    💹 ROI: {alt.get('roi', 'MISSING')}")
                        print(f"    🔧 Risk Adjusted Value: {alt.get('risk_adjusted_value', 'MISSING')}")
                        print(f"    🤝 Relationship Impact: {alt.get('relationship_impact', 'MISSING')} (-1 to 1 range)")
                        
                        # Analyze scenarios
                        scenarios = alt.get('scenarios', {})
                        print(f"    📈 Scenarios:")
                        for scenario_name in ['best', 'likely', 'worst']:
                            scenario = scenarios.get(scenario_name, {})
                            value = scenario.get('value', 'MISSING')
                            prob = scenario.get('prob', 'MISSING')
                            print(f"      {scenario_name.capitalize()}: value={value}, prob={prob}")
                        print()
                    
                    # Analyze decision notes
                    decision_notes = data.get('decision_notes', [])
                    print(f"📝 DECISION NOTES ({len(decision_notes)} items):")
                    for i, note in enumerate(decision_notes, 1):
                        print(f"  {i}. {note}")
                    
                    # Analyze decision tree
                    decision_tree = data.get('decision_tree', {})
                    print(f"\n🌳 DECISION TREE:")
                    print(f"  Name: {decision_tree.get('name', 'MISSING')}")
                    children = decision_tree.get('children', [])
                    print(f"  Children: {len(children)} items")
                    for i, child in enumerate(children, 1):
                        if isinstance(child, dict):
                            print(f"    {i}. {child.get('name', f'Child {i}')}")
                        else:
                            print(f"    {i}. {child}")
                    
                    # Analyze metrics
                    metrics = data.get('metrics', {})
                    print(f"\n📊 METRICS:")
                    print(f"  🏆 Best Alternative: {metrics.get('best_alternative', 'MISSING')}")
                    print(f"  📈 Best Score: {metrics.get('best_score', 'MISSING')}")
                    print(f"  ⚠️  Average Risk: {metrics.get('avg_risk', 'MISSING')}")
                    print(f"  💹 Average ROI: {metrics.get('avg_roi', 'MISSING')}")
                    
                    print("\n" + "=" * 50)
                    print("🎯 COMPLIANCE CHECK:")
                    
                    # Check compliance with review request requirements
                    compliance_issues = []
                    
                    # Check required top-level fields
                    required_fields = ['batna_id', 'alternatives', 'recommended_walkaway_point', 'decision_notes', 'decision_tree', 'metrics']
                    for field in required_fields:
                        if field not in data:
                            compliance_issues.append(f"Missing required field: {field}")
                    
                    # Check alternatives count
                    if len(alternatives) != 3:
                        compliance_issues.append(f"Expected 3 alternatives, got {len(alternatives)}")
                    
                    # Check alternative fields
                    alt_required_fields = ['alt_id', 'name', 'description', 'expected_value', 'risk', 'time_cost_months', 'score', 'roi', 'risk_adjusted_value', 'relationship_impact', 'scenarios']
                    for i, alt in enumerate(alternatives):
                        for field in alt_required_fields:
                            if field not in alt:
                                compliance_issues.append(f"Alternative {i+1} missing field: {field}")
                        
                        # Check scenarios
                        scenarios = alt.get('scenarios', {})
                        for scenario_name in ['best', 'likely', 'worst']:
                            if scenario_name not in scenarios:
                                compliance_issues.append(f"Alternative {i+1} missing scenario: {scenario_name}")
                            else:
                                scenario = scenarios[scenario_name]
                                if 'value' not in scenario or 'prob' not in scenario:
                                    compliance_issues.append(f"Alternative {i+1} scenario {scenario_name} missing value or prob")
                    
                    # Check metrics fields
                    metrics_required_fields = ['best_alternative', 'best_score', 'avg_risk', 'avg_roi']
                    for field in metrics_required_fields:
                        if field not in metrics:
                            compliance_issues.append(f"Metrics missing field: {field}")
                    
                    if compliance_issues:
                        print("❌ COMPLIANCE ISSUES FOUND:")
                        for issue in compliance_issues:
                            print(f"  • {issue}")
                        return False
                    else:
                        print("✅ ALL REQUIREMENTS MET - FULLY COMPLIANT")
                        return True
                        
                else:
                    error_text = await response.text()
                    print(f"❌ {test_name} - HTTP {response.status}: {error_text}")
                    return False
                    
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            print(f"❌ {test_name} - Timeout after {TIMEOUT}s")
            return False
        except Exception as e:
            response_time = time.time() - start_time
            print(f"❌ {test_name} - Error: {str(e)}")
            return False

async def main():
    """Main test execution"""
    async with BATNADetailedTester() as tester:
        success = await tester.test_batna_detailed_response()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)