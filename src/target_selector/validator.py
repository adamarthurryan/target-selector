"""Configuration validation for target-selector."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from astropy.coordinates import SkyCoord
from astropy.time import Time
import astropy.units as u
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class Observatory(BaseModel):
    """Observatory location."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    latitude: float
    longitude: float
    elevation: float
    name: str = "Unnamed Observatory"

    @model_validator(mode="before")
    @classmethod
    def _check_required_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict) or not {"latitude", "longitude", "elevation"} <= data.keys():
            raise ValueError(
                "'observatory' must include 'latitude', 'longitude', and 'elevation' (use canonical keys)"
            )
        return data


class Target(BaseModel):
    """An observation target, identified by coordinates and/or a lookup id."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[str] = None
    name: Optional[str] = None
    ra: Optional[float] = None
    dec: Optional[float] = None
    coord: Optional[SkyCoord] = None

    @field_validator("ra", "dec", mode="before")
    @classmethod
    def _parse_numeric(cls, value: Any) -> Any:
        if value is None:
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError("has non-numeric 'ra'/'dec'")

    @model_validator(mode="after")
    def _check_identification(self) -> "Target":
        if self.ra is None or self.dec is None:
            if not self.id:
                raise ValueError("must provide either 'ra' and 'dec' or an 'id' for lookup")
            return self

        self.coord = SkyCoord(ra=self.ra * u.deg, dec=self.dec * u.deg, frame="icrs")
        return self


class DateRange(BaseModel):
    """The date range over which to search for observations."""

    start: datetime
    end: datetime

    @model_validator(mode="before")
    @classmethod
    def _check_required_keys(cls, data: Any) -> Any:
        if not isinstance(data, dict) or not data.get("start") or not data.get("end"):
            raise ValueError("'date_range' must include 'start' and 'end'")
        return data

    @field_validator("start", "end", mode="before")
    @classmethod
    def _parse_date(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            return value
        try:
            return Time(value, format="iso", scale="utc").to_datetime()
        except Exception:
            raise ValueError("'date_range.start' and 'date_range.end' must be ISO-8601 date strings")


class Constraints(BaseModel):
    """Constraints on observation viability."""

    min_elevation: float
    min_duration: int
    max_airmass: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def _check_required_keys(cls, data: Any) -> Any:
        if (
            not isinstance(data, dict)
            or data.get("min_elevation") is None
            or data.get("min_duration") is None
        ):
            raise ValueError("'constraints' must include 'min_elevation' and 'min_duration'")
        return data


class Config(BaseModel):
    """Top-level target-selector configuration."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    observatory: Observatory
    targets: List[Target]
    date_range: DateRange
    constraints: Optional[Constraints] = None

    @field_validator("targets")
    @classmethod
    def _check_targets_nonempty(cls, value: List[Target]) -> List[Target]:
        if not value:
            raise ValueError("'targets' must be a non-empty list")
        return value


def validate_config(config: Dict[str, Any]) -> Config:
    """
    Validate the structure and contents of a configuration dictionary.

    Parameters
    ----------
    config : dict
        Configuration dictionary, as loaded from YAML.

    Returns
    -------
    Config
        A validated, structured representation of the configuration.

    Raises
    ------
    ValueError
        If the configuration is invalid.
    """
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a mapping (YAML top-level must be a mapping)")

    return Config.model_validate(config)
