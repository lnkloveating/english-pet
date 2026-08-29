export type LearnerProfile = {
  grade?: 1 | 2 | 3 | 4 | 5 | 6;
  level: 1 | 2 | 3 | 4 | 5;
  confidence: number;
  target_sentence_words: number;
  interests: string[];
  recent_topics: string[];
};

export type AgentTurnRequest = {
  session_id: string;
  child_id: string;
  transcript: string;
  learner_profile: LearnerProfile;
  audio_metadata?: {
    duration_ms?: number;
    asr_confidence?: number;
    detected_language?: string;
    is_human_voice?: boolean;
  };
};

export type AgentTurnResponse = {
  turn_id: string;
  reply_text: string;
  teaching_action: "encourage" | "recast" | "scaffold" | "redirect";
  recast_text: string | null;
  reward: {
    valid_speaking_attempt: boolean;
    base_voice_fruit: number;
    bonus_voice_fruit: number;
    reasons: string[];
  };
  learner_profile: LearnerProfile;
  safety: { action: "allow" | "redirect" | "trusted_adult"; reason_code: string };
};

export type PetJobStatus =
  | "queued"
  | "structuring"
  | "generating_concept"
  | "review_required"
  | "generating_3d"
  | "completed"
  | "failed";

export type PetJobResponse = {
  job_id: string;
  status: PetJobStatus;
  created_at: string;
  concept_image_url: string | null;
  model_url: string | null;
  error_code: string | null;
};
