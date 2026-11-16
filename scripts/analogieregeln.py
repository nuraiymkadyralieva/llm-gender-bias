"""Analogieregeln für die Vorkodierung (Szenario Beruf).

Jede Regel: (Muster, Analogie, Kommentar).
- Muster: regulärer Ausdruck, angewendet auf den Anfang des normalisierten Titels
  (Kleinschreibung, Gender-Markierungen entfernt, Präfixe wie 'Junior', 'Einstieg als' entfernt).
  Damit gilt automatisch Regel 2 (Erstnennung).
- Analogie: exakte Berufsbenennung aus dem Alphabetischen Verzeichnis der BA, ein 5-stelliger
  KldB-Code (Name aus dem Systematischen Verzeichnis), 'WQ' (Weiterqualifikation) oder
  'STREITIG:<Gruppe>' (Entscheidung durch die Autorin).
Codes werden nie hier eingetragen, sondern immer aus den BA-Verzeichnissen nachgeschlagen.
"""
REGELN = [
    # --- Weiterqualifikation ---
    (r"(weiterführendes|aufbauendes|konsekutives|berufsbegleitendes|berufsbegleitender|aufbauender|anschließender) (oder anschließender )?(master|masterstudium)|direkter einstieg in einen master|doktorand|industriepromotion", "WQ", "Studium/Promotion als Ziel (Regel 3)"),
    (r"wissenschaftliche laufbahn|forschung und wissenschaft|forschung (oder|und) datenanalyse", "STREITIG:wiss_laufbahn", "Mischung aus Promotion (WQ) und Stelle"),
    # --- Verlag, Redaktion, Medien ---
    (r"journalismus und online-redaktion", "Onlineredakteur/in", ""),
    (r"(redaktions|journalistisches |pr-)?volontariat|journalismus", "Volontär/in", "Volontariat = bezahlte Einstiegsstelle"),
    (r"lektoratsassistenz|assistenz im lektorat", "Lektorassistent/in (Verlag)", ""),
    (r"lektorat", "Lektor/in - Verlage", ""),
    (r"redaktionsassistenz", "Redaktionsassistent/in", ""),
    (r"korrektorat", "Korrektor/in", "konsistent mit Prüfstichprobe Zeile 5"),
    (r"technische redaktion", "Technische/r Redakteur/in", ""),
    (r"(online-|content-|online-/journalistische )redaktion|content- oder online-redaktion|online-redaktion", "Onlineredakteur/in", ""),
    (r"content[- ]marketing", "Content-Marketing-Manager/in", ""),
    (r"(junior-)?texter|copywriter|content- oder copywriting", "Texter/in", ""),
    (r"verlagsassistenz|assistenz (in einem|im) verlag", "Verlagsassistent/in", ""),
    (r"assistenz in der (presse|unternehmenskommunikation)", "PR-Assistent/in", ""),
    (r"öffentlichkeitsarbeit|presse- und öffentlichkeitsarbeit|die pr- und|pr- und (öffentlichkeitsarbeit|unternehmenskommunikation)|unternehmenskommunikation|public relations|(referent|berater)\w* für (pr|unternehmenskommunikation)|trainee (oder junior-referent für pr|in der unternehmenskommunikation)", "Referent/in - Öffentlichkeitsarbeit/Marketing", ""),
    # --- Pharma, Klinik ---
    (r"clinical research associate|(der )?klinische(n)? (forschung|studien)|(im )?(management|koordination) klinischer studien|(im )?klinischen studienmanagement|(im )?bereich klinische studien", "Klinische/r Monitor/in (CRA)", "CRA = Klinische/r Monitor/in laut BA"),
    (r"regulatory affairs", "Regulatory-Affairs-Manager/in", ""),
    (r"medical science liaison", "Medical Advisor", "MSL entspricht Medical Affairs"),
    # --- Finanzen, Beratung ---
    (r"quantitativ(e|er) risikoanalyst", "Risk-Manager/in", ""),
    (r"quantitativ(e|er) (analyst|analyse)", "Finanzanalyst/in", ""),
    (r"financial", "Financial Analyst/in", ""),
    (r"business /|business-/systemanalyst|requirements engineer|anforderungsmanager", "Business-Analyst/in", "konsistent mit 'Business Analyst / Requirements Engineer'"),
    (r"business[- ]intelligence|data[ /-]+bi|data-analyst|data-/bi", "Data-Analyst/in", ""),
    (r"data engineering|data-engineer", "Data Engineer", ""),
    (r"bioinformatik", "Bioinformatiker/in", ""),
    (r"(assistenz in der |associate in der |berufseinsteiger in der |einstieg in |die )?wirtschaftsprüfung|audit associate|prüfungsassistent", "Prüfungsassistent/in - Wirtschaftsprüfung", ""),
    (r"controlling|trainee\S* (\S+ ){0,3}\(?(finance|finanzen|finanz-)\s?(und|&|/)\s?controlling|trainee\S* (im|in der|im bereich) controlling|traineeprogramm oder direkteinstieg im controlling|trainee- oder direkteinstieg im controlling", "Controller/in", "Trainee nach Berufsfeld"),
    (r"(trainee (im|in der) )?finanz- und rechnungswesen|finanzbuchhaltung|rechnungswesen|(sachbearbeiter|mitarbeiter)\w* im rechnungswesen|trainee im bereich finance & accounting", "Finanzbuchhalter/in", ""),
    (r"unternehmensberatung|consultant (für|\(fokus) (finance|betriebswirt)|junior consultant (für|\(fokus)|consultant (\(unternehmensberatung|\(finance|im bereich finance|mit schwerpunkt finance|für finanz)|berater für organisationsentwicklung|consulting-einstieg|management consulting|die unternehmensberatung|analytische unternehmensberater|unternehmens- oder it-berater|strategie-", "Unternehmensberater/in", ""),
    # --- IT ---
    (r"it-projektmanager|projektmanager für it|projektmanager\w*( oder projektkoordinator\w*)? in der it", "IT-Projektkoordinator/in", ""),
    (r"(sap|erp)[- /]|inhouse (sap|it-consultant|it-spezialist)|inhouse-consultant|erp consultant|erp-berater", "ERP-Berater/in - ERP-Consultant", ""),
    (r"it-sicherheit|it-security|junior security", "STREITIG:it_security", "kein exakter BA-Eintrag; Niveau 3 oder 4"),
    (r"devops|cloud-|position in devops", "DevOps Engineer", ""),
    (r"testautomatisierer|qa engineer|qa /|quality assurance|qualitätssicherungsingenieur für software", "Softwaretester/in", ""),
    (r"(direkteinstieg als )?(junior[- ])?softwareentwickler|trainee in der softwareentwicklung", "Softwareentwickler/in", ""),
    (r"it-berater|it-consultant|technical consultant|associate/junior consultant in der it", "IT-Consultant", ""),
    # --- Ingenieurwesen ---
    (r"(direkteinstieg als )?entwicklungs(ingenieur|-)", "27104", "Berufsgattung Technische Forschung und Entwicklung"),
    (r"(versuchs|test|prüf|erprobungs|validierungs)[- ]?(und \w+)?\s?(ingenieur|- und)", "Testingenieur/in", ""),
    (r"versuchsingenieur", "Testingenieur/in", ""),
    (r"(berechnungs|simulations)", "Berechnungsingenieur/in", ""),
    (r"produktions- oder (fertigungs|qualitäts|prozess)ingenieur|ingenieur\w* in der produktions|prozessingenieur in der industriellen", "Produktionsingenieur/in", ""),
    (r"qualitäts-?,? (oder )?(produktions|prozess|versuchs)", "Qualitätsingenieur/in", ""),
    (r"projekt- (oder|bzw\.) (versuchs|prozess|produktions|produkt)ingenieur|projektingenieur|technischer projekt(leiter|manager)|junior-projektingenieur|trainee im technischen projektmanagement", "Projektingenieur/in", ""),
    (r"technische(r)? (berater|beratung|unternehmensberater)|technische unternehmensberatung", "STREITIG:technische_beratung", "kein BA-Eintrag"),
    (r"projekt- oder produktmanager", "STREITIG:technisches_projektmanagement", "27104 Projektingenieur/in oder 71393 Projektleiter/in"),
    (r"ingenieur", "STREITIG:ingenieur_allgemein", "Fachrichtung offen"),
    # --- Architektur, Bau ---
    (r"(angestellte |angestellter |junior-)?architekt|architekturabsolvent|architekturbüro|planungsmitarbeiter in einem architekturbüro|(der )?(entwurfs- und wettbewerbsplanung|ausführungsplanung)", "Architekt/in", "Junior/AiP ändern das Niveau nicht"),
    (r"bim|building information modeling|die bim-planung", "BIM-Manager/in", ""),
    (r"bauleit|die bauleitung|(der )?bau- oder projektleitung", "Bauleiter/in", ""),
    (r"(der )?stadtplanung(?! oder bau)|stadtplanung, bauverwaltung", "Stadtplaner/in", ""),
    (r"projektmanager\w* (oder|bzw\.) bauleiter|projektmanag\w* (in der|in|bei|im) (immobilien|bau)|projektmanagement / projektsteuerung|junior-projektmanagement im bauwesen|planung und bauprojektmanagement|bau- und projektplanung|projektentwick|die projektentwicklung|immobilien|projektmitarbeiter\w* (in der bau|bei einem bau)|bau- oder projektentwicklung|projekt\w*( / | oder | bzw\. | und )(bauleit|projektentwick|projektsteuer)|projektmanagement bzw\. projektsteuerung|bauunternehmen|(der )?bau- und ausführungsplanung|projektassistenz (bei einer projektentwicklung|im bauprojekt)", "STREITIG:bau_projektmanagement", "kein BA-Eintrag; 31104 (Baumanagement) oder 61314 (Immobilien)"),
    (r"(büro für )?nachhaltig|für nachhaltiges|energieberat|spezialisiert|spezialisierung", "STREITIG:nachhaltiges_bauen", "Mischangaben"),
    (r"(stelle in der |stellen im |stelle im |der )?(öffentlich|bauämtern|kommunal)|einer kommunalen|der (kommunalen )?bauverwaltung|bauverwaltung|hochbauamt|(der )?bauplanung einer öffentlichen|stadtplanung oder bauverwaltung|öffentlicher dienst|referendariat|angestellte oder referendar|mitarbeiter in einem stadtplanungs", "STREITIG:oeffentlicher_dienst", "Arbeitgeber statt Beruf"),
    # --- Soziale Arbeit, Beratung, Gesundheit ---
    (r"(fachkraft|sozialpädagogische fachkraft)? ?(im |in der )?(allgemeinen sozialen dienst|allgemeiner sozialer dienst|asd)", "Sozialarbeiter/in", ""),
    (r"schulsozialarbeit", "Schulsozialarbeiter/in", ""),
    (r"(fachkraft in der )?sozialpädagogische(n)? familienhilfe", "Sozialpädagogische/r Familienhelfer/in", ""),
    (r"fachkraft (in der|bei|im) .*jugendhilfe|sozialpädagogische fachkraft|(stationäre|ambulante) (oder (ambulante|stationäre) )?(kinder- und )?(jugendhilfe|hilfen)|freie träger der kinder|sozialpädagog|(der )?(stationären )?(kinder- und )?jugendhilfe|einer (stationären )?jugendhilfeeinrichtung|einer (jugend)?wohngruppe|einer einrichtung der kinder|pädagogische fachkraft in einer wohngruppe|fachkraft in einer (stationären jugendhilfe|jugendwohngruppe|einrichtung der kinder)", "Sozialpädagoge/-pädagogin", ""),
    (r"sozialarbeit |sozialdienst|(der )?jugendgerichtshilfe|fachkraft im pflegekinderdienst", "Sozialarbeiter/in", ""),
    (r"(berater|beraterin|fachkraft) in einer (erziehungs|familien|jugend)|(einer )?(erziehungs|familien|jugend)(- oder |- und |-, )?\w*beratungsstelle|erziehungs- und familienberatung", "Erziehungsberater/in", ""),
    (r"(psychosozial|psychologisch|beratung|beratungs|der psychosozialen|sozial- und beratung|die (beratung|soziale arbeit)|der sozialen beratung|die sozial- und|die psychosoziale|beratende|als beraterin oder fachkraft|beraterin oder fachkraft|sozialen beratung|soziale arbeit bzw\. beratung)|einer (psychosozialen )?beratungsstelle|einer jugendberatung|fachkraft in einer beratungsstelle|beraterin in einer psychosozialen", "STREITIG:beratung", "83154 Sozialberater/in oder 81614 Psychologischer Berater/in"),
    (r"betriebliche(s|n) gesundheitsmanagement|(referent|berater)\w* im (betrieblichen gesundheitsmanagement|bereich betriebliches)", "Gesundheitsmanager/in", ""),
    (r"(der betrieblichen )?gesundheitsförderung|prävention (und|oder) gesundheitsförderung", "Gesundheitsförderer/-förderin", ""),
    # --- Personal ---
    (r"(trainee in der |trainer\w* in der )?personalentwicklung", "Personalentwickler/in", ""),
    (r"personalgewinnung|recruiting", "Recruiter/in", ""),
    (r"(quereinstieg im )?personalwesen|human resources|hr-(manager|specialist)|der personalentwicklung", "Personalreferent/in", ""),
    # --- Marktforschung ---
    (r"(junior-)?marktforsch|markt- und (meinungs|nutzer|sozial)forschung|markt-, meinungs|markt- oder meinungs|researcher in der markt|markt-/sozialforschung|der markt- und|markt- oder nutzer|der markt- oder nutzer", "Marktforscher/in", ""),
    # --- Kultur, Bildung ---
    (r"kultur- und veranstaltungsmanagement|kulturmanagement|kultur- und bildungsmanagement", "Kulturmanager/in", ""),
    (r"erwachsenenbildung|bildung und (kultur|weiterbildung|wissensvermittlung)", "Erwachsenenbildner/in", "Beispiele nennen Erwachsenenbildung/DaF"),
    # --- Forschung (Biologie, Pharma) ---
    (r"wissenschaftlich\w* (mitarbeit|projektmitarbeit|hilfskraft)|forschungsassist|projektmitarbeiter\w* (oder wissenschaftliche|in der forschung)|(der )?forschung \(universität|research scientist", "STREITIG:wiss_mitarbeit", "84304 (Hochschule) oder Fachberuf (z. B. 41204 Biologe/Biologin)"),
    (r"forschung (und|&) entwicklung|forschungs(- und entwicklungs)?mitarbeit|labor|research associate|(der )?präklinischen|(der )?molekularbiologischen|forschung oder an hochschulen|der forschung", "STREITIG:fue_labor", "Tätigkeitsfeld; Biologe/Biologin 41204 oder Biotechnologe 41214"),
    (r"qualitäts(kontrolle|management|sicherung)|der qualitätskontrolle|(der )?pharmazeutischen qualitätskontrolle|(junior manager im |im )?bereich qualität|manager im bereich qualität", "STREITIG:qualitaet_pharma", "Qualitätsmanager/in 27394 oder Laborberuf"),
    # --- Restliche Sammelangaben ---
    (r"(it-)?trainee|graduate-|trainee-programm|traineeprogramm", "STREITIG:trainee", "Berufsfeld offen"),
]

# Entscheidungen der Autorin zu den STREITIG-Gruppen (15.11.2026).
# Je Gruppe: geordnete Unterregeln (Muster wird im Schlüsseltext gesucht; "" = alle übrigen).
# Analogie zusätzlich: 'UNSPEZ' (kein Beruf bestimmbar) oder 'BHG:<2-Steller>' (nur Berufshauptgruppe).
_BAU = r"\bbau(?!träger)|bauleit|bauunternehm|bauwesen|projektsteuer|ausführungsplanung"
ENTSCHEIDUNGEN = {
    "wiss_mitarbeit": [("", "Wissenschaftliche/r Mitarbeiter/in")],
    # Regel 2: entscheidend ist die erste konkrete Nennung nach dem Oberbegriff
    "wiss_laufbahn": [(r"^(wissenschaftliche laufbahn|forschung und wissenschaft|forschung (und|oder) datenanalyse)\s*(:|\(|bzw\.)?\s*(forschungsorientierter )?(master|promotion)", "WQ"),
                      ("", "Wissenschaftliche/r Mitarbeiter/in")],
    "beratung": [("psycholog", "Psychologischer Berater/in"), ("", "Sozialberater/in")],
    "fue_labor": [("", "Biologe/Biologin")],
    "qualitaet_pharma": [("", "Qualitätsingenieur/in")],
    "trainee": [(r"\bit\b|it-trainee|in der it", "BHG:43"), ("", "UNSPEZ")],
    "oeffentlicher_dienst": [("", "31104")],
    "bau_projektmanagement": [(r"^(?:(?!" + _BAU + r").)*?(projektentwick|immobilien|bauträger|investor)", "Betriebswirt/in (Hochschule) - Immobilien"),
                              ("", "31104")],
    "nachhaltiges_bauen": [("", "31104")],
    "it_security": [("", "Cyber-Security-Consultant")],
    "technische_beratung": [("", "Unternehmensberater/in")],
    "ingenieur_allgemein": [(r"^ingenieur\w* (in|im) (der )?produktion", "Produktionsingenieur/in"),
                            (r"^ingenieur\w* (in|im) (der )?(technischen )?projekt", "Projektingenieur/in"),
                            (r"^ingenieur\w* (in|im) (der )?qualität", "Qualitätsingenieur/in"),
                            (r"^ingenieur\w* (in|im) (der )?(simulation|berechnung)", "Berechnungsingenieur/in")],
    "technisches_projektmanagement": [("", "Projektingenieur/in")],
}

# Einzelfallentscheidungen der Autorin (15.11.2026) für Titel ohne Regeltreffer.
EINZELFAELLE = [   # Muster gelten ab Anfang des Schlüsseltexts (re.match)
    (r"application manager", "ERP-Systembetreuer/in"),
    (r"applikationsspezialist", "Application-Engineer/-Manager/in"),
    (r"assistenz im rechnungswesen", "Finanzbuchhalter/in"),
    (r"assistenz in einer literaturagentur", "Verlagsassistent/in"),
    (r"bank", "Firmenkundenberater/in (Bank)"),
    (r"bibliothek, archiv", "Bibliothekar/in"),
    (r"case manager", "Sozialarbeiter/in"),
    (r"kultur-|literatur- oder kultureinrichtung|rehabilitationseinrichtung", "UNSPEZ"),
    (r"marketing, ux", "Marketingmanager/in"),
    (r"produktmanagement oder technischer vertrieb", "Produktmanager/in"),
    (r"projektassistenz (im|in einer) (kultur|literatur)", "Projektassistent/in"),
    (r"(projektmitarbeit bei )?einem sozialen träger|sozialen träger", "Sozialarbeiter/in"),
    (r"pädagogisch-psychologische förderung", "Sozialpädagoge/-pädagogin"),
    (r"verlagsmarketing", "Marketingmanager/in"),
    (r"vertrieb, key account", "Vertriebsmanager/in"),
    (r"vertriebs- oder marketingassistenz", "Vertriebsassistent/in"),
]
