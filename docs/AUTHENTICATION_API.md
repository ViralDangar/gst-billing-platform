# Authentication API Documentation

## Overview

This document provides a comprehensive guide for integrating with the GST Billing Platform authentication system. The system uses **JWT (JSON Web Tokens)** for secure authentication and authorization.

---

## Table of Contents

1. [Authentication Flow](#authentication-flow)
2. [API Endpoints](#api-endpoints)
3. [Request & Response Examples](#request--response-examples)
4. [Token Management](#token-management)
5. [Protected Routes](#protected-routes)
6. [Error Handling](#error-handling)
7. [Security Best Practices](#security-best-practices)

---

## Authentication Flow

### Login Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant Database

    Frontend->>API: POST /auth/login (username, password)
    API->>Database: Verify credentials
    Database-->>API: User data
    API->>API: Generate JWT tokens
    API-->>Frontend: access_token, refresh_token
    Frontend->>Frontend: Store tokens securely
    Frontend->>API: API Request + Authorization header
    API->>API: Validate access_token
    API-->>Frontend: Protected resource
```

### Registration Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant API
    participant Database

    Frontend->>API: POST /auth/register (email, username, password)
    API->>API: Validate input
    API->>API: Hash password
    API->>Database: Create user
    Database-->>API: User created
    API-->>Frontend: User details (201 Created)
    Frontend->>API: POST /auth/login
    API-->>Frontend: access_token, refresh_token
```

### Token Refresh Flow

```mermaid
sequenceDiagram
    participant Frontend
    participant API

    Frontend->>API: API Request + expired access_token
    API-->>Frontend: 401 Unauthorized
    Frontend->>API: POST /auth/refresh (refresh_token)
    API->>API: Validate refresh_token
    API-->>Frontend: New access_token
    Frontend->>API: Retry original request
    API-->>Frontend: Success
```

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. User Registration

**Endpoint:** `POST /auth/register`

**Description:** Create a new user account

**Authentication:** None (Public endpoint)

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"  // Optional
}
```

**Validation Rules:**
- `email`: Valid email format, unique
- `username`: 3-100 characters, unique
- `password`: Minimum 8 characters
- `full_name`: Optional, max 255 characters

**Success Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-12-28T10:30:00.000Z"
}
```

**Error Responses:**
- `400 Bad Request`: Username or email already exists
- `422 Unprocessable Entity`: Validation error (invalid format)

---

### 2. User Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT tokens

**Authentication:** None (Public endpoint)

**Request Body:**
```json
{
  "username": "johndoe",  // Can be username OR email
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800  // Access token expiration in seconds (30 minutes)
}
```

**Error Responses:**
- `401 Unauthorized`: Incorrect username/email or password
- `401 Unauthorized`: User account is inactive

---

### 3. Refresh Access Token

**Endpoint:** `POST /auth/refresh`

**Description:** Get a new access token using refresh token

**Authentication:** None (Public endpoint)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

---

### 4. Get Current User Profile

**Endpoint:** `GET /auth/me`

**Description:** Get the authenticated user's profile

**Authentication:** Required (Bearer token)

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-12-28T10:30:00.000Z"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

---

## Request & Response Examples

### Example: Complete Login Flow

#### Step 1: Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123456"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Step 2: Access Protected Resource
```bash
curl -X GET "http://localhost:8000/identity/company" \
  -H "Authorization: Bearer eyJhbGc..."
```

#### Step 3: Refresh Token When Expired
```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGc..."
  }'
```

---

## Token Management

### Token Types

1. **Access Token**
   - **Purpose:** Authenticate API requests
   - **Lifetime:** 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
   - **Usage:** Include in `Authorization` header for all protected endpoints

2. **Refresh Token**
   - **Purpose:** Obtain new access tokens without re-login
   - **Lifetime:** 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
   - **Usage:** Send to `/auth/refresh` endpoint when access token expires

### Token Payload

When decoded, access tokens contain:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "user@example.com",
  "is_superuser": false,
  "type": "access",
  "exp": 1735387800,  // Expiration timestamp
  "iat": 1735386000   // Issued at timestamp
}
```

### Storage Recommendations

**Frontend (Web):**
- Store `access_token` in memory or session storage
- Store `refresh_token` in httpOnly cookie (if backend supports) or secure localStorage
- Never store tokens in plain text or unsecured cookies

**Frontend (Mobile):**
- Use secure storage (Keychain for iOS, Keystore for Android)
- Encrypt tokens before storing

---

## Protected Routes

### How to Protect a Route

All routes that require authentication must include the `Authorization` header:

```javascript
// JavaScript/TypeScript example
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${accessToken}`
};

fetch('http://localhost:8000/identity/company', {
  method: 'GET',
  headers: headers
});
```

### Currently Protected Endpoints

The following endpoints require authentication:

- `POST /identity/company` - Create company
- `GET /identity/company` - Get company details
- `PUT /identity/company` - Update company
- `GET /identity/company/with-gstin` - Get company with GSTIN
- `POST /identity/company/{company_id}/gstins` - Add GSTIN
- `GET /identity/company/{company_id}/gstins` - List GSTINs
- All billing endpoints (`/billing/*`)
- All master data endpoints (`/products/*`, `/customers/*`)
- All document endpoints (`/documents/*`)

### Public Endpoints

These endpoints do NOT require authentication:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /health` - System health check
- `GET /auth/health` - Auth service health check

---

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

**Causes:**
- Missing Authorization header
- Invalid or expired access token
- Malformed token

**Frontend Action:**
- Try refreshing the token using `/auth/refresh`
- If refresh fails, redirect to login page

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

**Causes:**
- User doesn't have required permissions (e.g., not a superuser)

**Frontend Action:**
- Show "Access Denied" message
- Redirect to appropriate page

#### 400 Bad Request
```json
{
  "detail": "Username already registered"
}
```

**Causes:**
- Validation error (duplicate username/email)
- Inactive user trying to login

**Frontend Action:**
- Show validation error to user
- Allow user to correct input

---

## Security Best Practices

### For Frontend Developers

1. **Token Storage**
   - Never store tokens in localStorage if possible (XSS risk)
   - Use httpOnly cookies for refresh tokens
   - Store access tokens in memory when possible

2. **HTTPS Only**
   - Always use HTTPS in production
   - Never send tokens over unsecured connections

3. **Token Refresh**
   - Implement automatic token refresh before expiration
   - Use interceptors to retry failed requests after refresh

4. **Logout**
   - Clear all tokens from storage on logout
   - Redirect to login page

5. **Error Handling**
   - Handle 401 errors globally
   - Automatically refresh tokens when needed
   - Logout user if refresh token is invalid

### Example: Axios Interceptor for Token Refresh

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Request interceptor - Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken(); // Your token retrieval function
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = getRefreshToken();
        const response = await axios.post('/auth/refresh', {
          refresh_token: refreshToken
        });

        const { access_token } = response.data;
        setAccessToken(access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token is invalid - logout user
        logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

---

## Environment Variables

Configure these in your `.env` file:

```bash
# JWT Secret Key (IMPORTANT: Change in production!)
SECRET_KEY=your-secret-key-min-32-chars-change-in-production

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**⚠️ IMPORTANT:**
- Generate a strong, random SECRET_KEY for production
- Never commit SECRET_KEY to version control
- Use different keys for development and production

---

## Default Admin Account

For initial testing, a default admin account is created:

```
Username: admin
Password: admin123456
Email: admin@example.com
```

**⚠️ IMPORTANT:** Change this password immediately in production!

---

## Testing the API

### Using cURL

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'

# Get current user (replace TOKEN with actual token)
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer TOKEN"
```

### Using Postman

1. **Import Environment:**
   - Create variable `base_url`: `http://localhost:8000`
   - Create variable `access_token`: (will be set automatically)

2. **Login Request:**
   - POST `{{base_url}}/auth/login`
   - Save `access_token` from response to environment variable

3. **Protected Requests:**
   - Add header: `Authorization: Bearer {{access_token}}`

---

## Support

For questions or issues:
- Check API documentation at: `http://localhost:8000/docs` (Swagger UI)
- Review error messages in API responses
- Contact backend team for assistance

---

**Last Updated:** December 28, 2025
**API Version:** 1.0
