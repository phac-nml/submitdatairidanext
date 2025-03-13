include { CREATE_UPLOAD_MANIFEST } from '../../../modules/local/create_upload_manifest'

workflow UPLOAD_READS {
    take:
    input

    main:
    CREATE_UPLOAD_MANIFEST(input)

    emit:
    // upload_manifest = CREATE_UPLOAD_MANIFEST.out...         // channel: [ val(meta), upload_manifest ]
    versions = CREATE_UPLOAD_MANIFEST.out.versions // channel: [ versions.yml ]
}
