include { CREATE_SRA_ADDFILES_XML}   from '../../../modules/local/create_sra_addfiles_xml'
include { CREATE_SRA_SUBMISSION_XML} from '../../../modules/local/create_sra_submission_xml'
include { UPLOAD_TO_SRA }            from '../../../modules/local/upload_to_sra'

workflow SUBMIT_TO_SRA {
    take:
    input

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, reads -> meta }
    reads = input.map{ meta, reads -> reads }

    CREATE_SRA_ADDFILES_XML(input)
    ch_versions = ch_versions.mix(CREATE_SRA_ADDFILES_XML.out.versions)
    addfiles_xmls = CREATE_SRA_ADDFILES_XML.out.addfiles_xml.map{ meta, addfiles_xml -> addfiles_xml }.collect()
    CREATE_SRA_SUBMISSION_XML(addfiles_xmls)
    ch_versions = ch_versions.mix(CREATE_SRA_SUBMISSION_XML.out.versions)
    collected_reads = reads.collect()
    CREATE_SRA_SUBMISSION_XML.out.submission_xml.set { submission_xml }
    upload_to_sra_input = submission_xml.combine(collected_reads).map { tuple(it[0], it[1..-1]) }
    UPLOAD_TO_SRA(upload_to_sra_input)
    ch_versions = ch_versions.mix(UPLOAD_TO_SRA.out.versions)

    emit:
    versions = ch_versions        // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
