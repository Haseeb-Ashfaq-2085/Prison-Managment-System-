import streamlit as st
import database as db
from datetime import datetime

def show_dashboard():
    st.set_page_config(page_title="Medical Staff Dashboard", page_icon="🏥", layout="wide")
    
    st.title("🏥 Medical Staff Dashboard")
    st.markdown("---")

    # ------------------------- QUICK STATS -------------------------
    col1, col2, col3 = st.columns(3)
    
    try:
        total_prisoners = len(db.fetch_procedure('sp_GetAllPrisoners'))
    except:
        total_prisoners = 0

    try:
        total_records = len(db.fetch_procedure('sp_GetAllMedicalRecords'))
    except:
        total_records = 0

    try:
        upcoming_checkups = len(db.fetch_procedure('sp_GetMedicalSchedule', (7,)))
    except:
        upcoming_checkups = 0
    
    col1.metric("Total Prisoners", total_prisoners, "👤")
    col2.metric("Total Medical Records", total_records, "📋")
    col3.metric("Upcoming Checkups (7 days)", upcoming_checkups, "🗓️")
    
    st.markdown("---")
    
    # ------------------------- TABS -------------------------
    tab1, tab2, tab3 = st.tabs(["📄 Medical Records", "📅 Schedule", "🔍 Patient Search"])
    
    # ------------------------- TAB 1: Medical Records -------------------------
    with tab1:
        st.subheader("All Medical Records")
        records = db.fetch_procedure('sp_GetAllMedicalRecords')
        if not records.empty:
            st.dataframe(records, use_container_width=True, hide_index=True)
        else:
            st.info("No medical records found")
        
        st.markdown("### ➕ Add New Medical Record")
        with st.form("add_medical", clear_on_submit=True):
            prisoners = db.fetch_procedure('sp_GetAllPrisoners')
            if prisoners.empty:
                st.warning("No prisoners found. Please add prisoners first.")
            else:
                prisoner_options = [
                    f"{row['FullName']} ({row['CNIC']}) - Cell {row['CellNumber']}" 
                    for _, row in prisoners.iterrows()
                ]
                prisoner_idx = st.selectbox(
                    "Select Prisoner *", range(len(prisoner_options)), 
                    format_func=lambda x: prisoner_options[x]
                )
                
                col1f, col2f = st.columns(2)
                with col1f:
                    diagnosis = st.text_input("Diagnosis *")
                    medication = st.text_input("Medication *")
                    doctor = st.text_input("Doctor Name *")
                with col2f:
                    checkup_date = st.date_input("Checkup Date *", value=datetime.now())
                    next_checkup = st.date_input("Next Checkup Date")
                    notes = st.text_area("Notes")
                
                if st.form_submit_button("Add Record", use_container_width=True):
                    # Validate required fields
                    if not diagnosis or not medication or not doctor:
                        st.error("Please fill in all required fields")
                    else:
                        try:
                            # Cast prisoner_id to native Python int
                            prisoner_id = int(prisoners.iloc[prisoner_idx]['PrisonerID'])
                            checkup_date_str = checkup_date.strftime("%Y-%m-%d")
                            next_checkup_str = next_checkup.strftime("%Y-%m-%d") if next_checkup else None
                            
                            result = db.execute_procedure(
                                'sp_AddMedicalRecord', 
                                (prisoner_id, diagnosis, medication, doctor, checkup_date_str, next_checkup_str, notes)
                            )
                            
                            if result:
                                st.success("✅ Medical record added successfully")
                                st.experimental_rerun()
                            else:
                                st.error("❌ Failed to add record")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

    # ------------------------- TAB 2: Schedule -------------------------
    with tab2:
        st.subheader("Upcoming Medical Schedule")
        
        days = st.slider("Days ahead to show schedule", 1, 30, 7)
        schedule = db.fetch_procedure('sp_GetMedicalSchedule', (days,))
        
        if not schedule.empty:
            st.dataframe(schedule, use_container_width=True, hide_index=True)
            st.metric("Total Scheduled Checkups", len(schedule))
        else:
            st.info(f"No checkups scheduled for the next {days} days")
    
    # ------------------------- TAB 3: Patient Search -------------------------
    with tab3:
        st.subheader("Search Patient Medical History")
        
        prisoners = db.fetch_procedure('sp_GetAllPrisoners')
        if prisoners.empty:
            st.warning("No prisoners found.")
        else:
            search_options = [f"{row['FullName']} ({row['CNIC']})" for _, row in prisoners.iterrows()]
            search_idx = st.selectbox(
                "Select Prisoner", range(len(search_options)), 
                format_func=lambda x: search_options[x]
            )
            
            if st.button("🔎 Get Medical History"):
                try:
                    prisoner_id = int(prisoners.iloc[search_idx]['PrisonerID'])
                    history = db.fetch_procedure('sp_GetMedicalRecordsByPrisoner', (prisoner_id,))
                    
                    prisoner_info = prisoners.iloc[search_idx]
                    st.info(
                        f"**Patient:** {prisoner_info['FullName']} | "
                        f"**CNIC:** {prisoner_info['CNIC']} | "
                        f"**Cell:** {prisoner_info['CellNumber']}"
                    )
                    
                    if not history.empty:
                        st.dataframe(history, use_container_width=True, hide_index=True)
                    else:
                        st.warning("No medical history found for this prisoner")
                except Exception as e:
                    st.error(f"❌ Error fetching history: {e}")
    
    # ------------------------- FOOTER -------------------------
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; opacity:0.5; font-size:13px;'>🏥 Medical Dashboard | Developed by Haseeb Ashfaq</div>",
        unsafe_allow_html=True
    )
