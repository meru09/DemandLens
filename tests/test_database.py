
import pytest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.models import User, Business, BusinessMember, Dataset


@pytest.fixture
def db_session():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_create_user(db_session):
    user = User(
        email="owner@example.com",
        password_hash="hashed_password",
    )

    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "owner@example.com"


def test_create_business(db_session):
    business = Business(business_name="Test Store")

    db_session.add(business)
    db_session.commit()

    assert business.id is not None
    assert business.business_name == "Test Store"


def test_assign_user_as_business_owner(db_session):
    user = User(
        email="owner@example.com",
        password_hash="hashed_password",
    )
    business = Business(business_name="Test Store")

    db_session.add_all([user, business])
    db_session.commit()

    membership = BusinessMember(
        user_id=user.id,
        business_id=business.id,
        role="owner",
    )

    db_session.add(membership)
    db_session.commit()

    assert membership.role == "owner"
    assert membership.user.email == "owner@example.com"
    assert membership.business.business_name == "Test Store"


def test_attach_dataset_to_business(db_session):
    business = Business(business_name="Test Store")

    db_session.add(business)
    db_session.commit()

    dataset = Dataset(
        business_id=business.id,
        original_filename="sales.csv",
        file_path="uploads/sales.csv",
        status="uploaded",
    )

    db_session.add(dataset)
    db_session.commit()

    assert dataset.id is not None
    assert dataset.business.business_name == "Test Store"
    assert dataset.original_filename == "sales.csv"


def test_user_can_belong_to_multiple_businesses(db_session):
    user = User(
        email="owner@example.com",
        password_hash="hashed_password",
    )
    business_one = Business(business_name="Store One")
    business_two = Business(business_name="Store Two")

    db_session.add_all([user, business_one, business_two])
    db_session.commit()

    db_session.add_all([
        BusinessMember(
            user_id=user.id,
            business_id=business_one.id,
            role="owner",
        ),
        BusinessMember(
            user_id=user.id,
            business_id=business_two.id,
            role="member",
        ),
    ])

    db_session.commit()

    assert len(user.memberships) == 2


def test_duplicate_business_membership_is_rejected(db_session):
    user = User(
        email="owner@example.com",
        password_hash="hashed_password",
    )
    business = Business(business_name="Test Store")

    db_session.add_all([user, business])
    db_session.commit()

    membership = BusinessMember(
        user_id=user.id,
        business_id=business.id,
        role="owner",
    )

    db_session.add(membership)
    db_session.commit()

    # Remove the existing object from the session identity map
    # before testing the duplicate primary key.
    db_session.expunge(membership)

    duplicate = BusinessMember(
        user_id=user.id,
        business_id=business.id,
        role="member",
    )

    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_invalid_business_role_is_rejected(db_session):
    user = User(
        email="owner@example.com",
        password_hash="hashed_password",
    )
    business = Business(business_name="Test Store")

    db_session.add_all([user, business])
    db_session.commit()

    membership = BusinessMember(
        user_id=user.id,
        business_id=business.id,
        role="admin",
    )

    db_session.add(membership)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
