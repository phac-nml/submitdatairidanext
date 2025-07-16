include { RENAME_READS }                     from '../../../modules/local/rename_reads'
include { CREATE_ENA_UPLOAD_MANIFEST }       from '../../../modules/local/create_ena_upload_manifest'
include { UPLOAD_READS_TO_ENA }              from '../../../modules/local/upload_reads_to_ena'
include { UPLOAD_CHECKER }                   from '../../../modules/local/upload_checker'
include { APPEND_ERRORS_TO_UPLOAD_METADATA } from '../../../modules/local/append_errors_to_upload_metadata'

workflow SUBMIT_TO_ENA {
    take:
    input // channel: [ val(meta), path(reads) ]

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, _reads -> meta }

    RENAME_READS(input)
    renamed_reads = RENAME_READS.out.renamed_reads

    upload_manifest = CREATE_ENA_UPLOAD_MANIFEST(renamed_reads).upload_manifest
    ch_versions = ch_versions.mix(CREATE_ENA_UPLOAD_MANIFEST.out.versions)

    UPLOAD_READS_TO_ENA(renamed_reads.join(upload_manifest))
    ch_versions = ch_versions.mix(UPLOAD_READS_TO_ENA.out.versions)

    all_uploads = sample_metadata.join(UPLOAD_READS_TO_ENA.out.upload_metadata, remainder: true)
    // Not currently using completed_uploads channel but could be useful for future extensions
    // completed_uploads = all_uploads.filter{ it[1] != null }
    failed_uploads = all_uploads.filter{ it[1] == null }.toList()

    UPLOAD_CHECKER(failed_uploads)
    error_report = UPLOAD_CHECKER.out.error_report
    collected_upload_metadata_files = UPLOAD_READS_TO_ENA.out.upload_metadata.map{ it -> it[1] }.collect()
    APPEND_ERRORS_TO_UPLOAD_METADATA(collected_upload_metadata_files.combine(error_report))
    ch_versions = ch_versions.mix(APPEND_ERRORS_TO_UPLOAD_METADATA.out.versions)

    emit:
    versions = ch_versions         // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
