import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app_models import CrawlerSettings
from app_state import state
from crawler_service import reschedule_job, run_crawl_once


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Crawler Server")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
async def startup_event():
    state.scheduler.start()
    reschedule_job()


@app.on_event("shutdown")
async def shutdown_event():
    state.scheduler.shutdown(wait=False)


@app.get("/")
async def ui():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/settings")
async def api_get_settings():
    return JSONResponse(state.settings.model_dump())


@app.post("/api/settings")
async def api_set_settings(settings: CrawlerSettings):
    state.settings = settings
    reschedule_job()
    return JSONResponse({"status": "ok", "settings": state.settings.model_dump()})


@app.post("/api/run-now")
async def run_now():
    if state.is_running:
        return JSONResponse({"status": "already-running"})

    async def _runner():
        await run_crawl_once()

    asyncio.create_task(_runner())
    return JSONResponse({"status": "started"})


@app.get("/api/status")
async def api_status():
    return JSONResponse(state.status_payload())


@app.get("/api/report-json")
async def api_report_json():
    report_path = BASE_DIR / state.settings.report_filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="report file not found")
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(data)


@app.get("/api/report-graph")
async def api_report_graph():
    graph_path = BASE_DIR / state.settings.graph_filename
    if not graph_path.exists():
        raise HTTPException(status_code=404, detail="graph file not found")
    return FileResponse(graph_path)


@app.websocket("/ws/status")
async def ws_status(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(state.status_payload())
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        return
