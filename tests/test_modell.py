from geist import (
    EMOTION,
    KOERPER,
    ERINNERUNG,
    JETZIGE_ERFAHRUNG,
    SINNE,
    Entscheidung,
    Erfahrung,
    Geist,
    ManuelleBewussteIntention,
    Umgang,
    Unterbewusstsein,
)

GEBIET = "Alltag"


def nichts(lage):
    return Entscheidung()


def immer(umgang, thema="Thema"):
    return lambda lage: Entscheidung({thema: umgang})


def nach_plan(plan):
    """Entscheider, der pro Moment die Entscheidung aus `plan` nimmt."""
    momente = iter(range(10**6))
    return lambda lage: plan.get(next(momente), Entscheidung())


def geist_mit(
    entscheider=nichts,
    gebiet=GEBIET,
    erfahrungen=(),
    chance=0.0,
    mitnahme=0.5,
    haltungsschritt=0.0,
    **kwargs,
):
    """Ein Geist, bei dem jeder Test nur das sieht, was er prüft.

    Ohne Zufall, solange `chance` nicht gesetzt wird. Fremdes kommt immer mit
    halber Stärke mit; `mitnahme=None` lässt den Einfluss der Gebiete durch
    Erfahrung entstehen, wie im Modell. Die Haltung bleibt in der Mitte
    zwischen heilsam und unheilsam; erst ein `haltungsschritt` lässt sie sich
    verschieben.
    """
    geist = Geist(
        entscheider,
        gebiet,
        chance=chance,
        mitnahme=mitnahme,
        haltungsschritt=haltungsschritt,
        **kwargs,
    )
    for e in erfahrungen:
        geist.unterbewusstsein.erlebe(e)
    return geist


def aui(mitnahme=0.5, **kwargs):
    """Ein AUI mit festem Einfluss der Gebiete, siehe `geist_mit`."""
    return Unterbewusstsein(mitnahme=mitnahme, **kwargs)


def erfahrung(thema, staerke, gebiet=GEBIET, zeit=0):
    return Erfahrung(thema, staerke, zeit, (gebiet,))


def staerke(moment, thema):
    return next((i.staerke for i in moment.aui_feld if i.thema == thema), 0.0)


def impuls(moment, thema):
    return next(i for i in moment.aui_feld if i.thema == thema)


def themen(feld):
    """Die Impulse eines Feldes ohne die früheren Haltungen, die darin auftauchen."""
    return [i for i in feld if not i.haltung]


def im_feld(moment):
    return [i.thema for i in themen(moment.abi_feld)]


def haltungen_im_feld(moment):
    return [i.thema for i in moment.abi_feld if i.haltung]


STARK_UND_SCHWACH = (erfahrung("Stark", 0.9), erfahrung("Schwach", 0.1))
SORGE_AUS_DER_FAMILIE = (erfahrung("Sorge", 0.8, "Familie"),)
ERST_ENGAGE_DANN_DISENGAGE = {
    0: Entscheidung({"Sorge": Umgang.ENGAGE}),
    1: Entscheidung({"Sorge": Umgang.DISENGAGE}),
}


# --- AUI: Impulse aus Erfahrungen ---


def test_ohne_erfahrung_kein_impuls():
    assert geist_mit().schritt().aui_feld == ()


def test_impulse_entstehen_aus_vorherigen_und_jetzigen_erfahrungen():
    geist = geist_mit(erfahrungen=[erfahrung("Frueher", 0.6)])
    moment = geist.schritt({"Jetzt": 0.6})
    assert {i.thema for i in moment.aui_feld} == {"Frueher", "Jetzt"}


def test_erfahrungen_klingen_nach_und_werden_schwaecher():
    unterbewusstsein = aui(nachklang=0.5)
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
    mit = geist_mit(immer(Umgang.ENGAGE), erfahrungen=[erfahrung("Thema", 0.5)], nachklang=1.0)
    for geist in (ohne, mit):
        geist.schritt()

    assert staerke(ohne.schritt(), "Thema") == 0.5
    assert staerke(mit.schritt(), "Thema") == 0.9


def test_engage_auf_ein_thema_aus_einem_anderen_gebiet_ersetzt_die_haltung():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
    )
    erster, zweiter = geist.schritt(), geist.schritt()

    assert (erster.gebiete, erster.gebiete_danach) == (("Arbeit",), ("Sorge",))
    assert zweiter.gebiete == ("Sorge",)


def test_engage_auf_ein_thema_aus_der_jetzigen_haltung_laeuft_parallel():
    geist = geist_mit(immer(Umgang.ENGAGE, "Sorge"), "Familie", SORGE_AUS_DER_FAMILIE)
    geist.schritt()
    assert geist.schritt().gebiete == ("Familie", "Sorge")


def test_woher_ein_thema_stammt_entscheidet_die_groessere_haelfte_seiner_staerke():
    def haltung_nach_engage(aus_der_arbeit, aus_der_familie):
        geist = geist_mit(
            immer(Umgang.ENGAGE, "Sorge"),
            "Arbeit",
            [erfahrung("Sorge", aus_der_arbeit, "Arbeit"), erfahrung("Sorge", aus_der_familie, "Familie")],
        )
        return geist.schritt().gebiete_danach

    # Aus der Familie kommt nur die Hälfte mit: 0.5 gegen 0.4 und 0.3 gegen 0.4.
    assert haltung_nach_engage(0.5, 0.8) == ("Arbeit", "Sorge")
    assert haltung_nach_engage(0.3, 0.8) == ("Sorge",)


def test_nach_dem_ersetzen_liegt_die_vorherige_haltung_im_aui():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
    )
    geist.schritt()
    assert "Arbeit" in haltungen_im_feld(geist.schritt())


def test_im_eigenen_themengebiet_zaehlt_das_thema_voll():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
        nachklang=1.0,
    )
    mitgebracht, eigenes_gebiet = (impuls(geist.schritt(), "Sorge") for _ in range(2))

    assert (mitgebracht.staerke, mitgebracht.mitgebracht_aus) == (0.4, ("Familie",))
    assert (eigenes_gebiet.staerke, eigenes_gebiet.mitgebracht_aus) == (1.0, ())


def test_engage_gibt_es_nur_zu_dem_was_im_abi_feld_auftaucht():
    geist = geist_mit(
        immer(Umgang.ENGAGE, "Leise"), "Arbeit", [erfahrung("Leise", 0.2, "Arbeit")]
    )
    moment = geist.schritt()

    assert im_feld(moment) == []
    assert moment.umgang == {}
    assert moment.gebiete_danach == ("Arbeit",)
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_engage_gehoert_zu_den_gebieten_in_denen_die_mbi_agiert_hat():
    geist = geist_mit(immer(Umgang.ENGAGE, "Mail"), "Arbeit", [erfahrung("Mail", 0.5, "Arbeit")])
    geist.schritt()
    neu = geist.unterbewusstsein.erfahrungen[-1]
    assert (neu.thema, neu.staerke, neu.gebiete) == ("Mail", 0.4, ("Arbeit",))


# --- Disengage: schwächt im AUI und verhindert das Themengebiet ---


def test_disengage_schwaecht_das_thema_im_aui():
    geist = geist_mit(
        immer(Umgang.DISENGAGE), erfahrungen=[erfahrung("Thema", 0.8)], nachklang=1.0
    )
    verlauf = [staerke(geist.schritt(), "Thema") for _ in range(3)]
    assert [round(s, 2) for s in verlauf] == [0.8, 0.4, 0.0]


def test_disengage_macht_das_thema_nicht_zum_gebiet():
    geist = geist_mit(immer(Umgang.DISENGAGE, "Sorge"), "Arbeit", SORGE_AUS_DER_FAMILIE)
    assert geist.schritt().gebiete_danach == ("Arbeit",)


def test_disengage_beendet_ein_themengebiet_der_mbi():
    geist = geist_mit(nach_plan(ERST_ENGAGE_DANN_DISENGAGE), "Familie", SORGE_AUS_DER_FAMILIE)
    verlauf = [geist.schritt().gebiete_danach for _ in range(2)]
    assert verlauf == [("Familie", "Sorge"), ("Familie",)]


def test_ohne_eigenes_gebiet_bleibt_der_mbi_die_jetzige_erfahrung():
    geist = geist_mit(nach_plan(ERST_ENGAGE_DANN_DISENGAGE), "Arbeit", SORGE_AUS_DER_FAMILIE)
    verlauf = [geist.schritt().gebiete_danach for _ in range(2)]
    assert verlauf == [("Sorge",), (JETZIGE_ERFAHRUNG,)]


def test_disengage_gibt_es_nur_zu_dem_was_im_abi_feld_auftaucht():
    geist = geist_mit(immer(Umgang.DISENGAGE, "Nirgends"))
    assert geist.schritt().umgang == {}
    assert geist.unterbewusstsein.erfahrungen == []


# --- Weder noch: verstärkt nicht, schwächt nicht, lässt aber eine Chance ---


def test_weder_noch_verstaerkt_nicht_und_schwaecht_nicht():
    for entscheider in (nichts, immer(Umgang.WEDER_NOCH)):
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
    for umgang in (Umgang.ENGAGE, Umgang.DISENGAGE):
        geist = geist_mit(immer(umgang, "Sorge"), "Arbeit", SORGE_AUS_DER_FAMILIE, chance=1.0)
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
        nach_plan({1: Entscheidung({"Sorge": Umgang.ENGAGE})}),
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
        nach_plan({1: Entscheidung({"Sorge": Umgang.DISENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
        chance=1.0,
    )
    geist.schritt()
    moment = geist.schritt()

    assert (moment.gebiete_danach, moment.gebiete_ohne_mbi_danach) == (("Arbeit",), ())


# --- Autonomes Ausrichten: Themenwechsel oder Themenerhalt, kein engage ---


def test_themenwechsel_auf_ein_gebiet_das_nie_im_bewusstsein_war():
    geist = geist_mit(nach_plan({0: Entscheidung(themenwechsel="Urlaub")}), "Familie")
    erster, zweiter = geist.schritt(), geist.schritt()

    # Nichts ist aus dem AUI in die ABI gestiegen, und trotzdem wechselt die MBI.
    assert erster.aui_feld == erster.abi_feld == ()
    assert (erster.gebiete, erster.gebiete_danach) == (("Familie",), ("Urlaub",))
    assert zweiter.gebiete == ("Urlaub",)
    # Ein Themenwechsel ist kein engage: Im AUI wird nichts verstärkt.
    assert geist.unterbewusstsein.erfahrungen == []
    assert zweiter.aui_feld == ()


def test_themenerhalt_laesst_die_gebiete_wie_sie_sind():
    geist = geist_mit(gebiet="Arbeit", erfahrungen=SORGE_AUS_DER_FAMILIE)
    moment = geist.schritt()

    assert moment.gebiete_danach == ("Arbeit",)
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_themenwechsel_ersetzt_alle_gebiete_der_haltung():
    plan = {0: Entscheidung({"Sorge": Umgang.ENGAGE}), 1: Entscheidung(themenwechsel=SINNE)}
    geist = geist_mit(nach_plan(plan), "Familie", SORGE_AUS_DER_FAMILIE)
    verlauf = [geist.schritt().gebiete_danach for _ in range(2)]
    assert verlauf == [("Familie", "Sorge"), (SINNE,)]


# --- Gebiete: AUI und ABI orientieren sich daran ---


def test_aui_orientiert_sich_am_gebiet_der_mbi():
    unterbewusstsein = aui()
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, gebiet="Familie"))

    (daheim,) = themen(unterbewusstsein.erzeuge_impulse(0, ["Familie"]))
    (woanders,) = themen(unterbewusstsein.erzeuge_impulse(0, ["Arbeit"]))
    (beides,) = themen(unterbewusstsein.erzeuge_impulse(0, ["Arbeit", "Familie"]))

    assert (daheim.staerke, daheim.mitgebracht_aus) == (0.8, ())
    assert (woanders.staerke, woanders.mitgebracht_aus) == (0.4, ("Familie",))
    assert (beides.staerke, beides.mitgebracht_aus) == (0.8, ())


def test_aui_fuehrt_vergangene_themen_mit_in_neue_gebiete():
    geist = geist_mit(
        nach_plan({0: Entscheidung(themenwechsel="Arbeit")}),
        "Familie",
        [erfahrung("Sorge", 1.0, gebiet="Familie")],
    )
    geist.schritt()
    moment = geist.schritt()

    (sorge,) = themen(moment.abi_feld)
    assert moment.gebiete == ("Arbeit",)
    assert (sorge.thema, sorge.mitgebracht_aus) == ("Sorge", ("Familie",))


def test_zurueck_im_alten_gebiet_zaehlt_das_thema_wieder_voll():
    plan = {0: Entscheidung(themenwechsel="Arbeit"), 1: Entscheidung(themenwechsel="Familie")}
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
    (sorge,) = themen(geist.schritt().aui_feld)
    assert (sorge.staerke, sorge.mitgebracht_aus) == (0.4, ("Familie",))


# --- Die jetzige Erfahrung als Gebiet: alles, was im Feld der ABI auftaucht ---


def test_was_im_abi_feld_auftaucht_zaehlt_in_der_jetzigen_erfahrung_voll():
    plan = {0: Entscheidung(themenwechsel="Arbeit"), 1: Entscheidung(themenwechsel=JETZIGE_ERFAHRUNG)}
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
        (leise,) = themen(moment.aui_feld)
        assert moment.abi_feld == ()
        assert (leise.staerke, leise.mitgebracht_aus) == (0.2, ("Familie",))


def test_was_aus_dem_abi_feld_verschwindet_zaehlt_nicht_mehr_voll():
    geist = geist_mit(
        nach_plan({0: Entscheidung(themenwechsel=JETZIGE_ERFAHRUNG)}),
        erfahrungen=[erfahrung("Thema", 0.5)],
        nachklang=0.5,
        schwelle=0.2,
    )
    verlauf = [staerke(geist.schritt(), "Thema") for _ in range(4)]
    # 0.125 liegt unter der Schwelle: Ab da wird das Thema nur noch mitgeführt.
    assert verlauf == [0.5, 0.25, 0.125, 0.03125]


# --- Die Erinnerung als Gebiet: so aktiviert die MBI, was nur im AUI liegt ---

VERBLASSTER_STREIT = (erfahrung("Streit", 0.9, "Familie", zeit=-10),)
IN_DIE_ERINNERUNG = Entscheidung(themenwechsel=ERINNERUNG)


def test_mit_dem_was_nur_im_aui_liegt_gibt_es_keinen_umgang():
    geist = geist_mit(immer(Umgang.ENGAGE, "Streit"), "Familie", VERBLASSTER_STREIT)
    moment = geist.schritt()

    assert [i.thema for i in moment.aui_feld] == ["Streit"]
    assert moment.abi_feld == ()
    assert moment.umgang == {}


def test_in_der_erinnerung_zaehlt_frueheres_unverblasst_egal_aus_welchem_gebiet():
    unterbewusstsein = aui()
    unterbewusstsein.erlebe(VERBLASSTER_STREIT[0])

    (verblasst,) = themen(unterbewusstsein.erzeuge_impulse(0, ["Familie"]))
    (erinnert,) = themen(unterbewusstsein.erzeuge_impulse(0, [ERINNERUNG]))

    assert verblasst.staerke < 0.1
    assert (erinnert.staerke, erinnert.mitgebracht_aus) == (0.9, ())


def test_themenwechsel_in_die_erinnerung_laesst_verblasstes_in_der_abi_auftauchen():
    geist = geist_mit(nach_plan({0: IN_DIE_ERINNERUNG}), "Familie", VERBLASSTER_STREIT)
    vorher, in_der_erinnerung = geist.schritt(), geist.schritt()

    assert im_feld(vorher) == []
    assert in_der_erinnerung.gebiete == (ERINNERUNG,)
    assert im_feld(in_der_erinnerung) == ["Streit"]


def test_die_erinnerung_verstaerkt_nichts_im_aui():
    plan = {0: IN_DIE_ERINNERUNG, 1: Entscheidung(themenwechsel="Familie")}
    geist = geist_mit(nach_plan(plan), "Familie", VERBLASSTER_STREIT)
    verlauf = [im_feld(geist.schritt()) for _ in range(3)]

    # Zurück in der Familie ist der Streit so verblasst wie zuvor.
    assert verlauf == [[], ["Streit"], []]
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_was_gerade_erst_erlebt_wird_ist_noch_keine_erinnerung():
    moment = geist_mit(gebiet=ERINNERUNG).schritt({"Klang": 0.4})
    (klang,) = moment.aui_feld
    assert (klang.staerke, klang.mitgebracht_aus) == (0.2, (SINNE,))


def test_in_der_erinnerung_ist_engage_moeglich():
    plan = {0: IN_DIE_ERINNERUNG, 1: Entscheidung({"Streit": Umgang.ENGAGE})}
    geist = geist_mit(nach_plan(plan), "Arbeit", VERBLASSTER_STREIT)
    geist.schritt()
    moment = geist.schritt()

    assert moment.umgang == {"Streit": Umgang.ENGAGE}
    # Der Streit stammt aus der Erinnerung, also läuft er parallel zu ihr.
    assert moment.gebiete_danach == (ERINNERUNG, "Streit")


# --- Die Haltung: das Gebiet der MBI. Das AUI kann frühere Haltungen enthalten ---


def test_die_mbi_befindet_sich_immer_in_einer_haltung():
    geist = geist_mit(nach_plan(ERST_ENGAGE_DANN_DISENGAGE), "Arbeit", SORGE_AUS_DER_FAMILIE)
    assert all(geist.schritt().gebiete_danach for _ in range(3))


def test_eine_erfahrung_enthaelt_die_haltung_in_der_die_mbi_dabei_war():
    for umgang, wirkung in ((Umgang.ENGAGE, 0.4), (Umgang.DISENGAGE, -0.4)):
        geist = geist_mit(immer(umgang, "Sorge"), "Arbeit", SORGE_AUS_DER_FAMILIE)
        geist.schritt()
        neu = geist.unterbewusstsein.erfahrungen[-1]
        assert (neu.staerke, neu.gebiete) == (wirkung, ("Arbeit",))


def test_fruehere_haltung_aus_dem_aui_taucht_im_bewusstsein_auf():
    moment = geist_mit(gebiet="Arbeit", erfahrungen=SORGE_AUS_DER_FAMILIE).schritt()
    assert haltungen_im_feld(moment) == ["Familie"]


def test_die_haltung_in_der_die_mbi_gerade_ist_taucht_nicht_als_fruehere_auf():
    moment = geist_mit(gebiet="Familie", erfahrungen=SORGE_AUS_DER_FAMILIE).schritt()
    assert [i.thema for i in moment.aui_feld] == ["Sorge"]


def test_haltung_taucht_so_stark_auf_wie_ihr_staerkstes_thema():
    unterbewusstsein = aui()
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, "Familie"))
    unterbewusstsein.erlebe(erfahrung("Streit", 0.4, "Familie"))

    (familie,) = (i for i in unterbewusstsein.erzeuge_impulse(0, ["Arbeit"]) if i.haltung)

    assert (familie.thema, familie.staerke) == ("Familie", 0.4)


def test_mbi_kann_auf_eine_aufgetauchte_haltung_engagen():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Familie": Umgang.ENGAGE})}),
        "Arbeit",
        SORGE_AUS_DER_FAMILIE,
        nachklang=1.0,
    )
    erster, zweiter = geist.schritt(), geist.schritt()
    sorge = impuls(zweiter, "Sorge")

    assert erster.gebiete_danach == ("Familie",)
    # In der wieder eingenommenen Haltung zählt die Sorge voll.
    assert (sorge.staerke, sorge.mitgebracht_aus) == (0.8, ())
    # Die verlassene Haltung liegt jetzt ihrerseits im AUI.
    assert haltungen_im_feld(zweiter) == ["Arbeit"]


def test_eine_haltung_wird_nicht_ohne_die_mbi_zum_gebiet():
    geist = geist_mit(gebiet="Arbeit", erfahrungen=SORGE_AUS_DER_FAMILIE, chance=1.0)
    moment = geist.schritt()

    assert haltungen_im_feld(moment) == ["Familie"]
    assert moment.gebiete_ohne_mbi_danach == ("Sorge",)


def test_sinne_tauchen_nicht_als_fruehere_haltung_auf():
    moment = geist_mit(gebiet="Arbeit").schritt({"Laerm": 0.9})
    assert [i.thema for i in moment.aui_feld] == ["Laerm"]


# --- Die Kapazität der MBI: Ein zu starkes Thema verdrängt die anderen ---


def mbi_mit(*gebiete):
    mbi = ManuelleBewussteIntention(nichts, gebiete[0])
    mbi.gebiete = list(gebiete)
    return mbi


def test_solange_alles_hineinpasst_laeuft_es_parallel():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Familie",
        [erfahrung("Sorge", 0.5, "Familie")],
        nachklang=1.0,
    )
    geist.schritt()
    moment = geist.schritt()

    assert staerke(moment, "Sorge") == 0.9
    assert (moment.verdraengt, moment.gebiete_danach) == ((), ("Familie", "Sorge"))


def test_ein_zu_starkes_thema_verdraengt_die_anderen_ohne_die_mbi():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Familie",
        SORGE_AUS_DER_FAMILIE,
        nachklang=1.0,
    )
    geist.schritt()
    moment = geist.schritt()

    assert staerke(moment, "Sorge") == 1.0
    assert moment.umgang == {}
    assert (moment.verdraengt, moment.gebiete_danach) == (("Familie",), ("Sorge",))


def test_mit_mehr_kapazitaet_wird_nichts_verdraengt():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Familie",
        SORGE_AUS_DER_FAMILIE,
        nachklang=1.0,
        kapazitaet=2.0,
    )
    geist.schritt()
    assert geist.schritt().verdraengt == ()


def test_die_verdraengte_haltung_liegt_danach_im_aui():
    geist = geist_mit(
        nach_plan({0: Entscheidung({"Sorge": Umgang.ENGAGE})}),
        "Familie",
        SORGE_AUS_DER_FAMILIE,
        nachklang=1.0,
    )
    for _ in range(2):
        geist.schritt()
    assert haltungen_im_feld(geist.schritt()) == ["Familie"]


def test_zuerst_wird_das_schwaechste_gebiet_verdraengt():
    gewichte = {"A": 0.2, "B": 0.5, "C": 0.6}
    mbi = mbi_mit("A", "B", "C")

    verdraengt = mbi.verdraenge(lambda gebiet, alle: gewichte[gebiet], kapazitaet=1.0)

    assert (verdraengt, mbi.gebiete) == (["A", "B"], ["C"])


def test_was_die_mbi_gerade_erst_betreten_hat_wird_nicht_verdraengt():
    gewichte = {"A": 0.2, "B": 0.5, "C": 0.6}
    mbi = mbi_mit("A", "B", "C")

    verdraengt = mbi.verdraenge(
        lambda gebiet, alle: gewichte[gebiet], kapazitaet=1.0, geschuetzt=["A"]
    )

    assert (verdraengt, mbi.gebiete) == (["B"], ["A", "C"])


def test_ein_einzelnes_gebiet_wird_nie_verdraengt():
    mbi = mbi_mit("A")
    assert mbi.verdraenge(lambda gebiet, alle: 1.0, kapazitaet=1.0) == []
    assert mbi.gebiete == ["A"]


def test_ein_gebiet_ohne_eigenes_thema_wiegt_so_viel_wie_sein_staerkstes_anderes_thema():
    unterbewusstsein = aui()
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, "Familie"))
    unterbewusstsein.erlebe(erfahrung("Streit", 0.3, "Familie"))
    unterbewusstsein.erzeuge_impulse(0, ["Familie", "Sorge"])

    assert unterbewusstsein.gewicht("Sorge", ["Familie", "Sorge"]) == 0.8
    # Die Sorge zählt schon als eigenes Gebiet, also bleibt für die Familie der Streit.
    assert unterbewusstsein.gewicht("Familie", ["Familie", "Sorge"]) == 0.3
    assert unterbewusstsein.gewicht("Familie", ["Familie"]) == 0.8


# --- Gewohnheit: Wiederholtes engage prägt ein Thema ---


def test_engage_macht_ein_thema_zur_gewohnheit_und_disengage_baut_sie_ab():
    plan = {
        0: Entscheidung({"Thema": Umgang.ENGAGE}),
        1: Entscheidung({"Thema": Umgang.ENGAGE}),
        2: Entscheidung({"Thema": Umgang.DISENGAGE}),
    }
    geist = geist_mit(nach_plan(plan), erfahrungen=[erfahrung("Thema", 0.8)])
    verlauf = []
    for _ in range(3):
        geist.schritt()
        verlauf.append(geist.unterbewusstsein.gewohnheit["Thema"])

    assert verlauf == [1, 2, 1]


def test_engage_und_disengage_geschehen_nie_von_allein():
    geist = geist_mit(erfahrungen=[erfahrung("Thema", 0.8)], chance=1.0)
    for _ in range(3):
        assert geist.schritt().umgang == {}
    assert geist.unterbewusstsein.gewohnheit == {}
    assert len(geist.unterbewusstsein.erfahrungen) == 1


def test_je_oefter_engaged_desto_langsamer_verblasst_das_thema():
    unterbewusstsein = aui(nachklang=0.8)
    unterbewusstsein.gewohnheit = {"Oft": 3, "Einmal": 1, "Abgewöhnt": -2}
    nachklang = unterbewusstsein.nachklang_fuer

    assert nachklang("Oft") > nachklang("Einmal") > nachklang("Nie") == 0.8
    assert nachklang("Abgewöhnt") < 0.8


def test_gewohnheit_wirkt_auf_neue_erfahrungen_nicht_auf_fruehere():
    unterbewusstsein = aui(nachklang=0.8)
    unterbewusstsein.erlebe(erfahrung("Thema", 0.5))
    unterbewusstsein.uebe("Thema", 1)
    unterbewusstsein.erlebe(erfahrung("Thema", 0.5))
    vorher, nachher = unterbewusstsein.erfahrungen

    assert vorher.nachklang == 0.8
    assert nachher.nachklang > 0.8


def test_ein_gewohntes_thema_bleibt_laenger_im_feld_der_abi():
    def momente_im_feld(engagements):
        plan = {zeit: Entscheidung({"Thema": Umgang.ENGAGE}) for zeit in range(engagements)}
        geist = geist_mit(nach_plan(plan), erfahrungen=[erfahrung("Thema", 0.8)])
        return sum("Thema" in im_feld(geist.schritt()) for _ in range(40))

    assert momente_im_feld(3) > momente_im_feld(1) > momente_im_feld(0)


def test_der_impuls_zeigt_die_gewohnheit():
    geist = geist_mit(immer(Umgang.ENGAGE), erfahrungen=[erfahrung("Thema", 0.8)])
    geist.schritt()
    assert impuls(geist.schritt(), "Thema").gewohnheit == 1


# --- Emotion und Körper: zwei eigene Gebiete mit eigenen Themen ---


def test_emotionen_und_koerperempfindungen_gehoeren_zu_ihrem_eigenen_gebiet():
    geist = geist_mit(gebiet="Arbeit")
    geist.schritt({"Laerm": 0.5}, {"Angst": 0.5}, {"Enge": 0.5})
    assert [(e.thema, e.gebiete) for e in geist.unterbewusstsein.erfahrungen] == [
        ("Laerm", (SINNE,)),
        ("Angst", (EMOTION,)),
        ("Enge", (KOERPER,)),
    ]


def test_in_der_emotion_zaehlt_eine_emotion_voll_sonst_kommt_sie_nur_mit():
    in_der_emotion = impuls(geist_mit(gebiet=EMOTION).schritt(emotion={"Angst": 0.6}), "Angst")
    in_der_arbeit = impuls(geist_mit(gebiet="Arbeit").schritt(emotion={"Angst": 0.6}), "Angst")

    assert (in_der_emotion.staerke, in_der_emotion.mitgebracht_aus) == (0.6, ())
    assert (in_der_arbeit.staerke, in_der_arbeit.mitgebracht_aus) == (0.3, (EMOTION,))


def test_emotion_und_koerper_sind_zwei_verschiedene_gebiete():
    moment = geist_mit(gebiet=KOERPER).schritt(emotion={"Angst": 0.6}, koerper={"Enge": 0.6})

    assert impuls(moment, "Enge").mitgebracht_aus == ()
    assert impuls(moment, "Angst").mitgebracht_aus == (EMOTION,)


def test_emotion_und_koerper_tauchen_nicht_als_fruehere_haltung_auf():
    moment = geist_mit(gebiet="Arbeit").schritt(emotion={"Angst": 0.9}, koerper={"Enge": 0.9})
    assert haltungen_im_feld(moment) == []


def test_mbi_kann_eine_emotion_aufgreifen_wenn_sie_stark_genug_auftaucht():
    geist = geist_mit(immer(Umgang.ENGAGE, "Angst"), "Arbeit")
    zu_schwach = geist_mit(immer(Umgang.ENGAGE, "Angst"), "Arbeit").schritt(emotion={"Angst": 0.4})
    stark_genug = geist.schritt(emotion={"Angst": 0.8})

    assert zu_schwach.umgang == {}
    assert stark_genug.umgang == {"Angst": Umgang.ENGAGE}
    assert stark_genug.gebiete_danach == ("Angst",)


# --- Was zusammen erlebt wurde, taucht verstärkt zusammen auf ---


def aui_mit_streit(gemeinsam_erlebt):
    unterbewusstsein = aui(kopplung=0.5)
    unterbewusstsein.erlebe(Erfahrung("Streit", 0.8, 0, (SINNE,)))
    for _ in range(gemeinsam_erlebt):
        unterbewusstsein.verknuepfe(["Streit", "Wut"])
    return unterbewusstsein


def staerke_im_aui(unterbewusstsein, thema):
    feld = unterbewusstsein.erzeuge_impulse(0, [SINNE])
    return next((i.staerke for i in feld if i.thema == thema), 0.0)


def test_was_im_selben_moment_erlebt_wird_verknuepft_sich():
    geist = geist_mit(gebiet=SINNE)
    geist.schritt({"Streit": 0.9}, {"Wut": 0.7})
    assert geist.unterbewusstsein.verknuepfungen == {frozenset({"Streit", "Wut"}): 1}


def test_ein_verknuepftes_thema_taucht_mit_auf():
    assert staerke_im_aui(aui_mit_streit(gemeinsam_erlebt=0), "Wut") == 0.0
    assert staerke_im_aui(aui_mit_streit(gemeinsam_erlebt=1), "Wut") == 0.2


def test_je_oefter_zusammen_erlebt_desto_staerker_die_bindung():
    einmal = staerke_im_aui(aui_mit_streit(gemeinsam_erlebt=1), "Wut")
    zweimal = staerke_im_aui(aui_mit_streit(gemeinsam_erlebt=2), "Wut")
    assert zweimal > einmal


def test_beide_bleiben_eigene_themen_in_eigenen_gebieten():
    geist = geist_mit(gebiet=SINNE)
    geist.schritt({"Streit": 0.9}, {"Wut": 0.7})
    moment = geist.schritt()

    assert impuls(moment, "Streit").mitgebracht_aus == ()
    assert impuls(moment, "Wut").mitgebracht_aus == (EMOTION,)


def test_das_mit_auftauchen_hinterlaesst_keine_erfahrung():
    unterbewusstsein = aui_mit_streit(gemeinsam_erlebt=2)
    unterbewusstsein.erzeuge_impulse(0, [SINNE])
    assert [e.thema for e in unterbewusstsein.erfahrungen] == ["Streit"]


def test_verklungenes_taucht_wieder_auf_wenn_sein_partner_auftaucht():
    geist = geist_mit(gebiet=SINNE)
    geist.schritt({"Streit": 0.9}, {"Wut": 0.7})
    verklungen = [geist.schritt() for _ in range(5)][-1]
    wieder_da = geist.schritt({"Streit": 0.9})

    assert "Wut" not in im_feld(verklungen)
    assert "Wut" in im_feld(wieder_da)


# --- Jedes Gebiet beeinflusst die Impulse des AUI, gelernt durch Erfahrung ---


def gelerntes_aui(erfahrungen_im_hobby):
    unterbewusstsein = aui(mitnahme=None, nachklang=1.0)
    unterbewusstsein.erlebe(erfahrung("Sorge", 0.8, "Familie"))
    for _ in range(erfahrungen_im_hobby):
        unterbewusstsein.erlebe(erfahrung("Malen", 0.1, "Hobby"))
    return unterbewusstsein


def test_ein_gebiet_ohne_erfahrung_hat_keinen_einfluss():
    unterbewusstsein = gelerntes_aui(erfahrungen_im_hobby=0)
    (sorge,) = themen(unterbewusstsein.erzeuge_impulse(0, ["Hobby"]))

    assert unterbewusstsein.einfluss("Hobby") == 0.0
    # Die Sorge kommt aus der Familie mit, wird aber nicht zurückgedrängt.
    assert (sorge.staerke, sorge.mitgebracht_aus) == (0.8, ("Familie",))


def test_der_einfluss_waechst_mit_der_erfahrung_im_gebiet():
    einfluss = [gelerntes_aui(n).einfluss("Hobby") for n in (0, 2, 4, 8)]
    assert einfluss == [0.0, 0.5, 0.75, 0.9375]


def test_je_mehr_einfluss_desto_staerker_wird_fremdes_zurueckgedraengt():
    def sorge_im_hobby(erfahrungen):
        feld = gelerntes_aui(erfahrungen).erzeuge_impulse(0, ["Hobby"])
        return next(i.staerke for i in feld if i.thema == "Sorge")

    assert [sorge_im_hobby(n) for n in (0, 2, 4)] == [0.8, 0.4, 0.2]


def test_was_zum_gebiet_gehoert_wird_nicht_zurueckgedraengt():
    feld = gelerntes_aui(erfahrungen_im_hobby=4).erzeuge_impulse(0, ["Hobby"])
    assert next(i.staerke for i in feld if i.thema == "Malen") == 0.4


def test_engage_im_gebiet_laesst_seinen_einfluss_wachsen_und_disengage_schrumpfen():
    def einfluss_nach(umgang):
        geist = geist_mit(
            immer(umgang, "Malen"),
            "Hobby",
            [erfahrung("Malen", 0.8, "Hobby")],
            mitnahme=None,
        )
        vorher = geist.unterbewusstsein.einfluss("Hobby")
        geist.schritt()
        return vorher, geist.unterbewusstsein.einfluss("Hobby")

    vorher, nach_engage = einfluss_nach(Umgang.ENGAGE)
    _, nach_disengage = einfluss_nach(Umgang.DISENGAGE)

    assert nach_engage > vorher > nach_disengage


def test_bei_mehreren_gebieten_bestimmt_das_einflussreichste():
    unterbewusstsein = gelerntes_aui(erfahrungen_im_hobby=4)
    feld = unterbewusstsein.erzeuge_impulse(0, ["Hobby", "Neuland"])
    assert next(i.staerke for i in feld if i.thema == "Sorge") == 0.2


def test_der_moment_zeigt_den_einfluss_der_gebiete():
    geist = geist_mit(gebiet="Hobby", erfahrungen=[erfahrung("Malen", 0.5, "Hobby")] * 2, mitnahme=None)
    assert geist.schritt().einfluss == {"Hobby": 0.5}


# --- Die Haltung liegt auf einem Spektrum von heilsam zu unheilsam ---


def haltung_nach(*entscheidungen, erfahrungen=(erfahrung("Thema", 0.8),)):
    """Wo die Haltung nach diesen Entscheidungen liegt, eine pro Moment."""
    geist = geist_mit(
        nach_plan(dict(enumerate(entscheidungen))), erfahrungen=erfahrungen, haltungsschritt=0.2
    )
    for _ in entscheidungen:
        moment = geist.schritt()
    return moment.heilsamkeit_danach


def test_die_haltung_beginnt_in_der_mitte():
    assert geist_mit(haltungsschritt=0.2).schritt().heilsamkeit == 0.0


def test_engage_aus_verlangen_und_disengage_aus_abneigung_machen_die_haltung_unheilsam():
    assert haltung_nach(Entscheidung({"Thema": Umgang.VERLANGEN})) == -0.2
    assert haltung_nach(Entscheidung({"Thema": Umgang.ABNEIGUNG})) == -0.2


def test_engage_und_disengage_ohne_verlangen_und_abneigung_machen_sie_heilsam():
    assert haltung_nach(Entscheidung({"Thema": Umgang.ENGAGE})) == 0.2
    assert haltung_nach(Entscheidung({"Thema": Umgang.DISENGAGE})) == 0.2


def test_autonomes_ausrichten_macht_die_haltung_heilsam():
    themenwechsel = Entscheidung(themenwechsel="Neuland")
    themenerhalt = Entscheidung(themenwechsel=GEBIET)

    assert haltung_nach(themenwechsel) == 0.2
    assert haltung_nach(themenerhalt) == 0.2


def test_weder_noch_und_nichtstun_verschieben_die_haltung_nicht():
    assert haltung_nach(Entscheidung({"Thema": Umgang.WEDER_NOCH})) == 0.0
    assert haltung_nach(Entscheidung(), Entscheidung(), Entscheidung()) == 0.0


def test_die_haltung_bleibt_zwischen_ganz_unheilsam_und_ganz_heilsam():
    verlangen = [Entscheidung({"Thema": Umgang.VERLANGEN})] * 8
    assert haltung_nach(*verlangen) == -1.0


def test_verlangen_und_abneigung_wirken_im_aui_wie_engage_und_disengage():
    for unheilsam, heilsam in ((Umgang.VERLANGEN, Umgang.ENGAGE), (Umgang.ABNEIGUNG, Umgang.DISENGAGE)):
        verlauf = []
        for umgang in (unheilsam, heilsam):
            geist = geist_mit(immer(umgang), erfahrungen=[erfahrung("Thema", 0.8)])
            moment = geist.schritt()
            verlauf.append((geist.unterbewusstsein.erfahrungen[-1].staerke, moment.gebiete_danach))
        assert verlauf[0] == verlauf[1]


def test_themengebiete_sind_weder_heilsam_noch_unheilsam_es_ist_die_haltung():
    plan = {0: Entscheidung({"Thema": Umgang.VERLANGEN}), 1: Entscheidung(themenwechsel="Neuland")}
    geist = geist_mit(nach_plan(plan), erfahrungen=[erfahrung("Thema", 0.8)], haltungsschritt=0.2)
    geist.schritt()

    # Die Haltung geht mit der MBI in das neue Gebiet, sie hängt nicht am alten.
    assert geist.schritt().heilsamkeit == -0.2


def test_durch_den_umgang_wird_ein_thema_negativ_oder_heilsam():
    def faerbung_nach(*umgaenge):
        geist = geist_mit(
            nach_plan({zeit: Entscheidung({"Thema": u}) for zeit, u in enumerate(umgaenge)}),
            erfahrungen=[erfahrung("Thema", 0.8)],
            nachklang=1.0,
        )
        for _ in umgaenge:
            geist.schritt()
        return impuls(geist.schritt(), "Thema").faerbung

    assert faerbung_nach() == 0.0
    assert faerbung_nach(Umgang.VERLANGEN) == -0.5
    assert faerbung_nach(Umgang.VERLANGEN, Umgang.VERLANGEN) == -0.75
    assert faerbung_nach(Umgang.ENGAGE) == 0.5
    assert faerbung_nach(Umgang.VERLANGEN, Umgang.ENGAGE) == 0.0


def aui_mit_faerbung():
    unterbewusstsein = aui(faerbekraft=0.5, ruhe=0.5)
    for thema, bilanz in (("Negativ", -8), ("Neutral", 0), ("Heilsam", 8)):
        unterbewusstsein.erlebe(erfahrung(thema, 0.4))
        unterbewusstsein.umgangsbilanz[thema] = bilanz
    return unterbewusstsein


def staerken_bei(heilsamkeit):
    feld = aui_mit_faerbung().erzeuge_impulse(0, [GEBIET], heilsamkeit=heilsamkeit)
    staerken = {i.thema: round(i.staerke, 2) for i in feld}
    return staerken["Negativ"], staerken["Neutral"], staerken["Heilsam"]


def test_in_der_mitte_veraendert_die_haltung_die_impulse_nicht():
    assert staerken_bei(0.0) == (0.4, 0.4, 0.4)


def test_je_unheilsamer_desto_mehr_negative_und_desto_weniger_heilsame_impulse():
    negativ, neutral, heilsam = staerken_bei(-1.0)
    assert (negativ, neutral, heilsam) == (0.6, 0.4, 0.2)
    assert staerken_bei(-0.5)[0] < negativ


def test_je_heilsamer_desto_weniger_impulse_und_desto_eher_heilsame():
    negativ, neutral, heilsam = staerken_bei(1.0)

    # Insgesamt weniger als in der Mitte, und davon am ehesten das Heilsame.
    assert sum((negativ, neutral, heilsam)) < sum(staerken_bei(0.0))
    assert heilsam > neutral > negativ
    assert (negativ, neutral, heilsam) == (0.1, 0.2, 0.3)


def test_die_haltung_wirkt_erst_ab_dem_naechsten_moment_auf_die_impulse():
    geist = geist_mit(
        nach_plan({0: Entscheidung(themenwechsel=GEBIET)}),
        erfahrungen=[erfahrung("Thema", 0.8)],
        nachklang=1.0,
        haltungsschritt=1.0,
    )
    verlauf = [staerke(geist.schritt(), "Thema") for _ in range(2)]
    assert verlauf == [0.8, 0.4]
