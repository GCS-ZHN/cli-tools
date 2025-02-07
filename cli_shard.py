import pandas as pd
from pathlib import Path


def shard(input_file: Path, output_dir: Path, num_shard: int, shuffle: bool = False) -> None:
    """
    Shard the input file into smaller files based on the number of rows.
    """

    file_read = {
        '.txt': pd.read_table,
        '.tsv': pd.read_table,
        '.csv': pd.read_csv,
        '.h5': pd.read_hdf,
        '.pkl': pd.read_pickle,
        '.xlsx': pd.read_excel,
        '.xls': pd.read_excel
    }

    file_ext = input_file.suffix
    if file_ext in file_read:
        df: pd.DataFrame = file_read[file_ext](input_file)
    else:
        supported_formats = ', '.join(file_read.keys())
        raise ValueError(f"Unsupported file format. Supported formats are: {supported_formats}")
    
    if shuffle:
        df = df.sample(frac=1).reset_index(drop=True)
    
    shard_size = len(df) // num_shard
    assert shard_size > 0, "Number of shards is too large for the input file."
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(num_shard):
        start = i * shard_size
        end = (i + 1) * shard_size
        if i == num_shard - 1:
            end = len(df)
        shard_df = df.iloc[start:end]
        shard_df.to_csv(output_dir / f"shard_{i}.csv", index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Shard the input file into smaller files.")
    parser.add_argument(
        "--input_file", '-i', type=Path, required=True,
        help="Path to the input file (txt, tsv, csv, h5, pkl, xlsx, xls)."
    )
    parser.add_argument(
        "--output_dir", '-o', type=Path, required=True,
        help="Path to the output directory."
    )
    parser.add_argument(
        "--num_shard", '-n', type=int, required=True,
        help="Number of shards to split the input file into."
    )
    parser.add_argument(
        "--shuffle", action="store_true",
        help="Shuffle the input file before sharding."
    )

    args = parser.parse_args()
    shard(args.input_file, args.output_dir, args.num_shard, args.shuffle)
