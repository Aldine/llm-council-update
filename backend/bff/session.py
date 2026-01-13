"""Server-side session storage for BFF pattern.

In production, replace InMemorySessionStore with Redis or database storage.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Session:
    """Session data stored server-side."""
    session_id: str
    user: Dict[str, Any]
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    last_activity: datetime = field(default_factory=datetime.utcnow)


class InMemorySessionStore:
    """In-memory session storage for development.
    
    WARNING: This loses all sessions on restart. Use Redis for production.
    """
    
    def __init__(self, session_lifetime_hours: int = 24, idle_timeout_minutes: int = 60):
        self._sessions: Dict[str, Session] = {}
        self.session_lifetime = timedelta(hours=session_lifetime_hours)
        self.idle_timeout = timedelta(minutes=idle_timeout_minutes)
    
    def create_session(self, user: Dict[str, Any], access_token: Optional[str] = None, 
                      refresh_token: Optional[str] = None) -> Session:
        """Create a new session with opaque session ID."""
        session_id = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.session_lifetime,
            last_activity=datetime.utcnow()
        )
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session and update last activity."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Check expiry
        now = datetime.utcnow()
        if session.expires_at < now:
            self.delete_session(session_id)
            return None
        
        # Check idle timeout
        if now - session.last_activity > self.idle_timeout:
            self.delete_session(session_id)
            return None
        
        # Update activity
        session.last_activity = now
        return session
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        self._sessions.pop(session_id, None)
    
    def cleanup_expired(self) -> None:
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            sid for sid, session in self._sessions.items()
            if session.expires_at < now or (now - session.last_activity) > self.idle_timeout
        ]
        for sid in expired:
            self._sessions.pop(sid, None)


# Global session store (replace with Redis in production)
session_store = InMemorySessionStore()


# OAuth state storage (for PKCE and CSRF protection)
class OAuthStateStore:
    """Temporary storage for OAuth state and PKCE verifiers."""
    
    def __init__(self, state_lifetime_minutes: int = 10):
        self._states: Dict[str, Dict[str, Any]] = {}
        self.state_lifetime = timedelta(minutes=state_lifetime_minutes)
    
    def create_state(self, verifier: str) -> str:
        """Create OAuth state with PKCE verifier."""
        state = secrets.token_urlsafe(32)
        self._states[state] = {
            'verifier': verifier,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + self.state_lifetime
        }
        return state
    
    def verify_state(self, state: str) -> Optional[str]:
        """Verify state and return PKCE verifier, then delete."""
        data = self._states.get(state)
        if not data:
            return None
        
        # Check expiry
        if data['expires_at'] < datetime.utcnow():
            self._states.pop(state, None)
            return None
        
        # Remove state (one-time use)
        self._states.pop(state, None)
        return data['verifier']
    
    def cleanup_expired(self) -> None:
        """Remove expired states."""
        now = datetime.utcnow()
        expired = [
            state for state, data in self._states.items()
            if data['expires_at'] < now
        ]
        for state in expired:
            self._states.pop(state, None)


# Global OAuth state store
oauth_state_store = OAuthStateStore()
