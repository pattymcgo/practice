"""
Create a test dataset with only the 22 courses that don't exist in Alma
"""

import pandas as pd

# Courses to include in test
test_courses = [
    'ENG WK95', 'HSD 110', 'HSD 190', 'HSD 195', 'HSD 202', 'HSD 211',
    'HSD 220', 'HSD 225', 'HSD 230', 'HSD 235', 'HSD 240', 'HSD 250',
    'HSD 255', 'HSD 260', 'HSD 280', 'HSD 290', 'HSD 295', 'HSD 296',
    'HSD 301', 'HSD 302', 'ITL 106H', 'MAT 104.5'
]

print("=" * 70)
print("Creating test dataset with 22 courses")
print("=" * 70)
print()

# Read the full dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx'
print(f"Reading: {input_file}")
df = pd.read_excel(input_file)

print(f"Total rows in original file: {len(df)}")
print()

# Filter to only the test courses
df_test = df[df['Course'].isin(test_courses)].copy()

print(f"Filtered to {len(df_test)} rows for the 22 test courses")
print()

# Show breakdown by course
print("Rows per course:")
course_counts = df_test['Course'].value_counts().sort_index()
for course, count in course_counts.items():
    print(f"  {course:15} - {count:3} rows")

print()

# Save the test dataset in the test folder
output_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses.xlsx'
df_test.to_excel(output_file, index=False)

print(f"Saved test dataset to: {output_file}")
print("=" * 70)
