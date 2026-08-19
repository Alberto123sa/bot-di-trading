#!/usr/bin/env python3
import base64, gzip, hashlib, json, pathlib, sys, urllib.request

OWNER = "Alberto123sa"
REPO = "bot-di-trading"
BLOB_SHA = "4d377f60e56f55dd92f2b0da3813ec7c3ce6b387"
OUT = pathlib.Path("mexc_global_spot_opportunity_router_demo_v11_0_0.py")
EXPECTED_GZ_SHA256 = "3ad5b5d7343d48fd21f9b79194180f6fe13cd7407b9263e63c76e2549252fc3d"
EXPECTED_PY_SHA256 = "4390131f45f1e1f650a07c9bf51983cdb486703dc701dfe87e06b6498c6de21c"
EXPECTED_PY_SIZE = 60696

url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/blobs/{BLOB_SHA}"
req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"V11-installer"})
with urllib.request.urlopen(req, timeout=30) as r:
    payload = json.load(r)
raw = base64.b64decode(payload["content"].replace("\n", ""))

gz_sha = hashlib.sha256(raw).hexdigest()
if gz_sha != EXPECTED_GZ_SHA256:
    raise SystemExit(f"ERRORE SHA gzip: {gz_sha}")

src = gzip.decompress(raw)
py_sha = hashlib.sha256(src).hexdigest()
if len(src) != EXPECTED_PY_SIZE:
    raise SystemExit(f"ERRORE dimensione sorgente: {len(src)}")
if py_sha != EXPECTED_PY_SHA256:
    raise SystemExit(f"ERRORE SHA sorgente: {py_sha}")

OUT.write_bytes(src)
print(f"OK scritto: {OUT}")
print(f"SIZE: {len(src)}")
print(f"SHA256: {py_sha}")
