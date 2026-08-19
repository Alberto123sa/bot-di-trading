#!/usr/bin/env python3
import base64, gzip, hashlib, pathlib, urllib.request

BASE = "https://raw.githubusercontent.com/Alberto123sa/bot-di-trading/main/v11_1_0_payload"
OUT = pathlib.Path("mexc_global_spot_opportunity_router_demo_v11_1_0.py")
EXPECTED_B64_LEN = 25088
EXPECTED_B64_SHA = "b0ce3b51b55e44ec2bae0cf7c620e8c25ea21edd44cc394df2ec47f1243d29dd"
EXPECTED_GZ_LEN = 18816
EXPECTED_GZ_SHA = "f73f6059ea55ee9047fb98f60ac74a9c6cddef55bca40042e9f207f367eb2c93"
EXPECTED_PY_LEN = 72108
EXPECTED_PY_SHA = "40a7a71d7ddc72dcb4cbc4c3bee89db9c3f732f6a06aacc7d9f590d628642db8"

parts = []
for i in range(13):
    url = f"{BASE}/part{i:02d}.txt?nocache=202608191035"
    req = urllib.request.Request(url, headers={"User-Agent": "V11.1-text-parts-installer"})
    with urllib.request.urlopen(req, timeout=30) as r:
        part = r.read().decode("ascii").strip()
    print(f"part{i:02d}: {len(part)} chars")
    parts.append(part)

b64 = "".join(parts)
b64_sha = hashlib.sha256(b64.encode("ascii")).hexdigest()
print(f"BASE64: {len(b64)} chars | {b64_sha}")
if len(b64) != EXPECTED_B64_LEN or b64_sha != EXPECTED_B64_SHA:
    raise SystemExit("ERRORE: payload BASE64 non coincide. Nessun file scritto.")

raw = base64.b64decode(b64, validate=True)
gz_sha = hashlib.sha256(raw).hexdigest()
print(f"GZIP: {len(raw)} bytes | {gz_sha}")
if len(raw) != EXPECTED_GZ_LEN or gz_sha != EXPECTED_GZ_SHA:
    raise SystemExit("ERRORE: payload GZIP non coincide. Nessun file scritto.")

src = gzip.decompress(raw)
py_sha = hashlib.sha256(src).hexdigest()
print(f"PYTHON: {len(src)} bytes | {py_sha}")
if len(src) != EXPECTED_PY_LEN or py_sha != EXPECTED_PY_SHA:
    raise SystemExit("ERRORE: sorgente Python non coincide. Nessun file scritto.")

OUT.write_bytes(src)
print("INSTALLAZIONE V11.1.0 SUPERATA")
print(f"FILE: {OUT}")
print(f"SIZE: {len(src)}")
print(f"SHA256: {py_sha}")
