#!/usr/bin/env python3
import sys
import csv
from collections import defaultdict

def show_duplicate_rows(filename):
    # Map title → list of (line_no, row_dict)
    occurrences = defaultdict(list)
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=2):  # start=2 to account for header line
            title = row['Title']
            occurrences[title].append((idx, row))

    # Find and print duplicates
    found = False
    for title, rows in occurrences.items():
        if len(rows) > 1:
            found = True
            print(f"\nDuplicate Title: “{title}” appears {len(rows)} times:\n")
            for line_no, row in rows:
                # Reconstruct the CSV line for clarity
                choices = [row[f'Choice{i}'] for i in range(1,5)]
                print(f"  Line {line_no}: MCQ,\"{row['Title']}\",{','.join(f'\"{c}\"' if ',' in c else c for c in choices)},{row['Correct']}")
    if not found:
        print("No duplicate titles found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <docker.csv>")
        sys.exit(1)
    show_duplicate_rows(sys.argv[1])
