# Primo ISBN Search & Dashboard Guide

## Overview

The Primo ISBN Search tool checks your library catalog (CUNY BMCC Primo) to determine:
- What textbooks are already available
- What needs to be purchased
- Edition matches/mismatches
- Physical vs Electronic availability

## Quick Start

### 1. Run Primo ISBN Search

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts/isbn_search"

# Search for all books in your dataset
python primo_isbn_search.py \
  --input "../../data/full_dataset_BOOKS_consolidated.xlsx" \
  --semester "Spring2026"
```

**What it does:**
- Searches Primo catalog for each ISBN
- Checks edition matches
- Identifies purchase needs
- Saves results to Excel file

### 2. Launch Interactive Dashboard

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"
streamlit run primo_results_dashboard.py
```

**Dashboard automatically opens at:** `http://localhost:8501`

---

## Dashboard Features

### 5 Interactive Tabs:

#### 1. 📈 Overview
- Search results status (Found/Not Found)
- Recommendation breakdown
- Physical vs Electronic availability
- Edition match status pie charts

#### 2. 🏢 By Department
- Purchase needs by department
- Found vs Not Found comparison
- Department summary table with found rates
- Identify which departments need most support

#### 3. ✅ Availability
- Top courses needing purchases (prioritized)
- Books with wrong editions
- High-enrollment courses requiring purchases
- Action items for library purchases

#### 4. 📚 Edition Analysis
- Edition matches by department
- Format availability (Physical vs Electronic)
- Books requiring manual verification
- Detailed edition comparison

#### 5. 📋 Data Table
- Searchable full dataset
- Customizable column selection
- CSV export for filtered data
- Advanced filtering options

---

## Key Insights You'll Get

### Purchase Planning
- **Total books needing purchase** - Immediate budget estimate
- **Priority by enrollment** - Which courses impact most students
- **Department breakdown** - Allocate resources by department

### Edition Management
- **Edition mismatches** - Books available but wrong edition
- **Verify manually** - Books needing staff review
- **Exact matches** - Books ready to use as-is

### Format Optimization
- **Physical availability** - Books in your collection
- **Electronic availability** - Online access available
- **Neither** - True gaps in collection

---

## Workflow Integration

### Complete Course Reserves Workflow:

1. **Process semester data** → `process_full_dataset.py`
2. **Search Primo catalog** → `primo_isbn_search.py` ✓ (You just ran this!)
3. **Analyze in dashboard** → `primo_results_dashboard.py` ✓ (About to launch!)
4. **Identify purchases needed** → Use dashboard filters
5. **Submit purchase requests** → Export CSV from dashboard
6. **Create Alma courses** → `course_automation_tool.py` (when API ready)

---

## Understanding the Results

### Status Types:
- **Found** - ISBN exists in Primo catalog
- **Not Found** - ISBN not in catalog
- **Invalid ISBN** - ISBN format issue

### Recommendations:
- **Already Available - Correct Edition** ✅ - Ready to use!
- **Wrong Edition - Verify or Purchase Needed** ⚠️ - Action required
- **Available - Verify Edition Manually** 🔍 - Staff review needed
- **Purchase Required** ❌ - Not in collection
- **May Need Purchase (verify manually)** - Found but unclear availability

### Edition Match:
- **Match** - Required edition available
- **Mismatch** - Different edition in catalog
- **Verify Manually** - Could not auto-determine
- **N/A** - No edition info available

---

## Tips for Using the Dashboard

1. **Start with Overview tab** - Get big picture
2. **Check Department tab** - See which depts need help
3. **Use Availability tab** - Prioritize purchases by enrollment
4. **Export filtered data** - Share with acquisitions team
5. **Apply filters** - Focus on specific departments or statuses

---

## Recent Search Results

**File:** `full_dataset_primo_results_20260302_144755.xlsx`

**Summary:**
- Total ISBNs searched: 520
- Found in Primo: 143 (27.5%)
- Not found: 124 (23.8%)
- Purchase needed: 267 (51.3%)
- Edition mismatches: 3

---

**Created:** March 2, 2026
**Version:** 1.0
