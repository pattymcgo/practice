# Course Reserves Automation Skill

Help manage CUNY BMCC Course Reserves automation workflow using Alma API.

## Usage

```
/course-reserves [command]
```

## Available Commands

- `search` - Search ISBNs in Alma catalog
- `automate` - Run course automation in dry-run mode (safe, no changes)
- `help` - Show detailed help and workflow guide

## Examples

```bash
# Search for ISBNs in Alma
/course-reserves search

# Run automation in dry-run mode (safe, no changes)
/course-reserves automate
```

---

## Skill Behavior

### For `/course-reserves search` command:

**What it does:**
1. Navigates to the ISBN search script directory
2. Runs `alma_isbn_search_tool.py`
3. Searches all ISBNs from the input Excel file against Alma catalog
4. Creates a results Excel file with findings

**After running, explain to the user:**
- How many ISBNs were searched
- How many were found vs not found in Alma
- How many are already available (correct edition)
- How many need purchase
- Where the results file was saved
- What the key columns mean:
  - **Status**: Found or Not Found
  - **Edition_Match**: Match, Mismatch, or Verify Manually
  - **Recommendation**: What action to take (already available, purchase needed, verify manually)
  - **Physical_Copies**: Number of physical items in library
  - **Electronic_Access**: Yes/No for e-books

**Important notes to mention:**
- Results are saved with a timestamp in the filename
- Check the Recommendation column to see what needs to be purchased
- Items with "Wrong Edition" may need manual verification

---

### For `/course-reserves automate` command:

**What it does:**
1. Navigates to the course automation script directory
2. Runs `course_automation_tool.py` in DRY-RUN mode (no actual changes)
3. Checks which courses already exist in Alma
4. Shows what would be created if run in live mode
5. Creates a results Excel file

**After running, explain to the user:**
- Total number of courses processed
- **Course Status Breakdown:**
  - How many courses already exist in Alma
  - How many courses need to be created
- Total textbooks that would be added
- Where the results file was saved
- Remind them this was DRY-RUN (no actual changes made)

**Important concepts to explain:**
- **Already Exists**: Course was found in Alma, would add textbooks to existing course
- **Needs Creation**: Course doesn't exist, would create new course
- **Lecture vs Lab sections**:
  - B suffix = Lecture (BMCC buys textbooks for these)
  - L suffix = Lab (BMCC does NOT buy textbooks for these)
  - Tool matches sections exactly to respect this distinction

**What the results file shows:**
- Course_Code and Section for each course
- Instructor name
- Course_Status (Already Exists or Needs Creation)
- Textbooks_Added count
- Mode (Dry Run)

**Next steps to suggest:**
- Review the results Excel file carefully
- Check which courses need creation vs already exist
- If everything looks correct, they can run in live mode later
- Reference the README.md for more details

---

### For `/course-reserves help` command:

**Show the complete workflow:**

1. **Step 1: Test Permissions** (not yet implemented in skill)
   - Run `test_permissions.py` to verify API access
   - Make sure you have all required permissions

2. **Step 2: Search ISBNs**
   - Run `/course-reserves search`
   - Review which textbooks are available vs need purchase

3. **Step 3: Dry-Run Automation**
   - Run `/course-reserves automate`
   - See which courses exist vs need creation
   - No actual changes are made

4. **Step 4: Review Results**
   - Open the Excel results file
   - Verify the course statuses are correct
   - Check the textbook counts

5. **Step 5: Run Live** (not yet implemented in skill)
   - Only after reviewing dry-run results
   - Requires manually editing the script
   - Creates actual courses and reading lists in Alma

**Important Files:**
- Input: `/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx`
- Config: `/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/config.json`
- Scripts: `/Users/patty_home/Desktop/Agentic AI/scripts/`
- Results: `/Users/patty_home/Desktop/Agentic AI/data/`
- Documentation: `/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update/README.md`

**Lecture vs Lab Sections:**
- B = Lecture sections (BMCC purchases textbooks)
- L = Lab sections (BMCC does NOT purchase textbooks)
- Other campuses may have different policies
- Tool matches exactly to prevent mixing these up

---

## General Instructions

When this skill is invoked:

1. **Be beginner-friendly**: Use clear, non-technical language
2. **Explain results**: Don't just show numbers, explain what they mean
3. **Provide context**: Help the user understand what happened and why
4. **Suggest next steps**: Always tell them what to do next
5. **Reference documentation**: Point to README.md for detailed info
6. **Safety first**: Always emphasize dry-run before live mode

## Error Handling

If errors occur:
- Explain what went wrong in plain English
- Suggest fixes (check file paths, verify permissions, check input data)
- Point to relevant documentation
- Don't leave user stuck - provide actionable next steps

## File Paths

- ISBN Search Script: `/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/alma_isbn_search_tool.py`
- Course Automation Script: `/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update/course_automation_tool.py`
- Input Data: `/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx`
- Results: `/Users/patty_home/Desktop/Agentic AI/data/` (timestamped files)
