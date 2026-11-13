from __future__ import annotations

import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import uvicorn

from config import get_settings
from dashboard.app import create_dashboard_app
from dashboard.webhook import create_webhook_app
from modules.coordinator import CoStreamerRuntime


def configure_logging(root: Path) -> None:
    log_dir = root / "logs"
    log_dir.mkdir(exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(log_dir / "assistant.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


async def run() -> None:
    settings = get_settings()
    configure_logging(settings.root_dir)
    runtime = CoStreamerRuntime(settings)
    dashboard_app = create_dashboard_app(runtime, settings)
    webhook_app = create_webhook_app(runtime)
    await runtime.startup()

    dashboard_server = uvicorn.Server(
        uvicorn.Config(dashboard_app, host=settings.bind_host, port=settings.port, log_level="warning", access_log=False)
    )
    webhook_server = uvicorn.Server(
        uvicorn.Config(webhook_app, host=settings.webhook_bind_host, port=settings.webhook_port, log_level="warning", access_log=False)
    )
    logging.getLogger(__name__).info(
        "Dashboard on http://%s:%d; isolated webhook listener on %s:%d%s",
        settings.bind_host,
        settings.port,
        settings.webhook_bind_host,
        settings.webhook_port,
        settings.kick_webhook_path,
    )
    try:
        await asyncio.gather(dashboard_server.serve(), webhook_server.serve())
    finally:
        dashboard_server.should_exit = True
        webhook_server.should_exit = True
        await runtime.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
