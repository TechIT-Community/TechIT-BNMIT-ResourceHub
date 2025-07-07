import streamlit as st
from io import BytesIO
from db import get_all_metadata
from utils.file_routing import classify_file, upload_to_drive, create_github_pr

st.set_page_config(page_title="📤 Contribute to ResourceHub", layout="wide")

st.title("📤 Contribute to TechIT ResourceHub")
st.markdown("""
Welcome! Upload your academic resources here.

- **Code files** will be automatically sent to GitHub.
- **PDFs, DOCXs, JPGs** and other binaries will go to Google Drive.
- Please make sure to select correct metadata for each file.
---
""")

# 🔎 Fetch metadata
departments, semesters, subjects = get_all_metadata()
if not departments: departments = ["CSE", "ISE", "ECE"]
if not semesters: semesters = ["1", "2", "3", "4", "5", "6", "7", "8"]
if not subjects: subjects = []

# 📦 Upload Form
with st.form("upload_form"):
    uploaded_files = st.file_uploader(
        "Upload your files", accept_multiple_files=True,
        type=["pdf", "docx", "jpg", "jpeg", "png", "py", "c", "cpp", "java", "js", "ts", "html", "css"]
    )

    department = st.selectbox("Department", departments)
    semester = st.selectbox("Semester", semesters)

    subject_choice = st.selectbox("Subject", list(subjects) + ["Other (Add new subject)"])
    if subject_choice == "Other (Add new subject)":
        subject = st.text_input("Enter new subject name")
    else:
        subject = subject_choice

    submitted = st.form_submit_button("🚀 Submit")

# 🔽 Submission logic
if submitted:
    if not uploaded_files:
        st.error("Please upload at least one file.")
        st.stop()
    if not subject:
        st.error("Please enter or select a subject.")
        st.stop()

    with st.spinner("Uploading your files..."):
        for file in uploaded_files:
            file_bytes = BytesIO(file.read())
            filename = file.name
            category = classify_file(filename)
            type_label = "contributions"

            try:
                if category == "code":
                    pr_url = create_github_pr(file_bytes, filename, department, semester, subject, type_label)
                    st.success(f"✅ GitHub PR created: [View PR]({pr_url})")
                elif category == "binary":
                    view_url = upload_to_drive(file_bytes, filename, department, semester, subject, type_label)
                    st.success(f"✅ Uploaded to Google Drive: [View File]({view_url})")
                else:
                    st.warning(f"⚠️ Skipped unsupported file: {filename}")
            except Exception as e:
                st.error(f"❌ Error while uploading {filename}: {str(e)}")
