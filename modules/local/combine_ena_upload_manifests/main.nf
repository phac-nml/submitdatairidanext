process COMBINE_ENA_UPLOAD_MANIFESTS {
    label 'process_single'

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    path(upload_manifests)

    output:
    path("multi_upload_manifest.json")  , emit: multi_upload_manifest
    path "versions.yml"                 , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    combine_ena_upload_manifests.py \\
        ./*_ena_upload_manifest.json \\
        --output multi_upload_manifest.json
        

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        combine_ena_upload_manifests.py : 0.1.0
    END_VERSIONS
    """
}