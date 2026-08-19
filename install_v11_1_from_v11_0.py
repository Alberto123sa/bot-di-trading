#!/usr/bin/env python3
import hashlib, pathlib, shutil, subprocess, sys, tempfile, urllib.request

BASE = pathlib.Path("mexc_global_spot_opportunity_router_demo_v11_0_0.py")
OUT = pathlib.Path("mexc_global_spot_opportunity_router_demo_v11_1_0.py")
PATCH_URL = "https://raw.githubusercontent.com/Alberto123sa/bot-di-trading/main/v1100_to_v1110.patch"
BASE_SIZE = 60696
BASE_SHA = "4390131f45f1e1f650a07c9bf51983cdb486703dc701dfe87e06b6498c6de21c"
OUT_SIZE = 72108
OUT_SHA = "40a7a71d7ddc72dcb4cbc4c3bee89db9c3f732f6a06aacc7d9f590d628642db8"

def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

if not BASE.exists():
    raise SystemExit(f"ERRORE: manca {BASE}")
if BASE.stat().st_size != BASE_SIZE or sha256(BASE) != BASE_SHA:
    raise SystemExit("ERRORE: V11.0.0 di base non coincide con la versione verificata. Nessun file modificato.")

req = urllib.request.Request(PATCH_URL + "?nocache=202608191020", headers={"User-Agent":"V11.1-installer"})
with urllib.request.urlopen(req, timeout=30) as r:
    patch_bytes = r.read()
if not patch_bytes.startswith(b"--- mexc_global_spot_opportunity_router_demo_v11_0_0.py"):
    raise SystemExit("ERRORE: patch GitHub non valida.")

with tempfile.TemporaryDirectory() as td:
    td = pathlib.Path(td)
    work = td / OUT.name
    pf = td / "v1100_to_v1110.patch"
    shutil.copy2(BASE, work)
    pf.write_bytes(patch_bytes)
    cp = subprocess.run(["patch", "-s", str(work), "-i", str(pf)], text=True, capture_output=True)
    if cp.returncode != 0:
        raise SystemExit("ERRORE applicazione patch:\n" + cp.stdout + cp.stderr)
    size = work.stat().st_size
    digest = sha256(work)
    print(f"PATCH ricevuta: {len(patch_bytes)} bytes")
    print(f"V11.1 candidata: {size} bytes | {digest}")
    if size != OUT_SIZE or digest != OUT_SHA:
        raise SystemExit("ERRORE: V11.1 finale non coincide byte-per-byte. Nessun file scritto.")
    shutil.copy2(work, OUT)

print("INSTALLAZIONE V11.1.0 SUPERATA")
print(f"FILE: {OUT}")
print(f"SIZE: {OUT.stat().st_size}")
print(f"SHA256: {sha256(OUT)}")
