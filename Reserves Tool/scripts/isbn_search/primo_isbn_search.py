"""
Primo ISBN Search Tool for CUNY BMCC
-------------------------------------
This script searches the CUNY BMCC Primo library catalog for a list of ISBNs
and reports on availability, holdings, and whether items need to be purchased.

Uses the Primo Brief Search API for reliable ISBN searching.

Author: Patty (with Claude Code assistance)
Date: 2026-02-23
"""

import pandas as pd
import requests
from datetime import datetime
import os
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

# Primo configuration for CUNY BMCC
PRIMO_HOST = "https://cuny-bm.primo.exlibrisgroup.com"
PRIMO_VID = "01CUNY_BM:CUNY_BM"
PRIMO_SCOPE = "MyInst_and_CI"

# ============================================================================
# ISBN NORMALIZATION
# ============================================================================

def normalize_isbn(isbn):
    """
    Clean and standardize ISBN format.
    - Removes hyphens and spaces
    - Converts to string
    - Removes any extra characters

    Args:
        isbn: ISBN in any format (string or number)

    Returns:
        Cleaned ISBN as string
    """
    if pd.isna(isbn):
        return ""

    # Convert to string and remove hyphens, spaces
    isbn_clean = str(isbn).replace('-', '').replace(' ', '').strip()

    # Remove any non-numeric characters except 'X' (for ISBN-10)
    isbn_clean = ''.join(c for c in isbn_clean if c.isdigit() or c.upper() == 'X')

    return isbn_clean

# ============================================================================
# EDITION COMPARISON
# ============================================================================

def compare_editions(required_edition, found_edition):
    """
    Compare required edition with found edition.
    Handles both numeric and text editions (e.g., "11" matches "Eleventh edition").

    Args:
        required_edition: Edition from textbook list (e.g., "4th", "4", "Fourth")
        found_edition: Edition from library catalog

    Returns:
        String: "Match", "Mismatch", or "Verify Manually"
    """
    if not required_edition or not found_edition:
        return "Verify Manually"

    # Normalize editions for comparison
    req_norm = str(required_edition).lower().strip()
    found_norm = str(found_edition).lower().strip()

    # Direct match
    if req_norm == found_norm:
        return "Match"

    # Number word to digit mapping
    word_to_num = {
        'first': '1', 'second': '2', 'third': '3', 'fourth': '4', 'fifth': '5',
        'sixth': '6', 'seventh': '7', 'eighth': '8', 'ninth': '9', 'tenth': '10',
        'eleventh': '11', 'twelfth': '12', 'thirteenth': '13', 'fourteenth': '14',
        'fifteenth': '15', 'sixteenth': '16', 'seventeenth': '17', 'eighteenth': '18',
        'nineteenth': '19', 'twentieth': '20', 'twenty-first': '21', 'twenty-second': '22',
        'twenty-third': '23', 'twenty-fourth': '24', 'twenty-fifth': '25'
    }

    # Convert text editions to numbers
    import re
    for word, num in word_to_num.items():
        req_norm = req_norm.replace(word, num)
        found_norm = found_norm.replace(word, num)

    # Extract numbers from editions for comparison
    req_nums = re.findall(r'\d+', req_norm)
    found_nums = re.findall(r'\d+', found_norm)

    if req_nums and found_nums:
        if req_nums[0] == found_nums[0]:
            return "Match"
        else:
            return "Mismatch"

    return "Verify Manually"

# ============================================================================
# PRIMO API SEARCH FUNCTIONS
# ============================================================================

def search_primo_by_isbn(isbn):
    """
    Search CUNY BMCC Primo catalog for a specific ISBN using the Brief Search API.

    Args:
        isbn: The ISBN to search for (string)

    Returns:
        Dictionary with search results or None if not found
    """
    try:
        # Use Primo Brief Search API
        endpoint = f"{PRIMO_HOST}/primaws/rest/pub/pnxs"

        params = {
            'q': f'isbn,exact,{isbn}',
            'vid': PRIMO_VID,
            'scope': PRIMO_SCOPE,
            'lang': 'en'
        }

        response = requests.get(endpoint, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            total = data.get('info', {}).get('total', 0)

            if total > 0:
                return data
            else:
                return None
        else:
            print(f"  Primo API returned status {response.status_code}")
            return None

    except Exception as e:
        print(f"Error searching for ISBN {isbn}: {str(e)}")
        return None

def extract_primo_info(primo_result):
    """
    Extract relevant information from Primo search result.

    Args:
        primo_result: The JSON response from Primo API

    Returns:
        Dictionary with extracted information
    """
    info = {
        'title': '',
        'mms_id': '',
        'format': '',
        'availability': '',
        'has_electronic': False,
        'has_physical': False,
        'course_info': '',
        'edition': '',
        'publication_date': ''
    }

    try:
        docs = primo_result.get('docs', [])
        if not docs:
            return info

        # Get first result
        doc = docs[0]
        pnx = doc.get('pnx', {})
        display = pnx.get('display', {})

        # Extract title
        title_list = display.get('title', [])
        info['title'] = title_list[0] if title_list else 'Unknown'

        # Extract MMS ID from the @id field
        record_id = doc.get('@id', '')
        if record_id:
            # Extract MMS ID from URL like: .../pnxs/L/9994494967306141
            parts = record_id.split('/')
            if len(parts) > 0:
                info['mms_id'] = parts[-1]

        # Extract format/type
        type_list = display.get('type', [])
        info['format'] = type_list[0] if type_list else 'Unknown'

        # Check for electronic/physical availability
        avail = display.get('availlibrary', [])
        if avail:
            avail_text = ' '.join(avail).lower()
            info['has_electronic'] = 'electronic' in avail_text or 'online' in avail_text
            info['has_physical'] = 'main campus' in avail_text or 'available' in avail_text

        # Get availability status
        lds50 = display.get('lds50', [])
        if lds50:
            info['availability'] = lds50[0]

        # Extract course information if available
        crsinfo = display.get('crsinfo', [])
        if crsinfo:
            info['course_info'] = crsinfo[0]

        # Extract edition information
        edition_list = display.get('edition', [])
        if edition_list:
            info['edition'] = edition_list[0]

        # Extract publication date
        creation_date = display.get('creationdate', [])
        if creation_date:
            info['publication_date'] = creation_date[0]

    except Exception as e:
        print(f"  Warning: Error extracting info: {e}")

    return info

# ============================================================================
# PROCESS ISBN LIST
# ============================================================================

def process_isbn_list(input_file):
    """
    Main function to process a list of ISBNs and search Primo.

    Args:
        input_file: Path to Excel file with ISBNs

    Returns:
        DataFrame with search results
    """

    print("Preparing to search Primo catalog...")

    # Read input Excel file
    print(f"Reading input file: {input_file}")
    df_input = pd.read_excel(input_file)

    # Check that ISBN column exists
    if 'ISBN' not in df_input.columns:
        print("ERROR: Input file must have a column named 'ISBN'")
        print(f"Found columns: {df_input.columns.tolist()}")
        exit(1)

    print(f"  Loaded {len(df_input)} entries")
    if 'Instructor_Name' in df_input.columns:
        print(f"  With course information: {df_input['Instructor_Name'].notna().sum()} entries")

    # Normalize ISBNs
    print("Normalizing ISBNs...")
    df_input['ISBN_Clean'] = df_input['ISBN'].apply(normalize_isbn)

    # Prepare results list
    results = []

    # Process each ISBN
    total = len(df_input)
    print(f"\nSearching Primo for {total} ISBNs...\n")

    for idx, row in df_input.iterrows():
        isbn = row['ISBN_Clean']

        # Progress indicator every 50 records
        if (idx + 1) % 50 == 0:
            print(f"Progress: {idx + 1}/{total} ({(idx + 1)/total*100:.1f}%)")

        # Build base result with course info from input
        base_result = {
            'Course': row.get('Course', ''),
            'Section': row.get('Section', ''),
            'Instructor_Name': row.get('Instructor_Name', ''),
            'Total_Enrollment': row.get('Total_Enrollment', ''),
            'EmplID': row.get('EmplID', ''),
            'Class_Number': row.get('Class_Number', ''),
            'ISBN_Original': row['ISBN'],
            'ISBN_Clean': isbn,
            'Required_Edition': row.get('Edition', ''),
            'Required_Title': row.get('Title', '')
        }

        if not isbn:
            results.append({
                **base_result,
                'Status': 'Invalid ISBN',
                'Title': '',
                'MMS_ID': '',
                'Format': '',
                'Found_Edition': '',
                'Publication_Year': '',
                'Edition_Match': 'N/A',
                'Has_Physical': 'No',
                'Has_Electronic': 'No',
                'Availability': '',
                'Course_Assignment': '',
                'Recommendation': 'Check ISBN'
            })
            continue

        # Search Primo
        search_result = search_primo_by_isbn(isbn)

        if search_result:
            # Found in Primo!
            primo_info = extract_primo_info(search_result)

            # Compare editions
            edition_match = compare_editions(
                row.get('Edition', ''),
                primo_info['edition']
            )

            # Determine recommendation
            if primo_info['has_physical'] or primo_info['has_electronic']:
                if edition_match == 'Match':
                    recommendation = 'Already Available - Correct Edition'
                elif edition_match == 'Mismatch':
                    recommendation = 'Wrong Edition - Verify or Purchase Needed'
                else:
                    recommendation = 'Available - Verify Edition Manually'
            else:
                recommendation = 'May Need Purchase (verify manually)'

            results.append({
                **base_result,
                'Status': 'Found',
                'Title': primo_info['title'],
                'MMS_ID': primo_info['mms_id'],
                'Format': primo_info['format'],
                'Found_Edition': primo_info['edition'],
                'Publication_Year': primo_info['publication_date'],
                'Edition_Match': edition_match,
                'Has_Physical': 'Yes' if primo_info['has_physical'] else 'No',
                'Has_Electronic': 'Yes' if primo_info['has_electronic'] else 'No',
                'Availability': primo_info['availability'],
                'Course_Assignment': primo_info['course_info'],
                'Recommendation': recommendation
            })

        else:
            # Not found in Primo
            results.append({
                **base_result,
                'Status': 'Not Found',
                'Title': '',
                'MMS_ID': '',
                'Format': '',
                'Found_Edition': '',
                'Publication_Year': '',
                'Edition_Match': 'N/A',
                'Has_Physical': 'No',
                'Has_Electronic': 'No',
                'Availability': '',
                'Course_Assignment': '',
                'Recommendation': 'Purchase Required'
            })

    # Convert results to DataFrame
    df_results = pd.DataFrame(results)

    return df_results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function.
    """
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Search Primo catalog for ISBNs')
    parser.add_argument('--input',
                       default='/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/full_dataset_BOOKS_consolidated.xlsx',
                       help='Path to input Excel file with ISBNs')
    parser.add_argument('--semester',
                       default=None,
                       help='Semester identifier (e.g., Spring2026)')
    parser.add_argument('--output',
                       default=None,
                       help='Path to output Excel file')

    args = parser.parse_args()

    print("=" * 70)
    print("PRIMO ISBN SEARCH TOOL - CUNY BMCC")
    print("=" * 70)
    print()

    # Set input/output files
    input_file = args.input
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Determine output directory and filename
    if args.output:
        output_file = args.output
    else:
        output_dir = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data'
        if args.semester:
            output_file = f'{output_dir}/{args.semester}_primo_results_{timestamp}.xlsx'
        else:
            output_file = f'{output_dir}/primo_isbn_results_{timestamp}.xlsx'

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found!")
        print("Please check the file path.")
        exit(1)

    # Process ISBNs
    results_df = process_isbn_list(input_file)

    # Save results
    print(f"\nSaving results to: {output_file}")
    results_df.to_excel(output_file, index=False)

    # Print summary
    print("\n" + "=" * 70)
    print("SEARCH COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"Total ISBNs searched: {len(results_df)}")
    print(f"Found in Primo: {len(results_df[results_df['Status'] == 'Found'])}")
    print(f"Not found: {len(results_df[results_df['Status'] == 'Not Found'])}")
    print(f"Already available (correct edition): {len(results_df[results_df['Recommendation'] == 'Already Available - Correct Edition'])}")
    print(f"Purchase needed: {len(results_df[results_df['Recommendation'].str.contains('Purchase', na=False)])}")
    print(f"Edition mismatch: {len(results_df[results_df['Edition_Match'] == 'Mismatch'])}")
    print(f"\nResults saved to: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
