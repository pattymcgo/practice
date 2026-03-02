"""
Data Visualizations for Course Reserves
- Bubble Chart: Books vs Enrollment
- Before/After Consolidation Impact
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 70)
print("CREATING COURSE RESERVES VISUALIZATIONS")
print("=" * 70)
print()

# ============================================================================
# LOAD DATA
# ============================================================================

# Load the course summary report
report_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/course_summary_20260302_130942.xlsx'
print(f"Loading: {report_file}")

df_books = pd.read_excel(report_file, sheet_name='Books by Course')
print(f"Books by Course: {len(df_books)} rows loaded")
print()

# ============================================================================
# VISUALIZATION 1: BUBBLE CHART - BOOKS VS ENROLLMENT
# ============================================================================

print("Creating Bubble Chart: Books vs Enrollment...")

# Prepare data
df_books['Num_Sections'] = df_books['Section'].str.count(',') + 1  # Count sections

# Get department from course code
df_books['Department'] = df_books['Course'].str.extract(r'^([A-Z]+)')[0]

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))

# Get unique departments for colors
departments = df_books['Department'].unique()
colors = sns.color_palette("husl", len(departments))
dept_colors = dict(zip(departments, colors))

# Create bubble chart
for dept in departments:
    dept_data = df_books[df_books['Department'] == dept]

    ax.scatter(
        dept_data['Num_Books'],
        dept_data['Total_Enrollment'],
        s=dept_data['Num_Sections'] * 50,  # Size based on sections
        alpha=0.6,
        c=[dept_colors[dept]],
        label=dept,
        edgecolors='white',
        linewidth=1.5
    )

# Annotate top 10 courses by enrollment
top_10 = df_books.nlargest(10, 'Total_Enrollment')
for idx, row in top_10.iterrows():
    ax.annotate(
        row['Course'],
        (row['Num_Books'], row['Total_Enrollment']),
        xytext=(5, 5),
        textcoords='offset points',
        fontsize=8,
        fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3)
    )

# Labels and title
ax.set_xlabel('Number of Different Books', fontsize=12, fontweight='bold')
ax.set_ylabel('Total Student Enrollment', fontsize=12, fontweight='bold')
ax.set_title('Course Reserves: Books vs Enrollment\n(Bubble size = Number of Sections)',
             fontsize=14, fontweight='bold', pad=20)

# Legend
ax.legend(title='Department', bbox_to_anchor=(1.05, 1), loc='upper left',
          fontsize=9, title_fontsize=10, frameon=True, shadow=True)

# Grid
ax.grid(True, alpha=0.3, linestyle='--')

# Add statistics text box
stats_text = f"""Dataset Statistics:
Total Courses: {len(df_books)}
Total Students: {df_books['Total_Enrollment'].sum():,.0f}
Avg Books/Course: {df_books['Num_Books'].mean():.1f}
Avg Students/Course: {df_books['Total_Enrollment'].mean():.1f}"""

ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
        fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Save
output_file_1 = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/bubble_chart_books_vs_enrollment.png'
plt.savefig(output_file_1, dpi=300, bbox_inches='tight')
print(f"✓ Saved: bubble_chart_books_vs_enrollment.png")
plt.close()

# ============================================================================
# VISUALIZATION 2: BEFORE/AFTER CONSOLIDATION IMPACT
# ============================================================================

print("Creating Before/After Consolidation Chart...")

# Consolidation statistics (from the processing summary)
consolidation_data = {
    'Books': {
        'Original': 1874,
        'Consolidated': 520,
        'Reduction': 1354
    },
    'Non-Print': {
        'Original': 721,
        'Consolidated': 212,
        'Reduction': 509
    },
    'Total': {
        'Original': 2595,
        'Consolidated': 732,
        'Reduction': 1863
    }
}

# Create figure with subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# ---- Subplot 1: Before/After Bar Chart ----
categories = ['Books\n(Physical)', 'Non-Print\n(E-Resources)', 'Total']
original_values = [1874, 721, 2595]
consolidated_values = [520, 212, 732]

x = np.arange(len(categories))
width = 0.35

bars1 = ax1.bar(x - width/2, original_values, width,
                label='Original', color='#FF6B6B', alpha=0.8, edgecolor='black')
bars2 = ax1.bar(x + width/2, consolidated_values, width,
                label='Consolidated', color='#4ECDC4', alpha=0.8, edgecolor='black')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)

ax1.set_xlabel('Category', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Entries', fontsize=12, fontweight='bold')
ax1.set_title('Data Consolidation: Before vs After', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(categories)
ax1.legend(fontsize=11, loc='upper left', frameon=True, shadow=True)
ax1.grid(True, axis='y', alpha=0.3, linestyle='--')

# ---- Subplot 2: Reduction Percentages ----
reduction_pct = [
    (1354/1874) * 100,  # Books
    (509/721) * 100,    # Non-Print
    (1863/2595) * 100   # Total
]

bars3 = ax2.barh(categories, reduction_pct, color=['#FF6B6B', '#95E1D3', '#4ECDC4'],
                 alpha=0.8, edgecolor='black')

# Add percentage labels
for i, (bar, pct) in enumerate(zip(bars3, reduction_pct)):
    ax2.text(pct + 1, bar.get_y() + bar.get_height()/2,
            f'{pct:.1f}%',
            ha='left', va='center', fontweight='bold', fontsize=11)

ax2.set_xlabel('Reduction Percentage', fontsize=12, fontweight='bold')
ax2.set_title('Consolidation Efficiency\n(% Rows Reduced)', fontsize=14, fontweight='bold')
ax2.set_xlim(0, 100)
ax2.grid(True, axis='x', alpha=0.3, linestyle='--')

# Add summary text box
summary_text = f"""Smart Consolidation Results:
✓ Combined duplicate courses
✓ Merged multiple sections
✓ Unified different editions
✓ Normalized title variations

Overall Efficiency: {(1863/2595)*100:.1f}% reduction
Ready for Alma automation!"""

fig.text(0.5, -0.05, summary_text, ha='center', fontsize=10,
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()

# Save
output_file_2 = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/consolidation_impact.png'
plt.savefig(output_file_2, dpi=300, bbox_inches='tight')
print(f"✓ Saved: consolidation_impact.png")
plt.close()

# ============================================================================
# BONUS: Department Breakdown Visualization
# ============================================================================

print("Creating Department Breakdown Chart...")

fig, ax = plt.subplots(figsize=(12, 8))

# Get top 15 departments by total students
dept_summary = df_books.groupby('Department').agg({
    'Total_Enrollment': 'sum',
    'Num_Books': 'sum',
    'Course': 'count'
}).rename(columns={'Course': 'Num_Courses'})

dept_summary = dept_summary.sort_values('Total_Enrollment', ascending=True).tail(15)

# Create horizontal bar chart
y_pos = np.arange(len(dept_summary))
bars = ax.barh(y_pos, dept_summary['Total_Enrollment'],
               color=plt.cm.viridis(np.linspace(0.3, 0.9, len(dept_summary))),
               edgecolor='black', alpha=0.8)

# Add value labels
for i, (idx, row) in enumerate(dept_summary.iterrows()):
    ax.text(row['Total_Enrollment'] + 50, i,
           f"{row['Total_Enrollment']:.0f} students\n{row['Num_Courses']:.0f} courses",
           va='center', fontsize=8, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(dept_summary.index, fontweight='bold')
ax.set_xlabel('Total Student Enrollment', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Departments by Student Enrollment', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()

# Save
output_file_3 = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/department_breakdown.png'
plt.savefig(output_file_3, dpi=300, bbox_inches='tight')
print(f"✓ Saved: department_breakdown.png")
plt.close()

# ============================================================================
# SUMMARY
# ============================================================================

print()
print("=" * 70)
print("VISUALIZATIONS COMPLETE!")
print("=" * 70)
print()
print("Generated 3 visualizations:")
print(f"1. Bubble Chart: Books vs Enrollment")
print(f"   → {output_file_1}")
print(f"2. Before/After Consolidation Impact")
print(f"   → {output_file_2}")
print(f"3. BONUS: Department Breakdown")
print(f"   → {output_file_3}")
print()
print("All files saved in: reports/")
print("=" * 70)
