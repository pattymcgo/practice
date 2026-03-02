"""
Alma ISBN Search Tool - Reusable for Multiple Semesters
--------------------------------------------------------
This script searches the Alma library system for a list of ISBNs
and reports on availability, holdings, and whether items need to be purchased.

Uses the Alma Bibs API for ISBN searching.

Usage:
    python alma_isbn_search_tool.py
    python alma_isbn_search_tool.py --input /path/to/data.xlsx
    python alma_isbn_search_tool.py --input Spring2026_BOOKS_consolidated.xlsx --semester "Spring2026"

Author: Patty (with Claude Code assistance)
Date: 2026-02-23
Updated: 2026-03-02 - Made reusable for multiple semesters
"""

import pandas as pd
import requests
from datetime import datetime
import os
import json
import argparse
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config():
    """
    Load API configuration from config.json file.
    This keeps your API key secure and separate from the code.
    """
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("ERROR: config.json not found!")
        print("Please create a config.json file with your API key.")
        print("See README.md for instructions.")
        exit(1)

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
# ALMA API SEARCH FUNCTIONS
# ============================================================================

def search_alma_by_isbn(isbn, api_key):
    """
    Search Alma for a specific ISBN using the Bibs API.

    Args:
        isbn: The ISBN to search for (string)
        api_key: Alma API key

    Returns:
        Dictionary with search results or None if not found
    """
    try:
        # Use Alma Bibs API to search by ISBN
        base_url = "https://api-na.hosted.exlibrisgroup.com"
        endpoint = f"{base_url}/almaws/v1/bibs"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        # Search using other_system_id parameter for ISBN
        params = {
            "other_system_id": isbn,
            "view": "brief"
        }

        response = requests.get(endpoint, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            # Not found
            return None
        else:
            print(f"  API returned status {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"Error searching for ISBN {isbn}: {str(e)}")
        return None

def get_holdings_info(mms_id, api_key):
    """
    Get holdings information for a specific bibliographic record.

    Args:
        mms_id: The Alma MMS ID (bibliographic record ID)
        api_key: Alma API key

    Returns:
        Dictionary with holdings information
    """
    try:
        base_url = "https://api-na.hosted.exlibrisgroup.com"
        endpoint = f"{base_url}/almaws/v1/bibs/{mms_id}/holdings"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error getting holdings for MMS ID {mms_id}: {str(e)}")
        return None

def get_availability_status(mms_id, holding_id, api_key):
    """
    Get detailed availability for a specific holding.

    Args:
        mms_id: Bibliographic record ID
        holding_id: Holding record ID
        api_key: Alma API key

    Returns:
        Dictionary with item availability details
    """
    try:
        base_url = "https://api-na.hosted.exlibrisgroup.com"
        endpoint = f"{base_url}/almaws/v1/bibs/{mms_id}/holdings/{holding_id}/items"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        print(f"Error getting items: {str(e)}")
        return None

# ============================================================================
# PROCESS ISBN LIST
# ============================================================================

def process_isbn_list(input_file, alma_api_key, alma_region='na'):
    """
    Main function to process a list of ISBNs and search Alma.

    Args:
        input_file: Path to Excel file with ISBNs
        alma_api_key: Your Alma API key
        alma_region: Alma region (na=North America, eu=Europe, ap=Asia Pacific)

    Returns:
        DataFrame with search results
    """

    # Alma API will be accessed via direct requests
    print("Preparing to search Alma...")

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
    print(f"\nSearching Alma for {total} ISBNs...\n")

    for idx, row in df_input.iterrows():
        isbn = row['ISBN_Clean']
        print(f"[{idx+1}/{total}] Searching: {isbn}")

        # Get required edition from input data
        required_edition = row.get('Edition', '')
        required_title = row.get('Title', '')

        if not isbn:
            results.append({
                'ISBN_Original': row['ISBN'],
                'ISBN_Clean': isbn,
                'Required_Edition': required_edition,
                'Required_Title': required_title,
                'Status': 'Invalid ISBN',
                'Title': '',
                'MMS_ID': '',
                'Found_Edition': '',
                'Edition_Match': 'N/A',
                'Physical_Copies': 0,
                'Electronic_Access': 'No',
                'Location': '',
                'Availability': '',
                'Recommendation': 'Check ISBN'
            })
            continue

        # Search Alma
        search_result = search_alma_by_isbn(isbn, alma_api_key)

        if search_result and 'bib' in search_result:
            # Found in Alma!
            bib_records = search_result['bib']

            # Handle multiple results (take first one)
            if isinstance(bib_records, list):
                bib = bib_records[0]
            else:
                bib = bib_records

            mms_id = bib.get('mms_id', '')
            title = bib.get('title', 'Unknown Title')

            # Extract edition information from bibliographic record
            # Note: Alma API may not always include edition in brief view
            found_edition = bib.get('edition', '')

            # Compare editions
            edition_match = compare_editions(required_edition, found_edition)

            # Get holdings information
            holdings_info = get_holdings_info(mms_id, alma_api_key)

            physical_count = 0
            electronic_access = 'No'
            locations = []
            availability = 'Unknown'

            if holdings_info and 'holding' in holdings_info:
                holdings = holdings_info['holding']
                if not isinstance(holdings, list):
                    holdings = [holdings]

                for holding in holdings:
                    holding_id = holding.get('holding_id', '')
                    location = holding.get('location', {}).get('desc', 'Unknown')

                    # Check if electronic
                    if holding.get('holding_type') == 'electronic':
                        electronic_access = 'Yes'
                    else:
                        # Physical holding - get item count
                        items_info = get_availability_status(mms_id, holding_id, alma_api_key)
                        if items_info and 'item' in items_info:
                            items = items_info['item']
                            if not isinstance(items, list):
                                items = [items]
                            physical_count += len(items)

                            # Check availability of first item
                            if items and 'item_data' in items[0]:
                                availability = items[0]['item_data'].get('base_status', {}).get('desc', 'Unknown')

                        locations.append(location)

            # Determine recommendation based on availability and edition
            if physical_count > 0 or electronic_access == 'Yes':
                if edition_match == 'Match':
                    recommendation = 'Already Available - Correct Edition'
                elif edition_match == 'Mismatch':
                    recommendation = 'Wrong Edition - Verify or Purchase Needed'
                else:
                    recommendation = 'Available - Verify Edition Manually'
            else:
                recommendation = 'Purchase Needed'

            results.append({
                'ISBN_Original': row['ISBN'],
                'ISBN_Clean': isbn,
                'Required_Edition': required_edition,
                'Required_Title': required_title,
                'Status': 'Found',
                'Title': title,
                'MMS_ID': mms_id,
                'Found_Edition': found_edition,
                'Edition_Match': edition_match,
                'Physical_Copies': physical_count,
                'Electronic_Access': electronic_access,
                'Location': ', '.join(locations) if locations else 'N/A',
                'Availability': availability,
                'Recommendation': recommendation
            })

        else:
            # Not found in Alma
            results.append({
                'ISBN_Original': row['ISBN'],
                'ISBN_Clean': isbn,
                'Required_Edition': required_edition,
                'Required_Title': required_title,
                'Status': 'Not Found',
                'Title': '',
                'MMS_ID': '',
                'Found_Edition': '',
                'Edition_Match': 'N/A',
                'Physical_Copies': 0,
                'Electronic_Access': 'No',
                'Location': '',
                'Availability': '',
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
    Main execution function - now accepts command-line arguments for flexibility.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Search Alma for ISBNs from course/textbook data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python alma_isbn_search_tool.py
  python alma_isbn_search_tool.py --input Spring2026_BOOKS_consolidated.xlsx
  python alma_isbn_search_tool.py --input data.xlsx --semester "Fall2026"
        """
    )

    # Default input file
    default_input = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/merged_course_textbooks_CLEANED.xlsx'

    parser.add_argument(
        '--input',
        default=default_input,
        help='Path to input Excel file with course/textbook data'
    )

    parser.add_argument(
        '--semester',
        default=None,
        help='Semester identifier for output file naming (e.g., "Spring2026")'
    )

    parser.add_argument(
        '--output',
        default=None,
        help='Custom output file path (optional)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("ALMA ISBN SEARCH TOOL")
    print("=" * 70)
    print()

    # Load configuration
    config = load_config()
    api_key = config.get('alma_api_key', '')
    region = config.get('alma_region', 'na')

    if not api_key:
        print("ERROR: No API key found in config.json")
        sys.exit(1)

    # Set input file
    input_file = args.input

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found!")
        print("Please check the file path.")
        sys.exit(1)

    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if args.output:
        output_file = args.output
    elif args.semester:
        output_dir = os.path.dirname(input_file) or '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data'
        output_file = f'{output_dir}/{args.semester}_isbn_results_{timestamp}.xlsx'
    else:
        output_dir = os.path.dirname(input_file) or '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data'
        output_file = f'{output_dir}/isbn_results_{timestamp}.xlsx'

    print(f"Input file: {input_file}")
    if args.semester:
        print(f"Semester: {args.semester}")
    print(f"Output file: {output_file}")
    print()

    # Process ISBNs
    results_df = process_isbn_list(input_file, api_key, region)

    # Save results
    print(f"\nSaving results to: {output_file}")
    results_df.to_excel(output_file, index=False)

    # Print summary
    print("\n" + "=" * 70)
    print("SEARCH COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"Total ISBNs searched: {len(results_df)}")
    print(f"Found in Alma: {len(results_df[results_df['Status'] == 'Found'])}")
    print(f"Not found: {len(results_df[results_df['Status'] == 'Not Found'])}")
    print(f"Already available: {len(results_df[results_df['Recommendation'] == 'Already Available'])}")
    print(f"Purchase needed: {len(results_df[results_df['Recommendation'].str.contains('Purchase')])}")
    print(f"\nResults saved to: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
