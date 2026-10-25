#!/usr/bin/env python3
"""Minimal HTTP wrapper around the tesseract CLI binary.

POST an image (raw bytes -- PNG/JPEG/TIFF, anything leptonica reads) to
/ocr and get back {"text": "..."}. Deliberately stdlib-only and calls
tesseract as a plain subprocess per request rather than embedding a
model-serving framework: this container exists purely to isolate one
lightweight OCR engine (a ~5MB binary + ~22MB language data, no
persistent model loaded in memory) as its own portable service, kept
separate from the WordPress runtime so it stays easy to move to a new
host independently of everything else.
"""
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080
LANG = "nld"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json({"ok": True})
            return
        self._send_json({"error": "not found"}, status=404)

    def do_POST(self):
        if self.path != "/ocr":
            self._send_json({"error": "not found"}, status=404)
            return

        length = int(self.headers.get("Content-Length", 0))
        image_bytes = self.rfile.read(length)
        print(f"[ocr] received {len(image_bytes)} bytes (Content-Length header: {length})", flush=True)
        if not image_bytes:
            self._send_json({"error": "empty body"}, status=400)
            return

        try:
            result = subprocess.run(
                ["tesseract", "-", "-", "-l", LANG],
                input=image_bytes,
                capture_output=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            self._send_json({"error": "OCR timed out"}, status=504)
            return
        except FileNotFoundError:
            self._send_json({"error": "tesseract binary not found"}, status=500)
            return

        if result.returncode != 0:
            err = result.stderr.decode("utf-8", "replace")
            print(f"[tesseract exit {result.returncode}] {err}", flush=True)
            self._send_json({"error": err}, status=500)
            return

        self._send_json({"text": result.stdout.decode("utf-8", "replace")})


if __name__ == "__main__":
    print(f"Tesseract OCR service listening on :{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
