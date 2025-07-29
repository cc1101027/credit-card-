from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CardType(str, Enum):
    CASHBACK = "cashback"
    POINTS = "points"
    MILES = "miles"
    ISLAMIC = "islamic"

class RewardType(str, Enum):
    CASHBACK = "cashback"
    POINTS = "points"
    MILES = "miles"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Credit Card Schemas
class CreditCardBase(BaseModel):
    name: str
    bank: str
    card_type: CardType
    annual_fee: float = 0.0
    minimum_income: Optional[float] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CreditCardCreate(CreditCardBase):
    pass

class CreditCard(CreditCardBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

# Merchant Schemas
class MerchantBase(BaseModel):
    name: str
    category_id: int
    mcc_code: Optional[str] = None
    logo_url: Optional[str] = None

class MerchantCreate(MerchantBase):
    pass

class Merchant(MerchantBase):
    id: int
    category: Category
    
    class Config:
        from_attributes = True

# Card Reward Schemas
class CardRewardBase(BaseModel):
    credit_card_id: int
    category_id: Optional[int] = None
    merchant_id: Optional[int] = None
    reward_type: RewardType
    reward_rate: float
    minimum_spend: float = 0.0
    maximum_spend: Optional[float] = None
    conditions: Optional[str] = None

class CardRewardCreate(CardRewardBase):
    pass

class CardReward(CardRewardBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# Expense Schemas
class ExpenseBase(BaseModel):
    merchant_id: int
    amount: float
    description: Optional[str] = None
    expense_date: datetime
    credit_card_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    merchant_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    expense_date: Optional[datetime] = None
    credit_card_id: Optional[int] = None

class Expense(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    merchant: Merchant
    
    class Config:
        from_attributes = True

# User Card Schemas
class UserCardBase(BaseModel):
    credit_card_id: int

class UserCardCreate(UserCardBase):
    pass

class UserCard(UserCardBase):
    id: int
    user_id: int
    added_at: datetime
    is_active: bool
    credit_card: CreditCard
    
    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationRequest(BaseModel):
    analysis_period: Optional[str] = None  # e.g., "2024-01" or None for current month

class CardCombination(BaseModel):
    cards: List[CreditCard]
    projected_cashback: float
    projected_points: float
    total_annual_fee: float
    net_benefit: float

class RecommendationResponse(BaseModel):
    user_id: int
    analysis_period: str
    current_spending: dict  # Category -> Amount
    recommendations: List[CardCombination]
    potential_savings: float
    generated_at: datetime

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Analytics Schemas
class SpendingByCategory(BaseModel):
    category: Category
    total_amount: float
    transaction_count: int
    percentage: float

class MonthlySpending(BaseModel):
    month: str
    total_amount: float
    categories: List[SpendingByCategory]

class SpendingAnalytics(BaseModel):
    user_id: int
    period: str
    total_spending: float
    monthly_breakdown: List[MonthlySpending]
    top_categories: List[SpendingByCategory]
    top_merchants: List[dict]