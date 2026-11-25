"""Dem Geistmodell zusehen.

    python -m geist                  interaktiv: du bist die MBI
    python -m geist --demo           die drei Haltungen im Vergleich
    python -m geist --demo gebiete   wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo erinnerung  wie die MBI in die Erinnerung wechselt

Mit --mehrere hält die MBI mehrere Gebiete zugleich statt nur eines.
"""

from __future__ import annotations

import argparse
import random

from .modell import (
    ERINNERUNG,
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
    "erinnerung": ERINNERUNG,
}


def benenne(gebiete: tuple[str, ...]) -> str:
    namen = [
        g if g in (SINNE, JETZIGE_ERFAHRUNG, ERINNERUNG) else f"Themengebiet {g}" for g in gebiete
    ]
    return " + ".join(namen)


def zeige(moment: Moment, schwelle: float) -> None:
    kopf = f"\nMoment {moment.zeit} · MBI agiert in: {benenne(moment.gebiete)}"
    if moment.gebiete_ohne_mbi:
        kopf += f" · ohne MBI: {benenne(moment.gebiete_ohne_mbi)}"
    print(kopf)

    impulse = {i.thema: i for i in moment.aui_feld}
    themen = list(impulse)
    if themen:
        breite = max(len("Thema"), *(len(t) for t in themen))
        # Die beiden Felder grenzen aneinander: Der Balken reicht über die Grenze,
        # sobald ein Impuls stark genug ist, um auch im Feld der ABI aufzutauchen.
        grenze = round(schwelle * BALKENBREITE)
        felder = f"{'AUI':<{grenze}}│{'ABI':<{BALKENBREITE - grenze}}"
        print(
            f"  {'Thema':<{breite}}  {felder}  {'':4}  {'Haltung':<10}"
            f"  {'Themengebiet':<12}  mitgebracht aus"
        )
        for thema in themen:
            impuls = impulse.get(thema)
            staerke = impuls.staerke if impuls else 0.0
            voll = round(staerke * BALKENBREITE)
            # Rundung darf den Balken nicht auf die falsche Seite der Grenze setzen.
            voll = max(voll, grenze + 1) if staerke >= schwelle else min(voll, grenze)
            balken = "█" * voll + "░" * (BALKENBREITE - voll)
            haltung = moment.haltungen.get(thema)
            if thema in moment.gebiete:
                gebiet = "der MBI"
            elif thema in moment.gebiete_ohne_mbi:
                gebiet = "ohne MBI"
            else:
                gebiet = "-"
            herkunft = ", ".join(impuls.mitgebracht_aus) if impuls else ""
            print(
                f"  {thema:<{breite}}  {balken[:grenze]}│{balken[grenze:]}  {staerke:.2f}"
                f"  {haltung.value if haltung else '-':<10}  {gebiet:<12}  {herkunft or '-'}"
            )
    else:
        print("  (nichts)")

    if moment.gebiete_danach != moment.gebiete:
        print(f"  → Die MBI agiert ab jetzt in: {benenne(moment.gebiete_danach)}")
    for gebiet in moment.gebiete_ohne_mbi_danach:
        if gebiet not in moment.gebiete_ohne_mbi:
            print(f"  → Ohne die MBI wird zum Themengebiet: {gebiet}")
    for gebiet in moment.gebiete_ohne_mbi:
        if gebiet not in moment.gebiete_ohne_mbi_danach + moment.gebiete_danach:
            print(f"  → Themengebiet ohne MBI löst sich auf: {gebiet}")


def demo_haltungen(mehrere: bool) -> None:
    """Die drei Haltungen nebeneinander.

    Sorge, Hunger und Ohrwurm stammen alle aus dem Themengebiet Zuhause und
    sind gleich stark. Die MBI agiert in der Arbeit, also kommen alle drei nur
    abgeschwächt mit. Dann nimmt sie zu jedem eine andere Haltung ein:

    - Sorge: engage. Sie wird im AUI stärker und zum Themengebiet der MBI.
    - Hunger: disengage. Er wird im AUI schwächer und verschwindet.
    - Ohrwurm: weder noch. Er verblasst, hat aber in jedem Moment die Chance,
      ohne die MBI zum Themengebiet zu werden.
    """

    def entscheider(lage: Lage) -> Entscheidung:
        im_feld = {impuls.thema for impuls in lage.abi_feld}
        haltungen = {}
        if geist.zeit < 3:
            haltungen["Sorge"] = Haltung.ENGAGE
        if "Hunger" in im_feld:
            haltungen["Hunger"] = Haltung.DISENGAGE
        return Entscheidung(haltungen)

    # Fester Zufall, damit der Ablauf jedes Mal gleich ist.
    geist = Geist(entscheider, "Arbeit", mehrere=mehrere, zufall=random.Random(7))
    for thema in ("Sorge", "Hunger", "Ohrwurm"):
        geist.unterbewusstsein.erlebe(Erfahrung(thema, 1.0, 0, ("Zuhause",)))
    for _ in range(7):
        zeige(geist.schritt(), geist.automatisch.schwelle)


def demo_gebiete(mehrere: bool) -> None:
    """Die MBI wandert durch alle drei Arten von Gebieten.

    Die Sorge stammt aus dem Themengebiet Familie, der Atem ist ein
    Sinneseindruck. In der Familie taucht nur die Sorge im Feld der ABI auf. In
    den Sinnen zählt der Atem voll, und die Sorge kommt abgeschwächt mit. In der
    jetzigen Erfahrung zählt alles voll, was im Feld der ABI auftaucht, egal
    woher es stammt. Zurück in der Familie ist es der Atem, der mitgebracht
    wird. Themengebiete ohne die MBI sind hier abgeschaltet.
    """
    ablauf = {
        0: Entscheidung(themenwechsel=SINNE),
        1: Entscheidung(themenwechsel=JETZIGE_ERFAHRUNG),
        3: Entscheidung(themenwechsel="Familie"),
    }
    geist = Geist(
        lambda lage: ablauf.get(geist.zeit, Entscheidung()),
        "Familie",
        mehrere=mehrere,
        chance=0.0,
    )
    geist.unterbewusstsein.erlebe(Erfahrung("Sorge", 1.0, 0, ("Familie",)))
    for _ in range(5):
        zeige(geist.schritt({"Atem": 0.3}), geist.automatisch.schwelle)


def demo_erinnerung(mehrere: bool) -> None:
    """Die MBI holt etwas Verblasstes zurück, indem sie in die Erinnerung wechselt.

    Der Streit liegt lange zurück und ist im AUI fast verklungen. Er taucht
    nicht im Feld der ABI auf, also kann die MBI nicht zu ihm engagen. Sie kann
    aber ihr Thema in die Erinnerung wechseln. Dort zählt Früheres unverblasst,
    der Streit taucht in der ABI auf, und erst jetzt ist engage möglich: Der
    Streit wird ein eigenes Themengebiet der MBI. Themengebiete ohne die MBI
    sind hier abgeschaltet.
    """
    ablauf = {
        0: Entscheidung(themenwechsel=ERINNERUNG),
        1: Entscheidung({"Streit": Haltung.ENGAGE}),
        2: Entscheidung({"Streit": Haltung.ENGAGE}),
    }
    geist = Geist(
        lambda lage: ablauf.get(geist.zeit, Entscheidung()),
        "Familie",
        mehrere=mehrere,
        chance=0.0,
    )
    geist.unterbewusstsein.erlebe(Erfahrung("Streit", 0.9, -10, ("Familie",)))
    for _ in range(4):
        zeige(geist.schritt(), geist.automatisch.schwelle)


DEMOS = {
    "haltungen": demo_haltungen,
    "gebiete": demo_gebiete,
    "erinnerung": demo_erinnerung,
}


def lies_gebiet(text: str) -> str:
    """'jetzt' -> jetzige Erfahrung, 'sinne' -> Sinne, alles andere: ein Themengebiet"""
    return BESONDERE_GEBIETE.get(text.strip().lower(), text.strip())


def lies_entscheidung(text: str) -> Entscheidung:
    """'e Sorge, d Musik, g sinne' -> Haltungen zu Sorge und Musik, Wechsel in die Sinne"""
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
    print(f"  Du agierst in: {benenne(lage.gebiete)}")
    if lage.gebiete_ohne_mbi:
        print(f"  Ohne dich:     {benenne(lage.gebiete_ohne_mbi)}")
    print(f"  ABI-Feld:      {feld or '-'}")
    print(f"  Sinne:         {sinne or '-'}")
    im_feld = {impuls.thema for impuls in lage.abi_feld}
    while True:
        antwort = input("  Was tust du? ")
        try:
            entscheidung = lies_entscheidung(antwort)
        except ValueError as fehler:
            print(f"  Nicht verstanden: '{fehler}'. Beispiel: e Sorge, d Musik, g sinne")
            continue
        fremd = [thema for thema in entscheidung.haltungen if thema not in im_feld]
        if not fremd:
            return entscheidung
        print(f"  Nicht im ABI-Feld: {', '.join(fremd)}. Engage und disengage gibt es")
        print("  nur zu dem, was dort auftaucht. Für einen Themenwechsel: g Gebiet")


def lies_sinne(text: str) -> dict[str, float]:
    """'Laerm, Atem=0.1' -> {'Laerm': 0.5, 'Atem': 0.1}"""
    sinne: dict[str, float] = {}
    for teil in text.split(","):
        thema, _, staerke = teil.partition("=")
        if thema.strip():
            sinne[thema.strip()] = float(staerke) if staerke.strip() else 0.5
    return sinne


def interaktiv(mehrere: bool) -> None:
    print("Du bist die manuelle bewusste Intention (MBI).")
    if mehrere:
        print("Du hältst mehrere Gebiete zugleich.")
    else:
        print("Du hältst immer nur ein Gebiet. (Mehrere zugleich: mit --mehrere starten.)")
    print()
    print("Jeder Moment hat zwei Eingaben:")
    print("1. Sinne: 'Thema' oder 'Thema=Stärke' (0 bis 1), mehrere mit Komma.")
    print("   Leer = keine Eindrücke, 'q' beendet.")
    print("2. Was du tust, mehrere mit Komma:")
    print("   'e Thema'  engage: verstärkt das Thema und macht es zu deinem Themengebiet.")
    print("   'd Thema'  disengage: schwächt das Thema, es ist kein Gebiet von dir mehr.")
    print("              Beides geht nur zu Themen, die im ABI-Feld auftauchen.")
    print("   'g Gebiet' Themenwechsel, ohne etwas zu verstärken: in ein beliebiges")
    print("              Themengebiet, 'sinne', 'jetzt' (die jetzige Erfahrung) oder")
    print("              'erinnerung'.")
    print("   Leer = Themenerhalt und weder noch: Dann kann ein Thema im ABI-Feld")
    print("   von selbst zum Themengebiet werden.")
    try:
        gebiet = ""
        while not gebiet:
            gebiet = lies_gebiet(input("\nIn welchem Gebiet agierst du? "))
        geist = Geist(frage_entscheidung, gebiet, mehrere=mehrere)
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
        const="haltungen",
        choices=sorted(DEMOS),
        help="festen Ablauf zeigen (Standard: haltungen)",
    )
    parser.add_argument(
        "--mehrere",
        action="store_true",
        help="die MBI hält mehrere Gebiete zugleich statt nur eines",
    )
    args = parser.parse_args()
    if args.demo:
        DEMOS[args.demo](args.mehrere)
    else:
        interaktiv(args.mehrere)


if __name__ == "__main__":
    main()
