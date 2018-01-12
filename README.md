# op1svg

Normalize SVG files so that the OP-1 understands them.


- Decimals are limited to 4 (the OP-1 supports max 4 decimals)
- Styles are coverted to attributes
- Inkscape ellipses are converted to real ellipses
- Remove Inkscape specific tags and attributes
- Remove comments

## Usage

    ./main.py original-file.svg fixed-file.svg

## Dependencies

This requires svg.path to be installed. Install it by running the following
command:

    pip3 install svg.path

NOTE: when this project matures it'll be made installable so that you don't have
to worry about dependencies.

