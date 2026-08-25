# Deo I — Osnove

## Pre nego što krenemo: tri odluke koje se donose samo jednom

Uvod knjige je već postavio scenu — koji sistem knjiga prati, odakle
dolazi materijal, kako je svako poglavlje strukturirano. Deo I je mesto
gde ta priča prestaje da bude samo kontekst i postaje **rečnik**: tri
poglavlja, tri odluke koje se u stvarnoj implementaciji donose tačno
jednom, na samom početku, i posle toga ih sve ostalo u knjizi
prećutno pretpostavlja kao rešene.

Redosled nije proizvoljan:

- **Poglavlje 1** postavlja pitanje pre bilo kog alata: šta uopšte znači
  "observability" kad se razlikuje od monitoringa koji je postojao i pre
  toga naziva — i zašto ta razlika nije kozmetička, nego menja šta se
  gradi prvo.
- **Poglavlje 2** uvodi OpenTelemetry ne kao biblioteku koju treba
  instalirati, nego kao mentalni model — zajednički jezik kojim svaki
  deo sistema, bez obzira ko ga je pisao, opisuje ono što meri. Bez ovog
  poglavlja, poglavlje 3 nema o čemu da odlučuje.
- **Poglavlje 3** je prvi put da knjiga stane na jedno tlo koje je čisto
  poslovno, ne tehničko: gde telemetrija fizički živi, ko je operativno
  drži i po kojoj ceni — pitanje koje mora doći poslednje u ovom delu,
  jer se poređenje platformi ne može smisleno raditi dok se ne zna šta
  se uopšte šalje (Poglavlje 2) i zašto to nešto vredi meriti (Poglavlje 1).

Ovaj obrazac — prvo pojam, pa protokol, pa platforma — vredi zapamtiti,
jer se knjiga na njega ne vraća eksplicitno, ali ga svaki naredni deo
tiho koristi. Deo II, koji sledi, ne postavlja ponovo pitanje "šta je
observability" niti "zašto OpenTelemetry" — pretpostavlja da su oba
pitanja iza nas, i prelazi direktno na to kako se signal stvarno
prikuplja iz svakog sloja sistema.
