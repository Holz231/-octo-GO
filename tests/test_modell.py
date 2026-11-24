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


def geist_mit(entscheider=nichts, gebiet=GEBIET, erfahrungen=(), chance=0.0, **kwargs):
    """Ein Geist ohne Zufall, solange `chance` nicht gesetzt wird."""
    geist = Geist(entscheider, gebiet, chance=chance, **kwargs)
    for e in erfahrungen:
        geist.unterbewusstsein.erlebe(e)
    return geist


def erfahrung(thema, staerke, gebiet=GEBIET, zeit=0):
    return Erfahrung(thema, staerke, zeit, (gebiet,))


def staerke(moment, thema):
    return next((i.staerke for i in moment.aui_feld if i.thema == thema), 0.0)


def impuls(moment, thema):
    return next(i for i in moment.aui_feld if i.thema == thema)


def im_feld(moment):
    return [i.thema for i in moment.abi_feld]


STARK_UND_SCHWACH = (erfahrung("Stark", 0.9), erfahrung("Schwach", 0.1))
SORGE_AUS_DER_FAMILIE = (erfahrung("Sorge", 0.8, "Familie"),)


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
    assert unterbewusstsein.erzeuge_impulse(0, [GEBIET])[0].staerke == 0.8
    assert unterbewusstsein.erzeuge_impulse(1, [GEBIET])[0].staerke == 0.4


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
    assert lage.gebiete == (SINNE,)
    assert [i.thema for i in lage.abi_feld] == ["Laut"]
    assert dict(lage.sinne) == {"Laut": 0.9, "Leise": 0.1}
    assert lage.staerke("Verborgen") == 0.0


# --- Engage: verstärkt im AUI und macht das Thema zum Themengebiet der MBI ---


def test_engage_verstaerkt_das_thema_im_aui():
    ohne = geist_mit(erfahrungen=[erfahrung("Thema", 0.5)], nachklang=1.0)
    mit = geist_mit(immer(Haltung.ENGAGE), erfahrungen=[erfahrung("Thema", 0.5)], nachklang=1.0)
    for geist in (ohne, mit):
        geist.schritt()

    assert staerke(ohne.schritt(), "Thema") == 0.5
    assert staerke(mit.schritt(), "Thema") == 0.9


def test_engage_macht_das_thema_zum_alleinigen_gebiet_wenn_die_mbi_nur_eines_haelt():
    geist = geist_mit(nach_plan({0: Entscheidung({"Sorge": Haltung.ENGAGE})}), "Arbeit")
    erster, zweiter = geist.schritt(), geist.schritt()

    assert (erster.gebiete, erster.gebiete_danach) == (("Arbeit",), ("Sorge",))
    assert zweiter.gebiete == ("Sorge",)


def test_engage_stellt_das_thema_parallel_wenn_die_mbi_mehrere_haelt():
    geist = geist_mit(immer(Haltung.ENGAGE, "Sorge"), "Arbeit", mehrere=True)
    geist.schritt()
    assert geist.schritt().gebiete == ("Arbeit", "Sorge")


def test_im_eigenen_themengebiet_zaehlt_das_thema_voll():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Haltung.ENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
        nachklang=1.0,
    )
    mitgebracht, eigenes_gebiet = (impuls(geist.schritt(), "Sorge") for _ in range(2))

    assert (mitgebracht.staerke, mitgebracht.mitgebracht_aus) == (0.4, ("Familie",))
    assert (eigenes_gebiet.staerke, eigenes_gebiet.mitgebracht_aus) == (1.0, ())


def test_frei_gewaehltes_thema_taucht_nach_engage_im_feld_auf():
    geist = geist_mit(immer(Haltung.ENGAGE, "Urlaub"))
    assert im_feld(geist.schritt()) == []
    assert im_feld(geist.schritt()) == ["Urlaub"]


def test_engage_gehoert_zu_den_gebieten_in_denen_die_mbi_agiert_hat():
    geist = geist_mit(immer(Haltung.ENGAGE, "Mail"), "Arbeit")
    geist.schritt()
    assert [(e.thema, e.gebiete) for e in geist.unterbewusstsein.erfahrungen] == [
        ("Mail", ("Arbeit",))
    ]


# --- Disengage: schwächt im AUI und verhindert das Themengebiet ---


def test_disengage_schwaecht_das_thema_im_aui():
    geist = geist_mit(
        immer(Haltung.DISENGAGE), erfahrungen=[erfahrung("Thema", 0.8)], nachklang=1.0
    )
    verlauf = [staerke(geist.schritt(), "Thema") for _ in range(3)]
    assert [round(s, 2) for s in verlauf] == [0.8, 0.4, 0.0]


def test_disengage_macht_das_thema_nicht_zum_gebiet():
    geist = geist_mit(immer(Haltung.DISENGAGE, "Sorge"), "Arbeit", SORGE_AUS_DER_FAMILIE)
    assert geist.schritt().gebiete_danach == ("Arbeit",)


def test_disengage_beendet_ein_themengebiet_der_mbi():
    plan = {0: Entscheidung({"Sorge": Haltung.ENGAGE}), 1: Entscheidung({"Sorge": Haltung.DISENGAGE})}
    geist = geist_mit(nach_plan(plan), "Arbeit", mehrere=True)
    verlauf = [geist.schritt().gebiete_danach for _ in range(2)]
    assert verlauf == [("Arbeit", "Sorge"), ("Arbeit",)]


def test_ohne_eigenes_gebiet_bleibt_der_mbi_die_jetzige_erfahrung():
    geist = geist_mit(immer(Haltung.DISENGAGE, "Arbeit"), "Arbeit")
    assert geist.schritt().gebiete_danach == (JETZIGE_ERFAHRUNG,)


def test_disengage_von_nicht_wahrnehmbarem_hinterlaesst_keine_spur():
    geist = geist_mit(immer(Haltung.DISENGAGE, "Nirgends"))
    geist.schritt()
    assert geist.unterbewusstsein.erfahrungen == []


# --- Weder noch: verstärkt nicht, schwächt nicht, lässt aber eine Chance ---


def test_weder_noch_verstaerkt_nicht_und_schwaecht_nicht():
    for entscheider in (nichts, immer(Haltung.WEDER_NOCH)):
        geist = geist_mit(entscheider, erfahrungen=[erfahrung("Thema", 0.9)])
        geist.schritt()
        assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_weder_noch_kann_das_thema_ohne_mbi_zum_themengebiet_machen():
    geist = geist_mit(gebiet="Arbeit", erfahrungen=SORGE_AUS_DER_FAMILIE, chance=1.0)
    moment = geist.schritt()

    assert moment.gebiete_ohne_mbi_danach == ("Sorge",)
    assert moment.gebiete_danach == ("Arbeit",)


def test_oder_eben_nicht():
    geist = geist_mit(gebiet="Arbeit", erfahrungen=SORGE_AUS_DER_FAMILIE, chance=0.0)
    assert geist.schritt().gebiete_ohne_mbi_danach == ()


def test_nur_was_im_abi_feld_auftaucht_kann_von_selbst_zum_gebiet_werden():
    geist = geist_mit(gebiet="Arbeit", erfahrungen=[erfahrung("Leise", 0.2, "Familie")], chance=1.0)
    assert geist.schritt().gebiete_ohne_mbi_danach == ()


def test_engage_und_disengage_lassen_keine_chance():
    for haltung in (Haltung.ENGAGE, Haltung.DISENGAGE):
        geist = geist_mit(immer(haltung, "Sorge"), "Arbeit", SORGE_AUS_DER_FAMILIE, chance=1.0)
        assert geist.schritt().gebiete_ohne_mbi_danach == ()


def test_auch_am_themengebiet_ohne_mbi_orientieren_sich_aui_und_abi():
    geist = geist_mit(
        gebiet="Arbeit", erfahrungen=SORGE_AUS_DER_FAMILIE, chance=1.0, nachklang=1.0
    )
    mitgebracht, als_gebiet = (impuls(geist.schritt(), "Sorge") for _ in range(2))

    assert (mitgebracht.staerke, mitgebracht.mitgebracht_aus) == (0.4, ("Familie",))
    assert (als_gebiet.staerke, als_gebiet.mitgebracht_aus) == (0.8, ())


def test_themengebiet_ohne_mbi_loest_sich_auf_wenn_das_thema_verblasst():
    geist = geist_mit(
        gebiet="Familie", erfahrungen=SORGE_AUS_DER_FAMILIE, chance=1.0, nachklang=0.5
    )
    verlauf = [geist.schritt().gebiete_ohne_mbi_danach for _ in range(3)]
    assert verlauf == [("Sorge",), ("Sorge",), ()]


def test_engage_uebernimmt_ein_themengebiet_das_ohne_mbi_entstanden_ist():
    geist = geist_mit(
        nach_plan({1: Entscheidung({"Sorge": Haltung.ENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
        chance=1.0,
    )
    geist.schritt()
    moment = geist.schritt()

    assert moment.gebiete_ohne_mbi == ("Sorge",)
    assert (moment.gebiete_danach, moment.gebiete_ohne_mbi_danach) == (("Sorge",), ())


def test_disengage_beendet_ein_themengebiet_das_ohne_mbi_entstanden_ist():
    geist = geist_mit(
        nach_plan({1: Entscheidung({"Sorge": Haltung.DISENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
        chance=1.0,
    )
    geist.schritt()
    moment = geist.schritt()

    assert (moment.gebiete_danach, moment.gebiete_ohne_mbi_danach) == (("Arbeit",), ())


# --- Gebiete: die MBI bewegt sich, AUI und ABI orientieren sich daran ---


def test_mbi_kann_sich_auf_ein_gebiet_richten_ohne_etwas_zu_verstaerken():
    geist = geist_mit(nach_plan({0: Entscheidung(gebiet="Arbeit")}), "Familie")
    erster, zweiter = geist.schritt(), geist.schritt()

    assert (erster.gebiete, erster.gebiete_danach) == (("Familie",), ("Arbeit",))
    assert zweiter.gebiete == ("Arbeit",)
    assert geist.unterbewusstsein.erfahrungen == []


def test_richten_stellt_das_gebiet_parallel_wenn_die_mbi_mehrere_haelt():
    geist = geist_mit(nach_plan({0: Entscheidung(gebiet=SINNE)}), "Arbeit", mehrere=True)
    assert geist.schritt().gebiete_danach == ("Arbeit", SINNE)


def test_aui_orientiert_sich_am_gebiet_der_mbi():
    unterbewusstsein = Unterbewusstsein(mitnahme=0.5)
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, gebiet="Familie"))

    (daheim,) = unterbewusstsein.erzeuge_impulse(0, ["Familie"])
    (woanders,) = unterbewusstsein.erzeuge_impulse(0, ["Arbeit"])
    (beides,) = unterbewusstsein.erzeuge_impulse(0, ["Arbeit", "Familie"])

    assert (daheim.staerke, daheim.mitgebracht_aus) == (0.8, ())
    assert (woanders.staerke, woanders.mitgebracht_aus) == (0.4, ("Familie",))
    assert (beides.staerke, beides.mitgebracht_aus) == (0.8, ())


def test_aui_fuehrt_vergangene_themen_mit_in_neue_gebiete():
    geist = geist_mit(
        nach_plan({0: Entscheidung(gebiet="Arbeit")}),
        "Familie",
        [erfahrung("Sorge", 1.0, gebiet="Familie")],
    )
    geist.schritt()
    moment = geist.schritt()

    (sorge,) = moment.abi_feld
    assert moment.gebiete == ("Arbeit",)
    assert (sorge.thema, sorge.mitgebracht_aus) == ("Sorge", ("Familie",))


def test_zurueck_im_alten_gebiet_zaehlt_das_thema_wieder_voll():
    plan = {0: Entscheidung(gebiet="Arbeit"), 1: Entscheidung(gebiet="Familie")}
    geist = geist_mit(nach_plan(plan), "Familie", SORGE_AUS_DER_FAMILIE, nachklang=1.0)
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
    assert [(e.thema, e.gebiete) for e in geist.unterbewusstsein.erfahrungen] == [
        ("Laerm", (SINNE,))
    ]


def test_in_den_sinnen_zaehlen_sinneseindruecke_voll_sonst_kommen_sie_nur_mit():
    in_den_sinnen = geist_mit(gebiet=SINNE).schritt({"Atem": 0.4})
    im_thema = geist_mit(gebiet="Arbeit").schritt({"Atem": 0.4})

    assert im_feld(in_den_sinnen) == ["Atem"]
    assert im_feld(im_thema) == []
    assert im_thema.aui_feld[0].mitgebracht_aus == (SINNE,)


def test_themen_kommen_abgeschwaecht_mit_in_die_sinne():
    geist = geist_mit(gebiet=SINNE, erfahrungen=SORGE_AUS_DER_FAMILIE)
    (sorge,) = geist.schritt().aui_feld
    assert (sorge.staerke, sorge.mitgebracht_aus) == (0.4, ("Familie",))


# --- Die jetzige Erfahrung als Gebiet: alles, was im Feld der ABI auftaucht ---


def test_was_im_abi_feld_auftaucht_zaehlt_in_der_jetzigen_erfahrung_voll():
    plan = {0: Entscheidung(gebiet="Arbeit"), 1: Entscheidung(gebiet=JETZIGE_ERFAHRUNG)}
    geist = geist_mit(nach_plan(plan), "Familie", SORGE_AUS_DER_FAMILIE, nachklang=1.0)
    daheim, in_der_arbeit, jetzt = (geist.schritt().aui_feld[0] for _ in range(3))

    assert (daheim.staerke, daheim.mitgebracht_aus) == (0.8, ())
    assert (in_der_arbeit.staerke, in_der_arbeit.mitgebracht_aus) == (0.4, ("Familie",))
    # Die Sorge taucht im Feld der ABI auf, also gehört sie zur jetzigen Erfahrung.
    assert (jetzt.staerke, jetzt.mitgebracht_aus) == (0.8, ())


def test_was_nicht_im_abi_feld_auftaucht_wird_nur_mitgefuehrt():
    geist = geist_mit(
        gebiet=JETZIGE_ERFAHRUNG,
        erfahrungen=[erfahrung("Leise", 0.4, "Familie")],
        nachklang=1.0,
    )
    for _ in range(2):
        moment = geist.schritt()
        (leise,) = moment.aui_feld
        assert moment.abi_feld == ()
        assert (leise.staerke, leise.mitgebracht_aus) == (0.2, ("Familie",))


def test_was_aus_dem_abi_feld_verschwindet_zaehlt_nicht_mehr_voll():
    geist = geist_mit(
        nach_plan({0: Entscheidung(gebiet=JETZIGE_ERFAHRUNG)}),
        erfahrungen=[erfahrung("Thema", 0.5)],
        nachklang=0.5,
        schwelle=0.2,
    )
    verlauf = [staerke(geist.schritt(), "Thema") for _ in range(4)]
    # 0.125 liegt unter der Schwelle: Ab da wird das Thema nur noch mitgeführt.
    assert verlauf == [0.5, 0.25, 0.125, 0.03125]
