process UPLOAD_CHECKER {
    label 'process_single'

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

    input:
    val failures

    output:
    path("errors.csv")       , emit: error_report

    when:
    task.ext.when == null || task.ext.when

    exec:
    task.workDir.resolve("errors.csv").withWriter { writer ->

        def sample_name = false
        failures.each {
            if ( it[0].id != null) {
                sample_name = true
            }
        }

        // Failures
        if (failures.size() > 0 && sample_name) {
            writer.writeLine("sample,sample_name,success")  // header
            failures.each { writer.writeLine "${it[0].irida_id},${it[0].id},false" }
        } else {
            writer.writeLine("sample,success")  // header
            failures.each { writer.writeLine "${it[0].irida_id},false" }
        }
    }
}
