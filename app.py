import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Bowtie Diagram Generator", layout="centered")
st.title("📌 Bowtie Diagram Generator + GPT Suggestions")

uploaded_file = st.file_uploader("Upload Excel with 'Threats' and 'Consequences' sheets", type=['xlsx'])

if uploaded_file:
    try:
        # Read Excel
        df_threats = pd.read_excel(uploaded_file, sheet_name='Threats')
        df_cons = pd.read_excel(uploaded_file, sheet_name='Consequences')

        # Central event input
        hazard_input = st.text_input("Enter Central Event (Top Event)", "Loss of Containment")
        hazard = f"[TOP] {hazard_input.strip()}"

        # Create graph
        G = nx.DiGraph()

        # Track all nodes and labels
        labels = {}

        # Threats
        for i, row in df_threats.iterrows():
            threat = str(row['Threat']).strip()
            threat_node = f"[THREAT] {threat}"
            G.add_edge(threat_node, hazard)
            labels[threat_node] = threat_node

        # Consequences
        for i, row in df_cons.iterrows():
            consequence = str(row['Consequence']).strip()
            cons_node = f"[CONSEQ] {consequence}"
            G.add_edge(hazard, cons_node)
            labels[cons_node] = cons_node

        labels[hazard] = hazard

        # Manual layout for bowtie shape
        pos = {}
        threats = list(df_threats['Threat'].dropna())
        consequences = list(df_cons['Consequence'].dropna())

        for idx, t in enumerate(threats):
            pos[f"[THREAT] {t.strip()}"] = (-1, idx * -1)

        for idx, c in enumerate(consequences):
            pos[f"[CONSEQ] {c.strip()}"] = (1, idx * -1)

        pos[hazard] = (0, 0)  # Center top event

                # Draw diagram
        st.subheader("📊 Bowtie Diagram")
        fig, ax = plt.subplots(figsize=(14, 7))
        nx.draw(G, pos, with_labels=True, labels=labels,
                node_size=2000, node_color="lightblue", font_size=9,
                font_weight='bold', edge_color='gray', ax=ax)
        st.pyplot(fig)

        # Save to PDF
        pdf_filename = "bowtie_diagram.pdf"
        fig.savefig(pdf_filename, format='pdf')

        # Download button
        with open(pdf_filename, "rb") as f:
            st.download_button("📥 Download as PDF", f, file_name=pdf_filename)

        


        # GPT Suggestion Section
        with st.expander("🤖 GPT Suggestions"):
            with st.spinner("Thinking..."):
                prompt = f"""
You are a risk expert. Given these threats and consequences in a Bowtie diagram, suggest:
1. Missing threats
2. Preventive controls
3. Recovery controls
4. Additional consequences

### Threats:
{chr(10).join(threats)}

### Consequences:
{chr(10).join(consequences)}
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
                    st.error("❌ GPT API Error")
                    st.code(str(gpt_error))

    except Exception as e:
        st.error("⚠️ Failed to process the file. Make sure 'Threats' and 'Consequences' sheets exist.")
        st.code(str(e))

else:
    st.info("📂 Please upload an Excel file to begin.") 
