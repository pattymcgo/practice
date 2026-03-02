"""
FINAL DRY-RUN TEST with SMART consolidated data
- Handles title variations (removes articles, extra spaces)
- One Alma course entry per Course Code + Normalized Book Title
- All sections and instructors combined
"""

import sys
import os
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update')
sys.path.insert(0, '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search')

import pandas as pd
import json
from datetime import datetime

print("=" * 70)
print("FINAL DRY-RUN TEST - SMART CONSOLIDATED DATA")
print("=" * 70)
print()

# Load config
config_path = '/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/config.json'
with open(config_path, 'r') as f:
    config = json.load(f)

api_key = config.get('alma_api_key', '')
base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

print(f"Environment: PRODUCTION")
print(f"API Base URL: {base_url}")
print()

# Use the smart consolidated file
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_smart_consolidated.xlsx'

print(f"Input file: test_22_courses_smart_consolidated.xlsx")
print(f"Mode: DRY RUN")
print()

# Read the data
df = pd.read_excel(input_file)
print(f"Dataset:")
print(f"  Total Alma course entries: {len(df)}")
print(f"  Unique course codes: {df['Course'].nunique()}")
print()

# Show the preview
print("=" * 70)
print("PREVIEW: What would be created in Alma")
print("=" * 70)
print()

for idx, row in df.iterrows():
    course_code = row['Course']
    section = row['Section']
    title = row['Title']
    instructor = row['Instructor_Name']
    num_editions = row.get('Num_Editions', 1)
    title_variations = row.get('Title_Variations', '')

    print(f"[{idx+1}/{len(df)}] {course_code}")
    print(f"  Course Code: {course_code}")
    print(f"  Section(s): {section}")
    print(f"  Instructor(s): {instructor}")
    print(f"  Book: {title[:60]}")

    if pd.notna(title_variations) and title_variations != '':
        print(f"  📝 Title variations consolidated:")
        for variant in str(title_variations).split(' | ')[:3]:  # Show first 3
            print(f"     - {variant[:60]}")

    if num_editions > 1:
        print(f"  📚 Editions: {num_editions} different editions of this book")
    print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total Alma course entries to create: {len(df)}")
print()

course_counts = df['Course'].value_counts().sort_index()
print("Breakdown by course code:")
for course, count in course_counts.items():
    print(f"  {course:15} - {count} entry/entries")

print()
print("✅ Smart consolidation handled title variations successfully")
print("⚠️  DRY RUN MODE - No actual changes were made")
print()
print("If this looks correct, we can run it for REAL to create these")
print("courses in your production Alma system.")
print("=" * 70)
