# Alma Course Loader - Manual Upload Guide

## ✅ File Created Successfully!

**File location:** `/Reserves Tool/projects/030226_test/alma_course_loader_20260302_160314.txt`

**Summary:**
- **14 courses** ready to upload
- **962 total students**
- **Format:** Tab-separated text file
- **Operation:** NEW (all courses)
- **Processing Department:** RESERVES

---

## 📤 How to Upload to Alma

### Method 1: Manual Upload (Recommended for Testing)

1. **Log into Alma**
   - Go to your Alma instance
   - Use your administrator credentials

2. **Navigate to Course Upload**
   ```
   Admin → Fulfillment Configuration → Courses → Actions → Upload Courses
   ```

   Alternative path:
   ```
   Configuration Menu → Fulfillment → Course Reserves → Upload Courses
   ```

3. **Select the File**
   - Click "Choose File" or "Browse"
   - Navigate to: `/Reserves Tool/projects/030226_test/`
   - Select: `alma_course_loader_20260302_160314.txt`

4. **Configure Upload Settings**
   - **File Format:** Tab-delimited
   - **Operation:** Create New Courses
   - **Processing Department:** RESERVES (or your library's department)

5. **Upload and Process**
   - Click "Upload" or "Submit"
   - Alma will validate the file
   - Review any error messages
   - Confirm the upload

6. **Verify**
   - Check that courses appear in Alma
   - Verify course details (dates, instructors, enrollment)
   - Check for any warnings or errors

---

### Method 2: FTP Upload (For Automated Processing)

If you have FTP access configured:

1. **Upload to FTP Server**
   - Connect to your Alma FTP server
   - Place file in the designated course loader directory
   - Ensure filename has proper timestamp

2. **Scheduled Processing**
   - Alma will automatically process the file
   - Check for processing logs
   - Review results in Alma interface

---

## 📋 File Format Details

**Key Features:**
- **Tab-separated** (NOT comma-separated)
- **UTF-8 encoding**
- **CRLF line endings**
- **First row:** Headers (automatically ignored by Alma)

**Required Fields (in order):**
1. Code (Course code)
2. Section (Section ID)
3. Operation (NEW, CHANGED, DELETED, ROLLOVER)
4. Name (Course title)
5. Processing Department
6. Start Date (YYYY-MM-DD)
7. End Date (YYYY-MM-DD)
8. Number of Participants (integer)
9. Instructor
10. Academic Department
11. Year (integer)
12. Term
13. Weekly Hours (integer)
14. All Instructors
15. Search ID (optional)

---

## 🔍 Troubleshooting

### Common Issues:

**"File format not recognized"**
- Ensure file is tab-separated (not comma-separated)
- Check that file extension is .txt
- Verify UTF-8 encoding

**"Missing required field"**
- Check that all required columns are present
- Ensure Processing Department is valid in your system
- Verify dates are in YYYY-MM-DD format

**"Duplicate course code"**
- Check for duplicate Course + Section combinations
- Only first instance will be processed
- Remove duplicates before upload

**"Invalid date format"**
- Dates must be: YYYY-MM-DD
- Example: 2026-01-26
- No other formats accepted

**"Processing department not found"**
- Update the department name to match your Alma configuration
- Contact your Alma administrator for valid department codes
- Regenerate file with correct department

---

## 🔄 Regenerating the File

To create a new file or change settings:

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"

# Basic usage
python create_alma_course_loader_file.py

# With custom input file
python create_alma_course_loader_file.py \
  --input ../data/Spring2027_BOOKS_consolidated.xlsx

# With custom processing department
python create_alma_course_loader_file.py \
  --processing-dept "TECHNICAL_SERVICES"

# With custom output location
python create_alma_course_loader_file.py \
  --output ~/Desktop/my_courses.txt
```

---

## 📊 What Gets Created in Alma

For each course, Alma will create:
- **Course record** with code, section, and details
- **Enrollment information**
- **Instructor assignments**
- **Date ranges** (auto-activate/deactivate)
- **Processing department** assignment

**Note:** This only creates the COURSE. Reading lists and citations must be added separately (either via API or manually).

---

## ⚙️ Next Steps After Upload

1. **Verify Courses Created**
   - Search for courses in Alma
   - Check enrollment numbers
   - Verify instructor names

2. **Add Reading Lists** (Optional)
   - Can be done manually in Alma
   - Or use Reading List Loader (separate file)
   - Or use API (when permissions are available)

3. **Add Citations/Textbooks** (Optional)
   - Manual entry through Alma interface
   - Or wait for API permissions
   - Or use citation loader file

4. **Configure Settings**
   - Set up email notifications
   - Configure student access
   - Adjust visibility settings

---

## 💡 Tips for Production Use

### For Full Semester Data:

When you're ready to upload ALL your courses (not just test data):

```bash
# Process full semester data first
python scripts/process_full_dataset.py \
  --input data/Fall2026_merged.xlsx \
  --semester "Fall2026"

# Generate Alma loader file
python scripts/create_alma_course_loader_file.py \
  --input data/Fall2026_BOOKS_consolidated.xlsx \
  --output data/Fall2026_alma_loader.txt \
  --processing-dept "RESERVES"
```

### Incremental Updates:

To UPDATE existing courses (not create new ones):

1. Change the **Operation** column to "CHANGED"
2. Include same Code + Section as existing course
3. Update only the fields that changed
4. Use "+" in a field to keep existing value

---

## 🎯 Benefits vs API Method

**Course Loader (No API) Advantages:**
- ✅ No API permissions needed
- ✅ Works immediately
- ✅ Familiar file format
- ✅ Easy to review before upload
- ✅ Manual control over each step

**API Method Advantages:**
- ✅ Also creates reading lists
- ✅ Also adds citations/textbooks
- ✅ Fully automated
- ✅ Better for large batches
- ✅ Can update existing courses easily

**Best Strategy:**
1. Use Course Loader NOW (test immediately)
2. Switch to API method when permissions arrive
3. Or use hybrid: Course Loader + manual citations

---

## 📚 Additional Resources

- [Alma Course Loading Documentation](https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_(English)/090Integrations_with_External_Systems/040Fulfillment/010Courses_and_Reading_Lists/Configuring_Course_Loading)
- [Managing Courses in Alma](https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_(English)/030Fulfillment/060Courses_and_Reading_Lists/020Managing_Courses)

---

**Created:** March 2, 2026
**Test File:** 14 courses, 962 students
**Ready for:** Manual upload to Alma
