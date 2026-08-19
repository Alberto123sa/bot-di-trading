#!/usr/bin/env python3
import base64, gzip, hashlib, pathlib, urllib.request

BASE = "https://raw.githubusercontent.com/Alberto123sa/bot-di-trading/main/v11_0_0_payload"
OUT = pathlib.Path("mexc_global_spot_opportunity_router_demo_v11_0_0.py")
EXPECTED_B64_LEN = 20876
EXPECTED_B64_SHA = "cba7ff4e17d692935056d9f5fbce8cbded7747595a21b44ef6d11d0adf5d0b48"
EXPECTED_GZ_LEN = 15657
EXPECTED_GZ_SHA = "cf9bb5dc467c48aba746a818994bf9ff51a287c231047fb884a1a5db9badf61d"
EXPECTED_PY_LEN = 60696
EXPECTED_PY_SHA = "4390131f45f1e1f650a07c9bf51983cdb486703dc701dfe87e06b6498c6de21c"

parts = []
for i in range(11):
    url = f"{BASE}/part{i:02d}.txt?nocache=202608190934"
    req = urllib.request.Request(url, headers={"User-Agent": "V11-text-parts-installer"})
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
print("INSTALLAZIONE V11.0.0 SUPERATA")
print(f"FILE: {OUT}")
print(f"SIZE: {len(src)}")
print(f"SHA256: {py_sha}")
