# persona_manager.py - Persona Detection and Adaptive UI Components

import streamlit as st
from typing import Dict, Optional, Tuple
import json

# Persona definitions
PERSONAS = {
    "beginner": {
        "name": "Beginner",
        "icon": "🌱",
        "description": "New to BI dashboards, learning the ropes",
        "features": {
            "show_tips": True,
            "show_examples": True,
            "show_progress": True,
            "detailed_explanations": True,
            "estimated_times": True,
            "simplified_options": True
        }
    },
    "intermediate": {
        "name": "Intermediate",
        "icon": "📊",
        "description": "Familiar with BI concepts, building experience",
        "features": {
            "show_tips": True,
            "show_examples": False,
            "show_progress": True,
            "detailed_explanations": False,
            "estimated_times": True,
            "simplified_options": False
        }
    },
    "expert": {
        "name": "Expert",
        "icon": "🚀",
        "description": "BI professional, focused on efficiency",
        "features": {
            "show_tips": False,
            "show_examples": False,
            "show_progress": False,
            "detailed_explanations": False,
            "estimated_times": False,
            "simplified_options": False
        }
    }
}

GOALS = {
    "learning": {
        "name": "Learning & Building",
        "icon": "📚",
        "button_text": "I want to learn how to build",
        "description": "Understanding BI concepts while creating dashboards",
        "adaptations": {
            "show_learning_resources": True,
            "step_by_step_guidance": True,
            "concept_explanations": True
        }
    },
    "asset_generation": {
        "name": "Asset Generation", 
        "icon": "🏭",
        "button_text": "I want delivery assets",
        "description": "Creating reusable templates and components",
        "adaptations": {
            "emphasis_on_downloads": True,
            "batch_processing": True,
            "template_library": True
        }
    },
    "client_delivery": {
        "name": "Client Delivery",
        "icon": "💼", 
        "button_text": "I want to deliver solutions",
        "description": "Delivering polished dashboards to clients",
        "adaptations": {
            "professional_outputs": True,
            "export_options": True,
            "client_ready_docs": True
        }
    }
}

# NEW OBJECTIVES for replacement
OBJECTIVES = {
    "client_assets": {
        "name": "Client Assets",
        "icon": "📋",
        "description": "Generate deliverable materials for client engagements (KPIs, relationships documentation, data model exports, business context)",
        "sections": ["kpis", "relationships", "data_model_exports", "business_context", "data_dictionary"]
    },
    "dashboard_build": {
        "name": "Dashboard Build",
        "icon": "🔧",
        "description": "Focus on creating the actual dashboard solution (data prep implementation, dashboard dev instructions, technical details)",
        "sections": ["transformations", "technical_implementation", "m_code_dax", "performance_optimization", "validation_steps"]
    }
}


def initialize_persona_state():
    """Initialize persona-related session state variables"""
    if "user_persona" not in st.session_state:
        st.session_state.user_persona = None
    
    if "onboarding_completed" not in st.session_state:
        st.session_state.onboarding_completed = False
    
    if "show_onboarding" not in st.session_state:
        st.session_state.show_onboarding = True


def get_current_persona() -> Optional[Dict]:
    """Get the current user persona configuration"""
    if st.session_state.user_persona:
        return st.session_state.user_persona
    return None


def get_current_objectives() -> list:
    """Get the current selected objectives (for new checkbox system)"""
    if hasattr(st.session_state, 'selected_objectives') and st.session_state.selected_objectives:
        return st.session_state.selected_objectives
    return []


def initialize_objectives_state():
    """Initialize objectives-related session state"""
    if "selected_objectives" not in st.session_state:
        st.session_state.selected_objectives = []


def should_show_feature(feature: str) -> bool:
    """Check if a feature should be shown based on current persona"""
    persona = get_current_persona()
    if not persona:
        return True  # Default to showing features if no persona set
    
    level = persona.get("experience_level", "intermediate")
    persona_config = PERSONAS.get(level, PERSONAS["intermediate"])
    
    return persona_config["features"].get(feature, True)


def get_persona_prompt_modifier() -> str:
    """Get a prompt modifier based on current persona for AI requests"""
    persona = get_current_persona()
    if not persona:
        return ""
    
    level = persona.get("experience_level", "intermediate")
    goal = persona.get("primary_goal", "learning")
    
    modifiers = []
    
    # Enhanced experience-based modifiers
    if level == "beginner":
        modifiers.append("Explain concepts in simple terms suitable for someone new to BI dashboards.")
        modifiers.append("Include step-by-step instructions with clear explanations.")
        modifiers.append("Assume zero prior knowledge and explain technical terms.")
        modifiers.append("Make AI-generated instructions ultra-detailed with comprehensive coverage.")
        modifiers.append("For data prep: explain every single transformation, even if repetitive.")
        modifiers.append("For dashboard dev: explain every visualization thoroughly, regardless of similarity.")
    elif level == "expert":
        modifiers.append("Provide concise, technical instructions without basic explanations.")
        modifiers.append("Focus on advanced features and optimization techniques.")
        modifiers.append("Condense instructions into summaries focusing on quick asset access.")
        modifiers.append("Use technical terminology without explanation.")
        modifiers.append("Focus on performance and optimization over explanations.")
    else:  # intermediate
        modifiers.append("Balance detail with efficiency for users with some BI experience.")
        modifiers.append("Group similar transformations and provide structured instructions.")
        modifiers.append("Include key validations for critical transformations.")
        modifiers.append("Provide both UI and code options when applicable.")
    
    # Enhanced goal-based modifiers
    if goal == "asset_generation":
        modifiers.append("Emphasize reusability and template patterns.")
        modifiers.append("Focus on creating downloadable, reusable assets.")
    elif goal == "client_delivery":
        modifiers.append("Focus on professional presentation and client-ready outputs.")
        modifiers.append("Ensure polished, production-ready deliverables.")
    elif goal == "learning":
        modifiers.append("Include educational context and concept explanations.")
        modifiers.append("Provide learning-focused guidance with why explanations.")
    
    return " ".join(modifiers)


def get_enhanced_prompt_modifier(objectives: list = None) -> str:
    """Get enhanced prompt modifier supporting multiple objectives"""
    persona = get_current_persona()
    if not persona:
        return ""
    
    level = persona.get("experience_level", "intermediate")
    modifiers = []
    
    # Experience-based instruction complexity
    if level == "beginner":
        modifiers.append("BEGINNER MODE: Provide ultra-detailed, step-by-step instructions with comprehensive explanations.")
        modifiers.append("Explain every technical term and assume zero prior knowledge.")
        modifiers.append("Include validation steps and common troubleshooting tips.")
    elif level == "expert":
        modifiers.append("EXPERT MODE: Provide condensed, technical summaries without basic explanations.")
        modifiers.append("Focus on efficiency, patterns, and optimization techniques.")
        modifiers.append("Use advanced terminology and code-first approaches.")
    else:  # intermediate
        modifiers.append("INTERMEDIATE MODE: Balance detail with efficiency, group similar operations.")
        modifiers.append("Provide both UI and code approaches where applicable.")
        modifiers.append("Include key validations for critical steps.")
    
    # Objective-based content filtering
    if objectives:
        if "client_assets" in objectives:
            modifiers.append("Include business-focused content: KPIs, relationships, data models, business context.")
        if "dashboard_build" in objectives:
            modifiers.append("Include technical implementation: transformations, code, performance optimization.")
        if len(objectives) > 1:
            modifiers.append("Organize content with clear sections for different objectives.")
    
    return " ".join(modifiers)


def render_onboarding_modal():
    """Render the onboarding modal for new users"""
    
    # Center the modal on the page
    st.markdown("""
    <style>
    .onboarding-container {
        background-color: white;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 700px;
        border: 1px solid #e0e0e0;
    }
    .onboarding-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo-container {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main[data-testid="stAppViewContainer"] {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo
        import base64
        import os
        
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_data}" 
                     style="height: 80px; width: auto; margin-bottom: 1rem;" 
                     alt="BI Assistant Logo">
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fallback if logo.png not found
            st.markdown("""
            <div class="logo-container">
                <h2 style="color: #0C62FB; margin-bottom: 1rem;">📊 BI Assistant</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Welcome Header
        st.markdown("""
        <div class="onboarding-header">
            <h1 style="color: #333; margin-bottom: 0.5rem;">Welcome to the AI BI Workflow Accelerator</h1>
            <p style="color: #666; font-size: 1.1rem; margin-bottom: 1rem;">Let's personalize your experience in just 2 quick questions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Question 1: Experience Level
        st.markdown("### 1️⃣ What's your BI dashboard experience level?")
        
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        
        experience_level = None
        
        with exp_col1:
            if st.button(f"{PERSONAS['beginner']['icon']} Beginner", 
                        use_container_width=True,
                        help="New to BI dashboards, learning the basics"):
                experience_level = "beginner"
        
        with exp_col2:
            if st.button(f"{PERSONAS['intermediate']['icon']} Intermediate", 
                        use_container_width=True,
                        help="Familiar with BI concepts, building experience"):
                experience_level = "intermediate"
        
        with exp_col3:
            if st.button(f"{PERSONAS['expert']['icon']} Expert", 
                        use_container_width=True,
                        help="BI professional, focused on efficiency"):
                experience_level = "expert"
        
        if experience_level:
            st.session_state.temp_experience = experience_level
        
        # Question 2: Project Objectives (NEW SYSTEM)
        st.markdown("### 2️⃣ What are your project objectives?")
        st.markdown("Select what you need (you can choose both):")
        
        # Initialize objectives state
        if 'temp_objectives' not in st.session_state:
            st.session_state.temp_objectives = []
        
        obj_col1, obj_col2 = st.columns(2)
        
        with obj_col1:
            client_assets_selected = st.checkbox(
                f"{OBJECTIVES['client_assets']['icon']} **{OBJECTIVES['client_assets']['name']}**",
                value="client_assets" in st.session_state.temp_objectives,
                help=OBJECTIVES['client_assets']['description'],
                key="onboarding_client_assets"
            )
        
        with obj_col2:
            dashboard_build_selected = st.checkbox(
                f"{OBJECTIVES['dashboard_build']['icon']} **{OBJECTIVES['dashboard_build']['name']}**",
                value="dashboard_build" in st.session_state.temp_objectives,
                help=OBJECTIVES['dashboard_build']['description'],
                key="onboarding_dashboard_build"
            )
        
        # Update temp objectives
        new_temp_objectives = []
        if client_assets_selected:
            new_temp_objectives.append("client_assets")
        if dashboard_build_selected:
            new_temp_objectives.append("dashboard_build")
        
        st.session_state.temp_objectives = new_temp_objectives
        
        # Show helper text
        if not new_temp_objectives:
            st.info("💡 Select at least one objective to customize your experience.")
        elif len(new_temp_objectives) == 2:
            st.success("✅ Both objectives selected - you'll get comprehensive, organized content.")
        else:
            selected_obj = OBJECTIVES[new_temp_objectives[0]]
            st.success(f"✅ {selected_obj['icon']} {selected_obj['name']} selected.")
        
        # Objectives are handled above via checkboxes
        
        # Show current selections
        if hasattr(st.session_state, 'temp_experience') or st.session_state.temp_objectives:
            st.markdown("---")
            st.markdown("**Your selections:**")
            
            if hasattr(st.session_state, 'temp_experience'):
                exp = PERSONAS[st.session_state.temp_experience]
                st.markdown(f"- Experience: {exp['icon']} **{exp['name']}**")
            
            if st.session_state.temp_objectives:
                obj_names = [f"{OBJECTIVES[obj]['icon']} {OBJECTIVES[obj]['name']}" for obj in st.session_state.temp_objectives]
                st.markdown(f"- Objectives: {', '.join(obj_names)}")
        
        # Action buttons
        st.markdown("---")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("Skip for now", use_container_width=True, type="secondary"):
                st.session_state.user_persona = {
                    "experience_level": "intermediate",
                    "primary_goal": "learning",  # Keep for legacy compatibility
                    "skipped": True
                }
                st.session_state.selected_objectives = ["dashboard_build"]  # Default to dashboard build
                st.session_state.onboarding_completed = True
                st.session_state.show_onboarding = False
                # Clean up temp variables
                for key in ['temp_experience', 'temp_objectives']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()
        
        with action_col2:
            # Enable Continue only if both selections made
            can_continue = (hasattr(st.session_state, 'temp_experience') and 
                          len(st.session_state.temp_objectives) > 0)
            
            if st.button("Continue →", 
                        use_container_width=True, 
                        type="primary",
                        disabled=not can_continue):
                if can_continue:
                    st.session_state.user_persona = {
                        "experience_level": st.session_state.temp_experience,
                        "primary_goal": "learning",  # Keep for legacy compatibility
                        "skipped": False
                    }
                    st.session_state.selected_objectives = st.session_state.temp_objectives.copy()
                    st.session_state.onboarding_completed = True
                    st.session_state.show_onboarding = False
                    # Clean up temp variables
                    delattr(st.session_state, 'temp_experience')
                    delattr(st.session_state, 'temp_objectives')
                    st.rerun()


def render_persona_indicator():
    """Render the current persona indicator in the sidebar"""
    persona = get_current_persona()
    if not persona:
        return
    
    level = persona.get("experience_level", "intermediate")
    goal = persona.get("primary_goal", "learning")
    
    persona_config = PERSONAS.get(level, PERSONAS["intermediate"])
    goal_config = GOALS.get(goal, GOALS["learning"])
    
    st.sidebar.markdown(f"""
    <div style='background-color: white; border: 1px solid #dee2e6; padding: 0.75rem; border-radius: 8px; margin: 1rem 0;'>
        <div style='font-size: 0.9rem; color: #6c757d; margin-bottom: 0.5rem;'>Current Mode</div>
        <div style='font-weight: 600; color: black;'>
            {persona_config['icon']} {persona_config['name']} Mode
        </div>
        <div style='font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem;'>
            {goal_config['icon']} {goal_config['name']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Switch mode button
    if st.sidebar.button("🔄 Switch Mode", use_container_width=True, key="switch_persona"):
        # Reset onboarding flags to allow re-selection
        st.session_state.show_onboarding = True
        st.session_state.onboarding_completed = False
        # Clear any temporary selections
        for key in ['temp_experience', 'temp_objectives']:
            if hasattr(st.session_state, key):
                delattr(st.session_state, key)
        st.rerun()


def render_adaptive_help(context: str, content: str):
    """Render help content that adapts based on persona"""
    if not should_show_feature("show_tips"):
        return
    
    persona = get_current_persona()
    level = persona.get("experience_level", "intermediate") if persona else "intermediate"
    
    # Adjust help style based on experience level
    if level == "beginner":
        icon = "💡"
        title = "Helpful Tip"
        style = "info"
    elif level == "expert":
        # Experts don't see basic tips
        return
    else:
        icon = "ℹ️"
        title = "Note"
        style = "info"
    
    with st.expander(f"{icon} {title}: {context}", expanded=(level == "beginner")):
        st.markdown(content)


def render_progress_indicator(current_step: int, total_steps: int, step_name: str):
    """Render a progress indicator if appropriate for persona"""
    if not should_show_feature("show_progress"):
        return
    
    progress = current_step / total_steps
    progress_percent = int(progress * 100)
    
    # Custom progress bar with better contrast
    st.markdown(f"""
    <style>
    .custom-progress-container {{
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        margin: 10px 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }}
    .custom-progress-bar {{
        background: linear-gradient(90deg, #0C62FB 0%, #0A52D9 100%);
        height: 100%;
        width: {progress_percent}%;
        border-radius: 10px;
        transition: width 0.3s ease;
        position: relative;
    }}
    .custom-progress-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    .progress-label {{
        color: #666;
        font-size: 14px;
        margin-bottom: 5px;
        font-weight: 500;
    }}
    </style>
    <div class="progress-label">Step {current_step} of {total_steps}: {step_name}</div>
    <div class="custom-progress-container">
        <div class="custom-progress-bar">
            <div class="custom-progress-text">{progress_percent}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_estimated_time(task: str, minutes: int):
    """Show estimated time for tasks if appropriate for persona"""
    if not should_show_feature("estimated_times"):
        return
    
    if minutes < 60:
        time_str = f"{minutes} min"
    else:
        hours = minutes // 60
        mins = minutes % 60
        time_str = f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    
    st.caption(f"⏱️ Estimated time for {task}: {time_str}")


def get_adaptive_button_text(base_text: str, action_type: str) -> str:
    """Get button text adapted to persona"""
    persona = get_current_persona()
    if not persona:
        return base_text
    
    level = persona.get("experience_level", "intermediate")
    goal = persona.get("primary_goal", "learning")
    
    # Add context for beginners
    if level == "beginner" and action_type == "generate":
        return f"{base_text} (AI will help)"
    elif goal == "asset_generation" and action_type == "download":
        return f"⬇️ {base_text} (Template)"
    
    return base_text


def render_example_content(title: str, content: str):
    """Show examples if appropriate for persona"""
    if not should_show_feature("show_examples"):
        return
    
    with st.expander(f"📝 Example: {title}"):
        st.markdown(content)


def get_sample_inputs_for_persona(field_type: str) -> dict:
    """Get sample inputs based on persona level"""
    persona = get_current_persona()
    level = persona.get("experience_level", "intermediate") if persona else "intermediate"
    
    samples = {
        "beginner": {
            "sketch_description": "Top row: 3 KPI cards showing Total Sales, Orders, and Customers. Middle: Large bar chart of Sales by Month. Bottom left: Table of Top Products. Bottom right: Pie chart of Sales by Category.",
            "wireframe_text": "Dashboard with sales metrics at top, main chart in center, details below",
            "custom_prompt": "Make this beginner-friendly with clear labels and explanations",
            "kpi_notes": "Total Sales: sum of all sales amounts. Customer Count: unique customers. Order Count: total number of orders.",
            "data_dict_notes": "Sales table has: SaleID (unique identifier), Amount (price), Date (when sold), CustomerID (who bought). Product table has: ProductID, Name, Category."
        },
        "intermediate": {
            "sketch_description": "Executive dashboard: KPI row (Revenue, Growth %, Margin), trend analysis section, regional breakdown, performance metrics",
            "custom_prompt": "Focus on actionable insights and drill-down capabilities",
            "kpi_notes": "Revenue YoY growth, Gross margin percentage, Customer acquisition cost, Lifetime value trends"
        },
        "expert": {
            "sketch_description": "Advanced analytics dashboard with time-series forecasting, cohort analysis, and performance attribution modeling",
            "custom_prompt": "Implement advanced DAX/calculated fields for complex business logic"
        }
    }
    
    return samples.get(level, {}).get(field_type, "")


def should_show_sample_input(field_type: str) -> bool:
    """Determine if sample input should be shown based on persona"""
    persona = get_current_persona()
    if not persona:
        return True
    
    level = persona.get("experience_level", "intermediate")
    
    # Beginners see samples for all fields
    if level == "beginner":
        return True
    
    # Intermediates see samples for complex fields only
    if level == "intermediate":
        complex_fields = ["kpi_notes", "data_dict_notes", "custom_prompt"]
        return field_type in complex_fields
    
    # Experts don't see sample inputs
    return False