from geist import Erfahrung, Geist, Haltung, Unterbewusstsein


def immer(haltung):
    return lambda impuls: haltung


def staerke(moment, thema):
    return next((i.staerke for i in moment.impulse if i.thema == thema), 0.0)


def test_ohne_erfahrung_kein_impuls():
    assert Geist(immer(Haltung.WEDER_NOCH)).schritt().impulse == ()


def test_impulse_entstehen_aus_vorherigen_und_jetzigen_erfahrungen():
    geist = Geist(immer(Haltung.WEDER_NOCH))
    geist.unterbewusstsein.erlebe(Erfahrung("Frueher", 0.6, zeit=0))
    moment = geist.schritt({"Jetzt": 0.6})
    assert {i.thema for i in moment.impulse} == {"Frueher", "Jetzt"}


def test_erfahrungen_klingen_nach_und_werden_schwaecher():
    unterbewusstsein = Unterbewusstsein(nachklang=0.5)
    unterbewusstsein.erlebe(Erfahrung("Thema", 0.8, zeit=0))
    assert unterbewusstsein.erzeuge_impulse(zeit=0)[0].staerke == 0.8
    assert unterbewusstsein.erzeuge_impulse(zeit=1)[0].staerke == 0.4


def test_nur_ein_teil_steigt_auf():
    geist = Geist(immer(Haltung.WEDER_NOCH), schwelle=0.3)
    moment = geist.schritt({"Stark": 0.9, "Schwach": 0.1})
    assert [i.thema for i in moment.aufgestiegen] == ["Stark"]
    assert {i.thema for i in moment.impulse} == {"Stark", "Schwach"}


def test_manuelle_intention_sieht_nur_aufgestiegenes():
    gesehen = []

    def entscheider(impuls):
        gesehen.append(impuls.thema)
        return Haltung.DISENGAGE

    geist = Geist(entscheider, schwelle=0.3)
    moment = geist.schritt({"Stark": 0.9, "Schwach": 0.1})

    assert gesehen == ["Stark"]
    assert moment.haltungen == {"Stark": Haltung.DISENGAGE}
    # Das Unbewusste bleibt von der manuellen Intention unberuehrt.
    assert [e.thema for e in geist.unterbewusstsein.erfahrungen].count("Schwach") == 1


def test_weder_noch_hinterlaesst_keine_spur():
    geist = Geist(immer(Haltung.WEDER_NOCH))
    geist.schritt({"Thema": 0.9})
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_haltung_wirkt_ueber_erfahrung_auf_spaetere_impulse():
    verlauf = {}
    for haltung in Haltung:
        geist = Geist(immer(haltung))
        geist.schritt({"Thema": 0.8})
        verlauf[haltung] = staerke(geist.schritt(), "Thema")

    assert verlauf[Haltung.ENGAGE] > verlauf[Haltung.WEDER_NOCH] > verlauf[Haltung.DISENGAGE]


def test_disengagtes_sinkt_unter_die_schwelle_und_ist_dann_nicht_mehr_lenkbar():
    geist = Geist(immer(Haltung.DISENGAGE), schwelle=0.3)
    geist.schritt({"Thema": 0.8})
    momente = [geist.schritt() for _ in range(5)]
    assert momente[-1].aufgestiegen == ()
    assert momente[-1].haltungen == {}
