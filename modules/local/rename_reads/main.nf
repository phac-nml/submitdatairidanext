process RENAME_READS {
    tag "$meta.id"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/coreutils%3A8.31--h14c3975_0' :
        'biocontainers/coreutils:8.31--h14c3975_0' }"

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
