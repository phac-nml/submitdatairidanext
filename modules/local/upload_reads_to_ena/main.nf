process UPLOAD_READS_TO_ENA {
    tag "$meta.id"
    label 'process_single'

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/ena-webin-cli:8.1.1--hdfd78af_1' :
        'biocontainers/ena-webin-cli:8.1.1--hdfd78af_1' }"

    input:
    tuple val(meta), path(reads), path(upload_manifest)

    output:
    tuple val(meta), path("${meta.id}_ena_upload.log.txt")    , emit: upload_log
    tuple val(meta), path("${meta.id}_upload_metadata.csv")   , emit: upload_metadata
    path "versions.yml"                      , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    test_flag = params.test_upload ? "--test-upload" : ""
    """

    upload_reads_to_ena.py \\
        --upload-username "${params.upload_username}" \\
        --upload-password "${params.upload_password}" \\
        --upload-manifest ${upload_manifest} \\
        --input-dir . \\
        ${test_flag} \\
        --upload-metadata ${meta.id}_upload_metadata.csv \\
        2> >(tee -a ${meta.id}_ena_upload.log.txt >&2)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        upload_reads_to_ena.py : \$(upload_reads_to_ena.py --version | awk '{print \$2}')
        ena-webin-cli : 8.1.1
    END_VERSIONS
    """
}
