# Balance Sheet Analysis Platform

A full-stack AI-powered financial analysis platform that parses balance sheet PDFs, extracts structured data, and provides natural language Q&A capabilities with role-based access control.

## 📋 Project Documentation

- **📊 [Development Report](https://docs.google.com/document/d/1lAWIoOJZpNKrlxrxxCJFqw2D0iOofbhBc1k8WJl3yeQ/edit?usp=sharing)** - Comprehensive technical report detailing architecture, challenges, and solutions
- **🎯 [Project Presentation](https://www.loom.com/share/2cf53e24d7494475bdbc385e7fddbe48?sid=ef3c61af-0236-4be1-9b5e-f5bceab7ad24)** - Visual presentation of features and capabilities

## 🚀 Live Demo

- **Frontend**: [https://balance-sheet-analysis-one.vercel.app](https://balance-sheet-analysis-one.vercel.app)
- **Backend API**: [https://web-production-35e92.up.railway.app](https://web-production-35e92.up.railway.app)

## ✨ Features

### 🔐 Role-Based Access Control
- **Analysts**: Access assigned companies only
- **CEOs**: Access all companies in their organization  
- **Ambani Family**: Access all data across all companies

### 📄 PDF Processing
- Extract financial data from balance sheets, P&L statements, and cash flow statements
- Memory-efficient processing for large PDFs (100+ pages)
- Support for complex table structures and varying formats
- Automatic data cleaning and validation

### 🤖 AI-Powered Analysis
- Natural language Q&A using OpenAI GPT-4/o4-mini
- Context-aware financial data retrieval
- Dynamic chart generation
- Fallback responses for API limitations

### 📊 Data Visualization
- Interactive charts using Chart.js
- Real-time financial data analysis
- Customizable dashboards per user role
- Export capabilities for reports

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt
- **PDF Processing**: PyMuPDF, pdfplumber
- **AI Integration**: LangChain, OpenAI GPT-4/o4-mini
- **Deployment**: Railway

### Frontend
- **Framework**: React 18 with functional components
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Charts**: Chart.js
- **Deployment**: Vercel

## 📁 Project Structure

```
bs-analysis/
├── app/                    # Backend FastAPI application
│   ├── __init__.py
│   ├── main.py            # Main FastAPI app with all endpoints
│   ├── config.py          # Configuration and environment variables
│   ├── database.py        # Database connection and session
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic schemas for validation
│   ├── auth.py            # JWT authentication and password hashing
│   ├── pdf_parser.py      # PDF processing and data extraction
│   └── ai_chat.py         # AI chat functionality
├── frontend/              # React frontend application
│   ├── public/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts (AuthContext)
│   │   └── index.js       # App entry point
│   └── package.json
├── uploads/               # PDF upload directory
├── requirements.txt       # Python dependencies
├── railway.json          # Railway deployment config
├── Procfile             # Railway process file
├── runtime.txt          # Python version
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 16+
- PostgreSQL database
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/preyalameta02/balance-sheet-analysis.git
   cd balance-sheet-analysis
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp env.example .env
   # Edit .env with your configuration
   
   # Run the backend
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname
DATABASE_PUBLIC_URL=postgresql://user:password@localhost/dbname

# JWT Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
FRONTEND_URL=https://your-frontend-domain.com
```

## 📚 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /users/me` - Get current user info

### PDF Processing
- `POST /upload` - Upload and process PDF
- `POST /debug-pdf-upload` - Debug PDF processing
- `POST /detailed-pdf-debug` - Detailed PDF analysis

### Data Management
- `GET /data` - Get financial data
- `GET /companies` - Get companies (role-based)
- `GET /metrics` - Get available metrics
- `GET /chart-data` - Get chart data

### AI Chat
- `POST /chat` - AI-powered Q&A

### Admin
- `POST /add-test-data` - Add sample data (Ambani Family only)
- `POST /add-sample-data` - Add sample financial data

## 🗄 Database Schema

### Core Tables
```sql
-- Users with role-based access
users (
  id, email, password_hash, role, 
  assigned_companies, created_at, updated_at
)

-- Companies
companies (id, name, created_at)

-- Financial data entries
balance_sheet_entries (
  id, company_id, fiscal_year, metric_type, 
  value, description, created_at
)

-- Uploaded documents
raw_documents (
  id, company_id, file_url, file_name, 
  processed, upload_time
)
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt
- **Role-Based Access**: Granular permissions
- **CORS Protection**: Cross-origin resource sharing
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM
- **File Upload Security**: Type and size validation

## 📊 Sample Queries

The AI chat supports natural language queries like:
- "Show Jio's net profit over the last 2 years"
- "What's the YoY change in liabilities?"
- "Compare total assets between 2023 and 2024"
- "Generate a chart for revenue trends"

## 🚀 Deployment

### Backend (Railway)
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `build`
4. Deploy automatically on push to main branch

## 🧪 Testing

### Backend Testing
```bash
# Run with virtual environment activated
pytest app/tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Performance

- **Response Time**: < 2 seconds for most API calls
- **PDF Processing**: Handles 100+ page documents efficiently
- **Memory Usage**: Optimized chunked processing
- **Uptime**: 99.9% availability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👥 Team

- **Developer**: Preyal Ameta
- **Project**: Balance Sheet Analysis Platform
- **Technology**: FastAPI, React, AI/ChatGPT, PostgreSQL

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact: ameta.preyal@gmail.com

---