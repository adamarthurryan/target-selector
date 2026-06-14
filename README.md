# Target Selector

An astronomical observation planning tool for determining optimal observation windows for celestial targets.

## Features

- Load target information from YAML configuration files
- Support for sky coordinates or Simbad identifiers
- Calculate visibility windows based on:
  - Observatory location (latitude/longitude)
  - Observation date range
  - Minimum target elevation
  - Minimum observation duration
- Report observation times in both local and UTC timezone

## Requirements

- Python 3.9+
- astropy
- astroquery
- pyyaml

## Installation

Clone the repository and install in development mode:

```bash
git clone <repository-url>
cd target-selector
pip install -e .
```

## Usage

Create a YAML configuration file with your observation parameters:

```yaml
observatory:
  latitude: 40.0
  longitude: -105.0

targets:
  - name: M31
    identifier: Andromeda Galaxy
  - name: M42
    ra: 83.8
    dec: -5.4

date_range:
  start: 2026-06-14
  end: 2026-06-21

constraints:
  min_elevation: 30
  min_duration: 120  # minutes
```

Then run:

```bash
target-selector config.yaml
```

## Development

Install development dependencies and run tests:

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT License
