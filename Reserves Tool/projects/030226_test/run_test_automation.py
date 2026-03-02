"""
Test script to run course automation on the consolidated 22 courses dataset
This is a DRY-RUN by default - no actual changes will be made to Alma
"""

import sys
import os

# Add the scripts directory to the path so we can import the automation functions
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update')
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search')

import pandas as pd
import json
from datetime import datetime

# Import the automation functions
from course_automation_tool import load_config, process_courses

print("=" * 70)
print("TEST AUTOMATION - 22 COURSES")
print("=" * 70)
print()

# Load production config
print("Loading configuration...")
config = load_config(use_sandbox=False)
api_key = config.get('alma_api_key', '')
base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

if not api_key:
    print("ERROR: No API key found in config.json")
    sys.exit(1)

print(f"Environment: PRODUCTION")
print(f"API Base URL: {base_url}")
print()

# Use the consolidated test dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books_consolidated.xlsx'

print(f"Input file: test_22_courses_books_consolidated.xlsx")
print(f"Mode: DRY RUN (no changes will be made)")
print()

# Check if input file exists
if not os.path.exists(input_file):
    print(f"ERROR: Input file not found!")
    sys.exit(1)

# Show what we're testing
df = pd.read_excel(input_file)
print(f"Test dataset:")
print(f"  Total rows: {len(df)}")
print(f"  Unique courses: {df['Course'].nunique()}")
print(f"  Unique books: {len(df)}")
print()

# Run in DRY RUN mode
dry_run = True

print("⚠️  DRY RUN MODE - Checking which courses exist in Alma...")
print()

# Process courses
results_df = process_courses(input_file, api_key, base_url, dry_run=dry_run)

# Save results to the test folder
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_automation_results_{timestamp}.xlsx'

print(f"\nSaving results to: test_automation_results_{timestamp}.xlsx")
results_df.to_excel(output_file, index=False)

# Print summary
print("\n" + "=" * 70)
print("TEST AUTOMATION COMPLETE - SUMMARY")
print("=" * 70)
print(f"Total courses processed: {len(results_df)}")
print()

# Count course statuses
if 'Course_Status' in results_df.columns:
    status_counts = results_df['Course_Status'].value_counts()
    print("Course Status Breakdown:")
    if 'Already Exists' in status_counts:
        print(f"  ✓ Courses already in Alma: {status_counts['Already Exists']}")
    if 'Needs Creation' in status_counts:
        print(f"  + Courses that need to be created: {status_counts['Needs Creation']}")
    if 'Newly Created' in status_counts:
        print(f"  ✓ Courses newly created: {status_counts['Newly Created']}")
    if 'Failed' in status_counts:
        print(f"  ✗ Failed operations: {status_counts['Failed']}")
    print()

print(f"Total books to be added: {results_df['Textbooks_Added'].sum()}")

if dry_run:
    print(f"\n⚠️  DRY RUN MODE - No actual changes were made")
    print(f"Review the results file to see what would be created.")
    print(f"If everything looks good, we can run it for real next.")

print(f"\nResults saved to: {output_file}")
print("=" * 70)
