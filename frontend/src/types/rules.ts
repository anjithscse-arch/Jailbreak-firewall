export interface DetectionRule {
  id: number;
  rule_code: string;
  name: string;
  description: string;
  category: string;
  pattern_type: 'keyword' | 'phrase' | 'regex' | 'structural' | 'obfuscation' | 'template' | 'unicode';
  pattern: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  weight: number;
  enabled: boolean;
  case_sensitive: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface RuleCreatePayload {
  rule_code: string;
  name: string;
  description: string;
  category: string;
  pattern_type: string;
  pattern: string;
  severity: string;
  weight: number;
  enabled: boolean;
  case_sensitive: boolean;
}
