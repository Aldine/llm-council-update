# OAuth Setup Guide for BFF Authentication

This guide explains how to set up OAuth authentication for the LLM Council web app using the Backend-for-Frontend (BFF) pattern with server-side sessions.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [JWT vs BFF Comparison](#jwt-vs-bff-comparison)
- [Quick Start (Mock OAuth)](#quick-start-mock-oauth)
- [Production Setup](#production-setup)
- [Provider-Specific Guides](#provider-specific-guides)

---

## Architecture Overview

### BFF Pattern Benefits

The BFF (Backend-for-Frontend) authentication pattern offers several advantages over client-side JWT:

**Security:**
- ✅ Tokens never exposed to JavaScript (XSS protection)
- ✅ HttpOnly cookies prevent token theft
- ✅ CSRF protection with SameSite cookies
- ✅ No localStorage vulnerabilities
- ✅ Server-side token storage and validation

**Simplicity:**
- ✅ Frontend doesn't handle OAuth flows
- ✅ No token refresh logic in client
- ✅ Single redirect-based login
- ✅ Automatic session management

**Production-Ready:**
- ✅ Works with standard OAuth providers
- ✅ Supports PKCE for added security
- ✅ Session rotation and expiry
- ✅ Idle timeout support

### How It Works

```
┌─────────┐       ┌─────────┐       ┌──────────────┐       ┌─────────────┐
│         │       │         │       │              │       │             │
│ Browser │◄─────►│ Backend │◄─────►│ OAuth Server │       │  Sessions   │
│         │       │  (BFF)  │       │   Provider   │       │   (Redis)   │
└─────────┘       └─────────┘       └──────────────┘       └─────────────┘
     │                  │
     │  1. /login       │
     ├─────────────────►│
     │                  │  2. Redirect to OAuth
     │◄─────────────────┤
     │                  │
     │  3. User logs in at OAuth provider
     │                  │
     │  4. Callback     │
     │  with code       │
     ├─────────────────►│
     │                  │  5. Exchange code for tokens
     │                  ├─────────────────►
     │                  │◄─────────────────┤
     │                  │  6. Create session, set cookie
     │◄─────────────────┤
     │                  │
     │  7. All requests │
     │  include cookie  │
     ├─────────────────►│
```

---

## JWT vs BFF Comparison

| Feature | JWT (Current) | BFF (New) |
|---------|--------------|-----------|
| **Token Storage** | localStorage (browser) | Server-side session |
| **Token Exposure** | ❌ Exposed to JavaScript | ✅ HttpOnly cookie |
| **XSS Vulnerability** | ❌ High risk | ✅ Protected |
| **CSRF Protection** | ✅ Not needed (no cookies) | ✅ SameSite + tokens |
| **Frontend Complexity** | ❌ High (token management) | ✅ Low (simple redirects) |
| **Session Management** | ❌ Client-side | ✅ Server-side |
| **Token Refresh** | ❌ Frontend handles | ✅ Backend handles |
| **Logout** | ❌ Clear localStorage | ✅ Server session + token revocation |
| **Best For** | Mobile apps, SPAs with API | Web apps, teams with backend focus |

---

## Quick Start (Mock OAuth)

For local development, the BFF system includes **mock OAuth** that simulates a real provider without requiring external services.

### 1. Enable Mock OAuth

In your `.env` file:

```bash
OAUTH_USE_MOCK=true
APP_BASE_URL=http://localhost:5173
OAUTH_REDIRECT_URI=http://localhost:8001/bff/auth/callback
```

### 2. Start the Backend

```bash
cd backend
uv run python -m backend.main
```

Backend will start on `http://localhost:8001`

### 3. Test the Flow

1. Open browser to: `http://localhost:8001/bff/auth/login`
2. Mock OAuth will auto-approve and redirect back
3. Session cookie is set automatically
4. Check session: `curl -b cookies.txt http://localhost:8001/bff/me`

### 4. Mock Endpoints Available

- `GET /bff/mock/authorize` - Simulates OAuth login page (auto-approves)
- `POST /bff/mock/token` - Returns mock tokens
- `GET /bff/mock/userinfo` - Returns demo user profile

**Mock User Profile:**
```json
{
  "email": "demo@llmcouncil.com",
  "name": "Demo User",
  "sub": "mock-user-123"
}
```

---

## Production Setup

### Step 1: Choose an OAuth Provider

Popular providers:
- **Auth0** - Easy setup, generous free tier
- **Okta** - Enterprise-grade security
- **Google OAuth** - Familiar login for users
- **Azure AD** - Best for Microsoft environments
- **GitHub OAuth** - Good for developer tools

### Step 2: Register Your Application

Register a **Web Application** (not SPA or mobile) with your provider.

**Required Settings:**

| Setting | Local Development | Production |
|---------|------------------|------------|
| **Redirect URI** | `http://localhost:8001/bff/auth/callback` | `https://api.yourdomain.com/bff/auth/callback` |
| **Post-Logout URI** | `http://localhost:5173/` | `https://app.yourdomain.com/` |
| **Application Type** | Web Application | Web Application |
| **Grant Types** | Authorization Code + PKCE | Authorization Code + PKCE |

### Step 3: Configure Environment

Update `.env` with your provider details:

```bash
# Disable mock OAuth
OAUTH_USE_MOCK=false

# Provider configuration
OAUTH_ISSUER=https://your-domain.auth0.com
OAUTH_AUTHORIZATION_ENDPOINT=https://your-domain.auth0.com/authorize
OAUTH_TOKEN_ENDPOINT=https://your-domain.auth0.com/oauth/token
OAUTH_USERINFO_ENDPOINT=https://your-domain.auth0.com/userinfo
OAUTH_REVOCATION_ENDPOINT=https://your-domain.auth0.com/oauth/revoke

# Your application credentials
OAUTH_CLIENT_ID=your_client_id_here
OAUTH_CLIENT_SECRET=your_client_secret_here

# Scopes (start minimal)
OAUTH_SCOPES=openid profile email

# Redirect configuration
OAUTH_REDIRECT_URI=http://localhost:8001/bff/auth/callback
APP_BASE_URL=http://localhost:5173

# Session security (generate with: openssl rand -hex 32)
SESSION_SECRET=replace_with_random_secret
COOKIE_SECURE=false  # Set to true in production with HTTPS
```

### Step 4: Update CORS

In `backend/main.py`, ensure your production frontend origin is allowed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://app.yourdomain.com",  # Production
    ],
    allow_credentials=True,  # CRITICAL for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 5: Production Checklist

Before deploying:

- [ ] Replace `SESSION_SECRET` with strong random value
- [ ] Set `COOKIE_SECURE=true` (requires HTTPS)
- [ ] Use Redis/database for session storage (not in-memory)
- [ ] Enable rate limiting on auth endpoints
- [ ] Add CSRF protection for state-changing routes
- [ ] Configure HSTS header for HTTPS
- [ ] Set up log redaction for sensitive data
- [ ] Test token revocation on logout
- [ ] Configure session expiry and idle timeout
- [ ] Set up monitoring for failed logins

---

## Provider-Specific Guides

### Auth0

**1. Create Application:**
- Go to [Auth0 Dashboard](https://manage.auth0.com/)
- Applications → Create Application
- Choose "Regular Web Application"

**2. Configure Settings:**
```
Allowed Callback URLs: http://localhost:8001/bff/auth/callback
Allowed Logout URLs: http://localhost:5173/
Allowed Web Origins: http://localhost:5173
```

**3. Get Configuration:**
- Domain: `your-tenant.auth0.com`
- Client ID: Found in application settings
- Client Secret: Found in application settings

**4. Environment Variables:**
```bash
OAUTH_ISSUER=https://your-tenant.auth0.com
OAUTH_AUTHORIZATION_ENDPOINT=https://your-tenant.auth0.com/authorize
OAUTH_TOKEN_ENDPOINT=https://your-tenant.auth0.com/oauth/token
OAUTH_USERINFO_ENDPOINT=https://your-tenant.auth0.com/userinfo
OAUTH_REVOCATION_ENDPOINT=https://your-tenant.auth0.com/oauth/revoke
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_SCOPES=openid profile email
```

---

### Google OAuth

**1. Create Project:**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project
- Enable Google+ API

**2. Create OAuth Client:**
- APIs & Services → Credentials → Create Credentials → OAuth Client ID
- Application type: Web application

**3. Configure:**
```
Authorized redirect URIs: http://localhost:8001/bff/auth/callback
Authorized JavaScript origins: http://localhost:5173
```

**4. Environment Variables:**
```bash
OAUTH_ISSUER=https://accounts.google.com
OAUTH_AUTHORIZATION_ENDPOINT=https://accounts.google.com/o/oauth2/v2/auth
OAUTH_TOKEN_ENDPOINT=https://oauth2.googleapis.com/token
OAUTH_USERINFO_ENDPOINT=https://openidconnect.googleapis.com/v1/userinfo
OAUTH_REVOCATION_ENDPOINT=https://oauth2.googleapis.com/revoke
OAUTH_CLIENT_ID=your_client_id.apps.googleusercontent.com
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_SCOPES=openid profile email
```

---

### Azure AD / Microsoft Entra

**1. Register Application:**
- Go to [Azure Portal](https://portal.azure.com/)
- Azure Active Directory → App registrations → New registration

**2. Configure:**
```
Redirect URI: http://localhost:8001/bff/auth/callback (Web)
Supported account types: Single tenant or multitenant
```

**3. Create Client Secret:**
- Certificates & secrets → New client secret

**4. API Permissions:**
- Add Microsoft Graph → Delegated permissions
- Add: `openid`, `profile`, `email`, `User.Read`

**5. Environment Variables:**
```bash
OAUTH_ISSUER=https://login.microsoftonline.com/{tenant-id}/v2.0
OAUTH_AUTHORIZATION_ENDPOINT=https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize
OAUTH_TOKEN_ENDPOINT=https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
OAUTH_USERINFO_ENDPOINT=https://graph.microsoft.com/v1.0/me
OAUTH_CLIENT_ID=your_application_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_SCOPES=openid profile email User.Read
```

---

### Okta

**1. Create Application:**
- Go to [Okta Developer Console](https://developer.okta.com/)
- Applications → Create App Integration
- Choose "OIDC - OpenID Connect"
- Application type: Web Application

**2. Configure:**
```
Sign-in redirect URIs: http://localhost:8001/bff/auth/callback
Sign-out redirect URIs: http://localhost:5173/
Controlled access: Allow everyone in your organization to access
```

**3. Environment Variables:**
```bash
OAUTH_ISSUER=https://your-domain.okta.com/oauth2/default
OAUTH_AUTHORIZATION_ENDPOINT=https://your-domain.okta.com/oauth2/default/v1/authorize
OAUTH_TOKEN_ENDPOINT=https://your-domain.okta.com/oauth2/default/v1/token
OAUTH_USERINFO_ENDPOINT=https://your-domain.okta.com/oauth2/default/v1/userinfo
OAUTH_REVOCATION_ENDPOINT=https://your-domain.okta.com/oauth2/default/v1/revoke
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
OAUTH_SCOPES=openid profile email
```

---

## Testing Your Setup

### Test Login Flow

```bash
# 1. Start backend
uv run python -m backend.main

# 2. Open browser and initiate login
open http://localhost:8001/bff/auth/login

# 3. Complete OAuth flow at provider

# 4. Verify session was created
curl -v http://localhost:8001/bff/me \
  -H "Cookie: session_id=YOUR_SESSION_COOKIE"
```

### Test Logout

```bash
curl -X POST http://localhost:8001/bff/auth/logout \
  -H "Cookie: session_id=YOUR_SESSION_COOKIE"
```

### Verify Cookie Settings

Check that session cookie has correct security flags:
```
Set-Cookie: session_id=...; 
  Path=/; 
  HttpOnly; 
  SameSite=Lax; 
  Secure  (in production only)
```

---

## Troubleshooting

### Common Issues

**1. "Invalid or expired state"**
- State token expired (10 min lifetime)
- Solution: Restart login flow

**2. "No access token received"**
- Check redirect URI matches exactly
- Verify client credentials
- Check provider configuration

**3. "Session expired"**
- Default: 24 hour session lifetime, 60 min idle timeout
- Adjust in `backend/bff/session.py`

**4. Cookies not being sent**
- Verify `allow_credentials=True` in CORS
- Check frontend uses `credentials: 'include'`
- Verify domains match (localhost to localhost)

**5. OAuth provider rejects redirect**
- Redirect URI must match EXACTLY (check trailing slashes)
- Must be registered in provider console
- HTTP only works for localhost, use HTTPS in production

---

## Migration from JWT

If migrating from existing JWT system:

### Backend Changes

1. Keep existing `/api/auth/*` endpoints for mobile app
2. Add new `/bff/auth/*` endpoints for web app
3. Both can coexist using different auth dependencies

### Frontend Changes

1. Create new `frontend-bff/` directory
2. Remove `auth.js` (token management)
3. Simplify `AuthContext` to only track user state
4. Update `Login` component to redirect to `/bff/auth/login`
5. Change API client to use `credentials: 'include'`

### Gradual Migration

- Keep JWT for mobile app (already implemented)
- Use BFF for new web app users
- Migrate existing web users gradually
- Eventually deprecate JWT for web

---

## Security Best Practices

1. **Never expose tokens to frontend** - Store in HttpOnly cookies only
2. **Use HTTPS in production** - Required for `Secure` cookie flag
3. **Implement CSRF protection** - SameSite cookies + CSRF tokens for mutations
4. **Rate limit auth endpoints** - Prevent brute force attacks
5. **Log security events** - Track failed logins, token revocations
6. **Rotate secrets regularly** - Client secrets, session secrets
7. **Validate all inputs** - State tokens, authorization codes
8. **Set appropriate timeouts** - Session expiry, idle timeout
9. **Revoke tokens on logout** - Call provider revocation endpoint
10. **Monitor for anomalies** - Alert on unusual patterns

---

## Support

For issues or questions:
1. Check provider documentation for OAuth specifics
2. Review FastAPI CORS and cookie documentation
3. Test with mock OAuth first before real provider
4. Check browser console for cookie/CORS errors

---

## Additional Resources

- [OAuth 2.0 RFC](https://datatracker.ietf.org/doc/html/rfc6749)
- [PKCE RFC](https://datatracker.ietf.org/doc/html/rfc7636)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
