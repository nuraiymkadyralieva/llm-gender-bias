"""Datenerhebung: sendet alle Prompts an alle Modelle und speichert die Rohantworten.

- Jede Antwort wird sofort als eine Zeile in data/raw/responses.jsonl angehaengt.
- Bereits erhobene Kombinationen (Modell, Prompt, Wiederholung) werden uebersprungen;
  ein abgebrochener Lauf kann also einfach neu gestartet werden.
- Die Reihenfolge der Aufrufe wird mit festem Seed gemischt, damit Varianten
  nicht systematisch zu unterschiedlichen Zeitpunkten abgefragt werden.

API-Schluessel: Umgebungsvariable OPENROUTER_API_KEY (oder Datei .env, nie committen).

Beispiele:
  python scripts/collect.py --dry-run                         # nur zaehlen, nichts senden
  python scripts/collect.py --profiles S01,S10,B03 --reps 2 --out data/raw/pilot.jsonl
  python scripts/collect.py                                   # Hauptlauf laut config.json
"""
import argparse
import json
import os
import random
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
lock = threading.Lock()


def lade_env():
    env = ROOT / ".env"
    if env.exists():
        for zeile in env.read_text(encoding="utf-8").splitlines():
            if "=" in zeile and not zeile.strip().startswith("#"):
                k, v = zeile.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def bereits_erledigt(pfad):
    erledigt = set()
    if pfad.exists():
        for zeile in pfad.read_text(encoding="utf-8").splitlines():
            if zeile.strip():
                d = json.loads(zeile)
                # abgeschnittene Antworten (finish_reason "length") werden erneut abgefragt
                if d.get("status") == "ok" and d.get("finish_reason") != "length":
                    erledigt.add((d["model_key"], d["prompt_id"], d["repetition"]))
    return erledigt


def aufruf(cfg, modell, prompt, schluessel):
    body = {"model": modell["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": cfg["max_tokens"]}
    if cfg.get("temperature") is not None:
        body["temperature"] = cfg["temperature"]
    body.update(modell.get("extra", {}))
    for versuch in range(5):
        try:
            r = requests.post(cfg["api_url"], json=body, timeout=180,
                              headers={"Authorization": f"Bearer {schluessel}"})
            if r.status_code == 200:
                return body, r.json(), None
            fehler = f"HTTP {r.status_code}: {r.text[:500]}"
            if r.status_code in (400, 401, 403, 404):
                return body, None, fehler  # Konfigurationsfehler: nicht wiederholen
        except requests.RequestException as e:
            fehler = str(e)
        time.sleep(2 ** versuch * 3)
    return body, None, fehler


def bearbeite(auftrag, cfg, schluessel, ziel):
    modell, p, wdh = auftrag
    start = datetime.now(timezone.utc).isoformat()
    body, antwort, fehler = aufruf(cfg, modell, p["prompt"], schluessel)
    datensatz = {
        "run_id": uuid.uuid4().hex[:12],
        "timestamp": start,
        "model_key": modell["key"],
        "model_requested": modell["model"],
        "request_params": {k: v for k, v in body.items() if k != "messages"},
        "prompt_id": p["prompt_id"], "profile_id": p["profile_id"],
        "scenario": p["scenario"], "variant": p["variant"], "typ": p["typ"],
        "repetition": wdh,
        "prompt": p["prompt"],
        "status": "ok" if antwort else "fehler",
    }
    if antwort:
        wahl = antwort["choices"][0]
        datensatz.update({
            "model_returned": antwort.get("model"),
            "provider_returned": antwort.get("provider"),
            "response_id": antwort.get("id"),
            "finish_reason": wahl.get("finish_reason"),
            "response_text": wahl["message"].get("content"),
            "usage": antwort.get("usage"),
        })
    else:
        datensatz["error"] = fehler
    with lock:
        with ziel.open("a", encoding="utf-8") as f:
            f.write(json.dumps(datensatz, ensure_ascii=False) + "\n")
    print(f"{datensatz['status']:6} {modell['key']:10} {p['prompt_id']:6} Wdh.{wdh}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", help="nur diese Profil-IDs, z. B. S01,B03")
    ap.add_argument("--models", help="nur diese Modell-Keys, z. B. openai,google")
    ap.add_argument("--reps", type=int, help="Wiederholungen (ueberschreibt config)")
    ap.add_argument("--out", default="data/raw/responses.jsonl")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    lade_env()
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    prompts = [json.loads(z) for z in (ROOT / "prompts/prompts.jsonl").read_text(encoding="utf-8").splitlines() if z.strip()]
    if args.profiles:
        auswahl = set(args.profiles.split(","))
        prompts = [p for p in prompts if p["profile_id"] in auswahl]
    modelle = cfg["modelle"]
    if args.models:
        modelle = [m for m in modelle if m["key"] in args.models.split(",")]
    reps = args.reps or cfg["repetitions"]

    ziel = ROOT / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    erledigt = bereits_erledigt(ziel)
    auftraege = [(m, p, w) for m in modelle for p in prompts for w in range(1, reps + 1)
                 if (m["key"], p["prompt_id"], w) not in erledigt]
    random.Random(cfg["seed_reihenfolge"]).shuffle(auftraege)

    print(f"{len(auftraege)} offene Aufrufe ({len(erledigt)} bereits erledigt) -> {args.out}")
    if args.dry_run:
        return
    schluessel = os.environ.get("OPENROUTER_API_KEY")
    if not schluessel:
        raise SystemExit("OPENROUTER_API_KEY fehlt (Umgebungsvariable oder .env).")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(bearbeite, a, cfg, schluessel, ziel) for a in auftraege]
        for fut in futures:
            if fut.exception():  # unerwartete Fehler sichtbar machen statt sie zu verschlucken
                print("FEHLER:", repr(fut.exception()))


if __name__ == "__main__":
    main()
