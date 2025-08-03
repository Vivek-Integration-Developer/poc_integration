# POC Integration

## Overview
Python middleware to integrate Oracle Unifier with Oracle Fusion, complete with audit.

### Prerequisites
- Python 3.8+
- `pip install -r requirements.txt`
- Create a `.env` file in project root with:
  ```
  UNIFIER_BASE_URL=https://eu1.unifier.oraclecloud.com
  UNIFIER_REPORT_NAME=POC_INT_V2
  UNIFIER_BEARER_TOKEN=<your-token>

  POLL_INTERVAL_MINUTES=5

  AUDIT_URL=http://10.100.5.198:5008/Test/POC/insertRequest

  FUSION_VALIDATION_URL=http://10.100.5.198:6003/poc-status/test

  FUSION_RECEIPT_URL=https://eoay-test.fa.em2.oraclecloud.com:443/fscmRestApi/resources/11.13.18.05/receivingReceiptRequests
  FUSION_USER=<username>
  FUSION_PASS=<password>
  ```

### Running
```bash
python main.py
```
The scheduler will poll Unifier every `POLL_INTERVAL_MINUTES`.
