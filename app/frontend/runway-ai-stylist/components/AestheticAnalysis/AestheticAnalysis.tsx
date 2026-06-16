"use client";

import type { RecommendationGroup, RecommendationResponse } from "@/lib/api";
import { Info } from "lucide-react";
import { useState } from "react";

import styles from "./AestheticAnalysis.module.css";

type AestheticAnalysisProps = {
  result: RecommendationResponse;
  recommendationGroups: RecommendationGroup[];
  selectedStyleIndex: number;
  onSelectStyle: (index: number) => void;
};

function formatLabel(value: string) {
  if (value === "tshirt") return "T-shirt";

  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatConfidence(value: number) {
  return `${Math.round(value * 100)}%`;
}

function getReliabilityLabel(reliability: string) {
  return reliability.charAt(0).toUpperCase() + reliability.slice(1);
}

export default function AestheticAnalysis({
  result,
  recommendationGroups,
  selectedStyleIndex,
  onSelectStyle,
}: AestheticAnalysisProps) {
  const [isReliabilityOpen, setIsReliabilityOpen] = useState(false);

  const selectedStyles =
    result.analysis?.predicted_styles ??
    result.predicted_styles ??
    result.style_candidates.map((candidate) => candidate.style);

  const styleScores =
    result.analysis?.style_scores ??
    result.style_scores ??
    result.style_probabilities ??
    {};

  const styleThreshold =
    result.analysis?.style_threshold ?? result.style_threshold ?? 0.35;

  const styleOptions = selectedStyles.map((style, index) => {
    const candidate = result.style_candidates.find(
      (styleCandidate) => styleCandidate.style === style,
    );

    return {
      style,
      confidence:
        styleScores[style] ??
        candidate?.confidence ??
        (index === 0 ? result.style_confidence : 0),
      reason:
        index === 0
          ? "Primary selected aesthetic"
          : `Selected because it passed the ${formatConfidence(styleThreshold)} threshold`,
    };
  });

  const safeSelectedStyleIndex =
    selectedStyleIndex >= 0 && selectedStyleIndex < styleOptions.length
      ? selectedStyleIndex
      : 0;

  const activeStyleOption =
    styleOptions[safeSelectedStyleIndex] ?? styleOptions[0];

  const hasMultipleDirections = styleOptions.length > 1;

  const styleProbabilityEntries = Object.entries(
    result.style_probabilities ?? {},
  ).sort(([, firstValue], [, secondValue]) => secondValue - firstValue);

  const mainAesthetic =
    result.analysis?.main_style ?? result.main_style ?? result.predicted_style;

  const mainAestheticConfidence =
    styleScores[mainAesthetic] ?? result.style_confidence;

  const selectedAesthetic = activeStyleOption?.style ?? mainAesthetic;
  const selectedAestheticConfidence =
    activeStyleOption?.confidence ?? mainAestheticConfidence;

  const reliabilityDescription =
    result.reliability === "high"
      ? "We are confident in both the style and garment type."
      : result.reliability === "medium"
        ? "The result is usable, but one prediction may still need review."
        : "The result is exploratory because the style confidence is low.";

  return (
    <section className={styles.analysisSection}>
      <div className={styles.sectionHeader}>
        <span className={styles.sectionEyebrow}>Chapter Two</span>

        <h2>
          The <em>Analysis</em>
        </h2>

        <div className={styles.titleDivider} />

        <p>
          We looked at your garment’s style, shape, and overall mood to suggest
          outfit directions that fit it best.
        </p>
      </div>

      <div className={styles.editorialSummary}>
        <span className={styles.editorialLabel}>Garment profile</span>

        <p className={styles.editorialSentence}>
          Your garment reads as
          <br />
          <button
            type="button"
            className={styles.inlineAestheticButton}
            onClick={() => {
              document
                .getElementById("aesthetic-directions")
                ?.scrollIntoView({ behavior: "smooth", block: "center" });
            }}
          >
            {formatLabel(mainAesthetic)}
          </button>{" "}
          {formatLabel(result.predicted_type).toLowerCase()}.
        </p>

        <div className={styles.editorialMeta}>
          <div className={styles.metaMetric}>
            <span>
              <strong>{formatConfidence(mainAestheticConfidence)}</strong> style
              confidence
            </span>
            <div className={styles.metaBar}>
              <div
                className={styles.metaBarFill}
                style={{ width: formatConfidence(mainAestheticConfidence) }}
              />
            </div>
          </div>

          <span className={styles.metaDot}>·</span>

          <div className={styles.metaMetric}>
            <span>
              <strong>{formatConfidence(result.type_confidence)}</strong>{" "}
              garment confidence
            </span>
            <div className={styles.metaBar}>
              <div
                className={styles.metaBarFill}
                style={{ width: formatConfidence(result.type_confidence) }}
              />
            </div>
          </div>

          <span className={styles.metaDot}>·</span>

          <div className={`${styles.reliabilityInline} ${styles.metaMetric}`}>
            <span>
              <strong>{getReliabilityLabel(result.reliability)}</strong>{" "}
              reliability
            </span>

            <span className={styles.infoHoverArea}>
              <Info className={styles.infoIcon} strokeWidth={1.5} />
            </span>

            <p className={styles.reliabilityPopover}>
              {reliabilityDescription}
            </p>
          </div>
        </div>
      </div>

      <div className={styles.compactAnalysisGrid}>
        <div className={styles.directionPanel}>
          <div className={styles.directionHeader}>
            <span className={styles.cardLabel}>Aesthetic interpretation</span>

            <h3>
              {hasMultipleDirections
                ? "Detected aesthetic pool"
                : "Recommended aesthetic direction"}
            </h3>

            <p>
              {hasMultipleDirections
                ? "The model detected multiple possible aesthetics. The system uses these selected styles as the recommendation pool and ranks matching items with CLIP similarity."
                : "The model found one selected aesthetic for the recommendation pool."}
            </p>
          </div>

          <div className={styles.directionOptions}>
            {styleOptions.map((option, index) => (
              <button
                key={option.style}
                type="button"
                onClick={() => onSelectStyle(index)}
                className={`${styles.directionOption} ${
                  safeSelectedStyleIndex === index ? styles.active : ""
                }`}
              >
                <div>
                  <span className={styles.directionName}>
                    {formatLabel(option.style)}
                  </span>

                  <span className={styles.directionReason}>
                    {index === 0
                      ? "Primary selected aesthetic"
                      : "Also selected"}
                  </span>
                </div>

                <span className={styles.directionConfidence}>
                  {formatConfidence(option.confidence)}
                </span>
              </button>
            ))}
          </div>

          {styleOptions.length > 0 && (
            <p className={styles.activeDirectionNote}>
              Recommendation pool:{" "}
              <strong>
                {styleOptions
                  .map((option) => formatLabel(option.style))
                  .join(" + ")}
              </strong>
              . Items are ranked with CLIP visual similarity.
            </p>
          )}
        </div>

        {styleProbabilityEntries.length > 0 && (
          <div className={styles.probabilityPanel}>
            <div className={styles.probabilityHeader}>
              <span className={styles.cardLabel}>
                Style probability breakdown
              </span>
              <p>
                How the classifier distributed confidence across aesthetics.
              </p>
            </div>

            <div className={styles.probabilityList}>
              {styleProbabilityEntries.map(([style, value]) => (
                <div key={style} className={styles.probabilityRow}>
                  <span className={styles.probabilityName}>
                    {formatLabel(style)}
                  </span>

                  <div className={styles.probabilityTrack}>
                    <div
                      className={styles.probabilityFill}
                      style={{ width: `${Math.round(value * 100)}%` }}
                    />
                  </div>

                  <strong>{formatConfidence(value)}</strong>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {result.styling_notes && (
        <details className={styles.explanationDisclosure}>
          <summary>
            <span>How was this generated?</span>
            <span className={styles.explanationHint}>Open explanation</span>
          </summary>

          <div className={styles.explanationContent}>
            <p>{result.styling_notes}</p>
          </div>
        </details>
      )}
    </section>
  );
}
