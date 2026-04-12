import os
import csv

dataset_root = "../dataset/cleaned"
output_csv = "../dataset/metadata/labels.csv"

rows = []

for style in os.listdir(dataset_root):
  style_path = os.path.join(dataset_root, style)
  if not os.path.isdir(style_path):
    continue

  for item_type in os.listdir(style_path):
    type_path = os.path.join(style_path, item_type)
    if not os.path.isdir(type_path):
      continue

    for filename in os.listdir(type_path):
      file_path = os.path.join(type_path, filename)

      if os.path.isfile(file_path):
        rows.append([filename, style, item_type, "unknown"])

# Sort rows for neatness
rows.sort(key=lambda x: (x[1], x[2], x[0]))

# Make sure metadata folder exists
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "style", "type", "source"])
    writer.writerows(rows)

print(f"Created {output_csv} with {len(rows)} rows.")