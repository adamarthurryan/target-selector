"""Catalog lookup helpers for target-selector."""

from typing import Dict, List
import copy

from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

from target_selector.validator import Target


def lookup_targets(targets: List[Target]) -> List[Target]:

    targets = copy.deepcopy(targets)

    targets_to_lookup: List[str] = []
    target_indices: Dict[str, int] = {}

    for i, target in enumerate(targets):
        if target.ra is not None and target.dec is not None:
            continue

        if not target.id:
            raise ValueError(
                f"Target '{target.name or 'unknown'}' has no coordinates and no identifier for lookup"
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
            if lookup_id.lower() in identifier.lower() or identifier.lower() in lookup_id.lower():
                matched_identifier = lookup_id
                break

        if matched_identifier is None:
            continue

        target_idx = target_indices[matched_identifier]
        targets[target_idx].ra = float(result["ra"])
        targets[target_idx].dec = float(result["dec"])
        targets[target_idx].coord = SkyCoord(
            ra=targets[target_idx].ra * u.deg,
            dec=targets[target_idx].dec * u.deg,
            frame="icrs",
        )

    for identifier in targets_to_lookup:
        target_idx = target_indices[identifier]
        if targets[target_idx].ra is None:
            #TODO: don't need to fail on missing targets, just warn and skip
            raise ValueError(f"Target '{identifier}' not found in SIMBAD")

    return targets
