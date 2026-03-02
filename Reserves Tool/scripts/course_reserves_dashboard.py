"""
Interactive Course Reserves Dashboard
Run with: streamlit run course_reserves_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Course Reserves Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def load_data():
    """Load and process course reserves data"""
    try:
        # Try Spring2026 file first
        df_raw = pd.read_excel('/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/Spring2026_BOOKS_consolidated.xlsx')
    except FileNotFoundError:
        # Fall back to full dataset
        df_raw = pd.read_excel('/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/full_dataset_BOOKS_consolidated.xlsx')

    # Group by course to count books and aggregate data
    # Each row in raw data is a course-textbook pair, so we need to count books per course
    df = df_raw.groupby('Course').agg({
        'Title': lambda x: ' | '.join(str(t) for t in x.head(3) if pd.notna(t)) if len(x) <= 3 else ' | '.join(str(t) for t in x.head(3) if pd.notna(t)) + f' (+{len(x)-3} more)',
        'Section': 'first',
        'Instructor_Name': 'first',
        'Total_Enrollment': 'first',
        'Course_Description': 'first',
        'ISBN': 'count'  # Count number of books
    }).reset_index()

    # Rename ISBN count column to Num_Books
    df.rename(columns={'ISBN': 'Num_Books'}, inplace=True)

    # Add derived columns
    df['Department'] = df['Course'].str.extract(r'^([A-Z]+)')[0]
    df['Num_Sections'] = df['Section'].str.count(',') + 1
    df['Num_Instructors'] = df['Instructor_Name'].str.count('/') + 1

    # Store the raw data for textbook analysis
    df_raw['Department'] = df_raw['Course'].str.extract(r'^([A-Z]+)')[0]

    return df, df_raw

# Load data
with st.spinner('Loading data...'):
    df, df_raw = load_data()

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<p class="main-header">📚 Course Reserves Dashboard</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.header("🔍 Filters")

# Department filter
departments = ['All'] + sorted(df['Department'].unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)

# Filter data
if selected_dept != 'All':
    filtered_df = df[df['Department'] == selected_dept]
else:
    filtered_df = df.copy()

# Enrollment range filter
min_enrollment = int(filtered_df['Total_Enrollment'].min())
max_enrollment = int(filtered_df['Total_Enrollment'].max())

enrollment_range = st.sidebar.slider(
    "Student Enrollment Range",
    min_value=min_enrollment,
    max_value=max_enrollment,
    value=(min_enrollment, max_enrollment)
)

filtered_df = filtered_df[
    (filtered_df['Total_Enrollment'] >= enrollment_range[0]) &
    (filtered_df['Total_Enrollment'] <= enrollment_range[1])
]

# Books per course filter
max_books = int(filtered_df['Num_Books'].max())
books_threshold = st.sidebar.slider(
    "Minimum Books per Course",
    min_value=1,
    max_value=max_books,
    value=1
)

filtered_df = filtered_df[filtered_df['Num_Books'] >= books_threshold]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Filtered Results:** {len(filtered_df)} courses")

# ============================================================================
# KEY METRICS
# ============================================================================

st.header("📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Courses", f"{len(filtered_df):,}")

with col2:
    st.metric("Total Students", f"{filtered_df['Total_Enrollment'].sum():,}")

with col3:
    st.metric("Unique Departments", f"{filtered_df['Department'].nunique()}")

with col4:
    st.metric("Avg Books/Course", f"{filtered_df['Num_Books'].mean():.1f}")

with col5:
    st.metric("Total Books", f"{filtered_df['Num_Books'].sum():,}")

st.markdown("---")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🏢 Departments",
    "👥 Instructors",
    "📚 Textbooks",
    "📋 Data Table"
])

# TAB 1: OVERVIEW
with tab1:
    st.header("Overview Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Top courses by enrollment
        st.subheader("Top 15 Courses by Enrollment")

        top_courses = filtered_df.nlargest(15, 'Total_Enrollment')

        fig1 = go.Figure(data=[
            go.Bar(
                y=top_courses['Course'],
                x=top_courses['Total_Enrollment'],
                orientation='h',
                marker=dict(
                    color=top_courses['Total_Enrollment'],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=top_courses['Total_Enrollment'],
                textposition='outside'
            )
        ])

        fig1.update_layout(
            xaxis_title="Student Enrollment",
            yaxis_title="Course",
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Books vs Enrollment scatter
        st.subheader("Books vs Enrollment (Bubble Chart)")

        fig2 = px.scatter(
            filtered_df,
            x='Num_Books',
            y='Total_Enrollment',
            size='Num_Sections',
            color='Department',
            hover_data=['Course', 'Instructor_Name'],
            title="",
            labels={
                'Num_Books': 'Number of Books',
                'Total_Enrollment': 'Student Enrollment',
                'Num_Sections': 'Sections'
            }
        )

        fig2.update_layout(height=500)

        st.plotly_chart(fig2, use_container_width=True)

    # Distribution charts
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Books per Course Distribution")

        books_dist = filtered_df['Num_Books'].value_counts().sort_index()

        fig3 = go.Figure(data=[
            go.Bar(
                x=books_dist.index,
                y=books_dist.values,
                marker_color='lightblue',
                text=books_dist.values,
                textposition='outside'
            )
        ])

        fig3.update_layout(
            xaxis_title="Number of Books",
            yaxis_title="Number of Courses",
            height=400
        )

        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Enrollment Distribution")

        fig4 = go.Figure(data=[
            go.Histogram(
                x=filtered_df['Total_Enrollment'],
                nbinsx=20,
                marker_color='coral'
            )
        ])

        fig4.update_layout(
            xaxis_title="Student Enrollment",
            yaxis_title="Number of Courses",
            height=400
        )

        st.plotly_chart(fig4, use_container_width=True)

# TAB 2: DEPARTMENTS
with tab2:
    st.header("Department Analysis")

    # Department summary
    dept_summary = filtered_df.groupby('Department').agg({
        'Total_Enrollment': 'sum',
        'Num_Books': 'sum',
        'Course': 'count'
    }).rename(columns={'Course': 'Num_Courses'}).reset_index()

    dept_summary = dept_summary.sort_values('Total_Enrollment', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Department Enrollment")

        fig5 = px.bar(
            dept_summary.head(15),
            x='Department',
            y='Total_Enrollment',
            color='Total_Enrollment',
            color_continuous_scale='Blues',
            title="Top 15 Departments by Student Enrollment"
        )

        fig5.update_layout(height=400)

        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Books by Department")

        fig6 = px.pie(
            dept_summary.head(10),
            values='Num_Books',
            names='Department',
            title="Top 10 Departments - Book Distribution"
        )

        fig6.update_layout(height=400)

        st.plotly_chart(fig6, use_container_width=True)

    # Department comparison table
    st.subheader("Department Comparison Table")

    dept_summary_display = dept_summary.copy()
    dept_summary_display.columns = ['Department', 'Total Students', 'Total Books', 'Number of Courses']

    st.dataframe(
        dept_summary_display.style.background_gradient(subset=['Total Students'], cmap='Blues'),
        use_container_width=True,
        height=400
    )

# TAB 3: INSTRUCTORS
with tab3:
    st.header("Instructor Analysis")

    # Parse instructors (they may be combined with /)
    instructor_data = []

    for idx, row in filtered_df.iterrows():
        instructors = str(row['Instructor_Name']).split(' / ')
        for instr in instructors:
            if instr and instr != 'nan':
                instructor_data.append({
                    'Instructor': instr.strip(),
                    'Course': row['Course'],
                    'Enrollment': row['Total_Enrollment'],
                    'Books': row['Num_Books']
                })

    instr_df = pd.DataFrame(instructor_data)

    if len(instr_df) > 0:
        # Top instructors
        instr_summary = instr_df.groupby('Instructor').agg({
            'Course': 'count',
            'Enrollment': 'sum',
            'Books': 'sum'
        }).reset_index()

        instr_summary.columns = ['Instructor', 'Num_Courses', 'Total_Students', 'Total_Books']
        instr_summary = instr_summary.sort_values('Num_Courses', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 20 Instructors by Course Load")

            fig7 = go.Figure(data=[
                go.Bar(
                    y=instr_summary.head(20)['Instructor'],
                    x=instr_summary.head(20)['Num_Courses'],
                    orientation='h',
                    marker_color='lightgreen',
                    text=instr_summary.head(20)['Num_Courses'],
                    textposition='outside'
                )
            ])

            fig7.update_layout(
                xaxis_title="Number of Courses",
                yaxis_title="Instructor",
                height=600,
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            st.subheader("Instructor Workload Metrics")

            # Scatter: courses vs students
            fig8 = px.scatter(
                instr_summary.head(30),
                x='Num_Courses',
                y='Total_Students',
                size='Total_Books',
                hover_data=['Instructor'],
                title="Courses vs Students (size = total books)"
            )

            fig8.update_layout(height=600)

            st.plotly_chart(fig8, use_container_width=True)

        # Instructor table
        st.subheader("Instructor Details")

        st.dataframe(
            instr_summary.style.background_gradient(subset=['Num_Courses'], cmap='Greens'),
            use_container_width=True,
            height=400
        )

# TAB 4: TEXTBOOKS
with tab4:
    st.header("Textbook Analysis")

    # Get filtered courses to use for textbook analysis
    filtered_courses = filtered_df['Course'].unique()
    filtered_raw = df_raw[df_raw['Course'].isin(filtered_courses)]

    # Textbook sharing
    title_usage = filtered_raw.groupby('Title').agg({
        'Course': lambda x: list(set(x)),  # Unique courses
        'Total_Enrollment': lambda x: filtered_df[filtered_df['Course'].isin(x)]['Total_Enrollment'].sum() if len(x) > 0 else 0,
        'Num_Editions': 'first'
    }).reset_index()

    title_usage['Num_Courses'] = title_usage['Course'].apply(len)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Most Used Textbooks")

        top_books = title_usage.sort_values('Num_Courses', ascending=False).head(15)

        fig9 = go.Figure(data=[
            go.Bar(
                x=top_books['Num_Courses'],
                y=top_books['Title'].str[:40],
                orientation='h',
                marker_color='purple',
                text=top_books['Num_Courses'],
                textposition='outside'
            )
        ])

        fig9.update_layout(
            xaxis_title="Number of Courses",
            yaxis_title="Textbook",
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        st.subheader("Textbook Sharing Distribution")

        sharing_dist = title_usage['Num_Courses'].value_counts().sort_index()

        fig10 = go.Figure(data=[
            go.Bar(
                x=sharing_dist.index,
                y=sharing_dist.values,
                marker_color='orange',
                text=sharing_dist.values,
                textposition='outside'
            )
        ])

        fig10.update_layout(
            xaxis_title="Courses Using Same Book",
            yaxis_title="Number of Textbooks",
            height=500
        )

        st.plotly_chart(fig10, use_container_width=True)

    # Shared textbooks table
    shared_books = title_usage[title_usage['Num_Courses'] > 1].sort_values('Num_Courses', ascending=False)

    if len(shared_books) > 0:
        st.subheader(f"Shared Textbooks ({len(shared_books)} books)")

        shared_display = shared_books[['Title', 'Num_Courses', 'Total_Enrollment']].copy()
        shared_display.columns = ['Textbook', 'Courses', 'Total Students']

        st.dataframe(
            shared_display.style.background_gradient(subset=['Courses'], cmap='Oranges'),
            use_container_width=True,
            height=400
        )

# TAB 5: DATA TABLE
with tab5:
    st.header("Raw Data Explorer")

    # Column selector
    all_columns = filtered_df.columns.tolist()
    default_columns = ['Course', 'Title', 'Instructor_Name', 'Total_Enrollment', 'Num_Books', 'Section']

    selected_columns = st.multiselect(
        "Select columns to display:",
        options=all_columns,
        default=[col for col in default_columns if col in all_columns]
    )

    if selected_columns:
        display_df = filtered_df[selected_columns].copy()

        # Search functionality
        search_term = st.text_input("🔍 Search in data:", "")

        if search_term:
            mask = display_df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            display_df = display_df[mask]

        st.dataframe(display_df, use_container_width=True, height=600)

        # Download button
        csv = display_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"course_reserves_filtered_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("**Course Reserves Dashboard** | Built with Streamlit | Data updates automatically from consolidated files")
