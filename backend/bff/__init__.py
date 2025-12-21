"""Backend-for-Frontend (BFF) authentication module.

This module implements OAuth2 + PKCE with server-side sessions.
Compared to JWT approach in backend/auth.py:
- More secure: HttpOnly cookies, no token exposure to JavaScript
- Simpler frontend: no token management needed
- Better for web apps: sessions server-side, tokens never leave backend
"""
