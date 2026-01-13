# BFF Auth Demo - Frontend

Simple React demo showing the Backend-for-Frontend (BFF) OAuth pattern.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start dev server (port 5174)
npm run dev
```

Then open: http://localhost:5174

## 🎯 What This Demonstrates

### Traditional JWT (Insecure)
```javascript
// ❌ Tokens stored in localStorage (XSS vulnerable)
localStorage.setItem('token', response.token)

// ❌ Frontend manages token lifecycle
fetch('/api', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

### BFF Pattern (Secure)
```javascript
// ✅ No tokens in frontend - just redirect
window.location.href = '/bff/auth/login'

// ✅ HttpOnly cookies (XSS protected)
fetch('/bff/me', {
  credentials: 'include'  // That's it!
})
```

## 🔐 Security Benefits

1. **No tokens in JavaScript** - HttpOnly cookies prevent XSS attacks
2. **Server-side sessions** - Tokens never touch the browser
3. **CSRF protection** - SameSite cookies + state parameter
4. **Simpler frontend** - No token refresh logic needed

## 📁 Files

- `src/App.jsx` - Main demo component (100 lines)
- `src/index.css` - Styling
- `package.json` - Dependencies (React + Vite only)

## 🧪 Testing

1. **Start backend**: `uv run python -m backend.main` (port 8001)
2. **Start frontend**: `npm run dev` (port 5174)
3. **Click "Test Mock OAuth"** to try without real OAuth provider
4. **Click "Login (Real OAuth)"** requires OAuth setup in `.env`

## 🔗 Related

- Backend BFF implementation: `backend/bff/`
- OAuth setup guide: See `.env.example`
- Main app (JWT-based): `frontend/`
