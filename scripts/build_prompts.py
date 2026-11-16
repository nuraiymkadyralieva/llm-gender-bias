"""Erzeugt aus Profilen und Vorlagen alle Prompts (prompts/prompts.jsonl).

Pruefung: Die drei Varianten (w/m/n) eines Profils unterscheiden sich
ausschliesslich in der Selbstbeschreibung. Andernfalls bricht das Skript ab.

Aufruf:  python scripts/build_prompts.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARIANTEN = ["w", "m", "n"]


def main():
    profile = json.loads((ROOT / "profiles/profiles.json").read_text(encoding="utf-8"))
    vorlagen = json.loads((ROOT / "prompts/templates.json").read_text(encoding="utf-8"))
    prompts = []

    for p in profile["studienwahl"]:
        v = vorlagen["studienwahl"]
        texte = {}
        for var in VARIANTEN:
            selbst = v["selbst"][var]
            texte[var] = (selbst, v["text"].format(selbst=selbst, **p))
        prompts += pruefen_und_sammeln(p, "studienwahl", texte)

    for p in profile["beruf"]:
        v = vorlagen["beruf"]
        texte = {}
        for var in VARIANTEN:
            selbst = p["selbst"][var]
            texte[var] = (selbst, v["text"].format(
                selbst=selbst, abschluss=p["abschluss"],
                erfahrung=p["erfahrung"], note=p["note"]))
        prompts += pruefen_und_sammeln(p, "beruf", texte)

    ziel = ROOT / "prompts/prompts.jsonl"
    with ziel.open("w", encoding="utf-8") as f:
        for z in prompts:
            f.write(json.dumps(z, ensure_ascii=False) + "\n")
    print(f"{len(prompts)} Prompts geschrieben nach {ziel.relative_to(ROOT)}")


def pruefen_und_sammeln(profil, szenario, texte):
    # Rest des Prompts ohne Selbstbeschreibung muss bei allen Varianten identisch sein
    reste = {var: t.replace(s, "", 1) for var, (s, t) in texte.items()}
    if len(set(reste.values())) != 1:
        raise SystemExit(f"Varianten von {profil['id']} unterscheiden sich nicht nur in der Selbstbeschreibung!")
    return [{
        "prompt_id": f"{profil['id']}-{var}",
        "profile_id": profil["id"],
        "scenario": szenario,
        "variant": var,
        "typ": profil["typ"],
        "prompt": t,
    } for var, (s, t) in texte.items()]


if __name__ == "__main__":
    main()
