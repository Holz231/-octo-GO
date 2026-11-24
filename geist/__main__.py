"""Dem Geistmodell zusehen.

    python -m geist                  interaktiv: du bist die MBI
    python -m geist --demo           wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo haltungen die drei Haltungen und Quellen im Vergleich
"""

from __future__ import annotations

import argparse

from .modell import Entscheidung, Erfahrung, Geist, Haltung, Lage, Moment

BALKENBREITE = 20
TASTEN = {"e": Haltung.ENGAGE, "d": Haltung.DISENGAGE, "w": Haltung.WEDER_NOCH}


def zeige(moment: Moment, schwelle: float) -> None:
    print(f"\nMoment {moment.zeit} · MBI im Themengebiet: {moment.gebiet}")
    impulse = {i.thema: i for i in moment.aui_feld}
    ausrichtungen = {a.thema: a for a in moment.ausrichtungen}
    # Auch Themen zeigen, auf die sich die MBI richtet, ohne dass ein Impuls da ist.
    themen = list(impulse) + [t for t in ausrichtungen if t not in impulse]
    if themen:
        breite = max(len("Thema"), *(len(t) for t in themen))
        # Die beiden Felder grenzen aneinander: Der Balken reicht über die Grenze,
        # sobald ein Impuls stark genug ist, um auch im Feld der ABI aufzutauchen.
        grenze = round(schwelle * BALKENBREITE)
        felder = f"{'AUI':<{grenze}}│{'ABI':<{BALKENBREITE - grenze}}"
        print(
            f"  {'Thema':<{breite}}  {felder}  {'':4}  {'MBI':<10}"
            f"  {'Haltung zu':<17}  mitgebracht aus"
        )
        for thema in themen:
            impuls = impulse.get(thema)
            staerke = impuls.staerke if impuls else 0.0
            voll = round(staerke * BALKENBREITE)
            # Rundung darf den Balken nicht auf die falsche Seite der Grenze setzen.
            voll = max(voll, grenze + 1) if staerke >= schwelle else min(voll, grenze)
            balken = "█" * voll + "░" * (BALKENBREITE - voll)
            a = ausrichtungen.get(thema)
            herkunft = ", ".join(impuls.mitgebracht_aus) if impuls else ""
            print(
                f"  {thema:<{breite}}  {balken[:grenze]}│{balken[grenze:]}  {staerke:.2f}"
                f"  {a.haltung.value if a else '-':<10}"
                f"  {a.quelle.value if a else '-':<17}  {herkunft or '-'}"
            )
    else:
        print("  (nichts)")
    if moment.wechsel_nach:
        print(f"  Die MBI richtet sich auf ein neues Themengebiet: {moment.wechsel_nach}")


def demo_gebiete() -> None:
    """Das AUI führt Themen aus einem Gebiet mit in das nächste.

    Die Sorge stammt aus dem Gebiet Familie. Wechselt die MBI zur Arbeit, kommt
    die Sorge abgeschwächt mit und prägt dort die wahrgenommene Realität, bis
    sie verblasst. Zurück in der Familie ist sie wieder voll da, und jetzt ist
    es die Mail aus der Arbeit, die mitgebracht wird.
    """
    ablauf = {
        0: Entscheidung({"Sorge": Haltung.ENGAGE}),
        1: Entscheidung(gebiet="Arbeit"),
        2: Entscheidung({"Mail": Haltung.ENGAGE}),
        3: Entscheidung({"Mail": Haltung.ENGAGE}),
        4: Entscheidung(gebiet="Familie"),
    }
    sinne = {2: {"Mail": 0.6}}
    geist = Geist(lambda lage: ablauf.get(geist.zeit, Entscheidung()), "Familie")
    geist.unterbewusstsein.erlebe(Erfahrung("Sorge", 1.0, zeit=0, gebiet="Familie"))
    for zeit in range(6):
        zeige(geist.schritt(sinne.get(zeit)), geist.automatisch.schwelle)


def demo_haltungen() -> None:
    """Drei Haltungen und drei Quellen nebeneinander, in einem einzigen Gebiet.

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
            gebiet = name
        else:
            haltungen[name] = TASTEN[taste]
    return Entscheidung(haltungen, gebiet)


def frage_entscheidung(lage: Lage) -> Entscheidung:
    feld = ", ".join(f"{i.thema} ({i.staerke:.2f})" for i in lage.abi_feld)
    sinne = ", ".join(f"{t} ({s:.2f})" for t, s in lage.sinne.items())
    print(f"  Themengebiet: {lage.gebiet}")
    print(f"  ABI-Feld:     {feld or '-'}")
    print(f"  Sinne:        {sinne or '-'}")
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
    print("Jeder Moment hat zwei Eingaben:")
    print("1. Sinne: 'Thema' oder 'Thema=Stärke' (0 bis 1), mehrere mit Komma.")
    print("   Leer = keine Eindrücke, 'q' beendet.")
    print("2. Was du tust, mehrere mit Komma:")
    print("   'e Thema' engage, 'd Thema' disengage. Das Thema darf aus dem")
    print("   ABI-Feld, aus den Sinnen oder frei gewählt sein.")
    print("   'g Gebiet' richtet dich auf ein neues Themengebiet.")
    print("   Leer = weder noch, im Gebiet bleiben.")
    try:
        gebiet = ""
        while not gebiet:
            gebiet = input("\nIn welchem Themengebiet bewegst du dich? ").strip()
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
