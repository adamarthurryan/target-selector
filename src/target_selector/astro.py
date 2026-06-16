"""Astronomical utility functions."""

from typing import List, Optional

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation

from astroplan import Observer, FixedTarget, observability_table
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint, TimeConstraint)

from target_selector.validator import Config, Constraints, Observatory, Target

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

    print(constraint_list)
    return constraint_list

def observable_times(config: Config):
    print("Calculating observable times...")
    date_range = [Time(config.date_range.start), Time(config.date_range.end)]
    constraints = _create_constraints(config.constraints)
    targets = _create_fixed_targets(config.targets)
    observer = _create_observer(config.observatory)

    return observability_table(constraints, observer, targets, time_range=date_range)
