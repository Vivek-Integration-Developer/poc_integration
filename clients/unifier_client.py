import requests
from urllib.parse import urljoin
from config import UNIFIER_BASE_URL, UNIFIER_REPORT_NAME, UNIFIER_BEARER_TOKEN
from utils.datetime_utils import iso_datetime

class Record:
    def __init__(self, row: dict):
        self.c1 = row.get("c1")
        self.c2 = row.get("c2")
        self.c3 = float(row.get("c3", "0").replace(",", ""))
        self.c4 = row.get("c4")
        self.c5 = row.get("c5")
        self.c6 = row.get("c6")
        self.c7 = float(row.get("c7", "0").replace(",", ""))
        self.c8 = row.get("c8")
        self.c9 = row.get("c9")
        self.c10 = row.get("c10")
        self.c11 = row.get("c11")

class UnifierClient:
    def __init__(self):
        self.base_url = UNIFIER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {UNIFIER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

    def fetch_records(self, today_str: str) -> list[Record]:
        url = urljoin(self.base_url, "/tatweer/stage/ws/rest/service/v1/data/udr/get")
        payload = {
            "reportname": UNIFIER_REPORT_NAME,
            "query": [
                {"label": "stutas", "value1": "Approved"},
                {"label": "integration_flag", "value1": "New"},
                {
                    "label": "approved date",
                    "operator": "between",
                    "value1": today_str,
                    "value2": today_str
                }
            ]
        }
        resp = requests.post(url, json=payload, headers=self.headers)
        data = resp.json()
        if data.get("status") != 200:
            return []
        rows = data.get("data", [])
        if not rows or not rows[0].get("report_row"):
            return []
        return [Record(r) for r in rows[0]["report_row"]]

    def build_flag_payload(self, record: Record, status: str, seq_no: int, message: str) -> dict:
        return {
            "options": {"bpname": "POC"},
            "data": [
                {
                    "record_no": record.c11,
                    "INTEGRATION_FLAG": status,
                    "_bp_lineitems": [
                        {
                            "POC_FusStatus_SDT250": status,
                            "POC_FusStatusDate_SDT250": iso_datetime(),
                            "POC_FusSeqNo_SDT250": str(seq_no),
                            "POC_FusrecDetails_MTB4K": message,
                            "uuu_tab_id": "Fusion Record Status",
                            "short_desc": "Testing"
                        }
                    ]
                }
            ]
        }

    def update_flag(self, record: Record, status: str, seq_no: int, message: str) -> requests.Response:
        url = urljoin(self.base_url, f"/tatweer/stage/ws/rest/service/v1/bp/record/{record.c10}")
        payload = self.build_flag_payload(record, status, seq_no, message)
        return requests.put(url, json=payload, headers=self.headers)
