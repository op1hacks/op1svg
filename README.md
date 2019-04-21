# OP-1 SVG Normalizer

Normalize SVG files so that the OP-1 understands them.

- Remove unsupported tags and attributes
- Remove comments
- Convert styles to attributes, and drop unsupported styles
- Fix decimals. A maximum of 4 decimals is supported by the OP-1
- Reformat the path data in paths. Use svg.path to stringify them into a uniform format


## Usage

    ./main.py original-file.svg fixed-file.svg

The above command reads `original-file.svg` normalizes it and saves the normalized version to `fixed-file.svg`.

## Dependencies

This requires svg.path to be installed. Install it by running the following
command:

    pip3 install svg.path
