"""
Quick script to check if specific courses exist in Alma
"""

import pandas as pd
import requests
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

# Load config
config_path = os.path.join(os.path.dirname(__file__), 'isbn_search', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

api_key = config['alma_api_key']
base_url = config.get('base_url', 'https://api-na.hosted.exlibrisgroup.com')

# Courses to check
courses_to_check = [
    'ENG WK95', 'HSD 110', 'HSD 190', 'HSD 195', 'HSD 202', 'HSD 211',
    'HSD 220', 'HSD 225', 'HSD 230', 'HSD 235', 'HSD 240', 'HSD 250',
    'HSD 255', 'HSD 260', 'HSD 280', 'HSD 290', 'HSD 295', 'HSD 296',
    'HSD 301', 'HSD 302', 'ITL 106H', 'MAT 104.5'
]

print("=" * 70)
print("CHECKING COURSES IN ALMA")
print("=" * 70)
print()

# Get all courses from Alma
endpoint = f"{base_url}/almaws/v1/courses"
headers = {
    "Authorization": f"apikey {api_key}",
    "Accept": "application/json"
}
params = {"limit": 1000}

print("Fetching all courses from Alma...")
response = requests.get(endpoint, headers=headers, params=params)

if response.status_code != 200:
    print(f"ERROR: Could not fetch courses from Alma (status {response.status_code})")
    print(f"Response: {response.text[:200]}")
    sys.exit(1)

result = response.json()
alma_courses = result.get('course', [])
print(f"Found {len(alma_courses)} total courses in Alma")
print()

# Extract all course codes from Alma
alma_course_codes = set()
for course in alma_courses:
    code = course.get('code', '')
    # Remove instructor names in parentheses
    if '(' in code:
        code = code.split('(')[0].strip()
    alma_course_codes.add(code)

# Check each course
print("Checking if courses exist in Alma:")
print("-" * 70)

found = []
not_found = []

for course_code in courses_to_check:
    # Check direct match
    if course_code in alma_course_codes:
        found.append(course_code)
        print(f"✓ {course_code:15} - FOUND in Alma")
    else:
        not_found.append(course_code)
        print(f"✗ {course_code:15} - NOT FOUND in Alma")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total courses checked: {len(courses_to_check)}")
print(f"Found in Alma: {len(found)}")
print(f"NOT found in Alma: {len(not_found)}")

if not_found:
    print()
    print("Courses NOT in Alma:")
    for course in not_found:
        print(f"  - {course}")
