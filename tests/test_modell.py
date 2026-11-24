from geist import (
    JETZIGE_ERFAHRUNG,
    SINNE,
    Entscheidung,
    Erfahrung,
    Geist,
    Haltung,
    Unterbewusstsein,
)

GEBIET = "Alltag"


def nichts(lage):
    return Entscheidung()


def immer(haltung, thema="Thema"):
    return lambda lage: Entscheidung({thema: haltung})


def nach_plan(plan):
    """Entscheider, der pro Moment die Entscheidung aus `plan` nimmt."""
    momente = iter(range(10**6))
    return lambda lage: plan.get(next(momente), Entscheidung())


def geist_mit(entscheider=nichts, gebiet=GEBIET, erfahrungen=(), **kwargs):
    geist = Geist(entscheider, gebiet, **kwargs)
    for e in erfahrungen:
        geist.unterbewusstsein.erlebe(e)
    return geist


def erfahrung(thema, staerke, gebiet=GEBIET, zeit=0):
    return Erfahrung(thema, staerke, zeit, gebiet)


def staerke(moment, thema):
    return next((i.staerke for i in moment.aui_feld if i.thema == thema), 0.0)


def im_feld(moment):
    return [i.thema for i in moment.abi_feld]


STARK_UND_SCHWACH = (erfahrung("Stark", 0.9), erfahrung("Schwach", 0.1))


# --- AUI: Impulse aus Erfahrungen ---


def test_ohne_erfahrung_kein_impuls():
    assert geist_mit().schritt().aui_feld == ()


def test_impulse_entstehen_aus_vorherigen_und_jetzigen_erfahrungen():
    geist = geist_mit(erfahrungen=[erfahrung("Frueher", 0.6)])
    moment = geist.schritt({"Jetzt": 0.6})
    assert {i.thema for i in moment.aui_feld} == {"Frueher", "Jetzt"}


def test_erfahrungen_klingen_nach_und_werden_schwaecher():
    unterbewusstsein = Unterbewusstsein(nachklang=0.5)
    unterbewusstsein.erlebe(erfahrung("Thema", 0.8))
    assert unterbewusstsein.erzeuge_impulse(zeit=0, gebiet=GEBIET)[0].staerke == 0.8
    assert unterbewusstsein.erzeuge_impulse(zeit=1, gebiet=GEBIET)[0].staerke == 0.4


# --- AUI und ABI: zwei angrenzende Felder ---


def test_aui_und_abi_sind_zwei_felder():
    geist = geist_mit(erfahrungen=STARK_UND_SCHWACH, schwelle=0.3)
    geist.schritt()
    assert [i.thema for i in geist.unterbewusstsein.feld] == ["Stark", "Schwach"]
    assert [i.thema for i in geist.automatisch.feld] == ["Stark"]


def test_nur_ein_teil_taucht_im_feld_der_abi_auf():
    moment = geist_mit(erfahrungen=STARK_UND_SCHWACH, schwelle=0.3).schritt()
    assert im_feld(moment) == ["Stark"]
    assert {i.thema for i in moment.aui_feld} == {"Stark", "Schwach"}


# --- MBI: was sie sieht ---


def test_mbi_sieht_abi_feld_und_sinne_aber_nicht_das_aui_feld():
    lagen = []

    def entscheider(lage):
        lagen.append(lage)
        return Entscheidung()

    geist = geist_mit(entscheider, SINNE, [erfahrung("Verborgen", 0.1)], schwelle=0.3)
    geist.schritt({"Laut": 0.9, "Leise": 0.1})

    (lage,) = lagen
    assert lage.gebiet == SINNE
    assert [i.thema for i in lage.abi_feld] == ["Laut"]
    assert dict(lage.sinne) == {"Laut": 0.9, "Leise": 0.1}
    assert lage.staerke("Verborgen") == 0.0


# --- Haltungen wirken nur indirekt, als Erfahrung ---


def test_ohne_haltung_bleibt_keine_spur():
    geist = geist_mit(erfahrungen=[erfahrung("Thema", 0.9)])
    geist.schritt()
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_weder_noch_hinterlaesst_keine_spur():
    geist = geist_mit(immer(Haltung.WEDER_NOCH), erfahrungen=[erfahrung("Thema", 0.9)])
    geist.schritt()
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_haltung_wirkt_ueber_erfahrung_auf_spaetere_impulse():
    verlauf = {}
    for haltung in Haltung:
        geist = geist_mit(immer(haltung), erfahrungen=[erfahrung("Thema", 0.8)])
        geist.schritt()
        verlauf[haltung] = staerke(geist.schritt(), "Thema")

    assert verlauf[Haltung.ENGAGE] > verlauf[Haltung.WEDER_NOCH] > verlauf[Haltung.DISENGAGE]


def test_haltung_gehoert_zum_gebiet_in_dem_sich_die_mbi_bewegt():
    geist = geist_mit(immer(Haltung.ENGAGE, "Mail"), "Arbeit")
    geist.schritt()
    assert [(e.thema, e.gebiet) for e in geist.unterbewusstsein.erfahrungen] == [
        ("Mail", "Arbeit")
    ]


def test_frei_gewaehltes_thema_taucht_erst_danach_im_feld_auf():
    geist = geist_mit(immer(Haltung.ENGAGE, "Urlaub"))
    assert im_feld(geist.schritt()) == []
    assert im_feld(geist.schritt()) == ["Urlaub"]


def test_disengage_von_nicht_wahrnehmbarem_tut_nichts():
    geist = geist_mit(immer(Haltung.DISENGAGE, "Nirgends"))
    geist.schritt()
    assert geist.unterbewusstsein.erfahrungen == []


def test_disengagtes_verschwindet_aus_dem_feld():
    geist = geist_mit(
        immer(Haltung.DISENGAGE), erfahrungen=[erfahrung("Thema", 0.8)], schwelle=0.3
    )
    momente = [geist.schritt() for _ in range(6)]
    assert im_feld(momente[0]) == ["Thema"]
    assert momente[-1].abi_feld == ()
    assert staerke(momente[-1], "Thema") == 0.0


# --- Gebiete: die MBI bewegt sich, AUI und ABI orientieren sich daran ---


def test_mbi_bewegt_sich_immer_in_einem_gebiet_und_kann_wechseln():
    geist = geist_mit(nach_plan({0: Entscheidung(gebiet="Arbeit")}), "Familie")
    erster, zweiter = geist.schritt(), geist.schritt()

    assert (erster.gebiet, erster.wechsel_nach) == ("Familie", "Arbeit")
    assert (zweiter.gebiet, zweiter.wechsel_nach) == ("Arbeit", None)


def test_aui_orientiert_sich_am_gebiet_der_mbi():
    unterbewusstsein = Unterbewusstsein(mitnahme=0.5)
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, gebiet="Familie"))

    (daheim,) = unterbewusstsein.erzeuge_impulse(zeit=0, gebiet="Familie")
    (woanders,) = unterbewusstsein.erzeuge_impulse(zeit=0, gebiet="Arbeit")

    assert (daheim.staerke, daheim.mitgebracht_aus) == (0.8, ())
    assert (woanders.staerke, woanders.mitgebracht_aus) == (0.4, ("Familie",))


def test_aui_fuehrt_vergangene_themen_mit_in_neue_gebiete():
    geist = geist_mit(
        nach_plan({0: Entscheidung(gebiet="Arbeit")}),
        "Familie",
        [erfahrung("Sorge", 1.0, gebiet="Familie")],
    )
    geist.schritt()
    moment = geist.schritt()

    (sorge,) = moment.abi_feld
    assert moment.gebiet == "Arbeit"
    assert (sorge.thema, sorge.mitgebracht_aus) == ("Sorge", ("Familie",))


def test_zurueck_im_alten_gebiet_zaehlt_das_thema_wieder_voll():
    plan = {0: Entscheidung(gebiet="Arbeit"), 1: Entscheidung(gebiet="Familie")}
    geist = geist_mit(
        nach_plan(plan),
        "Familie",
        [erfahrung("Sorge", 0.8, gebiet="Familie")],
        nachklang=1.0,
    )
    verlauf = [staerke(geist.schritt(), "Sorge") for _ in range(3)]
    assert verlauf == [0.8, 0.4, 0.8]


def test_mbi_und_aui_formen_zusammen_die_wahrgenommene_realitaet():
    def wahrgenommen(gebiet_der_mbi, erfahrungen):
        return im_feld(geist_mit(gebiet=gebiet_der_mbi, erfahrungen=erfahrungen).schritt())

    aui = [erfahrung("Sorge", 0.5, "Familie"), erfahrung("Mail", 0.5, "Arbeit")]

    # Gleiches AUI, andere MBI: andere Realität.
    assert wahrgenommen("Familie", aui) == ["Sorge"]
    assert wahrgenommen("Arbeit", aui) == ["Mail"]
    # Gleiche MBI, anderes AUI: andere Realität.
    assert wahrgenommen("Arbeit", aui[:1]) == []


# --- Die Sinne als Gebiet ---


def test_sinneseindruecke_gehoeren_zum_gebiet_der_sinne():
    geist = geist_mit(gebiet="Arbeit")
    geist.schritt({"Laerm": 0.5})
    assert [(e.thema, e.gebiet) for e in geist.unterbewusstsein.erfahrungen] == [
        ("Laerm", SINNE)
    ]


def test_in_den_sinnen_zaehlen_sinneseindruecke_voll_sonst_kommen_sie_nur_mit():
    in_den_sinnen = geist_mit(gebiet=SINNE).schritt({"Atem": 0.4})
    im_thema = geist_mit(gebiet="Arbeit").schritt({"Atem": 0.4})

    assert im_feld(in_den_sinnen) == ["Atem"]
    assert im_feld(im_thema) == []
    assert im_thema.aui_feld[0].mitgebracht_aus == (SINNE,)


def test_themen_kommen_abgeschwaecht_mit_in_die_sinne():
    geist = geist_mit(gebiet=SINNE, erfahrungen=[erfahrung("Sorge", 0.8, "Familie")])
    (sorge,) = geist.schritt().aui_feld
    assert (sorge.staerke, sorge.mitgebracht_aus) == (0.4, ("Familie",))


def test_schwacher_sinneseindruck_kommt_durch_engage_ins_feld():
    ohne = geist_mit(gebiet=SINNE)
    mit = geist_mit(immer(Haltung.ENGAGE, "Atem"), SINNE)
    for geist in (ohne, mit):
        geist.schritt({"Atem": 0.05})

    assert im_feld(ohne.schritt({"Atem": 0.05})) == []
    assert im_feld(mit.schritt({"Atem": 0.05})) == ["Atem"]


# --- Die jetzige Erfahrung als Gebiet ---


def test_in_der_jetzigen_erfahrung_zaehlt_voll_was_jetzt_erlebt_wird():
    geist = geist_mit(gebiet=JETZIGE_ERFAHRUNG, nachklang=1.0)

    (jetzt,) = geist.schritt({"Klang": 0.6}).aui_feld
    (danach,) = geist.schritt().aui_feld

    assert (jetzt.staerke, jetzt.mitgebracht_aus) == (0.6, ())
    assert (danach.staerke, danach.mitgebracht_aus) == (0.3, (SINNE,))


def test_in_der_jetzigen_erfahrung_ist_alles_fruehere_mitgebracht():
    geist = geist_mit(
        immer(Haltung.ENGAGE, "Gedanke"),
        JETZIGE_ERFAHRUNG,
        [erfahrung("Sorge", 0.8, "Familie", zeit=-1)],
        nachklang=1.0,
    )
    geist.schritt()
    herkunft = {i.thema: i.mitgebracht_aus for i in geist.schritt().aui_feld}

    assert herkunft == {"Sorge": ("Familie",), "Gedanke": ("früher",)}
