---
name: course-reserves-automate
description: Run course reserves automation in dry-run mode for CUNY BMCC. Use when the user wants to automate course creation, check which courses exist in Alma, or process course reserves.
---

# Course Reserves Automation (Dry-Run)

Run the course automation tool in DRY-RUN mode (no actual changes are made). This checks which courses already exist in Alma and shows what would be created if run in live mode.

## What to do

1. Run the course automation script in dry-run mode:
   ```bash
   cd "/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update" && python course_automation_tool.py
   ```
2. Wait for it to complete

## After running, explain to the user

- Total number of courses processed
- **Course Status Breakdown:**
  - How many courses already exist in Alma
  - How many courses need to be created
- Total textbooks that would be added
- Where the results file was saved
- Remind them this was DRY-RUN (no actual changes made)

## Important concepts to explain

- **Already Exists**: Course was found in Alma, would add textbooks to existing course
- **Needs Creation**: Course doesn't exist, would create new course
- **Lecture vs Lab sections**:
  - B suffix = Lecture (BMCC buys textbooks for these)
  - L suffix = Lab (BMCC does NOT buy textbooks for these)
  - Tool matches sections exactly to respect this distinction

## What the results file shows

- Course_Code and Section for each course
- Instructor name
- Course_Status (Already Exists or Needs Creation)
- Textbooks_Added count
- Mode (Dry Run)

## Next steps to suggest

- Review the results Excel file carefully
- Check which courses need creation vs already exist
- If everything looks correct, they can run in live mode later

## General Instructions

1. **Be beginner-friendly**: Use clear, non-technical language
2. **Explain results**: Don't just show numbers, explain what they mean
3. **Suggest next steps**: Always tell them what to do next
4. **Safety first**: Always emphasize this is dry-run, no actual changes are made

## Error Handling

If errors occur:
- Explain what went wrong in plain English
- Suggest fixes (check file paths, verify permissions, check input data)
- Don't leave user stuck - provide actionable next steps

## File Paths

- Course Automation Script: `/Users/patty_home/Desktop/Agentic AI/scripts/course_reserves_update/course_automation_tool.py`
- Input Data: `/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx`
- Results: `/Users/patty_home/Desktop/Agentic AI/data/` (timestamped files)
