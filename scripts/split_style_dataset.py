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

# Create output folders
for split in split_counts:
    for style in styles:
        os.makedirs(os.path.join(output_root, split, style), exist_ok=True)

for style in styles:
    all_files = []

    style_path = os.path.join(input_root, style)

    for item_type in os.listdir(style_path):
        type_path = os.path.join(style_path, item_type)

        if not os.path.isdir(type_path):
            continue

        for filename in os.listdir(type_path):
            file_path = os.path.join(type_path, filename)

            if os.path.isfile(file_path):
                all_files.append(file_path)

    random.shuffle(all_files)

    train_files = all_files[:split_counts["train"]]
    val_files = all_files[split_counts["train"]:split_counts["train"] + split_counts["val"]]
    test_files = all_files[split_counts["train"] + split_counts["val"]:]

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