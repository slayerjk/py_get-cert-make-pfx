# py_get-cert-make-pfx
Get cert from MS PKI server and make .pfx file

Just a small script to automatize PKI cert releasing.

!To run in Linux only, where openSSL is in /usr/bin/openssl.!

**Workflow**
- Create RESULTS_<date> dir
- Create inside results <CN> named dir based on <CN> in data_files/cns_data
- Make <CN>.CSR & <CN>.KEY files using openSSL in each <CN>
- Make <CN>.CER file in <CN> dir using Playwright and Windows PKI server(check creds & urls in data_files/data-prod.json)
- Make <CN>.PFX file using openSSL with '123' pass
