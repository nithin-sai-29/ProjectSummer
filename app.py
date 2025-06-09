import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI

# Load OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Bowtie Diagram Generator", layout="centered")
st.title("📌 Bowtie Diagram Generator + GPT Suggestions")

# Upload Excel file
uploaded_file = st.file_uploader("Upload Excel with 'Threats' and 'Consequences'", type=['xlsx'])

if uploaded_file:
    try:
        # Read Excel sheets
        df_threats = pd.read_excel(uploaded_file, sheet_name='Threats')
        df_cons = pd.read_excel(uploaded_file, sheet_name='Consequences')

        # Central hazard input
        hazard = st.text_input("Enter Central Hazard/Event", "Hazard_Event")

        # Build the diagram with networkx
        G = nx.DiGraph()

        for threat in df_threats["Threat"].dropna():
            G.add_edge(threat, hazard)

        for cons in df_cons["Consequence"].dropna():
            G.add_edge(hazard, cons)

        # Draw the graph
        st.subheader("📊 Bowtie Diagram")
        fig, ax = plt.subplots(figsize=(10, 6))
        pos = nx.spring_layout(G, k=0.9)
        nx.draw(G, pos, with_labels=True, arrows=True,
                node_size=2000, node_color='skyblue', font_size=10, ax=ax)
        st.pyplot(fig)

        # GPT Suggestions
        with st.expander("🤖 GPT Suggestions"):
            with st.spinner("Thinking..."):
                prompt = f"""
You are a risk assessment expert. Based on the threats and consequences in this Bowtie diagram, suggest:
1. Any missing threats
2. Preventive barriers/controls (left side)
3. Additional consequences
4. Recovery controls (right side)

### Threats:
{chr(10).join(df_threats['Threat'].dropna())}

### Consequences:
{chr(10).join(df_cons['Consequence'].dropna())}
"""

                try:
                    response = client.chat.completions.create(
                        model="gpt-4",  # You can change to "gpt-3.5-turbo" if needed
                        messages=[
                            {"role": "system", "content": "You are a Bowtie diagram assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.6
                    )
                    suggestions = response.choices[0].message.content
                    st.markdown(suggestions)

                except Exception as e:
                    st.error("❌ OpenAI API Error:")
                    st.code(str(e))

    except Exception as e:
        st.error("⚠️ Error reading Excel file. Please ensure it has 'Threats' and 'Consequences' sheets.")
        st.code(str(e))

else:
    st.info("📂 Please upload an Excel file to begin.")
