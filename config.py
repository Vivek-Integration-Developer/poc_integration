import os
from dotenv import load_dotenv

load_dotenv()

# Unifier settings
UNIFIER_BASE_URL = os.getenv("UNIFIER_BASE_URL", "https://eu1.unifier.oraclecloud.com")
UNIFIER_REPORT_NAME = os.getenv("UNIFIER_REPORT_NAME", "POC_INT_V2")
UNIFIER_BEARER_TOKEN = os.getenv("UNIFIER_BEARER_TOKEN")

# Polling interval (minutes)
POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", "5"))

# Audit service
AUDIT_URL = os.getenv("AUDIT_URL", "http://10.100.5.198:5008/Test/POC/insertRequest")

# Fusion validation
FUSION_VALIDATION_URL = os.getenv("FUSION_VALIDATION_URL", "http://10.100.5.198:6003/poc-status/test")

# Fusion receipt
FUSION_RECEIPT_URL = os.getenv(
    "FUSION_RECEIPT_URL",
    "https://eoay-test.fa.em2.oraclecloud.com:443/"
    "fscmRestApi/resources/11.13.18.05/receivingReceiptRequests"
)
FUSION_USER = os.getenv("FUSION_USER")
FUSION_PASS = os.getenv("FUSION_PASS")
