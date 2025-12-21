"""BFF authentication routes with OAuth + sessions.

This router handles:
- GET /bff/auth/login: Redirect to OAuth provider
- GET /bff/auth/callback: Handle OAuth callback, create session
- POST /bff/auth/logout: Clear session and logout
- GET /bff/me: Get current user from session

For development, also includes mock OAuth endpoints.
"""
from typing import Optional

from fastapi import APIRouter, Response, Request, HTTPException, Query
from fastapi.responses import RedirectResponse

from .oauth import (
    oauth_config,
    generate_pkce_pair,
    build_authorization_url,
    exchange_code_for_tokens,
    get_user_info,
    revoke_token
)
from .session import session_store, oauth_state_store


router = APIRouter(prefix="/bff", tags=["BFF Auth"])


# Cookie settings
COOKIE_NAME = "session_id"
COOKIE_MAX_AGE = 86400  # 24 hours
COOKIE_SECURE = False  # Set to True in production with HTTPS
COOKIE_SAMESITE = "lax"


@router.get("/auth/login")
async def login(response: Response):
    """Initiate OAuth login flow.
    
    Generates PKCE challenge, saves state, redirects to OAuth provider.
    """
    # Generate PKCE pair
    verifier, challenge = generate_pkce_pair()
    
    # Create state for CSRF protection
    state = oauth_state_store.create_state(verifier)
    
    # Build authorization URL
    auth_url = build_authorization_url(oauth_config, state, challenge)
    
    # Redirect user to OAuth provider
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/auth/callback")
async def callback(
    request: Request,
    response: Response,
    code: str = Query(...),
    state: str = Query(...)
):
    """Handle OAuth callback.
    
    Validates state, exchanges code for tokens, creates session, sets cookie.
    """
    # Verify state and get PKCE verifier
    verifier = oauth_state_store.verify_state(state)
    if not verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(oauth_config, code, verifier)
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    if not access_token:
        raise HTTPException(status_code=500, detail="No access token received")
    
    # Get user profile
    user_info = await get_user_info(oauth_config, access_token)
    
    # Create server-side session
    session = session_store.create_session(
        user=user_info,
        access_token=access_token,
        refresh_token=refresh_token
    )
    
    # Set HttpOnly cookie with session ID
    response = RedirectResponse(url=oauth_config.app_base_url, status_code=302)
    response.set_cookie(
        key=COOKIE_NAME,
        value=session.session_id,
        max_age=COOKIE_MAX_AGE,
        httponly=True,  # Prevents JavaScript access
        secure=COOKIE_SECURE,  # HTTPS only in production
        samesite=COOKIE_SAMESITE,
        path="/"
    )
    
    return response


@router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user, clear session and cookie."""
    # Get session ID from cookie
    session_id = request.cookies.get(COOKIE_NAME)
    
    if session_id:
        # Get session to access refresh token
        session = session_store.get_session(session_id)
        
        # Revoke refresh token if available
        if session and session.refresh_token:
            await revoke_token(oauth_config, session.refresh_token)
        
        # Delete server-side session
        session_store.delete_session(session_id)
    
    # Clear cookie
    response = Response(content='{"message": "Logged out"}', media_type="application/json")
    response.delete_cookie(key=COOKIE_NAME, path="/")
    
    return response


@router.get("/me")
async def get_current_user(request: Request):
    """Get current user from session.
    
    Frontend calls this on app start to restore session.
    Returns 401 if no valid session.
    """
    # Get session ID from cookie
    session_id = request.cookies.get(COOKIE_NAME)
    
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get session
    session = session_store.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Return user profile (never expose tokens to frontend)
    return {
        "user": session.user,
        "authenticated": True
    }


# =============================================================================
# MOCK OAUTH ENDPOINTS FOR DEVELOPMENT
# =============================================================================
# These simulate an OAuth provider for local testing without external services.
# Remove these in production or when using a real OAuth provider.


@router.get("/mock/authorize")
async def mock_authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(...),
    state: str = Query(...),
    code_challenge: str = Query(...),
    code_challenge_method: str = Query(...),
    nonce: Optional[str] = Query(None)
):
    """Mock OAuth authorization endpoint for testing.
    
    In production, user would see OAuth provider login page here.
    For testing, we auto-approve and redirect back with code.
    """
    # Generate mock authorization code
    mock_code = f"mock_code_{state[:8]}"
    
    # Redirect back to callback with code
    callback_url = f"{redirect_uri}?code={mock_code}&state={state}"
    return RedirectResponse(url=callback_url, status_code=302)


@router.post("/mock/token")
async def mock_token(
    grant_type: str = Query(...),
    code: str = Query(...),
    redirect_uri: str = Query(...),
    client_id: str = Query(...),
    code_verifier: str = Query(...)
):
    """Mock OAuth token endpoint for testing.
    
    Returns mock access and refresh tokens.
    """
    # In production, validate PKCE verifier against stored challenge
    return {
        "access_token": f"mock_access_token_{code[:8]}",
        "refresh_token": f"mock_refresh_token_{code[:8]}",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "openid profile email"
    }


@router.get("/mock/userinfo")
async def mock_userinfo(request: Request):
    """Mock OAuth userinfo endpoint for testing.
    
    Returns mock user profile.
    """
    # In production, validate access token
    authorization = request.headers.get("Authorization", "")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "sub": "mock-user-123",
        "email": "demo@llmcouncil.com",
        "name": "Demo User",
        "given_name": "Demo",
        "family_name": "User",
        "email_verified": True
    }
