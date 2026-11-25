"""Das Geistmodell: drei Layer und wie sie aufeinander wirken.

Die Layer:

- AUI: das automatische Unterbewusstsein
- ABI: die automatische bewusste Intention
- MBI: die manuelle bewusste Intention

AUI und ABI sind zwei verschiedene, aneinander angrenzende Felder.

Die MBI befindet sich immer in einer Haltung. Die Haltung ist das Gebiet, das
die MBI erschafft und in dem sie agiert, manchmal mehrere zugleich. Ein
Gebiet kann ein Themengebiet sein (davon gibt es unendlich viele), die jetzige
Erfahrung, die Sinne, die Erinnerung, die Emotion oder der Körper. Emotion und
Körper sind zwei verschiedene Gebiete, und was darin liegt, sind eigene Themen
wie alles andere auch. Die jetzige Erfahrung ist alles, was
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
  Die MBI hat außerdem eine begrenzte Kapazität. Jedes Gebiet, das sie hält,
  verbraucht davon so viel, wie sein Thema gerade stark ist. Wird ein Thema zu
  stark, verdrängt es die anderen, ohne dass die MBI das entscheidet.
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

Jedes Themengebiet beeinflusst die Impulse des AUI, von stark bis gar nicht.
Wie stark, ist durch Erfahrung gelernt.

Gewohnheit entsteht durch Wiederholung: Je öfter die MBI zu einem Thema
engaged, desto langsamer verblasst es im AUI. Engage und disengage geschehen
aber nie von allein, es ist immer die MBI.

Eine Erfahrung und eine Emotion sind eigene Themen. Sie können aber verstärkt
zusammen auftauchen.

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
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable, Collection, Mapping

# Schwächere Impulse gelten als nicht vorhanden.
MINDESTSTAERKE = 0.01

# Fünf besondere Gebiete, in denen sich die MBI bewegen kann. Jeder andere Name
# steht für ein Themengebiet.
SINNE = "Sinne"
JETZIGE_ERFAHRUNG = "jetzige Erfahrung"
ERINNERUNG = "Erinnerung"
EMOTION = "Emotion"
KOERPER = "Körper"
BESONDERE_GEBIETE = (SINNE, JETZIGE_ERFAHRUNG, ERINNERUNG, EMOTION, KOERPER)

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
    # Um welchen Faktor sie pro Moment schwächer nachwirkt. Das AUI legt ihn
    # fest, wenn es die Erfahrung aufnimmt.
    nachklang: float | None = None


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
    # Wie oft die MBI dazu engaged hat, abzüglich der Male, die sie disengaged hat.
    gewohnheit: int = 0


@dataclass(frozen=True)
class Lage:
    """Alles, was der MBI zugänglich ist. Das Feld des AUI gehört nicht dazu."""

    gebiete: tuple[str, ...]  # ihre Haltung: die Gebiete, in denen sie gerade agiert
    gebiete_ohne_mbi: tuple[str, ...]  # Themengebiete, die von selbst entstanden sind
    abi_feld: tuple[Impuls, ...]  # die wahrgenommene Realität
    sinne: Mapping[str, float]  # sensorische Eindrücke: Thema -> Stärke
    emotion: Mapping[str, float] = field(default_factory=dict)  # Emotionen dieses Moments
    koerper: Mapping[str, float] = field(default_factory=dict)  # Körperempfindungen

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

    def __init__(
        self,
        nachklang: float = 0.8,
        mitnahme: float | None = None,
        praegung: float = 0.5,
        kopplung: float = 0.5,
        lerntempo: float = 2.0,
    ):
        # ANNAHME: Eine Erfahrung wirkt pro Moment um diesen Faktor schwächer nach.
        self.nachklang = nachklang
        # Mit welchem Anteil ihrer Stärke Erfahrungen aus anderen Gebieten
        # mitkommen. None heißt: Das hängt vom gelernten Einfluss der Gebiete
        # ab, in denen die MBI ist. Eine Zahl legt den Anteil stattdessen fest.
        self.mitnahme = mitnahme
        # ANNAHME: Nach so vielen Erfahrungen in einem Gebiet hat es den halben
        # Einfluss, nach doppelt so vielen drei Viertel und so weiter.
        self.lerntempo = lerntempo
        # ANNAHME: Wie stark jedes engage oder disengage das Verblassen eines
        # Themas verlangsamt oder beschleunigt.
        self.praegung = praegung
        # ANNAHME: Welchen Anteil seiner Stärke ein Thema an ein anderes
        # weitergibt, mit dem es fest verknüpft ist.
        self.kopplung = kopplung
        # Thema -> wie oft engaged, abzüglich wie oft disengaged.
        self.gewohnheit: dict[str, int] = {}
        # Zwei Themen -> wie oft sie im selben Moment erlebt wurden.
        self.verknuepfungen: dict[frozenset[str], int] = {}
        self.erfahrungen: list[Erfahrung] = []
        self.feld: list[Impuls] = []
        # Stand der letzten Impulse, für das Gewicht der Gebiete der MBI.
        self._staerken: dict[str, float] = {}  # Thema -> Stärke
        self._eigene: dict[str, dict[str, float]] = {}  # Gebiet -> Thema -> Stärke

    def erlebe(self, erfahrung: Erfahrung) -> None:
        if erfahrung.nachklang is None:
            erfahrung = replace(erfahrung, nachklang=self.nachklang_fuer(erfahrung.thema))
        self.erfahrungen.append(erfahrung)

    def uebe(self, thema: str, richtung: int) -> None:
        """Hält fest, dass die MBI engaged (+1) oder disengaged (-1) hat."""
        self.gewohnheit[thema] = self.gewohnheit.get(thema, 0) + richtung

    def nachklang_fuer(self, thema: str) -> float:
        """Wie langsam eine neue Erfahrung zu diesem Thema verblasst."""
        # ANNAHME: Die Gewohnheit wirkt auf Erfahrungen, die ab jetzt dazukommen.
        # Was schon im AUI liegt, verblasst weiter wie bisher.
        gewohnheit = self.gewohnheit.get(thema, 0)
        if gewohnheit >= 0:
            return self.nachklang ** (1 / (1 + self.praegung * gewohnheit))
        return self.nachklang ** (1 - self.praegung * gewohnheit)

    def einfluss(self, gebiet: str) -> float:
        """Wie stark ein Gebiet zurückdrängt, was nicht zu ihm gehört: 0 bis 1."""
        if self.mitnahme is not None:
            return 1 - self.mitnahme
        # ANNAHME: Der Einfluss ist durch Erfahrung gelernt. Er wächst mit
        # allem, was in dem Gebiet erlebt oder dort durch engage verstärkt
        # wurde, und schrumpft mit jedem disengage dort.
        menge = sum(
            1 if e.staerke > 0 else -1
            for e in self.erfahrungen
            if gebiet in e.gebiete or e.thema == gebiet
        )
        return 1 - 0.5 ** (max(0, menge) / self.lerntempo)

    def verknuepfe(self, themen: Collection[str]) -> None:
        """Hält fest, dass diese Themen im selben Moment erlebt wurden."""
        themen = sorted(set(themen))
        for i, a in enumerate(themen):
            for b in themen[i + 1 :]:
                paar = frozenset((a, b))
                self.verknuepfungen[paar] = self.verknuepfungen.get(paar, 0) + 1

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
        # Das einflussreichste Gebiet bestimmt, wie viel von allem, was nicht
        # dazugehört, noch mitkommt.
        mitnahme = 1 - max((self.einfluss(g) for g in gebiete), default=0.0)
        staerken: dict[str, float] = {}
        aus_haltung: dict[str, float] = {}  # Thema -> Stärke aus der Haltung der MBI
        eigene: dict[str, dict[str, float]] = {}  # Gebiet der MBI -> Thema -> Stärke
        herkunft: dict[str, dict[str, float]] = {}  # Thema -> Gebiet -> Stärke
        enthalten: dict[str, dict[str, float]] = {}  # Haltung -> Thema -> Stärke
        for e in self.erfahrungen:
            # ANNAHME: In der Erinnerung zählt jede frühere Erfahrung voll und
            # unverblasst, egal aus welchem Gebiet sie stammt.
            if ERINNERUNG in gebiete and e.zeit < zeit:
                beitrag, mitgefuehrt = e.staerke, False
            else:
                nachklang = self.nachklang if e.nachklang is None else e.nachklang
                beitrag = e.staerke * nachklang ** (zeit - e.zeit)
                mitgefuehrt = not any(
                    gehoert_zum_gebiet(e, g, im_abi_feld) for g in gebiete
                )
                if mitgefuehrt:
                    beitrag *= mitnahme
            staerken[e.thema] = staerken.get(e.thema, 0.0) + beitrag
            zugehoerig = [
                g
                for g in haltung
                if (g == ERINNERUNG and e.zeit < zeit)
                or gehoert_zum_gebiet(e, g, im_abi_feld)
            ]
            if zugehoerig:
                aus_haltung[e.thema] = aus_haltung.get(e.thema, 0.0) + beitrag
            for g in zugehoerig:
                je_thema = eigene.setdefault(g, {})
                je_thema[e.thema] = je_thema.get(e.thema, 0.0) + beitrag
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

        # Was zusammen erlebt wurde, taucht verstärkt zusammen auf: Jedes Thema
        # bekommt einen Teil der Stärke seiner Partner dazu.
        # ANNAHME: Die Bindung wächst mit jedem gemeinsamen Erleben (einmal: 0,5,
        # zweimal: 0,75) und zieht auch ein Thema mit, das sonst verklungen wäre.
        basis = dict(staerken)
        for paar, anzahl in self.verknuepfungen.items():
            a, b = sorted(paar)
            bindung = 1 - 0.5**anzahl
            for thema, partner in ((a, b), (b, a)):
                zug = self.kopplung * bindung * min(1.0, max(0.0, basis.get(partner, 0.0)))
                if zug:
                    staerken[thema] = staerken.get(thema, 0.0) + zug

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
            # Was ein Thema von seinen Partnern dazubekommt, zählt dabei nicht.
            eigenes = basis.get(thema, 0.0)
            stammt_aus_haltung = eigenes > 0 and 2 * aus_haltung.get(thema, 0.0) >= eigenes
            impulse.append(
                Impuls(
                    thema,
                    min(1.0, staerke),
                    tuple(mitgebracht_aus),
                    aus_haltung=stammt_aus_haltung,
                    gewohnheit=self.gewohnheit.get(thema, 0),
                )
            )

        # Eine Haltung, die das AUI enthält, liegt selbst als Impuls im Feld.
        # ANNAHME: Sie ist so stark wie das stärkste Thema, das sie enthält.
        # Gibt es zugleich ein Thema dieses Namens, zählt das Stärkere von beiden.
        themen = {impuls.thema: impuls for impuls in impulse}
        for frueher, je_thema in enthalten.items():
            staerke = max(je_thema.values())
            if frueher in themen:
                staerke = max(staerke, themen[frueher].staerke)
            if staerke >= MINDESTSTAERKE:
                themen[frueher] = Impuls(
                    frueher,
                    min(1.0, staerke),
                    haltung=True,
                    gewohnheit=self.gewohnheit.get(frueher, 0),
                )

        self.feld = sorted(themen.values(), key=lambda i: i.staerke, reverse=True)
        self._staerken = {i.thema: i.staerke for i in self.feld}
        self._eigene = eigene
        return self.feld

    def gewicht(self, gebiet: str, gebiete: Collection[str]) -> float:
        """Wie viel Kapazität der MBI ein Gebiet gerade verbraucht.

        `gebiete` sind alle Gebiete, die die MBI hält.
        """
        # ANNAHME: Ein Gebiet wiegt so viel, wie sein eigenes Thema stark ist.
        # Hat es keines, wiegt es so viel wie das stärkste Thema darin, das
        # die MBI nicht ohnehin als eigenes Gebiet hält.
        if gebiet in self._staerken:
            return self._staerken[gebiet]
        andere = [
            staerke
            for thema, staerke in self._eigene.get(gebiet, {}).items()
            if thema not in gebiete
        ]
        return min(1.0, max(andere, default=0.0))


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

    def verdraenge(
        self,
        gewicht: Callable[[str, Collection[str]], float],
        kapazitaet: float,
        geschuetzt: Collection[str] = (),
    ) -> list[str]:
        """Gibt Gebiete auf, bis die übrigen in die Kapazität passen.

        Das geschieht ohne Entscheidung der MBI. Gibt die verdrängten Gebiete
        zurück.
        """
        verdraengt = []
        while len(self.gebiete) > 1:
            gewichte = {g: gewicht(g, self.gebiete) for g in self.gebiete}
            if sum(gewichte.values()) < kapazitaet:
                break
            # ANNAHME: Zuerst geht das schwächste Gebiet. Was die MBI in diesem
            # Moment erst betreten hat, bleibt.
            kandidaten = [g for g in self.gebiete if g not in geschuetzt]
            if not kandidaten:
                break
            schwaechstes = min(kandidaten, key=gewichte.__getitem__)
            self.gebiete.remove(schwaechstes)
            verdraengt.append(schwaechstes)
        return verdraengt


@dataclass(frozen=True)
class Moment:
    """Was in einem Zeitschritt in den drei Layern passiert ist."""

    zeit: int
    gebiete: tuple[str, ...]  # die Haltung der MBI: die Gebiete, in denen sie agiert hat
    gebiete_ohne_mbi: tuple[str, ...]  # Themengebiete, die von selbst bestanden
    sinne: Mapping[str, float]  # sensorische Eindrücke dieses Moments
    emotion: Mapping[str, float]  # Emotionen dieses Moments
    koerper: Mapping[str, float]  # Körperempfindungen dieses Moments
    aui_feld: tuple[Impuls, ...]  # alles, was im Feld des AUI liegt
    abi_feld: tuple[Impuls, ...]  # der Teil, der auch im Feld der ABI auftaucht
    umgang: Mapping[str, Umgang]  # Thema -> Umgang der MBI
    einfluss: Mapping[str, float]  # Gebiet -> wie stark es Fremdes zurückdrängt
    verdraengt: tuple[str, ...]  # Gebiete, die nicht mehr in die Kapazität passten
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
        kapazitaet: float = 1.0,
        nachklang: float = 0.8,
        mitnahme: float | None = None,
        praegung: float = 0.5,
        kopplung: float = 0.5,
        schwelle: float = 0.3,
        chance: float = 0.25,
        zufall: random.Random | None = None,
        wirkung: Mapping[Umgang, float] = STANDARD_WIRKUNG,
    ):
        self.unterbewusstsein = Unterbewusstsein(nachklang, mitnahme, praegung, kopplung)
        self.automatisch = AutomatischeBewussteIntention(schwelle, chance, zufall)
        self.manuell = ManuelleBewussteIntention(entscheider, gebiet)
        self.wirkung = wirkung
        # ANNAHME: Die Kapazität der MBI entspricht einem Thema in voller Stärke.
        self.kapazitaet = kapazitaet
        self.zeit = 0

    def schritt(
        self,
        sinne: Mapping[str, float] | None = None,
        emotion: Mapping[str, float] | None = None,
        koerper: Mapping[str, float] | None = None,
    ) -> Moment:
        """Ein Moment.

        `sinne`, `emotion` und `koerper` sind, was in diesem Moment erlebt wird:
        jeweils Thema -> Stärke.
        """
        sinne, emotion, koerper = dict(sinne or {}), dict(emotion or {}), dict(koerper or {})
        gebiete = tuple(self.manuell.gebiete)
        gebiete_ohne_mbi = tuple(self.automatisch.gebiete_ohne_mbi)
        # ANNAHME: Sinneseindrücke, Emotionen und Körperempfindungen gehen ins
        # AUI und gehören jeweils zu ihrem eigenen Gebiet, egal in welchem
        # Gebiet sich die MBI gerade bewegt.
        for gebiet, erlebtes in ((SINNE, sinne), (EMOTION, emotion), (KOERPER, koerper)):
            for thema, staerke in erlebtes.items():
                self.unterbewusstsein.erlebe(Erfahrung(thema, staerke, self.zeit, (gebiet,)))

        # ANNAHME: Was im Feld der ABI auftaucht, bemisst sich am Feld, wie es
        # zu Beginn des Moments ist, also am Ergebnis des vorigen Moments.
        bisher_im_abi_feld = {impuls.thema for impuls in self.automatisch.feld}
        einfluss = {
            g: self.unterbewusstsein.einfluss(g) for g in gebiete + gebiete_ohne_mbi
        }
        # ANNAHME: AUI und ABI orientieren sich auch an den Themengebieten, die
        # ohne die MBI entstanden sind.
        aui_feld = self.unterbewusstsein.erzeuge_impulse(
            self.zeit, gebiete + gebiete_ohne_mbi, bisher_im_abi_feld, gebiete
        )
        abi_feld = self.automatisch.nimm_wahr(aui_feld)
        # ANNAHME: Was im selben Moment erlebt wird, verknüpft sich miteinander.
        # Die Verknüpfung wirkt ab dem nächsten Moment.
        self.unterbewusstsein.verknuepfe([*sinne, *emotion, *koerper])
        lage = Lage(gebiete, gebiete_ohne_mbi, tuple(abi_feld), sinne, emotion, koerper)
        # ANNAHME: Ein Wechsel der Gebiete gilt ab dem nächsten Moment.
        umgang = self.manuell.richte_aus(lage)

        for thema, art in umgang.items():
            wirkung = self.wirkung[art]
            if wirkung < 0:
                # Schwächen lässt sich etwas nur so weit, wie es auftaucht.
                wirkung = max(wirkung, -lage.staerke(thema))
            # Wiederholung prägt: Engage macht das Thema zur Gewohnheit,
            # disengage baut sie wieder ab.
            if art is not Umgang.WEDER_NOCH:
                self.unterbewusstsein.uebe(thema, 1 if art is Umgang.ENGAGE else -1)
            if wirkung:
                # Die Erfahrung enthält die Haltung, in der die MBI dabei war.
                self.unterbewusstsein.erlebe(Erfahrung(thema, wirkung, self.zeit, gebiete))

        gerade_betreten = [g for g in self.manuell.gebiete if g not in gebiete]
        verdraengt = self.manuell.verdraenge(
            self.unterbewusstsein.gewicht, self.kapazitaet, gerade_betreten
        )

        self.automatisch.lasse_gebiete_entstehen(umgang, self.manuell.gebiete)

        moment = Moment(
            self.zeit,
            gebiete,
            gebiete_ohne_mbi,
            sinne,
            emotion,
            koerper,
            tuple(aui_feld),
            lage.abi_feld,
            umgang,
            einfluss,
            tuple(verdraengt),
            tuple(self.manuell.gebiete),
            tuple(self.automatisch.gebiete_ohne_mbi),
        )
        self.zeit += 1
        return moment
