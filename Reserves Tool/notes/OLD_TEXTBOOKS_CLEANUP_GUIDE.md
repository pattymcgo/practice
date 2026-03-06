# Old Textbooks Collection Cleanup Guide
## CUNY BMCC Library

**Script:** `scripts/old_textbooks_cleanup.py`
**Last updated:** March 5, 2026

---

## Overview

This tool analyzes the Old Textbooks (OLDTX) collection and flags items for weeding based on
edition age and copy count policies. It also flags items in other locations (STACK, CLOSED, etc.)
that are currently on the Reserves shelf and have old editions, for staff review.

**No changes are made to Alma.** The script generates a review report only.

---

## Step 1: Download the Alma Analytics Report

### Subject Area
Physical Items

### Columns to Include
| Column Name |
|---|
| MMS Id |
| Lifecycle |
| Location Code |
| Temporary Location Code |
| Title |
| Title (Normalized) |
| Publication Date |
| Due Back Date (calendar) |
| Barcode |
| Physical Item Id |
| Base Status |
| Process Type |
| Copy ID |
| Holdings ID |
| Permanent Call Number |
| Normalized Call Number |

### Filter Logic
Set up three conditions connected with **OR**:

| Field | Condition | Value |
|---|---|---|
| Permanent Location Code | equals | `OLDTX` |
| **OR** Permanent Location Code | equals | `CLOSED` |
| **OR** Temporary Location Code | equals | `RESE` |

> **Why this works:**
> - `OLDTX` = Old Textbooks stacks — primary collection for weeding
> - `CLOSED` = Closed stacks items — included for edition policy only
> - Temporary Location = `RESE` = any item currently sitting on the Reserves shelf
>   (catches STACK, DICT, COMIC, BMPB, and other permanent locations currently on reserves)

### Export Format
CSV (UTF-8)

### Expected Output Profile (as of March 2026)
- ~3,869 rows total
- Permanent locations: OLDTX (~3,500), STACK (~292), CLOSED (~66), others (~31)
- Temporary locations: RESE (~903), blank/none (~2,940), OLDTX (~26)

---

## Step 2: Update the Input File Path

Open `scripts/old_textbooks_cleanup.py` and update line 48:

```python
INPUT_FILE = os.path.join(BASE_DIR, "data/YOUR_NEW_FILENAME.csv")
```

Save the file in `data/` with any filename you like.

---

## Step 3: Run the Script

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool"
python scripts/old_textbooks_cleanup.py
```

The report is saved to the `reports/` folder with a timestamp in the filename.

---

## Policy Rules

### Missing/Lost Detection
Uses the **Process Type** column (not Base Status alone):
- **Truly missing/lost** = Process Type is `Lost`, `Missing`, or `Lost and paid`
  - Excluded from edition ranking and copy count
- **On loan** = Process Type is `Loan`, `Transit`, `In Process`, or `Acquisition`
  - Count as real copies — they will return

### Edition Ranking
- Items are grouped by **call number stem** (publication year stripped off)
  - Example: `RT41 .K74 2019` → stem `rt41 .k74`
- Within each stem group, editions are ranked **newest-first**
- Edition ranking uses **all locations** (OLDTX + STACK + CLOSED + others)
- Editions where **all copies are missing/lost** do not occupy an edition slot

### Edition Limits
| Subject Type | Keep Latest N Editions |
|---|---|
| Health / Biology (LCC R class, QH/QK/QL/QM/QP/QR) | 2 |
| All other subjects | 3 |

### Copy Count Limit
- Maximum **3 copies** per edition
- Copy count applies to **OLDTX items only**
- Missing/lost copies are **not counted**
- On-loan copies **are counted** (they hold a copy slot)

### Location-Based Actions
| Item Location | Old Edition? | Action |
|---|---|---|
| OLDTX | Yes | → `Weed_Old_Edition` tab |
| OLDTX | No, but copy rank > 3 | → `Weed_Excess_Copy` tab |
| OLDTX | No, but missing/lost | → `Weed_Missing_Lost` tab |
| STACK / CLOSED / other | Yes | → `Needs_Review` tab (no automatic weed) |
| Any | Complies with policy | → `Keep` tab |

---

## Output Report Tabs

| Tab | Contents |
|---|---|
| **Summary** | Policy overview and item counts |
| **Weed_Old_Edition** | OLDTX items from editions beyond the keep limit |
| **Weed_Excess_Copy** | OLDTX excess copies of editions being kept |
| **Weed_Missing_Lost** | OLDTX items with Process Type = Lost/Missing/Lost and paid |
| **All_Weed** | Combined list of all OLDTX items to weed |
| **Needs_Review** | Non-OLDTX items (STACK, CLOSED, etc.) with old editions — review with staff |
| **Keep** | OLDTX items that comply with policy — no action needed |
| **No_Year_Found** | OLDTX items kept but pub year could not be detected — review manually |

---

## Notes

- The `Needs_Review` tab exists because STACK/CLOSED items on reserves came in via the
  Temporary Location = RESE filter. They are included for edition policy comparison but
  should not be automatically weeded — discuss with staff.
- Items with `Unknown` or blank call numbers will appear in `No_Year_Found`.
- The script never modifies Alma. All output is read-only.
