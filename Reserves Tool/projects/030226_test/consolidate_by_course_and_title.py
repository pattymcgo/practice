"""
Consolidate by Course + Book Title (not ISBN)
This combines all sections/instructors for the same course+book,
even if they're using different editions/ISBNs
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("Consolidating by COURSE + BOOK TITLE")
print("=" * 70)
print()

# Read the books dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books.xlsx'
print(f"Reading: {input_file}")
df = pd.read_excel(input_file)

print(f"Original rows: {len(df)}")
print()

# Group by Course and Title (not ISBN!)
def consolidate_group(group):
    """Consolidate all rows for the same course+title"""
    # Get unique sections and instructors
    sections = group['Section'].dropna().unique()
    instructors = group['Instructor_Name'].dropna().unique()
    emplids = group['EmplID'].dropna().unique()

    # Get all unique ISBNs for this title
    isbns = group['ISBN'].dropna().unique()

    # Create the consolidated row
    consolidated = group.iloc[0].copy()

    # Combine sections (comma-separated, sorted)
    consolidated['Section'] = ', '.join(sorted([str(s) for s in sections]))

    # Combine instructors (slash-separated, sorted)
    consolidated['Instructor_Name'] = ' / '.join(sorted(instructors))

    # Combine EmplIDs (comma-separated, no decimals)
    def fix_emplid(val):
        try:
            return str(int(float(val)))
        except:
            return str(val)

    consolidated['EmplID'] = ', '.join(sorted([fix_emplid(e) for e in emplids if pd.notna(e)]))

    # Sum enrollments
    consolidated['Total_Enrollment'] = group['Total_Enrollment'].sum()

    # Use the max capacity
    consolidated['Capacity'] = group['Capacity'].max()

    # Combine class numbers
    class_numbers = group['Class_Number'].dropna().unique()
    consolidated['Class_Number'] = ', '.join(sorted([str(c) for c in class_numbers]))

    # Keep all ISBNs (comma-separated)
    consolidated['ISBN_All_Editions'] = ', '.join([str(isbn) for isbn in isbns])
    consolidated['Num_Editions'] = len(isbns)

    return consolidated

# Group by Course and Title
print("Grouping by Course and Title (combining different editions)...")
grouped = df.groupby(['Course', 'Title']).apply(consolidate_group, include_groups=False).reset_index()

# Remove extra level columns
cols_to_drop = [col for col in grouped.columns if col.startswith('level_')]
if cols_to_drop:
    grouped = grouped.drop(cols_to_drop, axis=1)

print(f"Consolidated rows: {len(grouped)}")
print(f"Reduced by: {len(df) - len(grouped)} rows")
print()

# Save consolidated dataset
output_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_final_consolidated.xlsx'
grouped.to_excel(output_file, index=False)

print(f"Saved to: test_22_courses_final_consolidated.xlsx")
print()

# Show examples
print("Examples of consolidated courses:")
print("-" * 70)

# Show courses with multiple sections/editions
multi_section = grouped[grouped['Section'].str.contains(',', na=False)]
if len(multi_section) > 0:
    print(f"\nCourses with multiple sections combined ({len(multi_section)} entries):")
    for idx, row in multi_section.head(10).iterrows():
        print(f"\n{row['Course']:15} - {row['Title'][:50]}")
        print(f"  Sections: {row['Section']}")
        print(f"  Instructors: {row['Instructor_Name']}")
        print(f"  Editions: {row['Num_Editions']} ({row['ISBN_All_Editions'][:60]}...)")

print()
print("Courses per course code:")
course_counts = grouped['Course'].value_counts().sort_index()
for course, count in course_counts.items():
    print(f"  {course:15} - {count} unique book(s)")

print()
print(f"Total Alma course entries to create: {len(grouped)}")
print("=" * 70)
