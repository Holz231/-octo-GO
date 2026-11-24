# Geistmodell (Arbeitstitel)

Ein Programm, das ein Modell des Geistes abbildet: seine fundamentalen
Eigenschaften, deren Funktionen und die Dynamiken und Beziehungen zwischen ihnen.

Stand: Der Kern läuft. Diese Datei hält fest, was im Modell feststeht und
welche Lücken das Programm vorläufig mit eigenen Annahmen füllt.

## Ausprobieren

    python -m geist --demo             # wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo haltungen   # die drei Haltungen im Vergleich
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
3. Die MBI bewegt sich immer in einem bestimmten Gebiet. Es gibt drei Arten
   von Gebieten:
   - ein Themengebiet (davon gibt es unendlich viele, etwa Familie oder Arbeit),
   - die jetzige Erfahrung,
   - die sensorischen Eindrücke.
4. An dem Gebiet, in dem sich die MBI bewegt, orientieren sich ABI und AUI.
5. Das AUI führt vergangene Themen und Erfahrungen mit sich in neue Gebiete,
   auf die sich die MBI richtet.
6. Wie die MBI und das AUI gerade sind, formt gleichzeitig die wahrgenommene
   Realität der ABI.
7. Die MBI nimmt eine von drei Haltungen ein: **engage**, **disengage** oder
   **weder noch** („non disengage and non engage“).
8. Die MBI hat keinen direkten Zugriff auf das AUI. Sie erreicht es nur
   indirekt.

Bewusst zurückgestellt: Grenzen der MBI (Aufmerksamkeit, Energie),
Gewohnheitsbildung, weitere Bausteine wie Emotion, Erinnerung oder Körper.

## 3. Vorläufige Annahmen im Programm

Diese Punkte gibt das Modell noch nicht vor. Das Programm braucht sie aber, um
zu laufen. Sie stehen in `geist/modell.py` und sind dort mit `ANNAHME` markiert.

Zu den Gebieten:

- **Wie sich das AUI am Gebiet orientiert:** Erfahrungen aus dem Gebiet, in dem
  sich die MBI gerade bewegt, zählen voll. Erfahrungen aus anderen Gebieten
  kommen mit halber Stärke mit.
- **Was zu den Sinnen gehört:** jeder sensorische Eindruck, egal in welchem
  Gebiet sich die MBI gerade bewegt. Starke Eindrücke tauchen deshalb überall
  im Feld der ABI auf, schwache nur, wenn die MBI in den Sinnen ist.
- **Was zur jetzigen Erfahrung gehört:** das, was in diesem Moment erlebt wird.
  Alles Frühere ist vergangen und wird nur mitgeführt.
- **Was zu einem Themengebiet gehört:** die Haltungen, die die MBI dort
  eingenommen hat.
- **Was die wahrgenommene Realität ist:** das Feld der ABI.
- **Wann ein Gebietswechsel gilt:** ab dem nächsten Moment.

Zu den Haltungen:

- **Wozu die MBI eine Haltung einnimmt:** zu einzelnen Themen, während sie sich
  in einem Gebiet bewegt. Das Thema ist frei wählbar.
- **Was eine Haltung bewirkt:** Die Haltung wird selbst zur Erfahrung und wirkt
  so auf spätere Impulse zurück. Engage stärkt das Thema, disengage schwächt
  es, weder noch hinterlässt keine Spur. Lösen kann man sich nur von etwas,
  das gerade wahrnehmbar ist.

Zu den Feldern:

- **Welcher Teil im Feld der ABI auftaucht:** alles, was mindestens so stark
  ist wie eine feste Schwelle (0,3). Die Schwelle ist die Grenze zwischen den
  beiden Feldern.
- **Ob etwas in beiden Feldern zugleich ist:** Ja. Was im Feld der ABI
  auftaucht, liegt weiterhin auch im Feld des AUI.
- **Wie Erfahrungen nachwirken:** Jede Erfahrung klingt pro Moment um den
  Faktor 0,8 ab.
- **Themen:** Erfahrungen und Impulse haben ein Thema (ein Wort) und eine
  Stärke zwischen 0 und 1.
