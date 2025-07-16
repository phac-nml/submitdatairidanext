process UPLOAD_CHECKER {
    label 'process_single'

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
        failures.each { writer.writeLine "${it[0].irida_id},${it[0].library_name},false,Upload failed" }
    }
}
