"""In-memory session store for BFF authentication."""
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

class SessionStore:
    """Simple in-memory session storage. Use Redis in production."""
    
    def __init__(self, session_timeout_minutes: int = 60):
        self._sessions: Dict[str, dict] = {}
        self._session_timeout = timedelta(minutes=session_timeout_minutes)
    
    def create_session(self, user_data: dict, access_token: str, refresh_token: Optional[str] = None) -> str:
        """Create a new session and return session ID."""
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = {
            "user": user_data,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session by ID, return None if expired or not found."""
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        # Check if expired
        if datetime.utcnow() - session["last_accessed"] > self._session_timeout:
            self.delete_session(session_id)
            return None
        
        # Update last accessed
        session["last_accessed"] = datetime.utcnow()
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        self._sessions.pop(session_id, None)
    
    def cleanup_expired(self):
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session["last_accessed"] > self._session_timeout
        ]
        for sid in expired:
            self.delete_session(sid)

# Global session store instance
session_store = SessionStore()
