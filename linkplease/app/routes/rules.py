import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Rule
from app.schemas.rule import RuleCreate, RuleResponse


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/rules",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED
)
def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db)
):
    rule = Rule(
        id=str(uuid.uuid4()),
        keyword=rule_data.keyword,
        dm_message=rule_data.dm_message
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return RuleResponse(
        rule_id=rule.id,
        keyword=rule.keyword,
        dm_message=rule.dm_message
    )