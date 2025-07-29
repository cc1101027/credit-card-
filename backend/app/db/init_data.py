from sqlalchemy.orm import Session
from app.db.models import CreditCard, CardReward, Category, Merchant, CardType, RewardType
from app.db.database import SessionLocal

def initialize_malaysian_credit_cards_and_rewards(db: Session):
    """Initialize Malaysian credit cards with their reward structures"""
    
    # Check if data already exists
    if db.query(CreditCard).count() > 0:
        print("Credit cards already initialized")
        return
    
    # Create categories first
    categories_data = [
        {"name": "Dining", "description": "Restaurant and food expenses", "icon": "🍽️"},
        {"name": "Groceries", "description": "Supermarket and grocery shopping", "icon": "🛒"},
        {"name": "Petrol", "description": "Fuel and petrol stations", "icon": "⛽"},
        {"name": "E-commerce", "description": "Online shopping platforms", "icon": "🛍️"},
        {"name": "Transportation", "description": "Grab, taxi, public transport", "icon": "🚗"},
        {"name": "Entertainment", "description": "Movies, streaming, gaming", "icon": "🎬"},
        {"name": "Bills & Utilities", "description": "Electricity, water, telco bills", "icon": "📄"},
        {"name": "Healthcare", "description": "Medical, pharmacy, wellness", "icon": "🏥"},
        {"name": "Shopping", "description": "Retail stores and malls", "icon": "🏬"},
        {"name": "Travel", "description": "Airlines, hotels, booking", "icon": "✈️"},
        {"name": "General", "description": "All other purchases", "icon": "💳"}
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        db.flush()
        categories[cat_data["name"]] = category
    
    # Malaysian Credit Cards with detailed reward structures
    cards_data = [
        {
            "card": {
                "name": "Maybank 2 Cards",
                "bank": "Maybank",
                "card_type": CardType.CASHBACK,
                "annual_fee": 0.0,
                "minimum_income": 24000.0,
                "description": "5% cashback on weekend dining, 2% on groceries and petrol"
            },
            "rewards": [
                {"category": "Dining", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "conditions": "Weekends only"},
                {"category": "Groceries", "reward_type": RewardType.CASHBACK, "reward_rate": 0.02, "maximum_spend": 300.0},
                {"category": "Petrol", "reward_type": RewardType.CASHBACK, "reward_rate": 0.02, "maximum_spend": 300.0},
                {"category": "General", "reward_type": RewardType.CASHBACK, "reward_rate": 0.005}
            ]
        },
        {
            "card": {
                "name": "CIMB Cash Rebate Platinum",
                "bank": "CIMB",
                "card_type": CardType.CASHBACK,
                "annual_fee": 0.0,
                "minimum_income": 36000.0,
                "description": "8% cashback on petrol, 0.2% on other purchases"
            },
            "rewards": [
                {"category": "Petrol", "reward_type": RewardType.CASHBACK, "reward_rate": 0.08, "maximum_spend": 500.0},
                {"category": "General", "reward_type": RewardType.CASHBACK, "reward_rate": 0.002}
            ]
        },
        {
            "card": {
                "name": "Public Bank Quantum Visa",
                "bank": "Public Bank",
                "card_type": CardType.CASHBACK,
                "annual_fee": 0.0,
                "minimum_income": 24000.0,
                "description": "5% cashback on petrol, 1% on other purchases"
            },
            "rewards": [
                {"category": "Petrol", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "maximum_spend": 300.0},
                {"category": "General", "reward_type": RewardType.CASHBACK, "reward_rate": 0.01}
            ]
        },
        {
            "card": {
                "name": "RHB Easy Visa",
                "bank": "RHB",
                "card_type": CardType.CASHBACK,
                "annual_fee": 0.0,
                "minimum_income": 24000.0,
                "description": "5% cashback on groceries and petrol"
            },
            "rewards": [
                {"category": "Groceries", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "maximum_spend": 500.0},
                {"category": "Petrol", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "maximum_spend": 500.0},
                {"category": "General", "reward_type": RewardType.CASHBACK, "reward_rate": 0.005}
            ]
        },
        {
            "card": {
                "name": "Hong Leong Wise Platinum",
                "bank": "Hong Leong",
                "card_type": CardType.CASHBACK,
                "annual_fee": 0.0,
                "minimum_income": 36000.0,
                "description": "5% cashback on petrol and groceries"
            },
            "rewards": [
                {"category": "Petrol", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "maximum_spend": 400.0},
                {"category": "Groceries", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "maximum_spend": 400.0},
                {"category": "General", "reward_type": RewardType.CASHBACK, "reward_rate": 0.005}
            ]
        },
        {
            "card": {
                "name": "AmBank True Cash Back",
                "bank": "AmBank",
                "card_type": CardType.CASHBACK,
                "annual_fee": 0.0,
                "minimum_income": 30000.0,
                "description": "5% cashback on petrol, 1% on other purchases"
            },
            "rewards": [
                {"category": "Petrol", "reward_type": RewardType.CASHBACK, "reward_rate": 0.05, "maximum_spend": 200.0},
                {"category": "General", "reward_type": RewardType.CASHBACK, "reward_rate": 0.01}
            ]
        },
        {
            "card": {
                "name": "Maybank Treats General Card",
                "bank": "Maybank",
                "card_type": CardType.POINTS,
                "annual_fee": 150.0,
                "minimum_income": 36000.0,
                "description": "Earn TreatsPoints for dining, shopping and travel"
            },
            "rewards": [
                {"category": "Dining", "reward_type": RewardType.POINTS, "reward_rate": 5.0},
                {"category": "Shopping", "reward_type": RewardType.POINTS, "reward_rate": 3.0},
                {"category": "Travel", "reward_type": RewardType.POINTS, "reward_rate": 3.0},
                {"category": "General", "reward_type": RewardType.POINTS, "reward_rate": 1.0}
            ]
        },
        {
            "card": {
                "name": "Standard Chartered Platinum",
                "bank": "Standard Chartered",
                "card_type": CardType.POINTS,
                "annual_fee": 150.0,
                "minimum_income": 42000.0,
                "description": "Earn points on dining and shopping"
            },
            "rewards": [
                {"category": "Dining", "reward_type": RewardType.POINTS, "reward_rate": 4.0},
                {"category": "Shopping", "reward_type": RewardType.POINTS, "reward_rate": 2.0},
                {"category": "General", "reward_type": RewardType.POINTS, "reward_rate": 1.0}
            ]
        }
    ]
    
    # Create cards and their rewards
    for card_data in cards_data:
        # Create credit card
        card = CreditCard(**card_data["card"])
        db.add(card)
        db.flush()
        
        # Create card rewards
        for reward_data in card_data["rewards"]:
            category_name = reward_data.pop("category")
            category = categories[category_name]
            
            card_reward = CardReward(
                credit_card_id=card.id,
                category_id=category.id,
                **reward_data
            )
            db.add(card_reward)
    
    db.commit()
    print(f"Successfully initialized {len(cards_data)} Malaysian credit cards with rewards")

def initialize_malaysian_merchants(db: Session):
    """Initialize Malaysian merchants"""
    
    if db.query(Merchant).count() > 0:
        print("Merchants already initialized")
        return
    
    # Get categories
    categories = {cat.name: cat for cat in db.query(Category).all()}
    
    merchants_data = {
        "Dining": [
            "McDonald's", "KFC", "Pizza Hut", "Burger King", "Subway",
            "Starbucks", "Old Town White Coffee", "Secret Recipe",
            "Sushi King", "Sakae Sushi", "Local Restaurant", "Mamak Stall"
        ],
        "Groceries": [
            "AEON", "Tesco", "Giant", "Jaya Grocer", "Cold Storage",
            "Village Grocer", "Mercato", "Ben's Independent Grocer",
            "NSK Trade City", "Econsave", "99 Speedmart"
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
    
    total_merchants = 0
    for category_name, merchant_names in merchants_data.items():
        category = categories.get(category_name)
        if category:
            for merchant_name in merchant_names:
                merchant = Merchant(
                    name=merchant_name,
                    category_id=category.id
                )
                db.add(merchant)
                total_merchants += 1
    
    db.commit()
    print(f"Successfully initialized {total_merchants} Malaysian merchants")

def main():
    """Initialize all data"""
    db = SessionLocal()
    try:
        print("Initializing Malaysian credit card recommender data...")
        initialize_malaysian_credit_cards_and_rewards(db)
        initialize_malaysian_merchants(db)
        print("Data initialization completed successfully!")
    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()