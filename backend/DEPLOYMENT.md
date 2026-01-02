# 🚀 Hugging Face Deployment Guide

## Step-by-Step Instructions for Deploying Backend to Hugging Face Spaces

### 1. Prepare Your Database

You need a PostgreSQL database. Options:

**Option A: Free PostgreSQL Hosting**
- [Neon](https://neon.tech) - Free tier with PostgreSQL
- [Supabase](https://supabase.com) - Free tier with PostgreSQL
- [ElephantSQL](https://www.elephantsql.com) - Free tier (20MB)

**Option B: Use Hugging Face Persistent Storage**
- Enable persistent storage in Space settings
- Use SQLite instead (modify DATABASE_URL)

### 2. Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Navigate to API Keys
3. Create a new secret key
4. Copy and save it securely

### 3. Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in details:
   - **Space name**: `smart-todo-backend` (or your choice)
   - **License**: MIT
   - **SDK**: Select **Docker**
   - **Visibility**: Public or Private
4. Click **"Create Space"**

### 4. Upload Files to Hugging Face

**Method A: Git (Recommended)**

```bash
# Navigate to backend directory
cd backend

# Initialize git if not already
git init

# Add Hugging Face as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/smart-todo-backend

# Add all files
git add .

# Commit
git commit -m "Initial deployment"

# Push to Hugging Face
git push hf main
```

**Method B: Web Interface**

1. In your Space, click **"Files and versions"**
2. Click **"Add file"** > **"Upload files"**
3. Upload these files:
   - `app.py`
   - `Dockerfile`
   - `requirements-deploy.txt`
   - `README.md`
   - `alembic.ini`
   - Entire `src/` directory
   - Entire `alembic/` directory
4. Click **"Commit changes to main"**

### 5. Configure Environment Variables

1. In your Space, go to **Settings** tab
2. Scroll to **"Variables and secrets"**
3. Add the following secrets:

```bash
DATABASE_URL=postgresql://username:password@host:5432/dbname
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=your-random-secret-key-here
JWT_REFRESH_SECRET_KEY=your-random-refresh-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate Secret Keys:**
```bash
# In Python:
import secrets
print(secrets.token_urlsafe(32))
```

### 6. Run Database Migrations

Once your Space is running:

```bash
# SSH into your Space (if available) or run locally then migrate
alembic upgrade head
```

Alternatively, create tables manually using the API:
- The app will auto-create tables on first run (if init_db is enabled)

### 7. Test Your Deployment

1. Wait for build to complete (check logs)
2. Once running, visit: `https://YOUR_USERNAME-smart-todo-backend.hf.space/docs`
3. Test endpoints:
   - Health check: `GET /health`
   - Signup: `POST /api/auth/signup`
   - Signin: `POST /api/auth/signin`

### 8. Configure CORS for Frontend

If you have a frontend deployed elsewhere:

1. Add to environment variables:
```bash
CORS_ORIGINS=https://your-frontend-url.com,https://another-allowed-origin.com
```

2. Or update `src/api/middleware/cors.py` before deployment

### 9. Monitor Your Space

- **Logs**: Check Space logs for errors
- **Metrics**: Monitor usage in Space settings
- **Restart**: If needed, restart from Space settings

## 🔧 Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all dependencies in requirements-deploy.txt
- Check logs for specific errors

### Database Connection Fails
- Verify DATABASE_URL format
- Check database host is accessible
- Ensure database exists

### API Returns 500 Errors
- Check environment variables are set
- Review application logs
- Verify OpenAI API key is valid

### CORS Errors
- Add frontend URL to CORS_ORIGINS
- Check CORS middleware configuration

## 📊 Production Checklist

- [ ] Database is set up and accessible
- [ ] All environment variables configured
- [ ] Database migrations run successfully
- [ ] API documentation accessible at /docs
- [ ] Health endpoint returns 200 OK
- [ ] Authentication endpoints working
- [ ] CORS configured for frontend
- [ ] Logs show no errors
- [ ] Test user signup and signin
- [ ] Test creating and fetching tasks

## 🎉 Next Steps

After successful deployment:

1. **Update Frontend**: Point frontend API calls to your Hugging Face Space URL
2. **Monitor**: Set up monitoring and alerts
3. **Scale**: Upgrade Space tier if needed
4. **Secure**: Review security settings
5. **Document**: Update API documentation

## 📞 Support

If you encounter issues:
- Check Hugging Face Spaces documentation
- Review application logs
- Check this project's issues on GitHub

---

Happy deploying! 🚀
