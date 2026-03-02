# Path Updates for "Reserves Tool" Folder Structure

## Summary

All file paths have been updated from:
```
/Users/patty_home/Desktop/Agentic AI/...
```

To:
```
/Users/patty_home/Desktop/Agentic AI/Reserves Tool/...
```

---

## Updated Files

### Main Workflow Scripts ✅

1. **process_full_dataset.py**
   - `default_input` → `Reserves Tool/data/...`
   - `output_dir` → `Reserves Tool/data`

2. **alma_isbn_search_tool.py**
   - `default_input` → `Reserves Tool/data/...`
   - `output_dir` fallback → `Reserves Tool/data`

3. **course_automation_tool.py**
   - `default_input` → `Reserves Tool/data/...`
   - `output_dir` fallback → `Reserves Tool/data`

4. **generate_dataset_reports.py**
   - `books_file` → `Reserves Tool/data/...`
   - `nonprint_file` → `Reserves Tool/data/...`
   - `reports_dir` → `Reserves Tool/reports`

5. **process_semester_data.py**
   - `DEFAULT_INPUT` → `Reserves Tool/data/...`
   - `OUTPUT_DIR` → `Reserves Tool/data`
   - `REPORTS_DIR` → `Reserves Tool/reports`

6. **verify_api_permissions.py**
   - `sys.path.insert` → `Reserves Tool/scripts/isbn_search`
   - `config_path` → `Reserves Tool/scripts/isbn_search/config.json`

---

## Files That Still Need Manual Update (If Used)

These are older test scripts that may need updating if you use them:

- `/projects/030226_test/run_automation_test.py`
- `/projects/030226_test/run_final_test.py`
- `/projects/030226_test/run_final_test_smart.py`
- `/scripts/isbn_search/primo_isbn_search.py`
- `/scripts/isbn_search/clean_isbn_data.py`
- `/scripts/isbn_search/merge_course_data.py`
- Various test scripts in `/scripts/isbn_search/test_*.py`

---

## New Folder Structure

```
/Users/patty_home/Desktop/Agentic AI/Reserves Tool/
├── data/                    # All data files
├── scripts/                 # All scripts
│   ├── isbn_search/        # ISBN search tools
│   ├── course_reserves_update/  # Course automation
│   ├── process_full_dataset.py
│   ├── generate_dataset_reports.py
│   └── verify_api_permissions.py
├── projects/               # Project-specific work
│   └── 030226_test/       # Test project
├── reports/                # Generated reports
└── notes/                  # Documentation
```

---

## Updated Workflow Commands

### Step 1: Process Data
```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"
python process_full_dataset.py --input ~/Desktop/Fall2026.xlsx --semester "Fall2026"
```

### Step 2: ISBN Search
```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/isbn_search"
python alma_isbn_search_tool.py \
  --input ../data/Fall2026_BOOKS_consolidated.xlsx \
  --semester "Fall2026"
```

### Step 3: Course Automation
```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/course_reserves_update"
python course_automation_tool.py \
  --input ../../data/Fall2026_isbn_results_*.xlsx \
  --semester "Fall2026" \
  --dry-run true
```

---

## Verification

To verify all paths are correct, run:
```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"

# Check if default paths exist
ls -l "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/"
ls -l "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/"
ls -l "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/"
```

---

**Updated:** March 2, 2026
**Status:** All main workflow scripts updated ✅
