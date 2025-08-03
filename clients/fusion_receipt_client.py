import requests
from config import FUSION_RECEIPT_URL, FUSION_USER, FUSION_PASS

class ReceiptResult:
    def __init__(self, raw: dict):
        self.raw = raw
        self.status = raw.get("ReturnStatus")
        self.number = raw.get("ReceiptNumber")
        self.message = raw.get("ReturnMessage")

class FusionReceiptClient:
    def __init__(self):
        self.url = FUSION_RECEIPT_URL
        self.auth = (FUSION_USER, FUSION_PASS)
        self.headers = {"Content-Type": "application/json"}

    def create_receipt(self, record, validation_result) -> tuple[dict, ReceiptResult]:
        tx_date = f"{record.c5}-{record.c9}-01"
        line = validation_result.g1
        order_amt = float(line.get("LINE_ORDER_AMOUNT", 0))
        delivered = float(line.get("LINE_DELIVERD_AMOUNT", 0))
        cum_pct = record.c3
        line_type = line.get("LINETYPE")

        if line_type == "Fixed Price Services":
            amount = cum_pct * order_amt - delivered
        else:
            amount = cum_pct * order_amt + delivered

        payload = {
            "ReceiptSourceCode": "VENDOR",
            "TransactionDate": tx_date,
            "OrganizationCode": line.get("ORGANIZATIONCODE"),
            "VendorNumber": line.get("SUPPLIERNUMBER"),
            "BusinessUnit": line.get("BUSINESSUNIT"),
            "EmployeeId": line.get("REQUESTERID"),
            "lines": [
                {
                    "TransactionDate": tx_date,
                    "ReceiptSourceCode": "VENDOR",
                    "SourceDocumentCode": "PO",
                    "TransactionType": "RECEIVE",
                    "AutoTransactCode": "DELIVER",
                    "DocumentDistributionNumber": "1",
                    "DocumentShipmentLineNumber": "1",
                    "OrganizationCode": line.get("ORGANIZATIONCODE"),
                    "ItemDescription": line.get("ITEMDESCRIPTION"),
                    "DocumentNumber": record.c8,
                    "DocumentLineNumber": record.c4,
                    "Quantity": "",
                    "Amount": amount,
                    "CurrencyCode": "SAR",
                    "SoldtoLegalEntity": "TBC"
                }
            ]
        }
        print(
            f"FusionReceiptClient.create_receipt -> POST {self.url} payload: {payload}"
        )
        resp = requests.post(self.url, json=payload, auth=self.auth, headers=self.headers)
        print(
            "FusionReceiptClient.create_receipt <-",
            f"status {getattr(resp, 'status_code', 'unknown')} response: {getattr(resp, 'text', '')}",
        )
        raw = resp.json() if resp.ok else {}
        return payload, ReceiptResult(raw)
