"""
Comprehensive Dataset Analysis & Reporting
Generates detailed reports about the consolidated dataset
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("DATASET ANALYSIS & REPORTING")
print("=" * 80)
print()

# Load consolidated datasets
books_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/full_dataset_BOOKS_consolidated.xlsx'
nonprint_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/full_dataset_NONPRINT_consolidated.xlsx'

print("Loading consolidated datasets...")
df_books = pd.read_excel(books_file)
df_nonprint = pd.read_excel(nonprint_file)

print(f"Books: {len(df_books)} entries")
print(f"Non-print: {len(df_nonprint)} entries")
print()

# ============================================================================
# REPORT 1: Course Summary
# ============================================================================

print("=" * 80)
print("REPORT 1: Course Summary")
print("=" * 80)
print()

# Books breakdown by course
course_books = df_books.groupby('Course').agg({
    'Course': 'first',
    'Title': 'count',
    'Section': 'first',
    'Instructor_Name': 'first',
    'Total_Enrollment': 'first'
}).rename(columns={'Title': 'Num_Books'})

course_books = course_books.sort_values('Num_Books', ascending=False)

print("Top 20 courses by number of books:")
print("-" * 80)
for idx, (course, row) in enumerate(course_books.head(20).iterrows(), 1):
    sections = str(row['Section'])[:40]
    print(f"{idx:2}. {course:20} - {row['Num_Books']:2} books | Sections: {sections}...")

print()

# ============================================================================
# REPORT 2: Instructor Summary
# ============================================================================

print("=" * 80)
print("REPORT 2: Instructor Analysis")
print("=" * 80)
print()

# Extract individual instructors
all_instructors = []
for instructors_str in df_books['Instructor_Name'].dropna():
    if str(instructors_str) != 'nan':
        # Split by " / " for combined instructors
        instr_list = str(instructors_str).split(' / ')
        all_instructors.extend(instr_list)

instructor_counts = pd.Series(all_instructors).value_counts()

print(f"Total unique instructors: {len(instructor_counts)}")
print()
print("Top 15 instructors by number of course entries:")
print("-" * 80)
for idx, (instructor, count) in enumerate(instructor_counts.head(15).items(), 1):
    print(f"{idx:2}. {instructor:40} - {count} course entries")

print()

# ============================================================================
# REPORT 3: Consolidation Impact
# ============================================================================

print("=" * 80)
print("REPORT 3: Consolidation Impact Analysis")
print("=" * 80)
print()

# Books with title variations
variations = df_books[df_books['Title_Variations'] != '']
print(f"Books with title variations: {len(variations)}")
print()

if len(variations) > 0:
    print("Examples of consolidated title variations:")
    print("-" * 80)
    for idx, row in variations.head(10).iterrows():
        print(f"\n{row['Course']} - {row['Title'][:60]}")
        print(f"  Sections: {row['Section'][:60]}...")
        variations_list = str(row['Title_Variations']).split(' | ')
        print(f"  {len(variations_list)} variations consolidated:")
        for var in variations_list[:3]:
            print(f"    - {var[:70]}")
        if len(variations_list) > 3:
            print(f"    ... and {len(variations_list) - 3} more")

print()

# Books with multiple editions
multi_edition = df_books[df_books['Num_Editions'] > 1]
print(f"\nBooks with multiple editions: {len(multi_edition)}")
print()

if len(multi_edition) > 0:
    print("Top 10 books by number of editions:")
    print("-" * 80)
    multi_edition_sorted = multi_edition.sort_values('Num_Editions', ascending=False)
    for idx, row in multi_edition_sorted.head(10).iterrows():
        print(f"\n{row['Course']:15} - {row['Title'][:50]}")
        print(f"  Editions: {row['Num_Editions']}")
        print(f"  Sections: {row['Section'][:60]}...")

print()

# ============================================================================
# REPORT 4: Enrollment Statistics
# ============================================================================

print("=" * 80)
print("REPORT 4: Enrollment Statistics")
print("=" * 80)
print()

total_enrollment = df_books['Total_Enrollment'].sum()
avg_enrollment = df_books['Total_Enrollment'].mean()
median_enrollment = df_books['Total_Enrollment'].median()

print(f"Total student enrollment (books): {total_enrollment:,}")
print(f"Average enrollment per course entry: {avg_enrollment:.1f}")
print(f"Median enrollment per course entry: {median_enrollment:.1f}")
print()

# Largest courses
largest = df_books.sort_values('Total_Enrollment', ascending=False).head(10)
print("Top 10 course entries by enrollment:")
print("-" * 80)
for idx, row in largest.iterrows():
    title = str(row['Title'])[:40] if pd.notna(row['Title']) else 'No Title'
    print(f"{row['Course']:15} - {title:40} | {row['Total_Enrollment']:4} students")

print()

# ============================================================================
# REPORT 5: Non-Print Items Analysis
# ============================================================================

print("=" * 80)
print("REPORT 5: Non-Print Items Analysis")
print("=" * 80)
print()

print("Non-print items by type:")
print("-" * 80)
nonprint_types = df_nonprint['TextbookType'].value_counts()
for item_type, count in nonprint_types.items():
    print(f"  {item_type:15} - {count:3} entries")

print()

# Non-print by course
course_nonprint = df_nonprint.groupby('Course').size().sort_values(ascending=False)
print(f"Courses with non-print items: {len(course_nonprint)}")
print()
print("Top 10 courses by number of non-print items:")
print("-" * 80)
for course, count in course_nonprint.head(10).items():
    print(f"  {course:20} - {count} non-print items")

print()

# ============================================================================
# REPORT 6: Data Quality Check
# ============================================================================

print("=" * 80)
print("REPORT 6: Data Quality Check")
print("=" * 80)
print()

# Missing data analysis
print("Books - Missing Data:")
print("-" * 80)
missing_title = df_books['Title'].isna().sum()
missing_instructor = (df_books['Instructor_Name'].isna() | (df_books['Instructor_Name'] == 'nan')).sum()
missing_isbn = df_books['ISBN'].isna().sum()
missing_sections = df_books['Section'].isna().sum()

print(f"  Missing titles: {missing_title}")
print(f"  Missing instructors: {missing_instructor}")
print(f"  Missing ISBNs: {missing_isbn}")
print(f"  Missing sections: {missing_sections}")
print()

# Courses with issues
print("Potential data quality issues:")
print("-" * 80)
issues = []

# Entries with no instructor
no_instructor = df_books[(df_books['Instructor_Name'].isna()) | (df_books['Instructor_Name'] == 'nan')]
if len(no_instructor) > 0:
    print(f"  • {len(no_instructor)} entries with no instructor")
    issues.append(('No Instructor', no_instructor))

# Entries with no enrollment
no_enrollment = df_books[df_books['Total_Enrollment'] == 0]
if len(no_enrollment) > 0:
    print(f"  • {len(no_enrollment)} entries with zero enrollment")
    issues.append(('Zero Enrollment', no_enrollment))

# Entries with no ISBN
no_isbn = df_books[df_books['ISBN'].isna()]
if len(no_isbn) > 0:
    print(f"  • {len(no_isbn)} entries with no ISBN")
    issues.append(('No ISBN', no_isbn))

print()

# ============================================================================
# SAVE SUMMARY REPORTS
# ============================================================================

print("=" * 80)
print("Saving Summary Reports")
print("=" * 80)
print()

# Create reports directory if it doesn't exist
import os
reports_dir = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports'
os.makedirs(reports_dir, exist_ok=True)

# Save course summary
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

course_summary_file = f'{reports_dir}/course_summary_{timestamp}.xlsx'
with pd.ExcelWriter(course_summary_file) as writer:
    course_books.to_excel(writer, sheet_name='Books by Course')

    if len(course_nonprint) > 0:
        course_nonprint_df = course_nonprint.reset_index()
        course_nonprint_df.columns = ['Course', 'Num_NonPrint_Items']
        course_nonprint_df.to_excel(writer, sheet_name='NonPrint by Course', index=False)

    instructor_counts.reset_index().to_excel(writer, sheet_name='Instructor Counts', index=False)

    if len(variations) > 0:
        variations[['Course', 'Title', 'Title_Variations', 'Section']].to_excel(
            writer, sheet_name='Title Variations', index=False
        )

    if len(multi_edition) > 0:
        multi_edition[['Course', 'Title', 'Num_Editions', 'ISBN_All_Editions', 'Section']].to_excel(
            writer, sheet_name='Multiple Editions', index=False
        )

print(f"✓ Saved: course_summary_{timestamp}.xlsx")

# Save data quality report
if len(issues) > 0:
    quality_report_file = f'{reports_dir}/data_quality_issues_{timestamp}.xlsx'
    with pd.ExcelWriter(quality_report_file) as writer:
        for issue_name, issue_df in issues:
            sheet_name = issue_name.replace(' ', '_')
            issue_df[['Course', 'Title', 'Section', 'Instructor_Name', 'Total_Enrollment']].to_excel(
                writer, sheet_name=sheet_name, index=False
            )
    print(f"✓ Saved: data_quality_issues_{timestamp}.xlsx")

print()
print("=" * 80)
print("Analysis complete! All reports generated.")
print("=" * 80)
