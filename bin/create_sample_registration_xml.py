#!/usr/bin/env python

"""Create a Sample Registration XML file."""

import argparse
import csv
import json
import logging
import sys

import xml.etree.ElementTree as ET

from pathlib import Path

logger = logging.getLogger()

def parse_input(input_path: Path):
    """
    Parse input CSV file and return a list of dictionaries.
    
    :param input_path: Path to the CSV file.
    :type input_path: Path
    :return: List of dictionaries representing each row in the CSV.
    :rtype: list[dict[str, str]]
    """
    parsed_input = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed_input.append(row)

    return parsed_input

def convert_to_xml(sample_metadata: dict, fieldname_mapping: dict):
    """
    Convert a CSV file to an XML file in the specified format.
    
    :param sample_metadata: Parsed sample metadata.
    :type sample_metadata: list[dict]
    :param fieldname_mapping: Mapping of XML element tags to sample metadata fieldnames.
    :type fieldname_mapping: dict[str, str]
    """
    root = ET.Element("SAMPLE_SET")
    
    for row in sample_metadata:
        alias_fieldname = fieldname_mapping['sample_alias']
        sample = ET.SubElement(root, "SAMPLE", alias=row[alias_fieldname])
        
        taxon_id_fieldname = fieldname_mapping['taxon_id']
        sample_name = ET.SubElement(sample, "SAMPLE_NAME")
        ET.SubElement(sample_name, "TAXON_ID").text = row[taxon_id_fieldname]
        
        sample_attribute_mapping = {
            "collection_date": "collection date",
            "geographic_location_country": "geographic location (country and/or sea)",
        }
        
        attributes = ET.SubElement(sample, "SAMPLE_ATTRIBUTES")
        for attribute_fieldname, attribute_tag in sample_attribute_mapping.items():
            attribute = ET.SubElement(attributes, "SAMPLE_ATTRIBUTE")
            ET.SubElement(attribute, "TAG").text = attribute_tag
            ET.SubElement(attribute, "VALUE").text = row[attribute_fieldname]

    tree = ET.ElementTree(root)
    
    return tree

def write_output_xml(output_xml_tree, output_xml_path):
    """
    """
    ET.indent(output_xml_tree, space="  ", level=0)
    if output_xml_path:
        output_xml_tree.write(output_xml_path, encoding="utf-8", xml_declaration=True)
    else:
        sys.stdout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        ET.dump(output_xml_tree)


def main(args):
    fieldname_mapping = {
        "sample_alias": args.sample_alias_fieldname,
        "taxon_id": args.taxon_id_fieldname,
        "collection_date": args.collection_date_fieldname,
        "geographic_location_country": args.geographic_location_country_fieldname,
    }
    input_sample_metadata = parse_input(args.input)
    sample_submission_xml_data = convert_to_xml(input_sample_metadata, fieldname_mapping)

    write_output_xml(sample_submission_xml_data, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=Path, help="Input Sample Metadata File.")
    parser.add_argument('--sample-alias-fieldname', type=str, default="sample", help="Fieldname associated with sample alias in input file.")
    parser.add_argument('--taxon-id-fieldname', type=str, default="taxon_id", help="Fieldname associated with sample taxon ID in input file.")
    parser.add_argument('--collection-date-fieldname', type=str, default="collection_date", help="Fieldname associated with sample collection date in input file.")
    parser.add_argument('--geographic-location-country-fieldname', type=str, default="geographic_location_country", help="Fieldname associated with sample collection geographic location (country) in input file.")
    parser.add_argument('-o', '--output', type=Path, help="Output Sample Submission XML File.")
    args = parser.parse_args()
    main(args)