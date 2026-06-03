export type RecommendationItem = {
  type: string;
  name: string;
  brand: string;
  image_url: string;
  score: number;
};

export type OutfitRecommendation = {
  name: string;
  items: RecommendationItem[];
};

export type RecommendationResponse = {
  predicted_style: string;
  style_confidence: number;
  predicted_type: string;
  type_confidence: number;
  reliability: string;
  styling_notes: string;
  recommendations: RecommendationItem[];
  outfits: OutfitRecommendation[];
};

export type ReplacementItemResponse = {
  item: RecommendationItem;
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
): Promise<ReplacementItemResponse> {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("target_type", targetType);
  formData.append("predicted_style", predictedStyle);
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
