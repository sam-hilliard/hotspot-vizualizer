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

    args = parser.parse_args()

    try:
        file_alerts = parse_sarif(args.sarif_file)

        if not file_alerts:
            print("No file-level alerts found.")
            return

        print("\n=== SARIF Alert Summary ===\n")

        for file, count in sorted(
            file_alerts.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"{count:4} alerts | {file}")

        print(f"\nTotal files affected: {len(file_alerts)}")
        print(f"Total alerts: {sum(file_alerts.values())}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
