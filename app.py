import streamlit as st
import styles
import auth
import dash_admin
import dash_medical
import dash_security
import dash_visitor
import auth as auth_module

st.set_page_config(
    page_title="Prison Management System - Pakistan",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SESSION STATE INITIALIZATION
if "user_id" not in st.session_state:
    st.session_state.update({
        "user_id": None,
        "role": None,
        "email": None,
        "page": "Home"
    })

# APPLY ENHANCED THEME
st.markdown(styles.get_design_system(), unsafe_allow_html=True)
styles.render_top_nav()

# ===================== NAVIGATION BAR =====================
def render_header():
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        if not st.session_state["user_id"]:
            # Guest Navigation
            menu_options = ["🏠 Home", "📋 About System", "👤 Login", "✍️ Register"]
            selected = st.radio(
                "Navigation", 
                menu_options, 
                horizontal=True, 
                label_visibility="collapsed",
                index=menu_options.index(st.session_state.get("page", "🏠 Home")) if st.session_state.get("page", "🏠 Home") in menu_options else 0
            )
            
            if selected != st.session_state["page"]:
                st.session_state["page"] = selected
                st.rerun()
        else:
            # Logged-in User Header
            st.markdown(f"""
                <div style='text-align:center;padding:15px;background:linear-gradient(135deg, #DDF0FF, #CFEAFF);
                            border-radius:12px;border:1px solid #B6DAF2;'>
                    <span style='font-size:16px;font-weight:600;color:#000;'>
                        👤 Signed in as <span style='color:#10B981;font-weight:700;'>{st.session_state["role"]}</span>
                    </span>
                    <br>
                    <span style='font-size:13px;color:#000;opacity:0.7;'>
                        {st.session_state["email"]}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state["user_id"]:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.update({
                    "user_id": None, 
                    "role": None, 
                    "email": None, 
                    "page": "🏠 Home"
                })
                st.rerun()

render_header()
st.markdown("<br>", unsafe_allow_html=True)

# ===================== PAGES =====================

# HOME PAGE
if not st.session_state["user_id"] and st.session_state["page"] == "🏠 Home":
    with st.container():
        col_text, col_img = st.columns([6, 5])
        
        with col_text:
            st.markdown("""
                <h1 style='font-size:68px;line-height:1.1;font-weight:800;margin-bottom:20px;'>
                    Modern Prison<br>
                    <span class='gradient-text'>Management System</span>
                </h1>
                <h3 style='font-size:22px;line-height:1.5;opacity:0.85;margin-bottom:30px;'>
                    Digitizing Pakistan's prison records for efficiency, transparency, and better governance.
                </h3>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔐 Access Portal →", use_container_width=True):
                    st.session_state["page"] = "👤 Login"
                    st.rerun()
            with col_btn2:
                if st.button("📝 Create Account →", use_container_width=True):
                    st.session_state["page"] = "✍️ Register"
                    st.rerun()
        
        with col_img:
            st.image("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?q=80&w=1600", 
                    use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # FEATURES SECTION
    st.markdown("<h2 style='text-align:center;margin-top:40px;'>System Features</h2>", unsafe_allow_html=True)
    
    feat1, feat2, feat3, feat4 = st.columns(4)
    
    with feat1:
        st.markdown("""
            <div class='metric-card' style='text-align:center;min-height:180px;'>
                <div style='font-size:42px;margin-bottom:10px;'>👥</div>
                <h4>Prisoner Management</h4>
                <p style='font-size:14px;opacity:0.8;'>Complete digital records, sentence tracking, and release calculations</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat2:
        st.markdown("""
            <div class='metric-card' style='text-align:center;min-height:180px;'>
                <div style='font-size:42px;margin-bottom:10px;'>🏥</div>
                <h4>Medical Records</h4>
                <p style='font-size:14px;opacity:0.8;'>Track health checkups, medications, and scheduled treatments</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat3:
        st.markdown("""
            <div class='metric-card' style='text-align:center;min-height:180px;'>
                <div style='font-size:42px;margin-bottom:10px;'>🔒</div>
                <h4>Visitor Security</h4>
                <p style='font-size:14px;opacity:0.8;'>Monitor and approve all visitor activity with detailed logs</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat4:
        st.markdown("""
            <div class='metric-card' style='text-align:center;min-height:180px;'>
                <div style='font-size:42px;margin-bottom:10px;'>📊</div>
                <h4>Smart Reports</h4>
                <p style='font-size:14px;opacity:0.8;'>Automated occupancy tracking and predictive analytics</p>
            </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE (REWRITTEN FOR STREAMLIT)
elif not st.session_state["user_id"] and st.session_state["page"] == "📋 About System":
    st.header("About Prison Management System")
    st.write("""
    Pakistan's prison system has traditionally relied on manual record-keeping, 
    leading to inefficiency, errors, and security risks. This project digitizes 
    prisoner records and administrative processes to enhance transparency and governance.
    """)

    st.subheader("Key Objectives")
    st.write("""
    - Digitize prisoner personal, legal, and medical records  
    - Automate release date calculations with remission tracking  
    - Monitor visitor activity for enhanced security  
    - Track jail occupancy and predict overcrowding  
    - Generate comprehensive reports for policy planning
    """)

    st.subheader("Developer")
    st.write("Developed by **Haseeb Ashfaq** as a full DBMS project using SQL Server and Python (Streamlit).")

# LOGIN PAGE
elif not st.session_state["user_id"] and st.session_state["page"] == "👤 Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align:center;margin-bottom:30px;'>🔐 Portal Access</h2>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
                <div class='metric-card'>
                    <p style='text-align:center;font-size:14px;opacity:0.8;margin-bottom:20px;'>
                        Sign in with your approved account credentials
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
                password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("🚀 Enter Portal", use_container_width=True)
                
                if submit:
                    if not email or not password:
                        st.error("⚠️ Please fill in all fields")
                    else:
                        with st.spinner("Authenticating..."):
                            result = auth.login_user(email, password)
                            
                            if result:
                                st.session_state.update({
                                    "user_id": result[0],
                                    "role": result[1],
                                    "email": email
                                })
                                st.success(f"✅ Welcome back, {result[1]}!")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Invalid credentials or account not approved yet")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 New user? Click 'Register' in the menu to create an account")

# REGISTER PAGE
elif not st.session_state["user_id"] and st.session_state["page"] == "✍️ Register":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 style='text-align:center;margin-bottom:30px;'>✍️ Create New Account</h2>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
                <div class='metric-card'>
                    <p style='text-align:center;font-size:14px;opacity:0.8;margin-bottom:20px;'>
                        ⚠️ <strong>Important:</strong> Your account requires admin approval before activation.
                        You'll receive an email notification once approved.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("register_form"):
                full_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
                email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
                password = st.text_input("🔑 Password", type="password", placeholder="Create a strong password")
                confirm_password = st.text_input("🔑 Confirm Password", type="password", placeholder="Re-enter your password")
                
                role = st.selectbox("🎭 Select Your Role", 
                    ["Medical", "Security", "Visitor"],
                    help="Admin accounts are created internally")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("📝 Submit Registration", use_container_width=True)
                
                if submit:
                    if not all([full_name, email, password, confirm_password]):
                        st.error("⚠️ Please fill in all fields")
                    elif password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating your account..."):
                            result = auth.register_user(email, password, role, full_name)
                            
                            if "SUCCESS" in result or "pending" in result.lower():
                                st.success("✅ Registration successful!")
                                st.info("""
                                    📧 **Next Steps:**
                                    1. Admin has been notified of your registration
                                    2. You'll receive an approval email within 24-48 hours
                                    3. Once approved, you can login with your credentials
                                """)
                                st.balloons()
                            else:
                                st.error(f"❌ {result}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 Already have an account? Click 'Login' in the menu")

# AUTHENTICATED DASHBOARDS
else:
    role = st.session_state["role"]
    
    if role == "Admin":
        dash_admin.show_dashboard()
    elif role == "Medical":
        dash_medical.show_dashboard()
    elif role == "Security":
        dash_security.show_dashboard()
    elif role == "Visitor":
        dash_visitor.show_dashboard()

# FOOTER
st.markdown("""
    <br><br>
    <div style='text-align:center;opacity:0.5;font-size:13px;padding:20px;'>
        🏛️ Prison Management System © 2025 | Developed by Haseeb Ashfaq
    </div>
""", unsafe_allow_html=True)
