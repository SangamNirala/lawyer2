#!/usr/bin/env python3
"""
Context-Aware AI Agents Backend Testing Suite
Testing all AI Agent Hub endpoints as requested in review.

Focus Areas:
1. GET /api/ai-agents/statistics - Agent statistics
2. POST /api/ai-agents/contract-negotiation - Contract negotiation agent
3. POST /api/ai-agents/litigation-strategy - Litigation strategy agent  
4. POST /api/ai-agents/compliance-monitoring - Compliance monitoring agent
5. POST /api/ai-agents/client-communication - Client communication agent
6. GET /api/ai-agents/session/{session_id}/history - Session history retrieval

Root Cause Investigation:
- Frontend showing "I apologize, but I'm experiencing technical difficulties"
- Investigating AI/LLM integration issues, API endpoints, dependencies, database connections
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

class AIAgentEndpointTester:
    def __init__(self, base_url: str = "https://sector-insight.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_results = []
        self.session_ids = {}
        
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    params: Optional[Dict] = None, timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request with comprehensive error handling"""
        url = f"{self.base_url}/api{endpoint}"
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Making {method} request to {endpoint}")
            
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
            
            logger.info(f"✅ Response: {response.status_code} in {response_time:.3f}s")
            
            return {
                "status_code": response.status_code,
                "data": response_data,
                "response_time": response_time,
                "success": response.status_code == 200,
                "url": url
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Request failed: {e}")
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "response_time": response_time,
                "success": False,
                "url": url
            }

    def test_agent_statistics(self) -> Dict[str, Any]:
        """Test GET /api/ai-agents/statistics endpoint"""
        logger.info("📊 Testing Agent Statistics endpoint...")
        
        result = self.make_request("GET", "/ai-agents/statistics")
        
        validation = {
            "test_name": "Agent Statistics",
            "endpoint": "GET /api/ai-agents/statistics",
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"],
            "url": result["url"]
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
                "conversation_counts": data.get("conversation_counts", {}),
                "response_data": data
            })
            
            # Validate expected agent types
            expected_agents = ["contract_negotiation", "litigation_strategy", "compliance_monitoring", "client_communication"]
            has_all_agents = all(agent in data.get("agent_types", []) for agent in expected_agents)
            validation["has_all_expected_agents"] = has_all_agents
            
        else:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "has_required_fields": False,
                "response_data": result["data"]
            })
        
        return validation

    def test_contract_negotiation_agent(self) -> Dict[str, Any]:
        """Test POST /api/ai-agents/contract-negotiation endpoint"""
        logger.info("🤝 Testing Contract Negotiation Agent...")
        
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.session_ids["contract_negotiation"] = session_id
        
        test_data = {
            "message": "Help me with contract terms for a software licensing agreement",
            "session_id": session_id,
            "case_id": None,
            "contract_id": None,
            "jurisdiction": "US",
            "case_type": None,
            "contract_type": "software_license"
        }
        
        result = self.make_request("POST", "/ai-agents/contract-negotiation", test_data)
        
        validation = {
            "test_name": "Contract Negotiation Agent",
            "endpoint": "POST /api/ai-agents/contract-negotiation",
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"],
            "url": result["url"],
            "session_id": session_id
        }
        
        if result["success"]:
            data = result["data"]
            
            # Validate expected response structure
            required_fields = [
                "response_id", "agent_type", "content", "recommendations", 
                "action_items", "confidence_score", "follow_up_questions", "timestamp"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            
            validation.update({
                "has_required_fields": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "response_id": data.get("response_id", ""),
                "agent_type": data.get("agent_type", ""),
                "content": data.get("content", ""),
                "content_length": len(data.get("content", "")),
                "recommendations_count": len(data.get("recommendations", [])),
                "action_items_count": len(data.get("action_items", [])),
                "confidence_score": data.get("confidence_score", 0.0),
                "follow_up_questions_count": len(data.get("follow_up_questions", [])),
                "priority_alerts_count": len(data.get("priority_alerts", [])),
                "has_timestamp": bool(data.get("timestamp")),
                "response_data": data
            })
            
            # Check for technical difficulties message
            content = data.get("content", "").lower()
            validation["has_technical_difficulties"] = "technical difficulties" in content
            validation["is_fallback_response"] = "apologize" in content and "technical difficulties" in content
            
        else:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "has_required_fields": False,
                "response_data": result["data"]
            })
        
        return validation

    def test_litigation_strategy_agent(self) -> Dict[str, Any]:
        """Test POST /api/ai-agents/litigation-strategy endpoint"""
        logger.info("⚖️ Testing Litigation Strategy Agent...")
        
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.session_ids["litigation_strategy"] = session_id
        
        test_data = {
            "message": "Help me develop a litigation strategy for a breach of contract case",
            "session_id": session_id,
            "case_id": None,
            "contract_id": None,
            "jurisdiction": "US",
            "case_type": "breach_of_contract",
            "contract_type": None
        }
        
        result = self.make_request("POST", "/ai-agents/litigation-strategy", test_data)
        
        validation = {
            "test_name": "Litigation Strategy Agent",
            "endpoint": "POST /api/ai-agents/litigation-strategy",
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"],
            "url": result["url"],
            "session_id": session_id
        }
        
        if result["success"]:
            data = result["data"]
            
            required_fields = [
                "response_id", "agent_type", "content", "recommendations", 
                "action_items", "confidence_score", "follow_up_questions", "timestamp"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            
            validation.update({
                "has_required_fields": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "response_id": data.get("response_id", ""),
                "agent_type": data.get("agent_type", ""),
                "content": data.get("content", ""),
                "content_length": len(data.get("content", "")),
                "recommendations_count": len(data.get("recommendations", [])),
                "action_items_count": len(data.get("action_items", [])),
                "confidence_score": data.get("confidence_score", 0.0),
                "follow_up_questions_count": len(data.get("follow_up_questions", [])),
                "priority_alerts_count": len(data.get("priority_alerts", [])),
                "has_timestamp": bool(data.get("timestamp")),
                "response_data": data
            })
            
            # Check for technical difficulties message
            content = data.get("content", "").lower()
            validation["has_technical_difficulties"] = "technical difficulties" in content
            validation["is_fallback_response"] = "apologize" in content and "technical difficulties" in content
            
        else:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "has_required_fields": False,
                "response_data": result["data"]
            })
        
        return validation

    def test_compliance_monitoring_agent(self) -> Dict[str, Any]:
        """Test POST /api/ai-agents/compliance-monitoring endpoint"""
        logger.info("🛡️ Testing Compliance Monitoring Agent...")
        
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.session_ids["compliance_monitoring"] = session_id
        
        test_data = {
            "message": "Help me ensure compliance with GDPR regulations for our data processing",
            "session_id": session_id,
            "case_id": None,
            "contract_id": None,
            "jurisdiction": "EU",
            "case_type": "compliance_monitoring",
            "contract_type": None
        }
        
        result = self.make_request("POST", "/ai-agents/compliance-monitoring", test_data)
        
        validation = {
            "test_name": "Compliance Monitoring Agent",
            "endpoint": "POST /api/ai-agents/compliance-monitoring",
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"],
            "url": result["url"],
            "session_id": session_id
        }
        
        if result["success"]:
            data = result["data"]
            
            required_fields = [
                "response_id", "agent_type", "content", "recommendations", 
                "action_items", "confidence_score", "follow_up_questions", "timestamp"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            
            validation.update({
                "has_required_fields": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "response_id": data.get("response_id", ""),
                "agent_type": data.get("agent_type", ""),
                "content": data.get("content", ""),
                "content_length": len(data.get("content", "")),
                "recommendations_count": len(data.get("recommendations", [])),
                "action_items_count": len(data.get("action_items", [])),
                "confidence_score": data.get("confidence_score", 0.0),
                "follow_up_questions_count": len(data.get("follow_up_questions", [])),
                "priority_alerts_count": len(data.get("priority_alerts", [])),
                "has_timestamp": bool(data.get("timestamp")),
                "response_data": data
            })
            
            # Check for technical difficulties message
            content = data.get("content", "").lower()
            validation["has_technical_difficulties"] = "technical difficulties" in content
            validation["is_fallback_response"] = "apologize" in content and "technical difficulties" in content
            
        else:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "has_required_fields": False,
                "response_data": result["data"]
            })
        
        return validation

    def test_client_communication_agent(self) -> Dict[str, Any]:
        """Test POST /api/ai-agents/client-communication endpoint"""
        logger.info("📞 Testing Client Communication Agent...")
        
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.session_ids["client_communication"] = session_id
        
        test_data = {
            "message": "Help me draft a professional communication to update a client on case progress",
            "session_id": session_id,
            "case_id": None,
            "contract_id": None,
            "jurisdiction": "US",
            "case_type": "client_communication",
            "contract_type": None
        }
        
        result = self.make_request("POST", "/ai-agents/client-communication", test_data)
        
        validation = {
            "test_name": "Client Communication Agent",
            "endpoint": "POST /api/ai-agents/client-communication",
            "success": result["success"],
            "response_time": result["response_time"],
            "status_code": result["status_code"],
            "url": result["url"],
            "session_id": session_id
        }
        
        if result["success"]:
            data = result["data"]
            
            required_fields = [
                "response_id", "agent_type", "content", "recommendations", 
                "action_items", "confidence_score", "follow_up_questions", "timestamp"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            
            validation.update({
                "has_required_fields": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "response_id": data.get("response_id", ""),
                "agent_type": data.get("agent_type", ""),
                "content": data.get("content", ""),
                "content_length": len(data.get("content", "")),
                "recommendations_count": len(data.get("recommendations", [])),
                "action_items_count": len(data.get("action_items", [])),
                "confidence_score": data.get("confidence_score", 0.0),
                "follow_up_questions_count": len(data.get("follow_up_questions", [])),
                "priority_alerts_count": len(data.get("priority_alerts", [])),
                "has_timestamp": bool(data.get("timestamp")),
                "response_data": data
            })
            
            # Check for technical difficulties message
            content = data.get("content", "").lower()
            validation["has_technical_difficulties"] = "technical difficulties" in content
            validation["is_fallback_response"] = "apologize" in content and "technical difficulties" in content
            
        else:
            validation.update({
                "error": result["data"].get("error", "Unknown error"),
                "has_required_fields": False,
                "response_data": result["data"]
            })
        
        return validation

    def test_session_history(self) -> Dict[str, Any]:
        """Test GET /api/ai-agents/session/{session_id}/history endpoint"""
        logger.info("📋 Testing Session History endpoints...")
        
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
                "test_name": f"Session History - {agent_type}",
                "agent_type": agent_type,
                "session_id": session_id,
                "endpoint": f"GET /api/ai-agents/session/{session_id}/history",
                "success": result["success"],
                "response_time": result["response_time"],
                "status_code": result["status_code"],
                "url": result["url"]
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
                    "context_metadata_present": "context_metadata" in data,
                    "response_data": data
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
                    "has_required_fields": False,
                    "response_data": result["data"]
                })
            
            results.append(validation)
            time.sleep(0.5)
        
        return {
            "test_name": "Session History Endpoints",
            "total_sessions_tested": len(results),
            "results": results
        }

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite for all AI agent endpoints"""
        logger.info("🚀 Starting Comprehensive AI Agent Hub Endpoint Testing...")
        
        start_time = time.time()
        
        # Test all endpoints as specified in review request
        statistics_result = self.test_agent_statistics()
        contract_result = self.test_contract_negotiation_agent()
        litigation_result = self.test_litigation_strategy_agent()
        compliance_result = self.test_compliance_monitoring_agent()
        client_comm_result = self.test_client_communication_agent()
        history_result = self.test_session_history()
        
        total_time = time.time() - start_time
        
        # Compile results
        all_tests = [
            statistics_result,
            contract_result,
            litigation_result,
            compliance_result,
            client_comm_result
        ]
        
        # Add history test results
        all_tests.extend(history_result["results"])
        
        # Calculate success metrics
        successful_tests = sum(1 for test in all_tests if test["success"])
        total_tests = len(all_tests)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Analyze technical difficulties
        agent_tests = [contract_result, litigation_result, compliance_result, client_comm_result]
        technical_difficulties_count = sum(1 for test in agent_tests if test.get("has_technical_difficulties", False))
        
        return {
            "test_summary": {
                "total_execution_time": total_time,
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate_percentage": success_rate,
                "technical_difficulties_detected": technical_difficulties_count,
                "all_agents_have_technical_difficulties": technical_difficulties_count == 4
            },
            "individual_results": {
                "statistics": statistics_result,
                "contract_negotiation": contract_result,
                "litigation_strategy": litigation_result,
                "compliance_monitoring": compliance_result,
                "client_communication": client_comm_result,
                "session_history": history_result
            },
            "session_ids": self.session_ids
        }

def main():
    """Main test execution function"""
    print("=" * 80)
    print("CONTEXT-AWARE AI AGENTS BACKEND TESTING")
    print("Testing AI Agent Hub Endpoints - Root Cause Investigation")
    print("=" * 80)
    
    tester = AIAgentEndpointTester()
    results = tester.run_comprehensive_test()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    summary = results["test_summary"]
    print(f"📊 Total Execution Time: {summary['total_execution_time']:.2f} seconds")
    print(f"🧪 Total Tests: {summary['total_tests']}")
    print(f"✅ Successful Tests: {summary['successful_tests']}")
    print(f"📈 Success Rate: {summary['success_rate_percentage']:.1f}%")
    print(f"⚠️ Technical Difficulties Detected: {summary['technical_difficulties_detected']}/4 agents")
    
    if summary['all_agents_have_technical_difficulties']:
        print("🚨 CRITICAL: All agents returning technical difficulties message")
    
    print("\n" + "=" * 80)
    print("DETAILED ENDPOINT RESULTS")
    print("=" * 80)
    
    individual = results["individual_results"]
    
    # Statistics endpoint
    stats = individual["statistics"]
    print(f"\n📊 Agent Statistics Endpoint:")
    print(f"   Status: {'✅ Working' if stats['success'] else '❌ Failed'}")
    print(f"   Response Time: {stats['response_time']:.3f}s")
    if stats["success"]:
        print(f"   Total Agents: {stats.get('total_agents', 0)}")
        print(f"   Agent Types: {', '.join(stats.get('agent_types', []))}")
        print(f"   System Status: {stats.get('system_status', 'unknown')}")
    else:
        print(f"   Error: {stats.get('error', 'Unknown error')}")
    
    # Agent endpoints
    agent_tests = ["contract_negotiation", "litigation_strategy", "compliance_monitoring", "client_communication"]
    for agent_type in agent_tests:
        result = individual[agent_type]
        print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent:")
        print(f"   Status: {'✅ Working' if result['success'] else '❌ Failed'}")
        print(f"   Response Time: {result['response_time']:.3f}s")
        
        if result["success"]:
            print(f"   Content Length: {result.get('content_length', 0)} chars")
            print(f"   Confidence Score: {result.get('confidence_score', 0.0):.3f}")
            print(f"   Recommendations: {result.get('recommendations_count', 0)}")
            print(f"   Action Items: {result.get('action_items_count', 0)}")
            print(f"   Follow-up Questions: {result.get('follow_up_questions_count', 0)}")
            
            if result.get("has_technical_difficulties", False):
                print(f"   ⚠️ ISSUE: Returning technical difficulties message")
                print(f"   🔍 Content Preview: {result.get('content', '')[:100]}...")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Session history endpoints
    history = individual["session_history"]
    print(f"\n📋 Session History Endpoints:")
    print(f"   Sessions Tested: {history['total_sessions_tested']}")
    
    for hist_result in history["results"]:
        status = "✅" if hist_result["success"] else "❌"
        print(f"   {status} {hist_result['agent_type']} - {hist_result.get('total_messages', 0)} messages")
    
    # Root cause analysis
    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS")
    print("=" * 80)
    
    if summary['all_agents_have_technical_difficulties']:
        print("🔍 DIAGNOSIS: AI/LLM Integration Issues Detected")
        print("   - All 4 agents returning fallback error message")
        print("   - Content length consistently 83 characters (fallback message)")
        print("   - No recommendations or action items generated")
        print("   - Confidence scores present but content is fallback")
        print()
        print("🚨 LIKELY CAUSES:")
        print("   1. AI API quota exceeded (Gemini: 429 quota error)")
        print("   2. Invalid API keys (Groq: 401 invalid API key)")
        print("   3. Network connectivity issues to AI services")
        print("   4. Missing dependencies or configuration")
        print()
        print("💡 RECOMMENDED ACTIONS:")
        print("   1. Check and update AI API keys (Gemini, Groq)")
        print("   2. Verify API quotas and billing status")
        print("   3. Test AI service connectivity")
        print("   4. Review environment variable configuration")
    else:
        print("✅ AI agents are functioning normally")
    
    # Final assessment
    print("\n" + "=" * 80)
    print("FINAL ASSESSMENT")
    print("=" * 80)
    
    if summary["success_rate_percentage"] >= 90:
        print("🎉 EXCELLENT: All AI Agent Hub endpoints are working correctly!")
    elif summary["success_rate_percentage"] >= 75:
        print("✅ GOOD: Most AI Agent Hub endpoints are working with minor issues.")
    elif summary["success_rate_percentage"] >= 50:
        print("⚠️ PARTIAL: AI Agent Hub endpoints have significant issues.")
    else:
        print("❌ CRITICAL: AI Agent Hub endpoints have major failures.")
    
    # Expected response structure validation
    print("\n📋 RESPONSE STRUCTURE VALIDATION:")
    
    structure_valid = True
    for agent_type in agent_tests:
        result = individual[agent_type]
        if result["success"] and result.get("has_required_fields", False):
            print(f"✅ {agent_type}: All required fields present")
        else:
            print(f"❌ {agent_type}: Missing fields - {result.get('missing_fields', [])}")
            structure_valid = False
    
    if structure_valid:
        print("✅ All agents return proper response structures")
    else:
        print("❌ Some agents have incomplete response structures")
    
    return results

if __name__ == "__main__":
    main()