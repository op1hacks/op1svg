#!/usr/bin/env python3

# Quick and dirty tool to bulk analyze SVG files in a directory

import os
import re
import sys
import xml.etree.ElementTree as ET

ET.register_namespace('', "http://www.w3.org/2000/svg")


def get_element_tag_name(elem):
    name = elem.tag
    if "}" in name:
        name = name[name.find("}")+1:]
    return name


def attributes_to_string(attrib):
    s = ""
    for key in attrib:
        s = s + key + "=\"" + attrib[key] + "\" "
    return s.strip()


def element_start_tag_string(elem):
    name = get_element_tag_name(elem)
    return "<" + name + " " + attributes_to_string(elem.attrib) + ">"


def element_end_tag_string(elem):
    name = get_element_tag_name(elem)
    return "</" + name + ">"


def iterate_tree(tree, depth, callback=None):
    depth += 1
    for elem in tree:
        if callback:
            callback(elem)
        # indent = " " * (depth * 2)

        # print(indent + element_start_tag_string(elem))

        if elem.text and elem.text.strip():
            print(elem.text)
        iterate_tree(elem, depth, callback)

        # print(indent + element_end_tag_string(elem))

    depth -= 1


def analyze_element(elem):
    name = get_element_tag_name(elem)
    if name not in tag_names:
        tag_names.append(name)
    for name in elem.attrib:
        if name not in attribute_names:
            attribute_names.append(name)
        if name == "transform":
            transforms.append(elem.attrib[name])
        if name == "d":
            path = elem.attrib[name]
            print(path)
            cmds = re.findall(r"[A-z]", path)
            for cmd in cmds:
                if not cmd in path_commands:
                    path_commands.append(cmd)
            #print(cmds)


def analyze_file(path):
    tree = ET.parse(path)
    root = tree.getroot()

    analyze_element(root)
    iterate_tree(root, 0, analyze_element)


tag_names = []
attribute_names = []
transforms = []
path_commands = []

path = sys.argv[1]
files = os.listdir(path)
print(files)
for f in files:
    if f.startswith("."):
        continue
    print(f)
    fpath = os.path.join(path, f)
    analyze_file(fpath)


print("TAGS")
print(tag_names)
print("ATTRIBUTES")
print(attribute_names)
print("TRANSFORMS")
print(transforms)
print("PATH COMMANDS")
print(path_commands)
