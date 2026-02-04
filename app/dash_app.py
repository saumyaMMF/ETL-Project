"""Dash application entrypoint for ERP-safe ETL workflow."""

from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone

import dash
from dash import Dash, Input, Output, State, dcc, html

from app.config.settings import CONFIG
from app.logging.ai_logger import AILogger, AILog
from app.logging.file_logger import FileLog, FileLogger
from app.logging.workflow_logger import WorkflowLog, WorkflowLogger
from app.services.s3_service import S3Service
from app.services.signed_url_service import SignedUrlService
from app.utils.hash_utils import stable_hash


app: Dash = dash.Dash(__name__)
s3_service = S3Service()
file_logger = FileLogger()
workflow_logger = WorkflowLogger()
ai_logger = AILogger()
signed_url_service = SignedUrlService(s3_service)


app.layout = html.Div(
    [
        html.H1("ERP GenAI ETL POC"),
        dcc.Upload(
            id="file-upload",
            children=html.Div(["Drag and Drop or ", html.A("Select File")]),
            multiple=False,
        ),
        html.Div(id="upload-status"),
        html.Div(id="file-type"),
        html.Div(id="mapping-preview"),
        html.Div(id="processing-status"),
        html.Div(id="download-links"),
        dcc.Store(id="file-id-store"),
    ]
)


@app.callback(
    Output("upload-status", "children"),
    Output("file-id-store", "data"),
    Input("file-upload", "contents"),
    State("file-upload", "filename"),
    prevent_initial_call=True,
)
def handle_upload(contents: str | None, filename: str | None) -> tuple[str, str | None]:
    if not contents or not filename:
        return "No file uploaded.", None
    file_id = str(uuid.uuid4())
    content_type, content_string = contents.split(",", maxsplit=1)
    raw_bytes = base64.b64decode(content_string)
    key = f"{CONFIG.inputs_prefix}/{file_id}/{filename}"
    s3_service.put_bytes(key, raw_bytes, content_type)

    file_log = FileLog(file_id=file_id, original_filename=filename)
    file_logger.write(file_log)

    return f"Uploaded {filename} with file_id={file_id}", file_id


@app.callback(
    Output("processing-status", "children"),
    Input("file-id-store", "data"),
    State("file-upload", "filename"),
    prevent_initial_call=True,
)
def start_workflow(file_id: str | None, filename: str | None) -> str:
    if not file_id or not filename:
        return "No workflow started."
    workflow_id = str(uuid.uuid4())
    workflow_log = WorkflowLog(workflow_id=workflow_id, file_ids=[file_id])
    workflow_log.add_step("upload", "completed")
    workflow_logger.write(workflow_log)
    return f"Workflow {workflow_id} started at {datetime.now(timezone.utc).isoformat()}"


@app.callback(
    Output("download-links", "children"),
    Input("file-id-store", "data"),
    prevent_initial_call=True,
)
def show_download_links(file_id: str | None) -> list[html.Li]:
    if not file_id:
        return []
    outputs_prefix = f"{CONFIG.outputs_prefix}/{file_id}"
    keys = [
        f"{outputs_prefix}/file_a.xlsx",
        f"{outputs_prefix}/file_b.xlsx",
        f"{outputs_prefix}/file_c.xlsx",
        f"{outputs_prefix}/cancellations.xlsx",
    ]
    links = []
    for key in keys:
        url = signed_url_service.create_download_url(key)
        links.append(html.Li(html.A(key.split("/")[-1], href=url)))
    return links


def log_ai_decision(file_id: str, agent_name: str, model_name: str, prompt: dict, output: dict, confidence: float) -> None:
    payload = {
        "agent": agent_name,
        "model": model_name,
        "input_snapshot": prompt.get("input_snapshot", {}),
        "output": output,
    }
    validation_result = "valid" if output else "invalid"
    ai_log = AILog(
        file_id=file_id,
        agent_name=agent_name,
        model_name=model_name,
        prompt=prompt,
        input_snapshot=prompt.get("input_snapshot", {}),
        output=output,
        confidence=confidence,
        validation_result=validation_result,
    )
    ai_logger.write(ai_log)
    stable_hash(payload)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=False)
