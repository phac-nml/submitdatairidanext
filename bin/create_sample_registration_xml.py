#!/usr/bin/env python

"""Create a Sample Registration XML file."""

import argparse
import csv
import json
import logging
import sys

import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Optional

logger = logging.getLogger()

def convert_to_xml(sample_metadata: dict):
    """
    Convert a CSV file to an XML file in the specified format.

    :param sample_metadata: Parsed sample metadata.
    :type sample_metadata: dict
    :return: The sample registration XML element tree
    :rtype: ET.ElementTree
    """
    root = ET.Element("SAMPLE_SET")

    
    sample = ET.SubElement(root, "SAMPLE", alias=sample_metadata['sample_alias'])

    sample_name = ET.SubElement(sample, "SAMPLE_NAME")
    ET.SubElement(sample_name, "TAXON_ID").text = sample_metadata['taxon_id']

    sample_attribute_mapping = {
        "collection_date": "collection date",
        "geographic_location_country": "geographic location (country and/or sea)",
    }

    attributes = ET.SubElement(sample, "SAMPLE_ATTRIBUTES")
    for attribute_fieldname, attribute_tag in sample_attribute_mapping.items():
        attribute = ET.SubElement(attributes, "SAMPLE_ATTRIBUTE")
        ET.SubElement(attribute, "TAG").text = attribute_tag
        ET.SubElement(attribute, "VALUE").text = sample_metadata[attribute_fieldname]

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

    input_sample_metadata = {
        "sample_alias": args.sample_alias,
        "taxon_id": args.taxon_id,
        "collection_date": args.collection_date,
        "geographic_location_country": args.geographic_location_country
    }

    sample_submission_xml_data = convert_to_xml(input_sample_metadata)

    write_output_xml(sample_submission_xml_data, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-alias', type=str, help="Sample alias.")
    parser.add_argument('--taxon-id', type=str, default="taxon_id", help="Sample taxon ID.")
    parser.add_argument('--collection-date', type=str, default="collection_date", help="Sample collection date.")
    parser.add_argument('--geographic-location-country', type=str, default="geographic_location_country", help="Sample collection geographic location (country).")
    parser.add_argument('-o', '--output', type=Path, help="Output Sample Submission XML File.")
    args = parser.parse_args()
    main(args)
