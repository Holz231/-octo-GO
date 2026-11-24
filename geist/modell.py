"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Die Layer:

- AUI: das automatische Unterbewusstsein
- ABI: die automatische bewusste Intention
- MBI: die manuelle bewusste Intention

Ablauf eines Moments:

1. Das AUI erzeugt Impulse aus vorherigen und jetzigen Erfahrungen.
2. Ein Teil davon taucht im Feld der ABI auf. Die Impulse werden dabei nicht
   zur ABI, sie werden von ihr nur wahrgenommen.
3. Die MBI richtet sich aus: auf ein beliebiges Thema, auf die jetzige
   Erfahrung oder auf einen sensorischen Eindruck. Dazu nimmt sie eine Haltung
   ein: engage, disengage oder weder noch.
4. Die Haltung wird selbst zur Erfahrung. Nur so, also indirekt, erreicht die
   MBI das AUI.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping

# Schwächere Impulse gelten als nicht vorhanden.
MINDESTSTAERKE = 0.01


class Haltung(Enum):
    """Was die MBI mit dem tut, worauf sie gerichtet ist."""

    ENGAGE = "engage"
    DISENGAGE = "disengage"
    WEDER_NOCH = "weder noch"  # "non disengage and non engage"


class Quelle(Enum):
    """Woher das stammt, worauf die MBI gerichtet ist."""

    THEMENGEBIET = "Themengebiet"  # unendlich: jedes beliebige Thema
    ERFAHRUNG = "jetzige Erfahrung"
    SINNE = "Sinne"


@dataclass(frozen=True)
class Erfahrung:
    thema: str
    staerke: float  # negativ = wirkt dem Thema entgegen
    zeit: int


@dataclass(frozen=True)
class Impuls:
    thema: str
    staerke: float  # 0 bis 1


@dataclass(frozen=True)
class Lage:
    """Alles, was der MBI zugänglich ist. Das AUI gehört nicht dazu."""

    feld: tuple[Impuls, ...]  # was gerade im Feld der ABI auftaucht
    sinne: Mapping[str, float]  # sensorische Eindrücke: Thema -> Stärke

    def staerke(self, thema: str) -> float:
        """Wie stark ein Thema gerade wahrnehmbar ist (0 = gar nicht)."""
        for impuls in self.feld:
            if impuls.thema == thema:
                return impuls.staerke
        return self.sinne.get(thema, 0.0)

    def quelle(self, thema: str) -> Quelle:
        if thema in self.sinne:
            return Quelle.SINNE
        if any(impuls.thema == thema for impuls in self.feld):
            return Quelle.ERFAHRUNG
        return Quelle.THEMENGEBIET


@dataclass(frozen=True)
class Ausrichtung:
    """Worauf die MBI in einem Moment gerichtet ist und mit welcher Haltung."""

    thema: str
    quelle: Quelle
    haltung: Haltung


# ANNAHME (noch nicht vom Modell vorgegeben): wie stark eine Haltung als neue
# Erfahrung auf das Thema zurückwirkt.
STANDARD_WIRKUNG: Mapping[Haltung, float] = {
    Haltung.ENGAGE: 0.4,
    Haltung.DISENGAGE: -0.4,
    Haltung.WEDER_NOCH: 0.0,
}


class Unterbewusstsein:
    """AUI. Automatisch und unbewusst: läuft ständig und erzeugt Impulse."""

    def __init__(self, nachklang: float = 0.8):
        # ANNAHME: Eine Erfahrung wirkt pro Moment um diesen Faktor schwächer nach.
        self.nachklang = nachklang
        self.erfahrungen: list[Erfahrung] = []

    def erlebe(self, erfahrung: Erfahrung) -> None:
        self.erfahrungen.append(erfahrung)

    def erzeuge_impulse(self, zeit: int) -> list[Impuls]:
        """Impulse aus allen bisherigen Erfahrungen, stärkster zuerst."""
        summen: dict[str, float] = {}
        for e in self.erfahrungen:
            gewicht = self.nachklang ** (zeit - e.zeit)
            summen[e.thema] = summen.get(e.thema, 0.0) + e.staerke * gewicht
        impulse = [
            Impuls(thema, min(1.0, summe))
            for thema, summe in summen.items()
            if summe >= MINDESTSTAERKE
        ]
        return sorted(impulse, key=lambda i: i.staerke, reverse=True)


class AutomatischeBewussteIntention:
    """ABI. Automatisch und bewusst: ein Feld, in dem auftaucht, was das AUI erzeugt.

    Die Impulse bleiben Impulse des AUI. Die ABI nimmt sie nur wahr.
    """

    def __init__(self, schwelle: float = 0.3):
        # ANNAHME: Im Feld taucht auf, was mindestens so stark ist wie die Schwelle.
        self.schwelle = schwelle
        self.feld: list[Impuls] = []

    def nimm_wahr(self, impulse: list[Impuls]) -> list[Impuls]:
        self.feld = [i for i in impulse if i.staerke >= self.schwelle]
        return self.feld


# Bekommt die Lage und gibt zurück, worauf sich die MBI wie richtet:
# Thema -> Haltung. Alles, was nicht genannt wird, bleibt bei "weder noch".
Entscheider = Callable[[Lage], Mapping[str, Haltung]]


class ManuelleBewussteIntention:
    """MBI. Manuell und bewusst: was man willentlich lenkt.

    Sie kann sich auf jedes beliebige Thema richten, auf die jetzige Erfahrung
    oder auf sensorische Eindrücke. Das AUI selbst bekommt sie nie zu sehen.
    """

    def __init__(self, entscheider: Entscheider):
        self.entscheider = entscheider

    def richte_aus(self, lage: Lage) -> list[Ausrichtung]:
        return [
            Ausrichtung(thema, lage.quelle(thema), haltung)
            for thema, haltung in self.entscheider(lage).items()
        ]


@dataclass(frozen=True)
class Moment:
    """Was in einem Zeitschritt in den drei Layern passiert ist."""

    zeit: int
    sinne: Mapping[str, float]  # sensorische Eindrücke dieses Moments
    impulse: tuple[Impuls, ...]  # alles, was das AUI erzeugt hat
    feld: tuple[Impuls, ...]  # der Teil, der im Feld der ABI aufgetaucht ist
    ausrichtungen: tuple[Ausrichtung, ...]  # worauf sich die MBI gerichtet hat


class Geist:
    """Die drei Layer zusammen."""

    def __init__(
        self,
        entscheider: Entscheider,
        *,
        nachklang: float = 0.8,
        schwelle: float = 0.3,
        wirkung: Mapping[Haltung, float] = STANDARD_WIRKUNG,
    ):
        self.unterbewusstsein = Unterbewusstsein(nachklang)
        self.automatisch = AutomatischeBewussteIntention(schwelle)
        self.manuell = ManuelleBewussteIntention(entscheider)
        self.wirkung = wirkung
        self.zeit = 0

    def schritt(self, sinne: Mapping[str, float] | None = None) -> Moment:
        """Ein Moment. `sinne` sind die sensorischen Eindrücke: Thema -> Stärke."""
        sinne = dict(sinne or {})
        # ANNAHME: Sensorische Eindrücke sind jetzige Erfahrung und gehen ins AUI.
        for thema, staerke in sinne.items():
            self.unterbewusstsein.erlebe(Erfahrung(thema, staerke, self.zeit))

        impulse = self.unterbewusstsein.erzeuge_impulse(self.zeit)
        feld = self.automatisch.nimm_wahr(impulse)
        lage = Lage(tuple(feld), sinne)
        ausrichtungen = self.manuell.richte_aus(lage)

        for ausrichtung in ausrichtungen:
            wirkung = self.wirkung[ausrichtung.haltung]
            if wirkung < 0:
                # Lösen kann man sich nur so weit, wie etwas wahrnehmbar ist.
                wirkung = max(wirkung, -lage.staerke(ausrichtung.thema))
            if wirkung:
                self.unterbewusstsein.erlebe(
                    Erfahrung(ausrichtung.thema, wirkung, self.zeit)
                )

        moment = Moment(self.zeit, sinne, tuple(impulse), lage.feld, tuple(ausrichtungen))
        self.zeit += 1
        return moment
