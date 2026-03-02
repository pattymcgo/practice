"""
Alma Course Reserves Automation Tool for CUNY BMCC
---------------------------------------------------
This script automates the creation of courses and reading lists in Alma
based on your textbook and course data.

IMPORTANT: Requires API permissions for:
- Courses API (Read/Write)
- Reading Lists API (Read/Write)
- Citations API (Read/Write)

Author: Patty (with Claude Code assistance)
Date: 2026-02-23
"""

import pandas as pd
import requests
from datetime import datetime
import os
import json
import sys
import argparse

# Add parent directory to path for config access
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ============================================================================
# CONFIGURATION
# ============================================================================

def load_config(use_sandbox=False):
    """
    Load API configuration from config file.

    Args:
        use_sandbox: If True, loads config_sandbox.json instead of config.json

    Returns:
        Dictionary with API configuration
    """
    config_filename = 'config_sandbox.json' if use_sandbox else 'config.json'
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'isbn_search', config_filename)

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Set default base URL if not specified in config
        if 'base_url' not in config:
            config['base_url'] = "https://api-na.hosted.exlibrisgroup.com"

        return config
    except FileNotFoundError:
        print(f"ERROR: {config_filename} not found at {config_path}!")
        if use_sandbox:
            print("Please create a config_sandbox.json file with your sandbox API key.")
            print("See config_sandbox.json template for required format.")
        else:
            print("Please create a config.json file with your API key.")
        exit(1)

# ============================================================================
# ALMA COURSES API FUNCTIONS
# ============================================================================

def create_course(course_data, api_key, base_url):
    """
    Create a course in Alma.

    Args:
        course_data: Dictionary with course information
        api_key: Alma API key
        base_url: Alma API base URL

    Returns:
        Course ID if successful, None otherwise
    """
    try:
        endpoint = f"{base_url}/almaws/v1/courses"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Build course JSON payload
        course_payload = {
            "code": course_data['course_code'],
            "name": course_data['course_name'],
            "section": course_data['section'],
            "academic_department": {
                "value": course_data.get('department', 'General')
            },
            "term": [{
                "value": course_data.get('term', '2026 Spring')
            }],
            "instructor": [{
                "primary_id": course_data.get('instructor_id', ''),
                "first_name": course_data.get('instructor_first', ''),
                "last_name": course_data.get('instructor_last', '')
            }],
            "start_date": course_data.get('start_date', '2026-01-26'),
            "end_date": course_data.get('end_date', '2026-05-26'),
            "participants_number": course_data.get('enrollment', 0)
        }

        response = requests.post(endpoint, headers=headers, json=course_payload)

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            course_id = result.get('id', '')
            print(f"  ✓ Course created: {course_id}")
            return course_id
        elif response.status_code == 401 or response.status_code == 403:
            print(f"  ✗ PERMISSION ERROR: Your API key doesn't have Courses API permissions")
            print(f"    Please request 'Courses - Read/Write' permissions from your Alma admin")
            return None
        else:
            print(f"  ✗ Error creating course: {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"  ✗ Exception: {str(e)}")
        return None

def get_course(course_code, section, api_key, base_url):
    """
    Check if a course already exists in Alma.

    Note: In Alma, one course can have multiple sections (e.g., "ACC 330" with sections "0900, 1000, 1800").
    Also, course codes may have instructor names appended (e.g., "ANT 100 (Zaman)").
    This function searches flexibly and checks if the section is included.

    Args:
        course_code: Course code to search for (e.g., "ACC 330")
        section: Section number (e.g., "0900")
        api_key: Alma API key
        base_url: Alma API base URL

    Returns:
        Course ID if found, None otherwise
    """
    try:
        endpoint = f"{base_url}/almaws/v1/courses"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Accept": "application/json"
        }

        # Get all courses - increase limit to 1000 to catch most courses
        # Note: Alma has ~761 courses, so 1000 should be sufficient
        params = {"limit": 1000}
        response = requests.get(endpoint, headers=headers, params=params)

        if response.status_code == 200:
            result = response.json()
            courses = result.get('course', [])

            # First pass: Try to find exact section match
            for course in courses:
                alma_course_code = course.get('code', '')

                # Match exact code OR code that starts with our course_code
                # This handles cases like "ANT 100" matching "ANT 100 (Zaman)"
                code_matches = (
                    alma_course_code == course_code or
                    alma_course_code.startswith(f"{course_code} (") or
                    alma_course_code.startswith(f"{course_code}(")
                )

                if code_matches:
                    # Check if this course has our section
                    course_sections = course.get('section', '')
                    # Section field can be a single section or comma-separated sections
                    if course_sections:
                        section_list = [s.strip() for s in str(course_sections).split(',')]
                        if section in section_list:
                            return course.get('id', None)

            # Second pass: If no exact section match, try courses with empty sections
            # This handles cases where all sections are grouped under one course record
            for course in courses:
                alma_course_code = course.get('code', '')

                code_matches = (
                    alma_course_code == course_code or
                    alma_course_code.startswith(f"{course_code} (") or
                    alma_course_code.startswith(f"{course_code}(")
                )

                if code_matches:
                    course_sections = course.get('section', '')
                    # Match courses with empty sections as fallback
                    if not course_sections:
                        return course.get('id', None)

            return None
        elif response.status_code == 401 or response.status_code == 403:
            print(f"  ⚠️  Permission check: Courses API not accessible")
            return None
        else:
            return None

    except Exception as e:
        print(f"  ⚠️  Error checking course: {str(e)}")
        return None

# ============================================================================
# ALMA READING LISTS API FUNCTIONS
# ============================================================================

def create_reading_list(course_id, list_name, api_key, base_url):
    """
    Create a reading list for a course.

    Args:
        course_id: Alma course ID
        list_name: Name for the reading list
        api_key: Alma API key
        base_url: Alma API base URL

    Returns:
        Reading list ID if successful, None otherwise
    """
    try:
        endpoint = f"{base_url}/almaws/v1/courses/{course_id}/reading-lists"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        list_payload = {
            "name": list_name,
            "status": {
                "value": "BeingPrepared"
            }
        }

        response = requests.post(endpoint, headers=headers, json=list_payload)

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            list_id = result.get('id', '')
            print(f"    ✓ Reading list created: {list_id}")
            return list_id
        elif response.status_code == 401 or response.status_code == 403:
            print(f"    ✗ PERMISSION ERROR: No Reading Lists API permissions")
            return None
        else:
            print(f"    ✗ Error creating reading list: {response.status_code}")
            return None

    except Exception as e:
        print(f"    ✗ Exception: {str(e)}")
        return None

# ============================================================================
# ALMA CITATIONS API FUNCTIONS
# ============================================================================

def add_citation(course_id, list_id, citation_data, api_key, base_url):
    """
    Add a citation (textbook) to a reading list.

    Args:
        course_id: Alma course ID
        list_id: Reading list ID
        citation_data: Dictionary with citation information
        api_key: Alma API key
        base_url: Alma API base URL

    Returns:
        Citation ID if successful, None otherwise
    """
    try:
        endpoint = f"{base_url}/almaws/v1/courses/{course_id}/reading-lists/{list_id}/citations"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Build citation payload
        citation_payload = {
            "type": {
                "value": "BK"  # Book
            },
            "status": {
                "value": "Active"
            },
            "metadata": {
                "title": citation_data.get('title', ''),
                "author": citation_data.get('author', ''),
                "isbn": citation_data.get('isbn', ''),
                "publisher": citation_data.get('publisher', ''),
                "publication_year": citation_data.get('year', ''),
                "edition": citation_data.get('edition', '')
            }
        }

        # If we have MMS ID (book is in catalog), link to it
        if citation_data.get('mms_id'):
            citation_payload['mms_id'] = citation_data['mms_id']

        response = requests.post(endpoint, headers=headers, json=citation_payload)

        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            citation_id = result.get('id', '')
            print(f"      ✓ Citation added: {citation_data.get('title', '')[:40]}")
            return citation_id
        elif response.status_code == 401 or response.status_code == 403:
            print(f"      ✗ PERMISSION ERROR: No Citations API permissions")
            return None
        else:
            print(f"      ✗ Error adding citation: {response.status_code}")
            return None

    except Exception as e:
        print(f"      ✗ Exception: {str(e)}")
        return None

# ============================================================================
# PROCESS COURSE DATA
# ============================================================================

def process_courses(input_file, api_key, base_url, dry_run=False):
    """
    Process course data and create courses/reading lists in Alma.

    Args:
        input_file: Path to Excel file with course and textbook data
        api_key: Alma API key
        base_url: Alma API base URL
        dry_run: If True, only show what would be created (don't actually create)

    Returns:
        DataFrame with results
    """
    print("=" * 70)
    if dry_run:
        print("DRY RUN MODE - No changes will be made to Alma")
    print("=" * 70)

    # Read input data
    print(f"\nReading input file: {input_file}")
    df = pd.read_excel(input_file)

    # Filter to only include books that were found in catalog
    if 'Status' in df.columns:
        df_found = df[df['Status'] == 'Found'].copy()
        print(f"  Found {len(df_found)} textbooks in catalog (out of {len(df)} total)")
        df = df_found

    # Group by course
    courses = df.groupby(['Course', 'Section'])

    results = []

    print(f"\nProcessing {len(courses)} unique courses...\n")

    for (course_code, section), course_data in courses:
        print(f"\n[Course: {course_code} Section: {section}]")

        # Get course information from first row
        first_row = course_data.iloc[0]

        # Parse instructor name
        instructor_name = str(first_row.get('Instructor_Name', ''))
        if ',' in instructor_name:
            last_name, first_name = instructor_name.split(',', 1)
            last_name = last_name.strip()
            first_name = first_name.strip()
        else:
            first_name = ''
            last_name = instructor_name

        course_info = {
            'course_code': f"{course_code}-{section}",
            'course_name': str(first_row.get('Course_Description', course_code)),
            'section': str(section),
            'department': course_code.split()[0] if ' ' in course_code else course_code,
            'term': str(first_row.get('Term', '2026 Spring Term')),
            'instructor_id': str(first_row.get('EmplID', '')),
            'instructor_first': first_name,
            'instructor_last': last_name,
            'start_date': str(first_row.get('Course_Start_Date', '2026-01-26')),
            'end_date': str(first_row.get('Course_End_Date', '2026-05-26')),
            'enrollment': int(first_row.get('Total_Enrollment', 0))
        }

        # Track whether course already existed or was newly created
        course_status = ""

        if dry_run:
            # Check if course exists even in dry run mode
            existing_course_id = get_course(course_code, str(section), api_key, base_url)

            if existing_course_id:
                print(f"  [DRY RUN] Course already exists: {existing_course_id}")
                print(f"    Would add {len(course_data)} textbook(s) to existing course")
                course_status = "Already Exists"
                course_id = existing_course_id
            else:
                print(f"  [DRY RUN] Would create NEW course:")
                print(f"    Code: {course_info['course_code']}")
                print(f"    Section: {course_info['section']}")
                print(f"    Instructor: {course_info['instructor_first']} {course_info['instructor_last']}")
                print(f"    Textbooks: {len(course_data)} items")
                course_status = "Needs Creation"
                course_id = "DRY_RUN_COURSE_ID"

            list_id = "DRY_RUN_LIST_ID"
        else:
            # Check if course already exists
            course_id = get_course(course_code, str(section), api_key, base_url)

            if course_id:
                print(f"  ℹ️  Course already exists: {course_id}")
                course_status = "Already Exists"
            else:
                # Create course
                course_id = create_course(course_info, api_key, base_url)
                if course_id:
                    course_status = "Newly Created"

            if not course_id:
                print(f"  ⚠️  Skipping - could not create/find course")
                course_status = "Failed"
                continue

            # Create reading list for this course
            list_name = f"{course_code} Required Textbooks"
            list_id = create_reading_list(course_id, list_name, api_key, base_url)

            if not list_id:
                print(f"  ⚠️  Skipping reading list creation")
                continue

        # Add textbooks as citations
        textbook_count = 0
        for idx, textbook in course_data.iterrows():
            citation_info = {
                'title': str(textbook.get('Title', '')),
                'author': str(textbook.get('Author', '')),
                'isbn': str(textbook.get('ISBN', '')),
                'publisher': str(textbook.get('Publisher', '')),
                'year': str(textbook.get('Published', '')),
                'edition': str(textbook.get('Edition', '')),
                'mms_id': str(textbook.get('MMS_ID', ''))
            }

            if dry_run:
                print(f"    [DRY RUN] Would add citation: {citation_info['title'][:40]}")
                textbook_count += 1
            else:
                citation_id = add_citation(course_id, list_id, citation_info, api_key, base_url)
                if citation_id:
                    textbook_count += 1

        results.append({
            'Course': course_code,
            'Section': section,
            'Instructor': f"{first_name} {last_name}",
            'Course_ID': course_id,
            'List_ID': list_id if not dry_run else 'DRY_RUN',
            'Textbooks_Added': textbook_count,
            'Course_Status': course_status,
            'Mode': 'Dry Run' if dry_run else 'Live'
        })

    return pd.DataFrame(results)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Alma Course Reserves Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python course_automation_tool.py                    # Run in production mode (dry-run)
  python course_automation_tool.py --sandbox          # Run in sandbox mode (dry-run)
        """
    )
    parser.add_argument(
        '--sandbox',
        action='store_true',
        help='Use sandbox environment (config_sandbox.json)'
    )
    args = parser.parse_args()

    print("=" * 70)
    print("ALMA COURSE RESERVES AUTOMATION TOOL")
    if args.sandbox:
        print("🧪 SANDBOX MODE")
    print("=" * 70)
    print()

    # Check for permissions first
    print("⚠️  IMPORTANT: This tool requires additional API permissions:")
    print("   - Courses API (Read/Write)")
    print("   - Reading Lists API (Read/Write)")
    print("   - Citations API (Read/Write)")
    print()
    print("Running in DRY RUN mode to show what would be created...")
    print()

    # Load configuration
    config = load_config(use_sandbox=args.sandbox)
    api_key = config.get('alma_api_key', '')
    base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

    if not api_key:
        config_file = 'config_sandbox.json' if args.sandbox else 'config.json'
        print(f"ERROR: No API key found in {config_file}")
        exit(1)

    print(f"Environment: {'SANDBOX' if args.sandbox else 'PRODUCTION'}")
    print(f"API Base URL: {base_url}")
    print()

    # Input file (use your ISBN search results with course info)
    input_file = '/Users/patty_home/Desktop/Agentic AI/data/primo_isbn_results_20260223_133345.xlsx'

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found!")
        print("Please run the ISBN search first to generate this file.")
        exit(1)

    # Default to dry run for safety (change to False when you have permissions)
    dry_run = True

    # Process courses
    results_df = process_courses(input_file, api_key, base_url, dry_run=dry_run)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = '/Users/patty_home/Desktop/Agentic AI/data'
    output_file = f'{output_dir}/course_automation_results_{timestamp}.xlsx'

    print(f"\nSaving results to: {output_file}")
    results_df.to_excel(output_file, index=False)

    # Print summary
    print("\n" + "=" * 70)
    print("AUTOMATION COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"Total courses processed: {len(results_df)}")
    print()

    # Count course statuses
    if 'Course_Status' in results_df.columns:
        status_counts = results_df['Course_Status'].value_counts()
        print("Course Status Breakdown:")
        if 'Already Exists' in status_counts:
            print(f"  • Courses already in Alma: {status_counts['Already Exists']}")
        if 'Needs Creation' in status_counts:
            print(f"  • Courses that need to be created: {status_counts['Needs Creation']}")
        if 'Newly Created' in status_counts:
            print(f"  • Courses newly created: {status_counts['Newly Created']}")
        if 'Failed' in status_counts:
            print(f"  • Failed operations: {status_counts['Failed']}")
        print()

    print(f"Total textbooks to be added: {results_df['Textbooks_Added'].sum()}")

    if dry_run:
        print(f"\n⚠️  DRY RUN MODE - No actual changes were made")
        print(f"To run for real, edit line 440 and set dry_run=False")
        print(f"(Only do this after you have the required API permissions)")
    print(f"\nResults saved to: {output_file}")
    print("=" * 70)

if __name__ == "__main__":
    main()
