import csv

input_file = 'merge_split_NGA2.csv'
output_file = 'cleaned_merge_split_NGA2.csv'

with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        cleaned_row = [cell.strip() for cell in row]  # Remove leading/trailing spaces
        writer.writerow(cleaned_row)

print(f"Cleaned CSV file saved as {output_file}")
