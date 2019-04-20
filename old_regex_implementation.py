#!/usr/bin/env python3

import re
import sys

from svg.path import parse_path


# Limit decimals. The OP-1 supports up to 4 decimals
def fix_decimals(pat):
    text = pat.group(1)
    text = "." + text[:4]
    return text


# Inkscape (and others) store SVG properties in the style attribute instead of
# using a real attribute for each value. OP-1 doesn't like that. This converts
# the styles to real attributes.
def styles_to_attributes(styles):
    if not styles:
        return ""

    if ";" in styles:
        properties = styles.split(";")
    else:
        properties = [styles]

    attrs = []
    for prop in properties:
        attrs.append(style_property_to_attribute(prop))

    attr_str = " ".join(attrs)
    return attr_str


def style_property_to_attribute(prop):
    whitelist = [
        "color",
        "display",
        "opacity",
        "fill",
        "stroke",
        "stroke-width",
        "stroke-linecap",
        "stroke-linejoin",
        "stroke-miterlimit",
    ]

    parts = prop.split(":")
    if parts[0] not in whitelist:
        return ""

    attr = parts[0] + '="' + parts[1] + '"'
    return attr


# Convert properties in style attribute to real attributes
def fix_styles(pat):
    text = pat.group(1)[7:-1]
    attr_str = styles_to_attributes(text)
    return attr_str


# Normalize Inkscapes ellipses to actual ellipse tags
def fix_ellipses(pat):
    text = pat.group(1)

    style = get_attr(text, "style")

    cx = get_attr(text, "sodipodi:cx")
    cy = get_attr(text, "sodipodi:cy")

    rx = get_attr(text, "sodipodi:rx")
    ry = get_attr(text, "sodipodi:ry")

    new_tag = '<ellipse cx="{}" cy="{}" rx="{}" ry="{}" style="{}" />'.format(cx, cy, rx, ry, style)
    return new_tag


# Reformat the path data in paths
def fix_paths(pat):
    text = pat.group(1)
    d = get_attr(text, "d")

    # Parse the path with svg.path
    path = parse_path(d)
    # Render the path back to a string
    # This generates a uniform path string that the OP-1 understand
    new_d = path.d()
    print(d, "->", new_d)

    text = re.sub(r' d="(.*?)"', ' d="' + new_d + '"', text)
    return text


# Get an attribute value by its name
def get_attr(data, attr_name):
    r = r' ' + re.escape(attr_name) + '="(.*?)"'
    match = re.search(r, data)
    if not match:
        return ""
    return match.group(1)


def delete(data):
    return ""


def remove_tags(data, tag_name):
    data = re.sub(r'<' + tag_name + r'.*?</' + tag_name + r'>', delete, data, flags=re.MULTILINE | re.DOTALL)
    return data


def normalize_svg_str(svg_data):
    # Convert Inkscape ellipses to circles
    svg_data = re.sub(r'(<path .*?sodipodi:type="arc".*?>)', fix_ellipses, svg_data)

    # Normalize paths
    svg_data = re.sub(r'(<path.*? d=".*?>)', fix_paths, svg_data)

    # Convert styles to attributes
    svg_data = re.sub(r'(style=".*?")', fix_styles, svg_data)

    # Remove extra decimals from numbers (maximum is 4)
    svg_data = re.sub(r'\.(\d{5,})', fix_decimals, svg_data)

    # Remove inkscape specific attributes
    svg_data = re.sub(r'[^<]inkscape:.*?".*?"', delete, svg_data)

    # Remove sodipodi attributes
    svg_data = re.sub(r'[^<]sodipodi:.*?=".*?"', delete, svg_data)

    svg_data = re.sub(r'<!--.*?-->', delete, svg_data)

    # Remove useless tags
    svg_data = remove_tags(svg_data, "sodipodi:namedview")
    svg_data = remove_tags(svg_data, "metadata")
    svg_data = remove_tags(svg_data, "defs")

    svg_data = re.sub(" +", " ", svg_data)

    return svg_data


if __name__ == "__main__":
    in_file = sys.argv[1]
    out_file = sys.argv[2]

    print("Optimizing '{}' for OP-1...".format(in_file))

    f = open(in_file)
    data = f.read()
    f.close()

    # Normalize SVG
    data = normalize_svg_str(data)

    print("Saving to '{}'...".format(out_file))
    f = open(out_file, "w")
    f.write(data)
    f.close()

    print("Done.")
