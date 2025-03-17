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

def convert_to_xml(submission_data: dict) -> ET.ElementTree:
    """
    Convert a dictionary of submission data to an XML element tree.

    :param submission_data: The submission data
    :type submission_data: dict
    :return: The sample registration XML element tree
    :rtype: ET.ElementTree
    """
    root = ET.Element("Submission")

    description = ET.SubElement(root, "Description")

    add_biosample_action = ET.SubElement(root, "Action")
    add_biosample_data_element = ET.SubElement(add_biosample_action, "AddData", {"target_db": "Biosample"})

    add_files_action = ET.SubElement(root, "Action")
    add_files_element = ET.SubElement(add_files_action, "AddFiles" , {"target_db": "SRA"})

    bioproject_attribute_ref_id_element = ET.SubElement(add_files_element, "AttributeRefId", {"name": "BioProject"})
    bioproject_attribute_ref_id_container_element = ET.SubElement(bioproject_attribute_ref_id_element, "RefId")
    bioproject_primary_id_element = ET.SubElement(bioproject_attribute_ref_id_container_element, "PrimaryId", {"db": "BioProject"})
    bioproject_primary_id_element.text = submission_data['bioproject_accession']

    biosample_attribute_ref_id_element = ET.SubElement(add_files_element, "AttributeRefId", {"name": "BioSample"})
    biosample_attribute_ref_id_container_element = ET.SubElement(biosample_attribute_ref_id_element, "RefId")
    biosample_spuid_element = ET.SubElement(biosample_attribute_ref_id_container_element, "SPUID", {"spuid_namespace": "**TODO**"}) # TODO: Determine how to supply SPUID namespace
    for fastq in submission_data['sequenced_library_attributes']["fastq_files"]:
        add_file_element = ET.SubElement(add_files_element, "File", {"file_path": fastq["filename"]})
        data_type_element = ET.SubElement(add_file_element, "DataType")
        data_type_element.text = "generic-data"

    excluded_attributes = ["fastq_files"]
    for attribute_name, attribute_value in submission_data['sequenced_library_attributes'].items():
        if attribute_name not in excluded_attributes:
            attribute_element = ET.SubElement(add_biosample_data_element, "Attribute", {"name": attribute_name})
            attribute_element.text = attribute_value

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

    if args.fastq2 == 'null':
        args.fastq2 = None

    instrument_lookup = {
        "miseq": "Illumina MiSeq",
        "hiseq": "Illumina HiSeq",
        "nextseq": "Illumina NextSeq",
        "novaseq": "Illumina NovaSeq",
        "pacbio": "PacBio Sequel II",
        "sanger": "Sanger Sequencing"
    }
    sequencing_instrument = instrument_lookup.get(args.sequencing_instrument.lower())
    if not sequencing_instrument:
        logger.error(f"Invalid sequencing instrument: {args.sequencing_instrument}")
        sys.exit(1)

    sample_submission = {
        "bioproject_accession": args.study_accession,
        "platform": args.sequencing_platform.upper(),
        "biosample_attributes": {

        },
        "sequenced_library_attributes": {
            "instrument_model": sequencing_instrument,
            "library_name": args.library_name,
            "library_source": args.library_source.upper(),
            "library_selection": args.library_selection.upper(),
            "library_strategy": args.library_strategy.upper(),
            "library_layout": "PAIRED" if args.fastq2 else "SINGLE",
            "fastq_files": [],
        },
    }
    read_type = "paired" if args.fastq2 else "single"
    fastq_1 = {
        "filename": args.fastq1.name,
        "read_type": read_type,
    }
    sample_submission['sequenced_library_attributes']["fastq_files"].append(fastq_1)
    if args.fastq2:
        fastq_2 = {
            "filename": args.fastq2.name,
            "read_type": read_type,
        }
        sample_submission['sequenced_library_attributes']['fastq_files'].append(fastq_2)

    xml_tree = convert_to_xml(sample_submission)

    if args.output:
        output_xml_path = Path(args.output)
    else:
        output_xml_path = None
    write_output_xml(xml_tree, output_xml_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an SRA Submission XML file')
    parser.add_argument('--study-accession', type=str, required=True, help="BioProject Accession")
    parser.add_argument('--sequencing-platform', type=str, default="illumina", help="Sequencing Platform (default: 'illumina')")
    parser.add_argument('--sequencing-instrument', type=str, default="miseq", help="Sequencing instrument (default: 'miseq')")
    parser.add_argument('--library-name', type=str, help="Library Name")
    parser.add_argument('--library-source', type=str, default="genomic", help="Library Source (default: 'genomic')")
    parser.add_argument('--library-selection', type=str, default="random", help="Library Selection (default: 'random')")
    parser.add_argument('--library-strategy', type=str, default="wgs", help="Library Strategy (default: 'wgs')")
    parser.add_argument('--fastq1', type=Path, required=True, help="Path to FASTQ file 1")
    parser.add_argument('--fastq2', type=Path, help="Path to FASTQ file 2")
    parser.add_argument('--output', type=str, help='Output file')
    args = parser.parse_args()
    main(args)
