"""Core functionality for astronomical observation planning."""

import yaml
from pathlib import Path
from typing import Dict, Any, List

from astroquery.simbad import Simbad


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
        # TODO: Implement validation logic
    
    def _lookup_targets(self):
        """
        Look up target information in astronomical catalogs.

        Targets are specified in the configuration and may include names, coordinates, etc. 
        This method will query catalogs (e.g., SIMBAD, Gaia) to retrieve necessary information

        """
        targets = self.config.get("targets", [])
        
        # Collect targets that need coordinate lookup
        targets_to_lookup = []
        target_indices = {}
        
        for i, target in enumerate(targets):
            # Skip targets that already have coordinates
            if "ra" in target and "dec" in target:
                continue
            
            # Validate that target has an identifier
            if "id" not in target:
                raise ValueError(f"Target '{target.get('name', 'unknown')}' has no coordinates and no identifier for lookup")
            
            identifier = target["id"]
            targets_to_lookup.append(identifier)
            target_indices[identifier] = i
        
        # Exit early if all targets have coordinates
        if not targets_to_lookup:
            return
        
        # Query SIMBAD for all targets at once
        try:
            results = Simbad.query_objects(targets_to_lookup)
            
            if results is None:
                raise ValueError(f"No targets found in SIMBAD: {targets_to_lookup}")
            
            # Create a mapping of identifier to coordinates
            for result in results:
                identifier = result["user_specified_id"].decode() if isinstance(result["user_specified_id"], bytes) else result["user_specified_id"]
                
                # Find the original identifier in our list (case-insensitive match)
                matched_identifier = None
                for lookup_id in targets_to_lookup:
                    if lookup_id.lower() in identifier.lower() or identifier.lower() in lookup_id.lower():
                        matched_identifier = lookup_id
                        break
                
                if matched_identifier is None:
                    continue
                
                # Update the target with coordinates
                target_idx = target_indices[matched_identifier]
                targets[target_idx]["ra"] = float(result["ra"])
                targets[target_idx]["dec"] = float(result["dec"])

            # Verify all targets were found
            for identifier in targets_to_lookup:
                target_idx = target_indices[identifier]

                if "ra" not in targets[target_idx]:
                    raise ValueError(f"Target '{identifier}' not found in SIMBAD")
                    
        except Exception as e:
            if "not found in SIMBAD" in str(e):
                raise
            raise ValueError(f"Failed to query SIMBAD: {e}")

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
        print("Observation planning results:")
        print(self.config)
