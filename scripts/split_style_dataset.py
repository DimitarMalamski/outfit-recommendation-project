import os
import random
import shutil

random.seed(42)

input_root = "../dataset/cleaned"
output_root = "../dataset/split_style"

split_ratios = {
    "train": 0.7,
    "val": 0.15,
    "test": 0.15
}

styles = sorted([
    folder for folder in os.listdir(input_root)
    if os.path.isdir(os.path.join(input_root, folder))
])

print("Detected styles:", styles)

if os.path.exists(output_root):
    shutil.rmtree(output_root)

for split in split_ratios:
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

    total = len(all_files)
    if total == 0:
        print(f"Style '{style}' has no images, skipping.")
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
        for file_path in files:
            item_type = os.path.basename(os.path.dirname(file_path))
            filename = os.path.basename(file_path)
            new_filename = f"{item_type}_{filename}"
            destination = os.path.join(output_root, split_name, style, new_filename)
            shutil.copy2(file_path, destination)

    print(
        f"Style '{style}': "
        f"{len(train_files)} train, {len(val_files)} val, {len(test_files)} test "
        f"(total: {total})"
    )

print("Style-only dataset split created successfully.")