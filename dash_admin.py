import streamlit as st
import database as db
from datetime import datetime

def show_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            background: #f0f2f6;
            border-radius: 10px;
            margin: 5px 0;
        }
        .stButton>button {
            width: 100%;
        }
        .pending-visit {
            background: #FFF3CD;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 5px solid #FFC107;
        }
        .approved-visit {
            background: #D1FAE5;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 5px solid #10B981;
        }
        .rejected-visit {
            background: #FEE2E2;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 5px solid #EF4444;
        }
        </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", 
        "👥 Prisoners", 
        "🏢 Cells",
        "👨‍👩‍👧 Visitors",
        "📋 Reports", 
        "📜 Activity Log",
        "⚙️ Settings"
    ])
    
    # ==================== TAB 1: OVERVIEW ====================
    with tab1:
        st.subheader("📊 Dashboard Overview")
        
        try:
            stats = db.fetch_procedure('sp_GetDashboardStats')
            
            if not stats.empty:
                # Top Metrics Row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    active_prisoners = int(stats.iloc[0]['ActivePrisoners'])
                    st.markdown(f"""
                        <div class='metric-card' style='text-align:center;'>
                            <div style='font-size:42px;margin-bottom:5px;'>👥</div>
                            <h2 style='margin:5px 0;color:#2563EB;'>{active_prisoners}</h2>
                            <p style='opacity:0.7;margin:0;'>Active Prisoners</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    total_cells = int(stats.iloc[0]['TotalCells'])
                    st.markdown(f"""
                        <div class='metric-card' style='text-align:center;'>
                            <div style='font-size:42px;margin-bottom:5px;'>🏢</div>
                            <h2 style='margin:5px 0;color:#10B981;'>{total_cells}</h2>
                            <p style='opacity:0.7;margin:0;'>Total Cells</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_occ = float(stats.iloc[0]['AvgOccupancy']) if stats.iloc[0]['AvgOccupancy'] else 0
                    occ_color = "#EF4444" if avg_occ > 90 else "#F59E0B" if avg_occ > 75 else "#10B981"
                    st.markdown(f"""
                        <div class='metric-card' style='text-align:center;'>
                            <div style='font-size:42px;margin-bottom:5px;'>📊</div>
                            <h2 style='margin:5px 0;color:{occ_color};'>{avg_occ:.1f}%</h2>
                            <p style='opacity:0.7;margin:0;'>Avg Occupancy</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    pending_visits = int(stats.iloc[0]['PendingVisits'])
                    st.markdown(f"""
                        <div class='metric-card' style='text-align:center;'>
                            <div style='font-size:42px;margin-bottom:5px;'>⏳</div>
                            <h2 style='margin:5px 0;color:#F59E0B;'>{pending_visits}</h2>
                            <p style='opacity:0.7;margin:0;'>Pending Visits</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Secondary Metrics Row
                col5, col6, col7, col8 = st.columns(4)
                
                with col5:
                    upcoming = int(stats.iloc[0]['UpcomingReleases'])
                    st.metric("🚪 Releases (30d)", upcoming)
                with col6:
                    checkups = int(stats.iloc[0]['UpcomingCheckups'])
                    st.metric("🏥 Checkups (7d)", checkups)
                with col7:
                    security = int(stats.iloc[0]['SecurityOfficers'])
                    st.metric("🔐 Security", security)
                with col8:
                    doctors = int(stats.iloc[0]['Doctors'])
                    st.metric("👨‍⚕️ Doctors", doctors)
            else:
                st.warning("No dashboard statistics available")
        except Exception as e:
            st.error(f"Error loading dashboard: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Recent Admissions and Pending Visits side by side
        col_recent, col_pending = st.columns(2)
        
        with col_recent:
            st.subheader("📅 Recent Admissions")
            try:
                recent = db.fetch_procedure('sp_GetRecentAdmissions', (30,))
                if not recent.empty:
                    st.dataframe(recent.head(5), use_container_width=True, hide_index=True)
                else:
                    st.info("No recent admissions")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        with col_pending:
            st.subheader("⏳ Pending Visit Requests")
            try:
                pending = db.fetch_procedure('sp_GetPendingVisits')
                if not pending.empty:
                    st.dataframe(pending.head(5), use_container_width=True, hide_index=True)
                    if len(pending) > 5:
                        st.info(f"📋 {len(pending) - 5} more pending visits. Check Visitors tab.")
                else:
                    st.success("✅ No pending visits")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # ==================== TAB 2: PRISONERS ====================
    with tab2:
        st.subheader("👥 Prisoner Management")
        
        # Action selector
        view_type = st.radio("Select Action", 
            ["📋 View All", "🔍 Search Prisoner", "➕ Add New Prisoner", "✏️ Update Prisoner"], 
            horizontal=True, key="prisoner_action")
        
        # VIEW ALL PRISONERS
        if view_type == "📋 View All":
            try:
                prisoners = db.fetch_procedure('sp_GetAllPrisoners')
                if not prisoners.empty:
                    st.dataframe(prisoners, use_container_width=True, hide_index=True)
                    st.metric("Total Prisoners", len(prisoners))
                else:
                    st.info("No prisoners found in the system")
            except Exception as e:
                st.error(f"Error loading prisoners: {str(e)}")
        
        # SEARCH PRISONER
        elif view_type == "🔍 Search Prisoner":
            search_term = st.text_input("🔎 Search by Name, CNIC, or Crime", 
                                       placeholder="Enter search term...",
                                       key="search_prisoner")
            
            if st.button("🔍 Search", type="primary", key="btn_search"):
                if search_term:
                    try:
                        results = db.fetch_procedure('sp_SearchPrisoners', (search_term,))
                        if not results.empty:
                            st.success(f"✅ Found {len(results)} result(s)")
                            st.dataframe(results, use_container_width=True, hide_index=True)
                        else:
                            st.warning("⚠️ No prisoners found matching your search")
                    except Exception as e:
                        st.error(f"Search error: {str(e)}")
                else:
                    st.warning("Please enter a search term")
        
        # UPDATE PRISONER
        elif view_type == "✏️ Update Prisoner":
            st.markdown("### 🔄 Update Prisoner Details")
            
            prisoner_id = st.number_input("Enter Prisoner ID", min_value=1, step=1, 
                                         key="update_prisoner_id")
            
            if prisoner_id > 0:
                try:
                    prisoner_details = db.fetch_procedure('sp_GetPrisonerByID', (prisoner_id,))
                    
                    if not prisoner_details.empty:
                        st.success(f"✅ Found: {prisoner_details.iloc[0]['FullName']}")
                        
                        with st.expander("📋 View Current Details", expanded=False):
                            st.dataframe(prisoner_details, use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        st.markdown("### Select Update Action")
                        
                        update_action = st.selectbox(
                            "What would you like to update?",
                            ["Add Remission Days", "Update Status", "Transfer to Another Cell"],
                            key="update_action_select"
                        )
                        
                        if update_action == "Add Remission Days":
                            st.info("💡 Remission days reduce the total sentence duration")
                            
                            remission_days = st.number_input(
                                "Remission Days to Add", 
                                min_value=1, 
                                max_value=365, 
                                step=1,
                                value=30,
                                key="remission_input"
                            )
                            
                            if st.button("💾 Add Remission", type="primary", key="btn_add_remission"):
                                try:
                                    result = db.execute_procedure('sp_UpdatePrisoner', 
                                                                 (prisoner_id, remission_days, None, None))
                                    if result:
                                        st.success(f"✅ Added {remission_days} remission days!")
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        elif update_action == "Update Status":
                            st.info("💡 Change the prisoner's current status")
                            
                            current_status = prisoner_details.iloc[0]['Status']
                            st.write(f"Current Status: **{current_status}**")
                            
                            new_status = st.selectbox(
                                "Select New Status",
                                ["Active", "Released", "Transferred", "Deceased"],
                                key="status_select"
                            )
                            
                            if new_status != current_status:
                                if st.button("💾 Update Status", type="primary", key="btn_update_status"):
                                    try:
                                        result = db.execute_procedure('sp_UpdatePrisoner', 
                                                                     (prisoner_id, None, new_status, None))
                                        if result:
                                            st.success(f"✅ Status updated to {new_status}!")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to update")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            else:
                                st.warning("⚠️ Please select a different status")
                        
                        else:
                            st.info("💡 Transfer prisoner to a different cell")
                            
                            current_cell = prisoner_details.iloc[0]['CellNumber']
                            st.write(f"Current Cell: **{current_cell}**")
                            
                            try:
                                cells = db.fetch_procedure('sp_GetAllCells')
                                
                                if not cells.empty:
                                    available_cells = cells[cells['CurrentOccupancy'] < cells['Capacity']]
                                    
                                    if not available_cells.empty:
                                        cell_options = {}
                                        for _, row in available_cells.iterrows():
                                            cell_label = f"{row['CellNumber']} - Block {row['Block']} (Available: {row['Capacity'] - row['CurrentOccupancy']})"
                                            cell_options[cell_label] = row['CellID']
                                        
                                        selected_cell = st.selectbox(
                                            "Select New Cell",
                                            list(cell_options.keys()),
                                            key="transfer_cell_select"
                                        )
                                        
                                        new_cell_id = cell_options[selected_cell]
                                        
                                        if st.button("🔄 Transfer Prisoner", type="primary", key="btn_transfer"):
                                            try:
                                                result = db.execute_procedure('sp_TransferPrisoner', 
                                                                             (prisoner_id, new_cell_id))
                                                if result:
                                                    st.success("✅ Prisoner transferred!")
                                                    st.balloons()
                                                    st.rerun()
                                                else:
                                                    st.error("❌ Failed to transfer")
                                            except Exception as e:
                                                st.error(f"Error: {str(e)}")
                                    else:
                                        st.warning("⚠️ No cells available")
                                else:
                                    st.error("No cells found")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    else:
                        st.warning("⚠️ No prisoner found with this ID")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                # ADD NEW PRISONER
        elif view_type == "➕ Add New Prisoner":

            # ✅ Show global success message if prisoner was added
            if st.session_state.get("prisoner_added_success"):
                st.success(st.session_state["prisoner_added_success"])
                del st.session_state["prisoner_added_success"]

            with st.form("add_prisoner_form"):
                st.markdown("### 📝 New Prisoner Registration")

                col1, col2 = st.columns(2)

                # ---------- PERSONAL INFORMATION ----------
                with col1:
                    st.markdown("**Personal Information**")
                    name = st.text_input("Full Name *", placeholder="Enter full name")
                    cnic = st.text_input("CNIC *", placeholder="35202-1234567-1", max_chars=15)
                    dob = st.date_input("Date of Birth *", max_value=datetime.now())
                    gender = st.selectbox("Gender *", ["Male", "Female"])
                    address = st.text_area("Address", placeholder="Complete address")
                    emergency = st.text_input("Emergency Contact", placeholder="03XX-XXXXXXX")

                # ---------- INCARCERATION DETAILS ----------
                with col2:
                    st.markdown("**Incarceration Details**")

                    cell_id = None
                    try:
                        cells = db.fetch_procedure('sp_GetAllCells')

                        if cells.empty:
                            st.warning("⚠️ No cells found")
                        else:
                            available_cells = cells[cells['CurrentOccupancy'] < cells['Capacity']]

                            if available_cells.empty:
                                st.warning("⚠️ All cells are full")
                            else:
                                cell_options = {
                                    f"{row['CellNumber']} - Block {row['Block']} "
                                    f"(Available: {row['Capacity'] - row['CurrentOccupancy']})":
                                    row['CellID']
                                    for _, row in available_cells.iterrows()
                                }

                                selected_cell = st.selectbox(
                                    "Assign Cell *",
                                    list(cell_options.keys())
                                )
                                cell_id = cell_options[selected_cell]

                    except Exception as e:
                        st.error(f"❌ Error loading cells: {e}")

                    admission = st.date_input("Admission Date *", value=datetime.now())
                    sentence = st.number_input(
                        "Sentence (Years) *",
                        min_value=1,
                        max_value=99,
                        step=1,
                        value=1
                    )
                    crime = st.text_input("Crime *", placeholder="Brief description")

                # ---------- SUBMIT ----------
                submitted = st.form_submit_button("➕ Add Prisoner", type="primary")

                if submitted:
                    if not name or not cnic or not crime or cell_id is None:
                        st.error("❌ Please fill all required fields")
                    else:
                        try:
                            result = db.execute_procedure(
                                'sp_AddPrisoner',
                                (
                                    name,
                                    cnic,
                                    dob.strftime("%Y-%m-%d"),
                                    gender,
                                    cell_id,
                                    admission.strftime("%Y-%m-%d"),
                                    sentence,
                                    crime,
                                    address or "",
                                    emergency or ""
                                )
                            )

                            if result:
                                # ✅ Set session state for persistent success message
                                st.session_state["prisoner_added_success"] = f"✅ Prisoner **{name}** added successfully!"
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ CNIC may already exist or cell is full")

                        except Exception as e:
                            st.error(f"❌ Database Error: {e}")

    # ==================== TAB 3: CELLS ====================
    # ==================== TAB 3: CELLS (COMPLETE FIXED VERSION) ====================
# Replace your TAB 3 code with this entire section

    with tab3:
        st.subheader("🏢 Cell Management")
        
        # Action selector
        cell_action = st.radio("Select Action", 
            ["📊 View All Cells", "➕ Add New Cell", "✏️ Update Cell"], 
            horizontal=True, key="cell_action")
        
        # ==================== VIEW ALL CELLS ====================
        if cell_action == "📊 View All Cells":
            st.markdown("### 📊 Cell Status Overview")
            
            try:
                cells_df = db.fetch_procedure('sp_GetAllCells')
                
                if not cells_df.empty:
                    for _, cell in cells_df.iterrows():
                        occupancy_pct = float(cell['OccupancyPercent']) if cell['OccupancyPercent'] else 0
                        
                        if occupancy_pct > 100:
                            status_icon = "🔴"
                            status_text = "OVERCROWDED"
                            status_color = "#FEE2E2"
                        elif occupancy_pct >= 100:
                            status_icon = "🟠"
                            status_text = "FULL"
                            status_color = "#FFEDD5"
                        elif occupancy_pct > 80:
                            status_icon = "🟡"
                            status_text = "NEAR CAPACITY"
                            status_color = "#FEF3C7"
                        else:
                            status_icon = "🟢"
                            status_text = "NORMAL"
                            status_color = "#D1FAE5"
                        
                        assigned_officer = cell['AssignedOfficer'] if cell['AssignedOfficer'] else "Not Assigned"
                        
                        st.markdown(f"""
                            <div style='background-color:{status_color}; padding:15px; border-radius:10px; margin-bottom:10px;'>
                                <div style='display:flex;justify-content:space-between;align-items:center;'>
                                    <div>
                                        {status_icon} <strong style='font-size:18px;'>Cell {cell['CellNumber']}</strong> - Block {cell['Block']}
                                        <br>
                                        <span style='font-size:13px; opacity:0.8;'>👮 Officer: {assigned_officer}</span>
                                        <br>
                                        <span style='font-size:11px; opacity:0.6;'>Cell ID: {cell['CellID']} | Status: {cell['Status']}</span>
                                    </div>
                                    <div style='text-align:right;'>
                                        <span style='font-weight:700;font-size:16px;'>{cell['CurrentOccupancy']}/{cell['Capacity']}</span>
                                        <span style='opacity:0.7;'> ({occupancy_pct:.0f}%)</span>
                                        <br>
                                        <span style='font-size:12px;font-weight:600;'>{status_text}</span>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.metric("Total Cells", len(cells_df))
                else:
                    st.info("No cells found")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # ==================== ADD NEW CELL ====================
        elif cell_action == "➕ Add New Cell":
            st.markdown("### ➕ Add New Cell")
            
            # Show success message if cell was added
            if st.session_state.get("cell_added_success"):
                st.success(st.session_state["cell_added_success"])
                del st.session_state["cell_added_success"]
            
            with st.form("add_cell_form"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    cell_num = st.text_input("Cell Number *", placeholder="D-101", key="new_cell_num")
                
                with col2:
                    capacity = st.number_input(
                        "Capacity *",
                        min_value=1,
                        max_value=20,
                        step=1,
                        value=4,
                        key="new_cell_capacity"
                    )
                
                with col3:
                    block = st.text_input("Block *", placeholder="A, B, C, D", key="new_cell_block")
                
                with col4:
                    officer_id = None
                    try:
                        officers = db.fetch_procedure('sp_GetSecurityOfficers')
                        
                        if officers.empty:
                            st.warning("⚠️ No officers available")
                        else:
                            officer_map = {
                                f"{row['FullName']} (Shift: {row['Shift'] if row['Shift'] else 'None'})": row['UserID']
                                for _, row in officers.iterrows()
                            }
                            
                            selected = st.selectbox(
                                "Assign Officer *",
                                list(officer_map.keys()),
                                key="new_cell_officer"
                            )
                            officer_id = officer_map[selected]
                    except Exception as e:
                        st.error(f"Error loading officers: {str(e)}")
                
                submitted = st.form_submit_button("➕ Add Cell", type="primary")
                
                if submitted:
                    if not cell_num or not block or officer_id is None:
                        st.error("❌ Please fill all required fields")
                    else:
                        try:
                            result = db.execute_procedure(
                                'sp_AddCell',
                                (cell_num, capacity, block, officer_id)
                            )
                            
                            if result:
                                st.session_state["cell_added_success"] = f"✅ Cell {cell_num} added successfully!"
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Cell number already exists")
                        
                        except Exception as e:
                            st.error(f"❌ Database Error: {str(e)}")
        
        # ==================== UPDATE CELL ====================
        else:  # Update Cell
            st.markdown("### ✏️ Update Cell")
            
            # Show success message if cell was updated
            if st.session_state.get("cell_updated_success"):
                st.success(st.session_state["cell_updated_success"])
                del st.session_state["cell_updated_success"]
            
            try:
                cells_df = db.fetch_procedure('sp_GetAllCells')
                
                if cells_df.empty:
                    st.warning("⚠️ No cells available to update")
                else:
                    # Create cell selection map
                    cell_map = {
                        f"{row['CellNumber']} - Block {row['Block']} (Officer: {row['AssignedOfficer'] if row['AssignedOfficer'] else 'Not Assigned'})": row['CellID']
                        for _, row in cells_df.iterrows()
                    }
                    
                    selected_cell = st.selectbox(
                        "Select Cell to Update",
                        list(cell_map.keys()),
                        key="update_cell_select"
                    )
                    
                    cell_id = cell_map[selected_cell]
                    
                    # Get current cell details
                    current_cell = cells_df[cells_df['CellID'] == cell_id].iloc[0]
                    
                    with st.expander("📋 Current Cell Details", expanded=True):
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Cell Number", current_cell['CellNumber'])
                        col2.metric("Capacity", current_cell['Capacity'])
                        col3.metric("Block", current_cell['Block'])
                        col4.metric("Occupancy", f"{current_cell['CurrentOccupancy']}/{current_cell['Capacity']}")
                        
                        st.info(f"👮 Assigned Officer: {current_cell['AssignedOfficer'] if current_cell['AssignedOfficer'] else 'Not Assigned'}")
                    
                    st.markdown("---")
                    st.markdown("### Select What to Update")
                    
                    update_type = st.selectbox(
                        "What would you like to update?",
                        ["Change Assigned Officer", "Update Capacity", "Change Status"],
                        key="cell_update_type"
                    )
                    
                    # ========== CHANGE OFFICER ==========
                    if update_type == "Change Assigned Officer":
                        st.info("💡 Assign a different security officer to this cell")
                        
                        try:
                            officers = db.fetch_procedure('sp_GetSecurityOfficers')
                            
                            if officers.empty:
                                st.warning("⚠️ No officers available")
                            else:
                                officer_map = {
                                    f"{row['FullName']} (Shift: {row['Shift'] if row['Shift'] else 'None'})": row['UserID']
                                    for _, row in officers.iterrows()
                                }
                                
                                new_officer_selected = st.selectbox(
                                    "Select New Officer",
                                    list(officer_map.keys()),
                                    key="update_officer_select"
                                )
                                
                                new_officer_id = officer_map[new_officer_selected]
                                
                                if st.button("💾 Update Officer", type="primary", key="btn_update_officer"):
                                    try:
                                        result = db.execute_procedure(
                                            'sp_UpdateCell',
                                            (cell_id, new_officer_id, None, None)
                                        )
                                        
                                        if result:
                                            st.session_state["cell_updated_success"] = "✅ Officer updated successfully!"
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to update officer")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        except Exception as e:
                            st.error(f"Error loading officers: {str(e)}")
                    
                    # ========== UPDATE CAPACITY ==========
                    elif update_type == "Update Capacity":
                        st.info("💡 Change the maximum capacity of this cell")
                        
                        current_capacity = int(current_cell['Capacity'])
                        current_occupancy = int(current_cell['CurrentOccupancy'])
                        
                        st.warning(f"⚠️ Current occupancy: {current_occupancy}. New capacity must be >= {current_occupancy}")
                        
                        new_capacity = st.number_input(
                            "New Capacity",
                            min_value=current_occupancy,  # Can't be less than current occupancy
                            max_value=20,
                            value=current_capacity,
                            step=1,
                            key="update_capacity_input"
                        )
                        
                        if new_capacity != current_capacity:
                            if st.button("💾 Update Capacity", type="primary", key="btn_update_capacity"):
                                try:
                                    result = db.execute_procedure(
                                        'sp_UpdateCell',
                                        (cell_id, None, new_capacity, None)
                                    )
                                    
                                    if result:
                                        st.session_state["cell_updated_success"] = f"✅ Capacity updated from {current_capacity} to {new_capacity}!"
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update capacity")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        else:
                            st.info("ℹ️ Please change the capacity value")
                    
                    # ========== CHANGE STATUS ==========
                    else:  # Change Status
                        st.info("💡 Change the operational status of this cell")
                        
                        current_status = current_cell['Status']
                        st.write(f"Current Status: **{current_status}**")
                        
                        new_status = st.selectbox(
                            "Select New Status",
                            ["Active", "Inactive", "Maintenance"],
                            key="update_status_select"
                        )
                        
                        if new_status != current_status:
                            if current_cell['CurrentOccupancy'] > 0 and new_status != 'Active':
                                st.error(f"⚠️ Cannot change status: Cell has {current_cell['CurrentOccupancy']} prisoner(s)")
                            else:
                                if st.button("💾 Update Status", type="primary", key="btn_update_status"):
                                    try:
                                        result = db.execute_procedure(
                                            'sp_UpdateCell',
                                            (cell_id, None, None, new_status)
                                        )
                                        
                                        if result:
                                            st.session_state["cell_updated_success"] = f"✅ Status updated to {new_status}!"
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to update status")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        else:
                            st.info("ℹ️ Please select a different status")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

        
    # ==================== TAB 4: VISITORS & APPROVALS ====================
    with tab4:
        st.subheader("👨‍👩‍👧 Visitor Management & Approvals")
        
        visitor_tab = st.radio("Select View", 
            ["⏳ Pending Approvals", "✅ Approved Visits", "❌ Rejected Visits", "📋 All Visits"],
            horizontal=True, key="visitor_view")
        
        # PENDING APPROVALS
        if visitor_tab == "⏳ Pending Approvals":
            st.markdown("### ⏳ Visit Requests Awaiting Approval")
            
            try:
                pending_visits = db.fetch_procedure('sp_GetPendingVisits')
                
                if not pending_visits.empty:
                    st.warning(f"⚠️ {len(pending_visits)} visit request(s) pending approval")
                    
                    for idx, visit in pending_visits.iterrows():
                        hours_until = visit['HoursUntilVisit']
                        
                        if hours_until < 0:
                            time_badge = "🔴 OVERDUE"
                            time_text = f"{abs(hours_until)} hours ago"
                        elif hours_until < 24:
                            time_badge = "🟠 URGENT"
                            time_text = f"in {hours_until} hours"
                        else:
                            time_badge = "🟡 PENDING"
                            time_text = f"in {hours_until} hours"
                        
                        st.markdown(f"""
                            <div class='pending-visit'>
                                <strong>Visit Request #{visit['LogID']}</strong> - {time_badge}
                                <br>
                                <strong>Visitor:</strong> {visit['VisitorName']} ({visit['Relationship']})
                                <br>
                                <strong>Prisoner:</strong> {visit['PrisonerName']} - Cell {visit['CellNumber']}, Block {visit['Block']}
                                <br>
                                <strong>Scheduled:</strong> {visit['VisitDate']} at {visit['VisitTime']} ({time_text})
                                <br>
                                <strong>Purpose:</strong> {visit['Purpose']}
                                <br>
                                <strong>Contact:</strong> {visit['VisitorPhone']}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1, 1, 3])
                        
                        with col1:
                            if st.button("✅ Approve", key=f"approve_{visit['LogID']}", 
                                        type="primary", use_container_width=True):
                                admin_name = st.session_state.get('user_name', 'Admin')
                                try:
                                    result = db.execute_procedure('sp_ApproveVisit', 
                                                                 (visit['LogID'], admin_name))
                                    if result:
                                        st.success(f"✅ Visit approved!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Approval failed")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        with col2:
                            if st.button("❌ Reject", key=f"reject_{visit['LogID']}", 
                                        use_container_width=True):
                                admin_name = st.session_state.get('user_name', 'Admin')
                                
                                reason = st.text_input(f"Reason for rejection", 
                                                      key=f"reason_{visit['LogID']}")
                                
                                if st.button("Confirm Rejection", key=f"confirm_reject_{visit['LogID']}"):
                                    try:
                                        result = db.execute_procedure('sp_RejectVisit', 
                                                                     (visit['LogID'], admin_name, reason))
                                        if result:
                                            st.info(f"❌ Visit rejected")
                                            st.rerun()
                                        else:
                                            st.error("❌ Rejection failed")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                        
                        st.markdown("---")
                else:
                    st.success("✅ No pending visit requests")
            except Exception as e:
                st.error(f"Error loading pending visits: {str(e)}")
        
        # APPROVED VISITS
        elif visitor_tab == "✅ Approved Visits":
            st.markdown("### ✅ Approved Visits")
            
            try:
                approved_visits = db.fetch_procedure('sp_GetVisitsByStatus', ('Approved',))
                
                if not approved_visits.empty:
                    st.success(f"📊 Total approved visits: {len(approved_visits)}")
                    st.dataframe(approved_visits, use_container_width=True, hide_index=True)
                else:
                    st.info("No approved visits")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # REJECTED VISITS
        elif visitor_tab == "❌ Rejected Visits":
            st.markdown("### ❌ Rejected Visits")
            
            try:
                rejected_visits = db.fetch_procedure('sp_GetVisitsByStatus', ('Rejected',))
                
                if not rejected_visits.empty:
                    st.warning(f"📊 Total rejected visits: {len(rejected_visits)}")
                    st.dataframe(rejected_visits, use_container_width=True, hide_index=True)
                else:
                    st.info("No rejected visits")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # ALL VISITS
        else:
            st.markdown("### 📋 All Visit Records")
            
            try:
                all_visits = db.fetch_procedure('sp_GetAllVisitorLogs')
                
                if not all_visits.empty:
                    st.success(f"📊 Total visit records: {len(all_visits)}")
                    
                    # Filter by status
                    status_filter = st.selectbox("Filter by Status", 
                        ["All", "Pending", "Approved", "Rejected", "Completed"])
                    
                    if status_filter != "All":
                        filtered = all_visits[all_visits['Status'] == status_filter]
                        st.dataframe(filtered, use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(all_visits, use_container_width=True, hide_index=True)
                else:
                    st.info("No visit records")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # ==================== TAB 5: REPORTS ====================                  
    with tab5:
     st.subheader("📋 System Reports")
    
    report_type = st.selectbox(
        "📊 Select Report Type",
        ["Overcrowded Cells", "Upcoming Releases", "Prisoners by Status", "Visit Statistics"],
        key="report_type"
    )
    
    st.markdown("---")
    
    try:
        if report_type == "Overcrowded Cells":
            df = db.fetch_procedure('sp_GetOvercrowdedCells')
            if not df.empty:
                st.error(f"⚠️ {len(df)} overcrowded cell(s)!")
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No overcrowded cells")
        
        elif report_type == "Prisoners by Status":
            status = st.selectbox(
                "Status",
                ["Active", "Released", "Transferred", "Deceased"],
                key="status_filter"
            )

            df = db.fetch_procedure('sp_GetPrisonersByStatus', (status,))

            if not df.empty:
                st.success(f"Found {len(df)} prisoner(s): {status}")
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No prisoners found")

    except Exception as e:
        st.error(f"❌ Error loading report: {e}")
# ==================== TAB 6: ACTIVITY LOG ====================
    with tab6:
        st.subheader("📜 Activity Log")

        st.info("System activities and admin actions")

        try:
            logs = db.fetch_procedure('sp_GetActivityLog')

            if not logs.empty:
                st.success(f"Total Activities: {len(logs)}")
                st.dataframe(logs, use_container_width=True, hide_index=True)
            else:
                st.info("No activity logs found")

        except Exception as e:
            st.error(f"❌ Error loading activity log: {e}")


# ==================== TAB 7: SETTINGS ====================
    with tab7:
        st.subheader("⚙️ System Settings & Administration")

        # ---------------- ADMIN PROFILE ----------------
        st.markdown("### 👤 Admin Profile")

        admin_name = st.session_state.get("user_name", "Admin")
        st.text_input("Username", value=admin_name, disabled=True)

        st.markdown("---")

        # ---------------- SECURITY SETTINGS ----------------
        st.markdown("### 🔐 Security Management")

        with st.expander("🔑 Change Admin Password", expanded=False):
            old_pass = st.text_input("Old Password", type="password", key="old_pass")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirm New Password", type="password", key="confirm_pass")

            if st.button("💾 Update Password", type="primary"):
                if not old_pass or not new_pass or not confirm_pass:
                    st.warning("⚠️ Please fill all fields")
                elif new_pass != confirm_pass:
                    st.error("❌ Passwords do not match")
                else:
                    try:
                        result = db.execute_procedure(
                            'sp_ChangeAdminPassword',
                            (admin_name, old_pass, new_pass)
                        )
                        if result:
                            st.success("✅ Password updated successfully")
                        else:
                            st.error("❌ Incorrect old password")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with st.expander("🛡️ Security Overview", expanded=False):
            try:
                security_stats = db.fetch_procedure('sp_GetSecurityStats')

                if not security_stats.empty:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("👮 Total Officers", security_stats.iloc[0]['TotalOfficers'])
                    col2.metric("🔐 On Duty", security_stats.iloc[0]['OnDuty'])
                    col3.metric("⚠️ Security Alerts", security_stats.iloc[0]['Alerts'])
                else:
                    st.info("No security data available")
            except:
                st.warning("Security stats procedure not found")

        st.markdown("---")

        # ---------------- MEDICAL SETTINGS ----------------
        st.markdown("### 🏥 Medical Management")

        with st.expander("🩺 Medical Overview", expanded=False):
            try:
                medical_stats = db.fetch_procedure('sp_GetMedicalStats')

                if not medical_stats.empty:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("👨‍⚕️ Doctors", medical_stats.iloc[0]['Doctors'])
                    col2.metric("🏥 Active Patients", medical_stats.iloc[0]['ActivePatients'])
                    col3.metric("📅 Upcoming Checkups", medical_stats.iloc[0]['UpcomingCheckups'])
                else:
                    st.info("No medical records found")
            except:
                st.warning("Medical stats procedure not found")

        with st.expander("🚑 Emergency Controls", expanded=False):
            if st.button("🚨 Trigger Medical Emergency"):
                st.warning("🚨 Emergency protocol activated")
                # future: call procedure sp_TriggerMedicalEmergency

        st.markdown("---")

        # ---------------- SYSTEM SETTINGS ----------------
        st.markdown("### ⚙️ System Controls")

        with st.expander("🧩 Feature Toggles", expanded=False):
            visits_enabled = st.toggle("Enable Visitor System", value=True)
            medical_enabled = st.toggle("Enable Medical Module", value=True)
            security_enabled = st.toggle("Enable Security Alerts", value=True)

            if st.button("💾 Save System Settings"):
                st.success("✅ Settings saved successfully")

        with st.expander("🧹 Maintenance Actions", expanded=False):
            if st.button("🔄 Refresh Dashboard"):
                st.rerun()

            if st.button("🗑️ Clear Cache"):
                st.success("Cache cleared successfully")

        st.markdown("---")

        # ---------------- LOGOUT ----------------
        st.markdown("### 🚪 Session")

        if st.button("Logout", type="secondary"):
            st.session_state.clear()
            st.rerun()
