# Setup Summary - Course Reserves ISBN Search Tool

## What We Built

### 1. Data Merger (`merge_course_data.py`)
✅ Combines textbook list with course information
- **Input Files:**
  - `textbooklist_spring2026_01262026.xlsx` (1,752 textbook entries)
  - `courseinfo_spring2026_01262026 (1).xlsx` (7,774 course sections)
- **Output:** `merged_course_textbooks.xlsx` (2,595 entries)
- **Match Rate:** 95.9% (2,489 entries with instructor/enrollment data)

### 2. ISBN Search Tool (`isbn_search_tool.py`)
✅ Searches Alma catalog for ISBNs and reports availability
- Uses direct Alma API (no third-party dependencies)
- Processes Excel file with ISBNs
- Outputs detailed availability report
- Now uses the merged file with course information

### 3. Configuration (`config.json`)
✅ Stores your Alma API credentials securely
- API Key: Configured
- Region: North America (na)

### 4. Test Script (`test_isbn_search.py`)
✅ Tests API connection with first 5 ISBNs
- Validates API key works
- Quick sanity check before full run

---

## Files Created

```
/Users/patty_home/Desktop/Agentic AI/
├── scripts/
│   ├── isbn_search_tool.py          # Main ISBN search tool
│   ├── merge_course_data.py          # Data merger
│   ├── test_isbn_search.py           # Test script
│   ├── config.json                   # API configuration (DO NOT commit to git!)
│   ├── config.json.template          # Template for API config
│   └── README.md                     # Documentation
│
└── data/
    ├── textbooklist_spring2026_01262026.xlsx          # Original textbook list
    ├── courseinfo_spring2026_01262026 (1).xlsx        # Original course info
    └── merged_course_textbooks.xlsx                    # ⭐ MERGED FILE (ready to use)
```

---

## Merged Data Includes

Your `merged_course_textbooks.xlsx` file now has:

**From Textbook List:**
- Course code, Section
- ISBN, Title, Author, Publisher
- Edition, Price
- Textbook type, Status

**From Course Info:**
- Course description
- **Instructor name** 👨‍🏫
- Total enrollment, Capacity
- Meeting days, times
- Room/location
- Course start/end dates

---

## How to Use

### Run Data Merge (if needed again):
```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts"
python3 merge_course_data.py
```

### Run ISBN Search:
```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts"
python3 isbn_search_tool.py
```

This will:
1. Read 2,595 entries from merged file
2. Search Alma for each unique ISBN
3. Create `isbn_results_[timestamp].xlsx` with availability

---

## What's in the Results File

The ISBN search creates a report with:

| Column | Description |
|--------|-------------|
| ISBN_Original | ISBN as it appeared in input |
| ISBN_Clean | Normalized ISBN |
| Status | Found, Not Found, or Invalid |
| Title | Book title (if found) |
| MMS_ID | Alma record ID |
| Physical_Copies | Number of physical items |
| Electronic_Access | Yes/No for e-access |
| Location | Where items are located |
| Availability | Item status |
| Recommendation | Purchase needed or already available |

---

## Next Steps

**Option 1: Run Full ISBN Search**
```bash
python3 isbn_search_tool.py
```
- Processes all 2,595 entries
- Takes 20-40 minutes
- Uses your API quota

**Option 2: Test with Sample First**
```bash
python3 test_isbn_search.py
```
- Tests first 5 ISBNs only
- Validates everything works

**Option 3: Build Next Tool**
Based on your workflow recommendations, we could build:
- Course update automation tool
- Alert system for items to remove
- Historical repository

---

## Important Notes

### API Key Security
⚠️ **NEVER commit `config.json` to GitHub!** It contains your secret API key.

### Git Ignore
Add this to `.gitignore`:
```
config.json
*.xlsx
data/
```

### Data Updates
When you get new semester data:
1. Replace the input files in `/data/`
2. Run `merge_course_data.py` to re-merge
3. Run `isbn_search_tool.py` with new merged file

---

## Sample Output

Here's what the merged data looks like:

| Course | Section | Instructor_Name | ISBN | Title |
|--------|---------|-----------------|------|-------|
| ACC-122 | 0701 | Spolansky,Arthur | 9780135368749 | Accounting Principles I Package... |
| ACC-122 | 0800 | Donnay,Wilbert | 9780135368749 | Accounting Principles I Package... |
| BIO-211 | 1201 | Kim,Susan | 9781266574641 | Human Anatomy |

---

## Questions?

Ask Claude Code for help with:
- Running the tools
- Interpreting results
- Modifying scripts
- Building additional features

**Your ISBN search tool is ready to use!** 🎉
