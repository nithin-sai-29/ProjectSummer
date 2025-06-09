import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Bowtie Diagram Generator", layout="centered")
st.title("📌 Bowtie Diagram Generator + GPT Suggestions")

uploaded_file = st.file_uploader("Upload Excel with 'Threats' and 'Consequences'", type=['xlsx'])

if uploaded_file:
    try:
        df_threats = pd.read_excel(uploaded_file, sheet_name='Threats')
        df_cons = pd.read_excel(uploaded_file, sheet_name='Consequences')

        hazard_input = st.text_input("Enter Central Hazard/Event", "Loss of Containment")
        hazard = f"🔺 {hazard_input.strip()}"

        # Create directed graph
        G = nx.DiGraph()

        for threat in df_threats["Threat"].dropna():
            G.add_edge(f"⚠️ {threat.strip()}", hazard)

        for cons in df_cons["Consequence"].dropna():
            G.add_edge(hazard, f"💥 {cons.strip()}")

        # Draw the graph
        st.subheader("📊 Bowtie Diagram")
        fig, ax = plt.subplots(figsize=(12, 6))
        pos = nx.spring_layout(G, k=0.9, seed=42)
        nx.draw(G, pos, with_labels=True, arrows=True,
                node_size=2500, node_color='lightblue', font_size=9, font_weight='bold', ax=ax)
        st.pyplot(fig)

        # GPT Suggestions
        with st.expander("🤖 GPT-3.5 Suggestions"):
            with st.spinner("Calling GPT-3.5-turbo for suggestions..."):
                prompt = f"""
You are a risk assessment expert. Based on the threats and consequences in this Bowtie diagram, suggest:
1. Additional threats
2. Preventive controls (left side)
3. Additional consequences
4. Recovery controls (right side)

### Threats:
{chr(10).join(df_threats['Threat'].dropna())}

### Consequences:
{chr(10).join(df_cons['Consequence'].dropna())}
"""

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a Bowtie diagram assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.6
                    )
                    output = response.choices[0].message.content
                    st.markdown(output)

                except Exception as gpt_error:
                    st.error("❌ OpenAI API Error")
                    st.code(str(gpt_error))

    except Exception as e:
        st.error("⚠️ Failed to read Excel file. Make sure it has sheets 'Threats' and 'Consequences'.")
        st.code(str(e))

else:
    st.info("📂 Please upload an Excel file to begin.")
