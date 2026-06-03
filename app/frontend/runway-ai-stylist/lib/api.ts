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
    throw new Error("Failed to get recommendations");
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
    throw new Error("Failed to replace recommendation item");
  }

  return response.json();
}
