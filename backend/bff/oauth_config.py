"""OAuth configuration for BFF pattern."""
import os

class OAuthConfig:
    """OAuth provider configuration."""
    
    def __init__(self):
        self.issuer = os.getenv("OAUTH_ISSUER", "")
        self.client_id = os.getenv("OAUTH_CLIENT_ID", "")
        self.client_secret = os.getenv("OAUTH_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8002/bff/auth/callback")
        self.scopes = os.getenv("OAUTH_SCOPES", "openid profile email").split()
        self.app_base_url = os.getenv("APP_BASE_URL", "http://localhost:5173")
        
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured."""
        return bool(self.issuer and self.client_id and self.client_secret)

oauth_config = OAuthConfig()
