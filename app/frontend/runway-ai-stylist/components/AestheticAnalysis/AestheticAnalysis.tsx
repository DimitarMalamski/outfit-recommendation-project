"use client";

import type { RecommendationGroup, RecommendationResponse } from "@/lib/api";

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
  const activeGroup =
    recommendationGroups[selectedStyleIndex] ?? recommendationGroups[0];

  const hasMultipleDirections = recommendationGroups.length > 1;

  const styleProbabilityEntries = Object.entries(
    result.style_probabilities ?? {},
  ).sort(([, firstValue], [, secondValue]) => secondValue - firstValue);

  const selectedAesthetic = activeGroup?.style ?? result.predicted_style;
  const selectedAestheticConfidence =
    activeGroup?.confidence ?? result.style_confidence;

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
          We read this as a{" "}
          <button
            type="button"
            className={styles.inlineAestheticButton}
            onClick={() => {
              document
                .getElementById("aesthetic-directions")
                ?.scrollIntoView({ behavior: "smooth", block: "center" });
            }}
          >
            {formatLabel(selectedAesthetic)}
          </button>{" "}
          {formatLabel(result.predicted_type).toLowerCase()}.
        </p>

        <div className={styles.editorialMeta}>
          <span className={styles.metaItem}>
            <strong>{formatConfidence(selectedAestheticConfidence)}</strong>{" "}
            style confidence
          </span>

          <span className={styles.metaDot}>·</span>

          <span className={styles.metaItem}>
            <strong>{formatConfidence(result.type_confidence)}</strong> garment
            confidence
          </span>

          <span className={styles.metaDot}>·</span>

          <details className={`${styles.reliabilityInline} ${styles.metaItem}`}>
            <summary>
              <strong>{getReliabilityLabel(result.reliability)}</strong>{" "}
              reliability
            </summary>

            <p>{reliabilityDescription}</p>
          </details>
        </div>
      </div>

      <div className={styles.compactAnalysisGrid}>
        <div className={styles.directionPanel}>
          <div className={styles.directionHeader}>
            <span className={styles.cardLabel}>Aesthetic interpretation</span>

            <h3>
              {hasMultipleDirections
                ? "This item may fit more than one aesthetic"
                : "Recommended aesthetic direction"}
            </h3>

            <p>
              {hasMultipleDirections
                ? "Choose which aesthetic direction you want the outfit recommendations to follow."
                : "The model found one clear style direction for the recommendations."}
            </p>
          </div>

          <div className={styles.directionOptions}>
            {recommendationGroups.map((group, index) => (
              <button
                key={group.style}
                type="button"
                onClick={() => onSelectStyle(index)}
                className={`${styles.directionOption} ${
                  selectedStyleIndex === index ? styles.active : ""
                }`}
              >
                <div>
                  <span className={styles.directionName}>
                    {formatLabel(group.style)}
                  </span>

                  <span className={styles.directionReason}>
                    {index === 0
                      ? "Primary direction"
                      : "Alternative direction"}
                  </span>
                </div>

                <span className={styles.directionConfidence}>
                  {formatConfidence(group.confidence)}
                </span>
              </button>
            ))}
          </div>

          {activeGroup && (
            <p className={styles.activeDirectionNote}>
              Showing recommendations for the{" "}
              <strong>{formatLabel(activeGroup.style)}</strong> direction.
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
