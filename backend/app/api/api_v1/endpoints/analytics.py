from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db.database import get_db
from app.db.models import User, Expense, Merchant, Category
from app.schemas import SpendingAnalytics, MonthlySpending, SpendingByCategory
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/spending-trends")
def get_spending_trends(
    months: int = Query(6, description="Number of months to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get spending trends over time"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    monthly_trends = db.query(
        extract('year', Expense.expense_date).label('year'),
        extract('month', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('transaction_count')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).group_by(
        extract('year', Expense.expense_date),
        extract('month', Expense.expense_date)
    ).order_by(
        extract('year', Expense.expense_date),
        extract('month', Expense.expense_date)
    ).all()
    
    trends = []
    for trend in monthly_trends:
        month_str = f"{int(trend.year)}-{int(trend.month):02d}"
        trends.append({
            "month": month_str,
            "total_amount": float(trend.total_amount),
            "transaction_count": trend.transaction_count,
            "average_transaction": float(trend.total_amount) / trend.transaction_count if trend.transaction_count > 0 else 0
        })
    
    return {
        "period_months": months,
        "trends": trends,
        "total_spending": sum(t["total_amount"] for t in trends),
        "average_monthly": sum(t["total_amount"] for t in trends) / len(trends) if trends else 0
    }

@router.get("/category-breakdown")
def get_category_breakdown(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    category_spending = db.query(
        Category.name.label('category'),
        Category.icon.label('icon'),
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('transaction_count'),
        func.avg(Expense.amount).label('average_amount')
    ).join(
        Merchant, Category.id == Merchant.category_id
    ).join(
        Expense, Merchant.id == Expense.merchant_id
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).group_by(Category.id, Category.name, Category.icon).all()
    
    total_spending = sum(float(cat.total_amount) for cat in category_spending)
    
    breakdown = []
    for cat in category_spending:
        breakdown.append({
            "category": cat.category,
            "icon": cat.icon,
            "total_amount": float(cat.total_amount),
            "transaction_count": cat.transaction_count,
            "average_amount": float(cat.average_amount),
            "percentage": (float(cat.total_amount) / total_spending * 100) if total_spending > 0 else 0
        })
    
    # Sort by total amount
    breakdown.sort(key=lambda x: x["total_amount"], reverse=True)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "total_spending": total_spending,
        "categories": breakdown
    }

@router.get("/merchant-analysis")
def get_merchant_analysis(
    limit: int = Query(10, description="Number of top merchants to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get top merchants by spending"""
    top_merchants = db.query(
        Merchant.name.label('merchant'),
        Category.name.label('category'),
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('transaction_count'),
        func.avg(Expense.amount).label('average_amount')
    ).join(
        Category, Merchant.category_id == Category.id
    ).join(
        Expense, Merchant.id == Expense.merchant_id
    ).filter(
        Expense.user_id == current_user.id
    ).group_by(
        Merchant.id, Merchant.name, Category.name
    ).order_by(
        func.sum(Expense.amount).desc()
    ).limit(limit).all()
    
    merchants = []
    for merchant in top_merchants:
        merchants.append({
            "merchant": merchant.merchant,
            "category": merchant.category,
            "total_amount": float(merchant.total_amount),
            "transaction_count": merchant.transaction_count,
            "average_amount": float(merchant.average_amount)
        })
    
    return {
        "top_merchants": merchants,
        "total_merchants_analyzed": len(merchants)
    }

@router.get("/savings-potential")
def get_savings_potential(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate potential savings with optimal credit card usage"""
    from app.services.recommendation_engine import RecommendationEngine
    
    engine = RecommendationEngine(db)
    spending_pattern = engine.get_user_spending_pattern(current_user.id)
    
    if not spending_pattern:
        return {
            "message": "No spending data available for analysis",
            "potential_savings": 0.0
        }
    
    # Get current rewards (assuming no optimized card usage)
    current_rewards = sum(amount * 0.005 for amount in spending_pattern.values()) * 12  # Assume 0.5% base rate
    
    # Get optimized recommendations
    recommendations = engine.optimize_card_combination(current_user.id)
    
    if not recommendations:
        return {
            "message": "No optimization recommendations available",
            "potential_savings": 0.0
        }
    
    best_combination = recommendations[0]
    potential_savings = best_combination.net_benefit - current_rewards
    
    return {
        "current_estimated_rewards": current_rewards,
        "optimized_rewards": best_combination.projected_cashback,
        "potential_annual_savings": potential_savings,
        "recommended_cards": [
            {
                "name": card.name,
                "bank": card.bank,
                "annual_fee": card.annual_fee
            }
            for card in best_combination.cards
        ],
        "spending_pattern": spending_pattern
    }

@router.get("/dashboard-summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get summary data for the dashboard"""
    # Current month spending
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_spending = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= current_month_start
    ).scalar() or 0.0
    
    # Last month spending
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = current_month_start - timedelta(seconds=1)
    last_month_spending = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= last_month_start,
        Expense.expense_date <= last_month_end
    ).scalar() or 0.0
    
    # Total transactions this month
    current_month_transactions = db.query(func.count(Expense.id)).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= current_month_start
    ).scalar() or 0
    
    # Top category this month
    top_category = db.query(
        Category.name,
        func.sum(Expense.amount).label('total')
    ).join(
        Merchant, Category.id == Merchant.category_id
    ).join(
        Expense, Merchant.id == Expense.merchant_id
    ).filter(
        Expense.user_id == current_user.id,
        Expense.expense_date >= current_month_start
    ).group_by(Category.name).order_by(func.sum(Expense.amount).desc()).first()
    
    # Calculate month-over-month change
    spending_change = 0.0
    if last_month_spending > 0:
        spending_change = ((current_month_spending - last_month_spending) / last_month_spending) * 100
    
    return {
        "current_month_spending": float(current_month_spending),
        "last_month_spending": float(last_month_spending),
        "spending_change_percentage": spending_change,
        "current_month_transactions": current_month_transactions,
        "top_category": top_category.name if top_category else "No data",
        "top_category_amount": float(top_category.total) if top_category else 0.0,
        "average_transaction": float(current_month_spending) / current_month_transactions if current_month_transactions > 0 else 0.0
    }