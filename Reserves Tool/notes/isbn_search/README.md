# ISBN Search Tool for Alma

This tool automatically searches your Alma library catalog for a list of ISBNs and generates a report showing availability, holdings, and purchase recommendations.

## Files in this Folder

- **isbn_search_tool.py** - Main Python script
- **config.json.template** - Configuration template (copy and rename to config.json)
- **README.md** - This file (instructions)

## Setup Instructions

### 1. Install Required Libraries

The libraries should already be installed, but if needed:
```bash
pip3 install almapipy pandas openpyxl requests
```

### 2. Create Configuration File

1. Copy `config.json.template` and rename it to `config.json`:
   ```bash
   cp config.json.template config.json
   ```

2. Open `config.json` in a text editor

3. Replace `YOUR_API_KEY_HERE` with your actual Alma API key

4. Set your region:
   - `"na"` for North America
   - `"eu"` for Europe
   - `"ap"` for Asia Pacific

**Example config.json:**
```json
{
  "alma_api_key": "l7xx1234567890abcdef1234567890ab",
  "alma_region": "na"
}
```

⚠️ **IMPORTANT:** Never commit `config.json` to GitHub (it contains your secret API key!)

### 3. Create Input File

Create an Excel file named `isbn_input.xlsx` in the same folder as the script.

The file must have a column named **ISBN** (case-sensitive).

**Example:**

| ISBN |
|------|
| 9780143039983 |
| 978-0-06-112008-4 |
| 0451524934 |

You can include ISBNs in any format (with or without hyphens).

## How to Run

### Complete Workflow

See [WORKFLOW.md](WORKFLOW.md) for the complete step-by-step guide.

### Quick Start

1. **Merge course data:**
   ```bash
   cd "/Users/patty_home/Desktop/Agentic AI/scripts"
   python3 merge_course_data.py
   ```

2. **Clean ISBN data:**
   ```bash
   python3 clean_isbn_data.py
   ```

3. **Run ISBN search:**
   ```bash
   python3 isbn_search_tool.py
   ```

4. **Review results:**
   - Open `data/isbn_results_YYYYMMDD_HHMMSS.xlsx`
   - Filter by "Recommendation" column

## Output File

The results Excel file contains these columns:

- **ISBN_Original** - ISBN as it appeared in your input file
- **ISBN_Clean** - Normalized ISBN (no hyphens)
- **Status** - Found, Not Found, or Invalid ISBN
- **Title** - Book title (if found)
- **MMS_ID** - Alma record ID
- **Physical_Copies** - Number of physical items
- **Electronic_Access** - Yes/No for electronic availability
- **Location** - Where physical items are located
- **Availability** - Item availability status
- **Recommendation** - Already Available, Purchase Needed, or Purchase Required

## Understanding the Results

### Status Column
- **Found** - Item exists in your Alma catalog
- **Not Found** - Item not in catalog
- **Invalid ISBN** - ISBN format issue

### Recommendation Column
- **Already Available** - Item is in your collection (physical or electronic)
- **Purchase Needed** - Found in Alma but no available copies
- **Purchase Required** - Not found in Alma at all

## Example Workflow

1. Export list of ISBNs from course reserves request
2. Save as `isbn_input.xlsx` with ISBN column
3. Run the script
4. Review the results file
5. Filter by "Purchase Required" or "Purchase Needed" to create purchase list
6. Filter by "Already Available" to identify items ready for course reserves

## Troubleshooting

### "config.json not found"
- Make sure you copied and renamed `config.json.template` to `config.json`

### "Input file 'isbn_input.xlsx' not found"
- Create the Excel file in the same folder as the script
- Make sure it's named exactly `isbn_input.xlsx`

### "ERROR: Input file must have a column named 'ISBN'"
- Your Excel file needs a column header named `ISBN` (all caps)

### API Errors
- Check that your API key is correct in `config.json`
- Verify your API key has permissions for Bibs API
- Check that your region is set correctly

## Next Steps

After successfully running the ISBN search tool, you can:

1. **Automate Course Updates** - Build the course information update utility
2. **Create Alert System** - Set up alerts for items to remove from reserves
3. **Historical Repository** - Build the searchable historical database

See `Course_Reserves_Workflow_Recommendations.md` for the full implementation plan.

## Questions?

If you run into issues or need help:
1. Check the error message carefully
2. Review the troubleshooting section above
3. Ask Claude Code for help debugging

---

**Created:** 2026-02-23
**Author:** Patty (with Claude Code)
