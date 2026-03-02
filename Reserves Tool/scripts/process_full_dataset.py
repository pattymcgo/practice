"""
SEMESTER DATA PROCESSING - Reusable Workflow
=============================================
Run this each semester to process new course/textbook data

Usage:
    python process_full_dataset.py
    python process_full_dataset.py --input /path/to/data.xlsx
    python process_full_dataset.py --input data.xlsx --semester "Fall2026"

Features:
- Separates books from non-print items
- Applies smart title normalization (handles variations)
- Consolidates by Course + Normalized Title
- Prepares data for Alma automation
"""

import pandas as pd
import numpy as np
import re
import sys
import os
import argparse
from datetime import datetime

# ============================================================================
# CONFIGURATION & ARGUMENT PARSING
# ============================================================================

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Process semester course/textbook data',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  python process_full_dataset.py
  python process_full_dataset.py --input Spring2026_merged.xlsx
  python process_full_dataset.py --input data.xlsx --semester "Fall2026"
    """
)

default_input = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/merged_course_textbooks_CLEANED.xlsx'
output_dir = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data'

parser.add_argument('--input', default=default_input, help='Input Excel file path')
parser.add_argument('--semester', default=None, help='Semester name (e.g., "Spring2026")')
args = parser.parse_args()

# Setup
input_file = args.input
semester_name = args.semester if args.semester else datetime.now().strftime('%Y%m_semester')
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

print("=" * 80)
print("SEMESTER DATA PROCESSING")
print("=" * 80)
print()
print(f"Input: {input_file}")
print(f"Semester: {semester_name}")
print()

# ============================================================================
# STEP 1: LOAD DATASET
# ============================================================================

if not os.path.exists(input_file):
    print(f"ERROR: Input file not found: {input_file}")
    sys.exit(1)

print(f"Loading: {input_file}")
df = pd.read_excel(input_file)

print(f"Total rows: {len(df):,}")
print(f"Unique courses: {df['Course'].nunique()}")
print()

# ============================================================================
# STEP 2: SEPARATE BY TEXTBOOK TYPE
# ============================================================================

print("=" * 80)
print("STEP 1: Separating by Textbook Type")
print("=" * 80)
print()

# Books (physical textbooks)
df_books = df[df['TextbookType'] == 'Book'].copy()

# Non-print items (everything else)
df_nonprint = df[df['TextbookType'] != 'Book'].copy()

print(f"Books (physical):        {len(df_books)} rows")
print(f"Non-print items:         {len(df_nonprint)} rows")
print()

print("Non-print breakdown:")
print(df_nonprint['TextbookType'].value_counts().to_string())
print()

# Save separated datasets
books_file = f'{output_dir}/{semester_name}_BOOKS_raw.xlsx'
nonprint_file = f'{output_dir}/{semester_name}_NONPRINT_raw.xlsx'

df_books.to_excel(books_file, index=False)
df_nonprint.to_excel(nonprint_file, index=False)

print(f"✓ Saved: {semester_name}_BOOKS_raw.xlsx")
print(f"✓ Saved: {semester_name}_NONPRINT_raw.xlsx")
print()

# ============================================================================
# STEP 3: SMART CONSOLIDATION FUNCTION
# ============================================================================

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
    valid_titles = [t for t in titles if pd.notna(t) and str(t) != 'nan' and str(t).strip() != '']
    if len(valid_titles) > 0:
        consolidated['Title'] = valid_titles[0]
    elif len(titles) > 0:
        consolidated['Title'] = titles[0]
    else:
        consolidated['Title'] = ''

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

# ============================================================================
# STEP 4: CONSOLIDATE BOOKS
# ============================================================================

print("=" * 80)
print("STEP 2: Smart Consolidation - BOOKS")
print("=" * 80)
print()

print(f"Processing {len(df_books)} book rows...")

# Add normalized title column
df_books['Title_Normalized'] = df_books['Title'].apply(normalize_title)

# Group by Course and Normalized Title
print("Consolidating by Course + Normalized Title...")
books_consolidated = df_books.groupby(['Course', 'Title_Normalized']).apply(
    consolidate_group, include_groups=False
).reset_index()

# Remove extra level columns
cols_to_drop = [col for col in books_consolidated.columns if col.startswith('level_')]
if cols_to_drop:
    books_consolidated = books_consolidated.drop(cols_to_drop, axis=1)

print(f"Original rows:     {len(df_books)}")
print(f"Consolidated rows: {len(books_consolidated)}")
print(f"Reduced by:        {len(df_books) - len(books_consolidated)} rows")
print()

# Show examples with title variations
variations = books_consolidated[books_consolidated['Title_Variations'] != '']
if len(variations) > 0:
    print(f"Found {len(variations)} books with title variations consolidated")
    print()
    print("Examples (first 5):")
    for idx, row in variations.head(5).iterrows():
        print(f"  {row['Course']} - {row['Title'][:50]}")
        print(f"    Variations: {row['Title_Variations'][:80]}...")
        print()

# Save consolidated books
books_consolidated_file = f'{output_dir}/{semester_name}_BOOKS_consolidated.xlsx'
books_consolidated.to_excel(books_consolidated_file, index=False)
print(f"✓ Saved: {semester_name}_BOOKS_consolidated.xlsx")
print()

# ============================================================================
# STEP 5: CONSOLIDATE NON-PRINT ITEMS
# ============================================================================

print("=" * 80)
print("STEP 3: Smart Consolidation - NON-PRINT ITEMS")
print("=" * 80)
print()

print(f"Processing {len(df_nonprint)} non-print rows...")

# Add normalized title column
df_nonprint['Title_Normalized'] = df_nonprint['Title'].apply(normalize_title)

# Group by Course and Normalized Title
print("Consolidating by Course + Normalized Title...")
nonprint_consolidated = df_nonprint.groupby(['Course', 'Title_Normalized']).apply(
    consolidate_group, include_groups=False
).reset_index()

# Remove extra level columns
cols_to_drop = [col for col in nonprint_consolidated.columns if col.startswith('level_')]
if cols_to_drop:
    nonprint_consolidated = nonprint_consolidated.drop(cols_to_drop, axis=1)

print(f"Original rows:     {len(df_nonprint)}")
print(f"Consolidated rows: {len(nonprint_consolidated)}")
print(f"Reduced by:        {len(df_nonprint) - len(nonprint_consolidated)} rows")
print()

# Save consolidated non-print
nonprint_consolidated_file = f'{output_dir}/{semester_name}_NONPRINT_consolidated.xlsx'
nonprint_consolidated.to_excel(nonprint_consolidated_file, index=False)
print(f"✓ Saved: {semester_name}_NONPRINT_consolidated.xlsx")
print()

# ============================================================================
# STEP 6: SUMMARY STATISTICS
# ============================================================================

print("=" * 80)
print("SUMMARY - Full Dataset Processing")
print("=" * 80)
print()

print("BOOKS (Physical Textbooks):")
print(f"  Original entries:      {len(df_books)}")
print(f"  Consolidated entries:  {len(books_consolidated)}")
print(f"  Unique courses:        {books_consolidated['Course'].nunique()}")
print(f"  Title variations found: {len(variations)}")
print()

print("NON-PRINT ITEMS (E-Books, E-Resources, etc.):")
print(f"  Original entries:      {len(df_nonprint)}")
print(f"  Consolidated entries:  {len(nonprint_consolidated)}")
print(f"  Unique courses:        {nonprint_consolidated['Course'].nunique()}")
print()

print("TOTAL:")
print(f"  Original total:        {len(df)}")
print(f"  Consolidated total:    {len(books_consolidated) + len(nonprint_consolidated)}")
print(f"  Reduction:             {len(df) - (len(books_consolidated) + len(nonprint_consolidated))} rows")
print()

# Course counts
print("Top 10 courses by number of Alma entries (Books):")
course_counts = books_consolidated['Course'].value_counts().head(10)
for course, count in course_counts.items():
    print(f"  {course:20} - {count} entries")

print()
print("=" * 80)
print("Processing complete! Ready for Alma automation when API permissions are granted.")
print("=" * 80)
