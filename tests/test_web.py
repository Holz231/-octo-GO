"""Prüft, dass die Browser-Fassung (web/geist.js) dasselbe rechnet wie geist/modell.py.

Zufällig erzeugte Abläufe werden in beiden Fassungen durchgespielt und Moment
für Moment verglichen. Braucht Node; ohne Node wird der Test übersprungen.
"""

import json
import random
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path

import pytest

from geist import EMOTION, ERINNERUNG, JETZIGE_ERFAHRUNG, KOERPER, SINNE, Entscheidung, Erfahrung, Geist, Umgang

LAEUFER = Path(__file__).with_name("web_lauf.js")
THEMEN = ["Sorge", "Streit", "Atem", "Mail", "Wut", "Enge", "Musik"]
GEBIETE = ["Arbeit", "Familie", SINNE, JETZIGE_ERFAHRUNG, ERINNERUNG, EMOTION, KOERPER, "Sorge"]
GENAUIGKEIT = 1e-9


class ZufallAusListe:
    """Liefert der Reihe nach vorgegebene Zahlen, damit beide Fassungen dieselben bekommen."""

    def __init__(self, zahlen):
        self.zahlen = zahlen
        self.stelle = 0

    def random(self):
        zahl = self.zahlen[self.stelle % len(self.zahlen)]
        self.stelle += 1
        return zahl


def erlebtes(wuerfel):
    """Was in einem Moment erlebt wird: je Gebiet ein paar Themen mit Stärke."""
    auswahl = lambda: {
        thema: round(wuerfel.uniform(0.05, 1.0), 2)
        for thema in wuerfel.sample(THEMEN, wuerfel.choice([0, 0, 1, 2]))
    }
    return {"sinne": auswahl(), "emotion": auswahl(), "koerper": auswahl()}


def erzeuge_szenario(nummer):
    """Spielt einen zufälligen Ablauf in Python durch und hält ihn zum Nachspielen fest."""
    wuerfel = random.Random(nummer)
    optionen = {
        "kapazitaet": wuerfel.choice([1.0, 1.0, 0.8, 2.0]),
        "nachklang": wuerfel.choice([0.8, 0.8, 0.6, 1.0]),
        "mitnahme": wuerfel.choice([None, None, 0.5]),
        "chance": wuerfel.choice([0.25, 0.0, 1.0]),
        "sog": wuerfel.choice([True, True, False]),
        "spontan": wuerfel.choice([0.05, 0.0, 0.5]),
        "haltungsschritt": wuerfel.choice([0.2, 0.2, 0.0]),
    }
    zufall = [round(wuerfel.random(), 6) for _ in range(97)]
    gebiet = wuerfel.choice(GEBIETE)
    vorher = [
        Erfahrung(wuerfel.choice(THEMEN), round(wuerfel.uniform(0.1, 1.0), 2), -wuerfel.randrange(4), (wuerfel.choice(GEBIETE),))
        for _ in range(wuerfel.randrange(5))
    ]

    entscheidungen = []

    def entscheider(lage):
        umgang = {
            impuls.thema: wuerfel.choice(list(Umgang))
            for impuls in lage.abi_feld
            if wuerfel.random() < 0.5
        }
        # Gelegentlich auch etwas, das gar nicht im Feld der ABI auftaucht.
        if wuerfel.random() < 0.1:
            umgang[wuerfel.choice(THEMEN)] = Umgang.ENGAGE
        themenwechsel = wuerfel.choice(GEBIETE) if wuerfel.random() < 0.2 else None
        entscheidungen.append(
            {"umgang": {thema: art.value for thema, art in umgang.items()}, "themenwechsel": themenwechsel}
        )
        return Entscheidung(umgang, themenwechsel)

    geist = Geist(entscheider, gebiet, zufall=ZufallAusListe(zufall), **optionen)
    for erfahrung in vorher:
        geist.unterbewusstsein.erlebe(erfahrung)

    eingaben, momente = [], []
    for _ in range(25):
        eingaben.append(erlebtes(wuerfel))
        momente.append(geist.schritt(**eingaben[-1]))

    szenario = {
        "gebiet": gebiet,
        "optionen": optionen,
        "zufall": zufall,
        "vorher": [
            {"thema": e.thema, "staerke": e.staerke, "zeit": e.zeit, "gebiete": list(e.gebiete)}
            for e in vorher
        ],
        "momente": [
            {**eingabe, "entscheidung": entscheidung}
            for eingabe, entscheidung in zip(eingaben, entscheidungen)
        ],
    }
    return szenario, momente


def als_vergleich(moment):
    """Ein Moment aus Python in der Form, in der die Browser-Fassung ihn liefert."""
    werte = asdict(moment)
    werte["umgang"] = {thema: art.value for thema, art in moment.umgang.items()}
    return json.loads(json.dumps(werte))


def gleich(python, browser, wo):
    """Vergleicht verschachtelte Werte, Zahlen mit kleiner Toleranz."""
    if isinstance(python, float) or isinstance(browser, float):
        assert python == pytest.approx(browser, abs=GENAUIGKEIT), wo
    elif isinstance(python, dict):
        assert set(python) == set(browser), wo
        for schluessel in python:
            gleich(python[schluessel], browser[schluessel], f"{wo}.{schluessel}")
    elif isinstance(python, list):
        assert len(python) == len(browser), wo
        for stelle, (links, rechts) in enumerate(zip(python, browser)):
            gleich(links, rechts, f"{wo}[{stelle}]")
    else:
        assert python == browser, wo


@pytest.mark.skipif(shutil.which("node") is None, reason="braucht Node")
def test_browser_fassung_rechnet_wie_python():
    szenarien, erwartet = zip(*(erzeuge_szenario(nummer) for nummer in range(60)))
    ausgabe = subprocess.run(
        ["node", str(LAEUFER)],
        input=json.dumps(szenarien),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    tatsaechlich = json.loads(ausgabe)

    for nummer, (momente, browser_momente) in enumerate(zip(erwartet, tatsaechlich)):
        for moment, browser_moment in zip(momente, browser_momente):
            vergleich = als_vergleich(moment)
            # Die Browser-Fassung führt zusätzlich, was sie zum Anzeigen braucht.
            gekuerzt = {schluessel: browser_moment[schluessel] for schluessel in vergleich}
            gleich(vergleich, gekuerzt, f"Szenario {nummer}, Moment {moment.zeit}")
