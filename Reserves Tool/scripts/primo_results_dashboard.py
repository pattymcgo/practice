"""
Primo ISBN Search Results Dashboard
Run with: streamlit run primo_results_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import glob

# Page configuration
st.set_page_config(
    page_title="Primo Search Results Dashboard",
    page_icon="📖",
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
    .purchase-needed {
        color: #d62728;
        font-weight: bold;
    }
    .available {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def load_primo_results():
    """Load Primo ISBN search results"""
    # Look for the most recent primo results file
    data_dir = Path('/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data')
    primo_files = list(data_dir.glob('*primo_results_*.xlsx'))

    if not primo_files:
        st.error("No Primo results files found! Please run primo_isbn_search.py first.")
        st.stop()

    # Get most recent file
    latest_file = max(primo_files, key=lambda p: p.stat().st_mtime)

    df = pd.read_excel(latest_file)

    # Add Department column from Course code
    df['Department'] = df['Course'].str.extract(r'^([A-Z]+)')[0]

    # Clean up recommendation text
    df['Recommendation_Clean'] = df['Recommendation'].fillna('Unknown')

    return df, latest_file.name

# Load data
with st.spinner('Loading Primo search results...'):
    df, filename = load_primo_results()

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<p class="main-header">📖 Primo ISBN Search Results</p>', unsafe_allow_html=True)
st.info(f"**Data source:** {filename}")
st.markdown("---")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.header("🔍 Filters")

# Department filter
departments = ['All'] + sorted(df['Department'].dropna().unique().tolist())
selected_dept = st.sidebar.selectbox("Department", departments)

# Filter data
if selected_dept != 'All':
    filtered_df = df[df['Department'] == selected_dept]
else:
    filtered_df = df.copy()

# Status filter
status_options = ['All'] + sorted(filtered_df['Status'].unique().tolist())
selected_status = st.sidebar.selectbox("Status", status_options)

if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['Status'] == selected_status]

# Recommendation filter
rec_options = ['All'] + sorted(filtered_df['Recommendation_Clean'].unique().tolist())
selected_rec = st.sidebar.selectbox("Recommendation", rec_options)

if selected_rec != 'All':
    filtered_df = filtered_df[filtered_df['Recommendation_Clean'] == selected_rec]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Filtered Results:** {len(filtered_df)} books")

# ============================================================================
# KEY METRICS
# ============================================================================

st.header("📊 Summary Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total ISBNs", f"{len(filtered_df):,}")

with col2:
    found_count = len(filtered_df[filtered_df['Status'] == 'Found'])
    st.metric("Found in Primo", f"{found_count:,}",
              delta=f"{found_count/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%")

with col3:
    not_found = len(filtered_df[filtered_df['Status'] == 'Not Found'])
    st.metric("Not Found", f"{not_found:,}",
              delta=f"{not_found/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%",
              delta_color="inverse")

with col4:
    purchase_needed = len(filtered_df[filtered_df['Recommendation_Clean'].str.contains('Purchase', na=False)])
    st.metric("Purchase Needed", f"{purchase_needed:,}",
              delta_color="inverse")

with col5:
    available = len(filtered_df[filtered_df['Recommendation_Clean'].str.contains('Available', na=False)])
    st.metric("Already Available", f"{available:,}")

st.markdown("---")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🏢 By Department",
    "✅ Availability",
    "📚 Edition Analysis",
    "📋 Data Table"
])

# TAB 1: OVERVIEW
with tab1:
    st.header("Overview Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Status breakdown
        st.subheader("Search Results Status")

        status_counts = filtered_df['Status'].value_counts()

        fig1 = go.Figure(data=[
            go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.4,
                marker=dict(colors=['#2ca02c', '#d62728', '#ff7f0e'])
            )
        ])

        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Recommendation breakdown
        st.subheader("Recommendations")

        rec_counts = filtered_df['Recommendation_Clean'].value_counts()

        colors = []
        for rec in rec_counts.index:
            if 'Purchase' in rec:
                colors.append('#d62728')  # Red
            elif 'Available' in rec:
                colors.append('#2ca02c')  # Green
            else:
                colors.append('#ff7f0e')  # Orange

        fig2 = go.Figure(data=[
            go.Bar(
                x=rec_counts.values,
                y=rec_counts.index,
                orientation='h',
                marker_color=colors,
                text=rec_counts.values,
                textposition='outside'
            )
        ])

        fig2.update_layout(
            xaxis_title="Number of Books",
            yaxis_title="Recommendation",
            height=400,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig2, use_container_width=True)

    # Format availability
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Physical vs Electronic")

        format_data = pd.DataFrame({
            'Format': ['Physical', 'Electronic', 'Neither'],
            'Count': [
                len(filtered_df[filtered_df['Has_Physical'] == 'Yes']),
                len(filtered_df[filtered_df['Has_Electronic'] == 'Yes']),
                len(filtered_df[(filtered_df['Has_Physical'] == 'No') & (filtered_df['Has_Electronic'] == 'No')])
            ]
        })

        fig3 = px.bar(
            format_data,
            x='Format',
            y='Count',
            color='Format',
            color_discrete_map={
                'Physical': '#1f77b4',
                'Electronic': '#ff7f0e',
                'Neither': '#d62728'
            },
            text='Count'
        )

        fig3.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Edition Match Status")

        edition_counts = filtered_df['Edition_Match'].value_counts()

        fig4 = go.Figure(data=[
            go.Pie(
                labels=edition_counts.index,
                values=edition_counts.values,
                marker=dict(colors=['#2ca02c', '#d62728', '#ff7f0e', '#9467bd'])
            )
        ])

        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

# TAB 2: BY DEPARTMENT
with tab2:
    st.header("Analysis by Department")

    # Department summary
    dept_summary = filtered_df.groupby('Department').agg({
        'ISBN_Clean': 'count',
        'Status': lambda x: (x == 'Found').sum(),
        'Recommendation_Clean': lambda x: x.str.contains('Purchase', na=False).sum()
    }).reset_index()

    dept_summary.columns = ['Department', 'Total_Books', 'Found_in_Primo', 'Purchase_Needed']
    dept_summary = dept_summary.sort_values('Purchase_Needed', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Purchase Needs by Department")

        fig5 = go.Figure(data=[
            go.Bar(
                y=dept_summary['Department'].head(15),
                x=dept_summary['Purchase_Needed'].head(15),
                orientation='h',
                marker=dict(
                    color=dept_summary['Purchase_Needed'].head(15),
                    colorscale='Reds',
                    showscale=True
                ),
                text=dept_summary['Purchase_Needed'].head(15),
                textposition='outside'
            )
        ])

        fig5.update_layout(
            xaxis_title="Books Needing Purchase",
            yaxis_title="Department",
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Found vs Not Found by Department")

        dept_status = filtered_df.groupby(['Department', 'Status']).size().unstack(fill_value=0).reset_index()

        fig6 = go.Figure()

        if 'Found' in dept_status.columns:
            fig6.add_trace(go.Bar(
                y=dept_status['Department'].head(15),
                x=dept_status['Found'].head(15),
                name='Found',
                orientation='h',
                marker_color='#2ca02c'
            ))

        if 'Not Found' in dept_status.columns:
            fig6.add_trace(go.Bar(
                y=dept_status['Department'].head(15),
                x=dept_status['Not Found'].head(15),
                name='Not Found',
                orientation='h',
                marker_color='#d62728'
            ))

        fig6.update_layout(
            xaxis_title="Number of Books",
            yaxis_title="Department",
            height=500,
            barmode='stack'
        )

        st.plotly_chart(fig6, use_container_width=True)

    # Department comparison table
    st.subheader("Department Summary Table")

    dept_display = dept_summary.copy()
    dept_display['Found_Rate'] = (dept_display['Found_in_Primo'] / dept_display['Total_Books'] * 100).round(1)

    st.dataframe(
        dept_display.style.background_gradient(subset=['Purchase_Needed'], cmap='Reds'),
        use_container_width=True,
        height=400
    )

# TAB 3: AVAILABILITY
with tab3:
    st.header("Availability Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Courses Needing Purchases")

        # Courses with most purchase needs
        course_purchase = filtered_df[
            filtered_df['Recommendation_Clean'].str.contains('Purchase', na=False)
        ].groupby('Course').size().sort_values(ascending=False).head(20)

        fig7 = go.Figure(data=[
            go.Bar(
                y=course_purchase.index,
                x=course_purchase.values,
                orientation='h',
                marker_color='#d62728',
                text=course_purchase.values,
                textposition='outside'
            )
        ])

        fig7.update_layout(
            xaxis_title="Books Needing Purchase",
            yaxis_title="Course",
            height=600,
            yaxis={'categoryorder': 'total ascending'}
        )

        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        st.subheader("Books with Wrong Editions")

        wrong_edition = filtered_df[filtered_df['Edition_Match'] == 'Mismatch']

        if len(wrong_edition) > 0:
            st.markdown(f"**{len(wrong_edition)} books** have edition mismatches")

            wrong_display = wrong_edition[['Course', 'Required_Title', 'Required_Edition', 'Found_Edition', 'Recommendation_Clean']].head(20)

            st.dataframe(
                wrong_display,
                use_container_width=True,
                height=550
            )
        else:
            st.success("No edition mismatches found! ✓")

        st.subheader("Purchase Priorities")

        # Books that need purchase with high enrollment
        purchase_priority = filtered_df[
            filtered_df['Recommendation_Clean'].str.contains('Purchase', na=False)
        ].nlargest(10, 'Total_Enrollment')[['Course', 'Required_Title', 'Total_Enrollment', 'Recommendation_Clean']]

        if len(purchase_priority) > 0:
            st.dataframe(
                purchase_priority.style.background_gradient(subset=['Total_Enrollment'], cmap='Reds'),
                use_container_width=True,
                height=350
            )

# TAB 4: EDITION ANALYSIS
with tab4:
    st.header("Edition Match Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Edition match by department
        st.subheader("Edition Matches by Department")

        edition_dept = filtered_df.groupby(['Department', 'Edition_Match']).size().unstack(fill_value=0).reset_index()

        fig8 = go.Figure()

        colors_map = {
            'Match': '#2ca02c',
            'Mismatch': '#d62728',
            'Verify Manually': '#ff7f0e',
            'N/A': '#9467bd'
        }

        for col in edition_dept.columns[1:]:
            if col in colors_map:
                fig8.add_trace(go.Bar(
                    y=edition_dept['Department'].head(15),
                    x=edition_dept[col].head(15),
                    name=col,
                    orientation='h',
                    marker_color=colors_map[col]
                ))

        fig8.update_layout(
            xaxis_title="Number of Books",
            yaxis_title="Department",
            height=500,
            barmode='stack'
        )

        st.plotly_chart(fig8, use_container_width=True)

    with col2:
        # Format breakdown
        st.subheader("Format Availability by Department")

        format_dept = filtered_df.groupby('Department').agg({
            'Has_Physical': lambda x: (x == 'Yes').sum(),
            'Has_Electronic': lambda x: (x == 'Yes').sum()
        }).reset_index().head(15)

        fig9 = go.Figure()

        fig9.add_trace(go.Bar(
            y=format_dept['Department'],
            x=format_dept['Has_Physical'],
            name='Physical',
            orientation='h',
            marker_color='#1f77b4'
        ))

        fig9.add_trace(go.Bar(
            y=format_dept['Department'],
            x=format_dept['Has_Electronic'],
            name='Electronic',
            orientation='h',
            marker_color='#ff7f0e'
        ))

        fig9.update_layout(
            xaxis_title="Number of Books",
            yaxis_title="Department",
            height=500,
            barmode='group'
        )

        st.plotly_chart(fig9, use_container_width=True)

    # Detailed edition table
    st.subheader("Books Requiring Manual Verification")

    verify_books = filtered_df[filtered_df['Edition_Match'] == 'Verify Manually']

    if len(verify_books) > 0:
        verify_display = verify_books[[
            'Course', 'Required_Title', 'Required_Edition',
            'Found_Edition', 'Has_Physical', 'Has_Electronic'
        ]]

        st.dataframe(
            verify_display,
            use_container_width=True,
            height=400
        )
    else:
        st.success("No books require manual verification! ✓")

# TAB 5: DATA TABLE
with tab5:
    st.header("Raw Data Explorer")

    # Column selector
    all_columns = filtered_df.columns.tolist()
    default_columns = [
        'Course', 'Required_Title', 'ISBN_Clean', 'Status',
        'Recommendation_Clean', 'Edition_Match', 'Has_Physical', 'Has_Electronic'
    ]

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
            file_name=f"primo_results_filtered_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("**Primo Search Results Dashboard** | Built with Streamlit | Search your library catalog for availability")
