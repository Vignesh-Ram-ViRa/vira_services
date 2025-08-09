# Google OAuth Integration Guide

> **Complete guide to setup and use Google OAuth authentication with Vira Services**

## 📋 **Overview**

This guide covers:
- Setting up Google OAuth credentials
- Configuring Vira Services for Google OAuth
- Integrating with React applications
- Production deployment considerations

## 🎯 **How Google OAuth Works in Vira Services**

### Authentication Flow
1. **User clicks "Login with Google"** in React app
2. **Redirects to Google OAuth** consent screen
3. **User grants permission** to access profile/email
4. **Google redirects back** with authorization code
5. **Backend exchanges code** for user profile data
6. **Creates/links user account** and generates JWT token
7. **Returns JWT token** to React app for authentication

### User Account Handling
- **New Google Users**: Automatically creates account with `NORMAL_USER` role
- **Existing Users**: Links Google account to existing user (by email)
- **Role Assignment**: All Google OAuth users get `NORMAL_USER` role by default

---

## 🔧 **Part 1: Google Cloud Console Setup**

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create New Project** or select existing
3. **Note the Project ID** for reference

### Step 2: Enable Google+ API

1. **Navigate to APIs & Services > Library**
2. **Search for "Google+ API"**
3. **Click Enable** (required for user profile access)

### Step 3: Create OAuth 2.0 Credentials

1. **Go to APIs & Services > Credentials**
2. **Click "Create Credentials" > OAuth 2.0 Client IDs**
3. **Configure OAuth consent screen** (if first time):
   - **Application type**: External
   - **Application name**: Vira Services
   - **User support email**: Your email
   - **Developer contact**: Your email
   - **Scopes**: Add `openid`, `profile`, `email`

4. **Create OAuth Client ID**:
   - **Application type**: Web application
   - **Name**: Vira Services OAuth
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (React dev)
     - `http://localhost:8080` (Backend dev)
     - `https://your-production-domain.com` (Production)
   - **Authorized redirect URIs**:
     - `http://localhost:8080/api/auth/oauth2/callback/google` (Local)
     - `https://your-backend-domain.com/api/auth/oauth2/callback/google` (Production)

5. **Copy Client ID and Client Secret** - you'll need these!

### Step 4: Test Domain Verification (Production Only)

For production, verify your domain ownership in Google Cloud Console.

---

## ⚙️ **Part 2: Backend Configuration**

### Local Development Setup

**Update `application-dev.yml`:**
```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: YOUR_GOOGLE_CLIENT_ID_HERE
            client-secret: YOUR_GOOGLE_CLIENT_SECRET_HERE
            redirect-uri: "http://localhost:8080/api/auth/oauth2/callback/google"
            scope:
              - openid
              - profile
              - email
        provider:
          google:
            authorization-uri: https://accounts.google.com/o/oauth2/v2/auth
            token-uri: https://oauth2.googleapis.com/token
            user-info-uri: https://www.googleapis.com/oauth2/v3/userinfo
```

### Production Setup

**Set Environment Variables:**
```bash
# Railway/Production environment
GOOGLE_CLIENT_ID=your_actual_client_id
GOOGLE_CLIENT_SECRET=your_actual_client_secret
```

**Update `application-prod.yml`:**
```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: ${GOOGLE_CLIENT_ID}
            client-secret: ${GOOGLE_CLIENT_SECRET}
            redirect-uri: "https://your-backend-domain.com/api/auth/oauth2/callback/google"
            scope:
              - openid
              - profile
              - email
        provider:
          google:
            authorization-uri: https://accounts.google.com/o/oauth2/v2/auth
            token-uri: https://oauth2.googleapis.com/token
            user-info-uri: https://www.googleapis.com/oauth2/v3/userinfo
```

### Test Backend Configuration

**Start your application and test:**
```bash
# This should redirect to Google OAuth (in browser)
http://localhost:8080/oauth2/authorization/google
```

---

## ⚛️ **Part 3: React Integration**

### Installation

```bash
npm install @google-cloud/local-auth google-auth-library
# OR use a React OAuth library
npm install react-google-login
```

### Option 1: Direct OAuth Flow

**Create OAuth Component:**
```jsx
// components/GoogleOAuth.jsx
import React from 'react';

const GoogleOAuth = () => {
  const handleGoogleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = 'http://localhost:8080/oauth2/authorization/google';
  };

  return (
    <button 
      onClick={handleGoogleLogin}
      className="google-login-btn"
    >
      <img src="/google-icon.svg" alt="Google" />
      Continue with Google
    </button>
  );
};

export default GoogleOAuth;
```

### Option 2: Using React Google Login Library

**Install:**
```bash
npm install react-google-login
```

**Component Implementation:**
```jsx
// components/GoogleLogin.jsx
import React from 'react';
import { GoogleLogin } from 'react-google-login';

const GoogleLoginComponent = ({ onSuccess, onFailure }) => {
  const handleSuccess = (response) => {
    // Send the authorization code to your backend
    fetch('http://localhost:8080/api/auth/oauth2/callback/google', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: response.code,
        // Additional data if needed
      }),
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Store JWT token
        localStorage.setItem('token', data.data.token);
        localStorage.setItem('refreshToken', data.data.refreshToken);
        onSuccess(data.data);
      }
    })
    .catch(onFailure);
  };

  return (
    <GoogleLogin
      clientId="YOUR_GOOGLE_CLIENT_ID"
      buttonText="Login with Google"
      onSuccess={handleSuccess}
      onFailure={onFailure}
      cookiePolicy={'single_host_origin'}
      responseType="code"
      accessType="offline"
    />
  );
};

export default GoogleLoginComponent;
```

### Option 3: Complete Authentication Service

**Create Auth Service:**
```javascript
// services/authService.js
class AuthService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8080';
  }

  // Traditional login
  async login(username, password) {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    return this.handleAuthResponse(response);
  }

  // Google OAuth login
  initiateGoogleLogin() {
    window.location.href = `${this.baseURL}/oauth2/authorization/google`;
  }

  // Handle OAuth callback (if implementing client-side handling)
  async handleGoogleCallback(code) {
    const response = await fetch(`${this.baseURL}/api/auth/oauth2/callback/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    });
    return this.handleAuthResponse(response);
  }

  async handleAuthResponse(response) {
    const data = await response.json();
    if (data.success) {
      localStorage.setItem('token', data.data.token);
      localStorage.setItem('refreshToken', data.data.refreshToken);
      localStorage.setItem('user', JSON.stringify(data.data.user));
      return data.data;
    }
    throw new Error(data.error || 'Authentication failed');
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  getToken() {
    return localStorage.getItem('token');
  }
}

export default new AuthService();
```

### OAuth Callback Handling

**Create callback page (React Router):**
```jsx
// pages/OAuthCallback.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('processing');

  useEffect(() => {
    const processCallback = async () => {
      try {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
          setStatus('error');
          return;
        }

        if (code) {
          // The backend should handle this automatically
          // but you can add additional processing here
          
          // Check if we have tokens (backend should redirect with tokens)
          const urlHash = window.location.hash;
          const params = new URLSearchParams(urlHash.substring(1));
          
          const token = params.get('token');
          const refreshToken = params.get('refreshToken');
          
          if (token) {
            localStorage.setItem('token', token);
            localStorage.setItem('refreshToken', refreshToken);
            setStatus('success');
            navigate('/dashboard');
          } else {
            // Fallback: fetch user info with current token
            navigate('/dashboard');
          }
        }
      } catch (error) {
        console.error('OAuth callback error:', error);
        setStatus('error');
      }
    };

    processCallback();
  }, [searchParams, navigate]);

  return (
    <div className="oauth-callback">
      {status === 'processing' && <div>Processing login...</div>}
      {status === 'success' && <div>Login successful! Redirecting...</div>}
      {status === 'error' && <div>Login failed. Please try again.</div>}
    </div>
  );
};

export default OAuthCallback;
```

### Add to React Router

```jsx
// App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import OAuthCallback from './pages/OAuthCallback';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth/callback" element={<OAuthCallback />} />
        {/* Other routes */}
      </Routes>
    </Router>
  );
}
```

---

## 🚀 **Part 4: Production Deployment**

### Backend Configuration (Railway)

**Set Environment Variables in Railway:**
```bash
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret
FRONTEND_URL=https://your-frontend-domain.com
```

### Frontend Configuration

**Environment Variables:**
```bash
# .env.production
REACT_APP_API_URL=https://your-backend-domain.com
REACT_APP_GOOGLE_CLIENT_ID=your_production_client_id
```

### Update Google OAuth Settings

1. **Add Production URLs** to Google Cloud Console:
   - **Authorized origins**: `https://your-frontend-domain.com`
   - **Redirect URIs**: `https://your-backend-domain.com/api/auth/oauth2/callback/google`

2. **Verify Domain Ownership** in Google Cloud Console

3. **Update OAuth Consent Screen** for production

---

## 🧪 **Testing Guide**

### Local Testing

1. **Start Backend**: `./mvnw spring-boot:run`
2. **Start React**: `npm start`
3. **Test OAuth Flow**:
   - Click "Login with Google" button
   - Complete Google auth flow
   - Verify JWT token received
   - Test authenticated API calls

### Test Endpoints

```bash
# Test OAuth initiation (should redirect to Google)
curl -v "http://localhost:8080/oauth2/authorization/google"

# Test authenticated endpoint with Google user
curl -X GET "http://localhost:8080/api/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Debugging

**Check browser console for:**
- CORS errors
- Redirect issues
- Token storage problems

**Check backend logs for:**
- OAuth processing errors
- User creation/linking issues
- JWT generation problems

---

## 🔐 **Security Considerations**

### Best Practices

1. **Never expose Client Secret** in frontend code
2. **Use HTTPS** in production
3. **Validate redirect URIs** properly
4. **Store tokens securely** (httpOnly cookies recommended for production)
5. **Implement token refresh** logic
6. **Handle user consent revocation**

### CORS Configuration

Ensure your backend allows requests from your frontend domain:
```yaml
cors:
  allowed-origins: 
    - "https://your-frontend-domain.com"
    - "http://localhost:3000"  # Development
```

---

## 📚 **API Reference**

### Backend Endpoints

```bash
# Initiate Google OAuth
GET /oauth2/authorization/google

# OAuth callback (handled automatically)
GET /oauth2/callback/google

# Get current user (works for both traditional and OAuth users)
GET /api/auth/me
Authorization: Bearer {jwt_token}
```

### Response Format

**Successful OAuth Login:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "refresh_token_here",
    "tokenType": "Bearer",
    "user": {
      "id": 123,
      "username": "john.doe",
      "email": "john.doe@gmail.com",
      "enabled": true,
      "roles": ["NORMAL_USER"],
      "status": "APPROVED"
    },
    "message": "Login successful"
  }
}
```

---

## 🛠️ **Troubleshooting**

### Common Issues

**1. "redirect_uri_mismatch" Error:**
- Check Google Cloud Console redirect URIs
- Ensure exact match with configured URIs
- Check for trailing slashes

**2. "invalid_client" Error:**
- Verify Client ID and Secret
- Check environment variables
- Ensure OAuth consent screen is configured

**3. "Access blocked" Error:**
- Check OAuth consent screen status
- Verify domain ownership
- Ensure app is not restricted

**4. React Integration Issues:**
- Check CORS configuration
- Verify API URLs
- Check for token storage issues

**5. User Not Created:**
- Check backend logs for errors
- Verify email uniqueness constraints
- Check role assignment logic

### Debug Steps

1. **Check Google Cloud Console** settings
2. **Verify environment variables** are set correctly
3. **Test OAuth URL** directly in browser
4. **Check backend logs** for detailed errors
5. **Inspect network requests** in browser dev tools

---

## 🎯 **Next Steps**

- **Enhanced Security**: Implement token refresh rotation
- **User Management**: Add admin interface for OAuth users
- **Multiple Providers**: Add Facebook, GitHub OAuth
- **Mobile Integration**: Extend for React Native apps

**✅ Google OAuth is now integrated!** Users can seamlessly authenticate with their Google accounts! 🚀 