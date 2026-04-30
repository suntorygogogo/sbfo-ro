from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from ..database import get_db
from .. import models

router = APIRouter()


def _get_latest_entries_for_ibp_step(db: Session, ibp_step: str) -> list:
    """Return latest non-deleted versions of all entries with the given ibp_step."""
    subq = (
        db.query(
            models.Entry.original_entry_id,
            func.max(models.Entry.version).label("max_ver"),
        )
        .group_by(models.Entry.original_entry_id)
        .subquery()
    )
    return (
        db.query(models.Entry)
        .join(
            subq,
            (models.Entry.original_entry_id == subq.c.original_entry_id)
            & (models.Entry.version == subq.c.max_ver),
        )
        .filter(models.Entry.ibp_step == ibp_step)
        .filter(models.Entry.status != "Deleted")
        .all()
    )


def _entry_dict(entry, child_impacts) -> dict:
    return {
        "id": entry.id,
        "originalEntryId": entry.original_entry_id,
        "version": entry.version,
        "creationDate": entry.creation_date,
        "creationDatePeriod": entry.creation_date_period,
        "creationDateYear": entry.creation_date_year,
        "addToForecastByPeriod": entry.add_to_forecast_by_period,
        "addToForecastByYear": entry.add_to_forecast_by_year,
        "division": entry.division,
        "ibpStep": entry.ibp_step,
        "country": entry.country,
        "channel": entry.channel,
        "subChannel": entry.sub_channel,
        "account": entry.account,
        "brand": entry.brand,
        "brandFamily": entry.brand_family,
        "rAndO": entry.r_and_o,
        "probability": entry.probability,
        "categorisation": entry.categorisation,
        "impactPeriod": entry.impact_period,
        "impactYear": entry.impact_year,
        "nsvAud": entry.nsv_aud,
        "nsvNzd": entry.nsv_nzd,
        "volumeLitres": entry.volume_litres,
        "impactType": entry.impact_type,
        "owner": entry.owner,
        "creator": entry.creator,
        "modifiedUser": entry.modified_user,
        "status": entry.status,
        "description": entry.description,
        "lastModified": entry.last_modified.isoformat() + "Z" if entry.last_modified else None,
        "childImpacts": [
            {
                "id": ci.id,
                "impactYear": ci.impact_year,
                "impactPeriod": ci.impact_period,
                "nsvAud": ci.nsv_aud,
                "nsvNzd": ci.nsv_nzd,
                "volumeLitres": ci.volume_litres,
            }
            for ci in child_impacts
        ],
    }


def _snapshot_dict(s: models.Snapshot) -> dict:
    return {
        "id": s.id,
        "period": s.period,
        "year": s.year,
        "ibpStep": s.ibp_step,
        "createdBy": s.created_by,
        "createdAt": s.created_at.isoformat() + "Z" if s.created_at else None,
        "entryCount": s.entry_count,
    }


@router.get("/count")
def preview_count(ibp_step: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Return how many entries would be captured for the given ibp_step."""
    if not ibp_step:
        return {"count": 0}
    entries = _get_latest_entries_for_ibp_step(db, ibp_step)
    return {"count": len(entries)}


@router.post("")
def create_snapshot(
    period: str = Query(...),
    year: str = Query(...),
    ibp_step: str = Query(...),
    created_by: str = Query(...),
    db: Session = Depends(get_db),
):
    entries = _get_latest_entries_for_ibp_step(db, ibp_step)

    snapshot = models.Snapshot(
        period=period,
        year=year,
        ibp_step=ibp_step,
        created_by=created_by,
        entry_count=len(entries),
    )
    db.add(snapshot)
    db.flush()

    for entry in entries:
        db.add(
            models.SnapshotEntry(
                snapshot_id=snapshot.id,
                entry_id=entry.id,
                original_entry_id=entry.original_entry_id,
                version=entry.version,
            )
        )

    db.commit()
    db.refresh(snapshot)
    return _snapshot_dict(snapshot)


@router.get("")
def list_snapshots(db: Session = Depends(get_db)):
    snapshots = (
        db.query(models.Snapshot)
        .filter(models.Snapshot.is_deleted == False)
        .order_by(models.Snapshot.created_at.desc())
        .all()
    )
    return {"snapshots": [_snapshot_dict(s) for s in snapshots]}


@router.delete("/{snapshot_id}")
def delete_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(models.Snapshot).filter(models.Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    snapshot.is_deleted = True
    db.commit()
    return {"success": True}


@router.get("/{snapshot_id}/entries")
def get_snapshot_entries(snapshot_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(models.Snapshot).filter(models.Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    snapshot_entry_rows = (
        db.query(models.SnapshotEntry)
        .filter(models.SnapshotEntry.snapshot_id == snapshot_id)
        .all()
    )

    result = []
    for se in snapshot_entry_rows:
        entry = db.query(models.Entry).filter(models.Entry.id == se.entry_id).first()
        if entry:
            child_impacts = (
                db.query(models.ChildImpact)
                .filter(models.ChildImpact.entry_id == entry.id)
                .all()
            )
            result.append(_entry_dict(entry, child_impacts))

    return {"snapshot": _snapshot_dict(snapshot), "entries": result}
