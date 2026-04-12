import os
import random
import shutil

random.seed(42)

input_root = "../dataset/cleaned"
output_root = "../dataset/split_style"

split_counts = {
    "train": 28,
    "val": 6,
    "test": 6
}

styles = ["casual", "formal", "sporty", "streetwear"]

# Remove old split folder if it already exists
if os.path.exists(output_root):
    shutil.rmtree(output_root)

# Create output folders
for split in split_counts:
    for style in styles:
        os.makedirs(os.path.join(output_root, split, style), exist_ok=True)

for style in styles:
    all_files = []

    style_path = os.path.join(input_root, style)
    if not os.path.isdir(style_path):
        print(f"Warning: missing style folder {style_path}")
        continue

    for item_type in os.listdir(style_path):
        type_path = os.path.join(style_path, item_type)

        if not os.path.isdir(type_path):
            continue

        for filename in os.listdir(type_path):
            file_path = os.path.join(type_path, filename)

            if os.path.isfile(file_path):
                all_files.append(file_path)

    random.shuffle(all_files)

    expected_total = sum(split_counts.values())
    if len(all_files) != expected_total:
        raise ValueError(
            f"Style '{style}' has {len(all_files)} images, but {expected_total} are required "
            f"for the split ({split_counts})."
        )

    train_end = split_counts["train"]
    val_end = train_end + split_counts["val"]

    train_files = all_files[:train_end]
    val_files = all_files[train_end:val_end]
    test_files = all_files[val_end:]

    split_map = {
        "train": train_files,
        "val": val_files,
        "test": test_files
    }

    for split_name, files in split_map.items():
        for file_path in files:
            filename = os.path.basename(file_path)
            destination = os.path.join(output_root, split_name, style, filename)
            shutil.copy2(file_path, destination)

print("Style-only dataset split created successfully.")