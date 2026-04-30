from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas


def get_latest_entries(db: Session, filters: dict = None, include_deleted: bool = False, department_in: list = None):
    """Return latest version of each entry (max version per original_entry_id)."""
    subq = (
        db.query(
            models.Entry.original_entry_id,
            func.max(models.Entry.version).label("max_ver"),
        )
        .group_by(models.Entry.original_entry_id)
        .subquery()
    )
    query = db.query(models.Entry).join(
        subq,
        (models.Entry.original_entry_id == subq.c.original_entry_id)
        & (models.Entry.version == subq.c.max_ver),
    )
    if not include_deleted:
        query = query.filter(models.Entry.status != "Deleted")
    if filters:
        for field, value in filters.items():
            if value:
                query = query.filter(getattr(models.Entry, field) == value)
    # Department Approver restriction: filter by allowed departments
    if department_in:
        query = query.filter(models.Entry.ibp_step.in_(department_in))
    return query.order_by(models.Entry.last_modified.desc()).all()


def get_entry_by_id(db: Session, entry_id: int):
    return db.query(models.Entry).filter(models.Entry.id == entry_id).first()


def get_entry_history(db: Session, original_entry_id: int):
    return (
        db.query(models.Entry)
        .filter(models.Entry.original_entry_id == original_entry_id)
        .order_by(models.Entry.version.desc())
        .all()
    )


def get_child_impacts(db: Session, entry_id: int):
    return db.query(models.ChildImpact).filter(models.ChildImpact.entry_id == entry_id).all()


def create_entry(db: Session, data: schemas.EntryCreate):
    child_impacts_data = data.child_impacts or []
    entry_data = data.model_dump(exclude={"child_impacts"})
    entry = models.Entry(**entry_data, version=1)
    db.add(entry)
    db.flush()
    entry.original_entry_id = entry.id
    for ci in child_impacts_data:
        child = models.ChildImpact(entry_id=entry.id, **ci.model_dump())
        db.add(child)
    db.commit()
    db.refresh(entry)
    return entry


def _get_max_version(db: Session, original_entry_id: int) -> int:
    return db.query(func.max(models.Entry.version)).filter(
        models.Entry.original_entry_id == original_entry_id
    ).scalar() or 0


def update_entry(db: Session, entry_id: int, data: schemas.EntryUpdate):
    current = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not current:
        return None

    max_version = _get_max_version(db, current.original_entry_id)

    child_impacts_data = data.child_impacts or []
    entry_data = data.model_dump(exclude={"child_impacts"})

    new_entry = models.Entry(
        original_entry_id=current.original_entry_id,
        version=max_version + 1,
        creator=current.creator,
        **entry_data,
    )
    db.add(new_entry)
    db.flush()
    for ci in child_impacts_data:
        child = models.ChildImpact(entry_id=new_entry.id, **ci.model_dump())
        db.add(child)
    db.commit()
    db.refresh(new_entry)
    return new_entry


def delete_entry(db: Session, entry_id: int, modified_user: str = None):
    """Soft delete: create a new version with status='Deleted'."""
    result = _new_version_with_status(db, entry_id, "Deleted", modified_user)
    return result is not None


def _new_version_with_status(db: Session, entry_id: int, new_status: str, modified_user: str = None):
    """Create a new version of an entry with only the status changed."""
    current = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not current:
        return None

    max_version = _get_max_version(db, current.original_entry_id)

    new_entry = models.Entry(
        original_entry_id=current.original_entry_id,
        version=max_version + 1,
        creation_date=current.creation_date,
        creation_date_period=current.creation_date_period,
        creation_date_year=current.creation_date_year,
        add_to_forecast_by_period=current.add_to_forecast_by_period,
        add_to_forecast_by_year=current.add_to_forecast_by_year,
        division=current.division,
        ibp_step=current.ibp_step,
        country=current.country,
        channel=current.channel,
        sub_channel=current.sub_channel,
        account=current.account,
        brand=current.brand,
        brand_family=current.brand_family,
        r_and_o=current.r_and_o,
        probability=current.probability,
        categorisation=current.categorisation,
        impact_period=current.impact_period,
        impact_year=current.impact_year,
        nsv_aud=current.nsv_aud,
        nsv_nzd=current.nsv_nzd,
        volume_litres=current.volume_litres,
        impact_type=current.impact_type,
        owner=current.owner,
        creator=current.creator,
        description=current.description,
        status=new_status,
        modified_user=modified_user,
    )
    db.add(new_entry)
    db.flush()

    for ci in db.query(models.ChildImpact).filter(models.ChildImpact.entry_id == current.id).all():
        db.add(models.ChildImpact(
            entry_id=new_entry.id,
            impact_year=ci.impact_year,
            impact_period=ci.impact_period,
            nsv_aud=ci.nsv_aud,
            nsv_nzd=ci.nsv_nzd,
            volume_litres=ci.volume_litres,
        ))

    db.commit()
    db.refresh(new_entry)
    return new_entry


def update_entry_status(db: Session, entry_id: int, new_status: str, modified_user: str = None):
    return _new_version_with_status(db, entry_id, new_status, modified_user)


def approve_entry(db: Session, entry_id: int, modified_user: str = None):
    return _new_version_with_status(db, entry_id, "Approved", modified_user)


def get_lookup_options(db: Session, category: str, parent_value: str = None):
    q = db.query(models.LookupOption).filter(
        models.LookupOption.category == category,
        models.LookupOption.is_active == True,
    )
    if parent_value:
        q = q.filter(models.LookupOption.parent_value == parent_value)
    else:
        q = q.filter(models.LookupOption.parent_value == None)
    return q.order_by(models.LookupOption.sort_order, models.LookupOption.value).all()


def get_all_users(db: Session):
    return (
        db.query(models.AppUser)
        .filter(models.AppUser.is_active == True)
        .order_by(models.AppUser.email)
        .all()
    )

