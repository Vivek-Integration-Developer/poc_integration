from datetime import datetime

def now_readable() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

def iso_datetime() -> str:
    return datetime.now().isoformat()
