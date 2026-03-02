"""
ISBN Data Cleaning Script
-------------------------
Cleans ISBNs in the merged course textbooks file by:
- Removing ISBN prefixes and labels
- Stripping special characters
- Flagging invalid/incomplete ISBNs

Author: Patty (with Claude Code assistance)
Date: 2026-02-23
"""

import pandas as pd
import re
from datetime import datetime

def clean_isbn(isbn):
    """
    Clean an ISBN by removing prefixes and special characters.

    Args:
        isbn: Raw ISBN string

    Returns:
        Tuple of (cleaned_isbn, was_modified, issue_flag)
    """
    if pd.isna(isbn):
        return ('', False, 'MISSING')

    original = str(isbn)
    cleaned = original
    was_modified = False
    issue_flag = None

    # Step 1: Remove common ISBN prefixes
    prefixes = [
        'ISBN-13:', 'ISBN-10:', 'ISBN:',
        'isbn-13:', 'isbn-10:', 'isbn:',
        '13:', '10:'
    ]

    for prefix in prefixes:
        if prefix.lower() in cleaned.lower():
            # Find and remove the prefix (case-insensitive)
            pattern = re.escape(prefix)
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            was_modified = True

    # Step 2: Remove spaces, hyphens, and other special characters
    # Keep only digits and 'X' (valid in ISBN-10)
    original_cleaned = cleaned
    cleaned = re.sub(r'[^0-9X]', '', cleaned, flags=re.IGNORECASE)

    if cleaned != original_cleaned:
        was_modified = True

    # Step 3: Check for issues
    if len(cleaned) == 0:
        issue_flag = 'EMPTY_AFTER_CLEAN'
    elif len(cleaned) < 10:
        issue_flag = 'TOO_SHORT'
    elif len(cleaned) > 13:
        issue_flag = 'TOO_LONG'
    elif len(cleaned) not in [10, 13]:
        issue_flag = 'INVALID_LENGTH'

    return (cleaned, was_modified, issue_flag)

def main():
    print("="*70)
    print("ISBN DATA CLEANING SCRIPT")
    print("="*70)

    # Input and output files
    input_file = '/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks.xlsx'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx'
    problem_file = f'/Users/patty_home/Desktop/Agentic AI/data/isbn_problems_{timestamp}.xlsx'

    # Read the merged file
    print(f"\nReading: {input_file}")
    df = pd.read_excel(input_file)
    print(f"  Total entries: {len(df)}")

    # Clean ISBNs
    print("\nCleaning ISBNs...")
    results = df['ISBN'].apply(clean_isbn)

    # Extract results
    df['ISBN_Original'] = df['ISBN']
    df['ISBN'] = results.apply(lambda x: x[0])
    df['ISBN_Modified'] = results.apply(lambda x: x[1])
    df['ISBN_Issue'] = results.apply(lambda x: x[2])

    # Statistics
    print("\n" + "="*70)
    print("CLEANING RESULTS")
    print("="*70)

    total = len(df)
    modified = df['ISBN_Modified'].sum()

    print(f"\nTotal entries: {total}")
    print(f"ISBNs modified: {modified}")

    # Issue breakdown
    issue_counts = df['ISBN_Issue'].value_counts()
    print("\nIssue breakdown:")
    for issue, count in issue_counts.items():
        if issue:
            print(f"  {issue}: {count}")

    valid_isbns = df[df['ISBN_Issue'].isna()]
    print(f"\n✓ Valid ISBNs after cleaning: {len(valid_isbns)}")

    # Examples of what was cleaned
    print("\n" + "="*70)
    print("SAMPLE CLEANINGS")
    print("="*70)

    modified_samples = df[df['ISBN_Modified'] == True].head(10)
    if len(modified_samples) > 0:
        print("\nExamples of cleaned ISBNs:")
        for idx, row in modified_samples.iterrows():
            print(f"  Before: {row['ISBN_Original']}")
            print(f"  After:  {row['ISBN']}")
            if row['ISBN_Issue']:
                print(f"  Issue:  {row['ISBN_Issue']}")
            print()

    # Save cleaned file
    print("\n" + "="*70)
    print("SAVING FILES")
    print("="*70)

    # Drop the temporary columns before saving main file
    df_clean = df.drop(columns=['ISBN_Original', 'ISBN_Modified', 'ISBN_Issue'])
    df_clean.to_excel(output_file, index=False)
    print(f"\n✓ Cleaned file saved: {output_file}")

    # Save problem ISBNs to separate file
    problem_isbns = df[df['ISBN_Issue'].notna()].copy()
    if len(problem_isbns) > 0:
        # Reorder columns to show issues first
        cols = ['ISBN_Issue', 'ISBN_Original', 'ISBN', 'Course', 'Section',
                'Instructor_Name', 'Title', 'Author', 'Publisher']
        # Only include columns that exist
        cols = [c for c in cols if c in problem_isbns.columns]
        problem_isbns = problem_isbns[cols]

        problem_isbns.to_excel(problem_file, index=False)
        print(f"✓ Problem ISBNs saved: {problem_file}")
        print(f"  ({len(problem_isbns)} entries need review)")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nBefore cleaning:")
    print(f"  - Valid ISBNs: {len(df) - df['ISBN_Original'].isna().sum()}")
    print(f"\nAfter cleaning:")
    print(f"  - Valid ISBNs: {len(valid_isbns)}")
    print(f"  - ISBNs needing review: {len(problem_isbns)}")
    print(f"  - Improvement: +{len(valid_isbns) - (len(df) - df['ISBN_Original'].isna().sum())} ISBNs")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Review problem ISBNs in:")
    print(f"   {problem_file}")
    print("\n2. Use cleaned file for ISBN search:")
    print(f"   {output_file}")
    print("\n3. Update isbn_search_tool.py to use cleaned file")
    print("="*70)

if __name__ == "__main__":
    main()
