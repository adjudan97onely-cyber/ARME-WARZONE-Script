import requests
import sys
import json
from datetime import datetime

class ZenHubBackendTester:
    def __init__(self, base_url="https://projet-studio.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_weapon_id = None
        self.created_script_id = None

    def log_test(self, name, success, message=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {message}")
        if message and success:
            print(f"   ℹ️  {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                try:
                    json_response = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}")
                    return True, json_response
                except:
                    self.log_test(name, True, f"Status: {response.status_code} (no JSON)")
                    return True, {}
            else:
                try:
                    error_detail = response.json().get('detail', 'No error details')
                except:
                    error_detail = response.text[:100] if response.text else 'No response content'
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {error_detail}")
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        success, response = self.run_test("Get Stats", "GET", "stats", 200)
        if success:
            required_keys = ['total_weapons', 'total_scripts', 'meta_weapons', 'hidden_meta_weapons', 'categories']
            for key in required_keys:
                if key not in response:
                    self.log_test("Stats Structure", False, f"Missing key: {key}")
                    return False
            self.log_test("Stats Structure", True, f"All required keys present")
        return success

    def test_weapons_crud(self):
        """Test complete weapons CRUD operations"""
        
        # 1. Get all weapons initially
        success, initial_weapons = self.run_test("Get All Weapons", "GET", "weapons", 200)
        if not success:
            return False
        
        initial_count = len(initial_weapons)
        print(f"   📊 Initial weapons count: {initial_count}")

        # 2. Create a new weapon
        test_weapon = {
            "name": "Test Weapon XM4",
            "category": "AR",
            "game": "BO6",
            "vertical_recoil": 25,
            "horizontal_recoil": 12,
            "fire_rate": 750,
            "damage": 32,
            "range_meters": 45,
            "rapid_fire": True,
            "rapid_fire_value": 30,
            "recommended_build": "Test Build Components",
            "notes": "This is a test weapon for API testing",
            "is_meta": True,
            "is_hidden_meta": False
        }
        
        success, created_weapon = self.run_test("Create Weapon", "POST", "weapons", 200, test_weapon)
        if not success:
            return False
        
        self.created_weapon_id = created_weapon.get('id')
        if not self.created_weapon_id:
            self.log_test("Weapon Creation ID", False, "No ID returned in created weapon")
            return False
        
        # 3. Get the created weapon by ID
        success, weapon_detail = self.run_test("Get Weapon by ID", "GET", f"weapons/{self.created_weapon_id}", 200)
        if not success:
            return False
        
        # Verify weapon data
        if weapon_detail.get('name') != test_weapon['name']:
            self.log_test("Weapon Data Verification", False, "Created weapon data mismatch")
            return False
        
        # 4. Update the weapon
        update_data = {
            "name": "Updated Test Weapon XM4",
            "vertical_recoil": 30,
            "notes": "Updated notes for testing"
        }
        
        success, updated_weapon = self.run_test("Update Weapon", "PUT", f"weapons/{self.created_weapon_id}", 200, update_data)
        if not success:
            return False
        
        # Verify update
        if updated_weapon.get('name') != update_data['name']:
            self.log_test("Weapon Update Verification", False, "Updated weapon data mismatch")
            return False
        
        # 5. Test weapon filters
        success, ar_weapons = self.run_test("Filter Weapons by Category", "GET", "weapons", 200, params={"category": "AR"})
        if success:
            ar_count = len(ar_weapons)
            print(f"   📊 AR weapons found: {ar_count}")
        
        success, bo6_weapons = self.run_test("Filter Weapons by Game", "GET", "weapons", 200, params={"game": "BO6"})
        if success:
            bo6_count = len(bo6_weapons)
            print(f"   📊 BO6 weapons found: {bo6_count}")

        return True

    def test_seed_weapons(self):
        """Test seeding default weapons"""
        success, response = self.run_test("Seed Default Weapons", "POST", "seed-weapons", 200)
        if success:
            if response.get('seeded'):
                count = response.get('count', 0)
                print(f"   📊 Seeded {count} weapons")
                # Verify expected count
                if count != 31:
                    self.log_test("Seed Count Verification", False, f"Expected 31 weapons, got {count}")
                    return False
                else:
                    self.log_test("Seed Count Verification", True, f"Correctly seeded {count} weapons")
            else:
                print(f"   ℹ️  {response.get('message', 'Already seeded')}")
        return success

    def test_master_script_generation(self):
        """Test master script generation"""
        success, response = self.run_test("Generate Master Script", "POST", "generate-master-script", 200)
        if success:
            # Check response structure
            required_keys = ['script', 'script_id', 'weapon_count', 'message']
            for key in required_keys:
                if key not in response:
                    self.log_test("Master Script Response", False, f"Missing key: {key}")
                    return False
            
            self.created_script_id = response.get('script_id')
            weapon_count = response.get('weapon_count')
            print(f"   📊 Master script created with {weapon_count} weapons")
            
            # Check if script contains expected GPC code
            script_code = response.get('script', '')
            if 'main {' not in script_code or 'define AR_V_' not in script_code:
                self.log_test("Master Script Content", False, "Generated script missing expected GPC content")
                return False
            
            self.log_test("Master Script Content", True, "GPC script content verified")
            
        return success

    def test_scripts_crud(self):
        """Test scripts CRUD operations"""
        
        # 1. Get all scripts
        success, scripts = self.run_test("Get All Scripts", "GET", "scripts", 200)
        if not success:
            return False
        
        print(f"   📊 Current scripts count: {len(scripts)}")
        
        # 2. Create a test script
        test_script = {
            "title": "Test Anti-Recoil Script",
            "code": """/*
 * Test GPC Script
 */
#include <zen.gph>

main {
    if(get_val(PS4_L2) && get_val(PS4_R2)) {
        set_val(PS4_RY, get_val(PS4_RY) + 25);
    }
}""",
            "weapon_ids": [self.created_weapon_id] if self.created_weapon_id else [],
            "script_type": "single"
        }
        
        success, created_script = self.run_test("Create Script", "POST", "scripts", 200, test_script)
        if success:
            script_id = created_script.get('id')
            if script_id:
                print(f"   📊 Created script ID: {script_id}")
                # Test script deletion later
                self.test_script_id = script_id
        
        return success

    def test_ai_chat(self):
        """Test AI chat functionality"""
        
        # Test sending a message
        chat_request = {
            "session_id": self.session_id,
            "message": "Génère un script anti-recoil simple pour tester l'API"
        }
        
        success, response = self.run_test("AI Chat Send Message", "POST", "chat", 200, chat_request)
        if success:
            if 'response' not in response or 'session_id' not in response:
                self.log_test("AI Chat Response Structure", False, "Missing required response fields")
                return False
            
            ai_response = response.get('response', '')
            if len(ai_response) < 10:
                self.log_test("AI Response Quality", False, "AI response too short or empty")
                return False
            
            print(f"   📊 AI response length: {len(ai_response)} characters")
            self.log_test("AI Response Quality", True, "AI provided meaningful response")
            
            # Test getting chat history
            success, history = self.run_test("Get Chat History", "GET", f"chat/{self.session_id}", 200)
            if success:
                if len(history) < 2:  # Should have user message + AI response
                    self.log_test("Chat History", False, f"Expected at least 2 messages, got {len(history)}")
                    return False
                print(f"   📊 Chat history messages: {len(history)}")
                self.log_test("Chat History", True, "Chat history properly stored")
        
        return success

    def test_cleanup(self):
        """Clean up test data"""
        success = True
        
        # Delete test weapon if created
        if self.created_weapon_id:
            weapon_success, _ = self.run_test("Delete Test Weapon", "DELETE", f"weapons/{self.created_weapon_id}", 200)
            success = success and weapon_success
        
        # Delete test script if created
        if hasattr(self, 'test_script_id'):
            script_success, _ = self.run_test("Delete Test Script", "DELETE", f"scripts/{self.test_script_id}", 200)
            success = success and script_success
        
        # Clear chat history
        chat_success, _ = self.run_test("Clear Chat History", "DELETE", f"chat/{self.session_id}", 200)
        success = success and chat_success
        
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Zen Hub Pro Backend API Tests")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_api_root():
            print("💥 API root test failed - aborting")
            return False
        
        # Core functionality tests
        tests = [
            ("Stats API", self.test_stats_endpoint),
            ("Seed Weapons", self.test_seed_weapons), 
            ("Weapons CRUD", self.test_weapons_crud),
            ("Master Script Generation", self.test_master_script_generation),
            ("Scripts CRUD", self.test_scripts_crud),
            ("AI Chat Integration", self.test_ai_chat),
            ("Cleanup", self.test_cleanup),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name} tests...")
            success = test_func()
            if not success:
                print(f"💥 {test_name} tests failed")
                # Continue with other tests but note the failure
        
        # Final results
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Backend API is functioning excellently!")
            return True
        elif success_rate >= 75:
            print("⚠️  Backend API has some issues but is mostly functional")
            return True
        else:
            print("💥 Backend API has significant issues")
            return False

def main():
    tester = ZenHubBackendTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())