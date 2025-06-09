import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI

# Set up OpenAI client (uses Streamlit secrets)
client = OpenAI(api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

st.title("📌 Bowtie Diagram Generator + GPT-4 Suggestions")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel with 'Threats' and 'Consequences'", type=['xlsx'])

if uploaded_file:
    # Read sheets
    df_threats = pd.read_excel(uploaded_file, sheet_name='Threats')
    df_cons = pd.read_excel(uploaded_file, sheet_name='Consequences')

    # Central hazard input
    hazard = st.text_input("Enter Central Hazard/Event", "Hazard_Event")

    # Create directed graph
    G = nx.DiGraph()

    for threat in df_threats["Threat"].dropna():
        G.add_edge(threat, hazard)

    for cons in df_cons["Consequence"].dropna():
        G.add_edge(hazard, cons)

    # Draw graph
    st.subheader("📊 Bowtie Diagram")
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, k=0.8)
    nx.draw(G, pos, with_labels=True, arrows=True,
            node_size=2000, node_color='lightblue', font_size=10, ax=ax)
    st.pyplot(fig)

    # AI Suggestions
    with st.expander("🤖 GPT-4 Suggestions"):
        with st.spinner("Thinking..."):
            # Prepare prompt
            prompt = f"""
You are a safety expert. Based on these Bowtie diagram components, suggest:
- Additional threats
- Missing consequences
- Preventive and recovery controls

Threats:
{chr(10).join(df_threats['Threat'].dropna())}

Consequences:
{chr(10).join(df_cons['Consequence'].dropna())}
"""

            # OpenAI GPT-4 call
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Bowtie diagram assistant helping improve risk diagrams."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )

            suggestions = response.choices[0].message.content
            st.markdown(suggestions)
