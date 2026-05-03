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

Finally, the improved style model was tested inside the embedding-based recommendation pipeline. The results showed that recommendations became more useful when style prediction was correct, but the system is still affected by style and clothing type prediction errors.

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

The final experiment tested the embedding-based recommendation system using the improved style classifier.

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

## 12. Overall Results Comparison

The table below summarizes the main experiments and results from the project.

| Experiment                                | Main goal                                          |     Curated/Internal Result |                                             Real-world Result | Main conclusion                                                                                         |
| ----------------------------------------- | -------------------------------------------------- | --------------------------: | ------------------------------------------------------------: | ------------------------------------------------------------------------------------------------------- |
| Style classification baseline             | Predict fashion style                              |        0.8417 test accuracy |                                    0.4750 real-world accuracy | The model learned style patterns on clean data but struggled with realistic images.                     |
| Clothing type classification baseline     | Predict clothing type                              | 1.00 internal test accuracy |              0.90 small external / 0.7500 real-world accuracy | Clothing type classification was more reliable than style classification.                               |
| Rule-based recommendation                 | Recommend same-style, different-type items         |                 Qualitative |                               Not tested on real-world images | The pipeline worked, but recommendations were randomly selected.                                        |
| Embedding-based recommendation            | Rank recommendations by visual similarity          |                 Qualitative |                     Not initially tested on real-world images | Embeddings improved recommendation ranking compared with random selection.                              |
| Real-world evaluation                     | Test generalization                                |                         N/A |                                   Style: 0.4750, Type: 0.7500 | Style prediction was the main weakness of the system.                                                   |
| Style fine-tuning                         | Improve style classifier using partial fine-tuning |     0.9417 curated accuracy |                                    0.4250 real-world accuracy | Fine-tuning improved clean-data performance but did not improve real-world generalization.              |
| Style dataset improvement                 | Improve style classifier using extra targeted data |     0.8667 curated accuracy |                                    0.6000 real-world accuracy | Extra data improved real-world style performance and was more useful than fine-tuning alone.            |
| Recommendation with improved style model  | Test recommender with improved style classifier    |                 Qualitative |                                                   Qualitative | Recommendations improved when predictions were correct, but errors in style/type still affected output. |
| Recommendation with confidence safeguards | Add warnings for uncertain predictions             |                 Qualitative | 4 reliable, 2 type_uncertain, 2 style_uncertain on 8 examples | Confidence warnings improved transparency, but high-confidence wrong predictions still occurred.        |

## 13. Selected Models for Current Prototype

Based on the experiments, the current prototype uses the following models:

| Component                | Selected model                       | Reason                                                                                                                                                       |
| ------------------------ | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Style classifier         | `style_resnet34_extra_data.pth`      | This model achieved the best real-world style accuracy, improving from 0.4750 to 0.6000.                                                                     |
| Clothing type classifier | `type_resnet34.pth`                  | This model remained the strongest available type classifier, with 1.00 internal test accuracy, 0.90 small external accuracy, and 0.7500 real-world accuracy. |
| Recommendation ranking   | ResNet34 embedding feature extractor | This provides visual similarity ranking using cosine similarity and improves the recommender compared with random selection.                                 |

The selected style model is not the model with the highest curated test accuracy. The fine-tuned layer4 model achieved the highest curated test accuracy at 0.9417, but it performed worse on the real-world test set with 0.4250 accuracy. Because the recommendation system is intended to work with realistic input images, the dataset-improved style model is selected instead.

The current recommendation prototype therefore uses the dataset-improved style classifier together with the existing clothing type classifier and embedding-based retrieval.

## 14. Main Development Decisions

Several important development decisions were made during the project.

1. The project was scoped down from direct outfit compatibility to classification-supported recommendation because outfit compatibility is subjective and difficult to evaluate directly.

2. Style and clothing type were treated as intermediate representations for recommendation.

3. ResNet34 transfer learning was used because the dataset was manually curated and relatively small.

4. The first recommendation prototype was rule-based to prove the basic pipeline before adding more complex ranking.

5. Embedding-based retrieval was added to improve recommendation quality compared with random selection.

6. A real-world evaluation set was created because curated test results were not enough to prove generalization.

7. Fine-tuning was tested, but the result showed that better curated performance does not automatically mean better real-world performance.

8. Extra targeted data was added after the error analysis showed that streetwear was the weakest class.

9. The improved style model was integrated back into the recommender to test whether model improvement helped the full pipeline.

## 15. Final Conclusion

The final system is a working prototype for fashion recommendation based on image classification and embedding-based retrieval.

The system can predict the style and clothing type of an input image, then recommend visually similar items from the same predicted style and different clothing categories.

The strongest technical result was the dataset-improved style model, which increased real-world style accuracy from **0.4750** to **0.6000**. This showed that improving the dataset was more effective for real-world generalization than fine-tuning alone.

The project also showed that clothing type classification is more reliable than style classification. Style is more subjective and depends on visual cues that overlap between categories, especially gothic, sporty, and streetwear.

The recommendation pipeline works best when both style and type predictions are correct. When the style prediction is wrong, the system recommends items from the wrong style. When the type prediction is wrong, the system may recommend an item from the same actual clothing category.

This means that the current system is a useful prototype, but not yet a complete outfit compatibility model. It demonstrates that classification and embedding retrieval can support fashion recommendation, while also showing the limits of this approach.

## 16. Next Steps

The next development steps are:

1. Add confidence-based safeguards so the recommender can detect uncertain predictions.

2. Improve the clothing type classifier on real-world jacket and tshirt examples, because type prediction errors can cause the recommender to exclude the wrong clothing category.

3. Add more balanced boundary examples between streetwear, gothic, and sporty so the style classifier does not overpredict streetwear.

4. Improve recommendation ranking with color features or fashion-specific compatibility features.

5. Add a simple user evaluation where people rate whether the recommended outfits make sense.

6. Expand the recommendation catalogue with more varied clothing items so the system has better options to retrieve from.

7. Keep the real-world test set separate from training data so future improvements can be evaluated fairly.
