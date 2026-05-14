import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd


def dms2dec(value):
    """Convert DMS text (or decimal input) to decimal degrees."""
    if value is None:
        raise ValueError("LATITUDE/LONGITUDE value cannot be None")

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    text = str(value).strip()
    if text == "":
        raise ValueError("LATITUDE/LONGITUDE value cannot be empty")

    try:
        return float(text)
    except ValueError:
        pass

    dms_str = re.sub(r"\s", "", text)
    sign = -1 if re.search(r"[swSW]", dms_str) else 1
    numbers = re.findall(r"\d+(?:\.\d+)?", dms_str)

    if not numbers:
        raise ValueError(f"Invalid DMS coordinate: {value}")

    degree = numbers[0]
    minute = numbers[1] if len(numbers) >= 2 else "0"
    second = numbers[2] if len(numbers) >= 3 else "0"

    return sign * (float(degree) + float(minute) / 60 + float(second) / 3600)


def zone_to_indices(col, row, total_col):
    # order of points for a plot:
    # 0--1
    # |  |
    # 2--3
    index = row * total_col * 4 + col * 2
    ind_p1 = index
    ind_p2 = ind_p1 + 1
    ind_p3 = index + 2 * total_col
    ind_p4 = ind_p3 + 1
    return [ind_p1, ind_p2, ind_p3, ind_p4]


def boundary_raw2mat_single_rc(csv_filepath):
    df = pd.read_csv(csv_filepath)
    df["LATITUDE"] = df["LATITUDE"].apply(dms2dec)
    df["LONGITUDE"] = df["LONGITUDE"].apply(dms2dec)

    horiz_pts = df[df["LABEL"] == "HP"].sort_index().reset_index(drop=True)
    verti_pts = df[df["LABEL"] == "VP"].sort_index().reset_index(drop=True)

    if len(verti_pts) == 0 or len(horiz_pts) == 0:
        raise ValueError("Input CSV must contain both HP and VP labels")

    horiz_list = [horiz_pts.copy()]
    for _, pt in verti_pts.iloc[1:].iterrows():
        x_diff = pt["X"] - verti_pts.iloc[0]["X"]
        y_diff = pt["Y"] - verti_pts.iloc[0]["Y"]
        lat_diff = pt["LATITUDE"] - verti_pts.iloc[0]["LATITUDE"]
        lon_diff = pt["LONGITUDE"] - verti_pts.iloc[0]["LONGITUDE"]

        new_horiz = horiz_pts.copy()
        new_horiz["X"] += x_diff
        new_horiz["Y"] += y_diff
        new_horiz["LATITUDE"] += lat_diff
        new_horiz["LONGITUDE"] += lon_diff
        horiz_list.append(new_horiz)

    pts_grid_df = pd.concat(horiz_list)

    if len(df[df["LABEL"] == "VP"]) % 2 != 0:
        raise ValueError("Number of VP points must be even")
    if len(df[df["LABEL"] == "HP"]) % 2 != 0:
        raise ValueError("Number of HP points must be even")

    n_rows = int(len(df[df["LABEL"] == "VP"]) / 2)
    n_cols = int(len(df[df["LABEL"] == "HP"]) / 2)

    points_list = []
    for r in range(n_rows):
        for c in range(n_cols):
            indices = zone_to_indices(c, r, n_cols)
            lat_lon = pts_grid_df.iloc[indices][["LATITUDE", "LONGITUDE"]].values
            points_list.append(lat_lon)

    boundary_arr = np.array(points_list).reshape(n_rows, n_cols, 4, 2)
    return boundary_arr


def export_single_rc_boundaries(input_dir: Path, output_dir: Path, prefix: str | None, n_cols_parts: int) -> int:
    if n_cols_parts < 1:
        raise ValueError("n_cols_parts must be >= 1")

    file_names = sorted(
        f.name
        for f in input_dir.iterdir()
        if f.is_file() and f.suffix == ".csv" and (prefix is None or f.name.startswith(prefix))
    )

    if not file_names:
        if prefix is None:
            print(f"No CSV files found in {input_dir}.")
        else:
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
        help="directory containing source boundary CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        help="directory where converted CSV files will be written.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="only process files whose names start with this prefix.",
    )
    parser.add_argument(
        "--n-cols-parts",
        type=int,
        default=1,
        help="split columns into this many output parts per source file.",
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
