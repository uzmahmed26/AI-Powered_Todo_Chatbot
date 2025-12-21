# Vercel Deployment Guide

This guide walks you through deploying the Phase III Smart Todo ChatKit App to Vercel.

## Prerequisites

Before deploying, ensure you have:

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional but recommended):
   ```bash
   npm install -g vercel
   ```
3. **Environment Variables Ready**:
   - Neon PostgreSQL connection string
   - OpenAI API key
   - Better Auth credentials

## Project Structure

This is a monorepo with:
- **Frontend**: `frontend/` - React/Vite application
- **Backend**: `backend/` - FastAPI Python application

Vercel will:
- Build the frontend as a static site
- Deploy the backend as serverless functions

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from project root**:
   ```bash
   cd C:\Users\laptop world\Desktop\phase3
   vercel
   ```

4. **Follow the prompts**:
   - Set up and deploy? **Yes**
   - Which scope? Select your account
   - Link to existing project? **No** (first time)
   - Project name: `phase3-smart-todo-chatkit` (or your choice)
   - In which directory is your code? `./`
   - Override settings? **No**

5. **Set environment variables** (after first deployment):
   ```bash
   vercel env add DATABASE_URL
   vercel env add OPENAI_API_KEY
   vercel env add BETTER_AUTH_SECRET
   vercel env add BETTER_AUTH_URL
   vercel env add ALLOWED_ORIGINS
   ```

   For each variable, select the environment (production, preview, development) and paste the value.

6. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Import Git Repository**:
   - Click "Add New..." → "Project"
   - Import your Git repository (GitHub, GitLab, or Bitbucket)
   - Select the `phase3` repository

3. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as root)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `npm install`

4. **Add Environment Variables**:
   Click "Environment Variables" and add the following:

   **Backend Variables:**
   - `DATABASE_URL` = `postgresql+asyncpg://user:password@ep-xyz.us-east-1.aws.neon.tech/smarttodo`
   - `OPENAI_API_KEY` = `sk-proj-...your-key-here...`
   - `BETTER_AUTH_SECRET` = `your-secret-key-here-min-32-chars`
   - `BETTER_AUTH_URL` = `https://your-auth-domain.com`
   - `ALLOWED_ORIGINS` = `https://your-vercel-domain.vercel.app`
   - `OPENAI_MODEL` = `gpt-4`
   - `OPENAI_TEMPERATURE` = `0.7`
   - `MAX_CONTEXT_MESSAGES` = `20`
   - `APP_ENV` = `production`
   - `LOG_LEVEL` = `INFO`

   **Frontend Variables:**
   - `VITE_API_URL` = `https://your-vercel-domain.vercel.app`
   - `VITE_BETTER_AUTH_URL` = `https://your-auth-domain.com`
   - `VITE_APP_NAME` = `Smart Todo ChatKit`
   - `VITE_APP_ENV` = `production`

5. **Deploy**:
   - Click "Deploy"
   - Wait for the build to complete (3-5 minutes)

## Post-Deployment Configuration

### 1. Update CORS Settings

After deployment, you'll have a Vercel URL like `https://phase3-smart-todo-chatkit.vercel.app`.

Update the `ALLOWED_ORIGINS` environment variable in Vercel:
```
ALLOWED_ORIGINS=https://phase3-smart-todo-chatkit.vercel.app,https://*.vercel.app
```

### 2. Update Frontend API URL

Update the `VITE_API_URL` environment variable:
```
VITE_API_URL=https://phase3-smart-todo-chatkit.vercel.app
```

### 3. Run Database Migrations

Vercel serverless functions are stateless, so you need to run migrations manually:

**Option A: Run locally pointing to production DB**
```bash
cd backend
# Update .env with production DATABASE_URL
alembic upgrade head
```

**Option B: Use Vercel CLI**
```bash
vercel env pull .env.production
cd backend
export $(cat ../.env.production | xargs)
alembic upgrade head
```

### 4. Test the Deployment

1. **Test Health Endpoint**:
   ```bash
   curl https://your-vercel-domain.vercel.app/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "phase3-smart-todo-api",
     "version": "0.1.0"
   }
   ```

2. **Test Frontend**:
   - Visit `https://your-vercel-domain.vercel.app`
   - You should see the ChatKit interface

3. **Test API Documentation**:
   - Visit `https://your-vercel-domain.vercel.app/docs`
   - Swagger UI should load

## Continuous Deployment

Vercel automatically deploys:
- **Production**: Pushes to `main` branch
- **Preview**: Pull requests and other branches

To configure:
1. Go to Project Settings → Git
2. Configure Production Branch (default: `main`)
3. Enable/disable automatic deployments for branches

## Troubleshooting

### Build Fails

**Issue**: Frontend build fails
```
Error: Command "npm run build" exited with 1
```

**Solution**:
1. Check frontend build locally: `cd frontend && npm run build`
2. Ensure all dependencies are in `package.json`
3. Check build logs in Vercel dashboard for specific errors

**Issue**: Python dependencies fail
```
Error: Could not find a version that satisfies the requirement
```

**Solution**:
1. Verify `backend/api/requirements.txt` has correct versions
2. Ensure Python version is 3.11 (set in `vercel.json`)

### Runtime Errors

**Issue**: 500 Internal Server Error on API calls
```
{"detail":"Internal Server Error"}
```

**Solution**:
1. Check Vercel Function Logs: Project → Deployments → [Latest] → Functions
2. Common issues:
   - Missing environment variables
   - Database connection string incorrect
   - OpenAI API key invalid

**Issue**: CORS errors in browser console
```
Access to fetch has been blocked by CORS policy
```

**Solution**:
1. Update `ALLOWED_ORIGINS` environment variable
2. Include your Vercel domain: `https://your-domain.vercel.app`
3. Redeploy after updating environment variables

**Issue**: Database connection timeout
```
asyncpg.exceptions.ConnectionDoesNotExistError
```

**Solution**:
1. Verify Neon PostgreSQL connection string
2. Check Neon dashboard for connection limits
3. Ensure database is not paused (Neon auto-pauses after inactivity)

### Performance Issues

**Issue**: API responses are slow (>5 seconds)

**Cause**: Vercel serverless functions cold start

**Solutions**:
1. **Upgrade Vercel Plan**: Pro plan has faster cold starts
2. **Use Edge Functions**: For certain endpoints (requires code changes)
3. **Implement Caching**: Cache OpenAI responses where appropriate
4. **Optimize Dependencies**: Reduce Python package sizes

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql+asyncpg://user:pass@ep-xyz.neon.tech/db` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-...` |
| `BETTER_AUTH_SECRET` | Better Auth secret (min 32 chars) | `your-secret-key-here` |
| `BETTER_AUTH_URL` | Better Auth domain | `https://auth.example.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `OPENAI_TEMPERATURE` | Response creativity (0-1) | `0.7` |
| `MAX_CONTEXT_MESSAGES` | Max messages in context | `20` |
| `APP_ENV` | Application environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://your-domain.vercel.app` |
| `VITE_BETTER_AUTH_URL` | Better Auth URL | `https://auth.example.com` |
| `VITE_APP_NAME` | App display name | `Smart Todo ChatKit` |
| `VITE_APP_ENV` | Environment | `production` |

## Custom Domain (Optional)

To use a custom domain:

1. **Add Domain in Vercel**:
   - Project Settings → Domains
   - Add your domain (e.g., `todo.example.com`)

2. **Configure DNS**:
   - Add CNAME record: `todo.example.com` → `cname.vercel-dns.com`
   - Or A record pointing to Vercel's IP

3. **Update Environment Variables**:
   - `ALLOWED_ORIGINS` → `https://todo.example.com`
   - `VITE_API_URL` → `https://todo.example.com`

4. **Redeploy**

## Monitoring

### View Logs

**Function Logs**:
1. Go to Project → Deployments
2. Click on latest deployment
3. Click "Functions" tab
4. View real-time logs

**Build Logs**:
1. Go to Project → Deployments
2. Click on deployment
3. View "Building" section

### Analytics

Enable Vercel Analytics:
1. Project Settings → Analytics
2. Enable Web Analytics
3. Add analytics snippet to frontend (optional)

## Scaling Considerations

Vercel serverless functions have limits:

- **Execution Time**: 10s (Hobby), 60s (Pro), 900s (Enterprise)
- **Memory**: 1024 MB (Hobby), 3008 MB (Pro)
- **Payload Size**: 4.5 MB (request), 5 MB (response)

For this app:
- Most API calls complete in <3 seconds
- OpenAI calls may take 2-5 seconds
- Database queries are fast (<100ms with Neon)

If you hit limits:
1. **Optimize OpenAI calls**: Use streaming, reduce context
2. **Implement caching**: Cache frequent queries
3. **Upgrade plan**: Pro plan has higher limits
4. **Consider alternative**: Deploy backend on Railway/Render for long-running processes

## Security Checklist

Before going live:

- [ ] All environment variables set correctly
- [ ] Database connection string uses SSL (`?sslmode=require`)
- [ ] `ALLOWED_ORIGINS` restricted to your domain
- [ ] OpenAI API key is from production account
- [ ] Better Auth configured for production
- [ ] No hardcoded secrets in code
- [ ] `.env` files not committed to Git
- [ ] HTTPS enforced (automatic on Vercel)
- [ ] Database backups enabled (in Neon dashboard)

## Support

For deployment issues:

1. **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
2. **Vercel Support**: support@vercel.com
3. **Project Issues**: Check GitHub issues
4. **Community**: Vercel Discord

## Next Steps

After successful deployment:

1. **Test all features**: Create, update, delete todos
2. **Monitor performance**: Check response times
3. **Set up monitoring**: Configure alerts for errors
4. **Configure backups**: Enable database backups in Neon
5. **Add custom domain**: (optional)
6. **Enable analytics**: Track usage

---

**Deployment Status**: Ready for production
**Estimated Deploy Time**: 5-10 minutes
**Estimated Cost**: Free tier supported (with limits)
