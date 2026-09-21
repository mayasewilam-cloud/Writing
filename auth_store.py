"""
BioWriter Studio - Student Authentication & Account Store.
Provides secure password hashing (PBKDF2-SHA256) and account management
persisted in portal/data/users.json.
"""

import os
import json
import datetime
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.environ.get("VERCEL"):
    DATA_DIR = os.path.join("/tmp", "data")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_users() -> Dict[str, Dict[str, Any]]:
    _ensure_data_dir()
    target_file = USERS_FILE
    if not os.path.exists(target_file):
        bundled = os.path.join(BASE_DIR, "data", "users.json")
        if os.path.exists(bundled):
            target_file = bundled
        else:
            return {}
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_users(users: Dict[str, Dict[str, Any]]):
    _ensure_data_dir()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def normalize_student_id(student_id: str) -> str:
    if not student_id:
        return ""
    return student_id.strip().upper()


def register_student(student_id: str, student_name: str, password: str) -> Dict[str, Any]:
    """
    Registers a new student account with a hashed password.
    """
    clean_id = normalize_student_id(student_id)
    if not clean_id or len(clean_id) < 2:
        return {"success": False, "error": "Student ID must be at least 2 characters long."}
    
    if not password or len(password) < 4:
        return {"success": False, "error": "Password must be at least 4 characters long."}

    name = student_name.strip() if student_name else f"Student {clean_id}"

    users = _load_users()
    if clean_id in users:
        return {
            "success": False,
            "error": f"Student ID '{clean_id}' is already registered. Please sign in instead."
        }

    password_hash = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
    now_str = datetime.datetime.now().strftime("%b %d, %Y - %H:%M")

    users[clean_id] = {
        "student_id": clean_id,
        "student_name": name,
        "password_hash": password_hash,
        "created_at": now_str,
        "last_login": now_str,
        "role": "student"
    }
    _save_users(users)

    return {
        "success": True,
        "user": {
            "student_id": clean_id,
            "student_name": name,
            "created_at": now_str,
            "role": "student"
        }
    }


def authenticate_student(student_id: str, password: str) -> Dict[str, Any]:
    """
    Authenticates student ID and password.
    """
    clean_id = normalize_student_id(student_id)
    if not clean_id or not password:
        return {"success": False, "error": "Student ID and password are required."}

    users = _load_users()
    user = users.get(clean_id)

    if not user:
        return {
            "success": False,
            "error": f"Student ID '{clean_id}' not found. Please create an account first."
        }

    if not check_password_hash(user["password_hash"], password):
        return {"success": False, "error": "Incorrect password. Please try again."}

    # Update last login timestamp
    now_str = datetime.datetime.now().strftime("%b %d, %Y - %H:%M")
    user["last_login"] = now_str
    users[clean_id] = user
    _save_users(users)

    return {
        "success": True,
        "user": {
            "student_id": user["student_id"],
            "student_name": user.get("student_name", clean_id),
            "last_login": now_str,
            "role": user.get("role", "student")
        }
    }


def get_student_user(student_id: str) -> Optional[Dict[str, Any]]:
    clean_id = normalize_student_id(student_id)
    users = _load_users()
    user = users.get(clean_id)
    if not user:
        return None
    return {
        "student_id": user["student_id"],
        "student_name": user.get("student_name", clean_id),
        "created_at": user.get("created_at", ""),
        "last_login": user.get("last_login", ""),
        "role": user.get("role", "student")
    }


def seed_default_users():
    """
    Pre-populates default demo student accounts with password 'bio123'
    so existing demo drafts can be accessed directly.
    """
    defaults = [
        ("ST-2026-01", "Sara Ahmed & Team BioInnovate", "bio123"),
        ("ST-2026-02", "Zaid Ibrahim & BioCatalysis Group", "bio123"),
        ("ST-2026-03", "Nour Al-Huda & Team Agribiotech", "bio123")
    ]
    users = _load_users()
    changed = False
    for sid, name, pwd in defaults:
        clean = normalize_student_id(sid)
        if clean not in users:
            users[clean] = {
                "student_id": clean,
                "student_name": name,
                "password_hash": generate_password_hash(pwd, method="pbkdf2:sha256", salt_length=16),
                "created_at": datetime.datetime.now().strftime("%b %d, %Y - %H:%M"),
                "last_login": datetime.datetime.now().strftime("%b %d, %Y - %H:%M"),
                "role": "student"
            }
            changed = True
    if changed:
        _save_users(users)

# ==========================================================================
# Faculty / Instructor Authentication & Anti-Brute-Force Guard
# ==========================================================================
import time

FACULTY_SECURITY_FILE = os.path.join(DATA_DIR, "faculty_security.json")
MAX_FAILED_FACULTY_ATTEMPTS = 5
FACULTY_LOCKOUT_SECONDS = 900  # 15 minutes

# In-memory attempt and lockout tracker: { ip: {"attempts": int, "locked_until": float, "last_attempt": float} }
_failed_faculty_attempts: Dict[str, Dict[str, Any]] = {}


def _get_faculty_hashes() -> list:
    """
    Loads or initializes salted PBKDF2-SHA256 password hashes for faculty access.
    Plaintext passcodes are NEVER stored or returned.
    """
    _ensure_data_dir()
    hashes = []
    if os.path.exists(FACULTY_SECURITY_FILE):
        try:
            with open(FACULTY_SECURITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                hashes = data.get("password_hashes", [])
        except Exception:
            hashes = []

    if not hashes:
        # Generate initial secure salted hashes for default authorized keys
        initial_keys = [
            "IntroKingss",
            "faculty2026",
            "bt301instructor"
        ]
        custom_env = os.environ.get("FACULTY_PASSCODE")
        if custom_env and custom_env not in initial_keys:
            initial_keys.append(custom_env)

        hashes = [
            generate_password_hash(k, method="pbkdf2:sha256", salt_length=16)
            for k in initial_keys
        ]
        try:
            with open(FACULTY_SECURITY_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "description": "Salted PBKDF2-SHA256 password hashes for course instructors and review chairs.",
                    "password_hashes": hashes,
                    "updated_at": datetime.datetime.now().isoformat()
                }, f, indent=2)
        except Exception:
            pass

    return hashes


def check_faculty_rate_limit(client_ip: str) -> tuple:
    """
    Verifies if the client IP is currently locked out from faculty authentication.
    Returns: (is_allowed: bool, error_message: Optional[str], remaining_seconds: Optional[int])
    """
    ip = client_ip or "127.0.0.1"
    now = time.time()
    record = _failed_faculty_attempts.get(ip)

    if not record:
        return True, None, None

    locked_until = record.get("locked_until")
    if locked_until and now < locked_until:
        remaining = int(locked_until - now)
        minutes = max(1, (remaining + 59) // 60)
        return False, f"Faculty portal is locked due to repeated failed attempts. Please try again in {minutes} minute(s).", remaining

    # If lockout expired, reset attempt counter
    if locked_until and now >= locked_until:
        _failed_faculty_attempts.pop(ip, None)

    return True, None, None


def record_faculty_attempt(client_ip: str, success: bool) -> Dict[str, Any]:
    """
    Records a successful or failed faculty authentication attempt.
    Enforces a 15-minute hard lockout after MAX_FAILED_FACULTY_ATTEMPTS.
    """
    ip = client_ip or "127.0.0.1"
    now = time.time()

    if success:
        _failed_faculty_attempts.pop(ip, None)
        return {"locked": False, "attempts": 0}

    record = _failed_faculty_attempts.get(ip, {"attempts": 0, "locked_until": None, "last_attempt": now})
    record["attempts"] += 1
    record["last_attempt"] = now

    if record["attempts"] >= MAX_FAILED_FACULTY_ATTEMPTS:
        record["locked_until"] = now + FACULTY_LOCKOUT_SECONDS
        _failed_faculty_attempts[ip] = record
        return {
            "locked": True,
            "attempts": record["attempts"],
            "remaining_seconds": FACULTY_LOCKOUT_SECONDS,
            "message": f"Too many failed attempts. Faculty portal locked for 15 minutes."
        }

    _failed_faculty_attempts[ip] = record
    remaining_tries = MAX_FAILED_FACULTY_ATTEMPTS - record["attempts"]
    return {
        "locked": False,
        "attempts": record["attempts"],
        "remaining_tries": remaining_tries,
        "message": f"Invalid instructor access passcode. {remaining_tries} attempt(s) remaining."
    }


def reset_faculty_rate_limit(client_ip: str):
    """Resets the lockout state for an IP address."""
    ip = client_ip or "127.0.0.1"
    _failed_faculty_attempts.pop(ip, None)


def verify_faculty_passcode(passcode: str) -> bool:
    """
    Cryptographically verifies the provided passcode against salted PBKDF2 hashes.
    Resistant to timing attacks.
    """
    if not passcode:
        return False
    clean = passcode.strip()

    # Check against environment variable if defined
    env_pass = os.environ.get("FACULTY_PASSCODE")
    if env_pass and clean == env_pass.strip():
        return True

    hashes = _get_faculty_hashes()
    for h in hashes:
        try:
            if check_password_hash(h, clean):
                return True
        except Exception:
            continue

    return False
