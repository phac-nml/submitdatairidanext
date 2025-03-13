include { CREATE_ENA_SAMPLE_REGISTRATION_XML} from '../../../modules/local/create_ena_sample_registration_xml'
include { CREATE_ENA_UPLOAD_MANIFEST }        from '../../../modules/local/create_ena_upload_manifest'
include { UPLOAD_TO_ENA }                     from '../../../modules/local/upload_to_ena'

workflow SUBMIT_TO_ENA {
    take:
    input

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, reads -> meta }

    CREATE_ENA_SAMPLE_REGISTRATION_XML(sample_metadata)
    ch_versions = ch_versions.mix(CREATE_ENA_SAMPLE_REGISTRATION_XML.out.versions)

    CREATE_ENA_UPLOAD_MANIFEST(input)
    ch_versions = ch_versions.mix(CREATE_ENA_UPLOAD_MANIFEST.out.versions)

    // Upload process needs some work. The container is currently broken. Waiting on
    // This PR for a fix: https://github.com/bioconda/bioconda-recipes/pull/54548
    // UPLOAD_TO_ENA(input.join(CREATE_ENA_UPLOAD_MANIFEST.out.upload_manifest).view())
    // ch_versions = ch_versions.mix(UPLOAD_TO_ENA.out.versions)

    emit:
    versions = ch_versions                          // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
