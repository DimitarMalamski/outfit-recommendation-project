import os
import random
import shutil

random.seed(42)

input_root = "../dataset/cleaned"
output_root = "../dataset/split_type"

split_ratios = {
    "train": 0.7,
    "val": 0.15,
    "test": 0.15
}

# Detect styles from cleaned/
styles = sorted([
  folder for folder in os.listdir(input_root)
  if os.path.isdir(os.path.join(input_root, folder))
])

print("Detected styles:", styles)

# Detect clothing types by looking inside the style folders
types = set()
for style in styles:
    style_path = os.path.join(input_root, style)
    for item_type in os.listdir(style_path):
        type_path = os.path.join(style_path, item_type)
        if os.path.isdir(type_path):
            types.add(item_type)

types = sorted(types)
print("Detected clothing types:", types)

# Remove old output folder if it exists
if os.path.exists(output_root):
    shutil.rmtree(output_root)

# Create output folder structure
for split in split_ratios:
    for item_type in types:
        os.makedirs(os.path.join(output_root, split, item_type), exist_ok=True)

# Build split per clothing type
for item_type in types:
    all_files = []

    for style in styles:
        type_path = os.path.join(input_root, style, item_type)

        if not os.path.isdir(type_path):
            continue

        for filename in os.listdir(type_path):
            file_path = os.path.join(type_path, filename)

            if os.path.isfile(file_path):
                all_files.append((style, file_path))

    random.shuffle(all_files)

    total = len(all_files)
    if total == 0:
        print(f"Type '{item_type}' has no images, skipping.")
        continue

    train_count = int(total * split_ratios["train"])
    val_count = int(total * split_ratios["val"])
    test_count = total - train_count - val_count

    train_end = train_count
    val_end = train_end + val_count

    train_files = all_files[:train_end]
    val_files = all_files[train_end:val_end]
    test_files = all_files[val_end:]

    split_map = {
        "train": train_files,
        "val": val_files,
        "test": test_files
    }

    for split_name, files in split_map.items():
        for style, file_path in files:
            filename = os.path.basename(file_path)

            # Prefix with style so filenames stay unique and traceable
            new_filename = f"{style}_{filename}"

            destination = os.path.join(output_root, split_name, item_type, new_filename)
            shutil.copy2(file_path, destination)

    print(
        f"Type '{item_type}': "
        f"{len(train_files)} train, {len(val_files)} val, {len(test_files)} test "
        f"(total: {total})"
    )

print("Type-only dataset split created successfully.")