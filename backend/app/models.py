from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from .database import Base

SCHEMA = "sbfo_ro"


class Entry(Base):
    __tablename__ = "entries"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_entry_id = Column(Integer, nullable=True, index=True)
    version = Column(Integer, nullable=False, default=1)

    creation_date = Column(String(20), nullable=False)
    creation_date_period = Column(String(5), nullable=True)
    creation_date_year = Column(String(4), nullable=True)
    add_to_forecast_by_period = Column(String(5), nullable=True)
    add_to_forecast_by_year = Column(String(4), nullable=True)

    division = Column(String(100), nullable=False)
    ibp_step = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)

    channel = Column(String(100), nullable=False)
    sub_channel = Column(String(100), nullable=False)
    account = Column(String(100), nullable=False)

    brand = Column(String(100), nullable=False)
    brand_family = Column(Text, nullable=True)

    r_and_o = Column(String(50), nullable=False)
    probability = Column(String(50), nullable=False)
    categorisation = Column(String(100), nullable=False)

    impact_period = Column(String(5), nullable=True)
    impact_year = Column(String(4), nullable=True)

    nsv_aud = Column(String(50), nullable=True)
    nsv_nzd = Column(String(50), nullable=True)
    volume_litres = Column(String(50), nullable=True)
    impact_type = Column(String(20), nullable=True)  # "NSV" | "OI"

    owner = Column(String(100), nullable=False)
    creator = Column(String(100), nullable=True)
    modified_user = Column(String(100), nullable=True)

    status = Column(String(50), nullable=True, default="Open")
    description = Column(Text, nullable=True)

    last_modified = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())


class ChildImpact(Base):
    __tablename__ = "child_impacts"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(
        Integer,
        ForeignKey(f"{SCHEMA}.entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    impact_year = Column(String(4), nullable=False)
    impact_period = Column(String(5), nullable=False)
    nsv_aud = Column(String(50), nullable=True)
    nsv_nzd = Column(String(50), nullable=True)
    volume_litres = Column(String(50), nullable=True)


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), nullable=False, unique=True)
    display_name = Column(String(100), nullable=True)
    role = Column(Integer, nullable=False)  # 0=System Admin, 1=User, 2=Department Approver, 3=Finance Approver
    departments = Column(JSON, nullable=True)  # None = all; ["Supply","Marketing"] = restricted
    is_active = Column(Boolean, default=True)


class LookupOption(Base):
    __tablename__ = "lookup_options"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False, index=True)
    value = Column(String(200), nullable=False)
    parent_category = Column(String(50), nullable=True)
    parent_value = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class Snapshot(Base):
    __tablename__ = "snapshots"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(5), nullable=False)
    year = Column(String(4), nullable=False)
    ibp_step = Column(String(100), nullable=False)
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    entry_count = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Boolean, default=False, nullable=False)


class SnapshotEntry(Base):
    __tablename__ = "snapshot_entries"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(
        Integer,
        ForeignKey(f"{SCHEMA}.snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entry_id = Column(Integer, ForeignKey(f"{SCHEMA}.entries.id"), nullable=False)
    original_entry_id = Column(Integer, nullable=True)
    version = Column(Integer, nullable=True)


