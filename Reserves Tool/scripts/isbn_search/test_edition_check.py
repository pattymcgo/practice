"""
Test edition checking feature with a few examples
"""
import pandas as pd
import requests
from datetime import datetime
import re

# Primo configuration
PRIMO_HOST = "https://cuny-bm.primo.exlibrisgroup.com"
PRIMO_VID = "01CUNY_BM:CUNY_BM"

def compare_editions(required_edition, found_edition):
    """Compare required edition with found edition."""
    if not required_edition or not found_edition:
        return "Verify Manually"

    req_norm = str(required_edition).lower().strip()
    found_norm = str(found_edition).lower().strip()

    if req_norm == found_norm:
        return "Match"

    req_nums = re.findall(r'\d+', req_norm)
    found_nums = re.findall(r'\d+', found_norm)

    if req_nums and found_nums:
        if req_nums[0] == found_nums[0]:
            return "Match"
        else:
            return "Mismatch"

    return "Verify Manually"

# Read data
input_file = '/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx'
df = pd.read_excel(input_file)

# Test with first 5 ISBNs that have edition info
test_rows = df[df['Edition'].notna()].head(5)

print("=" * 80)
print("EDITION CHECKING TEST")
print("=" * 80)

for idx, row in test_rows.iterrows():
    isbn = row['ISBN']
    required_edition = row['Edition']
    title = row['Title'][:50] + "..." if len(str(row['Title'])) > 50 else row['Title']

    print(f"\n[Test {idx+1}]")
    print(f"  ISBN: {isbn}")
    print(f"  Required Title: {title}")
    print(f"  Required Edition: {required_edition}")

    # Search Primo
    try:
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
                docs = data.get('docs', [])
                if docs:
                    pnx = docs[0].get('pnx', {})
                    display = pnx.get('display', {})

                    found_title = display.get('title', ['Unknown'])[0] if display.get('title') else 'Unknown'
                    found_edition = display.get('edition', [''])[0] if display.get('edition') else ''
                    pub_date = display.get('creationdate', [''])[0] if display.get('creationdate') else ''

                    edition_match = compare_editions(required_edition, found_edition)

                    print(f"  ✓ FOUND in catalog!")
                    print(f"    Found Title: {found_title[:50]}...")
                    print(f"    Found Edition: {found_edition if found_edition else 'Not specified'}")
                    print(f"    Publication Year: {pub_date}")
                    print(f"    Edition Match: {edition_match}")

                    if edition_match == "Match":
                        print(f"    ✓ Correct edition available!")
                    elif edition_match == "Mismatch":
                        print(f"    ⚠️  WRONG EDITION - may need to purchase correct version")
                    else:
                        print(f"    ⚠️  Verify edition manually")
            else:
                print(f"  ✗ NOT FOUND in catalog")
                print(f"    Recommendation: Purchase required")
        else:
            print(f"  ✗ Error: Status {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 80)
print("Test complete!")
print("\nThe full search script now includes edition checking!")
print("Run: python3 primo_isbn_search.py")
print("=" * 80)
