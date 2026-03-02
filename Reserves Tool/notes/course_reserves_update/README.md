# Course Reserves Automation Tool

This tool automates the process of creating course reserves in Alma by reading textbook requirements from an Excel file and creating courses with reading lists and citations.

## Overview

The automation tool:
1. Reads textbook data from an Excel file
2. Checks if courses already exist in Alma
3. Creates new courses (or uses existing ones)
4. Creates reading lists for each course
5. Adds textbook citations to the reading lists
6. Reports on what was created vs what already existed

## Features

- **Smart Course Detection**: Checks if courses already exist before creating duplicates
- **Flexible Matching**: Handles courses with:
  - Multiple sections in one course record (e.g., "ACC 330" with sections "0900, 1000, 1800")
  - Instructor names in course codes (e.g., "ANT 100 (Zaman)")
  - Empty section fields (matches as fallback)
- **Exact Section Matching**: Preserves lecture/lab distinctions (see below)
- **Dry Run Mode**: Test the tool without making changes to Alma
- **Comprehensive Reporting**: Shows which courses existed vs which were created

## Important: Lecture vs Lab Sections

### Section Suffix Meanings

Courses may have different section types indicated by suffixes:
- **B suffix** = Lecture sections (e.g., 092B, 114B, 183B)
- **L suffix** = Lab sections (e.g., 092L, 114L, 183L)

### Why This Matters

The tool uses **exact section matching** including these suffixes because:

1. **Lecture and lab are distinct sections** - They should not be matched together
2. **Campus policies vary**:
   - **CUNY BMCC**: Does not purchase textbooks for lab sections, only for lecture sections
   - **Other campuses**: May purchase materials for both lectures and labs
3. **Accurate tracking**: Ensures course materials are added to the correct section type

### Example

If your Excel file has:
- CHE 118, Section 092L (lab)
- CHE 118, Section 092B (lecture)

And Alma has:
- CHE 118 with sections "092B, 114B, 183B" (lectures only)

The tool will:
- ✓ Match section 092B (lecture exists)
- ✗ NOT match section 092L (lab section doesn't exist)

This is **correct behavior** - it prevents adding lab materials to lecture sections or vice versa.

## Prerequisites

### Required API Permissions

You need the following permissions in Alma:
1. **Bibs API** - Read access (for ISBN searches)
2. **Courses API** - Read/Write access
3. **Reading Lists API** - Read/Write access
4. **Citations API** - Read/Write access

### Testing Your Permissions

Before running the automation tool, test your API permissions:

```bash
cd /Users/patty_home/Desktop/Agentic\ AI/scripts/course_reserves_update
python test_permissions.py
```

This will verify you have all required permissions.

## Installation

1. Ensure you have Python 3.x installed
2. Install required packages:
   ```bash
   pip install pandas requests openpyxl
   ```

## Configuration

The tool uses the API configuration from:
```
/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/config.json
```

Make sure this file contains:
```json
{
    "alma_api_key": "your_api_key_here",
    "alma_region": "na"
}
```

## Input File Format

Your Excel file should have these columns:
- **Course_Code**: Course code (e.g., "ACC 330", "ANT 100")
- **Section**: Section number (e.g., "0900", "1200", "092L", "183B")
- **Instructor_First**: Instructor first name
- **Instructor_Last**: Instructor last name
- **Title**: Textbook title
- **Author**: Textbook author
- **Edition**: Edition (optional)
- **ISBN**: ISBN number

Example:
```
Course_Code | Section | Instructor_First | Instructor_Last | Title              | Author        | Edition | ISBN
ACC 330     | 0900    | Clive           | Nair           | Accounting Book    | Smith, J.     | 5th     | 9781234567890
ACC 330     | 0900    | Clive           | Nair           | Finance Workbook   | Jones, K.     | 3rd     | 9780987654321
ANT 100     | 1200    | Meryem          | Zaman          | Anthropology Intro | Brown, L.     | 2nd     | 9781122334455
```

## Usage

### Dry Run Mode (Recommended First)

Test without making changes:

```bash
cd /Users/patty_home/Desktop/Agentic\ AI/scripts/course_reserves_update
python course_automation_tool.py --dry-run
```

This will:
- Check which courses exist in Alma
- Show what would be created
- Not make any actual changes

### Live Mode

Run the actual automation:

```bash
python course_automation_tool.py
```

This will:
- Check existing courses
- Create new courses as needed
- Add textbooks to reading lists
- Generate a detailed results file

## Output

The tool creates an Excel file with results:
```
/Users/patty_home/Desktop/Agentic AI/data/course_results_YYYYMMDD_HHMMSS.xlsx
```

### Output Columns

- **Course_Code**: Course code from input
- **Section**: Section from input
- **Instructor**: Full instructor name
- **Textbook_Title**: Textbook title
- **Course_ID**: Alma course ID
- **Reading_List_ID**: Alma reading list ID
- **Citation_ID**: Alma citation ID
- **Status**: Success/Failed
- **Error_Message**: Error details (if any)
- **Course_Status**: One of:
  - "Already Exists" - Course was found in Alma
  - "Needs Creation" - Course doesn't exist (dry run mode)
  - "Newly Created" - Course was created (live mode)
  - "Failed" - Operation failed
- **Mode**: "DRY_RUN" or "LIVE"

### Summary Report

The tool prints a summary showing:
- Total courses processed
- Successful vs failed operations
- Course status breakdown (Already Exists vs Needs Creation vs Newly Created)
- Output file location

## How Course Matching Works

The tool uses a two-pass matching strategy:

### Pass 1: Exact Section Match
1. Retrieves all courses from Alma (up to 1000 courses)
2. For each course, checks if:
   - Course code matches exactly, OR
   - Course code starts with the search code + " (" (for instructor names)
3. If course code matches, checks if the specific section exists in the course's section list
4. Sections must match exactly (e.g., "092L" will NOT match "092B")

### Pass 2: Empty Section Fallback
1. If no exact section match found in Pass 1
2. Looks for courses with matching code but empty section field
3. These are treated as "all-sections" courses

### Examples

**Example 1**: Course with multiple sections
- Alma has: "ACC 330" with sections "0900, 1000, 1800"
- Input has: Course_Code="ACC 330", Section="0900"
- Result: ✓ Match found (section 0900 exists in list)

**Example 2**: Course with instructor name
- Alma has: "ANT 100 (Zaman)" with sections "1200, 1400"
- Input has: Course_Code="ANT 100", Section="1200"
- Result: ✓ Match found (code matches with instructor name)

**Example 3**: Course with empty sections (fallback)
- Alma has: "AST 110" with empty section field
- Input has: Course_Code="AST 110", Section="1000"
- Result: ✓ Match found (fallback to empty section course)

**Example 4**: Lecture vs Lab distinction
- Alma has: "CHE 118" with sections "092B, 114B, 183B"
- Input has: Course_Code="CHE 118", Section="092L"
- Result: ✗ No match (092L ≠ 092B, different section types)

## Troubleshooting

### "Permission denied" errors
- Run `test_permissions.py` to check your API permissions
- Contact your Alma administrator to request required permissions

### "Course not found" but it exists in Alma
- Check if the course code in Alma has instructor name appended (e.g., "ANT 100 (Zaman)")
- Check if the section number exactly matches (including L/B suffixes)
- Check if section is in comma-separated list for that course

### "Too many courses not found"
- The tool retrieves up to 1000 courses from Alma
- If your institution has more than 1000 courses, some may not be checked
- Consider filtering by academic period in future versions

### Lecture/Lab section confusion
- Remember: B = lecture, L = lab
- These are distinct and should not be matched together
- Check your campus policy on purchasing materials for labs

## API Rate Limits

The Alma API has rate limits:
- Be aware of your institution's API threshold
- The tool processes courses sequentially to avoid hitting limits
- For large batches (100+ courses), consider running in smaller batches

## Best Practices

1. **Always test with dry run first**: `--dry-run` flag
2. **Review the output file**: Check for errors before celebrating
3. **Verify in Alma**: Spot-check a few courses to ensure correct creation
4. **Keep backups**: Save your input Excel files
5. **Check section types**: Ensure lecture/lab sections match your campus policy

## Support

If you encounter issues:
1. Check the error message in the results Excel file
2. Review the console output for details
3. Run `test_permissions.py` to verify API access
4. Check this README for troubleshooting tips

## Version History

- **v1.0** - Initial release with course creation
- **v1.1** - Added existing course detection
- **v1.2** - Enhanced course matching (instructor names, multiple sections)
- **v1.3** - Added two-pass matching for empty sections
- **v1.4** - Current version with lecture/lab section documentation

---

**Note**: This tool was developed for CUNY BMCC but can be adapted for other institutions using Alma. Section suffix conventions (B/L) may vary by institution.
