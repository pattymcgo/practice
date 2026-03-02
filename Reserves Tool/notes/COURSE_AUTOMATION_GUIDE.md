# Alma Course Reserves Automation - Complete Guide

## Overview

This guide documents the complete workflow for automating course reserves in Alma using course and textbook data from your registrar system.

**Created:** February 23, 2026
**Status:** Ready for API permissions

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Data Processing Workflow](#data-processing-workflow)
3. [Running the Automation](#running-the-automation)
4. [Files & Locations](#files--locations)
5. [Troubleshooting](#troubleshooting)
6. [Future Updates](#future-updates)

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

1. Place new files in `/data/` directory
2. Run `process_full_dataset.py` on new data
3. Review reports for quality issues
4. Run automation (test first, then full)
5. Archive old semester data

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

**Last Updated:** March 2, 2026
**Version:** 1.0
