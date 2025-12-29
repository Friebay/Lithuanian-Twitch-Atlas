import pandas as pd
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_PARQUET = BASE_DIR / "rustlog" / "message_structured_full.parquet"
OUTPUT_CSV = BASE_DIR / "analytics" / "channel_message_counts.csv"


def count_messages_by_channel(source_path: Path) -> pd.Series:
    """
    Counts messages per channel from a data file. Supports Parquet and JSONL.

    Args:
        source_path: Path to the source file (.parquet or .json).

    Returns:
        pd.Series: Series with channel_login as index and message count as values, sorted descending.
    """
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return pd.Series(dtype=int)

    print(f"Reading and counting messages from {source_path.name}...")

    try:
        df = pd.read_parquet(source_path, columns=['channel_login'])
        total_counts = df['channel_login'].value_counts()

    except Exception as e:
        print(f"\nError counting messages: {e}")
        return pd.Series(dtype=int)

    if total_counts.empty:
        print("No messages found.")
        return pd.Series(dtype=int)

    return total_counts.sort_values(ascending=False).astype(int)


def get_top_messages_for_channel(
    source_path: Path, 
    channel_name: str, 
    top_n: int = 100
) -> pd.Series:
    """
    Extracts the top N most frequent messages for a specific channel.

    Args:
        source_path: Path to the source file (.parquet or .json).
        channel_name: The channel login to filter by.
        top_n: The number of top messages to return. Defaults to 100.

    Returns:
        pd.Series: Series with message text as index and frequency as values.
    """
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return pd.Series(dtype=int)

    print(f"Reading messages for channel '{channel_name}' from {source_path.name}...")

    try:
        df = pd.read_parquet(source_path, columns=['channel_login', 'text'])
        channel_messages = df[df['channel_login'] == channel_name]['text']
        all_message_counts = channel_messages.value_counts()

    except Exception as e:
        print(f"\nError processing top messages for {channel_name}: {e}")
        return pd.Series(dtype=int)

    if all_message_counts.empty:
        print(f"No messages found for channel {channel_name}.")
        return pd.Series(dtype=int)

    return all_message_counts.sort_values(ascending=False).head(top_n).astype(int)


def get_top_words_for_channel(
    source_path: Path, 
    channel_name: str, 
    top_n: int = 100
) -> pd.Series:
    """
    Extracts the top N most frequent words for a specific channel.

    Args:
        source_path: Path to the source file (.parquet or .json).
        channel_name: The channel login to filter by.
        top_n: The number of top words to return. Defaults to 100.

    Returns:
        pd.Series: Series with words as index and frequency as values.
    """
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return pd.Series(dtype=int)

    print(f"Reading and tokenizing words for channel '{channel_name}' from {source_path.name}...")

    try:
        df = pd.read_parquet(source_path, columns=['channel_login', 'text'])
        channel_messages = df[df['channel_login'] == channel_name]['text']

        if channel_messages.empty:
            return pd.Series(dtype=int)

        # Tokenization: convert to lowercase, split by whitespace, and explode into rows
        words = channel_messages.str.lower().str.split().explode()
        
        # Remove empty strings
        word_counts = words[words.str.len() > 0].value_counts()

    except Exception as e:
        print(f"\nError processing top words for {channel_name}: {e}")
        return pd.Series(dtype=int)

    if word_counts.empty:
        print(f"No words found for channel {channel_name}.")
        return pd.Series(dtype=int)

    return word_counts.sort_values(ascending=False).head(top_n).astype(int)


def main():
    source_file = SOURCE_PARQUET
    '''
    # 1. Get overall message counts per channel
    counts = count_messages_by_channel(source_file)
    
    if not counts.empty:
        print("\nTop 10 Channels by Message Count:")
        print(counts.head(10))

        try:
            counts.to_csv(OUTPUT_CSV, header=['message_count'], index_label='channel_login')
            print(f"\nSaved full results to {OUTPUT_CSV.name}")
        except Exception as e:
            print(f"Failed to save results to CSV: {e}")
    '''

    target_channel = "elthebird"
    top_messages = get_top_messages_for_channel(source_file, target_channel, top_n = 250)

    if not top_messages.empty:
        output_messages_csv = BASE_DIR / "analytics" / f"{target_channel}_top_messages.csv"
        try:
            top_messages.to_csv(output_messages_csv, header=['frequency'], index_label='message_text')
            print(f"Saved top messages for '{target_channel}' to {output_messages_csv.name}")
        except Exception as e:
            print(f"Failed to save top messages for '{target_channel}': {e}")

    top_words = get_top_words_for_channel(source_file, target_channel, top_n = 250)

    if not top_words.empty:
        output_words_csv = BASE_DIR / "analytics" / f"{target_channel}_top_words.csv"
        try:
            top_words.to_csv(output_words_csv, header=['frequency'], index_label='word')
            print(f"Saved top words for '{target_channel}' to {output_words_csv.name}")
        except Exception as e:
            print(f"Failed to save top words for '{target_channel}': {e}")
if __name__ == "__main__":
    main()