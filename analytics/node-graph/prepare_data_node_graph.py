import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from itertools import combinations

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOURCE_FILE = BASE_DIR / "rustlog" / "message_structured_full.parquet"
OUTPUT_NODES_CSV = Path(__file__).resolve().parent / "nodes.csv"
OUTPUT_EDGES_CSV = Path(__file__).resolve().parent / "edges.csv"


def build_graph_data(source_path: Path, min_shared_users: int = 5, top_channels: int = 50):
    """
    Builds node graph data from chat logs: nodes are channels, edges are shared chatters.
    
    Args:
        source_path: Path to the source Parquet file.
        min_shared_users: Minimum shared users required to create an edge.
        top_channels: Number of top channels to include (by message count).

    Returns:
        dict: Graph data with 'nodes' and 'edges' arrays.
    """
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return {"nodes": [], "edges": []}

    print(f"Processing {source_path.name} to build graph data")
    
    try:
        df = pd.read_parquet(source_path, columns=['channel_login', 'user_login'])
        
        channel_message_counts = df['channel_login'].value_counts().to_dict()
        
        sorted_channels = sorted(channel_message_counts.items(), key=lambda x: x[1], reverse=True)
        top_channel_names = [ch for ch, _ in sorted_channels[:top_channels]]
        
        df_top = df[df['channel_login'].isin(top_channel_names)]
        
        # Group to get sets of users per channel
        channel_users = df_top.groupby('channel_login')['user_login'].apply(set).to_dict()
            
    except Exception as e:
        print(f"\nError reading Parquet file: {e}")
        return {"nodes": [], "edges": []}

    if not channel_message_counts:
        print("No data found.")
        return {"nodes": [], "edges": []}

    # Get top channels by message count
    sorted_channels = sorted(channel_message_counts.items(), key=lambda x: x[1], reverse=True)
    top_channel_names = [ch for ch, _ in sorted_channels[:top_channels]]
    
    # Create nodes
    nodes = []
    for channel in top_channel_names:
        nodes.append({
            "id": channel,
            "label": channel,
            "size": channel_message_counts[channel],
            "userCount": len(channel_users[channel])
        })

    # Create edges based on shared users
    edges = []
    edge_id = 0
    
    for ch1, ch2 in combinations(top_channel_names, 2):
        shared = channel_users[ch1] & channel_users[ch2]
        shared_count = len(shared)
        
        if shared_count >= min_shared_users:
            edges.append({
                "id": edge_id,
                "source": ch1,
                "target": ch2,
                "weight": shared_count
            })
            edge_id += 1
    
    return {
        "nodes": nodes,
        "edges": edges
    }


def export_to_gephi_csv(graph_data: dict, nodes_path: Path, edges_path: Path) -> None:
    """
    Exports graph data to Gephi-compatible CSV files.

    Args:
        graph_data: Dictionary containing 'nodes' and 'edges' lists.
        nodes_path: Path to save the nodes CSV.
        edges_path: Path to save the edges CSV.
    """
    nodes_df = pd.DataFrame(graph_data["nodes"])
    # Rename columns for Gephi: 'id' -> 'Id', 'label' -> 'Label'
    nodes_df = nodes_df.rename(columns={"id": "Id", "label": "Label"})
    nodes_df.to_csv(nodes_path, index=False)

    # Export Edges
    edges_data = []
    for edge in graph_data["edges"]:
        edges_data.append({
            "Source": edge["source"],
            "Target": edge["target"],
            "Weight": edge["weight"],
            "Type": "Undirected"
        })
    edges_df = pd.DataFrame(edges_data)
    edges_df.to_csv(edges_path, index=False)


def main():
    graph_data = build_graph_data(SOURCE_FILE, min_shared_users=10, top_channels=150)
    
    if not graph_data["nodes"]:
        print("No data to save.")
        return

    export_to_gephi_csv(graph_data, OUTPUT_NODES_CSV, OUTPUT_EDGES_CSV)
    
    print(f"\nGraph data saved to:")
    print(f"Nodes CSV: {OUTPUT_NODES_CSV}")
    print(f"Edges CSV: {OUTPUT_EDGES_CSV}")
    print(f"Nodes: {len(graph_data['nodes'])}")
    print(f"Edges: {len(graph_data['edges'])}")

if __name__ == "__main__":
    main()