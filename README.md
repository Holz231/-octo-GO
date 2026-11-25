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
    python -m geist --demo heilsam     # wie Abneigung die Haltung unheilsam macht
    python -m geist --demo sog         # wie etwas zu Starkes die MBI mitreißt
    python -m geist --demo zufall      # wie der Gesamtzustand die Wahrscheinlichkeiten verschiebt
    python -m geist                    # interaktiv: du bist die MBI
    python -m pytest                   # Tests

Braucht nur Python 3.10 oder neuer, für die Tests zusätzlich pytest.

## Im Browser

`web/index.html` ist dieselbe Simulation zum Anklicken, gedacht für Übende: Man
sieht die beiden Felder, die eigene Haltung und den Verlauf und wählt in jedem
Moment, wie man mit dem umgeht, was auftaucht. `web/geist.js` ist das Modell
dafür, eine Übertragung von `geist/modell.py`. `tests/test_web.py` spielt
zufällige Abläufe in beiden Fassungen durch und vergleicht jeden Moment; der
Test braucht Node und wird ohne übersprungen.

Die Seite ist als Inhalt ohne `<html>`-Gerüst geschrieben, so wie sie als
Artifact veröffentlicht wird.

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

15. Es gibt ein Spektrum von heilsam zu unheilsam. Themengebiete sind weder
    heilsam noch unheilsam: Es ist die Haltung, die die MBI einnimmt. Welche
    sie einnimmt, kann durch das beeinflusst werden, was aus dem AUI in die
    ABI steigt.
16. Unheilsam wird die Haltung, wenn die MBI aus Verlangen oder Abneigung
    agiert, also negativ engaged oder disengaged. Das ist auch gemeint, wenn
    sie auf Dinge aus dem AUI in der ABI reagiert.
17. Heilsam wird die Haltung durch engage ohne Verlangen und durch autonomes
    Ausrichten.
18. Je unheilsamer die Haltung, desto mehr negative Impulse: Ihre Frequenz im
    AUI ist erhöht, und die Chance auf heilsame ist geringer. Je heilsamer,
    desto weniger Impulse des AUI und desto höher die Chance auf heilsame.
19. Negativ oder heilsam wird ein einzelner Impuls durch den Umgang der MBI
    mit seinem Thema: negativ durch Verlangen oder Abneigung, heilsam ohne
    beides. Es ist also gelernt.
20. Ein negativer Impuls in der ABI verschiebt die Haltung noch nicht. Das
    geschieht erst, wenn die MBI aus Verlangen reagiert. Dazu kommt es, wenn
    etwas aus dem AUI in der ABI zu stark wird, sodass die MBI sich darauf
    richtet.
21. Je unheilsamer, also leidvoller, der Gesamtzustand ist, desto schwerer
    oder unwahrscheinlicher ist es, dass die MBI sich nicht beeinflussen lässt.
22. Es gibt auch eine Zufälligkeitsvariable: eine Wahrscheinlichkeit, auch im
    AUI, die je nach Stärke des Gesamtzustands von heilsam zu unheilsam jeweils
    erhöht ist. Selbst in den Extremen gibt es noch eine Chance für
    gegensätzliche Impulse aus dem AUI.

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

Zum Spektrum von heilsam zu unheilsam:

- **Wie die Haltung sich verschiebt:** um ein Fünftel des Wegs je Handlung.
  Nach fünf Handlungen aus Verlangen oder Abneigung ist sie ganz unheilsam.
- **Disengage ohne Abneigung** ist heilsam wie engage ohne Verlangen.
- **Themenerhalt** zählt nur dann als autonomes Ausrichten, wenn sich die MBI
  ausdrücklich auf das Gebiet richtet, in dem sie schon ist. Bloßes Nichtstun
  und weder noch verschieben die Haltung nicht.
- **Die Haltung klingt nicht von selbst ab.** Sie bleibt, wo sie ist, bis die
  MBI wieder handelt, und sie geht mit der MBI in jedes neue Gebiet.
- **Verlangen und Abneigung wirken auf das Thema wie engage und disengage:**
  Sie verstärken oder schwächen es im AUI gleich stark, zählen gleich für die
  Gewohnheit und machen es genauso zum Themengebiet.
- **Häufigkeit und Chance sind als Stärke umgesetzt.** Bei ganz unheilsamer
  Haltung sind negative Impulse um die Hälfte stärker und heilsame um die
  Hälfte schwächer. Bei ganz heilsamer Haltung sind alle Impulse halb so
  stark, heilsame davon am wenigsten geschwächt.
- **Wie negativ oder heilsam ein Thema ist,** wächst mit jedem Umgang in
  dieselbe Richtung, nach einem Mal auf die Hälfte, nach zweien auf drei
  Viertel. Umgang in die andere Richtung hebt es wieder auf.
- **Der Gesamtzustand** ist im Programm die Haltung der MBI.
- **Mitgerissen werden ist eine Wahrscheinlichkeit.** In der Mitte zwischen
  heilsam und unheilsam ist sie am höchsten, wenn etwas allein die Kapazität
  der MBI füllt, also bei voller Stärke. Darunter sinkt sie: bei Stärke 0,9 auf
  60 %, bei 0,8 auf 20 %, ab 0,75 auf null.
- **Wie der Gesamtzustand das verschiebt:** Bei ganz unheilsamer Haltung reicht
  schon die halbe Stärke für die höchste Wahrscheinlichkeit. Bei heilsam 20 %
  liegt sie selbst bei voller Stärke nur noch bei 60 %.
- **Restchance in beide Richtungen:** Sicher ist nichts. Die Wahrscheinlichkeit
  steigt nie über 95 %, auch nicht im ganz Unheilsamen. Und sie fällt für
  alles, was die MBI in der Mitte mitreißen könnte, nie unter 5 %, auch nicht
  im ganz Heilsamen. Was schon in der Mitte zu schwach wäre, reißt in
  heilsamer Haltung nie mit.
- **Was sicher davor bewahrt:** nur, im selben Moment selbst zu dem Thema zu
  engagen oder zu disengagen. Weder noch und ein Themenwechsel schützen
  nicht, sie lassen den Zufall entscheiden.
- **Es ist immer Verlangen.** Dass die MBI von etwas zu Starkem aus Abneigung
  weggerissen wird, gibt es im Programm nicht.
- **In den Demo-Läufen** außer `sog` ist das Mitreißen abgeschaltet. Der Lauf
  `sog` verwendet einen festen Zufall, damit er jedes Mal gleich abläuft.

Zum Zufall im AUI:

- **Was der Zufall dort tut:** In jedem Moment kann jedes Thema, das das AUI
  kennt, von selbst wieder aufkommen. In der Mitte zwischen heilsam und
  unheilsam liegt die Wahrscheinlichkeit dafür bei 5 % je Thema und Moment.
- **Wie der Gesamtzustand sie verschiebt:** Bei ganz unheilsamer Haltung kommt
  ein ganz negatives Thema viermal so oft auf und ein ganz heilsames ein
  Viertel so oft. Bei ganz heilsamer Haltung kommt ein heilsames doppelt so
  oft auf, ein neutrales halb so oft und ein negatives ein Achtel so oft. Auf
  null fällt die Wahrscheinlichkeit nie.
- **Was aufkommt, ist eine neue Erfahrung** mittlerer Stärke (0,3) in dem
  Gebiet, in dem das Thema am stärksten erlebt wurde. Sie klingt ab wie jede
  andere und zählt wie jede andere.
- **Zusätzlich zur Stärke:** Der Gesamtzustand verändert weiterhin auch die
  Stärke der Impulse (siehe oben). Der Zufall kommt hinzu, er ersetzt das nicht.
- **In den Demo-Läufen** außer `zufall` ist das Aufkommen abgeschaltet.

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
  und außer in `heilsam` bleibt die Haltung in der Mitte zwischen heilsam und
  unheilsam, damit jeder Lauf nur seinen eigenen Punkt zeigt.

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

- **Wie groß die Chance ist:** in der Mitte zwischen heilsam und unheilsam
  25 Prozent pro Moment, für jedes Thema im Feld der ABI, zu dem die MBI weder
  noch hält.
- **Sie hängt am Gesamtzustand,** genauso wie das Aufkommen im AUI: Im ganz
  Unheilsamen wird ein negatives Thema viermal so wahrscheinlich von selbst zum
  Themengebiet und ein heilsames ein Viertel so wahrscheinlich. Im ganz
  Heilsamen ist es umgekehrt, und insgesamt halb so wahrscheinlich.
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
