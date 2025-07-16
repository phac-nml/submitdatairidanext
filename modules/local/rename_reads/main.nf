process RENAME_READS {
    tag "$meta.id"
    label 'process_single'

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("${meta.library_name}_R*.f*q*"), emit: renamed_reads

    script:
    """
    # Rename reads to match the library name
    # Check file types and rename accordingly
    if [[ ${reads[0]} == *.gz ]]; then
        mv ${reads[0]} ${meta.library_name}_R1.fastq.gz
    else
        mv ${reads[0]} ${meta.library_name}_R1.fastq
    fi

    if [[ ${reads[1]} == *.gz ]]; then
        mv ${reads[1]} ${meta.library_name}_R2.fastq.gz
    else
        mv ${reads[1]} ${meta.library_name}_R2.fastq
    fi
    """
}
