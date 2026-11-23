"""Dem Geistmodell zusehen.

    python -m geist          interaktiv: du bist die manuelle bewusste Intention
    python -m geist --demo   fester Ablauf, der die drei Haltungen vergleicht
"""

from __future__ import annotations

import argparse

from .modell import Geist, Haltung, Impuls, Moment

BALKENBREITE = 20
TASTEN = {"e": Haltung.ENGAGE, "d": Haltung.DISENGAGE, "w": Haltung.WEDER_NOCH}


def zeige(moment: Moment) -> None:
    print(f"\nMoment {moment.zeit}")
    if not moment.impulse:
        print("  (das Unterbewusstsein erzeugt gerade nichts)")
        return
    bewusst = {i.thema for i in moment.aufgestiegen}
    breite = max(len(i.thema) for i in moment.impulse)
    print(f"  {'Thema':<{breite}}  {'Stärke':<{BALKENBREITE + 5}}  bewusst  Haltung")
    for impuls in moment.impulse:
        voll = round(impuls.staerke * BALKENBREITE)
        balken = "█" * voll + "░" * (BALKENBREITE - voll)
        haltung = moment.haltungen.get(impuls.thema)
        print(
            f"  {impuls.thema:<{breite}}  {balken} {impuls.staerke:.2f}"
            f"  {'ja' if impuls.thema in bewusst else 'nein':<7}"
            f"  {haltung.value if haltung else '-'}"
        )


def demo() -> None:
    """Drei gleich starke Themen, jedes bekommt dauerhaft eine andere Haltung."""
    haltung_je_thema = {
        "Sorge": Haltung.ENGAGE,
        "Ohrwurm": Haltung.WEDER_NOCH,
        "Hunger": Haltung.DISENGAGE,
    }
    geist = Geist(lambda impuls: haltung_je_thema[impuls.thema])
    zeige(geist.schritt({thema: 0.8 for thema in haltung_je_thema}))
    for _ in range(7):
        zeige(geist.schritt())


def frage_haltung(impuls: Impuls) -> Haltung:
    while True:
        antwort = input(
            f"  '{impuls.thema}' steigt auf ({impuls.staerke:.2f}). "
            "[e]ngage / [d]isengage / [w]eder noch? "
        )
        haltung = TASTEN.get(antwort.strip().lower()[:1])
        if haltung:
            return haltung


def lies_erfahrungen(text: str) -> dict[str, float]:
    """'Hunger, Sorge=0.9' -> {'Hunger': 0.5, 'Sorge': 0.9}"""
    erfahrungen: dict[str, float] = {}
    for teil in text.split(","):
        thema, _, staerke = teil.partition("=")
        if thema.strip():
            erfahrungen[thema.strip()] = float(staerke) if staerke.strip() else 0.5
    return erfahrungen


def interaktiv() -> None:
    print("Du bist die manuelle bewusste Intention.")
    print("Erfahrungen eingeben als 'Thema' oder 'Thema=Stärke' (0 bis 1), mehrere")
    print("mit Komma. Leere Eingabe: nichts Neues erleben. 'q' beendet.")
    geist = Geist(frage_haltung)
    while True:
        try:
            eingabe = input("\nWas erlebst du gerade? ")
        except EOFError:
            break
        if eingabe.strip().lower() == "q":
            break
        try:
            erfahrungen = lies_erfahrungen(eingabe)
        except ValueError:
            print("  Stärke muss eine Zahl sein, zum Beispiel Sorge=0.9")
            continue
        try:
            zeige(geist.schritt(erfahrungen))
        except EOFError:
            break


def main() -> None:
    parser = argparse.ArgumentParser(prog="geist", description=__doc__.splitlines()[0])
    parser.add_argument("--demo", action="store_true", help="festen Ablauf zeigen")
    if parser.parse_args().demo:
        demo()
    else:
        interaktiv()


if __name__ == "__main__":
    main()
