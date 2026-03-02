# Course Reserves ISBN Search - Quick Reference

## 🚀 Quick Start (3 Commands)

```bash
cd "/Users/patty_home/Desktop/Agentic AI/scripts"

# 1. Merge course data
python3 merge_course_data.py

# 2. Clean ISBNs
python3 clean_isbn_data.py

# 3. Search Alma
python3 isbn_search_tool.py
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `merge_course_data.py` | Combines textbook + course info |
| `clean_isbn_data.py` | Fixes ISBN formatting issues |
| `isbn_search_tool.py` | Searches Alma catalog |
| `test_isbn_search.py` | Tests with 10 ISBNs |
| `config.json` | Your API credentials |

---

## 📊 Data Flow

```
Original Data → Merge → Clean → Search → Results
    ↓            ↓       ↓        ↓        ↓
Textbook +   2,595   1,063    Alma    Purchase
CourseInfo   rows    valid    API      List
                     ISBNs
```

---

## ⚙️ Setup (One Time)

1. **Install libraries:**
   ```bash
   pip3 install pandas openpyxl requests
   ```

2. **Configure API:**
   ```bash
   cp config.json.template config.json
   # Edit config.json with your API key
   ```

---

## 🔍 What Each Script Does

### merge_course_data.py
- Matches textbooks to courses
- Adds instructor names, enrollment
- Output: `merged_course_textbooks.xlsx`
- Time: ~30 seconds

### clean_isbn_data.py
- Removes "ISBN:" prefixes
- Strips special characters
- Output: `merged_course_textbooks_CLEANED.xlsx`
- Output: `isbn_problems_XXXXXX.xlsx`
- Time: ~10 seconds

### isbn_search_tool.py
- Searches each ISBN in Alma
- Gets availability info
- Output: `isbn_results_YYYYMMDD_HHMMSS.xlsx`
- Time: ~20-30 minutes

---

## 📋 Results Interpretation

| Recommendation | Meaning | Action |
|---------------|---------|--------|
| Already Available | In catalog with copies | Place on reserves |
| Purchase Needed | In catalog, no copies | Order more copies |
| Purchase Required | Not in catalog | Acquire item |

---

## 🛠️ Common Issues

**"config.json not found"**
→ Copy template: `cp config.json.template config.json`

**"API key invalid"**
→ Check `config.json` has correct key

**"Too many bad ISBNs"**
→ Review `isbn_problems_XXXXXX.xlsx` and fix source data

---

## 📞 For More Help

- Full workflow: See [WORKFLOW.md](WORKFLOW.md)
- Tool details: See [README.md](README.md)
- Best practices: See [Course_Reserves_Workflow_Recommendations.md](../notes/Course_Reserves_Workflow_Recommendations.md)

---

**Last Updated:** 2026-02-23
