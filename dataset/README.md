# Dataset Structure

This folder contains the datasets used for the Fashion Outfit Recommendation project.

The project uses multiple dataset stages because the system was developed iteratively. Some folders are used for training, while others are used only for evaluation.

## Folder Overview

```text
dataset/
├── raw/
├── cleaned/
├── split_style/
├── split_type/
├── external_type_test/
├── real_world_test/
├── style_extra/
├── type_extra/
└── metadata/
```

## raw/

The `raw` folder contains the initially collected clothing images before final review and organization.

These images are not used directly for model training. They are kept as the original collection source.

## cleaned/

The `cleaned` folder contains the reviewed and organized dataset used as the main catalogue.

The images are organized by:

```text
style/type/image
```

Example:

```text
cleaned/gothic/jacket/gothic_jacket_001.png
```

This means:

```text
style = gothic
type = jacket
```

The cleaned dataset is also used as the recommendation catalogue for the rule-based and embedding-based recommender prototypes.

## split_style/

The `split_style` folder contains the train, validation, and test split used for style classification.

The model predicts one of four style classes:

- formal
- gothic
- sporty
- streetwear

This split is organized as:

```text
split_style/train/style/image
split_style/val/style/image
split_style/test/style/image
```

## split_type/

The `split_type` folder contains the train, validation, and test split used for clothing type classification.

The model predicts one of four clothing type classes:

- jacket
- pants
- shoes
- tshirt

This split is organized as:

```text
split_type/train/type/image
split_type/val/type/image
split_type/test/type/image
```

## external_type_test/

The `external_type_test` folder contains a small external test set for the clothing type classifier.

It was created after the internal type classifier achieved perfect accuracy on the curated test set. The purpose of this folder is to check whether the type classifier can generalize to images outside the original split.

This dataset is used only for evaluation.

## real_world_test/

The `real_world_test` folder contains the real-world evaluation set.

It includes 80 images:

- 4 styles
- 4 clothing types
- 5 images per style/type combination

The folder structure is:

```text
real_world_test/style/type/image
```

Example:

```text
real_world_test/streetwear/jacket/streetwear_jacket_rw_001.png
```

This means:

```text
true style = streetwear
true type = jacket
```

This dataset is used only for external evaluation. It must not be used for training.

## style_extra/

The `style_extra` folder contains extra targeted training images for improving the style classifier.

This dataset was created after the real-world evaluation showed that the style classifier struggled with real-world images, especially streetwear.

The extra dataset contains 100 images focused on the main failure cases:

- streetwear jackets, pants, shoes, and tshirts
- formal pants and shoes
- sporty jackets and shoes

This dataset is used for training in the style dataset improvement experiment.

It must remain separate from `real_world_test`.

## type_extra/

The `type_extra` folder contains extra targeted training images for improving the clothing type classifier.

This dataset was created after the recommendation experiments showed that type prediction errors can break the recommendation structure. For example, when a jacket is predicted as a tshirt, the recommender excludes the wrong category and may recommend another jacket.

The extra dataset contains 90 images focused on real-world-like type variation:

- 30 jacket images
- 30 tshirt images
- 15 pants images
- 15 shoes images

This dataset is used for training in the type dataset improvement experiment.

It must remain separate from `real_world_test`.

## metadata/

The `metadata` folder contains supporting files that document the dataset.

Examples include:

- dataset rules
- generated labels
- style extra labels

Important metadata files:

```text
labels.csv
style_extra_labels.csv
dataset_rules.md
```

## Important Dataset Rules

The `real_world_test` dataset is only used for evaluation.

The `style_extra` dataset is used for training improvement.

Images from `real_world_test` should not be copied into `style_extra`, `type_extra`, `cleaned`, `split_style`, or `split_type`.

This separation is important because it prevents data leakage and keeps the real-world evaluation fair.

## Label Names

The final style labels are:

- formal
- gothic
- sporty
- streetwear

The final clothing type labels are:

- jacket
- pants
- shoes
- tshirt

The code uses `tshirt` as the class name. Documentation may refer to this as “t-shirt” in normal writing, but folder names and code should use `tshirt`.
