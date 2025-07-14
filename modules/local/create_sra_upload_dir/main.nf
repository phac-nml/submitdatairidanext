process CREATE_SRA_UPLOAD_DIR {
    label 'process_single'
    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    output:
    path("sra_upload_directory_name.txt") , emit: upload_dir_name

    script:
    sra_submission_dir = params.test_upload ? "Test" : "Production"
    """
    create_sra_upload_dir.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "${params.upload_username}" \\
        --ftp-password "${params.upload_password}" \\
        --remote-path "submit/${sra_submission_dir}" \\
        --upload-dir-name "sra_upload_directory_name.txt" \\
        2> >(tee -a sra_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_upload_dir.py : 0.1.0
    END_VERSIONS
    """
}