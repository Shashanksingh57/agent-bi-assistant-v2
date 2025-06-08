import streamlit as st
import requests
import json

st.set_page_config(page_title="Dashboard Assembly AI", layout="centered")
st.title("🧠 Dashboard Assembly AI Assistant")

st.markdown("Paste your structured JSON input to get step-by-step dashboard build instructions:")

user_input = st.text_area("Dashboard JSON Input", height=300)

if st.button("✨ Generate Instructions"):
    if user_input:
        try:
            payload = json.loads(user_input)
            response = requests.post("http://127.0.0.1:8000/api/v1/generate-instructions", json=payload)

            if response.status_code == 200:
                result = response.json()

                st.subheader("✅ Generated Dashboard Instructions:")

                # Case 1: API returns a list of instruction strings
                if isinstance(result, list):
                    for step in result:
                        st.write(f"- {step}")

                # Case 2: API returns a dict with a single 'instructions' string
                elif isinstance(result, dict):
                    instructions = result.get("instructions", "")
                    if isinstance(instructions, str):
                        steps = instructions.split("\n")
                        for step in steps:
                            if step.strip():
                                st.write(f"- {step.strip()}")
                    elif isinstance(instructions, list):
                        for step in instructions:
                            st.write(f"- {step}")
                    else:
                        st.warning("⚠️ Unexpected 'instructions' format in response.")

                else:
                    st.warning("⚠️ Unexpected response format from API.")
            else:
                st.error(f"❌ API Error: Status code {response.status_code}")

        except json.JSONDecodeError:
            st.error("❌ Invalid JSON format. Please check your input.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("⚠️ Please paste valid JSON input.")