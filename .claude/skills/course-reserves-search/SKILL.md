---
name: course-reserves-search
description: Search ISBNs in Alma catalog for CUNY BMCC Course Reserves. Use when the user wants to search for textbooks, check ISBN availability, or find books in the library catalog.
---

# Course Reserves ISBN Search

Search all ISBNs from the input Excel file against the Alma library catalog.

## What to do

1. Run the ISBN search script:
   ```bash
   cd "/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search" && python alma_isbn_search_tool.py
   ```
2. Wait for it to complete

## After running, explain to the user

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

## Important notes to mention

- Results are saved with a timestamp in the filename
- Check the Recommendation column to see what needs to be purchased
- Items with "Wrong Edition" may need manual verification

## General Instructions

1. **Be beginner-friendly**: Use clear, non-technical language
2. **Explain results**: Don't just show numbers, explain what they mean
3. **Suggest next steps**: Always tell them what to do next
4. **Safety first**: This is a read-only search, no changes are made

## Error Handling

If errors occur:
- Explain what went wrong in plain English
- Suggest fixes (check file paths, verify permissions, check input data)
- Don't leave user stuck - provide actionable next steps

## File Paths

- ISBN Search Script: `/Users/patty_home/Desktop/Agentic AI/scripts/isbn_search/alma_isbn_search_tool.py`
- Input Data: `/Users/patty_home/Desktop/Agentic AI/data/merged_course_textbooks_CLEANED.xlsx`
- Results: `/Users/patty_home/Desktop/Agentic AI/data/` (timestamped files)
