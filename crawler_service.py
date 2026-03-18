import asyncio
from datetime import datetime, timezone

from app_state import state
from crawl import crawl_site_async
from graph_report import write_graph_report
from json_report import write_json_report
from resend_email import send_report_email


async def run_crawl_once(force=False):
    async with state.run_lock:
        if state.is_running and not force:
            return False
        state.is_running = True
        state.last_started_at = datetime.now(timezone.utc)

    try:
        settings = state.settings
        page_data = await crawl_site_async(
            settings.url,
            max_concurrency=settings.max_concurrency,
            max_pages=settings.max_pages,
            request_timeout=settings.request_timeout,
            max_retries=settings.max_retries,
        )

        write_json_report(page_data, settings.report_filename)
        graph_path = write_graph_report(page_data, settings.graph_filename)

        total_internal = sum(page.get("internal_link_count", 0) for page in page_data.values())
        total_external = sum(page.get("external_link_count", 0) for page in page_data.values())

        state.last_summary = {
            "pages": len(page_data),
            "internal_links": total_internal,
            "external_links": total_external,
            "report": settings.report_filename,
            "graph": graph_path,
        }
        state.last_run_at = datetime.now(timezone.utc)
        state.last_error = ""

        if settings.send_email:
            if not settings.email_to:
                raise ValueError("Email destination is required when send_email is enabled")

            await asyncio.to_thread(
                send_report_email,
                to_email=settings.email_to,
                subject=f"Crawler report for {settings.url}",
                html=(
                    f"<h2>Crawl complete</h2>"
                    f"<p><strong>URL:</strong> {settings.url}</p>"
                    f"<p><strong>Pages:</strong> {len(page_data)}</p>"
                    f"<p><strong>Internal links:</strong> {total_internal}</p>"
                    f"<p><strong>External links:</strong> {total_external}</p>"
                ),
                resend_api_key=settings.resend_api_key,
                from_email=settings.resend_from,
                report_json_path=settings.report_filename,
                graph_path=graph_path,
            )

        return True
    except Exception as error:
        state.last_error = str(error)
        return False
    finally:
        async with state.run_lock:
            state.is_running = False


def reschedule_job():
    if state.scheduler.get_job("crawl-job"):
        state.scheduler.remove_job("crawl-job")
    state.scheduler.add_job(
        run_crawl_once,
        "interval",
        minutes=state.settings.interval_minutes,
        id="crawl-job",
        max_instances=1,
        coalesce=True,
    )
