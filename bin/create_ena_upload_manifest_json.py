#!/usr/bin/env python

"""Create a Sample Upload Manifest JSON File."""

import argparse
import json
import sys

from pathlib import Path

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

    if args.sequencing_instrument.lower() not in instrument_lookup:
        print(f"Invalid sequencing instrument: {args.sequencing_instrument}", file=sys.stderr)
        sys.exit(1)

    sequencing_instrument = instrument_lookup[args.sequencing_instrument.lower()]

    sample_upload_manifest = {
        "study": args.study_accession,
        "sample": args.sample_accession,
        "platform": args.sequencing_platform,
        "instrument": sequencing_instrument,
        "library_name": args.library_name,
        "library_source": args.library_source,
        "library_selection": args.library_selection,
        "library_strategy": args.library_strategy,
        "fastq": [],
    }

    if args.experiment_name:
        sample_upload_manifest["name"] = args.experiment_name

    read_type = "paired" if args.fastq2 else "single"
    fastq_1 = {
        "value": args.fastq1.name,
        "attributes": {
            "read_type": read_type,
        },
    }
    sample_upload_manifest["fastq"].append(fastq_1)
    if args.fastq2:
        fastq_2 = {
            "value": args.fastq2.name,
            "attributes": {
                "read_type": read_type,
            },
        }
        sample_upload_manifest["fastq"].append(fastq_2)
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(sample_upload_manifest, f, indent=4)
            f.write('\n')
    else:
        print(json.dumps(sample_upload_manifest, indent=4))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--study-accession', type=str, help="Registered Study Accession")
    parser.add_argument('--sample-accession', type=str, help="Registered Sample Accession")
    parser.add_argument('--sequencing-platform', type=str, default="ILLUMINA", help="Sequencing platform (default: 'ILLUMINA')")
    parser.add_argument('--experiment-name', type=str, help="Experiment Name")
    parser.add_argument('--sequencing-instrument', type=str, default="MISEQ", help="Sequencing platform (default: 'MISEQ')")
    parser.add_argument('--library-name', type=str, help="Library Name")
    parser.add_argument('--library-source', type=str, default="GENOMIC", help="Library Source (default: 'GENOMIC')")
    parser.add_argument('--library-selection', type=str, default="RANDOM", help="Library Selection (default: 'RANDOM')")
    parser.add_argument('--library-strategy', type=str, default="WGS", help="Library Strategy (default: 'WGS')")
    parser.add_argument('--fastq1', type=Path, required=True, help="Path to FASTQ file 1")
    parser.add_argument('--fastq2', type=Path, help="Path to FASTQ file 2")
    parser.add_argument('-o', '--output', type=Path, help="Output Sample Upload Manifest JSON File.")
    args = parser.parse_args()
    main(args)
