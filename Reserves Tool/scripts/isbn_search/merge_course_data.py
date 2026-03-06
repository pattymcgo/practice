"""
Merge Course Information with Textbook List
-------------------------------------------
This script combines course details (instructor, enrollment, etc.) with
the textbook list using course code and section as the matching key.

Author: Patty (with Claude Code assistance)
Date: 2026-02-23
"""

import pandas as pd
from datetime import datetime

def merge_course_data():
    """
    Merge course information with textbook list.
    """
    print("="*70)
    print("MERGING COURSE DATA WITH TEXTBOOK LIST")
    print("="*70)

    # File paths
    textbook_file = '/Users/patty_home/Desktop/Agentic AI/data/textbooklist_spring2026_01262026.xlsx'
    course_file = '/Users/patty_home/Desktop/Agentic AI/data/courseinfo_spring2026_01262026 (1).xlsx'
    output_file = '/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks.xlsx'

    # Read textbook list (header in row 2)
    print("\nReading textbook list...")
    textbooks = pd.read_excel(textbook_file, header=1)
    print(f"  Loaded {len(textbooks)} textbook entries")

    # Read course info (header in row 2)
    print("\nReading course information...")
    courses = pd.read_excel(course_file, header=1)
    print(f"  Loaded {len(courses)} course sections")

    # Create matching keys
    print("\nCreating matching keys...")

    # Clean up course info - remove extra spaces from Catalog
    courses['Catalog'] = courses['Catalog'].astype(str).str.strip()
    courses['Subject'] = courses['Subject'].astype(str).str.strip()
    courses['Section'] = courses['Section'].astype(str).str.strip()

    # Clean textbooks
    textbooks['Section'] = textbooks['Section'].astype(str).str.strip()

    # For textbooks: Course-Section (e.g., "ACC-122-0701")
    textbooks['Match_Key_Full'] = textbooks['Course'] + '-' + textbooks['Section']
    textbooks['Match_Key_Course'] = textbooks['Course']  # Just course for fallback

    # For courses: Subject-Catalog-Section (e.g., "ACC-122-1206")
    courses['Match_Key_Full'] = courses['Subject'] + '-' + courses['Catalog'] + '-' + courses['Section']
    courses['Match_Key_Course'] = courses['Subject'] + '-' + courses['Catalog']  # Just course for fallback

    # Select relevant course info columns to merge
    course_columns = [
        'Match_Key_Full',
        'Match_Key_Course',
        'Section',
        'Class Nbr',       # Class number (unique course section ID)
        'Descr',           # Course description
        'ID',              # Instructor/Employee ID
        'Name',            # Instructor name
        'Tot Enrl',        # Total enrollment
        'Cap Enrl',        # Capacity enrollment
        'Mtg Start',       # Meeting start time
        'Mtg End',         # Meeting end time
        'Days',            # Meeting days
        'Facil ID',        # Room/facility
        'CLASS_MTG Start Date',  # Class start date
        'CLASS_MTG End Date'     # Class end date
    ]

    # Keep only the columns we want from courses
    courses_subset = courses[course_columns].copy()

    # Rename columns to be more descriptive
    courses_subset = courses_subset.rename(columns={
        'Section': 'CourseInfo_Section',
        'Class Nbr': 'Class_Number',
        'Descr': 'Course_Description',
        'ID': 'EmplID',
        'Name': 'Instructor_Name',
        'Tot Enrl': 'Total_Enrollment',
        'Cap Enrl': 'Capacity',
        'Mtg Start': 'Meeting_Start_Time',
        'Mtg End': 'Meeting_End_Time',
        'Days': 'Meeting_Days',
        'Facil ID': 'Room',
        'CLASS_MTG Start Date': 'Course_Start_Date',
        'CLASS_MTG End Date': 'Course_End_Date'
    })

    # Try merging on full key first (Course + Section)
    print("\nAttempting merge on Course + Section...")
    merged_full = textbooks.merge(
        courses_subset,
        left_on='Match_Key_Full',
        right_on='Match_Key_Full',
        how='left',
        suffixes=('', '_full')
    )

    matched_full = merged_full['Instructor_Name'].notna().sum()
    print(f"  ✓ Matched by Course+Section: {matched_full}")

    # For unmatched entries, try matching on just course code
    # This gives us ANY section of the same course
    unmatched_mask = merged_full['Instructor_Name'].isna()

    if unmatched_mask.sum() > 0:
        print(f"\nAttempting merge on Course only for {unmatched_mask.sum()} unmatched entries...")

        # For unmatched rows, try course-only match
        unmatched_df = merged_full[unmatched_mask].copy()

        # Drop the NaN columns from failed full match
        cols_to_drop = [col for col in unmatched_df.columns if col in courses_subset.columns and col != 'Match_Key_Course']
        unmatched_df = unmatched_df.drop(columns=cols_to_drop, errors='ignore')

        # Get first matching section for each course (arbitrary but gives some info)
        courses_first = courses_subset.drop_duplicates(subset=['Match_Key_Course'], keep='first')

        unmatched_df = unmatched_df.merge(
            courses_first,
            left_on='Match_Key_Course',
            right_on='Match_Key_Course',
            how='left',
            suffixes=('', '_course')
        )

        # Combine matched and unmatched
        matched_df = merged_full[~unmatched_mask]
        merged = pd.concat([matched_df, unmatched_df], ignore_index=True)

        matched_course = unmatched_df['Instructor_Name'].notna().sum()
        print(f"  ✓ Matched by Course only: {matched_course}")
    else:
        merged = merged_full

    print(f"\n  Total merged dataset: {len(merged)} rows")

    # Check how many matched
    matched = merged['Instructor_Name'].notna().sum()
    unmatched = merged['Instructor_Name'].isna().sum()

    print(f"\n  ✓ Total matched with course info: {matched} ({matched/len(merged)*100:.1f}%)")
    print(f"  ✗ No course info found: {unmatched} ({unmatched/len(merged)*100:.1f}%)")

    # Replace hyphens with spaces in Course column
    if 'Course' in merged.columns:
        merged['Course'] = merged['Course'].str.replace('-', ' ')

    # Reorder columns for better readability
    # Put course info first, then textbook info
    column_order = [
        'Course', 'Section', 'Class_Number',
        'Course_Description', 'Instructor_Name', 'EmplID',
        'Total_Enrollment', 'Capacity',
        'Meeting_Days', 'Meeting_Start_Time', 'Meeting_End_Time',
        'Room', 'Course_Start_Date', 'Course_End_Date',
        'TextbookType', 'Title', 'ISBN', 'Author', 'Publisher',
        'Edition', 'Published', 'Price',
        'Institution', 'Term', 'Session', 'Notes', 'TextbookStatus'
    ]

    # Only select columns that exist in the merged dataframe
    available_columns = [col for col in column_order if col in merged.columns]
    merged = merged[available_columns]

    # -------------------------------------------------------------------------
    # Title-based filters
    # -------------------------------------------------------------------------

    # Titles the library does not purchase - exclude entirely
    EXCLUDE_TITLE_TERMS = [
        'lab manual', 'lab. manual', 'laboratory manual', 'laboratory',
        'with connect', 'access with connect', 'connect online access',
        'conect core', 'w/connect', '+online access', '+ online access',
        'with quickbooks',
    ]
    # Publishers the library does not purchase from - exclude entirely
    EXCLUDE_PUBLISHER_TERMS = [
        'openstax', 'open stax', 'opentextbook',
    ]
    # OER/OpenStax titles - reclassify from Book to non-print
    OER_TITLE_TERMS = ['oer', 'openstax', 'open stax']

    title_lower = merged['Title'].str.lower().fillna('')

    exclude_title_mask = title_lower.apply(
        lambda t: any(term in t for term in EXCLUDE_TITLE_TERMS)
    )
    print(f"\nExcluded {exclude_title_mask.sum()} rows with non-purchasable title terms")
    merged = merged[~exclude_title_mask].copy()

    publisher_lower = merged['Publisher'].str.lower().fillna('')
    exclude_pub_mask = publisher_lower.apply(
        lambda p: any(term in p for term in EXCLUDE_PUBLISHER_TERMS)
    )
    print(f"Excluded {exclude_pub_mask.sum()} rows from OER publishers (OpenStax, OpenTextbook, etc.)")
    merged = merged[~exclude_pub_mask].copy()

    title_lower = merged['Title'].str.lower().fillna('')
    oer_mask = (merged['TextbookType'] == 'Book') & title_lower.apply(
        lambda t: any(term in t for term in OER_TITLE_TERMS)
    )
    print(f"Reclassified {oer_mask.sum()} OER/OpenStax titles from Book to non-print")
    merged.loc[oer_mask, 'TextbookType'] = 'OER / Open Educational Resource'

    # Split by TextbookType: Books vs everything else
    books = merged[merged['TextbookType'] == 'Book']
    nonprint = merged[merged['TextbookType'] != 'Book']

    # Derive output paths for split files
    books_file = output_file.replace('.xlsx', '_BOOKS.xlsx')
    nonprint_file = output_file.replace('.xlsx', '_NONPRINT.xlsx')

    # Save all three files
    print(f"\nSaving merged data to: {output_file}")
    merged.to_excel(output_file, index=False)

    print(f"Saving books-only data to: {books_file}")
    books.to_excel(books_file, index=False)

    print(f"Saving non-print data to: {nonprint_file}")
    nonprint.to_excel(nonprint_file, index=False)

    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total textbook entries: {len(merged)}")
    print(f"  - Books (TextbookType = 'Book'): {len(books)}")
    print(f"  - Non-print (all other types):   {len(nonprint)}")
    if 'TextbookType' in merged.columns:
        print(f"\nNon-print breakdown:")
        for ttype, count in nonprint['TextbookType'].value_counts().items():
            print(f"  {ttype}: {count}")
    print(f"\nUnique courses: {merged['Course'].nunique()}")
    print(f"Unique sections (textbook): {merged['Section'].nunique()}")
    print(f"Unique ISBNs: {merged['ISBN'].nunique()}")
    if 'Instructor_Name' in merged.columns:
        print(f"Unique instructors: {merged['Instructor_Name'].dropna().nunique()}")

    print(f"\nFiles saved:")
    print(f"  All items:  {output_file}")
    print(f"  Books only: {books_file}")
    print(f"  Non-print:  {nonprint_file}")
    print("="*70)

    # Show sample of merged data
    print("\nSample of merged data:")
    print(merged[['Course', 'Section', 'Instructor_Name', 'ISBN', 'Title']].head(5).to_string())

    return output_file

if __name__ == "__main__":
    merge_course_data()
