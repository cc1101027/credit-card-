import api from './api';

export interface DashboardSummary {
  current_month_spending: number;
  last_month_spending: number;
  spending_change_percentage: number;
  current_month_transactions: number;
  top_category: string;
  top_category_amount: number;
  average_transaction: number;
}

export interface CategoryBreakdown {
  period: {
    start_date: string;
    end_date: string;
  };
  total_spending: number;
  categories: Array<{
    category: string;
    icon: string;
    total_amount: number;
    transaction_count: number;
    average_amount: number;
    percentage: number;
  }>;
}

export interface SpendingTrends {
  period_months: number;
  trends: Array<{
    month: string;
    total_amount: number;
    transaction_count: number;
    average_transaction: number;
  }>;
  total_spending: number;
  average_monthly: number;
}

export interface MerchantAnalysis {
  top_merchants: Array<{
    merchant: string;
    category: string;
    total_amount: number;
    transaction_count: number;
    average_amount: number;
  }>;
  total_merchants_analyzed: number;
}

export interface SavingsPotential {
  current_estimated_rewards: number;
  optimized_rewards: number;
  potential_annual_savings: number;
  recommended_cards: Array<{
    name: string;
    bank: string;
    annual_fee: number;
  }>;
  spending_pattern: Record<string, number>;
}

export const analyticsService = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    const response = await api.get('/analytics/dashboard-summary');
    return response.data;
  },

  async getCategoryBreakdown(startDate?: string, endDate?: string): Promise<CategoryBreakdown> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await api.get(`/analytics/category-breakdown?${params.toString()}`);
    return response.data;
  },

  async getSpendingTrends(months: number = 6): Promise<SpendingTrends> {
    const response = await api.get(`/analytics/spending-trends?months=${months}`);
    return response.data;
  },

  async getMerchantAnalysis(limit: number = 10): Promise<MerchantAnalysis> {
    const response = await api.get(`/analytics/merchant-analysis?limit=${limit}`);
    return response.data;
  },

  async getSavingsPotential(): Promise<SavingsPotential> {
    const response = await api.get('/analytics/savings-potential');
    return response.data;
  },
};