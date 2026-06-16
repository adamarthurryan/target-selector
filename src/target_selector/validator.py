"""Configuration validation for target-selector."""

from datetime import datetime
from typing import Any, Dict, List

from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u


def _validate_observatory(obs: Dict[str, Any]) -> None:
    if not isinstance(obs, dict):
        raise ValueError("'observatory' section missing or not a mapping")

    if "latitude" not in obs or "longitude" not in obs or "elevation" not in obs:
        raise ValueError("'observatory' must include 'latitude', 'longitude', and 'elevation' (use canonical keys)")

    try:
        obs["latitude"] = float(obs["latitude"])
        obs["longitude"] = float(obs["longitude"])
        obs["elevation"] = float(obs["elevation"])
    except Exception:
        raise ValueError(
            "'observatory.latitude', 'observatory.longitude', and 'observatory.elevation' must be numeric"
        )


def _validate_targets(targets: List[Dict[str, Any]]) -> None:
    if not isinstance(targets, list) or len(targets) == 0:
        raise ValueError("'targets' must be a non-empty list")

    for i, target in enumerate(targets):
        if not isinstance(target, dict):
            raise ValueError(f"Each target must be a mapping; target at index {i} is invalid")

        has_coords = ("ra" in target and "dec" in target)
        has_id = ("id" in target)
        if not has_id:
            raise ValueError(
                f"Target '{target.get('id', 'index:'+str(i))}' has no id"
            )
        
        if has_coords:
            try:
                target["ra"] = float(target["ra"])
                target["dec"] = float(target["dec"])
                target["coord"] = SkyCoord(
                    ra=target["ra"] * u.deg,
                    dec=target["dec"] * u.deg,
                    frame="icrs",
                )
            except Exception:
                raise ValueError(
                    f"Target '{target.get('name', 'index:'+str(i))}' has non-numeric 'ra'/'dec'"
                )


def _validate_date_range(date_range: Dict[str, Any]) -> None:
    if not isinstance(date_range, dict):
        raise ValueError("'date_range' section missing or not a mapping")

    start = date_range.get("start")
    end = date_range.get("end")
    if not start or not end:
        raise ValueError("'date_range' must include 'start' and 'end'")

    try:
        date_range["start"] = Time(start, format="iso", scale="utc")
        date_range["end"] = Time(end, format="iso", scale="utc")
    except Exception:
        raise ValueError("'date_range.start' and 'date_range.end' must be ISO-8601 date strings")


def _validate_constraints(constraints: Dict[str, Any]) -> None:
    if not isinstance(constraints, dict):
        return  # Constraints are optional, so if not provided or not a dict, just skip

    try:
        if (constraints["min_duration"] is not None):
            constraints["min_duration"] = int(constraints["min_duration"])
        if (constraints["min_elevation"] is not None):
            constraints["min_elevation"] = float(constraints["min_elevation"])
        if (constraints["max_airmass"] is not None):
            constraints["max_airmass"] = float(constraints["max_airmass"])

    except Exception:
        raise ValueError("'min_duration', 'min_elevation', and 'max_airmass' must be numeric")


def validate_config(config: Dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a mapping (YAML top-level must be a mapping)")

    _validate_observatory(config.get("observatory"))
    _validate_targets(config.get("targets"))
    _validate_date_range(config.get("date_range"))
    _validate_constraints(config.get("constraints"))
