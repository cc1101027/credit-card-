from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, UserCard, CreditCard
from app.schemas import User as UserSchema, UserUpdate, UserCard as UserCardSchema, UserCardCreate
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/cards", response_model=List[UserCardSchema])
def get_user_cards(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's credit cards"""
    user_cards = db.query(UserCard).filter(
        UserCard.user_id == current_user.id,
        UserCard.is_active == True
    ).all()
    return user_cards

@router.post("/me/cards", response_model=UserCardSchema)
def add_user_card(
    card_data: UserCardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a credit card to user's wallet"""
    # Check if card exists
    card = db.query(CreditCard).filter(CreditCard.id == card_data.credit_card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Credit card not found")
    
    # Check if user already has this card
    existing_user_card = db.query(UserCard).filter(
        UserCard.user_id == current_user.id,
        UserCard.credit_card_id == card_data.credit_card_id,
        UserCard.is_active == True
    ).first()
    
    if existing_user_card:
        raise HTTPException(status_code=400, detail="Card already added to your wallet")
    
    user_card = UserCard(
        user_id=current_user.id,
        credit_card_id=card_data.credit_card_id
    )
    db.add(user_card)
    db.commit()
    db.refresh(user_card)
    
    return user_card

@router.delete("/me/cards/{card_id}")
def remove_user_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a credit card from user's wallet"""
    user_card = db.query(UserCard).filter(
        UserCard.user_id == current_user.id,
        UserCard.credit_card_id == card_id,
        UserCard.is_active == True
    ).first()
    
    if not user_card:
        raise HTTPException(status_code=404, detail="Card not found in your wallet")
    
    user_card.is_active = False
    db.commit()
    
    return {"message": "Card removed from wallet successfully"}