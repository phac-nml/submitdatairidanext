process APPEND_ERRORS_TO_UPLOAD_METADATA {
    label 'process_single'

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    tuple path(upload_metadata), path(errors_csv)

    output:
    path("metadata.json") , emit: metadata_json
    path "versions.yml"   , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    append_errors_to_upload_metadata.py \\
        --destination "${params.destination}" \\
        --errors "${errors_csv}" \\
        --upload-metadata "${upload_metadata}" \\
        > metadata.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        append_errors_to_upload_metadata.py : \$(append_errors_to_upload_metadata.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
