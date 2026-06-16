export type RecommendationItem = {
  type: string;
  name: string;
  brand: string;
  image_url: string;
  score: number;

  // New backend fields
  style?: string;
  filename?: string;
  clip_similarity?: number;
};

export type OutfitRecommendation = {
  name: string;
  items: RecommendationItem[];
};

export type StyleCandidate = {
  style: string;
  confidence: number;
  reason: string;
};

export type RecommendationGroup = {
  style: string;
  styles?: string[];
  confidence: number;
  reason: string;
  outfits: OutfitRecommendation[];
  recommendations: RecommendationItem[];
};

export type StyleMode = "single_style" | "multi_style";

export type RecommendationAnalysis = {
  predicted_type: string;
  type_confidence: number;
  main_style: string;
  predicted_styles: string[];
  style_scores: Record<string, number>;
  style_threshold: number;
  used_top1_fallback: boolean;
  style_model_mode: string;
  recommendation_strategy: string;
};

export type RecommendationResponse = {
  predicted_style: string;
  main_style?: string;
  style_confidence: number;

  style_probabilities: Record<string, number>;
  style_candidates: StyleCandidate[];
  style_mode: StyleMode;

  // New multi-label fields
  predicted_styles?: string[];
  style_scores?: Record<string, number>;
  style_threshold?: number;
  used_top1_fallback?: boolean;

  predicted_type: string;
  type_confidence: number;

  analysis?: RecommendationAnalysis;

  reliability: string;
  styling_notes: string;

  recommendations: RecommendationItem[];
  outfits: OutfitRecommendation[];

  recommendation_groups: RecommendationGroup[];
};

export type ReplacementItemResponse = {
  item: RecommendationItem;
};

export type RefinedRecommendationResponse = {
  selected_styles: string[];
  recommendations: RecommendationItem[];
  outfits: OutfitRecommendation[];
  recommendation_groups: RecommendationGroup[];
};

async function getApiErrorMessage(response: Response, fallbackMessage: string) {
  try {
    const errorBody = await response.json();

    if (typeof errorBody.detail === "string") {
      return errorBody.detail;
    }

    if (errorBody.detail?.message) {
      return errorBody.detail.message;
    }

    return fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}

export async function getRecommendations(
  file: File,
): Promise<RecommendationResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/recommend`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const message = await getApiErrorMessage(
      response,
      "Something went wrong while generating recommendations.",
    );

    throw new Error(message);
  }

  return response.json();
}

export async function replaceRecommendationItem(
  file: File,
  targetType: string,
  predictedStyle: string,
  excludeImageUrls: string[],
  predictedStyles?: string[],
): Promise<ReplacementItemResponse> {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("target_type", targetType);
  formData.append("predicted_style", predictedStyle);

  if (predictedStyles && predictedStyles.length > 0) {
    formData.append("predicted_styles", JSON.stringify(predictedStyles));
  }

  formData.append("exclude_image_urls", JSON.stringify(excludeImageUrls));

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/recommend/replace-item`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const message = await getApiErrorMessage(
      response,
      "No alternative item could be found for this piece.",
    );

    throw new Error(message);
  }

  return response.json();
}

export async function refineRecommendationsByStylePool(
  file: File,
  selectedStyles: string[],
  predictedType: string,
  mainStyle: string,
  typeConfidence: number,
): Promise<RefinedRecommendationResponse> {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("selected_styles", JSON.stringify(selectedStyles));
  formData.append("predicted_type", predictedType);
  formData.append("main_style", mainStyle);
  formData.append("type_confidence", String(typeConfidence));

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/recommend/refine-style`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const message = await getApiErrorMessage(
      response,
      "Could not update recommendations for the selected aesthetic mode.",
    );

    throw new Error(message);
  }

  return response.json();
}
