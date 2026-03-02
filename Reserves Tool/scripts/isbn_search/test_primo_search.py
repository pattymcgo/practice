"""
Test searching via Primo Discovery API
"""
import requests
import json

# Test ISBN that user confirmed is available
test_isbn = "9781266574641"

primo_host = "https://cuny-bm.primo.exlibrisgroup.com"
vid = "01CUNY_BM:CUNY_BM"

print(f"Testing Primo search for ISBN: {test_isbn}")
print(f"Using CUNY BMCC Primo instance")
print("=" * 70)

# Method 1: Primo Brief Search API
print("\n[Method 1] Primo Brief Search API...")
try:
    url = f"{primo_host}/primaws/rest/pub/pnxs"
    params = {
        'q': f'isbn,exact,{test_isbn}',
        'vid': vid,
        'scope': 'MyInst_and_CI',
        'lang': 'en'
    }

    response = requests.get(url, params=params, timeout=15)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        total = data.get('info', {}).get('total', 0)
        print(f"✓ Total results found: {total}")

        if total > 0:
            print("\nFOUND IT!")
            # Show first result
            docs = data.get('docs', [])
            if docs:
                first = docs[0]
                pnx = first.get('pnx', {})
                display = pnx.get('display', {})
                title = display.get('title', ['Unknown'])[0] if display.get('title') else 'Unknown'
                print(f"Title: {title}")
                print(f"\nFull response sample:")
                print(json.dumps(data, indent=2)[:1500])
        else:
            print("No results found")
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Error: {response.text[:500]}")

except Exception as e:
    print(f"Error: {e}")

# Method 2: Try with 'any' field instead of isbn
print("\n[Method 2] Searching with 'any' field...")
try:
    url = f"{primo_host}/primaws/rest/pub/pnxs"
    params = {
        'q': f'any,contains,{test_isbn}',
        'vid': vid,
        'scope': 'MyInst_and_CI',
        'lang': 'en'
    }

    response = requests.get(url, params=params, timeout=15)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        total = data.get('info', {}).get('total', 0)
        print(f"✓ Total results found: {total}")

        if total > 0:
            print("\nFOUND IT!")
            docs = data.get('docs', [])
            if docs:
                first = docs[0]
                pnx = first.get('pnx', {})
                display = pnx.get('display', {})
                title = display.get('title', ['Unknown'])[0] if display.get('title') else 'Unknown'
                print(f"Title: {title}")
        else:
            print("No results found")

    else:
        print(f"Error: {response.text[:500]}")

except Exception as e:
    print(f"Error: {e}")

# Method 3: Try different scope
print("\n[Method 3] Searching with different scope...")
try:
    url = f"{primo_host}/primaws/rest/pub/pnxs"
    params = {
        'q': f'isbn,exact,{test_isbn}',
        'vid': vid,
        'scope': 'everything',
        'lang': 'en'
    }

    response = requests.get(url, params=params, timeout=15)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        total = data.get('info', {}).get('total', 0)
        print(f"✓ Total results found: {total}")

        if total > 0:
            print("\nFOUND IT!")
        else:
            print("No results found")

    else:
        print(f"Error: {response.text[:500]}")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("\nTest complete!")
