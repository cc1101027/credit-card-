import api from './api';

export interface CreditCard {
  id: number;
  name: string;
  bank: string;
  card_type: string;
  annual_fee: number;
  minimum_income?: number;
  description: string;
  image_url?: string;
  is_active: boolean;
  created_at: string;
}

export interface CardCombination {
  cards: CreditCard[];
  projected_cashback: number;
  projected_points: number;
  total_annual_fee: number;
  net_benefit: number;
}

export interface RecommendationResponse {
  user_id: number;
  analysis_period: string;
  current_spending: Record<string, number>;
  recommendations: CardCombination[];
  potential_savings: number;
  generated_at: string;
}

export interface PurchaseAdvice {
  recommended_card?: {
    id: number;
    name: string;
    bank: string;
  };
  reward_amount: number;
  reward_type: string;
  merchant: string;
  category: string;
  message?: string;
}

export interface SpendingAnalysis {
  analysis_period_months: number;
  total_monthly_spending: number;
  spending_breakdown: Array<{
    category: string;
    monthly_amount: number;
    percentage: number;
  }>;
  top_categories: Array<{
    category: string;
    monthly_amount: number;
    percentage: number;
  }>;
}

export interface CardSimulation {
  card: {
    id: number;
    name: string;
    bank: string;
    annual_fee: number;
  };
  simulation_results: {
    total_annual_spending: number;
    projected_cashback: number;
    projected_points: number;
    annual_fee: number;
    net_benefit: number;
    category_breakdown: Record<string, any>;
  };
}

export interface CardComparison {
  comparison_results: Array<{
    card: {
      id: number;
      name: string;
      bank: string;
      annual_fee: number;
    };
    projected_cashback: number;
    projected_points: number;
    net_benefit: number;
    rank: number;
  }>;
  spending_pattern: Record<string, number>;
}

export const recommendationService = {
  async getOptimizedRecommendations(analysisPeriod?: string): Promise<RecommendationResponse> {
    const response = await api.post('/recommendations/optimize', {
      analysis_period: analysisPeriod,
    });
    return response.data;
  },

  async getPurchaseAdvice(merchantId: number, amount: number): Promise<PurchaseAdvice> {
    const response = await api.get(
      `/recommendations/purchase-advice?merchant_id=${merchantId}&amount=${amount}`
    );
    return response.data;
  },

  async getSpendingAnalysis(months: number = 3): Promise<SpendingAnalysis> {
    const response = await api.get(`/recommendations/spending-analysis?months=${months}`);
    return response.data;
  },

  async simulateCard(cardId: number): Promise<CardSimulation> {
    const response = await api.post(`/recommendations/simulate-card?card_id=${cardId}`);
    return response.data;
  },

  async compareCards(cardIds: number[]): Promise<CardComparison> {
    const response = await api.get(
      `/recommendations/card-comparison?card_ids=${cardIds.join(',')}`
    );
    return response.data;
  },
};