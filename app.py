import streamlit as st
import pandas as pd
import openai
import os

# ---------- OpenAI Setup ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Or use a text_input if you're running locally

# ---------- Streamlit Interface ----------
st.title("🧷 Bowtie Diagram Generator with AI Suggestions")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file with 'Threats' and 'Consequences' sheets", type=["xlsx"])

if uploaded_file:
    # Read Excel sheets
    df_threats = pd.read_excel(uploaded_file, sheet_name="Threats")
    df_consequences = pd.read_excel(uploaded_file, sheet_name="Consequences")

    # Input central event
    central_event = st.text_input("Enter the central event (hazard)", "Hazard_Event")

    # Generate Mermaid Diagram
    mermaid_str = "```mermaid\ngraph TD\n"
    for threat in df_threats["Threat"].dropna():
        mermaid_str += f"{threat.replace(' ', '_')} --> {central_event.replace(' ', '_')}\n"
    for consequence in df_consequences["Consequence"].dropna():
        mermaid_str += f"{central_event.replace(' ', '_')} --> {consequence.replace(' ', '_')}\n"
    mermaid_str += "```"

    st.markdown("### 📌 Bowtie Diagram")
    st.markdown(mermaid_str)

    # AI Suggestions
    st.markdown("### 🤖 AI Suggestions")
    with st.spinner("Thinking..."):
        threats_text = "\n".join(df_threats["Threat"].dropna().tolist())
        consequences_text = "\n".join(df_consequences["Consequence"].dropna().tolist())

        prompt = f"""
You are a risk and safety analysis expert. Based on the following threats and consequences, suggest:
1. Potential missing threats
2. Preventive controls (left side of Bowtie)
3. Consequences not yet included
4. Recovery controls (right side of Bowtie)

### Threats:
{threats_text}

### Consequences:
{consequences_text}

Please list your suggestions clearly and concisely.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a risk assessment assistant helping build Bowtie diagrams."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        suggestions = response['choices'][0]['message']['content']
        st.markdown(suggestions)
