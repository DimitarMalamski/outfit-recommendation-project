import os
import hashlib
from collections import defaultdict


DATASET_FOLDERS = {
    "cleaned": "dataset/cleaned",
    "split_style": "dataset/split_style",
    "split_type": "dataset/split_type",
    "real_world_test": "dataset/real_world_test",
    "style_extra": "dataset/style_extra",
    "external_type_test": "dataset/external_type_test",
}

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# These overlaps are expected because split_style and split_type were created from cleaned.
EXPECTED_OVERLAP_GROUPS = [
    {"cleaned", "split_style"},
    {"cleaned", "split_type"},
    {"cleaned", "split_style", "split_type"},
    {"split_style", "split_type"},
]


def calculate_file_hash(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def collect_image_hashes():
    hash_map = defaultdict(list)

    for dataset_name, folder_path in DATASET_FOLDERS.items():
        if not os.path.exists(folder_path):
            print(f"Skipping missing folder: {folder_path}")
            continue

        for root, _, files in os.walk(folder_path):
            for filename in files:
                if not filename.lower().endswith(VALID_EXTENSIONS):
                    continue

                file_path = os.path.join(root, filename)
                file_hash = calculate_file_hash(file_path)

                hash_map[file_hash].append({
                    "dataset": dataset_name,
                    "path": file_path
                })

    return hash_map


def is_expected_overlap(entries):
    datasets = {entry["dataset"] for entry in entries}

    return any(
        datasets == expected_group
        for expected_group in EXPECTED_OVERLAP_GROUPS
    )


def main():
    hash_map = collect_image_hashes()

    duplicate_groups = {
        file_hash: entries
        for file_hash, entries in hash_map.items()
        if len(entries) > 1
    }

    expected_duplicates = {}
    problematic_duplicates = {}

    for file_hash, entries in duplicate_groups.items():
        if is_expected_overlap(entries):
            expected_duplicates[file_hash] = entries
        else:
            problematic_duplicates[file_hash] = entries

    print("Duplicate check complete.")
    print(f"Total duplicate groups found: {len(duplicate_groups)}")
    print(f"Expected duplicate groups: {len(expected_duplicates)}")
    print(f"Problematic duplicate groups: {len(problematic_duplicates)}")

    if not problematic_duplicates:
        print("No problematic duplicate files found.")
        return

    print("\nProblematic duplicate groups:\n")

    for index, (_, entries) in enumerate(problematic_duplicates.items(), start=1):
        print(f"Problematic duplicate group {index}:")

        for entry in entries:
            print(f"  [{entry['dataset']}] {entry['path']}")

        print()


if __name__ == "__main__":
    main()