export type RecommendationItem = {
  type: string;
  name: string;
  brand: string;
  image_url: string;
  score: number;
};

export type RecommendationResponse = {
  predicted_style: string;
  style_confidence: number;
  predicted_type: string;
  type_confidence: number;
  reliability: string;
  styling_notes: string;
  recommendations: RecommendationItem[];
};

export async function getRecommendations(
  file: File,
): Promise<RecommendationResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/recommend", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to get recommendations");
  }

  return response.json();
}
