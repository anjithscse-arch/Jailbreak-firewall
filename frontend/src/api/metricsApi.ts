import api from './client';
import { MetricsSummary, TimelinePoint, CategoryDistribution, EvaluationResult } from '../types/metrics';

export const metricsApi = {
  getSummary: async (): Promise<MetricsSummary> => {
    const res = await api.get<{ success: boolean; data: MetricsSummary }>('/metrics/summary');
    return res.data.data;
  },

  getTimeline: async (): Promise<TimelinePoint[]> => {
    const res = await api.get<{ success: boolean; data: TimelinePoint[] }>('/metrics/timeline');
    return res.data.data;
  },

  getCategories: async (): Promise<CategoryDistribution[]> => {
    const res = await api.get<{ success: boolean; data: CategoryDistribution[] }>('/metrics/categories');
    return res.data.data;
  },

  runEvaluation: async (): Promise<EvaluationResult> => {
    const res = await api.post<{ success: boolean; data: EvaluationResult }>('/metrics/evaluate');
    return res.data.data;
  },
};
