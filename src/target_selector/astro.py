"""Astronomical utility functions."""

from typing import List, Optional

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation

from astroplan import Observer, FixedTarget, observability_table, months_observable
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint, TimeConstraint)

from target_selector.validator import Constraints, Observatory, Targets

def _create_observer(observatory: Observatory) -> Observer:
    location = EarthLocation.from_geodetic(
        lon=observatory.longitude * u.deg,
        lat=observatory.latitude * u.deg,
        height=observatory.elevation * u.m,
    )
    return Observer(
        location=location,
        name=observatory.name,
        timezone="UTC"
    )

def _create_fixed_targets(targets: List[Target]) -> List[FixedTarget]:
    fixed_targets = []
    for target in targets:
        if target.coord is None:
            continue
        fixed_targets.append(FixedTarget(name=target.id or target.name, coord=target.coord))
    return fixed_targets

def _create_constraints(constraints: Optional[Constraints]) -> List:
    constraint_list = []
    if constraints is not None:
        if constraints.min_elevation is not None:
            constraint_list.append(AltitudeConstraint(min=constraints.min_elevation * u.deg))
        if constraints.max_airmass is not None:
            constraint_list.append(AirmassConstraint(max=constraints.max_airmass))

    constraint_list.append(AtNightConstraint.twilight_astronomical())

    return constraint_list

#date_range = [Time.now(), Time.now() + 7*u.day]
    
def observable_calendar(observatory: Observatory, targets: Targets):
    constraints = _create_constraints(targets.constraints)
    targets = _create_fixed_targets(targets.targets)
    observer = _create_observer(observatory)

    rows = []
    print(f"Calculating observability calendar for targets...")
    months_all = months_observable(constraints, observer, targets, time_grid_resolution=1.5*u.hour)
    for index, target in enumerate(targets):
        rows.append({"id": target.name, "months": months_all[index]})


    return rows
