import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load your OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Wireframe to Layout Assistant", layout="centered")
st.title("📐 Wireframe to Layout Instruction Generator")

st.markdown("### ✏️ Step 1: Describe your dashboard layout sketch")

description = st.text_area("Describe layout like a wireframe (pseudo-OCR)", height=200, placeholder="""
Example:
Top: KPI - Net Sales
Top: KPI - Gross Margin %
Left Sidebar: Slicer - Region
Left Sidebar: Slicer - Year
Main: Line Chart - Sales Trend Over Time
Main: Bar Chart - Sales by Product Category
Bottom: Table - Detailed Sales by Store
""")

# Button to generate JSON wireframe
if st.button("✨ Generate JSON Wireframe"):
    if description.strip():
        prompt = f"""You are a dashboard assistant. A wireframe layout was described as:

{description}

Please return a JSON object with layout_type as 'grid' and a sections array. Each section must have:
- zone
- visual_title
- visual_type

Only return valid JSON. No commentary. Example format:
{{
  "layout_type": "grid",
  "sections": [...]
}}"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that converts dashboard sketches to structured layout JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            # Display JSON wireframe
            json_text = response['choices'][0]['message']['content']
            st.subheader("✅ Generated JSON Wireframe:")
            st.code(json_text, language="json")

            # Store json_text in session state to use for downstream step
            st.session_state["json_text"] = json_text

        except Exception as e:
            st.error(f"Error from OpenAI: {e}")
    else:
        st.warning("Please enter a description first.")

# Button to generate layout instructions
st.markdown("---")
st.markdown("### 🧠 Step 2: Generate layout instructions from JSON")

if "json_text" in st.session_state:
    if st.button("📐 Generate Layout Instructions"):
        try:
            layout_prompt = f"""You are a dashboard layout assistant. 
Given the following wireframe JSON layout, generate step-by-step layout instructions for Power BI. 
Be specific about placement, zones (e.g., Top, Left Sidebar, Main), spacing, grouping, and best practices.

Wireframe JSON:
{st.session_state["json_text"]}

Instructions:"""

            layout_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You generate detailed layout build instructions for dashboards."},
                    {"role": "user", "content": layout_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )

            layout_instructions = layout_response['choices'][0]['message']['content']
            st.subheader("📋 Layout Instructions:")
            st.text(layout_instructions)

        except Exception as e:
            st.error(f"Error generating layout instructions: {e}")
else:
    st.info("First generate the JSON wireframe above before running layout instructions.")