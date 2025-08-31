# Midora.ai Backend

A FastAPI-based backend application with JWT authentication and user management.

## Features

- 🔐 JWT Authentication
- 👤 User Management
- 🗄️ SQLAlchemy ORM
- 📝 API Documentation (Swagger/OpenAPI)
- 🔒 Secure Password Hashing
- 🚀 FastAPI Framework

## Prerequisites

- Python 3.8+
- PostgreSQL (or your preferred database)
- pip

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd midora.ai-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

### User Management
- `GET /api/v1/user/profile` - Get user profile
- `PUT /api/v1/user/profile` - Update user profile

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8
```

## Project Structure

```
midora.ai-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth_routes.py
│   │       └── user_routes.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── deps.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   └── user.py
│   ├── services/
│   │   └── auth_service.py
│   ├── repository/
│   │   └── user_repository.py
│   └── main.py
├── test/
├── scripts/
├── .env.example
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For support, please contact [your-email@example.com] 