import re
import os
from typing import Optional


def sanitize_filename(filename: str) -> str:
    """
    Strips dangerous characters, path traversal elements, and limits length.
    """
    base = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    return clean[:120]


def validate_indian_phone_number(phone: str) -> bool:
    """
    Validates standard 10-digit Indian mobile number format.
    """
    clean_phone = re.sub(r"[\s\-\+\(\)]", "", phone)
    if clean_phone.startswith("91") and len(clean_phone) == 12:
        clean_phone = clean_phone[2:]
    return bool(re.match(r"^[6-9]\d{9}$", clean_phone))
