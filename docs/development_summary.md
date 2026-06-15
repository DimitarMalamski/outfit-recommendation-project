# Development Summary - Outfit Recommendation System

## 1. Purpose of this document

The purpose of this document is to summarize the development process of the Outfit Recommendation System project.

This document explains the main experiments, the results, the development decisions, and the improvements made throughout the project. It also shows how the project evolved from simple classification baselines into a working recommendation prototype based on style prediction, clothing type prediction, and embedding-based retrieval.

The document is intended to support the final project documentation by providing a clear overview of what was built, why certain decisions were made, and what the main findings were.

## 2. Development overview

The project was developed iteratively. The original goal was to build an outfit recommendation system, but direct outfit compatibility was too subjective and difficult to model immediately. Because of this, the first development step focused on two simpler classification tasks: fashion style classification and clothing type classification.

After both classifiers were built, they were connected to a basic rule-based recommendation prototype. This prototype recommended items with the same predicted style and a different predicted clothing type. The next prototype improved this by using image embeddings and cosine similarity to rank recommendations by visual similarity.

After the first prototypes worked on the curated dataset, a real-world evaluation set was created. This showed that the style classifier struggled with realistic images, while the clothing type classifier remained more reliable. Because style prediction directly affects recommendation quality, the next development iterations focused on improving the style classifier.

A partial fine-tuning experiment improved curated test accuracy but made real-world performance worse. This showed that model changes alone were not enough. A later dataset-improvement experiment added targeted extra training images, especially for streetwear. This improved real-world style accuracy from 0.4750 to 0.6000.

The improved style model was then tested inside the embedding-based recommendation pipeline. The results showed that recommendations became more useful when style prediction was correct, but the system was still affected by style and clothing type prediction errors.

Because some recommendation failures were caused by wrong clothing type predictions, the next development step focused on improving the type classifier with targeted real-world-like images. This improved real-world type accuracy from 0.7500 to 0.8875.

The improved type model was then tested inside the full recommendation pipeline. The results showed that type-related structural recommendation failures were reduced. In the selected real-world examples, same-actual-type recommendation issues dropped from 2 examples to 0 examples. However, the system still had remaining style-related weaknesses, especially when gothic or sporty items were predicted as streetwear.

After this, a more systematic recommendation evaluation framework was created. Instead of only inspecting a few recommendation examples visually, 32 balanced real-world examples were evaluated using automatic checks and manual scoring criteria. This showed that the recommender was structurally strong, with an average structural validity score of 1.875 out of 2, but weaker in style consistency, visual coherence, and overall recommendation quality, each averaging 1.3125 out of 2. This confirmed that the next major improvement should focus on style reliability.

After the recommendation evaluation framework showed that style reliability was the main bottleneck, a new model architecture comparison experiment was created. This experiment compared ResNet34, MobileNetV3 Large, and EfficientNet-B0 using the same improved style training setup and the same real-world evaluation set. MobileNetV3 Large achieved the best real-world style result, with 0.6250 accuracy and 0.6242 macro F1-score. It also had a much smaller model size than ResNet34, which made it a better candidate for the next recommendation pipeline experiment.

After MobileNetV3 Large performed best in the architecture comparison, it was tested inside the full recommendation pipeline. This experiment kept the type classifier, recommendation catalogue, ResNet34 embedding extractor, cosine similarity ranking, confidence thresholds, and 32-example evaluation subset the same. Only the style classifier was changed. The MobileNetV3 setup improved automatic style accuracy from 0.5625 to 0.65625. The manual evaluation also improved: overall recommendation quality increased from 1.3125 to 1.40625, and the number of good recommendations increased from 17 to 19. Based on this, MobileNetV3 Large became the selected style classifier for the current prototype.

## 3. Experiment 1: Style Classification Baseline

The first experiment focused on fashion style classification.

The goal was to test whether the manually collected dataset could be used to train a model that predicts the visual style of an individual clothing item.

The four style classes were:

- formal
- gothic
- sporty
- streetwear

A pretrained ResNet34 model was used with transfer learning. The pretrained feature extractor was frozen, and only the final classification layer was trained.

The model was trained on the curated style split:

- 560 training images
- 120 validation images
- 120 test images

The style baseline achieved a curated test accuracy of **0.8417** and a macro F1-score of **0.84**.

The results showed that style classification was feasible, but some style categories were harder than others. Gothic and formal performed strongly, while streetwear was the weakest class. This suggested that streetwear visually overlaps more with other styles, especially sporty and gothic.

## 4. Experiment 2: Clothing Type Classification Baseline

The second experiment focused on clothing type classification.

The goal was to test whether the model could identify what kind of clothing item was shown in an image. This was important because the recommendation system needs to avoid recommending the same type of item as the input.

The four clothing type classes were:

- jacket
- pants
- shoes
- tshirt

The same ResNet34 transfer learning approach was used. The pretrained feature extractor was frozen, and only the final classification layer was trained.

The clothing type classifier achieved an internal test accuracy of **1.00** on the curated test split. Because this result was unusually high, a small external test set of 20 images was created. On this external test set, the model achieved **0.90** accuracy.

Later, during the larger real-world evaluation, the clothing type classifier achieved **0.7500** accuracy.

These results showed that clothing type classification was more reliable than style classification. This makes sense because clothing types have clearer visual structure than fashion styles.

## 5. Experiment 3: Rule-Based Recommendation Prototype

The third experiment connected the style and clothing type classifiers to a first recommendation prototype.

The goal was to prove that the two classification models could be used together in a basic recommendation workflow.

The rule-based recommender used the following logic:

```text
Recommend items where:
    item style = predicted style
    item type != predicted type
```

For example, if the input image was predicted as a gothic jacket, the system recommended gothic items that were not jackets, such as gothic pants, gothic shoes, and gothic tshirts.

This prototype showed that the classification outputs could be used to generate structured outfit suggestions. However, the recommended items were selected randomly from the filtered catalogue. This meant that the system could produce logically valid recommendations, but it did not yet rank items by visual compatibility.

## 6. Experiment 4: Embedding-Based Recommendation Prototype

The fourth experiment improved the rule-based recommendation prototype by adding visual similarity.

Instead of randomly selecting items from the filtered catalogue, the system used image embeddings extracted from a pretrained ResNet34 feature extractor. These embeddings represented each image as a feature vector.

The recommendation process became:

1. Predict the style of the input image.
2. Predict the clothing type of the input image.
3. Filter the catalogue to items with the same predicted style.
4. Exclude items with the same predicted clothing type.
5. Compute cosine similarity between the input image embedding and candidate embeddings.
6. Select the most similar item from each remaining clothing type.

This improved the recommendation system because items were no longer selected randomly. The system could now rank candidates based on visual similarity, making the recommendations more structured and explainable.

This experiment showed that embedding-based retrieval was a stronger foundation for recommendation than simple rule-based random selection.

## 7. Experiment 5: Real-World Evaluation

After the baseline models and recommendation prototypes were created, a separate real-world test set was collected.

The purpose of this evaluation was to test whether the trained models could generalize beyond the clean curated dataset.

The real-world test set contained **80 images**:

- 4 styles
- 4 clothing types
- 5 images per style/type combination

The images were more realistic than the original dataset and included more varied presentation styles, such as worn clothing, different backgrounds, and less controlled image conditions.

The results were:

| Model                    | Real-world accuracy |
| ------------------------ | ------------------: |
| Style classifier         |              0.4750 |
| Clothing type classifier |              0.7500 |

The results showed that the clothing type classifier generalized better than the style classifier. The biggest issue was the style classifier, especially the streetwear class. Streetwear had **0.00 recall**, meaning that none of the real-world streetwear images were correctly predicted as streetwear.

This evaluation was important because it revealed that good curated test performance was not enough. The system needed to be tested on more realistic images before improving the recommendation pipeline further.

## 8. Experiment 6: Style Classifier Fine-Tuning

After the real-world evaluation showed weak style generalization, the next experiment focused on improving the style classifier.

The original style classifier trained only the final classification layer. In this experiment, the last ResNet34 block, `layer4`, was unfrozen together with the final classification layer. This allowed the model to adapt more to fashion-specific visual features.

The fine-tuned model achieved:

| Evaluation set      | Accuracy |
| ------------------- | -------: |
| Curated test set    |   0.9417 |
| Real-world test set |   0.4250 |

The curated test accuracy improved strongly compared with the original style baseline, which achieved **0.8417**. However, real-world accuracy decreased from **0.4750** to **0.4250**.

This showed that fine-tuning helped the model perform better on clean curated images, but it did not improve generalization to realistic images. The model likely adapted too strongly to the curated dataset.

This experiment was useful because it showed that changing the training strategy alone was not enough. The main problem was likely the mismatch between the curated training data and the real-world test images.

## 9. Experiment 7: Style Dataset Improvement

After the fine-tuning experiment failed to improve real-world performance, the next experiment focused on improving the style training dataset.

The real-world evaluation showed that the main problem was the style classifier, especially streetwear. Because of this, extra targeted training images were collected and added to a new dataset folder called `style_extra`.

The extra dataset contained **100 images**:

- 60 streetwear images
- 20 formal images
- 20 sporty images

The images were selected based on the main failure cases from the real-world evaluation:

- streetwear was often confused with gothic or sporty
- formal pants and shoes were often misclassified
- sporty jackets and shoes were often confused with other styles

The new model was trained using the original style training set plus the extra targeted images. The model used the same basic training strategy as the original baseline, where the pretrained ResNet34 feature extractor was frozen and only the final classification layer was trained.

The dataset-improved model achieved:

| Evaluation set      | Accuracy |
| ------------------- | -------: |
| Curated test set    |   0.8667 |
| Real-world test set |   0.6000 |

This was the best real-world style result so far.

The most important improvement was streetwear recall. In the original real-world evaluation, streetwear recall was **0.00**. In the dataset-improved model, streetwear recall increased to **0.90**.

However, the model also started predicting streetwear too often. Many gothic and sporty images were incorrectly classified as streetwear. This means that the extra data helped the model recognize streetwear, but also shifted the model too strongly toward the streetwear class.

Overall, this experiment showed that dataset improvement was more effective than fine-tuning alone for improving real-world generalization.

## 10. Experiment 8: Recommendation with Improved Style Model

The eighth experiment tested the embedding-based recommendation system using the improved style classifier.

The recommendation system used:

- the dataset-improved style classifier
- the existing clothing type classifier
- the cleaned catalogue dataset
- ResNet34 image embeddings
- cosine similarity ranking

The goal was to check whether the improved style classifier helped the recommender produce better results for real-world input images.

Several real-world examples were tested. The results showed that the improved style model helped when the style prediction was correct. For example, the system produced useful recommendations for examples such as formal shoes, gothic jackets, sporty jackets, and streetwear tshirts.

However, the recommendation pipeline was still affected by classification errors. If the style prediction was wrong, the recommender retrieved items from the wrong style category. If the clothing type prediction was wrong, the system sometimes recommended another item from the same actual clothing category.

For example, a streetwear jacket was correctly predicted as streetwear, but incorrectly predicted as a tshirt. Because the recommender excluded tshirts instead of jackets, it recommended another streetwear jacket. This showed that recommendation quality depends on both the style classifier and the clothing type classifier.

This experiment confirmed that the improved style model was useful, but the full recommendation system still needs stronger safeguards and more robust prediction handling.

## 11. Experiment 9: Recommendation with Confidence Safeguards

The ninth experiment improved the recommendation pipeline by adding confidence-based safeguards.

The previous recommendation experiment showed that the recommender still depended strongly on the correctness of the style and clothing type classifiers. When the predicted type was wrong, the system could exclude the wrong clothing category and recommend another item of the same actual type. When the predicted style was wrong, the system retrieved items from the wrong style category.

To make the system more transparent, confidence thresholds were added:

- style confidence threshold: 0.60
- type confidence threshold: 0.60

The system assigns one of four statuses:

- reliable
- type_uncertain
- style_uncertain
- style_and_type_uncertain

The recommender still generates recommendations, but it now adds warnings when the style or clothing type confidence is low.

On the eight selected real-world examples, the safeguard results were:

| Status                   | Count |
| ------------------------ | ----: |
| reliable                 |     4 |
| type_uncertain           |     2 |
| style_uncertain          |     2 |
| style_and_type_uncertain |     0 |

This showed that confidence safeguards can make some uncertain recommendation cases more explainable. For example, the streetwear jacket example was correctly marked as `type_uncertain` because the type classifier predicted `tshirt` with low confidence.

However, the experiment also showed that confidence thresholds are not a complete reliability solution. The gothic tshirt example was incorrectly predicted as streetwear with high confidence, so it was still marked as reliable. This shows that the model can be confidently wrong.

Overall, this experiment improved the transparency of the recommendation system, but future work would need better calibration or fallback behavior for uncertain predictions.

## 12. Experiment 10: Clothing Type Dataset Improvement

The tenth experiment focused on improving the clothing type classifier using targeted real-world-like training data.

Previous recommendation experiments showed that type prediction errors could break the recommendation structure. If the input type was predicted incorrectly, the recommender excluded the wrong category and could recommend another item of the same actual type.

For example, a streetwear jacket was correctly predicted as streetwear, but incorrectly predicted as a tshirt. Because the recommender excluded tshirts instead of jackets, it recommended another streetwear jacket. This showed that type prediction was not only a classifier issue, but a structural issue for the recommendation system.

To address this, a new dataset folder called `type_extra` was created. It contained 90 targeted extra images:

- 30 jacket images
- 30 tshirt images
- 15 pants images
- 15 shoes images

The extra images focused on real-world-like cases, especially worn jackets, open jackets, oversized tshirts, cropped upper-body views, pants, and shoes in more varied presentation styles.

The improved type classifier was trained using the original type training split plus the `type_extra` dataset. The model architecture and training setup stayed the same as the original type baseline:

- pretrained ResNet34
- frozen feature extractor
- replaced final classification layer
- trained final layer only

This made the experiment focused on the effect of dataset improvement rather than architecture changes.

The improved type model achieved:

| Evaluation set           | Accuracy |
| ------------------------ | -------: |
| Curated type test set    |   1.0000 |
| External type test set   |   0.9000 |
| Real-world type test set |   0.8875 |

The curated and external test results stayed the same as the original type model, meaning that the extra data did not damage performance on cleaner evaluation sets.

The most important improvement was on the real-world test set. The original type classifier achieved 0.7500 real-world accuracy, while the improved type classifier achieved 0.8875. This showed that targeted type data helped the model generalize better to realistic input images.

The remaining issue was that some pants and tshirts were still predicted as jackets. This suggests that the added jacket data helped the model recognize jackets better, but also made the jacket class slightly more dominant in ambiguous cases.

Overall, this experiment showed that improving the type dataset directly improved the model where the recommendation pipeline needed it most.

## 13. Experiment 11: Recommendation with Improved Models

The eleventh experiment tested the full recommendation pipeline using both improved classifiers.

The recommendation system used:

- the dataset-improved style classifier
- the dataset-improved type classifier
- the cleaned catalogue dataset
- ResNet34 image embeddings
- cosine similarity ranking
- confidence safeguards

The goal was to check whether the improved type classifier reduced structural recommendation failures in the full pipeline.

The experiment compared two setups:

| Setup          | Style model                     | Type model                     |
| -------------- | ------------------------------- | ------------------------------ |
| Previous setup | `style_resnet34_extra_data.pth` | `type_resnet34.pth`            |
| Improved setup | `style_resnet34_extra_data.pth` | `type_resnet34_extra_data.pth` |

The same eight real-world examples from the confidence safeguard experiment were tested again. This made the comparison fair because the input images stayed the same.

The improved type model fixed two type prediction errors:

- a formal jacket was previously predicted as pants, but was now correctly predicted as jacket
- a streetwear jacket was previously predicted as tshirt, but was now correctly predicted as jacket

The type prediction comparison was:

| Metric                   | Previous setup | Improved setup |
| ------------------------ | -------------: | -------------: |
| Correct type predictions |          6 / 8 |          8 / 8 |
| Type errors fixed        |            N/A |              2 |
| Type errors introduced   |            N/A |              0 |
| Reliable examples        |          4 / 8 |          6 / 8 |

The recommendation structure also improved. With the previous setup, 2 out of 8 examples included a recommendation with the same actual type as the input item. With the improved setup, this dropped to 0 out of 8.

| Metric                                 | Previous setup | Improved setup |
| -------------------------------------- | -------------: | -------------: |
| Same-actual-type recommendation issues |              2 |              0 |
| Structural issues fixed                |            N/A |              2 |
| Structural issues introduced           |            N/A |              0 |

This showed that the improved type classifier did not only improve standalone classification accuracy. It also improved the recommendation pipeline by preventing duplicate actual clothing types in the output.

However, the experiment also showed that some remaining issues are style-related. For example, some gothic and sporty images were still predicted as streetwear. In these cases, the recommendation structure can be correct, but the retrieved items may still come from the wrong style category.

Overall, this experiment confirmed that the improved type classifier is the better choice for the current prototype. It reduced type-related structural failures, while the main remaining bottleneck became style reliability and recommendation evaluation.

## 14. Experiment 12: Recommendation Evaluation Framework

The twelfth experiment focused on evaluating the current final recommendation prototype more systematically.

Previous recommendation experiments used selected examples and visual inspection. This was useful for understanding the system qualitatively, but it was not repeatable enough to compare future improvements. Because of this, a small evaluation framework was created.

The evaluation used the current final prototype:

- `style_resnet34_extra_data.pth`
- `type_resnet34_extra_data.pth`
- ResNet34 image embeddings
- cosine similarity ranking
- confidence safeguards

A balanced subset of the real-world test set was selected:

- 4 styles
- 4 clothing types
- 2 examples per style/type combination
- 32 examples in total

For each example, the system recorded automatic information such as:

- true style
- true clothing type
- predicted style
- predicted clothing type
- style confidence
- type confidence
- safeguard status
- recommended item types
- whether the recommendations included the same actual type as the input

The automatic evaluation showed:

| Metric                                         | Result |
| ---------------------------------------------- | -----: |
| Style prediction accuracy on selected examples | 0.5625 |
| Type prediction accuracy on selected examples  | 0.9375 |
| Same-actual-type recommendation issues         | 2 / 32 |

This confirmed that clothing type prediction was now strong, while style prediction remained the main bottleneck.

A manual scoring framework was then added. Each recommendation was scored from 0 to 2 using the following criteria:

- structural validity
- style consistency
- visual coherence
- confidence warning usefulness
- overall recommendation quality

The manual evaluation results were:

| Criterion                     | Average score |
| ----------------------------- | ------------: |
| Structural validity           |        1.8750 |
| Style consistency             |        1.3125 |
| Visual coherence              |        1.3125 |
| Confidence warning usefulness |        1.4688 |
| Overall quality               |        1.3125 |

The overall recommendation quality distribution was:

| Quality          | Count |
| ---------------- | ----: |
| Bad              |     7 |
| Partially useful |     8 |
| Good             |    17 |

This means that 17 out of 32 recommendations were scored as good, while 15 were either partially useful or bad.

The by-style results showed that streetwear had the best average overall quality score at 1.625, while gothic had the weakest score at 1.125. This fits the earlier findings: the extra style data improved streetwear recognition, but gothic and sporty boundary cases are still difficult.

The by-type results showed that jacket inputs performed best, with an average overall quality score of 1.750. Shoe inputs performed worst, with an average overall quality score of 0.625. This does not mean that shoe type prediction was weak. Instead, shoe inputs often caused style prediction errors, which led the recommender to retrieve items from the wrong style category.

Overall, this experiment showed that the current recommender is structurally reliable, but still limited by style prediction quality. The recommendation logic can usually select useful clothing categories, but it still struggles when the predicted style is wrong.

## 15. Experiment 13: Style Model Architecture Comparison

The thirteenth experiment focused on comparing different model architectures for the style classification task.

This experiment was created based on teacher feedback, which suggested that a relevant next step was to understand and test the differences between models such as MobileNet and EfficientNet.

The goal was to check whether changing the model architecture could improve real-world style classification compared with the current ResNet34-based approach.

The experiment compared three architectures:

- ResNet34
- MobileNetV3 Large
- EfficientNet-B0

All models were trained using the same improved style training setup. This included the original `split_style/train` data plus the extra targeted images from `style_extra`. The validation and curated test sets stayed unchanged, and the `real_world_test` set was used only for evaluation.

The results were:

| Model             | Curated accuracy | Curated macro F1 | Real-world accuracy | Real-world macro F1 | Model size |
| ----------------- | ---------------: | ---------------: | ------------------: | ------------------: | ---------: |
| ResNet34          |           0.7833 |           0.7777 |              0.5875 |              0.5898 |   81.34 MB |
| MobileNetV3 Large |           0.8167 |           0.8105 |              0.6250 |              0.6242 |   16.25 MB |
| EfficientNet-B0   |           0.8417 |           0.8422 |              0.5500 |              0.5541 |   15.60 MB |

MobileNetV3 Large achieved the best real-world performance. It improved real-world accuracy compared with the retrained ResNet34 model and was also much smaller in model size.

EfficientNet-B0 achieved the highest curated test accuracy, but it performed worst on the real-world test set. This confirmed an earlier project finding: better curated performance does not automatically mean better real-world generalization.

The class-level results showed that MobileNetV3 Large had the most balanced real-world recall. It did not fully solve the style classification problem, because sporty recall was still weak, but it performed better overall than the other tested architectures.

Based on this experiment, MobileNetV3 Large was selected as the best candidate style model for the next recommendation pipeline experiment. It still needed to be tested inside the full recommender before replacing the current ResNet34-based style model.

## 16. Experiment 14: Recommendation Evaluation with MobileNetV3 Style Classifier

The fourteenth experiment tested whether the MobileNetV3 Large style classifier improved the full recommendation pipeline.

The previous architecture comparison showed that MobileNetV3 Large had the best real-world style classification performance, with **0.6250** accuracy and **0.6242** macro F1-score. However, better standalone classification accuracy does not automatically mean better recommendation quality. Because of this, the model needed to be tested inside the actual recommender.

The experiment used the same setup as the previous 32-example recommendation evaluation, except for the style classifier.

| Component             | Previous setup                  | New setup                                              |
| --------------------- | ------------------------------- | ------------------------------------------------------ |
| Style classifier      | `style_resnet34_extra_data.pth` | `style_mobilenet_v3_large_architecture_comparison.pth` |
| Type classifier       | `type_resnet34_extra_data.pth`  | `type_resnet34_extra_data.pth`                         |
| Catalogue             | `dataset/cleaned`               | `dataset/cleaned`                                      |
| Embedding extractor   | ResNet34                        | ResNet34                                               |
| Ranking method        | Cosine similarity               | Cosine similarity                                      |
| Confidence thresholds | 0.60 style, 0.60 type           | 0.60 style, 0.60 type                                  |
| Evaluation subset     | 32 balanced real-world examples | Same 32 balanced real-world examples                   |

This made the comparison fair because only the style model changed.

The automatic evaluation results were:

| Metric                                 | Previous ResNet34 setup | New MobileNetV3 setup |
| -------------------------------------- | ----------------------: | --------------------: |
| Style prediction accuracy              |                  0.5625 |               0.65625 |
| Type prediction accuracy               |                  0.9375 |                0.9375 |
| Same-actual-type recommendation issues |                  2 / 32 |                2 / 32 |

MobileNetV3 improved style prediction accuracy by **0.09375**, which is a **9.375 percentage point improvement**. Type accuracy stayed the same because the type classifier was not changed. Same-actual-type issues also stayed the same at 2 out of 32, which makes sense because those issues are mainly caused by type prediction errors.

The manual evaluation also improved:

| Criterion                     | Previous ResNet34 score | New MobileNetV3 score | Difference |
| ----------------------------- | ----------------------: | --------------------: | ---------: |
| Structural validity           |                  1.8750 |                1.9375 |    +0.0625 |
| Style consistency             |                  1.3125 |               1.46875 |   +0.15625 |
| Visual coherence              |                  1.3125 |                1.3750 |    +0.0625 |
| Confidence warning usefulness |                  1.4688 |                1.5625 |    +0.0937 |
| Overall quality               |                  1.3125 |               1.40625 |   +0.09375 |

The biggest improvement was in style consistency. This is important because style consistency was one of the main weaknesses in the previous recommendation evaluation. The result shows that the improved style classifier helped the recommender retrieve items from a more suitable style category more often.

The overall quality distribution also improved:

| Quality          | Previous ResNet34 setup | New MobileNetV3 setup |
| ---------------- | ----------------------: | --------------------: |
| Bad              |                       7 |                     6 |
| Partially useful |                       8 |                     7 |
| Good             |                      17 |                    19 |

This means the number of good recommendations increased by 2, while bad recommendations decreased by 1.

Overall, this experiment confirmed that MobileNetV3 Large is better than the previous ResNet34 style classifier for the full recommendation pipeline. The improvement is not dramatic, but it is consistent across both automatic and manual evaluation. Based on this result, MobileNetV3 Large should replace the ResNet34 style classifier in the current prototype.

After the MobileNetV3 style classifier became the selected style model, the next experiment focused on the recommendation ranking method. Until this point, the recommender still used ResNet34 embeddings with cosine similarity to rank catalogue items. However, the previous evaluation showed that visual coherence was still weaker than structural validity. Because of this, Experiment 15 tested whether CLIP image embeddings could improve the visual quality of the selected recommendations.

The CLIP experiment kept the classifiers, catalogue, confidence thresholds, evaluation subset, and cosine similarity ranking method unchanged. Only the embedding extractor changed from ResNet34 to CLIP. The automatic metrics stayed the same, which was expected because the classifiers were not changed. The manual evaluation showed that CLIP improved visual coherence from 1.3750 to 1.6250 and overall quality from 1.40625 to 1.5625. The number of bad recommendations also dropped from 6 to 1. Based on this, CLIP image embeddings became the selected recommendation ranking method for the current prototype.

## 17. Experiment 15: CLIP Embedding Recommendation Ranking

The fifteenth experiment focused on improving the recommendation ranking method.

The previous MobileNetV3 recommendation experiment showed that the selected style classifier improved the full pipeline. However, visual coherence was still weaker than structural validity. This meant that the system usually recommended the correct clothing categories, but the selected items did not always form the best-looking outfit.

Until this point, the recommendation system used ResNet34 image embeddings with cosine similarity. These embeddings helped rank catalogue items by visual similarity, but they were not specifically designed for semantic image understanding or fashion-related visual matching.

Because of this, this experiment tested whether CLIP image embeddings could improve recommendation ranking.

The research question was:

**Does replacing ResNet34 image embeddings with CLIP image embeddings improve visual coherence and overall recommendation quality in the outfit recommendation pipeline?**

The experiment compared two setups:

| Component             | ResNet34 embedding baseline                            | CLIP embedding setup                                   |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------ |
| Style classifier      | `style_mobilenet_v3_large_architecture_comparison.pth` | `style_mobilenet_v3_large_architecture_comparison.pth` |
| Type classifier       | `type_resnet34_extra_data.pth`                         | `type_resnet34_extra_data.pth`                         |
| Catalogue             | `dataset/cleaned`                                      | `dataset/cleaned`                                      |
| Evaluation subset     | 32 balanced real-world examples                        | Same 32 balanced real-world examples                   |
| Embedding extractor   | ResNet34                                               | CLIP image encoder                                     |
| Ranking method        | Cosine similarity                                      | Cosine similarity                                      |
| Confidence thresholds | 0.60 style, 0.60 type                                  | 0.60 style, 0.60 type                                  |

Only the embedding extractor changed. This made the comparison fair because the classifiers, catalogue, evaluation subset, confidence thresholds, and ranking method stayed the same.

The automatic evaluation results were:

| Metric                                 | CLIP setup |
| -------------------------------------- | ---------: |
| Number of examples                     |         32 |
| Style accuracy                         |    0.65625 |
| Type accuracy                          |     0.9375 |
| Same-actual-type recommendation issues |     2 / 32 |
| Same-actual-type issue rate            |     0.0625 |
| Average number of recommendations      |        3.0 |

These automatic results stayed the same as the MobileNetV3 ResNet34 embedding baseline. This was expected because the style and type classifiers were not changed. The automatic metrics mainly checked classification and structural behaviour, not visual recommendation quality.

The manual evaluation showed the main difference:

| Criterion                     | ResNet34 embedding baseline | CLIP embedding setup | Difference |
| ----------------------------- | --------------------------: | -------------------: | ---------: |
| Structural validity           |                      1.9375 |               1.8750 |    -0.0625 |
| Style consistency             |                     1.46875 |              1.53125 |    +0.0625 |
| Visual coherence              |                      1.3750 |               1.6250 |    +0.2500 |
| Confidence warning usefulness |                      1.5625 |              1.71875 |   +0.15625 |
| Overall quality               |                     1.40625 |               1.5625 |   +0.15625 |

The most important improvement was visual coherence. It increased from **1.3750** to **1.6250**, which was the main goal of the experiment.

The overall quality score also improved from **1.40625** to **1.5625**.

The quality distribution changed as follows:

| Quality          | ResNet34 embedding baseline | CLIP embedding setup |
| ---------------- | --------------------------: | -------------------: |
| Bad              |                           6 |                    1 |
| Partially useful |                           7 |                   12 |
| Good             |                          19 |                   19 |

The number of good recommendations stayed the same, but the number of bad recommendations dropped from 6 to 1. This means that CLIP did not necessarily create more perfect recommendations, but it made the weak cases less bad and improved the stability of the ranking stage.

Overall, this experiment showed that CLIP embeddings are better than ResNet34 embeddings for recommendation ranking in the current prototype. CLIP improved visual coherence and overall recommendation quality while keeping the rest of the pipeline unchanged.

Based on this result, CLIP image embeddings should replace ResNet34 embeddings in the recommendation ranking stage.

## 18. Experiment 16: Style Error Analysis for Multi-Label Relabeling

The sixteenth experiment focused on preparing the style dataset for multi-label learning.

Until this point, the style classifier was trained as a single-label classifier. This meant that every image was forced into one style class only:

```text
formal OR gothic OR sporty OR streetwear
```

However, teacher feedback pointed out that many clothing items can belong to more than one aesthetic at the same time. For example, a black graphic t-shirt can be both gothic and streetwear, while a track jacket can be both sporty and streetwear.

The goal of this experiment was not to train a new model yet. The goal was to identify which training images should become multi-label examples.

The current MobileNetV3 style classifier was used to analyze images from:

    - split_style/train
    - split_style/val
    - split_style/test
    - style_extra
    - real_world_test

For each image, the notebook recorded:

    - true style
    - predicted style
    - top confidence
    - second predicted style
    - confidence margin
    - loss value
    - whether the prediction was correct
    - whether the image was a candidate for manual review

The analysis found 209 possible multi-label candidates across all sources. However, the real-world test set was not used for training or relabeling, because it must stay separate for fair evaluation.

Only trainable sources were used for the final training label file:

    - split_style_train
    - style_extra

The manually reviewed labels were then converted into a final multi-label training CSV.

The final training file contained 660 images:

| Label count | Number of images |
| ----------: | ---------------: |
|     1 label |              604 |
|    2 labels |               56 |

The final label totals were:

| Style label | Count |
| ----------- | ----: |
| formal      |   169 |
| gothic      |   147 |
| sporty      |   182 |
| streetwear  |   218 |

This experiment created the training data needed for the next experiment, where the style classifier was trained with a multi-label setup.

## 19. Experiment 17: Multi-Label Style Classification Training

The seventeenth experiment tested whether the selected MobileNetV3 style classifier could be improved by changing it from single-label classification to multi-label classification.

The previous style model used `CrossEntropyLoss` with softmax. This forces the model to choose one final style class for every image. However, fashion items can belong to more than one style at the same time. For example, a black graphic t-shirt can be both gothic and streetwear, while a track jacket can be both sporty and streetwear.

Because of this, the new model used `BCEWithLogitsLoss` with sigmoid outputs. This allowed each style to be predicted independently.

The model architecture stayed the same:

- MobileNetV3 Large
- pretrained ImageNet weights
- frozen feature extractor
- replaced final classifier layer
- four output labels: formal, gothic, sporty, streetwear

The model was trained using the multi-label training CSV created in Experiment 16. This file contained 660 training images, including 604 single-label images and 56 manually reviewed multi-label images.

The training results showed that the model learned successfully:

| Metric                         | Result |
| ------------------------------ | -----: |
| Best validation top-1 accuracy | 0.8000 |
| Best validation macro F1       | 0.7970 |

The model was then evaluated on the curated test set and real-world test set.

| Evaluation set  | Top-1 accuracy | Macro F1 |
| --------------- | -------------: | -------: |
| Curated test    |         0.8000 |   0.7968 |
| Real-world test |         0.6250 |   0.6252 |

The real-world top-1 accuracy stayed the same as the previous single-label MobileNetV3 model. This means that multi-label training did not improve the model's ability to choose one main style.

However, the multi-label output was still useful. A threshold sweep was performed to find a practical sigmoid threshold. A threshold of 0.35 was selected because it produced a reasonable number of multi-style predictions without creating too many empty predictions.

To make the system usable in the application, a top-1 fallback was added. This means that if no style reaches the threshold, the model still returns the highest scoring style.

With threshold 0.35 and top-1 fallback, the real-world output became:

| Metric                   |  Result |
| ------------------------ | ------: |
| Zero-label predictions   |       0 |
| Multi-label predictions  | 31 / 80 |
| Average predicted labels |  1.4125 |

This showed that the multi-label model was useful for recommendation, even though it did not improve top-1 classification accuracy.

The main conclusion is that the multi-label model should not be selected because it is more accurate. It should be selected because it gives the recommendation system more flexible style information. Instead of forcing one aesthetic, the model can return combined style directions such as sporty + streetwear, gothic + streetwear, or formal + gothic.

## 20. Experiment 18: Multi-Label Recommendation Evaluation

The eighteenth experiment tested whether the new multi-label style predictions improved outfit recommendations.

The previous experiment showed that the multi-label MobileNetV3 model could return combined style outputs, such as sporty + streetwear or gothic + streetwear. However, this still needed to be tested inside the recommendation pipeline.

The experiment compared two recommendation modes:

| Mode             | Description                                          |
| ---------------- | ---------------------------------------------------- |
| old_single_style | Uses only the main predicted style                   |
| new_multi_style  | Uses all predicted styles from the multi-label model |

A smaller evaluation set of 16 real-world examples was used to reduce manual scoring work:

- 4 formal examples
- 4 gothic examples
- 4 sporty examples
- 4 streetwear examples

The selected examples focused mostly on difficult cases where the multi-label model produced more than one possible style. This made the experiment useful for checking whether multi-label prediction actually helped recommendation quality.

Each recommendation was manually scored from 0 to 2 using four criteria:

- style match
- type match
- visual coherence
- overall quality

The results were:

| Mode             | Avg style match | Avg type match | Avg visual coherence | Avg overall quality | Avg total score |
| ---------------- | --------------: | -------------: | -------------------: | ------------------: | --------------: |
| old_single_style |          1.0625 |         2.0000 |               1.1250 |              1.3125 |          5.5000 |
| new_multi_style  |          1.0625 |         2.0000 |               0.8750 |              1.0000 |          4.9375 |

The paired comparison showed:

| Result          | Count |
| --------------- | ----: |
| old mode better |     7 |
| new mode better |     6 |
| equal           |     3 |

The results showed that the new multi-style recommendation mode did not improve the recommendations overall. The old single-style mode had a higher average total score.

The main issue was that the new multi-style mode only widened the allowed style pool. It did not improve how items were selected from that pool. Because item selection was still random, the system sometimes picked items from different style directions that did not work well together visually.

This experiment was still useful because it showed an important limitation: multi-label prediction alone is not enough. The recommendation system also needs a stronger ranking method to select visually compatible items.

The main conclusion is that multi-label style prediction should not be used as a simple random filter. It needs to be combined with a better ranking step, such as CLIP visual similarity.

## 21. Experiment 19: Multi-Label CLIP Recommendation Ranking

The nineteenth experiment improved the multi-label recommendation approach by adding CLIP visual similarity ranking.

Experiment 18 showed that multi-label prediction alone was not enough. The model could return multiple possible styles, but the recommender still selected items randomly from the allowed style pool. This sometimes reduced outfit coherence because the selected items matched different aesthetics but did not work well together visually.

Because of this, Experiment 19 tested a stronger recommendation approach:

```text
multi-label style prediction
+ clothing type filtering
+ CLIP visual similarity ranking
```

The experiment compared two recommendation modes:

| Mode                        | Description                                                              |
| --------------------------- | ------------------------------------------------------------------------ |
| previous_random_multi_style | Uses multi-label styles, then randomly selects items                     |
| new_multi_style_clip_ranked | Uses multi-label styles, then ranks candidate items with CLIP similarity |

The same 16 evaluation examples from Experiment 18 were reused. This made the comparison fair because the input images stayed exactly the same.

The CLIP-ranked recommender worked as follows:

1. Predict the clothing type of the input image.
2. Predict one or more possible styles using the multi-label style model.
3. Find the missing clothing types.
4. Filter catalogue items by the allowed predicted styles.
5. Rank candidate items using CLIP cosine similarity.
6. Select the highest-ranked item for each missing clothing type.

The results showed a clear improvement:

| Mode                        | Avg style match | Avg type match | Avg visual coherence | Avg overall quality | Avg total score |
| --------------------------- | --------------: | -------------: | -------------------: | ------------------: | --------------: |
| previous_random_multi_style |          1.0625 |         2.0000 |               0.8750 |              1.0000 |          4.9375 |
| new_multi_style_clip_ranked |          1.6875 |         2.0000 |               1.6875 |              1.8125 |          7.1875 |

The average total score improved by 2.25 points on an 8-point scale.

The paired comparison also showed that CLIP ranking improved most examples:

| Result             | Count |
| ------------------ | ----: |
| CLIP-ranked better |    11 |
| Random better      |     3 |
| Equal              |     2 |

The strongest improvements were in visual coherence and overall quality. This showed that the issue in Experiment 18 was not the multi-label prediction itself. The issue was the random item selection.

The conclusion is that multi-label style prediction becomes useful when it is combined with CLIP ranking. Multi-label prediction gives the system more possible style directions, while CLIP ranking helps select items that visually fit the uploaded clothing item.

Based on this result, the best tested recommendation architecture is:

```text
type classifier
+ multi-label MobileNetV3 style classifier
+ threshold 0.35 with top-1 fallback
+ CLIP visual similarity ranking
```

## 22. Overall Results Comparison

The table below summarizes the main experiments and results from the project.

| Experiment                                             | Main goal                                                                           |                                             Curated/Internal Result |                                                                                                                             Real-world Result | Main conclusion                                                                                                         |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------------------------------- |
| Style classification baseline                          | Predict fashion style                                                               |                                                0.8417 test accuracy |                                                                                                                    0.4750 real-world accuracy | The model learned style patterns on clean data but struggled with realistic images.                                     |
| Clothing type classification baseline                  | Predict clothing type                                                               |                                         1.00 internal test accuracy |                                                                                              0.90 small external / 0.7500 real-world accuracy | Clothing type classification was more reliable than style classification, but still made real-world errors.             |
| Rule-based recommendation                              | Recommend same-style, different-type items                                          |                                                         Qualitative |                                                                                                               Not tested on real-world images | The pipeline worked, but recommendations were randomly selected.                                                        |
| Embedding-based recommendation                         | Rank recommendations by visual similarity                                           |                                                         Qualitative |                                                                                                     Not initially tested on real-world images | Embeddings improved recommendation ranking compared with random selection.                                              |
| Real-world evaluation                                  | Test generalization                                                                 |                                                                 N/A |                                                                                                                   Style: 0.4750, Type: 0.7500 | Style prediction was the main weakness, but type errors also affected the recommender.                                  |
| Style fine-tuning                                      | Improve style classifier using partial fine-tuning                                  |                                             0.9417 curated accuracy |                                                                                                                    0.4250 real-world accuracy | Fine-tuning improved clean-data performance but did not improve real-world generalization.                              |
| Style dataset improvement                              | Improve style classifier using extra targeted data                                  |                                             0.8667 curated accuracy |                                                                                                                    0.6000 real-world accuracy | Extra data improved real-world style performance and was more useful than fine-tuning alone.                            |
| Recommendation with improved style model               | Test recommender with improved style classifier                                     |                                                         Qualitative |                                                                                                                                   Qualitative | Recommendations improved when predictions were correct, but errors in style/type still affected output.                 |
| Recommendation with confidence safeguards              | Add warnings for uncertain predictions                                              |                                                         Qualitative |                                                                                 4 reliable, 2 type_uncertain, 2 style_uncertain on 8 examples | Confidence warnings improved transparency, but high-confidence wrong predictions still occurred.                        |
| Type dataset improvement                               | Improve type classifier using extra targeted data                                   |                                    1.0000 curated / 0.9000 external |                                                                                                                    0.8875 real-world accuracy | Targeted type data improved real-world type prediction while preserving clean-data performance.                         |
| Recommendation with improved models                    | Test recommender with improved style and type models                                |                                                         Qualitative |                                                                                     Same-actual-type issues reduced from 2 to 0 on 8 examples | Improved type prediction reduced structural recommendation failures.                                                    |
| Recommendation evaluation framework                    | Evaluate final prototype systematically                                             |                                       Automatic + manual evaluation |                                                                             17 good, 8 partially useful, 7 bad recommendations on 32 examples | The recommender is structurally strong, but style consistency and visual coherence remain weaker.                       |
| Style model architecture comparison                    | Compare ResNet34, MobileNetV3 Large, and EfficientNet-B0 for style classification   |          EfficientNet-B0 had the highest curated accuracy at 0.8417 |                                                                                  MobileNetV3 Large had the best real-world accuracy at 0.6250 | MobileNetV3 Large was the best candidate because it improved real-world performance and was much smaller than ResNet34. |
| Recommendation evaluation with MobileNetV3 style model | Test whether MobileNetV3 improves the full recommendation pipeline                  |                                       Automatic + manual evaluation | Style accuracy improved from 0.5625 to 0.65625; overall quality improved from 1.3125 to 1.40625; good recommendations increased from 17 to 19 | MobileNetV3 improved the full pipeline and should replace the previous ResNet34 style classifier.                       |
| CLIP embedding recommendation ranking                  | Test whether CLIP improves recommendation ranking compared with ResNet34 embeddings |                                       Automatic + manual evaluation |     Visual coherence improved from 1.3750 to 1.6250; overall quality improved from 1.40625 to 1.5625; bad recommendations dropped from 6 to 1 | CLIP embeddings improved the ranking stage and should replace ResNet34 embeddings in the current prototype.             |
| Style error analysis for multi-label relabeling        | Identify ambiguous style images for multi-label training                            | Final training CSV: 660 images, 604 single-label and 56 multi-label |                                                                                                                                           N/A | Created a clean multi-label training file without using the real-world test set for training.                           |
| Multi-label style classification training              | Train MobileNetV3 with BCEWithLogitsLoss and sigmoid outputs                        |                                      Curated top-1 accuracy: 0.8000 |                     Real-world top-1 accuracy: 0.6250; 31 / 80 real-world images received multi-style outputs after threshold 0.35 + fallback | Multi-label training did not improve top-1 accuracy, but created useful combined style outputs.                         |
| Multi-label recommendation evaluation                  | Test whether multi-label prediction alone improves recommendations                  |                                    Manual evaluation on 16 examples |                                                                            Random multi-style score: 4.9375 vs old single-style score: 5.5000 | Multi-label filtering alone was not enough and reduced coherence when item selection was random.                        |
| Multi-label CLIP recommendation ranking                | Combine multi-label style prediction with CLIP visual ranking                       |                               Manual evaluation on same 16 examples |                                                                     CLIP-ranked multi-style score: 7.1875 vs random multi-style score: 4.9375 | Multi-label prediction becomes useful when combined with CLIP ranking, making this the best architecture so far.        |

## 23. Selected Models for Current Prototype

Based on the experiments, the current prototype uses the following components:

| Component                | Selected approach                                                         | Reason                                                                                                                                                                                                                                                                                                  |
| ------------------------ | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Style classifier         | Multi-label MobileNetV3 Large with `BCEWithLogitsLoss` and sigmoid output | The previous single-label MobileNetV3 model had the same real-world top-1 accuracy, but the multi-label version can output combined aesthetics such as sporty + streetwear or gothic + streetwear. This gives the recommender more flexible style information.                                          |
| Clothing type classifier | `type_resnet34_extra_data.pth`                                            | This model improved real-world type accuracy from 0.7500 to 0.8875 while preserving strong curated and external performance.                                                                                                                                                                            |
| Recommendation ranking   | CLIP image embeddings with cosine similarity                              | CLIP improved recommendation visual coherence and became much stronger when combined with multi-label style filtering. In the final 16-example evaluation, CLIP-ranked multi-style recommendation achieved an average total score of 7.1875 compared with 4.9375 for random multi-style recommendation. |
| Threshold handling       | Sigmoid threshold 0.35 with top-1 fallback                                | This produced no empty style predictions and allowed useful multi-style outputs for realistic images.                                                                                                                                                                                                   |
| Confidence safeguards    | Confidence reporting and warnings                                         | These make uncertain predictions more transparent for the user.                                                                                                                                                                                                                                         |

The selected style model is not chosen because it improves top-1 style accuracy. The real-world top-1 accuracy stayed at 0.6250, which is similar to the previous single-label MobileNetV3 model.

The reason for selecting the multi-label style model is that it supports recommendation better. Fashion items often combine aesthetics, and forcing every item into only one style can remove useful information. The multi-label model allows the system to keep multiple possible style directions.

However, Experiment 18 showed that multi-label prediction alone is not enough. When multiple styles were only used as a wider filter, recommendation quality decreased. The final improvement came from combining multi-label prediction with CLIP ranking.

Therefore, the selected final recommendation pipeline is:

```text
type classifier
+ multi-label MobileNetV3 style classifier
+ threshold 0.35 with top-1 fallback
+ CLIP visual similarity ranking
```

This is the strongest tested architecture so far.

## 24. Main Development Decisions

Several important development decisions were made during the project.

1. The project was scoped down from direct outfit compatibility to classification-supported recommendation because outfit compatibility is subjective and difficult to evaluate directly.

2. Style and clothing type were treated as intermediate representations for recommendation.

3. ResNet34 transfer learning was used at the start because the dataset was manually curated and relatively small.

4. The first recommendation prototype was rule-based to prove the basic pipeline before adding more complex ranking.

5. Embedding-based retrieval was added to improve recommendation quality compared with random selection.

6. A real-world evaluation set was created because curated test results were not enough to prove generalization.

7. Fine-tuning was tested, but the result showed that better curated performance does not automatically mean better real-world performance.

8. Extra targeted data was added after the error analysis showed that streetwear was the weakest class.

9. The improved style model was integrated back into the recommender to test whether model improvement helped the full pipeline.

10. The type classifier was improved after recommendation examples showed that type errors caused structural failures in the output.

11. The improved type model was selected because it reduced same-actual-type recommendation issues from 2 to 0 on the selected real-world examples.

12. A manual recommendation evaluation framework was added because visual inspection alone was not repeatable enough to compare future improvements.

13. The evaluation results showed that the next improvement should focus on style boundary cases, especially gothic, sporty, and streetwear confusion.

14. A model architecture comparison was added after teacher feedback suggested testing models such as MobileNet and EfficientNet.

15. MobileNetV3 Large was selected as the best single-label style model because it achieved the strongest real-world style result while being much smaller than ResNet34.

16. MobileNetV3 Large was tested inside the full recommendation pipeline before replacing ResNet34, because standalone classifier accuracy was not enough to prove recommendation improvement.

17. The recommendation ranking method was kept unchanged during the MobileNetV3 experiment so that the effect of changing the style classifier could be isolated.

18. CLIP embeddings were tested against the ResNet34 embedding baseline while keeping the classifiers, catalogue, confidence thresholds, and evaluation subset unchanged.

19. CLIP embeddings were selected for recommendation ranking because they improved visual coherence and overall quality, and reduced the number of bad recommendations.

20. Teacher feedback about overlapping aesthetics was addressed by testing multi-label style classification with `BCEWithLogitsLoss` and sigmoid outputs.

21. A separate error analysis notebook was created before training the multi-label model. This avoided blindly changing the loss function without checking whether the dataset labels supported multi-label learning.

22. Only trainable sources were used for multi-label relabeling. The real-world test set stayed separate so that evaluation remained fair.

23. The multi-label model was not selected because it improved top-1 accuracy. It was selected because it produced useful combined style outputs for recommendation.

24. Multi-label prediction alone was tested inside the recommendation pipeline before integration. This showed that simply allowing more styles into the recommendation pool can reduce visual coherence if item selection remains random.

25. CLIP ranking was added after the random multi-style recommendation experiment showed that the main weakness was candidate selection, not the multi-label prediction itself.

26. The final recommendation architecture combines multi-label style prediction with CLIP ranking because this produced the strongest manual recommendation scores.

27. The final architecture was selected based on full recommendation quality, not only classifier accuracy. This is important because the application goal is to recommend useful outfits, not only classify images.

## 25. Final Conclusion

The final system is a working prototype for fashion recommendation based on image classification, multi-label style prediction, and embedding-based retrieval.

The system predicts the clothing type of an uploaded item and predicts one or more possible fashion styles. Instead of forcing the style model to choose only one aesthetic, the final version can return combined style directions such as sporty + streetwear, gothic + streetwear, or formal + gothic.

The strongest type-related result was the dataset-improved type model, which increased real-world type accuracy from 0.7500 to 0.8875. This improved the structural reliability of the recommender because it reduced cases where the system recommended the same actual clothing type as the input.

The strongest style-related classifier result was MobileNetV3 Large. In the architecture comparison, it achieved the best real-world style result, with 0.6250 accuracy and 0.6242 macro F1-score. This model was later adapted into a multi-label version using `BCEWithLogitsLoss` and sigmoid outputs.

The multi-label model did not improve real-world top-1 style accuracy, but it improved the information available to the recommender. With a sigmoid threshold of 0.35 and top-1 fallback, it produced no empty predictions and generated multi-style outputs for 31 out of 80 real-world test images.

However, the project also showed that multi-label prediction alone is not enough. When multiple styles were used only as a wider random recommendation filter, the average total recommendation score decreased from 5.5000 to 4.9375. This showed that the recommender needed stronger ranking logic.

The best final result came from combining multi-label style prediction with CLIP ranking. In the final recommendation evaluation, CLIP-ranked multi-style recommendations achieved an average total score of 7.1875, compared with 4.9375 for random multi-style recommendation. CLIP-ranked recommendations were better in 11 out of 16 examples.

The final selected prototype therefore uses:

```text
multi-label MobileNetV3 Large style classification
+ dataset-improved ResNet34 clothing type classification
+ threshold 0.35 with top-1 fallback
+ CLIP image similarity ranking
```

This final architecture is stronger than the previous version because it combines flexible style understanding with visual similarity ranking. The system is still not perfect, but it now produces more coherent and useful recommendations than the earlier single-style or random multi-style approaches.

Overall, the project demonstrates that classification and embedding retrieval can support a basic fashion recommendation system. The final prototype is not a complete fashion stylist yet, because it does not fully understand colour matching, fit, season, occasion, or user preference. However, it provides a solid technical foundation and shows clear improvement through iterative experiments.

## 26. Next Steps

The next development steps are:

1. Integrate the multi-label MobileNetV3 style model into the FastAPI backend.

2. Replace single-style filtering with multi-label style filtering using threshold 0.35 and top-1 fallback.

3. Replace random candidate selection with CLIP-ranked candidate selection in the recommendation endpoint.

4. Keep the current dataset-improved type classifier, because it remains the strongest tested clothing type model.

5. Cache CLIP embeddings for catalogue items so recommendations can be generated quickly without recalculating embeddings every request.

6. Update the frontend so it can show multiple predicted styles instead of only one style.

7. Show recommendation reliability clearly to the user, especially when the model predicts multiple possible styles.

8. Add a larger user evaluation later to check whether real users also prefer the CLIP-ranked multi-style recommendations.

9. Improve the recommendation system further by adding extra clothing attributes, such as colour, season, occasion, material, and fit.

10. Keep the real-world test set separate from training data so future improvements can still be evaluated fairly.
