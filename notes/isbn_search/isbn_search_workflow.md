# Course Reserves Workflow - Complete Guide

This document outlines the complete workflow for managing Course Reserves with Alma integration.

## Table of Contents
1. [Data Preparation](#data-preparation)
2. [Data Quality Review](#data-quality-review)
3. [ISBN Search](#isbn-search)
4. [Results Analysis](#results-analysis)

---

## Data Preparation

### Step 1: Merge Course Data

**Purpose:** Combine textbook list with course information (instructors, enrollment, etc.)

**Script:** `merge_course_data.py`

**Input Files:**
- `data/textbooklist_spring2026_01262026.xlsx` - Textbook list from registrar
- `data/courseinfo_spring2026_01262026 (1).xlsx` - Course section information

**Output:**
- `data/merged_course_textbooks.xlsx` - Combined data with 95%+ match rate

**Run:**
```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts"
python3 merge_course_data.py
```

**What It Does:**
- Matches textbooks to course sections
- Adds instructor names, enrollment, meeting times
- Replaces hyphens with spaces in course codes
- Adds EmplID and Class_Number fields

**Expected Results:**
- ~2,595 entries (includes duplicates for multi-section courses)
- 95-96% match rate with course information
- Ready for quality review

---

## Data Quality Review

### Step 2: Check Data Quality

**Purpose:** Identify ISBN and data quality issues before searching

**Script:** Run inline quality check

**Run:**
```bash
python3 << 'EOF'
import pandas as pd
df = pd.read_excel('/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks.xlsx')

print("Quick Quality Check:")
print(f"Total entries: {len(df)}")
print(f"Missing ISBNs: {df['ISBN'].isna().sum()}")
print(f"Missing Instructors: {df['Instructor_Name'].isna().sum()}")
print(f"\nFirst 5 ISBNs:")
print(df['ISBN'].dropna().head(5).tolist())
EOF
```

**Common Issues Found:**
- Missing ISBNs (57% in original data)
- ISBNs with "ISBN:" prefixes
- ISBNs with special characters
- Short/incomplete ISBNs

---

### Step 3: Clean ISBN Data

**Purpose:** Automatically fix common ISBN formatting issues

**Script:** `clean_isbn_data.py`

**Input:**
- `data/merged_course_textbooks.xlsx`

**Output:**
- `data/merged_course_textbooks_CLEANED.xlsx` - Ready for search
- `data/isbn_problems_XXXXXX.xlsx` - ISBNs needing manual review

**Run:**
```bash
python3 clean_isbn_data.py
```

**What It Does:**
- Removes "ISBN-13:", "ISBN:", "13:" prefixes
- Strips hyphens, spaces, colons, and special characters
- Validates ISBN length (must be 10 or 13 digits)
- Flags problematic ISBNs for manual review

**Expected Results:**
- ~197 ISBNs automatically cleaned
- ~1,063 valid ISBNs ready to search
- ~1,532 ISBNs flagged for review

**Cleaning Examples:**
```
Before: "ISBN-13: 97803576886" → After: "97803576886"
Before: "13:978-0-19-518134-0" → After: "9780195181340"
Before: "978-1-5249-0801-0" → After: "9781524908010"
```

---

## ISBN Search

### Step 4: Test the Search

**Purpose:** Verify API connection with a small sample

**Script:** `test_isbn_search.py`

**Run:**
```bash
python3 test_isbn_search.py
```

**What It Does:**
- Tests first 10 unique ISBNs
- Verifies Alma API connection
- Shows sample results

**Expected Time:** 30 seconds

---

### Step 5: Run Full ISBN Search

**Purpose:** Search all ISBNs in Alma catalog

**Script:** `isbn_search_tool.py`

**Input:**
- `data/merged_course_textbooks_CLEANED.xlsx`
- `config.json` (API credentials)

**Output:**
- `data/isbn_results_YYYYMMDD_HHMMSS.xlsx`

**Run:**
```bash
python3 isbn_search_tool.py
```

**What It Does:**
- Searches each unique ISBN in Alma
- Checks physical and electronic holdings
- Reports availability and locations
- Generates purchase recommendations

**Expected Time:** 15-30 minutes for ~1,063 unique ISBNs

**Progress Tracking:**
- Displays `[X/Total] Searching: ISBN`
- Shows found/not found status for each
- Saves results incrementally

---

## Results Analysis

### Step 6: Review Results

**Output File Columns:**

| Column | Description |
|--------|-------------|
| ISBN_Original | Original ISBN from input |
| ISBN_Clean | Normalized ISBN |
| Status | Found / Not Found / Invalid ISBN |
| Title | Book title (if found) |
| MMS_ID | Alma bibliographic record ID |
| Physical_Copies | Number of physical items |
| Electronic_Access | Yes/No for e-access |
| Location | Where items are located |
| Availability | Item status (Available, In Use, etc.) |
| Recommendation | Already Available / Purchase Needed / Purchase Required |

### Step 7: Filter and Act

**Already Available:**
```excel
Filter: Recommendation = "Already Available"
```
These items are ready for Course Reserves - just need to be placed on reserve.

**Purchase Needed:**
```excel
Filter: Recommendation CONTAINS "Purchase"
```
These items need to be acquired:
- **Purchase Required**: Not in catalog at all
- **Purchase Needed**: In catalog but no available copies

**Next Steps:**
1. Export "Purchase Required" list for acquisitions
2. Notify faculty about items already available
3. Process items for Course Reserves placement

---

## Workflow Summary (Quick Reference)

```bash
# 1. Merge course data
python3 merge_course_data.py

# 2. Clean ISBNs
python3 clean_isbn_data.py

# 3. Test search (optional)
python3 test_isbn_search.py

# 4. Run full search
python3 isbn_search_tool.py

# 5. Review results in Excel
# Open: data/isbn_results_YYYYMMDD_HHMMSS.xlsx
```

---

## Troubleshooting

### Problem: "config.json not found"
**Solution:** Create config.json from template:
```bash
cp config.json.template config.json
# Edit config.json and add your API key
```

### Problem: "API key not valid"
**Solution:**
- Verify API key in config.json
- Check that key has Bibs API read permissions
- Confirm region is set correctly (na/eu/ap)

### Problem: "Too many ISBNs still have issues"
**Solution:**
1. Review `isbn_problems_XXXXXX.xlsx`
2. Fix common patterns manually in source data
3. Re-run merge and clean scripts

### Problem: "Search taking too long"
**Solution:**
- This is normal for 1,000+ ISBNs
- Each ISBN requires 1-3 API calls
- Script saves results at the end
- Can stop (Ctrl+C) and results are still saved

---

## Data Flow Diagram

```
textbooklist_spring2026.xlsx
         +
courseinfo_spring2026.xlsx
         ↓
    [MERGE DATA]
         ↓
merged_course_textbooks.xlsx
         ↓
  [CLEAN ISBNs]
         ↓
merged_course_textbooks_CLEANED.xlsx
         ↓
  [ISBN SEARCH]
         ↓
isbn_results_YYYYMMDD.xlsx
         ↓
[MANUAL REVIEW]
         ↓
Purchase List + Items to Place on Reserve
```

---

## Tips for Success

1. **Always clean data first** - Saves time and API quota
2. **Test with small sample** - Catches issues early
3. **Review problem ISBNs** - May contain patterns you can fix
4. **Keep backups** - Save original files before merging
5. **Document changes** - Note any manual corrections made

---

## Future Enhancements

Based on your workflow recommendations document, you can add:
- **Course update automation** - Auto-update course info in Alma
- **Alert system** - Notifications for items to remove from reserves
- **Historical repository** - Searchable archive of past course materials

See `Course_Reserves_Workflow_Recommendations.md` for details.

---

**Last Updated:** 2026-02-23
**Author:** Patty (with Claude Code assistance)
