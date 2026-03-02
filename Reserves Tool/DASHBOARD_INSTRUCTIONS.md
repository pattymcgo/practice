# Interactive Course Reserves Dashboard

## 🚀 Quick Start

### 1. Install Streamlit (one-time setup)
```bash
pip install streamlit plotly openpyxl
```

### 2. Run the Dashboard
```bash
cd "/Users/patty_home/Desktop/Agentic AI/Reserves Tool/scripts"
streamlit run course_reserves_dashboard.py
```

The dashboard will automatically open in your web browser at `http://localhost:8501`

---

## 📊 Dashboard Features

### **Interactive Filters** (Sidebar)
- Filter by Department
- Filter by Enrollment Range
- Filter by Minimum Books per Course
- See real-time filtered results count

### **5 Main Tabs:**

#### 1. 📈 Overview
- Top 15 courses by enrollment (interactive bar chart)
- Books vs Enrollment bubble chart (hover for details)
- Books per course distribution
- Enrollment distribution histogram

#### 2. 🏢 Departments
- Department enrollment bar chart
- Books distribution pie chart
- Sortable department comparison table with color gradients

#### 3. 👥 Instructors
- Top 20 instructors by course load
- Courses vs Students scatter plot
- Complete instructor workload table

#### 4. 📚 Textbooks
- Most used textbooks across courses
- Textbook sharing distribution
- Shared textbooks table (bulk purchase opportunities)

#### 5. 📋 Data Table
- Customizable column selection
- Search functionality
- Download filtered data as CSV
- Full data exploration

---

## 💡 Usage Tips

### **Exploring Data:**
1. Use sidebar filters to narrow down results
2. Hover over charts for detailed information
3. Click legend items to show/hide data series
4. Pan and zoom on charts by clicking and dragging

### **Finding Insights:**
- **Bulk Purchase**: Go to Textbooks tab → See shared textbooks
- **High Enrollment**: Overview tab → Top courses chart
- **Instructor Workload**: Instructors tab → Course load chart
- **Department Trends**: Departments tab → Compare metrics

### **Exporting Data:**
- Go to Data Table tab
- Apply filters and search
- Click "Download as CSV"

---

## 🎨 Screenshots

The dashboard includes:
- **Real-time filtering** - Changes update instantly
- **Interactive charts** - Zoom, pan, hover for details
- **Color-coded metrics** - Easy visual analysis
- **Responsive design** - Works on any screen size

---

## 🔧 Customization

Want to modify the dashboard? Edit these sections in `course_reserves_dashboard.py`:

- **Line 28**: Change data file path
- **Line 50+**: Modify filters
- **Line 120+**: Customize visualizations
- **Line 15-25**: Adjust styling/colors

---

## ⚠️ Troubleshooting

**Dashboard won't start?**
```bash
# Check if streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install --upgrade streamlit plotly
```

**Port already in use?**
```bash
# Run on different port
streamlit run course_reserves_dashboard.py --server.port 8502
```

**Data file not found?**
- Check that consolidated data exists in `/data/` folder
- Dashboard looks for: `Spring2026_BOOKS_consolidated.xlsx`
- Falls back to: `full_dataset_BOOKS_consolidated.xlsx`

---

## 📚 Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Plotly Docs**: https://plotly.com/python/
- **Your Data**: `/Reserves Tool/data/`

---

**Created:** March 2, 2026
**Version:** 1.0
