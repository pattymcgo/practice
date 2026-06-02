"""
Merge Semester Files
====================
Combines the two CUNYfirst exports into a single merged file ready for
process_semester_data.py.

Inputs:
  1. CU_SR_CLASS_SCHD_CLEANUP_X2_*.xlsx  -- course sections with instructor/enrollment/dates
  2. CU_SR_TEXTBOOK_DETAILS_*.xlsx       -- required textbooks per section

Output:
  data/merged_course_textbooks_SEMESTER.xlsx

Usage:
    python merge_semester_files.py --schedule SCHEDULE.xlsx --textbooks TEXTBOOKS.xlsx --semester Summer2026
"""

import pandas as pd
import argparse
import sys
from pathlib import Path

# ── column rename maps ────────────────────────────────────────────────────────

# Class schedule columns → merged output columns
SCHED_RENAME = {
    'Class Nbr':            'Class_Number',
    'Descr':                'Course_Description',
    'Name':                 'Instructor_Name',
    'ID':                   'EmplID',
    'Tot Enrl':             'Total_Enrollment',
    'Capacity':             'Capacity',
    'Days':                 'Meeting_Days',
    'Mtg Start':            'Meeting_Start_Time',
    'Mtg End':              'Meeting_End_Time',
    'Facil ID':             'Room',
    'CLASS_MTG Start Date': 'Course_Start_Date',
    'CLASS_MTG End Date':   'Course_End_Date',
}

# Columns we pull from the schedule (after rename)
SCHED_COLS = ['Course', 'Section'] + list(SCHED_RENAME.values())

# Columns we pull from the textbook file
TEXT_COLS = [
    'Institution', 'Term', 'Course', 'Session', 'Section',
    'TextbookType', 'Title', 'ISBN', 'Author', 'Publisher',
    'Edition', 'Published', 'Price', 'Notes', 'TextbookStatus',
]

# Final column order (matches merged_course_textbooks_CLEANED.xlsx)
FINAL_COLS = [
    'Course', 'Section', 'Class_Number', 'Course_Description',
    'Instructor_Name', 'EmplID', 'Total_Enrollment', 'Capacity',
    'Meeting_Days', 'Meeting_Start_Time', 'Meeting_End_Time', 'Room',
    'Course_Start_Date', 'Course_End_Date',
    'TextbookType', 'Title', 'ISBN', 'Author', 'Publisher',
    'Edition', 'Published', 'Price',
    'Institution', 'Term', 'Session', 'Notes', 'TextbookStatus',
]

# ── helpers ───────────────────────────────────────────────────────────────────

def load_cunyfirst_export(path: str, label: str) -> pd.DataFrame:
    """
    CUNYfirst exports have a title row in row 0 and real headers in row 1.
    Skip row 0 by using header=1.
    """
    df = pd.read_excel(path, header=1)
    print(f"  Loaded {label}: {len(df):,} rows, {len(df.columns)} columns")
    return df


def build_course_code(df: pd.DataFrame) -> pd.DataFrame:
    """Create 'Course' column from 'Subject' and 'Catalog' (e.g. 'ACC-360')."""
    df = df.copy()
    df['Course'] = df['Subject'].str.strip() + '-' + df['Catalog'].str.strip()
    return df


# ── main ──────────────────────────────────────────────────────────────────────

def merge_files(schedule_path: str, textbooks_path: str, semester: str) -> str:
    base_dir = Path(__file__).parent.parent / 'data'

    print("=" * 70)
    print("SEMESTER FILE MERGER")
    print("=" * 70)
    print()

    # ── Step 1: load ──────────────────────────────────────────────────────────
    print("Step 1 – Loading files")
    df_sched = load_cunyfirst_export(schedule_path, "class schedule")
    df_text  = load_cunyfirst_export(textbooks_path, "textbook details")
    print()

    # ── Step 2: prepare schedule ──────────────────────────────────────────────
    print("Step 2 – Preparing class schedule")
    df_sched = build_course_code(df_sched)
    df_sched = df_sched.rename(columns=SCHED_RENAME)

    # Keep Active ('A') and Stop-Enrollment ('S') sections; drop truly cancelled ones
    KEEP_STATUSES = {'A', 'S'}
    before = len(df_sched)
    df_sched = df_sched[df_sched['Class Stat'].isin(KEEP_STATUSES)].copy()
    dropped = before - len(df_sched)
    print(f"  Kept A/S sections: {len(df_sched):,} (dropped {dropped:,} cancelled/other)")

    # One row per section for the join (drop duplicates caused by multi-meeting patterns)
    df_sched_dedup = df_sched.drop_duplicates(subset=['Course', 'Section']).copy()
    print(f"  Unique Course+Section rows: {len(df_sched_dedup):,}")
    print()

    # ── Step 3: merge ─────────────────────────────────────────────────────────
    print("Step 3 – Merging textbooks onto schedule")

    # Validate that all textbook Course+Section keys exist in the schedule
    sched_keys = set(zip(df_sched_dedup['Course'], df_sched_dedup['Section']))
    text_keys  = set(zip(df_text['Course'], df_text['Section']))
    missing = text_keys - sched_keys
    if missing:
        print(f"  WARNING: {len(missing)} textbook Course+Section combos not found in schedule:")
        for c, s in sorted(missing):
            print(f"    {c} | {s}")
    else:
        print(f"  All {len(text_keys)} textbook Course+Section combos matched schedule")

    # Left join: keep all textbook rows, pull schedule info in
    merged = df_text.merge(
        df_sched_dedup[SCHED_COLS],
        on=['Course', 'Section'],
        how='left'
    )
    print(f"  Merged rows: {len(merged):,}")
    print()

    # ── Step 4: finalise columns ──────────────────────────────────────────────
    print("Step 4 – Finalising output")
    # Add any missing columns as empty
    for col in FINAL_COLS:
        if col not in merged.columns:
            merged[col] = None
    merged = merged[FINAL_COLS]

    # ── Step 5: save ──────────────────────────────────────────────────────────
    out_path = base_dir / f'merged_course_textbooks_{semester}.xlsx'
    merged.to_excel(out_path, index=False)
    print(f"  Saved: {out_path.name}")
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 70)
    print("MERGE COMPLETE")
    print("=" * 70)
    print(f"  Total rows:       {len(merged):,}")
    print(f"  Unique courses:   {merged['Course'].nunique()}")
    print(f"  Unique sections:  {merged['Section'].nunique()}")
    print(f"  Book entries:     {(merged['TextbookType'] == 'Book').sum():,}")
    print(f"  Non-print:        {(merged['TextbookType'] != 'Book').sum():,}")
    print()
    print("Next step:")
    print(f"  python process_semester_data.py --input data/merged_course_textbooks_{semester}.xlsx --semester {semester}")
    print()

    return str(out_path)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Merge CUNYfirst schedule + textbook exports')
    parser.add_argument('--schedule',  required=True, help='Path to CU_SR_CLASS_SCHD_*.xlsx')
    parser.add_argument('--textbooks', required=True, help='Path to CU_SR_TEXTBOOK_DETAILS_*.xlsx')
    parser.add_argument('--semester',  default='Summer2026', help='Semester label (e.g. Summer2026)')
    args = parser.parse_args()

    try:
        merge_files(args.schedule, args.textbooks, args.semester)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
