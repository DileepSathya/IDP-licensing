from datetime import date, datetime, timedelta
from pathlib import Path

from database import db_connection
from keygen.license_generator import generate_license_file
from __init__ import get_logger

logger = get_logger(__name__)

CUSTOMERS_DIR = Path(__file__).resolve().parent.parent / "Customers"


def get_user_id_by_email(email: str) -> int:
    conn = db_connection.DatabaseConnection.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError("No account found with this email.")
        return row[0]
    finally:
        cursor.close()
        conn.close()


def _compute_expires_at(plan: str) -> str:
    today = date.today()
    if plan == "monthly":
        return (today + timedelta(days=30)).isoformat()
    if plan == "yearly":
        return (today + timedelta(days=365)).isoformat()
    return "2099-12-31"


def _build_output_path(user_id: int) -> Path:
    user_dir = CUSTOMERS_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return user_dir / f"license_{timestamp}.lic"


def _save_license_record(
    *,
    email: str,
    fingerprint_id: str,
    plan: str,
    quota: int | None,
    expires_at: str,
    license_file_path: Path,
) -> None:
    conn = db_connection.DatabaseConnection.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO clients_licenses
                (email, fingerprint_id, plan, expiry_date, quota, license_file_path)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """,
            (
                email,
                fingerprint_id.strip().lower(),
                plan,
                expires_at,
                quota if plan == "quota" else None,
                str(license_file_path.resolve()),
            ),
        )
        conn.commit()
        logger.info("License record saved to database")
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def create_user_license(
    *,
    user_id: int,
    email: str,
    fingerprint_id: str,
    plan: str,
    quota: int | None = None,
) -> tuple[dict, Path]:
    if not fingerprint_id or not fingerprint_id.strip():
        raise ValueError("Fingerprint ID is required.")

    plan = plan.strip().lower()
    invoice_limit = 0
    if plan == "quota":
        if quota is None or quota <= 0:
            raise ValueError("Invoice count must be greater than 0 for quota plan.")
        invoice_limit = int(quota)

    expires_at = _compute_expires_at(plan)
    output_path = _build_output_path(user_id)

    payload, out_path = generate_license_file(
        customer_id=str(user_id),
        fingerprint=fingerprint_id,
        plan=plan,
        invoice_limit=invoice_limit,
        expires_at=expires_at,
        output=str(output_path),
    )

    _save_license_record(
        email=email,
        fingerprint_id=fingerprint_id,
        plan=plan,
        quota=invoice_limit if plan == "quota" else None,
        expires_at=payload["expiresAt"],
        license_file_path=out_path,
    )

    logger.info(f"License created for user {user_id} at {out_path}")
    return payload, out_path


def get_user_profile(user_id: int) -> dict:
    """
    Returns a dict with:
      - fname: str
      - plan: str | None        (monthly / yearly / quota / onetime or None)
      - expiry_date: date | None
      - quota: int | None
      - is_active: bool
    """
    conn = db_connection.DatabaseConnection.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT f_name FROM users WHERE user_id = %s;", (user_id,))
        user_row = cursor.fetchone()
        fname = user_row[0] if user_row else ""

        cursor.execute(
            """
            SELECT plan, expiry_date, quota
            FROM clients_licenses
            WHERE email = (SELECT email FROM users WHERE user_id = %s)
            ORDER BY issue_date DESC
            LIMIT 1
            """,
            (user_id,),
        )
        lic_row = cursor.fetchone()

        if lic_row is None:
            return {"fname": fname, "plan": None, "expiry_date": None, "quota": None, "is_active": False}

        plan, expiry_date, quota = lic_row

        if isinstance(expiry_date, str):
            expiry_date = date.fromisoformat(expiry_date)
        elif isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()

        is_active = expiry_date >= date.today() if expiry_date else False

        return {
            "fname": fname,
            "plan": plan,
            "expiry_date": expiry_date,
            "quota": quota,
            "is_active": is_active,
        }
    finally:
        cursor.close()
        conn.close()


def latest_license_retrival(email: str) -> Path:
    conn = db_connection.DatabaseConnection.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT license_file_path
            FROM clients_licenses
            WHERE email = %s
            ORDER BY issue_date DESC
            LIMIT 1
            """,
            (email,),
        )
        row = cursor.fetchone()
        if row is None or not row[0]:
            raise ValueError("No licence found for this account. Generate one first.")
        return Path(row[0])
    finally:
        cursor.close()
        conn.close()
