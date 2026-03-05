process CHECK_BIOSAMPLE_EXISTS {
    label 'process_single'

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'oras://community.wave.seqera.io/library/requests:2.32.5--3f6129b86a9344fc' :
        'community.wave.seqera.io/library/requests:2.32.5--734a8dc164d0c716' }"

    input:
    tuple val(meta), path(reads)

    output:
    path("biosample_exists.csv")  , emit: biosample_exists

    script:
    """
    check_biosample_exists.py
    """
}
