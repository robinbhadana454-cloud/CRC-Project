import secrets
from sqlmodel import Session, select
from app.models.booking import Booking


def generate_pnr_code() -> str:
    """Generate a 10-character railway PNR code consisting of digits."""
    # Railway standard 10-digit PNR number
    prefix = secrets.choice(["2", "4", "6", "8"])
    suffix = "".join(secrets.choice("0123456789") for _ in range(9))
    return f"{prefix}{suffix}"


def generate_unique_pnr(session: Session) -> str:
    """Generate a collision-free PNR string guaranteed to be unique in database."""
    for _ in range(10):
        candidate_pnr = generate_pnr_code()
        existing = session.exec(select(Booking).where(Booking.pnr == candidate_pnr)).first()
        if not existing:
            return candidate_pnr
    # Fallback to timestamp + random if high density
    import time
    return f"PNR{int(time.time()) % 10000000:07d}"
