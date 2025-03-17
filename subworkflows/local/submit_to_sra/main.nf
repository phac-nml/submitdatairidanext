include { CREATE_SRA_SUBMISSION_XML} from '../../../modules/local/create_sra_submission_xml'
include { UPLOAD_TO_SRA }            from '../../../modules/local/upload_to_sra'

workflow SUBMIT_TO_SRA {
    take:
    input

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, reads -> meta }

    CREATE_SRA_SUBMISSION_XML(input)
    ch_versions = ch_versions.mix(CREATE_SRA_SUBMISSION_XML.out.versions)

    // Temorarily disable the upload process while further testing and development is done
    // UPLOAD_TO_SRA(input.join(CREATE_SRA_SUBMISSION_XML.out.submission_xml).view())
    // ch_versions = ch_versions.mix(UPLOAD_TO_SRA.out.versions)

    emit:
    versions = ch_versions        // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
