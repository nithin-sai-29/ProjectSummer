import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Bowtie Diagram Generator", layout="wide")
st.title("📌 Bowtie Diagram Generator + GPT Suggestions")

uploaded_file = st.file_uploader("📂 Upload Excel with 'Threats' and 'Consequences' sheets", type=["xlsx"])

if uploaded_file:
    try:
        # List available sheet names for debugging
        xls = pd.ExcelFile(uploaded_file)
        st.sidebar.info(f"🧾 Sheets in file: {xls.sheet_names}")

        # Read expected sheets
        df_threats = pd.read_excel(xls, sheet_name='Threats')
        df_cons = pd.read_excel(xls, sheet_name='Consequences')

        # Dropdowns to confirm columns
        threat_col = st.sidebar.selectbox("Select Threat Column", df_threats.columns)
        consequence_col = st.sidebar.selectbox("Select Consequence Column", df_cons.columns)

        threats = df_threats[threat_col].dropna().astype(str).tolist()
        consequences = df_cons[consequence_col].dropna().astype(str).tolist()

        # Central event input
        hazard_input = st.text_input("Enter Central Event (Top Event)", "Loss of Containment")
        hazard = f"[TOP] {hazard_input.strip()}"

        # Styling Options
        st.sidebar.header("🎨 Node Styling")
        threat_color = st.sidebar.color_picker("Threat Color", "#00BFFF")
        consequence_color = st.sidebar.color_picker("Consequence Color", "#FF6347")
        top_color = st.sidebar.color_picker("Top Event Color", "#FFA500")
        shape_option = st.sidebar.selectbox("Node Shape", {
            "Square (s)": "s",
            "Circle (o)": "o",
            "Diamond (D)": "D",
            "Triangle Up (^)": "^",
            "Triangle Down (v)": "v"
        })

        # Build graph
        G = nx.DiGraph()
        labels = {}

        for t in threats:
            node = f"[THREAT] {t.strip()}"
            G.add_edge(node, hazard)
            labels[node] = node

        for c in consequences:
            node = f"[CONSEQ] {c.strip()}"
            G.add_edge(hazard, node)
            labels[node] = node

        labels[hazard] = hazard

        # Layout
        pos = {}
        for i, t in enumerate(threats):
            pos[f"[THREAT] {t.strip()}"] = (-2, -i)

        for i, c in enumerate(consequences):
            pos[f"[CONSEQ] {c.strip()}"] = (2, -i)

        pos[hazard] = (0, -len(threats) / 2)

        # Draw diagram
        st.subheader("📊 Bowtie Diagram")
        fig, ax = plt.subplots(figsize=(14, 8))
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', arrows=True)

        # Draw nodes with colors
        def draw_nodes(node_type, color):
            nodes = [n for n in G.nodes if n.startswith(node_type)]
            nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=color,
                                   node_size=3000, node_shape=shape_option, ax=ax)

        draw_nodes("[THREAT]", threat_color)
        draw_nodes("[TOP]", top_color)
        draw_nodes("[CONSEQ]", consequence_color)

        nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight="bold", ax=ax)

        plt.axis("off")
        st.pyplot(fig)

        # GPT Section
        with st.expander("🤖 GPT Suggestions"):
            with st.spinner("Thinking..."):
                prompt = f"""
You are a risk expert. Given these threats and consequences in a Bowtie diagram, suggest:
1. Additional threats
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
                    st.markdown(response.choices[0].message.content)
                except Exception as gpt_error:
                    st.error("❌ GPT API Error")
                    st.code(str(gpt_error))

    except Exception as e:
        st.error("⚠️ Failed to process the file.")
        st.code(str(e))

else:
    st.info("Please upload an Excel file to begin.")
