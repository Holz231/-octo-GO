from geist import Erfahrung, Geist, Haltung, Quelle, Unterbewusstsein


def nichts(lage):
    return {}


def immer(haltung, thema="Thema"):
    return lambda lage: {thema: haltung}


def staerke(moment, thema):
    return next((i.staerke for i in moment.aui_feld if i.thema == thema), 0.0)


def im_feld(moment):
    return [i.thema for i in moment.abi_feld]


def test_ohne_erfahrung_kein_impuls():
    assert Geist(nichts).schritt().aui_feld == ()


def test_impulse_entstehen_aus_vorherigen_und_jetzigen_erfahrungen():
    geist = Geist(nichts)
    geist.unterbewusstsein.erlebe(Erfahrung("Frueher", 0.6, zeit=0))
    moment = geist.schritt({"Jetzt": 0.6})
    assert {i.thema for i in moment.aui_feld} == {"Frueher", "Jetzt"}


def test_erfahrungen_klingen_nach_und_werden_schwaecher():
    unterbewusstsein = Unterbewusstsein(nachklang=0.5)
    unterbewusstsein.erlebe(Erfahrung("Thema", 0.8, zeit=0))
    assert unterbewusstsein.erzeuge_impulse(zeit=0)[0].staerke == 0.8
    assert unterbewusstsein.erzeuge_impulse(zeit=1)[0].staerke == 0.4


def test_aui_und_abi_sind_zwei_felder():
    geist = Geist(nichts, schwelle=0.3)
    geist.schritt({"Stark": 0.9, "Schwach": 0.1})
    assert [i.thema for i in geist.unterbewusstsein.feld] == ["Stark", "Schwach"]
    assert [i.thema for i in geist.automatisch.feld] == ["Stark"]


def test_nur_ein_teil_taucht_im_feld_auf():
    geist = Geist(nichts, schwelle=0.3)
    moment = geist.schritt({"Stark": 0.9, "Schwach": 0.1})
    assert im_feld(moment) == ["Stark"]
    assert {i.thema for i in moment.aui_feld} == {"Stark", "Schwach"}


def test_mbi_sieht_feld_und_sinne_aber_nicht_das_unterbewusstsein():
    lagen = []

    def entscheider(lage):
        lagen.append(lage)
        return {}

    geist = Geist(entscheider, schwelle=0.3)
    geist.unterbewusstsein.erlebe(Erfahrung("Verborgen", 0.1, zeit=0))
    geist.schritt({"Laut": 0.9, "Leise": 0.1})

    (lage,) = lagen
    assert [i.thema for i in lage.abi_feld] == ["Laut"]
    assert dict(lage.sinne) == {"Laut": 0.9, "Leise": 0.1}
    assert lage.staerke("Verborgen") == 0.0


def test_quelle_der_ausrichtung():
    def entscheider(lage):
        return {t: Haltung.ENGAGE for t in ("Gedanke", "Geraeusch", "Beliebig")}

    geist = Geist(entscheider)
    geist.unterbewusstsein.erlebe(Erfahrung("Gedanke", 0.8, zeit=0))
    moment = geist.schritt({"Geraeusch": 0.1})

    assert {a.thema: a.quelle for a in moment.ausrichtungen} == {
        "Gedanke": Quelle.ERFAHRUNG,
        "Geraeusch": Quelle.SINNE,
        "Beliebig": Quelle.THEMENGEBIET,
    }


def test_ohne_ausrichtung_bleibt_keine_spur():
    geist = Geist(nichts)
    geist.schritt({"Thema": 0.9})
    assert len(geist.unterbewusstsein.erfahrungen) == 1


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


def test_frei_gewaehltes_thema_taucht_erst_danach_im_feld_auf():
    geist = Geist(immer(Haltung.ENGAGE, "Urlaub"))
    assert im_feld(geist.schritt()) == []
    assert im_feld(geist.schritt()) == ["Urlaub"]


def test_schwacher_sinneseindruck_kommt_durch_engage_ins_feld():
    ohne = Geist(nichts)
    mit = Geist(immer(Haltung.ENGAGE, "Atem"))
    for geist in (ohne, mit):
        geist.schritt({"Atem": 0.05})

    assert im_feld(ohne.schritt({"Atem": 0.05})) == []
    assert im_feld(mit.schritt({"Atem": 0.05})) == ["Atem"]


def test_disengage_von_nicht_wahrnehmbarem_tut_nichts():
    geist = Geist(immer(Haltung.DISENGAGE, "Nirgends"))
    geist.schritt()
    assert geist.unterbewusstsein.erfahrungen == []


def test_disengagtes_verschwindet_aus_dem_feld():
    geist = Geist(immer(Haltung.DISENGAGE), schwelle=0.3)
    geist.schritt({"Thema": 0.8})
    momente = [geist.schritt() for _ in range(5)]
    assert momente[-1].abi_feld == ()
    assert staerke(momente[-1], "Thema") == 0.0
