workflow SUBMIT_TO_SRA {
    take:
    input

    main:
    sample_metadata = input.map{ meta, reads -> meta }

    emit:
    // registered_samples = REGISTER_SAMPLE.out...         // channel: [ val(meta), registration_confirmation ]
    versions = null
}
