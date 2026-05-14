import argparse
from pathlib import Path

import pandas as pd

try:
    # Works when run from repository root.
    from src.task_planner.utils import boundary_raw2mat_single_rc
except ImportError:
    # Works when imported as an installed package.
    from task_planner.utils import boundary_raw2mat_single_rc


def export_single_rc_boundaries(
    input_dir: Path,
    output_dir: Path,
    prefix: str,
    n_cols_parts: int,
) -> int:
    if n_cols_parts < 1:
        raise ValueError("n_cols_parts must be >= 1")

    file_names = sorted(
        f.name
        for f in input_dir.iterdir()
        if f.is_file() and f.name.startswith(prefix) and f.suffix == ".csv"
    )

    if not file_names:
        print(f"No matching CSV files found in {input_dir} with prefix '{prefix}'.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)

    line_count = 0
    for file_name in file_names:
        boundary_file_path = input_dir / file_name
        boundary_arr = boundary_raw2mat_single_rc(str(boundary_file_path))

        n_rows, n_cols, _, _ = boundary_arr.shape
        n_cols_per_part = n_cols // n_cols_parts
        n_cols_remainder = n_cols % n_cols_parts

        n_cols_splits = []
        start_col = 0
        for part in range(n_cols_parts):
            end_col = start_col + n_cols_per_part + (1 if part < n_cols_remainder else 0)
            n_cols_splits.append(range(start_col, end_col))
            start_col = end_col

        for part_idx, n_cols_in_part in enumerate(n_cols_splits, start=1):
            df_data_part = []
            for i in range(n_rows):
                for j in n_cols_in_part:
                    for k in [0, 1, 3, 2]:
                        lat, lon = boundary_arr[i, j, k]
                        df_data_part.append(
                            {
                                "LATITUDE": lat,
                                "LONGITUDE": lon,
                                "LABEL": f"R{i + 1}C{j + 1}_{k}",
                            }
                        )
                        line_count += 1

                    df_data_part.append(
                        {
                            "LATITUDE": None,
                            "LONGITUDE": None,
                            "LABEL": "",
                        }
                    )

            df_part = pd.DataFrame(df_data_part)
            part_name = f"_part{part_idx}" if n_cols_parts > 1 else ""
            out_filename = f"{Path(file_name).stem}{part_name}.csv"
            out_path = output_dir / out_filename
            df_part.to_csv(out_path, index=False)
            print(f"Wrote {out_path}")

    print(f"Total coordinate rows written: {line_count}")
    return line_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert single-RC plot boundary CSV files into Global Mapper boundary point files."
    )
    parser.add_argument(
        "--input-dir",
        default="exp_plot_boundary",
        help="Directory containing source boundary CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        default="jining_single_rc_plot_boundaries",
        help="Directory where converted CSV files will be written.",
    )
    parser.add_argument(
        "--prefix",
        default="jining",
        help="Only process files whose names start with this prefix.",
    )
    parser.add_argument(
        "--n-cols-parts",
        type=int,
        default=1,
        help="Split columns into this many output parts per source file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return export_single_rc_boundaries(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        prefix=args.prefix,
        n_cols_parts=args.n_cols_parts,
    )


if __name__ == "__main__":
    raise SystemExit(main())
