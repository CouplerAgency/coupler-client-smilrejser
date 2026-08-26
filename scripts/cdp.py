#!/usr/bin/env python3
"""
Minimal Chrome DevTools Protocol driver — standard library only.

Why this exists. Three cheaper approaches were tried and all failed:

  * `--screenshot` with old `--headless`: cannot suppress the Cookiebot modal, whose
    dark backdrop dims the whole viewport, so every shot misrepresents the page.
  * `--load-extension`: silently ignored by old headless Chrome.
  * `--headless=new` with an extension: hangs indefinitely on this machine (the same
    reason the bundled shot.sh avoids it).

CDP solves it properly and is required anyway for the booking-funnel walkthrough,
which needs clicking, typing and multi-step navigation. No pip install, so this ships
a small WebSocket client: a handshake, masked client frames, and a read loop.
"""

import base64
import json
import os
import re
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request

CHROME = os.environ.get(
    "CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


class WS:
    """Just enough RFC 6455 to talk to Chrome on loopback."""

    def __init__(self, url, timeout=40):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", url)
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            "GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\n"
            "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n" % (path, host, port, key)
        )
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        if b"101" not in buf.split(b"\r\n")[0]:
            raise RuntimeError("websocket handshake failed: %r" % buf[:120])
        self.buf = buf.split(b"\r\n\r\n", 1)[1]

    def send(self, payload):
        data = payload.encode()
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        n = len(data)
        if n < 126:
            hdr = struct.pack("!BB", 0x81, 0x80 | n)
        elif n < 65536:
            hdr = struct.pack("!BBH", 0x81, 0xFE, n)
        else:
            hdr = struct.pack("!BBQ", 0x81, 0xFF, n)
        self.sock.sendall(hdr + mask + masked)

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("socket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        while True:
            b0, b1 = struct.unpack("!BB", self._read(2))
            opcode = b0 & 0x0F
            length = b1 & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._read(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._read(8))[0]
            payload = self._read(length)
            if opcode == 0x1:
                return payload.decode("utf-8", "replace")
            if opcode == 0x8:
                raise RuntimeError("websocket closed by peer")
            # ignore ping/pong/continuation

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


class Browser:
    def __init__(self, width=1440, height=1400, lang="da-DK", port=9333,
                 mobile=False):
        self.profile = tempfile.mkdtemp(prefix="smilcdp.")
        self.port = port
        self.width, self.height, self.mobile = width, height, mobile
        args = [
            CHROME, "--headless", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
            "--disable-features=Translate", "--mute-audio",
            "--lang=%s" % lang, "--accept-lang=%s,da" % lang,
            "--user-data-dir=%s" % self.profile,
            "--remote-debugging-port=%d" % port,
            "--window-size=%d,%d" % (width, height),
            "about:blank",
        ]
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        self.ws = None
        self._id = 0
        self._connect()

    def _connect(self):
        url = None
        for _ in range(60):
            time.sleep(0.4)
            try:
                raw = urllib.request.urlopen(
                    "http://127.0.0.1:%d/json/list" % self.port, timeout=3).read()
                for t in json.loads(raw):
                    if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                        url = t["webSocketDebuggerUrl"]
                        break
                if url:
                    break
            except Exception:
                continue
        if not url:
            raise RuntimeError("could not reach Chrome DevTools on port %d" % self.port)
        self.ws = WS(url)
        self.cmd("Page.enable")
        self.cmd("Runtime.enable")
        self.cmd("Network.enable")
        self.cmd("Emulation.setDeviceMetricsOverride", {
            "width": self.width, "height": self.height,
            "deviceScaleFactor": 1, "mobile": self.mobile})
        # Pre-consent so Cookiebot never renders. Cheaper and more reliable than
        # clicking the banner on every page load.
        stamp = ("{stamp:'audit',necessary:true,preferences:true,statistics:true,"
                 "marketing:true,method:'explicit',ver:1}")
        for dom in (".smilrejser.dk", "smilrejser.dk"):
            self.cmd("Network.setCookie", {
                "name": "CookieConsent", "value": stamp, "domain": dom,
                "path": "/", "expires": time.time() + 31536000})
        # Belt and braces: strip the dialog on every document, in case consent
        # is versioned and the cookie is rejected.
        self.cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """
            (function(){
              var css='#CybotCookiebotDialog,#CybotCookiebotDialogBodyUnderlay,'+
                      '#CookiebotWidget,[id^="CybotCookiebotDialog"]'+
                      '{display:none!important;visibility:hidden!important}'+
                      'html,body{overflow:visible!important}';
              var add=function(){
                if(document.head&&!document.getElementById('__audit')){
                  var s=document.createElement('style');
                  s.id='__audit';s.textContent=css;document.head.appendChild(s);
                }
              };
              add();
              new MutationObserver(add).observe(document.documentElement,
                {childList:true,subtree:true});
            })();
        """})

    def cmd(self, method, params=None, timeout=45):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method,
                                 "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError("%s: %s" % (method, msg["error"]))
                return msg.get("result", {})
        raise RuntimeError("timeout waiting for %s" % method)

    def goto(self, url, settle=3.0):
        self.cmd("Page.navigate", {"url": url})
        # Poll readyState rather than trusting a fixed sleep: this is a Next.js
        # App Router site and sections hydrate after the load event.
        deadline = time.time() + 30
        while time.time() < deadline:
            time.sleep(0.5)
            try:
                if self.eval("document.readyState") == "complete":
                    break
            except Exception:
                pass
        time.sleep(settle)

    def eval(self, expr):
        r = self.cmd("Runtime.evaluate",
                     {"expression": expr, "returnByValue": True,
                      "awaitPromise": True})
        return r.get("result", {}).get("value")

    def shot(self, path, full=False):
        params = {"format": "png"}
        if full:
            params["captureBeyondViewport"] = True
        r = self.cmd("Page.captureScreenshot", params, timeout=90)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["data"]))
        return os.path.getsize(path)

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        finally:
            self.proc.kill()
            self.proc.wait(timeout=10)
            subprocess.run(["rm", "-rf", self.profile], check=False)
