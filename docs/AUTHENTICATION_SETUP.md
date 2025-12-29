# Authentication System Setup Guide

## Quick Start

This guide explains how to set up and use the authentication system in the GST Billing Platform.

---

## 1. Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the required authentication packages:
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT token generation
- `python-multipart` - Form data support
- `email-validator` - Email validation

---

## 2. Environment Configuration

### Create/Update `.env` File

Add the following environment variables to your `.env` file:

```bash
# JWT Configuration
SECRET_KEY=your-super-secret-key-min-32-characters-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ IMPORTANT:**
- Generate a secure SECRET_KEY for production
- Never commit `.env` file to version control
- Use different keys for development and production

### Generate Secure SECRET_KEY

```python
# Run this in Python to generate a secure key
import secrets
print(secrets.token_urlsafe(32))
```

---

## 3. Database Migration

### Run Migrations

Apply the database migrations to create the auth schema and users table:

```bash
# Windows
cd C:\Users\Viral\OneDrive\Desktop\Projects\gst-billing\gst-billing-platform

# Run migrations (use the method that works in your environment)
alembic upgrade head
```

This will:
- Create `auth` schema
- Create `users` table
- Add indexes and constraints
- Insert default admin user

---

## 4. Default Admin Account

A default admin account is created automatically:

```
Username: admin
Email: admin@example.com
Password: admin123456
```

**Test the admin login:**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123456"
  }'
```

---

## 5. Protecting Routes

### Add Authentication to Existing Routes

To protect a route, add the `get_current_user` dependency:

```python
from app.auth_service.middleware import get_current_user
from app.auth_service.models import User

@router.get("/protected-endpoint")
def protected_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Add this
):
    # current_user contains the authenticated user
    return {"message": f"Hello {current_user.username}"}
```

### Different Protection Levels

```python
from app.auth_service.middleware import (
    get_current_user,        # Any authenticated user
    get_current_active_user, # Only active users
    get_current_superuser,   # Only superusers/admins
    optional_user            # Optional authentication
)

# Example: Only superusers can access
@router.delete("/admin/delete-all")
def admin_only(current_user: User = Depends(get_current_superuser)):
    return {"message": "Admin access granted"}
```

---

## 6. File Structure

The authentication system consists of:

```
app/auth_service/
├── __init__.py              # Package initialization
├── models.py                # User model
├── schemas.py               # Pydantic schemas
├── security.py              # Password hashing & JWT utilities
├── service.py               # Business logic
├── middleware.py            # Route protection dependencies
└── router.py                # API endpoints

alembic/versions/
└── f6g7h8i9j0k1_create_auth_schema_and_users_table.py

docs/
├── AUTHENTICATION_API.md    # API documentation for frontend
└── AUTHENTICATION_SETUP.md  # This file
```

---

## 7. API Endpoints Summary

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/health` | Health check |

### Protected Endpoints (Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/me` | Get current user profile |

---

## 8. Testing the System

### Test User Registration

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

### Test Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Test Protected Endpoint

```bash
# Replace YOUR_ACCESS_TOKEN with the token from login response
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Swagger UI

Navigate to: `http://localhost:8000/docs`

1. Click **Authorize** button (lock icon)
2. Login to get access token
3. Paste token in format: `Bearer YOUR_ACCESS_TOKEN`
4. Click **Authorize**
5. Test protected endpoints

---

## 9. Security Features

### Implemented Security Measures

✅ **Password Hashing**
- Uses bcrypt algorithm
- Salted and hashed passwords
- Never stores plain text passwords

✅ **JWT Tokens**
- Secure token generation
- Token expiration
- Separate access and refresh tokens

✅ **Token Types**
- Access tokens: 30 minutes lifetime
- Refresh tokens: 7 days lifetime
- Token type validation

✅ **Input Validation**
- Email format validation
- Password strength requirements (min 8 chars)
- Username length validation (3-100 chars)

✅ **Database Security**
- Unique constraints on email and username
- Indexed fields for performance
- Prepared statements (SQL injection prevention)

✅ **User Status**
- Active/inactive user management
- Superuser role separation

---

## 10. Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'passlib'"

**Solution:**
```bash
pip install passlib[bcrypt]
pip install python-jose[cryptography]
```

### Issue: "Could not validate credentials"

**Possible causes:**
1. Token expired - Use refresh token
2. Invalid token - Login again
3. Token format wrong - Should be `Bearer <token>`

### Issue: Migration fails

**Solution:**
Ensure PostgreSQL is running and connection string is correct in `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Issue: "Username already registered"

**Solution:**
Username or email is already in use. Choose a different one or login with existing credentials.

---

## 11. Next Steps

### For Backend Developers

1. ✅ Add authentication to more routes as needed
2. ✅ Implement role-based permissions
3. ✅ Add password reset functionality (future)
4. ✅ Add email verification (future)
5. ✅ Add rate limiting (future)

### For Frontend Developers

1. ✅ Read [AUTHENTICATION_API.md](AUTHENTICATION_API.md) for API details
2. ✅ Implement login/register UI
3. ✅ Store tokens securely
4. ✅ Add token refresh logic
5. ✅ Handle 401 errors globally

---

## 12. Production Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong, random value
- [ ] Update ACCESS_TOKEN_EXPIRE_MINUTES if needed
- [ ] Change default admin password
- [ ] Enable HTTPS only
- [ ] Set up proper CORS origins (not "*")
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Review and test all security measures
- [ ] Backup database before migration

---

## Support

For questions or issues:
- Check [AUTHENTICATION_API.md](AUTHENTICATION_API.md) for API documentation
- Review this setup guide
- Check server logs for errors
- Contact the backend development team

---

**Last Updated:** December 28, 2025
