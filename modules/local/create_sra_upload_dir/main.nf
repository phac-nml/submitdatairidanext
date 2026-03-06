process CREATE_SRA_UPLOAD_DIR {
    label 'process_single'

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'oras://community.wave.seqera.io/library/paramiko:4.0.0--3788dfafc81b25dc' :
        'community.wave.seqera.io/library/paramiko:4.0.0--8a888bf2e2712e98' }"

    output:
    path("sra_upload_directory_name.txt") , emit: upload_dir_name
    path "versions.yml"                   , emit: versions

    script:
    sra_top_submission_dir = params.sra_account_type.toString().equalsIgnoreCase("center") ? "submit" : "uploads"
    def sra_submission_subdir;
    if (params.sra_account_type == "center") {
        if (params.test_upload) {
            sra_submission_subdir = "Test"
        } else {
            sra_submission_subdir = "Production"
        }
    } else {
        sra_submission_subdir = params.sra_user_account_dirname
    }
    """
    create_sra_upload_dir.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_USERNAME}" \\
        --ftp-password "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_PASSWORD}" \\
        --remote-path "${sra_top_submission_dir}/${sra_submission_subdir}" \\
        --upload-dir-name "sra_upload_directory_name.txt" \\
        --upload-dir-suffix "${params.upload_dir_suffix}" \\
        2> >(tee -a sra_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_upload_dir.py : \$(create_sra_upload_dir.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
