export interface MatchedRule {
  rule_id: string;
  name: string;
  category: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  score: number;
  description: string;
  matched_text?: string;
}

export interface TopFeature {
  feature: string;
  weight: number;
  direction: 'attack' | 'benign';
}

export interface MLResult {
  label: string;
  confidence: number;
  probabilities?: Record<string, number>;
  top_features: TopFeature[];
  model_version?: string;
}

export interface Explanation {
  summary: string;
  reasons: string[];
  evidence?: Array<{
    type: string;
    label?: string;
    text?: string;
    severity?: string;
    weight?: number;
    matched_text?: string;
  }>;
  recommended_action: string;
}

export interface LLMResponseDetail {
  provider: string;
  model: string;
  content: string;
  latency_ms: number;
  usage?: Record<string, any>;
}

export interface AnalyzePromptResponse {
  request_id: string;
  decision: 'ALLOW' | 'BLOCK' | 'REVIEW';
  is_attack: boolean;
  attack_category: string;
  confidence: number;
  risk_score: number;
  processing_time_ms: number;
  detected_by: 'RULE_ENGINE' | 'ML_CLASSIFIER' | 'BOTH' | 'NONE';
  normalized_prompt?: string;
  matched_rules: MatchedRule[];
  ml_result?: MLResult;
  explanation: Explanation;
  llm_response?: string;
  llm_metadata?: LLMResponseDetail;
  blocked_message?: string;
  created_at: string;
}

export interface AnalyzePromptRequest {
  prompt: string;
  conversation_id?: string;
  forward_to_llm?: boolean;
  llm_provider?: string;
  llm_model?: string;
}
