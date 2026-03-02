"""
Smart consolidation that handles title variations
- Normalizes titles (removes 'The', 'A', 'An', extra spaces, case)
- Groups by Course + Normalized Title
"""

import pandas as pd
import numpy as np
import re

def normalize_title(title):
    """Normalize a book title for matching"""
    if pd.isna(title):
        return ''

    # Convert to lowercase
    title = str(title).lower().strip()

    # Remove special characters and punctuation first (keep spaces)
    title = re.sub(r'[^\w\s]', '', title)

    # Remove common articles (the, a, an) from anywhere in the title
    title = re.sub(r'\b(the|a|an)\b', '', title)

    # Remove extra spaces
    title = re.sub(r'\s+', ' ', title)

    return title.strip()

print("=" * 70)
print("SMART CONSOLIDATION - Handles title variations")
print("=" * 70)
print()

# Read the books dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books.xlsx'
print(f"Reading: {input_file}")
df = pd.read_excel(input_file)

print(f"Original rows: {len(df)}")
print()

# Add normalized title column
df['Title_Normalized'] = df['Title'].apply(normalize_title)

# Show examples of normalization
print("Examples of title normalization:")
print("-" * 70)
sample_titles = df[['Title', 'Title_Normalized']].drop_duplicates().head(5)
for idx, row in sample_titles.iterrows():
    print(f"Original:   '{row['Title']}'")
    print(f"Normalized: '{row['Title_Normalized']}'")
    print()

# Group by Course and Normalized Title
def consolidate_group(group):
    """Consolidate all rows for the same course+normalized title"""
    # Get unique sections and instructors
    sections = group['Section'].dropna().unique()
    instructors = group['Instructor_Name'].dropna().unique()
    emplids = group['EmplID'].dropna().unique()

    # Get all unique ISBNs and original titles
    isbns = group['ISBN'].dropna().unique()
    titles = group['Title'].dropna().unique()

    # Create the consolidated row
    consolidated = group.iloc[0].copy()

    # Use the first non-null title as the canonical title
    consolidated['Title'] = [t for t in titles if pd.notna(t) and t != 'nan'][0] if len([t for t in titles if pd.notna(t) and t != 'nan']) > 0 else titles[0]

    # Combine sections (comma-separated, sorted)
    consolidated['Section'] = ', '.join(sorted([str(s) for s in sections]))

    # Combine instructors (slash-separated, sorted)
    valid_instructors = [i for i in instructors if pd.notna(i) and str(i) != 'nan']
    consolidated['Instructor_Name'] = ' / '.join(sorted(valid_instructors)) if valid_instructors else 'nan'

    # Combine EmplIDs
    def fix_emplid(val):
        try:
            return str(int(float(val)))
        except:
            return str(val)

    valid_emplids = [fix_emplid(e) for e in emplids if pd.notna(e)]
    consolidated['EmplID'] = ', '.join(sorted(valid_emplids)) if valid_emplids else ''

    # Sum enrollments
    consolidated['Total_Enrollment'] = group['Total_Enrollment'].sum()

    # Use the max capacity
    consolidated['Capacity'] = group['Capacity'].max()

    # Combine class numbers
    class_numbers = group['Class_Number'].dropna().unique()
    consolidated['Class_Number'] = ', '.join(sorted([str(c) for c in class_numbers]))

    # Keep all ISBNs
    valid_isbns = [str(isbn) for isbn in isbns if pd.notna(isbn)]
    consolidated['ISBN_All_Editions'] = ', '.join(valid_isbns) if valid_isbns else ''
    consolidated['Num_Editions'] = len(valid_isbns)

    # Show if there were title variations
    if len(titles) > 1:
        consolidated['Title_Variations'] = ' | '.join(titles)
    else:
        consolidated['Title_Variations'] = ''

    return consolidated

# Group by Course and Normalized Title
print("Grouping by Course and Normalized Title...")
grouped = df.groupby(['Course', 'Title_Normalized']).apply(consolidate_group, include_groups=False).reset_index()

# Remove extra level columns
cols_to_drop = [col for col in grouped.columns if col.startswith('level_')]
if cols_to_drop:
    grouped = grouped.drop(cols_to_drop, axis=1)

print(f"Consolidated rows: {len(grouped)}")
print(f"Reduced by: {len(df) - len(grouped)} rows")
print()

# Save consolidated dataset
output_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_smart_consolidated.xlsx'
grouped.to_excel(output_file, index=False)

print(f"Saved to: test_22_courses_smart_consolidated.xlsx")
print()

# Show examples of consolidation
print("Books with title variations (now consolidated):")
print("-" * 70)
variations = grouped[grouped['Title_Variations'] != '']
if len(variations) > 0:
    for idx, row in variations.iterrows():
        print(f"{row['Course']} - {row['Title']}")
        print(f"  Variations: {row['Title_Variations']}")
        print(f"  Sections: {row['Section']}")
        print()

# Show final summary
print("Courses per course code:")
course_counts = grouped['Course'].value_counts().sort_index()
for course, count in course_counts.items():
    print(f"  {course:15} - {count} unique book(s)")

print()
print(f"Total Alma course entries to create: {len(grouped)}")
print("=" * 70)
