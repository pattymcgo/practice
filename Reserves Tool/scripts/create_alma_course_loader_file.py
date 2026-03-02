"""
Create Alma Course Loader File (Tab-Separated Format)
Converts consolidated course data to Alma-ready course loader format
No API required - can be manually uploaded to Alma
"""

import pandas as pd
from datetime import datetime
import argparse
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Default processing department - UPDATE THIS for your institution
DEFAULT_PROCESSING_DEPT = "RESERVES"

# Default institution code
DEFAULT_INSTITUTION = "BMC01"

# ============================================================================
# ALMA COURSE LOADER FIELD MAPPING
# ============================================================================

def create_course_loader_file(input_file, output_file=None, processing_dept=DEFAULT_PROCESSING_DEPT):
    """
    Convert consolidated course data to Alma Course Loader format

    Alma Course Loader Required Fields (tab-separated):
    - Code: Course code
    - Section: Section ID
    - Operation: NEW, CHANGED, DELETED, or ROLLOVER
    - Name: Course title/name
    - Processing Department: Library department
    - Start Date: Course start date
    - End Date: Course end date
    - Number of Participants: Enrollment count
    - Instructor: Instructor name(s)
    - Academic Department: Academic department
    - Year: Academic year
    - Term: Semester/term
    - Weekly Hours: Contact hours per week
    """

    print("=" * 70)
    print("ALMA COURSE LOADER FILE GENERATOR")
    print("=" * 70)
    print()

    # Read input data
    print(f"Reading input file: {input_file}")
    df_raw = pd.read_excel(input_file)
    print(f"  Loaded {len(df_raw)} rows")

    # Group by course (since each row is a course-textbook pair)
    # We only need course info once per course
    print("\nConsolidating course information...")
    df_courses = df_raw.groupby('Course').agg({
        'Section': 'first',
        'Course_Description': 'first',
        'Instructor_Name': 'first',
        'Total_Enrollment': 'first',
        'Course_Start_Date': 'first',
        'Course_End_Date': 'first',
        'Term': 'first',
        'Institution': 'first',
        'Meeting_Days': 'first'
    }).reset_index()

    print(f"  Consolidated to {len(df_courses)} unique courses")

    # Extract department from course code (e.g., "ENG 101" -> "ENG")
    df_courses['Academic_Department'] = df_courses['Course'].str.extract(r'^([A-Z]+)')[0]

    # Extract year from term (e.g., "2026 Spring Term" -> "2026")
    df_courses['Year'] = df_courses['Term'].str.extract(r'(\d{4})')[0]

    # Extract term name (e.g., "2026 Spring Term" -> "Spring")
    df_courses['Term_Name'] = df_courses['Term'].str.extract(r'\d{4}\s+(\w+)')[0]

    # Calculate weekly hours (estimate based on meeting days)
    # This is an approximation - adjust as needed
    def estimate_weekly_hours(meeting_days):
        if pd.isna(meeting_days):
            return 3  # Default assumption
        # Count number of days (MW = 2, MWF = 3, etc.)
        days_count = len(str(meeting_days).replace(' ', ''))
        return min(days_count * 2, 15)  # Assume 2 hours per day, max 15

    df_courses['Weekly_Hours'] = df_courses['Meeting_Days'].apply(estimate_weekly_hours)

    # Format dates for Alma (YYYY-MM-DD)
    df_courses['Start_Date_Formatted'] = pd.to_datetime(df_courses['Course_Start_Date']).dt.strftime('%Y-%m-%d')
    df_courses['End_Date_Formatted'] = pd.to_datetime(df_courses['Course_End_Date']).dt.strftime('%Y-%m-%d')

    # Create Alma Course Loader DataFrame
    # IMPORTANT: Column order matters for some systems!
    alma_loader = pd.DataFrame({
        'Code': df_courses['Course'],
        'Section': df_courses['Section'],
        'Operation': 'NEW',  # All new courses
        'Name': df_courses['Course_Description'],
        'Processing Department': processing_dept,
        'Start Date': df_courses['Start_Date_Formatted'],
        'End Date': df_courses['End_Date_Formatted'],
        'Number of Participants': df_courses['Total_Enrollment'].fillna(0).astype(int),
        'Instructor': df_courses['Instructor_Name'],
        'Academic Department': df_courses['Academic_Department'],
        'Year': df_courses['Year'].fillna('2026').astype(int),
        'Term': df_courses['Term_Name'].fillna('Spring'),
        'Weekly Hours': df_courses['Weekly_Hours'].astype(int),
        'All Instructors': df_courses['Instructor_Name'],  # Duplicate for compatibility
        'Search ID': '',  # Optional field - leave blank
        'Instructor': df_courses['Instructor_Name']  # Some systems want this last
    })

    # Handle NaN values - replace with empty string
    alma_loader = alma_loader.fillna('')

    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(input_file).parent
        output_file = output_dir / f'alma_course_loader_{timestamp}.txt'

    # Save as tab-separated file
    # CRITICAL: Must be tab-separated, not comma-separated!
    print(f"\nSaving Alma Course Loader file: {output_file}")
    alma_loader.to_csv(
        output_file,
        sep='\t',  # TAB separator (required by Alma)
        index=False,  # No row numbers
        encoding='utf-8',  # UTF-8 encoding (required by Alma)
        lineterminator='\r\n'  # CRLF line endings (required by Alma)
    )

    # Print summary
    print("\n" + "=" * 70)
    print("ALMA COURSE LOADER FILE CREATED")
    print("=" * 70)
    print(f"\nFile: {output_file}")
    print(f"Format: Tab-separated (.txt)")
    print(f"Encoding: UTF-8")
    print(f"Line endings: CRLF")
    print(f"\nCourses: {len(alma_loader)}")
    print(f"Operation: NEW (all courses)")
    print(f"Processing Department: {processing_dept}")
    print(f"\nDate range: {alma_loader['Start Date'].min()} to {alma_loader['End Date'].max()}")
    print(f"Total enrollment: {alma_loader['Number of Participants'].sum():,} students")

    # Show sample of first 3 courses
    print("\n" + "-" * 70)
    print("SAMPLE - First 3 Courses:")
    print("-" * 70)
    for idx, row in alma_loader.head(3).iterrows():
        print(f"\n{idx+1}. {row['Code']} - {row['Section']}")
        print(f"   Name: {row['Name']}")
        print(f"   Instructor: {row['Instructor']}")
        print(f"   Enrollment: {row['Number of Participants']}")
        print(f"   Dates: {row['Start Date']} to {row['End Date']}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("\n1. Review the file to ensure data looks correct")
    print("2. Log into Alma")
    print("3. Go to: Admin → Fulfillment → Courses → Actions → Upload")
    print("4. Select the generated .txt file")
    print("5. Click 'Upload' to import courses")
    print("\nAlternatively, place file on FTP server for automatic processing")
    print("=" * 70)

    return alma_loader, output_file

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Create Alma Course Loader file from consolidated course data'
    )
    parser.add_argument(
        '--input',
        default='/Users/patty_home/Desktop/Agentic AI/Reserves Tool/projects/030226_test/test_22_courses_smart_consolidated.xlsx',
        help='Path to consolidated course data Excel file'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Path to output file (defaults to auto-generated timestamp file)'
    )
    parser.add_argument(
        '--processing-dept',
        default=DEFAULT_PROCESSING_DEPT,
        help=f'Processing department name (default: {DEFAULT_PROCESSING_DEPT})'
    )

    args = parser.parse_args()

    try:
        alma_data, output_file = create_course_loader_file(
            input_file=args.input,
            output_file=args.output,
            processing_dept=args.processing_dept
        )

        print(f"\n✅ Success! File ready for Alma upload:")
        print(f"   {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
