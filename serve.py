#!/usr/bin/env python3
"""Serve this folder the way a real web host does — byte ranges included.

    python showcase/serve.py           # http://localhost:8731
    python showcase/serve.py 9000      # ...on another port

⛔ **Why this exists.** `python -m http.server` answers a `Range:` request with
the WHOLE file and a `200 OK`. Browsers need `206 Partial Content` to play video:
Safari will not start a video at all without it, and Chrome can load one but
cannot seek in it. So the reels can look broken on `localhost` while being
perfectly fine once published — GitHub Pages serves ranges correctly.

⭐ This removes that difference, so what you see locally is what you ship. It
also sends `Cache-Control: no-store`, so an edit to `index.html` shows up on
reload instead of two reloads later.
"""
from __future__ import annotations

import os
import re
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

#: `bytes=0-1023`, `bytes=1024-` and `bytes=-512` (the last 512 bytes).
RANGE = re.compile(r"bytes=(\d*)-(\d*)\s*$")
CHUNK = 64 * 1024


class RangeHandler(SimpleHTTPRequestHandler):
    _sent_range_headers = False

    def end_headers(self):
        if not self._sent_range_headers:
            self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):                                    # noqa: N802
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or os.path.isdir(path):
            return super().do_GET()
        m = RANGE.match(rng.strip())
        if not m:
            return super().do_GET()                      # not a form we handle
        try:
            f = open(path, "rb")
        except OSError:
            return self.send_error(404, "File not found")
        with f:
            size = os.fstat(f.fileno()).st_size
            first, last = m.group(1), m.group(2)
            if first == "":                              # suffix: last N bytes
                n = int(last or 0)
                start, end = max(size - n, 0), size - 1
            else:
                start = int(first)
                end = int(last) if last else size - 1
            if start >= size:
                self._sent_range_headers = True
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            end = min(end, size - 1)
            length = end - start + 1

            self._sent_range_headers = True
            self.send_response(206)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(length))
            self.end_headers()

            f.seek(start)
            left = length
            while left > 0:
                buf = f.read(min(CHUNK, left))
                if not buf:
                    break
                try:
                    self.wfile.write(buf)
                except (BrokenPipeError, ConnectionResetError):
                    return                               # the player seeked away
                left -= len(buf)

    def log_message(self, fmt, *args):                   # quieter than default
        if "304" not in fmt % args:
            super().log_message(fmt, *args)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8731
    root = os.path.dirname(os.path.abspath(__file__))
    handler = partial(RangeHandler, directory=root)
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"showcase → http://localhost:{port}  (serving {root}, ranges on)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
