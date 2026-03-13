#!/usr/bin/env python3
"""
Meeting Intelligence Agent - API Demo Script
Test all major endpoints with real requests
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8001/api/v1"
TOKEN = None

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_request(method, endpoint):
    print(f"📤 {method} {endpoint}")

def print_response(status, data):
    print(f"📥 Status: {status}")
    print(f"Response:\n{json.dumps(data, indent=2)}\n")

def test_login():
    """Test user login"""
    global TOKEN
    print_header("1. TEST LOGIN")
    
    print_request("POST", "/auth/login")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        TOKEN = data.get("access_token")
        print_success(f"Logged in! Token: {TOKEN[:50]}...")
        return True
    else:
        print_error(f"Login failed: {data}")
        return False

def test_get_current_user():
    """Test get current user"""
    if not TOKEN:
        print_error("No token available. Run login first.")
        return False
    
    print_header("2. TEST GET CURRENT USER")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    print_request("GET", "/auth/me")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        print_success(f"Got user: {data.get('username')}")
        return True
    else:
        print_error(f"Failed to get user: {data}")
        return False

def test_list_meetings():
    """Test list meetings"""
    if not TOKEN:
        print_error("No token available. Run login first.")
        return False
    
    print_header("3. TEST LIST MEETINGS")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    print_request("GET", "/meetings/?skip=0&limit=10")
    response = requests.get(f"{BASE_URL}/meetings/?skip=0&limit=10", headers=headers)
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        print_success(f"Found {len(data)} meeting(s)")
        return True
    else:
        print_error(f"Failed to list meetings: {data}")
        return False

def test_create_meeting():
    """Test create meeting"""
    if not TOKEN:
        print_error("No token available. Run login first.")
        return None
    
    print_header("4. TEST CREATE MEETING")
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    meeting_data = {
        "title": "Q1 Planning Session",
        "description": "Quarterly planning and strategy discussion",
        "platform": "zoom",
        "scheduled_start": "2025-03-10T14:00:00",
        "scheduled_end": "2025-03-10T15:30:00",
        "meeting_type": "planning",
        "tags": ["planning", "quarterly", "strategy"]
    }
    
    print_request("POST", "/meetings/")
    response = requests.post(
        f"{BASE_URL}/meetings/",
        json=meeting_data,
        headers=headers
    )
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 201:
        print_success(f"Created meeting: {data.get('title')}")
        return data.get("id")
    else:
        print_error(f"Failed to create meeting: {data}")
        return None

def test_get_meeting(meeting_id: str):
    """Test get meeting details"""
    if not TOKEN or not meeting_id:
        print_error("No token or meeting_id available.")
        return False
    
    print_header("5. TEST GET MEETING DETAILS")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    print_request("GET", f"/meetings/{meeting_id}")
    response = requests.get(f"{BASE_URL}/meetings/{meeting_id}", headers=headers)
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        print_success(f"Got meeting details: {data.get('title')}")
        return True
    else:
        print_error(f"Failed to get meeting: {data}")
        return False

def test_list_action_items():
    """Test list action items"""
    if not TOKEN:
        print_error("No token available. Run login first.")
        return False
    
    print_header("6. TEST LIST ACTION ITEMS")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    print_request("GET", "/action-items/?skip=0&limit=10")
    response = requests.get(f"{BASE_URL}/action-items/?skip=0&limit=10", headers=headers)
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        print_success(f"Found {len(data)} action item(s)")
        return True
    else:
        print_error(f"Failed to list action items: {data}")
        return False

def test_create_action_item(meeting_id: str):
    """Test create action item"""
    if not TOKEN or not meeting_id:
        print_error("No token or meeting_id available.")
        return None
    
    print_header("7. TEST CREATE ACTION ITEM")
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    item_data = {
        "title": "Prepare Q1 budget proposal",
        "description": "Detailed budget breakdown for Q1 initiatives",
        "meeting_id": meeting_id,
        "priority": "high",
        "due_date": "2025-03-17T17:00:00",
        "category": "financial"
    }
    
    print_request("POST", "/action-items/")
    response = requests.post(
        f"{BASE_URL}/action-items/",
        json=item_data,
        headers=headers
    )
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 201:
        print_success(f"Created action item: {data.get('title')}")
        return data.get("id")
    else:
        print_error(f"Failed to create action item: {data}")
        return None

def test_analytics_dashboard():
    """Test get analytics dashboard"""
    if not TOKEN:
        print_error("No token available. Run login first.")
        return False
    
    print_header("8. TEST ANALYTICS DASHBOARD")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    print_request("GET", "/analytics/dashboard")
    response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        print_success("Got analytics data")
        return True
    else:
        print_error(f"Failed to get analytics: {data}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "Meeting Intelligence Agent" + " "*17 + "║")
    print("║" + " "*20 + "API Demo Script" + " "*23 + "║")
    print("╚" + "="*58 + "╝")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/../health", timeout=5)
    except requests.exceptions.ConnectionError:
        print_error("\n❌ Backend server not running!")
        print("   Start it with: cd backend && python3 -m uvicorn app.main:app --reload\n")
        return
    
    # Run tests
    tests_passed = 0
    tests_failed = 0
    
    # 1. Login
    if test_login():
        tests_passed += 1
    else:
        tests_failed += 1
        return
    
    # 2. Get current user
    if test_get_current_user():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 3. List meetings
    if test_list_meetings():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 4. Create meeting
    meeting_id = test_create_meeting()
    if meeting_id:
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 5. Get meeting
    if meeting_id and test_get_meeting(meeting_id):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 6. List action items
    if test_list_action_items():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 7. Create action item
    if meeting_id:
        item_id = test_create_action_item(meeting_id)
        if item_id:
            tests_passed += 1
        else:
            tests_failed += 1
    
    # 8. Analytics
    if test_analytics_dashboard():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Summary
    print_header("TEST SUMMARY")
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed} ✅")
    print(f"Failed: {tests_failed} ❌")
    print(f"Success Rate: {tests_passed/(tests_passed + tests_failed)*100:.1f}%")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
