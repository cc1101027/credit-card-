from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, credit_cards, expenses, recommendations, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(credit_cards.router, prefix="/credit-cards", tags=["credit-cards"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])