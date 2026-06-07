"use client";

import "./how-it-works-timeline.css";
import { Upload, Sparkles, Shirt } from "lucide-react";

interface TimelineStep {
  number: number;
  icon: typeof Upload;
  title: string;
  description: string;
  targetId: string;
  fallbackId?: string;
}

const steps: TimelineStep[] = [
  {
    number: 1,
    icon: Upload,
    title: "Upload your garment",
    description:
      "Upload a clear image of one clothing item, such as a jacket, shirt, pants, or shoes.",
    targetId: "upload-section",
  },
  {
    number: 2,
    icon: Sparkles,
    title: "AI identifies aesthetic",
    description: "The AI analyses the garment category and predicted style.",
    targetId: "analysis-section",
    fallbackId: "upload-section",
  },
  {
    number: 3,
    icon: Shirt,
    title: "Receive complete outfits",
    description:
      "The system recommends full outfit combinations that match your uploaded garment.",
    targetId: "outfit-results-anchor",
    fallbackId: "upload-section",
  },
];

export default function HowItWorksTimeline() {
  function handleStepClick(
    event: React.MouseEvent<HTMLAnchorElement>,
    targetId: string,
    fallbackId?: string,
  ) {
    event.preventDefault();

    const targetElement =
      document.getElementById(targetId) ||
      (fallbackId ? document.getElementById(fallbackId) : null);

    if (!targetElement) return;

    targetElement.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  return (
    <section className="section how-it-works-section">
      <div className="section-grid how-it-works-grid">
        <div className="hiw-timeline">
          {steps.map((step, index) => (
            <a
              key={step.number}
              href={`#${step.targetId}`}
              className="hiw-step"
              onClick={(event) =>
                handleStepClick(event, step.targetId, step.fallbackId)
              }
              aria-label={`Go to step ${step.number}: ${step.title}`}
            >
              <div className="hiw-step-marker">
                <step.icon className="hiw-step-icon" strokeWidth={1.4} />
              </div>

              {index < steps.length - 1 && <div className="hiw-connector" />}

              <div className="hiw-step-content">
                <h3 className="hiw-step-title">{step.title}</h3>
                <p className="hiw-step-description">{step.description}</p>
              </div>
            </a>
          ))}
        </div>

        <div className="section-text">
          <p className="chapter">The Process</p>
          <h2 className="section-title">
            How It <em>Works</em>
          </h2>
          <div className="divider" />
          <p className="section-desc">
            Three simple steps to understand what to upload, what the AI checks,
            and what kind of result you can expect.
          </p>
          <p className="hiw-footnote">
            For best results, upload one clearly visible clothing item on a
            simple background.
          </p>
        </div>
      </div>
    </section>
  );
}
