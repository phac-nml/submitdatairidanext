include { CREATE_ENA_SAMPLE_REGISTRATION_XML} from '../../../modules/local/create_ena_sample_registration_xml'
include { CREATE_ENA_UPLOAD_MANIFEST } from '../../../modules/local/create_ena_upload_manifest'

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

    emit:
    // registered_samples = REGISTER_SAMPLE.out...  // channel: [ val(meta), registration_confirmation ]
    versions = ch_versions                          // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
