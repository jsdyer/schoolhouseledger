"""Exercise the published records explorer at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "schoolhouseledger")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_BIN"))
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/schoolhouseledger/")
                page.wait_for_function("document.querySelector('#edition').textContent.includes('UTC')")
                assert "12.85" in page.locator("#comparison").inner_text()
                page.locator("#first").select_option("Port Kells")
                page.locator("#year").select_option("1890")
                assert "Port Kells has no entry" in page.locator("#finding").inner_text()
                assert "—" in page.locator("#comparison").inner_text()
                page.locator("#year").select_option("1895")
                assert "12.11" in page.locator("#annual").inner_text()
                assert "#page=125" in page.locator("#comparison a").first.get_attribute("href")
                with page.expect_download() as capture:
                    page.locator("#csv").click()
                download = capture.value
                assert download.suggested_filename.endswith(".csv")
                assert len(Path(download.path()).read_text().splitlines()) >= 2
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print("Browser checks passed: source records, filters, CSV download and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
