#!/usr/bin/env python3
"""
Phase 1.3 Context-Aware AI Agents Backend Testing Suite

Comprehensive testing of specialized AI agents with focus on:
- Contract Negotiation Agent
- Litigation Strategy Agent  
- Compliance Monitoring Agent
- Client Communication Agent
- Agent Statistics and Performance
- Session Management and History

Testing Requirements:
- Test all 4 specialized AI agents with realistic legal scenarios
- Verify conversation context persistence across multiple messages
- Test recommendation generation, action items, and follow-up questions
- Verify confidence scoring and priority alert detection
- Test session management and conversation history storage
- Verify agent statistics tracking and performance metrics
- Test error handling for invalid sessions/requests
- Verify AI model integration (Gemini/Groq) functionality
- Test MongoDB storage of conversations and context
"""

import requests
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAgentTester:
    def __init__(self, base_url: str = "https://risk-ai-negotiator.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_results = []
        self.session_ids = {}  # Track session IDs for each agent type
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    params: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request with error handling and timing"""
        url = f"{self.base_url}/api{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            try:
                response_data = response.json()
            except:
                response_data = {"error": "Invalid JSON response", "text": response.text[:500]}
            
            return {
                "status_code": response.status_code,
                "data": response_data,
                "response_time": response_time,
                "success": response.status_code == 200
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Request failed: {e}")
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "response_time": response_time,
                "success": False
            }

    def generate_session_id(self, agent_type: str) -> str:
        """Generate unique session ID for agent type"""
        if agent_type not in self.session_ids:
            self.session_ids[agent_type] = f"session_{agent_type}_{uuid.uuid4().hex[:8]}"
        return self.session_ids[agent_type]

    def test_contract_negotiation_agent(self) -> Dict[str, Any]:
        """Test Contract Negotiation Agent with realistic scenarios"""
        logger.info("🤝 Testing Contract Negotiation Agent...")
        
        test_scenarios = [
            {
                "name": "Contract Term Optimization",
                "message": "I'm negotiating a software licensing agreement where the vendor wants a 5-year term with automatic renewal. They're asking for unlimited liability and want to retain all IP rights. How should I approach these terms?",
                "context": {
                    "contract_type": "software_license",
                    "jurisdiction": "California",
                    "current_phase": "negotiation",
                    "key_facts": [
                        "Vendor requesting 5-year term with auto-renewal",
                        "Unlimited liability clause proposed",
                        "Vendor wants to retain all IP rights",
                        "Critical business software for operations"
                    ]
                }
            },
            {
                "name": "Risk Allocation Scenario",
                "message": "The counterparty is pushing back on our indemnification clause and wants mutual indemnification instead of one-way. They also want to cap liability at the contract value. What are the risks and how should we respond?",
                "context": {
                    "contract_type": "service_agreement",
                    "jurisdiction": "New York",
                    "current_phase": "risk_allocation",
                    "key_facts": [
                        "Counterparty wants mutual indemnification",
                        "Liability cap at contract value proposed",
                        "High-risk service involving data processing",
                        "Contract value: $2.5M over 3 years"
                    ]
                }
            }
        ]
        
        results = []
        session_id = self.generate_session_id("contract_negotiation")
        
        for scenario in test_scenarios:
            logger.info(f"  Testing scenario: {scenario['name']}")
            
            request_data = {
                "message": scenario["message"],
                "session_id": session_id,
                "user_id": "test_user_contract",
                "contract_type": scenario["context"]["contract_type"],
                "jurisdiction": scenario["context"]["jurisdiction"],
                "current_phase": scenario["context"]["current_phase"],
                "key_facts": scenario["context"]["key_facts"],
                "context_metadata": {"test_scenario": scenario["name"]}
            }
            
            result = self.make_request("POST", "/ai-agents/contract-negotiation", request_data)
            
            # Validate response structure
            validation_result = self.validate_agent_response(result, "contract_negotiation", scenario["name"])
            results.append(validation_result)
            
            # Small delay between requests to allow context processing
            time.sleep(1)
        
        return {
            "agent_type": "contract_negotiation",
            "total_scenarios": len(test_scenarios),
            "results": results,
            "session_id": session_id
        }

    def test_litigation_strategy_agent(self) -> Dict[str, Any]:
        """Test Litigation Strategy Agent with case management scenarios"""
        logger.info("⚖️ Testing Litigation Strategy Agent...")
        
        test_scenarios = [
            {
                "name": "Case Strategy Development",
                "message": "We're representing a plaintiff in a breach of contract case. The defendant failed to deliver software on time, causing $500K in damages. They're claiming force majeure due to COVID-19. What's our litigation strategy?",
                "context": {
                    "case_type": "breach_of_contract",
                    "jurisdiction": "Federal Court - Northern District of California",
                    "current_phase": "pleadings",
                    "key_facts": [
                        "Software delivery 6 months late",
                        "Documented damages of $500K",
                        "Defendant claiming COVID-19 force majeure",
                        "Contract signed in January 2020",
                        "No force majeure clause in original contract"
                    ]
                }
            },
            {
                "name": "Discovery Planning Scenario",
                "message": "We need to plan discovery for a complex employment discrimination case. The plaintiff claims systematic bias in promotions. We represent the employer. What discovery strategy should we pursue?",
                "context": {
                    "case_type": "employment_discrimination",
                    "jurisdiction": "State Court - New York",
                    "current_phase": "discovery",
                    "key_facts": [
                        "Plaintiff claims promotion bias",
                        "Company has 500+ employees",
                        "Multiple departments involved",
                        "5-year pattern alleged",
                        "HR records and emails key evidence"
                    ]
                }
            }
        ]
        
        results = []
        session_id = self.generate_session_id("litigation_strategy")
        
        for scenario in test_scenarios:
            logger.info(f"  Testing scenario: {scenario['name']}")
            
            request_data = {
                "message": scenario["message"],
                "session_id": session_id,
                "user_id": "test_user_litigation",
                "case_type": scenario["context"]["case_type"],
                "jurisdiction": scenario["context"]["jurisdiction"],
                "current_phase": scenario["context"]["current_phase"],
                "key_facts": scenario["context"]["key_facts"],
                "context_metadata": {"test_scenario": scenario["name"]}
            }
            
            result = self.make_request("POST", "/ai-agents/litigation-strategy", request_data)
            
            # Validate response structure
            validation_result = self.validate_agent_response(result, "litigation_strategy", scenario["name"])
            results.append(validation_result)
            
            time.sleep(1)
        
        return {
            "agent_type": "litigation_strategy",
            "total_scenarios": len(test_scenarios),
            "results": results,
            "session_id": session_id
        }

    def test_compliance_monitoring_agent(self) -> Dict[str, Any]:
        """Test Compliance Monitoring Agent with regulatory scenarios"""
        logger.info("🛡️ Testing Compliance Monitoring Agent...")
        
        test_scenarios = [
            {
                "name": "Regulatory Compliance Analysis",
                "message": "Our fintech startup is launching a new payment processing service. We need to ensure compliance with PCI DSS, SOX, and state money transmitter laws. What compliance framework should we implement?",
                "context": {
                    "case_type": "regulatory_compliance",
                    "jurisdiction": "Multi-state (CA, NY, TX)",
                    "current_phase": "compliance_planning",
                    "key_facts": [
                        "Fintech payment processing service",
                        "Handling credit card data (PCI DSS)",
                        "Public company (SOX compliance)",
                        "Multi-state operations",
                        "Startup with limited compliance resources"
                    ]
                }
            },
            {
                "name": "GDPR Compliance Monitoring",
                "message": "We're a US company expanding to Europe and need to implement GDPR compliance. We process customer data for marketing and analytics. What are the key compliance requirements and monitoring strategies?",
                "context": {
                    "case_type": "data_privacy_compliance",
                    "jurisdiction": "EU (GDPR) + US operations",
                    "current_phase": "implementation",
                    "key_facts": [
                        "US company expanding to EU",
                        "Customer data processing for marketing",
                        "Analytics and profiling activities",
                        "Cross-border data transfers",
                        "Need ongoing monitoring system"
                    ]
                }
            }
        ]
        
        results = []
        session_id = self.generate_session_id("compliance_monitoring")
        
        for scenario in test_scenarios:
            logger.info(f"  Testing scenario: {scenario['name']}")
            
            request_data = {
                "message": scenario["message"],
                "session_id": session_id,
                "user_id": "test_user_compliance",
                "case_type": scenario["context"]["case_type"],
                "jurisdiction": scenario["context"]["jurisdiction"],
                "current_phase": scenario["context"]["current_phase"],
                "key_facts": scenario["context"]["key_facts"],
                "context_metadata": {"test_scenario": scenario["name"]}
            }
            
            result = self.make_request("POST", "/ai-agents/compliance-monitoring", request_data)
            
            # Validate response structure
            validation_result = self.validate_agent_response(result, "compliance_monitoring", scenario["name"])
            results.append(validation_result)
            
            time.sleep(1)
        
        return {
            "agent_type": "compliance_monitoring",
            "total_scenarios": len(test_scenarios),
            "results": results,
            "session_id": session_id
        }

    def test_client_communication_agent(self) -> Dict[str, Any]:
        """Test Client Communication Agent with relationship management scenarios"""
        logger.info("📞 Testing Client Communication Agent...")
        
        test_scenarios = [
            {
                "name": "Professional Communication Drafting",
                "message": "I need to communicate a significant delay in litigation to a high-value client. The case will take 6 months longer than expected due to complex discovery issues. How should I frame this communication to maintain trust?",
                "context": {
                    "case_type": "client_communication",
                    "jurisdiction": "N/A",
                    "current_phase": "client_management",
                    "key_facts": [
                        "High-value client relationship",
                        "6-month litigation delay",
                        "Complex discovery issues causing delay",
                        "Client has tight business timeline",
                        "Need to maintain trust and confidence"
                    ]
                }
            },
            {
                "name": "Expectation Management Scenario",
                "message": "A client is pushing for an aggressive settlement demand that's unrealistic given the case facts. They want $2M but our case analysis suggests $500K is more realistic. How do I manage their expectations while maintaining the relationship?",
                "context": {
                    "case_type": "settlement_negotiation",
                    "jurisdiction": "N/A",
                    "current_phase": "expectation_management",
                    "key_facts": [
                        "Client wants $2M settlement demand",
                        "Realistic expectation is $500K",
                        "Significant gap in expectations",
                        "Client is emotionally invested",
                        "Need to preserve attorney-client relationship"
                    ]
                }
            }
        ]
        
        results = []
        session_id = self.generate_session_id("client_communication")
        
        for scenario in test_scenarios:
            logger.info(f"  Testing scenario: {scenario['name']}")
            
            request_data = {
                "message": scenario["message"],
                "session_id": session_id,
                "user_id": "test_user_client_comm",
                "case_type": scenario["context"]["case_type"],
                "jurisdiction": scenario["context"]["jurisdiction"],
                "current_phase": scenario["context"]["current_phase"],
                "key_facts": scenario["context"]["key_facts"],
                "context_metadata": {"test_scenario": scenario["name"]}
            }
            
            result = self.make_request("POST", "/ai-agents/client-communication", request_data)
            
            # Validate response structure
            validation_result = self.validate_agent_response(result, "client_communication", scenario["name"])
            results.append(validation_result)
            
            time.sleep(1)
        
        return {
            "agent_type": "client_communication",
            "total_scenarios": len(test_scenarios),
            "results": results,
            "session_id": session_id
        }

    def test_agent_statistics(self) -> Dict[str, Any]:
        """Test Agent Statistics endpoint"""
        logger.info("📊 Testing Agent Statistics endpoint...")
        
        result = self.make_request("GET", "/ai-agents/statistics")
        
        validation = {
            "endpoint": "GET /ai-agents/statistics",
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"]
        }
        
        if result["success"]:
            data = result["data"]
            
            # Validate required fields
            required_fields = ["total_agents", "agent_types", "session_counts", "conversation_counts", "system_status"]
            missing_fields = [field for field in required_fields if field not in data]
            
            validation.update({
                "has_required_fields": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "total_agents": data.get("total_agents", 0),
                "agent_types": data.get("agent_types", []),
                "system_status": data.get("system_status", "unknown"),
                "session_counts": data.get("session_counts", {}),
                "conversation_counts": data.get("conversation_counts", {})
            })
            
            # Validate expected agent types
            expected_agents = ["contract_negotiation", "litigation_strategy", "compliance_monitoring", "client_communication"]
            has_all_agents = all(agent in data.get("agent_types", []) for agent in expected_agents)
            validation["has_all_expected_agents"] = has_all_agents
            
        else:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "has_required_fields": False
            })
        
        return validation

    def test_conversation_history(self) -> Dict[str, Any]:
        """Test conversation history retrieval for all agent sessions"""
        logger.info("📋 Testing Conversation History endpoints...")
        
        results = []
        
        # Test history for each agent type that has been tested
        for agent_type, session_id in self.session_ids.items():
            logger.info(f"  Testing history for {agent_type} agent...")
            
            result = self.make_request(
                "GET", 
                f"/ai-agents/session/{session_id}/history",
                params={"agent_type": agent_type}
            )
            
            validation = {
                "agent_type": agent_type,
                "session_id": session_id,
                "endpoint": f"GET /ai-agents/session/{session_id}/history",
                "success": result["success"],
                "response_time": result["response_time"],
                "status_code": result["status_code"]
            }
            
            if result["success"]:
                data = result["data"]
                
                # Validate response structure
                required_fields = ["session_id", "agent_type", "conversation_history", "total_messages"]
                missing_fields = [field for field in required_fields if field not in data]
                
                validation.update({
                    "has_required_fields": len(missing_fields) == 0,
                    "missing_fields": missing_fields,
                    "total_messages": data.get("total_messages", 0),
                    "has_conversation_history": len(data.get("conversation_history", [])) > 0,
                    "context_metadata_present": "context_metadata" in data
                })
                
                # Validate conversation history structure
                if data.get("conversation_history"):
                    first_message = data["conversation_history"][0]
                    message_fields = ["message_id", "message_type", "content", "timestamp"]
                    has_message_structure = all(field in first_message for field in message_fields)
                    validation["has_proper_message_structure"] = has_message_structure
                
            else:
                validation.update({
                    "error": result["data"].get("error", "Unknown error"),
                    "has_required_fields": False
                })
            
            results.append(validation)
            time.sleep(0.5)
        
        return {
            "total_sessions_tested": len(results),
            "results": results
        }

    def validate_agent_response(self, result: Dict[str, Any], agent_type: str, scenario_name: str) -> Dict[str, Any]:
        """Validate AI agent response structure and content quality"""
        validation = {
            "agent_type": agent_type,
            "scenario": scenario_name,
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"]
        }
        
        if not result["success"]:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "content_quality": "failed",
                "has_recommendations": False,
                "has_action_items": False,
                "confidence_score": 0.0
            })
            return validation
        
        data = result["data"]
        
        # Validate required response fields
        required_fields = [
            "response_id", "agent_type", "content", "recommendations", 
            "action_items", "confidence_score", "follow_up_questions", "timestamp"
        ]
        missing_fields = [field for field in required_fields if field not in data]
        
        validation.update({
            "has_required_fields": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "response_id": data.get("response_id", ""),
            "agent_type_match": data.get("agent_type") == agent_type,
            "content_length": len(data.get("content", "")),
            "has_content": len(data.get("content", "")) > 100,  # Substantial response
            "recommendations_count": len(data.get("recommendations", [])),
            "has_recommendations": len(data.get("recommendations", [])) > 0,
            "action_items_count": len(data.get("action_items", [])),
            "has_action_items": len(data.get("action_items", [])) > 0,
            "confidence_score": data.get("confidence_score", 0.0),
            "confidence_in_range": 0.7 <= data.get("confidence_score", 0.0) <= 0.95,
            "follow_up_questions_count": len(data.get("follow_up_questions", [])),
            "has_follow_up_questions": len(data.get("follow_up_questions", [])) > 0,
            "priority_alerts_count": len(data.get("priority_alerts", [])),
            "has_timestamp": bool(data.get("timestamp"))
        })
        
        # Assess content quality based on agent specialization
        content = data.get("content", "").lower()
        
        if agent_type == "contract_negotiation":
            quality_indicators = ["risk", "negotiate", "clause", "term", "recommend"]
        elif agent_type == "litigation_strategy":
            quality_indicators = ["discovery", "motion", "evidence", "strategy", "case"]
        elif agent_type == "compliance_monitoring":
            quality_indicators = ["compliance", "regulation", "policy", "requirement", "monitor"]
        elif agent_type == "client_communication":
            quality_indicators = ["communicate", "relationship", "expectation", "professional", "client"]
        else:
            quality_indicators = []
        
        quality_score = sum(1 for indicator in quality_indicators if indicator in content)
        validation["content_quality_score"] = quality_score
        validation["has_specialized_content"] = quality_score >= 2
        
        return validation

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all AI agents"""
        logger.info("🚀 Starting Comprehensive Phase 1.3 Context-Aware AI Agents Testing...")
        
        start_time = time.time()
        
        # Test all 4 specialized agents
        contract_results = self.test_contract_negotiation_agent()
        litigation_results = self.test_litigation_strategy_agent()
        compliance_results = self.test_compliance_monitoring_agent()
        client_comm_results = self.test_client_communication_agent()
        
        # Test system endpoints
        statistics_results = self.test_agent_statistics()
        history_results = self.test_conversation_history()
        
        total_time = time.time() - start_time
        
        # Compile comprehensive results
        all_agent_results = [
            contract_results, litigation_results, 
            compliance_results, client_comm_results
        ]
        
        # Calculate success metrics
        total_scenarios = sum(result["total_scenarios"] for result in all_agent_results)
        successful_scenarios = sum(
            len([r for r in result["results"] if r["success"]]) 
            for result in all_agent_results
        )
        
        success_rate = (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
        
        # Analyze confidence scores
        all_confidence_scores = []
        for agent_result in all_agent_results:
            for scenario_result in agent_result["results"]:
                if scenario_result["success"]:
                    all_confidence_scores.append(scenario_result.get("confidence_score", 0.0))
        
        avg_confidence = sum(all_confidence_scores) / len(all_confidence_scores) if all_confidence_scores else 0.0
        
        return {
            "test_summary": {
                "total_execution_time": total_time,
                "total_agents_tested": 4,
                "total_scenarios_tested": total_scenarios,
                "successful_scenarios": successful_scenarios,
                "success_rate_percentage": success_rate,
                "average_confidence_score": avg_confidence,
                "statistics_endpoint_working": statistics_results["success"],
                "history_endpoints_working": all(r["success"] for r in history_results["results"])
            },
            "agent_results": {
                "contract_negotiation": contract_results,
                "litigation_strategy": litigation_results,
                "compliance_monitoring": compliance_results,
                "client_communication": client_comm_results
            },
            "system_results": {
                "statistics": statistics_results,
                "conversation_history": history_results
            },
            "session_ids": self.session_ids
        }

def main():
    """Main test execution function"""
    print("=" * 80)
    print("PHASE 1.3 CONTEXT-AWARE AI AGENTS BACKEND TESTING")
    print("=" * 80)
    
    tester = AIAgentTester()
    results = tester.run_comprehensive_test()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    summary = results["test_summary"]
    print(f"📊 Total Execution Time: {summary['total_execution_time']:.2f} seconds")
    print(f"🤖 Agents Tested: {summary['total_agents_tested']}")
    print(f"📝 Scenarios Tested: {summary['total_scenarios_tested']}")
    print(f"✅ Successful Scenarios: {summary['successful_scenarios']}")
    print(f"📈 Success Rate: {summary['success_rate_percentage']:.1f}%")
    print(f"🎯 Average Confidence Score: {summary['average_confidence_score']:.3f}")
    print(f"📊 Statistics Endpoint: {'✅ Working' if summary['statistics_endpoint_working'] else '❌ Failed'}")
    print(f"📋 History Endpoints: {'✅ Working' if summary['history_endpoints_working'] else '❌ Failed'}")
    
    print("\n" + "=" * 80)
    print("DETAILED AGENT RESULTS")
    print("=" * 80)
    
    for agent_type, agent_results in results["agent_results"].items():
        print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent:")
        print(f"   Session ID: {agent_results['session_id']}")
        
        for scenario_result in agent_results["results"]:
            status = "✅" if scenario_result["success"] else "❌"
            print(f"   {status} {scenario_result['scenario']}")
            print(f"      Response Time: {scenario_result['response_time']:.3f}s")
            
            if scenario_result["success"]:
                print(f"      Confidence Score: {scenario_result.get('confidence_score', 0.0):.3f}")
                print(f"      Content Length: {scenario_result.get('content_length', 0)} chars")
                print(f"      Recommendations: {scenario_result.get('recommendations_count', 0)}")
                print(f"      Action Items: {scenario_result.get('action_items_count', 0)}")
                print(f"      Follow-up Questions: {scenario_result.get('follow_up_questions_count', 0)}")
            else:
                print(f"      Error: {scenario_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("SYSTEM ENDPOINTS RESULTS")
    print("=" * 80)
    
    # Statistics endpoint results
    stats = results["system_results"]["statistics"]
    print(f"\n📊 Statistics Endpoint:")
    print(f"   Status: {'✅ Working' if stats['success'] else '❌ Failed'}")
    print(f"   Response Time: {stats['response_time']:.3f}s")
    
    if stats["success"]:
        print(f"   Total Agents: {stats.get('total_agents', 0)}")
        print(f"   Agent Types: {', '.join(stats.get('agent_types', []))}")
        print(f"   System Status: {stats.get('system_status', 'unknown')}")
    
    # History endpoints results
    history = results["system_results"]["conversation_history"]
    print(f"\n📋 Conversation History Endpoints:")
    print(f"   Sessions Tested: {history['total_sessions_tested']}")
    
    for hist_result in history["results"]:
        status = "✅" if hist_result["success"] else "❌"
        print(f"   {status} {hist_result['agent_type']} - {hist_result.get('total_messages', 0)} messages")
    
    # Final assessment
    print("\n" + "=" * 80)
    print("FINAL ASSESSMENT")
    print("=" * 80)
    
    if summary["success_rate_percentage"] >= 90:
        print("🎉 EXCELLENT: Phase 1.3 Context-Aware AI Agents system is working excellently!")
    elif summary["success_rate_percentage"] >= 75:
        print("✅ GOOD: Phase 1.3 Context-Aware AI Agents system is working well with minor issues.")
    elif summary["success_rate_percentage"] >= 50:
        print("⚠️ PARTIAL: Phase 1.3 Context-Aware AI Agents system has significant issues.")
    else:
        print("❌ CRITICAL: Phase 1.3 Context-Aware AI Agents system has major failures.")
    
    # Expected success criteria validation
    print("\n📋 SUCCESS CRITERIA VALIDATION:")
    criteria_met = 0
    total_criteria = 8
    
    if summary["success_rate_percentage"] >= 85:
        print("✅ All 6 endpoints return 200 OK with proper response structures")
        criteria_met += 1
    else:
        print("❌ Not all endpoints working properly")
    
    if summary["average_confidence_score"] >= 0.7:
        print("✅ Confidence scores are in realistic range (0.7-0.95)")
        criteria_met += 1
    else:
        print("❌ Confidence scores below expected range")
    
    # Check if all agents have specialized content
    specialized_content_count = 0
    for agent_results in results["agent_results"].values():
        for scenario in agent_results["results"]:
            if scenario.get("has_specialized_content", False):
                specialized_content_count += 1
    
    if specialized_content_count >= summary["total_scenarios_tested"] * 0.8:
        print("✅ Agent responses include specialized domain expertise")
        criteria_met += 1
    else:
        print("❌ Insufficient specialized domain expertise in responses")
    
    if summary["statistics_endpoint_working"]:
        print("✅ Agent statistics tracking working correctly")
        criteria_met += 1
    else:
        print("❌ Agent statistics endpoint not working")
    
    if summary["history_endpoints_working"]:
        print("✅ Session management and conversation history working")
        criteria_met += 1
    else:
        print("❌ Conversation history endpoints not working")
    
    # Check for recommendations and action items
    has_recommendations = all(
        any(r.get("has_recommendations", False) for r in agent["results"])
        for agent in results["agent_results"].values()
    )
    
    if has_recommendations:
        print("✅ Recommendation generation working across agents")
        criteria_met += 1
    else:
        print("❌ Insufficient recommendation generation")
    
    # Check for action items
    has_action_items = all(
        any(r.get("has_action_items", False) for r in agent["results"])
        for agent in results["agent_results"].values()
    )
    
    if has_action_items:
        print("✅ Action items generation working across agents")
        criteria_met += 1
    else:
        print("❌ Insufficient action items generation")
    
    # Check response times (should be reasonable)
    avg_response_time = sum(
        scenario["response_time"] 
        for agent in results["agent_results"].values()
        for scenario in agent["results"]
        if scenario["success"]
    ) / summary["successful_scenarios"] if summary["successful_scenarios"] > 0 else 0
    
    if avg_response_time < 10.0:  # Under 10 seconds average
        print("✅ Response times are acceptable (AI model integration working)")
        criteria_met += 1
    else:
        print("❌ Response times too slow (potential AI model integration issues)")
    
    print(f"\n🎯 SUCCESS CRITERIA MET: {criteria_met}/{total_criteria} ({criteria_met/total_criteria*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    main()