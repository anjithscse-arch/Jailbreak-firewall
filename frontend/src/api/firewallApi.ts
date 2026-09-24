import api from './client';
import { AnalyzePromptRequest, AnalyzePromptResponse } from '../types/firewall';

export const firewallApi = {
  analyzePrompt: async (payload: AnalyzePromptRequest): Promise<AnalyzePromptResponse> => {
    const res = await api.post<AnalyzePromptResponse>('/firewall/analyze', payload);
    return res.data;
  },

  analyzeBatch: async (prompts: string[]) => {
    const res = await api.post('/firewall/analyze-batch', { prompts });
    return res.data;
  },

  chat: async (messages: Array<{ role: string; content: string }>, provider?: string) => {
    const res = await api.post('/llm/chat', { messages, provider });
    return res.data;
  },
};
