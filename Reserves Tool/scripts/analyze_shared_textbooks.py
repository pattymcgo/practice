"""
Deep Analysis: Textbooks Used Across Multiple Courses
- Identifies shared textbooks
- Analyzes cross-departmental usage
- Finds bulk purchase opportunities
- Generates cost savings insights
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("TEXTBOOK SHARING ANALYSIS")
print("=" * 80)
print()

# ============================================================================
# LOAD DATA
# ============================================================================

# Load consolidated books data
books_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/Spring2026_BOOKS_consolidated.xlsx'
print(f"Loading: {books_file}")

try:
    df = pd.read_excel(books_file)
    print(f"✓ Loaded {len(df)} book entries")
except FileNotFoundError:
    # Try the older filename
    books_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/data/full_dataset_BOOKS_consolidated.xlsx'
    df = pd.read_excel(books_file)
    print(f"✓ Loaded {len(df)} book entries (using full dataset)")

print()

# Add department column
df['Department'] = df['Course'].str.extract(r'^([A-Z]+)')[0]

# ============================================================================
# ANALYSIS 1: TEXTBOOKS USED IN MULTIPLE COURSES
# ============================================================================

print("=" * 80)
print("ANALYSIS 1: Textbooks Used in Multiple Courses")
print("=" * 80)
print()

# Group by normalized title
title_usage = df.groupby('Title_Normalized').agg({
    'Title': 'first',  # Get the actual title
    'Course': lambda x: list(x),
    'Department': lambda x: list(set(x)),
    'Total_Enrollment': 'sum',
    'ISBN_All_Editions': 'first',
    'Num_Editions': 'first'
}).reset_index()

# Count courses per title
title_usage['Num_Courses'] = title_usage['Course'].apply(len)
title_usage['Num_Departments'] = title_usage['Department'].apply(len)

# Filter to books used in multiple courses
shared_books = title_usage[title_usage['Num_Courses'] > 1].copy()
shared_books = shared_books.sort_values('Num_Courses', ascending=False)

print(f"Total unique textbooks: {len(title_usage)}")
print(f"Textbooks used in multiple courses: {len(shared_books)}")
print(f"Percentage shared: {(len(shared_books)/len(title_usage))*100:.1f}%")
print()

# Top 20 most shared textbooks
print("Top 20 Most Shared Textbooks:")
print("-" * 80)
print(f"{'Rank':<6} {'Courses':<9} {'Depts':<7} {'Students':<10} {'Title':<50}")
print("-" * 80)

for i, (idx, row) in enumerate(shared_books.head(20).iterrows(), 1):
    title = row['Title'][:47] + '...' if len(str(row['Title'])) > 50 else row['Title']
    courses = row['Num_Courses']
    depts = row['Num_Departments']
    students = int(row['Total_Enrollment'])

    print(f"{i:<6} {courses:<9} {depts:<7} {students:<10,} {title:<50}")

print()

# ============================================================================
# ANALYSIS 2: CROSS-DEPARTMENTAL SHARING
# ============================================================================

print("=" * 80)
print("ANALYSIS 2: Cross-Departmental Textbook Sharing")
print("=" * 80)
print()

# Books used across multiple departments
cross_dept = shared_books[shared_books['Num_Departments'] > 1].copy()
cross_dept = cross_dept.sort_values('Num_Departments', ascending=False)

print(f"Textbooks shared across departments: {len(cross_dept)}")
print(f"Potential for bulk purchasing: {len(cross_dept[cross_dept['Num_Courses'] >= 3])}")
print()

print("Top 15 Cross-Departmental Textbooks:")
print("-" * 80)
print(f"{'Courses':<9} {'Depts':<7} {'Departments':<40} {'Title':<30}")
print("-" * 80)

for idx, row in cross_dept.head(15).iterrows():
    title = str(row['Title'])[:27] + '...' if len(str(row['Title'])) > 30 else row['Title']
    courses = row['Num_Courses']
    num_depts = row['Num_Departments']
    depts = ', '.join(sorted(row['Department']))[:37]
    if len(', '.join(sorted(row['Department']))) > 40:
        depts += '...'

    print(f"{courses:<9} {num_depts:<7} {depts:<40} {title:<30}")

print()

# ============================================================================
# ANALYSIS 3: DEPARTMENT-SPECIFIC PATTERNS
# ============================================================================

print("=" * 80)
print("ANALYSIS 3: Department Textbook Sharing Patterns")
print("=" * 80)
print()

# For each department, count how many books are shared vs unique
dept_sharing = {}

for dept in df['Department'].unique():
    dept_books = df[df['Department'] == dept]
    dept_titles = dept_books['Title_Normalized'].value_counts()

    shared_in_dept = len(dept_titles[dept_titles > 1])
    total_books = len(dept_titles)

    dept_sharing[dept] = {
        'Total_Books': total_books,
        'Shared_Within_Dept': shared_in_dept,
        'Unique_Books': total_books - shared_in_dept,
        'Sharing_Rate': (shared_in_dept / total_books * 100) if total_books > 0 else 0
    }

dept_df = pd.DataFrame(dept_sharing).T
dept_df = dept_df.sort_values('Total_Books', ascending=False).head(15)

print("Top 15 Departments - Textbook Sharing Patterns:")
print("-" * 80)
print(f"{'Dept':<8} {'Total Books':<12} {'Shared':<10} {'Unique':<10} {'% Shared':<10}")
print("-" * 80)

for dept, row in dept_df.iterrows():
    print(f"{dept:<8} {int(row['Total_Books']):<12} {int(row['Shared_Within_Dept']):<10} "
          f"{int(row['Unique_Books']):<10} {row['Sharing_Rate']:<10.1f}%")

print()

# ============================================================================
# ANALYSIS 4: BULK PURCHASE OPPORTUNITIES
# ============================================================================

print("=" * 80)
print("ANALYSIS 4: Bulk Purchase Opportunities")
print("=" * 80)
print()

# Books used in 3+ courses are good candidates for bulk purchase
bulk_candidates = shared_books[shared_books['Num_Courses'] >= 3].copy()

print(f"Textbooks used in 3+ courses: {len(bulk_candidates)}")
print(f"Total student impact: {bulk_candidates['Total_Enrollment'].sum():,} students")
print()

print("High-Impact Bulk Purchase Candidates:")
print("-" * 80)
print(f"{'Courses':<9} {'Students':<10} {'Editions':<10} {'Title':<50}")
print("-" * 80)

for idx, row in bulk_candidates.head(15).iterrows():
    title = str(row['Title'])[:47] + '...' if len(str(row['Title'])) > 50 else row['Title']
    courses = row['Num_Courses']
    students = int(row['Total_Enrollment'])
    editions = int(row['Num_Editions']) if pd.notna(row['Num_Editions']) else 1

    print(f"{courses:<9} {students:<10,} {editions:<10} {title:<50}")

print()

# ============================================================================
# VISUALIZATION 1: TEXTBOOK SHARING DISTRIBUTION
# ============================================================================

print("Creating visualizations...")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Chart 1: Distribution of courses per textbook
course_counts = title_usage['Num_Courses'].value_counts().sort_index()

ax1.bar(course_counts.index, course_counts.values,
        color=sns.color_palette("viridis", len(course_counts)),
        edgecolor='black', alpha=0.8)
ax1.set_xlabel('Number of Courses Using Same Textbook', fontweight='bold')
ax1.set_ylabel('Number of Textbooks', fontweight='bold')
ax1.set_title('Distribution: How Many Courses Share Each Textbook?', fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)

# Add value labels
for i, (x, y) in enumerate(zip(course_counts.index, course_counts.values)):
    ax1.text(x, y + 1, str(y), ha='center', fontweight='bold', fontsize=9)

# Chart 2: Top 15 most shared textbooks
top_shared = shared_books.head(15)
y_pos = np.arange(len(top_shared))
colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(top_shared)))

bars = ax2.barh(y_pos, top_shared['Num_Courses'], color=colors, edgecolor='black', alpha=0.8)

# Labels
titles_short = [t[:35] + '...' if len(t) > 35 else t for t in top_shared['Title']]
ax2.set_yticks(y_pos)
ax2.set_yticklabels(titles_short, fontsize=8)
ax2.set_xlabel('Number of Courses', fontweight='bold')
ax2.set_title('Top 15 Most Shared Textbooks', fontweight='bold', pad=15)
ax2.grid(True, axis='x', alpha=0.3)

# Add course count labels
for i, (idx, row) in enumerate(top_shared.iterrows()):
    ax2.text(row['Num_Courses'] + 0.1, i, f"{row['Num_Courses']:.0f}",
            va='center', fontweight='bold', fontsize=9)

# Chart 3: Cross-departmental sharing
dept_counts = shared_books['Num_Departments'].value_counts().sort_index()

ax3.bar(dept_counts.index, dept_counts.values,
        color=sns.color_palette("coolwarm", len(dept_counts)),
        edgecolor='black', alpha=0.8)
ax3.set_xlabel('Number of Departments Sharing Textbook', fontweight='bold')
ax3.set_ylabel('Number of Textbooks', fontweight='bold')
ax3.set_title('Cross-Departmental Textbook Sharing', fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3)

# Add value labels
for x, y in zip(dept_counts.index, dept_counts.values):
    ax3.text(x, y + 1, str(y), ha='center', fontweight='bold', fontsize=10)

# Chart 4: Department sharing rates
top_depts_for_viz = dept_df.head(10)
y_pos = np.arange(len(top_depts_for_viz))

# Stacked bar: shared vs unique
ax4.barh(y_pos, top_depts_for_viz['Shared_Within_Dept'],
         label='Shared within Dept', color='#FF6B6B', alpha=0.8, edgecolor='black')
ax4.barh(y_pos, top_depts_for_viz['Unique_Books'],
         left=top_depts_for_viz['Shared_Within_Dept'],
         label='Unique', color='#4ECDC4', alpha=0.8, edgecolor='black')

ax4.set_yticks(y_pos)
ax4.set_yticklabels(top_depts_for_viz.index, fontweight='bold')
ax4.set_xlabel('Number of Textbooks', fontweight='bold')
ax4.set_title('Top 10 Departments: Shared vs Unique Textbooks', fontweight='bold', pad=15)
ax4.legend(loc='lower right')
ax4.grid(True, axis='x', alpha=0.3)

plt.tight_layout()

# Save
output_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/textbook_sharing_analysis.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved visualization: textbook_sharing_analysis.png")
plt.close()

# ============================================================================
# SAVE DETAILED REPORT
# ============================================================================

print()
print("Generating detailed Excel report...")

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
report_file = f'/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/shared_textbooks_report_{timestamp}.xlsx'

with pd.ExcelWriter(report_file) as writer:
    # Sheet 1: All shared textbooks
    shared_export = shared_books[['Title', 'Num_Courses', 'Num_Departments',
                                   'Total_Enrollment', 'Num_Editions', 'Course']].copy()
    shared_export['Courses_List'] = shared_export['Course'].apply(lambda x: ', '.join(x))
    shared_export = shared_export.drop('Course', axis=1)
    shared_export.to_excel(writer, sheet_name='All Shared Textbooks', index=False)

    # Sheet 2: Cross-departmental
    cross_dept_export = cross_dept[['Title', 'Num_Courses', 'Num_Departments',
                                     'Department', 'Total_Enrollment']].copy()
    cross_dept_export['Departments_List'] = cross_dept_export['Department'].apply(
        lambda x: ', '.join(sorted(x)))
    cross_dept_export = cross_dept_export.drop('Department', axis=1)
    cross_dept_export.to_excel(writer, sheet_name='Cross-Departmental', index=False)

    # Sheet 3: Bulk purchase candidates
    bulk_export = bulk_candidates[['Title', 'Num_Courses', 'Total_Enrollment',
                                    'Num_Editions', 'ISBN_All_Editions']].copy()
    bulk_export.to_excel(writer, sheet_name='Bulk Purchase Candidates', index=False)

    # Sheet 4: Department patterns
    dept_df.to_excel(writer, sheet_name='Department Patterns')

print(f"✓ Saved detailed report: shared_textbooks_report_{timestamp}.xlsx")

# ============================================================================
# SUMMARY
# ============================================================================

print()
print("=" * 80)
print("ANALYSIS COMPLETE - KEY FINDINGS")
print("=" * 80)
print()
print(f"📊 Total Unique Textbooks: {len(title_usage)}")
print(f"🔄 Textbooks Shared Across Courses: {len(shared_books)} ({(len(shared_books)/len(title_usage))*100:.1f}%)")
print(f"🏢 Cross-Departmental Books: {len(cross_dept)}")
print(f"💰 Bulk Purchase Opportunities: {len(bulk_candidates)} (3+ courses)")
print(f"👥 Student Impact (shared books): {shared_books['Total_Enrollment'].sum():,}")
print()
print(f"📈 Top Shared Book: {shared_books.iloc[0]['Title']}")
print(f"   Used in {shared_books.iloc[0]['Num_Courses']} courses, "
      f"{shared_books.iloc[0]['Total_Enrollment']:.0f} students")
print()
print("Files generated:")
print(f"  • {output_file}")
print(f"  • {report_file}")
print("=" * 80)
