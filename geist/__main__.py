"""Dem Geistmodell zusehen.

    python -m geist                  interaktiv: du bist die MBI
    python -m geist --demo           wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo haltungen die drei Haltungen im Vergleich
"""

from __future__ import annotations

import argparse

from .modell import (
    JETZIGE_ERFAHRUNG,
    SINNE,
    Entscheidung,
    Erfahrung,
    Geist,
    Haltung,
    Lage,
    Moment,
)

BALKENBREITE = 20
TASTEN = {"e": Haltung.ENGAGE, "d": Haltung.DISENGAGE, "w": Haltung.WEDER_NOCH}
BESONDERE_GEBIETE = {
    "sinne": SINNE,
    "jetzt": JETZIGE_ERFAHRUNG,
    "jetzige erfahrung": JETZIGE_ERFAHRUNG,
}


def benenne(gebiet: str) -> str:
    if gebiet in (SINNE, JETZIGE_ERFAHRUNG):
        return gebiet
    return f"Themengebiet {gebiet}"


def zeige(moment: Moment, schwelle: float) -> None:
    print(f"\nMoment {moment.zeit} · MBI bewegt sich in: {benenne(moment.gebiet)}")
    impulse = {i.thema: i for i in moment.aui_feld}
    haltungen = {a.thema: a.haltung for a in moment.ausrichtungen}
    # Auch Themen zeigen, zu denen die MBI eine Haltung hat, ohne dass ein Impuls da ist.
    themen = list(impulse) + [t for t in haltungen if t not in impulse]
    if themen:
        breite = max(len("Thema"), *(len(t) for t in themen))
        # Die beiden Felder grenzen aneinander: Der Balken reicht über die Grenze,
        # sobald ein Impuls stark genug ist, um auch im Feld der ABI aufzutauchen.
        grenze = round(schwelle * BALKENBREITE)
        felder = f"{'AUI':<{grenze}}│{'ABI':<{BALKENBREITE - grenze}}"
        print(f"  {'Thema':<{breite}}  {felder}  {'':4}  {'MBI':<10}  mitgebracht aus")
        for thema in themen:
            impuls = impulse.get(thema)
            staerke = impuls.staerke if impuls else 0.0
            voll = round(staerke * BALKENBREITE)
            # Rundung darf den Balken nicht auf die falsche Seite der Grenze setzen.
            voll = max(voll, grenze + 1) if staerke >= schwelle else min(voll, grenze)
            balken = "█" * voll + "░" * (BALKENBREITE - voll)
            haltung = haltungen.get(thema)
            herkunft = ", ".join(impuls.mitgebracht_aus) if impuls else ""
            print(
                f"  {thema:<{breite}}  {balken[:grenze]}│{balken[grenze:]}  {staerke:.2f}"
                f"  {haltung.value if haltung else '-':<10}  {herkunft or '-'}"
            )
    else:
        print("  (nichts)")
    if moment.wechsel_nach:
        print(f"  Die MBI richtet sich neu aus: {benenne(moment.wechsel_nach)}")


def demo_gebiete() -> None:
    """Die MBI wandert durch alle drei Arten von Gebieten.

    Die Sorge stammt aus dem Themengebiet Familie, der Atem ist ein schwacher
    Sinneseindruck. In der Familie ist nur die Sorge im Feld der ABI. In den
    Sinnen zählt der Atem voll, und die Sorge kommt abgeschwächt mit. In der
    jetzigen Erfahrung zählt alles voll, was im Feld der ABI auftaucht, egal
    woher es stammt: Die Sorge ist dort wieder stärker als in den Sinnen.
    Zurück in der Familie ist es der Atem, der mitgebracht wird.
    """
    ablauf = {
        0: Entscheidung({"Sorge": Haltung.ENGAGE}, gebiet=SINNE),
        1: Entscheidung({"Atem": Haltung.ENGAGE}),
        2: Entscheidung({"Atem": Haltung.ENGAGE}),
        3: Entscheidung(gebiet=JETZIGE_ERFAHRUNG),
        5: Entscheidung(gebiet="Familie"),
    }
    geist = Geist(lambda lage: ablauf.get(geist.zeit, Entscheidung()), "Familie")
    geist.unterbewusstsein.erlebe(Erfahrung("Sorge", 1.0, zeit=0, gebiet="Familie"))
    for _ in range(7):
        zeige(geist.schritt({"Atem": 0.1}), geist.automatisch.schwelle)


def demo_haltungen() -> None:
    """Die drei Haltungen nebeneinander, in einem einzigen Themengebiet.

    Sorge, Ohrwurm und Hunger stammen aus vorherigen Erfahrungen und sind sofort
    im Feld der ABI. Der Atem ist ein schwacher sensorischer Eindruck, Urlaub ein
    frei gewähltes Thema: Beide tauchen dort erst auf, nachdem die MBI ab
    Moment 2 engaged.
    """

    def entscheider(lage: Lage) -> Entscheidung:
        im_feld = {impuls.thema for impuls in lage.abi_feld}
        haltungen = {}
        if "Sorge" in im_feld:
            haltungen["Sorge"] = Haltung.ENGAGE
        if "Hunger" in im_feld:
            haltungen["Hunger"] = Haltung.DISENGAGE
        if geist.zeit >= 2:
            haltungen["Atem"] = Haltung.ENGAGE
            haltungen["Urlaub"] = Haltung.ENGAGE
        return Entscheidung(haltungen)

    geist = Geist(entscheider, "Alltag")
    for thema in ("Sorge", "Ohrwurm", "Hunger"):
        geist.unterbewusstsein.erlebe(Erfahrung(thema, 0.8, zeit=0, gebiet="Alltag"))
    for _ in range(6):
        zeige(geist.schritt({"Atem": 0.05}), geist.automatisch.schwelle)


DEMOS = {"gebiete": demo_gebiete, "haltungen": demo_haltungen}


def lies_gebiet(text: str) -> str:
    """'jetzt' -> jetzige Erfahrung, 'sinne' -> Sinne, alles andere: ein Themengebiet"""
    return BESONDERE_GEBIETE.get(text.strip().lower(), text.strip())


def lies_entscheidung(text: str) -> Entscheidung:
    """'e Sorge, d Musik, g Arbeit' -> Haltungen zu Sorge und Musik, Wechsel zu Arbeit"""
    haltungen: dict[str, Haltung] = {}
    gebiet = None
    for teil in text.split(","):
        if not teil.strip():
            continue
        taste, _, name = teil.strip().partition(" ")
        taste, name = taste.lower(), name.strip()
        if not name or taste not in {*TASTEN, "g"}:
            raise ValueError(teil.strip())
        if taste == "g":
            gebiet = lies_gebiet(name)
        else:
            haltungen[name] = TASTEN[taste]
    return Entscheidung(haltungen, gebiet)


def frage_entscheidung(lage: Lage) -> Entscheidung:
    feld = ", ".join(f"{i.thema} ({i.staerke:.2f})" for i in lage.abi_feld)
    sinne = ", ".join(f"{t} ({s:.2f})" for t, s in lage.sinne.items())
    print(f"  Du bist in: {benenne(lage.gebiet)}")
    print(f"  ABI-Feld:   {feld or '-'}")
    print(f"  Sinne:      {sinne or '-'}")
    while True:
        antwort = input("  Was tust du? ")
        try:
            return lies_entscheidung(antwort)
        except ValueError as fehler:
            print(f"  Nicht verstanden: '{fehler}'. Beispiel: e Sorge, d Musik, g Arbeit")


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
    print("Du bewegst dich immer in einem Gebiet: in einem Themengebiet deiner Wahl")
    print("(zum Beispiel 'Arbeit'), in den Sinnen ('sinne') oder in der jetzigen")
    print("Erfahrung ('jetzt').")
    print()
    print("Jeder Moment hat zwei Eingaben:")
    print("1. Sinne: 'Thema' oder 'Thema=Stärke' (0 bis 1), mehrere mit Komma.")
    print("   Leer = keine Eindrücke, 'q' beendet.")
    print("2. Was du tust, mehrere mit Komma:")
    print("   'e Thema' engage, 'd Thema' disengage, zu jedem beliebigen Thema.")
    print("   'g Gebiet' richtet dich auf ein neues Gebiet.")
    print("   Leer = weder noch, im Gebiet bleiben.")
    try:
        gebiet = ""
        while not gebiet:
            gebiet = lies_gebiet(input("\nIn welchem Gebiet bewegst du dich? "))
        geist = Geist(frage_entscheidung, gebiet)
        while True:
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
        pass


def main() -> None:
    parser = argparse.ArgumentParser(prog="geist", description=__doc__.splitlines()[0])
    parser.add_argument(
        "--demo",
        nargs="?",
        const="gebiete",
        choices=sorted(DEMOS),
        help="festen Ablauf zeigen (Standard: gebiete)",
    )
    demo = parser.parse_args().demo
    if demo:
        DEMOS[demo]()
    else:
        interaktiv()


if __name__ == "__main__":
    main()
