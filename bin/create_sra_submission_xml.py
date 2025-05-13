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

def parse_addfiles_xml(addfiles_xml_path: Path) -> ET.ElementTree:
    """
    Parse an AddFiles XML file and return the root element.

    :param addfiles_xml_path: Path to the AddFiles XML file
    :type addfiles_xml_path: str
    :return: The root element of the AddFiles XML file
    :rtype: ET.ElementTree
    """
    tree = None
    try:
        tree = ET.parse(addfiles_xml_path)
    except ET.ParseError as e:
        logger.error(f"Error parsing {addfiles_xml_path}: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {addfiles_xml_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred while parsing {addfiles_xml_path}: {e}")
        sys.exit(1)

    return tree

def build_submission_xml(addfiles_trees: list[ET.ElementTree]) -> ET.ElementTree:
    """
    Convert a dictionary of submission data to an XML element tree.

    :param submission_data: The submission data
    :type submission_data: dict
    :return: The sample registration XML element tree
    :rtype: ET.ElementTree
    """
    root = ET.Element("Submission")

    action_element = ET.SubElement(root, "Action")
    for addfiles_tree in addfiles_trees:
        action_element.append(addfiles_tree.getroot())

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
        output_xml_tree.write(output_xml_path, encoding="utf-8", xml_declaration=False)
        with open(output_xml_path, "a") as f:
            f.write('\n')
    else:
        ET.dump(output_xml_tree)

def main(args):

    addfiles_trees = []
    for addfiles_xml in args.addfiles_xmls:
        addfiles_tree = parse_addfiles_xml(addfiles_xml)
        addfiles_trees.append(addfiles_tree)

    # Combine the AddFiles XML files into a single XML tree
    submission_tree = build_submission_xml(addfiles_trees)

    if args.output:
        output_xml_path = Path(args.output)
    else:
        output_xml_path = None
    write_output_xml(submission_tree, output_xml_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an SRA Submission XML file by combining AddFiles XML files')
    parser.add_argument('addfiles_xmls', type=str, nargs='+', help='AddFiles XML files')
    parser.add_argument('--output', type=str, help='Output file')
    args = parser.parse_args()
    main(args)
