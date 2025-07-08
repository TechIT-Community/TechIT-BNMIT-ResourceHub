import os
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime

# ✅ Use st.secrets when running inside Streamlit
try:
    import streamlit as st
    DATABASE_URL = st.secrets["DB_URL"]
    print("Database URL in use : ", DATABASE_URL)
except:
    # ✅ Use .env or fallback for local scripts like drive_scanner/github_scanner
    DATABASE_URL = os.getenv("DB_URL", "postgresql://postgres:admin@localhost/demodb")

# 🛢️ Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Base class for model definitions
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
    is_folder = Column(Boolean, default=False)

# 🔍 Metadata utility
def get_all_metadata():
    session = SessionLocal()
    try:
        departments = sorted(set(r.department for r in session.query(Resource).filter(Resource.department.isnot(None))))
        semesters = sorted(set(r.semester for r in session.query(Resource).filter(Resource.semester.isnot(None))))
        subjects = sorted(set(r.subject for r in session.query(Resource).filter(Resource.subject.isnot(None))))
        return departments, semesters, subjects
    finally:
        session.close()

# 🛠️ (Optional) create tables if running this directly
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")
