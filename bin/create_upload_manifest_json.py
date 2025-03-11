#!/usr/bin/env python

"""Create a Sample Upload Manifest JSON File."""

import argparse
import json
import sys

from pathlib import Path

def main(args):
    instrument_lookup = {
        "miseq": "Illumina MiSeq",
        "hiseq": "Illumina HiSeq",
        "nextseq": "Illumina NextSeq",
        "novaseq": "Illumina NovaSeq",
        "pacbio": "PacBio Sequel II",
        "sanger": "Sanger Sequencing"
    }

    if args.sequencing_instrument.lower() not in instrument_lookup:
        print(f"Invalid sequencing instrument: {args.sequencing_instrument}", file=sys.stderr)
        sys.exit(1)

    # TODO: Complete the following lists with the valid values for each field
    valid_platforms = [
        "illumina", 
    ]
    if args.sequencing_platform.lower() not in valid_platforms:
        print(f"Invalid sequencing platform: {args.sequencing_platform}", file=sys.stderr)
        sys.exit(1)

    valid_library_sources = [
        "genomic",
    ]
    if args.library_source.lower() not in valid_library_sources:
        print(f"Invalid library source: {args.library_source}", file=sys.stderr)
        sys.exit(1)

    valid_library_selections = [
        "random"
    ]
    if args.library_selection.lower() not in valid_library_selections:
        print(f"Invalid library selection: {args.library_selection}", file=sys.stderr)
        sys.exit(1)

    sequencing_instrument = instrument_lookup[args.sequencing_instrument.lower()]

    sample_upload_manifest = {
        "study": args.study_accession,
        "sample": args.sample_accession,
        "name": args.experiment_name,
        "platform": args.sequencing_platform.upper(),
        "instrument": sequencing_instrument,
        "library_name": args.library_name,
        "library_source": args.library_source.upper(),
        "library_selection": args.library_selection.upper(),
        "library_strategy": args.library_strategy.upper(),
        "fastq": [],
    }
    read_type = "paired" if args.fastq2 else "single"
    fastq_1 = {
        "filename": args.fastq1.name,
        "read_type": read_type,
    }
    sample_upload_manifest["fastq"].append(fastq_1)
    if args.fastq2:
        fastq_2 = {
            "filename": args.fastq2.name,
            "read_type": read_type,
        }
        sample_upload_manifest["fastq"].append(fastq_2)
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(sample_upload_manifest, f, indent=4)
    else:
        print(json.dumps(sample_upload_manifest, indent=4))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--study-accession', type=str, help="Registered Study Accession")
    parser.add_argument('--sample-accession', type=str, help="Registered Sample Accession")
    parser.add_argument('--sequencing-platform', type=str, default="illumina", help="Sequencing platform (default: 'illumina')")
    parser.add_argument('--experiment-name', type=str, help="Experiment Name")
    parser.add_argument('--sequencing-instrument', type=str, default="miseq", help="Sequencing platform (default: 'miseq')")
    parser.add_argument('--library-name', type=str, help="Library Name")
    parser.add_argument('--library-source', type=str, default="genomic", help="Library Source (default: 'genomic')")
    parser.add_argument('--library-selection', type=str, default="random", help="Library Selection (default: 'random')")
    parser.add_argument('--library-strategy', type=str, default="wgs", help="Library Strategy (default: 'wgs')")
    parser.add_argument('--fastq1', type=Path, required=True, help="Path to FASTQ file 1")
    parser.add_argument('--fastq2', type=Path, help="Path to FASTQ file 2")
    parser.add_argument('-o', '--output', type=Path, help="Output Sample Upload Manifest JSON File.")
    args = parser.parse_args()
    main(args)
