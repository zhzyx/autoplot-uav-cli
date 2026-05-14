import csv
import re
import argparse

def parse_polygon(wkt: str):
    match = re.search(r"POLYGON\s*\(\((.+)\)\)", wkt, flags=re.IGNORECASE)
    if not match:
        return []
    coords = match.group(1).split(",")
    points = []
    for c in coords:
        parts = c.strip().split()
        if len(parts) >= 2:
            lon, lat = parts[0], parts[1]    
            points.append((lon, lat))
    return points


def main(input_path: str, output_path: str, empty_line_separator: bool = False):
    with open(input_path, newline="") as fin, open(output_path, "w", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout)
        writer.writerow(["LABEL", "LATITUDE", "LONGITUDE"])
        for row in reader:
            label = row.get("LABEL", "").strip()
            label = label.split(";")[0].strip()  
            label = label.rsplit("_", 1)[0]  
            geometry = row.get("GEOMETRY", "")
            for lon, lat in parse_polygon(geometry):
                writer.writerow([label, lat, lon])
            if empty_line_separator:
                writer.writerow([None, None, None])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert WKT polygons CSV to points CSV.")
    parser.add_argument("--empty-line-separator", "-e", help="empty line separator between polygons", action="store_true")
    parser.add_argument("input", help="input CSV path")
    parser.add_argument("output", help="output CSV path")
    args = parser.parse_args()
    main(args.input, args.output, args.empty_line_separator)

