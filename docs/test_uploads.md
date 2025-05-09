# Setting Up Test Uploads

Before submitting data to the SRA or ENA, one might want to perform test uploads to confirm that the pipeline is working appropriately. There are a few ways
to perform this sort of test. Some of them may require up-front coordination with the SRA or ENA admin teams.

# Testing SRA Uploads with a local FTP server

Since the SRA upload process is based on FTP, we can simulate the upload process by directing our uploads to a local FTP server (or some other FTP server under our control).
We can then use a custom script to simulate the process that occurs on the SRA servers in response to new uploads, and confirm that the pipeline behaves as expected.

When running a test upload using this method, we must provide the hostname of the FTP server we want to direct our uploads to with the `--sra_ftp_server` flag. If we're running the
FTP server on the same system where the pipeline is being tested, then the value would be `localhost`.

# Testing ENA Uploads using Webin-cli test mode

The ENA provides a dedicated tool called `ena-webin-cli` for performing uploads. That tool offers a test mode
