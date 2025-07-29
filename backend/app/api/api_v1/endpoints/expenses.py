from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db.database import get_db
from app.db.models import Expense, Merchant, Category, User
from app.schemas import (
    Expense as ExpenseSchema, 
    ExpenseCreate, 
    ExpenseUpdate,
    Merchant as MerchantSchema,
    Category as CategorySchema
)
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=ExpenseSchema)
def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new expense record"""
    # Verify merchant exists
    merchant = db.query(Merchant).filter(Merchant.id == expense.merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    db_expense = Expense(
        user_id=current_user.id,
        **expense.dict()
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@router.get("/", response_model=List[ExpenseSchema])
def get_expenses(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's expenses with optional filtering"""
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    if category_id:
        query = query.join(Merchant).filter(Merchant.category_id == category_id)
    
    expenses = query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseSchema)
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense

@router.put("/{expense_id}", response_model=ExpenseSchema)
def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = expense_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)
    
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

@router.get("/summary/monthly")
def get_monthly_summary(
    year: int = Query(datetime.now().year),
    month: int = Query(datetime.now().month),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get monthly expense summary by category"""
    summary = db.query(
        Category.name.label('category'),
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('transaction_count')
    ).join(
        Merchant, Expense.merchant_id == Merchant.id
    ).join(
        Category, Merchant.category_id == Category.id
    ).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.expense_date) == year,
        extract('month', Expense.expense_date) == month
    ).group_by(Category.id, Category.name).all()
    
    total_spending = sum(item.total_amount for item in summary)
    
    result = {
        "year": year,
        "month": month,
        "total_spending": total_spending,
        "categories": [
            {
                "category": item.category,
                "total_amount": item.total_amount,
                "transaction_count": item.transaction_count,
                "percentage": (item.total_amount / total_spending * 100) if total_spending > 0 else 0
            }
            for item in summary
        ]
    }
    
    return result

@router.get("/merchants/", response_model=List[MerchantSchema])
def get_merchants(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get available merchants for expense tracking"""
    query = db.query(Merchant)
    
    if category_id:
        query = query.filter(Merchant.category_id == category_id)
    if search:
        query = query.filter(Merchant.name.ilike(f"%{search}%"))
    
    merchants = query.order_by(Merchant.name).all()
    return merchants

@router.get("/categories/", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    """Get all expense categories"""
    categories = db.query(Category).order_by(Category.name).all()
    return categories

@router.post("/initialize-malaysian-merchants")
def initialize_malaysian_merchants(db: Session = Depends(get_db)):
    """Initialize Malaysian merchants and categories"""
    
    # Check if data already exists
    existing_categories = db.query(Category).count()
    if existing_categories > 0:
        return {"message": "Merchants and categories already initialized"}
    
    # Categories and their merchants
    categories_data = {
        "Dining": [
            "McDonald's", "KFC", "Pizza Hut", "Burger King", "Subway",
            "Starbucks", "Old Town White Coffee", "Secret Recipe",
            "Sushi King", "Sakae Sushi", "Local Restaurant"
        ],
        "Groceries": [
            "AEON", "Tesco", "Giant", "Jaya Grocer", "Cold Storage",
            "Village Grocer", "Mercato", "Ben's Independent Grocer",
            "NSK Trade City", "Econsave"
        ],
        "Petrol": [
            "Shell", "Petronas", "BHP", "Caltex", "Esso"
        ],
        "E-commerce": [
            "Shopee", "Lazada", "Zalora", "PG Mall", "11street",
            "Hermo", "FashionValet", "Mudah.my"
        ],
        "Transportation": [
            "Grab", "Touch 'n Go", "MyRapid", "KTM", "MRT",
            "LRT", "Taxi", "Bus"
        ],
        "Entertainment": [
            "GSC", "TGV", "MBO", "Netflix", "Spotify",
            "Disney+", "Astro", "Gaming"
        ],
        "Bills & Utilities": [
            "TNB", "Syabas", "Indah Water", "Astro", "Maxis",
            "Celcom", "Digi", "U Mobile", "TIME", "Unifi"
        ],
        "Healthcare": [
            "Guardian", "Watsons", "Caring", "Hospital",
            "Clinic", "Pharmacy"
        ],
        "Shopping": [
            "Pavilion KL", "KLCC", "Mid Valley", "1 Utama",
            "Sunway Pyramid", "IOI City Mall", "The Gardens"
        ],
        "Travel": [
            "AirAsia", "Malaysia Airlines", "Agoda", "Booking.com",
            "Hotels.com", "Airbnb", "Hotel"
        ]
    }
    
    # Create categories and merchants
    for category_name, merchants in categories_data.items():
        # Create category
        category = Category(
            name=category_name,
            description=f"{category_name} related expenses"
        )
        db.add(category)
        db.flush()  # Get the ID
        
        # Create merchants for this category
        for merchant_name in merchants:
            merchant = Merchant(
                name=merchant_name,
                category_id=category.id
            )
            db.add(merchant)
    
    db.commit()
    
    total_categories = len(categories_data)
    total_merchants = sum(len(merchants) for merchants in categories_data.values())
    
    return {
        "message": f"Successfully initialized {total_categories} categories and {total_merchants} merchants"
    }