import argparse
import json
from collections import defaultdict


def parse_sarif(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sarif_data = json.load(f)

    file_alerts = defaultdict(int)

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
                    file_alerts[uri] += 1

    return file_alerts


def main():
    parser = argparse.ArgumentParser(
        description="Count SARIF alerts per file"
    )

    parser.add_argument(
        "sarif_file",
        help="Path to SARIF file"
    )

    parser.add_argument(
        "--top",
        type=int,
        help="Limit the results by n. Overrides default of 10"
    )

    args = parser.parse_args()

    result_limit = args.top or 10

    try:
        file_alerts = parse_sarif(args.sarif_file)

        if not file_alerts:
            print("No file-level alerts found.")
            return

        print("\n=== SARIF Alert Summary ===\n")
        print(f"[+] Showing top {result_limit} results...")

        sorted_results = sorted(
            file_alerts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for file, count in sorted_results[:result_limit]:
            print(f"{count:4} alerts | {file}")


        print(f"\nTotal files affected: {len(file_alerts)}")
        print(f"Total alerts: {sum(file_alerts.values())}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
