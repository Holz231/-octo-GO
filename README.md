# Geistmodell (Arbeitstitel)

Ein Programm, das ein Modell des Geistes abbildet: seine fundamentalen
Eigenschaften, deren Funktionen und die Dynamiken und Beziehungen zwischen ihnen.

Stand: Der Kern läuft. Diese Datei hält fest, was im Modell feststeht und
welche Lücken das Programm vorläufig mit eigenen Annahmen füllt.

## Ausprobieren

    python -m geist --demo             # wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo haltungen   # die drei Haltungen und Quellen im Vergleich
    python -m geist                    # interaktiv: du bist die MBI
    python -m pytest                   # Tests

Braucht nur Python 3.10 oder neuer, für die Tests zusätzlich pytest.

## 1. Fundamentale Layer des Geistes

| Kürzel | Layer | Steuerung | Bewusstheit |
|---|---|---|---|
| AUI | Automatisches Unterbewusstsein | automatisch | unbewusst |
| ABI | Automatische bewusste Intention | automatisch | bewusst |
| MBI | Manuelle bewusste Intention | manuell | bewusst |

Die Kombination „manuell + unbewusst“ gibt es im Modell bewusst nicht.

## 2. Funktionen und Beziehungen

Festgelegt:

1. Das AUI läuft ständig im Hintergrund und erzeugt Impulse, Gedanken und
   Wünsche, und zwar aufgrund von vorherigen und jetzigen Erfahrungen.
2. AUI und ABI sind zwei verschiedene Felder, die aneinander angrenzen. Ein
   Teil dessen, was das AUI erzeugt, taucht im Feld der ABI auf und wird von ihr
   wahrgenommen. Es wird dabei nicht selbst zur ABI.
3. Die MBI bewegt sich immer in einem bestimmten Themengebiet. An diesem
   Gebiet orientieren sich ABI und AUI.
4. Das AUI führt vergangene Themen und Erfahrungen mit sich in neue Gebiete,
   auf die sich die MBI richtet.
5. Wie die MBI und das AUI gerade sind, formt gleichzeitig die wahrgenommene
   Realität der ABI.
6. Die MBI kann sich auf drei Arten von Zielen richten:
   - auf ein Thema aus einem unendlichen Themengebiet, also auf Beliebiges,
   - auf die jetzige Erfahrung,
   - auf sensorische Eindrücke.
7. Zu dem, worauf sie gerichtet ist, nimmt die MBI eine von drei Haltungen ein:
   **engage**, **disengage** oder **weder noch**
   („non disengage and non engage“).
8. Die MBI hat keinen direkten Zugriff auf das AUI. Sie erreicht es nur
   indirekt.

Bewusst zurückgestellt: Grenzen der MBI (Aufmerksamkeit, Energie),
Gewohnheitsbildung, weitere Bausteine wie Emotion, Erinnerung oder Körper.

## 3. Vorläufige Annahmen im Programm

Diese Punkte gibt das Modell noch nicht vor. Das Programm braucht sie aber, um
zu laufen. Sie stehen in `geist/modell.py` und sind dort mit `ANNAHME` markiert.

- **Was eine Haltung bewirkt:** Die Haltung wird selbst zur Erfahrung und wirkt
  so auf spätere Impulse zurück. Engage stärkt das Thema, disengage schwächt
  es, weder noch hinterlässt keine Spur. Lösen kann man sich nur von etwas,
  das gerade wahrnehmbar ist.
- **Wie sich das AUI am Themengebiet orientiert:** Erfahrungen aus dem Gebiet,
  in dem sich die MBI gerade bewegt, zählen voll. Erfahrungen aus anderen
  Gebieten kommen mit halber Stärke mit.
- **Wozu eine Erfahrung gehört:** zu dem Themengebiet, in dem sich die MBI
  bewegt hat, als sie gemacht wurde.
- **Was die wahrgenommene Realität ist:** das Feld der ABI.
- **Wann ein Gebietswechsel gilt:** ab dem nächsten Moment.
- **Gebiet und Haltung sind zweierlei:** Die MBI bewegt sich in einem
  Themengebiet und nimmt darin Haltungen zu einzelnen Themen ein.
- **Was „jetzige Erfahrung“ heißt:** das, was gerade im Feld der ABI auftaucht.
- **Wohin sensorische Eindrücke gehen:** Sie sind jetzige Erfahrung und gehen
  ins AUI. Starke tauchen dadurch sofort im Feld auf, schwache erst, wenn sich
  die MBI auf sie richtet.
- **Welcher Teil im Feld der ABI auftaucht:** alles, was mindestens so stark
  ist wie eine feste Schwelle (0,3). Die Schwelle ist die Grenze zwischen den
  beiden Feldern.
- **Ob etwas in beiden Feldern zugleich ist:** Ja. Was im Feld der ABI
  auftaucht, liegt weiterhin auch im Feld des AUI.
- **Wie Erfahrungen nachwirken:** Jede Erfahrung klingt pro Moment um den
  Faktor 0,8 ab.
- **Themen:** Erfahrungen und Impulse haben ein Thema (ein Wort) und eine
  Stärke zwischen 0 und 1.
