import { AIFeedback } from '../types';

export const analyzeVideo = async (videoBlob: Blob): Promise<AIFeedback> => {
  const formData = new FormData();
  formData.append('audio', videoBlob, 'recording.webm'); // Using webm, or extract audio if needed.

  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${baseUrl}/api/sessions/latest/attempts`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    return (await response.json()) as AIFeedback;
  } catch (error) {
    console.error("Error analyzing with local backend:", error);
    throw new Error("The backend could not process the recording.");
  }
};
