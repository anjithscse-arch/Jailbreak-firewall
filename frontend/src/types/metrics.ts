export interface MetricsSummary {
  total_requests: number;
  allowed_requests: number;
  blocked_requests: number;
  review_requests: number;
  attack_rate: number;
  average_latency_ms: number;
  rule_detection_rate: number;
  ml_detection_rate: number;
  false_positive_rate?: number | null;
  false_negative_rate?: number | null;
  model_accuracy?: number | null;
  model_precision?: number | null;
  model_recall?: number | null;
  model_f1?: number | null;
}

export interface TimelinePoint {
  timestamp: string;
  total: number;
  allowed: number;
  blocked: number;
  review: number;
  avg_latency_ms: number;
}

export interface CategoryDistribution {
  category: string;
  count: number;
  percentage: number;
}

export interface LayerMetrics {
  total_evaluated: number;
  true_positives: number;
  true_negatives: number;
  false_positives: number;
  false_negatives: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  false_positive_rate: number;
  false_negative_rate: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
}

export interface EvaluationResult {
  rule_only: LayerMetrics;
  ml_only: LayerMetrics;
  combined: LayerMetrics;
  confusion_matrix: {
    labels: string[];
    rule_only: number[][];
    ml_only: number[][];
    combined: number[][];
  };
  evaluated_at: string;
}
