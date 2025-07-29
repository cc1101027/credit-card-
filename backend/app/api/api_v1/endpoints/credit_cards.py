from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import CreditCard, CardReward, Category, Merchant
from app.schemas import CreditCard as CreditCardSchema, CardReward as CardRewardSchema
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[CreditCardSchema])
def get_credit_cards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all available credit cards"""
    cards = db.query(CreditCard).filter(CreditCard.is_active == True).offset(skip).limit(limit).all()
    return cards

@router.get("/{card_id}", response_model=CreditCardSchema)
def get_credit_card(card_id: int, db: Session = Depends(get_db)):
    """Get a specific credit card by ID"""
    card = db.query(CreditCard).filter(CreditCard.id == card_id, CreditCard.is_active == True).first()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    return card

@router.get("/{card_id}/rewards", response_model=List[CardRewardSchema])
def get_card_rewards(card_id: int, db: Session = Depends(get_db)):
    """Get reward structure for a specific credit card"""
    card = db.query(CreditCard).filter(CreditCard.id == card_id, CreditCard.is_active == True).first()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    rewards = db.query(CardReward).filter(
        CardReward.credit_card_id == card_id,
        CardReward.is_active == True
    ).all()
    return rewards

@router.get("/bank/{bank_name}", response_model=List[CreditCardSchema])
def get_cards_by_bank(bank_name: str, db: Session = Depends(get_db)):
    """Get all credit cards from a specific bank"""
    cards = db.query(CreditCard).filter(
        CreditCard.bank.ilike(f"%{bank_name}%"),
        CreditCard.is_active == True
    ).all()
    return cards

@router.post("/initialize-malaysian-cards")
def initialize_malaysian_cards(db: Session = Depends(get_db)):
    """Initialize the database with popular Malaysian credit cards"""
    
    # Check if cards already exist
    existing_cards = db.query(CreditCard).count()
    if existing_cards > 0:
        return {"message": "Cards already initialized", "count": existing_cards}
    
    # Malaysian Credit Cards Data
    malaysian_cards = [
        # Maybank Cards
        {
            "name": "Maybank 2 Cards",
            "bank": "Maybank",
            "card_type": "cashback",
            "annual_fee": 0.0,
            "minimum_income": 24000.0,
            "description": "5% cashback on weekend dining, 2% on groceries and petrol"
        },
        {
            "name": "Maybank Islamic Ikhwan Card",
            "bank": "Maybank",
            "card_type": "islamic",
            "annual_fee": 0.0,
            "minimum_income": 24000.0,
            "description": "Islamic compliant card with cashback rewards"
        },
        {
            "name": "Maybank Treats General Card",
            "bank": "Maybank",
            "card_type": "points",
            "annual_fee": 150.0,
            "minimum_income": 36000.0,
            "description": "Earn TreatsPoints for dining, shopping and travel"
        },
        
        # CIMB Cards
        {
            "name": "CIMB Cash Rebate Platinum",
            "bank": "CIMB",
            "card_type": "cashback",
            "annual_fee": 0.0,
            "minimum_income": 36000.0,
            "description": "8% cashback on petrol, 0.2% on other purchases"
        },
        {
            "name": "CIMB Preferred Visa Infinite",
            "bank": "CIMB",
            "card_type": "points",
            "annual_fee": 800.0,
            "minimum_income": 150000.0,
            "description": "Premium card with travel benefits and rewards"
        },
        
        # Public Bank Cards
        {
            "name": "Public Bank Quantum Visa",
            "bank": "Public Bank",
            "card_type": "cashback",
            "annual_fee": 0.0,
            "minimum_income": 24000.0,
            "description": "5% cashback on petrol, 1% on other purchases"
        },
        
        # RHB Cards
        {
            "name": "RHB Easy Visa",
            "bank": "RHB",
            "card_type": "cashback",
            "annual_fee": 0.0,
            "minimum_income": 24000.0,
            "description": "5% cashback on groceries and petrol"
        },
        
        # Hong Leong Cards
        {
            "name": "Hong Leong Wise Platinum",
            "bank": "Hong Leong",
            "card_type": "cashback",
            "annual_fee": 0.0,
            "minimum_income": 36000.0,
            "description": "5% cashback on petrol and groceries"
        },
        
        # AmBank Cards
        {
            "name": "AmBank True Cash Back",
            "bank": "AmBank",
            "card_type": "cashback",
            "annual_fee": 0.0,
            "minimum_income": 30000.0,
            "description": "5% cashback on petrol, 1% on other purchases"
        },
        
        # Standard Chartered Cards
        {
            "name": "Standard Chartered Platinum",
            "bank": "Standard Chartered",
            "card_type": "points",
            "annual_fee": 150.0,
            "minimum_income": 42000.0,
            "description": "Earn points on dining and shopping"
        }
    ]
    
    # Add cards to database
    for card_data in malaysian_cards:
        card = CreditCard(**card_data)
        db.add(card)
    
    db.commit()
    
    return {"message": f"Successfully initialized {len(malaysian_cards)} Malaysian credit cards"}