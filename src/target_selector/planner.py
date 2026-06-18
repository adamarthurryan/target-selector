"""Astronomical utility functions."""

from datetime import timezone as dt_timezone, timedelta, tzinfo
from typing import List, Optional

import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation

from astroplan import Observer, FixedTarget, observability_table, months_observable, is_observable
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint, TimeConstraint)

from target_selector.validator import Constraints, Observatory, Target, Targets

def get_local_timezone(observatory: Observatory) -> tzinfo:
    """Return a tzinfo describing the observatory's local time.

    Uses the configured IANA timezone (e.g. "America/Denver") when provided,
    otherwise falls back to a fixed UTC offset estimated from the observatory's
    longitude (15 degrees per hour).
    """
    if observatory.timezone:
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(observatory.timezone)
        except Exception:
            import pytz
            return pytz.timezone(observatory.timezone)

    offset_hours = int(round(observatory.longitude / 15.0))
    return dt_timezone(timedelta(hours=offset_hours))


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


def observable_today(observatory: Observatory, targets: Targets):
    constraints = _create_constraints(targets.constraints)
    fixed_targets = _create_fixed_targets(targets.targets)
    observer = _create_observer(observatory)

    now = Time.now()
    noon_today = Time(now.datetime.strftime('%Y-%m-%d') + ' 12:00:00', scale='utc')

    sunset = observer.sun_set_time(noon_today, which='next', horizon=-18 * u.deg)
    sunrise = observer.sun_rise_time(sunset, which='next', horizon=-18 * u.deg)

    time_grid_resolution = 5 * u.minute
    n_steps = int(((sunrise - sunset).to(u.minute) / time_grid_resolution.to(u.minute)).decompose())
    time_grid = sunset + time_grid_resolution * np.arange(n_steps + 1)

    rows = []
    for target in fixed_targets:
        target_constraints = [c for c in constraints if not isinstance(c, AtNightConstraint)]
        observable_mask = np.ones(len(time_grid), dtype=bool)
        for constraint in target_constraints:
            observable_mask &= constraint(observer, target, times=time_grid)

        if not np.any(observable_mask):
            continue

        indices = np.where(observable_mask)[0]
        start = time_grid[indices[0]]
        end = time_grid[indices[-1]]
        rows.append({
            "id": target.name,
            "start": start,
            "end": end,
        })

    return rows
