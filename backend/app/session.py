import time
import secrets
from typing import Optional
from app.config import ENV


class SessionStore:
    """In-memory session store. In production, use Redis."""

    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._key_sessions: dict[str, dict] = {}

    def create_session(self) -> str:
        """Create a new session and return the token."""
        token = secrets.token_hex(32)
        self._sessions[token] = {
            'created_at': time.time(),
            'expires_at': time.time() + 3600,  # 1 hour
            'locked': False,
        }
        return token

    def validate_session(self, token: str) -> bool:
        """Check if a session token is valid."""
        if token not in self._sessions:
            return False
        session = self._sessions[token]
        if session['expires_at'] < time.time() or session['locked']:
            return False
        return True

    def get_session(self, token: str) -> Optional[dict]:
        """Get session data. Returns None if invalid."""
        if not self.validate_session(token):
            return None
        return self._sessions[token]

    def store_key(self, token: str, key: bytes, expires_at: float):
        """Store the AES key for a session."""
        self._key_sessions[token] = {
            'key': key,
            'expires_at': expires_at,
        }

    def get_key(self, token: str) -> Optional[bytes]:
        """Get the AES key for a session. Returns None if expired or not found."""
        if token not in self._key_sessions:
            return None
        key_data = self._key_sessions[token]
        if key_data['expires_at'] < time.time():
            del self._key_sessions[token]
            return None
        return key_data['key']

    def delete_key(self, token: str):
        """Delete the AES key for a session (lock)."""
        self._key_sessions.pop(token, None)

    def lock(self, token: str):
        """Lock the session."""
        if token in self._sessions:
            self._sessions[token]['locked'] = True
        self.delete_key(token)

    def cleanup_expired(self):
        """Remove expired sessions and keys."""
        now = time.time()
        expired_tokens = [t for t, s in self._sessions.items() if s['expires_at'] < now]
        for token in expired_tokens:
            self._sessions.pop(token, None)
            self._key_sessions.pop(token, None)


# Global session store instance
session_store = SessionStore()