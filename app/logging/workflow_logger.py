"""Workflow-level logging."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.logging.s3_logger import S3Logger


@dataclass
class WorkflowStep:
    name: str
    status: str
    started_at: str
    finished_at: str | None = None
    failure_reason: str | None = None


@dataclass
class WorkflowLog:
    workflow_id: str
    file_ids: List[str]
    steps: List[WorkflowStep] = field(default_factory=list)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "file_ids": self.file_ids,
            "steps": [step.__dict__ for step in self.steps],
        }

    def add_step(self, name: str, status: str, failure_reason: str | None = None) -> None:
        self.steps.append(
            WorkflowStep(
                name=name,
                status=status,
                started_at=datetime.now(timezone.utc).isoformat(),
                finished_at=datetime.now(timezone.utc).isoformat(),
                failure_reason=failure_reason,
            )
        )


class WorkflowLogger:
    def __init__(self, s3_logger: S3Logger | None = None) -> None:
        self.s3_logger = s3_logger or S3Logger()

    def write(self, log: WorkflowLog) -> None:
        key = f"workflows/{log.workflow_id}.json"
        self.s3_logger.write(key, log.to_payload())
