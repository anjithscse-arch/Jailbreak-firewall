import api from './client';
import { DetectionRule, RuleCreatePayload } from '../types/rules';

export const rulesApi = {
  getRules: async (params?: { category?: string; severity?: string; enabled?: boolean; search?: string }) => {
    const res = await api.get<{ success: boolean; data: DetectionRule[] }>('/rules', { params });
    return res.data.data;
  },

  createRule: async (payload: RuleCreatePayload) => {
    const res = await api.post<{ success: boolean; data: DetectionRule }>('/rules', payload);
    return res.data.data;
  },

  updateRule: async (id: number, payload: Partial<RuleCreatePayload>) => {
    const res = await api.put<{ success: boolean; data: DetectionRule }>(`/rules/${id}`, payload);
    return res.data.data;
  },

  deleteRule: async (id: number) => {
    const res = await api.delete(`/rules/${id}`);
    return res.data;
  },

  toggleRule: async (id: number) => {
    const res = await api.patch<{ success: boolean; data: DetectionRule }>(`/rules/${id}/toggle`);
    return res.data.data;
  },

  testPattern: async (prompt: string, pattern_type: string, pattern: string, case_sensitive = false) => {
    const res = await api.post('/rules/test', { prompt, pattern_type, pattern, case_sensitive });
    return res.data.data;
  },
};
