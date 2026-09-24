export interface DetectionEvent {
  id: number;
  rule_id?: string;
  detection_layer: string;
  category: string;
  severity: string;
  confidence: number;
  reason: string;
  matched_text_redacted?: string;
  created_at: string;
}

export interface PromptRecord {
  id: number;
  request_id: string;
  conversation_id?: string;
  user_id?: string;
  original_prompt_hash: string;
  redacted_prompt: string;
  prompt_length: number;
  decision: 'ALLOW' | 'BLOCK' | 'REVIEW';
  attack_category: string;
  confidence: number;
  risk_score: number;
  detected_by: string;
  processing_time_ms: number;
  llm_provider?: string;
  llm_model?: string;
  llm_called: boolean;
  created_at: string;
}

export interface LogDetail extends PromptRecord {
  llm_response?: string;
  events: DetectionEvent[];
}

export interface LogStatistics {
  total_logs: number;
  allowed_count: number;
  blocked_count: number;
  review_count: number;
  avg_latency_ms: number;
  layer_counts: Record<string, number>;
  category_counts: Record<string, number>;
}
