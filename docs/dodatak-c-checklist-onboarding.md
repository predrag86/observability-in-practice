# Dodatak C — Checklist za onboarding novog servisa na observability

Ova lista destiluje redosled koji se pokazao ispravnim kroz celu knjigu —
od prve linije instrumentacije do prvog alarma i prvog runbook-a — u
oblik koji se može direktno primeniti na sledeći servis koji treba
uključiti. Nije zamišljena da se sprovede linearno bez razmišljanja;
kao što je Poglavlje 29 pokazalo, stvarnost će otvoriti pitanja koja
ovaj spisak ne predviđa. Koristi je kao polaznu tačku, ne kao ugovor.

## Faza 0 — Pre nego što se napiše ijedna linija koda

- [ ] Da li ovaj servis PRIRODNO spada u postojeći obrazac instrumentacije
  (isti jezik/runtime kao već onboardovani servisi), ili zahteva nov
  recept? Ako nov recept — planiraj dodatno vreme za pilot, ne pretpostavi
  da će postojeći recept "samo raditi".
- [ ] Proceni radijus dejstva ovog servisa u odnosu na već onboardovane —
  ovo određuje GDE u redosledu dolazi (Pravilo iz Poglavlja 29: najkritičniji
  deo sistema dolazi POSLEDNJI, kao politika, ne izuzetak).
- [ ] Proveri da li centralni prolaz (gateway) ima kapacitet za novog
  pošiljaoca BEZ degradacije postojećih — ako ne, autoskaliranje/kapacitet
  prolaza ide PRE fan-out-a na nove servise.

## Faza 1 — Osnovna instrumentacija

- [ ] Automatska (zero-code) instrumentacija za standardne pozive
  (HTTP/DB/red poruka) uključena.
- [ ] Prilagođeni rasponi (custom spans) dodati za POSLOVNI kontekst koji
  automatska instrumentacija ne vidi — da li je zadatak zaista USPEO, ne
  samo da li je izašao sa kodom 0?
- [ ] `service.name` i drugi resource atributi eksplicitno postavljeni —
  ne osloniti se na difoltnu vrednost detektora okruženja.
- [ ] Ako je zadatak kratkotrajan (zakazan/batch): bočni kolektor
  (sidecar) dodat da uhvati poslednje raspone pri gašenju, sa dovoljno
  dugim `stopTimeout` za graciozno flush-ovanje.

## Faza 2 — Provera pre nego što se veruje bilo čemu

- [ ] Ručno pokreni jedan prolaz servisa i POTVRDI u platformi za
  posmatranje da su sva tri signala (metrike, logovi, rasponi) stigla —
  ne pretpostaviti na osnovu "kod izgleda ispravno".
- [ ] Proveri da li je novi atribut/oznaka koju servis uvodi proverio
  kardinalnost PRE produkcije (Dodatak A, Recept #11) — ne posle.
- [ ] Proveri da OTLP→Prometheus prevod imena metrika ne krije očekivanu
  metriku iza CamelCase sufiksa jedinice (Dodatak A, Recept #10).

## Faza 3 — Prvi alarm

- [ ] Definiši šta znači "uspešno, ali ništa nije urađeno" za OVAJ servis
  — spojen uslov (i pokrenuto, i bez izlaza), nikad prazan sam za sebe.
- [ ] Definiši grub, izlazni-kod alarm KAO PRIVREMENU meru dok se ne
  potvrdi da fini mehanizam radi — ali planiraj da ga ukloniš čim fini
  mehanizam prođe soak period, ne ostavi oba trajno.
- [ ] Dodeli nivo hitnosti (kritičan/standardan/tih) — nepoznat servis
  ide u standardan po difoltu (fail-safe), nikad tih po difoltu.
- [ ] Proveri da alarm koji prati OVAJ servis ne zavisi od ISTE
  infrastrukture čiji kvar pokušava da uhvati (watcher-nadživljava-
  posmatrano princip).

## Faza 4 — Prvi runbook

- [ ] Napiši runbook PRE prvog stvarnog incidenta, ne posle — čak i
  kratak, jedan-pasus runbook je bolji od praznog polja u trenutku kad
  je alarm već aktivan.
- [ ] Runbook mora imati deep-link direktno na relevantan prozor u
  platformi za posmatranje — ne opis "otvori dashboard i nađi
  odgovarajući panel".
- [ ] Runbook eksplicitno kaže KADA da eskalira dalje, ne samo šta da
  proba prvo.

## Faza 5 — Pre nego što se servis smatra "gotovim"

- [ ] Simuliraj barem jedan kvar namerno (ako je bezbedno) i proveri da
  li alarm STVARNO okine, ne samo da li bi trebalo da okine po definiciji.
- [ ] Dodaj servis u eksplicitnu listu "instrumentiranih" servisa koju
  koristi mehanizam alarmiranja za odlučivanje kakav nivo detalja da
  priloži u obaveštenje.
- [ ] Zapiši datum i verziju recepta korišćenog za onboarding — sledeći
  servis možda treba drugačiji recept, i ta razlika treba da bude vidljiva
  unazad.

## Faza 6 — Periodična provera (ne jednokratna)

- [ ] Ovaj servis ulazi u sledeću periodičnu reviziju programa (Poglavlje
  30) kao i svaki drugi — nema "jednom onboardovan, zauvek gotov".
- [ ] Ako je alarm ovog servisa ikad tih duže od očekivanog perioda
  aktivnosti, to je razlog za proveru, ne razlog za spokoj (Dodatak B —
  dead man's switch).
