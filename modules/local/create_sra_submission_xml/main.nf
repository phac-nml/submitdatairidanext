process CREATE_SRA_SUBMISSION_XML {
    label 'process_single'

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    path(addfiles_xmls)

    output:
    path("submission.xml")  , emit: submission_xml
    path "versions.yml"     , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    create_sra_submission_xml.py \\
        ./*_sra_addfiles.xml \\
        --output submission.xml

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_submission_xml.py : 0.1.0
    END_VERSIONS
    """
}
