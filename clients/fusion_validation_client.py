import requests
from config import FUSION_VALIDATION_URL

class ValidationResult:
    def __init__(self, raw: dict):
        self.raw = raw
        ds = raw.get("DATA_DS", {})
        self.g1 = ds.get("G_1", {})
        self.po_status = self.g1.get("PO_STATUS")

class FusionValidationClient:
    def __init__(self):
        self.url = FUSION_VALIDATION_URL

    def validate_po(self, record) -> tuple[dict, ValidationResult]:
        payload = {
            "poNumber": record.c8,
            "poLineAmount": record.c7,
            "projectNumber": record.c10,
            "poLineNum": record.c4
        }
        print(f"FusionValidationClient.validate_po -> POST {self.url} payload: {payload}")
        resp = requests.post(self.url, json=payload)
        print(
            "FusionValidationClient.validate_po <-",
            f"status {getattr(resp, 'status_code', 'unknown')} response: {getattr(resp, 'text', '')}",
        )
        raw = resp.json() if resp.ok else {}
        return payload, ValidationResult(raw)
