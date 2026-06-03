"use client";

import "./how-it-works-timeline.css";
import { Upload, Sparkles, Shirt, Icon } from "lucide-react";

interface TimelineStep {
  number: number;
  title: string;
  description: string;
}

const steps = [
  {
    number: 1,
    icon: Upload,
    title: "Upload your garment",
    description:
      "Upload a clear image of one clothing item, such as a jacket, shirt, trousers, dress, or shoes.",
  },
  {
    number: 2,
    icon: Sparkles,
    title: "Discover its style",
    description:
      "The AI analyses the garment category, predicted style, and visual features.",
  },
  {
    number: 3,
    icon: Shirt,
    title: "Receive complete outfits",
    description:
      "The system recommends full outfit combinations that match your uploaded garment.",
  },
];

export default function HowItWorksTimeline() {
  return (
    <section className="section how-it-works-section">
      <div className="section-num right">02</div>

      <div className="section-grid how-it-works-grid">
        <div className="hiw-timeline">
          {steps.map((step, index) => (
            <div key={step.number} className="hiw-step">
              <div className="hiw-step-marker">
                <step.icon className="hiw-step-icon" strokeWidth={1.4} />
              </div>

              {index < steps.length - 1 && <div className="hiw-connector" />}

              <div className="hiw-step-content">
                <h3 className="hiw-step-title">{step.title}</h3>
                <p className="hiw-step-description">{step.description}</p>
              </div>
            </div>
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
        </div>
      </div>
    </section>
  );
}
