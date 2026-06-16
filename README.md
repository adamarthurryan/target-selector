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

Create a YAML configuration file with your observation parameters: see **example_config.yaml** for an example.

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
