import os
import streamlit as st
import pandas as pd
from complaint_service import classify_complaint
from storage import add_complaint, load_complaints, update_status, export_csv

st.set_page_config(page_title="Campus Complaint Bot", page_icon="🏫", layout="wide")
st.title("🏫 Hostel & Campus Complaint Bot")
st.caption("Submit a campus complaint, receive a tracking ID, and check its status.")

CATEGORIES = ["Electrical", "Water", "Mess/Food", "Cleanliness", "Internet/Network",
              "Maintenance", "Security", "Other"]
URGENCIES = ["Low", "Medium", "High", "Critical"]

tab_submit, tab_track, tab_admin = st.tabs(["📝 Submit complaint", "🔎 Track complaint", "🛠 Admin dashboard"])

with tab_submit:
    with st.form("complaint_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        student_name = c1.text_input("Student name")
        room_number = c2.text_input("Room number / location", placeholder="e.g. B-204")
        contact = st.text_input("Contact (optional)", placeholder="Phone or email")
        complaint_text = st.text_area("Describe the problem", height=140,
            placeholder="Explain what happened, where it happened, and when...")
        submitted = st.form_submit_button("Submit complaint", type="primary")

    if submitted:
        if not student_name.strip() or not room_number.strip() or not complaint_text.strip():
            st.error("Please fill in your name, room/location, and complaint description.")
        else:
            with st.spinner("Analyzing complaint..."):
                result = classify_complaint(complaint_text)
            record = add_complaint(
                student_name=student_name.strip(),
                room_number=room_number.strip(),
                contact=contact.strip(),
                complaint_text=complaint_text.strip(),
                category=result["category"],
                urgency=result["urgency"],
                summary=result["summary"],
                ai_used=result["ai_used"],
            )
            st.success("Complaint submitted successfully.")
            st.markdown(f"### Your complaint ID: `{record['complaint_id']}`")
            st.info("Save this ID to track your complaint.")
            st.write(f"**Category:** {record['category']}  |  **Urgency:** {record['urgency']}")
            st.write(f"**Summary:** {record['summary']}")
            if not result["ai_used"]:
                st.warning("AI service was unavailable or not configured. A rule-based fallback classified the complaint.")

with tab_track:
    complaint_id = st.text_input("Enter complaint ID", placeholder="CMP-YYYYMMDD-XXXXXXXX")
    if st.button("Check status", key="track_button"):
        df = load_complaints()
        match = df[df["complaint_id"].str.upper() == complaint_id.strip().upper()] if not df.empty else pd.DataFrame()
        if match.empty:
            st.error("No complaint found for that ID.")
        else:
            row = match.iloc[0]
            st.success("Complaint found")
            st.write(f"**Status:** {row['status']}")
            st.write(f"**Category:** {row['category']} | **Urgency:** {row['urgency']}")
            st.write(f"**Submitted:** {row['created_at']}")
            st.write(f"**Summary:** {row['summary']}")
            st.write(f"**Location:** {row['room_number']}")

with tab_admin:
    st.subheader("Complaint records")
    admin_password = st.text_input("Admin password", type="password", help="Set ADMIN_PASSWORD in your .env file.")
    expected_password = os.getenv("ADMIN_PASSWORD", "change-me")
    if admin_password and admin_password == expected_password:
        df = load_complaints()
        if df.empty:
            st.info("No complaints submitted yet.")
        else:
            f1, f2, f3 = st.columns(3)
            category_filter = f1.selectbox("Category", ["All"] + sorted(df["category"].dropna().unique().tolist()))
            urgency_filter = f2.selectbox("Urgency", ["All"] + URGENCIES)
            status_filter = f3.selectbox("Status", ["All"] + sorted(df["status"].dropna().unique().tolist()))
            filtered = df.copy()
            if category_filter != "All":
                filtered = filtered[filtered["category"] == category_filter]
            if urgency_filter != "All":
                filtered = filtered[filtered["urgency"] == urgency_filter]
            if status_filter != "All":
                filtered = filtered[filtered["status"] == status_filter]
            st.metric("Total complaints", len(df))
            st.dataframe(filtered, use_container_width=True, hide_index=True)
            st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"),
                file_name="complaints_export.csv", mime="text/csv")
            st.divider()
            st.subheader("Update complaint status")
            selected_id = st.selectbox("Complaint ID", df["complaint_id"].tolist())
            new_status = st.selectbox("New status", ["Submitted", "In Progress", "Resolved", "Rejected"])
            if st.button("Update status"):
                if update_status(selected_id, new_status):
                    st.success("Status updated.")
                    st.rerun()
            st.download_button("Download all complaint records", export_csv(),
                file_name="campus_complaints.csv", mime="text/csv")
    elif admin_password:
        st.error("Incorrect admin password.")

# Footer
st.caption("Student complaint data is stored locally in data/complaints.csv. Avoid entering sensitive personal details.")
