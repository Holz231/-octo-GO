"""Dem Geistmodell zusehen.

    python -m geist          interaktiv: du bist die manuelle bewusste Intention
    python -m geist --demo   fester Ablauf, der Haltungen und Quellen vergleicht
"""

from __future__ import annotations

import argparse

from .modell import Erfahrung, Geist, Haltung, Lage, Moment

BALKENBREITE = 20
TASTEN = {"e": Haltung.ENGAGE, "d": Haltung.DISENGAGE, "w": Haltung.WEDER_NOCH}


def zeige(moment: Moment, schwelle: float) -> None:
    print(f"\nMoment {moment.zeit}")
    staerken = {i.thema: i.staerke for i in moment.aui_feld}
    ausrichtungen = {a.thema: a for a in moment.ausrichtungen}
    # Auch Themen zeigen, auf die sich die MBI richtet, ohne dass ein Impuls da ist.
    themen = list(staerken) + [t for t in ausrichtungen if t not in staerken]
    if not themen:
        print("  (nichts)")
        return
    breite = max(len("Thema"), *(len(t) for t in themen))
    # Die beiden Felder grenzen aneinander: Der Balken reicht über die Grenze,
    # sobald ein Impuls stark genug ist, um auch im Feld der ABI aufzutauchen.
    grenze = round(schwelle * BALKENBREITE)
    felder = f"{'AUI':<{grenze}}│{'ABI':<{BALKENBREITE - grenze}}"
    print(f"  {'Thema':<{breite}}  {felder}  {'':4}  {'MBI':<10}  gerichtet auf")
    for thema in themen:
        staerke = staerken.get(thema, 0.0)
        voll = round(staerke * BALKENBREITE)
        # Rundung darf den Balken nicht auf die falsche Seite der Grenze setzen.
        voll = max(voll, grenze + 1) if staerke >= schwelle else min(voll, grenze)
        balken = "█" * voll + "░" * (BALKENBREITE - voll)
        a = ausrichtungen.get(thema)
        print(
            f"  {thema:<{breite}}  {balken[:grenze]}│{balken[grenze:]}  {staerke:.2f}"
            f"  {a.haltung.value if a else '-':<10}  {a.quelle.value if a else '-'}"
        )


def demo() -> None:
    """Drei Haltungen und drei Quellen nebeneinander.

    Sorge, Ohrwurm und Hunger stammen aus vorherigen Erfahrungen und sind sofort
    im Feld der ABI. Der Atem ist ein schwacher sensorischer Eindruck, Urlaub ein frei
    gewähltes Thema: Beide tauchen dort erst auf, nachdem sich die MBI ab
    Moment 2 darauf gerichtet hat.
    """

    def entscheider(lage: Lage) -> dict[str, Haltung]:
        im_feld = {impuls.thema for impuls in lage.abi_feld}
        haltungen = {}
        if "Sorge" in im_feld:
            haltungen["Sorge"] = Haltung.ENGAGE
        if "Hunger" in im_feld:
            haltungen["Hunger"] = Haltung.DISENGAGE
        if geist.zeit >= 2:
            haltungen["Atem"] = Haltung.ENGAGE
            haltungen["Urlaub"] = Haltung.ENGAGE
        return haltungen

    geist = Geist(entscheider)
    for thema in ("Sorge", "Ohrwurm", "Hunger"):
        geist.unterbewusstsein.erlebe(Erfahrung(thema, 0.8, zeit=0))
    for _ in range(6):
        zeige(geist.schritt({"Atem": 0.05}), geist.automatisch.schwelle)


def lies_ausrichtung(text: str) -> dict[str, Haltung]:
    """'e Sorge, d Musik' -> {'Sorge': ENGAGE, 'Musik': DISENGAGE}"""
    haltungen: dict[str, Haltung] = {}
    for teil in text.split(","):
        if not teil.strip():
            continue
        taste, _, thema = teil.strip().partition(" ")
        if taste.lower() not in TASTEN or not thema.strip():
            raise ValueError(teil.strip())
        haltungen[thema.strip()] = TASTEN[taste.lower()]
    return haltungen


def frage_ausrichtung(lage: Lage) -> dict[str, Haltung]:
    feld = ", ".join(f"{i.thema} ({i.staerke:.2f})" for i in lage.abi_feld)
    sinne = ", ".join(f"{t} ({s:.2f})" for t, s in lage.sinne.items())
    print(f"  ABI-Feld: {feld or '-'}")
    print(f"  Sinne:    {sinne or '-'}")
    while True:
        antwort = input("  Worauf richtest du dich? ")
        try:
            return lies_ausrichtung(antwort)
        except ValueError as fehler:
            print(f"  Nicht verstanden: '{fehler}'. Beispiel: e Sorge, d Musik")


def lies_sinne(text: str) -> dict[str, float]:
    """'Laerm, Atem=0.1' -> {'Laerm': 0.5, 'Atem': 0.1}"""
    sinne: dict[str, float] = {}
    for teil in text.split(","):
        thema, _, staerke = teil.partition("=")
        if thema.strip():
            sinne[thema.strip()] = float(staerke) if staerke.strip() else 0.5
    return sinne


def interaktiv() -> None:
    print("Du bist die manuelle bewusste Intention (MBI).")
    print()
    print("Jeder Moment hat zwei Eingaben:")
    print("1. Sinne: 'Thema' oder 'Thema=Stärke' (0 bis 1), mehrere mit Komma.")
    print("   Leer = keine Eindrücke, 'q' beendet.")
    print("2. Ausrichtung: 'e Thema' (engage) oder 'd Thema' (disengage), mehrere")
    print("   mit Komma. Das Thema darf aus dem ABI-Feld, aus den Sinnen oder frei")
    print("   gewählt sein. Leer = weder noch.")
    geist = Geist(frage_ausrichtung)
    while True:
        try:
            eingabe = input("\nWas nehmen deine Sinne wahr? ")
            if eingabe.strip().lower() == "q":
                break
            try:
                sinne = lies_sinne(eingabe)
            except ValueError:
                print("  Stärke muss eine Zahl sein, zum Beispiel Atem=0.1")
                continue
            zeige(geist.schritt(sinne), geist.automatisch.schwelle)
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
