from IPython.display import Image, display
import os

def display_graph(graph):
    graph_image_path = os.path.join("output", "graph_visualization.png")
    try:
        graph_image = graph.get_graph(xray=True).draw_mermaid_png()
        with open(graph_image_path, "wb") as f:
            f.write(graph_image)
        display(Image(graph_image))  #Display the graph image in Jupiter Notebook
        print(f"Graph visualized and saved as PNG at '{graph_image_path}'")
    except Exception as e:
        print(f"Failed to create or display graph: {e}")
