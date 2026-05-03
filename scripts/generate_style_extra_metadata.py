import os
import pandas as pd

style_extra_dir = "../dataset/style_extra"
metadata_output_path = "../dataset/metadata/style_extra_labels.csv"

valid_extensions = (".jpg", ".jpeg", ".png", ".webp")

style_extra_items = []

for style in sorted(os.listdir(style_extra_dir)):
    style_path = os.path.join(style_extra_dir, style)

    if not os.path.isdir(style_path):
        continue

    for item_type in sorted(os.listdir(style_path)):
        type_path = os.path.join(style_path, item_type)

        if not os.path.isdir(type_path):
            continue

        for filename in sorted(os.listdir(type_path)):
            if not filename.lower().endswith(valid_extensions):
                continue

            image_path = os.path.join(type_path, filename)

            style_extra_items.append({
                "filename": filename,
                "relative_path": image_path,
                "style": style,
                "type": item_type,
                "reason_added": "added to improve real-world style generalization"
            })

style_extra_df = pd.DataFrame(style_extra_items)

style_extra_df.to_csv(metadata_output_path, index=False)

print("Extra style metadata saved.")
print("Total extra images:", len(style_extra_df))

style_extra_df.head()