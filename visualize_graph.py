from IPython.display import display, Image


def visualize_graph(graph_builder):
    try:
        display(Image(graph_builder.get_builder().visualize()))
    except Exception:
        print("Error: Could not visualize graph")


visualize_graph()
