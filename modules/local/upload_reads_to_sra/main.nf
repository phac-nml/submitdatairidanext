process UPLOAD_READS_TO_SRA {
    tag "$meta.id"
    label 'process_single'

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'oras://community.wave.seqera.io/library/paramiko:4.0.0--3788dfafc81b25dc' :
        task.ext.override_configured_container_registry != false ?
        'community.wave.seqera.io/library/paramiko:4.0.0--8a888bf2e2712e98' :
        'library/paramiko:4.0.0--8a888bf2e2712e98' }"

    input:
    tuple val(meta), path(reads), path(addfiles_xml), path(upload_dir_name)

    output:
    tuple val(meta), path("${meta.library_name}_sra_upload.log.txt")  , emit: upload_log
    tuple val(meta), path("${meta.library_name}_upload_metadata.csv") , emit: upload_metadata
    path "versions.yml"                                               , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    sra_top_submission_dir = params.sra_account_type == "center" ? "submit" : "uploads"
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

    upload_reads_to_sra.py \\
        --ftp-server "${params.sra_ftp_server}" \\
        --ftp-user "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_USERNAME}" \\
        --ftp-password "\${SUBMITDATAIRIDANEXT_SRA_UPLOAD_PASSWORD}" \\
        --remote-path "${sra_top_submission_dir}/${sra_submission_subdir}" \\
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
