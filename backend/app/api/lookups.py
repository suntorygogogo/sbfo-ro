from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import crud

router = APIRouter()


@router.get("")
def get_lookup_options(
    category: str = Query(..., description="Lookup category, e.g. 'channel', 'sub_channel'"),
    parent_value: Optional[str] = Query(None, description="Parent value for cascade filtering"),
    db: Session = Depends(get_db),
):
    rows = crud.get_lookup_options(db, category, parent_value)
    return {"options": [{"value": r.value, "label": r.value} for r in rows]}
