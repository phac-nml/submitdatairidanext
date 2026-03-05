process CREATE_SRA_SUBMISSION_XML {
    label 'process_single'

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
        ${addfiles_xmls} \\
        --organization-name ${params.submitter_organization_name} \\
        --output submission.xml

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        create_sra_submission_xml.py : \$(create_sra_submission_xml.py --version | awk '{print \$2}')
    END_VERSIONS
    """
}
