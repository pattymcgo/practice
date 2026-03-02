"""
Test SRU search with CUNY BMCC's actual endpoint
"""
import requests
import xml.etree.ElementTree as ET
import json

# Load API key
with open('config.json', 'r') as f:
    config = json.load(f)
api_key = config['alma_api_key']

# Test ISBN that user confirmed is in Alma
test_isbn = "9781266574641"

# CUNY BMCC institution codes to try
institution_codes = [
    '01CUNY_BM',      # Most likely based on URL
    'CUNY_BM',
    '01CUNY_BMCC',
    'CUNY_BMCC',
    'BMCC',
    'BM',
]

base_url = "https://cuny-bm.alma.exlibrisgroup.com/view/sru"

print(f"Testing SRU search for ISBN: {test_isbn}")
print(f"Using CUNY BMCC Alma instance")
print("=" * 70)

for inst_code in institution_codes:
    print(f"\n[Testing institution code: {inst_code}]")

    # Try with apikey parameter
    print("  Attempt 1: With apikey parameter...")
    try:
        sru_url = f"{base_url}/{inst_code}"
        params = {
            'version': '1.2',
            'operation': 'searchRetrieve',
            'query': f'alma.isbn={test_isbn}',
            'recordSchema': 'marcxml',
            'apikey': api_key
        }

        response = requests.get(sru_url, params=params, timeout=10)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            # Parse XML to check for results
            root = ET.fromstring(response.content)
            # Look for numberOfRecords in SRU response
            ns = {'srw': 'http://www.loc.gov/zing/srw/'}
            num_records = root.find('.//srw:numberOfRecords', ns)

            if num_records is not None:
                count = int(num_records.text)
                print(f"    ✓ SUCCESS! Found {count} record(s)")
                if count > 0:
                    print(f"\n    FOUND IT! Institution code is: {inst_code}")
                    print(f"    Full URL: {sru_url}")
                    # Print first 1000 chars of response
                    print(f"\n    Sample response:\n{response.text[:1000]}")
                    break
            else:
                print(f"    Response: {response.text[:300]}")
        else:
            print(f"    Error: {response.text[:200]}")

    except Exception as e:
        print(f"    Error: {e}")

    # Try without apikey (some SRU endpoints don't need it)
    print("  Attempt 2: Without apikey parameter...")
    try:
        params = {
            'version': '1.2',
            'operation': 'searchRetrieve',
            'query': f'alma.isbn={test_isbn}',
            'recordSchema': 'marcxml'
        }

        response = requests.get(sru_url, params=params, timeout=10)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            ns = {'srw': 'http://www.loc.gov/zing/srw/'}
            num_records = root.find('.//srw:numberOfRecords', ns)

            if num_records is not None:
                count = int(num_records.text)
                print(f"    ✓ SUCCESS! Found {count} record(s)")
                if count > 0:
                    print(f"\n    FOUND IT! Institution code is: {inst_code}")
                    print(f"    Full URL: {sru_url}")
                    print(f"    Note: This endpoint doesn't require API key")
                    print(f"\n    Sample response:\n{response.text[:1000]}")
                    break
            else:
                print(f"    Response: {response.text[:300]}")
        else:
            print(f"    Error: {response.text[:200]}")

    except Exception as e:
        print(f"    Error: {e}")

print("\n" + "=" * 70)
print("\nTest complete!")
