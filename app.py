import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 🎯 Function to generate Bowtie Diagram with custom styling
def generate_bowtie_diagram_styled(threats, consequences, top_event_text,
                                    threat_color="deepskyblue", consequence_color="orangered",
                                    top_event_color="orange", node_shape="s"):
    top_event = top_event_text
    G = nx.DiGraph()

    for threat in threats:
        G.add_edge(threat, top_event)
    for consequence in consequences:
        G.add_edge(top_event, consequence)

    pos = {}
    for i, threat in enumerate(threats):
        pos[threat] = (-2, -i)
    pos[top_event] = (0, -len(threats) / 2)
    for i, consequence in enumerate(consequences):
        pos[consequence] = (2, -i - 3)

    fig, ax = plt.subplots(figsize=(14, 8))
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', arrows=True)

    node_styles = {}
    for node in G.nodes():
        if node == top_event:
            node_styles[node] = top_event_color
        elif node in threats:
            node_styles[node] = threat_color
        else:
            node_styles[node] = consequence_color

    for color in set(node_styles.values()):
        nodes = [n for n in node_styles if node_styles[n] == color]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=color,
                               node_shape=node_shape, node_size=3000, ax=ax)

    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight="bold")
    plt.axis("off")
    plt.tight_layout()
    return fig

# 📌 Streamlit Interface
st.set_page_config(page_title="Bowtie Diagram", layout="wide")
st.title("📌 Customizable Bowtie Diagram Generator")

uploaded_file = st.file_uploader("Upload Excel with 'Threats' and 'Consequences' sheets", type=['xlsx'])

if uploaded_file:
    try:
        df_threats = pd.read_excel(uploaded_file, sheet_name='Threats')
        df_cons = pd.read_excel(uploaded_file, sheet_name='Consequences')

        threats = df_threats["Threat"].dropna().tolist()
        consequences = df_cons["Consequence"].dropna().tolist()

        st.sidebar.header("🎨 Styling Options")
        threat_color = st.sidebar.color_picker("Threat Node Color", "#00BFFF")
        consequence_color = st.sidebar.color_picker("Consequence Node Color", "#FF4500")
        top_event_color = st.sidebar.color_picker("Top Event Color", "#FFA500")

        shape_option = st.sidebar.selectbox("Node Shape", {
            "Square (s)": "s",
            "Circle (o)": "o",
            "Diamond (D)": "D",
            "Triangle Up (^)": "^",
            "Triangle Down (v)": "v"
        })

        top_event = st.text_input("Enter Top Event", "Loss of Containment\nwith hydrocarbon\nspilled to the bund")

        st.subheader("📊 Bowtie Diagram")
        fig = generate_bowtie_diagram_styled(
            threats,
            consequences,
            top_event_text=top_event,
            threat_color=threat_color,
            consequence_color=consequence_color,
