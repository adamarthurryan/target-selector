"""Command-line interface for target-selector."""

import argparse
import sys
from pathlib import Path
import traceback

from target_selector.core import ObservationPlanner

OBSERVATORY_PATH = Path("config") / "observatory.yaml"


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Plan astronomical observations for given targets"
    )
    parser.add_argument(
        "targets",
        type=Path,
        help="Path to YAML targets configuration file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="query for a specific date"
    )
    parser.add_argument(
        "-c",
        "--calendar",
        action="store_true",
        help="display an observability calendar"
    )

    args = parser.parse_args()

    try:
        planner = ObservationPlanner(args.targets, 
                                     OBSERVATORY_PATH, 
                                     date=args.date, 
                                     calendar=args.calendar, 
                                     verbose=args.verbose)
        planner.run()
    except FileNotFoundError as e:
        print(f"Error: Targets file not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
