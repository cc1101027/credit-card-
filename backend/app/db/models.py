from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class CardType(str, enum.Enum):
    CASHBACK = "cashback"
    POINTS = "points"
    MILES = "miles"
    ISLAMIC = "islamic"

class RewardType(str, enum.Enum):
    CASHBACK = "cashback"
    POINTS = "points"
    MILES = "miles"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    expenses = relationship("Expense", back_populates="user")
    user_cards = relationship("UserCard", back_populates="user")

class CreditCard(Base):
    __tablename__ = "credit_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bank = Column(String, nullable=False)
    card_type = Column(Enum(CardType), nullable=False)
    annual_fee = Column(Float, default=0.0)
    minimum_income = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    card_rewards = relationship("CardReward", back_populates="credit_card")
    user_cards = relationship("UserCard", back_populates="credit_card")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    
    # Relationships
    merchants = relationship("Merchant", back_populates="category")
    card_rewards = relationship("CardReward", back_populates="category")

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    mcc_code = Column(String, nullable=True)  # Merchant Category Code
    logo_url = Column(String, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="merchants")
    expenses = relationship("Expense", back_populates="merchant")

class CardReward(Base):
    __tablename__ = "card_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True)
    reward_type = Column(Enum(RewardType), nullable=False)
    reward_rate = Column(Float, nullable=False)  # e.g., 0.05 for 5% cashback
    minimum_spend = Column(Float, default=0.0)
    maximum_spend = Column(Float, nullable=True)  # Monthly cap
    conditions = Column(Text, nullable=True)  # Special conditions
    is_active = Column(Boolean, default=True)
    
    # Relationships
    credit_card = relationship("CreditCard", back_populates="card_rewards")
    category = relationship("Category", back_populates="card_rewards")

class UserCard(Base):
    __tablename__ = "user_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="user_cards")
    credit_card = relationship("CreditCard", back_populates="user_cards")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    expense_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional: Track which card was used for this expense
    credit_card_id = Column(Integer, ForeignKey("credit_cards.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="expenses")
    merchant = relationship("Merchant", back_populates="expenses")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommended_cards = Column(Text, nullable=False)  # JSON string of card combinations
    projected_savings = Column(Float, nullable=False)
    analysis_period = Column(String, nullable=False)  # e.g., "2024-01"
    created_at = Column(DateTime(timezone=True), server_default=func.now())