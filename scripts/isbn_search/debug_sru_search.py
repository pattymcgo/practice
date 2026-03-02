"""
Debug script to test SRU (Search/Retrieve via URL) API for ISBN searches
SRU is specifically designed for bibliographic searches
"""
import requests
import json
import xml.etree.ElementTree as ET

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['alma_api_key']

# The ISBN that the user confirmed is in Alma
test_isbn = "9781266574641"

print(f"Testing SRU search for ISBN: {test_isbn}")
print("=" * 70)

# SRU endpoint for bibliographic searches
# Documentation: https://developers.exlibrisgroup.com/alma/apis/docs/bibs/R0VUIC9hbG1hd3MvdjEvc3J1
sru_url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/sru"

# Try different SRU query formats
queries = [
    f'alma.isbn="{test_isbn}"',
    f'alma.isbn={test_isbn}',
    f'alma.standard_number={test_isbn}',
    f'isbn={test_isbn}',
]

for i, query in enumerate(queries, 1):
    print(f"\n[Query {i}] {query}")
    try:
        params = {
            'version': '1.2',
            'operation': 'searchRetrieve',
            'query': query,
            'apikey': api_key
        }

        response = requests.get(sru_url, params=params)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            # Parse XML response
            root = ET.fromstring(response.content)
            # Look for numberOfRecords
            ns = {'srw': 'http://www.loc.gov/zing/srw/'}
            num_records = root.find('.//srw:numberOfRecords', ns)
            if num_records is not None:
                print(f"Number of records found: {num_records.text}")
                if int(num_records.text) > 0:
                    print("✓ SUCCESS! Found the record!")
                    print(f"Full response:\n{response.text[:1000]}")
            else:
                print(f"Response (first 500 chars): {response.text[:500]}")
        else:
            print(f"Error response: {response.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 70)
