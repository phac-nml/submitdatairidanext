#!/usr/bin/env python

"""Create an SRA Submission XML file."""

import argparse
import csv
import json
import logging
import sys

import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Optional

logger = logging.getLogger()

def convert_to_xml():
    """
    Convert a CSV file to an XML file in the specified format.

    :return: The sample registration XML element tree
    :rtype: ET.ElementTree
    """
    root = ET.Element("Submission")

    description = ET.SubElement(root, "Description")

    add_biosample_action = ET.SubElement(root, "Action")

    add_files_action = ET.SubElement(root, "Action")

    tree = ET.ElementTree(root)

    return tree

def write_output_xml(output_xml_tree: ET.ElementTree, output_xml_path: Optional[Path]):
    """
    Write output XML to file (or stdout if no output path provided)
    :param output_xml_tree: XML data to write
    :type output_xml_tree: ET.ElementTree
    :param output_xml_path: Path to write XML file (or print to stdout if None)
    :type output_xml_path: Optional[Path]
    :return: None
    :rtype: None
    """
    ET.indent(output_xml_tree, space="  ", level=0)
    if output_xml_path:
        output_xml_tree.write(output_xml_path, encoding="utf-8", xml_declaration=True)
        with open(output_xml_path, "a") as f:
            f.write('\n')
    else:
        sys.stdout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        ET.dump(output_xml_tree)

def main(args):
    xml_tree = convert_to_xml()
    if args.output:
        output_xml_path = Path(args.output)
    else:
        output_xml_path = None
    write_output_xml(xml_tree, output_xml_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an SRA Submission XML file')
    parser.add_argument('--output', type=str, help='Output file')
    args = parser.parse_args()
    main(args)
