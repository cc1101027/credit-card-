# Malaysian Credit Card Recommender - Setup Guide

## Overview
This guide will help you set up and run the Malaysian Credit Card Recommender system locally.

## Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)

## Quick Start with Docker

1. **Clone and navigate to the project:**
```bash
git clone <repository-url>
cd credit-card-recommender
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Initialize the database:**
```bash
docker-compose exec backend python app/db/init_data.py
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Manual Setup

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database:**
```bash
createdb credit_card_recommender
```

5. **Configure environment variables:**
Create a `.env` file in the backend directory:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=credit_card_recommender
POSTGRES_PORT=5432
SECRET_KEY=your-secret-key-here
```

6. **Initialize database:**
```bash
python app/db/init_data.py
```

7. **Start the backend server:**
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure environment variables:**
Create a `.env` file in the frontend directory:
```env
REACT_APP_API_URL=http://localhost:8000
```

4. **Start the frontend server:**
```bash
npm start
```

## Features

### 1. User Authentication
- Register new account
- Login with email/password
- JWT-based authentication

### 2. Expense Tracking
- Add expenses with Malaysian merchant categories
- Track spending across different categories
- Monthly expense summaries

### 3. Credit Card Management
- Browse Malaysian credit cards
- Add cards to personal wallet
- View card details and reward structures

### 4. Smart Recommendations
- Analyze spending patterns
- Optimize credit card combinations
- Calculate potential savings
- Real-time purchase advice

### 5. Analytics Dashboard
- Spending trends visualization
- Category breakdown charts
- Monthly comparisons
- Savings potential analysis

## Malaysian Credit Cards Included

### Cashback Cards
- **Maybank 2 Cards**: 5% weekend dining, 2% groceries/petrol
- **CIMB Cash Rebate Platinum**: 8% petrol cashback
- **Public Bank Quantum Visa**: 5% petrol cashback
- **RHB Easy Visa**: 5% groceries and petrol
- **Hong Leong Wise Platinum**: 5% petrol and groceries
- **AmBank True Cash Back**: 5% petrol cashback

### Points/Miles Cards
- **Maybank Treats General**: TreatsPoints for dining/shopping
- **Standard Chartered Platinum**: Points on dining and shopping

## Merchant Categories

- **Dining**: McDonald's, KFC, Starbucks, Local restaurants
- **Groceries**: AEON, Tesco, Giant, Jaya Grocer
- **Petrol**: Shell, Petronas, BHP, Caltex
- **E-commerce**: Shopee, Lazada, Zalora
- **Transportation**: Grab, Touch 'n Go, Public transport
- **Entertainment**: GSC, Netflix, Spotify
- **Bills & Utilities**: TNB, Maxis, Celcom, Digi
- **Healthcare**: Guardian, Watsons, Clinics
- **Shopping**: Pavilion KL, KLCC, Mid Valley
- **Travel**: AirAsia, Malaysia Airlines, Hotels

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login

### Credit Cards
- `GET /api/v1/credit-cards/` - List all cards
- `GET /api/v1/credit-cards/{id}` - Get card details
- `POST /api/v1/credit-cards/initialize-malaysian-cards` - Initialize card database

### Expenses
- `POST /api/v1/expenses/` - Add new expense
- `GET /api/v1/expenses/` - List user expenses
- `GET /api/v1/expenses/summary/monthly` - Monthly summary

### Recommendations
- `POST /api/v1/recommendations/optimize` - Get optimized card combinations
- `GET /api/v1/recommendations/purchase-advice` - Get purchase advice
- `GET /api/v1/recommendations/spending-analysis` - Analyze spending patterns

### Analytics
- `GET /api/v1/analytics/dashboard-summary` - Dashboard data
- `GET /api/v1/analytics/spending-trends` - Spending trends
- `GET /api/v1/analytics/category-breakdown` - Category analysis

## Troubleshooting

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d db
docker-compose exec backend python app/db/init_data.py
```

### Frontend Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Backend Issues
```bash
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

## Development

### Adding New Credit Cards
1. Update `backend/app/db/init_data.py`
2. Add card data with reward structures
3. Restart the application

### Adding New Merchants
1. Update the merchants_data in `init_data.py`
2. Assign to appropriate categories
3. Reinitialize the database

### Customizing Recommendations
1. Modify `backend/app/services/recommendation_engine.py`
2. Adjust optimization algorithms
3. Update reward calculations

## Production Deployment

### Environment Variables
Set these in production:
```env
SECRET_KEY=strong-random-secret-key
POSTGRES_PASSWORD=secure-password
API_V1_STR=/api/v1
```

### Database Migration
```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### Security Considerations
- Use HTTPS in production
- Set strong SECRET_KEY
- Configure CORS properly
- Use environment variables for secrets
- Regular security updates

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify database connectivity

## License
MIT License - see LICENSE file for details.