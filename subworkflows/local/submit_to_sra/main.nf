include { CREATE_SRA_UPLOAD_DIR }    from '../../../modules/local/create_sra_upload_dir'
include { CREATE_SRA_ADDFILES_XML}   from '../../../modules/local/create_sra_addfiles_xml'
include { CREATE_SRA_SUBMISSION_XML} from '../../../modules/local/create_sra_submission_xml'
include { UPLOAD_READS_TO_SRA }      from '../../../modules/local/upload_reads_to_sra'
include { COMPLETE_SRA_UPLOAD }      from '../../../modules/local/complete_sra_upload'

workflow SUBMIT_TO_SRA {
    take:
    input

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, _reads -> meta }
    reads = input.map{ _meta, reads -> reads }

    CREATE_SRA_UPLOAD_DIR()
    upload_dir_name = CREATE_SRA_UPLOAD_DIR.out.upload_dir_name

    CREATE_SRA_ADDFILES_XML(input)
    ch_versions = ch_versions.mix(CREATE_SRA_ADDFILES_XML.out.versions)

    collected_addfiles_xmls = CREATE_SRA_ADDFILES_XML.out.addfiles_xml.map{ _meta, addfiles_xml -> addfiles_xml }.collect()
    CREATE_SRA_SUBMISSION_XML(collected_addfiles_xmls)
    ch_versions = ch_versions.mix(CREATE_SRA_SUBMISSION_XML.out.versions)

    submission_xml = CREATE_SRA_SUBMISSION_XML.out.submission_xml

    addfiles_xmls = CREATE_SRA_ADDFILES_XML.out.addfiles_xml
    UPLOAD_READS_TO_SRA(input.join(addfiles_xmls).combine(upload_dir_name))
    ch_versions = ch_versions.mix(UPLOAD_READS_TO_SRA.out.versions)

    COMPLETE_SRA_UPLOAD(submission_xml.combine(upload_dir_name))
    ch_versions = ch_versions.mix(COMPLETE_SRA_UPLOAD.out.versions)

    emit:
    versions = ch_versions        // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
