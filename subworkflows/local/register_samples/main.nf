include { CREATE_SAMPLE_REGISTRATION_XML} from '../../../modules/local/create_sample_registration_xml'

workflow REGISTER_SAMPLES {
    take:
    sample_metadata

    main:
    CREATE_SAMPLE_REGISTRATION_XML(sample_metadata)

    emit:
    // registered_samples = REGISTER_SAMPLE.out...         // channel: [ val(meta), registration_confirmation ]
    versions = CREATE_SAMPLE_REGISTRATION_XML.out.versions // channel: [ versions.yml ]
}
