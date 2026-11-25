/* Das Geistmodell für den Browser.
 *
 * Eine Übertragung von geist/modell.py, Zeile für Zeile. Die Python-Fassung ist
 * die Vorlage: Dort stehen die Regeln des Modells und alle Annahmen erklärt.
 * tests/test_web.py prüft, dass beide Fassungen dasselbe rechnen.
 *
 * Ein Unterschied im Ablauf: Im Browser entscheidet ein Mensch. Ein Moment hat
 * deshalb zwei Hälften. `beginne` nimmt auf, was erlebt wird, und zeigt die
 * Felder. `entscheide` nimmt, was die MBI tut, und schließt den Moment ab.
 */
(function (wurzel, fabrik) {
  const modell = fabrik();
  if (typeof module === "object" && module.exports) module.exports = modell;
  else wurzel.GeistModell = modell;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const MINDESTSTAERKE = 0.01;

  const SINNE = "Sinne";
  const JETZIGE_ERFAHRUNG = "jetzige Erfahrung";
  const ERINNERUNG = "Erinnerung";
  const EMOTION = "Emotion";
  const KOERPER = "Körper";
  const BESONDERE_GEBIETE = [SINNE, JETZIGE_ERFAHRUNG, ERINNERUNG, EMOTION, KOERPER];
  const FRUEHER = "früher";

  const Umgang = Object.freeze({
    ENGAGE: "engage",
    DISENGAGE: "disengage",
    WEDER_NOCH: "weder noch",
    VERLANGEN: "Verlangen",
    ABNEIGUNG: "Abneigung",
  });
  const ist_engage = (art) => art === Umgang.ENGAGE || art === Umgang.VERLANGEN;
  const ist_disengage = (art) => art === Umgang.DISENGAGE || art === Umgang.ABNEIGUNG;
  const ist_unheilsam = (art) => art === Umgang.VERLANGEN || art === Umgang.ABNEIGUNG;

  const STANDARD_WIRKUNG = Object.freeze({
    [Umgang.ENGAGE]: 0.4,
    [Umgang.DISENGAGE]: -0.4,
    [Umgang.WEDER_NOCH]: 0.0,
    [Umgang.VERLANGEN]: 0.4,
    [Umgang.ABNEIGUNG]: -0.4,
  });

  const runde = (zahl) => Math.round(zahl * 1e9) / 1e9;
  const plus = (karte, schluessel, betrag) => karte.set(schluessel, (karte.get(schluessel) || 0) + betrag);
  const unterkarte = (karte, schluessel) => {
    if (!karte.has(schluessel)) karte.set(schluessel, new Map());
    return karte.get(schluessel);
  };

  function zustandsfaktor(heilsamkeit, faerbung, hebel, ruhe) {
    let faktor = Math.pow(hebel, heilsamkeit * faerbung);
    if (heilsamkeit > 0) faktor *= 1 - ruhe * heilsamkeit;
    return faktor;
  }

  function gehoert_zum_gebiet(erfahrung, gebiet, im_abi_feld) {
    if (gebiet === JETZIGE_ERFAHRUNG) return im_abi_feld.has(erfahrung.thema);
    return erfahrung.gebiete.includes(gebiet) || erfahrung.thema === gebiet;
  }

  /* AUI. Automatisch und unbewusst: läuft ständig und erzeugt Impulse. */
  class Unterbewusstsein {
    constructor(o = {}) {
      this.nachklang = o.nachklang ?? 0.8;
      this.mitnahme = o.mitnahme ?? null;
      this.praegung = o.praegung ?? 0.5;
      this.kopplung = o.kopplung ?? 0.5;
      this.lerntempo = o.lerntempo ?? 2.0;
      this.faerbekraft = o.faerbekraft ?? 0.5;
      this.ruhe = o.ruhe ?? 0.5;
      this.spontan = o.spontan ?? 0.05;
      this.spontanstaerke = o.spontanstaerke ?? 0.3;
      this.zufallshebel = o.zufallshebel ?? 4.0;
      this.zufall = o.zufall ?? Math;
      this.gewohnheit = new Map();
      this.umgangsbilanz = new Map();
      this.verknuepfungen = new Map(); // "a\u0000b" -> Anzahl, a vor b
      this.erfahrungen = [];
      this.feld = [];
      this._staerken = new Map();
      this._eigene = new Map();
    }

    erlebe(erfahrung) {
      const e = { ...erfahrung };
      if (e.nachklang == null) e.nachklang = this.nachklang_fuer(e.thema);
      this.erfahrungen.push(e);
    }

    uebe(thema, richtung) {
      plus(this.gewohnheit, thema, richtung);
    }

    faerbe(thema, richtung) {
      plus(this.umgangsbilanz, thema, richtung);
    }

    faerbung(thema) {
      const bilanz = this.umgangsbilanz.get(thema) || 0;
      const betrag = 1 - Math.pow(0.5, Math.abs(bilanz));
      return bilanz >= 0 ? betrag : -betrag;
    }

    haltungsfaktor(thema, heilsamkeit) {
      let faktor = 1 + this.faerbekraft * heilsamkeit * this.faerbung(thema);
      if (heilsamkeit > 0) faktor *= 1 - this.ruhe * heilsamkeit;
      return Math.max(0, faktor);
    }

    aufkommenschance(thema, heilsamkeit) {
      const faktor = zustandsfaktor(heilsamkeit, this.faerbung(thema), this.zufallshebel, this.ruhe);
      return Math.min(1, this.spontan * faktor);
    }

    lasse_aufkommen(zeit, heilsamkeit) {
      if (!this.spontan) return [];
      const staerkste = new Map();
      for (const e of this.erfahrungen) {
        const bisher = staerkste.has(e.thema) ? staerkste.get(e.thema).staerke : 0;
        if (e.staerke > 0 && e.staerke > bisher) staerkste.set(e.thema, e);
      }
      const aufgekommen = [];
      for (const [thema, vorlage] of staerkste) {
        if (this.zufall.random() < this.aufkommenschance(thema, heilsamkeit)) {
          this.erlebe({ thema, staerke: this.spontanstaerke, zeit, gebiete: vorlage.gebiete });
          aufgekommen.push(thema);
        }
      }
      return aufgekommen;
    }

    nachklang_fuer(thema) {
      const gewohnheit = this.gewohnheit.get(thema) || 0;
      if (gewohnheit >= 0) return Math.pow(this.nachklang, 1 / (1 + this.praegung * gewohnheit));
      return Math.pow(this.nachklang, 1 - this.praegung * gewohnheit);
    }

    einfluss(gebiet) {
      if (this.mitnahme != null) return 1 - this.mitnahme;
      let menge = 0;
      for (const e of this.erfahrungen) {
        if (e.gebiete.includes(gebiet) || e.thema === gebiet) menge += e.staerke > 0 ? 1 : -1;
      }
      return 1 - Math.pow(0.5, Math.max(0, menge) / this.lerntempo);
    }

    verknuepfe(themen) {
      const sortiert = [...new Set(themen)].sort();
      for (let i = 0; i < sortiert.length; i++) {
        for (let j = i + 1; j < sortiert.length; j++) {
          plus(this.verknuepfungen, sortiert[i] + "\u0000" + sortiert[j], 1);
        }
      }
    }

    erzeuge_impulse(zeit, gebiete, im_abi_feld = new Set(), haltung = null, heilsamkeit = 0) {
      haltung = haltung === null ? gebiete : haltung;
      let staerkster_einfluss = 0;
      for (const g of gebiete) staerkster_einfluss = Math.max(staerkster_einfluss, this.einfluss(g));
      const mitnahme = 1 - staerkster_einfluss;

      const staerken = new Map();
      const aus_haltung = new Map(); // Thema -> Stärke aus der Haltung der MBI
      const eigene = new Map(); // Gebiet der MBI -> Thema -> Stärke
      const herkunft = new Map(); // Thema -> Gebiet -> Stärke
      const enthalten = new Map(); // Haltung -> Thema -> Stärke
      const in_der_erinnerung = gebiete.includes(ERINNERUNG);

      for (const e of this.erfahrungen) {
        let beitrag;
        let mitgefuehrt;
        if (in_der_erinnerung && e.zeit < zeit) {
          beitrag = e.staerke;
          mitgefuehrt = false;
        } else {
          const nachklang = e.nachklang == null ? this.nachklang : e.nachklang;
          beitrag = e.staerke * Math.pow(nachklang, zeit - e.zeit);
          mitgefuehrt = !gebiete.some((g) => gehoert_zum_gebiet(e, g, im_abi_feld));
          if (mitgefuehrt) beitrag *= mitnahme;
        }
        plus(staerken, e.thema, beitrag);
        const zugehoerig = haltung.filter(
          (g) => (g === ERINNERUNG && e.zeit < zeit) || gehoert_zum_gebiet(e, g, im_abi_feld)
        );
        if (zugehoerig.length) plus(aus_haltung, e.thema, beitrag);
        for (const g of zugehoerig) plus(unterkarte(eigene, g), e.thema, beitrag);
        for (const g of e.gebiete) {
          if (mitgefuehrt) {
            const name = gebiete.includes(g) ? FRUEHER : g;
            plus(unterkarte(herkunft, e.thema), name, beitrag);
          }
          if (!gebiete.includes(g) && !BESONDERE_GEBIETE.includes(g)) {
            plus(unterkarte(enthalten, g), e.thema, beitrag);
          }
        }
      }

      // Was zusammen erlebt wurde, taucht verstärkt zusammen auf.
      const basis = new Map(staerken);
      for (const [paar, anzahl] of this.verknuepfungen) {
        const [a, b] = paar.split("\u0000");
        const bindung = 1 - Math.pow(0.5, anzahl);
        for (const [thema, partner] of [[a, b], [b, a]]) {
          const zug = this.kopplung * bindung * Math.min(1, Math.max(0, basis.get(partner) || 0));
          if (zug) plus(staerken, thema, zug);
        }
      }

      const themen = new Map();
      for (const [thema, roh] of staerken) {
        const staerke = roh * this.haltungsfaktor(thema, heilsamkeit);
        if (staerke < MINDESTSTAERKE) continue;
        const je_gebiet = herkunft.get(thema) || new Map();
        const mitgebracht_aus = [...je_gebiet.keys()]
          .filter((g) => je_gebiet.get(g) >= MINDESTSTAERKE)
          .sort((x, y) => je_gebiet.get(y) - je_gebiet.get(x));
        const eigenes = basis.get(thema) || 0;
        themen.set(thema, {
          thema,
          staerke: Math.min(1, staerke),
          mitgebracht_aus,
          haltung: false,
          aus_haltung: eigenes > 0 && 2 * (aus_haltung.get(thema) || 0) >= eigenes,
          gewohnheit: this.gewohnheit.get(thema) || 0,
          faerbung: this.faerbung(thema),
        });
      }

      // Eine Haltung, die das AUI enthält, liegt selbst als Impuls im Feld.
      for (const [frueher, je_thema] of enthalten) {
        let staerke = Math.max(...je_thema.values()) * this.haltungsfaktor(frueher, heilsamkeit);
        if (themen.has(frueher)) staerke = Math.max(staerke, themen.get(frueher).staerke);
        if (staerke >= MINDESTSTAERKE) {
          const eintrag = {
            thema: frueher,
            staerke: Math.min(1, staerke),
            mitgebracht_aus: [],
            haltung: true,
            aus_haltung: false,
            gewohnheit: this.gewohnheit.get(frueher) || 0,
            faerbung: this.faerbung(frueher),
          };
          // Wie in Python: Ein vorhandener Eintrag behält seinen Platz in der Reihenfolge.
          themen.set(frueher, eintrag);
        }
      }

      this.feld = [...themen.values()].sort((x, y) => y.staerke - x.staerke);
      this._staerken = new Map(this.feld.map((i) => [i.thema, i.staerke]));
      this._eigene = eigene;
      return this.feld;
    }

    gewicht(gebiet, gebiete) {
      if (this._staerken.has(gebiet)) return this._staerken.get(gebiet);
      let staerkstes = 0;
      for (const [thema, staerke] of this._eigene.get(gebiet) || []) {
        if (!gebiete.includes(thema)) staerkstes = Math.max(staerkstes, staerke);
      }
      return Math.min(1, staerkstes);
    }
  }

  /* ABI. Automatisch und bewusst: ein eigenes Feld, das an das des AUI angrenzt. */
  class AutomatischeBewussteIntention {
    constructor(o = {}) {
      this.schwelle = o.schwelle ?? 0.3;
      this.chance = o.chance ?? 0.25;
      this.zufallshebel = o.zufallshebel ?? 4.0;
      this.ruhe = o.ruhe ?? 0.5;
      this.zufall = o.zufall ?? Math;
      this.feld = [];
      this.gebiete_ohne_mbi = [];
    }

    nimm_wahr(aui_feld) {
      this.feld = aui_feld.filter((i) => i.staerke >= this.schwelle);
      return this.feld;
    }

    gebietschance(faerbung, heilsamkeit) {
      const faktor = zustandsfaktor(heilsamkeit, faerbung, this.zufallshebel, this.ruhe);
      return Math.min(1, this.chance * faktor);
    }

    lasse_gebiete_entstehen(umgang, gebiete_der_mbi, heilsamkeit = 0) {
      const faerbungen = new Map(this.feld.filter((i) => !i.haltung).map((i) => [i.thema, i.faerbung]));
      const im_feld = [...faerbungen.keys()];
      const sich_selbst_ueberlassen = (thema) =>
        (umgang.get(thema) || Umgang.WEDER_NOCH) === Umgang.WEDER_NOCH &&
        !gebiete_der_mbi.includes(thema);

      this.gebiete_ohne_mbi = this.gebiete_ohne_mbi.filter(
        (g) => im_feld.includes(g) && sich_selbst_ueberlassen(g)
      );
      for (const thema of im_feld) {
        if (
          sich_selbst_ueberlassen(thema) &&
          !this.gebiete_ohne_mbi.includes(thema) &&
          this.zufall.random() < this.gebietschance(faerbungen.get(thema), heilsamkeit)
        ) {
          this.gebiete_ohne_mbi.push(thema);
        }
      }
    }
  }

  /* MBI. Manuell und bewusst: was man willentlich lenkt. */
  class ManuelleBewussteIntention {
    constructor(gebiet, o = {}) {
      this.gebiete = [gebiet];
      this.haltungsschritt = o.haltungsschritt ?? 0.2;
      this.sog = o.sog === undefined ? 1.0 : o.sog; // null schaltet das Mitreißen ab
      this.anfaelligkeit = o.anfaelligkeit ?? 0.5;
      this.uebergang = o.uebergang ?? 0.25;
      this.restchance = o.restchance ?? 0.05;
      this.zufall = o.zufall ?? Math;
      this.mitgerissen = [];
      this.heilsamkeit = 0;
    }

    sogchance(staerke, heilsamkeit) {
      if (this.sog === null) return 0;
      const rampe = (h) => {
        const voll_ab = this.sog * (1 + this.anfaelligkeit * h);
        return Math.max(0, Math.min(1, 1 - (voll_ab - staerke) / this.uebergang));
      };
      let chance = Math.min(rampe(heilsamkeit), 1 - this.restchance);
      if (rampe(0) > 0) chance = Math.max(chance, this.restchance);
      return runde(chance);
    }

    _verschiebe(richtung) {
      const verschoben = this.heilsamkeit + richtung * this.haltungsschritt;
      this.heilsamkeit = runde(Math.max(-1, Math.min(1, verschoben)));
    }

    /* `entscheidung`: { umgang: Map oder Objekt Thema -> Umgang, themenwechsel: Gebiet oder null } */
    richte_aus(lage, entscheidung) {
      if (entscheidung.themenwechsel) {
        this.gebiete = [entscheidung.themenwechsel];
        this._verschiebe(+1);
      }

      const im_feld = new Map(lage.abi_feld.map((i) => [i.thema, i]));
      const gewaehlt =
        entscheidung.umgang instanceof Map
          ? entscheidung.umgang
          : new Map(Object.entries(entscheidung.umgang || {}));
      const umgang = new Map([...gewaehlt].filter(([thema]) => im_feld.has(thema)));

      this.mitgerissen = [];
      for (const impuls of lage.abi_feld) {
        if ((umgang.get(impuls.thema) || Umgang.WEDER_NOCH) !== Umgang.WEDER_NOCH) continue;
        const chance = this.sogchance(impuls.staerke, lage.heilsamkeit);
        if (chance > 0 && this.zufall.random() < chance) {
          umgang.set(impuls.thema, Umgang.VERLANGEN);
          this.mitgerissen.push(impuls.thema);
        }
      }

      for (const [thema, art] of umgang) {
        if (art !== Umgang.WEDER_NOCH) this._verschiebe(ist_unheilsam(art) ? -1 : +1);
        if (ist_engage(art)) {
          if (!im_feld.get(thema).aus_haltung) this.gebiete = [thema];
          else if (!this.gebiete.includes(thema)) this.gebiete.push(thema);
        } else if (ist_disengage(art) && this.gebiete.includes(thema)) {
          this.gebiete.splice(this.gebiete.indexOf(thema), 1);
        }
      }
      if (!this.gebiete.length) this.gebiete = [JETZIGE_ERFAHRUNG];
      return umgang;
    }

    verdraenge(gewicht, kapazitaet, geschuetzt = []) {
      const verdraengt = [];
      while (this.gebiete.length > 1) {
        const gewichte = new Map(this.gebiete.map((g) => [g, gewicht(g, this.gebiete)]));
        let summe = 0;
        for (const wert of gewichte.values()) summe += wert;
        if (summe < kapazitaet) break;
        const kandidaten = this.gebiete.filter((g) => !geschuetzt.includes(g));
        if (!kandidaten.length) break;
        let schwaechstes = kandidaten[0];
        for (const g of kandidaten) if (gewichte.get(g) < gewichte.get(schwaechstes)) schwaechstes = g;
        this.gebiete.splice(this.gebiete.indexOf(schwaechstes), 1);
        verdraengt.push(schwaechstes);
      }
      return verdraengt;
    }
  }

  /* Die drei Layer zusammen. */
  class Geist {
    constructor(gebiet, o = {}) {
      const zufall = o.zufall ?? Math;
      this.kapazitaet = o.kapazitaet ?? 1.0;
      this.wirkung = o.wirkung ?? STANDARD_WIRKUNG;
      this.unterbewusstsein = new Unterbewusstsein({ ...o, zufall });
      this.automatisch = new AutomatischeBewussteIntention({
        schwelle: o.schwelle,
        chance: o.chance,
        ruhe: o.ruhe,
        zufall,
      });
      this.manuell = new ManuelleBewussteIntention(gebiet, {
        haltungsschritt: o.haltungsschritt,
        sog: o.sog === false ? null : this.kapazitaet,
        zufall,
      });
      this.zeit = 0;
      this._offen = null; // der begonnene, noch nicht entschiedene Moment
    }

    /* Erste Hälfte des Moments: Was erlebt wird, geht ins AUI, die Felder entstehen. */
    beginne(sinne = {}, emotion = {}, koerper = {}) {
      if (this._offen) throw new Error("Der laufende Moment ist noch nicht entschieden.");
      const gebiete = [...this.manuell.gebiete];
      const gebiete_ohne_mbi = [...this.automatisch.gebiete_ohne_mbi];
      for (const [gebiet, erlebtes] of [[SINNE, sinne], [EMOTION, emotion], [KOERPER, koerper]]) {
        for (const [thema, staerke] of Object.entries(erlebtes)) {
          this.unterbewusstsein.erlebe({ thema, staerke, zeit: this.zeit, gebiete: [gebiet] });
        }
      }

      const bisher_im_abi_feld = new Set(this.automatisch.feld.map((i) => i.thema));
      const heilsamkeit = this.manuell.heilsamkeit;
      const aufgekommen = this.unterbewusstsein.lasse_aufkommen(this.zeit, heilsamkeit);
      const aktiv = [...gebiete, ...gebiete_ohne_mbi];
      const einfluss = {};
      for (const g of aktiv) einfluss[g] = this.unterbewusstsein.einfluss(g);
      const aui_feld = this.unterbewusstsein.erzeuge_impulse(
        this.zeit, aktiv, bisher_im_abi_feld, gebiete, heilsamkeit
      );
      const abi_feld = this.automatisch.nimm_wahr(aui_feld);
      this.unterbewusstsein.verknuepfe([
        ...Object.keys(sinne), ...Object.keys(emotion), ...Object.keys(koerper),
      ]);

      const lage = {
        zeit: this.zeit,
        gebiete,
        gebiete_ohne_mbi,
        aui_feld,
        abi_feld,
        sinne,
        emotion,
        koerper,
        heilsamkeit,
        einfluss,
        aufgekommen,
      };
      this._offen = lage;
      return lage;
    }

    /* Zweite Hälfte: Die MBI geht mit dem um, was auftaucht, und der Moment endet. */
    entscheide(entscheidung = {}) {
      const lage = this._offen;
      if (!lage) throw new Error("Es gibt keinen begonnenen Moment.");
      this._offen = null;
      const aui = this.unterbewusstsein;
      const umgang = this.manuell.richte_aus(lage, entscheidung);

      for (const [thema, art] of umgang) {
        let wirkung = this.wirkung[art];
        if (wirkung < 0) {
          const auftauchend = lage.abi_feld.find((i) => i.thema === thema);
          wirkung = Math.max(wirkung, -(auftauchend ? auftauchend.staerke : 0));
        }
        if (art !== Umgang.WEDER_NOCH) {
          aui.uebe(thema, ist_engage(art) ? 1 : -1);
          aui.faerbe(thema, ist_unheilsam(art) ? -1 : 1);
        }
        if (wirkung) aui.erlebe({ thema, staerke: wirkung, zeit: this.zeit, gebiete: lage.gebiete });
      }

      const gerade_betreten = this.manuell.gebiete.filter((g) => !lage.gebiete.includes(g));
      const verdraengt = this.manuell.verdraenge(
        (gebiet, gebiete) => aui.gewicht(gebiet, gebiete), this.kapazitaet, gerade_betreten
      );
      this.automatisch.lasse_gebiete_entstehen(umgang, this.manuell.gebiete, lage.heilsamkeit);

      const moment = {
        ...lage,
        umgang: Object.fromEntries(umgang),
        mitgerissen: [...this.manuell.mitgerissen],
        heilsamkeit_danach: this.manuell.heilsamkeit,
        verdraengt,
        gebiete_danach: [...this.manuell.gebiete],
        gebiete_ohne_mbi_danach: [...this.automatisch.gebiete_ohne_mbi],
      };
      this.zeit += 1;
      return moment;
    }

    /* Ein ganzer Moment auf einmal. `entscheider` bekommt die Lage wie in Python. */
    schritt(erlebtes = {}, entscheider = () => ({})) {
      const lage = this.beginne(erlebtes.sinne || {}, erlebtes.emotion || {}, erlebtes.koerper || {});
      return this.entscheide(entscheider(lage) || {});
    }
  }

  return {
    MINDESTSTAERKE,
    SINNE,
    JETZIGE_ERFAHRUNG,
    ERINNERUNG,
    EMOTION,
    KOERPER,
    BESONDERE_GEBIETE,
    Umgang,
    STANDARD_WIRKUNG,
    zustandsfaktor,
    Unterbewusstsein,
    AutomatischeBewussteIntention,
    ManuelleBewussteIntention,
    Geist,
  };
});
