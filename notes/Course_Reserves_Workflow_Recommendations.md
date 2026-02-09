# Course Reserves Workflow Improvement Recommendations

**Prepared for:** Library Technical Services
**System:** Ex Libris Alma
**Date:** February 2, 2026

---

## Executive Summary

This document provides recommendations for modernizing and automating your library's Course Reserves workflow in Alma. Based on current best practices and available technologies, this plan leverages Alma's native capabilities, APIs, and custom automation to create a more efficient, cohesive system.

---

## Current Workflow Analysis

### Identified Pain Points
1. Manual data transformation in Excel
2. Time-consuming title searches and purchasing workflows
3. Manual course information and citation list updates
4. Lack of systematic alerts for items to remove from reserves
5. No centralized historical repository for course materials

---

## Recommendations

### 1. Data Transformation: Python/R Scripts

#### Recommendation: Python (Primary) with R as Secondary Option

**Python Advantages:**
- **almapipy** library specifically designed for Alma API integration
- Strong Excel/CSV processing with pandas library
- Better REST API support and JSON handling
- Larger library automation community

**R Considerations:**
- Excellent for statistical analysis and reporting
- Good CSV/Excel processing with readr and writexl packages
- Limited Alma-specific libraries found in research
- Better suited for Analytics reporting than API automation

#### Implementation Plan:

**Phase 1: Core Data Transformation Scripts**
```python
# Recommended Python libraries:
- pandas: Excel/CSV data manipulation
- almapipy: Alma API wrapper
- openpyxl: Excel file handling
- requests: API calls
```

**Suggested Scripts:**
1. **ISBN Normalization Script**: Standardize ISBN formats (ISBN-10 to ISBN-13, remove hyphens)
2. **Citation Data Transformer**: Convert instructor spreadsheets to Alma-ready format
3. **Course Data Validator**: Check for required fields before upload
4. **Batch Import Formatter**: Prepare data for Alma's course loader

**Best Practice from Research:**
- Alma supports batch course imports via course loader files (CARLI documentation)
- Courses should include start/end dates for automatic activation/deactivation
- Use standardized data formats to reduce manual Excel manipulation

---

### 2. ISBN Availability Search Tool

#### Recommended Solution: Python-based Search Utility

**Architecture:**
```
Input (Excel/CSV with ISBNs)
    → Python Script using almapipy
    → Alma Bibs API + SRU Search
    → Output Report (Excel) with availability status
```

**Key Features:**
1. **Batch ISBN Search**: Process lists of 100+ ISBNs automatically
2. **Availability Check**: Query physical and electronic holdings
3. **Staff Report Generation**:
   - Found/Not Found status
   - Current location and availability
   - Number of copies available
   - Electronic access links
   - Purchase recommendations for missing items

**Technical Implementation:**

**Search Method:**
- Use Alma's SRU (Search/Retrieve via URL) for ISBN searches
- Fallback to Alma Bibs API for detailed holdings information
- Query format: `alma.isbn=9781234567890`

**API Endpoints Needed:**
- `/almaws/v1/bibs` - Bibliographic records search
- SRU endpoint for title/ISBN searches
- `/almaws/v1/bibs/{mms_id}/holdings` - Holdings information

**Output Report Columns:**
- ISBN
- Title (if found)
- MMS ID (Alma record ID)
- Physical copies available
- Location(s)
- Electronic access (Yes/No/Link)
- Status (Available/In Use/Not Found)
- Recommendation (Purchase/Already Available/Request)

**Best Practice:**
- Search for "Physical Items" specifically to avoid retrieving all items on a bib record (Midlands Technical College guide)
- Run searches during off-peak hours for large batches

---

### 3. Automated Course Information & Citation List Updates

#### Recommended Solution: Python API Integration Tool

**Core Functionality:**

**A. Course Information Updates**
```python
# Using Alma Courses API
- Create new courses from registrar data
- Update existing course information
- Modify instructor assignments
- Adjust enrollment numbers and dates
```

**B. Citation List Management**
```python
# Using Reading Lists API
- Create/update reading lists
- Add/remove citations
- Link citations to bibliographic records
- Update copyright information
```

**API Endpoints:**
- `POST/PUT /almaws/v1/courses` - Course management
- `POST/PUT /almaws/v1/courses/{course_id}/reading-lists` - Reading list management
- `POST/PUT /almaws/v1/courses/{course_id}/reading-lists/{reading_list_id}/citations` - Citation management

**Automation Workflow:**
1. **Input**: Receive registrar file (CSV/XML) with course updates
2. **Validation**: Check for required fields and data quality
3. **Matching**: Match courses to existing Alma course records
4. **Update**: Push changes via API
5. **Report**: Generate success/error log for staff review

**Integration with Learning Management System (LMS):**
- Alma supports LTI integration with Canvas, Blackboard, Moodle
- Consider direct LMS-to-Alma integration for real-time course sync
- Reduces manual data entry significantly

**Best Practice:**
- Set reading list "Due Back Date" at least 14 days after final exams (CARLI best practices)
- Do not suppress items from discovery
- Use course start/end dates to trigger automatic activation/deactivation

---

### 4. Alert System for Items to Remove from Reserves

#### Recommended Solution: Alma Analytics + Python Alert System

**Approach A: Leverage Alma's Native Automation**

Alma automatically deactivates courses and reading lists based on end dates. Configure:
- Course end dates 2 weeks after semester end
- Automatic status changes when dates pass
- Staff notifications through Alma alerts

**Approach B: Custom Analytics-Based Alert System**

**Architecture:**
```
Alma Analytics Report
    → Scheduled Export (CSV)
    → Python Alert Script
    → Email notifications to staff
```

**Analytics Report Components:**
- Course end dates
- Reading list status
- Item locations (reserves vs. regular stacks)
- Last circulation date
- Current course term

**Alert Triggers:**
1. **End of Semester**: 2 weeks after course end date
2. **Inactive Items**: No circulation in 90+ days while on reserves
3. **Expired Courses**: Reading lists still active past end date
4. **Historical Processing**: Items ready for archival

**Staff Alert Categories:**
- **Immediate Action**: Remove from reserves (within 1 week)
- **Review Needed**: Low-circulation items (faculty may want to continue)
- **Historical Archive**: Items ready for historical repository

**Implementation:**
```python
# Python script scheduled weekly via cron/Task Scheduler
1. Fetch Alma Analytics report via API
2. Parse and analyze data
3. Generate categorized alert lists
4. Send email notifications to appropriate staff
5. Log actions for tracking
```

**Best Practice:**
- Don't delete courses entirely - this removes them from Analytics
- Archive reading lists for retention in Analytics (Ex Libris recommendation)
- Maintain audit trail of removed items

---

### 5. Historical Repository of Course Materials

#### Recommended Solution: Lightweight Database + Search Interface

**Architecture:**

**Backend:**
- SQLite database (simple, file-based, no server needed)
- Python scripts for data ingestion
- Automated nightly sync from Alma Analytics

**Data Model:**
```sql
Tables:
- courses (course_id, code, title, instructor, semester, year)
- reading_lists (list_id, course_id, list_name, date_created)
- citations (citation_id, list_id, title, author, isbn, format)
- items (item_id, citation_id, barcode, call_number, location)
- usage_stats (stat_id, item_id, checkouts, last_checkout_date)
```

**Frontend Options:**

**Option 1: Simple Web Interface** (Recommended for beginners)
- Flask (Python web framework) - lightweight and easy to learn
- Basic HTML forms for search
- Bootstrap CSS for clean appearance
- Can run on local server or cloud

**Option 2: Excel/Access Alternative** (Quick Start)
- Microsoft Access database with search forms
- Excel with pivot tables and slicers
- Lower learning curve, but less scalable

**Option 3: Advanced Solution** (Future Enhancement)
- Full web application with React/Vue.js frontend
- PostgreSQL database for better performance
- Institutional repository integration (DSpace, Fedora)

**Search Capabilities:**
- Course code, title, instructor
- ISBN, title, author
- Semester/year range
- Department or subject area
- Full-text search across all fields

**Data Ingestion Process:**
```python
# Automated nightly script
1. Export Course Reserves data from Alma Analytics
2. Transform data to match repository schema
3. Insert/update records in historical database
4. Generate monthly usage statistics
5. Create backup of database
```

**Historical Data Retention:**
- Minimum 7 years (recommended for accreditation)
- Course syllabi and reading lists (PDF storage)
- Circulation statistics
- Instructor notes and historical context

**Best Practice - Digital Preservation:**
Following Harvard and Duke Libraries' approaches:
- Regular backups (daily incremental, weekly full)
- Format migration planning (ensure long-term accessibility)
- Metadata standards (Dublin Core for course materials)
- Documentation of data structures and processes

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-2)
**Priority: High Impact, Lower Complexity**

1. **Set up Python development environment**
   - Install Python 3.9+, pandas, almapipy
   - Obtain Alma API keys (production and sandbox)
   - Create GitHub repository for version control

2. **Develop ISBN Search Tool** ⭐ Quick Win
   - Build basic search script
   - Test with sample ISBN list
   - Create Excel output template
   - Train staff on usage

3. **Create Data Transformation Scripts**
   - ISBN normalization
   - Citation data formatter
   - Course data validator

**Deliverables:** Working ISBN search tool, reusable transformation scripts

---

### Phase 2: Automation (Months 3-4)
**Priority: Core Automation**

1. **Develop Course Update Utility**
   - Build API integration for course updates
   - Create citation list management tool
   - Implement error handling and logging
   - Test with sandbox environment

2. **Configure Alma Analytics Reports**
   - Build course status report
   - Create items-to-remove report
   - Set up scheduled exports

3. **Implement Alert System**
   - Develop Python alert script
   - Configure email notifications
   - Schedule automated runs

**Deliverables:** Automated course updates, staff alert system

---

### Phase 3: Historical Repository (Months 5-6)
**Priority: Long-term Infrastructure**

1. **Design Database Schema**
   - Map Alma data to repository structure
   - Plan for future expansion
   - Document relationships

2. **Build Data Ingestion Pipeline**
   - Extract data from Analytics
   - Transform and load to repository
   - Implement error checking

3. **Create Search Interface**
   - Basic web interface (Flask)
   - Search functionality
   - Results display

**Deliverables:** Searchable historical repository, automated data sync

---

### Phase 4: Refinement (Ongoing)
**Priority: Optimization**

1. **Staff Training**
   - Tool documentation
   - Workflow procedures
   - Troubleshooting guides

2. **Performance Optimization**
   - Script efficiency improvements
   - Error handling refinement
   - User interface enhancements

3. **Integration Testing**
   - End-to-end workflow testing
   - Staff feedback incorporation
   - Process documentation

---

## Technical Requirements

### Software & Tools
- **Python 3.9+** (free, cross-platform)
- **Python Libraries:**
  - almapipy (Alma API wrapper)
  - pandas (data manipulation)
  - requests (HTTP/API calls)
  - openpyxl (Excel handling)
  - flask (web interface, optional)
  - sqlite3 (built-in with Python)
  - smtplib (email alerts, built-in)

### Alma Configuration
- **API Keys** (read/write permissions for):
  - Bibs
  - Courses
  - Analytics
- **Analytics Reports** configured and scheduled
- **Course Loader** template configured

### Infrastructure
- **Development Environment**: Any computer (Windows/Mac/Linux)
- **Production Server** (optional):
  - For web interface hosting
  - Can use institution's existing servers
  - Cloud alternatives: AWS, Azure, Google Cloud (free tiers available)

### Staff Skills Needed
- Basic Python programming (or willingness to learn)
- Excel/CSV data handling
- Alma functional knowledge
- API concepts (training available)

---

## Cost Analysis

### Software Costs
- **$0** - All recommended software is free/open-source
- **$0** - Alma API access (included with Alma subscription)
- **$0** - Python and all libraries (free)

### Time Investment
- **Initial Development**: 200-300 hours (can be spread over 6 months)
- **Ongoing Maintenance**: 2-5 hours/week
- **Staff Training**: 10-20 hours total

### Potential Savings
- **Estimated Time Saved Per Semester:**
  - Data transformation: 20 hours → 2 hours (90% reduction)
  - ISBN searching: 15 hours → 1 hour (93% reduction)
  - Course updates: 30 hours → 5 hours (83% reduction)
  - Item removal tracking: 10 hours → 1 hour (90% reduction)
  - **Total: 75 hours saved per semester = 150 hours/year**

---

## Risk Mitigation

### Technical Risks
| Risk | Mitigation Strategy |
|------|-------------------|
| API changes breaking scripts | Version control, regular testing, sandbox testing |
| Data quality issues | Validation scripts, error logging, staff review checkpoints |
| System downtime | Graceful error handling, retry logic, offline mode |
| Learning curve | Comprehensive documentation, training sessions, peer support |

### Operational Risks
| Risk | Mitigation Strategy |
|------|-------------------|
| Staff resistance to new tools | Early involvement, phased rollout, demonstrate time savings |
| Maintenance burden | Document code, create runbooks, build staff expertise |
| Over-automation | Maintain staff review checkpoints for critical decisions |

---

## Success Metrics

### Quantitative Measures
- **Time Savings**: Hours saved per semester (target: 60% reduction)
- **Error Reduction**: Fewer data entry errors (target: 80% reduction)
- **Processing Speed**: Faster course setup (target: 3 days → 1 day)
- **Search Efficiency**: ISBN searches (target: 100 ISBNs in 5 minutes)

### Qualitative Measures
- Staff satisfaction with new tools
- Faculty feedback on course reserves experience
- Data quality improvements
- Confidence in historical data accessibility

---

## Next Steps

### Immediate Actions (This Week)
1. ✅ **Review this document** with technical services leadership
2. ✅ **Obtain Alma API keys** from Ex Libris
3. ✅ **Identify pilot course** for testing (low-risk, upcoming semester)
4. ✅ **Designate project lead** and development team

### Short-term (Next Month)
1. **Set up development environment**
2. **Start with ISBN search tool** (quick win to demonstrate value)
3. **Schedule training** on Python basics if needed
4. **Document current workflow** in detail for baseline comparison

### Medium-term (Months 2-3)
1. **Pilot test** ISBN search tool with real data
2. **Begin Phase 2** automation development
3. **Regular check-ins** with stakeholders
4. **Iterate based on feedback**

---

## Additional Resources

### Alma Documentation
- [Course Reserves Overview - Ex Libris Knowledge Center](https://knowledge.exlibrisgroup.com/Alma/Product_Materials/050Alma_FAQs/Fulfillment/Course_Reserves)
- [Alma Courses API Documentation](https://developers.exlibrisgroup.com/alma/apis/courses/)
- [Alma Analytics Course Reserves Reports](https://knowledge.exlibrisgroup.com/Alma/Product_Documentation/010Alma_Online_Help_(English)/080Analytics/Alma_Analytics_Subject_Areas/Course_Reserves)

### Technical Resources
- [almapipy GitHub Repository](https://github.com/UCDavisLibrary/almapipy) - Python wrapper for Alma API
- [Code4Lib: Working with Alma APIs using Postman](https://journal.code4lib.org/articles/16597) - API tutorial
- [CARLI: How To - Course Reserves in Alma](https://www.carli.illinois.edu/products-services/i-share/alma-fulfillment/how-to_reserves) - Best practices guide

### Institutional Examples
- [Harvard Libraries: Course Reserves Processing](https://harvardwiki.atlassian.net/wiki/spaces/LibraryStaffDoc/pages/43362276/Processing+Course+Reserves+Requests) - Workflow documentation
- [Alliance PCSG: Primo Course Reserves Module](https://github.com/alliance-pcsg/primo-explore-course-reserves) - Example implementation

### Learning Resources
- **Python for Libraries**: Programming for librarians courses
- **Alma API Training**: Ex Libris Developer Network tutorials
- **Digital Preservation**: [Harvard Digital Preservation](https://preservation.library.harvard.edu/digital-preservation) and [Duke Digital Preservation Guide](https://library.duke.edu/using/policies/digital-preservation-guide)

---

## Conclusion

This comprehensive approach addresses all identified workflow pain points while building on Alma's existing capabilities. The phased implementation allows for:

✅ **Quick wins** (ISBN search tool in Month 1-2)
✅ **Progressive automation** (reducing manual work incrementally)
✅ **Sustainable maintenance** (documented, version-controlled code)
✅ **Future scalability** (extensible architecture)
✅ **Staff empowerment** (building internal technical expertise)

By leveraging Python's strong library ecosystem, Alma's robust APIs, and following digital preservation best practices, your library can create a modern, efficient Course Reserves workflow that significantly reduces manual effort while improving data quality and historical recordkeeping.

The estimated 150+ hours saved annually can be redirected to higher-value activities like collection development, faculty consultations, and enhanced student support services.

---

**Questions or need clarification on any recommendations? I'm happy to discuss implementation details or provide code examples for specific components.**
