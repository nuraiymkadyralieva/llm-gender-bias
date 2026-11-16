"""Analogieregeln für Studienempfehlungen (Destatis-Fächersystematik WS 2026/27).
(Muster am Anfang des normalisierten Kerns, Destatis-Studienfach exakt | 'STREITIG:<Gruppe>', Kommentar)
"""
REGELN = [
    (r"lehramt|.*auf lehramt", "STREITIG:lehramt", "Lehramt: Destatis zählt nach 1. Studienfach"),
    (r"elektrotechnik", "Elektrotechnik/Elektronik", ""),
    (r"landschaftsarchitektur", "Landschaftsgestaltung", ""),
    (r"umweltwissenschaft|umweltnaturwissenschaft", "STREITIG:umwelt", "kein eigenes Fach"),
    (r"umweltchemie", "Chemie", ""),
    (r"umweltbiotechnologie", "Biotechnologie", ""),
    (r"umweltingenieurwesen|umwelt- und verfahrenstechnik", "Umwelttechnik (einschl. Recycling)", ""),
    (r"erziehungswissenschaft", "Erziehungswissenschaften (Pädagogik)", ""),
    (r"stadtplanung|stadt- und (raum|regional)planung", "Raumplanung", ""),
    (r"journalistik|journalismus", "Kommunikationswissenschaft/Publizistik", ""),
    (r"geschichtswissenschaft", "Geschichte", ""),
    (r"gesundheits- und (pflege|kindheits)pädagogik", "Gesundheitspädagogik", ""),
    (r"gesundheitswissenschaft|gesundheitsförderung|gesundheits- und (sozial|sport|pflege)wissenschaft", "Gesundheitswissenschaft/-management", "Erstnennung Gesundheit"),
    (r"robotik|mechatronik und robotik", "Mechatronik", "Robotik-Studiengänge i. d. R. Mechatronik"),
    (r"humanmedizin", "Medizin (Allgemein-Medizin)", ""),
    (r"game(s)? (engineering|development)|computerspielentwicklung|computerspieleentwicklung|spieleentwicklung", "Medieninformatik", ""),
    (r"game design", "Graphikdesign/Kommunikationsgestaltung", ""),
    (r"medien- und (kommunikations|kultur)wissenschaft", "Medienwissenschaft", "Erstnennung"),
    (r"kommunikations- und medienwissenschaft", "Kommunikationswissenschaft/Publizistik", "Erstnennung"),
    (r"finanz- und wirtschaftsmathematik|finanzmathematik", "Wirtschaftsmathematik", ""),
    (r"finanzwirtschaft|finance|banking and finance|finanz- und investment", "Betriebswirtschaftslehre", "kein eigenes Fach Finance"),
    (r"wirtschaftsingenieurwesen", "STREITIG:wiing", "zwei Destatis-Varianten"),
    (r"komparatistik|(allgemeine und )?vergleichende literaturwissenschaft|literaturwissenschaft|(angewandte )?literatur- und kulturwissenschaft|literarisches schreiben", "Allgemeine Literaturwissenschaft", ""),
    (r"sprachwissenschaft|linguistik", "Allgemeine Sprachwissenschaft", ""),
    (r"pädagogik der kindheit", "Kindheitspädagogik", ""),
    (r"heilpädagogik", "Sonderpädagogik", ""),
    (r"computervisualistik|angewandte informatik|data science|computational science", "Informatik", ""),
    (r"public policy|internationale beziehungen|internationale politik", "Politikwissenschaft/Politologie", ""),
    (r"public management|öffentliche verwaltung", "Verwaltungswissenschaft/-wesen", ""),
    (r"philosophy", "Philosophie", "PPE: Erstnennung Philosophy"),
    (r"anglistik und amerikanistik", "Anglistik/Englisch", ""),
    (r"international business|internationales management", "Internationale Betriebswirtschaft/Management", ""),
    (r"kinderkrankenpflege|pädiatrische pflege|pflege", "Pflegewissenschaft/-management", ""),
    (r"rechtswissenschaften", "Rechtswissenschaft", ""),
    (r"kognitionswissenschaft|liberal arts", "STREITIG:interdisziplinaer", "interdisziplinär"),
]

# Entscheidungen der Autorin (16.11.2026)
ENTSCHEIDUNGEN = {
    "umwelt": [("", "Interdisziplinäre Studien (Schwerpunkt Naturwissenschaften)")],
    "wiing": [("", "Wirtschaftsingenieurwesen mit ingenieurwissenschaftlichem Schwerpunkt")],
    "interdisziplinaer": [("kognition", "Interdisziplinäre Studien (Schwerpunkt Sozial- und Verhaltenswissenschaften)"),
                          ("liberal arts", "Interdisziplinäre Studien (Schwerpunkt Geisteswissenschaften)")],
}
# Lehramt: erstes genanntes Unterrichtsfach (auch in Klammern), wie in der Destatis-Zählung nach 1. Studienfach.
# Ohne Fach: Grundschule -> Grundschulpädagogik, sonst Erziehungswissenschaften.
LEHRAMT_FAECHER = {
    "deutsch": "Germanistik/Deutsch", "englisch": "Anglistik/Englisch", "biologie": "Biologie",
    "sport": "Sportwissenschaft", "mathematik": "Mathematik", "geschichte": "Geschichte",
    "pädagogik": "Erziehungswissenschaften (Pädagogik)", "sachunterricht": "Sachunterricht (einschl. Schulgarten)",
    "politik": "Politikwissenschaft/Politologie", "sozialkunde": "Sozialkunde",
}
LEHRAMT_OHNE_FACH = [("grundschule", "Grundschul-/Primarstufenpädagogik"), ("", "Erziehungswissenschaften (Pädagogik)")]
