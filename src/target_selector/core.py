"""Core functionality for astronomical observation planning."""

from logging import config

import yaml
from pathlib import Path
from typing import Dict, Any

from target_selector.lookup import lookup_targets
from target_selector.validator import validate_config
from target_selector.astro import observable_times

class ObservationPlanner:
    """Plan observations for astronomical targets."""

    def __init__(self, config_path: Path):
        """
        Initialize the observation planner.

        Parameters
        ----------
        config_path : Path
            Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

        self._validate_config()


    def _load_config(self) -> Dict[str, Any]:
        """
        Load and parse the YAML configuration file.

        Returns
        -------
        dict
            Configuration dictionary
        """
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)
        

    def _validate_config(self):
        """
        Validate the structure and contents of the configuration.

        Raises
        ------
        ValueError
            If the configuration is invalid
        """
        validate_config(self.config)
    
    def _lookup_targets(self):
        """
        Look up target information in astronomical catalogs.

        Targets are specified in the configuration and may include names, coordinates, etc. 
        This method will query catalogs (e.g., SIMBAD, Gaia) to retrieve necessary information
        """
        targets = self.config["targets"]
        self.config["targets"] = lookup_targets(targets)

    def run(self):
        """
        Execute the observation planning process.

        Loads targets from config, calculates visibility windows,
        and outputs results to stdout.
        """
        # Look up targets in catalogs
        self._lookup_targets()
        

        # Calculate visibility windows (TODO)
        # TODO: Implement observation planning logic

        table=observable_times(self.config)
        print(table)
