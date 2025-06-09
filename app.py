import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import openai
import os

# OpenAI API Key (Streamlit secrets or manual)
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Recommended
# openai.api_key = "sk-..."  # For local testing only

st.title("📌 Bowtie Diagram Generator + GPT Suggestions")

uploaded_file = st.file_uploader("Upload Excel with 'Threats' and 'Consequences'", type=['xlsx'])

if uploaded_file:
    df_threats = pd.read_excel(uploaded_file, sheet_name='Threats')
    df_cons = pd.read_excel(uploaded_file, sheet_name='Consequences')

    hazard = st.text_input("Enter Central Hazard/Event", "Hazard_Event")

    # Create graph
    G = nx.DiGraph()

    # Add edges from threats to hazard
    for threat in df_threats["Threat"].dropna():
        G.add_edge(threat, hazard)

    # Add edges from hazard to consequences
    for cons in df_cons["Consequence"].dropna():
        G.add_edge(hazard, cons)

    # Plot
    st.subheader("📊 Bowtie Graph")
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, k=0.8)
    nx.draw(G, pos, with_labels=True, arrows=True, node_size=2000, node_color='lightblue', font_size=10, ax=ax)
    st.pyplot(fig)

    # GPT Analysis
    with st.expander("🤖 AI Suggestions from GPT-4"):
        with st.spinner("Generating suggestions..."):
            prompt = f"""
You are a safety expert. Based on these Bowtie diagram components, suggest:
- Missing threats
- Missing consequences
- Preventive and recovery controls

Threats:
{chr(10).join(df_threats['Threat'].dropna())}

Consequences:
{chr(10).join(df_cons['Consequence'].dropna())}
"""
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Bowtie diagram assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            st.markdown(response.choices[0].message.content)
