# Balance Sheet Analyst - AI-Powered Financial Analysis Tool

A full-stack AI application for analyzing company balance sheets from PDFs with natural language Q&A capabilities.

## 🚀 Features

- **PDF Processing**: Upload and parse balance sheet PDFs using PyMuPDF and pdfplumber
- **AI Chat**: Natural language Q&A about financial data using GPT-4
- **Data Visualization**: Interactive charts and tables for financial metrics
- **Role-Based Access Control**: 
  - **Analyst**: View assigned companies
  - **CEO**: View company-specific data
  - **Ambani Family**: Access all verticals
- **Real-time Charts**: Line and bar charts with Chart.js
- **Modern UI**: Beautiful React frontend with Tailwind CSS

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **FastAPI**: RESTful API with JWT authentication
- **PostgreSQL**: Relational database for financial data
- **PyMuPDF/pdfplumber**: PDF parsing and data extraction
- **LangChain + OpenAI**: AI-powered chat functionality
- **SQLAlchemy**: ORM for database operations

### Frontend (React + Tailwind)
- **React 18**: Modern UI components
- **Tailwind CSS**: Utility-first styling
- **Chart.js**: Interactive data visualizations
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- OpenAI API key

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd balance-sheet-analyst
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Database Setup
1. Create a PostgreSQL database
2. Update the database URL in `env.example` and rename to `.env`
3. Run database migrations:
```bash
# Create tables (already handled in main.py)
python -c "from app.main import app; print('Database tables created')"
```

#### Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/balance_sheet_db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Backend
```bash
# From the root directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# From the frontend directory
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📊 Usage

### 1. User Registration
- Register with email, password, and role
- Roles: Analyst, CEO, Ambani Family

### 2. PDF Upload
- Upload balance sheet PDFs
- System automatically extracts financial data
- Supports multiple companies

### 3. Data Visualization
- Select company and metric
- View interactive charts and tables
- Export data for analysis

### 4. AI Chat
- Ask natural language questions
- Get AI-powered insights
- View generated charts and data

## 🔧 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /users/me` - Get current user

### File Management
- `POST /upload` - Upload and process PDF

### Data Access
- `GET /data` - Get financial data with filters
- `GET /chart-data` - Get chart data
- `GET /companies` - Get available companies
- `GET /metrics` - Get available metrics

### AI Chat
- `POST /chat` - AI-powered Q&A

## 🗄️ Database Schema

### Users
- `id`: Primary key
- `email`: User email
- `password_hash`: Hashed password
- `role`: User role (analyst/ceo/ambani_family)
- `assigned_companies`: JSON array of company IDs

### Companies
- `id`: Primary key
- `name`: Company name

### Balance Sheet Entries
- `id`: Primary key
- `company_id`: Foreign key to companies
- `fiscal_year`: Financial year
- `metric_type`: Type of financial metric
- `value`: Financial value in ₹ Crore
- `description`: Additional description

### Raw Documents
- `id`: Primary key
- `company_id`: Foreign key to companies
- `file_url`: Path to uploaded file
- `file_name`: Original filename
- `processed`: Processing status

## 🎯 Sample Queries

The AI chat supports questions like:
- "Show Jio's net profit over the last 2 years"
- "What's the YoY change in liabilities?"
- "How did cash flow change from 2023 to 2024?"
- "Visualize total equity trend for Jio Platforms"

## 🚀 Deployment

### Backend (Render/Railway)
1. Set environment variables
2. Deploy using Git integration
3. Configure PostgreSQL database

### Frontend (Vercel)
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Deploy automatically

## 🔒 Security Features

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- CORS protection
- File upload validation

## 📈 Performance

- Async PDF processing
- Efficient database queries
- Cached chart data
- Optimized React components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for financial analysis and AI-powered insights** 