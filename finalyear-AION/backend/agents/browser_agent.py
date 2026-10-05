from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from backend.agents.base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    name = "BrowserAgent"

    def open_url(self, url: str) -> dict[str, Any]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            title = page.title()
            browser.close()
        return {"url": url, "title": title}

    def search_web(self, query: str, engine: str = "https://duckduckgo.com/?q=") -> dict[str, Any]:
        url = f"{engine}{quote_plus(query)}"
        return self.open_url(url)

    def download_file(self, url: str, download_dir: str) -> dict[str, Any]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            browser.close()
        return {"status": "opened", "url": url, "download_dir": download_dir}

    def execute(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if not hasattr(self, action):
            raise ValueError(f"Unsupported action: {action}")
        return getattr(self, action)(**parameters)
