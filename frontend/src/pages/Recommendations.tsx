import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  TrendingUp,
  CreditCard,
  Star,
  MonetizationOn,
  CompareArrows,
} from '@mui/icons-material';
import { recommendationService } from '../services/recommendationService';

interface CreditCard {
  id: number;
  name: string;
  bank: string;
  card_type: string;
  annual_fee: number;
  description: string;
}

interface CardCombination {
  cards: CreditCard[];
  projected_cashback: number;
  projected_points: number;
  total_annual_fee: number;
  net_benefit: number;
}

interface RecommendationData {
  user_id: number;
  analysis_period: string;
  current_spending: Record<string, number>;
  recommendations: CardCombination[];
  potential_savings: number;
  generated_at: string;
}

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await recommendationService.getOptimizedRecommendations();
      setRecommendations(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-MY', {
      style: 'currency',
      currency: 'MYR',
    }).format(amount);
  };

  const getCardTypeColor = (cardType: string) => {
    switch (cardType.toLowerCase()) {
      case 'cashback':
        return 'success';
      case 'points':
        return 'primary';
      case 'miles':
        return 'secondary';
      case 'islamic':
        return 'info';
      default:
        return 'default';
    }
  };

  const CardCombinationCard: React.FC<{
    combination: CardCombination;
    rank: number;
    isRecommended?: boolean;
  }> = ({ combination, rank, isRecommended = false }) => (
    <Card
      sx={{
        border: isRecommended ? '2px solid #1976d2' : '1px solid #e0e0e0',
        position: 'relative',
      }}
    >
      {isRecommended && (
        <Box
          sx={{
            position: 'absolute',
            top: -1,
            right: 16,
            backgroundColor: '#1976d2',
            color: 'white',
            px: 2,
            py: 0.5,
            borderRadius: '0 0 8px 8px',
            fontSize: '0.75rem',
            fontWeight: 'bold',
          }}
        >
          <Star sx={{ fontSize: 16, mr: 0.5 }} />
          RECOMMENDED
        </Box>
      )}
      
      <CardContent sx={{ pt: isRecommended ? 4 : 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" color="primary">
            Option #{rank}
          </Typography>
          <Typography variant="h5" color="success.main" fontWeight="bold">
            {formatCurrency(combination.net_benefit)}
          </Typography>
        </Box>

        <Typography variant="body2" color="textSecondary" gutterBottom>
          Annual Net Benefit
        </Typography>

        <Divider sx={{ my: 2 }} />

        {/* Cards in this combination */}
        <Typography variant="subtitle2" gutterBottom>
          Credit Cards ({combination.cards.length})
        </Typography>
        <List dense>
          {combination.cards.map((card, index) => (
            <ListItem key={card.id} sx={{ px: 0 }}>
              <ListItemIcon>
                <CreditCard color="primary" />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="body2" fontWeight="medium">
                      {card.name}
                    </Typography>
                    <Chip
                      label={card.card_type}
                      size="small"
                      color={getCardTypeColor(card.card_type) as any}
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      {card.bank} • Annual Fee: {formatCurrency(card.annual_fee)}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        {/* Benefits breakdown */}
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Box textAlign="center">
              <Typography variant="h6" color="success.main">
                {formatCurrency(combination.projected_cashback)}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Cashback
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary.main">
                {combination.projected_points.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Points
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Box mt={2} textAlign="center">
          <Typography variant="body2" color="textSecondary">
            Total Annual Fees: {formatCurrency(combination.total_annual_fee)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Analyzing your spending patterns...
        </Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Credit Card Recommendations
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Optimized combinations based on your spending patterns
          </Typography>
        </Box>
        <Button
          variant="outlined"
          onClick={fetchRecommendations}
          disabled={loading}
          startIcon={<CompareArrows />}
        >
          Refresh Analysis
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {recommendations && (
        <>
          {/* Summary Card */}
          <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Grid container spacing={3} alignItems="center">
                <Grid item xs={12} md={8}>
                  <Typography variant="h6" color="white" gutterBottom>
                    Potential Annual Savings
                  </Typography>
                  <Typography variant="h3" color="white" fontWeight="bold">
                    {formatCurrency(recommendations.potential_savings)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    Based on your spending pattern from {recommendations.analysis_period}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box display="flex" justifyContent="center">
                    <MonetizationOn sx={{ fontSize: 80, color: 'rgba(255,255,255,0.3)' }} />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Current Spending Pattern */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Your Spending Pattern
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(recommendations.current_spending).map(([category, amount]) => (
                  <Grid item xs={12} sm={6} md={4} key={category}>
                    <Box
                      sx={{
                        p: 2,
                        border: '1px solid #e0e0e0',
                        borderRadius: 1,
                        textAlign: 'center',
                      }}
                    >
                      <Typography variant="body2" color="textSecondary">
                        {category}
                      </Typography>
                      <Typography variant="h6" color="primary">
                        {formatCurrency(amount * 12)} {/* Convert monthly to annual */}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        per year
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Typography variant="h5" gutterBottom>
            Recommended Card Combinations
          </Typography>
          <Grid container spacing={3}>
            {recommendations.recommendations.map((combination, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <CardCombinationCard
                  combination={combination}
                  rank={index + 1}
                  isRecommended={index === 0}
                />
              </Grid>
            ))}
          </Grid>

          {recommendations.recommendations.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No recommendations available. Please add some expenses to get personalized recommendations.
            </Alert>
          )}
        </>
      )}
    </Box>
  );
};

export default Recommendations;