#!/usr/bin/env python3

import argparse
from svg.path import parse_path
import xml.etree.ElementTree as ET


__author__ = "Richard Lewis"
__copyright__ = "Copyright 2019, Richard Lewis"
__license__ = "MIT"
__status__ = "Development"
__version__ = "0.1.0"


description = """
Normalize SVG files so that the OP-1 understands them.
"""

"""
NOTES

- Group transformations are not supported. Only transformations for individual elements.
- Only the following transforms are supported: matrix, translate, scale (TODO: verify this)

DONE:
- Remove unsupported tags and attributes
- Remove comments
- Convert styles to attributes, and drop unsupported styles
- Fix decimals. A maximum of 4 decimals is supported by the OP-1
- Reformat the path data in paths. Use svg.path to stringify them into a uniform format

TODO:
- Fix group transforms (they are unsnupported by the OP-1)
- Check what color notations are supported. The original graphics files only use hex notation.

"""

# Supported tags
TAGS = ["svg", "rect", "g", "line", "path", "polyline", "circle", "polygon", "ellipse", "defs", "clipPath", "use"]

# Supported attributes
ATTR_ALL = [
    "xmlns", "xmlns:xlink",
    "version", "id", "x", "y", "width", "height", "viewBox",
    "enable-background", "space", "fill", "stroke", "d", "stroke-width",
    "cx", "cy", "r", "x1", "y1", "x2", "y2", "stroke-dasharray", "display",
    "stroke-linecap", "points", "rx", "ry", "stroke-linejoin", "transform",
    "stroke-miterlimit", "href", "overflow", "clip-path", "opacity",
]

# Numeric attributes (TODO: include points or not?)d
ATTR_NUMERIC = [
    "x", "y", "width", "height", "stroke-width", "cx", "cy", "r", "x1", "y1",
    "x2", "y2", "rx", "ry", "opacity"  # , "points"
]


DECIMAL_PRECISION = 4


def is_self_closing(elem):
    return ET.tostring(elem).strip().endswith(b"/>")


def is_supported_tag(elem):
    return get_element_tag_name(elem) in TAGS


def is_supported_attr(name):
    return name in ATTR_ALL


def normalize_name(name):
    if "}" in name:
        name = name[name.find("}")+1:]
    return name


def limit_decimals(n):
    if not "." in n:
        return n
    # TODO: Handle px and other units?
    return ("{0:." + str(DECIMAL_PRECISION) + "f}").format(float(n))


def get_element_tag_name(elem):
    return normalize_name(elem.tag)


def parse_styles(styles_str):
    # Inkscape (and others) store SVG properties in the style attribute instead of
    # using a real attribute for each value. OP-1 doesn't like that. This converts
    # the styles to real attributes.
    if not styles_str:
        return {}

    if ";" in styles_str:
        items = styles_str.split(";")
    else:
        items = [styles_str]

    styles = {}
    for item in items:
        parts = item.split(":")
        styles[parts[0]] = parts[1]

    return styles


def attributes_to_string(attrs):
    s = ""
    if "style" in attrs:
        styles = parse_styles(attrs["style"])
        del attrs["style"]
        attrs.update(styles)

    for key in attrs:
        if not is_supported_attr(key):
            continue
        value = attrs[key]
        # Limit decimals
        if key in ATTR_NUMERIC:
            value = limit_decimals(value)
        # Normalize svg paths
        if key == "d":
            path = parse_path(value)
            # Render the path back to a string
            # This generates a uniform path string that the OP-1 understands
            value = path.d()
        s = s + " " + normalize_name(key) + "=\"" + value + "\""
    return s


def element_start_tag_string(elem):
    name = get_element_tag_name(elem)
    attrs = attributes_to_string(elem.attrib)
    return "<" + name + attrs + ("/>" if is_self_closing(elem) else ">")


def element_end_tag_string(elem):
    if is_self_closing(elem):
        return ""
    name = get_element_tag_name(elem)
    return "</" + name + ">"


def iterate_tree(tree, depth, callback=None):
    output = ""

    depth += 1

    for elem in tree:
        if not is_supported_tag(elem):
            continue
        if callback:
            callback(elem)
        # Set indent level
        indent = " " * (depth * 2)

        # Add start tag to output
        output += indent + element_start_tag_string(elem) + "\n"

        # Add text contents if element has any
        if elem.text and elem.text.strip():
            output += elem.text

        # Add children
        output += iterate_tree(elem, depth, callback)

        # Add end tag if necessary
        end_tag = element_end_tag_string(elem)
        if end_tag:
            output += indent + end_tag + "\n"

    depth -= 1

    return output


def clean_svg_tree(tree):
    root = tree.getroot()

    root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
    root.attrib["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

    output = '<?xml version="1.0" encoding="utf-8"?>\n'
    output += '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
    output += element_start_tag_string(root) + "\n"
    output += iterate_tree(root, 0) + "\n"
    output += element_end_tag_string(root)

    return output


def main():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("in_path", type=str, nargs=1, help="file path of svg file to fix")
    parser.add_argument("out_path", type=str, nargs=1, help="file path to write the fixed svg to")
    parser.add_argument("--debug", action="store_true", help="print debug messages") # TODO
    parser.add_argument("--version", action="version", version=__version__,
                        help="show program's version number and exit")
    args = parser.parse_args()

    ET.register_namespace("", "http://www.w3.org/2000/svg")
    print("Parsing file...")
    tree = ET.parse(args.in_path[0])

    print("Optimizing SVG...")
    output = clean_svg_tree(tree)

    print("Saving...")
    f = open(args.out_path[0], "w")
    f.write(output)
    f.close()

    print("Done.")


if __name__ == '__main__':
    main()
