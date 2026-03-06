# React App Authentication API

This document describes the authentication API endpoints available for React app integration with the BES module.

## Overview

The authentication controller provides RESTful API endpoints for React frontend applications to authenticate users with the DGS Portal security group.

## Security Group

Users must be assigned to the **DGS Portal** security group (`bes.group_dgs_portal`) to access these endpoints.

## API Endpoints

### 1. Login
**Endpoint:** `POST /api/auth/login`

**Authentication:** None (public endpoint)

**Request Body:**
```json
{
  "db": "database_name",
  "login": "username",
  "password": "password"
}
```

**Response (Success):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "name": "User Name",
    "login": "username",
    "email": "user@example.com",
    "groups": ["DGS Portal", "Other Groups"],
    "is_admin": false,
    "has_dgs_portal": true,
    "authenticated": true
  },
  "session": {
    "sid": "session_id",
    "expires_at": "2025-11-01 10:00:00"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message"
}
```

### 2. Check Authentication
**Endpoint:** `GET /api/auth/check`

**Authentication:** User session required

**Response (Success):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "name": "User Name",
    "login": "username",
    "email": "user@example.com",
    "groups": ["DGS Portal", "Other Groups"],
    "is_admin": false,
    "has_dgs_portal": true,
    "authenticated": true
  }
}
```

### 3. Logout
**Endpoint:** `POST /api/auth/logout`

**Authentication:** User session required

**Response (Success):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### 4. Refresh Token
**Endpoint:** `POST /api/auth/refresh`

**Authentication:** User session required

**Response (Success):**
```json
{
  "success": true,
  "message": "Session is valid",
  "user": {
    "id": 1,
    "name": "User Name",
    "login": "username"
  }
}
```

## Usage Examples

### React Login Example
```javascript
const login = async (username, password) => {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        db: 'your_database_name',
        login: username,
        password: password
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Store session info
      localStorage.setItem('user', JSON.stringify(data.user));
      localStorage.setItem('session', JSON.stringify(data.session));
      return data;
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};
```

### Check Authentication Example
```javascript
const checkAuth = async () => {
  try {
    const response = await fetch('/api/auth/check', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Auth check failed:', error);
    return { success: false, authenticated: false };
  }
};
```

## Error Handling

- **Invalid credentials**: User will receive "Invalid credentials" error
- **Missing DGS Portal group**: User will receive "Access denied" error
- **Session expired**: User will need to login again
- **Server errors**: Generic error message with details logged server-side

## Security Notes

- All endpoints except login require valid session authentication
- CORS should be configured appropriately for your React app domain
- Session cookies are managed automatically by Odoo
- Users must be assigned to the DGS Portal security group