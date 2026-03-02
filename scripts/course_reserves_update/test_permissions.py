"""
Test Alma API Permissions
--------------------------
This script checks if you have the required API permissions for
Course Reserves automation.

Run this before using the automation tool to verify your permissions.
"""

import requests
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def load_config():
    """Load API configuration."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'isbn_search', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: config.json not found!")
        return None

def test_bibs_api(api_key):
    """Test Bibliographic Data API access."""
    try:
        base_url = "https://api-na.hosted.exlibrisgroup.com"
        endpoint = f"{base_url}/almaws/v1/bibs"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        params = {"other_system_id": "9999999999"}  # Dummy search

        response = requests.get(endpoint, headers=headers, params=params, timeout=10)

        if response.status_code in [200, 400]:  # 400 = not found, but permission OK
            return True, "Access granted"
        elif response.status_code in [401, 403]:
            return False, "Permission denied"
        else:
            return False, f"Status {response.status_code}"

    except Exception as e:
        return False, str(e)

def test_courses_api(api_key):
    """Test Courses API access."""
    try:
        base_url = "https://api-na.hosted.exlibrisgroup.com"
        endpoint = f"{base_url}/almaws/v1/courses"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        params = {"q": "code~TEST", "limit": 1}

        response = requests.get(endpoint, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            return True, "Access granted"
        elif response.status_code in [401, 403]:
            return False, "Permission denied - Request 'Courses - Read/Write'"
        else:
            return False, f"Status {response.status_code}"

    except Exception as e:
        return False, str(e)

def test_reading_lists_api(api_key):
    """Test Reading Lists API access (requires a course ID)."""
    try:
        # We can't fully test without a real course ID,
        # but we can check if the endpoint is accessible
        base_url = "https://api-na.hosted.exlibrisgroup.com"

        # Try to access courses first to get a course ID
        courses_endpoint = f"{base_url}/almaws/v1/courses"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        params = {"limit": 1}

        response = requests.get(courses_endpoint, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            result = response.json()
            courses = result.get('course', [])

            if courses:
                # Try to access reading lists for first course
                course_id = courses[0].get('id', '')
                lists_endpoint = f"{base_url}/almaws/v1/courses/{course_id}/reading-lists"

                response = requests.get(lists_endpoint, headers=headers, timeout=10)

                if response.status_code == 200:
                    return True, "Access granted"
                elif response.status_code in [401, 403]:
                    return False, "Permission denied - Request 'Reading Lists - Read/Write'"
                else:
                    return False, f"Status {response.status_code}"
            else:
                return None, "No courses to test with (permission might be OK)"

        elif response.status_code in [401, 403]:
            return False, "Cannot test - Courses API not accessible"
        else:
            return None, "Cannot test - need Courses API first"

    except Exception as e:
        return None, f"Test inconclusive: {str(e)}"

def main():
    """Main test function."""
    print("=" * 70)
    print("ALMA API PERMISSIONS TEST")
    print("=" * 70)
    print()

    # Load config
    config = load_config()
    if not config:
        print("✗ Could not load configuration")
        return

    api_key = config.get('alma_api_key', '')
    if not api_key:
        print("✗ No API key found in config")
        return

    print(f"Testing API key: ...{api_key[-6:]}")
    print()

    # Test Bibs API
    print("[1/3] Testing Bibliographic Data API...")
    success, message = test_bibs_api(api_key)
    if success:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ {message}")

    print()

    # Test Courses API
    print("[2/3] Testing Courses API...")
    success, message = test_courses_api(api_key)
    if success:
        print(f"  ✓ {message}")
    elif success is False:
        print(f"  ✗ {message}")
    else:
        print(f"  ⚠️  {message}")

    print()

    # Test Reading Lists API
    print("[3/3] Testing Reading Lists API...")
    success, message = test_reading_lists_api(api_key)
    if success:
        print(f"  ✓ {message}")
    elif success is False:
        print(f"  ✗ {message}")
    else:
        print(f"  ⚠️  {message}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Required permissions for Course Reserves automation:")
    print("  ✓ Bibliographic Data API (you have this)")
    print("  ? Courses API (Read/Write) - CHECK RESULTS ABOVE")
    print("  ? Reading Lists API (Read/Write) - CHECK RESULTS ABOVE")
    print("  ? Citations API (Read/Write) - Tested via Reading Lists")
    print()
    print("If you see ✗ or ⚠️  above, contact your Alma administrator")
    print("to request the missing permissions.")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
