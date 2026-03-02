"""
Generate Shareable HTML Reports from Dashboard Data
Creates standalone HTML files with interactive charts that can be shared via email/network
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
import glob

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = Path('/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data')
REPORTS_DIR = Path('/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports')
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================

def load_course_data():
    """Load course reserves consolidated data"""
    try:
        df = pd.read_excel(DATA_DIR / 'Spring2026_BOOKS_consolidated.xlsx')
    except FileNotFoundError:
        df = pd.read_excel(DATA_DIR / 'full_dataset_BOOKS_consolidated.xlsx')

    # Add Department column
    df['Department'] = df['Course'].str.extract(r'^([A-Z]+)')[0]

    # Group by course to count books
    df_courses = df.groupby('Course').agg({
        'Title': 'count',
        'Section': 'first',
        'Instructor_Name': 'first',
        'Total_Enrollment': 'first',
        'Course_Description': 'first',
        'Department': 'first'
    }).reset_index()

    df_courses.rename(columns={'Title': 'Num_Books'}, inplace=True)

    return df, df_courses

def load_primo_results():
    """Load most recent Primo ISBN search results"""
    primo_files = list(DATA_DIR.glob('*primo_results_*.xlsx'))

    if not primo_files:
        return None, None

    latest_file = max(primo_files, key=lambda p: p.stat().st_mtime)
    df = pd.read_excel(latest_file)
    df['Department'] = df['Course'].str.extract(r'^([A-Z]+)')[0]

    return df, latest_file.name

# ============================================================================
# GENERATE COURSE RESERVES REPORT
# ============================================================================

def create_course_reserves_report(df_raw, df_courses):
    """Create HTML report for Course Reserves data"""

    print("Creating Course Reserves HTML Report...")

    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Top 15 Courses by Enrollment',
            'Books per Course Distribution',
            'Department Enrollment Comparison',
            'Books vs Enrollment by Department',
            'Enrollment Distribution',
            'Textbook Sharing Opportunities'
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "scatter"}],
            [{"type": "histogram"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Top courses by enrollment
    top_courses = df_courses.nlargest(15, 'Total_Enrollment')
    fig.add_trace(
        go.Bar(
            y=top_courses['Course'],
            x=top_courses['Total_Enrollment'],
            orientation='h',
            marker_color='#1f77b4',
            name='Enrollment',
            text=top_courses['Total_Enrollment'],
            textposition='outside',
            showlegend=False
        ),
        row=1, col=1
    )

    # 2. Books per course distribution
    books_dist = df_courses['Num_Books'].value_counts().sort_index()
    fig.add_trace(
        go.Bar(
            x=books_dist.index,
            y=books_dist.values,
            marker_color='#ff7f0e',
            name='Courses',
            text=books_dist.values,
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. Department enrollment
    dept_summary = df_courses.groupby('Department').agg({
        'Total_Enrollment': 'sum',
        'Num_Books': 'sum'
    }).reset_index().sort_values('Total_Enrollment', ascending=True).tail(15)

    fig.add_trace(
        go.Bar(
            y=dept_summary['Department'],
            x=dept_summary['Total_Enrollment'],
            orientation='h',
            marker_color='#2ca02c',
            name='Students',
            text=dept_summary['Total_Enrollment'],
            textposition='outside',
            showlegend=False
        ),
        row=2, col=1
    )

    # 4. Books vs Enrollment by department
    fig.add_trace(
        go.Scatter(
            x=dept_summary['Num_Books'],
            y=dept_summary['Total_Enrollment'],
            mode='markers+text',
            marker=dict(size=12, color='#d62728'),
            text=dept_summary['Department'],
            textposition='top center',
            name='Departments',
            showlegend=False
        ),
        row=2, col=2
    )

    # 5. Enrollment distribution
    fig.add_trace(
        go.Histogram(
            x=df_courses['Total_Enrollment'],
            nbinsx=20,
            marker_color='#9467bd',
            name='Courses',
            showlegend=False
        ),
        row=3, col=1
    )

    # 6. Textbook sharing
    title_usage = df_raw.groupby('Title').size().reset_index(name='Num_Courses')
    sharing_dist = title_usage['Num_Courses'].value_counts().sort_index()

    fig.add_trace(
        go.Bar(
            x=sharing_dist.index,
            y=sharing_dist.values,
            marker_color='#8c564b',
            name='Books',
            text=sharing_dist.values,
            textposition='outside',
            showlegend=False
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        height=1400,
        title_text="<b>Course Reserves Dashboard - Overview Report</b>",
        title_x=0.5,
        title_font_size=24,
        showlegend=False
    )

    # Update axes labels
    fig.update_xaxes(title_text="Student Enrollment", row=1, col=1)
    fig.update_xaxes(title_text="Number of Books", row=1, col=2)
    fig.update_xaxes(title_text="Total Students", row=2, col=1)
    fig.update_xaxes(title_text="Total Books", row=2, col=2)
    fig.update_xaxes(title_text="Enrollment", row=3, col=1)
    fig.update_xaxes(title_text="Courses Sharing Book", row=3, col=2)

    fig.update_yaxes(title_text="Course", row=1, col=1)
    fig.update_yaxes(title_text="Number of Courses", row=1, col=2)
    fig.update_yaxes(title_text="Department", row=2, col=1)
    fig.update_yaxes(title_text="Students", row=2, col=2)
    fig.update_yaxes(title_text="Number of Courses", row=3, col=1)
    fig.update_yaxes(title_text="Number of Books", row=3, col=2)

    # Generate summary statistics HTML
    total_courses = len(df_courses)
    total_students = df_courses['Total_Enrollment'].sum()
    total_books = df_courses['Num_Books'].sum()
    avg_books_per_course = df_courses['Num_Books'].mean()
    unique_depts = df_courses['Department'].nunique()

    summary_html = f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: #1f77b4; text-align: center;">📊 Summary Statistics</h2>
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 20px; text-align: center;">
            <div>
                <h3 style="color: #555; margin: 5px;">Total Courses</h3>
                <p style="font-size: 28px; font-weight: bold; color: #1f77b4; margin: 5px;">{total_courses:,}</p>
            </div>
            <div>
                <h3 style="color: #555; margin: 5px;">Total Students</h3>
                <p style="font-size: 28px; font-weight: bold; color: #2ca02c; margin: 5px;">{total_students:,}</p>
            </div>
            <div>
                <h3 style="color: #555; margin: 5px;">Total Books</h3>
                <p style="font-size: 28px; font-weight: bold; color: #ff7f0e; margin: 5px;">{total_books:,}</p>
            </div>
            <div>
                <h3 style="color: #555; margin: 5px;">Avg Books/Course</h3>
                <p style="font-size: 28px; font-weight: bold; color: #d62728; margin: 5px;">{avg_books_per_course:.1f}</p>
            </div>
            <div>
                <h3 style="color: #555; margin: 5px;">Departments</h3>
                <p style="font-size: 28px; font-weight: bold; color: #9467bd; margin: 5px;">{unique_depts}</p>
            </div>
        </div>
    </div>
    """

    # Combine HTML
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_html = f"""
    <html>
    <head>
        <title>Course Reserves Report - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: white; }}
            h1 {{ color: #1f77b4; text-align: center; }}
            .info {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>📚 Course Reserves Analysis Report</h1>
        <div class="info">
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Data Source:</strong> Course Reserves Consolidated Dataset</p>
        </div>
        {summary_html}
        {fig.to_html(include_plotlyjs='cdn', div_id='course-charts')}
        <hr style="margin: 40px 0;">
        <p style="text-align: center; color: #666;">
            <em>This is an interactive report. Hover over charts for details, click legend items to show/hide data.</em>
        </p>
    </body>
    </html>
    """

    # Save HTML
    output_file = REPORTS_DIR / f'course_reserves_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    output_file.write_text(full_html)
    print(f"✓ Course Reserves Report saved: {output_file.name}")

    return output_file

# ============================================================================
# GENERATE PRIMO RESULTS REPORT
# ============================================================================

def create_primo_results_report(df, filename):
    """Create HTML report for Primo ISBN search results"""

    print("Creating Primo Results HTML Report...")

    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Search Results Status',
            'Recommendations Breakdown',
            'Purchase Needs by Department',
            'Physical vs Electronic Availability',
            'Edition Match Status',
            'Top Courses Needing Purchases'
        ),
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "pie"}, {"type": "bar"}]
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.15
    )

    # 1. Status breakdown pie chart
    status_counts = df['Status'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            marker=dict(colors=['#2ca02c', '#d62728', '#ff7f0e']),
            name='Status'
        ),
        row=1, col=1
    )

    # 2. Recommendations bar chart
    rec_counts = df['Recommendation'].value_counts().head(8)
    colors = ['#d62728' if 'Purchase' in rec else '#2ca02c' if 'Available' in rec else '#ff7f0e'
              for rec in rec_counts.index]

    fig.add_trace(
        go.Bar(
            y=rec_counts.index,
            x=rec_counts.values,
            orientation='h',
            marker_color=colors,
            text=rec_counts.values,
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. Purchase needs by department
    dept_purchase = df[df['Recommendation'].str.contains('Purchase', na=False)].groupby('Department').size().sort_values(ascending=True).tail(10)

    fig.add_trace(
        go.Bar(
            y=dept_purchase.index,
            x=dept_purchase.values,
            orientation='h',
            marker_color='#d62728',
            text=dept_purchase.values,
            textposition='outside',
            showlegend=False
        ),
        row=2, col=1
    )

    # 4. Physical vs Electronic
    format_data = pd.DataFrame({
        'Format': ['Physical', 'Electronic', 'Neither'],
        'Count': [
            len(df[df['Has_Physical'] == 'Yes']),
            len(df[df['Has_Electronic'] == 'Yes']),
            len(df[(df['Has_Physical'] == 'No') & (df['Has_Electronic'] == 'No')])
        ]
    })

    fig.add_trace(
        go.Bar(
            x=format_data['Format'],
            y=format_data['Count'],
            marker_color=['#1f77b4', '#ff7f0e', '#d62728'],
            text=format_data['Count'],
            textposition='outside',
            showlegend=False
        ),
        row=2, col=2
    )

    # 5. Edition match status
    edition_counts = df['Edition_Match'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=edition_counts.index,
            values=edition_counts.values,
            marker=dict(colors=['#2ca02c', '#d62728', '#ff7f0e', '#9467bd']),
            name='Edition'
        ),
        row=3, col=1
    )

    # 6. Top courses needing purchases
    course_purchase = df[df['Recommendation'].str.contains('Purchase', na=False)].groupby('Course').size().sort_values(ascending=True).tail(10)

    fig.add_trace(
        go.Bar(
            y=course_purchase.index,
            x=course_purchase.values,
            orientation='h',
            marker_color='#8c564b',
            text=course_purchase.values,
            textposition='outside',
            showlegend=False
        ),
        row=3, col=2
    )

    # Update layout
    fig.update_layout(
        height=1400,
        title_text="<b>Primo ISBN Search Results - Analysis Report</b>",
        title_x=0.5,
        title_font_size=24,
        showlegend=False
    )

    # Update axes
    fig.update_xaxes(title_text="Number of Books", row=1, col=2)
    fig.update_xaxes(title_text="Books Needing Purchase", row=2, col=1)
    fig.update_xaxes(title_text="Count", row=2, col=2)
    fig.update_xaxes(title_text="Books Needing Purchase", row=3, col=2)

    # Generate summary statistics
    total_isbns = len(df)
    found = len(df[df['Status'] == 'Found'])
    not_found = len(df[df['Status'] == 'Not Found'])
    purchase_needed = len(df[df['Recommendation'].str.contains('Purchase', na=False)])
    available = len(df[df['Recommendation'].str.contains('Available', na=False)])
    edition_mismatch = len(df[df['Edition_Match'] == 'Mismatch'])

    summary_html = f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h2 style="color: #1f77b4; text-align: center;">📖 Primo Search Summary</h2>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center; margin-bottom: 20px;">
            <div>
                <h3 style="color: #555; margin: 5px;">Total ISBNs</h3>
                <p style="font-size: 28px; font-weight: bold; color: #1f77b4; margin: 5px;">{total_isbns:,}</p>
            </div>
            <div>
                <h3 style="color: #555; margin: 5px;">Found in Primo</h3>
                <p style="font-size: 28px; font-weight: bold; color: #2ca02c; margin: 5px;">{found:,}</p>
                <p style="color: #666; margin: 5px;">({found/total_isbns*100:.1f}%)</p>
            </div>
            <div>
                <h3 style="color: #555; margin: 5px;">Not Found</h3>
                <p style="font-size: 28px; font-weight: bold; color: #d62728; margin: 5px;">{not_found:,}</p>
                <p style="color: #666; margin: 5px;">({not_found/total_isbns*100:.1f}%)</p>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center;">
            <div style="background-color: #ffebee; padding: 15px; border-radius: 5px;">
                <h3 style="color: #d62728; margin: 5px;">⚠️ Purchase Needed</h3>
                <p style="font-size: 32px; font-weight: bold; color: #d62728; margin: 5px;">{purchase_needed:,}</p>
            </div>
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px;">
                <h3 style="color: #2ca02c; margin: 5px;">✓ Already Available</h3>
                <p style="font-size: 32px; font-weight: bold; color: #2ca02c; margin: 5px;">{available:,}</p>
            </div>
            <div style="background-color: #fff3e0; padding: 15px; border-radius: 5px;">
                <h3 style="color: #ff7f0e; margin: 5px;">🔍 Edition Mismatch</h3>
                <p style="font-size: 32px; font-weight: bold; color: #ff7f0e; margin: 5px;">{edition_mismatch:,}</p>
            </div>
        </div>
    </div>
    """

    # Combine HTML
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_html = f"""
    <html>
    <head>
        <title>Primo Results Report - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: white; }}
            h1 {{ color: #1f77b4; text-align: center; }}
            .info {{ background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>📖 Primo ISBN Search Results Report</h1>
        <div class="info">
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Data Source:</strong> {filename}</p>
        </div>
        {summary_html}
        {fig.to_html(include_plotlyjs='cdn', div_id='primo-charts')}
        <hr style="margin: 40px 0;">
        <p style="text-align: center; color: #666;">
            <em>This is an interactive report. Hover over charts for details, click legend items to show/hide data.</em>
        </p>
    </body>
    </html>
    """

    # Save HTML
    output_file = REPORTS_DIR / f'primo_results_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    output_file.write_text(full_html)
    print(f"✓ Primo Results Report saved: {output_file.name}")

    return output_file

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("HTML REPORT GENERATOR")
    print("=" * 70)
    print()

    reports_created = []

    # Generate Course Reserves Report
    print("\n1. Loading course reserves data...")
    try:
        df_raw, df_courses = load_course_data()
        report_file = create_course_reserves_report(df_raw, df_courses)
        reports_created.append(report_file)
    except Exception as e:
        print(f"  ✗ Error creating course reserves report: {e}")

    # Generate Primo Results Report
    print("\n2. Loading Primo search results...")
    try:
        df_primo, primo_filename = load_primo_results()
        if df_primo is not None:
            report_file = create_primo_results_report(df_primo, primo_filename)
            reports_created.append(report_file)
        else:
            print("  ✗ No Primo results found. Run primo_isbn_search.py first.")
    except Exception as e:
        print(f"  ✗ Error creating Primo results report: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("REPORTS GENERATED")
    print("=" * 70)

    if reports_created:
        for report in reports_created:
            print(f"\n✓ {report.name}")
            print(f"  Location: {report}")
            print(f"  Share via: Email, Slack, Google Drive, etc.")
    else:
        print("\nNo reports were created.")

    print("\n" + "=" * 70)
    print("\nTo view reports: Double-click any .html file to open in your browser")
    print("To share: Email the .html files as attachments\n")

if __name__ == "__main__":
    main()
