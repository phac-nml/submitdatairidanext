process CREATE_SRA_UPLOAD_DIR {
    label 'process_single'

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    output:
    path("sra_upload_directory_name.txt") , emit: upload_dir_name
    path "versions.yml"                   , emit: versions

    script:
    // We're temporarily using the sra_user_account_dirname param to control
    // where uploads go to facilitate testing & development.
    // In the future we'll likely revert to using the sra_submission_dir param
    // to control whether uploads go to a test or production area on the SRA FTP server
    // sra_submission_dir = params.test_upload ? "Test" : "Production"
    """
    create_sra_upload_dir.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_USERNAME}" \\
        --ftp-password "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_PASSWORD}" \\
        --remote-path "uploads/${params.sra_user_account_dirname}" \\
        --upload-dir-name "sra_upload_directory_name.txt" \\
        2> >(tee -a sra_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_upload_dir.py : \$(create_sra_upload_dir.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
