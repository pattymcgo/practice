"""
Debug script to test different ways of searching for ISBN in Alma
"""
import requests
import json

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['alma_api_key']
base_url = "https://api-na.hosted.exlibrisgroup.com"

# The ISBN that the user confirmed is in Alma
test_isbn = "9781266574641"

print(f"Testing different search methods for ISBN: {test_isbn}")
print("=" * 70)

# Method 1: Using other_system_id (current method)
print("\n[Method 1] Searching with other_system_id parameter...")
try:
    endpoint = f"{base_url}/almaws/v1/bibs"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json"
    }
    params = {
        "other_system_id": test_isbn,
        "view": "brief"
    }
    response = requests.get(endpoint, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Method 2: Using q parameter with isbn search
print("\n[Method 2] Searching with q=isbn~{isbn}...")
try:
    endpoint = f"{base_url}/almaws/v1/bibs"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json"
    }
    params = {
        "q": f"isbn~{test_isbn}",
        "view": "brief"
    }
    response = requests.get(endpoint, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Method 3: Using SRU search
print("\n[Method 3] Searching with SRU style query...")
try:
    endpoint = f"{base_url}/almaws/v1/bibs"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json"
    }
    params = {
        "q": f"alma.isbn={test_isbn}",
        "view": "brief"
    }
    response = requests.get(endpoint, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Method 4: Try with hyphens added
formatted_isbn = f"{test_isbn[0:3]}-{test_isbn[3]}-{test_isbn[4:7]}-{test_isbn[7:12]}-{test_isbn[12]}"
print(f"\n[Method 4] Searching with formatted ISBN: {formatted_isbn}")
try:
    endpoint = f"{base_url}/almaws/v1/bibs"
    headers = {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json"
    }
    params = {
        "other_system_id": formatted_isbn,
        "view": "brief"
    }
    response = requests.get(endpoint, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("\nDebug test complete!")
