# -----------------------------
# app1.py (Streamlit App)
# -----------------------------
import streamlit as st
from db import SessionLocal, Resource
from sqlalchemy import func, or_
from datetime import datetime
from github_scanner import run_github_sync
from drive_scanner import run_drive_sync

st.set_page_config(page_title="TechIT ResourceHub", layout="wide")

# 🎯 Title
st.title("📚 TechIT ResourceHub")
st.markdown("Search, sort, and filter all files and folders across GitHub and Google Drive.")

# 📊 Resource Counter
session = SessionLocal()
total_count = session.query(Resource).count()
st.markdown(f"### 📦 Total Resources Indexed: `{total_count}`")
session.close()

# 🔁 Sync buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Sync GitHub"):
        run_github_sync()
        st.success("✅ GitHub sync completed.")

with col2:
    if st.button("🔄 Sync Google Drive"):
        run_drive_sync()
        st.success("✅ Google Drive sync completed.")

st.markdown("---")

# 🔍 Search Bar
query = st.text_input("🔎 Search", placeholder="Enter keyword (e.g., Regression, Semester4)")

# 🔽 Filters
col1, col2, col3, col4 = st.columns(4)
with col1:
    dept_filter = st.selectbox("Department", ["All", "CSE", "ISE", "ECE", "ME", "CIV", "AI/ML"])
with col2:
    sem_filter = st.selectbox("Semester", ["All", "Semester1", "Semester2", "Semester3", "Semester4", "Semester5", "Semester6", "Semester7", "Semester8"])
with col3:
    type_filter = st.selectbox("Type", ["All", "notes", "lab", "question-paper", "assignment", "misc", "folder"])
with col4:
    show_filter = st.selectbox("Show", ["Everything", "Files only", "Folders only"])

# 🔃 Sorting
col1, col2 = st.columns([2, 1])
with col1:
    sort_field = st.selectbox("Sort By", ["Date Added", "Title"])
with col2:
    sort_order = st.radio("Order", ["Newest First", "Oldest First"], horizontal=True)

# 🔎 Query logic
def get_filtered_results(query, filters, sort_field, sort_order, show_folders):
    session = SessionLocal()
    base_query = session.query(Resource)

    # Hybrid Search: tsvector first, fallback to ILIKE
    if query:
        tsquery = func.plainto_tsquery(query)
        results = base_query.filter(Resource.search_vector.op('@@')(tsquery))

        if results.count() == 0:
            pattern = f"%{query}%"
            results = base_query.filter(
                or_(
                    Resource.title.ilike(pattern),
                    Resource.subject.ilike(pattern),
                    Resource.semester.ilike(pattern),
                    Resource.department.ilike(pattern)
                )
            )
    else:
        results = base_query

    # Filters
    if filters["department"] != "All":
        results = results.filter(Resource.department.ilike(filters["department"]))
    if filters["semester"] != "All":
        results = results.filter(Resource.semester.ilike(filters["semester"]))
    if filters["type"] != "All":
        results = results.filter(Resource.type.ilike(filters["type"]))

    if filters["show"] == "Files only":
        results = results.filter(Resource.type != "folder")
    elif filters["show"] == "Folders only":
        results = results.filter(Resource.type == "folder")

    # Sorting
    if sort_field == "Title":
        sort_col = Resource.title
    else:
        sort_col = Resource.last_updated

    results = results.order_by(sort_col.desc() if sort_order == "Newest First" else sort_col.asc())
    return results.all()

# 🧠 Run Query
filters = {
    "department": dept_filter,
    "semester": sem_filter,
    "type": type_filter,
    "show": show_filter
}
results = get_filtered_results(query, filters, sort_field, sort_order, show_filter)

# 📋 Results
st.markdown("---")
if query:
    st.subheader(f"🔍 Results for: _{query}_ ({len(results)} found)")
elif len(results) > 0:
    st.subheader(f"📁 Showing {len(results)} items")

if results:
    for r in results:
        with st.container():
            st.markdown(f"### {'📁' if r.type == 'folder' else '📄'} [{r.title}]({r.link})")
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"- **Department:** {r.department}")
                st.markdown(f"- **Semester:** {r.semester}")
                st.markdown(f"- **Subject:** {r.subject}")
            with cols[1]:
                st.markdown(f"- **Type:** `{r.type}`")
                st.markdown(f"- **Source:** {r.source}")
                st.markdown(f"- **Added:** {r.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown("---")
else:
    st.info("No resources found. Try changing the filters or search term.")
