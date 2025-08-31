# 🚀 Junior Developer Setup Task: Midora.ai Backend

## 📋 Task Overview
Your task is to set up the **Midora.ai Backend** application on your local development environment. This is a FastAPI-based backend with JWT authentication, user management, and AI API integrations.

**Estimated Time:** 1-2 hours  
**Difficulty:** Beginner to Intermediate

---

## 🎯 Learning Objectives
By completing this task, you will learn:
- How to set up a Python FastAPI application
- Working with virtual environments
- Database setup and migrations with Alembic
- Environment variable configuration
- API testing with FastAPI's built-in documentation

---

## 📚 Prerequisites

### Required Software
Before starting, ensure you have the following installed:

1. **Python 3.8+** 
   - Check: `python --version` or `python3 --version`
   - Install from: https://python.org/downloads/
   - **Windows**: Make sure to check "Add Python to PATH" during installation

2. **PostgreSQL** 
   - Check: `psql --version`
   - **Windows**: Download from https://postgresql.org/download/windows/
   - **Linux/Mac**: Install from package manager or https://postgresql.org/download/
   - Alternative: Use Docker `docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres`

3. **Git**
   - Check: `git --version`
   - **Windows**: Download from https://git-scm.com/download/win
   - **Linux/Mac**: Install from https://git-scm.com/downloads

4. **Code Editor** (VS Code recommended)
   - Download from: https://code.visualstudio.com/

### Optional but Recommended
- **Redis** (for caching - can skip for basic setup)
- **Postman** or **Thunder Client** (VS Code extension) for API testing

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Clone and Navigate to Project
```bash
# Navigate to your desired directory
# Windows:
cd C:\Users\%USERNAME%\Desktop\projects
# Linux/Mac:
cd ~/Desktop/projects

# Create projects directory if it doesn't exist
# Windows:
mkdir projects 2>nul
# Linux/Mac:
mkdir -p projects

# Clone the repository (if not already cloned)
git clone <repository-url>
cd midora.ai-backend

# Verify you're in the right directory
# Windows:
dir
# Linux/Mac:
ls -la
# Should see app/, alembic/, requirements.txt, etc.
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment
# Windows:
python -m venv venv
# Linux/Mac:
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Verify activation (should show (venv) in terminal prompt)
# Windows:
where python
# Linux/Mac:
which python
# Should point to your venv directory
```

### Step 3: Install Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list  # Should show fastapi, uvicorn, sqlalchemy, etc.
```

### Step 4: Database Setup

#### Option A: Local PostgreSQL
```bash
# Connect to PostgreSQL
# Windows (if psql is in PATH):
psql -U postgres
# Windows (if psql not in PATH, find it in PostgreSQL installation folder):
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
# Linux/Mac:
psql -U postgres

# Create database (run these commands inside psql)
CREATE DATABASE midora_ai_db;

# Create user (optional but recommended)
CREATE USER midora_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE midora_ai_db TO midora_user;

# Exit PostgreSQL
\q
```

#### Option B: Docker PostgreSQL (Alternative)
```bash
# Run PostgreSQL in Docker (same command for all platforms)
docker run --name midora-postgres \
  -e POSTGRES_DB=midora_ai_db \
  -e POSTGRES_USER=midora_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:13

# Verify it's running
docker ps
```

### Step 5: Environment Configuration
```bash
# Create environment file
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env

# Edit the .env file with your preferred editor
# Windows:
notepad .env
# Or if you have VS Code:
code .env
# Linux/Mac:
nano .env  # or code .env for VS Code
```

**Configure these REQUIRED variables in `.env`:**
```env
# Database Configuration
DATABASE_URL=postgresql://midora_user:your_password@localhost:5432/midora_ai_db

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_MINUTES=10080

# Application Configuration
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]

# Redis (Optional - can use dummy URL for now)
REDIS_URL=redis://localhost:6379

# AI API Keys (Optional - can be dummy values for initial setup)
OPENAI_API_KEY=sk-dummy-key-for-development
ANTHROPIC_API_KEY=dummy-key-for-development
GEMINI_API_KEY=dummy-key-for-development
```

**⚠️ Important Notes:**
- Replace `your_password` with your actual PostgreSQL password
- Generate a strong JWT_SECRET (you can use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- AI API keys are optional for basic setup

### Step 6: Database Migrations
```bash
# Run database migrations to create tables
alembic upgrade head

# Verify migration worked
alembic current  # Should show current migration
```

### Step 7: Start the Application
```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# You should see output like:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

### Step 8: Test the Setup
Open your browser and test these URLs:

1. **Basic API Response:** http://localhost:8000/
   - Should show: `{"message": "Welcome to Midora.ai API"}`

2. **API Documentation:** http://localhost:8000/docs
   - Should show interactive Swagger UI

3. **Alternative Docs:** http://localhost:8000/redoc
   - Should show ReDoc documentation

---

## ✅ Verification Checklist

Check off each item as you complete it:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] PostgreSQL database created and accessible
- [ ] `.env` file created with all required variables
- [ ] Database migrations completed successfully
- [ ] Application starts without errors
- [ ] Can access http://localhost:8000/ and see welcome message
- [ ] Can access http://localhost:8000/docs and see API documentation
- [ ] Can test a simple API endpoint (like registration) in Swagger UI

---

## 🧪 Testing Your Setup

### Test User Registration
1. Go to http://localhost:8000/docs
2. Find the `POST /api/v1/auth/register` endpoint
3. Click "Try it out"
4. Use this test data:
```json
{
  "email": "test@example.com",
  "password": "testpassword123",
  "full_name": "Test User"
}
```
5. Click "Execute"
6. Should get a 200 response with user data

### Test User Login
1. Find the `POST /api/v1/auth/login` endpoint
2. Use the same email/password from registration
3. Should get a response with access_token

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError"
**Solution:** Make sure your virtual environment is activated and all dependencies are installed.
```bash
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Then reinstall:
pip install -r requirements.txt
```

### Issue: "Database connection failed"
**Solutions:**
1. **Windows**: Check PostgreSQL service is running in Services app (services.msc)
2. **Linux**: Check PostgreSQL is running: `sudo systemctl status postgresql`
3. Verify database exists: `psql -U postgres -l`
4. Check DATABASE_URL in `.env` matches your setup

### Issue: "Port 8000 already in use"
**Solution:** Use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: "Permission denied" on PostgreSQL
**Solution:** Check user permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE midora_ai_db TO midora_user;
```

### Issue: Alembic migration errors
**Solution:** Reset migrations if needed:
```bash
# Check current migration
alembic current

# If issues, you might need to reset
alembic downgrade base
alembic upgrade head
```

### Issue: "python/python3 not found" (Windows)
**Solution:** 
1. Reinstall Python and check "Add Python to PATH"
2. Or use `py` instead of `python`:
```bash
py -m venv venv
py -m pip install --upgrade pip
```

### Issue: PowerShell Execution Policy (Windows)
**Solution:** If you get execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📖 Next Steps

After successful setup:

1. **Explore the Code:**
   - `app/main.py` - Application entry point
   - `app/routes/` - API endpoints
   - `app/models/` - Database models
   - `app/services/` - Business logic

2. **Try Making Changes:**
   - Add a new API endpoint
   - Modify user model
   - Add validation

3. **Learn More:**
   - Read FastAPI documentation: https://fastapi.tiangolo.com/
   - Learn about SQLAlchemy: https://sqlalchemy.org/
   - Understand JWT authentication

---

## 🆘 Getting Help

If you're stuck:

1. **Check the logs** - Look at the terminal output for error messages
2. **Read error messages carefully** - They usually tell you what's wrong
3. **Google the error** - Include "FastAPI" or "Python" and your OS in your search
4. **Ask for help** - Share the specific error message, your OS, and what you were trying to do

---

## 🎉 Completion

Once you can successfully:
- Start the application
- Access the API documentation
- Register a new user
- Login with that user

**Congratulations! 🎊** You've successfully set up the Midora.ai backend on your local system.

---

## 📝 Submission

Please provide:
1. Screenshot of http://localhost:8000/docs working
2. Screenshot of successful user registration response
3. Any issues you encountered and how you solved them
4. Questions about the codebase or setup process
5. **Your Operating System** (Windows 10/11, macOS, Linux distribution)

**Good luck! 🚀** 