from unittest.mock import patch

from clients.unifier_client import Record
from clients.audit_client import AuditClient


def test_record_handles_none_values():
    r = Record({"c3": None, "c7": None, "c10": "p", "c11": "r"})
    assert r.c3 == 0.0
    assert r.c7 == 0.0


def test_audit_client_uses_correct_project_number_key():
    client = AuditClient()
    with patch("requests.post") as post:
        client.log("id", "step", "status", "type", "prj", "rec", "",
                   "INT", "1", "path", {"a": 1})
        body = post.call_args.kwargs["json"]
        assert "ProjectNumber" in body
        assert "Projectumber" not in body
