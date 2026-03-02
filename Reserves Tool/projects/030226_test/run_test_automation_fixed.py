"""
Test script with FIXED course creation logic
- Course Code: HSD 110 (not "HSD 110-0800, 0803, 1101")
- Section: "0800, 0803, 1101" (combined sections)
"""

import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update')
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search')

import pandas as pd
import requests
from datetime import datetime
import json

print("=" * 70)
print("TEST AUTOMATION - FIXED COURSE CODE FORMAT")
print("=" * 70)
print()

# Load config
config_path = '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

api_key = config.get('alma_api_key', '')
base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

if not api_key:
    print("ERROR: No API key found")
    sys.exit(1)

print(f"Environment: PRODUCTION")
print(f"API Base URL: {base_url}")
print()

# Input file
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books_consolidated.xlsx'

print(f"Input file: test_22_courses_books_consolidated.xlsx")
print(f"Mode: DRY RUN (no changes will be made)")
print()

# Read the data
df = pd.read_excel(input_file)
print(f"Test dataset:")
print(f"  Total rows: {len(df)}")
print(f"  Unique courses: {df['Course'].nunique()}")
print()

# Process courses - FIXED VERSION
print("=" * 70)
print("DRY RUN MODE - Previewing what would be created")
print("=" * 70)
print()

results = []

# Group by Course and Section (each unique course+section combination)
for idx, (group_key, course_data) in enumerate(df.groupby(['Course', 'Section'])):
    course_code, section = group_key
    first_row = course_data.iloc[0]

    # Parse instructor name
    instructor_full = str(first_row.get('Instructor_Name', '')).split(',')
    if len(instructor_full) >= 2:
        instructor_last = instructor_full[0].strip()
        instructor_first = instructor_full[1].strip()
    else:
        instructor_first = instructor_full[0].strip() if instructor_full else ''
        instructor_last = ''

    print(f"[Course: {course_code} Section: {section}]")
    print(f"  [DRY RUN] Would create NEW course:")
    print(f"    Course Code: {course_code}")  # <-- FIXED: Just the course code!
    print(f"    Section: {section}")
    print(f"    Instructor: {first_row.get('Instructor_Name', '')}")
    print(f"    Books: {len(course_data)} item(s)")

    # Show the books
    for book_idx, book_row in course_data.iterrows():
        title = book_row['Title'][:50]
        print(f"    [DRY RUN] Would add citation: {title}")

    results.append({
        'Course': course_code,
        'Section': section,
        'Instructor': first_row.get('Instructor_Name', ''),
        'Course_Status': 'Needs Creation',
        'Textbooks_Added': len(course_data),
        'Mode': 'Dry Run'
    })
    print()

# Save results
results_df = pd.DataFrame(results)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_automation_fixed_{timestamp}.xlsx'

results_df.to_excel(output_file, index=False)

# Print summary
print("=" * 70)
print("TEST AUTOMATION COMPLETE - SUMMARY")
print("=" * 70)
print(f"Total course entries to create: {len(results_df)}")
print()

# Show breakdown
print("Courses to be created:")
course_counts = results_df.groupby('Course').size().sort_index()
for course, count in course_counts.items():
    print(f"  {course:15} - {count} entries")

print()
print(f"Total books to be added: {results_df['Textbooks_Added'].sum()}")
print()
print(f"⚠️  DRY RUN MODE - No actual changes were made")
print(f"Results saved to: test_automation_fixed_{timestamp}.xlsx")
print("=" * 70)
