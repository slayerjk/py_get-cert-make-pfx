# py_get-cert-make-pfx
Get cert from MS PKI server and make .pfx file

Just a small script to automatize PKI cert releasing.

**Workflow**
- You must have a dir with .csr and .key files this format:
  BASE_DIR
    -CNANME1
      - CNAME1.csr
      - CNAME1.key
    - CNAME2
- Takes all csr and get via Playwright .crt file and put it in the CNAME dir with CNAME.crt.
- Then it make .pfx file
