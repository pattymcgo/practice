"""
Consolidate courses by combining sections and instructors for the same course/book
"""

import pandas as pd

print("=" * 70)
print("Consolidating courses - combining sections and instructors")
print("=" * 70)
print()

# Read the books dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books.xlsx'
print(f"Reading: {input_file}")
df = pd.read_excel(input_file)

print(f"Original rows: {len(df)}")
print()

# Group by Course and ISBN (each unique book)
# Combine sections and instructors
def consolidate_group(group):
    """Consolidate a group of rows for the same course+book"""
    # Get unique sections and instructors
    sections = group['Section'].dropna().unique()
    instructors = group['Instructor_Name'].dropna().unique()
    emplids = group['EmplID'].dropna().unique()

    # Create the consolidated row
    consolidated = group.iloc[0].copy()

    # Combine sections (comma-separated)
    consolidated['Section'] = ', '.join(sorted([str(s) for s in sections]))

    # Combine instructors (comma-separated)
    consolidated['Instructor_Name'] = ' / '.join(sorted(instructors))

    # Combine EmplIDs (comma-separated)
    consolidated['EmplID'] = ', '.join(sorted([str(e) for e in emplids]))

    # Sum enrollments
    consolidated['Total_Enrollment'] = group['Total_Enrollment'].sum()

    # Use the max capacity
    consolidated['Capacity'] = group['Capacity'].max()

    # Combine class numbers
    class_numbers = group['Class_Number'].dropna().unique()
    consolidated['Class_Number'] = ', '.join(sorted([str(c) for c in class_numbers]))

    return consolidated

# Group by Course and ISBN
print("Grouping by Course and ISBN...")
grouped = df.groupby(['Course', 'ISBN']).apply(consolidate_group, include_groups=False).reset_index(drop=True)

print(f"Consolidated rows: {len(grouped)}")
print(f"Reduced by: {len(df) - len(grouped)} rows")
print()

# Save consolidated dataset
output_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books_consolidated.xlsx'
grouped.to_excel(output_file, index=False)

print(f"Saved to: test_22_courses_books_consolidated.xlsx")
print()

# Show examples of consolidation
print("Examples of consolidated courses:")
print("-" * 70)

# Show courses that had multiple sections combined
multi_section = grouped[grouped['Section'].str.contains(',', na=False)]
if len(multi_section) > 0:
    print(f"\nCourses with multiple sections combined ({len(multi_section)} books):")
    for idx, row in multi_section.head(5).iterrows():
        print(f"  {row['Course']:15} - {row['Title'][:40]:40}")
        print(f"    Sections: {row['Section']}")
        print(f"    Instructors: {row['Instructor_Name']}")
        print()

# Show breakdown by course
print("Books per course (after consolidation):")
course_counts = grouped['Course'].value_counts().sort_index()
for course, count in course_counts.items():
    print(f"  {course:15} - {count:3} unique books")

print()
print("=" * 70)
