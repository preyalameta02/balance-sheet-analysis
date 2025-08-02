# 🚀 Free Deployment Guide

This guide will help you deploy your Balance Sheet Analysis app for free using Railway (backend) and Vercel (frontend).

## 📋 Prerequisites

1. **GitHub Account** - For hosting your code
2. **Railway Account** - For backend deployment (free tier)
3. **Vercel Account** - For frontend deployment (free tier)
4. **OpenAI API Key** - For AI features (optional, has fallback)

## 🔧 Step 1: Prepare Your Code

### 1.1 Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create a new repository on GitHub and push
git remote add origin https://github.com/yourusername/balance-sheet-analysis.git
git push -u origin main
```

### 1.2 Environment Variables
Create a `.env` file in your project root:
```bash
# Database (Railway will provide this)
DATABASE_URL=your_railway_postgres_url

# JWT Secret (generate a strong secret)
SECRET_KEY=your-super-secret-jwt-key-change-this

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Frontend URL (update after Vercel deployment)
FRONTEND_URL=https://your-app.vercel.app
```

## 🚂 Step 2: Deploy Backend to Railway

### 2.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

### 2.2 Deploy Backend
1. **Connect GitHub Repository**
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect it's a Python app

2. **Add PostgreSQL Database**
   - Go to your project dashboard
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will automatically add `DATABASE_URL` to your environment

3. **Configure Environment Variables**
   - Go to "Variables" tab
   - Add these variables:
   ```
   SECRET_KEY=your-super-secret-jwt-key-change-this
   OPENAI_API_KEY=your-openai-api-key
   FRONTEND_URL=https://your-app.vercel.app
   ```

4. **Deploy**
   - Railway will automatically deploy when you push to GitHub
   - Your backend will be available at: `https://your-app-name.railway.app`

### 2.3 Test Backend
```bash
# Test your API
curl https://your-app-name.railway.app/docs
```

## ⚡ Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository

### 3.2 Configure Frontend
1. **Set Build Settings**
   - Framework Preset: `Create React App`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

2. **Add Environment Variables**
   - Go to "Settings" → "Environment Variables"
   - Add:
   ```
   REACT_APP_API_URL=https://your-app-name.railway.app
   ```

3. **Deploy**
   - Click "Deploy"
   - Your frontend will be available at: `https://your-app-name.vercel.app`

### 3.3 Update Backend CORS
1. Go back to Railway dashboard
2. Update `FRONTEND_URL` to your Vercel URL
3. Redeploy the backend

## 🗄️ Step 4: Database Setup

### 4.1 Run Migrations
```bash
# Connect to Railway's PostgreSQL
railway run python -c "
from app.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created!')
"
```

### 4.2 Seed Data
```bash
# Run seed script
railway run python seed_data.py
```

## 🔍 Step 5: Test Your Deployment

### 5.1 Test URLs
- **Frontend**: `https://your-app-name.vercel.app`
- **Backend API**: `https://your-app-name.railway.app`
- **API Docs**: `https://your-app-name.railway.app/docs`

### 5.2 Test Features
1. **Register/Login**: Create test accounts
2. **Upload PDF**: Test file upload
3. **Chat**: Test AI features
4. **Charts**: Test data visualization

## 🛠️ Troubleshooting

### Common Issues

#### 1. CORS Errors
- Ensure `FRONTEND_URL` is set correctly in Railway
- Check that the URL includes `https://`

#### 2. Database Connection
- Verify `DATABASE_URL` is set in Railway
- Check that the URL starts with `postgresql://`

#### 3. Build Failures
- Check Railway logs for Python dependency issues
- Ensure all requirements are in `requirements.txt`

#### 4. Frontend Not Loading
- Check Vercel build logs
- Verify `REACT_APP_API_URL` is set correctly

### Debug Commands
```bash
# Check Railway logs
railway logs

# Check Vercel logs
vercel logs

# Test database connection
railway run python -c "from app.database import engine; print('DB connected!')"
```

## 📊 Monitoring

### Railway Monitoring
- **Logs**: View real-time logs in Railway dashboard
- **Metrics**: Monitor CPU, memory usage
- **Deployments**: Track deployment history

### Vercel Monitoring
- **Analytics**: View page views and performance
- **Functions**: Monitor API calls
- **Builds**: Track build success/failure

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Both Railway and Vercel provide HTTPS by default
3. **CORS**: Only allow your frontend domain
4. **Rate Limiting**: Consider adding rate limiting for production

## 💰 Cost Optimization

### Railway Free Tier
- **Usage**: $5/month credit
- **Limits**: 500 hours/month for hobby plan
- **Database**: 1GB PostgreSQL included

### Vercel Free Tier
- **Usage**: Unlimited static sites
- **Limits**: 100GB bandwidth/month
- **Functions**: 100GB-hours/month

## 🚀 Next Steps

1. **Custom Domain**: Add your own domain
2. **SSL Certificate**: Automatically provided by Railway/Vercel
3. **CDN**: Vercel provides global CDN
4. **Monitoring**: Set up alerts for downtime
5. **Backup**: Set up database backups

## 📞 Support

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **GitHub**: Your repository issues

---

🎉 **Congratulations!** Your Balance Sheet Analysis app is now live and accessible to users worldwide! 