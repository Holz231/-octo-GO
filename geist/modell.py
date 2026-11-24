"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Die Layer:

- AUI: das automatische Unterbewusstsein
- ABI: die automatische bewusste Intention
- MBI: die manuelle bewusste Intention

Ablauf eines Moments:

AUI und ABI sind zwei verschiedene, aneinander angrenzende Felder.

1. Das AUI erzeugt Impulse aus vorherigen und jetzigen Erfahrungen. Sie liegen
   im Feld des AUI.
2. Ein Teil davon taucht im angrenzenden Feld der ABI auf. Die Impulse werden
   dabei nicht zur ABI, sie werden von ihr nur wahrgenommen.
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

    abi_feld: tuple[Impuls, ...]  # was gerade im Feld der ABI auftaucht
    sinne: Mapping[str, float]  # sensorische Eindrücke: Thema -> Stärke

    def staerke(self, thema: str) -> float:
        """Wie stark ein Thema gerade wahrnehmbar ist (0 = gar nicht)."""
        for impuls in self.abi_feld:
            if impuls.thema == thema:
                return impuls.staerke
        return self.sinne.get(thema, 0.0)

    def quelle(self, thema: str) -> Quelle:
        if thema in self.sinne:
            return Quelle.SINNE
        if any(impuls.thema == thema for impuls in self.abi_feld):
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
    """AUI. Automatisch und unbewusst: läuft ständig und erzeugt Impulse.

    Die Impulse liegen in seinem Feld, das an das Feld der ABI angrenzt.
    """

    def __init__(self, nachklang: float = 0.8):
        # ANNAHME: Eine Erfahrung wirkt pro Moment um diesen Faktor schwächer nach.
        self.nachklang = nachklang
        self.erfahrungen: list[Erfahrung] = []
        self.feld: list[Impuls] = []

    def erlebe(self, erfahrung: Erfahrung) -> None:
        self.erfahrungen.append(erfahrung)

    def erzeuge_impulse(self, zeit: int) -> list[Impuls]:
        """Füllt das Feld mit Impulsen aus allen Erfahrungen, stärkster zuerst."""
        summen: dict[str, float] = {}
        for e in self.erfahrungen:
            gewicht = self.nachklang ** (zeit - e.zeit)
            summen[e.thema] = summen.get(e.thema, 0.0) + e.staerke * gewicht
        impulse = [
            Impuls(thema, min(1.0, summe))
            for thema, summe in summen.items()
            if summe >= MINDESTSTAERKE
        ]
        self.feld = sorted(impulse, key=lambda i: i.staerke, reverse=True)
        return self.feld


class AutomatischeBewussteIntention:
    """ABI. Automatisch und bewusst: ein eigenes Feld, das an das des AUI angrenzt.

    Was im Feld des AUI stark genug ist, taucht auch hier auf. Die Impulse
    bleiben Impulse des AUI. Die ABI nimmt sie nur wahr.
    """

    def __init__(self, schwelle: float = 0.3):
        # ANNAHME: Über die Grenze reicht, was mindestens so stark ist wie die Schwelle.
        self.schwelle = schwelle
        self.feld: list[Impuls] = []

    def nimm_wahr(self, aui_feld: list[Impuls]) -> list[Impuls]:
        self.feld = [i for i in aui_feld if i.staerke >= self.schwelle]
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
    aui_feld: tuple[Impuls, ...]  # alles, was im Feld des AUI liegt
    abi_feld: tuple[Impuls, ...]  # der Teil, der auch im Feld der ABI auftaucht
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

        aui_feld = self.unterbewusstsein.erzeuge_impulse(self.zeit)
        abi_feld = self.automatisch.nimm_wahr(aui_feld)
        lage = Lage(tuple(abi_feld), sinne)
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

        moment = Moment(
            self.zeit, sinne, tuple(aui_feld), lage.abi_feld, tuple(ausrichtungen)
        )
        self.zeit += 1
        return moment
