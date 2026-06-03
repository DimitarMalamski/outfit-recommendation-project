"use client";

import { useState } from "react";
import {
  getRecommendations,
  replaceRecommendationItem,
  RecommendationResponse,
} from "@/lib/api";
import "./upload-section.css";
import "./ensemble-section.css";
import HowItWorksTimeline from "../components/HowItWorksTimeline";

export default function RunwayAIStylist() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
      setSelectedFile(null);
      setPreviewUrl(null);
      setResult(null);
      setError("Please upload a JPG or PNG image.");
      setRefreshError(null);
      setRefreshingItemKey(null);
      setRefreshHistory({});

      event.target.value = "";
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setRefreshError(null);
    setRefreshHistory({});
  }

  function handleRemoveImage() {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setRefreshError(null);
    setRefreshingItemKey(null);
    setRefreshHistory({});
  }

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
      setResult(data);
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

    const itemKey = `${outfitIndex}-${itemIndex}`;

    const currentOutfits = result.outfits?.length
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
        result.predicted_style,
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

        const existingOutfits = previousResult.outfits?.length
          ? previousResult.outfits
          : previousResult.recommendations?.length
            ? [{ name: "Outfit 1", items: previousResult.recommendations }]
            : [];

        const updatedOutfits = existingOutfits.map(
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
          ...previousResult,
          outfits: updatedOutfits,
          recommendations:
            outfitIndex === 0
              ? (updatedOutfits[0]?.items ?? previousResult.recommendations)
              : previousResult.recommendations,
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

  const outfits = result?.outfits?.length
    ? result.outfits
    : result?.recommendations?.length
      ? [{ name: "Outfit 1", items: result.recommendations }]
      : [];

  return (
    <>
      <section className="hero">
        <p className="hero-tag">The Future of Personal Style</p>
        <h1 className="hero-title">RUNWAY</h1>
        <div className="hero-divider">
          <span className="line" />
          <span className="hero-ai">AI</span>
          <span className="line" />
        </div>
        <h2 className="hero-subtitle">Stylist</h2>
        <p className="hero-desc">
          Upload a clear image of a clothing item, such as a jacket, shirt,
          pants, or shoes. The AI analyses the item&apos;s style, and category,
          then recommends outfit combinations that match it.
        </p>
      </section>

      <HowItWorksTimeline />

      <section className="section upload-section">
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

      <section className="section analysis-section">
        <span className="section-num right">02</span>
        <p className="chapter">Chapter Two</p>
        <h2 className="section-title">
          The <em>Analysis</em>
        </h2>

        <div className="analysis-grid">
          <div className="analysis-item">
            <p className="analysis-label">Detected Aesthetic</p>
            <p className="analysis-value">{analysis.style}</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${analysis.styleConf}%` }}
              />
            </div>
            <p className="confidence">{analysis.styleConf}%</p>
          </div>

          <div className="analysis-item">
            <p className="analysis-label">Garment Classification</p>
            <p className="analysis-value">{analysis.type}</p>
            <div className="progress-bar">
              <div
                className="progress-fill accent"
                style={{ width: `${analysis.typeConf}%` }}
              />
            </div>
            <p className="confidence accent">{analysis.typeConf}%</p>
          </div>
        </div>

        {result && (
          <div className={`reliability-box reliability-${result.reliability}`}>
            <p className="reliability-label">Reliability</p>
            <p className="reliability-value">{result.reliability}</p>
            <p className="reliability-text">
              {result.reliability === "high" &&
                "The model is confident in both the predicted style and clothing type."}
              {result.reliability === "medium" &&
                "The result is usable, but one prediction is not highly confident. Review the outfit manually."}
              {result.reliability === "low" &&
                "The model is uncertain. The recommendation may not match the uploaded item correctly."}
            </p>
          </div>
        )}
      </section>

      {result && (
        <section className="section ensemble-section">
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
                Explore complete outfit combinations generated from your
                uploaded garment.
              </p>
            </div>
          </div>

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

      <section className="section notes-section">
        <span className="section-num right">04</span>
        <div className="section-grid">
          <div className="section-text">
            <p className="chapter">Chapter Four</p>
            <h2 className="section-title">
              The <em>Notes</em>
            </h2>
          </div>

          <div className="quote-area">
            <blockquote className="quote">
              <span className="quote-mark">&ldquo;</span>
              {result
                ? result.styling_notes
                : "The AI styling explanation will appear here after the outfit is generated."}
              <span className="quote-mark end">&rdquo;</span>
            </blockquote>
            <p className="quote-attr">— AI Styling Intelligence</p>
          </div>
        </div>
      </section>

      <footer className="footer">
        <p>RUNWAY AI STYLIST</p>
        <p className="footer-sub">Fashion Recommendation Prototype</p>
      </footer>
    </>
  );
}
