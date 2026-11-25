# Geistmodell (Arbeitstitel)

Ein Programm, das ein Modell des Geistes abbildet: seine fundamentalen
Eigenschaften, deren Funktionen und die Dynamiken und Beziehungen zwischen ihnen.

Stand: Der Kern läuft. Diese Datei hält fest, was im Modell feststeht und
welche Lücken das Programm vorläufig mit eigenen Annahmen füllt.

## Ausprobieren

    python -m geist --demo             # engage, disengage und weder noch im Vergleich
    python -m geist --demo haltung     # wie eine frühere Haltung aus dem AUI auftaucht
    python -m geist --demo gebiete     # wie das AUI Themen in neue Gebiete mitführt
    python -m geist --demo erinnerung  # wie die MBI in die Erinnerung wechselt
    python -m geist --demo gewohnheit  # wie wiederholtes engage ein Thema prägt
    python -m geist --demo emotion     # wie Emotion und Erfahrung zusammen auftauchen
    python -m geist --demo einfluss    # wie ein Gebiet durch Erfahrung an Einfluss gewinnt
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
3. Die MBI bewegt sich immer in einem bestimmten Gebiet. Dieses Gebiet ist
   ihre Haltung: Eine Haltung wird durch die MBI erschaffen, und man befindet
   sich immer in einer. Es gibt sechs Arten von Gebieten:
   - ein Themengebiet (davon gibt es unendlich viele, etwa Familie oder Arbeit),
   - die jetzige Erfahrung: alles, was im Feld der ABI auftaucht,
   - die sensorischen Eindrücke,
   - die Erinnerung,
   - die Emotion,
   - den Körper.

   Emotion und Körper sind zwei verschiedene Gebiete. Was darin liegt, sind
   eigene Themen wie alles andere auch. Auch ein Zustand oder eine
   Grundstimmung ist nur ein Thema: Ist es stark genug, kommt es in die ABI,
   und die MBI kann es aufgreifen und durch engage oder disengage beeinflussen.
4. An dem Gebiet, in dem sich die MBI bewegt, orientieren sich ABI und AUI.
5. Das AUI führt vergangene Themen und Erfahrungen mit sich in neue Gebiete,
   auf die sich die MBI richtet.
6. Wie die MBI und das AUI gerade sind, formt gleichzeitig die wahrgenommene
   Realität der ABI.
7. Die MBI geht mit einem Thema auf eine von drei Arten um. Das gibt es nur
   bei AUI und ABI, also mit dem, was aus dem AUI im Feld der ABI auftaucht:
   - **engage** verstärkt das Thema im AUI. Zugleich macht die MBI es zu einem
     neuen Themengebiet, in dem sie agiert. Stammt das neue Thema aus der
     jetzigen Haltung, läuft es parallel. Kommt es aus einem anderen Gebiet,
     ersetzt es sie. Der Wechsel ist dabei nicht total, weil das Vorherige
     dann im AUI auftaucht. Die MBI hat außerdem eine begrenzte Kapazität:
     Jedes Gebiet, das sie hält, verbraucht davon so viel, wie sein Thema
     gerade stark ist. Solange alles hineinpasst, läuft es parallel. Wird
     ein Thema zu stark, verdrängt es die anderen, und zwar ohne Entscheidung
     der MBI.
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
   kann sie weder engagen noch disengagen.
10. Die MBI kann Erinnerungen aktivieren. Die Erinnerung ist dabei nur ein
    anderes Themengebiet.
11. Das AUI kann die Haltung beeinflussen: Enthält es eine Haltung, kann diese
    ins Bewusstsein auftauchen, und die MBI kann dann darauf engagen.
12. Gewohnheit entsteht durch Wiederholung: Je öfter die MBI zu einem Thema
    engaged, desto langsamer verblasst es im AUI und desto leichter taucht es
    von selbst in der ABI auf. Haltungen sind dabei auch nur Themengebiete.
    Engage und disengage geschehen nie von allein, es ist immer die MBI. Sie
    verstärken oder verringern aber die Präsenz im AUI.
13. Eine Erfahrung und eine Emotion sind grundsätzlich eigene Themen. Sie
    können aber verstärkt zusammen auftauchen.

14. Jedes Themengebiet beeinflusst die Impulse des AUI, im vollen Spektrum von
    stark bis gar nicht. Wie stark, ist durch Erfahrung gelernt.

Festgehalten, aber noch nicht eingebaut: Ein Themengebiet kann dazu führen,
dass das AUI insgesamt mehr oder weniger Impulse erzeugt, etwa Müdigkeit oder
Anspannung. Offen ist, was entscheidet, ob es mehr oder weniger werden.

## 3. Vorläufige Annahmen im Programm

Diese Punkte gibt das Modell noch nicht vor. Das Programm braucht sie aber, um
zu laufen. Sie stehen in `geist/modell.py` und sind dort mit `ANNAHME` markiert.

Zum Umgang mit einem Thema (engage, disengage, weder noch). Das Wort „Umgang“
stammt von mir, im Modell hat diese Dreiheit noch keinen eigenen Namen:

- **Wie stark engage und disengage wirken:** um einen festen Betrag (0,4), als
  neue Erfahrung im AUI. Disengage schwächt höchstens so weit, wie das Thema
  gerade auftaucht.
- **Woher ein Thema stammt:** aus der jetzigen Haltung, wenn mindestens die
  Hälfte seiner Stärke von dort kommt, sonst aus einem anderen Gebiet. Eine
  frühere Haltung, die auftaucht, kommt immer aus einem anderen Gebiet.
- **Was zur jetzigen Haltung zählt:** nur die Gebiete der MBI, nicht die
  Themengebiete, die ohne sie entstanden sind.
- **Disengage beendet ein Gebiet:** Ist das Thema schon ein Themengebiet der
  MBI, hört es durch disengage auf, eines zu sein.
- **Ohne eigenes Gebiet:** Gibt die MBI ihr letztes Gebiet auf, bleibt ihr die
  jetzige Erfahrung.
- **Themenwechsel ersetzt:** Wechselt die MBI autonom das Thema, gibt sie alle
  bisherigen Gebiete auf. Parallel kommt ein Gebiet nur durch engage dazu.
- **Themenwechsel in die Sinne oder die jetzige Erfahrung:** Auch dorthin
  kommt die MBI durch einen Themenwechsel.
- **Themenerhalt:** Tut die MBI nichts, bleibt sie in ihren Gebieten.

Zum Einfluss der Gebiete auf die Impulse des AUI. Eingebaut sind zwei Wege:
Ein Gebiet drängt zurück, was nicht zu ihm gehört, und ein Thema zieht
bestimmte andere Themen mit (siehe „Zum gemeinsamen Auftauchen“).

- **Woran der Einfluss gelernt wird:** an der Menge der Erfahrung im Gebiet.
  Jede Erfahrung dort und jedes engage dort zählen dazu, jedes disengage dort
  zählt ab.
- **Wie schnell er wächst:** Ein Gebiet ohne Erfahrung hat keinen Einfluss.
  Nach zwei Erfahrungen hat es den halben, nach vier drei Viertel, nach acht
  fast den vollen.
- **Wie er wirkt:** Ist die MBI in dem Gebiet, kommt alles, was nicht
  dazugehört, nur mit dem Rest der Stärke mit: bei 75 % Einfluss mit einem
  Viertel. Das ersetzt die frühere feste halbe Stärke.
- **Bei mehreren Gebieten** bestimmt das einflussreichste.
- **In den Demo-Läufen** außer `einfluss` ist der Einfluss auf 50 % festgelegt,
  damit jeder Lauf nur seinen eigenen Punkt zeigt.

Zur Gewohnheit:

- **Was gezählt wird:** pro Thema, wie oft die MBI dazu engaged hat, abzüglich
  der Male, die sie disengaged hat.
- **Wie sie wirkt:** Jede neue Erfahrung zu einem gewohnten Thema verblasst
  langsamer: ohne Gewohnheit um den Faktor 0,8 pro Moment, nach einem engage
  um 0,86, nach dreien um 0,91. Überwiegt disengage, verblasst sie schneller.
- **Nicht rückwirkend:** Die Gewohnheit wirkt auf Erfahrungen, die ab dann
  dazukommen. Was schon im AUI liegt, verblasst weiter wie bisher.
- **Leichteres Auftauchen** ist keine eigene Regel, sondern folgt daraus:
  Was langsamer verblasst, sammelt sich an und bleibt länger im Feld der ABI.

Zu Emotion und Körper:

- **Woher sie kommen:** Wie Sinneseindrücke werden Emotionen und
  Körperempfindungen pro Moment von außen eingegeben und gehen ins AUI. Sie
  gehören jeweils zu ihrem eigenen Gebiet, egal wo die MBI gerade ist.
- **Keine frühere Haltung:** Wie die Sinne tauchen Emotion und Körper nicht
  als frühere Haltung auf. Die MBI kommt durch einen Themenwechsel dorthin.

Zum gemeinsamen Auftauchen:

- **Wann sich Themen verknüpfen:** wenn sie im selben Moment erlebt werden,
  egal in welchen Gebieten. Das gilt nicht nur für Emotion und Erfahrung.
- **Wie stark die Bindung ist:** Sie wächst mit jedem gemeinsamen Erleben,
  nach einem Mal auf 0,5, nach zweien auf 0,75.
- **Was sie bewirkt:** Jedes Thema bekommt die Hälfte der Stärke seines
  Partners, mal die Bindung, dazu. Das zieht auch ein Thema mit, das sonst
  verklungen wäre. Im AUI wird dadurch nichts dauerhaft verstärkt.
- **Ab wann:** ab dem Moment nach dem gemeinsamen Erleben.

Zur Kapazität der MBI:

- **Wie groß sie ist:** so groß wie ein Thema in voller Stärke (1,0). Erreicht
  das Gewicht aller Gebiete diesen Wert, wird verdrängt.
- **Was ein Gebiet wiegt:** so viel, wie sein eigenes Thema stark ist. Ein
  Gebiet ohne eigenes Thema, etwa Familie oder die Sinne, wiegt so viel wie
  das stärkste Thema darin, das die MBI nicht schon als eigenes Gebiet hält.
- **Wer verdrängt wird:** zuerst das schwächste Gebiet, dann das nächste, bis
  der Rest hineinpasst. Ein einzelnes Gebiet bleibt immer. Was die MBI in
  diesem Moment erst betreten hat, wird nicht verdrängt.
- **Wohin das Verdrängte geht:** Es liegt wie jede verlassene Haltung im AUI
  und kann von dort wieder auftauchen.

Zu den Erinnerungen:

- **Die Erinnerung ist ein einziges Gebiet** neben den Sinnen und der
  jetzigen Erfahrung, nicht ein eigenes Gebiet pro Erinnerung. Die MBI
  aktiviert Erinnerungen, indem sie ihr Thema dorthin wechselt.
- **Was zur Erinnerung gehört:** jede frühere Erfahrung im AUI, egal aus
  welchem Gebiet sie stammt. In der Erinnerung zählt sie voll und unverblasst.
  Was gerade erst erlebt wird, ist noch keine Erinnerung.
- **Die Erinnerung verstärkt nichts:** Verlässt die MBI sie wieder, ist alles
  so verblasst wie zuvor. Festhalten kann sie etwas nur durch engage.

Zur Haltung:

- **Wann das AUI eine Haltung enthält:** wenn es Erfahrungen enthält, die in
  dieser Haltung gemacht wurden. Jede Erfahrung trägt die Haltung in sich, in
  der die MBI dabei war.
- **Wie stark eine frühere Haltung auftaucht:** so stark wie das stärkste
  Thema, das sie enthält. Ist das stark genug, taucht sie neben den Themen im
  Feld der ABI auf.
- **Welche Haltungen auftauchen:** nur Themengebiete, und nur solche, in denen
  die MBI gerade nicht ist. Die Sinne, die jetzige Erfahrung und die
  Erinnerung tauchen nicht als frühere Haltung auf.
- **Nur die MBI erschafft eine Haltung:** Eine frühere Haltung, die auftaucht,
  wird nicht von selbst zum Gebiet. Dafür muss die MBI darauf engagen.

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
  jetzigen Gebieten zählen voll. Erfahrungen aus anderen Gebieten kommen
  abgeschwächt mit, je nach Einfluss der jetzigen Gebiete.
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
