import pandas as pd
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOURCE_FILE = BASE_DIR / "analytics" / "six-seven" / "six_seven.json"
MIN_MESSAGES = 5
TOP_N = 3

def load_data(file_path: Path) -> pd.DataFrame:
    """Loads message data from a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        A pandas DataFrame.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")
    
    try:
        return pd.read_json(file_path)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return pd.DataFrame()

def analyze_top_users(df: pd.DataFrame, min_messages: int, top_n: int) -> None:
    """Finds and prints the top users who wrote the target message the most in each community.

    Args:
        df: DataFrame containing 'channel_login' and 'display_name'.
        min_messages: Minimum number of target messages for a community to be analyzed.
        top_n: Number of top users to display for each community.
    """
    if df.empty:
        print("No data to analyze.")
        return

    # Count total messages per channel for filtering
    channel_counts = df['channel_login'].value_counts()
    eligible_channels = channel_counts[channel_counts > min_messages].index.tolist()

    if not eligible_channels:
        print(f"No communities found with more than {min_messages} target messages.")
        return

    # Filter for eligible channels
    filtered_df = df[df['channel_login'].isin(eligible_channels)]

    print(f"Found {len(eligible_channels)} communities with more than {min_messages} messages")

    # Group by channel and user, then count
    user_counts = filtered_df.groupby(['channel_login', 'display_name']).size().reset_index(name='message_count')

    # Sort and get top N for each channel
    top_users = (
        user_counts.sort_values(['channel_login', 'message_count'], ascending=[True, False])
        .groupby('channel_login')
        .head(top_n)
    )

    # Print results to console
    current_channel = None
    for _, row in top_users.iterrows():
        channel = row['channel_login']
        if channel != current_channel:
            print(f"\nCommunity: {channel} (total messages: {channel_counts[channel]})")
            current_channel = channel
        
        print(f"{row['display_name']}: {row['message_count']} messages")

def main() -> None:
    try:
        df = load_data(SOURCE_FILE)
        analyze_top_users(df, MIN_MESSAGES, TOP_N)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
