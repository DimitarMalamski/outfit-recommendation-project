# Outfit Recommendation System

This repository contains the source code, notebooks, datasets, trained models, results, and documentation for the Outfit Recommendation System project.

The goal of the project is to recommend outfit items based on one uploaded clothing item. The final prototype uses clothing type prediction, multi-label style prediction, and CLIP-based visual ranking to generate outfit suggestions.

## Final prototype

The final application is called **Runway AI Stylist**.

It allows a user to:

- upload a clothing image
- receive a garment analysis
- see detected clothing type and possible styles
- generate outfit recommendations
- switch between combined or focused style recommendations
- refresh individual recommended items

The application uses:

- **React** for the frontend
- **FastAPI** for the backend
- **MobileNetV3 Large** for multi-label style classification
- **ResNet34** for clothing type classification
- **CLIP embeddings** for recommendation ranking

## Live demo

The application is hosted online and can be accessed here:

**Frontend:** [Runway AI Stylist](https://outfit-recommendation-project.vercel.app/)  
**Backend/API:** [FastAPI backend](https://huggingface.co/spaces/DimitarM/runway-ai-stylist-api)

The frontend is responsible for the user interface, image upload flow, recommendation mode selection, and displaying generated outfits. The backend runs the AI pipeline, including image validation, garment analysis, CLIP embedding generation, and recommendation ranking.

Because the backend loads machine learning models and CLIP resources, the first request after inactivity may `take longer`. After the models are loaded, later recommendations are processed faster.

## Repository structure

```text
app/          Web application source code
dataset/      Clothing image datasets used for training and evaluation
docs/         Main project documentation and reports
htmls/        Exported notebook or report HTML files
notebooks/    Experiment notebooks, ordered by development step
notes/        Supporting notes
pdfs/         Final exported PDF documents
results/      Evaluation outputs, metrics, and generated result files
scripts/      Reusable scripts for training, evaluation, or processing
```

## Main documentation

The most important documents are located in `docs/` or `pdfs/`.

Recommended reading order:

1. **Project Proposal**  
   Explains the project idea, relevance, target users, scope, stakeholders, and planned approach.

2. **Development Summary**  
   Summarizes the machine learning experiments, model improvements, evaluation results, and final model selection.

3. **Application Development Report**  
   Explains how the selected AI pipeline was integrated into the web application and how the main features were implemented.

## Experiments

The `notebooks/` folder contains the experiments in order. Each notebook represents one development step, starting from baseline classification models and ending with the final multi-label CLIP-ranked recommendation approach.

Examples include:

- style classification baseline
- clothing type classification baseline
- rule-based recommendation
- embedding-based recommendation
- real-world evaluation
- dataset improvement
- model architecture comparison
- CLIP recommendation ranking
- multi-label style classification
- multi-label CLIP recommendation ranking

The final selected architecture is:

```text
multi-label MobileNetV3 Large style classification
+ improved ResNet34 clothing type classification
+ threshold 0.35 with top-1 fallback
+ CLIP image similarity ranking
```

## Results

The `results/` folder contains saved outputs from model evaluation and recommendation experiments.

The main results are summarized in the Development Summary report, including:

- style classification results
- clothing type classification results
- real-world evaluation results
- recommendation quality comparisons
- final model selection reasoning

## Models

The `models/` folder contains the trained model files used during experimentation and in the final prototype.

The final prototype uses:

- **Multi-label MobileNetV3 Large** for style prediction
- **Improved ResNet34** for clothing type prediction
- **CLIP catalogue embeddings** for recommendation ranking

The model files are included in the repository so the selected final models can be inspected together with the notebooks, results, and documentation.

The final selected architecture is:

```text
multi-label MobileNetV3 Large style classification
+ improved ResNet34 clothing type classification
+ threshold 0.35 with top-1 fallback
+ CLIP image similarity ranking
```

The model training process, model comparison, and model selection reasoning are explained in the **Development Summary** report.

## Application

The application source code is stored in the `app/` folder.

The frontend handles user interaction, image upload, recommendation mode selection, and displaying the generated results.

The backend handles image validation, model prediction, CLIP embedding generation, recommendation ranking, and communication with the frontend.

## Notes

This project is a prototype and is limited to the current project scope. It focuses on basic outfit compatibility using clothing type, style, and visual similarity.

It does not fully handle personalization, body type, skin tone, occasion, season, material, or fit. These limitations are discussed in the documentation as future improvements.
