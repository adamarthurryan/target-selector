import os
import sys

import pytest
from astropy.coordinates import SkyCoord
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from target_selector.validator import Observatory, Targets, Target, DateRange, Constraints


def make_valid_observatory_config():
    return {
        "latitude": 40.0,
        "longitude": -105.0,
        "elevation": 1600,
    }


def make_valid_targets_config():
    return {
        "targets": [
            {
                "id": "M42",
                "ra": 83.82,
                "dec": -5.39,
            },
            {
                "id": "Andromeda Galaxy",
            },
        ],
        "constraints": {
            "min_elevation": 30,
            "min_duration": 120,
        },
    }


class TestObservatory:
    """Test Observatory model validation."""

    def test_valid_observatory(self):
        obs = Observatory.model_validate(make_valid_observatory_config())
        assert obs.latitude == 40.0
        assert obs.longitude == -105.0
        assert obs.elevation == 1600.0

    def test_missing_latitude(self):
        config = make_valid_observatory_config()
        del config["latitude"]
        with pytest.raises(ValueError, match="latitude.*longitude.*elevation"):
            Observatory.model_validate(config)

    def test_missing_longitude(self):
        config = make_valid_observatory_config()
        del config["longitude"]
        with pytest.raises(ValueError, match="latitude.*longitude.*elevation"):
            Observatory.model_validate(config)

    def test_missing_elevation(self):
        config = make_valid_observatory_config()
        del config["elevation"]
        with pytest.raises(ValueError, match="latitude.*longitude.*elevation"):
            Observatory.model_validate(config)

    def test_non_numeric_values(self):
        config = make_valid_observatory_config()
        config["latitude"] = "not-a-number"
        with pytest.raises(ValueError):
            Observatory.model_validate(config)


class TestTarget:
    """Test Target model validation."""

    def test_target_with_coordinates(self):
        target_data = {"id": "M42", "ra": 83.82, "dec": -5.39}
        target = Target.model_validate(target_data)
        assert target.id == "M42"
        assert target.ra == 83.82
        assert target.dec == -5.39
        assert isinstance(target.coord, SkyCoord)
        assert target.coord.ra.deg == pytest.approx(83.82)
        assert target.coord.dec.deg == pytest.approx(-5.39)

    def test_target_with_id_only(self):
        target_data = {"id": "Andromeda Galaxy"}
        target = Target.model_validate(target_data)
        assert target.id == "Andromeda Galaxy"
        assert target.ra is None
        assert target.dec is None
        assert target.coord is None

    def test_target_missing_coordinates_and_id(self):
        target_data = {}
        with pytest.raises(ValueError, match="must provide either 'ra' and 'dec' or an 'id'"):
            Target.model_validate(target_data)

    def test_target_non_numeric_ra(self):
        target_data = {"ra": "not-a-number", "dec": -5.39}
        with pytest.raises(ValueError, match="non-numeric"):
            Target.model_validate(target_data)

    def test_target_non_numeric_dec(self):
        target_data = {"ra": 83.82, "dec": "not-a-number"}
        with pytest.raises(ValueError, match="non-numeric"):
            Target.model_validate(target_data)


class TestTargets:
    """Test Targets model validation."""

    def test_valid_targets_config(self):
        config = {
            "targets": [
                {"id": "M42", "ra": 83.82, "dec": -5.39},
                {"id": "Andromeda Galaxy"},
            ],
            "constraints": {"min_elevation": 30, "min_duration": 120},
        }
        targets = Targets.model_validate(config)
        assert len(targets.targets) == 2
        assert targets.targets[0].id == "M42"
        assert targets.targets[1].id == "Andromeda Galaxy"
        assert targets.constraints.min_elevation == 30.0
        assert targets.constraints.min_duration == 120

    def test_empty_targets_list(self):
        config = {"targets": [], "constraints": {"min_elevation": 30, "min_duration": 120}}
        with pytest.raises(ValueError, match="non-empty list"):
            Targets.model_validate(config)

    def test_targets_without_constraints(self):
        config = {
            "targets": [{"id": "M42", "ra": 83.82, "dec": -5.39}],
        }
        targets = Targets.model_validate(config)
        assert len(targets.targets) == 1
        assert targets.constraints is None


class TestDateRange:
    """Test DateRange model validation."""

    def test_valid_date_range(self):
        dr = DateRange.model_validate(
            {"start": "2026-06-14", "end": "2026-06-21"}
        )
        assert isinstance(dr.start, datetime)
        assert isinstance(dr.end, datetime)
        assert dr.start.year == 2026

    def test_missing_start_date(self):
        with pytest.raises(ValueError, match="start.*end"):
            DateRange.model_validate({"start": None, "end": "2026-06-21"})

    def test_missing_end_date(self):
        with pytest.raises(ValueError, match="start.*end"):
            DateRange.model_validate({"start": "2026-06-14", "end": None})

    def test_invalid_date_format(self):
        with pytest.raises(ValueError, match="ISO-8601"):
            DateRange.model_validate({"start": "invalid", "end": "also-invalid"})


class TestConstraints:
    """Test Constraints model validation."""

    def test_valid_constraints(self):
        constraints = Constraints.model_validate(
            {"min_elevation": 30, "min_duration": 120}
        )
        assert constraints.min_elevation == 30.0
        assert constraints.min_duration == 120

    def test_missing_min_elevation(self):
        with pytest.raises(ValueError, match="min_elevation.*min_duration"):
            Constraints.model_validate({"min_elevation": None, "min_duration": 120})

    def test_missing_min_duration(self):
        with pytest.raises(ValueError, match="min_elevation.*min_duration"):
            Constraints.model_validate({"min_elevation": 30, "min_duration": None})

    def test_non_numeric_values(self):
        with pytest.raises(ValueError):
            Constraints.model_validate(
                {"min_elevation": "not-a-number", "min_duration": 120}
            )

