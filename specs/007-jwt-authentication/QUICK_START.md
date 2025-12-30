# JWT Authentication - Quick Start Guide

**TL;DR**: Complete guide to add signup, signin, and JWT authentication to your AI-Powered Todo project.

---

## 📋 What You'll Get

✅ **Signup Page** - Users create accounts with email/password
✅ **Signin Page** - Users authenticate and get JWT tokens
✅ **Protected Routes** - All todo/chat APIs require valid JWT
✅ **Auto Refresh** - Tokens refresh automatically
✅ **User Isolation** - Each user sees only their own data

---

## 🚀 Quick Implementation (1 Hour)

### Backend (30 minutes)

```bash
# 1. Install dependencies
cd backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email]

# 2. Add to .env file
echo "JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
echo "JWT_REFRESH_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
echo "JWT_ALGORITHM=HS256" >> .env
echo "ACCESS_TOKEN_EXPIRE_MINUTES=15" >> .env
echo "REFRESH_TOKEN_EXPIRE_DAYS=7" >> .env

# 3. Copy these files from IMPLEMENTATION_STEPS.md:
# - backend/src/models/user.py
# - backend/src/auth/jwt.py
# - backend/src/auth/dependencies.py
# - backend/src/auth/schemas.py
# - backend/src/api/routes/auth.py

# 4. Update backend/src/api/app.py (add auth router)

# 5. Update backend/src/api/routes/chat.py (add auth dependency)

# 6. Run migration
python -m alembic revision --autogenerate -m "add users table"
python -m alembic upgrade head

# 7. Test
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'
```

### Frontend (30 minutes)

```bash
# 1. Install dependencies
cd frontend
npm install react-router-dom jwt-decode zod

# 2. Copy these files from IMPLEMENTATION_STEPS.md:
# - frontend/src/context/AuthContext.tsx
# - frontend/src/pages/SignupPage.tsx
# - frontend/src/pages/SigninPage.tsx
# - frontend/src/components/ProtectedRoute.tsx

# 3. Update frontend/src/services/api.ts (add auth methods + interceptor)

# 4. Update frontend/src/main.tsx (add Router + AuthProvider)

# 5. Update frontend/src/pages/SmartTodoApp.tsx (add logout button)

# 6. Test
npm run dev
# Visit http://localhost:5173 - should redirect to /signin
```

---

## 📁 Files to Create/Modify

### Backend (9 files)

**New Files**:
1. `backend/src/models/user.py` - User database model
2. `backend/src/auth/jwt.py` - JWT utilities (encode, decode, hash)
3. `backend/src/auth/dependencies.py` - FastAPI auth dependencies
4. `backend/src/auth/schemas.py` - Pydantic request/response schemas
5. `backend/src/api/routes/auth.py` - Auth endpoints (signup, signin, refresh)

**Modified Files**:
6. `backend/.env` - Add JWT secrets
7. `backend/src/api/app.py` - Register auth router
8. `backend/src/api/routes/chat.py` - Add auth to chat endpoint
9. `backend/src/models/__init__.py` - Export User model

**Migration**:
10. Run `alembic revision --autogenerate -m "add users table"`

---

### Frontend (7 files)

**New Files**:
1. `frontend/src/context/AuthContext.tsx` - Auth state management
2. `frontend/src/pages/SignupPage.tsx` - Signup form
3. `frontend/src/pages/SigninPage.tsx` - Signin form
4. `frontend/src/components/ProtectedRoute.tsx` - Route protection

**Modified Files**:
5. `frontend/src/services/api.ts` - Add auth methods + token interceptor
6. `frontend/src/main.tsx` - Add Router + AuthProvider
7. `frontend/src/pages/SmartTodoApp.tsx` - Add logout button

---

## 🔑 Key Concepts

### JWT Token Flow

```
1. User signs up/in
   ↓
2. Backend returns access_token + refresh_token
   ↓
3. Frontend stores tokens in localStorage
   ↓
4. Frontend sends access_token in Authorization header
   ↓
5. Backend validates token + returns data
   ↓
6. When access_token expires (15 min), use refresh_token to get new access_token
```

### Token Security

- **Access Token**: Short-lived (15 min), sent with every request
- **Refresh Token**: Long-lived (7 days), only used to get new access tokens
- **Secret Keys**: Random 32+ character strings, never commit to git
- **Password Hashing**: bcrypt with 12 rounds, never store plaintext

---

## 🧪 Testing Checklist

### Backend API Tests

```bash
# 1. Signup (should return 201 + tokens)
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"SecurePass123","full_name":"John Doe"}'

# 2. Signin (should return 200 + tokens)
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"SecurePass123"}'

# 3. Get current user (should return 200 + user info)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Protected chat (should return 200 if token valid)
curl -X POST http://localhost:8000/api/YOUR_USER_ID/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Add buy milk","conversation_id":null}'
```

### Frontend User Tests

1. ✅ Visit http://localhost:5173 → Redirects to /signin
2. ✅ Click "Sign up" → Shows signup form
3. ✅ Submit signup form → Creates account + redirects to chat
4. ✅ User name appears in header
5. ✅ Send chat message → Works (authenticated)
6. ✅ Refresh page → Stays logged in
7. ✅ Click logout → Redirects to signin
8. ✅ Try to access / without login → Redirects to signin

---

## 🐛 Common Issues

### Issue 1: "Invalid authentication credentials"
**Cause**: Token expired or invalid
**Fix**: Check token expiry in jwt_decode, ensure JWT_SECRET_KEY matches

### Issue 2: "Email already registered"
**Cause**: User already exists in database
**Fix**: Use different email or check database

### Issue 3: "CORS error"
**Cause**: Frontend and backend on different origins
**Fix**: Add frontend URL to CORS_ORIGINS in backend/.env

### Issue 4: 404 on /auth/signup
**Cause**: Auth router not registered
**Fix**: Verify `app.include_router(auth.router, prefix="/api")` in app.py

### Issue 5: Infinite redirect loop
**Cause**: AuthContext not initialized or token invalid
**Fix**: Check localStorage has valid token, clear localStorage and try again

---

## 📚 Documentation

- **Full Spec**: `specs/007-jwt-authentication/spec.md`
- **Step-by-Step Guide**: `specs/007-jwt-authentication/IMPLEMENTATION_STEPS.md`
- **This Quick Start**: `specs/007-jwt-authentication/QUICK_START.md`

---

## 🎯 Next Steps After Implementation

1. ✅ Test signup/signin flow end-to-end
2. ✅ Test protected chat routes work
3. ✅ Test logout clears tokens
4. ✅ Migrate existing demo-user data to real users
5. ⏳ Add password reset (Phase 2)
6. ⏳ Add email verification (Phase 2)
7. ⏳ Add OAuth providers (Phase 2)
8. ⏳ Deploy to production

---

## 💡 Tips

- **Development**: Use localStorage for tokens (easier debugging)
- **Production**: Use httpOnly cookies (more secure)
- **Secrets**: Never commit JWT_SECRET_KEY to git
- **Passwords**: Enforce strong password requirements (8+ chars, uppercase, lowercase, number)
- **Testing**: Create test user accounts, don't use real emails in development
- **Debugging**: Use browser DevTools → Application → Local Storage to inspect tokens

---

## ⚡ One-Command Setup (Advanced)

If you want to automate the setup, create this script:

```bash
#!/bin/bash
# File: scripts/setup-auth.sh

echo "🚀 Setting up JWT Authentication..."

# Backend
cd backend
echo "📦 Installing backend dependencies..."
pip install python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email]

echo "🔑 Generating JWT secrets..."
JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
REFRESH_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')

echo "" >> .env
echo "# JWT Authentication" >> .env
echo "JWT_SECRET_KEY=$JWT_SECRET" >> .env
echo "JWT_REFRESH_SECRET_KEY=$REFRESH_SECRET" >> .env
echo "JWT_ALGORITHM=HS256" >> .env
echo "ACCESS_TOKEN_EXPIRE_MINUTES=15" >> .env
echo "REFRESH_TOKEN_EXPIRE_DAYS=7" >> .env

echo "✅ Backend dependencies installed and secrets generated"

# Frontend
cd ../frontend
echo "📦 Installing frontend dependencies..."
npm install react-router-dom jwt-decode zod

echo "✅ Frontend dependencies installed"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy the code snippets from IMPLEMENTATION_STEPS.md"
echo "2. Run database migration: cd backend && alembic revision --autogenerate -m 'add users'"
echo "3. Apply migration: alembic upgrade head"
echo "4. Start servers and test!"
```

Make it executable: `chmod +x scripts/setup-auth.sh`

Then run: `./scripts/setup-auth.sh`

---

**Good luck! 🚀**
