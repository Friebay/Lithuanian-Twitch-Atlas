import pandas as pd
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = BASE_DIR / "rustlog" / "message_structured_full.json"
OUTPUT_CSV = BASE_DIR / "analytics" /  "channel_message_counts.csv"


def count_messages_by_channel(source_path: Path) -> pd.Series:
    """
    Counts messages per channel from a JSONL file, processing in chunks.
    
    Args:
        source_path: Path to the source JSONL file.

    Returns:
        pd.Series: Series with channel_login as index and message count as values, sorted descending.
    """
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return pd.Series(dtype=int)

    print(f"Reading and counting messages from {source_path.name}...")
    
    total_counts = pd.Series(dtype=int)
    chunk_size = 100_000

    try:
        with pd.read_json(source_path, lines=True, chunksize=chunk_size, encoding='utf-8') as reader:
            for i, chunk in enumerate(reader):
                if 'channel_login' in chunk.columns:
                    counts = chunk['channel_login'].value_counts()
                    # Add current chunk counts to running total
                    total_counts = total_counts.add(counts, fill_value=0)
                
                print(f"Processed chunk {i+1}...", end='\r')
        
        print("\nFinished processing all chunks.")
            
    except ValueError as e:
        print(f"\nError reading JSON file (possible formatting issue): {e}")
        return pd.Series(dtype=int)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return pd.Series(dtype=int)

    if total_counts.empty:
        print("No messages found.")
        return pd.Series(dtype=int)

    # Clean up and sort
    return total_counts.sort_values(ascending=False).astype(int)


def main():
    counts = count_messages_by_channel(SOURCE_FILE)
    
    if counts.empty:
        print("No data to analyze.")
        return

    print("\nTop 10 Channels by Message Count:")
    print(counts.head(10))

    try:
        counts.to_csv(OUTPUT_CSV, header=['message_count'], index_label='channel_login')
        print(f"\nSaved full results to {OUTPUT_CSV.name}")
    except Exception as e:
        print(f"Failed to save results to CSV: {e}")


if __name__ == "__main__":
    main()