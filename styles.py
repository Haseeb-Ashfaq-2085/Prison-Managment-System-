import streamlit as st

def get_design_system():
    # THEME COLORS
    bg_color = "#EAF6FF"       # App background (sky blue)
    card_bg = "#DDF0FF"        # Cards / containers background (light blue)
    text_color = "#000000"     # All text black
    blue = "#2563EB"           # Blue border normal
    green = "#10B981"          # Green hover border
    border_color = "#B6DAF2"   # Light blue border for cards

    # Button hover colors
    btn_hover_bg = "#D4F4DD"   # Light green on hover
    btn_active_bg = "#C6EACB"  # Slightly darker green on click
    btn_normal_bg = "#CFEAFF"  # Normal button background

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* MAIN APP */
    .stApp {{
        background-color: {bg_color};
        font-family: 'Inter', sans-serif;
        color: {text_color};
    }}

    /* FORCE ALL TEXT BLACK */
    h1, h2, h3, h4, h5, h6,
    p, span, div, label, small, li, ul, ol, a {{
        color: {text_color} !important;
    }}

    /* CARDS / CONTAINERS */
    .metric-card,
    div[data-testid="stContainer"],
    [data-testid="stExpander"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        border-color: {green};
    }}

    /* TABS */
    .stTabs [data-baseweb="tab"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        border-radius: 8px;
        font-weight: 600;
        color: {text_color} !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #CFEAFF;
        border-color: {blue};
        color: {text_color} !important;
    }}

    /* BUTTONS - LIGHT BLUE NORMAL, LIGHT GREEN HOVER */
    div.stButton > button {{
        background-color: {btn_normal_bg} !important;
        color: {text_color} !important;
        border: 1px solid {blue};
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 22px;
        box-shadow: none;
        transition: all 0.2s ease;
    }}

    div.stButton > button:hover {{
        background-color: {btn_hover_bg} !important;
        color: {text_color} !important;
        border-color: {green};
    }}

    div.stButton > button:active {{
        background-color: {btn_active_bg} !important;
        color: {text_color} !important;
    }}

    /* INPUT FIELDS */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: #F0F9FF;
        border: 1px solid {border_color};
        border-radius: 8px;
        color: {text_color} !important;
    }}

    .stTextInput input::placeholder {{
        color: {text_color};
        opacity: 0.6;
    }}

    /* ALERTS / NOTIFICATIONS */
    div[data-testid="stAlert"],
    div[data-testid="stNotification"] {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        color: {text_color} !important;
    }}

    /* GRADIENT TEXT (HEADLINES ONLY) */
    .gradient-text {{
        background: linear-gradient(135deg, {blue}, {green});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* ENSURE ALL BUTTON TEXT IS BLACK */
    button, button * {{
        color: {text_color} !important;
    }}

    </style>
    """

def render_top_nav():
    st.markdown("""
    <div style="
        height:4px;
        width:100%;
        position:fixed;
        top:0;
        left:0;
        z-index:99999;
        background: #2563EB;
    "></div>
    """, unsafe_allow_html=True)
