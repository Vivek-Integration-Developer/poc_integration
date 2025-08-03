import json
import requests
from config import AUDIT_URL
from utils.datetime_utils import now_readable

class AuditClient:
    def __init__(self):
        self.url = AUDIT_URL

    def log(self, unique_id: str, step: str, status: str, status_type: str,
            project_no: str, record_no: str, link_id: str,
            integration_status: str, seq_no: str, path: str, payload: dict) -> requests.Response:
        body = {
            "UniqueId": unique_id,
            "ApplicationName": "APP_POC",
            "Step": step,
            "Status": status,
            "StatusType": status_type,
            "TimeStamp": now_readable(),
            "ProjectNumber": project_no,
            "RecordNumber": record_no,
            "linkId": link_id,
            "IntegrationStatus": integration_status,
            "SeqNo": seq_no,
            "path": path,
            "Payload": json.dumps(payload)
        }
        print(f"AuditClient.log -> POST {self.url} payload: {body}")
        resp = requests.post(self.url, json=body)
        print(
            "AuditClient.log <-",
            f"status {getattr(resp, 'status_code', 'unknown')} response: {getattr(resp, 'text', '')}",
        )
        return resp
