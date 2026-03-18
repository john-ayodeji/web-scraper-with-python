# Web Scraper With Python

An async web crawler that can:
- Crawl pages concurrently with retry and timeout safeguards
- Stop automatically at a configurable max page limit
- Track internal and external links per page
- Export crawl results to JSON
- Generate a graph image showing page-link relationships
- Run continuously on a timer from a server
- Let you change crawl settings from a web UI or API while the server is running
- Stream live run status to the UI using WebSockets
- Show graph and discovered image previews directly in the UI
- Send report updates by email using Resend

## Project structure

- app_models.py: Pydantic models for runtime settings
- app_state.py: Shared scheduler and runtime status state
- crawler_service.py: Crawl execution, report generation, email sending
- server.py: FastAPI routes, static serving, websocket status endpoint
- static/index.html: UI layout
- static/styles.css: responsive and interactive styles
- static/app.js: API wiring, websocket updates, and UI interactions

## 1) Clone and setup

### Clone
```bash
git clone <your-repo-url>
cd "web scraper with python"
```

### Install dependencies
This project uses uv.

```bash
uv sync
```

If you do not have uv, install it first:
```bash
pip install uv
```

## 2) Run one crawl from CLI

```bash
uv run main.py https://example.com 3 25
```

Arguments:
1. URL
2. max_concurrency
3. max_pages

Output files:
- report.json

## 3) Run as a server with runtime configuration

Start the server:

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8000
```

Open:
- http://localhost:8000

From the UI, you can set:
- URL
- max concurrency
- max pages
- timer interval (minutes)
- request timeout
- max retries
- Resend API key
- destination email
- sender email
- whether email updates are enabled

Use "Save and Apply" to update settings live.
Use "Run Now" to trigger an immediate crawl.

### API endpoints
- GET /api/settings
- POST /api/settings
- GET /api/status
- POST /api/run-now
- GET /api/report-json
- GET /api/report-graph
- WS /ws/status

Example API update:

```bash
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "max_concurrency": 5,
    "max_pages": 100,
    "interval_minutes": 30,
    "request_timeout": 20,
    "max_retries": 2,
    "report_filename": "report.json",
    "graph_filename": "report_graph.png",
    "send_email": false,
    "email_to": "",
    "resend_api_key": "",
    "resend_from": "Crawler Bot <onboarding@resend.dev>"
  }'
```

## 4) Resend email setup

Set your API key either in the web UI or environment variable:

```bash
export RESEND_API_KEY="re_xxx"
export CRAWLER_EMAIL_TO="you@example.com"
```

When email is enabled, each scheduled run can send:
- report.json as attachment
- report_graph.png as attachment
- summary stats in the email body

## 5) Deployment (example on Ubuntu)

### Install project and dependencies
```bash
sudo apt update
sudo apt install -y python3-pip git
pip install uv

git clone <your-repo-url>
cd "web scraper with python"
uv sync
```

### Run with systemd
Create /etc/systemd/system/crawler.service:

```ini
[Unit]
Description=Web Crawler Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/web scraper with python
Environment="RESEND_API_KEY=re_xxx"
Environment="CRAWLER_EMAIL_TO=you@example.com"
ExecStart=/home/ubuntu/.local/bin/uv run uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable crawler
sudo systemctl start crawler
sudo systemctl status crawler
```

## 6) Report format

Each page object includes:
- url
- heading
- first_paragraph
- outgoing_links
- internal_links
- external_links
- internal_link_count
- external_link_count
- image_urls

## 7) Notes for large sites

For better stability on large crawls:
- Keep max_concurrency moderate (for example 3-10)
- Set a sane max_pages cap
- Increase request_timeout for slow sites
- Increase max_retries cautiously
