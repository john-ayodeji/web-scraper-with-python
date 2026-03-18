import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx


def write_graph_report(page_data, filename="report_graph.png", max_external_nodes=60):
    graph = nx.DiGraph()

    crawled_pages = set(page_data.keys())
    external_nodes_added = 0

    for page in page_data.values():
        source = page["url"]
        graph.add_node(source, node_type="internal")

        for target in page.get("internal_links", []):
            if target in crawled_pages:
                graph.add_node(target, node_type="internal")
                graph.add_edge(source, target)

        for target in page.get("external_links", []):
            if external_nodes_added >= max_external_nodes:
                break
            graph.add_node(target, node_type="external")
            graph.add_edge(source, target)
            external_nodes_added += 1

    if graph.number_of_nodes() == 0:
        fig = plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "No graph data available", ha="center", va="center")
        plt.axis("off")
        fig.savefig(filename, dpi=180, bbox_inches="tight")
        plt.close(fig)
        return filename

    positions = nx.spring_layout(graph, seed=42, k=1.2)

    internal_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "internal"]
    external_nodes = [n for n, d in graph.nodes(data=True) if d.get("node_type") == "external"]

    fig = plt.figure(figsize=(14, 10))
    nx.draw_networkx_edges(graph, positions, alpha=0.25, arrows=True, arrowsize=10)
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=internal_nodes,
        node_color="#0B7285",
        node_size=380,
        alpha=0.95,
    )
    nx.draw_networkx_nodes(
        graph,
        positions,
        nodelist=external_nodes,
        node_color="#E67700",
        node_size=240,
        alpha=0.8,
    )

    labels = {node: node if len(node) <= 38 else f"{node[:35]}..." for node in graph.nodes}
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=7)

    plt.title("Website Link Graph", fontsize=14)
    plt.axis("off")
    fig.savefig(filename, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return filename
