process CREATE_SRA_SUBMISSION_XML {
    tag "$meta.id"
    label 'process_single'

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*_sra_submission.xml")  , emit: submission_xml
    path "versions.yml"                            , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    create_sra_submission_xml.py \\
        --study-accession ${params.bioproject_accession} \\
        --library-name "" \\
        --fastq1 ${reads[0]} \\
        --fastq2 ${reads[1]} \\
        --output ${meta.id}_sra_submission.xml

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_submission_xml.py : 0.1.0
    END_VERSIONS
    """
}
