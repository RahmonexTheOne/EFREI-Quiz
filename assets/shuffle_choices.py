#!/usr/bin/env python3
import csv
import random
import sys

input_file  = 'docker.csv'
output_file = 'docker_shuffled.csv'

with open(input_file, newline='', encoding='utf-8') as fin, \
     open(output_file, 'w', newline='', encoding='utf-8') as fout:

    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()

    for lineno, row in enumerate(reader, start=2):
        # Skip any stray header lines or malformed rows
        if row.get('Type','').strip().lower() == 'type':
            print(f"Skipping repeated header at input line {lineno}")
            continue

        # Ensure 'Correct' is numeric
        try:
            correct_idx = int(row['Correct']) - 1  # zero-based
            if not (0 <= correct_idx < 4):
                raise ValueError
        except ValueError:
            print(f"Skipping line {lineno}: invalid Correct value “{row['Correct']}”")
            continue

        # Grab and shuffle the choices
        choices = [row['Choice1'], row['Choice2'], row['Choice3'], row['Choice4']]
        paired = list(enumerate(choices))  # [(0,ch1), ...]
        random.shuffle(paired)

        # Re-assign shuffled choices and find the new correct index
        new_choices = []
        new_correct = None
        for new_pos, (orig_idx, text) in enumerate(paired):
            new_choices.append(text)
            if orig_idx == correct_idx:
                new_correct = new_pos + 1  # back to 1-based

        # Update the row
        row['Choice1'], row['Choice2'], row['Choice3'], row['Choice4'] = new_choices
        row['Correct'] = str(new_correct)

        writer.writerow(row)

print(f"\nDone! Shuffled file written to {output_file}")