"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Die Layer:

- AUI: das automatische Unterbewusstsein
- ABI: die automatische bewusste Intention
- MBI: die manuelle bewusste Intention

AUI und ABI sind zwei verschiedene, aneinander angrenzende Felder.

Die MBI bewegt sich immer in einem bestimmten Gebiet, je nachdem auch in
mehreren zugleich. Ein Gebiet kann ein Themengebiet sein (davon gibt es
unendlich viele), die jetzige Erfahrung oder die Sinne. Die jetzige Erfahrung
ist alles, was im Feld der ABI auftaucht. An den Gebieten orientieren sich AUI
und ABI. Das AUI führt aber vergangene Themen und Erfahrungen mit in jedes neue
Gebiet. Wie die MBI und das AUI gerade sind, formt gleichzeitig die
wahrgenommene Realität der ABI.

Die drei Haltungen der MBI zu einem Thema:

- engage verstärkt das Thema im AUI. Zugleich macht die MBI es zu einem neuen
  Themengebiet, in dem sie agiert: parallel zu den bisherigen, wenn sie mehrere
  zugleich hält, sonst allein.
- disengage schwächt das Thema im AUI und verhindert, dass die MBI es zu einem
  Themengebiet macht.
- weder noch verstärkt nicht und schwächt nicht. Es lässt aber die Chance, dass
  das Thema ohne die MBI aus dem AUI in die ABI geht und dort von selbst zu
  einem Themengebiet wird. Oder es verblasst wieder.

Ablauf eines Moments:

1. Das AUI erzeugt Impulse aus vorherigen und jetzigen Erfahrungen, orientiert
   an den Gebieten. Sie liegen im Feld des AUI.
2. Ein Teil davon taucht im angrenzenden Feld der ABI auf: Das ist die
   wahrgenommene Realität. Die Impulse werden dabei nicht zur ABI, sie werden
   von ihr nur wahrgenommen.
3. Die MBI nimmt Haltungen ein und kann sich auf ein neues Gebiet richten.
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

# Zwei besondere Gebiete, in denen sich die MBI bewegen kann. Jeder andere Name
# steht für ein Themengebiet.
SINNE = "Sinne"
JETZIGE_ERFAHRUNG = "jetzige Erfahrung"

# Herkunft von etwas, das in der jetzigen Erfahrung entstanden ist, aber nicht
# mehr im Feld der ABI auftaucht.
FRUEHER = "früher"


class Haltung(Enum):
    """Was die MBI mit einem Thema tut."""

    ENGAGE = "engage"
    DISENGAGE = "disengage"
    WEDER_NOCH = "weder noch"  # "non disengage and non engage"


@dataclass(frozen=True)
class Erfahrung:
    thema: str
    staerke: float  # negativ = wirkt dem Thema entgegen
    zeit: int
    gebiete: tuple[str, ...]  # die Gebiete, zu denen sie gehört


@dataclass(frozen=True)
class Impuls:
    thema: str
    staerke: float  # 0 bis 1
    # Andere Gebiete, aus denen das AUI diesen Impuls mitgebracht hat.
    mitgebracht_aus: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lage:
    """Alles, was der MBI zugänglich ist. Das Feld des AUI gehört nicht dazu."""

    gebiete: tuple[str, ...]  # die Gebiete, in denen sie gerade agiert
    gebiete_ohne_mbi: tuple[str, ...]  # Themengebiete, die von selbst entstanden sind
    abi_feld: tuple[Impuls, ...]  # die wahrgenommene Realität
    sinne: Mapping[str, float]  # sensorische Eindrücke: Thema -> Stärke

    def staerke(self, thema: str) -> float:
        """Wie stark ein Thema gerade wahrnehmbar ist (0 = gar nicht)."""
        for impuls in self.abi_feld:
            if impuls.thema == thema:
                return impuls.staerke
        return self.sinne.get(thema, 0.0)


@dataclass(frozen=True)
class Entscheidung:
    """Was die MBI in einem Moment willentlich tut."""

    # Thema -> Haltung. Alles, was nicht genannt wird, bleibt bei "weder noch".
    haltungen: Mapping[str, Haltung] = field(default_factory=dict)
    # Ein Gebiet, auf das sie sich richtet, ohne ein Thema zu verstärken.
    gebiet: str | None = None


# ANNAHME (noch nicht vom Modell vorgegeben): wie stark engage und disengage als
# neue Erfahrung im AUI wirken. Weder noch wirkt laut Modell gar nicht.
STANDARD_WIRKUNG: Mapping[Haltung, float] = {
    Haltung.ENGAGE: 0.4,
    Haltung.DISENGAGE: -0.4,
    Haltung.WEDER_NOCH: 0.0,
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
        self, zeit: int, gebiete: Collection[str], im_abi_feld: Collection[str] = ()
    ) -> list[Impuls]:
        """Füllt das Feld mit Impulsen, orientiert an den Gebieten.

        `im_abi_feld` sind die Themen, die bisher im Feld der ABI auftauchen.
        Sie bestimmen, was zur jetzigen Erfahrung gehört.
        """
        staerken: dict[str, float] = {}
        herkunft: dict[str, dict[str, float]] = {}  # Thema -> Gebiet -> Stärke
        for e in self.erfahrungen:
            nachwirkung = e.staerke * self.nachklang ** (zeit - e.zeit)
            if any(gehoert_zum_gebiet(e, g, im_abi_feld) for g in gebiete):
                staerken[e.thema] = staerken.get(e.thema, 0.0) + nachwirkung
                continue
            mitgebracht = nachwirkung * self.mitnahme
            staerken[e.thema] = staerken.get(e.thema, 0.0) + mitgebracht
            je_gebiet = herkunft.setdefault(e.thema, {})
            for g in e.gebiete:
                name = g if g not in gebiete else FRUEHER
                je_gebiet[name] = je_gebiet.get(name, 0.0) + mitgebracht

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
            impulse.append(Impuls(thema, min(1.0, staerke), tuple(mitgebracht_aus)))

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
        self, haltungen: Mapping[str, Haltung], gebiete_der_mbi: Collection[str]
    ) -> None:
        """Themengebiete ohne die MBI: Manche lösen sich auf, neue können entstehen."""
        im_feld = [impuls.thema for impuls in self.feld]

        def sich_selbst_ueberlassen(thema: str) -> bool:
            weder_noch = haltungen.get(thema, Haltung.WEDER_NOCH) is Haltung.WEDER_NOCH
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

    Sie agiert immer in mindestens einem Gebiet: in einem Themengebiet, in der
    jetzigen Erfahrung oder in den Sinnen. Das Feld des AUI bekommt sie nie zu
    sehen.
    """

    def __init__(self, entscheider: Entscheider, gebiet: str, mehrere: bool = False):
        self.entscheider = entscheider
        self.gebiete = [gebiet]
        # ANNAHME: Ob die MBI mehrere Gebiete zugleich hält oder nur eines, ist
        # eine Eigenschaft der MBI, die von außen eingestellt wird.
        self.mehrere = mehrere

    def richte_aus(self, lage: Lage) -> Mapping[str, Haltung]:
        """Fragt den Entscheider, wechselt die Gebiete und gibt die Haltungen zurück."""
        entscheidung = self.entscheider(lage)
        if entscheidung.gebiet:
            self._betritt(entscheidung.gebiet)
        for thema, haltung in entscheidung.haltungen.items():
            if haltung is Haltung.ENGAGE:
                self._betritt(thema)
            elif haltung is Haltung.DISENGAGE and thema in self.gebiete:
                self.gebiete.remove(thema)
        if not self.gebiete:
            # ANNAHME: Ohne ein eigenes Gebiet bleibt der MBI die jetzige Erfahrung.
            self.gebiete = [JETZIGE_ERFAHRUNG]
        return dict(entscheidung.haltungen)

    def _betritt(self, gebiet: str) -> None:
        if not self.mehrere:
            self.gebiete = [gebiet]
        elif gebiet not in self.gebiete:
            self.gebiete.append(gebiet)


@dataclass(frozen=True)
class Moment:
    """Was in einem Zeitschritt in den drei Layern passiert ist."""

    zeit: int
    gebiete: tuple[str, ...]  # die Gebiete, in denen die MBI agiert hat
    gebiete_ohne_mbi: tuple[str, ...]  # Themengebiete, die von selbst bestanden
    sinne: Mapping[str, float]  # sensorische Eindrücke dieses Moments
    aui_feld: tuple[Impuls, ...]  # alles, was im Feld des AUI liegt
    abi_feld: tuple[Impuls, ...]  # der Teil, der auch im Feld der ABI auftaucht
    haltungen: Mapping[str, Haltung]  # Thema -> Haltung der MBI
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
        mehrere: bool = False,
        nachklang: float = 0.8,
        mitnahme: float = 0.5,
        schwelle: float = 0.3,
        chance: float = 0.25,
        zufall: random.Random | None = None,
        wirkung: Mapping[Haltung, float] = STANDARD_WIRKUNG,
    ):
        self.unterbewusstsein = Unterbewusstsein(nachklang, mitnahme)
        self.automatisch = AutomatischeBewussteIntention(schwelle, chance, zufall)
        self.manuell = ManuelleBewussteIntention(entscheider, gebiet, mehrere)
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
            self.zeit, gebiete + gebiete_ohne_mbi, bisher_im_abi_feld
        )
        abi_feld = self.automatisch.nimm_wahr(aui_feld)
        lage = Lage(gebiete, gebiete_ohne_mbi, tuple(abi_feld), sinne)
        # ANNAHME: Ein Wechsel der Gebiete gilt ab dem nächsten Moment.
        haltungen = self.manuell.richte_aus(lage)

        for thema, haltung in haltungen.items():
            wirkung = self.wirkung[haltung]
            if wirkung < 0:
                # Lösen kann man sich nur so weit, wie etwas wahrnehmbar ist.
                wirkung = max(wirkung, -lage.staerke(thema))
            if wirkung:
                # ANNAHME: Die Erfahrung gehört zu den Gebieten, in denen die MBI
                # agiert hat, als sie die Haltung einnahm.
                self.unterbewusstsein.erlebe(Erfahrung(thema, wirkung, self.zeit, gebiete))

        self.automatisch.lasse_gebiete_entstehen(haltungen, self.manuell.gebiete)

        moment = Moment(
            self.zeit,
            gebiete,
            gebiete_ohne_mbi,
            sinne,
            tuple(aui_feld),
            lage.abi_feld,
            haltungen,
            tuple(self.manuell.gebiete),
            tuple(self.automatisch.gebiete_ohne_mbi),
        )
        self.zeit += 1
        return moment
