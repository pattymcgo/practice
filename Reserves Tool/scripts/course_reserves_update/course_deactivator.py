"""
Course Deactivator
==================
Lists active courses for a given semester in Alma and optionally deactivates them.
Designed to be reused each semester -- just change the --semester argument.

This script uses the Alma Courses API (not Primo -- course status lives in Alma).

HOW TO RUN:

  Check active Spring 2026 courses (safe, read-only):
    python course_deactivator.py

  Check a different semester:
    python course_deactivator.py --semester "2026 Fall"

  Preview which courses WOULD be deactivated (no changes made):
    python course_deactivator.py --deactivate --dry-run

  Actually deactivate courses whose end_date has already passed:
    python course_deactivator.py --deactivate

  Find ALL active courses across ALL semesters with an expired end_date:
    python course_deactivator.py --all-expired
    python course_deactivator.py --all-expired --deactivate --dry-run
    python course_deactivator.py --all-expired --deactivate

  Show all semester courses including already-inactive ones:
    python course_deactivator.py --all

  List courses with NO terms from Fall 2024 or later (stale courses to review/remove):
    python course_deactivator.py --stale

DEACTIVATION SAFETY:
  --deactivate only acts on courses whose end_date is already in the past.
  Courses that are still running (end_date today or future) are skipped
  automatically, even if they match the semester filter.

OUTPUT:
  Always prints a summary table to the terminal.
  Saves a report to: reports/course_deactivator_YYYYMMDD_HHMMSS.xlsx
  The End_Date_Status column shows: Expired | Still Active | Unknown
"""

import argparse
import json
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_PATH = Path(__file__).parent.parent / "isbn_search" / "config.json"
OUTPUT_DIR  = Path(__file__).parent.parent.parent / "reports"
OUTPUT_DIR.mkdir(exist_ok=True)

ALMA_BASE = "https://api-na.hosted.exlibrisgroup.com"

DEFAULT_SEMESTER = "2026 Spring"

# Alternative labels Alma might use for the same semester
SEMESTER_ALIASES = {
    "2026 spring": {"2026 spring", "spring 2026", "sp26", "s26", "spring26", "spring 26"},
    "2026 fall":   {"2026 fall",   "fall 2026",   "fa26", "f26", "fall26"},
    "2027 spring": {"2027 spring", "spring 2027", "sp27", "s27", "spring27"},
    "2027 fall":   {"2027 fall",   "fall 2027",   "fa27", "f27", "fall27"},
}

# Date windows per semester -- used as fallback if term field is empty
SEMESTER_DATE_WINDOWS = {
    "2026 spring": (datetime(2026, 1, 1),  datetime(2026, 6, 30)),
    "2026 fall":   (datetime(2026, 8, 1),  datetime(2026, 12, 31)),
    "2027 spring": (datetime(2027, 1, 1),  datetime(2027, 6, 30)),
    "2027 fall":   (datetime(2027, 8, 1),  datetime(2027, 12, 31)),
}


def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: config.json not found at {CONFIG_PATH}")
        sys.exit(1)

# ============================================================================
# ALMA API HELPERS
# ============================================================================

def make_headers(api_key):
    return {
        "Authorization": f"apikey {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def fetch_all_courses(api_key):
    """
    Fetch every course from Alma (all statuses, all semesters).
    Paginates automatically. Returns a list of course dicts.
    """
    url    = f"{ALMA_BASE}/almaws/v1/courses"
    offset = 0
    limit  = 100
    total  = None
    all_courses = []

    print("Fetching all courses from Alma...")

    while True:
        resp = requests.get(
            url,
            headers=make_headers(api_key),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )

        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text[:300]}")
            sys.exit(1)

        data = resp.json()

        if total is None:
            total = int(data.get("total_record_count", 0))
            print(f"  Total courses in Alma: {total:,}")

        courses = data.get("course", [])
        if not isinstance(courses, list):
            courses = [courses] if courses else []

        all_courses.extend(courses)
        print(f"  Fetched {len(all_courses):,} / {total:,} ...", end="\r")

        if len(all_courses) >= total or not courses:
            break

        offset += limit
        time.sleep(0.2)

    print(f"\n  Done fetching courses.")
    return all_courses

# ============================================================================
# COURSE CLASSIFICATION HELPERS
# ============================================================================

def get_status(course):
    """Extract status string (ACTIVE / INACTIVE) from a course dict."""
    s = course.get("status", "")
    if isinstance(s, dict):
        return s.get("value", "").upper()
    return str(s).upper()


def get_term_label(course):
    """Return all term labels joined by ' | ' (a course can span multiple terms)."""
    terms = course.get("term", [])
    if isinstance(terms, list) and terms:
        labels = [t.get("desc") or t.get("value") or "" for t in terms]
        return " | ".join(t for t in labels if t)
    if isinstance(terms, str):
        return terms
    return ""


def parse_end_date(course):
    """
    Parse the course end_date into a Python date object.
    Returns a date on success, or None if the field is missing/unparseable.
    """
    raw = course.get("end_date", "")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.rstrip("Z").split("T")[0]).date()
    except ValueError:
        return None


def end_date_status(course):
    """
    Return a human-readable label for the course's end date relative to today:
      'Expired'      -- end_date is in the past  --> safe to deactivate
      'Still Active' -- end_date is today or future --> do NOT deactivate
      'Unknown'      -- no end_date in the record
    """
    end = parse_end_date(course)
    if end is None:
        return "Unknown"
    return "Expired" if end < date.today() else "Still Active"


def is_semester_match(course, semester_key, aliases, date_window):
    """
    Return True if this course belongs to the specified semester.
    Checks the 'term' field first, then falls back to date range.
    """
    terms = course.get("term", [])
    if isinstance(terms, list):
        for t in terms:
            val = (t.get("value") or t.get("desc") or "").lower().strip()
            if any(alias in val for alias in aliases):
                return True
    elif isinstance(terms, str):
        if any(alias in terms.lower() for alias in aliases):
            return True

    # Fallback: check if start_date or end_date falls in the semester window
    if date_window:
        start_win, end_win = date_window
        for field in ("start_date", "end_date"):
            raw = course.get(field, "")
            if not raw:
                continue
            try:
                d = datetime.fromisoformat(raw.rstrip("Z").split("T")[0])
                if start_win <= d <= end_win:
                    return True
            except ValueError:
                pass

    return False


def instructor_name(course):
    instructors = course.get("instructor", [])
    if not isinstance(instructors, list):
        instructors = [instructors] if instructors else []
    names = []
    for i in instructors:
        last  = i.get("last_name",  "")
        first = i.get("first_name", "")
        names.append(f"{last}, {first}".strip(", "))
    return "; ".join(names)


def dept_name(course):
    dept = course.get("academic_department", {})
    if isinstance(dept, dict):
        return dept.get("desc") or dept.get("value") or ""
    return str(dept)


def has_term_fall_2024_or_later(course):
    """
    Return True if the course has ANY term from Fall 2024 onward.
    Courses that return False are considered stale (Spring 2024 or earlier).
    Checks term labels first, then falls back to end_date.
    """
    terms = course.get("term", [])
    term_labels = []
    if isinstance(terms, list):
        for t in terms:
            val = (t.get("value") or t.get("desc") or "").lower().strip()
            term_labels.append(val)
    elif isinstance(terms, str):
        term_labels.append(terms.lower().strip())

    for label in term_labels:
        # Any 2025+ year is recent
        if any(str(yr) in label for yr in range(2025, 2035)):
            return True
        # Fall 2024 specifically (covers: "fall 2024", "2024 fall", "fa24", "f24")
        if "2024" in label and (
            "fall" in label
            or "fa24" in label
            or label.endswith("f24")
        ):
            return True

    # Fallback: Fall 2024 starts around August 2024
    end = parse_end_date(course)
    if end and end >= date(2024, 8, 1):
        return True

    return False

# ============================================================================
# DEACTIVATION
# ============================================================================

def deactivate_course(course, api_key, dry_run=True):
    """
    Set a course's status to INACTIVE via a PUT request.
    If dry_run=True, prints what would happen but makes no API call.
    Returns True on success (or dry-run), False on error.
    """
    course_id   = course.get("id", "")
    course_code = course.get("code", "")
    end         = parse_end_date(course)

    if not course_id:
        print(f"  SKIP {course_code}: no course ID")
        return False

    if dry_run:
        end_str = str(end) if end else "no end date"
        print(f"  [DRY RUN] Would deactivate: {course_code}  (ended: {end_str})")
        return True

    updated           = dict(course)
    updated["status"] = {"value": "INACTIVE"}

    resp = requests.put(
        f"{ALMA_BASE}/almaws/v1/courses/{course_id}",
        headers=make_headers(api_key),
        json=updated,
        timeout=30,
    )

    if resp.status_code in (200, 204):
        print(f"  DEACTIVATED: {course_code}")
        return True
    else:
        print(f"  ERROR {course_code}: {resp.status_code} - {resp.text[:200]}")
        return False

# ============================================================================
# REPORT
# ============================================================================

def save_report(courses, filename_prefix="course_deactivator"):
    """Save course list to Excel with an End_Date_Status column."""
    rows = [{
        "Course_ID":       c.get("id", ""),
        "Code":            c.get("code", ""),
        "Name":            c.get("name", ""),
        "Section":         c.get("section", ""),
        "Status":          get_status(c),
        "Term":            get_term_label(c),
        "Start_Date":      c.get("start_date", ""),
        "End_Date":        c.get("end_date", ""),
        "End_Date_Status": end_date_status(c),  # Expired | Still Active | Unknown
        "Instructor":      instructor_name(c),
        "Enrollment":      c.get("participants_number", ""),
        "Department":      dept_name(c),
    } for c in courses]

    df   = pd.DataFrame(rows)
    path = OUTPUT_DIR / f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(path, index=False)
    print(f"Report saved: {path}")
    return path

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="List and optionally deactivate expired courses in Alma",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python course_deactivator.py                               # check Spring 2026 active courses
  python course_deactivator.py --semester "2026 Fall"        # different semester
  python course_deactivator.py --deactivate --dry-run        # preview (no changes)
  python course_deactivator.py --deactivate                  # deactivate expired courses only

  python course_deactivator.py --all-expired                 # ALL semesters, expired end_date
  python course_deactivator.py --all-expired --deactivate --dry-run
  python course_deactivator.py --all-expired --deactivate
        """,
    )
    parser.add_argument("--semester", default=DEFAULT_SEMESTER,
                        help=f'Semester to check (default: "{DEFAULT_SEMESTER}")')
    parser.add_argument("--deactivate", action="store_true",
                        help="Deactivate courses (only those whose end_date has passed)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview deactivation without making any changes")
    parser.add_argument("--all", action="store_true",
                        help="Include already-inactive courses in the report")
    parser.add_argument("--all-expired", action="store_true",
                        help="Ignore semester filter -- find ALL active courses with a past end_date")
    parser.add_argument("--stale", action="store_true",
                        help="List all courses (any status) with NO terms after Fall 2024")
    args = parser.parse_args()

    config  = load_config()
    api_key = config.get("alma_api_key", "")
    if not api_key:
        print("ERROR: No alma_api_key in config.json")
        sys.exit(1)

    # ---- Fetch all courses from Alma ----
    if args.stale:
        print("=" * 65)
        print("COURSE DEACTIVATOR  --  STALE (no terms Fall 2024 or later)")
        print("=" * 65)
    elif args.all_expired:
        print("=" * 65)
        print("COURSE DEACTIVATOR  --  ALL EXPIRED (any semester)")
        print("=" * 65)
    else:
        print("=" * 65)
        print(f"COURSE DEACTIVATOR  --  {args.semester.upper()}")
        print("=" * 65)

    all_courses = fetch_all_courses(api_key)

    # ---- Filter to the relevant set ----
    if args.stale:
        # Courses with no term label from Spring 2025 onward
        stale_courses = [c for c in all_courses if not has_term_fall_2024_or_later(c)]
        print(f"\n  Courses with no terms from Fall 2024 or later: {len(stale_courses):,}")

        print(f"\n{'CODE':<25} {'SECTION':<10} {'STATUS':<10} {'END DATE':<14} TERM")
        print("-" * 80)
        for c in sorted(stale_courses, key=lambda x: x.get("code", "")):
            end = parse_end_date(c)
            print(
                f"{c.get('code', ''):<25}"
                f"{c.get('section', ''):<10}"
                f"{get_status(c):<10}"
                f"{str(end) if end else 'N/A':<14}"
                f"{get_term_label(c)}"
            )

        print()
        active_stale   = sum(1 for c in stale_courses if get_status(c) == "ACTIVE")
        inactive_stale = sum(1 for c in stale_courses if get_status(c) != "ACTIVE")
        print(f"Active (still on):   {active_stale:,}")
        print(f"Already inactive:    {inactive_stale:,}")

        save_report(stale_courses, "stale_courses_pre_fall2024")
        return

    elif args.all_expired:
        # All active courses whose end_date is in the past, regardless of semester
        candidates = [
            c for c in all_courses
            if get_status(c) == "ACTIVE" and end_date_status(c) == "Expired"
        ]
        print(f"\n  Active courses with expired end_date (any semester): {len(candidates):,}")
        display = candidates

    else:
        semester_key = args.semester.lower().strip()
        aliases      = SEMESTER_ALIASES.get(semester_key, {semester_key})
        date_window  = SEMESTER_DATE_WINDOWS.get(semester_key)

        semester_courses = [
            c for c in all_courses
            if is_semester_match(c, semester_key, aliases, date_window)
        ]

        print(f"\n  {args.semester} courses found: {len(semester_courses):,}")

        if not semester_courses:
            print(
                "\n  No courses matched. The term field in Alma may use a different label."
                "\n  Saving a sample so you can check the format used:"
            )
            save_report(all_courses[:30], "alma_courses_sample")
            print('\n  Re-run with: python course_deactivator.py --semester "exact label"')
            return

        active   = [c for c in semester_courses if get_status(c) == "ACTIVE"]
        inactive = [c for c in semester_courses if get_status(c) != "ACTIVE"]
        display  = semester_courses if args.all else active

        # Further split active into expired vs. still running
        expired_active = [c for c in active if end_date_status(c) == "Expired"]
        still_running  = [c for c in active if end_date_status(c) == "Still Active"]
        unknown_end    = [c for c in active if end_date_status(c) == "Unknown"]

        candidates = expired_active  # only expired ones are safe to deactivate

    # ---- Print summary table ----
    print(f"\n{'CODE':<25} {'SECTION':<10} {'STATUS':<10} {'END DATE':<14} {'END STATUS':<14} TERM")
    print("-" * 95)
    for c in sorted(display, key=lambda x: x.get("code", "")):
        end = parse_end_date(c)
        print(
            f"{c.get('code', ''):<25}"
            f"{c.get('section', ''):<10}"
            f"{get_status(c):<10}"
            f"{str(end) if end else 'N/A':<14}"
            f"{end_date_status(c):<14}"
            f"{get_term_label(c)}"
        )

    print()
    if not args.all_expired:
        print(f"Active - end date expired:    {len(expired_active):,}  (safe to deactivate)")
        print(f"Active - still running:       {len(still_running):,}  (will be skipped)")
        print(f"Active - end date unknown:    {len(unknown_end):,}  (will be skipped)")
        print(f"Already inactive:             {len(inactive):,}")
    else:
        print(f"Active courses with expired end_date: {len(candidates):,}")

    # ---- Save report ----
    prefix = "course_deactivator_all_expired" if args.all_expired \
             else f"course_deactivator_{args.semester.lower().replace(' ', '_')}"
    save_report(display, prefix)

    # ---- Deactivation ----
    if not args.deactivate:
        if candidates:
            print(
                f"\n{len(candidates):,} course(s) have expired and could be deactivated."
                f"\nRun with --deactivate --dry-run to preview, then --deactivate to act."
            )
        else:
            print("\nNo expired courses to deactivate.")
        return

    if not candidates:
        print("\nNo expired courses to deactivate.")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] {len(candidates):,} courses would be deactivated:\n")
        for c in sorted(candidates, key=lambda x: x.get("code", "")):
            deactivate_course(c, api_key, dry_run=True)
        print(f"\nNo changes made. Remove --dry-run to actually deactivate.")
        return

    # Live deactivation -- confirm first
    scope = "ALL semesters" if args.all_expired else args.semester
    print(f"\nAbout to DEACTIVATE {len(candidates):,} expired courses ({scope}).")
    print("Their reading lists will become inaccessible to students.")
    confirm = input("\nType 'yes' to continue, anything else to cancel: ").strip().lower()
    if confirm != "yes":
        print("Cancelled. No changes made.")
        return

    print(f"\nDeactivating {len(candidates):,} courses...")
    success = 0
    failed  = 0
    for c in sorted(candidates, key=lambda x: x.get("code", "")):
        if deactivate_course(c, api_key, dry_run=False):
            success += 1
        else:
            failed += 1
        time.sleep(0.3)

    print(f"\n{'=' * 65}")
    print(f"Done.")
    print(f"  Deactivated: {success:,}")
    print(f"  Failed:      {failed:,}")
    print("=" * 65)


if __name__ == "__main__":
    main()
