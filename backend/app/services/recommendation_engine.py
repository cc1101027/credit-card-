from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db.models import (
    User, Expense, CreditCard, CardReward, Merchant, Category, UserCard
)
from app.schemas import CardCombination, RecommendationResponse
import itertools
import json

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_spending_pattern(self, user_id: int, months: int = 3) -> Dict[str, float]:
        """Analyze user's spending pattern by category over the last N months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        spending_by_category = self.db.query(
            Category.name,
            func.avg(func.sum(Expense.amount)).label('avg_monthly_amount')
        ).join(
            Merchant, Category.id == Merchant.category_id
        ).join(
            Expense, Merchant.id == Expense.merchant_id
        ).filter(
            Expense.user_id == user_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).group_by(
            Category.id, Category.name,
            extract('year', Expense.expense_date),
            extract('month', Expense.expense_date)
        ).group_by(Category.id, Category.name).all()
        
        return {category: float(amount) for category, amount in spending_by_category}
    
    def calculate_card_rewards(self, card: CreditCard, spending_pattern: Dict[str, float]) -> Dict[str, float]:
        """Calculate potential rewards for a card based on spending pattern"""
        rewards = self.db.query(CardReward).filter(
            CardReward.credit_card_id == card.id,
            CardReward.is_active == True
        ).all()
        
        total_cashback = 0.0
        total_points = 0.0
        category_rewards = {}
        
        for category, monthly_amount in spending_pattern.items():
            annual_amount = monthly_amount * 12
            best_reward_rate = 0.0
            reward_type = "cashback"
            
            # Find the best reward rate for this category
            for reward in rewards:
                if reward.category and reward.category.name == category:
                    # Apply spending caps if any
                    applicable_amount = annual_amount
                    if reward.maximum_spend:
                        applicable_amount = min(applicable_amount, reward.maximum_spend * 12)
                    
                    if reward.reward_rate > best_reward_rate:
                        best_reward_rate = reward.reward_rate
                        reward_type = reward.reward_type.value
            
            # If no specific category reward, check for general rewards
            if best_reward_rate == 0.0:
                for reward in rewards:
                    if reward.category is None:  # General reward
                        applicable_amount = annual_amount
                        if reward.maximum_spend:
                            applicable_amount = min(applicable_amount, reward.maximum_spend * 12)
                        
                        if reward.reward_rate > best_reward_rate:
                            best_reward_rate = reward.reward_rate
                            reward_type = reward.reward_type.value
            
            # Calculate rewards
            reward_amount = annual_amount * best_reward_rate
            category_rewards[category] = {
                'amount': reward_amount,
                'rate': best_reward_rate,
                'type': reward_type
            }
            
            if reward_type == "cashback":
                total_cashback += reward_amount
            else:
                total_points += reward_amount
        
        return {
            'total_cashback': total_cashback,
            'total_points': total_points,
            'category_breakdown': category_rewards
        }
    
    def optimize_card_combination(self, user_id: int, max_cards: int = 3) -> List[CardCombination]:
        """Find the optimal combination of credit cards for maximum rewards"""
        spending_pattern = self.get_user_spending_pattern(user_id)
        
        if not spending_pattern:
            return []
        
        # Get all available cards
        available_cards = self.db.query(CreditCard).filter(
            CreditCard.is_active == True
        ).all()
        
        # Get user's current cards (if any)
        user_cards = self.db.query(UserCard).filter(
            UserCard.user_id == user_id,
            UserCard.is_active == True
        ).all()
        user_card_ids = [uc.credit_card_id for uc in user_cards]
        
        best_combinations = []
        
        # Try different combinations of cards (1 to max_cards)
        for num_cards in range(1, min(max_cards + 1, len(available_cards) + 1)):
            for card_combination in itertools.combinations(available_cards, num_cards):
                combination_rewards = self._calculate_combination_rewards(
                    card_combination, spending_pattern
                )
                
                total_annual_fee = sum(card.annual_fee for card in card_combination)
                net_benefit = combination_rewards['total_cashback'] - total_annual_fee
                
                # Convert points to approximate cash value (assuming 1 point = RM 0.01)
                points_cash_value = combination_rewards['total_points'] * 0.01
                total_benefit = net_benefit + points_cash_value
                
                card_combo = CardCombination(
                    cards=list(card_combination),
                    projected_cashback=combination_rewards['total_cashback'],
                    projected_points=combination_rewards['total_points'],
                    total_annual_fee=total_annual_fee,
                    net_benefit=total_benefit
                )
                
                best_combinations.append(card_combo)
        
        # Sort by net benefit and return top combinations
        best_combinations.sort(key=lambda x: x.net_benefit, reverse=True)
        return best_combinations[:5]  # Return top 5 combinations
    
    def _calculate_combination_rewards(self, cards: Tuple[CreditCard], spending_pattern: Dict[str, float]) -> Dict[str, float]:
        """Calculate rewards for a combination of cards, optimizing category allocation"""
        total_cashback = 0.0
        total_points = 0.0
        
        # For each spending category, find the best card in the combination
        for category, monthly_amount in spending_pattern.items():
            annual_amount = monthly_amount * 12
            best_reward = 0.0
            best_type = "cashback"
            
            for card in cards:
                card_rewards = self.db.query(CardReward).filter(
                    CardReward.credit_card_id == card.id,
                    CardReward.is_active == True
                ).all()
                
                for reward in card_rewards:
                    if reward.category and reward.category.name == category:
                        applicable_amount = annual_amount
                        if reward.maximum_spend:
                            applicable_amount = min(applicable_amount, reward.maximum_spend * 12)
                        
                        reward_amount = applicable_amount * reward.reward_rate
                        if reward_amount > best_reward:
                            best_reward = reward_amount
                            best_type = reward.reward_type.value
            
            # If no specific category reward found, use general rewards
            if best_reward == 0.0:
                for card in cards:
                    card_rewards = self.db.query(CardReward).filter(
                        CardReward.credit_card_id == card.id,
                        CardReward.is_active == True,
                        CardReward.category == None
                    ).all()
                    
                    for reward in card_rewards:
                        applicable_amount = annual_amount
                        if reward.maximum_spend:
                            applicable_amount = min(applicable_amount, reward.maximum_spend * 12)
                        
                        reward_amount = applicable_amount * reward.reward_rate
                        if reward_amount > best_reward:
                            best_reward = reward_amount
                            best_type = reward.reward_type.value
            
            if best_type == "cashback":
                total_cashback += best_reward
            else:
                total_points += best_reward
        
        return {
            'total_cashback': total_cashback,
            'total_points': total_points
        }
    
    def get_purchase_recommendation(self, user_id: int, merchant_id: int, amount: float) -> Dict:
        """Recommend the best card for a specific purchase"""
        # Get user's cards
        user_cards = self.db.query(UserCard).join(CreditCard).filter(
            UserCard.user_id == user_id,
            UserCard.is_active == True,
            CreditCard.is_active == True
        ).all()
        
        if not user_cards:
            return {"message": "No active cards found for user"}
        
        # Get merchant and category
        merchant = self.db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return {"error": "Merchant not found"}
        
        best_card = None
        best_reward = 0.0
        best_type = "cashback"
        
        for user_card in user_cards:
            card = user_card.credit_card
            rewards = self.db.query(CardReward).filter(
                CardReward.credit_card_id == card.id,
                CardReward.is_active == True
            ).all()
            
            for reward in rewards:
                reward_amount = 0.0
                
                # Check category-specific rewards
                if reward.category_id == merchant.category_id:
                    reward_amount = amount * reward.reward_rate
                # Check merchant-specific rewards
                elif reward.merchant_id == merchant_id:
                    reward_amount = amount * reward.reward_rate
                # Check general rewards
                elif reward.category_id is None and reward.merchant_id is None:
                    reward_amount = amount * reward.reward_rate
                
                if reward_amount > best_reward:
                    best_reward = reward_amount
                    best_card = card
                    best_type = reward.reward_type.value
        
        if best_card:
            return {
                "recommended_card": {
                    "id": best_card.id,
                    "name": best_card.name,
                    "bank": best_card.bank
                },
                "reward_amount": best_reward,
                "reward_type": best_type,
                "merchant": merchant.name,
                "category": merchant.category.name
            }
        
        return {"message": "No suitable card found for this purchase"}