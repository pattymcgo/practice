# Missing Items Workflow Guide

## Overview
This guide documents the end-to-end workflow for processing missing items reports.
All scripts live in the `missing items/` folder and are run from that folder.

---

## Step-by-Step Workflow

### STEP 1 — Separate the worked file by status
**Script:** `separate_by_status.py`
**Input:** A file with Sheet1 where the Found? column is already filled in.

**What it does:** Splits Sheet1 into four output sheets:
- **Found Items** — Found? is any "found" variant
- **Needs Review** — Found? is blank/unknown, or call number is "Unknown"
- **Not Found With Notes** — Not found AND notes contain keywords (last searched, discard, not on shelf, etc.)
- **Not Found No Notes** — Not found AND no relevant keywords in notes

**To run:**
1. Open `separate_by_status.py`
2. Update `INPUT_FILE` and `OUTPUT_FILE` at the top to match your file names
3. Run: `python3 separate_by_status.py`

> **Note:** If your file has IC/YH/PL sub-sheets with Found? data,
> run `clean_missing_items.py` first (see Optional Step below), then run this script.

---

### STEP 2 — Manual review
Open the output file and review:
- **Needs Review** tab — decide action for each item
- **Found Items** tab — confirm and close out found items

---

### STEP 3 — Export barcodes for Alma processing
**Script:** `export_barcodes.py`
**Input:** The `_separated.xlsx` file produced in Step 1.

**What it does:** Creates two separate barcode-only Excel files:
- `barcodes_not_found_with_notes.xlsx`
- `barcodes_not_found_no_notes.xlsx`

**To run:**
1. Open `export_barcodes.py`
2. Update `INPUT_FILE` at the top if your separated file has a different name
3. Run: `python3 export_barcodes.py`

Upload these barcode lists to Alma for further processing.

---

### STEP 4 — Divide new Alma missing report among team
**Script:** `split_missing_report.py`
**Input:** The fresh missing items report downloaded from Alma (raw export, Sheet1 only,
title row on row 1, headers on row 3, data from row 4, Found? column blank).

**What it does:** Splits items into three sheets by location as evenly as possible:
- **IC**
- **PL**
- **YH**

**To run:**
1. Open `split_missing_report.py`
2. Update `INPUT_FILE` and `OUTPUT_FILE` at the top
3. Check location names in the new file match what's in `YH_LOCATIONS` and `PL_LOCATIONS`
   (if locations changed, update those sets and re-check `STACKS_IC_LIMIT` for balance)
4. Run: `python3 split_missing_report.py`

Distribute each tab to the appropriate team member.

---

## Optional Step — Clean a file with sub-sheets
**Script:** `clean_missing_items.py`
**Input:** A file that has Sheet1 PLUS sub-sheets named IC, YH, and PL.

**What it does:**
- Normalizes Found? values across all sheets
- Looks up barcodes from sub-sheets to populate Found? on Sheet1
- Removes fully empty rows
- Saves a `_cleaned.xlsx` file

**To run:**
1. Update `INPUT_FILE` and `OUTPUT_FILE` at the top
2. Run: `python3 clean_missing_items.py`
3. Then use the cleaned output as the input for `separate_by_status.py` (Step 1)

---

## Quick Reference — Which script do I need?

| File type | Scripts to run (in order) |
|---|---|
| Has Sheet1 + sub-sheets (IC/YH/PL) | `clean_missing_items.py` → `separate_by_status.py` → `export_barcodes.py` |
| Has Sheet1 only, Found? filled in | `separate_by_status.py` → `export_barcodes.py` |
| Raw Alma export (Found? blank, title row) | `split_missing_report.py` |

---

## Notes on Keywords (separate_by_status.py)
Items are placed in **Not Found With Notes** if either notes column contains:
- `last searched` (extra spaces between words are handled automatically)
- `discard`
- `not found on shelf`
- `not on shelf`
- `wanted to weed`
- `missing`

To add new keywords in the future, open `separate_by_status.py` and add a new line
to the `NOTE_PATTERNS` list following the same format as the existing entries.
