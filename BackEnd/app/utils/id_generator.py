import uuid

def generate_id(prefix=""):
    """Generate a unique ID with optional prefix"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"
