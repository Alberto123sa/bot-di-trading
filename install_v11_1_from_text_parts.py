#!/usr/bin/env python3
import base64, gzip, hashlib, pathlib, subprocess, sys, urllib.request

BASE = "https://raw.githubusercontent.com/Alberto123sa/bot-di-trading/main/v11_1_0_payload"
OUT = pathlib.Path("mexc_global_spot_opportunity_router_demo_v11_1_0.py")
EXPECTED_B64_LEN = 25088
EXPECTED_B64_SHA = "b0ce3b51b55e44ec2bae0cf7c620e8c25ea21edd44cc394df2ec47f1243d29dd"
EXPECTED_GZ_LEN = 18816
EXPECTED_GZ_SHA = "f73f6059ea55ee9047fb98f60ac74a9c6cddef55bca40042e9f207f367eb2c93"
EXPECTED_PY_LEN = 76735
EXPECTED_PY_SHA = "25b8b373fa840dd02f1a1b36c12c891643b690c7d1ef74e74cdb8157375417df"

parts = []
for i in range(13):
    url = f"{BASE}/part{i:02d}.txt?nocache=202608191047"
    req = urllib.request.Request(url, headers={"User-Agent": "V11.1-single-installer"})
    with urllib.request.urlopen(req, timeout=30) as r:
        parts.append(r.read().decode("ascii").strip())

b64 = "".join(parts)
b64_sha = hashlib.sha256(b64.encode("ascii")).hexdigest()
if len(b64) != EXPECTED_B64_LEN or b64_sha != EXPECTED_B64_SHA:
    raise SystemExit(f"ERRORE PAYLOAD BASE64: {len(b64)} | {b64_sha}")

raw = base64.b64decode(b64, validate=True)
gz_sha = hashlib.sha256(raw).hexdigest()
if len(raw) != EXPECTED_GZ_LEN or gz_sha != EXPECTED_GZ_SHA:
    raise SystemExit(f"ERRORE PAYLOAD GZIP: {len(raw)} | {gz_sha}")

src = gzip.decompress(raw)
py_sha = hashlib.sha256(src).hexdigest()
if len(src) != EXPECTED_PY_LEN or py_sha != EXPECTED_PY_SHA:
    raise SystemExit(f"ERRORE SORGENTE: {len(src)} | {py_sha}")
if b'VERSION = "11.1.0"' not in src:
    raise SystemExit("ERRORE: il sorgente non dichiara VERSION 11.1.0")

OUT.write_bytes(src)
try:
    subprocess.run([sys.executable, "-m", "py_compile", str(OUT)], check=True)
    p = subprocess.run([sys.executable, str(OUT), "--self-test"], check=True, text=True, capture_output=True)
except Exception:
    OUT.unlink(missing_ok=True)
    raise

print("INSTALLAZIONE V11.1.0 SUPERATA")
print(f"FILE: {OUT}")
print(f"SIZE: {len(src)}")
print(f"SHA256: {py_sha}")
print(p.stdout.strip())
