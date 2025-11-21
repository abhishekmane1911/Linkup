import api from '@/lib/api';

export type ReportType = 
  | 'spam'
  | 'harassment'
  | 'hate_speech'
  | 'violence'
  | 'inappropriate_content'
  | 'copyright'
  | 'fake_news'
  | 'impersonation'
  | 'other';

export interface CreateReportRequest {
  content_type: 'tweet' | 'user';
  object_id: number;
  report_type: ReportType;
  description: string;
}

export interface Report {
  id: number;
  reporter: {
    id: number;
    username: string;
  };
  content_type: string;
  object_id: number;
  report_type: ReportType;
  description: string;
  status: 'pending' | 'under_review' | 'resolved' | 'dismissed' | 'escalated';
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

class ReportService {
  async createReport(data: CreateReportRequest): Promise<Report> {
    const response = await api.post<Report>('/moderation/reports/', data);
    return response.data;
  }

  async getMyReports(): Promise<{ results: Report[]; count: number }> {
    const response = await api.get('/moderation/my-reports/');
    return response.data;
  }
}

export const reportService = new ReportService();
