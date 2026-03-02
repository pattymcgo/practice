# How to Share HTML Reports with Colleagues

## ✅ Reports Generated

Two interactive HTML reports have been created in the `reports/` folder:

1. **Course Reserves Report** - Overview of all course reserves data
2. **Primo Results Report** - Library catalog search results and purchase needs

## 📧 Sharing Methods

### Method 1: Email (Recommended)
1. Open your email client
2. Attach the HTML files from: `/Reserves Tool/reports/`
3. Send to colleagues
4. Recipients simply **double-click** the HTML file to open in their browser

**Pros:**
- ✓ No installation needed
- ✓ Works on any device (PC, Mac, tablet, phone)
- ✓ Interactive charts included
- ✓ Recipients can save for later

**Email Template:**
```
Subject: Course Reserves Analysis Reports

Hi Team,

Attached are interactive reports for our course reserves data:

1. course_reserves_report.html - Overview of all courses, enrollment, and textbooks
2. primo_results_report.html - Library catalog availability and purchase needs

Simply double-click the file to open in your browser. The charts are interactive -
hover for details and click legend items to filter.

Key Findings:
- [Add your insights here]

Best,
[Your name]
```

---

### Method 2: Google Drive / OneDrive / Dropbox
1. Upload HTML files to your cloud storage
2. Share the link with colleagues
3. Colleagues download and open in browser

**Note:** Some cloud services show HTML source code instead of rendering. If this happens, colleagues should download first, then open.

---

### Method 3: Network Share / SharePoint
1. Copy HTML files to your shared network drive
2. Notify colleagues of the location
3. They can open directly from the network drive

---

### Method 4: Slack / Teams
1. Upload HTML files to your channel
2. Colleagues download and open
3. Add context message with key insights

---

## 🔄 Regenerating Reports

When you have new data, regenerate reports:

```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"
python generate_html_reports.py
```

This creates new timestamped reports with your latest data.

---

## 📊 What's Included in the Reports

### Course Reserves Report:
- ✓ Top 15 courses by enrollment
- ✓ Books per course distribution
- ✓ Department enrollment comparison
- ✓ Books vs enrollment analysis
- ✓ Enrollment distribution histogram
- ✓ Textbook sharing opportunities
- ✓ Key summary statistics

### Primo Results Report:
- ✓ Search results status (Found/Not Found)
- ✓ Recommendations breakdown
- ✓ Purchase needs by department
- ✓ Physical vs Electronic availability
- ✓ Edition match analysis
- ✓ Top courses needing purchases
- ✓ Budget impact estimates

---

## 💡 Tips for Presenting

**In Meetings:**
- Share screen and walk through the HTML report
- Click on chart elements to demonstrate interactivity
- Use hover details to show specific data points

**For Budget Requests:**
- Use Primo Results Report
- Focus on "Purchase Needed" section
- Export key charts as screenshots if needed

**For Faculty:**
- Use Course Reserves Report
- Show department-specific views
- Highlight textbook sharing opportunities

---

## 🎯 Report Locations

**Current Reports:**
```
/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/
├── course_reserves_report_20260302_151737.html
└── primo_results_report_20260302_151737.html
```

**To open a report:**
- Double-click the .html file
- Or right-click → Open With → Your Browser

---

## ❓ Troubleshooting

**Q: The HTML file shows code instead of charts**
A: Download the file first, then open it (don't try to view in cloud storage)

**Q: Charts don't appear**
A: Make sure you have internet connection (charts use CDN for Plotly library)

**Q: Can I edit the reports?**
A: Yes! Open in a text editor to customize colors, add notes, etc.

**Q: How do I get a PDF version?**
A: Open HTML in browser → Print → Save as PDF

---

## 📅 Regular Reporting Schedule

**Suggested workflow:**
1. Run Primo search weekly/monthly
2. Generate HTML reports after each search
3. Email to stakeholders
4. Archive previous reports for comparison

**File naming includes timestamps** so you can track changes over time.

---

**Created:** March 2, 2026
**Report Files:** Interactive HTML with embedded Plotly charts
**No Software Required:** Opens in any modern browser
