# 🚀 Quick Start Guide

Get the Balance Sheet Analyst running in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (or use SQLite for testing)

## 1. Setup Environment

```bash
# Clone and navigate to project
git clone <repository-url>
cd balance-sheet-analyst

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd frontend
npm install
cd ..
```

## 3. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
# For quick testing with SQLite:
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

## 4. Seed Sample Data

```bash
# Run the seeding script
python seed_data.py
```

## 5. Start the Application

```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Start manually
# Terminal 1 - Backend:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend:
cd frontend
npm start
```

## 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 7. Test with Sample Data

### Login Credentials
- **Analyst**: analyst@example.com / password123
- **CEO**: ceo@example.com / password123
- **Ambani Family**: ambani@example.com / password123

### Sample Companies
- Jio Platforms
- Reliance Industries
- Reliance Retail
- Reliance Jio Infocomm

### Test Queries
Try these in the AI Chat:
- "What was Jio's profit growth in 2024?"
- "Show me Jio's revenue trend"
- "Compare assets vs liabilities for Jio Platforms"

## 🎯 What to Test

1. **User Registration/Login**: Try different roles
2. **PDF Upload**: Upload any PDF (system will extract what it can)
3. **Data Visualization**: Select companies and metrics
4. **AI Chat**: Ask questions about financial data
5. **Role-based Access**: Test different user permissions

## 🔧 Troubleshooting

### Database Issues
```bash
# If using SQLite, the database will be created automatically
# If using PostgreSQL, make sure it's running and accessible
```

### Port Conflicts
```bash
# If ports are in use, change them in the startup commands
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
npm start -- --port 3001
```

### Missing Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

## 📊 Sample Data Included

The seeding script creates:
- 4 companies (Jio Platforms, Reliance Industries, etc.)
- 3 users with different roles
- Financial data for 2022-23 and 2023-24
- Multiple metrics: revenue, profit, assets, liabilities, equity, cash flow

## 🚀 Next Steps

1. **Add Real Data**: Upload actual balance sheet PDFs
2. **Configure OpenAI**: Add your API key for AI features
3. **Deploy**: Use the deployment guide in README.md
4. **Customize**: Modify the PDF parser for your specific documents

---

**Happy analyzing! 📈** 