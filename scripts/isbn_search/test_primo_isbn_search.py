"""
Test version of Primo ISBN Search Tool - Processes only first 10 ISBNs
This is for testing the Primo connection and making sure everything works.
"""

import pandas as pd
import requests
from datetime import datetime
import json

# Primo configuration
PRIMO_HOST = "https://cuny-bm.primo.exlibrisgroup.com"
PRIMO_VID = "01CUNY_BM:CUNY_BM"

# Read the cleaned textbook file
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
        # Use Primo Brief Search API
        endpoint = f"{PRIMO_HOST}/primaws/rest/pub/pnxs"

        params = {
            'q': f'isbn,exact,{isbn}',
            'vid': PRIMO_VID,
            'scope': 'MyInst_and_CI',
            'lang': 'en'
        }

        response = requests.get(endpoint, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            total = data.get('info', {}).get('total', 0)

            if total > 0:
                # Extract title from first result
                docs = data.get('docs', [])
                if docs:
                    pnx = docs[0].get('pnx', {})
                    display = pnx.get('display', {})
                    title = display.get('title', ['Unknown'])[0] if display.get('title') else 'Unknown'

                    # Check for electronic/physical
                    avail = display.get('availlibrary', [])
                    has_electronic = any('electronic' in str(a).lower() or 'online' in str(a).lower() for a in avail)
                    has_physical = any('main campus' in str(a).lower() or 'available' in str(a).lower() for a in avail)

                    print(f"  ✓ FOUND: {title}")
                    if has_physical:
                        print(f"    Has physical copies")
                    if has_electronic:
                        print(f"    Has electronic access")
                    if not has_physical and not has_electronic:
                        print(f"    Format/availability details in record")
            else:
                print(f"  ✗ NOT FOUND in Primo")
        else:
            print(f"  ✗ ERROR: Status {response.status_code}")

    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")

print("\n" + "="*70)
print("\nTest complete!")
print("\nIf the test worked, you can run the full script:")
print("  python3 primo_isbn_search.py")
print("\nThis will process all valid ISBNs from the cleaned data (may take 20-30 minutes)")
