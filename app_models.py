from pydantic import BaseModel, Field


class CrawlerSettings(BaseModel):
    url: str = "https://wagslane.dev"
    max_concurrency: int = Field(default=3, ge=1, le=100)
    max_pages: int = Field(default=50, ge=1, le=100000)
    interval_minutes: int = Field(default=60, ge=1, le=10080)
    request_timeout: int = Field(default=20, ge=3, le=180)
    max_retries: int = Field(default=2, ge=0, le=10)
    report_filename: str = "report.json"
    graph_filename: str = "report_graph.png"
    send_email: bool = False
    email_to: str = ""
    resend_api_key: str = ""
    resend_from: str = "Crawler Bot <onboarding@resend.dev>"
