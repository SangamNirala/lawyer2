#!/usr/bin/env python3
"""
AI Agent Hub Backend Testing Script
Tests the AI Agent Hub endpoints after libmagic dependency fix
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://clever-jepsen.preview.emergentagent.com/api"

def test_ai_agent_statistics():
    """Test GET /api/ai-agents/statistics endpoint"""
    print("\n🔍 Testing AI Agent Statistics Endpoint...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/ai-agents/statistics", timeout=10)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # Verify required fields
            required_fields = ['total_agents', 'agent_types', 'system_status']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify agent types
            expected_agents = ['contract_negotiation', 'litigation_strategy', 'compliance_monitoring', 'client_communication']
            if 'agent_types' in data and isinstance(data['agent_types'], list):
                for agent in expected_agents:
                    if agent not in data['agent_types']:
                        print(f"❌ Missing expected agent type: {agent}")
                        return False
            
            print("✅ AI Agent Statistics endpoint working correctly")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing statistics endpoint: {str(e)}")
        return False

def test_contract_negotiation_agent():
    """Test POST /api/ai-agents/contract-negotiation endpoint"""
    print("\n🔍 Testing Contract Negotiation Agent Endpoint...")
    
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        payload = {
            "message": "I need help negotiating a software licensing agreement. The vendor is asking for $50,000 annually with a 3-year commitment. What are my negotiation options?",
            "session_id": session_id
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/ai-agents/contract-negotiation",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Length: {len(str(data))} characters")
            
            # Verify required response structure
            required_fields = ['response_id', 'agent_type', 'content', 'recommendations', 
                             'action_items', 'confidence_score', 'follow_up_questions', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, session_id
            
            # Verify confidence score range
            if 'confidence_score' in data:
                confidence = data['confidence_score']
                if not (0.0 <= confidence <= 1.0):
                    print(f"❌ Confidence score {confidence} not in range 0.0-1.0")
                    return False, session_id
            
            # Verify agent type
            if data.get('agent_type') != 'contract_negotiation':
                print(f"❌ Wrong agent type: {data.get('agent_type')}")
                return False, session_id
            
            # Check for meaningful content (not fallback message)
            content = data.get('content', '')
            if 'technical difficulties' in content.lower() or len(content) < 100:
                print(f"❌ Appears to be fallback response: {content[:100]}...")
                return False, session_id
            
            print(f"✅ Contract Negotiation Agent working correctly")
            print(f"   Agent Type: {data.get('agent_type')}")
            print(f"   Confidence Score: {data.get('confidence_score')}")
            print(f"   Content Length: {len(content)} characters")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
            print(f"   Action Items: {len(data.get('action_items', []))}")
            print(f"   Follow-up Questions: {len(data.get('follow_up_questions', []))}")
            
            return True, session_id
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False, session_id
            
    except Exception as e:
        print(f"❌ Error testing contract negotiation endpoint: {str(e)}")
        return False, session_id

def test_litigation_strategy_agent():
    """Test POST /api/ai-agents/litigation-strategy endpoint"""
    print("\n🔍 Testing Litigation Strategy Agent Endpoint...")
    
    try:
        session_id = str(uuid.uuid4())
        
        payload = {
            "message": "I'm facing a breach of contract lawsuit. The plaintiff claims we failed to deliver services on time, but we have evidence of their delayed payments. What litigation strategy should I consider?",
            "session_id": session_id
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/ai-agents/litigation-strategy",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required response structure
            required_fields = ['response_id', 'agent_type', 'content', 'recommendations', 
                             'action_items', 'confidence_score', 'follow_up_questions', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, session_id
            
            # Verify agent type
            if data.get('agent_type') != 'litigation_strategy':
                print(f"❌ Wrong agent type: {data.get('agent_type')}")
                return False, session_id
            
            # Check for meaningful content
            content = data.get('content', '')
            if 'technical difficulties' in content.lower() or len(content) < 100:
                print(f"❌ Appears to be fallback response: {content[:100]}...")
                return False, session_id
            
            print(f"✅ Litigation Strategy Agent working correctly")
            print(f"   Agent Type: {data.get('agent_type')}")
            print(f"   Confidence Score: {data.get('confidence_score')}")
            print(f"   Content Length: {len(content)} characters")
            
            return True, session_id
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False, session_id
            
    except Exception as e:
        print(f"❌ Error testing litigation strategy endpoint: {str(e)}")
        return False, session_id

def test_compliance_monitoring_agent():
    """Test POST /api/ai-agents/compliance-monitoring endpoint"""
    print("\n🔍 Testing Compliance Monitoring Agent Endpoint...")
    
    try:
        session_id = str(uuid.uuid4())
        
        payload = {
            "message": "Our company is expanding to Europe and we need to ensure GDPR compliance for our data processing activities. What compliance monitoring strategies should we implement?",
            "session_id": session_id
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/ai-agents/compliance-monitoring",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required response structure
            required_fields = ['response_id', 'agent_type', 'content', 'recommendations', 
                             'action_items', 'confidence_score', 'follow_up_questions', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, session_id
            
            # Verify agent type
            if data.get('agent_type') != 'compliance_monitoring':
                print(f"❌ Wrong agent type: {data.get('agent_type')}")
                return False, session_id
            
            # Check for meaningful content
            content = data.get('content', '')
            if 'technical difficulties' in content.lower() or len(content) < 100:
                print(f"❌ Appears to be fallback response: {content[:100]}...")
                return False, session_id
            
            print(f"✅ Compliance Monitoring Agent working correctly")
            print(f"   Agent Type: {data.get('agent_type')}")
            print(f"   Confidence Score: {data.get('confidence_score')}")
            print(f"   Content Length: {len(content)} characters")
            
            return True, session_id
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False, session_id
            
    except Exception as e:
        print(f"❌ Error testing compliance monitoring endpoint: {str(e)}")
        return False, session_id

def test_client_communication_agent():
    """Test POST /api/ai-agents/client-communication endpoint"""
    print("\n🔍 Testing Client Communication Agent Endpoint...")
    
    try:
        session_id = str(uuid.uuid4())
        
        payload = {
            "message": "I need to draft a professional email to a client explaining a delay in contract execution due to regulatory approval requirements. How should I communicate this sensitively while maintaining their confidence?",
            "session_id": session_id
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/ai-agents/client-communication",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required response structure
            required_fields = ['response_id', 'agent_type', 'content', 'recommendations', 
                             'action_items', 'confidence_score', 'follow_up_questions', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, session_id
            
            # Verify agent type
            if data.get('agent_type') != 'client_communication':
                print(f"❌ Wrong agent type: {data.get('agent_type')}")
                return False, session_id
            
            # Check for meaningful content
            content = data.get('content', '')
            if 'technical difficulties' in content.lower() or len(content) < 100:
                print(f"❌ Appears to be fallback response: {content[:100]}...")
                return False, session_id
            
            print(f"✅ Client Communication Agent working correctly")
            print(f"   Agent Type: {data.get('agent_type')}")
            print(f"   Confidence Score: {data.get('confidence_score')}")
            print(f"   Content Length: {len(content)} characters")
            
            return True, session_id
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False, session_id
            
    except Exception as e:
        print(f"❌ Error testing client communication endpoint: {str(e)}")
        return False, session_id

def test_session_history(session_id):
    """Test GET /api/ai-agents/session/{session_id}/history endpoint"""
    print(f"\n🔍 Testing Session History Endpoint for session {session_id}...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/ai-agents/session/{session_id}/history?agent_type=contract_negotiation", timeout=10)
        response_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required response structure
            required_fields = ['session_id', 'conversation_history']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Verify session ID matches
            if data.get('session_id') != session_id:
                print(f"❌ Session ID mismatch: expected {session_id}, got {data.get('session_id')}")
                return False
            
            conversation_history = data.get('conversation_history', [])
            print(f"✅ Session History endpoint working correctly")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Conversation Messages: {len(conversation_history)}")
            print(f"   Total Messages: {data.get('total_messages', 0)}")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing session history endpoint: {str(e)}")
        return False

def main():
    """Run all AI Agent Hub tests"""
    print("🚀 Starting AI Agent Hub Backend Testing")
    print("=" * 60)
    
    test_results = []
    session_ids = []
    
    # Test 1: Statistics endpoint
    result = test_ai_agent_statistics()
    test_results.append(("AI Agent Statistics", result))
    
    # Test 2: Contract Negotiation Agent
    result, session_id = test_contract_negotiation_agent()
    test_results.append(("Contract Negotiation Agent", result))
    if result:
        session_ids.append(session_id)
    
    # Test 3: Litigation Strategy Agent
    result, session_id = test_litigation_strategy_agent()
    test_results.append(("Litigation Strategy Agent", result))
    if result:
        session_ids.append(session_id)
    
    # Test 4: Compliance Monitoring Agent
    result, session_id = test_compliance_monitoring_agent()
    test_results.append(("Compliance Monitoring Agent", result))
    if result:
        session_ids.append(session_id)
    
    # Test 5: Client Communication Agent
    result, session_id = test_client_communication_agent()
    test_results.append(("Client Communication Agent", result))
    if result:
        session_ids.append(session_id)
    
    # Test 6: Session History (using first successful session)
    if session_ids:
        result = test_session_history(session_ids[0])
        test_results.append(("Session History", result))
    else:
        test_results.append(("Session History", False))
        print("\n❌ No successful sessions to test history endpoint")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 AI AGENT HUB TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 ALL AI AGENT HUB ENDPOINTS WORKING PERFECTLY!")
    elif success_rate >= 80:
        print("✅ AI Agent Hub mostly functional with minor issues")
    else:
        print("❌ AI Agent Hub has significant issues requiring attention")
    
    return success_rate

if __name__ == "__main__":
    main()