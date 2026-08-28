import type {
  AgentTurnRequest,
  AgentTurnResponse,
  PetJobResponse,
} from "../../../../shared/typescript/contracts";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    throw new Error(`api_error_${response.status}`);
  }
  return (await response.json()) as T;
}

export function sendSpeakingTurn(request: AgentTurnRequest): Promise<AgentTurnResponse> {
  return requestJson(`/v1/sessions/${request.session_id}/turns`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export function createPet(childId: string, description: string): Promise<PetJobResponse> {
  return requestJson("/v1/pets", {
    method: "POST",
    headers: { "Idempotency-Key": `${childId}:${description}` },
    body: JSON.stringify({ child_id: childId, description, output_mode: "concept_2d" }),
  });
}
