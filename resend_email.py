import base64
import os

import resend


def _file_to_attachment(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return {
        "filename": os.path.basename(path),
        "content": encoded,
    }


def send_report_email(
    to_email,
    subject,
    html,
    resend_api_key,
    from_email="Crawler Bot <onboarding@resend.dev>",
    report_json_path="report.json",
    graph_path=None,
):
    if not resend_api_key:
        raise ValueError("Missing RESEND_API_KEY")

    attachments = []
    if report_json_path and os.path.exists(report_json_path):
        attachments.append(_file_to_attachment(report_json_path))
    if graph_path and os.path.exists(graph_path):
        attachments.append(_file_to_attachment(graph_path))

    resend.api_key = resend_api_key
    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html,
        "attachments": attachments,
    }
    return resend.Emails.send(params)
