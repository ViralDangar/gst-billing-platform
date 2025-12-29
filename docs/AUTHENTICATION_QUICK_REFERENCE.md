# Authentication Quick Reference

Quick reference guide for frontend developers integrating with the authentication API.

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

---

## 1. Register New User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-12-28T10:30:00.000Z"
}
```

---

## 2. Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## 3. Refresh Token

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## 4. Get Current User

```http
GET /auth/me
Authorization: Bearer eyJhbGc...
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-12-28T10:30:00.000Z"
}
```

---

## Using Protected Endpoints

All protected endpoints require the `Authorization` header:

```http
GET /identity/company
Authorization: Bearer eyJhbGc...
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | - |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Check request body validation |
| 401 | Unauthorized | Token invalid/expired - refresh or login |
| 403 | Forbidden | Insufficient permissions |
| 422 | Validation Error | Check input format |
| 500 | Server Error | Contact backend team |

---

## Token Expiration

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

When you receive a 401 error:
1. Try refreshing the access token
2. If refresh fails, redirect to login

---

## Default Admin Credentials

```
Username: admin
Password: admin123456
Email: admin@example.com
```

---

## JavaScript/TypeScript Example

```typescript
// Login
const login = async (username: string, password: string) => {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
};

// Make authenticated request
const getCompany = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/identity/company', {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (response.status === 401) {
    // Token expired, try refresh
    await refreshToken();
    return getCompany(); // Retry
  }

  return response.json();
};

// Refresh token
const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  const response = await fetch('http://localhost:8000/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh })
  });

  if (!response.ok) {
    // Refresh failed, logout
    logout();
    window.location.href = '/login';
    throw new Error('Session expired');
  }

  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
};

// Logout
const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
```

---

## React Example with Axios

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refresh = localStorage.getItem('refresh_token');
        const { data } = await axios.post('/auth/refresh', {
          refresh_token: refresh
        });

        localStorage.setItem('access_token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;

        return api(originalRequest);
      } catch {
        localStorage.clear();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

---

## Vue.js Example

```typescript
// auth.service.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const authService = {
  async login(username: string, password: string) {
    const response = await axios.post(`${API_URL}/auth/login`, {
      username,
      password
    });

    if (response.data.access_token) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }

    return response.data;
  },

  logout() {
    localStorage.removeItem('user');
  },

  async register(email: string, username: string, password: string, fullName?: string) {
    return axios.post(`${API_URL}/auth/register`, {
      email,
      username,
      password,
      full_name: fullName
    });
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (userStr) return JSON.parse(userStr);
    return null;
  },

  getAuthHeader() {
    const user = this.getCurrentUser();
    if (user && user.access_token) {
      return { Authorization: 'Bearer ' + user.access_token };
    }
    return {};
  }
};
```

---

## Storage Best Practices

### ✅ Recommended
- Memory storage for access tokens (if possible)
- Secure httpOnly cookies for refresh tokens
- sessionStorage for short sessions

### ⚠️ Use with Caution
- localStorage (vulnerable to XSS)
- Regular cookies (vulnerable to CSRF)

### ❌ Never
- Store passwords
- Store tokens in URL parameters
- Store tokens in plain text files

---

## Checklist for Frontend

- [ ] Implement login page
- [ ] Implement registration page
- [ ] Store tokens securely
- [ ] Add Authorization header to protected requests
- [ ] Implement automatic token refresh
- [ ] Handle 401 errors globally
- [ ] Implement logout functionality
- [ ] Clear tokens on logout
- [ ] Redirect to login on session expiry
- [ ] Show appropriate error messages

---

For detailed documentation, see [AUTHENTICATION_API.md](AUTHENTICATION_API.md)
