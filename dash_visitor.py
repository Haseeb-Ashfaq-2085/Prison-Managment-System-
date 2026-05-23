import streamlit as st
import database as db
from datetime import date

def show_dashboard():
    st.title("Visitor Registration Portal")
    
    tab1, tab2 = st.tabs(["Register as Visitor", "My Visit History"])
    
    # -------------------- REGISTER NEW VISITOR --------------------
    with tab1:
        st.subheader("New Visitor Registration")
        st.info("Please register yourself to schedule visits with prisoners")
        
        with st.form("visitor_registration"):
            col1, col2 = st.columns(2)
            
            # Left Column
            with col1:
                full_name = st.text_input("Full Name *")
                cnic = st.text_input("CNIC Number *", placeholder="35202-1234567-1")
                phone = st.text_input("Phone Number *", placeholder="0300-1234567")
                dob = st.date_input("Date of Birth *", max_value=date.today())
                email = st.text_input("Email Address *", placeholder="example@email.com")
            
            # Right Column
            with col2:
                relationship = st.selectbox(
                    "Relationship with Prisoner *", 
                    ["Parent", "Sibling", "Spouse", "Child", "Friend", "Lawyer", "Other"]
                )
                address = st.text_area("Complete Address *")
                preferred_date = st.date_input("Preferred Visit Date *", min_value=date.today())
            
            # Submit Button
            if st.form_submit_button("Register Now", use_container_width=True):
                # Basic Validation
                if not all([full_name, cnic, phone, dob, email, relationship, address, preferred_date]):
                    st.warning("⚠️ Please fill all required fields")
                else:
                    with st.spinner("Registering your visit..."):
                        result = db.execute_procedure(
                            'sp_RegisterVisitor', 
                            (full_name, cnic, phone, dob.strftime("%Y-%m-%d"), email, relationship, address, preferred_date.strftime("%Y-%m-%d"))
                        )
                        if result:
                            st.success("✅ Registration successful! You can now contact security to schedule a visit.")
                        else:
                            st.error("❌ Registration failed. Your CNIC may already be registered.")
    
    # -------------------- VIEW VISIT HISTORY --------------------
    with tab2:
        st.subheader("Search Your Visit History")
        st.info("Enter your CNIC to view all your scheduled and completed visits")
        
        search_cnic = st.text_input("Enter your CNIC", placeholder="35202-1234567-1")
        
        if st.button("Search My Visits", use_container_width=True):
            if search_cnic:
                visitor_data = db.fetch_procedure('sp_GetVisitorByCNIC', (search_cnic,))
                
                if not visitor_data.empty:
                    visitor = visitor_data.iloc[0]
                    st.success(f"Welcome, {visitor['FullName']}!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Name", visitor['FullName'])
                    with col2:
                        st.metric("Relationship", visitor['Relationship'])
                    with col3:
                        st.metric("Status", visitor['Status'])
                    
                    st.subheader("Your Visit History")
                    visits = db.fetch_procedure('sp_GetVisitorHistory', (visitor['VisitorID'],))
                    
                    if not visits.empty:
                        st.dataframe(visits, use_container_width=True, hide_index=True)
                        st.metric("Total Visits", len(visits))
                    else:
                        st.info("No visit history found. Contact security to schedule your first visit.")
                else:
                    st.warning("⚠️ CNIC not found in our system. Please register first.")
            else:
                st.warning("Please enter your CNIC number")
