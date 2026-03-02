"""
Quick check of HSD 195 entries in the smart consolidated file
"""
import pandas as pd

df = pd.read_excel('test_22_courses_smart_consolidated.xlsx')
hsd195 = df[df['Course'] == 'HSD 195']

print('HSD 195 entries in smart consolidated file:')
print('=' * 70)
for idx, row in hsd195.iterrows():
    print(f"Section(s): {row['Section']}")
    print(f"Title: {row['Title']}")
    print(f"Title_Normalized: {row['Title_Normalized']}")
    print(f"Title_Variations: {row.get('Title_Variations', 'N/A')}")
    print(f"ISBN_All_Editions: {row.get('ISBN_All_Editions', 'N/A')}")
    print()
