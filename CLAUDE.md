# CLAUDE.md


## Project

`target-selector` — an astronomical observation planning tool

input data:
 - a list of targets
    either sky coordinates or an identifier to be looked up with Simbad
 - lat/long of observatory
 - date range
 - minimum elevation of target (degrees)
 - minimum length of observation (minutes)

output data:
 - a list of observations possible for each target given the above criteria
    - all observations need to be scheduled in full astronomical darkness at the given location
 - observation times should be reported in observatory local time and UTC

technical specs:
    - a command-line python application
    - input data is in yaml format
    - uses astropy and astroquery libraries
    - output is displayed to stdout

## Commands

build
