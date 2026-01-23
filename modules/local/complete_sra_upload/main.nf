process COMPLETE_SRA_UPLOAD {
    label 'process_single'

    // biobb_remote is a lightweight container that includes paramiko.
    // preferably switch to paramiko-specific container
    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biobb_remote:1.2.2--pyhdfd78af_0' :
        'biocontainers/biobb_remote:1.2.2--pyhdfd78af_0' }"

    input:
    tuple path(submission_xml), path(upload_dir_name)

    output:
    path("sra_upload.log.txt")  , emit: upload_log
    path "versions.yml"         , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    // We're temporarily using the sra_user_account_dirname param to control
    // where uploads go to facilitate testing & development.
    // In the future we'll likely revert to using the sra_submission_dir param
    // to control whether uploads go to a test or production area on the SRA FTP server
    // sra_submission_dir = params.test_upload ? "Test" : "Production"
    """

    complete_sra_upload.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_USERNAME}" \\
        --ftp-password "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_PASSWORD}" \\
        --remote-path "uploads/${params.sra_user_account_dirname}" \\
        --submission-xml "${submission_xml}" \\
        --upload-dir-name "${upload_dir_name}" \\
        2> >(tee -a sra_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        complete_sra_upload.py : \$(complete_sra_upload.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
