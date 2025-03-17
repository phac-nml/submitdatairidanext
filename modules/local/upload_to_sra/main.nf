process UPLOAD_TO_SRA {
    tag "$meta.id"

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    tuple val(meta), path(reads), path(submission_xml)

    output:
    tuple val(meta), path("${meta.id}_sra_upload.log.txt")  , emit: sra_upload_log
    path "versions.yml"                                     , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """

    upload_to_sra.py \\
        --ftp-user ${params.upload_username} \\
        --ftp-password ${params.upload_password} \\
        --remote-path "" \\
        ${submission_xml} \\
        ${reads} \\
        > ${meta.id}_sra_upload.log.txt

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        upload_to_sra.py : 0.1.0
    END_VERSIONS
    """
}
