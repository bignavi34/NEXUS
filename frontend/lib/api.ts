export interface ChatResponse {
  response: string;
}

const API_URL = "http://127.0.0.1:8000";

export async function sendMessage(
  message: string
): Promise<string> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail || "NEXUS backend is unavailable."
    );
  }

  const data: ChatResponse = await response.json();

  return data.response;
}
