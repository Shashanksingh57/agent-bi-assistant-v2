# streamlit_layout_ui.py - Complete Enhanced Version with Multi-file Upload & Progress Tracking

import os
import json
import re
import requests
import streamlit as st
import base64
from dotenv import load_dotenv
from file_parsers import (
    parse_kpi_excel, parse_kpi_word,
    parse_data_dictionary_excel, parse_data_dictionary_csv,
    validate_kpi_list, validate_data_dictionary
)
from persona_manager import (
    initialize_persona_state, get_current_persona, should_show_feature,
    get_persona_prompt_modifier, render_onboarding_modal, render_persona_indicator,
    render_adaptive_help, render_progress_indicator, render_estimated_time,
    get_adaptive_button_text, render_example_content
)
from report_generators import (
    generate_kpi_summary_text, generate_kpi_business_report, generate_single_kpi_section,
    generate_data_dictionary_summary_text, generate_data_dictionary_business_report,
    generate_combined_business_summary, generate_combined_business_report
)




# ─── Load Custom CSS ──────────────────────────────────────────────────────────────
def load_custom_css():
    """Load custom CSS for branding and styling"""
    st.markdown("""
    <style>
    /* Brand Colors */
    :root {
        --brand-blue: #0C62FB;
        --brand-grey: #6c757d;
        --light-grey: #f8f9fa;
        --border-grey: #dee2e6;
    }
    
    /* Sidebar logo styling */
    .sidebar-logo {
        display: flex;
        justify-content: flex-start;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-logo img {
        height: 22px;
        width: auto;
        max-width: 110px;
    }
    
    /* Sidebar styling - grey theme */
    section[data-testid="stSidebar"] {
        background-color: var(--light-grey);
        border-right: 1px solid var(--border-grey);
    }
    
    /* Navigation buttons - white boxes with grey borders and black text */
    .nav-button-container .stButton > button {
        background-color: white;
        color: black;
        border: 1px solid var(--border-grey);
        border-radius: 8px;
        font-weight: 500;
        padding: 0.75rem 1.25rem;
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        transition: all 0.3s ease;
        margin: 0.25rem 0;
    }
    
    .nav-button-container .stButton > button:hover {
        background-color: #f8f9fa;
        border-color: var(--brand-grey);
        color: black;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Active navigation button */
    .nav-active .stButton > button {
        background-color: white;
        border-color: var(--brand-blue);
        color: black;
        box-shadow: inset 3px 0 0 var(--brand-blue);
        font-weight: 600;
    }
    
    /* Regular buttons in main content - white with grey border */
    .stButton > button {
        background-color: white;
        color: black;
        border: 1px solid var(--border-grey);
        border-radius: 8px;
        font-weight: 500;
        padding: 0.75rem 1.25rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa;
        border-color: var(--brand-grey);
        color: black;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Primary buttons - keep blue but with black text when needed */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--brand-blue) 0%, #0A52D9 100%);
        border: none;
        color: white;
        box-shadow: 0 3px 10px rgba(12, 98, 251, 0.3);
        font-weight: 600;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0A52D9 0%, #083DAD 100%);
        box-shadow: 0 5px 15px rgba(12, 98, 251, 0.4);
        transform: translateY(-1px);
    }
    
    /* Form submit buttons - make them blue like primary buttons */
    .stForm .stButton > button[type="submit"] {
        background: linear-gradient(135deg, var(--brand-blue) 0%, #0A52D9 100%);
        border: none;
        color: white;
        box-shadow: 0 3px 10px rgba(12, 98, 251, 0.3);
        font-weight: 600;
    }

    .stForm .stButton > button[type="submit"]:hover {
        background: linear-gradient(135deg, #0A52D9 0%, #083DAD 100%);
        box-shadow: 0 5px 15px rgba(12, 98, 251, 0.4);
        transform: translateY(-1px);
    }

    /* Alternative: Target all form buttons */
    .stForm button {
        background: linear-gradient(135deg, var(--brand-blue) 0%, #0A52D9 100%) !important;
        border: none !important;
        color: white !important;
    }

    /* Progress bars - keep blue */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--brand-blue) 0%, #0A52D9 100%);
    }
    
    /* Metrics styling - white with grey border */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid var(--border-grey);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    [data-testid="metric-container"] > div {
        color: black;
    }
    
    /* Info boxes - keep blue accent but lighter */
    .stInfo {
        background-color: rgba(12, 98, 251, 0.05);
        border-left: 4px solid var(--brand-blue);
        border-radius: 4px;
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.05);
        border-left: 4px solid #28a745;
        border-radius: 4px;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.05);
        border-left: 4px solid #ffc107;
        border-radius: 4px;
    }
    
    .stError {
        background-color: rgba(220, 53, 69, 0.05);
        border-left: 4px solid #dc3545;
        border-radius: 4px;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        color: black;
        font-weight: 600;
        background-color: white;
        border: 1px solid var(--border-grey);
        border-radius: 4px;
    }
    
    /* Select boxes and inputs - white with grey border */
    .stSelectbox > div > div {
        background-color: white;
        border-color: var(--border-grey);
    }
    
    .stTextInput > div > div > input {
        background-color: white;
        border-color: var(--border-grey);
        color: black;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--brand-blue);
        box-shadow: 0 0 0 1px var(--brand-blue);
    }
    
    /* File uploader - white with grey border */
    .stFileUploader > div {
        background-color: white;
        border: 2px dashed var(--border-grey);
        border-radius: 8px;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--brand-grey);
    }
    
    /* Download buttons - keep green */
    .stDownloadButton > button {
        background-color: #28a745;
        border-color: #28a745;
        color: white;
    }
    
    .stDownloadButton > button:hover {
        background-color: #218838;
        border-color: #1e7e34;
    }
    
    /* Reset button - different styling */
    .reset-button .stButton > button {
        background-color: #f8f9fa;
        color: #6c757d;
        border: 1px solid #dee2e6;
    }
    
    .reset-button .stButton > button:hover {
        background-color: #e9ecef;
        color: #495057;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    </style>
    """, unsafe_allow_html=True)

# ─── Logo Functions ────────────────────────────────────────────────────────────
def get_logo_base64():
    """Load logo from file and convert to base64 for embedding"""
    # Try different logo file names
    possible_logos = ["logo.png", "logo.jpg", "logo.jpeg", "logo.svg", "assets/logo.png"]
    
    for logo_path in possible_logos:
        try:
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_bytes = f.read()
                    logo_base64 = base64.b64encode(logo_bytes).decode()
                    
                    # Determine MIME type
                    if logo_path.lower().endswith('.svg'):
                        mime_type = "image/svg+xml"
                    elif logo_path.lower().endswith(('.jpg', '.jpeg')):
                        mime_type = "image/jpeg"
                    else:
                        mime_type = "image/png"
                    
                    return f"data:{mime_type};base64,{logo_base64}"
        except Exception as e:
            continue
    
    # Fallback: Create a branded SVG logo with your brand color
    fallback_svg = """
    <svg width="180" height="60" viewBox="0 0 180 60" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#0C62FB;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#0A52D9;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="180" height="60" rx="12" fill="url(#brandGradient)"/>
        <text x="90" y="25" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="14" font-weight="bold">
            BI Assistant
        </text>
        <text x="90" y="42" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-family="Arial, sans-serif" font-size="10">
            Agentic Analytics
        </text>
        <circle cx="25" cy="30" r="12" fill="rgba(255,255,255,0.2)"/>
        <circle cx="155" cy="30" r="12" fill="rgba(255,255,255,0.2)"/>
        <rect x="20" y="25" width="10" height="10" fill="white" opacity="0.8"/>
        <rect x="150" y="25" width="10" height="10" fill="white" opacity="0.8"/>
    </svg>
    """
    return f"data:image/svg+xml;base64,{base64.b64encode(fallback_svg.encode()).decode()}"


load_dotenv()
API_TOKEN   = os.getenv("OPENAI_API_KEY")
FASTAPI_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Agentic BI Assistant", layout="wide")
state = st.session_state

load_custom_css()

# Logo is now displayed in the sidebar navigation

# ─── Initialize session state ───────────────────────────────────────────────────
for key, default in {
    "page": "Data Model",
    "model_metadata": None,
    "data_prep_instructions": "",
    "wireframe_json": "",
    "dev_instructions": "",
    "sprint_stories": [],
    "over_under_capacity": None,
    "input_method": "text",
    "ai_analysis_result": None,
    "current_platform": "Power BI",
    "kpi_list": None,
    "data_dictionary": None
}.items():
    if key not in state:
        state[key] = default

# Initialize persona state
initialize_persona_state()

# ─── Show Onboarding if Needed ──────────────────────────────────────────────────
if st.session_state.show_onboarding and not st.session_state.onboarding_completed:
    render_onboarding_modal()
    st.stop()

# ─── Helper Functions ────────────────────────────────────────────────────────────
def safe_get_dict(obj, default=None):
    """Safely get dictionary from object, handling string/None cases"""
    if obj is None:
        return default or {}
    if isinstance(obj, str):
        try:
            import json
            return json.loads(obj)
        except (json.JSONDecodeError, ValueError):
            return default or {}
    if isinstance(obj, dict):
        return obj
    return default or {}

def safe_get_list(obj, default=None):
    """Safely get list from object"""
    if obj is None:
        return default or []
    if isinstance(obj, str):
        try:
            import json
            parsed = json.loads(obj)
            return parsed if isinstance(parsed, list) else default or []
        except (json.JSONDecodeError, ValueError):
            return default or []
    if isinstance(obj, list):
        return obj
    return default or []

def tidy_md(md: str) -> str:
    """Clean up markdown formatting for better display"""
    md = re.sub(r'(?m)^(## .+)$', r'\1\n', md)
    md = re.sub(r'(?m)^(\d+\.)', r'\n\1', md)
    md = re.sub(r'(?m)^\s*-\s+', r'  - ', md)
    return md.strip()

def display_data_quality_insights(model_metadata: dict):
    """Display data quality insights based on the model"""
    if not model_metadata:
        return
    
    st.subheader("🔍 Data Quality Insights")
    
    model_dict = safe_get_dict(model_metadata)
    if not model_dict:
        st.warning("Could not parse data model for quality analysis")
        return
    
    tables = safe_get_list(model_dict.get("tables", []))
    total_issues = 0
    issues_found = []
    recommendations = []
    
    for table in tables:
        table_dict = safe_get_dict(table)
        if not table_dict:
            continue
            
        # Support both schema formats: "table_name" (detailed) and "name" (simple)
        table_name = table_dict.get("table_name", "") or table_dict.get("name", "")
        columns = safe_get_list(table_dict.get("columns", []))
        
        nullable_ids = []
        text_amounts = []
        text_dates = []
        
        for c in columns:
            # Handle both formats: object with details OR simple string
            if isinstance(c, str):
                # Simple format: just column name as string
                col_name = c
                col_type = "string"  # default type
                is_nullable = True
            else:
                # Detailed format: object with column details
                col_dict = safe_get_dict(c)
                if not col_dict:
                    continue
                    
                col_name = col_dict.get("column_name", "")
                col_type = str(col_dict.get("data_type", "")).lower()
                is_nullable = col_dict.get("nullable", True)
            
            if "id" in col_name.lower() and is_nullable:
                nullable_ids.append(col_name)
            
            if any(word in col_name.lower() for word in ["amount", "price", "cost", "salary"]) and "varchar" in col_type:
                text_amounts.append(col_name)
            
            if "date" in col_name.lower() and "varchar" in col_type:
                text_dates.append(col_name)
        
        # Check for primary keys in both formats
        no_primary_key = not any(
            (isinstance(c, str) and False) or  # simple format has no primary keys
            (isinstance(c, dict) and safe_get_dict(c).get("primary_key", False))
            for c in columns
        )
        
        if nullable_ids:
            issues_found.append(f"🔴 **{table_name}**: ID columns that allow nulls: {', '.join(nullable_ids)}")
            recommendations.append(f"Set {', '.join(nullable_ids)} as NOT NULL to ensure data integrity")
            total_issues += len(nullable_ids)
        
        if text_amounts:
            issues_found.append(f"🟡 **{table_name}**: Monetary columns stored as text: {', '.join(text_amounts)}")
            recommendations.append(f"Convert {', '.join(text_amounts)} to DECIMAL/CURRENCY type for calculations")
            total_issues += len(text_amounts)
        
        if text_dates:
            issues_found.append(f"🟡 **{table_name}**: Date columns stored as text: {', '.join(text_dates)}")
            recommendations.append(f"Convert {', '.join(text_dates)} to DATE/DATETIME type for time-based analysis")
            total_issues += len(text_dates)
        
        if no_primary_key:
            issues_found.append(f"🟡 **{table_name}**: No primary key defined")
            recommendations.append(f"Define a primary key for {table_name} to ensure unique record identification")
            total_issues += 1
    
    if issues_found:
        col1, col2 = st.columns(2)
        
        with col1:
            st.warning(f"Found {total_issues} potential data quality issues:")
            for issue in issues_found:
                st.markdown(issue)
        
        with col2:
            st.info("📋 **Recommendations:**")
            for rec in recommendations:
                st.markdown(f"• {rec}")
        
        st.markdown("💡 These issues will be addressed in the generated preparation steps.")
    else:
        st.success("✅ No obvious data quality issues detected!")

def safe_display_table_summary(tables, data_dictionary=None):
    """Safely display table summary with expandable column details"""
    st.markdown("**📋 Tables in Your Data Model:**")
    
    for table in tables:
        table_dict = safe_get_dict(table)
        if not table_dict:
            continue
            
        # Support both schema formats: "table_name" (detailed) and "name" (simple)
        table_name = table_dict.get("table_name", "") or table_dict.get("name", "Unknown")
        columns = safe_get_list(table_dict.get("columns", []))
        
        # Count column types
        date_cols = []
        numeric_cols = []
        text_cols = []
        key_cols = []
        
        for c in columns:
            # Handle both formats: object with details OR simple string
            if isinstance(c, str):
                # Simple format: just column name as string
                col_name = c
                col_type = "string"  # default type
                
                # Enhanced type detection using data dictionary for simple format
                if data_dictionary and table_name in data_dictionary:
                    dict_table = data_dictionary[table_name]
                    if col_name in dict_table:
                        dict_col_info = dict_table[col_name]
                        dict_type = str(dict_col_info.get("type", "")).lower()
                        if dict_type:
                            col_type = dict_type
                
                col_dict = {
                    "column_name": col_name,
                    "data_type": col_type,
                    "nullable": True,
                    "primary_key": False,
                    "foreign_key": None
                }
                is_primary = False
                is_foreign = False
            else:
                # Detailed format: object with column details
                col_dict = safe_get_dict(c)
                if not col_dict:
                    continue
                
                col_type = str(col_dict.get("data_type", "")).lower()
                is_primary = col_dict.get("primary_key", False)
                foreign_key_val = col_dict.get("foreign_key", None)
                is_foreign = foreign_key_val is not None and foreign_key_val != False and str(foreign_key_val).strip() != ""
                
                # Enhanced type detection using data dictionary
                col_name = col_dict.get("column_name", "")
                if data_dictionary and table_name in data_dictionary:
                    dict_table = data_dictionary[table_name]
                    if col_name in dict_table:
                        dict_col_info = dict_table[col_name]
                        dict_type = str(dict_col_info.get("type", "")).lower()
                        # Use data dictionary type if available, otherwise fallback to schema type
                        if dict_type:
                            col_type = dict_type
            
            if is_primary or is_foreign:
                key_cols.append(col_dict)
            
            # More flexible type detection
            if any(t in col_type for t in ["date", "time", "timestamp"]):
                date_cols.append(col_dict)
            elif any(t in col_type for t in ["int", "float", "decimal", "numeric", "money", "number", "double", "real", "bigint", "smallint", "tinyint"]):
                numeric_cols.append(col_dict)
            elif any(t in col_type for t in ["varchar", "char", "text", "string", "nvarchar", "nchar", "clob"]):
                text_cols.append(col_dict)
            else:
                # If type doesn't match any category, treat as text
                text_cols.append(col_dict)
        
        # Create expandable section for each table
        with st.expander(f"📊 **{table_name}** ({len(columns)} columns)", expanded=False):
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Columns", len(columns))
            with col2:
                st.metric("Key Columns", len(key_cols))
            with col3:
                st.metric("Numeric", len(numeric_cols))
            with col4:
                st.metric("Text", len(text_cols))
            
            # Column details
            st.markdown("### 📋 Column Details")
            
            # Debug: Show all columns if none are categorized
            if not key_cols and not numeric_cols and not date_cols and not text_cols:
                st.markdown("**All Columns:**")
                for c in columns:
                    col_dict = safe_get_dict(c)
                    if col_dict:
                        col_name = col_dict.get("column_name", "Unknown")
                        col_type = col_dict.get("data_type", "Unknown")
                        nullable = "nullable" if col_dict.get("nullable", True) else "not null"
                        st.markdown(f"- `{col_name}` ({col_type}) - {nullable}")
            
            # Group columns by type
            if key_cols:
                st.markdown("**🔑 Key Columns:**")
                for col in key_cols:
                    col_name = col.get("column_name", "")
                    col_type = col.get("data_type", "")
                    is_primary = col.get("primary_key", False)
                    foreign_key_val = col.get("foreign_key", None)
                    is_foreign = foreign_key_val is not None and foreign_key_val != False and str(foreign_key_val).strip() != ""
                    key_type = "PK" if is_primary else "FK"
                    st.markdown(f"- `{col_name}` ({col_type}) - **{key_type}**")
            
            if numeric_cols:
                st.markdown("**🔢 Numeric Columns:**")
                for col in numeric_cols:
                    if col not in key_cols:  # Avoid duplicates
                        col_name = col.get("column_name", "")
                        col_type = col.get("data_type", "")
                        nullable = "nullable" if col.get("nullable", True) else "not null"
                        st.markdown(f"- `{col_name}` ({col_type}) - {nullable}")
            
            if date_cols:
                st.markdown("**📅 Date/Time Columns:**")
                for col in date_cols:
                    col_name = col.get("column_name", "")
                    col_type = col.get("data_type", "")
                    nullable = "nullable" if col.get("nullable", True) else "not null"
                    st.markdown(f"- `{col_name}` ({col_type}) - {nullable}")
            
            if text_cols:
                st.markdown("**📝 Text Columns:**")
                for col in text_cols:
                    if col not in key_cols:  # Avoid duplicates
                        col_name = col.get("column_name", "")
                        col_type = col.get("data_type", "")
                        nullable = "nullable" if col.get("nullable", True) else "not null"
                        st.markdown(f"- `{col_name}` ({col_type}) - {nullable}")

def analyze_model_complexity(model_metadata):
    """Analyze the complexity of the data model"""
    if not model_metadata:
        return "Unknown"
    
    model_dict = safe_get_dict(model_metadata)
    if not model_dict:
        return "Unknown"
    
    tables = safe_get_list(model_dict.get("tables", []))
    relationships = safe_get_list(model_dict.get("relationships", []))
    
    total_columns = 0
    for table in tables:
        table_dict = safe_get_dict(table)
        if table_dict:
            columns = safe_get_list(table_dict.get("columns", []))
            total_columns += len(columns)
    
    if len(tables) <= 3 and total_columns <= 20 and len(relationships) <= 3:
        return "Simple"
    elif len(tables) <= 10 and total_columns <= 100 and len(relationships) <= 10:
        return "Moderate"
    else:
        return "Complex"

# ─── Sidebar Navigation with Logo ───────────────────────────────────────────────
# Display logo in sidebar
logo_src = get_logo_base64()
st.sidebar.markdown(f'''
<div class="sidebar-logo">
    <img src="{logo_src}" alt="BI Assistant Logo">
</div>
''', unsafe_allow_html=True)

# ─── Sidebar Navigation & Controls ──────────────────────────────────────────────
st.sidebar.markdown("<h3 style='color: black; font-size:18px; margin-bottom: 1rem; margin-top: 0.5rem;'>🧭 Navigation & Controls</h3>", unsafe_allow_html=True)

# Navigation buttons with grey/white theme
pages = [
    ("🏗️ Data Model", "Data Model"),
    ("🔧 Data Prep", "Data Prep"), 
    ("📊 Dashboard Dev", "Dashboard Dev"),
    ("📋 Sprint Board", "Sprint Board"),
    ("❓ Help", "Help")
]

for icon_title, page_key in pages:
    # Add CSS class for active state
    if state.page == page_key:
        st.sidebar.markdown('<div class="nav-button-container nav-active">', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
    
    if st.sidebar.button(icon_title, use_container_width=True, key=f"nav_{page_key}"):
        state.page = page_key
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Current page indicator
st.sidebar.markdown(f"""
<div style='background-color: white; border: 1px solid #dee2e6; padding: 0.5rem; border-radius: 4px; margin: 1rem 0; text-align: center;'>
    <strong style='color: black;'>📍 Current: {state.page}</strong>
</div>
""", unsafe_allow_html=True)

# Persona indicator
render_persona_indicator()

# Reset button with different styling
if state.page != "Data Model":
    st.sidebar.markdown('<div class="nav-button-container reset-button">', unsafe_allow_html=True)
    if st.sidebar.button("🔄 Reset All", use_container_width=True, key="reset_all"):
        for k in ["model_metadata","data_prep_instructions","wireframe_json",
                  "dev_instructions","sprint_stories","over_under_capacity","ai_analysis_result"]:
            state[k] = None if k=="model_metadata" else ([] if isinstance(state[k], list) else "")
        state.page = "Data Model"
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Branding info
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: #6c757d; font-size: 0.75rem; margin-top: 1.5rem; padding: 0.75rem; background-color: white; border: 1px solid #dee2e6; border-radius: 8px;'>
        <strong style='color: black;'>Agentic BI Assistant</strong><br>
        <span>AI-Powered Dashboard Development</span>
    </div>
    """, 
    unsafe_allow_html=True
)
# ─── FastAPI POST helper ─────────────────────────────────────────────────────────
def call_api(endpoint, payload, timeout=900, max_retries=2):
    """Helper function to call FastAPI endpoints with retry logic and better timeout handling"""
    import time
    
    url = f"{FASTAPI_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type":  "application/json"
    }
    
    for attempt in range(max_retries + 1):
        try:
            # Add slight delay between retries
            if attempt > 0:
                wait_time = 2 ** attempt  # Exponential backoff: 2, 4 seconds
                st.info(f"🔄 Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(wait_time)
            
            r = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if r.status_code != 200:
                if attempt == max_retries:  # Last attempt
                    st.error(f"❌ {endpoint} error {r.status_code}: {r.text}")
                return {}
            return r.json()
            
        except requests.exceptions.Timeout as e:
            if attempt == max_retries:  # Last attempt
                st.error(f"❌ Request timed out after {timeout} seconds. The AI is taking longer than expected. Please try chunked processing for large models.")
                st.info(f"🔍 **Debug info**: Timeout was set to {timeout} seconds. Error: {str(e)}")
            continue
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:  # Last attempt
                st.error(f"❌ Connection error: {str(e)}")
            continue
    
    return {}

# ─── AI Vision Helper Functions ──────────────────────────────────────────────────
def optimize_image_for_analysis(uploaded_file):
    """Optimize image for faster AI analysis while maintaining quality for GPT-4o Vision"""
    from PIL import Image
    import io
    
    # Read the image
    image = Image.open(uploaded_file)
    
    # Convert to RGB if needed (for JPEG compatibility)
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    # Get original dimensions
    width, height = image.size
    original_size = len(uploaded_file.getvalue())
    
    # For GPT-4o Vision, we can use higher resolution for better accuracy
    # But need to balance with API speed and limits
    max_dimension = 2048  # Increased for better AI vision analysis
    
    # Only resize if image is very large
    if max(width, height) > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int((height * max_dimension) / width)
        else:
            new_height = max_dimension
            new_width = int((width * max_dimension) / height)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Save to bytes with optimized settings
    img_byte_arr = io.BytesIO()
    
    # Use higher quality for AI Vision analysis - GPT-4o can handle larger images
    # But compress if the file is very large
    if original_size > 5 * 1024 * 1024:  # If original > 5MB
        quality = 80  # More compression
    elif original_size > 2 * 1024 * 1024:  # If original > 2MB  
        quality = 85  # Moderate compression
    else:
        quality = 92  # High quality for smaller files
    
    image.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
    
    return img_byte_arr.getvalue()

def upload_and_analyze_image(uploaded_file, platform, analysis_type="ai_vision"):
    """Handle image upload and analysis with progress tracking and optimization"""
    if not uploaded_file:
        return None
    
    # Get original file info
    original_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    
    # More restrictive size limit for faster processing
    if original_size_mb > 5:
        st.warning("⚠️ Large image detected. Compressing for faster analysis...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Optimize image for faster processing
        status_text.text("🔄 Optimizing image for analysis...")
        progress_bar.progress(10)
        
        # Compress and resize image if needed
        optimized_file_data = optimize_image_for_analysis(uploaded_file)
        optimized_size_mb = len(optimized_file_data) / (1024 * 1024)
        
        if optimized_size_mb > 8:
            st.error("⚠️ Image still too large after optimization. Please use a smaller image or lower resolution.")
            return None
        
        if analysis_type == "ai_vision":
            status_text.text("📤 Uploading optimized image...")
            progress_bar.progress(25)
            
            files = {"file": (uploaded_file.name, optimized_file_data, uploaded_file.type)}
            data = {"platform": platform}
            
            status_text.text("🧠 AI Vision analyzing layout... (This may take 5-15 minutes)")
            progress_bar.progress(50)
            
            # Show helpful message while processing
            processing_msg = st.info("💡 **AI Vision is working**: GPT-4o is carefully analyzing your wireframe. Complex images may take up to 15 minutes - please be patient!")
            
            # Much longer timeout for AI Vision processing - revert to working timeouts
            try:
                response = requests.post(
                    f"{FASTAPI_URL}/analyze-image",
                    files=files,
                    data=data,
                    timeout=900  # Increased to 15 minutes to match backend (was working before)
                )
                # Clear the processing message on success
                processing_msg.empty()
            except requests.exceptions.Timeout:
                processing_msg.empty()
                progress_bar.progress(100)
                status_text.text("❌ Analysis timed out")
                st.error("🕐 **AI Vision timed out.** This can happen with complex images. Please try:")
                st.markdown("""
                - **Use a simpler image**: Less detailed wireframes process faster
                - **Try again**: Sometimes the AI service is busy
                - **Check image quality**: Ensure the wireframe is clear and well-lit
                - **Reduce image size**: Try resizing to 1024x768 or smaller
                """)
                return None
            except requests.exceptions.RequestException as e:
                processing_msg.empty()
                progress_bar.progress(100)
                status_text.text("❌ Connection error")
                st.error(f"Connection error: {str(e)}")
                return None
            
            progress_bar.progress(75)
            
            if response.status_code == 200:
                result = response.json()
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Show optimization info if compression was significant
                if original_size_mb > optimized_size_mb * 1.2:
                    st.info(f"📊 Image optimized: {original_size_mb:.1f}MB → {optimized_size_mb:.1f}MB for faster processing")
                
                return result
            else:
                progress_bar.progress(100)
                status_text.text("❌ Analysis failed")
                
                if response.status_code == 408 or "timeout" in response.text.lower():
                    st.error("⏱️ **Analysis timed out.** Try these solutions:")
                    st.markdown("""
                    - Use a **smaller image** (< 2MB recommended)
                    - **Crop** the wireframe to focus on the main layout
                    - **Reduce image resolution** (1024x768 or smaller)
                    - Try the **Text Description** method instead
                    """)
                else:
                    st.error(f"❌ AI Vision analysis failed (Error {response.status_code})")
                    with st.expander("🔍 Error Details"):
                        st.code(response.text)
                return None
                
        elif analysis_type == "simple_detection":
            status_text.text("🔍 Detecting layout shapes...")
            progress_bar.progress(50)
            
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            response = requests.post(
                f"{FASTAPI_URL}/detect-layout",
                files=files,
                timeout=300
            )
            
            progress_bar.progress(100)
            
            if response.status_code == 200:
                result = response.json()
                status_text.text("✅ Detection complete!")
                return result
            else:
                status_text.text("❌ Detection failed")
                st.error(f"❌ Layout detection failed (Error {response.status_code})")
                return None
                
    except requests.exceptions.Timeout:
        progress_bar.progress(100)
        status_text.text("⏰ Request timed out")
        st.error("⏱️ **Analysis timed out.** Try these solutions:")
        st.markdown("""
        - Use a **smaller image** (< 2MB recommended)
        - **Crop** the wireframe to focus on the main layout
        - **Reduce image resolution** (1024x768 or smaller)
        - Try the **Text Description** method instead
        - Check your internet connection
        """)
        return None
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("❌ Error occurred")
        
        # Better error messages based on error type
        error_str = str(e).lower()
        if "timeout" in error_str:
            st.error("⏱️ **Analysis timed out.** Please try a smaller image or use text description instead.")
        elif "connection" in error_str or "network" in error_str:
            st.error("🌐 **Connection error.** Please check your internet connection and try again.")
        elif "memory" in error_str or "size" in error_str:
            st.error("💾 **Image too large.** Please use a smaller image (< 2MB recommended).")
        else:
            st.error(f"❌ **Analysis error:** {str(e)}")
            st.markdown("**Try these solutions:**")
            st.markdown("- Use a smaller, clearer image\n- Try the Text Description method\n- Refresh the page and try again")
        
        return None

# ─── Page: Data Model (Simplified - removed Enterprise Schema Alternative) ───────────
if state.page == "Data Model":
    st.header("1️⃣ Define Your Data Model")
    st.markdown(
        "**Overview:** Upload an existing JSON schema or build one from SQL DDLs.  \n"
        "When ready, navigate to **Data Prep** via the sidebar."
    )
    
    # Show progress for beginners
    render_progress_indicator(1, 4, "Define Data Model")
    
    # Show estimated time for task
    render_estimated_time("data model setup", 10)
    
    # Adaptive help for beginners
    render_adaptive_help(
        "What is a Data Model?",
        """A data model defines the structure of your data - the tables, columns, and relationships 
        between them. Think of it as the blueprint for your dashboard's data foundation.
        
        **Example:** A sales data model might have:
        - Customer table (customer info)
        - Product table (product details)
        - Sales table (transactions)
        - Relationships connecting them"""
    )

    mode = st.radio("Mode:", ["Upload JSON", "Build from SQL"], index=0)
    
    if mode == "Upload JSON":
        f = st.file_uploader("Upload data-model JSON", type=["json"])
        if f:
            try:
                state.model_metadata = json.load(f)
                st.success("✅ Data model loaded.")
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
    
    else:  # Build from SQL
        st.markdown("### 📁 Upload DDL Files")
        
        # Show different info based on persona
        persona = get_current_persona()
        if persona and persona.get("experience_level") == "beginner":
            st.info("💡 **What are DDL files?** DDL (Data Definition Language) files contain SQL CREATE TABLE statements that define your database structure. Upload one file per table, plus a relationships file.")
            
            render_example_content(
                "Sample DDL File",
                """```sql
-- customers.sql
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    country VARCHAR(50)
);
```"""
            )
        else:
            st.info("💡 Upload multiple table DDL files at once, plus one relationships file.")
        
        # Multi-file uploader for DDL files
        ddl_files = st.file_uploader(
            "Upload Table DDL Files (.sql, .txt)", 
            type=["sql", "txt"], 
            accept_multiple_files=True,
            help="Select multiple files containing your CREATE TABLE statements"
        )
        
        # Single relationships file
        rel_file = st.file_uploader(
            "Upload Relationships File (.sql, .txt)", 
            type=["sql", "txt"],
            help="Single file containing ALTER TABLE or relationship definitions"
        )
        
        # Show uploaded files summary
        if ddl_files:
            st.markdown("### 📋 Uploaded Files Summary")
            
            total_size = 0
            ddl_contents = []
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**📄 Table DDL Files:**")
                for i, file in enumerate(ddl_files, 1):
                    content = file.getvalue().decode("utf-8")
                    file_size = len(content)
                    total_size += file_size
                    ddl_contents.append(content)
                    
                    st.markdown(f"- **{file.name}** ({file_size:,} characters)")
            
            with col2:
                if rel_file:
                    rel_content = rel_file.getvalue().decode("utf-8")
                    rel_size = len(rel_content)
                    total_size += rel_size
                    
                    st.markdown("**🔗 Relationships File:**")
                    st.markdown(f"- **{rel_file.name}** ({rel_size:,} characters)")
                else:
                    st.warning("⚠️ Relationships file required")
            
            # Schema size analysis
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📁 Total Files", len(ddl_files) + (1 if rel_file else 0))
            with col2:
                st.metric("📊 Total Size", f"{total_size:,} chars")
            with col3:
                if total_size < 10000:
                    complexity = "Simple"
                    est_time = "30-60s"
                    color = "🟢"
                elif total_size < 50000:
                    complexity = "Moderate" 
                    est_time = "1-2 min"
                    color = "🟡"
                else:
                    complexity = "Complex"
                    est_time = "2-5 min"
                    color = "🔴"
                
                st.metric("⏱️ Est. Time", est_time)
            
            # Size-based warnings and tips
            if total_size > 50000:  # Large schema
                st.warning(f"🔴 **Large Schema Detected** ({total_size:,} characters)")
                st.markdown("""
                **📋 For large schemas:**
                - ✅ Processing may take 2-5 minutes
                - ✅ Consider starting with core tables first
                - ✅ You can always add more tables later
                - ✅ Enterprise schemas work best with manual JSON editing
                """)
                
                if len(ddl_files) > 10:
                    st.info("💡 **Tip:** Try uploading 5-10 most important tables first, then expand your model later.")
                
                proceed = st.checkbox("I understand this may take several minutes to process")
                if not proceed:
                    st.stop()
                    
            elif total_size > 20000:  # Medium schema
                st.info(f"🟡 **Medium Schema** ({total_size:,} characters) - Processing should take 1-2 minutes")
            else:  # Small schema
                st.success(f"🟢 **Manageable Schema** ({total_size:,} characters) - Should process quickly!")
            
            # Generate button with enhanced progress tracking
            button_text = get_adaptive_button_text("Generate Model JSON", "generate")
            if rel_file and st.button(f"🚀 {button_text}", type="primary", use_container_width=True):
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                base_timeout = 300  # Start with 5 minutes
                size_factor = max(1, total_size // 10000)
                dynamic_timeout = min(900, base_timeout + (size_factor * 60))  # Max 15 minutes
                
                try:
                    status_text.text(f"🔄 Processing {len(ddl_files)} DDL files... (Est. {est_time})")
                    progress_bar.progress(10)
                    
                    with st.spinner(f"🤖 AI is analyzing your schema... This may take up to {dynamic_timeout//60} minutes for large schemas"):
                        resp = call_api("generate-model", {
                            "tables_sql": ddl_contents,
                            "relationships_sql": rel_content
                        }, timeout=dynamic_timeout)
                        
                        progress_bar.progress(75)
                        status_text.text("🔍 Validating generated model...")
                        
                        if "data_model" in resp and resp["data_model"]:
                            model = resp["data_model"]
                            tables_count = len(model.get("tables", []))
                            rels_count = len(model.get("relationships", []))
                            
                            if tables_count > 0:
                                state.model_metadata = model
                                progress_bar.progress(100)
                                status_text.text("✅ Model generated successfully!")
                                
                                st.success(f"✅ Generated data model with {tables_count} tables and {rels_count} relationships!")
                                
                                with st.expander("📊 Processing Summary", expanded=False):
                                    st.markdown(f"""
                                    **Input Files:** {len(ddl_files)} DDL files + 1 relationships file  
                                    **Total Size:** {total_size:,} characters  
                                    **Generated:** {tables_count} tables, {rels_count} relationships  
                                    **Processing:** Completed successfully  
                                    """)
                            else:
                                progress_bar.progress(100)
                                status_text.text("❌ No tables generated")
                                st.error("❌ No tables were generated. Check your DDL syntax.")
                        else:
                            progress_bar.progress(100)
                            status_text.text("❌ Generation failed")
                            st.error("❌ Failed to generate model. Try with fewer/smaller DDL files or check syntax.")
                            
                except Exception as e:
                    progress_bar.progress(100)
                    status_text.text("❌ Processing error")
                    st.error(f"❌ Error during processing: {str(e)}")

    # Model Preview
    if state.model_metadata:
        st.markdown("---")
        st.subheader("📊 Model Preview")
        
        model_dict = safe_get_dict(state.model_metadata)
        tables = safe_get_list(model_dict.get("tables", []))
        relationships = safe_get_list(model_dict.get("relationships", []))
        
        total_columns = 0
        for table in tables:
            table_dict = safe_get_dict(table)
            if table_dict:
                columns = safe_get_list(table_dict.get("columns", []))
                total_columns += len(columns)
        
        complexity = analyze_model_complexity(state.model_metadata)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tables", len(tables))
        with col2:
            st.metric("Total Columns", total_columns)
        with col3:
            st.metric("Relationships", len(relationships))
        with col4:
            st.metric("Complexity", complexity)
        
        with st.expander("View Full JSON Schema"):
            st.json(state.model_metadata)
        
        # ─── Additional Context Section (KPIs and Data Dictionary) ─────────────
        st.markdown("---")
        st.subheader("📈 Additional Context (Optional)")
        st.markdown("Provide business context to generate more accurate dashboard layouts and data preparation instructions.")
        
        col1, col2 = st.columns(2)
        
        # KPI List Upload
        with col1:
            st.markdown("### 📊 KPI Definitions")
            st.markdown("Define your key performance indicators through file upload or text input.")
            
            # Input method selection for KPIs
            kpi_input_method = st.radio(
                "KPI Input Method:",
                ["📁 Upload File", "✏️ Text Input"],
                key="kpi_input_method",
                horizontal=True
            )
            
            if kpi_input_method == "📁 Upload File":
                kpi_file = st.file_uploader(
                    "Upload KPI List",
                    type=["xlsx", "docx"],
                    help="Excel: Columns for KPI Name, Description, Formula (optional), Target (optional), Category (optional)\nWord: Bulleted list of KPIs with descriptions"
                )
            else:
                kpi_file = None
                st.markdown("**Enter unstructured KPI notes:**")
                kpi_text_input = st.text_area(
                    "KPI Notes",
                    height=200,
                    placeholder="""Enter your KPI information in any format, for example:

• Sales revenue should hit $2M monthly with 15% growth target
• Customer satisfaction score measured quarterly, target 4.5/5
• Marketing: Click-through rate = clicks/impressions, aim for 3%
• Cost per acquisition should be under $150
• Employee retention rate annually, target 90%
• Profit margin = (revenue - costs) / revenue * 100

The AI will extract structured KPI definitions from your notes.""",
                    key="kpi_text_input"
                )
            
            if kpi_file:
                try:
                    file_bytes = kpi_file.read()
                    
                    if kpi_file.name.endswith('.xlsx'):
                        kpi_list = parse_kpi_excel(file_bytes)
                    else:  # .docx
                        kpi_list = parse_kpi_word(file_bytes)
                    
                    if validate_kpi_list(kpi_list):
                        state.kpi_list = kpi_list
                        st.success(f"✅ Loaded {len(kpi_list)} KPIs")
                        
                        # Show preview
                        with st.expander("Preview KPIs", expanded=False):
                            for i, kpi in enumerate(kpi_list[:5]):  # Show first 5
                                st.markdown(f"**{i+1}. {kpi['name']}**")
                                st.markdown(f"   *{kpi['description']}*")
                                if 'formula' in kpi:
                                    st.markdown(f"   Formula: `{kpi['formula']}`")
                                if 'target' in kpi:
                                    st.markdown(f"   Target: {kpi['target']}")
                            if len(kpi_list) > 5:
                                st.markdown(f"... and {len(kpi_list) - 5} more")
                    else:
                        st.error("Invalid KPI file format. Please check the structure.")
                        state.kpi_list = None
                        
                except Exception as e:
                    st.error(f"Error parsing KPI file: {str(e)}")
                    state.kpi_list = None
            elif kpi_input_method == "✏️ Text Input" and 'kpi_text_input' in st.session_state and st.session_state.kpi_text_input.strip():
                # Process unstructured KPI text
                if st.button("🔮 Parse KPI Notes", key="parse_kpis", use_container_width=True):
                    with st.spinner("🧠 AI is analyzing your KPI notes..."):
                        try:
                            # Call the API to parse unstructured KPIs
                            response = call_api("parse-unstructured-kpis", {
                                "notes_text": st.session_state.kpi_text_input
                            }, timeout=600)
                            
                            if response and "kpi_list" in response:
                                kpi_list = response["kpi_list"]
                                parsing_notes = response.get("parsing_notes", "")
                                
                                if validate_kpi_list(kpi_list):
                                    state.kpi_list = kpi_list
                                    st.success(f"✅ Parsed {len(kpi_list)} KPIs from your notes!")
                                    
                                    # Show parsing notes
                                    if parsing_notes:
                                        st.info(f"📝 **Parsing Notes:** {parsing_notes}")
                                    
                                    # Show preview
                                    with st.expander("Preview Parsed KPIs", expanded=True):
                                        for i, kpi in enumerate(kpi_list[:5]):  # Show first 5
                                            st.markdown(f"**{i+1}. {kpi.get('name', 'Unnamed KPI')}**")
                                            st.markdown(f"   *{kpi.get('description', 'No description')}*")
                                            if kpi.get('formula'):
                                                st.markdown(f"   📊 Formula: `{kpi['formula']}`")
                                            if kpi.get('target'):
                                                st.markdown(f"   🎯 Target: {kpi['target']}")
                                            if kpi.get('category'):
                                                st.markdown(f"   📂 Category: {kpi['category']}")
                                        if len(kpi_list) > 5:
                                            st.markdown(f"... and {len(kpi_list) - 5} more KPIs")
                                else:
                                    st.error("Could not validate parsed KPIs. Please check your notes format.")
                                    state.kpi_list = None
                            else:
                                st.error("Failed to parse KPI notes. Please try rephrasing or contact support.")
                                
                        except Exception as e:
                            st.error(f"Error parsing KPI notes: {str(e)}")
                            state.kpi_list = None
            elif state.kpi_list:
                st.info(f"✅ {len(state.kpi_list)} KPIs loaded from previous upload")
        
        # Data Dictionary Upload
        with col2:
            st.markdown("### 📖 Data Dictionary")
            st.markdown("Define your data fields and business rules through file upload or text input.")
            
            # Input method selection for Data Dictionary
            dict_input_method = st.radio(
                "Dictionary Input Method:",
                ["📁 Upload File", "✏️ Text Input"],
                key="dict_input_method",
                horizontal=True
            )
            
            if dict_input_method == "📁 Upload File":
                dict_file = st.file_uploader(
                    "Upload Data Dictionary",
                    type=["xlsx", "csv"],
                    help="Expected columns: Table Name, Column Name, Description, Data Type (optional), Example Values (optional), Business Rules (optional)"
                )
            else:
                dict_file = None
                st.markdown("**Enter unstructured data dictionary notes:**")
                dict_text_input = st.text_area(
                    "Data Dictionary Notes",
                    height=200,
                    placeholder="""Enter your data field information in any format, for example:

Customer table:
- customer_id: unique identifier, integer, must not be null
- first_name: customer's first name, text, required
- email: contact email, text format: name@domain.com
- registration_date: when customer joined, date format YYYY-MM-DD
- status: active/inactive/suspended

Sales table has order_id, customer_id, product_name, amount (positive decimal), order_date

Product categories include: Electronics, Books, Clothing, Home & Garden

The AI will structure this into a proper data dictionary format.""",
                    key="dict_text_input"
                )
            
            if dict_file:
                try:
                    file_bytes = dict_file.read()
                    
                    if dict_file.name.endswith('.xlsx'):
                        data_dict = parse_data_dictionary_excel(file_bytes)
                    else:  # .csv
                        data_dict = parse_data_dictionary_csv(file_bytes)
                    
                    if validate_data_dictionary(data_dict):
                        state.data_dictionary = data_dict
                        
                        # Count entries
                        total_entries = sum(len(cols) for cols in data_dict.values())
                        st.success(f"✅ Loaded dictionary for {len(data_dict)} tables ({total_entries} columns)")
                        
                        # Show preview
                        with st.expander("Preview Data Dictionary", expanded=False):
                            for table_name, columns in list(data_dict.items())[:2]:  # Show first 2 tables
                                st.markdown(f"**Table: {table_name}**")
                                for col_name, col_info in list(columns.items())[:3]:  # Show first 3 columns
                                    st.markdown(f"- `{col_name}`: {col_info['description']}")
                                    if 'type' in col_info:
                                        st.markdown(f"  Type: {col_info['type']}")
                                if len(columns) > 3:
                                    st.markdown(f"  ... and {len(columns) - 3} more columns")
                            if len(data_dict) > 2:
                                st.markdown(f"... and {len(data_dict) - 2} more tables")
                    else:
                        st.error("Invalid data dictionary format. Please check the structure.")
                        state.data_dictionary = None
                        
                except Exception as e:
                    st.error(f"Error parsing data dictionary: {str(e)}")
                    state.data_dictionary = None
            elif dict_input_method == "✏️ Text Input" and 'dict_text_input' in st.session_state and st.session_state.dict_text_input.strip():
                # Process unstructured data dictionary text
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    parse_dict_button = st.button("🔮 Parse Dictionary Notes", key="parse_dict", use_container_width=True)
                with col_b:
                    # Option to include model context
                    include_model_context = st.checkbox("Use Model Context", 
                                                       help="Include existing data model as context for better parsing")
                
                if parse_dict_button:
                    with st.spinner("🧠 AI is analyzing your data dictionary notes..."):
                        try:
                            # Prepare context from existing model if available
                            table_context = ""
                            if include_model_context and state.model_metadata:
                                model_dict = safe_get_dict(state.model_metadata)
                                tables = safe_get_list(model_dict.get("tables", []))
                                if tables:
                                    table_context = "Existing data model tables: "
                                    for table in tables[:5]:  # Limit to 5 tables for context
                                        table_dict = safe_get_dict(table)
                                        table_name = table_dict.get("table_name", "") or table_dict.get("name", "")
                                        if table_name:
                                            table_context += f"{table_name}, "
                                    table_context = table_context.rstrip(", ")
                            
                            # Call the API to parse unstructured data dictionary
                            response = call_api("parse-unstructured-dictionary", {
                                "notes_text": st.session_state.dict_text_input,
                                "table_context": table_context
                            }, timeout=600)
                            
                            if response and "data_dictionary" in response:
                                data_dict = response["data_dictionary"]
                                parsing_notes = response.get("parsing_notes", "")
                                
                                if validate_data_dictionary(data_dict):
                                    state.data_dictionary = data_dict
                                    
                                    # Count entries
                                    total_entries = sum(len(cols) for cols in data_dict.values())
                                    st.success(f"✅ Parsed dictionary for {len(data_dict)} tables ({total_entries} columns)!")
                                    
                                    # Show parsing notes
                                    if parsing_notes:
                                        st.info(f"📝 **Parsing Notes:** {parsing_notes}")
                                    
                                    # Show preview
                                    with st.expander("Preview Parsed Data Dictionary", expanded=True):
                                        for table_name, columns in list(data_dict.items())[:3]:  # Show first 3 tables
                                            st.markdown(f"**📋 Table: {table_name}**")
                                            for col_name, col_info in list(columns.items())[:4]:  # Show first 4 columns
                                                st.markdown(f"- `{col_name}`: {col_info.get('description', 'No description')}")
                                                if col_info.get('type'):
                                                    st.markdown(f"  📊 Type: {col_info['type']}")
                                                if col_info.get('rules'):
                                                    st.markdown(f"  📋 Rules: {col_info['rules']}")
                                            if len(columns) > 4:
                                                st.markdown(f"  ... and {len(columns) - 4} more columns")
                                        if len(data_dict) > 3:
                                            st.markdown(f"... and {len(data_dict) - 3} more tables")
                                else:
                                    st.error("Could not validate parsed data dictionary. Please check your notes format.")
                                    state.data_dictionary = None
                            else:
                                st.error("Failed to parse data dictionary notes. Please try rephrasing or contact support.")
                                
                        except Exception as e:
                            st.error(f"Error parsing data dictionary notes: {str(e)}")
                            state.data_dictionary = None
            elif state.data_dictionary:
                total_entries = sum(len(cols) for cols in state.data_dictionary.values())
                st.info(f"✅ Dictionary loaded: {len(state.data_dictionary)} tables, {total_entries} columns")
        
        # ─── Business-Friendly Sharing & Export ──────────────────────────────────
        if state.kpi_list or state.data_dictionary:
            st.markdown("---")
            st.subheader("📤 Business-Friendly Sharing")
            st.markdown("Export your KPIs and Data Dictionary in professional formats for stakeholder sharing.")
            
            col1, col2, col3 = st.columns(3)
            
            # KPI Export Options
            if state.kpi_list:
                with col1:
                    st.markdown("**📊 KPI Definitions Export**")
                    
                    # Preview KPIs
                    with st.expander("👀 Preview KPIs", expanded=False):
                        for i, kpi in enumerate(state.kpi_list[:5], 1):
                            st.markdown(f"**{i}. {kpi.get('name', 'Unnamed KPI')}**")
                            st.markdown(f"_{kpi.get('description', 'No description')}_")
                            if kpi.get('formula'):
                                st.code(kpi['formula'], language='text')
                            if i < len(state.kpi_list):
                                st.markdown("---")
                        if len(state.kpi_list) > 5:
                            st.markdown(f"... and {len(state.kpi_list) - 5} more KPIs")
                    
                    # Export buttons
                    if st.button("📋 Copy KPI Summary", key="copy_kpi", use_container_width=True):
                        kpi_summary = generate_kpi_summary_text(state.kpi_list)
                        st.code(kpi_summary, language='markdown')
                        st.success("✅ KPI summary generated! Copy the text above.")
                    
                    if st.button("📄 Download KPI Report", key="download_kpi", use_container_width=True):
                        kpi_report = generate_kpi_business_report(state.kpi_list)
                        st.download_button(
                            label="📥 Download KPI Report.md",
                            data=kpi_report,
                            file_name="KPI_Definitions_Report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
            
            # Data Dictionary Export Options  
            if state.data_dictionary:
                with col2:
                    st.markdown("**📖 Data Dictionary Export**")
                    
                    # Preview Data Dictionary
                    with st.expander("👀 Preview Data Dictionary", expanded=False):
                        table_count = 0
                        for table_name, columns in state.data_dictionary.items():
                            if table_count >= 3:
                                st.markdown(f"... and {len(state.data_dictionary) - 3} more tables")
                                break
                            st.markdown(f"**📋 {table_name}**")
                            col_count = 0
                            for col_name, col_info in columns.items():
                                if col_count >= 5:
                                    st.markdown(f"... and {len(columns) - 5} more columns")
                                    break
                                st.markdown(f"- `{col_name}`: {col_info.get('description', 'No description')}")
                                col_count += 1
                            st.markdown("")
                            table_count += 1
                    
                    # Export buttons
                    if st.button("📋 Copy Dictionary Summary", key="copy_dict", use_container_width=True):
                        dict_summary = generate_data_dictionary_summary_text(state.data_dictionary)
                        st.code(dict_summary, language='markdown')
                        st.success("✅ Data dictionary summary generated! Copy the text above.")
                    
                    if st.button("📄 Download Dictionary Report", key="download_dict", use_container_width=True):
                        dict_report = generate_data_dictionary_business_report(state.data_dictionary)
                        st.download_button(
                            label="📥 Download Data Dictionary.md",
                            data=dict_report,
                            file_name="Data_Dictionary_Report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
            
            # Combined Export Options
            if state.kpi_list and state.data_dictionary:
                with col3:
                    st.markdown("**📊📖 Combined Export**")
                    st.markdown("Export both KPIs and Data Dictionary together")
                    
                    if st.button("📋 Copy Combined Summary", key="copy_combined", use_container_width=True):
                        combined_summary = generate_combined_business_summary(state.kpi_list, state.data_dictionary)
                        st.code(combined_summary, language='markdown')
                        st.success("✅ Combined summary generated! Copy the text above.")
                    
                    if st.button("📄 Download Complete Report", key="download_combined", use_container_width=True):
                        combined_report = generate_combined_business_report(state.kpi_list, state.data_dictionary, state.model_metadata)
                        st.download_button(
                            label="📥 Download Complete Business Report.md",
                            data=combined_report,
                            file_name="Business_Context_Complete_Report.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

# ─── Page: Data Prep (Simplified - hidden complexity, default to Advanced) ───────
elif state.page == "Data Prep":
    st.header("2️⃣ Data Preparation")
    st.markdown(
        "**Overview:** Analyze your data model and generate detailed, column-specific data preparation instructions.  \n"
        "After data is clean and joined, move to **Dashboard Dev**."
    )
    
    # Show progress for beginners
    render_progress_indicator(2, 4, "Data Preparation")
    
    # Show estimated time
    render_estimated_time("data preparation", 15)
    
    # Adaptive help
    render_adaptive_help(
        "Why Data Prep?",
        """Data preparation is crucial for dashboard success. This step helps you:
        - Clean and validate your data
        - Create proper joins between tables
        - Calculate derived fields and KPIs
        - Optimize for your chosen BI platform
        
        Good data prep = faster, more accurate dashboards!"""
    )
    
    if not state.model_metadata:
        st.info("Define your Data Model first under **Data Model**.")
    else:
        st.subheader("📊 Data Model Summary")
        
        model_dict = safe_get_dict(state.model_metadata)
        if model_dict:
            tables = safe_get_list(model_dict.get("tables", []))
            relationships = safe_get_list(model_dict.get("relationships", []))
            
            col1, col2 = st.columns(2)
            
            with col1:
                safe_display_table_summary(tables, state.data_dictionary)
            
            with col2:
                st.markdown("**🔗 Relationships:**")
                if relationships:
                    for rel in relationships:
                        rel_dict = safe_get_dict(rel)
                        if rel_dict:
                            # Support both relationship formats
                            if "from_table" in rel_dict:
                                # Detailed format: separate table and column fields
                                from_table = rel_dict.get("from_table", "Unknown")
                                from_column = rel_dict.get("from_column", "")
                                to_table = rel_dict.get("to_table", "Unknown")
                                to_column = rel_dict.get("to_column", "")
                                rel_type = rel_dict.get("relationship_type", "Unknown")
                                
                                from_ref = f"{from_table}[{from_column}]" if from_column else from_table
                                to_ref = f"{to_table}[{to_column}]" if to_column else to_table
                            else:
                                # Simple format: combined table[column] format
                                from_ref = rel_dict.get("from", "Unknown")
                                to_ref = rel_dict.get("to", "Unknown")
                                rel_type = rel_dict.get("type", "Unknown")
                            
                            st.markdown(f"- **{from_ref}** → **{to_ref}** ({rel_type})")
                else:
                    st.markdown("No relationships defined")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tool = st.selectbox("Select BI Platform", [
                "Power BI", 
                "Tableau", 
                "Qlik Sense",
                "Looker",
                "Other"
            ])
        
        with col2:
            data_source = st.selectbox("Data Source Type", [
                "SQL Server",
                "MySQL",
                "PostgreSQL", 
                "Oracle",
                "Excel/CSV",
                "Cloud (Azure/AWS)",
                "Other"
            ])
        
        with st.expander("🔧 Advanced Options"):
            include_validation = st.checkbox("Include data validation steps", value=True)
            include_performance = st.checkbox("Include performance optimization tips", value=True)
            include_troubleshooting = st.checkbox("Include troubleshooting guidance", value=True)
            include_code_snippets = st.checkbox("Include code snippets/formulas", value=True)
            
            # Add table selection for complex models
            model_dict = safe_get_dict(state.model_metadata or {})
            tables = safe_get_list(model_dict.get("tables", []))
            
            if len(tables) > 10:
                st.warning(f"⚠️ You have {len(tables)} tables. Consider selecting a subset for better performance.")
                
                # Option to select specific tables
                table_selection_method = st.radio(
                    "Table Selection",
                    ["Use all tables", "Select specific tables"],
                    help="For large models, selecting specific tables improves generation speed"
                )
                
                selected_tables = None
                if table_selection_method == "Select specific tables":
                    table_names = [safe_get_dict(t).get("table_name", f"Table {i}") for i, t in enumerate(tables)]
                    selected_tables = st.multiselect(
                        "Select tables to include",
                        table_names,
                        default=table_names[:10],  # Default to first 10
                        help="Select the most important tables for your data prep instructions"
                    )
            
            custom_requirements = st.text_area(
                "Additional Requirements", 
                placeholder="e.g., Specific business rules, data quality requirements, compliance needs...",
                height=100
            )
        
        # Chunked generation option for large models
        model_dict = safe_get_dict(state.model_metadata or {})
        tables = safe_get_list(model_dict.get("tables", []))
        total_columns = sum(len(safe_get_list(safe_get_dict(t).get("columns", []))) for t in tables)
        is_very_large = len(tables) > 25 or total_columns > 300
        
        if is_very_large:
            st.warning(f"🚨 **Very Large Model Detected**: {len(tables)} tables, {total_columns} columns")
            col1, col2 = st.columns(2)
            with col1:
                use_chunked = st.checkbox("📦 Use Chunked Processing", value=True, 
                                        help="Process tables in smaller batches to prevent timeouts")
            with col2:
                chunk_size = st.slider("Tables per chunk", min_value=3, max_value=8, value=5) if use_chunked else len(tables)
        else:
            use_chunked = False
            chunk_size = len(tables)

        if st.button("🚀 Generate Data Preparation Instructions", type="primary"):
            # Add progress tracking
            progress_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            with st.spinner("Analyzing data model and generating detailed instructions..."):
                # Default to Advanced complexity (hidden from UI)
                complexity = "Advanced (Complex Logic)"
                
                # Determine complexity
                is_complex = len(tables) > 10 or total_columns > 100
                is_very_complex = len(tables) > 20 or total_columns > 200
                
                if use_chunked and is_very_large:
                    # CHUNKED PROCESSING FOR VERY LARGE MODELS
                    st.info(f"🔄 Processing {len(tables)} tables in chunks of {chunk_size}...")
                    
                    all_instructions = []
                    table_chunks = [tables[i:i + chunk_size] for i in range(0, len(tables), chunk_size)]
                    
                    for chunk_idx, chunk_tables in enumerate(table_chunks):
                        progress_placeholder.text(f"📊 Processing chunk {chunk_idx + 1}/{len(table_chunks)} ({len(chunk_tables)} tables)...")
                        progress_pct = int((chunk_idx / len(table_chunks)) * 80)  # Use 80% for chunks
                        progress_bar.progress(progress_pct)
                        
                        # Create simplified prompt for each chunk
                        chunk_requirements = f"""
Create data preparation instructions for {tool} using {data_source}.

Tables in this chunk: {', '.join(safe_get_dict(t).get("table_name", "") for t in chunk_tables)}

Focus on:
1. Essential data cleaning for these tables
2. Key relationships within this chunk
3. Required calculations and transformations

Keep instructions specific to these tables only.
{custom_requirements if chunk_idx == 0 else ''}
"""
                        
                        # Create minimal metadata for this chunk
                        chunk_metadata = {
                            "tables": [
                                {
                                    "table_name": safe_get_dict(t).get("table_name"),
                                    "columns": safe_get_dict(t).get("columns", [])[:10]  # Limit columns per table
                                }
                                for t in chunk_tables
                            ],
                            "relationships": [
                                r for r in model_dict.get("relationships", [])
                                if any(safe_get_dict(t).get("table_name") in str(r) for t in chunk_tables)
                            ][:5]  # Only relationships relevant to this chunk
                        }
                        
                        chunk_payload = {
                            "sketch_description": "",
                            "platform_selected": tool,
                            "custom_prompt": chunk_requirements.strip(),
                            "model_metadata": chunk_metadata,
                            "include_data_prep": True,
                            "data_prep_only": True,
                            "kpi_list": state.kpi_list if chunk_idx == 0 else None,  # Only include KPIs in first chunk
                            "data_dictionary": state.data_dictionary if chunk_idx == 0 else None
                        }
                        
                        try:
                            # Use longer timeout for chunks and no retries (was working before)
                            resp = call_api("generate-layout", chunk_payload, timeout=600, max_retries=0)  # 10 minutes per chunk, no retries
                            chunk_instructions = resp.get("layout_instructions", "")
                            
                            if chunk_instructions:
                                # Add chunk header
                                chunk_header = f"\n\n## Chunk {chunk_idx + 1}: {', '.join(safe_get_dict(t).get('table_name', '') for t in chunk_tables)}\n\n"
                                all_instructions.append(chunk_header + chunk_instructions)
                                st.success(f"✅ Chunk {chunk_idx + 1} completed successfully")
                            else:
                                st.warning(f"⚠️ Chunk {chunk_idx + 1} failed to generate. Continuing with other chunks...")
                                
                        except Exception as e:
                            st.warning(f"⚠️ Chunk {chunk_idx + 1} error: {str(e)}. Continuing with other chunks...")
                            continue
                    
                    # Combine all instructions
                    if all_instructions:
                        # Add overall header
                        combined_instructions = f"# Data Preparation Instructions for {tool}\n\n"
                        combined_instructions += f"**Generated for {len(tables)} tables in {len(table_chunks)} chunks**\n\n"
                        combined_instructions += "".join(all_instructions)
                        
                        # Add final summary section
                        combined_instructions += f"""

## Summary and Next Steps

This data preparation guide covers all {len(tables)} tables in your model. Each chunk above provides specific instructions for its tables.

### Recommended Processing Order:
1. Start with foundational tables (dimension tables, lookup tables)
2. Process fact tables and transaction tables
3. Create calculated fields and derived metrics
4. Validate relationships and data quality
5. Optimize performance for {tool}

### Key Considerations:
- Ensure consistent data types across related tables
- Validate foreign key relationships between chunks
- Monitor data quality throughout the process
- Test performance with sample data before full load
"""
                        
                        state.data_prep_instructions = combined_instructions
                        progress_bar.progress(100)
                        progress_placeholder.empty()
                        st.success(f"✅ Chunked processing complete! Generated instructions for {len(tables)} tables in {len(table_chunks)} chunks.")
                    else:
                        progress_bar.progress(100)
                        progress_placeholder.empty()
                        st.error("❌ All chunks failed. Try reducing chunk size or simplifying the model.")
                
                else:
                    # SINGLE REQUEST PROCESSING (Original logic with optimizations)
                    # Simplify requirements for better performance
                    if is_very_complex:
                        # Minimal prompt for very complex models
                        enhanced_requirements = f"""
Create data preparation instructions for {tool} using {data_source}.

Focus on:
1. Essential data cleaning steps
2. Key table joins
3. Required calculations

Keep instructions concise and practical.
{custom_requirements}
"""
                    elif is_complex:
                        # Reduced prompt for complex models
                        enhanced_requirements = f"""
Data Source: {data_source}
Platform: {tool}

Provide data preparation steps including:
- Data cleaning and validation
- Table relationships and joins
- Essential calculations

{custom_requirements}
"""
                    else:
                        # Full prompt only for simple models
                        enhanced_requirements = f"""
Data Source: {data_source}
Platform: {tool}
Include Validation: {include_validation}
Include Performance Tips: {include_performance}

Provide comprehensive data preparation instructions with:
1. Data cleaning and transformation steps
2. Table joining strategies
3. Calculations and derived fields
4. Best practices for {tool}

{custom_requirements}
"""
                    
                    # Add persona modifier to prompt
                    persona_modifier = get_persona_prompt_modifier()
                    if persona_modifier:
                        enhanced_requirements += f"\n\n{persona_modifier}"
                    
                    enhanced_payload = {
                        "sketch_description": "",
                        "platform_selected": tool,
                        "custom_prompt": enhanced_requirements.strip(),
                        "model_metadata": state.model_metadata,
                        "include_data_prep": True,
                        "data_prep_only": True,
                        "kpi_list": state.kpi_list,
                        "data_dictionary": state.data_dictionary
                    }
                    
                    # Update progress
                    progress_placeholder.text("📊 Analyzing model complexity...")
                    progress_bar.progress(10)
                    
                    # Show warning for very complex models
                    if is_very_complex:
                        st.warning(f"⚠️ Large data model detected ({len(tables)} tables, {total_columns} columns). Processing may take a few minutes...")
                    
                    progress_placeholder.text("🔧 Preparing optimization settings...")
                    progress_bar.progress(20)
                    
                    # Less aggressive optimization - revert closer to working version
                    if is_very_complex:
                        # For very complex models, still optimize but less aggressively
                        st.info("💡 Applying moderate optimization for large model...")
                        
                        # Send more tables and columns than before
                        simplified_tables = []
                        for table in tables[:15]:  # Increased from 8 to 15 tables
                            table_dict = safe_get_dict(table)
                            if table_dict:
                                # Include more columns per table
                                simplified_table = {
                                    "table_name": table_dict.get("table_name"),
                                    "columns": table_dict.get("columns", [])[:20]  # Increased from 6 to 20 columns
                                }
                                simplified_tables.append(simplified_table)
                        
                        optimized_metadata = {
                            "tables": simplified_tables,
                            "relationships": model_dict.get("relationships", [])[:15]  # Increased from 6 to 15 relationships
                        }
                        enhanced_payload["model_metadata"] = optimized_metadata
                        
                    # Handle table selection if available
                    elif 'selected_tables' in locals() and selected_tables:
                        # Filter tables based on selection
                        filtered_tables = []
                        for table in tables:
                            table_dict = safe_get_dict(table)
                            if table_dict and table_dict.get("table_name") in selected_tables:
                                # Simplify columns for selected tables too
                                simplified_table = {
                                    "table_name": table_dict.get("table_name"),
                                    "columns": table_dict.get("columns", [])[:12]  # Limit columns
                                }
                                filtered_tables.append(simplified_table)
                        
                        # Update metadata with filtered tables
                        optimized_metadata = {
                            "tables": filtered_tables,
                            "relationships": model_dict.get("relationships", [])[:12]
                        }
                        enhanced_payload["model_metadata"] = optimized_metadata
                        st.info(f"📊 Processing {len(filtered_tables)} selected tables...")
                        
                    # Optimize payload for large models - less aggressive than before
                    elif is_complex:
                        # For complex models, optimize moderately
                        simplified_tables = []
                        for table in tables[:20]:  # Increased from 10 to 20
                            table_dict = safe_get_dict(table)
                            if table_dict:
                                simplified_table = {
                                    "table_name": table_dict.get("table_name"),
                                    "columns": table_dict.get("columns", [])[:25]  # Increased from 12 to 25
                                }
                                simplified_tables.append(simplified_table)
                        
                        optimized_metadata = {
                            "tables": simplified_tables,
                            "relationships": model_dict.get("relationships", [])[:20]  # Increased limit
                        }
                        enhanced_payload["model_metadata"] = optimized_metadata
                        
                        st.info("💡 Applying light optimization for better processing...")
                    
                    # Much more generous timeout strategy - revert to working timeouts
                    if is_very_complex:
                        timeout = 900  # 15 minutes for very complex (was working before)
                    elif is_complex:
                        timeout = 720  # 12 minutes for complex (was working before)
                    else:
                        timeout = 600  # 10 minutes for normal (was working before)
                    
                    try:
                        progress_placeholder.text("🤖 Generating AI-powered instructions...")
                        progress_bar.progress(50)
                        
                        # Use fewer retries with longer timeouts (was working before)
                        resp = call_api("generate-layout", enhanced_payload, timeout=timeout, max_retries=0)
                        
                        progress_bar.progress(90)
                        progress_placeholder.text("📝 Finalizing instructions...")
                        
                        state.data_prep_instructions = resp.get("layout_instructions", "")
                        
                        if state.data_prep_instructions:
                            progress_bar.progress(100)
                            progress_placeholder.empty()
                            st.success("✅ Data preparation instructions generated successfully!")
                        else:
                            progress_bar.progress(100)
                            progress_placeholder.empty()
                            st.error("❌ Failed to generate instructions. Please try chunked processing for large models.")
                            
                    except Exception as e:
                        progress_bar.progress(100)
                        progress_placeholder.empty()
                        if "timeout" in str(e).lower():
                            st.error("⏱️ **Generation timed out.** Try these solutions:")
                            if is_very_large:
                                st.markdown("""
                                - **✅ Use Chunked Processing**: Enable the checkbox above to process tables in smaller batches
                                - **Reduce chunk size**: Try 3-4 tables per chunk instead of 5-8
                                - **Focus on key tables**: Select only the most important tables first
                                """)
                            else:
                                st.markdown("""
                                - **Reduce complexity**: Focus on 5-10 most important tables
                                - **Split the work**: Generate instructions for groups of tables separately
                                - **Simplify requirements**: Uncheck some advanced options
                                - **Try again**: Sometimes the server is just busy
                                """)
                        else:
                            st.error(f"❌ Error: {str(e)}")
        
        if state.data_prep_instructions:
            st.subheader("📋 Data Preparation Instructions")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="📥 Download Instructions",
                    data=state.data_prep_instructions,
                    file_name=f"data_prep_{tool.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            with col2:
                if st.button("🔄 Regenerate"):
                    state.data_prep_instructions = ""
                    st.rerun()
            
            st.markdown(tidy_md(state.data_prep_instructions))
            
            st.subheader("✅ Data Preparation Checklist")
            st.markdown("""
            Use this checklist to track your progress:
            
            - [ ] Data sources connected successfully
            - [ ] Data types corrected for all columns
            - [ ] Null values handled according to business rules
            - [ ] Duplicate records identified and removed
            - [ ] Relationships established and validated
            - [ ] Data quality validation completed
            - [ ] Performance optimization applied
            - [ ] Test queries verified
            - [ ] Data refresh process tested
            - [ ] Ready for dashboard development
            """)
            
            st.info("✨ **Next Steps:** Once your data preparation is complete, navigate to **Dashboard Dev** to create your visualizations!")

# ─── Business-Friendly Export Functions ─────────────────────────────────────────
# ─── Page: Dashboard Dev (Tips moved above, Examples removed) ─────────────────────
elif state.page == "Dashboard Dev":
    st.header("3️⃣ Dashboard Development")
    st.markdown(
        "**Overview:**  \n"
        "- Choose your BI tool and input method.  \n"
        "- Describe, sketch, or upload your wireframe.  \n"
        "- Get detailed, platform-specific build instructions.  \n\n"
        "After building visuals, move to **Sprint Board**."
    )
    
    # Show progress
    render_progress_indicator(3, 4, "Dashboard Development")
    
    # Show estimated time
    render_estimated_time("dashboard design", 30)
    
    # Adaptive help
    render_adaptive_help(
        "Dashboard Design Tips",
        """**Best Practices:**
        - Start with your most important KPIs at the top
        - Use consistent colors and fonts
        - Group related information together
        - Leave white space for visual breathing room
        - Test with actual users for feedback
        
        **Common Layouts:**
        - Executive Summary (KPI cards on top)
        - Analytical Deep Dive (filters + detailed charts)
        - Operational Monitor (real-time metrics + alerts)"""
    )
    
    if not state.model_metadata:
        st.info("Define your Data Model first under **Data Model**.")
    else:
        # Platform and context selection
        col1, col2 = st.columns([1, 2])
        with col1:
            platform = st.selectbox("🛠️ BI Tool", ["Power BI", "Tableau", "Qlik Sense", "Looker", "Other"])
            state.current_platform = platform
        with col2:
            prompt = st.text_area("Additional context (optional)", height=80, 
                                placeholder="Any specific requirements, styling preferences, or constraints...")
        
        # Input method selection
        st.subheader("📝 Choose Input Method")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Text Description", use_container_width=True, 
                        type="primary" if state.input_method == "text" else "secondary"):
                state.input_method = "text"
        with col2:
            if st.button("🤖 AI Vision Upload", use_container_width=True,
                        type="primary" if state.input_method == "ai_vision" else "secondary"):
                state.input_method = "ai_vision"
        with col3:
            if st.button("🔧 Simple Detection", use_container_width=True,
                        type="primary" if state.input_method == "simple" else "secondary"):
                state.input_method = "simple"
        
        method_descriptions = {
            "text": "✏️ **Text Description** - Describe your dashboard layout in words. Best for detailed specifications.",
            "ai_vision": "🤖 **AI Vision** - Upload sketches, wireframes, or screenshots for intelligent AI analysis. **Recommended!**",
            "simple": "🔧 **Simple Detection** - Basic geometric shape detection. Fallback option for simple layouts."
        }
        st.info(method_descriptions[state.input_method])

        # Tips moved above upload sections
        st.markdown("---")
        st.markdown("### 💡 Tips for Better Results")
        
        if state.input_method == "text":
            st.info("""
            **📝 Text Description Tips:**
            - Be specific about positioning (top-left, center, bottom-right)
            - Mention visual types (bar chart, line chart, KPI card, table)
            - Include any labels, titles, or text you want
            - Specify colors, sizes, or styling preferences
            - Describe interactions (filters, slicers, drill-downs)
            """)
        
        elif state.input_method == "ai_vision":
            st.info("""
            **🤖 AI Vision Best Practices:**
            - ✅ Hand-drawn sketches work excellently
            - ✅ High-contrast wireframes are ideal
            - ✅ Screenshots of existing dashboards
            - ✅ Whiteboard photos with clear markings
            - ✅ Digital mockups and design files
            """)
        
        else:
            st.info("""
            **🔧 Simple Detection Tips:**
            - Use images with clear, distinct rectangular shapes
            - High contrast works best (dark lines on light background)
            - Avoid complex backgrounds or textures
            - Make sure shapes are large enough to be detected
            - Simple geometric wireframes are ideal
            """)

        st.markdown("---")

        # Text Description Method
        if state.input_method == "text":
            st.subheader("📝 Describe Your Dashboard Layout")
            
            with st.form("text_description"):
                desc = st.text_area("Dashboard layout description", height=250, placeholder="""
📋 Example detailed description:

**Header Section:**
- Top row: 3 KPI cards showing Total Sales ($2.5M), Gross Margin % (34%), and Customer Count (1,247)
- Use large, bold numbers with green/red indicators for positive/negative trends

**Navigation Panel:**
- Left sidebar: Region dropdown slicer and Year range slider
- Date picker for custom date ranges

**Main Analytics Area:**
- Center-left: Large line chart showing Sales Trend over Time (last 12 months)
- Center-right: Horizontal bar chart showing Sales by Product Category (top 10)

**Detail Section:**
- Bottom: Scrollable data table with sales by store location
- Include columns: Store Name, Region, Sales Amount, Growth %

**Styling:**
- Corporate blue (#1f4e79) and gray theme
- Green accent (#70ad47) for positive metrics
- Consistent fonts and spacing throughout
                """)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    go = st.form_submit_button("✨ Generate Layout Instructions", type="primary")
                with col2:
                    if st.form_submit_button("🎲 Use Example Layout"):
                        desc = """Top row: 3 KPI cards (Total Sales, Margin %, Customer Count)
Left sidebar: Region and Year slicers
Main area: Sales trend line chart and category bar chart  
Bottom: Detailed sales table by store"""
                        go = True
                
            if go and desc.strip():
                with st.spinner("🎨 Generating dashboard layout instructions..."):
                    # Dynamic timeout based on model complexity
                    model_dict = safe_get_dict(state.model_metadata or {})
                    tables = safe_get_list(model_dict.get("tables", []))
                    total_columns = sum(len(safe_get_list(safe_get_dict(t).get("columns", []))) for t in tables)
                    is_complex = len(tables) > 10 or total_columns > 100
                    
                    timeout = 240 if is_complex else 150  # 4 minutes for complex, 2.5 for others
                    out = call_api("generate-layout", {
                        "sketch_description": desc,
                        "platform_selected": platform,
                        "custom_prompt": prompt,
                        "model_metadata": state.model_metadata,
                        "include_data_prep": False,
                        "data_prep_only": False,
                        "kpi_list": state.kpi_list,
                        "data_dictionary": state.data_dictionary
                    }, timeout=timeout)
                    state.wireframe_json = out.get("wireframe_json", "")
                    state.dev_instructions = out.get("layout_instructions", "")
            elif go and not desc.strip():
                st.warning("⚠️ Please enter a description of your dashboard layout.")

        # AI Vision Method
        elif state.input_method == "ai_vision":
            st.subheader("🤖 AI Vision Analysis")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.success("🎯 **Best Choice!** AI Vision provides the most accurate analysis of wireframes, sketches, and screenshots.")
            with col2:
                st.info(f"🎯 **Target:** {platform}")
            
            # Show previous analysis if available
            if state.ai_analysis_result and not st.session_state.get('show_new_upload', False):
                st.info("🎯 **Previous Analysis Available** - You can use the existing analysis or upload a new image.")
                
                with st.expander("🔍 Previous AI Vision Analysis", expanded=True):
                    st.text_area(
                        f"Previous AI Analysis for {platform}:", 
                        state.ai_analysis_result, 
                        height=300, 
                        key="previous_ai_result_display",
                        help="Previous AI Vision analysis of your dashboard layout"
                    )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    button_text = get_adaptive_button_text("Generate Dashboard Instructions", "generate")
                    if st.button(f"✨ {button_text}", type="primary", key="ai_generate_from_previous"):
                        with st.spinner("🔨 Creating detailed dashboard instructions..."):
                            enhanced_prompt = prompt
                            # Add persona modifier
                            persona_modifier = get_persona_prompt_modifier()
                            if persona_modifier:
                                enhanced_prompt = f"{enhanced_prompt}\n\n{persona_modifier}" if enhanced_prompt else persona_modifier
                            
                            if prompt:
                                enhanced_prompt += f"\n\nAI Vision Analysis:\n{state.ai_analysis_result}"
                            else:
                                enhanced_prompt = f"AI Vision Analysis:\n{state.ai_analysis_result}"
                            
                            # Dynamic timeout based on model complexity
                            model_dict = safe_get_dict(state.model_metadata or {})
                            tables = safe_get_list(model_dict.get("tables", []))
                            total_columns = sum(len(safe_get_list(safe_get_dict(t).get("columns", []))) for t in tables)
                            is_complex = len(tables) > 10 or total_columns > 100
                            
                            timeout = 240 if is_complex else 150  # 4 minutes for complex, 2.5 for others
                            out = call_api("generate-layout", {
                                "sketch_description": state.ai_analysis_result,
                                "platform_selected": platform,
                                "custom_prompt": enhanced_prompt,
                                "model_metadata": state.model_metadata,
                                "include_data_prep": False,
                                "data_prep_only": False,
                                "kpi_list": state.kpi_list,
                                "data_dictionary": state.data_dictionary
                            }, timeout=timeout)
                            state.wireframe_json = out.get("wireframe_json", "")
                            state.dev_instructions = out.get("layout_instructions", "")
                            if state.dev_instructions:
                                st.success("✅ Dashboard instructions generated successfully!")
                
                with col2:
                    if st.button("📤 Upload New Image", key="upload_new_image"):
                        st.session_state['show_new_upload'] = True
                        st.rerun()
            
            # File uploader with optimization tips
            if not state.ai_analysis_result or st.session_state.get('show_new_upload', False):
                st.markdown("### 📤 Upload Your Wireframe")
                
                # Add tips for better performance
                with st.expander("💡 Tips for Faster Analysis", expanded=False):
                    st.markdown("""
                    **For best performance:**
                    - 📏 **Optimal size:** < 2MB (images are automatically optimized)
                    - 📐 **Resolution:** 1024x768 or smaller works great
                    - ✂️ **Crop tightly:** Focus on the main dashboard layout
                    - 🖼️ **Clear images:** Good lighting and contrast
                    - 📱 **Formats:** JPG/PNG recommended
                    
                    **What works well:**
                    - Hand-drawn sketches ✏️
                    - Digital wireframes 🖥️ 
                    - Whiteboard photos 📸
                    - Design mockups 🎨
                    """)
                
                uploaded_file = st.file_uploader(
                    "Choose an image file", 
                    type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                    help="Upload wireframes, sketches, screenshots, or mockups",
                    key="ai_vision_upload"
                )
                
                if uploaded_file:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.image(uploaded_file, caption=f"📸 {uploaded_file.name}", use_column_width=True)
                    
                    with col2:
                        st.markdown("**📊 Image Analysis:**")
                        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                        st.metric("File Size", f"{file_size_mb:.1f} MB")
                        st.metric("Type", f"{uploaded_file.type}")
                        
                        if file_size_mb > 10:
                            st.error("⚠️ File too large!")
                            st.caption("Max: 10MB")
                        else:
                            st.success("✅ Ready")
                    
                    if st.button("🚀 Analyze with AI Vision", type="primary", 
                               disabled=(file_size_mb > 10), use_container_width=True):
                        
                        result = upload_and_analyze_image(uploaded_file, platform, "ai_vision")
                        
                        if result:
                            layout_description = result.get("layout_description", "")
                            
                            st.success("🎉 AI Vision analysis completed successfully!")
                            
                            state.ai_analysis_result = layout_description
                            st.session_state['show_new_upload'] = False
                            
                            with st.expander("🔍 AI Vision Analysis Results", expanded=True):
                                st.markdown("### 🎯 Layout Analysis")
                                st.text_area(
                                    f"AI Analysis for {platform}:", 
                                    layout_description, 
                                    height=300, 
                                    key="ai_result_display_new",
                                    help="AI Vision analysis of your dashboard layout"
                                )
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                if st.button("✨ Generate Dashboard Instructions", type="primary", key="ai_generate_new"):
                                    with st.spinner("🔨 Creating detailed dashboard instructions..."):
                                        enhanced_prompt = prompt
                                        if prompt:
                                            enhanced_prompt += f"\n\nAI Vision Analysis:\n{layout_description}"
                                        else:
                                            enhanced_prompt = f"AI Vision Analysis:\n{layout_description}"
                                        
                                        # Dynamic timeout based on model complexity
                                        model_dict = safe_get_dict(state.model_metadata or {})
                                        tables = safe_get_list(model_dict.get("tables", []))
                                        total_columns = sum(len(safe_get_list(safe_get_dict(t).get("columns", []))) for t in tables)
                                        is_complex = len(tables) > 10 or total_columns > 100
                                        
                                        timeout = 240 if is_complex else 150  # 4 minutes for complex, 2.5 for others
                                        out = call_api("generate-layout", {
                                            "sketch_description": layout_description,
                                            "platform_selected": platform,
                                            "custom_prompt": enhanced_prompt,
                                            "model_metadata": state.model_metadata,
                                            "include_data_prep": False,
                                            "data_prep_only": False,
                                            "kpi_list": state.kpi_list,
                                            "data_dictionary": state.data_dictionary
                                        }, timeout=timeout)
                                        state.wireframe_json = out.get("wireframe_json", "")
                                        state.dev_instructions = out.get("layout_instructions", "")
                                        if state.dev_instructions:
                                            st.success("✅ Dashboard instructions generated successfully!")
                            
                            with col2:
                                if st.button("🔄 Re-analyze", key="reanalyze_new"):
                                    st.session_state['show_new_upload'] = True
                                    st.rerun()
                        else:
                            st.info("💡 **Suggestions:**\n- Try a different image\n- Use Simple Detection method\n- Or describe manually")

        # Simple Detection Method
        else:  # state.input_method == "simple"
            st.subheader("🔧 Simple Layout Detection")
            st.info("🛠️ **Backup Method** - Uses basic shape detection. Works without AI but provides less detailed analysis.")
            
            uploaded_file = st.file_uploader(
                "Upload dashboard image", 
                type=['png', 'jpg', 'jpeg'],
                help="🎯 **Works best with:** Clear wireframes, high contrast images, distinct geometric shapes",
                key="simple_detection_upload"
            )
            
            if uploaded_file:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.image(uploaded_file, caption=f"📸 {uploaded_file.name}", use_column_width=True)
                
                with col2:
                    st.markdown("**📊 File Info:**")
                    file_size_kb = len(uploaded_file.getvalue()) / 1024
                    st.write(f"📁 **Size:** {file_size_kb:.1f} KB")
                    st.write(f"🎨 **Type:** {uploaded_file.type}")
                
                if st.button("🔍 Detect Layout Shapes", type="primary", key="simple_detect"):
                    with st.spinner("🔍 Detecting layout elements..."):
                        result = upload_and_analyze_image(uploaded_file, platform, "simple_detection")
                        
                        if result:
                            layout_description = result.get("layout_description", "")
                            elements_found = result.get("elements_found", 0)
                            
                            if elements_found > 0:
                                st.success(f"✅ Detected {elements_found} layout elements!")
                            else:
                                st.warning("⚠️ No clear layout elements detected.")
                            
                            with st.expander("🔍 Detection Results", expanded=True):
                                st.text_area("Detected Layout:", layout_description, height=200, key="simple_result")
                            
                            st.markdown("### ✏️ Enhance Description")
                            manual_edit = st.text_area(
                                "Edit or enhance the detected layout:", 
                                layout_description, 
                                height=150,
                                key="manual_edit",
                                help="Improve the description by adding details the detection missed"
                            )
                            
                            if st.button("✨ Generate Dashboard Instructions", type="primary", key="simple_generate"):
                                with st.spinner("🔨 Generating dashboard instructions..."):
                                    # Dynamic timeout based on model complexity
                                    model_dict = safe_get_dict(state.model_metadata or {})
                                    tables = safe_get_list(model_dict.get("tables", []))
                                    total_columns = sum(len(safe_get_list(safe_get_dict(t).get("columns", []))) for t in tables)
                                    is_complex = len(tables) > 10 or total_columns > 100
                                    
                                    timeout = 240 if is_complex else 150  # 4 minutes for complex, 2.5 for others
                                    out = call_api("generate-layout", {
                                        "sketch_description": manual_edit,
                                        "platform_selected": platform,
                                        "custom_prompt": prompt,
                                        "model_metadata": state.model_metadata,
                                        "include_data_prep": False,
                                        "data_prep_only": False,
                                        "kpi_list": state.kpi_list,
                                        "data_dictionary": state.data_dictionary
                                    }, timeout=timeout)
                                    state.wireframe_json = out.get("wireframe_json", "")
                                    state.dev_instructions = out.get("layout_instructions", "")
                        else:
                            st.info("💡 Try the AI Vision method for better results.")

        # Results Display
        if state.wireframe_json or state.dev_instructions:
            st.markdown("---")
            st.header("📋 Generated Results")

        if state.wireframe_json:
            st.subheader("📐 Wireframe Structure")
            wf = (json.dumps(state.wireframe_json, indent=2)
                  if isinstance(state.wireframe_json, dict)
                  else str(state.wireframe_json))
            
            with st.expander("View Wireframe JSON", expanded=False):
                st.code(wf, language="json")
        
        if state.dev_instructions:
            st.subheader("🛠️ Dashboard Development Instructions")
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                st.download_button(
                    label="📥 Download MD",
                    data=state.dev_instructions,
                    file_name=f"dashboard_{platform.lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                    help="Download as Markdown file"
                )
            
            with col2:
                st.download_button(
                    label="📄 Download TXT", 
                    data=state.dev_instructions,
                    file_name=f"dashboard_{platform.lower().replace(' ', '_')}.txt",
                    mime="text/plain",
                    help="Download as text file"
                )
            
            with col3:
                if st.button("🔄 Regenerate", key="regen_instructions", help="Generate new instructions"):
                    state.dev_instructions = ""
                    st.rerun()
            
            with col4:
                if st.button("🗑️ Clear All", key="clear_results", help="Clear all results"):
                    state.wireframe_json = ""
                    state.dev_instructions = ""
                    state.ai_analysis_result = None
                    if 'show_new_upload' in st.session_state:
                        del st.session_state['show_new_upload']
                    st.rerun()
            
            st.markdown(tidy_md(state.dev_instructions))
            
            st.success("✅ Dashboard development instructions generated successfully!")
            
            with st.expander("💡 Implementation Guide & Next Steps", expanded=False):
                st.markdown(f"""
                ### 🎯 Implementation Roadmap for {platform}
                
                **Phase 1: Setup & Data (Week 1)**
                - ✅ Follow data preparation steps from previous section
                - ✅ Set up {platform} workspace and connections
                - ✅ Import and validate your data model
                
                **Phase 2: Core Visuals (Week 2-3)**  
                - ✅ Create measures and calculated fields first
                - ✅ Build primary visuals (KPIs, main charts)
                - ✅ Test functionality and data accuracy
                
                **Phase 3: Polish & Deploy (Week 4)**
                - ✅ Add filters, slicers, and interactivity
                - ✅ Apply formatting and styling
                - ✅ User testing and refinements
                
                ### 🚀 Ready for Project Planning?
                **Navigate to Sprint Board** to:
                - Break these instructions into manageable tasks
                - Get effort estimates and timeline planning
                - Create a structured development backlog
                
                ### 📊 Quality Checklist
                - [ ] All data connections working
                - [ ] Calculations producing expected results
                - [ ] Visuals displaying correctly
                - [ ] Filters and interactions functional
                - [ ] Performance acceptable for end users
                - [ ] Styling consistent with brand guidelines
                """)
            
            st.info("🎯 **Ready for Sprint Planning?** Navigate to **Sprint Board** to convert these instructions into actionable project tasks with estimates!")

# ─── Page: Sprint Board (Team Context hidden but functionality preserved) ─────
elif state.page == "Sprint Board":
    st.header("4️⃣ Sprint Board")
    st.markdown("**Overview:** Convert your prep & dev steps into sprint stories with estimations and timeline planning.")
    
    # Show progress
    render_progress_indicator(4, 4, "Sprint Planning")
    
    # Show estimated time
    render_estimated_time("sprint planning", 20)
    
    # Adaptive help
    render_adaptive_help(
        "What is Sprint Planning?",
        """Sprint planning breaks your project into manageable tasks with time estimates.
        
        **Key Concepts:**
        - **User Stories**: Small, focused tasks (e.g., "Create sales KPI card")
        - **Story Points**: Effort estimates (1 point ≈ simple task, 8 points ≈ complex)
        - **Velocity**: How many points your team completes per sprint
        - **Sprint**: Fixed time period (usually 1-2 weeks) to complete tasks
        
        This helps you deliver working dashboards incrementally!"""
    )
    
    if not state.model_metadata:
        st.info("Define your Data Model first under **Data Model**.")
    else:
        st.subheader("📋 Sprint Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📦 Include Tasks From:**")
            include_prep = st.checkbox("Data Prep Tasks", value=True, help="Include data preparation and cleaning tasks")
            include_dev = st.checkbox("Dashboard Dev Tasks", value=True, help="Include visual development and styling tasks")
            
            st.markdown("**⏱️ Sprint Settings:**")
            sprint_length = st.number_input("Sprint length (days)", min_value=1, max_value=30, value=14)
            velocity = st.number_input("Team velocity (story points)", min_value=1, max_value=100, value=20)
        
        with col2:
            st.markdown("**🎯 Priority Focus:**")
            priority_focus = st.selectbox("Primary focus", [
                "Speed (MVP approach)",
                "Quality (thorough testing)",
                "Features (comprehensive build)",
                "Balanced approach"
            ])
        
        # Hidden team context - default values used but not shown in UI
        team_size = 3  # Hidden default
        experience_level = "Mid-level (3-5 years)"  # Hidden default
        
        if st.button("🚀 Generate Sprint Backlog", type="primary", use_container_width=True):
            with st.spinner("🔄 Analyzing tasks and generating sprint stories with estimates..."):
                try:
                    wf_json = {}
                    if state.wireframe_json:
                        try:
                            wf_json = json.loads(state.wireframe_json) if isinstance(state.wireframe_json, str) else state.wireframe_json
                        except:
                            wf_json = {}
                    
                    parts = []
                    if include_prep and state.data_prep_instructions:
                        parts.append("## Data Preparation Tasks\n" + state.data_prep_instructions)
                    if include_dev and state.dev_instructions:
                        parts.append("## Dashboard Development Tasks\n" + state.dev_instructions)
                    
                    if not parts:
                        st.warning("⚠️ No instructions available. Please generate Data Prep or Dashboard Dev instructions first.")
                    else:
                        enhanced_instructions = "\n\n".join(parts)
                        
                        # Add persona modifier
                        persona_modifier = get_persona_prompt_modifier()
                        if persona_modifier:
                            enhanced_instructions += f"\n\n{persona_modifier}"
                        
                        enhanced_instructions += f"""
                        
## Team Context
- Team Size: {team_size} people
- Experience Level: {experience_level}
- Priority Focus: {priority_focus}
- Sprint Length: {sprint_length} days
- Target Velocity: {velocity} points
"""
                        
                        spr = call_api("generate-sprint", {
                            "wireframe_json": wf_json,
                            "layout_instructions": enhanced_instructions,
                            "sprint_length_days": sprint_length,
                            "velocity": velocity
                        })
                        
                        state.sprint_stories = spr.get("sprint_stories", [])
                        state.over_under_capacity = spr.get("over_under_capacity")
                        
                        if state.sprint_stories:
                            st.success("✅ Sprint backlog generated successfully!")
                        
                except Exception as e:
                    st.error(f"❌ Error generating sprint: {str(e)}")

        if state.sprint_stories:
            st.subheader("📋 Sprint Backlog")
            
            total_points = sum(story.get("points", 0) for story in state.sprint_stories)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Stories", len(state.sprint_stories))
            with col2:
                st.metric("Total Points", total_points)
            with col3:
                st.metric("Team Velocity", velocity)
            with col4:
                capacity_status = "Over" if state.over_under_capacity and state.over_under_capacity > 0 else "Under" if state.over_under_capacity and state.over_under_capacity < 0 else "On Track"
                st.metric("Capacity", capacity_status)
            
            if state.over_under_capacity is not None:
                if state.over_under_capacity > 0:
                    st.warning(f"⚠️ **Over capacity by {state.over_under_capacity} points.** Consider moving some stories to the next sprint or reducing scope.")
                elif state.over_under_capacity < 0:
                    st.info(f"📈 **Under capacity by {abs(state.over_under_capacity)} points.** You can add more stories or include additional polish tasks.")
                else:
                    st.success("✅ **Perfect capacity match!** Sprint is well-balanced for your team.")
            
            st.markdown("### 📋 User Stories")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                story_filter = st.selectbox("Filter by points:", ["All Stories", "1-3 points", "4-6 points", "7+ points"])
            with col2:
                sort_by = st.selectbox("Sort by:", ["Story Order", "Points (Low to High)", "Points (High to Low)"])
            
            filtered_stories = state.sprint_stories.copy()
            
            if story_filter != "All Stories":
                if story_filter == "1-3 points":
                    filtered_stories = [s for s in filtered_stories if 1 <= s.get("points", 0) <= 3]
                elif story_filter == "4-6 points":
                    filtered_stories = [s for s in filtered_stories if 4 <= s.get("points", 0) <= 6]
                elif story_filter == "7+ points":
                    filtered_stories = [s for s in filtered_stories if s.get("points", 0) >= 7]
            
            if sort_by == "Points (Low to High)":
                filtered_stories.sort(key=lambda x: x.get("points", 0))
            elif sort_by == "Points (High to Low)":
                filtered_stories.sort(key=lambda x: x.get("points", 0), reverse=True)
            
            for i, story in enumerate(filtered_stories, 1):
                title = story.get("title", f"Story {i}")
                points = story.get("points", 0)
                description = story.get("description", "No description available")
                
                if points <= 3:
                    color = "🟢"
                elif points <= 6:
                    color = "🟡"
                else:
                    color = "🔴"
                
                with st.expander(f"{color} **{title}** ({points} pts)", expanded=False):
                    st.markdown(f"**Story Points:** {points}")
                    st.markdown(f"**Description:**")
                    st.markdown(description)
            
            st.markdown("### 📤 Export Sprint Backlog")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sprint_data = {
                    "sprint_summary": {
                        "total_stories": len(state.sprint_stories),
                        "total_points": total_points,
                        "team_velocity": velocity,
                        "capacity_variance": state.over_under_capacity,
                        "sprint_length": sprint_length,
                        "team_size": team_size,
                        "experience_level": experience_level,
                        "priority_focus": priority_focus
                    },
                    "stories": state.sprint_stories
                }
                
                st.download_button(
                    label="📄 Download JSON",
                    data=json.dumps(sprint_data, indent=2),
                    file_name="sprint_backlog.json",
                    mime="application/json"
                )
            
            with col2:
                csv_data = "Title,Points,Description\n"
                for story in state.sprint_stories:
                    title = story.get("title", "").replace('"', '""')
                    points = story.get("points", 0)
                    desc = story.get("description", "").replace('"', '""').replace('\n', ' ')
                    csv_data += f'"{title}",{points},"{desc}"\n'
                
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name="sprint_backlog.csv",
                    mime="text/csv"
                )
            
            with col3:
                md_data = f"# Sprint Backlog\n\n"
                md_data += f"**Team Size:** {team_size} | **Velocity:** {velocity} pts | **Sprint Length:** {sprint_length} days\n\n"
                
                for i, story in enumerate(state.sprint_stories, 1):
                    md_data += f"## {i}. {story.get('title', f'Story {i}')} ({story.get('points', 0)} pts)\n\n"
                    md_data += f"{story.get('description', 'No description')}\n\n"
                
                st.download_button(
                    label="📝 Download MD",
                    data=md_data,
                    file_name="sprint_backlog.md",
                    mime="text/markdown"
                )
            
            with st.expander("💡 Sprint Execution Tips", expanded=False):
                st.markdown(f"""
                ### 🎯 Sprint Success Tips
                
                **Daily Standup Focus:**
                - What did I complete yesterday?
                - What will I work on today?
                - Are there any blockers or dependencies?
                
                **Story Point Guidelines:**
                - **1-2 points:** Simple tasks, 1-4 hours
                - **3-5 points:** Medium complexity, 1-2 days  
                - **6-8 points:** Complex tasks, 2-3 days
                - **9+ points:** Consider breaking down further
                
                **Quality Gates:**
                - [ ] Code/configuration reviewed
                - [ ] Functionality tested with sample data
                - [ ] Performance acceptable
                - [ ] Documentation updated
                - [ ] Stakeholder approval if needed
                
                **Risk Mitigation:**
                - Start with highest-risk stories first
                - Have backup stories ready if team finishes early
                - Plan for dependencies and external blockers
                - Regular check-ins with business stakeholders
                """)
            
            st.success("🎉 **Sprint backlog ready!** You now have a structured development plan with effort estimates and timeline.")
        
        elif not state.data_prep_instructions and not state.dev_instructions:
            st.info("📝 **Generate instructions first:** Complete the Data Prep and/or Dashboard Dev sections to create sprint stories.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔧 Go to Data Prep", use_container_width=True):
                    state.page = "Data Prep"
                    st.rerun()
            with col2:
                if st.button("📊 Go to Dashboard Dev", use_container_width=True):
                    state.page = "Dashboard Dev"
                    st.rerun()

# ─── Page: Help ─────────────────────────────────────────────────────────────────
elif state.page == "Help":
    st.header("❓ Help & User Guide")
    st.markdown("Learn how to use the BI Assistant effectively with personalized modes")
    
    # Help navigation
    help_tab1, help_tab2, help_tab3, help_tab4 = st.tabs(["📚 Overview", "👤 Persona Modes", "🛠️ Features", "💡 Tips"])
    
    with help_tab1:
        st.subheader("Welcome to BI Assistant!")
        
        st.markdown("""
        ### 🎯 What is BI Assistant?
        
        BI Assistant is an AI-powered tool that helps you transform wireframe sketches and ideas into 
        fully functional BI dashboards. It guides you through the entire process from data modeling 
        to sprint planning.
        
        ### 🔄 The Workflow
        
        1. **🏗️ Data Model**: Define your data structure (tables, relationships)
        2. **🔧 Data Prep**: Get AI-generated data preparation instructions
        3. **📊 Dashboard Dev**: Convert wireframes into dashboard layouts
        4. **📋 Sprint Board**: Plan your development with sprint stories
        
        ### 🚀 Getting Started
        
        1. Start with the **Data Model** page
        2. Upload your SQL DDL files or create a JSON schema
        3. Progress through each step sequentially
        4. Download your outputs at any stage
        """)
        
        persona = get_current_persona()
        if persona and not persona.get("skipped", False):
            level = persona.get("experience_level", "intermediate")
            st.info(f"You're currently in **{level.title()} Mode**. The interface is adapted to your experience level!")
    
    with help_tab2:
        st.subheader("👤 Understanding Persona Modes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🌱 Beginner Mode
            
            **Perfect for:**
            - First-time BI dashboard creators
            - Learning the fundamentals
            - Step-by-step guidance needed
            
            **What you'll see:**
            - 💡 Helpful tips and explanations
            - 📝 Examples and templates
            - ⏱️ Time estimates for tasks
            - 📊 Progress indicators
            - ❓ "What is this?" help boxes
            
            **Benefits:**
            - Learn BI concepts as you build
            - Avoid common mistakes
            - Build confidence gradually
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Intermediate Mode
            
            **Perfect for:**
            - Some BI experience
            - Building proficiency
            - Balanced guidance
            
            **What you'll see:**
            - ℹ️ Key tips when helpful
            - ⏱️ Time estimates
            - 📊 Progress tracking
            - Standard options
            
            **Benefits:**
            - Efficient workflow
            - Helpful reminders
            - Room to explore
            """)
        
        with col3:
            st.markdown("""
            ### 🚀 Expert Mode
            
            **Perfect for:**
            - BI professionals
            - Maximum efficiency
            - Minimal interruptions
            
            **What you'll see:**
            - Clean, minimal interface
            - Advanced options visible
            - Direct access to features
            - No basic explanations
            
            **Benefits:**
            - Fast workflow
            - Advanced capabilities
            - Professional outputs
            """)
        
        st.markdown("---")
        
        st.subheader("🎯 Primary Goals")
        
        goal_col1, goal_col2, goal_col3 = st.columns(3)
        
        with goal_col1:
            st.markdown("""
            ### 📚 Learning & Building
            - Educational focus
            - Concept explanations
            - Best practices guidance
            """)
        
        with goal_col2:
            st.markdown("""
            ### 🏭 Asset Generation
            - Template creation
            - Bulk processing
            - Reusable components
            """)
        
        with goal_col3:
            st.markdown("""
            ### 💼 Client Delivery
            - Professional outputs
            - Export emphasis
            - Polished results
            """)
    
    with help_tab3:
        st.subheader("🛠️ Feature Guide")
        
        with st.expander("🏗️ Data Model", expanded=True):
            st.markdown("""
            **Purpose:** Define your data structure
            
            **Options:**
            - **Upload SQL DDL**: Best for existing databases
            - **Manual JSON**: For custom schemas
            - **Templates**: Quick start options
            
            **Tips:**
            - Start with 5-10 key tables
            - Always include relationships file
            - Review generated JSON before proceeding
            """)
        
        with st.expander("🔧 Data Prep"):
            st.markdown("""
            **Purpose:** Generate data preparation instructions
            
            **Features:**
            - Platform-specific guidance (Power BI, Tableau, etc.)
            - KPI list integration
            - Data dictionary support
            
            **Outputs:**
            - Step-by-step prep instructions
            - Platform best practices
            - Data quality checks
            """)
        
        with st.expander("📊 Dashboard Dev"):
            st.markdown("""
            **Purpose:** Convert wireframes to layouts
            
            **Input Methods:**
            - **Text Description**: Describe your dashboard
            - **Image Upload**: Upload wireframe sketches
            - **AI Vision**: Automatic layout detection
            
            **Outputs:**
            - Component specifications
            - Layout instructions
            - Styling guidelines
            """)
        
        with st.expander("📋 Sprint Board"):
            st.markdown("""
            **Purpose:** Agile project planning
            
            **Features:**
            - Story point estimation
            - Sprint capacity planning
            - Task prioritization
            
            **Outputs:**
            - User stories (JSON/CSV/MD)
            - Sprint timeline
            - Capacity analysis
            """)
    
    with help_tab4:
        st.subheader("💡 Pro Tips")
        
        persona = get_current_persona()
        level = persona.get("experience_level", "intermediate") if persona else "intermediate"
        
        if level == "beginner":
            st.markdown("""
            ### 🌱 Tips for Beginners
            
            1. **Start Simple**: Begin with 3-5 tables in your data model
            2. **Use Templates**: Look for example files in the test_cases folder
            3. **Read the Hints**: Hover over ℹ️ icons for helpful information
            4. **Take Your Time**: Follow the estimated times for each task
            5. **Ask Questions**: Use the help boxes to understand concepts
            
            ### 📈 Learning Path
            1. Complete a simple dashboard end-to-end
            2. Try different visualization types
            3. Experiment with different platforms
            4. Graduate to Intermediate mode when ready!
            """)
        
        elif level == "intermediate":
            st.markdown("""
            ### 📊 Tips for Intermediate Users
            
            1. **Batch Processing**: Upload multiple DDL files at once
            2. **Custom KPIs**: Define business-specific metrics
            3. **Platform Features**: Explore platform-specific optimizations
            4. **Sprint Planning**: Use realistic velocity estimates
            
            ### 🚀 Efficiency Boosters
            - Use keyboard shortcuts
            - Save templates for reuse
            - Leverage AI suggestions
            - Try Expert mode for faster workflows
            """)
        
        else:  # expert
            st.markdown("""
            ### 🚀 Expert Power User Tips
            
            1. **API Integration**: Use the FastAPI endpoints directly
            2. **Bulk Operations**: Process multiple projects in parallel
            3. **Custom Prompts**: Modify AI prompts for specific needs
            4. **Advanced Schemas**: Handle complex multi-schema models
            
            ### ⚡ Maximum Efficiency
            - Skip manual reviews with trusted schemas
            - Use JSON imports/exports for automation
            - Create project templates
            - Integrate with CI/CD pipelines
            """)
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("🎬 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Switch Persona Mode", use_container_width=True):
                # Reset onboarding flags to allow re-selection
                st.session_state.show_onboarding = True
                st.session_state.onboarding_completed = False
                # Clear any temporary selections
                for key in ['temp_experience', 'temp_goal']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()
        
        with col2:
            if st.button("📥 Download Sample Files", use_container_width=True):
                st.info("Check the test_cases folder for sample files!")
        
        with col3:
            if st.button("🏠 Back to Start", use_container_width=True):
                state.page = "Data Model"
                st.rerun()

# ─── Default Case ─────────────────────────────────────────────────────────────────
else:
    st.error(f"Unknown page: {state.page}")
    if st.button("🏠 Go to Home"):
        state.page = "Data Model"
        st.rerun()