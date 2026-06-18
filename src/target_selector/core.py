"""Core functionality for astronomical observation planning."""

from importlib.resources import path
from logging import config

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from target_selector.lookup import lookup_targets
from target_selector.validator import Targets, Observatory
from target_selector.astro import observable_calendar, observable_today, get_local_timezone

class ObservationPlanner:
    """Plan observations for astronomical targets."""

    def __init__(self, targets_path: Path, observatory_path: Path, date=False, calendar=False, today=False, verbose=False):
        """
        Initialize the observation planner.

        Parameters
        ----------
        targets_path : Path
            Path to YAML targets file
        observatory_path : Path
            Path to YAML observatory location file
        date : Time, optional
            Query for a specific date (default: False)
        calendar : bool, optional
            Whether to display an observability calendar (default: False)
        today : bool, optional
            Whether to display tonight's visibility windows (default: False)
        verbose : bool, optional
            Whether to enable verbose output (default: False)
        """

        self._targets_path = targets_path
        self._observatory_path = observatory_path
        self._date = date
        self._calendar = calendar
        self._today = today
        self._verbose = verbose

    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration from the specified path."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def run(self):
        """
        Execute the observation planning process.

        Loads targets from config, calculates visibility windows,
        and outputs results to stdout.
        """

        targets_path = Path(self._targets_path)
        targets_config = self._load_config(targets_path)
        targets = Targets.model_validate(targets_config)

        observatory_path = Path(self._observatory_path)
        observatory_config = self._load_config(observatory_path)
        observatory = Observatory.model_validate(observatory_config)

        # Look up targets in catalogs
        targets = lookup_targets(targets)

        if self._today:
            self._display_today(observatory, targets)
            return

        # Calculate visibility windows (TODO)
        # TODO: Implement observation planning logic

        calendar=observable_calendar(observatory, targets)

        #TODO print header row
        print("Target ID   | Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec")
        print("------------------------------------------------------------------------")
        for row in calendar:
            print(f"{row['id']:11.11} |", end="")
            for month in range(1, 13):
                observable = month in row['months']
                print(f"{ '  X  ' if observable else '     '}", end="")
            print()

    def _display_today(self, observatory, targets):
        """Display target visibility windows for tonight's observation night."""
        tz = get_local_timezone(observatory)
        rows = observable_today(observatory, targets)

        tz_label = datetime.now(tz).strftime("%Z") or str(tz)
        print(f"Visibility windows for tonight's observation night (times in local time, {tz_label}):")
        print(f"{'Target ID':<14} | {'Visible from':<19} | {'Visible until':<19}")
        print("-" * 60)

        if not rows:
            print("No targets are observable during tonight's observation window.")
            return

        for row in rows:
            start_local = row["start"].to_datetime(timezone=tz)
            end_local = row["end"].to_datetime(timezone=tz)
            print(
                f"{row['id']:<14.14} | "
                f"{start_local:%Y-%m-%d %H:%M} | "
                f"{end_local:%Y-%m-%d %H:%M}"
            )
