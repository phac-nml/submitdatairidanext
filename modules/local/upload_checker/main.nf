process UPLOAD_CHECKER {
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/coreutils%3A8.31--h14c3975_0' :
        'biocontainers/coreutils:8.31--h14c3975_0' }"

    input:
    val failures

    output:
    path("errors.csv")       , emit: error_report

    when:
    task.ext.when == null || task.ext.when

    exec:
    task.workDir.resolve("errors.csv").withWriter { writer ->
        def destination_lower = params.destination.toLowerCase()
        writer.writeLine("sample,sample_name,success,message")  // header
        failures.findAll{ it[0] != null }.each { writer.writeLine "${it[0].irida_id},${it[0].library_name},false,Upload failed" }
    }
}
