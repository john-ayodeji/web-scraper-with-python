import asyncio
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app_models import CrawlerSettings


class AppState:
    def __init__(self):
        self.settings = CrawlerSettings(
            resend_api_key=os.getenv("RESEND_API_KEY", ""),
            email_to=os.getenv("CRAWLER_EMAIL_TO", ""),
        )
        self.scheduler = AsyncIOScheduler(timezone="UTC")
        self.current_run_task = None
        self.is_running = False
        self.last_error = ""
        self.last_run_at: datetime | None = None
        self.last_started_at: datetime | None = None
        self.last_summary: dict = {}
        self.run_lock = asyncio.Lock()

    def status_payload(self):
        return {
            "running": self.is_running,
            "last_error": self.last_error,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_started_at": self.last_started_at.isoformat() if self.last_started_at else None,
            "summary": self.last_summary,
        }


state = AppState()
