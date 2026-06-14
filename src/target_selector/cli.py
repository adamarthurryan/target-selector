"""Command-line interface for target-selector."""

import argparse
import sys
from pathlib import Path

from target_selector.core import ObservationPlanner


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Plan astronomical observations for given targets"
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    try:
        planner = ObservationPlanner(args.config)
        planner.run()
    except FileNotFoundError as e:
        print(f"Error: Configuration file not found: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
