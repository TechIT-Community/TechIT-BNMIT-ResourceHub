import streamlit as st
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# --- DATABASE CONFIG ---
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:admin@localhost/demodb'
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- RESOURCE MODEL ---
class Resource(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    subject = Column(Text)
    semester = Column(Text)
    department = Column(Text)
    type = Column(Text)
    source = Column(Text)
    link = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

# Create tables (if not already)
Base.metadata.create_all(bind=engine)

# --- STREAMLIT UI ---
st.title("📚 TechIT ResourceHub")

if st.button("▶️ Run GitHub Scanner"):
    import github_scanner  # Make sure this uses the same Resource model and session
    st.success("✅ GitHub scanner completed!")

if st.button("▶️ Run Google Drive Scanner"):
    import drive_scanner  # Same here
    st.success("✅ Drive scanner completed!")

# Search UI
st.subheader("🔍 Search Resources")
query = st.text_input("Enter keyword:")
if query:
    session = SessionLocal()
    results = session.query(Resource).filter(Resource.title.ilike(f"%{query}%")).all()
    for r in results:
        st.write(f"📄 [{r.title}]({r.link}) — {r.subject}, {r.semester}, {r.department}")
    session.close()
