/* Spielt Szenarien aus tests/test_web.py mit der Browser-Fassung des Modells nach.
 * Liest die Szenarien als JSON von der Standardeingabe und gibt je Szenario die
 * Momente als JSON aus.
 */
const { Geist } = require("../web/geist.js");

const szenarien = JSON.parse(require("fs").readFileSync(0, "utf8"));

const ergebnisse = szenarien.map((szenario) => {
  let stelle = 0;
  const zufall = { random: () => szenario.zufall[stelle++ % szenario.zufall.length] };
  const geist = new Geist(szenario.gebiet, { ...szenario.optionen, zufall });
  for (const erfahrung of szenario.vorher) geist.unterbewusstsein.erlebe(erfahrung);
  return szenario.momente.map((m) => {
    geist.beginne(m.sinne, m.emotion, m.koerper);
    return geist.entscheide(m.entscheidung);
  });
});

process.stdout.write(JSON.stringify(ergebnisse));
