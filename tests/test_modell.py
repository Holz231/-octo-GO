from geist import Entscheidung, Erfahrung, Geist, Haltung, Quelle, Unterbewusstsein

GEBIET = "Alltag"


def nichts(lage):
    return Entscheidung()


def immer(haltung, thema="Thema"):
    return lambda lage: Entscheidung({thema: haltung})


def nach_plan(plan):
    """Entscheider, der pro Moment die Entscheidung aus `plan` nimmt."""
    momente = iter(range(10**6))
    return lambda lage: plan.get(next(momente), Entscheidung())


def geist_mit(entscheider=nichts, gebiet=GEBIET, **kwargs):
    return Geist(entscheider, gebiet, **kwargs)


def erfahrung(thema, staerke, gebiet=GEBIET, zeit=0):
    return Erfahrung(thema, staerke, zeit, gebiet)


def staerke(moment, thema):
    return next((i.staerke for i in moment.aui_feld if i.thema == thema), 0.0)


def im_feld(moment):
    return [i.thema for i in moment.abi_feld]


# --- AUI: Impulse aus Erfahrungen ---


def test_ohne_erfahrung_kein_impuls():
    assert geist_mit().schritt().aui_feld == ()


def test_impulse_entstehen_aus_vorherigen_und_jetzigen_erfahrungen():
    geist = geist_mit()
    geist.unterbewusstsein.erlebe(erfahrung("Frueher", 0.6))
    moment = geist.schritt({"Jetzt": 0.6})
    assert {i.thema for i in moment.aui_feld} == {"Frueher", "Jetzt"}


def test_erfahrungen_klingen_nach_und_werden_schwaecher():
    unterbewusstsein = Unterbewusstsein(nachklang=0.5)
    unterbewusstsein.erlebe(erfahrung("Thema", 0.8))
    assert unterbewusstsein.erzeuge_impulse(zeit=0, gebiet=GEBIET)[0].staerke == 0.8
    assert unterbewusstsein.erzeuge_impulse(zeit=1, gebiet=GEBIET)[0].staerke == 0.4


# --- AUI und ABI: zwei angrenzende Felder ---


def test_aui_und_abi_sind_zwei_felder():
    geist = geist_mit(schwelle=0.3)
    geist.schritt({"Stark": 0.9, "Schwach": 0.1})
    assert [i.thema for i in geist.unterbewusstsein.feld] == ["Stark", "Schwach"]
    assert [i.thema for i in geist.automatisch.feld] == ["Stark"]


def test_nur_ein_teil_taucht_im_feld_der_abi_auf():
    moment = geist_mit(schwelle=0.3).schritt({"Stark": 0.9, "Schwach": 0.1})
    assert im_feld(moment) == ["Stark"]
    assert {i.thema for i in moment.aui_feld} == {"Stark", "Schwach"}


# --- MBI: was sie sieht und worauf sie sich richtet ---


def test_mbi_sieht_abi_feld_und_sinne_aber_nicht_das_aui_feld():
    lagen = []

    def entscheider(lage):
        lagen.append(lage)
        return Entscheidung()

    geist = geist_mit(entscheider, schwelle=0.3)
    geist.unterbewusstsein.erlebe(erfahrung("Verborgen", 0.1))
    geist.schritt({"Laut": 0.9, "Leise": 0.1})

    (lage,) = lagen
    assert lage.gebiet == GEBIET
    assert [i.thema for i in lage.abi_feld] == ["Laut"]
    assert dict(lage.sinne) == {"Laut": 0.9, "Leise": 0.1}
    assert lage.staerke("Verborgen") == 0.0


def test_quelle_der_ausrichtung():
    def entscheider(lage):
        themen = ("Gedanke", "Geraeusch", "Beliebig")
        return Entscheidung({t: Haltung.ENGAGE for t in themen})

    geist = geist_mit(entscheider)
    geist.unterbewusstsein.erlebe(erfahrung("Gedanke", 0.8))
    moment = geist.schritt({"Geraeusch": 0.1})

    assert {a.thema: a.quelle for a in moment.ausrichtungen} == {
        "Gedanke": Quelle.ERFAHRUNG,
        "Geraeusch": Quelle.SINNE,
        "Beliebig": Quelle.THEMENGEBIET,
    }


# --- Haltungen wirken nur indirekt, als Erfahrung ---


def test_ohne_ausrichtung_bleibt_keine_spur():
    geist = geist_mit()
    geist.schritt({"Thema": 0.9})
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_weder_noch_hinterlaesst_keine_spur():
    geist = geist_mit(immer(Haltung.WEDER_NOCH))
    geist.schritt({"Thema": 0.9})
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_haltung_wirkt_ueber_erfahrung_auf_spaetere_impulse():
    verlauf = {}
    for haltung in Haltung:
        geist = geist_mit(immer(haltung))
        geist.schritt({"Thema": 0.8})
        verlauf[haltung] = staerke(geist.schritt(), "Thema")

    assert verlauf[Haltung.ENGAGE] > verlauf[Haltung.WEDER_NOCH] > verlauf[Haltung.DISENGAGE]


def test_frei_gewaehltes_thema_taucht_erst_danach_im_feld_auf():
    geist = geist_mit(immer(Haltung.ENGAGE, "Urlaub"))
    assert im_feld(geist.schritt()) == []
    assert im_feld(geist.schritt()) == ["Urlaub"]


def test_schwacher_sinneseindruck_kommt_durch_engage_ins_feld():
    ohne = geist_mit()
    mit = geist_mit(immer(Haltung.ENGAGE, "Atem"))
    for geist in (ohne, mit):
        geist.schritt({"Atem": 0.05})

    assert im_feld(ohne.schritt({"Atem": 0.05})) == []
    assert im_feld(mit.schritt({"Atem": 0.05})) == ["Atem"]


def test_disengage_von_nicht_wahrnehmbarem_tut_nichts():
    geist = geist_mit(immer(Haltung.DISENGAGE, "Nirgends"))
    geist.schritt()
    assert geist.unterbewusstsein.erfahrungen == []


def test_disengagtes_verschwindet_aus_dem_feld():
    geist = geist_mit(immer(Haltung.DISENGAGE), schwelle=0.3)
    geist.schritt({"Thema": 0.8})
    momente = [geist.schritt() for _ in range(5)]
    assert momente[-1].abi_feld == ()
    assert staerke(momente[-1], "Thema") == 0.0


# --- Themengebiet: die MBI bewegt sich, AUI und ABI orientieren sich daran ---


def test_mbi_bewegt_sich_immer_in_einem_gebiet_und_kann_wechseln():
    geist = geist_mit(nach_plan({0: Entscheidung(gebiet="Arbeit")}), "Familie")
    erster, zweiter = geist.schritt(), geist.schritt()

    assert (erster.gebiet, erster.wechsel_nach) == ("Familie", "Arbeit")
    assert (zweiter.gebiet, zweiter.wechsel_nach) == ("Arbeit", None)


def test_erfahrungen_gehoeren_zum_gebiet_in_dem_sie_gemacht_wurden():
    geist = geist_mit(immer(Haltung.ENGAGE, "Mail"), "Arbeit")
    geist.schritt({"Mail": 0.5})
    assert {e.gebiet for e in geist.unterbewusstsein.erfahrungen} == {"Arbeit"}


def test_aui_orientiert_sich_am_gebiet_der_mbi():
    unterbewusstsein = Unterbewusstsein(mitnahme=0.5)
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, gebiet="Familie"))

    (daheim,) = unterbewusstsein.erzeuge_impulse(zeit=0, gebiet="Familie")
    (woanders,) = unterbewusstsein.erzeuge_impulse(zeit=0, gebiet="Arbeit")

    assert (daheim.staerke, daheim.mitgebracht_aus) == (0.8, ())
    assert (woanders.staerke, woanders.mitgebracht_aus) == (0.4, ("Familie",))


def test_aui_fuehrt_vergangene_themen_mit_in_neue_gebiete():
    geist = geist_mit(nach_plan({0: Entscheidung(gebiet="Arbeit")}), "Familie")
    geist.unterbewusstsein.erlebe(erfahrung("Sorge", 1.0, gebiet="Familie"))
    geist.schritt()
    moment = geist.schritt()

    (sorge,) = moment.abi_feld
    assert moment.gebiet == "Arbeit"
    assert (sorge.thema, sorge.mitgebracht_aus) == ("Sorge", ("Familie",))


def test_zurueck_im_alten_gebiet_zaehlt_das_thema_wieder_voll():
    plan = {0: Entscheidung(gebiet="Arbeit"), 1: Entscheidung(gebiet="Familie")}
    geist = geist_mit(nach_plan(plan), "Familie", nachklang=1.0)
    geist.unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, gebiet="Familie"))

    verlauf = [staerke(geist.schritt(), "Sorge") for _ in range(3)]
    assert verlauf == [0.8, 0.4, 0.8]


def test_mbi_und_aui_formen_zusammen_die_wahrgenommene_realitaet():
    def wahrgenommen(gebiet_der_mbi, erfahrungen):
        geist = geist_mit(gebiet=gebiet_der_mbi, schwelle=0.3)
        for e in erfahrungen:
            geist.unterbewusstsein.erlebe(e)
        return im_feld(geist.schritt())

    aui = [erfahrung("Sorge", 0.5, "Familie"), erfahrung("Mail", 0.5, "Arbeit")]

    # Gleiches AUI, andere MBI: andere Realität.
    assert wahrgenommen("Familie", aui) == ["Sorge"]
    assert wahrgenommen("Arbeit", aui) == ["Mail"]
    # Gleiche MBI, anderes AUI: andere Realität.
    assert wahrgenommen("Arbeit", aui[:1]) == []
