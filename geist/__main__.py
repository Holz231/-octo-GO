"""Dem Geistmodell zusehen.

    python -m geist                  interaktiv: du bist die MBI
    python -m geist --demo           engage, disengage und weder noch im Vergleich
    python -m geist --demo haltung   wie eine frühere Haltung aus dem AUI auftaucht
    python -m geist --demo gebiete   wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo erinnerung  wie die MBI in die Erinnerung wechselt
    python -m geist --demo gewohnheit  wie wiederholtes engage ein Thema prägt
    python -m geist --demo emotion     wie Emotion und Erfahrung zusammen auftauchen
    python -m geist --demo einfluss    wie ein Gebiet durch Erfahrung an Einfluss gewinnt
    python -m geist --demo heilsam     wie Abneigung die Haltung unheilsam macht

Ein Thema mit Gewohnheit trägt in der Anzeige die Marke ↻ und die Zahl, wie
oft die MBI dazu engaged hat, abzüglich der Male, die sie disengaged hat.
"""

from __future__ import annotations

import argparse
import random
from typing import Mapping

from .modell import (
    EMOTION,
    ERINNERUNG,
    JETZIGE_ERFAHRUNG,
    KOERPER,
    SINNE,
    Entscheidung,
    Erfahrung,
    Geist,
    Umgang,
    Lage,
    Moment,
)

BALKENBREITE = 20
TASTEN = {
    "e": Umgang.ENGAGE,
    "d": Umgang.DISENGAGE,
    "w": Umgang.WEDER_NOCH,
    "v": Umgang.VERLANGEN,
    "a": Umgang.ABNEIGUNG,
}
BESONDERE_GEBIETE = {
    "sinne": SINNE,
    "jetzt": JETZIGE_ERFAHRUNG,
    "jetzige erfahrung": JETZIGE_ERFAHRUNG,
    "erinnerung": ERINNERUNG,
    "emotion": EMOTION,
    "körper": KOERPER,
    "koerper": KOERPER,
}
# Kürzel, mit denen man beim Eingeben sagt, in welchem Gebiet man etwas erlebt.
ERLEBEN = {"s": SINNE, "e": EMOTION, "k": KOERPER}


def benenne(gebiete: tuple[str, ...], einfluss: Mapping[str, float] | None = None) -> str:
    """Nennt die Gebiete, auf Wunsch mit ihrem Einfluss in Prozent."""
    namen = [
        g if g in BESONDERE_GEBIETE.values() else f"Themengebiet {g}" for g in gebiete
    ]
    if einfluss is not None:
        namen = [
            f"{name} (Einfluss {einfluss.get(g, 0.0):.0%})" for name, g in zip(namen, gebiete)
        ]
    return " + ".join(namen)


def nenne_haltung(heilsamkeit: float) -> str:
    """Wo die Haltung zwischen unheilsam und heilsam liegt, in Worten."""
    if heilsamkeit > 0:
        return f"heilsam {heilsamkeit:.0%}"
    if heilsamkeit < 0:
        return f"unheilsam {-heilsamkeit:.0%}"
    return "weder heilsam noch unheilsam"


def nenne_faerbung(faerbung: float) -> str:
    if faerbung > 0:
        return "heilsam"
    if faerbung < 0:
        return "negativ"
    return "-"


def zeige(moment: Moment, schwelle: float) -> None:
    kopf = f"\nMoment {moment.zeit} · Haltung der MBI: {benenne(moment.gebiete, moment.einfluss)}"
    kopf += f", {nenne_haltung(moment.heilsamkeit)}"
    if moment.gebiete_ohne_mbi:
        kopf += f" · ohne MBI: {benenne(moment.gebiete_ohne_mbi, moment.einfluss)}"
    print(kopf)

    impulse = {i.thema: i for i in moment.aui_feld}
    themen = list(impulse)
    if themen:
        # Eine frühere Haltung, die aus dem AUI auftaucht, als solche kennzeichnen.
        namen = {}
        for t in themen:
            namen[t] = f"{t} (Haltung)" if impulse[t].haltung else t
            if impulse[t].gewohnheit:
                namen[t] += f" ↻{impulse[t].gewohnheit}"
        breite = max(len("Thema"), *(len(n) for n in namen.values()))
        # Die beiden Felder grenzen aneinander: Der Balken reicht über die Grenze,
        # sobald ein Impuls stark genug ist, um auch im Feld der ABI aufzutauchen.
        grenze = round(schwelle * BALKENBREITE)
        felder = f"{'AUI':<{grenze}}│{'ABI':<{BALKENBREITE - grenze}}"
        print(
            f"  {'Thema':<{breite}}  {felder}  {'':4}  {'Impuls':<7}  {'MBI':<10}"
            f"  {'Themengebiet':<12}  mitgebracht aus"
        )
        for thema in themen:
            impuls = impulse.get(thema)
            staerke = impuls.staerke if impuls else 0.0
            voll = round(staerke * BALKENBREITE)
            # Rundung darf den Balken nicht auf die falsche Seite der Grenze setzen.
            voll = max(voll, grenze + 1) if staerke >= schwelle else min(voll, grenze)
            balken = "█" * voll + "░" * (BALKENBREITE - voll)
            umgang = moment.umgang.get(thema)
            if thema in moment.gebiete:
                gebiet = "der MBI"
            elif thema in moment.gebiete_ohne_mbi:
                gebiet = "ohne MBI"
            else:
                gebiet = "-"
            herkunft = ", ".join(impuls.mitgebracht_aus) if impuls else ""
            print(
                f"  {namen[thema]:<{breite}}  {balken[:grenze]}│{balken[grenze:]}  {staerke:.2f}"
                f"  {nenne_faerbung(impuls.faerbung):<7}"
                f"  {umgang.value if umgang else '-':<10}  {gebiet:<12}  {herkunft or '-'}"
            )
    else:
        print("  (nichts)")

    if moment.heilsamkeit_danach != moment.heilsamkeit:
        richtung = "heilsamer" if moment.heilsamkeit_danach > moment.heilsamkeit else "unheilsamer"
        print(f"  → Die Haltung wird {richtung}: {nenne_haltung(moment.heilsamkeit_danach)}")
    if moment.verdraengt:
        print(f"  → Zu viel für die MBI, verdrängt wird: {benenne(moment.verdraengt)}")
    if moment.gebiete_danach != moment.gebiete:
        print(f"  → Neue Haltung der MBI: {benenne(moment.gebiete_danach)}")
    for gebiet in moment.gebiete_ohne_mbi_danach:
        if gebiet not in moment.gebiete_ohne_mbi:
            print(f"  → Ohne die MBI wird zum Themengebiet: {gebiet}")
    for gebiet in moment.gebiete_ohne_mbi:
        if gebiet not in moment.gebiete_ohne_mbi_danach + moment.gebiete_danach:
            print(f"  → Themengebiet ohne MBI löst sich auf: {gebiet}")


def demo_umgang() -> None:
    """Engage, disengage und weder noch nebeneinander.

    Sorge, Hunger und Ohrwurm stammen alle aus dem Themengebiet Zuhause und
    sind gleich stark. Die MBI agiert in der Arbeit, also kommen alle drei nur
    abgeschwächt mit. Dann geht sie mit jedem anders um:

    - Sorge: engage. Sie wird im AUI stärker und zum Themengebiet der MBI.
    - Hunger: disengage. Er wird im AUI schwächer und verschwindet.
    - Ohrwurm: weder noch. Er verblasst, hat aber in jedem Moment die Chance,
      ohne die MBI zum Themengebiet zu werden.
    """

    def entscheider(lage: Lage) -> Entscheidung:
        im_feld = {impuls.thema for impuls in lage.abi_feld}
        umgang = {}
        if geist.zeit < 3:
            umgang["Sorge"] = Umgang.ENGAGE
        if "Hunger" in im_feld:
            umgang["Hunger"] = Umgang.DISENGAGE
        return Entscheidung(umgang)

    # Fester Zufall, damit der Ablauf jedes Mal gleich ist.
    geist = Geist(entscheider, "Arbeit", zufall=random.Random(7), mitnahme=0.5, haltungsschritt=0.0)
    for thema in ("Sorge", "Hunger", "Ohrwurm"):
        geist.unterbewusstsein.erlebe(Erfahrung(thema, 1.0, 0, ("Zuhause",)))
    for _ in range(7):
        zeige(geist.schritt(), geist.automatisch.schwelle)


def demo_gebiete() -> None:
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
        chance=0.0,
        mitnahme=0.5,
        haltungsschritt=0.0,
    )
    geist.unterbewusstsein.erlebe(Erfahrung("Sorge", 1.0, 0, ("Familie",)))
    for _ in range(5):
        zeige(geist.schritt({"Atem": 0.3}), geist.automatisch.schwelle)


def demo_erinnerung() -> None:
    """Die MBI holt etwas Verblasstes zurück, indem sie in die Erinnerung wechselt.

    Der Streit liegt lange zurück und ist im AUI fast verklungen. Er taucht
    nicht im Feld der ABI auf, also kann die MBI nicht zu ihm engagen. Sie kann
    aber ihr Thema in die Erinnerung wechseln. Dort zählt Früheres unverblasst,
    der Streit taucht in der ABI auf, und erst jetzt ist engage möglich. Weil
    der Streit aus der Erinnerung stammt, in der die MBI gerade ist, läuft er
    als Themengebiet parallel zu ihr. Dann ist er so stark, dass er die
    Kapazität der MBI allein füllt und die Erinnerung verdrängt. Übrig bleibt
    von ihm, was das Engage im AUI verstärkt hat. Themengebiete ohne die MBI
    sind hier abgeschaltet.
    """
    ablauf = {
        0: Entscheidung(themenwechsel=ERINNERUNG),
        1: Entscheidung({"Streit": Umgang.ENGAGE}),
    }
    geist = Geist(
        lambda lage: ablauf.get(geist.zeit, Entscheidung()),
        "Familie",
        chance=0.0,
        mitnahme=0.5,
        haltungsschritt=0.0,
    )
    geist.unterbewusstsein.erlebe(Erfahrung("Streit", 0.9, -10, ("Familie",)))
    for _ in range(4):
        zeige(geist.schritt(), geist.automatisch.schwelle)


def demo_haltung() -> None:
    """Eine frühere Haltung taucht aus dem AUI auf, und die MBI engaged darauf.

    Die Sorge wurde in der Haltung Familie erlebt, das AUI enthält diese
    Haltung also. Die MBI ist in der Arbeit. Mit der Sorge taucht auch die
    Familie als frühere Haltung im Feld der ABI auf. Die MBI engaged darauf.
    Die Familie kommt aus einem anderen Gebiet, also ersetzt sie die Arbeit als
    Haltung, und die Sorge zählt wieder voll. Der Wechsel ist nicht total: Die
    Arbeit liegt jetzt als frühere Haltung im AUI. Dann engaged die MBI zur
    Sorge. Die stammt aus der jetzigen Haltung, also läuft sie parallel zur
    Familie. Einen Moment später ist die Sorge so stark, dass beides nicht
    mehr in die Kapazität der MBI passt: Die Familie wird verdrängt und liegt
    ihrerseits als frühere Haltung im AUI. Themengebiete ohne die MBI sind
    hier abgeschaltet.
    """
    ablauf = {
        1: Entscheidung({"Familie": Umgang.ENGAGE}),
        2: Entscheidung({"Sorge": Umgang.ENGAGE}),
    }
    geist = Geist(
        lambda lage: ablauf.get(geist.zeit, Entscheidung()),
        "Arbeit",
        chance=0.0,
        mitnahme=0.5,
        haltungsschritt=0.0,
    )
    geist.unterbewusstsein.erlebe(Erfahrung("Sorge", 1.0, 0, ("Familie",)))
    for _ in range(5):
        zeige(geist.schritt(), geist.automatisch.schwelle)


def demo_gewohnheit() -> None:
    """Wiederholtes engage prägt ein Thema: Es verblasst langsamer.

    Grübeln und Ohrwurm sind anfangs gleich stark. Zum Grübeln engaged die MBI
    dreimal, zum Ohrwurm nie. Danach lässt sie beide in Ruhe. Der Ohrwurm
    verblasst schnell, das Grübeln bleibt lange im Feld der ABI, obwohl die
    MBI nichts mehr dafür tut. Themengebiete ohne die MBI sind hier
    abgeschaltet, und die Kapazität ist groß genug für beide.
    """

    def entscheider(lage: Lage) -> Entscheidung:
        return Entscheidung({"Grübeln": Umgang.ENGAGE} if geist.zeit < 3 else {})

    geist = Geist(entscheider, "Abend", chance=0.0, kapazitaet=3.0, mitnahme=0.5, haltungsschritt=0.0)
    for thema in ("Grübeln", "Ohrwurm"):
        geist.unterbewusstsein.erlebe(Erfahrung(thema, 0.8, 0, ("Abend",)))
    for _ in range(9):
        zeige(geist.schritt(), geist.automatisch.schwelle)


def demo_emotion() -> None:
    """Eine Emotion und eine Erfahrung sind eigene Themen, tauchen aber zusammen auf.

    In Moment 0 hört die MBI einen Streit und erlebt dabei Wut. Der Streit ist
    ein Sinneseindruck, die Wut eine Emotion: zwei Themen in zwei Gebieten.
    Weil sie zusammen erlebt wurden, sind sie verknüpft. Beide klingen ab und
    verschwinden aus dem Feld der ABI. In Moment 6 hört die MBI nur wieder
    einen Streit, ohne neue Wut, und die Wut taucht von selbst mit auf.
    Themengebiete ohne die MBI sind hier abgeschaltet.
    """
    sinne = {0: {"Streit": 0.9}, 6: {"Streit": 0.9}}
    emotion = {0: {"Wut": 0.7}}
    geist = Geist(lambda lage: Entscheidung(), SINNE, chance=0.0, mitnahme=0.5, haltungsschritt=0.0)
    for zeit in range(8):
        moment = geist.schritt(sinne.get(zeit), emotion.get(zeit))
        zeige(moment, geist.automatisch.schwelle)


def demo_einfluss() -> None:
    """Ein Gebiet gewinnt durch Erfahrung an Einfluss auf die Impulse des AUI.

    Die MBI ist im Hobby, einem Gebiet, in dem sie noch kaum etwas erlebt hat.
    Es hat deshalb wenig Einfluss, und die Sorge aus der Familie kommt fast
    ungebremst mit. Die MBI engaged nun Moment für Moment zum Malen. Mit jeder
    Erfahrung wächst der Einfluss des Hobbys, und es drängt die Sorge immer
    weiter zurück, bis sie aus dem Feld der ABI verschwindet. Damit man nur
    diese Wirkung sieht, verblasst hier nichts von selbst, die Kapazität ist
    groß, und Themengebiete ohne die MBI sind abgeschaltet.
    """
    geist = Geist(
        lambda lage: Entscheidung({"Malen": Umgang.ENGAGE}),
        "Hobby",
        nachklang=1.0,
        kapazitaet=9.0,
        chance=0.0,
        haltungsschritt=0.0,
    )
    geist.unterbewusstsein.erlebe(Erfahrung("Sorge", 0.9, 0, ("Familie",)))
    geist.unterbewusstsein.erlebe(Erfahrung("Malen", 0.5, 0, ("Hobby",)))
    for _ in range(5):
        zeige(geist.schritt(), geist.automatisch.schwelle)


def demo_heilsam() -> None:
    """Dieselbe Unruhe, zwei Arten, mit ihr umzugehen.

    In jedem Moment kommt neue Unruhe auf. Die MBI ist im Gebiet der Emotion
    und disengaged jedes Mal, wenn die Unruhe im Feld der ABI auftaucht: links
    aus Abneigung, rechts ohne Abneigung. Beides schwächt die Unruhe im AUI
    gleich stark. Aus Abneigung wird die Haltung aber unheilsam und die Unruhe
    negativ, und das AUI erzeugt mehr davon. Ohne Abneigung wird die Haltung
    heilsam, und das AUI erzeugt insgesamt weniger.
    """

    def lauf(umgang: Umgang) -> list[tuple[float, float]]:
        def entscheider(lage: Lage) -> Entscheidung:
            taucht_auf = any(impuls.thema == "Unruhe" for impuls in lage.abi_feld)
            return Entscheidung({"Unruhe": umgang} if taucht_auf else {})

        geist = Geist(entscheider, EMOTION, chance=0.0, mitnahme=0.5)
        verlauf = []
        for _ in range(9):
            moment = geist.schritt(emotion={"Unruhe": 0.3})
            unruhe = next((i.staerke for i in moment.aui_feld if i.thema == "Unruhe"), 0.0)
            verlauf.append((unruhe, moment.heilsamkeit))
        return verlauf

    print(f"\n{'':8}  {'disengage aus Abneigung':<37}  disengage ohne Abneigung")
    print(f"{'Moment':<8}  {'Unruhe':<7} {'Haltung':<29}  {'Unruhe':<7} Haltung")
    for zeit, (aus_abneigung, ohne) in enumerate(zip(lauf(Umgang.ABNEIGUNG), lauf(Umgang.DISENGAGE))):
        print(
            f"{zeit:<8}  {aus_abneigung[0]:<7.2f} {nenne_haltung(aus_abneigung[1]):<29}"
            f"  {ohne[0]:<7.2f} {nenne_haltung(ohne[1])}"
        )


DEMOS = {
    "heilsam": demo_heilsam,
    "einfluss": demo_einfluss,
    "gewohnheit": demo_gewohnheit,
    "emotion": demo_emotion,
    "haltung": demo_haltung,
    "umgang": demo_umgang,
    "gebiete": demo_gebiete,
    "erinnerung": demo_erinnerung,
}


def lies_gebiet(text: str) -> str:
    """'jetzt' -> jetzige Erfahrung, 'sinne' -> Sinne, alles andere: ein Themengebiet"""
    return BESONDERE_GEBIETE.get(text.strip().lower(), text.strip())


def lies_entscheidung(text: str) -> Entscheidung:
    """'e Sorge, d Musik, g sinne' -> Umgang mit Sorge und Musik, Wechsel in die Sinne"""
    umgang: dict[str, Umgang] = {}
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
            umgang[name] = TASTEN[taste]
    return Entscheidung(umgang, gebiet)


def frage_entscheidung(lage: Lage) -> Entscheidung:
    feld = ", ".join(f"{i.thema} ({i.staerke:.2f})" for i in lage.abi_feld)
    print(f"  Deine Haltung: {benenne(lage.gebiete)}, {nenne_haltung(lage.heilsamkeit)}")
    if lage.gebiete_ohne_mbi:
        print(f"  Ohne dich:     {benenne(lage.gebiete_ohne_mbi)}")
    print(f"  ABI-Feld:      {feld or '-'}")
    for name, erlebtes in (
        ("Sinne:", lage.sinne),
        ("Emotion:", lage.emotion),
        ("Körper:", lage.koerper),
    ):
        if erlebtes or name == "Sinne:":
            liste = ", ".join(f"{t} ({s:.2f})" for t, s in erlebtes.items())
            print(f"  {name:<14} {liste or '-'}")
    im_feld = {impuls.thema for impuls in lage.abi_feld}
    while True:
        antwort = input("  Was tust du? ")
        try:
            entscheidung = lies_entscheidung(antwort)
        except ValueError as fehler:
            print(f"  Nicht verstanden: '{fehler}'. Beispiel: e Sorge, d Musik, g sinne")
            continue
        fremd = [thema for thema in entscheidung.umgang if thema not in im_feld]
        if not fremd:
            return entscheidung
        print(f"  Nicht im ABI-Feld: {', '.join(fremd)}. Engage und disengage gibt es")
        print("  nur zu dem, was dort auftaucht. Für einen Themenwechsel: g Gebiet")


def lies_erlebtes(text: str) -> dict[str, dict[str, float]]:
    """'Laerm, e:Angst=0.7, k:Enge' -> je Gebiet, was darin erlebt wird.

    Ohne Kürzel ist es ein Sinneseindruck, 'e:' eine Emotion, 'k:' eine
    Körperempfindung. Ohne Stärke gilt 0.5.
    """
    erlebtes: dict[str, dict[str, float]] = {gebiet: {} for gebiet in ERLEBEN.values()}
    for teil in text.split(","):
        kuerzel, doppelpunkt, rest = teil.partition(":")
        if doppelpunkt and kuerzel.strip().lower() in ERLEBEN:
            gebiet, teil = ERLEBEN[kuerzel.strip().lower()], rest
        else:
            gebiet = SINNE
        thema, _, staerke = teil.partition("=")
        if thema.strip():
            erlebtes[gebiet][thema.strip()] = float(staerke) if staerke.strip() else 0.5
    return erlebtes


def interaktiv() -> None:
    print("Du bist die manuelle bewusste Intention (MBI).")
    print("Deine Haltung ist das Gebiet, in dem du agierst.")
    print()
    print("Jeder Moment hat zwei Eingaben:")
    print("1. Was du erlebst: 'Thema' oder 'Thema=Stärke' (0 bis 1), mehrere mit Komma.")
    print("   Ohne Kürzel ist es ein Sinneseindruck. 'e:Angst' ist eine Emotion,")
    print("   'k:Enge' eine Körperempfindung. Leer = nichts, 'q' beendet.")
    print("2. Was du tust, mehrere mit Komma:")
    print("   'e Thema'  engage: verstärkt das Thema und macht es zu deiner Haltung.")
    print("              Stammt es aus deiner jetzigen Haltung, läuft es parallel")
    print("              dazu. Kommt es aus einem anderen Gebiet, ersetzt es sie.")
    print("              Das geht auch mit einer früheren Haltung, die auftaucht.")
    print("   'd Thema'  disengage: schwächt das Thema, es gehört nicht mehr zu deiner Haltung.")
    print("              Beides geht nur zu Themen, die im ABI-Feld auftauchen, und")
    print("              macht deine Haltung heilsamer.")
    print("   'v Thema'  engage aus Verlangen, 'a Thema' disengage aus Abneigung:")
    print("              Sie wirken auf das Thema wie engage und disengage, machen")
    print("              deine Haltung aber unheilsamer und das Thema negativ.")
    print("   'g Gebiet' Themenwechsel, ohne etwas zu verstärken: in ein beliebiges")
    print("              Themengebiet, 'sinne', 'jetzt' (die jetzige Erfahrung),")
    print("              'erinnerung', 'emotion' oder 'körper'. Das macht deine Haltung")
    print("              heilsamer, auch wenn du dich auf dein jetziges Gebiet richtest.")
    print("   Leer = Themenerhalt und weder noch: Dann kann ein Thema im ABI-Feld")
    print("   von selbst zum Themengebiet werden.")
    try:
        gebiet = ""
        while not gebiet:
            gebiet = lies_gebiet(input("\nIn welcher Haltung bist du? "))
        geist = Geist(frage_entscheidung, gebiet)
        while True:
            eingabe = input("\nWas erlebst du gerade? ")
            if eingabe.strip().lower() == "q":
                break
            try:
                erlebtes = lies_erlebtes(eingabe)
            except ValueError:
                print("  Stärke muss eine Zahl sein, zum Beispiel Atem=0.1")
                continue
            moment = geist.schritt(erlebtes[SINNE], erlebtes[EMOTION], erlebtes[KOERPER])
            zeige(moment, geist.automatisch.schwelle)
    except EOFError:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(prog="geist", description=__doc__.splitlines()[0])
    parser.add_argument(
        "--demo",
        nargs="?",
        const="umgang",
        choices=sorted(DEMOS),
        help="festen Ablauf zeigen (Standard: umgang)",
    )
    args = parser.parse_args()
    if args.demo:
        DEMOS[args.demo]()
    else:
        interaktiv()


if __name__ == "__main__":
    main()
