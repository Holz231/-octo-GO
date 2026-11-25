"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Die Layer:

- AUI: das automatische Unterbewusstsein
- ABI: die automatische bewusste Intention
- MBI: die manuelle bewusste Intention

AUI und ABI sind zwei verschiedene, aneinander angrenzende Felder.

Die MBI befindet sich immer in einer Haltung. Die Haltung ist das Gebiet, das
die MBI erschafft und in dem sie agiert, manchmal mehrere zugleich. Ein
Gebiet kann ein Themengebiet sein (davon gibt es unendlich viele), die jetzige
Erfahrung, die Sinne oder die Erinnerung. Die jetzige Erfahrung ist alles, was
im Feld der ABI auftaucht. An den Gebieten orientieren sich AUI und ABI. Das
AUI führt aber vergangene Themen und Erfahrungen mit in jedes neue Gebiet. Wie
die MBI und das AUI gerade sind, formt gleichzeitig die wahrgenommene Realität
der ABI.

Das AUI kann die Haltung beeinflussen: Enthält es eine frühere Haltung, kann
diese im Bewusstsein auftauchen, und die MBI kann dann darauf engagen.

Einen Umgang gibt es nur mit dem, was aus dem AUI im Feld der ABI auftaucht.
Die drei Arten, wie die MBI mit einem solchen Thema umgeht:

- engage verstärkt das Thema im AUI. Zugleich macht die MBI es zu einem neuen
  Themengebiet, in dem sie agiert. Stammt das Thema aus der jetzigen Haltung,
  läuft es parallel zu ihr. Kommt es aus einem anderen Gebiet, ersetzt es sie.
  Der Wechsel ist dabei nicht total, weil die vorherige Haltung dann im AUI
  liegt und von dort wieder auftauchen kann.
- disengage schwächt das Thema im AUI und verhindert, dass die MBI es zu einem
  Themengebiet macht.
- weder noch verstärkt nicht und schwächt nicht. Es lässt aber die Chance, dass
  das Thema ohne die MBI aus dem AUI in die ABI geht und dort von selbst zu
  einem Themengebiet wird. Oder es verblasst wieder.

Die MBI kann sich auch autonom ausrichten, auch auf Themengebiete, die vorher
nicht im Bewusstsein waren. Das ist kein engage, sondern lediglich ein
Themenwechsel oder ein Themenerhalt: Im AUI wird dabei nichts verstärkt.

Mit etwas, das nur im AUI liegt, kann die MBI nicht umgehen. Sie kann aber
Erinnerungen aktivieren. Die Erinnerung ist dabei nur ein anderes Gebiet: Die
MBI aktiviert sie, indem sie ihr Thema dorthin wechselt.

Ablauf eines Moments:

1. Das AUI erzeugt Impulse aus vorherigen und jetzigen Erfahrungen, orientiert
   an den Gebieten. Sie liegen im Feld des AUI.
2. Ein Teil davon taucht im angrenzenden Feld der ABI auf: Das ist die
   wahrgenommene Realität. Die Impulse werden dabei nicht zur ABI, sie werden
   von ihr nur wahrgenommen.
3. Die MBI geht mit dem um, was auftaucht, und wechselt oder erhält ihr Thema.
4. Engage und disengage werden selbst zur Erfahrung. Nur so, also indirekt,
   erreicht die MBI das AUI.
5. In der ABI können Themengebiete ohne die MBI entstehen oder sich auflösen.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Collection, Mapping

# Schwächere Impulse gelten als nicht vorhanden.
MINDESTSTAERKE = 0.01

# Drei besondere Gebiete, in denen sich die MBI bewegen kann. Jeder andere Name
# steht für ein Themengebiet.
SINNE = "Sinne"
JETZIGE_ERFAHRUNG = "jetzige Erfahrung"
ERINNERUNG = "Erinnerung"
BESONDERE_GEBIETE = (SINNE, JETZIGE_ERFAHRUNG, ERINNERUNG)

# Herkunft von etwas, das in der jetzigen Erfahrung entstanden ist, aber nicht
# mehr im Feld der ABI auftaucht.
FRUEHER = "früher"


class Umgang(Enum):
    """Wie die MBI mit einem Thema umgeht, das im Feld der ABI auftaucht."""

    ENGAGE = "engage"
    DISENGAGE = "disengage"
    WEDER_NOCH = "weder noch"  # "non disengage and non engage"


@dataclass(frozen=True)
class Erfahrung:
    thema: str
    staerke: float  # negativ = wirkt dem Thema entgegen
    zeit: int
    # Die Gebiete, zu denen sie gehört. Bei allem, was die MBI erlebt hat, ist
    # das die Haltung, in der sie dabei war: Die Erfahrung enthält sie.
    gebiete: tuple[str, ...]


@dataclass(frozen=True)
class Impuls:
    thema: str
    staerke: float  # 0 bis 1
    # Andere Gebiete, aus denen das AUI diesen Impuls mitgebracht hat.
    mitgebracht_aus: tuple[str, ...] = ()
    # Ob das kein Thema ist, sondern eine frühere Haltung, die das AUI enthält.
    haltung: bool = False
    # Ob das Thema aus der jetzigen Haltung der MBI stammt.
    aus_haltung: bool = False


@dataclass(frozen=True)
class Lage:
    """Alles, was der MBI zugänglich ist. Das Feld des AUI gehört nicht dazu."""

    gebiete: tuple[str, ...]  # ihre Haltung: die Gebiete, in denen sie gerade agiert
    gebiete_ohne_mbi: tuple[str, ...]  # Themengebiete, die von selbst entstanden sind
    abi_feld: tuple[Impuls, ...]  # die wahrgenommene Realität
    sinne: Mapping[str, float]  # sensorische Eindrücke: Thema -> Stärke

    def staerke(self, thema: str) -> float:
        """Wie stark ein Thema im Feld der ABI auftaucht (0 = gar nicht)."""
        for impuls in self.abi_feld:
            if impuls.thema == thema:
                return impuls.staerke
        return 0.0


@dataclass(frozen=True)
class Entscheidung:
    """Was die MBI in einem Moment willentlich tut."""

    # Thema -> Umgang, nur mit Themen im Feld der ABI. Alles, was dort nicht
    # genannt wird, bleibt bei "weder noch".
    umgang: Mapping[str, Umgang] = field(default_factory=dict)
    # Das Gebiet, auf das sie sich autonom richtet. None = Themenerhalt.
    themenwechsel: str | None = None


# ANNAHME (noch nicht vom Modell vorgegeben): wie stark engage und disengage als
# neue Erfahrung im AUI wirken. Weder noch wirkt laut Modell gar nicht.
STANDARD_WIRKUNG: Mapping[Umgang, float] = {
    Umgang.ENGAGE: 0.4,
    Umgang.DISENGAGE: -0.4,
    Umgang.WEDER_NOCH: 0.0,
}


def gehoert_zum_gebiet(
    erfahrung: Erfahrung, gebiet: str, im_abi_feld: Collection[str]
) -> bool:
    """Ob eine Erfahrung in einem Gebiet voll zählt, statt nur mitgeführt zu werden."""
    if gebiet == JETZIGE_ERFAHRUNG:
        # Die jetzige Erfahrung ist alles, was im Feld der ABI auftaucht, egal
        # aus welchem Gebiet es stammt.
        return erfahrung.thema in im_abi_feld
    # ANNAHME: Zu einem Themengebiet gehört das Thema, aus dem es entstanden
    # ist, und alles, was in diesem Gebiet erlebt wurde.
    return gebiet in erfahrung.gebiete or erfahrung.thema == gebiet


class Unterbewusstsein:
    """AUI. Automatisch und unbewusst: läuft ständig und erzeugt Impulse.

    Die Impulse liegen in seinem Feld, das an das Feld der ABI angrenzt.
    """

    def __init__(self, nachklang: float = 0.8, mitnahme: float = 0.5):
        # ANNAHME: Eine Erfahrung wirkt pro Moment um diesen Faktor schwächer nach.
        self.nachklang = nachklang
        # ANNAHME: Erfahrungen aus anderen Gebieten kommen mit diesem Anteil
        # ihrer Stärke mit. Die aus den jetzigen Gebieten zählen voll.
        self.mitnahme = mitnahme
        self.erfahrungen: list[Erfahrung] = []
        self.feld: list[Impuls] = []

    def erlebe(self, erfahrung: Erfahrung) -> None:
        self.erfahrungen.append(erfahrung)

    def erzeuge_impulse(
        self,
        zeit: int,
        gebiete: Collection[str],
        im_abi_feld: Collection[str] = (),
        haltung: Collection[str] | None = None,
    ) -> list[Impuls]:
        """Füllt das Feld mit Impulsen, orientiert an den Gebieten.

        `im_abi_feld` sind die Themen, die bisher im Feld der ABI auftauchen.
        Sie bestimmen, was zur jetzigen Erfahrung gehört. `haltung` sind die
        Gebiete der MBI unter `gebiete`; ohne Angabe sind es alle.
        """
        haltung = gebiete if haltung is None else haltung
        staerken: dict[str, float] = {}
        aus_haltung: dict[str, float] = {}  # Thema -> Stärke aus der Haltung der MBI
        herkunft: dict[str, dict[str, float]] = {}  # Thema -> Gebiet -> Stärke
        enthalten: dict[str, dict[str, float]] = {}  # Haltung -> Thema -> Stärke
        for e in self.erfahrungen:
            # ANNAHME: In der Erinnerung zählt jede frühere Erfahrung voll und
            # unverblasst, egal aus welchem Gebiet sie stammt.
            if ERINNERUNG in gebiete and e.zeit < zeit:
                beitrag, mitgefuehrt = e.staerke, False
            else:
                beitrag = e.staerke * self.nachklang ** (zeit - e.zeit)
                mitgefuehrt = not any(
                    gehoert_zum_gebiet(e, g, im_abi_feld) for g in gebiete
                )
                if mitgefuehrt:
                    beitrag *= self.mitnahme
            staerken[e.thema] = staerken.get(e.thema, 0.0) + beitrag
            if any(
                (g == ERINNERUNG and e.zeit < zeit) or gehoert_zum_gebiet(e, g, im_abi_feld)
                for g in haltung
            ):
                aus_haltung[e.thema] = aus_haltung.get(e.thema, 0.0) + beitrag
            for g in e.gebiete:
                if mitgefuehrt:
                    name = g if g not in gebiete else FRUEHER
                    je_gebiet = herkunft.setdefault(e.thema, {})
                    je_gebiet[name] = je_gebiet.get(name, 0.0) + beitrag
                # ANNAHME: Als frühere Haltung taucht nur ein Themengebiet auf,
                # und nur eines, in dem die MBI gerade nicht ist.
                if g not in gebiete and g not in BESONDERE_GEBIETE:
                    je_thema = enthalten.setdefault(g, {})
                    je_thema[e.thema] = je_thema.get(e.thema, 0.0) + beitrag

        impulse = []
        for thema, staerke in staerken.items():
            if staerke < MINDESTSTAERKE:
                continue
            je_gebiet = herkunft.get(thema, {})
            mitgebracht_aus = sorted(
                (g for g, anteil in je_gebiet.items() if anteil >= MINDESTSTAERKE),
                key=lambda g: je_gebiet[g],
                reverse=True,
            )
            # ANNAHME: Ein Thema stammt aus der jetzigen Haltung, wenn
            # mindestens die Hälfte seiner Stärke von dort kommt.
            stammt_aus_haltung = 2 * aus_haltung.get(thema, 0.0) >= staerke
            impulse.append(
                Impuls(
                    thema,
                    min(1.0, staerke),
                    tuple(mitgebracht_aus),
                    aus_haltung=stammt_aus_haltung,
                )
            )

        # Eine Haltung, die das AUI enthält, liegt selbst als Impuls im Feld.
        # ANNAHME: Sie ist so stark wie das stärkste Thema, das sie enthält.
        vorhanden = {impuls.thema for impuls in impulse}
        for haltung, je_thema in enthalten.items():
            staerke = max(je_thema.values())
            if haltung not in vorhanden and staerke >= MINDESTSTAERKE:
                impulse.append(Impuls(haltung, min(1.0, staerke), haltung=True))

        self.feld = sorted(impulse, key=lambda i: i.staerke, reverse=True)
        return self.feld


class AutomatischeBewussteIntention:
    """ABI. Automatisch und bewusst: ein eigenes Feld, das an das des AUI angrenzt.

    Was im Feld des AUI stark genug ist, taucht auch hier auf. Die Impulse
    bleiben Impulse des AUI. Die ABI nimmt sie nur wahr. Ihr Feld ist die
    wahrgenommene Realität. In ihr liegen auch die Themengebiete, und manche
    davon entstehen ohne die MBI.
    """

    def __init__(
        self,
        schwelle: float = 0.3,
        chance: float = 0.25,
        zufall: random.Random | None = None,
    ):
        # ANNAHME: Über die Grenze reicht, was mindestens so stark ist wie die Schwelle.
        self.schwelle = schwelle
        # ANNAHME: Mit dieser Wahrscheinlichkeit pro Moment wird ein Thema im
        # Feld, zu dem die MBI "weder noch" hält, von selbst zum Themengebiet.
        self.chance = chance
        self.zufall = zufall or random.Random()
        self.feld: list[Impuls] = []
        self.gebiete_ohne_mbi: list[str] = []

    def nimm_wahr(self, aui_feld: list[Impuls]) -> list[Impuls]:
        self.feld = [i for i in aui_feld if i.staerke >= self.schwelle]
        return self.feld

    def lasse_gebiete_entstehen(
        self, umgang: Mapping[str, Umgang], gebiete_der_mbi: Collection[str]
    ) -> None:
        """Themengebiete ohne die MBI: Manche lösen sich auf, neue können entstehen."""
        # Eine Haltung erschafft nur die MBI: Eine frühere Haltung, die auftaucht,
        # wird deshalb nicht von selbst zum Gebiet.
        im_feld = [impuls.thema for impuls in self.feld if not impuls.haltung]

        def sich_selbst_ueberlassen(thema: str) -> bool:
            weder_noch = umgang.get(thema, Umgang.WEDER_NOCH) is Umgang.WEDER_NOCH
            return weder_noch and thema not in gebiete_der_mbi

        # ANNAHME: Ein von selbst entstandenes Themengebiet löst sich auf, wenn
        # sein Thema aus dem Feld verblasst oder die MBI disengaged. Engaged
        # sie, gehört es ab dann der MBI.
        self.gebiete_ohne_mbi = [
            g for g in self.gebiete_ohne_mbi if g in im_feld and sich_selbst_ueberlassen(g)
        ]
        for thema in im_feld:
            if (
                sich_selbst_ueberlassen(thema)
                and thema not in self.gebiete_ohne_mbi
                and self.zufall.random() < self.chance
            ):
                self.gebiete_ohne_mbi.append(thema)


Entscheider = Callable[[Lage], Entscheidung]


class ManuelleBewussteIntention:
    """MBI. Manuell und bewusst: was man willentlich lenkt.

    Sie befindet sich immer in einer Haltung: Das sind die Gebiete, die sie
    erschafft und in denen sie agiert. Ein Gebiet ist ein Themengebiet, die
    jetzige Erfahrung, die Sinne oder die Erinnerung. Sie kann ihr Thema
    autonom wechseln, auch zu einem Themengebiet, das vorher nicht im
    Bewusstsein war. Engage und disengage gibt es dagegen nur zu dem, was im
    Feld der ABI auftaucht. Das Feld des AUI bekommt sie nie zu sehen.
    """

    def __init__(self, entscheider: Entscheider, gebiet: str):
        self.entscheider = entscheider
        self.gebiete = [gebiet]

    def richte_aus(self, lage: Lage) -> Mapping[str, Umgang]:
        """Fragt den Entscheider, ändert die Haltung und gibt den Umgang zurück."""
        entscheidung = self.entscheider(lage)
        if entscheidung.themenwechsel:
            # ANNAHME: Ein Themenwechsel ersetzt alle bisherigen Gebiete.
            self.gebiete = [entscheidung.themenwechsel]

        # Umgehen kann die MBI nur mit dem, was im Feld der ABI auftaucht.
        im_feld = {impuls.thema: impuls for impuls in lage.abi_feld}
        umgang = {t: h for t, h in entscheidung.umgang.items() if t in im_feld}
        for thema, art in umgang.items():
            if art is Umgang.ENGAGE:
                if not im_feld[thema].aus_haltung:
                    # Aus einem anderen Gebiet: Es ersetzt die Haltung.
                    self.gebiete = [thema]
                elif thema not in self.gebiete:
                    # Aus der jetzigen Haltung: Es läuft parallel zu ihr.
                    self.gebiete.append(thema)
            elif art is Umgang.DISENGAGE and thema in self.gebiete:
                self.gebiete.remove(thema)
        if not self.gebiete:
            # ANNAHME: Ohne ein eigenes Gebiet bleibt der MBI die jetzige Erfahrung.
            self.gebiete = [JETZIGE_ERFAHRUNG]
        return umgang


@dataclass(frozen=True)
class Moment:
    """Was in einem Zeitschritt in den drei Layern passiert ist."""

    zeit: int
    gebiete: tuple[str, ...]  # die Haltung der MBI: die Gebiete, in denen sie agiert hat
    gebiete_ohne_mbi: tuple[str, ...]  # Themengebiete, die von selbst bestanden
    sinne: Mapping[str, float]  # sensorische Eindrücke dieses Moments
    aui_feld: tuple[Impuls, ...]  # alles, was im Feld des AUI liegt
    abi_feld: tuple[Impuls, ...]  # der Teil, der auch im Feld der ABI auftaucht
    umgang: Mapping[str, Umgang]  # Thema -> Umgang der MBI
    # Die Gebiete, wie sie ab dem nächsten Moment gelten.
    gebiete_danach: tuple[str, ...]
    gebiete_ohne_mbi_danach: tuple[str, ...]


class Geist:
    """Die drei Layer zusammen."""

    def __init__(
        self,
        entscheider: Entscheider,
        gebiet: str,
        *,
        nachklang: float = 0.8,
        mitnahme: float = 0.5,
        schwelle: float = 0.3,
        chance: float = 0.25,
        zufall: random.Random | None = None,
        wirkung: Mapping[Umgang, float] = STANDARD_WIRKUNG,
    ):
        self.unterbewusstsein = Unterbewusstsein(nachklang, mitnahme)
        self.automatisch = AutomatischeBewussteIntention(schwelle, chance, zufall)
        self.manuell = ManuelleBewussteIntention(entscheider, gebiet)
        self.wirkung = wirkung
        self.zeit = 0

    def schritt(self, sinne: Mapping[str, float] | None = None) -> Moment:
        """Ein Moment. `sinne` sind die sensorischen Eindrücke: Thema -> Stärke."""
        sinne = dict(sinne or {})
        gebiete = tuple(self.manuell.gebiete)
        gebiete_ohne_mbi = tuple(self.automatisch.gebiete_ohne_mbi)
        # ANNAHME: Sensorische Eindrücke gehen ins AUI und gehören zum Gebiet
        # der Sinne, egal in welchem Gebiet sich die MBI gerade bewegt.
        for thema, staerke in sinne.items():
            self.unterbewusstsein.erlebe(Erfahrung(thema, staerke, self.zeit, (SINNE,)))

        # ANNAHME: Was im Feld der ABI auftaucht, bemisst sich am Feld, wie es
        # zu Beginn des Moments ist, also am Ergebnis des vorigen Moments.
        bisher_im_abi_feld = {impuls.thema for impuls in self.automatisch.feld}
        # ANNAHME: AUI und ABI orientieren sich auch an den Themengebieten, die
        # ohne die MBI entstanden sind.
        aui_feld = self.unterbewusstsein.erzeuge_impulse(
            self.zeit, gebiete + gebiete_ohne_mbi, bisher_im_abi_feld, gebiete
        )
        abi_feld = self.automatisch.nimm_wahr(aui_feld)
        lage = Lage(gebiete, gebiete_ohne_mbi, tuple(abi_feld), sinne)
        # ANNAHME: Ein Wechsel der Gebiete gilt ab dem nächsten Moment.
        umgang = self.manuell.richte_aus(lage)

        for thema, art in umgang.items():
            wirkung = self.wirkung[art]
            if wirkung < 0:
                # Schwächen lässt sich etwas nur so weit, wie es auftaucht.
                wirkung = max(wirkung, -lage.staerke(thema))
            if wirkung:
                # Die Erfahrung enthält die Haltung, in der die MBI dabei war.
                self.unterbewusstsein.erlebe(Erfahrung(thema, wirkung, self.zeit, gebiete))

        self.automatisch.lasse_gebiete_entstehen(umgang, self.manuell.gebiete)

        moment = Moment(
            self.zeit,
            gebiete,
            gebiete_ohne_mbi,
            sinne,
            tuple(aui_feld),
            lage.abi_feld,
            umgang,
            tuple(self.manuell.gebiete),
            tuple(self.automatisch.gebiete_ohne_mbi),
        )
        self.zeit += 1
        return moment
