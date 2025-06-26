# shared/session.py
import json
import os

SESSION_FILE = "shared/session_store.json"

def save_session(session_id, data):
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            sessions = json.load(f)
    else:
        sessions = {}

    sessions[session_id] = data

    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def load_session(session_id):
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        sessions = json.load(f)
    return sessions.get(session_id)
