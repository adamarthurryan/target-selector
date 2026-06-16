"""Catalog lookup helpers for target-selector."""

from typing import Dict, List

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

from target_selector.validator import Targets


def lookup_targets(targets: Targets) -> Targets:
    print("Looking up targets in SIMBAD...")
    targets = targets.model_copy(deep=True)

    targets_to_lookup: List[str] = []
    target_indices: Dict[str, int] = {}

    for i, target in enumerate(targets.targets):
        if target.coord is not None or (target.ra is not None and target.dec is not None):
            continue

        if not target.id:
            raise ValueError(
                f"Target '{target.id or 'unknown'}' has no coordinates and no identifier for lookup"
            )

        identifier = target.id
        targets_to_lookup.append(identifier)
        target_indices[identifier] = i

    if not targets_to_lookup:
        return targets

    results = Simbad.query_objects(targets_to_lookup)
    if results is None:
        raise ValueError(f"No targets found in SIMBAD: {targets_to_lookup}")

    for result in results:
        identifier = (
            result["user_specified_id"].decode()
            if isinstance(result["user_specified_id"], bytes)
            else result["user_specified_id"]
        )

        matched_identifier = None
        for lookup_id in targets_to_lookup:
            if lookup_id.casefold() in identifier.casefold():
                matched_identifier = lookup_id
                break

        if matched_identifier == None:
            continue

        target_idx = target_indices[matched_identifier]
        target = targets.targets[target_idx]
        target.ra = float(result["ra"])
        target.dec = float(result["dec"])
        target.coord = SkyCoord(
            ra=target.ra * u.deg,
            dec=target.dec * u.deg,
            frame="icrs",
        )
    
    # TODO: Handle targets not found in SIMBAD (currently left with missing coordinates)
    for target in targets.targets:
        if target.coord is None and (target.ra is None or target.dec is None):
            print(f"Warning: Target '{target.id}' not found in SIMBAD and has no coordinates")

    return targets
