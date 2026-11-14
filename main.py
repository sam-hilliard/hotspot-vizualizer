import argparse
import json
from collections import defaultdict
import shutil
import yaml

def parse_sarif(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sarif_data = json.load(f)

    file_hotspots = defaultdict(int)

    for run in sarif_data.get("runs", []):
        for result in run.get("results", []):

            locations = result.get("locations", [])

            for location in locations:
                physical_location = location.get("physicalLocation", {})

                artifact_location = physical_location.get(
                    "artifactLocation", {}
                )

                uri = artifact_location.get("uri")

                if uri:
                    file_hotspots[uri] += 1

    return file_hotspots

def display_output(results, limit):
    total = len(results)
    results = results[:limit]

    count_width = 8
    terminal_width = shutil.get_terminal_size().columns
    path_width = max(20, terminal_width - count_width - 4)

    print("\n=== Hotspot Summary ===\n")
    print(f"Showing top {len(results)} of {total:,} files\n")

    print(f"{'Hotspots':>{count_width}}  File")
    print(f"{'─' * count_width}  {'─' * path_width}")

    for path, hotspots in results:
        if len(path) > path_width:
            path = path[:path_width - 1] + "…"

        print(f"{hotspots:>{count_width},}  {path}")

def output_file(file_path, results):
    data = {"results": [{"path": path, "hotspot_count": count} for path, count in results]}
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

def main():
    parser = argparse.ArgumentParser(
        description="Count SARIF hotspots per file"
    )

    parser.add_argument(
        "sarif_file",
        help="Path to SARIF file"
    )

    parser.add_argument(
        "--top",
        "-t",
        type=int,
        help="Limit the results by n. Overrides default of 10"
    )

    parser.add_argument(
        "--out-file",
        "-o",
        type=str,
        help="Output file path for YAML results"
    )

    parser.add_argument(
        "--show-all",
        "-a",
        action="store_true",
        help="Displays all results to std out, overriding top limit"
    )

    args = parser.parse_args()

    result_limit = args.top or 10

    try:
        file_hotspots = parse_sarif(args.sarif_file)

        if not file_hotspots:
            print("No file-level hotspots found.")
            return


        sorted_results = sorted(
            file_hotspots.items(),
            key=lambda x: x[1],
            reverse=True
        )

        if args.show_all:
            result_limit = len(sorted_results)

        display_output(sorted_results, result_limit)

        path = args.out_file
        if path:
            output_file(path, sorted_results)


    except (FileNotFoundError, json.JSONDecodeError) as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
