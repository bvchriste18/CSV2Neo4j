import csv

input_file = 'merge_split.csv'
output_file = 'updated_merge_split.csv'

# Read the CSV file and remove excess spaces
with open(input_file, 'r', newline='') as infile:
    reader = csv.reader(infile)
    rows = [[cell.strip() for cell in row] for row in reader]

# Extract header and data rows
header = rows[0]
data_rows = rows[1:]

# List to store new rows
new_rows = []

# Iterate over each row in the original CSV
for row in data_rows:
    row_dict = dict(zip(header, row))
    # Check if the EventType is "Merge"
    if row_dict['EventType'] == 'Merge':
        # Split the OldIDs by semi-colon
        old_ids = row_dict['OldIDs'].split(';')
        # Create a new row for each OldID
        for old_id in old_ids:
            if old_id and old_id != row_dict['NewID']:  # Ensure old_id is not empty and not equal to NewID
                new_row = row_dict.copy()
                new_row['OldIDs'] = old_id
                new_rows.append(new_row)
    else:
        # If not a "Merge" event, keep the original row
        new_rows.append(row_dict)

# Write the new rows to a new CSV file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=header)
    
    writer.writeheader()
    writer.writerows(new_rows)

print(f"Cleaned and updated CSV file saved as {output_file}.")
