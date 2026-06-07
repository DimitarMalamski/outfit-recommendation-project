"use client";

import { useEffect, useState } from "react";
import {
  getRecommendations,
  replaceRecommendationItem,
  RecommendationResponse,
} from "@/lib/api";
import "./upload-section.css";
import "./ensemble-section.css";
import HowItWorksTimeline from "../components/HowItWorksTimeline";
import AestheticAnalysis from "../components/AestheticAnalysis/AestheticAnalysis";
import HeroSection from "../components/HeroSection";

export default function RunwayAIStylist() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [selectedStyleIndex, setSelectedStyleIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [shouldScrollToEnsemble, setShouldScrollToEnsemble] = useState(false);
  const [refreshingItemKey, setRefreshingItemKey] = useState<string | null>(
    null,
  );
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [refreshHistory, setRefreshHistory] = useState<
    Record<string, string[]>
  >({});

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = ["image/jpeg", "image/png"];

    if (!allowedTypes.includes(file.type)) {
      setSelectedStyleIndex(0);
      setSelectedFile(null);
      setPreviewUrl(null);
      setResult(null);
      setError("Please upload a JPG or PNG image.");
      setRefreshError(null);
      setRefreshingItemKey(null);
      setRefreshHistory({});
      setShouldScrollToEnsemble(false);

      event.target.value = "";
      return;
    }

    setSelectedStyleIndex(0);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setRefreshError(null);
    setRefreshHistory({});
    setShouldScrollToEnsemble(false);
  }

  function handleRemoveImage() {
    setSelectedStyleIndex(0);
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setRefreshError(null);
    setRefreshingItemKey(null);
    setRefreshHistory({});
    setShouldScrollToEnsemble(false);
  }

  useEffect(() => {
    if (!result || !shouldScrollToEnsemble) return;

    requestAnimationFrame(() => {
      const ensembleSection = document.getElementById("outfit-results-anchor");

      if (!ensembleSection) return;

      ensembleSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

      setShouldScrollToEnsemble(false);
    });
  }, [result, shouldScrollToEnsemble]);

  async function handleSubmit() {
    if (!selectedFile) {
      setError("Please upload an image first.");
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setRefreshError(null);
      setRefreshHistory({});

      const data = await getRecommendations(selectedFile);

      setSelectedStyleIndex(0);
      setResult(data);
      setShouldScrollToEnsemble(true);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong while generating recommendations.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRefreshItem(
    outfitIndex: number,
    itemIndex: number,
    itemType: string,
  ) {
    if (!selectedFile || !result) return;

    const activeGroup =
      result.recommendation_groups?.[selectedStyleIndex] ??
      result.recommendation_groups?.[0];

    const activeStyle = activeGroup?.style ?? result.predicted_style;

    const itemKey = `${activeStyle}-${outfitIndex}-${itemIndex}`;

    const currentOutfits = activeGroup?.outfits?.length
      ? activeGroup.outfits
      : result.outfits?.length
        ? result.outfits
        : result.recommendations?.length
          ? [{ name: "Outfit 1", items: result.recommendations }]
          : [];

    const currentVisibleImageUrls = currentOutfits.flatMap((outfit) =>
      outfit.items.map((item) => item.image_url),
    );

    const allPreviouslyUsedImageUrls = Object.values(refreshHistory).flat();

    const excludeImageUrls = Array.from(
      new Set([...currentVisibleImageUrls, ...allPreviouslyUsedImageUrls]),
    );

    try {
      setRefreshingItemKey(itemKey);
      setRefreshError(null);

      const data = await replaceRecommendationItem(
        selectedFile,
        itemType,
        activeStyle,
        excludeImageUrls,
      );

      const newItem = data.item;

      const currentItem = currentOutfits[outfitIndex]?.items[itemIndex];

      setRefreshHistory((previousHistory) => {
        const existingHistory = previousHistory[itemKey] ?? [];

        const updatedHistory = Array.from(
          new Set(
            [
              ...existingHistory,
              currentItem?.image_url,
              newItem.image_url,
            ].filter(Boolean) as string[],
          ),
        );

        return {
          ...previousHistory,
          [itemKey]: updatedHistory,
        };
      });

      setResult((previousResult) => {
        if (!previousResult) return previousResult;

        const existingGroups = previousResult.recommendation_groups?.length
          ? previousResult.recommendation_groups
          : [
              {
                style: previousResult.predicted_style,
                confidence: previousResult.style_confidence,
                reason: "Most likely aesthetic",
                outfits: previousResult.outfits,
                recommendations: previousResult.recommendations,
              },
            ];

        const updatedGroups = existingGroups.map((group, groupIndex) => {
          if (groupIndex !== selectedStyleIndex) return group;

          const groupOutfits = group.outfits?.length
            ? group.outfits
            : group.recommendations?.length
              ? [{ name: "Outfit 1", items: group.recommendations }]
              : [];

          const updatedOutfits = groupOutfits.map(
            (outfit, currentOutfitIndex) => {
              if (currentOutfitIndex !== outfitIndex) return outfit;

              return {
                ...outfit,
                items: outfit.items.map((existingItem, currentItemIndex) =>
                  currentItemIndex === itemIndex ? newItem : existingItem,
                ),
              };
            },
          );

          return {
            ...group,
            outfits: updatedOutfits,
            recommendations:
              outfitIndex === 0
                ? (updatedOutfits[0]?.items ?? group.recommendations)
                : group.recommendations,
          };
        });

        const primaryGroup = updatedGroups[0];

        return {
          ...previousResult,
          recommendation_groups: updatedGroups,
          outfits: primaryGroup?.outfits ?? previousResult.outfits,
          recommendations:
            primaryGroup?.recommendations ?? previousResult.recommendations,
        };
      });
    } catch {
      setRefreshError("No further alternatives are available for this piece.");
    } finally {
      setRefreshingItemKey(null);
    }
  }

  const analysis = {
    style: result?.predicted_style ?? "Awaiting Image",
    type: result?.predicted_type ?? "Awaiting Image",
    styleConf: result ? Math.round(result.style_confidence * 100) : 0,
    typeConf: result ? Math.round(result.type_confidence * 100) : 0,
  };

  const recommendationGroups = result?.recommendation_groups?.length
    ? result.recommendation_groups
    : result
      ? [
          {
            style: result.predicted_style,
            confidence: result.style_confidence,
            reason: "Most likely aesthetic",
            outfits: result.outfits,
            recommendations: result.recommendations,
          },
        ]
      : [];

  const activeRecommendationGroup =
    recommendationGroups[selectedStyleIndex] ?? recommendationGroups[0];

  const outfits = activeRecommendationGroup?.outfits?.length
    ? activeRecommendationGroup.outfits
    : activeRecommendationGroup?.recommendations?.length
      ? [{ name: "Outfit 1", items: activeRecommendationGroup.recommendations }]
      : [];

  return (
    <>
      <HeroSection />

      <HowItWorksTimeline />

      <section id="upload-section" className="section upload-section">
        <span className="section-num">01</span>
        <div className="section-grid">
          <div className="section-text">
            <p className="chapter">Chapter One</p>
            <h2 className="section-title">
              The <em>Upload</em>
            </h2>
            <div className="divider" />
            <p className="section-desc">
              Every great ensemble begins with a single piece. Upload your
              chosen garment, then let the AI classify its style, type, and
              visual direction.
            </p>
          </div>

          <div className="upload-area">
            <div className="upload-box">
              <div className="upload-content">
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Uploaded clothing item"
                    className="preview-img"
                  />
                ) : (
                  <>
                    <div className="upload-icon">+</div>
                    <p className="upload-text">Drop Image Here</p>
                    <p className="upload-hint">or click to select</p>
                  </>
                )}
              </div>

              <div className="upload-actions">
                <label className="upload-button">
                  {previewUrl ? "Change Image" : "Choose Image"}
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/jpg"
                    onChange={handleFileChange}
                    hidden
                  />
                </label>

                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isLoading}
                  className="generate-button"
                >
                  {isLoading ? "Styling..." : "Generate Outfit"}
                </button>
              </div>

              {error && <p className="upload-error">{error}</p>}
            </div>
          </div>
        </div>
      </section>

      {result && (
        <AestheticAnalysis
          result={result}
          recommendationGroups={recommendationGroups}
          selectedStyleIndex={selectedStyleIndex}
          onSelectStyle={(index) => {
            setSelectedStyleIndex(index);
            setRefreshError(null);
          }}
        />
      )}

      {result && (
        <section id="ensemble-section" className="section ensemble-section">
          <div className="section-num">03</div>

          <div className="section-grid ensemble-header-grid">
            <div className="ensemble-header-spacer" />

            <div className="section-text ensemble-title-block">
              <p className="chapter">Chapter Three</p>
              <h2 className="section-title">
                Curated <em>Ensemble</em>
              </h2>
              <div className="divider" />
              <p className="section-desc">
                {activeRecommendationGroup
                  ? `Showing outfit suggestions for the ${activeRecommendationGroup.style} direction. You can change the aesthetic direction in the analysis section above.`
                  : "Explore complete outfit combinations generated from your uploaded garment."}
              </p>
            </div>
          </div>

          <div id="outfit-results-anchor" className="outfit-results-anchor" />

          <div className="outfit-carousel">
            {outfits.map((outfit, outfitIndex) => (
              <div className="outfit-slide" key={outfitIndex}>
                <h3 className="outfit-slide-title">{outfit.name}</h3>

                <div className="outfit-grid">
                  {outfit.items.map((item, itemIndex) => (
                    <div className="outfit-card" key={itemIndex}>
                      <img
                        src={`${process.env.NEXT_PUBLIC_API_URL}${item.image_url}`}
                        alt={item.name}
                        className="outfit-img"
                      />

                      <button
                        type="button"
                        className={`item-refresh-button ${
                          refreshingItemKey === `${outfitIndex}-${itemIndex}`
                            ? "loading"
                            : ""
                        }`}
                        onClick={() =>
                          handleRefreshItem(outfitIndex, itemIndex, item.type)
                        }
                        disabled={refreshingItemKey !== null}
                        aria-label={`Refresh ${item.type}`}
                        title="Find alternative piece"
                      >
                        <span className="refresh-symbol">↻</span>
                      </button>

                      <div className="outfit-overlay">
                        <p className="outfit-type">{item.type}</p>
                        <h3 className="outfit-name">{item.name}</h3>
                        <p className="outfit-brand">{item.brand}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {refreshError && <p className="refresh-error">{refreshError}</p>}
        </section>
      )}

      <footer className="footer">
        <p>RUNWAY AI STYLIST</p>
        <p className="footer-sub">Fashion Recommendation Prototype</p>
      </footer>
    </>
  );
}
