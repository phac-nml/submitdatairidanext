include { CREATE_ENA_SAMPLE_REGISTRATION_XML} from '../../../modules/local/create_ena_sample_registration_xml'
include { CREATE_ENA_UPLOAD_MANIFEST } from '../../../modules/local/create_ena_upload_manifest'

workflow SUBMIT_TO_ENA {
    take:
    input

    main:
    sample_metadata = input.map{ meta, reads -> meta }

    CREATE_ENA_SAMPLE_REGISTRATION_XML(sample_metadata)

    CREATE_ENA_UPLOAD_MANIFEST(input)

    emit:
    // registered_samples = REGISTER_SAMPLE.out...         // channel: [ val(meta), registration_confirmation ]
    versions = CREATE_ENA_SAMPLE_REGISTRATION_XML.out.versions // channel: [ versions.yml ]
}