import streamlit as st
import database as db
from datetime import datetime, date

def show_dashboard():
    st.title("🔐 Security Operations Dashboard")
    st.caption("Visitor access control, approvals & security monitoring")

    # ===================== TOP METRICS =====================
    try:
        logs = db.fetch_procedure('sp_GetAllVisitorLogs')
        total_visits = len(logs) if not logs.empty else 0
        pending = len(logs[logs['Status'] == 'Pending']) if not logs.empty else 0
        approved = len(logs[logs['Status'] == 'Approved']) if not logs.empty else 0
    except:
        total_visits = pending = approved = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📋 Total Visits", total_visits)
    col2.metric("⏳ Pending", pending)
    col3.metric("✅ Approved", approved)

    st.markdown("---")

    # ===================== TABS =====================
    tab1, tab2, tab3 = st.tabs([
        "📋 Visitor Logs",
        "✅ Approvals & Scheduling",
        "👤 Visitor Registry"
    ])

    # ======================================================
    # TAB 1: VISITOR LOGS
    # ======================================================
    with tab1:
        st.subheader("📋 Visitor Activity Logs")
        st.caption("Complete record of all visit requests and approvals")

        try:
            logs = db.fetch_procedure('sp_GetAllVisitorLogs')

            if not logs.empty:
                st.dataframe(logs, use_container_width=True, hide_index=True)

                with st.expander("🔍 Filter by Date Range"):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        start_date = st.date_input("From", value=date.today())
                    with col2:
                        end_date = st.date_input("To", value=date.today())
                    with col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        filter_btn = st.button("Apply", use_container_width=True)

                    if filter_btn:
                        filtered = db.fetch_procedure(
                            'sp_GetVisitorLogsByDate',
                            (start_date, end_date)
                        )
                        if not filtered.empty:
                            st.success(f"{len(filtered)} record(s) found")
                            st.dataframe(filtered, use_container_width=True, hide_index=True)
                        else:
                            st.info("No visits found in selected range")
            else:
                st.info("No visitor activity recorded")

        except Exception as e:
            st.error(f"Error loading logs: {e}")

    # ======================================================
    # TAB 2: APPROVALS & SCHEDULING
    # ======================================================
    with tab2:
        st.subheader("✅ Schedule & Approve Visits")
        st.caption("Authorize and schedule prisoner visit requests")

        with st.form("approve_visit_form"):
            col1, col2 = st.columns(2)

            # ---------- LEFT COLUMN ----------
            with col1:
                prisoners = db.fetch_procedure('sp_GetAllPrisoners')
                visitors = db.fetch_procedure('sp_GetAllVisitors')

                if prisoners.empty or visitors.empty:
                    st.warning("Prisoners or Visitors data missing")
                    st.stop()

                prisoner_options = {
                    f"{row['FullName']} | Cell {row['CellNumber']}": row['PrisonerID']
                    for _, row in prisoners.iterrows()
                }
                visitor_options = {
                    f"{row['FullName']} ({row['Relationship']})": row['VisitorID']
                    for _, row in visitors.iterrows()
                }

                prisoner_label = st.selectbox("Prisoner *", prisoner_options.keys())
                visitor_label = st.selectbox("Visitor *", visitor_options.keys())

            # ---------- RIGHT COLUMN ----------
            with col2:
                visit_date = st.date_input("Visit Date *", min_value=date.today())
                visit_time = st.time_input("Visit Time *")
                purpose = st.text_input("Purpose *", value="Family Visit")
                approved_by = st.text_input(
                    "Approved By *",
                    value=st.session_state.get("user_name", "Security Officer")
                )

            submitted = st.form_submit_button("✅ Approve & Schedule Visit", use_container_width=True)

            if submitted:
                result = db.execute_procedure(
                    'sp_ScheduleVisit',
                    (
                        prisoner_options[prisoner_label],
                        visitor_options[visitor_label],
                        visit_date,
                        visit_time,
                        purpose,
                        approved_by
                    )
                )

                if result:
                    st.success("Visit scheduled and approved successfully")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to schedule visit")

    # ======================================================
    # TAB 3: VISITOR REGISTRY
    # ======================================================
    with tab3:
        st.subheader("👤 Visitor Registry")
        st.caption("Manage authorized visitors")

        visitors = db.fetch_procedure('sp_GetAllVisitors')

        if not visitors.empty:
            st.dataframe(visitors, use_container_width=True, hide_index=True)
            st.metric("Total Registered Visitors", len(visitors))
        else:
            st.info("No visitors registered")

        st.markdown("---")
        st.markdown("### ➕ Register New Visitor")

        with st.form("register_visitor_form"):
            col1, col2 = st.columns(2)

            with col1:
                full_name = st.text_input("Full Name *")
                cnic = st.text_input("CNIC *")
                phone = st.text_input("Phone Number *")

            with col2:
                relationship = st.selectbox(
                    "Relationship *",
                    ["Parent", "Sibling", "Spouse", "Child", "Friend", "Lawyer", "Other"]
                )
                address = st.text_area("Address")

            if st.form_submit_button("➕ Register Visitor", use_container_width=True):
                if not full_name or not cnic or not phone:
                    st.warning("Please fill all required fields")
                else:
                    result = db.execute_procedure(
                        'sp_RegisterVisitor',
                        (full_name, cnic, phone, relationship, address)
                    )
                    if result:
                        st.success("Visitor registered successfully")
                        st.rerun()
                    else:
                        st.error("Registration failed – CNIC may already exist")
