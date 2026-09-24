import api from './client';
import { PromptRecord, LogDetail, LogStatistics } from '../types/logs';

export const logsApi = {
  getLogs: async (params?: {
    page?: number;
    page_size?: number;
    decision?: string;
    category?: string;
    detected_by?: string;
    search?: string;
  }) => {
    const res = await api.get<{
      success: boolean;
      data: {
        items: PromptRecord[];
        pagination: {
          page: number;
          page_size: number;
          total_count: number;
          total_pages: number;
        };
      };
    }>('/logs', { params });
    return res.data.data;
  },

  getLogDetail: async (requestId: string): Promise<LogDetail> => {
    const res = await api.get<{ success: boolean; data: LogDetail }>(`/logs/${requestId}`);
    return res.data.data;
  },

  getStatistics: async (): Promise<LogStatistics> => {
    const res = await api.get<{ success: boolean; data: LogStatistics }>('/logs/statistics');
    return res.data.data;
  },

  deleteLog: async (requestId: string) => {
    const res = await api.delete(`/logs/${requestId}`);
    return res.data;
  },
};
