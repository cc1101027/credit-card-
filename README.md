# Malaysian Credit Card Recommender System
testing
A web application that helps Malaysian users optimize their credit card usage by tracking expenses and recommending the best credit card combinations for maximum cashback and points.

## Features

- **Expense Tracking**: Track spending across detailed Malaysian merchant categories
- **Smart Recommendations**: Get optimal credit card suggestions for each purchase
- **Combination Optimization**: Find the best mix of credit cards for your spending pattern
- **Analytics Dashboard**: Visualize spending patterns and potential savings
- **Malaysian Focus**: Comprehensive database of Malaysian credit cards and merchants

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Deployment**: Docker

## Project Structure

```
credit-card-recommender/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── db/             # Database models and connection
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API calls
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)

### Installation

1. Clone the repository
2. Set up the backend (see backend/README.md)
3. Set up the frontend (see frontend/README.md)
4. Configure the database
5. Run the application

## Malaysian Credit Cards Supported

- Maybank (2 Cards, 2 Treats, Islamic)
- CIMB (Preferred, Cash Rebate, Islamic)
- Public Bank (Quantum, Visa Infinite)
- RHB (Easy, Rewards, Islamic)
- Hong Leong (Wise, Platinum)
- AmBank (True Cash Back, Islamic)
- Standard Chartered (Platinum, Unlimited)

## Merchant Categories

- E-commerce: Shopee, Lazada, Zalora
- Transportation: Grab, Touch 'n Go, Petrol stations
- Groceries: AEON, Tesco, Giant, Jaya Grocer
- Dining: McDonald's, KFC, local restaurants
- Bills: Utilities, telco, insurance
- Entertainment: Cinema, streaming services

## License

MIT License
