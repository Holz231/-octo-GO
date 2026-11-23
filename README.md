# Geistmodell (Arbeitstitel)

Ein Programm, das ein Modell des Geistes abbildet: seine fundamentalen
Eigenschaften, deren Funktionen und die Dynamiken und Beziehungen zwischen ihnen.

Stand: Der Kern läuft. Diese Datei hält fest, was im Modell feststeht und
welche Lücken das Programm vorläufig mit eigenen Annahmen füllt.

## Ausprobieren

    python -m geist --demo   # fester Ablauf: die drei Haltungen im Vergleich
    python -m geist          # interaktiv: du bist die manuelle bewusste Intention
    python -m pytest         # Tests

Braucht nur Python 3.10 oder neuer, für die Tests zusätzlich pytest.

## 1. Fundamentale Layer des Geistes

| Layer | Steuerung | Bewusstheit |
|---|---|---|
| Automatische bewusste Intention | automatisch | bewusst |
| Automatisches Unterbewusstsein | automatisch | unbewusst |
| Manuelle bewusste Intention | manuell | bewusst |

Festgelegt:

- Die Kombination „manuell + unbewusst“ gibt es im Modell bewusst nicht.
- Die automatische bewusste Intention ist das, was von selbst ins Bewusstsein
  tritt (Impulse, spontane Gedanken, Wünsche). Die manuelle bewusste Intention
  ist das, was man willentlich lenkt.

## 2. Funktionen und Beziehungen

Festgelegt:

1. Das Unterbewusstsein läuft ständig im Hintergrund und erzeugt Impulse,
   Gedanken und Wünsche, und zwar aufgrund von vorherigen und jetzigen
   Erfahrungen.
2. Ein Teil davon steigt auf und wird zur automatischen bewussten Intention.
   Sie ist das Fenster, durch das das Unterbewusstsein sichtbar wird.
3. Die manuelle bewusste Intention nimmt zu dem, was aufgestiegen ist, eine von
   drei Haltungen ein: **engage**, **disengage** oder **weder noch**
   („non disengage and non engage“).
4. Die manuelle Intention hat keinen direkten Zugriff auf das Unterbewusstsein.
   Sie erreicht es nur indirekt über die automatische bewusste Intention.

Bewusst zurückgestellt: Grenzen der manuellen Intention (Aufmerksamkeit,
Energie), Gewohnheitsbildung, weitere Bausteine wie Wahrnehmung, Emotion,
Erinnerung oder Körper.

## 3. Vorläufige Annahmen im Programm

Diese Punkte gibt das Modell noch nicht vor. Das Programm braucht sie aber, um
zu laufen. Sie stehen in `geist/modell.py` und sind dort mit `ANNAHME` markiert.

- **Was eine Haltung bewirkt:** Die Haltung wird selbst zur Erfahrung und wirkt
  so auf spätere Impulse zurück. Engage stärkt das Thema, disengage schwächt
  es, weder noch hinterlässt keine Spur.
- **Welcher Teil aufsteigt:** alles, was mindestens so stark ist wie eine feste
  Schwelle (0,3).
- **Wie Erfahrungen nachwirken:** Jede Erfahrung klingt pro Moment um den
  Faktor 0,8 ab.
- **Themen:** Erfahrungen und Impulse haben ein Thema (ein Wort) und eine
  Stärke zwischen 0 und 1.
