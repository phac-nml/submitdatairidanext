process CREATE_SRA_UPLOAD_DIR {
    label 'process_single'

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    output:
    path("sra_upload_directory_name.txt") , emit: upload_dir_name
    path "versions.yml"                   , emit: versions

    script:
    sra_submission_dir = params.test_upload ? "Test" : "Production"
    """
    create_sra_upload_dir.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "\${SRA_UPLOAD_USERNAME}" \\
        --ftp-password "\${SRA_UPLOAD_PASSWORD}" \\
        --remote-path "uploads/${params.sra_user_account_dirname}" \\
        --upload-dir-name "sra_upload_directory_name.txt" \\
        2> >(tee -a sra_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_upload_dir.py : \$(create_sra_upload_dir.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
