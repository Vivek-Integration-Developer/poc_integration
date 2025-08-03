import uuid
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify

from config import POLL_INTERVAL_MINUTES
from clients.unifier_client import UnifierClient
from clients.audit_client import AuditClient
from clients.fusion_validation_client import FusionValidationClient
from clients.fusion_receipt_client import FusionReceiptClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

unique_id = str(uuid.uuid4())

unifier = UnifierClient()
auditor = AuditClient()
validator = FusionValidationClient()
receipt_client = FusionReceiptClient()
scheduler = BackgroundScheduler()

def step_job(date_str: str):
    records = unifier.fetch_records(date_str)
    if not records:
        logger.info("No new records to process.")
        return

    for idx, rec in enumerate(records, start=1):
        seq_base = f"1.{idx}"
        # Step 1
        flag_msg = "The POC record has been read..."
        auditor.log(unique_id, "FUS_Step1_Req_UpdateIntRead", "Open", "Request",
                    rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.1", "POC",
                    unifier.build_flag_payload(rec, "INT READ", 1, flag_msg))
        resp_flag = unifier.update_flag(rec, "INT READ", 1, flag_msg)
        auditor.log(unique_id, "FUS_Step1_Res_UpdateIntRead", "Closed", "Response",
                    rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.2", "POC",
                    resp_flag.json())

        # Step 2
        payload_val, val_res = validator.validate_po(rec)
        auditor.log(unique_id, "FUS_Step2_Req_ValidatePO", "Open", "Request",
                    rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.3", "POC",
                    payload_val)
        auditor.log(unique_id, "FUS_Step2_Res_ValidatePO", "Closed", "Response",
                    rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.4", "POC",
                    val_res.raw)

        if not val_res.g1 or val_res.po_status != "OPEN":
            err_msg = "The POC record validation failed.."
            auditor.log(unique_id, "FUS_Step2_Req_UpdateIntError", "Open", "Request",
                        rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.5", "POC",
                        unifier.build_flag_payload(rec, "INT Error", 2, err_msg))
            resp_err = unifier.update_flag(rec, "INT Error", 2, err_msg)
            auditor.log(unique_id, "FUS_Step2_Res_UpdateIntError", "Closed", "Response",
                        rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.6", "POC",
                        resp_err.json())
            continue

        # Step 3
        payload_rcpt, rcpt_res = receipt_client.create_receipt(rec, val_res)
        auditor.log(unique_id, "FUS_Step3_Req_CreateReceipt", "Open", "Request",
                    rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.7", "POC",
                    payload_rcpt)
        auditor.log(unique_id, "FUS_Step3_Res_CreateReceipt", "Closed", "Response",
                    rec.c10, rec.c11, rcpt_res.number or "", "INT Inprogress", f"{seq_base}.8", "POC",
                    rcpt_res.raw)

        if rcpt_res.status == "SUCCESS":
            comp_msg = "Receipt Created Successfully"
            auditor.log(unique_id, "FUS_Step3_Req_UpdateIntComplete", "Open", "Request",
                        rec.c10, rec.c11, rcpt_res.number, "INT Inprogress", f"{seq_base}.9", "POC",
                        unifier.build_flag_payload(rec, "INT COMPLETE", 3, comp_msg))
            resp_comp = unifier.update_flag(rec, "INT COMPLETE", 3, comp_msg)
            auditor.log(unique_id, "FUS_Step3_Res_UpdateIntComplete", "Closed", "Response",
                        rec.c10, rec.c11, rcpt_res.number, "INT Inprogress", f"{seq_base}.10", "POC",
                        resp_comp.json())
        else:
            err3 = f"Receipt Creation Failed: {rcpt_res.message}"
            auditor.log(unique_id, "FUS_Step3_Req_UpdateIntError", "Open", "Request",
                        rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.9", "POC",
                        unifier.build_flag_payload(rec, "INT Error", 3, err3))
            resp_err3 = unifier.update_flag(rec, "INT Error", 3, err3)
            auditor.log(unique_id, "FUS_Step3_Res_UpdateIntError", "Closed", "Response",
                        rec.c10, rec.c11, "", "INT Inprogress", f"{seq_base}.10", "POC",
                        resp_err3.json())

@app.post("/run")
def run():
    data = request.get_json() or {}
    date_str = data.get("date")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    step_job(date_str)
    return jsonify({"status": "Job started", "date": date_str})

if __name__ == "__main__":
    scheduler.add_job(
        lambda: step_job(datetime.now().strftime("%Y-%m-%d")),
        "interval",
        minutes=POLL_INTERVAL_MINUTES,
    )
    logger.info(f"Scheduler started with run ID {unique_id}")
    scheduler.start()
    app.run(host="0.0.0.0", port=5000)
