"""
Split test dataset into books and non-print items
"""

import pandas as pd

print("=" * 70)
print("Splitting test dataset by item type")
print("=" * 70)
print()

# Read the test dataset
input_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses.xlsx'
print(f"Reading: {input_file}")
df = pd.read_excel(input_file)

print(f"Total rows: {len(df)}")
print()

# Show breakdown by type
print("TextbookType breakdown:")
type_counts = df['TextbookType'].value_counts()
for item_type, count in type_counts.items():
    print(f"  {item_type:15} - {count:3} items")
print()

# Split into books and non-print
df_books = df[df['TextbookType'] == 'Book'].copy()
df_nonprint = df[df['TextbookType'] != 'Book'].copy()

print(f"Books: {len(df_books)} items")
print(f"Non-print: {len(df_nonprint)} items")
print()

# Save both datasets
books_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_books.xlsx'
nonprint_file = '/Users/patty_home/Desktop/Agentic AI/projects/030226_test/test_22_courses_nonprint.xlsx'

df_books.to_excel(books_file, index=False)
df_nonprint.to_excel(nonprint_file, index=False)

print(f"Saved books to: test_22_courses_books.xlsx")
print(f"Saved non-print to: test_22_courses_nonprint.xlsx")
print()

# Show courses in each dataset
print("Courses with books:")
book_courses = df_books['Course'].value_counts().sort_index()
for course, count in book_courses.items():
    print(f"  {course:15} - {count:3} books")
print()

print("Courses with non-print items:")
nonprint_courses = df_nonprint['Course'].value_counts().sort_index()
for course, count in nonprint_courses.items():
    print(f"  {course:15} - {count:3} items")

print()
print("=" * 70)
