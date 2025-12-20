# LLM Council Mobile - Security Documentation

## Overview

This document outlines the security architecture of the LLM Council mobile application, including authentication flows, data storage, known risks, and production hardening requirements.

---

## Authentication Architecture

### JWT Token Flow

```
┌─────────────┐                  ┌─────────────┐
│   Client    │                  │   Backend   │
│  (Mobile)   │                  │  (FastAPI)  │
└─────────────┘                  └─────────────┘
      │                                 │
      │  POST /api/auth/login           │
      │  { email, password }            │
      │────────────────────────────────>│
      │                                 │
      │  200 OK                         │
      │  { access_token, refresh_token }│
      │<────────────────────────────────│
      │                                 │
      │  Store tokens in secure storage │
      │  (expo-secure-store, encrypted) │
      │                                 │
      │  GET /api/conversations         │
      │  Authorization: Bearer {token}  │
      │────────────────────────────────>│
      │                                 │
      │  200 OK { conversations }       │
      │<────────────────────────────────│
      │                                 │
      │  (Token expires after 60 min)   │
      │                                 │
      │  GET /api/conversations         │
      │  Authorization: Bearer {expired}│
      │────────────────────────────────>│
      │                                 │
      │  401 Unauthorized               │
      │<────────────────────────────────│
      │                                 │
      │  POST /api/auth/refresh         │
      │  { refresh_token }              │
      │────────────────────────────────>│
      │                                 │
      │  200 OK { new_access_token }    │
      │<────────────────────────────────│
      │                                 │
      │  Retry original request with new│
      │  token (automatic via axios)    │
      │────────────────────────────────>│
```

### State Machine

The app uses a 5-state authentication state machine:

- **INITIALIZING**: Checking for existing session on app launch
- **UNAUTHENTICATED**: No valid session, show login screen
- **AUTHENTICATING**: Login in progress (user submitted credentials)
- **AUTHENTICATED**: Valid session, app fully functional
- **ERROR**: Authentication failed, show error message

Transitions:
- `INITIALIZING` → `AUTHENTICATED` (found valid session)
- `INITIALIZING` → `UNAUTHENTICATED` (no session)
- `UNAUTHENTICATED` → `AUTHENTICATING` (user taps "Sign In")
- `AUTHENTICATING` → `AUTHENTICATED` (login success)
- `AUTHENTICATING` → `ERROR` (login failed)
- `ERROR` → `UNAUTHENTICATED` (user dismisses error)
- `AUTHENTICATED` → `UNAUTHENTICATED` (user logs out)

---

## Token Storage

### Secure Storage (expo-secure-store)

All authentication tokens and user data are stored using `expo-secure-store`, which provides:

- **Hardware-backed encryption** on supported devices (iOS Keychain, Android Keystore)
- **Fallback encryption** on devices without hardware support
- **Automatic key management** (no manual key handling required)

Storage Keys:
- `auth_access_token`: JWT access token (60 min expiry)
- `auth_refresh_token`: JWT refresh token (7 day expiry)
- `auth_user`: User profile JSON (email, name)

### What We Don't Store

- ❌ Passwords (never stored client-side)
- ❌ Plaintext tokens in AsyncStorage
- ❌ API keys or secrets in app bundle
- ❌ Conversation history locally (fetched on demand)

---

## Token Refresh Strategy

The app uses an **automatic token refresh** strategy to maintain sessions without user interruption:

1. **Interceptor Detection**: Axios response interceptor detects `401 Unauthorized` responses
2. **Single Refresh Attempt**: A flag prevents concurrent refresh attempts
3. **Queue Failed Requests**: While refreshing, failed requests are queued
4. **Call Refresh Endpoint**: POST to `/api/auth/refresh` with stored refresh token
5. **Update Tokens**: New access token saved to secure storage
6. **Retry Queued Requests**: All queued requests retried with new token
7. **Fallback to Re-auth**: If refresh fails, tokens are cleared and user returns to login

This ensures:
- No duplicate refresh requests
- No dropped API calls during refresh
- Seamless experience for the user

---

## Logging and Redaction

### Development Mode

Logs show **redacted tokens** to help debugging while preventing accidental exposure:

```javascript
// Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

// Logged as: "eyJh...w5c" (first 4 + last 4 characters)
```

### Production Mode

Logs are **minimal** and contain **no sensitive data**:
- ✅ Log: "Authentication successful"
- ❌ Don't log: Tokens, passwords, user emails, API responses

Configure via environment:
```javascript
const isProduction = !__DEV__;
if (isProduction) {
  console.log = () => {}; // Disable all logs
}
```

---

## Network Security

### API Communication

- **HTTPS Only**: Backend must use HTTPS in production (currently HTTP for local dev)
- **Bearer Token**: All authenticated requests include `Authorization: Bearer {token}` header
- **No Credentials in URL**: Never pass tokens or passwords in query params

### Certificate Pinning

**Status**: Not implemented (future enhancement)

For production, consider adding certificate pinning to prevent MITM attacks:
```javascript
// Example with react-native-ssl-pinning
const response = await SSLPinning.fetch('https://api.llmcouncil.com', {
  method: 'GET',
  sslPinning: {
    certs: ['sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=']
  }
});
```

---

## Known Risks and Mitigations

### 🔴 HIGH RISK: Mock User Database

**Issue**: Backend uses hardcoded mock users for demo purposes.

```python
# backend/auth.py
MOCK_USERS = {
    "demo@llmcouncil.com": {
        "email": "demo@llmcouncil.com",
        "hashed_password": "$2b$12$...",
        "name": "Demo User"
    }
}
```

**Mitigation Required**:
- Replace with PostgreSQL/MongoDB database
- Use environment-based user provisioning
- Implement proper user registration endpoint

---

### 🔴 HIGH RISK: Development JWT Secret

**Issue**: Backend uses default `SECRET_KEY = "dev-secret-key-change-in-production"`.

**Mitigation Required**:
1. Generate strong secret: `openssl rand -hex 32`
2. Store in EAS Secrets: `eas secret:create --scope project --name JWT_SECRET_KEY --value <secret>`
3. Update `backend/config.py`:
   ```python
   SECRET_KEY = os.getenv("JWT_SECRET_KEY")
   if not SECRET_KEY:
       raise ValueError("JWT_SECRET_KEY environment variable not set")
   ```

---

### 🟡 MEDIUM RISK: No Rate Limiting

**Issue**: Login endpoint has no rate limiting, vulnerable to brute force attacks.

**Mitigation Required**:
- Add rate limiting middleware (e.g., `slowapi` for FastAPI)
- Example: 5 login attempts per IP per 15 minutes
- Return 429 Too Many Requests after threshold

---

### 🟡 MEDIUM RISK: Token Expiry Windows

**Issue**: 
- Access token: 60 minutes (might be too long)
- Refresh token: 7 days (might be too long)

**Recommendation**:
- Consider reducing access token to 15-30 minutes for higher security
- Add configurable expiry per environment
- Implement token revocation list (blacklist) for compromised tokens

---

### 🟢 LOW RISK: No Biometric Authentication

**Issue**: Users must enter password on every fresh login.

**Enhancement**:
- Add Face ID/Touch ID support via `expo-local-authentication`
- Store refresh token in secure store, protect with biometric
- Code example:
  ```javascript
  import * as LocalAuthentication from 'expo-local-authentication';
  
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Authenticate to continue',
  });
  if (result.success) {
    // Retrieve refresh token and auto-login
  }
  ```

---

## Production Hardening Checklist

Before deploying to production, complete these steps:

### Backend
- [ ] Replace mock user database with PostgreSQL/MongoDB
- [ ] Generate and configure production JWT secret key
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Add rate limiting to `/api/auth/login` endpoint
- [ ] Configure CORS to allow only production mobile app origin
- [ ] Set up error monitoring (e.g., Sentry)
- [ ] Configure log aggregation (e.g., CloudWatch, Datadog)
- [ ] Implement token revocation/blacklist mechanism
- [ ] Add account lockout after failed login attempts
- [ ] Set up automated security scanning (e.g., Dependabot, Snyk)

### Mobile
- [ ] Configure production API base URL (replace localhost:8001)
- [ ] Store API URL in EAS Secrets or environment config
- [ ] Disable all console.log statements in production builds
- [ ] Enable certificate pinning for API requests
- [ ] Add biometric authentication option
- [ ] Implement session timeout (auto-logout after inactivity)
- [ ] Add "Remember Me" option (longer refresh token expiry)
- [ ] Test token refresh flow on real devices
- [ ] Test session restore after app kill
- [ ] Test logout flow (verify secure store cleared)
- [ ] Set up crash reporting (e.g., Sentry)
- [ ] Configure ProGuard/R8 obfuscation (Android)
- [ ] Enable bitcode/strip debug symbols (iOS)

### EAS Build
- [ ] Run `eas init` and link project
- [ ] Configure EAS Secrets for JWT_SECRET_KEY
- [ ] Build preview shell: `eas build --profile preview --platform all`
- [ ] Install preview build on test devices
- [ ] Publish test update: `eas update --channel preview --message "Test"`
- [ ] Verify update downloads and applies correctly
- [ ] Build production shell: `eas build --profile production --platform all`
- [ ] Submit to App Store/Play Store
- [ ] Monitor update adoption metrics

---

## Runtime Version Strategy

The app uses **SDK-based runtime version** (`runtimeVersion: { policy: "sdkVersion" }`):

- **Compatible Updates**: Any JavaScript/asset changes without native code changes
- **Incompatible Updates**: Native module additions, SDK upgrades, native config changes

### When to Bump Runtime Version

You **must build a new native shell** when:
- Upgrading Expo SDK (e.g., SDK 54 → SDK 55)
- Adding new native modules (e.g., `expo-camera`)
- Changing native configuration (AndroidManifest.xml, Info.plist)
- Modifying app.json splash/icon/orientation

You **can publish OTA update** when:
- Fixing bugs in JavaScript code
- Updating UI components
- Changing API endpoints
- Modifying business logic
- Updating assets (images, fonts)

### Manual Runtime Version Override

If needed, you can manually version in `app.json`:
```json
{
  "expo": {
    "runtimeVersion": "1.0.0"
  }
}
```

Then increment for incompatible changes: `1.0.0` → `1.1.0`

---

## Incident Response

### Compromised JWT Secret

If the JWT secret is exposed:

1. **Rotate Secret Immediately**:
   ```bash
   eas secret:delete --scope project --name JWT_SECRET_KEY
   eas secret:create --scope project --name JWT_SECRET_KEY --value <new-secret>
   ```

2. **Invalidate All Tokens**: Implement token blacklist or add `issued_before` timestamp check

3. **Force Re-authentication**: Clear all user sessions, require fresh login

4. **Audit Logs**: Check for suspicious token usage patterns

### Suspicious Login Activity

If detecting unusual login patterns:

1. **Lock Account**: Temporarily disable affected user accounts
2. **Notify User**: Send email about suspicious activity
3. **Require Password Reset**: Force password change on next login
4. **Review Logs**: Check access logs for unauthorized API calls

---

## Contact

For security issues, contact:
- **Email**: security@llmcouncil.com (example, update for production)
- **Bug Bounty**: (if applicable)

---

## Changelog

### v1.0.0 (2024)
- Initial JWT authentication implementation
- expo-secure-store integration
- Automatic token refresh
- Session restore on app launch
- EAS Update configuration
