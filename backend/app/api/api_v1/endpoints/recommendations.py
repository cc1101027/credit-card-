from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.db.models import User
from app.schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    CardCombination
)
from app.core.security import get_current_active_user
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.post("/optimize", response_model=RecommendationResponse)
def get_card_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get optimized credit card combination recommendations"""
    engine = RecommendationEngine(db)
    
    # Get spending pattern
    spending_pattern = engine.get_user_spending_pattern(current_user.id)
    
    if not spending_pattern:
        raise HTTPException(
            status_code=400, 
            detail="No spending data found. Please add some expenses first."
        )
    
    # Get optimized combinations
    recommendations = engine.optimize_card_combination(current_user.id)
    
    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail="No suitable card combinations found"
        )
    
    # Calculate potential savings (difference between best and current)
    best_combination = recommendations[0]
    current_rewards = 0.0  # This would be calculated based on user's current cards
    potential_savings = best_combination.net_benefit - current_rewards
    
    analysis_period = request.analysis_period or datetime.now().strftime("%Y-%m")
    
    return RecommendationResponse(
        user_id=current_user.id,
        analysis_period=analysis_period,
        current_spending=spending_pattern,
        recommendations=recommendations,
        potential_savings=potential_savings,
        generated_at=datetime.now()
    )

@router.get("/purchase-advice")
def get_purchase_advice(
    merchant_id: int = Query(..., description="ID of the merchant"),
    amount: float = Query(..., description="Purchase amount"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recommendation for which card to use for a specific purchase"""
    engine = RecommendationEngine(db)
    
    recommendation = engine.get_purchase_recommendation(
        current_user.id, merchant_id, amount
    )
    
    return recommendation

@router.get("/spending-analysis")
def get_spending_analysis(
    months: int = Query(3, description="Number of months to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed spending analysis for the user"""
    engine = RecommendationEngine(db)
    
    spending_pattern = engine.get_user_spending_pattern(current_user.id, months)
    
    if not spending_pattern:
        return {
            "message": "No spending data found",
            "spending_pattern": {},
            "total_monthly_spending": 0.0
        }
    
    total_monthly_spending = sum(spending_pattern.values())
    
    # Calculate percentages
    spending_breakdown = [
        {
            "category": category,
            "monthly_amount": amount,
            "percentage": (amount / total_monthly_spending * 100) if total_monthly_spending > 0 else 0
        }
        for category, amount in spending_pattern.items()
    ]
    
    # Sort by amount
    spending_breakdown.sort(key=lambda x: x["monthly_amount"], reverse=True)
    
    return {
        "analysis_period_months": months,
        "total_monthly_spending": total_monthly_spending,
        "spending_breakdown": spending_breakdown,
        "top_categories": spending_breakdown[:5]
    }

@router.post("/simulate-card")
def simulate_card_performance(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Simulate how a specific card would perform with user's spending pattern"""
    from app.db.models import CreditCard
    
    # Get the card
    card = db.query(CreditCard).filter(
        CreditCard.id == card_id,
        CreditCard.is_active == True
    ).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    engine = RecommendationEngine(db)
    spending_pattern = engine.get_user_spending_pattern(current_user.id)
    
    if not spending_pattern:
        raise HTTPException(
            status_code=400,
            detail="No spending data found for simulation"
        )
    
    # Calculate rewards for this specific card
    card_rewards = engine.calculate_card_rewards(card, spending_pattern)
    
    total_annual_spending = sum(amount * 12 for amount in spending_pattern.values())
    net_benefit = card_rewards['total_cashback'] - card.annual_fee
    
    return {
        "card": {
            "id": card.id,
            "name": card.name,
            "bank": card.bank,
            "annual_fee": card.annual_fee
        },
        "simulation_results": {
            "total_annual_spending": total_annual_spending,
            "projected_cashback": card_rewards['total_cashback'],
            "projected_points": card_rewards['total_points'],
            "annual_fee": card.annual_fee,
            "net_benefit": net_benefit,
            "category_breakdown": card_rewards['category_breakdown']
        }
    }

@router.get("/card-comparison")
def compare_cards(
    card_ids: str = Query(..., description="Comma-separated card IDs to compare"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Compare multiple cards based on user's spending pattern"""
    from app.db.models import CreditCard
    
    try:
        card_id_list = [int(id.strip()) for id in card_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid card IDs format")
    
    if len(card_id_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 cards can be compared")
    
    # Get cards
    cards = db.query(CreditCard).filter(
        CreditCard.id.in_(card_id_list),
        CreditCard.is_active == True
    ).all()
    
    if len(cards) != len(card_id_list):
        raise HTTPException(status_code=404, detail="One or more cards not found")
    
    engine = RecommendationEngine(db)
    spending_pattern = engine.get_user_spending_pattern(current_user.id)
    
    if not spending_pattern:
        raise HTTPException(
            status_code=400,
            detail="No spending data found for comparison"
        )
    
    comparison_results = []
    
    for card in cards:
        card_rewards = engine.calculate_card_rewards(card, spending_pattern)
        net_benefit = card_rewards['total_cashback'] - card.annual_fee
        
        comparison_results.append({
            "card": {
                "id": card.id,
                "name": card.name,
                "bank": card.bank,
                "annual_fee": card.annual_fee
            },
            "projected_cashback": card_rewards['total_cashback'],
            "projected_points": card_rewards['total_points'],
            "net_benefit": net_benefit,
            "rank": 0  # Will be set after sorting
        })
    
    # Sort by net benefit and assign ranks
    comparison_results.sort(key=lambda x: x["net_benefit"], reverse=True)
    for i, result in enumerate(comparison_results):
        result["rank"] = i + 1
    
    return {
        "comparison_results": comparison_results,
        "spending_pattern": spending_pattern
    }