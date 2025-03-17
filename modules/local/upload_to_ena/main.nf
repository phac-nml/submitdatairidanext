process UPLOAD_TO_ENA {
    tag "$meta.id"

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/ena-webin-cli:8.1.1--hdfd78af_1' :
        'biocontainers/ena-webin-cli:8.1.1--hdfd78af_1' }"

    input:
    tuple val(meta), path(reads), path(upload_manifest)

    output:
    tuple val(meta), path("${meta.id}_webin_validation_result.txt")  , emit: webin_validation_result
    path "versions.yml"                                              , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    # Temporarily only performing validation here
    # So we can test/develop without performing any actual uploads.

    ena-webin-cli \\
        -context reads \\
        -userName ${params.upload_username} \\
        -password ${params.upload_password} \\
        -manifest ${upload_manifest} \\
        -inputDir . \\
        -validate \\
        > ${meta.id}_webin_validation_result.txt

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        ena-webin-cli : 8.1.1
    END_VERSIONS
    """
}
