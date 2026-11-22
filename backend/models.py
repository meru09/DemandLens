
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    memberships: Mapped[list["BusinessMember"]] = relationship(
        back_populates="user"
    )


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    memberships: Mapped[list["BusinessMember"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
    )
    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
    )


class BusinessMember(Base):
    __tablename__ = "business_members"

    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'member')",
            name="check_business_member_role",
        ),
    )

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(20), default="member", nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="memberships")
    business: Mapped["Business"] = relationship(
        back_populates="memberships"
    )


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="uploaded", nullable=False
    )
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_column: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    product_column: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    quantity_column: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    business: Mapped["Business"] = relationship(back_populates="datasets")
