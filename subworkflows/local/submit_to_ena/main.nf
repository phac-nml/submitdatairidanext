include { CREATE_ENA_UPLOAD_MANIFEST }   from '../../../modules/local/create_ena_upload_manifest'
include { UPLOAD_READS_TO_ENA }          from '../../../modules/local/upload_reads_to_ena'
include { UPLOAD_CHECKER }           from '../../../modules/local/upload_checker'

workflow SUBMIT_TO_ENA {
    take:
    input // channel: [ val(meta), path(reads) ]

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, _reads -> meta }
    reads = input.map{ _meta, reads -> reads }

    upload_manifest = CREATE_ENA_UPLOAD_MANIFEST(input).upload_manifest
    ch_versions = ch_versions.mix(CREATE_ENA_UPLOAD_MANIFEST.out.versions)

    UPLOAD_READS_TO_ENA(input.join(upload_manifest))
    ch_versions = ch_versions.mix(UPLOAD_READS_TO_ENA.out.versions)

    all_uploads = sample_metadata.join(UPLOAD_READS_TO_ENA.out.upload_metadata, remainder: true)
    completed_uploads = all_uploads.filter{ it[1] != null }
    failed_uploads = all_uploads.filter{ it[1] == null }.toList()

    UPLOAD_CHECKER(failed_uploads)

    emit:
    versions = ch_versions         // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
