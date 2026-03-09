process CREATE_ENA_UPLOAD_MANIFEST {
    tag "$meta.id"
    label 'process_single'

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*_ena_upload_manifest.json")  , emit: upload_manifest
    path "versions.yml"                                  , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    create_ena_upload_manifest_json.py \\
        --study-accession "${meta.bioproject_accession}" \\
        --sample-accession "${meta.biosample_accession}" \\
        --experiment-name "${meta.bioproject_accession}-${meta.platform}-${meta.id}" \\
        --library-name "${meta.library_name}" \\
        --library-source "${meta.library_source}" \\
        --library-strategy "${meta.library_strategy}" \\
        --library-selection "${meta.library_selection}" \\
        --platform "${meta.platform}" \\
        --instrument-model "${meta.instrument_model}" \\
        --fastq1 ${reads[0]} \\
        --fastq2 ${reads[1]} \\
        --output ${meta.library_name}_ena_upload_manifest.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_ena_upload_manifest_json.py : 0.1.0
    END_VERSIONS
    """
}
