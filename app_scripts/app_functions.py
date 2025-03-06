import re
from playwright.sync_api import Playwright, expect
import subprocess


# CREATING CERT FILE
def create_cert(
        url: str,
        user: str,
        password: str,
        csr_file: str,
        template: str,
        cn: str,
        cer_ext: str,
        path_to_save_cer: str,
        playwright: Playwright
) -> str:
    """
    (CA server, Playwright)Create certificate via MS CA server

    :param url: url of PKI server
    :param user: username to auth on PKI server
    :param password: password to auth on PKI server
    :param csr_file: full path to csr file
    :param template: template name to use for PKI
    :param cn: cn to use in result cert name
    :param cer_ext: certificate extension
    :param path_to_save_cer: str, downloads dir for certs
    :param playwright: Playwright object
    :return: str, cert's download path(relative)

    req example:
        {'Title': 'RP1706597',
        'ServiceCall': 'serviceCall$593989602',
         'Cert Type': 'Внутренний сертификат',
         'Cert Format': '*.cer/*.crt', # OR may be '*.pem'
         'Template': 'SSL',
         'Domain': 'c***.***',
         'CSR file': 'new-pki.***.csr',
         'CSR FileID': 'file$593805516',
         'CSR Body': '-----BEGIN CERTIFICATE REQUEST-----\nMIIDNzC....5NLPmx88M=\n-----END CERTIFICATE REQUEST-----\n'}

    return example: f'{downloads}/{cert_name}.{cert_format}'
    """
    context = playwright.chromium.launch_persistent_context(
        "",
        # headless=False,
        headless=True,
        # slow_mo=1000,
        http_credentials={
            "username": user,
            "password": password
        },
        ignore_https_errors=True
    )

    page = context.new_page()
    page.goto(url)

    # CLICK "Request a certificate" LINK
    page.get_by_role('link', name='Request a certificate').click()

    # CLICK "Submit a certificate request..." LINK
    page.get_by_role('link', name='Submit a certificate request by using a base-64-encoded CMC or PKCS #10 file, '
                                  'or submit a renewal request by using a base-64-encoded PKCS #7	file.').click()

    # reading csr file
    with open(csr_file, 'r') as csr:
        csr_body = csr.read()

    # FILL TEXTFIELD WITH CSR BODY
    page.locator('#locTaRequest').fill(csr_body)

    # SELECT CORRESPONDING TEMPLATE
    if template == 'SSL':
        page.locator('#lbCertTemplateID').select_option(label="23https/ssl")
    elif template == 'Ldaps for pam':
        page.locator('#lbCertTemplateID').select_option(label="23LDAPS_for_PAM")
    elif template == 'Web client and server':
        page.locator('[name="lbCertTemplate"]').select_option(label='23Web Client and Server')
    else:
        raise Exception(f'TEMPLATE NOT IN LIST, CHECK TEMPLATE TYPE({template})')

    # CLICK SUBMIT
    page.locator('#btnSubmit').click()

    # EXPECT PAGE WITH NO ERROR("Certificate Issues")
    expect(page.locator('#locPageTitle')).to_have_text(re.compile('Certificate Issued'))

    # SELECT "Base 64 encoded" RADIO
    page.locator('#rbB64Enc').check()

    # DOWNLOAD CERTIFICATE(cer/pem)
    with page.expect_download() as download_info:
        page.locator('#locDownloadCert3').click()
    download = download_info.value
    download_path = f'{path_to_save_cer}/{cn}.{cer_ext}'
    try:
        download.save_as(download_path)
    except Exception as e:
        raise Exception(f'FAILED TO DOWNLOAD CERT WITH ERROR\n{e}\n')
    finally:
        # CLOSE PAGE(SESSION)
        page.close()
        # context.close()

    # sleep(1000)

    return download_path


# MAKE PFX FROM CERT & KEY
def make_pfx(openssl_bin_path: str, cn: str, cer_file_path: str, key_file_path: str, out_file_path: str, pfx_pass: str):
    """
    Make pfx file wit passsword from cer/crt file and key file
    :param openssl_bin_path: full path to OpenSSL binary, string
    :param cn: CN(or name for pfx file), string
    :param cer_file_path: cer/crt file path, string
    :param key_file_path: key file path, string
    :param out_file_path: result pfx file path to save, string
    :param pfx_pass: pfx password, string
    :return:

    Openssl command example:
        # openssl pkcs12 -inkey cert.key -in cert.crt -export -out cert.pfx -password pass:a1b2

        try:
            run([pidea_janitor_path, 'find', '--serial', token, '--action', 'delete'],
                capture_output=True, text=True).stdout
    """
    pfx_file_path = out_file_path+"/"+cn+".pfx"
    process_str = f'{openssl_bin_path} pkcs12 -inkey {key_file_path} -in {cer_file_path} -export -out {pfx_file_path} -password pass:{pfx_pass}'
    try:
        subprocess.run(
            [
                openssl_bin_path,
                "pkcs12",
                "-inkey",
                key_file_path,
                "-in",
                cer_file_path,
                "-export",
                "-out",
                pfx_file_path,
                "-password",
                "pass:"+pfx_pass
            ], capture_output=True, text=True).stdout
    except Exception as e:
        raise Exception(f'FAILED TO MAKE PFX FOR {cn}\n'
                        f'KEY:{key_file_path}\n'
                        f'CER:{cer_file_path}\n'
                        f'PFX:{pfx_file_path}\n'
                        f'PS_STR:\n{process_str}\n'
                        f'{e}')
