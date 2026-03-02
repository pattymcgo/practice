"""
Consolidate by COURSE ONLY - combine all sections, instructors, and books
for the same course into one Alma course entry
"""

import pandas as pd

print("=" * 70)
print("Consolidating by COURSE ONLY - combining all sections & instructors")
print("=" * 70)
print()

# Read the books dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books.xlsx'
print(f"Reading: {input_file}")
df = pd.read_excel(input_file)

print(f"Original rows: {len(df)}")
print()

# Group by Course ONLY (not by ISBN)
# For each course, collect ALL unique sections, instructors, and books
def consolidate_course(group):
    """Consolidate all rows for the same course"""
    # Get unique sections and instructors
    sections = group['Section'].dropna().unique()
    instructors = group['Instructor_Name'].dropna().unique()
    emplids = group['EmplID'].dropna().unique()

    # Create consolidated data
    consolidated = {
        'Course': group['Course'].iloc[0],
        'Section': ', '.join(sorted([str(s) for s in sections])),
        'Instructor_Name': ' / '.join(sorted(instructors)),
        'EmplID': ', '.join(sorted([str(int(float(e))) for e in emplids if pd.notna(e)])),
        'Total_Enrollment': group['Total_Enrollment'].sum(),
        'Capacity': group['Capacity'].max(),
        'Course_Start_Date': group['Course_Start_Date'].iloc[0],
        'Course_End_Date': group['Course_End_Date'].iloc[0],
        'Institution': group['Institution'].iloc[0],
        'Term': group['Term'].iloc[0],
        'Session': group['Session'].iloc[0],

        # Keep all the books as a list
        'Books': group[['ISBN', 'Title', 'Author', 'Publisher', 'Edition', 'Price']].to_dict('records')
    }

    return pd.Series(consolidated)

# Group by Course
print("Grouping by Course (combining all books per course)...")
grouped = df.groupby('Course').apply(consolidate_course, include_groups=False).reset_index(drop=True)

print(f"Consolidated to: {len(grouped)} courses")
print(f"Reduced by: {len(df) - len(grouped)} rows")
print()

# Save the course-level summary
output_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_by_course_only.xlsx'
grouped_for_excel = grouped.drop('Books', axis=1).copy()
grouped_for_excel.to_excel(output_file, index=False)

print(f"Saved course summary to: test_22_courses_by_course_only.xlsx")
print()

# Now create a detailed version with one row per book, but course info combined
print("Creating detailed version with one row per book...")
detailed_rows = []

for idx, course_row in grouped.iterrows():
    for book in course_row['Books']:
        detailed_row = {
            'Course': course_row['Course'],
            'Section': course_row['Section'],
            'Instructor_Name': course_row['Instructor_Name'],
            'EmplID': course_row['EmplID'],
            'Total_Enrollment': course_row['Total_Enrollment'],
            'Capacity': course_row['Capacity'],
            'Course_Start_Date': course_row['Course_Start_Date'],
            'Course_End_Date': course_row['Course_End_Date'],
            'Institution': course_row['Institution'],
            'Term': course_row['Term'],
            'Session': course_row['Session'],
            'ISBN': book['ISBN'],
            'Title': book['Title'],
            'Author': book['Author'],
            'Publisher': book['Publisher'],
            'Edition': book['Edition'],
            'Price': book['Price'],
        }
        detailed_rows.append(detailed_row)

detailed_df = pd.DataFrame(detailed_rows)

# Save detailed version (this is what the automation tool will use)
detailed_output = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_final.xlsx'
detailed_df.to_excel(detailed_output, index=False)

print(f"Saved detailed version to: test_22_courses_final.xlsx")
print(f"  - {len(detailed_df)} rows (one per book)")
print(f"  - {len(grouped)} unique courses")
print()

# Show summary
print("Summary of consolidated courses:")
print("-" * 70)
for idx, row in grouped.iterrows():
    print(f"{row['Course']:15} - {len(row['Books'])} books")
    print(f"  Sections: {row['Section'][:60]}...")
    print(f"  Instructors: {row['Instructor_Name'][:60]}...")
    print()

print("=" * 70)
