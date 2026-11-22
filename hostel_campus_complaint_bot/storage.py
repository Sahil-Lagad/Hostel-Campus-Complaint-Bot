from pathlib import Path
from datetime import datetime
import uuid
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = DATA_DIR / "complaints.csv"
COLUMNS = [
    "complaint_id", "created_at", "student_name", "room_number", "contact",
    "complaint_text", "category", "urgency", "summary", "status", "ai_used"
]

def load_complaints() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(CSV_PATH, dtype={"complaint_id": str})
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    except (pd.errors.EmptyDataError, OSError):
        return pd.DataFrame(columns=COLUMNS)

def add_complaint(**kwargs) -> dict:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    complaint_id = f"CMP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    record = {
        "complaint_id": complaint_id,
        "created_at": now,
        "student_name": kwargs.get("student_name", ""),
        "room_number": kwargs.get("room_number", ""),
        "contact": kwargs.get("contact", ""),
        "complaint_text": kwargs.get("complaint_text", ""),
        "category": kwargs.get("category", "Other"),
        "urgency": kwargs.get("urgency", "Medium"),
        "summary": kwargs.get("summary", ""),
        "status": "Submitted",
        "ai_used": bool(kwargs.get("ai_used", False)),
    }
    df = load_complaints()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    return record

def update_status(complaint_id: str, status: str) -> bool:
    allowed = {"Submitted", "In Progress", "Resolved", "Rejected"}
    if status not in allowed or not CSV_PATH.exists():
        return False
    df = load_complaints()
    mask = df["complaint_id"] == complaint_id
    if not mask.any():
        return False
    df.loc[mask, "status"] = status
    df.to_csv(CSV_PATH, index=False)
    return True

def export_csv() -> bytes:
    df = load_complaints()
    return df.to_csv(index=False).encode("utf-8")
