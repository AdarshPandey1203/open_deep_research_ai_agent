import json
import os
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Memory:
    def __init__(self, session_id, storage_path=None):
        self.session_id = str(session_id)
        
        # Determine robust storage path
        if storage_path:
            self.storage_path = storage_path
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.storage_path = os.path.join(base_dir, 'sessions')

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

        self.history = []
        self.load_history()

    def add_message(self, role: str, content):
        """Appends a message to the session history and persists to disk."""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        self.history.append(message)
        self.save_history()

    def get_history(self):
        """Returns the full chronological conversation history."""
        return self.history

    def get_title(self) -> str:
        """Derives a human-readable title from the first user message."""
        for msg in self.history:
            if msg.get('role') == 'user':
                raw = msg.get('content', '')
                if isinstance(raw, dict):
                    raw = raw.get('body', '')
                raw = str(raw).strip()
                # Remove file upload prefix if present
                clean = re.sub(r'I have uploaded a file[^\n]*\n*', '', raw).strip()
                clean = re.sub(r'https?://[^\s]+', '', clean).strip()
                if clean:
                    return clean[:35] + ("..." if len(clean) > 35 else "")
        return f"Research #{self.session_id}"

    def load_history(self):
        session_file = os.path.join(self.storage_path, f"{self.session_id}.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading session {self.session_id}: {e}")
                self.history = []

    def save_history(self):
        session_file = os.path.join(self.storage_path, f"{self.session_id}.json")
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving session {self.session_id}: {e}")

    def clear_history(self):
        self.history = []
        session_file = os.path.join(self.storage_path, f"{self.session_id}.json")
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except Exception as e:
                logger.error(f"Error deleting session file: {e}")
