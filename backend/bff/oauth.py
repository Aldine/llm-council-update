"""OAuth2 + PKCE implementation for BFF pattern.

This module handles OAuth authorization flow with PKCE.
Currently configured for mock OAuth (dev mode).
Replace with real provider (Auth0, Okta, Google, Azure AD) for production.
"""
import os
import secrets
import hashlib
import base64
from typing import Dict, Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException


class OAuthConfig:
    """OAuth provider configuration."""
    
    def __init__(self):
        # Mock OAuth for development (replace with real provider)
        self.use_mock = os.getenv("OAUTH_USE_MOCK", "true").lower() == "true"
        
        if self.use_mock:
            # Mock OAuth endpoints for local testing
            self.issuer = "http://localhost:8002"
            self.authorization_endpoint = "http://localhost:8002/bff/mock/authorize"
            self.token_endpoint = "http://localhost:8002/bff/mock/token"
            self.userinfo_endpoint = "http://localhost:8002/bff/mock/userinfo"
            self.client_id = "mock-client-id"
            self.client_secret = "mock-client-secret"
            self.scopes = ["openid", "profile", "email"]
        else:
            # Real OAuth provider configuration
            self.issuer = os.getenv("OAUTH_ISSUER", "")
            self.authorization_endpoint = os.getenv("OAUTH_AUTHORIZATION_ENDPOINT", "")
            self.token_endpoint = os.getenv("OAUTH_TOKEN_ENDPOINT", "")
            self.userinfo_endpoint = os.getenv("OAUTH_USERINFO_ENDPOINT", "")
            self.client_id = os.getenv("OAUTH_CLIENT_ID", "")
            self.client_secret = os.getenv("OAUTH_CLIENT_SECRET", "")
            self.scopes = os.getenv("OAUTH_SCOPES", "openid profile email").split()
        
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8002/bff/auth/callback")
        self.app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge.
    
    Returns:
        (verifier, challenge) tuple
    """
    # Generate verifier: 43-128 characters
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    # Generate challenge: SHA256 hash of verifier
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return verifier, challenge


def build_authorization_url(config: OAuthConfig, state: str, challenge: str) -> str:
    """Build OAuth authorization URL with PKCE.
    
    Args:
        config: OAuth configuration
        state: CSRF state token
        challenge: PKCE code challenge
    
    Returns:
        Full authorization URL to redirect user to
    """
    params = {
        'response_type': 'code',
        'client_id': config.client_id,
        'redirect_uri': config.redirect_uri,
        'scope': ' '.join(config.scopes),
        'state': state,
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
        'nonce': secrets.token_urlsafe(16)  # For ID token validation
    }
    return f"{config.authorization_endpoint}?{urlencode(params)}"


async def exchange_code_for_tokens(
    config: OAuthConfig, 
    code: str, 
    verifier: str
) -> Dict[str, Any]:
    """Exchange authorization code for tokens.
    
    Args:
        config: OAuth configuration
        code: Authorization code from callback
        verifier: PKCE code verifier
    
    Returns:
        Token response with access_token, refresh_token, etc.
    
    Raises:
        HTTPException: If token exchange fails
    """
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.redirect_uri,
        'client_id': config.client_id,
        'code_verifier': verifier
    }
    
    # Add client_secret if not using PKCE-only flow
    if config.client_secret:
        token_data['client_secret'] = config.client_secret
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                config.token_endpoint,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to exchange code for tokens: {str(e)}"
            )


async def get_user_info(config: OAuthConfig, access_token: str) -> Dict[str, Any]:
    """Get user profile from OAuth provider.
    
    Args:
        config: OAuth configuration
        access_token: Access token from token exchange
    
    Returns:
        User profile dict with email, name, etc.
    
    Raises:
        HTTPException: If userinfo request fails
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                config.userinfo_endpoint,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user info: {str(e)}"
            )


async def revoke_token(config: OAuthConfig, token: str) -> None:
    """Revoke refresh token on logout (if provider supports it).
    
    Args:
        config: OAuth configuration
        token: Refresh token to revoke
    """
    # Only attempt if provider has revocation endpoint
    revocation_endpoint = os.getenv("OAUTH_REVOCATION_ENDPOINT")
    if not revocation_endpoint:
        return
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                revocation_endpoint,
                data={
                    'token': token,
                    'token_type_hint': 'refresh_token',
                    'client_id': config.client_id,
                    'client_secret': config.client_secret
                }
            )
        except httpx.HTTPError:
            # Non-critical failure, just log it
            pass


# Global OAuth config
oauth_config = OAuthConfig()
