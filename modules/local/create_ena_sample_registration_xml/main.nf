process CREATE_ENA_SAMPLE_REGISTRATION_XML {
    tag "$meta.id"
    label 'process_single'

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    val(meta)

    output:
    tuple val(meta), path("*_ena_sample_registration.xml")  , emit: sample_registration_xml
    path "versions.yml"                                 , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    create_ena_sample_registration_xml.py \\
        --sample-alias ${meta.irida_id} \\
        --taxon-id ${meta.taxon_id} \\
        --collection-date ${meta.collection_date} \\
        --geographic-location-country ${meta.country} \\
        --output ${meta.id}_ena_sample_registration.xml

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_ena_sample_registration_xml.py : 0.1.0
    END_VERSIONS
    """
}
