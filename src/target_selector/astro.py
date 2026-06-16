"""Astronomical utility functions."""

from typing import Any, Dict, List

from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation

from astroplan import Observer, FixedTarget, observability_table
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint, TimeConstraint)

def _create_observer(observatory) -> Observer:
    location = EarthLocation.from_geodetic(
        lon=observatory["longitude"] * u.deg,
        lat=observatory["latitude"] * u.deg,
        height=observatory["elevation"] * u.m,
    )
    return Observer(
        location=location, 
        name=observatory.get("name", "Unnamed Observatory"), 
        timezone="UTC"
    )

def _create_fixed_targets(targets: List[Dict[str, Any]]) -> List[FixedTarget]:
    fixed_targets = []
    for target in targets:
        if "coord" not in target:
            continue
        fixed_targets.append(FixedTarget(name=target['id'], coord=target["coord"]))
    return fixed_targets

def _create_constraints(constraints: Dict[str, Any]) -> List:
    constraint_list = []
    if "min_elevation" in constraints:
        constraint_list.append(AltitudeConstraint(min=constraints["min_elevation"] * u.deg))
    if "max_airmass" in constraints:
        constraint_list.append(AirmassConstraint(max=constraints["max_airmass"]))

    constraint_list.append(AtNightConstraint.twilight_astronomical())

    print(constraint_list)
    return constraint_list

def observable_times(config: Dict[str, Any]): #observer: Observer, targets: List[FixedTarget], constraints: List, date_range: Dict[str, Time]):
    print("Calculating observable times...")
    date_range = [config["date_range"]["start"], config["date_range"]["end"]]
    constraints = _create_constraints(config["constraints"])
    targets = _create_fixed_targets(config["targets"])
    observer = _create_observer(config["observatory"])

    date_range=[config["date_range"]["start"], config["date_range"]["end"]]

    return observability_table(constraints, observer, targets, time_range=date_range)