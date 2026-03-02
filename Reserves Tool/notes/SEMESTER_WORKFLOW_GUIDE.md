# Semester Workflow Guide - Quick Reference

## Complete End-to-End Workflow for Any Semester

### Step 1: Process New Semester Data

```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts"

# Basic usage (uses default input)
python process_full_dataset.py

# Or specify your new semester data
python process_full_dataset.py --input ~/Downloads/Fall2026_merged.xlsx --semester "Fall2026"
```

**Output:**
- `Fall2026_BOOKS_consolidated.xlsx` → Use this for ISBN search
- `Fall2026_NONPRINT_consolidated.xlsx` → Non-print items
- Processing summary report in `/reports/`

---

### Step 2: ISBN Search Against Alma

```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search"

# Search for ISBNs in Alma catalog
python alma_isbn_search_tool.py \
  --input ../data/Fall2026_BOOKS_consolidated.xlsx \
  --semester "Fall2026"
```

**Output:**
- `Fall2026_isbn_results_[timestamp].xlsx` → Use this for course automation

---

### Step 3: Create Courses in Alma

```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update"

# DRY RUN first (recommended)
python course_automation_tool.py \
  --input ../../data/Fall2026_isbn_results_[timestamp].xlsx \
  --semester "Fall2026" \
  --dry-run true

# Once verified, run for real
python course_automation_tool.py \
  --input ../../data/Fall2026_isbn_results_[timestamp].xlsx \
  --semester "Fall2026" \
  --dry-run false
```

**Output:**
- `Fall2026_course_automation_results_[timestamp].xlsx` → Results log

---

## All-in-One Command Example

```bash
# Example for Spring 2027 semester
cd "/Users/patty_home/Desktop/Agentic AI"

# Step 1: Process
python scripts/process_full_dataset.py \
  --input data/Spring2027_merged.xlsx \
  --semester "Spring2027"

# Step 2: ISBN Search
python scripts/isbn_search/alma_isbn_search_tool.py \
  --input data/Spring2027_BOOKS_consolidated.xlsx \
  --semester "Spring2027"

# Step 3: Course Automation (dry-run)
python scripts/course_reserves_update/course_automation_tool.py \
  --input data/Spring2027_isbn_results_*.xlsx \
  --semester "Spring2027" \
  --dry-run true
```

---

## Script Features

### process_full_dataset.py
- ✅ Smart title normalization (handles variations)
- ✅ Consolidates by Course + Normalized Title
- ✅ Separates books from non-print items
- ✅ Generates quality reports
- ✅ Reusable for any semester

### alma_isbn_search_tool.py
- ✅ Searches Alma catalog for ISBNs
- ✅ Edition matching
- ✅ Purchase recommendations
- ✅ Accepts any input file
- ✅ Semester-based output naming

### course_automation_tool.py
- ✅ Creates courses in Alma
- ✅ Creates reading lists
- ✅ Adds citations (textbooks)
- ✅ Dry-run mode for safety
- ✅ Works with consolidated data

---

## Scalability for Different Colleges

All scripts are now institution-agnostic and can be used for any college:

### For a Different Institution:

1. **Create new config file:**
   ```bash
   cp scripts/isbn_search/config.json scripts/isbn_search/config_college2.json
   ```

2. **Update API credentials** in the new config file

3. **Run with custom config:**
   - Modify `load_config()` to accept config file parameter
   - Or create institution-specific wrapper scripts

### Multi-Institution Setup:
```
/Users/patty_home/Desktop/Agentic AI/
├── data/
│   ├── BMCC/
│   │   ├── Spring2026_BOOKS_consolidated.xlsx
│   │   └── Fall2026_BOOKS_consolidated.xlsx
│   └── CollegeB/
│       └── Spring2026_BOOKS_consolidated.xlsx
├── scripts/
│   └── isbn_search/
│       ├── config_bmcc.json
│       └── config_collegeb.json
```

---

## Common Usage Patterns

### Testing with Small Dataset
```bash
# Test with 22 courses
python process_full_dataset.py \
  --input projects/030226_test/test_22_courses.xlsx \
  --semester "Test"
```

### Production Full Semester
```bash
# Process 2000+ courses
python process_full_dataset.py \
  --input data/Fall2026_full_export.xlsx \
  --semester "Fall2026"
```

### Sandbox Testing
```bash
# Use sandbox environment
python course_automation_tool.py \
  --sandbox \
  --input data/test_data.xlsx \
  --dry-run false
```

---

## Troubleshooting

### Script Won't Run
```bash
# Check Python environment
which python
python --version  # Should be 3.x

# Check dependencies
pip install pandas requests openpyxl
```

### File Not Found
```bash
# Use absolute paths
python process_full_dataset.py \
  --input "/Users/patty_home/Desktop/data.xlsx"
```

### Permission Errors
```bash
# Verify API permissions
cd "/Users/patty_home/Desktop/Agentic AI/scripts"
python verify_api_permissions.py
```

---

## Quick Checklist

Before running for a new semester:

- [ ] Have merged course/textbook Excel file
- [ ] Verify API key in config.json
- [ ] Run Step 1 (process_full_dataset.py)
- [ ] Review consolidated output files
- [ ] Run Step 2 (alma_isbn_search_tool.py)
- [ ] Check ISBN search results
- [ ] Run Step 3 DRY-RUN first
- [ ] Review dry-run output
- [ ] Get API permissions (if needed)
- [ ] Run Step 3 for REAL

---

## Data Visualization & Analysis

### Step 4: Search Primo Catalog (Optional - Library Availability Check)

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/isbn_search"

# Search Primo for library catalog availability
python primo_isbn_search.py \
  --input ../../data/Fall2026_BOOKS_consolidated.xlsx \
  --semester "Fall2026"
```

**Output:**
- `Fall2026_primo_results_[timestamp].xlsx` → Availability analysis

**What it tells you:**
- Which books are already in your library
- Which books need to be purchased
- Edition matches/mismatches
- Physical vs Electronic availability

---

### Step 5: Generate Reports & Visualizations

After processing your data, create visual reports for stakeholders:

#### A. Interactive Dashboards (Web Browser)

**Course Reserves Dashboard:**
```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"
streamlit run course_reserves_dashboard.py
```
Opens at: `http://localhost:8501`

**Features:**
- Overview: Top courses, enrollment trends
- Departments: Resource allocation by department
- Instructors: Course load analysis
- Textbooks: Sharing opportunities, bulk purchases
- Data Table: Searchable data with CSV export

**Primo Results Dashboard:**
```bash
streamlit run primo_results_dashboard.py
```
Opens at: `http://localhost:8502`

**Features:**
- Overview: Found vs not found, purchase needs
- By Department: Budget priorities
- Availability: High-priority purchases
- Edition Analysis: Version mismatches
- Data Table: Full search results

#### B. Shareable HTML Reports (Email to Colleagues)

**For colleagues without Python:**
```bash
python generate_html_reports.py
```

**Generates:**
- `course_reserves_report_[timestamp].html` - Course overview
- `primo_results_report_[timestamp].html` - Purchase recommendations

**Location:** `/Reserves Tool/reports/`

**To Share:**
- Email as attachment
- Upload to Google Drive/OneDrive
- Place on network share

**Benefits:**
- Opens in any browser (PC, Mac, tablet, phone)
- No installation needed
- Interactive charts included

#### C. Static Visualizations (For Presentations)

**Create PNG charts:**
```bash
# Comprehensive visualizations
python create_visualizations.py

# Top courses analysis
python create_top_courses_chart.py

# Textbook sharing analysis
python analyze_shared_textbooks.py
```

**Output location:** `/Reserves Tool/reports/`

**Use for:**
- PowerPoint presentations
- Printed reports
- Email summaries
- Board meetings

---

### Complete Workflow Example

**Full semester processing with visualizations:**

```bash
# Navigate to project folder
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool"

# Step 1: Process semester data
python scripts/process_full_dataset.py \
  --input data/Spring2027_merged.xlsx \
  --semester "Spring2027"

# Step 2: Search Alma for ISBNs
python scripts/isbn_search/alma_isbn_search_tool.py \
  --input data/Spring2027_BOOKS_consolidated.xlsx \
  --semester "Spring2027"

# Step 3: Search Primo catalog
python scripts/isbn_search/primo_isbn_search.py \
  --input data/Spring2027_BOOKS_consolidated.xlsx \
  --semester "Spring2027"

# Step 4: Generate all reports
python scripts/generate_html_reports.py
python scripts/create_visualizations.py
python scripts/analyze_shared_textbooks.py

# Step 5: Launch dashboard for deep analysis
streamlit run scripts/course_reserves_dashboard.py
```

---

## Reporting Schedule Recommendations

### Weekly (During Semester)
- Update dashboards with latest data
- Monitor enrollment changes
- Track textbook requests

### Monthly
- Generate HTML reports for stakeholders
- Review purchase needs
- Update budget projections

### Semester Start
- Full data processing workflow
- Generate baseline reports
- Share dashboards with department liaisons

### Semester End
- Final analytics and trends
- Historical comparison
- Archive reports for reference

---

## Visualization Outputs Summary

| Tool | Output Type | Best For | Time to Generate |
|------|------------|----------|------------------|
| Streamlit Dashboards | Interactive web app | Deep analysis, filtering | Instant (live data) |
| HTML Reports | Standalone HTML files | Email sharing, no install | 30 seconds |
| Static Charts | PNG images | Presentations, print | 1-2 minutes |
| Excel Reports | Detailed data tables | Sharing with acquisitions | Automatic (with scripts) |

---

## Tips for Success

### For Technical Staff
- Run scripts weekly to keep data fresh
- Archive reports by semester for trends
- Document any customizations made

### For Library Administration
- Share HTML reports via email
- Use dashboards in budget meetings
- Track year-over-year comparisons

### For Faculty Liaisons
- Filter dashboards by department
- Export CSV data for custom analysis
- Share textbook sharing opportunities

---

**Last Updated:** March 2, 2026
**Version:** 3.0 - Complete Edition with Visualization & Analysis
