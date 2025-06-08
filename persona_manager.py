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
    
    if level == "beginner":
        modifiers.append("Explain concepts in simple terms suitable for someone new to BI dashboards.")
        modifiers.append("Include step-by-step instructions with clear explanations.")
    elif level == "expert":
        modifiers.append("Provide concise, technical instructions without basic explanations.")
        modifiers.append("Focus on advanced features and optimization techniques.")
    
    if goal == "asset_generation":
        modifiers.append("Emphasize reusability and template patterns.")
    elif goal == "client_delivery":
        modifiers.append("Focus on professional presentation and client-ready outputs.")
    
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
        
        # Question 2: Primary Goal
        st.markdown("### 2️⃣ What's your primary goal?")
        
        goal_col1, goal_col2, goal_col3 = st.columns(3)
        
        primary_goal = None
        
        with goal_col1:
            if st.button(f"{GOALS['learning']['icon']} {GOALS['learning']['button_text']}", 
                        use_container_width=True,
                        help=GOALS['learning']['description']):
                primary_goal = "learning"
        
        with goal_col2:
            if st.button(f"{GOALS['asset_generation']['icon']} {GOALS['asset_generation']['button_text']}", 
                        use_container_width=True,
                        help=GOALS['asset_generation']['description']):
                primary_goal = "asset_generation"
        
        with goal_col3:
            if st.button(f"{GOALS['client_delivery']['icon']} {GOALS['client_delivery']['button_text']}", 
                        use_container_width=True,
                        help=GOALS['client_delivery']['description']):
                primary_goal = "client_delivery"
        
        if primary_goal:
            st.session_state.temp_goal = primary_goal
        
        # Show current selections
        if hasattr(st.session_state, 'temp_experience') or hasattr(st.session_state, 'temp_goal'):
            st.markdown("---")
            st.markdown("**Your selections:**")
            
            if hasattr(st.session_state, 'temp_experience'):
                exp = PERSONAS[st.session_state.temp_experience]
                st.markdown(f"- Experience: {exp['icon']} **{exp['name']}**")
            
            if hasattr(st.session_state, 'temp_goal'):
                goal = GOALS[st.session_state.temp_goal]
                st.markdown(f"- Goal: {goal['icon']} **{goal['name']}**")
        
        # Action buttons
        st.markdown("---")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("Skip for now", use_container_width=True, type="secondary"):
                st.session_state.user_persona = {
                    "experience_level": "intermediate",
                    "primary_goal": "learning",
                    "skipped": True
                }
                st.session_state.onboarding_completed = True
                st.session_state.show_onboarding = False
                # Clean up temp variables
                for key in ['temp_experience', 'temp_goal']:
                    if hasattr(st.session_state, key):
                        delattr(st.session_state, key)
                st.rerun()
        
        with action_col2:
            # Enable Continue only if both selections made
            can_continue = (hasattr(st.session_state, 'temp_experience') and 
                          hasattr(st.session_state, 'temp_goal'))
            
            if st.button("Continue →", 
                        use_container_width=True, 
                        type="primary",
                        disabled=not can_continue):
                if can_continue:
                    st.session_state.user_persona = {
                        "experience_level": st.session_state.temp_experience,
                        "primary_goal": st.session_state.temp_goal,
                        "skipped": False
                    }
                    st.session_state.onboarding_completed = True
                    st.session_state.show_onboarding = False
                    # Clean up temp variables
                    delattr(st.session_state, 'temp_experience')
                    delattr(st.session_state, 'temp_goal')
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
        for key in ['temp_experience', 'temp_goal']:
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