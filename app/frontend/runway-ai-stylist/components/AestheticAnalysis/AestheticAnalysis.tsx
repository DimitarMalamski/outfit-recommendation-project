"use client";

import type { RecommendationGroup, RecommendationResponse } from "@/lib/api";
import { Info } from "lucide-react";

import styles from "./AestheticAnalysis.module.css";

type AestheticAnalysisProps = {
  result: RecommendationResponse;
  recommendationGroups: RecommendationGroup[];
  selectedStyleIndex: number;
  selectedStylePool?: string[];
  isRefiningStylePool?: boolean;
  onSelectStyle: (index: number) => void;
  onSelectStylePool?: (styles: string[]) => void;
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

function getUniqueStyles(styles: string[]) {
  return Array.from(
    new Set(styles.filter((style): style is string => Boolean(style))),
  );
}

function areStylePoolsEqual(firstPool: string[], secondPool: string[]) {
  if (firstPool.length !== secondPool.length) return false;

  const firstSorted = [...firstPool].sort();
  const secondSorted = [...secondPool].sort();

  return firstSorted.every((style, index) => style === secondSorted[index]);
}

export default function AestheticAnalysis({
  result,
  selectedStyleIndex,
  selectedStylePool = [],
  isRefiningStylePool = false,
  onSelectStyle,
  onSelectStylePool,
}: AestheticAnalysisProps) {
  const mainAesthetic =
    result.analysis?.main_style ?? result.main_style ?? result.predicted_style;

  const rawSelectedStyles =
    result.analysis?.predicted_styles ??
    result.predicted_styles ??
    result.style_candidates.map((candidate) => candidate.style);

  const selectedStyles = getUniqueStyles(
    rawSelectedStyles.length > 0 ? rawSelectedStyles : [mainAesthetic],
  );

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

  const hasMultipleDirections = styleOptions.length > 1;

  const defaultStylePool = styleOptions.map((option) => option.style);

  const activeStylePool =
    selectedStylePool.length > 0 ? selectedStylePool : defaultStylePool;

  const activeAestheticLabel =
    activeStylePool.length > 1
      ? activeStylePool.map((style) => formatLabel(style)).join(" + ")
      : formatLabel(activeStylePool[0] ?? mainAesthetic);

  const mainAestheticConfidence =
    styleScores[mainAesthetic] ?? result.style_confidence;

  const activeStyleConfidence =
    activeStylePool.length > 1
      ? activeStylePool.reduce((sum, style) => {
          return sum + (styleScores[style] ?? 0);
        }, 0) / activeStylePool.length
      : (styleScores[activeStylePool[0] ?? mainAesthetic] ??
        mainAestheticConfidence);

  const styleConfidenceMetricLabel =
    activeStylePool.length > 1 ? "style pool confidence" : "style confidence";

  const isCombinedMode =
    hasMultipleDirections &&
    areStylePoolsEqual(activeStylePool, defaultStylePool);

  function handleStylePoolSelection(styles: string[]) {
    const firstStyleIndex = styleOptions.findIndex(
      (styleOption) => styleOption.style === styles[0],
    );

    onSelectStyle(firstStyleIndex >= 0 ? firstStyleIndex : 0);
    onSelectStylePool?.(styles);
  }

  function handleCombinationToggle() {
    if (!hasMultipleDirections) return;

    if (isCombinedMode) {
      const primaryStyle = styleOptions[0]?.style;

      if (!primaryStyle) return;

      handleStylePoolSelection([primaryStyle]);
      return;
    }

    handleStylePoolSelection(defaultStylePool);
  }

  const styleProbabilityEntries = Object.entries(
    result.style_probabilities ?? {},
  ).sort(([, firstValue], [, secondValue]) => secondValue - firstValue);

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
            {activeAestheticLabel}
          </button>{" "}
          {formatLabel(result.predicted_type).toLowerCase()}.
        </p>

        <div className={styles.editorialMeta}>
          <div className={styles.metaMetric}>
            <span>
              <strong>{formatConfidence(activeStyleConfidence)}</strong>{" "}
              {styleConfidenceMetricLabel}
            </span>
            <div className={styles.metaBar}>
              <div
                className={styles.metaBarFill}
                style={{ width: formatConfidence(activeStyleConfidence) }}
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
            <div className={styles.directionHeaderText}>
              <span className={styles.cardLabel}>Aesthetic interpretation</span>

              <h3>
                {hasMultipleDirections
                  ? "Choose recommendation mode"
                  : "Recommended aesthetic mode"}
              </h3>

              <p>
                {hasMultipleDirections
                  ? "Use the detected styles together, or turn combination off to focus the outfit on one aesthetic."
                  : "The model found one selected aesthetic for the recommendation pool."}
              </p>
            </div>
          </div>

          <div className={styles.modeSelector}>
            {hasMultipleDirections && (
              <div className={styles.modeToggleRow}>
                <button
                  type="button"
                  className={`${styles.headerModeToggle} ${
                    isCombinedMode ? styles.headerModeToggleActive : ""
                  }`}
                  onClick={handleCombinationToggle}
                  disabled={isRefiningStylePool}
                  aria-pressed={isCombinedMode}
                >
                  <span className={styles.headerModeToggleLabel}>
                    {isCombinedMode ? "Combined" : "Focused"}
                  </span>

                  <span className={styles.switchTrack}>
                    <span className={styles.switchThumb} />
                  </span>
                </button>
              </div>
            )}

            {hasMultipleDirections ? (
              isCombinedMode ? (
                <div className={styles.combinedModeCard}>
                  <span className={styles.modeEyebrow}>
                    Combined recommendation pool
                  </span>

                  <strong className={styles.modeTitle}>
                    {defaultStylePool
                      .map((style) => formatLabel(style))
                      .join(" + ")}
                  </strong>

                  <span className={styles.modeDescription}>
                    Recommended. The outfit is generated from both detected
                    aesthetics.
                  </span>
                </div>
              ) : (
                <div className={styles.splitStyleGrid}>
                  {styleOptions.map((option) => {
                    const isActive = areStylePoolsEqual(activeStylePool, [
                      option.style,
                    ]);

                    return (
                      <button
                        key={option.style}
                        type="button"
                        className={`${styles.splitStyleCard} ${
                          isActive ? styles.splitStyleCardActive : ""
                        }`}
                        onClick={() => handleStylePoolSelection([option.style])}
                        disabled={isRefiningStylePool || isActive}
                      >
                        <span className={styles.modeEyebrow}>
                          Focused aesthetic
                        </span>

                        <strong className={styles.modeTitle}>
                          {formatLabel(option.style)}
                        </strong>

                        <span className={styles.modeDescription}>
                          Use only this aesthetic for the outfit.
                        </span>
                      </button>
                    );
                  })}
                </div>
              )
            ) : (
              <div className={styles.combinedModeCard}>
                <span className={styles.modeEyebrow}>Selected aesthetic</span>

                <strong className={styles.modeTitle}>
                  {formatLabel(defaultStylePool[0])}
                </strong>

                <span className={styles.modeDescription}>
                  The outfit is generated from this aesthetic.
                </span>
              </div>
            )}
          </div>

          {activeStylePool.length > 0 && (
            <p className={styles.activeDirectionNote}>
              {isRefiningStylePool ? (
                <>Updating recommendations for the selected aesthetic mode...</>
              ) : (
                <>
                  Active recommendation pool:{" "}
                  <strong>
                    {activeStylePool
                      .map((style) => formatLabel(style))
                      .join(" + ")}
                  </strong>
                  . Items are ranked with CLIP visual similarity.
                </>
              )}
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
