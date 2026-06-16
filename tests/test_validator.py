import os
import sys

import pytest
from astropy.coordinates import SkyCoord
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from target_selector.validator import Config, validate_config


def make_valid_config():
    return {
        "observatory": {
            "latitude": 40.0,
            "longitude": -105.0,
            "elevation": 1600,
        },
        "targets": [
            {
                "name": "M42",
                "ra": 83.82,
                "dec": -5.39,
            },
            {
                "name": "M31",
                "id": "Andromeda Galaxy",
            },
        ],
        "date_range": {
            "start": "2026-06-14",
            "end": "2026-06-21",
        },
        "constraints": {
            "min_elevation": 30,
            "min_duration": 120,
        },
    }


def test_validate_config_accepts_valid_config():
    config = validate_config(make_valid_config())

    assert isinstance(config, Config)

    assert config.observatory.latitude == 40.0
    assert config.observatory.longitude == -105.0
    assert config.observatory.elevation == 1600.0

    assert isinstance(config.date_range.start, datetime)
    assert isinstance(config.date_range.end, datetime)
    assert config.date_range.start.year == 2026

    assert config.constraints.min_elevation == 30.0
    assert config.constraints.min_duration == 120

    target = config.targets[0]
    assert isinstance(target.coord, SkyCoord)
    assert target.coord.ra.deg == pytest.approx(83.82)
    assert target.coord.dec.deg == pytest.approx(-5.39)


@pytest.mark.parametrize(
    "config, message",
    [
        (
            {"observatory": {"lat": 40.0, "longitude": -105.0, "elevation": 1600}},
            "observatory' must include 'latitude', 'longitude', and 'elevation",
        ),
        (
            {"observatory": {"latitude": 40.0, "longitude": -105.0, "elevation": 1600}, "targets": []},
            "'targets' must be a non-empty list",
        ),
        (
            {
                "observatory": {"latitude": 40.0, "longitude": -105.0, "elevation": 1600},
                "targets": [{"name": "BadTarget"}],
            },
            "must provide either 'ra' and 'dec' or an 'id' for lookup",
        ),
        (
            {
                "observatory": {"latitude": 40.0, "longitude": -105.0, "elevation": 1600},
                "targets": [{"name": "M42", "ra": "not-a-number", "dec": -5.39}],
            },
            "has non-numeric 'ra'/'dec'",
        ),
        (
            {
                "observatory": {"latitude": 40.0, "longitude": -105.0, "elevation": 1600},
                "targets": [{"id": "M31"}],
                "date_range": {"start": "2026-06-14"},
            },
            "'date_range' must include 'start' and 'end'",
        ),
        (
            {
                "observatory": {"latitude": 40.0, "longitude": -105.0, "elevation": 1600},
                "targets": [{"id": "M31"}],
                "date_range": {"start": "invalid", "end": "invalid"},
            },
            "'date_range.start' and 'date_range.end' must be ISO-8601 date strings",
        ),
        (
            {
                "observatory": {"latitude": 40.0, "longitude": -105.0, "elevation": 1600},
                "targets": [{"id": "M31"}],
                "date_range": {"start": "2026-06-14", "end": "2026-06-21"},
                "constraints": {"min_elevation": 30},
            },
            "'constraints' must include 'min_elevation' and 'min_duration'",
        ),
    ],
)
def test_validate_config_rejects_invalid_config(config, message):
    with pytest.raises(ValueError, match=message):
        validate_config(config)


def test_validate_config_rejects_non_mapping():
    with pytest.raises(ValueError, match="Configuration must be a mapping"):
        validate_config(["not", "a", "mapping"])
