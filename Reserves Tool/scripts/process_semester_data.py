"""
SEMESTER DATA PROCESSING - Master Script
=========================================
Run this script each semester to process new course/textbook data

What it does:
1. Loads your merged course/textbook data
2. Normalizes book titles (handles variations)
3. Separates books from non-print items
4. Consolidates by Course + Normalized Title
5. Generates summary reports
6. Prepares data for Alma automation

Usage:
    python process_semester_data.py

Or specify input file:
    python process_semester_data.py --input /path/to/your/data.xlsx
"""

import pandas as pd
import numpy as np
import re
import sys
import os
import argparse
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Default input file (change this for each semester or use --input)
DEFAULT_INPUT = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/merged_course_textbooks_CLEANED.xlsx'

# Output directory
OUTPUT_DIR = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data'
REPORTS_DIR = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports'

# ============================================================================
# TITLE NORMALIZATION
# ============================================================================

def normalize_title(title):
    """
    Normalize a book title for matching
    - Removes articles (the, a, an) from anywhere in title
    - Removes special characters and punctuation
    - Converts to lowercase
    - Removes extra spaces
    """
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

# ============================================================================
# CONSOLIDATION FUNCTION
# ============================================================================

def consolidate_group(group):
    """
    Consolidate all rows for the same course+normalized title
    Combines sections, instructors, ISBNs, and tracks title variations
    """
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
# MAIN PROCESSING
# ============================================================================

def process_semester_data(input_file, semester_name=None):
    """
    Main processing function for semester data

    Args:
        input_file: Path to merged course/textbook Excel file
        semester_name: Optional semester identifier (e.g., "Spring2026")
    """

    if not os.path.exists(input_file):
        print(f"ERROR: Input file not found: {input_file}")
        return False

    # Generate timestamp and semester identifier
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if not semester_name:
        semester_name = datetime.now().strftime('%Y%m_semester')

    print("=" * 80)
    print("SEMESTER DATA PROCESSING")
    print("=" * 80)
    print()
    print(f"Input file: {input_file}")
    print(f"Semester: {semester_name}")
    print(f"Timestamp: {timestamp}")
    print()

    # ========================================================================
    # STEP 1: LOAD DATA
    # ========================================================================

    print("=" * 80)
    print("STEP 1: Loading Data")
    print("=" * 80)
    print()

    df = pd.read_excel(input_file)
    print(f"Total rows: {len(df):,}")
    print(f"Unique courses: {df['Course'].nunique()}")
    print()

    # Check for required columns
    required_cols = ['Course', 'Title', 'TextbookType', 'Section', 'Instructor_Name']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"ERROR: Missing required columns: {missing_cols}")
        return False

    # ========================================================================
    # STEP 2: SEPARATE BY TYPE
    # ========================================================================

    print("=" * 80)
    print("STEP 2: Separating Books from Non-Print Items")
    print("=" * 80)
    print()

    df_books = df[df['TextbookType'] == 'Book'].copy()
    df_nonprint = df[df['TextbookType'] != 'Book'].copy()

    print(f"Books (physical):        {len(df_books):,} rows")
    print(f"Non-print items:         {len(df_nonprint):,} rows")
    print()

    if len(df_nonprint) > 0:
        print("Non-print breakdown:")
        for item_type, count in df_nonprint['TextbookType'].value_counts().items():
            print(f"  {item_type:15} - {count:,} entries")
        print()

    # Save separated datasets
    books_file = f'{OUTPUT_DIR}/{semester_name}_BOOKS_raw.xlsx'
    nonprint_file = f'{OUTPUT_DIR}/{semester_name}_NONPRINT_raw.xlsx'

    df_books.to_excel(books_file, index=False)
    df_nonprint.to_excel(nonprint_file, index=False)

    print(f"✓ Saved: {semester_name}_BOOKS_raw.xlsx")
    print(f"✓ Saved: {semester_name}_NONPRINT_raw.xlsx")
    print()

    # ========================================================================
    # STEP 3: CONSOLIDATE BOOKS
    # ========================================================================

    print("=" * 80)
    print("STEP 3: Smart Consolidation - BOOKS")
    print("=" * 80)
    print()

    print("Normalizing titles...")
    df_books['Title_Normalized'] = df_books['Title'].apply(normalize_title)

    print("Consolidating by Course + Normalized Title...")
    books_consolidated = df_books.groupby(['Course', 'Title_Normalized']).apply(
        consolidate_group, include_groups=False
    ).reset_index()

    # Remove extra level columns
    cols_to_drop = [col for col in books_consolidated.columns if col.startswith('level_')]
    if cols_to_drop:
        books_consolidated = books_consolidated.drop(cols_to_drop, axis=1)

    print(f"Original rows:     {len(df_books):,}")
    print(f"Consolidated rows: {len(books_consolidated):,}")
    print(f"Reduced by:        {len(df_books) - len(books_consolidated):,} rows ({((len(df_books) - len(books_consolidated)) / len(df_books) * 100):.1f}%)")
    print()

    # Show title variations
    variations = books_consolidated[
        (books_consolidated['Title_Variations'] != '') &
        (books_consolidated['Title_Variations'].notna())
    ]

    if len(variations) > 0:
        print(f"Found {len(variations)} books with title variations consolidated")
        print("\nExamples (first 5):")
        for idx, row in variations.head(5).iterrows():
            print(f"  {row['Course']} - {row['Title'][:50]}")
            var_list = str(row['Title_Variations']).split(' | ')
            if len(var_list) > 1:
                print(f"    Consolidated {len(var_list)} variations")
        print()

    # Save consolidated books
    books_consolidated_file = f'{OUTPUT_DIR}/{semester_name}_BOOKS_consolidated.xlsx'
    books_consolidated.to_excel(books_consolidated_file, index=False)
    print(f"✓ Saved: {semester_name}_BOOKS_consolidated.xlsx")
    print()

    # ========================================================================
    # STEP 4: CONSOLIDATE NON-PRINT
    # ========================================================================

    print("=" * 80)
    print("STEP 4: Smart Consolidation - NON-PRINT ITEMS")
    print("=" * 80)
    print()

    if len(df_nonprint) > 0:
        print("Normalizing titles...")
        df_nonprint['Title_Normalized'] = df_nonprint['Title'].apply(normalize_title)

        print("Consolidating by Course + Normalized Title...")
        nonprint_consolidated = df_nonprint.groupby(['Course', 'Title_Normalized']).apply(
            consolidate_group, include_groups=False
        ).reset_index()

        # Remove extra level columns
        cols_to_drop = [col for col in nonprint_consolidated.columns if col.startswith('level_')]
        if cols_to_drop:
            nonprint_consolidated = nonprint_consolidated.drop(cols_to_drop, axis=1)

        print(f"Original rows:     {len(df_nonprint):,}")
        print(f"Consolidated rows: {len(nonprint_consolidated):,}")
        print(f"Reduced by:        {len(df_nonprint) - len(nonprint_consolidated):,} rows")
        print()

        # Save consolidated non-print
        nonprint_consolidated_file = f'{OUTPUT_DIR}/{semester_name}_NONPRINT_consolidated.xlsx'
        nonprint_consolidated.to_excel(nonprint_consolidated_file, index=False)
        print(f"✓ Saved: {semester_name}_NONPRINT_consolidated.xlsx")
    else:
        nonprint_consolidated = pd.DataFrame()
        print("No non-print items to consolidate")

    print()

    # ========================================================================
    # STEP 5: GENERATE SUMMARY
    # ========================================================================

    print("=" * 80)
    print("STEP 5: Summary Statistics")
    print("=" * 80)
    print()

    print("BOOKS (Physical Textbooks):")
    print(f"  Original entries:       {len(df_books):,}")
    print(f"  Consolidated entries:   {len(books_consolidated):,}")
    print(f"  Unique courses:         {books_consolidated['Course'].nunique()}")
    print(f"  Total enrollment:       {books_consolidated['Total_Enrollment'].sum():,} students")
    print(f"  Title variations found: {len(variations)}")

    multi_edition = books_consolidated[books_consolidated['Num_Editions'] > 1]
    if len(multi_edition) > 0:
        print(f"  Multiple editions:      {len(multi_edition)} books")
    print()

    if len(df_nonprint) > 0:
        print("NON-PRINT ITEMS:")
        print(f"  Original entries:       {len(df_nonprint):,}")
        print(f"  Consolidated entries:   {len(nonprint_consolidated):,}")
        print(f"  Unique courses:         {nonprint_consolidated['Course'].nunique()}")
        print()

    print("TOTAL:")
    print(f"  Original total:         {len(df):,}")
    print(f"  Consolidated total:     {len(books_consolidated) + len(nonprint_consolidated):,}")
    print(f"  Reduction:              {len(df) - (len(books_consolidated) + len(nonprint_consolidated)):,} rows")
    print()

    # Top courses
    print("Top 10 courses by number of entries (Books):")
    course_counts = books_consolidated['Course'].value_counts().head(10)
    for course, count in course_counts.items():
        print(f"  {course:20} - {count} entries")
    print()

    # ========================================================================
    # STEP 6: SAVE SUMMARY REPORT
    # ========================================================================

    print("=" * 80)
    print("STEP 6: Saving Summary Report")
    print("=" * 80)
    print()

    # Create reports directory if needed
    os.makedirs(REPORTS_DIR, exist_ok=True)

    summary_file = f'{REPORTS_DIR}/{semester_name}_processing_summary_{timestamp}.xlsx'

    with pd.ExcelWriter(summary_file) as writer:
        # Course summary
        course_summary = books_consolidated.groupby('Course').agg({
            'Title': 'count',
            'Total_Enrollment': 'sum'
        }).rename(columns={'Title': 'Num_Books', 'Total_Enrollment': 'Total_Students'})
        course_summary = course_summary.sort_values('Num_Books', ascending=False)
        course_summary.to_excel(writer, sheet_name='Course Summary')

        # Title variations
        if len(variations) > 0:
            variations[['Course', 'Title', 'Title_Variations', 'Section', 'Num_Editions']].to_excel(
                writer, sheet_name='Title Variations', index=False
            )

        # Multiple editions
        if len(multi_edition) > 0:
            multi_edition[['Course', 'Title', 'Num_Editions', 'ISBN_All_Editions']].to_excel(
                writer, sheet_name='Multiple Editions', index=False
            )

        # Data quality checks
        quality_issues = []

        no_instructor = books_consolidated[
            (books_consolidated['Instructor_Name'].isna()) |
            (books_consolidated['Instructor_Name'] == 'nan')
        ]
        if len(no_instructor) > 0:
            quality_issues.append(('No Instructor', no_instructor))

        no_isbn = books_consolidated[books_consolidated['ISBN'].isna()]
        if len(no_isbn) > 0:
            quality_issues.append(('No ISBN', no_isbn))

        zero_enrollment = books_consolidated[books_consolidated['Total_Enrollment'] == 0]
        if len(zero_enrollment) > 0:
            quality_issues.append(('Zero Enrollment', zero_enrollment))

        if quality_issues:
            for issue_name, issue_df in quality_issues:
                sheet_name = issue_name.replace(' ', '_')
                issue_df[['Course', 'Title', 'Section', 'Instructor_Name']].to_excel(
                    writer, sheet_name=sheet_name, index=False
                )

    print(f"✓ Saved: {semester_name}_processing_summary_{timestamp}.xlsx")
    print()

    # ========================================================================
    # COMPLETION
    # ========================================================================

    print("=" * 80)
    print("PROCESSING COMPLETE!")
    print("=" * 80)
    print()
    print("📁 Output Files:")
    print(f"   • {semester_name}_BOOKS_consolidated.xlsx - USE THIS for Alma automation")
    print(f"   • {semester_name}_NONPRINT_consolidated.xlsx - Non-print items")
    print(f"   • {semester_name}_processing_summary_{timestamp}.xlsx - Reports")
    print()
    print("📊 Ready for Alma Automation:")
    print(f"   • {len(books_consolidated):,} book course entries")
    print(f"   • {len(nonprint_consolidated):,} non-print entries")
    print(f"   • {books_consolidated['Course'].nunique()} unique courses")
    print()
    print("Next steps:")
    print("1. Review the consolidated files")
    print("2. Check the processing summary for data quality issues")
    print("3. Run automation when ready:")
    print("   python run_automation_for_semester.py")
    print()
    print("=" * 80)

    return True

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Process semester course/textbook data for Alma automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_semester_data.py
  python process_semester_data.py --input /path/to/data.xlsx
  python process_semester_data.py --input data.xlsx --semester "Fall2026"
        """
    )

    parser.add_argument(
        '--input',
        default=DEFAULT_INPUT,
        help='Path to merged course/textbook Excel file'
    )

    parser.add_argument(
        '--semester',
        default=None,
        help='Semester identifier (e.g., "Spring2026", "Fall2026")'
    )

    args = parser.parse_args()

    # Process the data
    success = process_semester_data(args.input, args.semester)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
