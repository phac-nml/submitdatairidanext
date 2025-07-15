include { CREATE_SRA_UPLOAD_DIR }    from '../../../modules/local/create_sra_upload_dir'
include { CREATE_SRA_ADDFILES_XML}   from '../../../modules/local/create_sra_addfiles_xml'
include { CREATE_SRA_SUBMISSION_XML} from '../../../modules/local/create_sra_submission_xml'
include { UPLOAD_READS_TO_SRA }      from '../../../modules/local/upload_reads_to_sra'
include { COMPLETE_SRA_UPLOAD }      from '../../../modules/local/complete_sra_upload'
include { UPLOAD_CHECKER }           from '../../../modules/local/upload_checker'

workflow SUBMIT_TO_SRA {
    take:
    input // channel: [ val(meta), path(reads) ]

    main:
    ch_versions = Channel.empty()
    sample_metadata = input.map{ meta, _reads -> meta }

    // We'll upload all reads into a single timestamped directory
    // So we'll create the upload directory first and
    // Pass its name to the upload process
    CREATE_SRA_UPLOAD_DIR()
    upload_dir_name = CREATE_SRA_UPLOAD_DIR.out.upload_dir_name

    CREATE_SRA_ADDFILES_XML(input)
    ch_versions = ch_versions.mix(CREATE_SRA_ADDFILES_XML.out.versions)

    addfiles_xmls = CREATE_SRA_ADDFILES_XML.out.addfiles_xml
    upload_inputs = input.join(addfiles_xmls).combine(upload_dir_name)
    UPLOAD_READS_TO_SRA(upload_inputs)
    ch_versions = ch_versions.mix(UPLOAD_READS_TO_SRA.out.versions)

    all_uploads = sample_metadata.join(UPLOAD_READS_TO_SRA.out.upload_metadata, remainder: true)
    completed_uploads = all_uploads.filter{ it[1] != null }
    failed_uploads = all_uploads.filter{ it[1] == null }.toList()

    // Only addfiles.xml files from completed uploads
    // will be used to create the submission XML
    collected_addfiles_xmls = CREATE_SRA_ADDFILES_XML.out.addfiles_xml.join(completed_uploads).map{ _meta, addfiles_xml, _upload_metadata -> addfiles_xml }.collect()
    CREATE_SRA_SUBMISSION_XML(collected_addfiles_xmls)
    ch_versions = ch_versions.mix(CREATE_SRA_SUBMISSION_XML.out.versions)

    submission_xml = CREATE_SRA_SUBMISSION_XML.out.submission_xml
    COMPLETE_SRA_UPLOAD(submission_xml.combine(upload_dir_name))
    ch_versions = ch_versions.mix(COMPLETE_SRA_UPLOAD.out.versions)

    UPLOAD_CHECKER(failed_uploads)

    emit:
    versions = ch_versions        // channel: [ process_1_versions.yml, process_2_versions.yml, ... ]
}
