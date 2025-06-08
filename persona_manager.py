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
    with st.container():
        st.markdown("""
        <style>
        .onboarding-container {
            background-color: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 2rem auto;
            max-width: 600px;
        }
        .onboarding-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .persona-option {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .persona-option:hover {
            background-color: #e9ecef;
            border-color: #0C62FB;
        }
        .persona-selected {
            background-color: #e7f1ff;
            border-color: #0C62FB;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="onboarding-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="onboarding-header">
            <h2>👋 Welcome to BI Assistant!</h2>
            <p>Let's personalize your experience in just 2 quick questions</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Question 1: Experience Level
        st.markdown("### 1️⃣ What's your BI dashboard experience level?")
        
        col1, col2, col3 = st.columns(3)
        
        experience_level = None
        
        with col1:
            if st.button(f"{PERSONAS['beginner']['icon']} Beginner", 
                        use_container_width=True,
                        help="New to BI dashboards, learning the basics"):
                experience_level = "beginner"
        
        with col2:
            if st.button(f"{PERSONAS['intermediate']['icon']} Intermediate", 
                        use_container_width=True,
                        help="Familiar with BI concepts, building experience"):
                experience_level = "intermediate"
        
        with col3:
            if st.button(f"{PERSONAS['expert']['icon']} Expert", 
                        use_container_width=True,
                        help="BI professional, focused on efficiency"):
                experience_level = "expert"
        
        if experience_level:
            st.session_state.temp_experience = experience_level
        
        # Question 2: Primary Goal
        st.markdown("### 2️⃣ What's your primary goal?")
        
        col1, col2, col3 = st.columns(3)
        
        primary_goal = None
        
        with col1:
            if st.button(f"{GOALS['learning']['icon']} Learning", 
                        use_container_width=True,
                        help="Understanding BI while building"):
                primary_goal = "learning"
        
        with col2:
            if st.button(f"{GOALS['asset_generation']['icon']} Assets", 
                        use_container_width=True,
                        help="Creating reusable templates"):
                primary_goal = "asset_generation"
        
        with col3:
            if st.button(f"{GOALS['client_delivery']['icon']} Delivery", 
                        use_container_width=True,
                        help="Delivering to clients"):
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
        
        col1, col2 = st.columns(2)
        
        with col1:
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
        
        with col2:
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
        
        st.markdown('</div>', unsafe_allow_html=True)


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
        st.session_state.show_onboarding = True
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
    st.progress(progress)
    st.caption(f"Step {current_step} of {total_steps}: {step_name}")


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