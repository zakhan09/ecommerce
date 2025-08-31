# 🎯 Junior Developer Task: Local Setup of Midora.ai Backend

## 📋 Your Mission
Set up the Midora.ai FastAPI backend application on your local machine and get it running successfully.

**Time Estimate:** 1-2 hours  
**Difficulty:** Beginner-Intermediate

---

## ✅ What You Need to Deliver
1. Working application accessible at `http://localhost:8000`
2. Successful user registration via API
3. Screenshot of working Swagger UI documentation
4. Brief report of any issues encountered

---

## 🛠️ Setup Steps

### 1. Environment Setup
```bash
# Create and activate virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# Linux/Mac:
python3 -m venv venv
source venv/bin/activate

# Install dependencies (same for all platforms)
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Database Setup
Choose ONE option:

**Option A - Local PostgreSQL:**
```bash
# Windows (if psql in PATH):
psql -U postgres
# Windows (if psql not in PATH):
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
# Linux/Mac:
psql -U postgres

# Then run these commands in psql:
CREATE DATABASE midora_ai_db;
CREATE USER midora_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE midora_ai_db TO midora_user;
\q
```

**Option B - Docker PostgreSQL (Easier, same for all platforms):**
```bash
docker run --name midora-postgres \
  -e POSTGRES_DB=midora_ai_db \
  -e POSTGRES_USER=midora_user \
  -e POSTGRES_PASSWORD=dev_password \
  -p 5432:5432 \
  -d postgres:13
```

### 3. Environment Variables
Create a `.env` file in the project root:

```bash
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

Add these variables to your `.env` file:

```env
# Copy this exactly - replace dev_password with your actual password
DATABASE_URL=postgresql://midora_user:dev_password@localhost:5432/midora_ai_db
JWT_SECRET=dev-jwt-secret-key-make-this-long-and-random-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_MINUTES=10080
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=dummy-key-for-dev
ANTHROPIC_API_KEY=dummy-key-for-dev
GEMINI_API_KEY=dummy-key-for-dev
```

### 4. Database Migration
```bash
# Run migrations to create tables
alembic upgrade head

# Verify it worked
alembic current
```

### 5. Start the Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Testing & Verification

### Required Tests
1. **Basic API Test:**
   - Visit: `http://localhost:8000`
   - Should see: `{"message": "Welcome to Midora.ai API"}`

2. **API Documentation:**
   - Visit: `http://localhost:8000/docs`
   - Should see interactive Swagger UI

3. **User Registration Test:**
   - In Swagger UI, find `POST /api/v1/auth/register`
   - Test with:
   ```json
   {
     "email": "test@example.com",
     "password": "testpass123",
     "full_name": "Test User"
   }
   ```
   - Should get successful response

---

## 🚨 Common Problems & Quick Fixes

| Problem | Windows Fix | Linux/Mac Fix |
|---------|-------------|---------------|
| `ModuleNotFoundError` | `venv\Scripts\activate` | `source venv/bin/activate` |
| Python not found | Use `py` instead of `python` | Use `python3` instead of `python` |
| Database connection error | Check Services app (services.msc) | Check `sudo systemctl status postgresql` |
| Port 8000 in use | `uvicorn app.main:app --reload --port 8001` | Same |
| PowerShell execution policy | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` | N/A |
| psql not found | Use full path: `"C:\Program Files\PostgreSQL\15\bin\psql.exe"` | Install postgresql-client |

---

## 📸 Required Screenshots
Take screenshots of:
1. Terminal showing successful app startup
2. Browser showing `http://localhost:8000/docs` (Swagger UI)
3. Successful user registration response in Swagger UI

---

## 📝 Submission Checklist
- [ ] Application runs without errors
- [ ] Can access API documentation at `/docs`
- [ ] Successfully registered a test user
- [ ] Screenshots captured
- [ ] Any issues documented with solutions
- [ ] **Operating System noted** (Windows 10/11, macOS, Linux)

---

## 🆘 Need Help?
1. Check terminal logs for specific error messages
2. Verify all prerequisites are installed
3. Ensure virtual environment is activated
4. Double-check `.env` file configuration
5. **Include your OS** when asking for help
6. For Windows users: Try using `py` instead of `python`

**Good luck! 🚀** 