#!/usr/bin/env python3
from pathlib import Path
import hashlib, py_compile, shutil, sys

TARGET = Path.home() / "mexc_camaleonte_adaptive_portfolio_demo" / "mexc_camaleonte_adaptive_portfolio_demo_v2.py"
OLD_SHA = "789e4b9e202242cd38d49049d61319b455d342f4d5e6d9d4ae9731f28632c6c1"
NEW_SHA = "b65c030025f1e4f01bb796d1043ac8dce27865b11abe6b70b40e3d4ad1bacd84"
NEW_FUNCTION = 'def apply_funding(client: PublicMexcClient, state: Dict[str, Any],\n                  tickers: Dict[str, Dict[str, Any]]) -> None:\n    now = time.time()\n    if now - safe_float(state.get("last_funding_check_epoch")) < FUNDING_CHECK_SECONDS:\n        return\n    state["last_funding_check_epoch"] = now\n    open_symbols = sorted({\n        str(leg.get("symbol"))\n        for idea in state.get("ideas", {}).values()\n        for leg in idea.get("legs", [])\n        if safe_float(leg.get("qty")) > 0\n    })\n    last_settlements = state.setdefault("last_funding_settlement", {})\n    for symbol in open_symbols:\n        try:\n            history = client.funding_history(symbol, 30)\n        except Exception as exc:\n            log(f"Funding history {symbol} non disponibile: {exc}", "WARNING")\n            continue\n        last_seen = int(safe_float(last_settlements.get(symbol)))\n        settlements_by_time: Dict[int, float] = {}\n        for row in history:\n            ts = int(safe_float(row.get("settleTime") or row.get("timestamp") or row.get("time")))\n            rate = safe_float(row.get("fundingRate"))\n            if ts > 10_000_000_000:\n                ts //= 1000\n            if ts > last_seen and ts <= int(now) + 60:\n                settlements_by_time[ts] = rate\n        for ts, rate in sorted(settlements_by_time.items()):\n            for idea in state.get("ideas", {}).values():\n                idea_funding = 0.0\n                idea_entry = safe_float(idea.get("entry_time_epoch"), now)\n                for leg in idea.get("legs", []):\n                    if leg.get("symbol") != symbol or safe_float(leg.get("qty")) <= 0:\n                        continue\n                    opened_at = safe_float(leg.get("opened_at_epoch"), idea_entry)\n                    if ts <= int(opened_at):\n                        continue\n                    ticker = tickers.get(symbol)\n                    if not ticker:\n                        continue\n                    notional = leg_mark(leg, ticker)["current_notional"]\n                    pnl = -side_sign(str(leg["side"])) * notional * rate\n                    idea_funding += pnl\n                    append_csv(LEGS_CSV, CSV_LEG_FIELDS, {\n                        "timestamp_utc": utc_iso(), "idea_id": idea["idea_id"], "event": "FUNDING",\n                        "module": idea["module"], "symbol": symbol, "side": leg["side"],\n                        "qty": f"{safe_float(leg.get(\'qty\')):.12f}", "price": "", "notional": f"{notional:.6f}",\n                        "gross_pnl": "0", "fee": "0", "funding_pnl": f"{pnl:.6f}",\n                        "reason": f"settlement={utc_iso(ts)} rate={rate:+.6%}",\n                    })\n                if abs(idea_funding) > 0:\n                    idea["funding_pnl"] = safe_float(idea.get("funding_pnl")) + idea_funding\n                    state["cash"] = safe_float(state.get("cash")) + idea_funding\n                    state["funding_total"] = safe_float(state.get("funding_total")) + idea_funding\n                    log(f"[FUNDING DEMO] idea={idea[\'idea_id\']} {symbol} rate={rate:+.6%} pnl={idea_funding:+.5f}")\n            last_settlements[symbol] = ts\n\n\n# =============================================================================\n# GESTIONE DINAMICA DELLE IDEE\n# ============================================================================='

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

if not TARGET.exists():
    sys.exit(f"ERRORE: file V2 non trovato: {TARGET}")
current = sha(TARGET)
print(f"SHA_ATTUALE={current}")
if current == NEW_SHA:
    print("PATCH_GIA_APPLICATA=OK")
    raise SystemExit(0)
if current != OLD_SHA:
    sys.exit("ERRORE: versione V2 inattesa; nessuna modifica eseguita.")
text = TARGET.read_text(encoding="utf-8")
start = text.find("def apply_funding(")
end = text.find("\ndef ", start + 10)
if start < 0 or end < 0:
    sys.exit("ERRORE: blocco apply_funding non individuato.")
backup = TARGET.with_suffix(".py.pre_funding_fix")
shutil.copy2(TARGET, backup)
TARGET.write_text(text[:start] + NEW_FUNCTION + text[end:], encoding="utf-8")
try:
    py_compile.compile(str(TARGET), doraise=True)
except Exception as exc:
    shutil.copy2(backup, TARGET)
    sys.exit(f"ERRORE_COMPILAZIONE={exc}; backup ripristinato")
final = sha(TARGET)
print(f"SHA_NUOVO={final}")
if final != NEW_SHA:
    shutil.copy2(backup, TARGET)
    sys.exit("ERRORE: SHA finale errato; backup ripristinato")
print(f"BACKUP={backup}")
print("PATCH_FUNDING=OK")
print("COMPILAZIONE=0")
