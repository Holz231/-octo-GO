# Geistmodell (Arbeitstitel)

Ein Programm, das ein Modell des Geistes abbildet: seine fundamentalen
Eigenschaften, deren Funktionen und die Dynamiken und Beziehungen zwischen ihnen.

Stand: Der Kern läuft. Diese Datei hält fest, was im Modell feststeht und
welche Lücken das Programm vorläufig mit eigenen Annahmen füllt.

## Ausprobieren

    python -m geist --demo             # die drei Haltungen im Vergleich
    python -m geist --demo gebiete     # wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo erinnerung  # wie die MBI eine Erinnerung aktiviert
    python -m geist                    # interaktiv: du bist die MBI
    python -m pytest                   # Tests

Mit `--mehrere` hält die MBI mehrere Gebiete zugleich statt nur eines. Das geht
bei den Demos und im interaktiven Modus.

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
   - die jetzige Erfahrung: alles, was im Feld der ABI auftaucht,
   - die sensorischen Eindrücke.
4. An dem Gebiet, in dem sich die MBI bewegt, orientieren sich ABI und AUI.
5. Das AUI führt vergangene Themen und Erfahrungen mit sich in neue Gebiete,
   auf die sich die MBI richtet.
6. Wie die MBI und das AUI gerade sind, formt gleichzeitig die wahrgenommene
   Realität der ABI.
7. Die MBI nimmt zu einem Thema eine von drei Haltungen ein. Haltungen gibt
   es nur bei AUI und ABI, also zu dem, was aus dem AUI im Feld der ABI
   auftaucht:
   - **engage** verstärkt das Thema im AUI. Zugleich macht die MBI es zu einem
     neuen Themengebiet, in dem sie agiert: parallel zum bisherigen oder
     allein, je nachdem, ob die MBI mehrere Themen zugleich hat oder nur eines.
   - **disengage** schwächt das Thema im AUI und verhindert, dass die MBI es zu
     einem neuen Themengebiet in der ABI macht.
   - **weder noch** („non disengage and non engage“) verstärkt nicht und
     schwächt nicht. Es bringt aber die Chance mit, dass das Thema ohne die MBI
     aus dem AUI in die ABI geht und dort ohne die MBI zu einem neuen
     Themengebiet wird. Oder eben nicht, dann verblasst es wieder.
8. Die MBI kann sich auch autonom auf neue Themengebiete richten, auch wenn
   sie vorher nicht im Bewusstsein waren, also ohne dass etwas aus dem AUI in
   die ABI gestiegen ist. Das ist kein engage, sondern lediglich ein
   Themenwechsel oder ein Themenerhalt.
9. Die MBI hat keinen direkten Zugriff auf das AUI. Sie erreicht es nur
   indirekt. Zu etwas, das nur im AUI liegt und nicht in der ABI auftaucht,
   kann sie keine Haltung einnehmen.
10. Die MBI kann Erinnerungen aktivieren.

Bewusst zurückgestellt: Grenzen der MBI (Aufmerksamkeit, Energie),
Gewohnheitsbildung, weitere Bausteine wie Emotion oder Körper.

## 3. Vorläufige Annahmen im Programm

Diese Punkte gibt das Modell noch nicht vor. Das Programm braucht sie aber, um
zu laufen. Sie stehen in `geist/modell.py` und sind dort mit `ANNAHME` markiert.

Zu den Haltungen:

- **Wie stark engage und disengage wirken:** um einen festen Betrag (0,4), als
  neue Erfahrung im AUI. Disengage schwächt höchstens so weit, wie das Thema
  gerade auftaucht.
- **Mehrere oder eines:** Ob die MBI mehrere Gebiete zugleich hält, ist eine
  Einstellung von außen (`--mehrere`), keine Entscheidung im einzelnen Moment.
- **Disengage beendet ein Gebiet:** Ist das Thema schon ein Themengebiet der
  MBI, hört es durch disengage auf, eines zu sein.
- **Ohne eigenes Gebiet:** Gibt die MBI ihr letztes Gebiet auf, bleibt ihr die
  jetzige Erfahrung.
- **Themenwechsel ersetzt:** Wechselt die MBI autonom das Thema, gibt sie alle
  bisherigen Gebiete auf, auch wenn sie mehrere zugleich hält. Parallel kommt
  ein Gebiet nur durch engage dazu.
- **Themenwechsel in die Sinne oder die jetzige Erfahrung:** Auch dorthin
  kommt die MBI durch einen Themenwechsel.
- **Themenerhalt:** Tut die MBI nichts, bleibt sie in ihren Gebieten.

Zu den Erinnerungen:

- **Was eine Erinnerung ist:** eine frühere Erfahrung im AUI. Erinnern kann
  sich die MBI nur an Themen, zu denen es dort eine gibt.
- **Was aktivieren bewirkt:** Die stärkste frühere Erfahrung zu dem Thema wird
  noch einmal erlebt, in ihrer ursprünglichen Stärke und in ihren
  ursprünglichen Gebieten. Das ist weder engage noch Themenwechsel.
- **Wann sie in der ABI auftaucht:** frühestens im nächsten Moment, weil sie
  wie jede Erfahrung über das AUI wirkt. Gehört sie zu einem anderen Gebiet als
  dem der MBI, kommt sie nur mit halber Stärke mit.

Zu den Themengebieten ohne MBI:

- **Wie groß die Chance ist:** 25 Prozent pro Moment, für jedes Thema im Feld
  der ABI, zu dem die MBI weder noch hält.
- **Was „geht aus dem AUI in die ABI“ heißt:** Das Thema taucht im Feld der ABI
  auf, weil es stark genug ist. Erst dann hat es die Chance.
- **Was ein solches Gebiet bewirkt:** AUI und ABI orientieren sich daran wie an
  einem Gebiet der MBI.
- **Wann es sich auflöst:** wenn sein Thema aus dem Feld der ABI verblasst oder
  die MBI disengaged. Engaged sie, gehört es ab dann der MBI.

Zu den Gebieten:

- **Wie sich das AUI an den Gebieten orientiert:** Erfahrungen aus den
  jetzigen Gebieten zählen voll. Erfahrungen aus anderen Gebieten kommen mit
  halber Stärke mit.
- **Was zu einem Themengebiet gehört:** das Thema, aus dem es entstanden ist,
  und alles, wozu die MBI dort engaged oder disengaged hat.
- **Was zu den Sinnen gehört:** jeder sensorische Eindruck, egal in welchem
  Gebiet sich die MBI gerade bewegt.
- **Woran sich „taucht im Feld der ABI auf“ bemisst:** am Feld, wie es zu
  Beginn des Moments ist, also am Ergebnis des vorigen Moments.
- **Was die wahrgenommene Realität ist:** das Feld der ABI.
- **Wann ein Gebietswechsel gilt:** ab dem nächsten Moment.

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
