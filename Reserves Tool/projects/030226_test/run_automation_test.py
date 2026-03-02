"""
Automation tool for 22 test courses - UPDATED for smart consolidated data
- Uses correct course code format (no section suffix)
- Handles combined sections and instructors
- Creates courses + reading lists + citations
"""

import sys
import os
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update')
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search')

import pandas as pd
import requests
import json
from datetime import datetime

print("=" * 70)
print("AUTOMATION TOOL - 22 TEST COURSES")
print("=" * 70)
print()

# Load config
config_path = '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

api_key = config.get('alma_api_key', '')
base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

if not api_key:
    print("ERROR: No API key found in config.json")
    sys.exit(1)

print(f"Environment: PRODUCTION")
print(f"API Base URL: {base_url}")
print()

# Use smart consolidated data
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_smart_consolidated.xlsx'
print(f"Input file: test_22_courses_smart_consolidated.xlsx")
print()

# DRY RUN MODE (set to False to run for real)
DRY_RUN = True

if DRY_RUN:
    print("⚠️  MODE: DRY RUN (no changes will be made)")
else:
    print("🔴 MODE: LIVE RUN (will create courses in Alma)")

print()
print("=" * 70)
print()

# Read the smart consolidated data
df = pd.read_excel(input_file)

print(f"Dataset loaded:")
print(f"  Total rows: {len(df)}")
print(f"  Unique course codes: {df['Course'].nunique()}")
print()

# ============================================================================
# ALMA API FUNCTIONS
# ============================================================================

def create_course(course_data, api_key, base_url):
    """Create a course in Alma"""
    try:
        endpoint = f"{base_url}/almaws/v1/courses"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        course_payload = {
            "code": course_data['course_code'],  # Just the course code (no section suffix)
            "name": course_data['course_name'],
            "section": course_data['section'],  # Combined sections
            "academic_department": {
                "value": course_data.get('department', 'General')
            },
            "term": [{
                "value": course_data.get('term', '2026 Spring')
            }],
            "start_date": course_data.get('start_date', '2026-01-26'),
            "end_date": course_data.get('end_date', '2026-05-26'),
            "participants_number": course_data.get('enrollment', 0)
        }

        # Handle multiple instructors (if combined with " / ")
        instructor_names = course_data.get('instructor_name', '')
        if pd.notna(instructor_names) and str(instructor_names) != 'nan':
            instructors_list = str(instructor_names).split(' / ')
            course_payload['instructor'] = []

            for instr in instructors_list:
                if ',' in instr:
                    last, first = instr.split(',', 1)
                    course_payload['instructor'].append({
                        "first_name": first.strip(),
                        "last_name": last.strip()
                    })

        response = requests.post(endpoint, headers=headers, json=course_payload)

        if response.status_code in [200, 201]:
            result = response.json()
            course_id = result.get('id', '')
            print(f"    ✓ Course created: {course_id}")
            return course_id
        else:
            print(f"    ✗ Error creating course: {response.status_code}")
            print(f"      Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"    ✗ Exception: {str(e)}")
        return None

def create_reading_list(course_id, list_name, api_key, base_url):
    """Create a reading list for a course"""
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

        if response.status_code in [200, 201]:
            result = response.json()
            list_id = result.get('id', '')
            print(f"      ✓ Reading list created: {list_id}")
            return list_id
        else:
            print(f"      ✗ Error creating reading list: {response.status_code}")
            return None

    except Exception as e:
        print(f"      ✗ Exception: {str(e)}")
        return None

def add_citation(course_id, list_id, citation_data, api_key, base_url):
    """Add a citation (book) to a reading list"""
    try:
        endpoint = f"{base_url}/almaws/v1/courses/{course_id}/reading-lists/{list_id}/citations"

        headers = {
            "Authorization": f"apikey {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

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
                "edition": citation_data.get('edition', '')
            }
        }

        response = requests.post(endpoint, headers=headers, json=citation_payload)

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"        ✓ Citation added: {citation_data.get('title', '')[:40]}")
            return result.get('id', '')
        else:
            print(f"        ✗ Error adding citation: {response.status_code}")
            return None

    except Exception as e:
        print(f"        ✗ Exception: {str(e)}")
        return None

# ============================================================================
# PROCESS COURSES
# ============================================================================

print("Processing courses...")
print("=" * 70)
print()

results = []

# Group by Course + Section (to handle cases where same course+section has multiple books)
# In smart consolidated data, rows with same Course+Section should be in same Alma course
grouped = df.groupby(['Course', 'Section'])

for (course_code, section), course_books in grouped:
    # Get course info from first row
    first_row = course_books.iloc[0]

    print(f"[{course_code} - Section(s): {section}]")

    course_info = {
        'course_code': course_code,  # Just the course code (FIXED!)
        'course_name': str(first_row.get('Course', course_code)),
        'section': str(section),  # Combined sections
        'department': course_code.split()[0] if ' ' in course_code else course_code,
        'term': str(first_row.get('Term', '2026 Spring Term')),
        'instructor_name': str(first_row.get('Instructor_Name', '')),
        'start_date': str(first_row.get('Course_Start_Date', '2026-01-26')),
        'end_date': str(first_row.get('Course_End_Date', '2026-05-26')),
        'enrollment': int(first_row.get('Total_Enrollment', 0))
    }

    if DRY_RUN:
        print(f"  [DRY RUN] Would create course:")
        print(f"    Course Code: {course_info['course_code']}")
        print(f"    Section(s): {course_info['section']}")
        print(f"    Instructor(s): {course_info['instructor_name']}")
        print(f"    Enrollment: {course_info['enrollment']}")

        course_id = "DRY_RUN_COURSE_ID"
        list_id = "DRY_RUN_LIST_ID"

        print(f"  [DRY RUN] Would create reading list: {course_code} Required Textbooks")

        # Add books as citations
        print(f"  [DRY RUN] Would add {len(course_books)} book(s) as citations:")
        for idx, book_row in course_books.iterrows():
            title = book_row['Title']
            print(f"    - {title[:60]}")

        results.append({
            'Course': course_code,
            'Section': section,
            'Instructor': course_info['instructor_name'],
            'Course_ID': 'DRY_RUN',
            'List_ID': 'DRY_RUN',
            'Books_Added': len(course_books),
            'Mode': 'Dry Run'
        })

    else:
        # Create course
        course_id = create_course(course_info, api_key, base_url)

        if not course_id:
            print(f"  ⚠️  Failed to create course, skipping...")
            results.append({
                'Course': course_code,
                'Section': section,
                'Instructor': course_info['instructor_name'],
                'Course_ID': 'FAILED',
                'List_ID': 'N/A',
                'Books_Added': 0,
                'Mode': 'Live - Failed'
            })
            print()
            continue

        # Create reading list
        list_name = f"{course_code} Required Textbooks"
        list_id = create_reading_list(course_id, list_name, api_key, base_url)

        if not list_id:
            print(f"  ⚠️  Failed to create reading list, skipping...")
            results.append({
                'Course': course_code,
                'Section': section,
                'Instructor': course_info['instructor_name'],
                'Course_ID': course_id,
                'List_ID': 'FAILED',
                'Books_Added': 0,
                'Mode': 'Live - Failed'
            })
            print()
            continue

        # Add books as citations
        books_added = 0
        for idx, book_row in course_books.iterrows():
            citation_info = {
                'title': str(book_row.get('Title', '')),
                'author': str(book_row.get('Author', '')),
                'isbn': str(book_row.get('ISBN', '')),
                'publisher': str(book_row.get('Publisher', '')),
                'edition': str(book_row.get('Edition', ''))
            }

            citation_id = add_citation(course_id, list_id, citation_info, api_key, base_url)
            if citation_id:
                books_added += 1

        results.append({
            'Course': course_code,
            'Section': section,
            'Instructor': course_info['instructor_name'],
            'Course_ID': course_id,
            'List_ID': list_id,
            'Books_Added': books_added,
            'Mode': 'Live'
        })

    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================

results_df = pd.DataFrame(results)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'/Users/patty_home/Desktop/Agentic AI/projects/030226_test/automation_results_{timestamp}.xlsx'

results_df.to_excel(output_file, index=False)

# ============================================================================
# SUMMARY
# ============================================================================

print("=" * 70)
print("AUTOMATION COMPLETE - SUMMARY")
print("=" * 70)
print(f"Total courses processed: {len(results_df)}")
print(f"Total books added: {results_df['Books_Added'].sum()}")
print()

# Course breakdown
course_counts = results_df.groupby('Course').size().sort_index()
print("Courses created:")
for course, count in course_counts.items():
    print(f"  {course:15} - {count} entry/entries")

print()
if DRY_RUN:
    print("⚠️  DRY RUN MODE - No actual changes were made")
    print()
    print("To run for REAL:")
    print("  1. Edit this file and set DRY_RUN = False on line 34")
    print("  2. Make sure you have API permissions for:")
    print("     - Courses API (Read/Write)")
    print("     - Reading Lists API (Read/Write)")
    print("     - Citations API (Read/Write)")
    print("  3. Run the script again")
else:
    print("✅ LIVE RUN COMPLETE - Changes were made to Alma")

print()
print(f"Results saved to: automation_results_{timestamp}.xlsx")
print("=" * 70)
