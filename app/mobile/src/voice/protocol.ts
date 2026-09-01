import type { AgentTurnResponse, LearnerProfile } from "../../../../shared/typescript/contracts";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export const VOICE_URL = `${API_URL.replace(/^http/, "ws").replace(/\/$/, "")}/v1/voice`;

export type VoiceServerEvent =
  | { type: "session.ready" }
  | { type: "input.ready" }
  | { type: "asr.partial" | "asr.final"; text: string }
  | { type: "agent.reply"; transcript: string; turn: AgentTurnResponse }
  | { type: "turn.completed"; turn_id: string }
  | { type: "input.cancelled" | "session.closed" }
  | { type: "error"; error: { code: string; message: string; retryable: boolean } };

export function sessionStart(sessionId: string, profile: LearnerProfile) {
  return {
    type: "session.start",
    session_id: sessionId,
    child_id: "demo_child_001",
    learner_profile: profile,
    audio: { format: "pcm", sample_rate: 16000, bits: 16, channels: 1 },
    context: [],
  };
}

export function resamplePcm16(buffer: ArrayBuffer, sourceRate: number, targetRate = 16000): ArrayBuffer {
  if (sourceRate === targetRate) return buffer;
  const source = new Int16Array(buffer);
  if (source.length === 0) return buffer;
  const targetLength = Math.max(1, Math.round(source.length * targetRate / sourceRate));
  const target = new Int16Array(targetLength);
  const ratio = sourceRate / targetRate;
  for (let index = 0; index < targetLength; index += 1) {
    const position = index * ratio;
    const left = Math.floor(position);
    const right = Math.min(left + 1, source.length - 1);
    const fraction = position - left;
    const leftSample = source[left] ?? 0;
    const rightSample = source[right] ?? leftSample;
    target[index] = Math.round(leftSample * (1 - fraction) + rightSample * fraction);
  }
  return target.buffer;
}
