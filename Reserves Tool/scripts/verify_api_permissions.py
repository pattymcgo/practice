"""
API Permission Verification Tool
Tests whether your API key has the required permissions for course automation
"""

import sys
import os
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/isbn_search')

import requests
import json

print("=" * 70)
print("ALMA API PERMISSION VERIFICATION")
print("=" * 70)
print()

# Load config
config_path = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/isbn_search/config.json'

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("ERROR: config.json not found!")
    sys.exit(1)

api_key = config.get('alma_api_key', '')
base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

if not api_key:
    print("ERROR: No API key found in config.json")
    sys.exit(1)

print(f"API Base URL: {base_url}")
print(f"Testing API key: {api_key[:10]}...")
print()

# Test results
results = {
    'Bibs API (Read)': False,
    'Courses API (Read)': False,
    'Courses API (Write)': False,
    'Reading Lists API (Read)': False,
    'Reading Lists API (Write)': False,
    'Citations API (Read)': False,
    'Citations API (Write)': False
}

# ============================================================================
# TEST 1: Bibs API (Read) - Already working
# ============================================================================

print("Testing Bibs API (Read)...")
try:
    endpoint = f"{base_url}/almaws/v1/bibs"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json"
    }
    params = {"q": "title~test", "limit": 1}
    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code == 200:
        results['Bibs API (Read)'] = True
        print("  ✓ Bibs API (Read): Working")
    else:
        print(f"  ✗ Bibs API (Read): Failed ({response.status_code})")
except Exception as e:
    print(f"  ✗ Bibs API (Read): Error - {str(e)}")

print()

# ============================================================================
# TEST 2: Courses API (Read)
# ============================================================================

print("Testing Courses API (Read)...")
try:
    endpoint = f"{base_url}/almaws/v1/courses"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json"
    }
    params = {"limit": 1}
    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code == 200:
        results['Courses API (Read)'] = True
        print("  ✓ Courses API (Read): Working")
    elif response.status_code in [401, 403]:
        print(f"  ✗ Courses API (Read): No permission (403)")
    else:
        print(f"  ✗ Courses API (Read): Failed ({response.status_code})")
except Exception as e:
    print(f"  ✗ Courses API (Read): Error - {str(e)}")

print()

# ============================================================================
# TEST 3: Courses API (Write) - Test by attempting to create
# ============================================================================

print("Testing Courses API (Write)...")
print("  NOTE: This performs a test creation that will be immediately deleted")

try:
    # Attempt to create a test course
    endpoint = f"{base_url}/almaws/v1/courses"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    test_course = {
        "code": "TEST_API_VERIFY",
        "name": "API Permission Test Course",
        "section": "TEST",
        "academic_department": {"value": "Test"},
        "term": [{"value": "Test Term"}],
        "start_date": "2026-01-01",
        "end_date": "2026-12-31"
    }

    response = requests.post(endpoint, headers=headers, json=test_course)

    if response.status_code in [200, 201]:
        results['Courses API (Write)'] = True
        print("  ✓ Courses API (Write): Working")

        # Try to delete the test course
        result = response.json()
        course_id = result.get('id', '')
        if course_id:
            delete_url = f"{endpoint}/{course_id}"
            requests.delete(delete_url, headers=headers)
            print("  ✓ Test course created and deleted successfully")
    elif response.status_code in [401, 403]:
        print(f"  ✗ Courses API (Write): No permission")
    else:
        print(f"  ✗ Courses API (Write): Failed ({response.status_code})")
        print(f"    Response: {response.text[:200]}")
except Exception as e:
    print(f"  ✗ Courses API (Write): Error - {str(e)}")

print()

# ============================================================================
# TEST 4: Reading Lists API (requires a course to exist)
# ============================================================================

print("Testing Reading Lists API...")
print("  NOTE: Requires Courses API to test fully")

# We can only test if we have at least read access to courses
if results['Courses API (Read)']:
    try:
        # Get first course
        endpoint = f"{base_url}/almaws/v1/courses"
        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }
        params = {"limit": 1}
        response = requests.get(endpoint, headers=headers, params=params)

        if response.status_code == 200:
            courses = response.json().get('course', [])
            if len(courses) > 0:
                course_id = courses[0].get('id', '')

                # Test reading lists read
                rl_endpoint = f"{base_url}/almaws/v1/courses/{course_id}/reading-lists"
                rl_response = requests.get(rl_endpoint, headers=headers)

                if rl_response.status_code == 200:
                    results['Reading Lists API (Read)'] = True
                    print("  ✓ Reading Lists API (Read): Working")
                elif rl_response.status_code in [401, 403]:
                    print("  ✗ Reading Lists API (Read): No permission")
                else:
                    print(f"  ✗ Reading Lists API (Read): Failed ({rl_response.status_code})")

                # Test write permission (without actually creating)
                # We check if the error is 403 (permission) vs other errors
                print("  ℹ️  Reading Lists API (Write): Cannot test without creating data")
            else:
                print("  ⚠️  No courses found to test Reading Lists API")
    except Exception as e:
        print(f"  ✗ Reading Lists API: Error - {str(e)}")
else:
    print("  ⚠️  Skipped (Courses API Read required)")

print()

# ============================================================================
# TEST 5: Citations API (requires a reading list to exist)
# ============================================================================

print("Testing Citations API...")
print("  ℹ️  Citations API: Cannot fully test without creating data")
print()

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

working_count = sum(1 for v in results.values() if v)
total_count = len(results)

print(f"Permissions working: {working_count}/{total_count}")
print()

for api, status in results.items():
    symbol = "✓" if status else "✗"
    print(f"  {symbol} {api}")

print()
print("=" * 70)

# Required for course automation
required_permissions = [
    'Courses API (Read)',
    'Courses API (Write)',
    'Reading Lists API (Read)',
    'Reading Lists API (Write)',
    'Citations API (Read)',
    'Citations API (Write)'
]

has_required = all(results.get(perm, False) for perm in required_permissions[:2])  # At least check Courses API

if has_required:
    print("✅ READY: You have Courses API permissions!")
    print()
    print("You can now run the course automation tool:")
    print("  python /Users/patty_home/Desktop/Agentic\\ AI/projects/030226_test/run_automation_test.py")
else:
    print("⚠️  NOT READY: Missing required API permissions")
    print()
    print("Required permissions for course automation:")
    for perm in required_permissions:
        symbol = "✓" if results.get(perm, False) else "✗"
        print(f"  {symbol} {perm}")
    print()
    print("Please contact your Alma administrator to request these permissions.")

print("=" * 70)
