"""
BijliGuard AI - Graphify Knowledge & Grid Topology Engine
Maps structural electrical relationships from NEPRA down to 11kV Feeders, Transformers, and Consumers.
Uses NetworkX and PyVis for responsive, interactive graph visualization.
"""

import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components


def generate_disco_topology_graph(selected_disco: str = "IESCO") -> str:
    """
    Builds an interactive knowledge graph showing DISCO sub-stations, feeders,
    overloaded public transformers, diverted political compounds, and reported hazards.
    """
    G = nx.Graph()

    # Core Nodes Configuration: (ID, Label, Color, Size, Shape, Group/Title)
    nodes = [
        # Regulatory Apex
        ("NEPRA_HQ", "NEPRA Apex Standards\n(Tariff & Grid Code)", "#00F5A0", 35, "dot", "Regulatory Oversight"),

        # DISCO Grid Station
        (f"GRID_{selected_disco}", f"{selected_disco} 132kV Main Grid Station\n(Bijli Ghar)", "#38BDF8", 30, "dot", "Grid Station"),

        # 11kV Feeders
        ("FDR_KAKUL", "11kV Rural Feeder-03\n(Mandian)", "#F5A623", 22, "dot", "Feeder"),
        ("FDR_CIVIL", "11kV Civil Lines Feeder\n(Urban)", "#F5A623", 22, "dot", "Feeder"),

        # Transformers Under Rural Feeder
        ("TR_VILLAGE", "25 kVA Village Mohallah Transformer\n(STATUS: 184% Overloaded)", "#FF3B56", 26, "dot", "Overloaded Asset"),
        ("TR_POLITICAL", "200 kVA VIP Dera Compound\n(STATUS: Diverted Political)", "#FFB703", 26, "star", "Diverted Asset"),

        # Transformers Under Urban Feeder
        ("TR_BAZAAR", "100 kVA Main Bazaar Transformer\n(STATUS: Balanced 72%)", "#00F5A0", 20, "dot", "Balanced Asset"),

        # Field Hazard Nodes
        ("HAZ_POLE", "HAZARD: Snapped 11kV Pole\n(Kakul Road)", "#FF3B56", 18, "triangle", "Critical Hazard"),

        # Consumer Clusters
        ("VILLAGE_HOMES", "184 Rural Households\n(Low Voltage / Burnout Risk)", "#E2E8F0", 16, "square", "Citizens"),
        ("VIP_DERA", "2 Farmhouse Air Conditioners\n(Sequestered State Capacity)", "#FFD2D6", 16, "square", "VIP Compound"),
        ("BAZAAR_SHOPS", "92 Commercial Shops\n(Tariff Verified)", "#E2E8F0", 14, "square", "Shops")
    ]

    for node_id, label, color, size, shape, title in nodes:
        G.add_node(node_id, label=label, color=color, size=size, shape=shape, title=title)

    # Topology Edges (Relationships & Capacities)
    edges = [
        ("NEPRA_HQ", f"GRID_{selected_disco}", "Statutory Oversight"),
        (f"GRID_{selected_disco}", "FDR_KAKUL", "11kV High-Tension Transmission"),
        (f"GRID_{selected_disco}", "FDR_CIVIL", "11kV High-Tension Transmission"),

        # Feeders to Transformers
        ("FDR_KAKUL", "TR_VILLAGE", "Overburdened Stepped Down (415V)"),
        ("FDR_KAKUL", "TR_POLITICAL", "Illicit Diverted Feed (415V)"),
        ("FDR_KAKUL", "HAZ_POLE", "Direct Structural Hazard on Line"),
        ("FDR_CIVIL", "TR_BAZAAR", "Standard LT Distribution"),

        # Transformers to Consumers
        ("TR_VILLAGE", "VILLAGE_HOMES", "Severe Voltage Drop (184 Families)"),
        ("TR_POLITICAL", "VIP_DERA", "200 kVA Exclusively Diverted"),
        ("TR_BAZAAR", "BAZAAR_SHOPS", "Stable Load Delivery")
    ]

    for source, target, label in edges:
        G.add_edge(source, target, label=label, color="rgba(255, 255, 255, 0.25)")

    # Render with PyVis
    net = Network(
        height="520px",
        width="100%",
        bgcolor="#031410",
        font_color="#FFFFFF",
        cdn_resources="in_line",
    )
    net.from_nx(G)

    # Physical force-directed layout configuration
    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -60,
          "centralGravity": 0.015,
          "springLength": 110,
          "springConstant": 0.08
        },
        "maxVelocity": 40,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 120}
      },
      "edges": {
        "smooth": {
          "type": "continuous"
        },
        "font": {
          "size": 11,
          "color": "#8B9D98"
        }
      },
      "nodes": {
        "font": {
          "size": 13,
          "face": "Plus Jakarta Sans"
        }
      }
    }
    """)

    html_string = net.generate_html()
    return html_string


def generate_project_architecture_graph() -> str:
    """Build an interactive map of project modules and their runtime dependencies."""
    graph = nx.DiGraph()
    nodes = [
        ("APP", "Streamlit UI\nsrc/app.py", "#00F5A0", "box", "Application entry point"),
        ("EXTRACTOR", "Multimodal extraction\nsrc/extractor.py", "#38BDF8", "box", "Bills, meters, and hazards"),
        ("TARIFF", "Tariff rules\nsrc/tariff_engine.py", "#38BDF8", "box", "Slabs, billing-cycle audit, and meter deltas"),
        ("DISPUTE", "Dispute & Urdu audio\nsrc/dispute_generator.py", "#38BDF8", "box", "Complaint drafting and audio synthesis"),
        ("INVENTORY", "Inventory & tickets\nsrc/inventory_engine.py", "#38BDF8", "box", "Warehouse assets and dispatch tickets"),
        ("GRAPH", "Graphify visualization\nsrc/graph_engine.py", "#38BDF8", "box", "Interactive architecture and grid graphs"),
        ("STREAMLIT", "Streamlit", "#A78BFA", "ellipse", "Web application framework"),
        ("PANDAS", "Pandas", "#A78BFA", "ellipse", "Inventory tables and analytics"),
        ("PILLOW", "Pillow", "#A78BFA", "ellipse", "Image inputs"),
        ("PYDANTIC", "Pydantic", "#A78BFA", "ellipse", "Validated extraction models"),
        ("DOTENV", "python-dotenv", "#A78BFA", "ellipse", "Local environment configuration"),
        ("GEMINI_SDK", "google-generativeai", "#A78BFA", "ellipse", "Multimodal model client"),
        ("GTTS", "gTTS", "#A78BFA", "ellipse", "Urdu speech synthesis"),
        ("NETWORKX", "NetworkX", "#A78BFA", "ellipse", "Graph topology model"),
        ("PYVIS", "PyVis", "#A78BFA", "ellipse", "Interactive graph rendering"),
        ("GEMINI_API", "Gemini API", "#FFB703", "star", "External vision inference service"),
        ("TTS_API", "Google TTS service", "#FFB703", "star", "External speech synthesis service"),
    ]
    for node_id, label, color, shape, title in nodes:
        graph.add_node(
            node_id,
            label=label,
            color=color,
            shape=shape,
            size=24 if shape == "box" else 18,
            title=title,
        )

    edges = [
        ("APP", "STREAMLIT", "renders UI"),
        ("APP", "EXTRACTOR", "bill / meter / hazard"),
        ("APP", "TARIFF", "tariff audit"),
        ("APP", "DISPUTE", "complaints / Urdu audio"),
        ("APP", "INVENTORY", "assets / dispatch"),
        ("APP", "GRAPH", "Graphify views"),
        ("EXTRACTOR", "GEMINI_SDK", "model client"),
        ("EXTRACTOR", "PILLOW", "image handling"),
        ("EXTRACTOR", "PYDANTIC", "data validation"),
        ("EXTRACTOR", "DOTENV", "API configuration"),
        ("GEMINI_SDK", "GEMINI_API", "vision requests"),
        ("DISPUTE", "GTTS", "speech generation"),
        ("GTTS", "TTS_API", "audio requests"),
        ("INVENTORY", "PANDAS", "inventory tables"),
        ("GRAPH", "NETWORKX", "graph data"),
        ("GRAPH", "PYVIS", "interactive rendering"),
        ("GRAPH", "STREAMLIT", "embedded view"),
    ]
    for source, target, label in edges:
        graph.add_edge(
            source,
            target,
            label=label,
            color="rgba(148, 163, 184, 0.55)",
            arrows="to",
        )

    net = Network(
        height="620px",
        width="100%",
        bgcolor="#031410",
        font_color="#FFFFFF",
        directed=True,
        cdn_resources="in_line",
    )
    net.from_nx(graph)
    net.set_options("""
    {
      "layout": {"improvedLayout": true},
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "centralGravity": 0.02,
          "springLength": 130,
          "springConstant": 0.08
        },
        "maxVelocity": 35,
        "solver": "forceAtlas2Based",
        "stabilization": {"iterations": 180}
      },
      "edges": {
        "smooth": {"type": "dynamic"},
        "font": {"size": 10, "color": "#CBD5E1", "strokeWidth": 0},
        "arrows": {"to": {"enabled": true, "scaleFactor": 0.7}}
      },
      "nodes": {
        "font": {"size": 14, "face": "Arial", "multi": true},
        "borderWidth": 1
      },
      "interaction": {"hover": true, "navigationButtons": true, "keyboard": true}
    }
    """)
    return net.generate_html()


def render_graph_card(selected_disco: str):
    """Embeds the interactive network graph inside Streamlit."""
    html_graph = generate_disco_topology_graph(selected_disco)
    components.html(html_graph, height=540, scrolling=False)


def render_project_architecture_card():
    """Embed the interactive project architecture graph inside Streamlit."""
    html_graph = generate_project_architecture_graph()
    components.html(html_graph, height=640, scrolling=False)