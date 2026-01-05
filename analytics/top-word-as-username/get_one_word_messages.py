import pandas as pd
from pathlib import Path
from typing import Dict, List


def get_top_one_word_messages(limit: int = 100) -> Dict[str, int]:
    """
    Extracts the top one-word messages from a dataset.

    Args:
        limit (int): The number of top words to return. Defaults to 100.

    Returns:
        Dict[str, int]: A dictionary where keys are the top one-word messages and values are their counts.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    source_file = base_dir / "rustlog" / "combined_dataset.parquet"

    try:
        combined_df = pd.read_parquet(source_file)
    except Exception as e:
        print(f"Error loading parquet file: {e}")
        return {}

    filtered_df = combined_df[combined_df["channel_login"] != "dima_wallhacks"]
    filtered_df = filtered_df[filtered_df["text"].str.len().between(5, 24)]
    filtered_df = filtered_df[filtered_df["text"].str.match(r"^[a-zA-Z0-9_]+$")]

    filtered_df["text"] = filtered_df["text"].str.lower()

    top_words_series = filtered_df["text"].value_counts().head(limit)
    return top_words_series.to_dict()


if __name__ == "__main__":
    top_100_words = get_top_one_word_messages(100)
    pd.set_option("display.max_rows", 100)
    pd.set_option("display.min_rows", 50)
    print(top_100_words)
