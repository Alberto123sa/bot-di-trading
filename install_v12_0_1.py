#!/usr/bin/env python3
import base64, gzip, hashlib, pathlib, subprocess, sys, urllib.request

URL = "https://raw.githubusercontent.com/Alberto123sa/bot-di-trading/main/v12_0_1_payload_verified.txt?nocache=202608191150"
OUT = pathlib.Path("mexc_global_depth_capital_router_demo_v12_0_1.py")
EXPECTED_B64_LEN = 23064
EXPECTED_B64_SHA = "b280d4cf2a06755f32816fc1269abb29e5184f06d925e69e73df57f1da9cffe5"
EXPECTED_GZ_LEN = 17297
EXPECTED_GZ_SHA = "f5b800bc4dbb6d6d7d55cfac51c3be2604a41593fd4868580f93ff2cbc588527"
EXPECTED_PY_LEN = 69791
EXPECTED_PY_SHA = "d269b3a280214894038c0dc1585b4753da6d64d12d101a95a16611f1d86b923b"

req = urllib.request.Request(URL, headers={"User-Agent": "V12.0.1-installer"})
with urllib.request.urlopen(req, timeout=30) as r:
    b64 = r.read().decode("ascii").strip()

b64_sha = hashlib.sha256(b64.encode("ascii")).hexdigest()
if len(b64) != EXPECTED_B64_LEN or b64_sha != EXPECTED_B64_SHA:
    raise SystemExit(f"ERRORE BASE64: {len(b64)} | {b64_sha}")

raw = base64.b64decode(b64, validate=True)
gz_sha = hashlib.sha256(raw).hexdigest()
if len(raw) != EXPECTED_GZ_LEN or gz_sha != EXPECTED_GZ_SHA:
    raise SystemExit(f"ERRORE GZIP: {len(raw)} | {gz_sha}")

src = gzip.decompress(raw)
py_sha = hashlib.sha256(src).hexdigest()
if len(src) != EXPECTED_PY_LEN or py_sha != EXPECTED_PY_SHA:
    raise SystemExit(f"ERRORE PYTHON: {len(src)} | {py_sha}")
if b'VERSION = "12.0.1"' not in src:
    raise SystemExit("ERRORE VERSIONE: attesa V12.0.1")

OUT.write_bytes(src)
try:
    subprocess.run([sys.executable, "-m", "py_compile", str(OUT)], check=True)
    p = subprocess.run([sys.executable, str(OUT), "--self-test"], check=True, text=True, capture_output=True)
except Exception:
    OUT.unlink(missing_ok=True)
    raise

print("INSTALLAZIONE V12.0.1 SUPERATA")
print(f"FILE: {OUT}")
print(f"SIZE: {len(src)}")
print(f"SHA256: {py_sha}")
print(p.stdout.strip())
