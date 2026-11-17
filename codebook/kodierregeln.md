# Kodierregeln

Festgelegt vor der Hauptdatenerhebung (nach dem Pilot, 15.11.2026).

1. **Geschlechtsformen:** Weibliche, männliche und gegenderte Formen derselben Berufsbenennung
   (z. B. „Psychotherapeutin“, „Psychotherapeut“, „Psychotherapeut:in“) erhalten denselben Code.
2. **Mehrere Optionen in einer Empfehlung:** Kodiert wird die zuerst genannte Option
   (z. B. „Master in X oder Y“ → X).
3. **Weiterqualifikation:** Empfehlungen eines weiteren Studiums, einer Promotion oder Ausbildung
   (z. B. „Masterstudium …“) werden im Szenario Beruf als eigene Kategorie „Weiterqualifikation“
   kodiert, nicht über die KldB 2010.
4. **Tätigkeitsfelder statt Berufe:** Wird ein Tätigkeitsfeld genannt (z. B. „Mitarbeit in einer
   Beratungsstelle“), wird der passendste Beruf nach KldB 2010 zugeordnet; die Zuordnung wird in
   der Spalte `notiz` begründet.
5. **MINT-Abgrenzung:** MINT = Fächergruppen Mathematik/Naturwissenschaften und
   Ingenieurwissenschaften nach der Destatis-Fächersystematik. Architektur/Innenarchitektur gehört
   dort zu den Ingenieurwissenschaften und zählt daher als MINT.
6. **Unspezifische Empfehlungen (UNSPEZ):** Nennt eine Empfehlung nur eine Branche, einen Sektor
   oder ein Programm ohne bestimmbaren Beruf (z. B. „Kultur- und Bildungsbereich“, „Trainee-Programm
   in einem Industrieunternehmen“), wird sie als eigene Kategorie „UNSPEZ“ kodiert. Sie geht als
   Kategorie in Überschneidungsmaße ein, nicht aber in Analysen nach Berufshauptgruppe und Niveau.
   Ist nur das Berufsfeld bekannt (z. B. „IT-Trainee“), wird nur die Berufshauptgruppe vergeben.

7. **Reihenfolge entscheidet nicht (Ergänzung zu Regel 2):** Nennt eine Empfehlung mehrere
   Tätigkeiten in einer Aufzählung, ist deren Reihenfolge inhaltlich beliebig. Innerhalb eines
   Profils erhalten deshalb Empfehlungen, die dieselben Tätigkeiten nennen, denselben Code;
   gewählt wird die Fassung, die im Profil häufiger vorkommt, bei Gleichstand die inhaltlich
   spezifischere Systematikposition. Die betroffenen Fälle wurden gefunden, indem die Titel je
   Profil auf ihre Wortmenge normalisiert und alle Gruppen mit mehr als einem Code von Hand
   geprüft wurden; eine Gruppe wurde dabei als Fehltreffer verworfen. Ergebnis: neun Gruppen,
   123 Titel, 166 von 2250 Berufsempfehlungen. Die vollständige Liste steht in
   `codebook/vereinheitlichung.csv`, angewandt durch `scripts/vereinheitliche_codes.py`
   (läuft nach `finalisiere_beruf.py`). Diese Regel wurde nach der ersten Auswertung ergänzt;
   Abschnitt 5.7 der Arbeit berichtet die Kennzahlen vor und nach ihrer Anwendung.

## Vorgehen (Szenario Beruf)

1. Exakter Abgleich mit dem Alphabetischen Verzeichnis der Berufsbenennungen (BA, KldB 2010,
   Fassung 2020): `scripts/kodiere_beruf_auto.py`. Prüfstichprobe n = 50: 50/50 korrekt (Autorin).
2. Analogieregeln für Titel ohne exakten Treffer: `scripts/analogieregeln.py` (REGELN),
   angewendet mit `scripts/vorkodierung_analogie.py`. Jede Regel verweist auf eine Benennung bzw.
   einen Code aus den BA-Verzeichnissen; Codes werden nachgeschlagen, nicht eingetragen.
3. Mehrdeutige Gruppen (13) und Einzelfälle (26): Entscheidung der Autorin (ENTSCHEIDUNGEN,
   EINZELFAELLE), dokumentiert im selben Skript.
4. Prüfstichprobe der Analogieregeln (n = 50, Blatt `pruefung_regeln`, Autorin): 41 eindeutig
   korrekt, 7 regelkonform, aber interpretationsabhängig (Regel 4: Tätigkeitsfeld statt Beruf),
   2 Verstöße gegen Regel 2. Die zugrunde liegenden Regeln wurden korrigiert und alle betroffenen
   Titel neu kodiert.
5. Ergebnis nach Regel 7: `codebook/beruf_codes.csv` (1588 Titel, 2250 Empfehlungen: 2010 BERUF, 215 WQ, 25 UNSPEZ; vor Regel 7: 2025 / 198 / 27).

## Sensitivitätsanalyse

Spalte `analogie_typ` markiert Codes, die nur aus einem Tätigkeitsfeld abgeleitet wurden
(Regel 4; heuristisch: Titel beginnt mit „Mitarbeit/Tätigkeit/Einstieg in“ oder das erste Substantiv
bezeichnet ein Feld, z. B. „Personalwesen“, „Jugendhilfe“). Betroffen: 462 von 2250 Empfehlungen.
Die Hauptanalyse verwendet alle Codes; als Robustheitsprüfung wird sie ohne diese Empfehlungen wiederholt.

## Szenario Studienwahl

Klassifikation: Fächersystematik der amtlichen Hochschulstatistik (Statistisches Bundesamt,
Schlüsselverzeichnis H21, gültig WS 2026/27, Abschnitt 4.1), extrahiert nach
`codebook/quellen/destatis_faecher.csv` (264 Studienfächer, 64 Studienbereiche).
Frauenanteil: GENESIS-Tabelle 21311-0003, Studierende WS 2025/26, Nationalität insgesamt
(`codebook/quellen/destatis_faecher_frauenanteil.csv`, `destatis_studienbereich_frauenanteil.csv`).

1. Exakter Abgleich mit den Fachbezeichnungen (`scripts/kodiere_studium_auto.py`): 199 Titel.
2. Analogieregeln (`scripts/analogieregeln_studium.py`, `scripts/kodiere_studium_regeln.py`): 177 Titel.
3. Entscheidungen der Autorin (68 Titel):
   - **Lehramt:** erstes genanntes Unterrichtsfach (auch in Klammern), entsprechend der amtlichen
     Zählung nach dem 1. Studienfach; ohne Fach: Grundschule → Grundschul-/Primarstufenpädagogik,
     sonst Erziehungswissenschaften. (Ausnahme von Regel 2, da „Lehramt“ allein keine Fachrichtung angibt.)
   - Umweltwissenschaften → Interdisziplinäre Studien (Schwerpunkt Naturwissenschaften).
   - Wirtschaftsingenieurwesen → Variante mit ingenieurwissenschaftlichem Schwerpunkt
     (größere Studierendenzahl laut 21311-0003).
   - Kognitionswissenschaft / Liberal Arts → jeweilige interdisziplinäre Studien.
4. Prüfstichprobe der Analogieregeln: n = 30 (`codebook/pruefung_studium.xlsx`, Autorin): 27 eindeutig korrekt,
   3 regelkonform, aber interpretationsabhängig (Kreatives Schreiben → Allgemeine Literaturwissenschaft;
   Public Policy → Politikwissenschaft; Kinderkrankenpflege → Pflegewissenschaft), 0 Regelverstöße.
