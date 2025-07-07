from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime

# 🛢️ Database configuration
DATABASE_URL = "postgresql://postgres:admin@localhost/demodb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Base class
Base = declarative_base()

# 📄 Resource model
class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    subject = Column(Text)
    semester = Column(Text)
    department = Column(Text)
    type = Column(Text)
    source = Column(Text)
    link = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    search_vector = Column(TSVECTOR)
    is_folder = Column(Boolean, default=False)  # ✅ NEW COLUMN

# ⬇️ Add this at the end of db.py

def get_all_metadata():
    session = SessionLocal()
    try:
        departments = sorted(set(r.department for r in session.query(Resource).filter(Resource.department.isnot(None))))
        semesters = sorted(set(r.semester for r in session.query(Resource).filter(Resource.semester.isnot(None))))
        subjects = sorted(set(r.subject for r in session.query(Resource).filter(Resource.subject.isnot(None))))
        return departments, semesters, subjects
    finally:
        session.close()

