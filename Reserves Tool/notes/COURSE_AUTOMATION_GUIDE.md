# Alma Course Reserves Automation - Complete Guide

## Overview

This guide documents the complete workflow for managing course reserves in Alma using course and textbook data from your registrar system. It covers:

1. **Reserves Comparison & Maintenance** — checking staff work and generating removal lists each semester
2. **Course Reserves Automation** — creating Alma course entries and reading lists from textbook data

**Created:** February 23, 2026
**Last Updated:** March 5, 2026

---

## Table of Contents

1. [Reserves Maintenance Workflow (Each Semester)](#reserves-maintenance-workflow-each-semester)
2. [System Architecture](#system-architecture)
3. [Data Processing Workflow](#data-processing-workflow)
4. [Running the Automation](#running-the-automation)
5. [Files & Locations](#files--locations)
6. [Troubleshooting](#troubleshooting)
7. [Future Updates](#future-updates)

---

## Reserves Maintenance Workflow (Each Semester)

Run this workflow at the **start of each semester** to verify reserves are correct and clean up outdated items.

### What You Need

1. **Alma citations export** — Export from Alma: Reading Lists → Export citations to Excel
   - Save as: `/data/SP[YY] Citations.xlsx` (e.g., `SP26 Citations.xlsx`)
2. **Merged course/textbook dataset** — From registrar + bookstore data
   - Save as: `/data/merged_course_textbooks_CLEANED.xlsx`

### Step 1: Run the Comparison Report

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool"
python scripts/compare_reserves.py
```

This generates a timestamped Excel report in `/reports/` with the following tabs:

| Tab | Purpose | Action Needed |
|-----|---------|---------------|
| **Summary** | Overview counts for all categories | Review numbers |
| **Removal_Priority_RESE** | Items on the temporary RESE shelf NOT in current semester | PHYSICAL: retrieve book from RESE shelf and reshelve to permanent location |
| **Removal_ReadingList_Only** | Items in reading lists only (not on RESE shelf) NOT in current semester — includes CLOSED permanent location items | DIGITAL: remove citation from reading list in Alma only |
| **Missing_Books** | Textbooks (physical books) that should be on reserve but aren't in Alma | Add to reserves; Primo lookup included to check catalog availability |
| **Missing_NonPrint** | E-books, e-resources, etc. that should be in reading lists but aren't | Add citation to reading list in Alma |
| **Confirmed_On_Reserves** | Items correctly matched — nothing to do | For reference / spot-checking |
| **Needs_Review** | ISBN found in Alma but under a different course code | Manually verify if citation should be reassigned |

### Step 2: Process the Removal List

**Removal_Priority_RESE tab** (do first):
- Items on the RESE shelf that haven't been used since **Spring 2024 or earlier** (2+ years)
- Retrieve each physical book from the RESE shelf and reshelve it to its permanent location
- Then remove the citation from the Alma reading list

**Removal_ReadingList_Only tab**:
- Items only in Alma reading lists (no physical book to retrieve)
- Includes items in permanent CLOSED locations (book stays, only citation is removed)
- Remove each citation from its reading list in Alma

### Optional: Run the Reuse Analysis

To identify titles that are consistently requested semester after semester, run:

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool"
python scripts/reuse_analysis.py
```

This uses the same Alma citations file and produces a report in `/reports/reuse_analysis_[timestamp].xlsx`:

| Tab | Contents |
|-----|----------|
| **Summary** | Tier counts and overview |
| **Long_Term_Staples** | Titles used 5+ semesters — strong candidates for permanent reserve |
| **Frequently_Reused** | Titles used 3-4 semesters |
| **Occasional** | Titles used in exactly 2 semesters |
| **All_Titles** | All titles sorted by reuse count |
| **By_Course_Title** | Per-course view — same course reusing same book across semesters |

**Tip:** Cross-reference the `Long_Term_Staples` tab against the `Removal_Priority_RESE` tab in the comparison report. If a title appears on both lists (flagged for removal but historically high-use), consider keeping it on reserve rather than removing it.

---

### Step 3: Process the Missing Lists

**Missing_Books tab**:
- Books instructors have requested but are not found in Alma reserves
- The **Primo lookup columns** (In_Catalog, Has_Physical, Has_Electronic, Catalog_Action) show what's already in the library catalog
- Use `Catalog_Action` to decide next steps:
  - `In Catalog - Add to Reading List` → book exists, just add to reserves
  - `Not in Catalog - Purchase Needed` → submit purchase request

**Missing_NonPrint tab**:
- E-resources, e-books, etc. not found in reading lists
- Add the citation manually to the appropriate course reading list in Alma

### Step 4: Add Internal Notes to Reserve Items

At the start of each semester, add an internal note (e.g. `On Reserve SP26`) to all physical
items currently on reserve. This requires building an Alma set from barcodes.

**Step 4a — Extract ISBNs from course data**

The authoritative source is `data/full_dataset_BOOKS_consolidated.xlsx`.

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool"
python3 -c "
import pandas as pd, re
df = pd.read_excel('data/full_dataset_BOOKS_consolidated.xlsx')
isbns = set()
for val in df['ISBN_All_Editions'].dropna():
    for p in re.split(r'[,;]', str(val)):
        p = p.strip().replace('-', '')
        if re.fullmatch(r'\d{10}|\d{13}', p):
            isbns.add(p)
pd.DataFrame(sorted(isbns), columns=['ISBN']).to_csv('data/SP26_ISBNs_for_analytics.csv', index=False)
print(len(isbns), 'ISBNs saved')
"
```

Output: `data/SP26_ISBNs_for_analytics.csv` — one ISBN per row.

**Step 4b — Get barcodes from Alma Analytics**

Build a report in Alma Analytics (Physical Items subject area):

Columns: `ISBN`, `Barcode`

Filters:
| Field | Condition | Value |
|---|---|---|
| ISBN | is in | *(paste your ISBN list)* |
| **AND** Lifecycle | equals | `Active` |

> Always include `Lifecycle = Active`. Without it, weeded/suppressed items will appear
> and fail to load into a set in Alma.

Export as CSV and save to `data/`.

**Step 4c — Extract barcodes**

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data/YOUR_ANALYTICS_EXPORT.csv', dtype=str)
df['Barcode'] = df['Barcode'].str.strip()
df['Barcode'].drop_duplicates().sort_values().to_frame().to_excel('data/SP26_barcodes.xlsx', index=False)
"
```

**Step 4d — Load barcodes into an Alma set**

In Alma: **Admin > Manage Sets > Create Set (Itemized) > Upload from file**

Upload `SP26_barcodes.xlsx`. If any barcodes error out:
- **Malformed barcodes** (not 14 digits, has spaces or extra digits) — check the source data
- **"Error retrieving identifier"** with valid-looking barcodes — likely inactive items;
  confirm `Lifecycle = Active` was applied in Step 4b

**Step 4e — Bulk add the internal note**

In Alma: **Admin > Manage Sets > [your set] > Run a Job > Change Physical Items Information**

Set the internal note field to the current semester label (e.g. `On Reserve SP26`).

---

### Adjusting the Removal Cutoff Date

The script only flags items last used **2+ years ago** (currently: Spring 2024 and older).

To change this, edit line ~57 in `scripts/compare_reserves.py`:
```python
REMOVAL_CUTOFF_TERM = 'Spring 2024'   # Change this term as needed
```

Available terms in order: Summer 2023, Fall 2023, Winter 2024, Spring 2024, Summer 2024, Fall 2024, Winter 2025, Spring 2025, Summer 2025, Fall 2025, Winter 2026, Spring 2026

### Title & Publisher Filters

The script automatically excludes items the library does not purchase. To update these lists, edit the constants in `scripts/compare_reserves.py` around line 187:

```python
EXCLUDE_TITLE_TERMS = [
    'lab manual', 'lab. manual', 'laboratory manual', 'laboratory',
    'with connect', 'connect online access', ...
]

EXCLUDE_PUBLISHER_TERMS = [
    'openstax', 'open stax', 'opentextbook',
]
```

Items with 'oer', 'openstax', or 'open stax' in the **title** are reclassified from Book to OER/non-print rather than excluded.

---

---

## System Architecture

### Components

1. **Data Sources**
   - Registrar course data (CSV)
   - Textbook/ISBN data (Excel)

2. **Processing Scripts**
   - `process_full_dataset.py` - Main data consolidation
   - `generate_dataset_reports.py` - Analysis and reporting
   - `verify_api_permissions.py` - API access verification

3. **Automation Tools**
   - `run_automation_test.py` - Test with 22 courses
   - Course automation for full dataset (TBD)

4. **Alma APIs Used**
   - Courses API (Read/Write)
   - Reading Lists API (Read/Write)
   - Citations API (Read/Write)

---

## Data Processing Workflow

### Step 1: Data Consolidation

**Purpose:** Reduce duplicate course entries by combining sections and instructors

**Logic:**
- Group by: **Course Code + Normalized Book Title**
- One Alma course entry = One unique Course + Book combination
- Combine: All sections and instructors for same course+book

**Smart Title Normalization:**
- Removes articles ("The", "A", "An") from anywhere in title
- Removes special characters and extra spaces
- Case-insensitive matching
- Handles title variations (e.g., "Three Squares: Invention Of American Meal" vs "Three Squares: The Invention Of The American Meal")

**Example:**
```
Input (3 rows):
- HSD 110, Section 0800, Belcastro, Book: Access to Health
- HSD 110, Section 0803, Thrower, Book: Access to Health
- HSD 110, Section 1101, Grace, Book: Access to Health

Output (1 row):
- HSD 110, Sections: "0800, 0803, 1101"
  Instructors: "Belcastro / Grace / Thrower"
  Book: Access to Health
```

### Step 2: Separation by Material Type

**Books (Physical Textbooks):**
- TextbookType = "Book"
- 1,874 original rows → 520 consolidated entries
- Covers 249 unique courses

**Non-Print Items:**
- E-Book, E-Resource, Ebook, Mixed, Recording, Software, Score, etc.
- 721 original rows → 212 consolidated entries
- Covers 118 unique courses

### Step 3: Data Quality Checks

**Automated Checks:**
- Missing titles (6 entries)
- Missing instructors (33 entries)
- Missing ISBNs (253 entries)
- Zero enrollment (31 entries)

**Reports Generated:**
- Course summary by number of books
- Instructor analysis
- Consolidation impact (title variations, multiple editions)
- Enrollment statistics
- Data quality issues

---

## Running the Automation

### Prerequisites

**Required API Permissions:**
1. Courses API (Read/Write)
2. Reading Lists API (Read/Write)
3. Citations API (Read/Write)

**How to Request:**
Contact your Alma administrator and provide:
```
"Please add the following API permissions to my API key for Course Reserves automation:
- Courses API - Read/Write
- Reading Lists API - Read/Write
- Citations API - Read/Write"
```

### Verify API Permissions

Run the verification script to check your permissions:

```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts"
python verify_api_permissions.py
```

**Expected Output (when ready):**
```
✅ READY: You have Courses API permissions!
```

### Test Run (22 Courses)

The test dataset includes 22 specific courses for initial testing:

```bash
cd "/Users/patty_home/Desktop/Agentic AI/projects/030226_test"
python run_automation_test.py
```

**What it does:**
- Creates 15 Alma course entries (22 course codes, 16 books, some combined)
- Creates reading list for each course: "{Course Code} Required Textbooks"
- Adds textbook(s) as citations to each reading list

**Test Courses:**
ENG WK95, HSD 110, HSD 190, HSD 195, HSD 202, HSD 211, HSD 220, HSD 225, HSD 230, HSD 235, HSD 240, HSD 250, HSD 255, HSD 260, HSD 280, HSD 290, HSD 295, HSD 296, HSD 301, HSD 302, ITL 106H, MAT 104.5

**To run for REAL:**
1. Open `run_automation_test.py`
2. Change `DRY_RUN = True` to `DRY_RUN = False` (line 34)
3. Run the script
4. Review results in Excel output file

### Full Dataset Run

**After successful test:**
1. Review consolidated data:
   - `/data/full_dataset_BOOKS_consolidated.xlsx` (520 entries)
   - `/data/full_dataset_NONPRINT_consolidated.xlsx` (212 entries)

2. Create full automation script (similar to test script but for all courses)

3. Run in stages by department or course prefix

**Statistics:**
- Total original entries: 2,595
- Total consolidated entries: 732 (520 books + 212 non-print)
- Reduction: 1,863 rows (72% consolidation rate)
- Unique courses: 310

---

## Files & Locations

### Data Files

**Original/Source:**
- `/data/merged_course_textbooks_CLEANED.xlsx` - Original merged dataset (2,595 rows)

**Processed/Separated:**
- `/data/full_dataset_BOOKS.xlsx` - Books only (1,874 rows)
- `/data/full_dataset_NONPRINT.xlsx` - Non-print items (721 rows)

**Consolidated:**
- `/data/full_dataset_BOOKS_consolidated.xlsx` - **USE THIS** (520 entries)
- `/data/full_dataset_NONPRINT_consolidated.xlsx` - **USE THIS** (212 entries)

**Test Data:**
- `/projects/030226_test/test_22_courses_smart_consolidated.xlsx` - 22 test courses (16 entries)

### Scripts

**Reserves Maintenance (run each semester):**
- `/scripts/compare_reserves.py` - **Main maintenance script** — compares Alma citations against semester dataset, generates removal lists and missing items report with Primo catalog lookup
- `/scripts/reuse_analysis.py` - **Reuse analysis** — identifies titles used across multiple semesters; outputs reuse tiers (Long-Term Staple, Frequently Reused, Occasional, Single Semester)

**Data Merging:**
- `/scripts/isbn_search/merge_course_data.py` - Merges registrar course info with textbook list; splits Books vs Non-Print; applies title/publisher filters

**Processing:**
- `/scripts/process_full_dataset.py` - Main consolidation script
- `/scripts/generate_dataset_reports.py` - Analysis and reporting

**Automation:**
- `/projects/030226_test/run_automation_test.py` - Test automation (22 courses)
- `/scripts/course_reserves_update/course_automation_tool.py` - Original automation tool
- `/scripts/verify_api_permissions.py` - Permission verification

**Helper Scripts:**
- `/projects/030226_test/consolidate_smart_titles.py` - Title normalization logic
- `/projects/030226_test/check_hsd195.py` - Specific course verification

### Reports

**Generated in:** `/reports/`
- `reserves_comparison_[timestamp].xlsx` - **Main maintenance report** (Summary, Removal tabs, Missing tabs, Confirmed, Needs_Review)
- `reuse_analysis_[timestamp].xlsx` - **Reuse analysis report** (Long-Term Staples, Frequently Reused, Occasional, All Titles, By Course+Title)
- `course_summary_[timestamp].xlsx` - Course statistics
- `data_quality_issues_[timestamp].xlsx` - Data quality problems

### Configuration

- `/scripts/isbn_search/config.json` - Production API key
- `/scripts/isbn_search/config_sandbox.json` - Sandbox API key (if needed)

---

## Troubleshooting

### Common Issues

**1. API Permission Errors (403 UNAUTHORIZED)**

**Problem:**
```
✗ Error creating course: 403
errorCode>UNAUTHORIZED</errorCode>
```

**Solution:**
- Your API key lacks required permissions
- Run `verify_api_permissions.py` to check
- Contact Alma administrator to add permissions

---

**2. Course Already Exists**

**Problem:** Course with same code already in Alma

**Solution:**
- The script detects existing courses and skips creation
- Textbooks will be added to existing course's reading list

---

**3. Missing Data (No Instructor, No ISBN, etc.)**

**Problem:** Some courses have missing information

**Solution:**
- Review `data_quality_issues_[timestamp].xlsx` report
- Decide whether to:
  - Create courses anyway (Alma allows empty fields)
  - Get missing data from registrar
  - Manually add info after creation

---

**4. Title Variations Not Consolidating**

**Problem:** Same book with different titles creates duplicate entries

**Solution:**
- Check title normalization in `consolidate_smart_titles.py`
- Verify `Title_Normalized` column matches
- May need to add custom normalization rules

---

### Validation Checks

**Before Running Automation:**

1. **Check consolidated data:**
   ```bash
   python -c "import pandas as pd; df = pd.read_excel('data/full_dataset_BOOKS_consolidated.xlsx'); print(f'Entries: {len(df)}')"
   ```

2. **Verify API permissions:**
   ```bash
   python scripts/verify_api_permissions.py
   ```

3. **Review course counts:**
   ```bash
   python scripts/generate_dataset_reports.py
   ```

**After Running Automation:**

1. Check results Excel file for failures
2. Log into Alma and spot-check created courses
3. Verify reading lists have correct textbooks
4. Confirm sections and instructors are combined correctly

---

## Future Updates

### Semester Updates

**When new semester data arrives:**

1. Get files from registrar and bookstore:
   - Textbook list → `/data/textbooklist_[semester]_[date].xlsx`
   - Course info → `/data/courseinfo_[semester]_[date].xlsx`
   - Alma citations export → `/data/[semester] Citations.xlsx`

2. Merge course and textbook data:
   ```bash
   python scripts/isbn_search/merge_course_data.py
   ```
   Output: `/data/merged_course_textbooks.xlsx` (and `_BOOKS.xlsx`, `_NONPRINT.xlsx`)

3. Run the reserves comparison report (see [Reserves Maintenance Workflow](#reserves-maintenance-workflow-each-semester)):
   ```bash
   python scripts/compare_reserves.py
   ```

4. Process removal lists and missing items from the report

5. Run Alma automation to create new course entries (test first, then full):
   ```bash
   python projects/030226_test/run_automation_test.py
   ```

6. Archive old semester data files

### Enhancements

**Planned Improvements:**
- [ ] Automated email notifications when automation completes
- [ ] Integration with student information system for real-time updates
- [ ] Web dashboard for monitoring course creation status
- [ ] Handling of course deletions/updates (not just creation)
- [ ] Non-print items automation (E-books, E-Resources)

### Maintenance

**Regular Tasks:**
- Update API key if rotated
- Review and clean up old test data
- Update normalization rules based on new title patterns
- Archive previous semester course data

---

## Key Statistics (Current Dataset)

### Books (Physical Textbooks)
- **Original entries:** 1,874
- **Consolidated entries:** 520
- **Unique courses:** 249
- **Total enrollment:** 40,774 students
- **Title variations found:** 20
- **Multiple editions:** 21 books

### Top Courses by Books
1. ENG 201 - 43 books
2. CHE 121 - 21 books
3. BIO 425 - 16 books

### Top Courses by Enrollment
1. SPN 105 - 1,405 students
2. ACC 122 - 1,281 students
3. BUS 110 - 981 students

### Top Instructors by Course Entries
1. Sanchez-Zweig,Sara Cristina - 13 entries
2. Bratsis,Peter - 9 entries
3. Schneiderman,Jason A - 8 entries

### Non-Print Items
- **Total entries:** 212
- **E-Books:** 98
- **E-Resources:** 48
- **Ebooks:** 29
- **Mixed:** 25
- **Other:** 12

---

## Contact & Support

**For questions about:**
- **Data processing:** Review this guide and script comments
- **API permissions:** Contact your Alma administrator
- **Alma configuration:** Consult Ex Libris documentation
- **Script errors:** Check error messages and troubleshooting section

**Last Updated:** March 5, 2026
**Version:** 1.2
