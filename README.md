# Geschlechter-Bias in großen Sprachmodellen bei Karriereempfehlungen

Daten, Skripte und Kodierunterlagen zur wissenschaftlichen Arbeit von N. Kadyralieva
(Westsächsische Hochschule Zwickau, Modul Wissenschaftliches Arbeiten, WS 2026/27,
Betreuer: Prof. Dr. R. Laue).

## Design in Kürze
- 20 künstliche Profile: 10 zur Studienwahl (S01–S10), 10 zu Berufsentscheidungen nach dem Studium (B01–B10)
- je drei Varianten, die sich nur in der Selbstbeschreibung unterscheiden: weiblich (`w`),
  männlich (`m`), ohne Geschlechtsangabe (`n`); das Geschlecht wird über die grammatische Form angegeben
- drei Sprachmodelle verschiedener Anbieter über die OpenRouter-API, fünf Wiederholungen je Prompt
  (3 × 60 × 5 = 900 Abfragen, 4.500 Empfehlungen)
- jede Antwort: fünf Empfehlungen in Rangfolge mit kurzer Begründung (JSON)

## Ablauf
```bash
pip install -r requirements.txt
cp .env.example .env                    # OPENROUTER_API_KEY eintragen (nicht einchecken)

python scripts/build_prompts.py         # profiles + templates -> prompts/prompts.jsonl
python scripts/collect.py --dry-run     # zeigt die Zahl der offenen Aufrufe
python scripts/collect.py               # Datenerhebung -> data/raw/responses.jsonl
python scripts/parse.py                 # -> data/processed/recommendations.csv

# Kodierung Beruf (KldB 2010, Fassung 2020)
python scripts/kodiere_beruf_auto.py    # exakter Abgleich mit dem BA-Verzeichnis
python scripts/erzeuge_kodierblatt.py   # Arbeitsblatt + Prüfstichproben
python scripts/vorkodierung_analogie.py # Analogieregeln + Entscheidungen der Autorin
python scripts/finalisiere_beruf.py     # -> codebook/beruf_codes.csv

# Kodierung Studienwahl (Destatis-Fächersystematik)
python scripts/kodiere_studium_auto.py
python scripts/kodiere_studium_regeln.py # -> codebook/studium_codes.csv

# Auswertung
python scripts/analyse.py               # Kennzahlen, Jaccard, Tests (+ Holm) -> results/tables/
python scripts/analyse.py --ohne-feld   # Robustheitsprüfung ohne Tätigkeitsfeld-Analogien
python scripts/analyse_rang.py          # FF1: Rangpositionen
python scripts/analyse_begruendungen.py # FF3: sprachliche Kategorien
python scripts/trennschaerfe.py         # Trennschärfe des Designs (Resampling)
python scripts/abbildungen.py           # Abbildungen -> results/figures/
```
Pilot: `python scripts/collect.py --profiles S01,S10,B03 --reps 2 --out data/raw/pilot.jsonl`

## Verzeichnisse
| Ordner | Inhalt |
|---|---|
| `profiles/` | Profile (unveränderliche Grundlage) |
| `prompts/` | Vorlagen und erzeugte Prompts |
| `scripts/` | Erhebung, Kodierung, Auswertung, Abbildungen |
| `data/raw/` | Rohantworten, unverändert (`responses.jsonl`, `pilot.jsonl`) |
| `data/processed/` | aufbereitete Tabellen |
| `codebook/` | Kodierregeln, Kodiertabellen, Prüfstichproben, amtliche Verzeichnisse (`quellen/`) |
| `results/tables/`, `results/figures/` | Tabellen und Abbildungen der Arbeit |

## Kodierung
`codebook/kodierregeln.md` enthält die sechs Kodierregeln, das Vorgehen je Situation und die
Ergebnisse der drei Prüfstichproben. Die Analogieregeln stehen vollständig in
`scripts/analogieregeln.py` (Beruf) und `scripts/analogieregeln_studium.py` (Studienwahl);
die Codes werden daraus nicht fest eingetragen, sondern bei jedem Lauf aus den amtlichen
Verzeichnissen in `codebook/quellen/` nachgeschlagen.

## Dokumentation der Erhebung
| Lauf | Datum | Modelle (angefragt → zurückgemeldet) | Parameter | Bemerkungen |
|---|---|---|---|---|
| Pilot | 15.11.2026 | `openai/gpt-6.1-terra` → `openai/gpt-6.1-terra`; `anthropic/claude-sonnet-5-5` → `anthropic/claude-sonnet-5.5`; `google/gemini-4-hydrogen` → `google/gemini-4-hydrogen` | temperature: Standardwert des Anbieters, `reasoning: minimal`, `max_tokens` 1.500 | 54 Abfragen, 3 Profile × 2 Wiederholungen; 6 Antworten von Gemini 4 wegen `finish_reason: length` abgeschnitten → `max_tokens` auf 4.000 erhöht und wiederholt |
| Hauptlauf | 15.11.2026 | wie oben | wie oben, `max_tokens` 4.000, `seed_reihenfolge` 2026 | 900 von 900 Antworten vollständig, keine Formatfehler; Kosten 6,25 US-Dollar |

## Hinweise
- `.env` enthält den API-Schlüssel und ist in `.gitignore` ausgenommen; sie darf nicht veröffentlicht werden.
- Die amtlichen Verzeichnisse liegen in der heruntergeladenen Fassung bei, damit die Kodierung
  auch nach einer Aktualisierung der Klassifikationen nachvollziehbar bleibt.
