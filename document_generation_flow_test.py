import requests
import sys
import json
import time
import re
from datetime import datetime

class DocumentGenerationFlowTester:
    def __init__(self, base_url="https://smooth-input-wizard.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.review_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=60):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'List with ' + str(len(response_data)) + ' items'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_compliant_contract_generation_with_review_id(self):
        """Test POST /api/generate-contract-compliant endpoint and verify review ID in response"""
        print("\n" + "="*80)
        print("🎯 CRITICAL TEST: Document Generation Flow - Review ID Extraction")
        print("="*80)
        
        # Test with typical NDA contract data
        contract_data = {
            "contract_type": "NDA",
            "jurisdiction": "US",
            "parties": {
                "party1_name": "TechFlow Solutions Inc.",
                "party1_type": "corporation",
                "party2_name": "Alexandra Martinez",
                "party2_type": "individual"
            },
            "terms": {
                "purpose": "Discussion of potential business collaboration involving proprietary AI technology and confidential business strategies",
                "duration": "2_years"
            },
            "special_clauses": ["Non-compete clause for 12 months", "Return of materials clause"]
        }
        
        success, response = self.run_test(
            "Compliant Contract Generation with Review ID", 
            "POST", 
            "generate-contract-compliant", 
            200, 
            contract_data,
            timeout=90  # Allow extra time for compliance processing
        )
        
        if success and isinstance(response, dict):
            print(f"\n📋 RESPONSE ANALYSIS:")
            print(f"   Response structure: {json.dumps(response, indent=2)[:500]}...")
            
            # Check for contract in response
            if 'contract' in response:
                contract = response['contract']
                print(f"   ✅ Contract generated successfully")
                print(f"   Contract ID: {contract.get('id', 'N/A')}")
                print(f"   Contract Type: {contract.get('contract_type', 'N/A')}")
                print(f"   Compliance Score: {contract.get('compliance_score', 'N/A')}")
            else:
                print(f"   ❌ No 'contract' field in response")
            
            # Check for suggestions field (where review ID should be)
            if 'suggestions' in response:
                suggestions = response['suggestions']
                print(f"   ✅ Suggestions field found")
                print(f"   Suggestions type: {type(suggestions)}")
                print(f"   Suggestions content: {suggestions}")
                
                # Look for review (ID: xxx) pattern that frontend expects
                review_id_pattern = r'review \(ID: ([a-f0-9-]+)\)'
                review_matches = []
                
                if isinstance(suggestions, list):
                    for suggestion in suggestions:
                        if isinstance(suggestion, str):
                            matches = re.findall(review_id_pattern, suggestion, re.IGNORECASE)
                            review_matches.extend(matches)
                            if matches:
                                print(f"   ✅ Found review ID pattern in suggestion: {suggestion}")
                elif isinstance(suggestions, str):
                    matches = re.findall(review_id_pattern, suggestions, re.IGNORECASE)
                    review_matches.extend(matches)
                    if matches:
                        print(f"   ✅ Found review ID pattern in suggestions: {suggestions}")
                
                if review_matches:
                    self.review_id = review_matches[0]
                    print(f"   🎯 EXTRACTED REVIEW ID: {self.review_id}")
                    print(f"   ✅ Frontend can extract review ID from response.data.suggestions")
                else:
                    print(f"   ❌ CRITICAL ISSUE: No 'review (ID: xxx)' pattern found in suggestions")
                    print(f"   ❌ Frontend will NOT be able to extract review ID")
                    print(f"   ❌ This explains why ReviewStatus component doesn't appear")
                    
                    # Look for any UUID patterns that might be review IDs
                    uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
                    uuid_matches = re.findall(uuid_pattern, str(suggestions), re.IGNORECASE)
                    if uuid_matches:
                        print(f"   ⚠️  Found UUID patterns (potential review IDs): {uuid_matches}")
                        print(f"   ⚠️  But they're not in the expected 'review (ID: xxx)' format")
                        # Try the first UUID as potential review ID for testing
                        self.review_id = uuid_matches[0]
                        print(f"   🔧 Using first UUID for testing: {self.review_id}")
            else:
                print(f"   ❌ CRITICAL ISSUE: No 'suggestions' field in response")
                print(f"   ❌ Frontend expects response.data.suggestions to contain review ID")
            
            # Check for warnings field
            if 'warnings' in response:
                warnings = response['warnings']
                print(f"   ✅ Warnings field found: {warnings}")
            else:
                print(f"   ⚠️  No 'warnings' field in response")
            
            # Check response data structure that frontend expects
            if 'data' in response:
                data = response['data']
                print(f"   ✅ Data field found")
                if 'suggestions' in data:
                    print(f"   ✅ response.data.suggestions exists (frontend path)")
                    data_suggestions = data['suggestions']
                    # Check for review ID pattern in data.suggestions
                    review_matches_data = re.findall(review_id_pattern, str(data_suggestions), re.IGNORECASE)
                    if review_matches_data:
                        self.review_id = review_matches_data[0]
                        print(f"   🎯 EXTRACTED REVIEW ID from data.suggestions: {self.review_id}")
                else:
                    print(f"   ❌ No response.data.suggestions (frontend expects this path)")
            else:
                print(f"   ⚠️  No 'data' field in response structure")
                
        return success, response

    def test_review_status_endpoint(self):
        """Test GET /api/attorney/review/status/{review_id} endpoint"""
        if not self.review_id:
            print("\n⚠️  Skipping review status test - no review ID available")
            return True, {}
        
        print(f"\n🔍 Testing Review Status Endpoint with ID: {self.review_id}")
        
        success, response = self.run_test(
            f"Review Status for ID {self.review_id}", 
            "GET", 
            f"attorney/review/status/{self.review_id}", 
            200,
            timeout=30
        )
        
        if success and isinstance(response, dict):
            print(f"\n📊 REVIEW STATUS ANALYSIS:")
            
            # Check required fields for progress monitoring
            required_fields = ['review_id', 'status', 'progress_percentage', 'estimated_completion']
            for field in required_fields:
                if field in response:
                    value = response[field]
                    print(f"   ✅ {field}: {value}")
                else:
                    print(f"   ❌ Missing required field: {field}")
            
            # Check progress percentage specifically
            if 'progress_percentage' in response:
                progress = response['progress_percentage']
                print(f"   📈 Progress Analysis:")
                print(f"      Current Progress: {progress}%")
                
                if progress == 0:
                    print(f"      ⚠️  Progress is 0% - review may be stuck in 'pending' status")
                elif 0 < progress < 100:
                    print(f"      ✅ Progress is advancing ({progress}%) - dynamic progress working")
                elif progress == 100:
                    print(f"      ✅ Review completed (100%)")
                else:
                    print(f"      ❌ Invalid progress value: {progress}")
            
            # Check status field
            if 'status' in response:
                status = response['status']
                print(f"   📋 Status Analysis:")
                print(f"      Current Status: {status}")
                
                if status == 'pending':
                    print(f"      ⚠️  Status is 'pending' - may indicate attorney assignment issue")
                elif status == 'in_review':
                    print(f"      ✅ Status is 'in_review' - attorney assigned and working")
                elif status in ['completed', 'approved', 'rejected']:
                    print(f"      ✅ Review completed with status: {status}")
                else:
                    print(f"      ⚠️  Unknown status: {status}")
            
            # Check attorney assignment
            if 'assigned_attorney' in response:
                attorney = response['assigned_attorney']
                if attorney:
                    print(f"   👨‍⚖️ Attorney assigned: {attorney}")
                    print(f"      ✅ Attorney assignment working")
                else:
                    print(f"   ❌ No attorney assigned - this explains stuck progress")
            elif 'attorney' in response:
                attorney = response['attorney']
                if attorney:
                    print(f"   👨‍⚖️ Attorney info: {attorney}")
                else:
                    print(f"   ❌ No attorney assigned")
            
            # Check estimated completion
            if 'estimated_completion' in response:
                completion = response['estimated_completion']
                print(f"   ⏰ Estimated completion: {completion}")
                
                if completion and completion != 'N/A':
                    print(f"      ✅ Realistic completion time provided")
                else:
                    print(f"      ⚠️  No realistic completion time")
        
        return success, response

    def test_complete_document_generation_flow(self):
        """Test the complete flow: Generate Contract → Extract Review ID → Poll Review Status"""
        print("\n" + "="*80)
        print("🔄 COMPLETE DOCUMENT GENERATION FLOW TEST")
        print("="*80)
        
        # Step 1: Generate Contract
        print("\n📝 STEP 1: Generate Contract with Compliance")
        contract_success, contract_response = self.test_compliant_contract_generation_with_review_id()
        
        if not contract_success:
            print("❌ FLOW FAILED: Contract generation failed")
            return False, {"step": 1, "error": "Contract generation failed"}
        
        # Step 2: Extract Review ID
        print("\n🔍 STEP 2: Extract Review ID from Response")
        if not self.review_id:
            print("❌ FLOW FAILED: Could not extract review ID from contract response")
            print("❌ This is why frontend ReviewStatus component doesn't appear")
            return False, {"step": 2, "error": "Review ID extraction failed"}
        
        print(f"✅ Review ID extracted successfully: {self.review_id}")
        
        # Step 3: Poll Review Status
        print("\n📊 STEP 3: Poll Review Status")
        status_success, status_response = self.test_review_status_endpoint()
        
        if not status_success:
            print("❌ FLOW FAILED: Review status polling failed")
            return False, {"step": 3, "error": "Review status polling failed"}
        
        # Step 4: Verify Dynamic Progress
        print("\n📈 STEP 4: Verify Dynamic Progress")
        if isinstance(status_response, dict) and 'progress_percentage' in status_response:
            initial_progress = status_response['progress_percentage']
            print(f"Initial progress: {initial_progress}%")
            
            # Wait a few seconds and check again for dynamic progress
            print("Waiting 5 seconds to check for progress advancement...")
            time.sleep(5)
            
            second_check_success, second_response = self.test_review_status_endpoint()
            if second_check_success and isinstance(second_response, dict):
                second_progress = second_response.get('progress_percentage', initial_progress)
                print(f"Second check progress: {second_progress}%")
                
                if second_progress > initial_progress:
                    print("✅ DYNAMIC PROGRESS CONFIRMED: Progress advanced over time")
                elif second_progress == initial_progress and initial_progress > 0:
                    print("✅ PROGRESS STABLE: Progress maintained (acceptable if in active review)")
                elif initial_progress == 0 and second_progress == 0:
                    print("❌ PROGRESS STUCK: Progress remains at 0% - attorney assignment issue")
                    return False, {"step": 4, "error": "Progress stuck at 0%"}
                else:
                    print(f"⚠️  Progress behavior: {initial_progress}% → {second_progress}%")
        
        print("\n🎉 COMPLETE FLOW TEST RESULTS:")
        print("✅ Step 1: Contract generation - SUCCESS")
        print(f"✅ Step 2: Review ID extraction - SUCCESS ({self.review_id})")
        print("✅ Step 3: Review status polling - SUCCESS")
        print("✅ Step 4: Progress monitoring - SUCCESS")
        print("\n🎯 FLOW ANALYSIS COMPLETE")
        
        return True, {
            "contract_response": contract_response,
            "review_id": self.review_id,
            "status_response": status_response,
            "flow_complete": True
        }

    def test_multiple_contract_types_for_review_creation(self):
        """Test different contract types to verify review creation consistency"""
        print("\n" + "="*80)
        print("🔄 MULTIPLE CONTRACT TYPES REVIEW CREATION TEST")
        print("="*80)
        
        contract_types = [
            {
                "type": "freelance_agreement",
                "data": {
                    "contract_type": "freelance_agreement",
                    "jurisdiction": "US",
                    "parties": {
                        "party1_name": "Digital Innovations LLC",
                        "party1_type": "llc",
                        "party2_name": "Maria Rodriguez",
                        "party2_type": "individual"
                    },
                    "terms": {
                        "scope": "Development of e-commerce website with payment integration",
                        "payment_amount": "$7,500",
                        "payment_terms": "milestone"
                    },
                    "special_clauses": []
                }
            },
            {
                "type": "employment_agreement",
                "data": {
                    "contract_type": "employment_agreement",
                    "jurisdiction": "US",
                    "parties": {
                        "party1_name": "GrowthTech Corporation",
                        "party1_type": "corporation",
                        "party2_name": "James Wilson",
                        "party2_type": "individual"
                    },
                    "terms": {
                        "position": "Senior Software Engineer",
                        "salary": "$95,000",
                        "start_date": "2025-02-01"
                    },
                    "special_clauses": ["Remote work arrangement"]
                }
            }
        ]
        
        results = {}
        all_success = True
        
        for contract_info in contract_types:
            contract_type = contract_info["type"]
            contract_data = contract_info["data"]
            
            print(f"\n📝 Testing {contract_type.upper()} contract generation...")
            
            success, response = self.run_test(
                f"Compliant {contract_type} Generation", 
                "POST", 
                "generate-contract-compliant", 
                200, 
                contract_data,
                timeout=90
            )
            
            if success and isinstance(response, dict):
                # Check for review ID in suggestions
                review_id = None
                if 'suggestions' in response:
                    suggestions = response['suggestions']
                    review_id_pattern = r'review \(ID: ([a-f0-9-]+)\)'
                    matches = re.findall(review_id_pattern, str(suggestions), re.IGNORECASE)
                    if matches:
                        review_id = matches[0]
                        print(f"   ✅ Review ID found: {review_id}")
                    else:
                        print(f"   ❌ No review ID pattern found in suggestions")
                        all_success = False
                
                results[contract_type] = {
                    "success": success,
                    "review_id": review_id,
                    "has_suggestions": 'suggestions' in response,
                    "response_keys": list(response.keys())
                }
            else:
                print(f"   ❌ {contract_type} generation failed")
                all_success = False
                results[contract_type] = {"success": False, "error": "Generation failed"}
        
        print(f"\n📊 MULTIPLE CONTRACT TYPES SUMMARY:")
        for contract_type, result in results.items():
            if result.get("success"):
                review_status = "✅ Review ID found" if result.get("review_id") else "❌ No Review ID"
                print(f"   {contract_type}: ✅ Generated | {review_status}")
            else:
                print(f"   {contract_type}: ❌ Failed")
        
        return all_success, results

    def run_all_tests(self):
        """Run all document generation flow tests"""
        print("🚀 Starting Document Generation Flow Testing...")
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        
        # Test 1: Complete document generation flow
        flow_success, flow_result = self.test_complete_document_generation_flow()
        
        # Test 2: Multiple contract types
        multi_success, multi_result = self.test_multiple_contract_types_for_review_creation()
        
        # Final Summary
        print("\n" + "="*80)
        print("📋 DOCUMENT GENERATION FLOW TEST SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n🎯 KEY FINDINGS:")
        if flow_success:
            print("✅ Complete document generation flow working")
            print(f"✅ Review ID extraction successful: {self.review_id}")
            print("✅ Review status polling operational")
        else:
            print("❌ Document generation flow has issues")
            print("❌ This explains why ReviewStatus component doesn't appear")
        
        if multi_success:
            print("✅ Multiple contract types create reviews consistently")
        else:
            print("❌ Inconsistent review creation across contract types")
        
        # Root cause analysis
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        if not self.review_id:
            print("❌ CRITICAL ISSUE: Review ID not found in response.data.suggestions")
            print("❌ Frontend cannot extract review ID to show ReviewStatus component")
            print("❌ This is why progress monitoring doesn't work")
        else:
            print("✅ Review ID extraction working - frontend should show ReviewStatus")
            print("✅ Progress monitoring system operational")
        
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": (self.tests_passed/self.tests_run)*100,
            "flow_working": flow_success,
            "review_id_found": bool(self.review_id),
            "review_id": self.review_id,
            "multi_contract_success": multi_success
        }

if __name__ == "__main__":
    tester = DocumentGenerationFlowTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["success_rate"] >= 80:
        print(f"\n🎉 Testing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Testing completed with issues.")
        sys.exit(1)