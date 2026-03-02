"""
Test version of ISBN Search Tool - Processes only first 10 ISBNs
This is for testing the connection and making sure everything works before
running the full search on all valid ISBNs.
"""

import pandas as pd
import requests
from datetime import datetime
import json

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config.get('alma_api_key', '')

# Read the cleaned textbook file (merged with course data and cleaned)
print("Reading cleaned textbook list...")
input_file = '/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx'
df = pd.read_excel(input_file)

print(f"Total entries in file: {len(df)}")
print(f"\nTesting with first 10 unique ISBNs...\n")

# Get first 10 unique ISBNs
test_isbns = df['ISBN'].dropna().unique()[:10].tolist()

# Test each ISBN
print("\n" + "="*70)
for i, isbn in enumerate(test_isbns, 1):
    print(f"\n[{i}/10] Testing ISBN: {isbn}")
    try:
        # Use Alma Bibs API
        base_url = "https://api-na.hosted.exlibrisgroup.com"
        endpoint = f"{base_url}/almaws/v1/bibs"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        params = {
            "other_system_id": str(isbn),
            "view": "brief"
        }

        response = requests.get(endpoint, headers=headers, params=params)

        if response.status_code == 200:
            result = response.json()
            if result and 'bib' in result:
                bib = result['bib']
                if isinstance(bib, list):
                    bib = bib[0]
                title = bib.get('title', 'Unknown')
                mms_id = bib.get('mms_id', 'N/A')
                print(f"  ✓ FOUND: {title}")
                print(f"    MMS ID: {mms_id}")
            else:
                print(f"  ✗ NOT FOUND in Alma")
        elif response.status_code == 400:
            print(f"  ✗ NOT FOUND in Alma (404)")
        else:
            print(f"  ✗ ERROR: Status {response.status_code}")
            print(f"    Response: {response.text[:200]}")

    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")

print("\n" + "="*70)
print("\nTest complete!")
print("\nIf the test worked, you can run the full script:")
print("  python3 isbn_search_tool.py")
print("\nThis will process all valid ISBNs from the cleaned data (may take 20-30 minutes)")
