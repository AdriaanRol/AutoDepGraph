import networkx as nx

# Colormap used to map states to node colors
state_cmap = {  # 'unknown': '#7f7f7f',            # middle gray
    'unknown': '#D3D3D3',            # light gray
    'active': '#1f77b4',             # muted blue
              'good': '#2ca02c',               # cooked asparagus green
              'needs calibration': '#ff7f0e',  # safety orange
              'bad': '#d62728',                # brick red
}

# symbol map
pyqtgraph_symbol_map = {'normal': 'o',              # a circle
                        'manual_cal': 'h', }        # a hexagon

dot_type_symbol_map = {'normal': 'circle',              # a circle
                       'manual_cal': 'hexagon', }        # a hexagon


def draw_graph_svg(nxG, filename: str):
    """
    Creates an svg using graphviz.

    If the file is saved to "autodepgraph/svg_viewer/adg_graph.svg" the
    realtime svg viewer can render it.
    """
    gvG = nx.nx_agraph.to_agraph(nxG)
    gvG.draw(filename, prog='dot')
