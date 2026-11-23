"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Ablauf eines Moments:

1. Das Unterbewusstsein erzeugt Impulse aus vorherigen und jetzigen Erfahrungen.
2. Ein Teil davon steigt auf und wird zur automatischen bewussten Intention.
3. Die manuelle bewusste Intention nimmt zu jedem aufgestiegenen Impuls eine
   Haltung ein: engage, disengage oder weder noch.
4. Die Haltung wird selbst zur Erfahrung. Nur so, also indirekt über das
   Aufgestiegene, erreicht die manuelle Intention das Unterbewusstsein.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping

# Schwächere Impulse gelten als nicht vorhanden.
MINDESTSTAERKE = 0.01


class Haltung(Enum):
    """Was die manuelle bewusste Intention mit einem aufgestiegenen Impuls tut."""

    ENGAGE = "engage"
    DISENGAGE = "disengage"
    WEDER_NOCH = "weder noch"  # "non disengage and non engage"


@dataclass(frozen=True)
class Erfahrung:
    thema: str
    staerke: float  # negativ = wirkt dem Thema entgegen
    zeit: int


@dataclass(frozen=True)
class Impuls:
    thema: str
    staerke: float  # 0 bis 1


# ANNAHME (noch nicht vom Modell vorgegeben): wie stark eine Haltung als neue
# Erfahrung auf das Thema zurückwirkt, als Anteil der Impulsstärke.
STANDARD_WIRKUNG: Mapping[Haltung, float] = {
    Haltung.ENGAGE: 0.5,
    Haltung.DISENGAGE: -0.5,
    Haltung.WEDER_NOCH: 0.0,
}


class Unterbewusstsein:
    """Automatisch und unbewusst: läuft ständig und erzeugt Impulse."""

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
    """Automatisch und bewusst: was von selbst ins Bewusstsein tritt."""

    def __init__(self, schwelle: float = 0.3):
        # ANNAHME: Es steigt auf, was mindestens so stark ist wie die Schwelle.
        self.schwelle = schwelle
        self.inhalt: list[Impuls] = []

    def lasse_aufsteigen(self, impulse: list[Impuls]) -> list[Impuls]:
        self.inhalt = [i for i in impulse if i.staerke >= self.schwelle]
        return self.inhalt


Entscheider = Callable[[Impuls], Haltung]


class ManuelleBewussteIntention:
    """Manuell und bewusst: was man willentlich lenkt.

    Sie bekommt nur zu sehen, was aufgestiegen ist, nie das Unterbewusstsein.
    """

    def __init__(self, entscheider: Entscheider):
        self.entscheider = entscheider

    def nimm_haltung_ein(self, aufgestiegen: list[Impuls]) -> dict[str, Haltung]:
        return {impuls.thema: self.entscheider(impuls) for impuls in aufgestiegen}


@dataclass(frozen=True)
class Moment:
    """Was in einem Zeitschritt in den drei Layern passiert ist."""

    zeit: int
    impulse: tuple[Impuls, ...]  # alles, was das Unterbewusstsein erzeugt hat
    aufgestiegen: tuple[Impuls, ...]  # der Teil, der bewusst wurde
    haltungen: Mapping[str, Haltung]  # Thema -> Haltung der manuellen Intention


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

    def schritt(self, jetzt: Mapping[str, float] | None = None) -> Moment:
        """Ein Moment. `jetzt` sind die jetzigen Erfahrungen: Thema -> Stärke."""
        for thema, staerke in (jetzt or {}).items():
            self.unterbewusstsein.erlebe(Erfahrung(thema, staerke, self.zeit))

        impulse = self.unterbewusstsein.erzeuge_impulse(self.zeit)
        aufgestiegen = self.automatisch.lasse_aufsteigen(impulse)
        haltungen = self.manuell.nimm_haltung_ein(aufgestiegen)

        for impuls in aufgestiegen:
            wirkung = self.wirkung[haltungen[impuls.thema]]
            if wirkung:
                self.unterbewusstsein.erlebe(
                    Erfahrung(impuls.thema, wirkung * impuls.staerke, self.zeit)
                )

        moment = Moment(self.zeit, tuple(impulse), tuple(aufgestiegen), haltungen)
        self.zeit += 1
        return moment
