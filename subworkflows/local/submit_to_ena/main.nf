include { CREATE_ENA_UPLOAD_MANIFEST }        from '../../../modules/local/create_ena_upload_manifest'
include { COMBINE_ENA_UPLOAD_MANIFESTS }      from '../../../modules/local/combine_ena_upload_manifests'
include { UPLOAD_TO_ENA }                     from '../../../modules/local/upload_to_ena'

workflow SUBMIT_TO_ENA {
    take:
    input

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, _reads -> meta }
    reads = input.map{ _meta, reads -> reads }

    CREATE_ENA_UPLOAD_MANIFEST(input)
    ch_versions = ch_versions.mix(CREATE_ENA_UPLOAD_MANIFEST.out.versions)

    upload_manifests = CREATE_ENA_UPLOAD_MANIFEST.out.upload_manifest.map{ _meta, upload_manifests -> upload_manifests }.collect()
    COMBINE_ENA_UPLOAD_MANIFESTS(upload_manifests)
    ch_versions = ch_versions.mix(COMBINE_ENA_UPLOAD_MANIFESTS.out.versions)

    collected_reads = reads.collect()
    multi_upload_manifest = COMBINE_ENA_UPLOAD_MANIFESTS.out.multi_upload_manifest
    multi_upload_manifest_with_collected_reads = multi_upload_manifest.combine(collected_reads).map { tuple(it[0], it[1..-1]) }
    UPLOAD_TO_ENA(multi_upload_manifest_with_collected_reads)
    ch_versions = ch_versions.mix(UPLOAD_TO_ENA.out.versions)

    emit:
    versions = ch_versions                          // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
