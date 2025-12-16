import uuid
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.accounting_service.models import Ledger

DEFAULT_LEDGERS = [
    {"name": "Sales", "ledger_type": "SALES"},
    {"name": "Output CGST", "ledger_type": "TAX"},
    {"name": "Output SGST", "ledger_type": "TAX"},
    {"name": "Output IGST", "ledger_type": "TAX"},
]


def seed_ledgers():
    db: Session = SessionLocal()
    try:
        for ledger_data in DEFAULT_LEDGERS:
            exists = db.query(Ledger).filter(
                Ledger.name == ledger_data["name"]
            ).first()

            if not exists:
                ledger = Ledger(
                    id=uuid.uuid4(),
                    name=ledger_data["name"],
                    ledger_type=ledger_data["ledger_type"],
                )
                db.add(ledger)

        db.commit()
        print("✅ Default ledgers seeded successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed_ledgers()
