"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Die Layer:

- AUI: das automatische Unterbewusstsein
- ABI: die automatische bewusste Intention
- MBI: die manuelle bewusste Intention

AUI und ABI sind zwei verschiedene, aneinander angrenzende Felder.

Die MBI bewegt sich immer in einem bestimmten Themengebiet. An diesem Gebiet
orientieren sich AUI und ABI. Das AUI führt aber vergangene Themen und
Erfahrungen mit in jedes neue Gebiet, auf das sich die MBI richtet. Wie die MBI
und das AUI gerade sind, formt gleichzeitig die wahrgenommene Realität der ABI.

Ablauf eines Moments:

1. Das AUI erzeugt Impulse aus vorherigen und jetzigen Erfahrungen, orientiert
   am Themengebiet der MBI. Sie liegen im Feld des AUI.
2. Ein Teil davon taucht im angrenzenden Feld der ABI auf: Das ist die
   wahrgenommene Realität. Die Impulse werden dabei nicht zur ABI, sie werden
   von ihr nur wahrgenommen.
3. Die MBI nimmt Haltungen ein (engage, disengage oder weder noch) und kann
   sich auf ein neues Themengebiet richten.
4. Jede Haltung wird selbst zur Erfahrung. Nur so, also indirekt, erreicht die
   MBI das AUI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    """Woher ein Thema stammt, zu dem die MBI eine Haltung einnimmt."""

    THEMENGEBIET = "Themengebiet"  # frei gewählt, weder im Feld noch in den Sinnen
    ERFAHRUNG = "jetzige Erfahrung"
    SINNE = "Sinne"


@dataclass(frozen=True)
class Erfahrung:
    thema: str
    staerke: float  # negativ = wirkt dem Thema entgegen
    zeit: int
    gebiet: str  # das Themengebiet, in dem sich die MBI dabei bewegt hat


@dataclass(frozen=True)
class Impuls:
    thema: str
    staerke: float  # 0 bis 1
    # Andere Themengebiete, aus denen das AUI diesen Impuls mitgebracht hat.
    mitgebracht_aus: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lage:
    """Alles, was der MBI zugänglich ist. Das Feld des AUI gehört nicht dazu."""

    gebiet: str  # das Themengebiet, in dem sie sich gerade bewegt
    abi_feld: tuple[Impuls, ...]  # die wahrgenommene Realität
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
class Entscheidung:
    """Was die MBI in einem Moment willentlich tut."""

    # Thema -> Haltung. Alles, was nicht genannt wird, bleibt bei "weder noch".
    haltungen: Mapping[str, Haltung] = field(default_factory=dict)
    # Das Themengebiet, auf das sie sich neu richtet. None = im bisherigen bleiben.
    gebiet: str | None = None


@dataclass(frozen=True)
class Ausrichtung:
    """Zu welchem Thema die MBI welche Haltung einnimmt."""

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

    def __init__(self, nachklang: float = 0.8, mitnahme: float = 0.5):
        # ANNAHME: Eine Erfahrung wirkt pro Moment um diesen Faktor schwächer nach.
        self.nachklang = nachklang
        # ANNAHME: Erfahrungen aus anderen Themengebieten kommen mit diesem
        # Anteil ihrer Stärke mit. Die aus dem jetzigen Gebiet zählen voll.
        self.mitnahme = mitnahme
        self.erfahrungen: list[Erfahrung] = []
        self.feld: list[Impuls] = []

    def erlebe(self, erfahrung: Erfahrung) -> None:
        self.erfahrungen.append(erfahrung)

    def erzeuge_impulse(self, zeit: int, gebiet: str) -> list[Impuls]:
        """Füllt das Feld mit Impulsen, orientiert am Themengebiet der MBI."""
        beitraege: dict[str, dict[str, float]] = {}  # Thema -> Gebiet -> Stärke
        for e in self.erfahrungen:
            je_gebiet = beitraege.setdefault(e.thema, {})
            nachwirkung = e.staerke * self.nachklang ** (zeit - e.zeit)
            je_gebiet[e.gebiet] = je_gebiet.get(e.gebiet, 0.0) + nachwirkung

        impulse = []
        for thema, je_gebiet in beitraege.items():
            mitgebracht = {
                g: staerke * self.mitnahme
                for g, staerke in je_gebiet.items()
                if g != gebiet
            }
            summe = je_gebiet.get(gebiet, 0.0) + sum(mitgebracht.values())
            if summe < MINDESTSTAERKE:
                continue
            herkunft = sorted(
                (g for g, staerke in mitgebracht.items() if staerke >= MINDESTSTAERKE),
                key=lambda g: mitgebracht[g],
                reverse=True,
            )
            impulse.append(Impuls(thema, min(1.0, summe), tuple(herkunft)))

        self.feld = sorted(impulse, key=lambda i: i.staerke, reverse=True)
        return self.feld


class AutomatischeBewussteIntention:
    """ABI. Automatisch und bewusst: ein eigenes Feld, das an das des AUI angrenzt.

    Was im Feld des AUI stark genug ist, taucht auch hier auf. Die Impulse
    bleiben Impulse des AUI. Die ABI nimmt sie nur wahr. Ihr Feld ist die
    wahrgenommene Realität.
    """

    def __init__(self, schwelle: float = 0.3):
        # ANNAHME: Über die Grenze reicht, was mindestens so stark ist wie die Schwelle.
        self.schwelle = schwelle
        self.feld: list[Impuls] = []

    def nimm_wahr(self, aui_feld: list[Impuls]) -> list[Impuls]:
        self.feld = [i for i in aui_feld if i.staerke >= self.schwelle]
        return self.feld


Entscheider = Callable[[Lage], Entscheidung]


class ManuelleBewussteIntention:
    """MBI. Manuell und bewusst: was man willentlich lenkt.

    Sie bewegt sich immer in genau einem Themengebiet und kann sich auf jedes
    andere richten. Das Feld des AUI bekommt sie nie zu sehen.
    """

    def __init__(self, entscheider: Entscheider, gebiet: str):
        self.entscheider = entscheider
        self.gebiet = gebiet

    def richte_aus(self, lage: Lage) -> list[Ausrichtung]:
        entscheidung = self.entscheider(lage)
        if entscheidung.gebiet:
            self.gebiet = entscheidung.gebiet
        return [
            Ausrichtung(thema, lage.quelle(thema), haltung)
            for thema, haltung in entscheidung.haltungen.items()
        ]


@dataclass(frozen=True)
class Moment:
    """Was in einem Zeitschritt in den drei Layern passiert ist."""

    zeit: int
    gebiet: str  # das Themengebiet, in dem sich die MBI bewegt hat
    sinne: Mapping[str, float]  # sensorische Eindrücke dieses Moments
    aui_feld: tuple[Impuls, ...]  # alles, was im Feld des AUI liegt
    abi_feld: tuple[Impuls, ...]  # der Teil, der auch im Feld der ABI auftaucht
    ausrichtungen: tuple[Ausrichtung, ...]  # die Haltungen der MBI
    wechsel_nach: str | None  # neues Themengebiet ab dem nächsten Moment


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
        wirkung: Mapping[Haltung, float] = STANDARD_WIRKUNG,
    ):
        self.unterbewusstsein = Unterbewusstsein(nachklang, mitnahme)
        self.automatisch = AutomatischeBewussteIntention(schwelle)
        self.manuell = ManuelleBewussteIntention(entscheider, gebiet)
        self.wirkung = wirkung
        self.zeit = 0

    def schritt(self, sinne: Mapping[str, float] | None = None) -> Moment:
        """Ein Moment. `sinne` sind die sensorischen Eindrücke: Thema -> Stärke."""
        sinne = dict(sinne or {})
        gebiet = self.manuell.gebiet
        # ANNAHME: Sensorische Eindrücke sind jetzige Erfahrung und gehen ins AUI.
        for thema, staerke in sinne.items():
            self.unterbewusstsein.erlebe(Erfahrung(thema, staerke, self.zeit, gebiet))

        aui_feld = self.unterbewusstsein.erzeuge_impulse(self.zeit, gebiet)
        abi_feld = self.automatisch.nimm_wahr(aui_feld)
        lage = Lage(gebiet, tuple(abi_feld), sinne)
        # ANNAHME: Ein Wechsel des Themengebiets gilt ab dem nächsten Moment.
        ausrichtungen = self.manuell.richte_aus(lage)

        for ausrichtung in ausrichtungen:
            wirkung = self.wirkung[ausrichtung.haltung]
            if wirkung < 0:
                # Lösen kann man sich nur so weit, wie etwas wahrnehmbar ist.
                wirkung = max(wirkung, -lage.staerke(ausrichtung.thema))
            if wirkung:
                self.unterbewusstsein.erlebe(
                    Erfahrung(ausrichtung.thema, wirkung, self.zeit, gebiet)
                )

        neues_gebiet = self.manuell.gebiet
        moment = Moment(
            self.zeit,
            gebiet,
            sinne,
            tuple(aui_feld),
            lage.abi_feld,
            tuple(ausrichtungen),
            neues_gebiet if neues_gebiet != gebiet else None,
        )
        self.zeit += 1
        return moment
