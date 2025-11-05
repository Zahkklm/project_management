from app.core.database import Base, engine, get_db


def test_get_db():
    """Test database session generator"""
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    db_gen.close()


def test_engine_exists():
    """Test database engine exists"""
    assert engine is not None


def test_base_exists():
    """Test SQLAlchemy Base exists"""
    assert Base is not None
