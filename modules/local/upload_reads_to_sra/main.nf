process UPLOAD_READS_TO_SRA {
    tag "$meta.id"
    label 'process_single'
    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    tuple val(meta), path(reads), path(addfiles_xml), path(upload_dir_name)

    output:
    tuple val(meta), path("${meta.library_name}_sra_upload.log.txt")  , emit: upload_log
    tuple val(meta), path("${meta.library_name}_upload_metadata.csv") , emit: upload_metadata
    path "versions.yml"                                               , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    // sra_submission_dir = params.test_upload ? "Test" : "Production"
    sra_submission_dir = "dfornika_bcgsc.ca_37h9i5Qj"
    """

    upload_reads_to_sra.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "\${SRA_UPLOAD_USERNAME}" \\
        --ftp-password "\${SRA_UPLOAD_PASSWORD}" \\
        --remote-path "uploads/${sra_submission_dir}" \\
        --addfiles-xml "${addfiles_xml}" \\
        --upload-dir-name "${upload_dir_name}" \\
        --irida-id "${meta.irida_id}" \\
        --upload-metadata "${meta.library_name}_upload_metadata.csv" \\
        --reads ${reads} \\
        2> >(tee -a ${meta.library_name}_sra_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        upload_reads_to_sra.py : \$(upload_reads_to_sra.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
