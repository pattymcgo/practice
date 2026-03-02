"""
Bar Chart: Courses with Most Students
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("Creating Top Courses by Enrollment Chart...")

# Load data
report_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/course_summary_20260302_130942.xlsx'
df_books = pd.read_excel(report_file, sheet_name='Books by Course')

# Get top 20 courses by enrollment
top_courses = df_books.nlargest(20, 'Total_Enrollment')

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))

# Create horizontal bar chart
y_pos = np.arange(len(top_courses))
colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(top_courses)))

bars = ax.barh(y_pos, top_courses['Total_Enrollment'],
               color=colors, edgecolor='black', alpha=0.8, linewidth=1.5)

# Add value labels on bars
for i, (idx, row) in enumerate(top_courses.iterrows()):
    # Get number of books for this course
    num_books = row['Num_Books']
    enrollment = row['Total_Enrollment']

    # Add enrollment value
    ax.text(enrollment + 20, i,
           f"{enrollment:.0f} students",
           va='center', fontweight='bold', fontsize=9)

    # Add number of books as annotation
    ax.text(enrollment/2, i,
           f"{num_books:.0f} books",
           va='center', ha='center', fontweight='bold',
           fontsize=8, color='white',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='darkblue', alpha=0.7))

# Set y-axis labels (course names)
course_labels = []
for idx, row in top_courses.iterrows():
    label = row['Course']
    # Add instructor name in smaller font
    instructor = str(row['Instructor_Name']).split('/')[0].split(',')[0]  # First instructor, last name
    if len(instructor) < 20 and instructor != 'nan':
        label = f"{label}\n({instructor})"
    course_labels.append(label)

ax.set_yticks(y_pos)
ax.set_yticklabels(course_labels, fontweight='bold', fontsize=10)

# Labels and title
ax.set_xlabel('Total Student Enrollment', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Courses by Student Enrollment\n(Color gradient: lighter = more students)',
             fontsize=14, fontweight='bold', pad=20)

# Grid
ax.grid(True, axis='x', alpha=0.3, linestyle='--')

# Add summary stats box
total_students_top20 = top_courses['Total_Enrollment'].sum()
total_books_top20 = top_courses['Num_Books'].sum()
avg_enrollment = top_courses['Total_Enrollment'].mean()

stats_text = f"""Top 20 Courses:
Total Students: {total_students_top20:,.0f}
Total Books: {total_books_top20:.0f}
Avg Enrollment: {avg_enrollment:.1f}

% of Total: {(total_students_top20/df_books['Total_Enrollment'].sum())*100:.1f}%"""

ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
        fontsize=9, verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))

plt.tight_layout()

# Save
output_file = '/Users/patty_home/Desktop/Agentic AI/Reserves Tool/reports/top_courses_by_enrollment.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved: top_courses_by_enrollment.png")
print(f"\nFile location: {output_file}")
plt.close()

# Also create a table view
print("\n" + "=" * 70)
print("TOP 20 COURSES BY ENROLLMENT - TABLE VIEW")
print("=" * 70)
print()
print(f"{'Rank':<6} {'Course':<12} {'Enrollment':<12} {'Books':<8} {'Instructor':<30}")
print("-" * 70)

for i, (idx, row) in enumerate(top_courses.iterrows(), 1):
    course = row['Course']
    enrollment = int(row['Total_Enrollment'])
    books = int(row['Num_Books'])
    instructor = str(row['Instructor_Name']).split('/')[0][:28]  # First instructor, truncated

    print(f"{i:<6} {course:<12} {enrollment:<12,} {books:<8} {instructor:<30}")

print()
print("=" * 70)
