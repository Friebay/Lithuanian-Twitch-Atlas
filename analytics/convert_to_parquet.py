import pandas as pd
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = BASE_DIR / "rustlog" / "message_structured_full.json"
OUTPUT_PARQUET = BASE_DIR / "rustlog" / "message_structured_full.parquet"


def convert_jsonl_to_parquet(source_path: Path, output_path: Path, chunk_size: int = 200_000) -> None:
    """
    Converts a large JSONL file to Parquet format using chunked processing.

    Args:
        source_path: Path to the source JSONL file.
        output_path: Path to save the Parquet file.
        chunk_size: Number of lines per chunk.
    """
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return

    print(f"Converting {source_path.name} to Parquet")
    
    writer = None
    total_rows = 0

    try:
        with pd.read_json(source_path, lines=True, chunksize=chunk_size, encoding='utf-8') as reader:
            for i, chunk in enumerate(reader):
                for col in chunk.columns:
                    if chunk[col].dtype == 'object':
                        chunk[col] = chunk[col].apply(lambda x: str(x) if x is not None else None)

                table = pa.Table.from_pandas(chunk)
                
                if writer is None:
                    writer = pq.ParquetWriter(output_path, table.schema, compression='snappy')
                
                writer.write_table(table)
                total_rows += len(chunk)
                print(f"Processed chunk {i+1} ({total_rows} rows total)", end='\r')

        if writer:
            writer.close()
        
        print(f"\nSuccessfully converted {total_rows} rows to {output_path.name}")
        print(f"Original size: {source_path.stat().st_size / (1024**2):.2f} MB")
        print(f"Parquet size: {output_path.stat().st_size / (1024**2):.2f} MB")

    except Exception as e:
        print(f"\nError during conversion at chunk {i+1}:")


if __name__ == "__main__":
    convert_jsonl_to_parquet(SOURCE_FILE, OUTPUT_PARQUET)
