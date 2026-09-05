# Poglavlje 32 — Zaključak: skupljena pravila

Avion nosi dva potpuno različita sistema za beleženje sopstvenog stanja
— instrumenti u kokpitu koji odgovaraju na pitanja postavljena unapred,
i crna kutija koja ne zna šta će pokvariti let, ali garantuje da će, kad
se to dogodi, dokaz postojati. Tom razlikom je ova knjiga počela, jer je
to razlika koja menja šta se gradi prvo.

Trideset i jedno poglavlje kasnije, vredi reći jasno šta se od tada nije
promenilo: ni jedan alat, ni jedan dashboard, ni jedna arhitektura
opisana u ovoj knjizi nije vredna sama po sebi. Vredna je jedino onoliko
koliko pouzdano odgovara na pitanje koje niko nije znao da postavi
unapred. Instrumenti u kokpitu i dalje imaju svoje mesto — alarm mora da
zna unapred šta je normalno, da bi prijavio kad nešto to nije. Ali svaka
ozbiljna implementacija u ovoj knjizi je, u jednom trenutku, otkrila
granicu instrumenta i posegla za crnom kutijom — za sposobnošću da se
postavi pitanje koje niko nije predvideo, o incidentu koji tek treba da
se dogodi.

Ono što sledi nije rezime poglavlja. To je gusta lista pravila
prikupljenih usput, organizovana po delovima knjige, zamišljena da se
otcepi i zalepi iznad monitora — referenca za trenutak kad se donosi
odluka, ne štivo za čitanje unapred.

## Osnove

- Monitoring odgovara na pitanja postavljena unapred; observability
  odgovara na pitanja postavljena posle, o incidentu koji nisi mogao
  dovoljno precizno da predvidiš da bi za njega napravio poseban alarm
  — a najskuplja poglavlja u svakom sistemu su ona za koja niko nije
  znao da postave pitanje unapred.
- Tri signala (metrike, logovi, rasponi) nisu tri nezavisna alata —
  vredni su onoliko koliko se mogu povezati preko istog konteksta, u
  istom trenutku istrage.
- Kardinalnost je trošak koji se plaća unapred za pitanja koja možda
  nikad nećeš postaviti — svaka nova oznaka mora opravdati sopstveno
  postojanje pre nego što uđe u produkciju, ne posle.

## Arhitektura prikupljanja

- Watcher signal nikad ne sme zavisiti od infrastrukture koju posmatra
  — alarm koji prati da li je sam sistem posmatranja živ mora imati
  nezavisan put do čoveka, jer je upravo taj trenutak kad standardni
  put najverovatnije već ne radi.
- Centralni prolaz (gateway) postoji da apsorbuje složenost koju bi
  inače svaki pošiljalac morao sam da nosi — kredencijale, uzorkovanje,
  usmeravanje — ali sam postaje tačka otkaza ako nije autoscaliran,
  meren i testiran isto strogo kao ono što kroz njega prolazi.
- Bez bočnog kolektora (sidecar) gube se poslednji rasponi pri gašenju
  zadatka — graciozno gašenje mora biti dokazano merenjem, ne
  pretpostavljeno jer "trebalo bi da radi".

## Obrada, kardinalnost, troškovi

- Svaka promena kardinalnosti mora imati merenje pre i posle, i
  trivijalan rollback — bez oba, promena je opklada, ne inženjerska
  odluka.
- Uzorkovanje na izvoru mora biti svesno onoga što tek treba da se
  dogodi, ne samo onoga što se već dogodilo — greška koja se prvi put
  javlja mora proći, čak i kad opšte pravilo kaže "smanji".
- Trošak posmatranja koji raste brže od sistema koji se posmatra je
  sopstveni signal koji zaslužuje sopstveni dashboard — ne uzgredna
  linija u mesečnom računu.

## Alarmiranje, SLO, incidenti

- Alarm koji nikad ne okine je isto toliko sumnjiv koliko i sistem koji
  nikad ne pada — dok se ne proveri da li bi zaista okinuo kad treba,
  tišina nije dokaz zdravlja.
- SLO mora biti izgrađen na signalu otpornom na šum koji ne znači kvar
  (restart, deploy, planirano održavanje) — inače budžet greške troši
  svaku rutinsku promenu jednako kao stvaran incident.
- Postmortem je formalni kanal kroz koji novo saznanje ulazi u
  postojeći plan — akcione stavke iz njega se prioritizuju kao i svaki
  drugi rad, ne ostavljaju u dokumentu koji niko ne prati.

## Domenske studije slučaja

- Dve nezavisne ravni posmatranja (spoljna i unutrašnja) retko su
  potpune jedna bez druge — svaka vidi drugačiju klasu kvara, i nijedna
  nije nadskup one druge.
- Model potpunosti (pokrenuto / proizvelo izlaz / zašto nije) je
  ispravniji okvir za zakazane zadatke od standardnog obrasca za
  servise koji stalno primaju saobraćaj — "uspešno završeno, ali
  prazno" mora biti spojen uslov, nikad prazan sam za sebe.
- Alarm o svežini podataka spoljnog servisa mora biti uslovljen
  zasebnom metrikom "da li je kolektor živ" — bez tog uslova, mrtav
  kolektor izgleda identično katastrofalnom prekidu dotoka.

## Upravljanje, usklađenost, zrelost

- Identifikator OSOBE i identifikator IMOVINE nad kojom je nešto
  urađeno su različite kategorije — prvi se pseudonimizuje ili
  briše, drugi se namerno i dalje beleži, jer identifikuje šta je
  urađeno, ne ko je uradio.
- Ono što revizor stvarno testira nije da li je sve savršeno, nego
  doslednost između onoga što se javno tvrdi i onoga što se stvarno
  radi — iskrena interna tabela stanja je dokaz te doslednosti, ne
  priznanje slabosti.
- Kratak rangiran spisak po domenu je koristan samo ako se iz njega
  briše kad je nešto stvarno završeno — arhiviranje precrtanih stavki
  vraća isti šum koji je spisak trebalo da ukloni.
- AI agent sa generičkim znanjem sistema posmatranja dolazi tačno do
  mesta gde je potreban specifičan uvid u konkretan sistem — sloj
  konteksta, ne pristup alatima, je ono što razlikuje tačan odgovor od
  samouverenog pogrešnog.
- Redosled uvođenja u produkciju ide po radijusu dejstva, ne po
  tehničkoj pogodnosti — najkritičniji deo sistema dolazi poslednji,
  kao politika zapisana unapred, ne izuzetak po slučaju.
- Periodična revizija mora ponovo meriti SVAKU brojku, ne samo dodavati
  nove nalaze na stari spisak — a kad je prošli nalaz bio pogrešan, to
  se priznaje otvoreno, sa uzrokom greške, ne tiho prepisuje.

## Poslednja rečenica

Nijedno pravilo sa ove liste nije bilo očigledno unapred. Svako je
naučeno tako što je nešto zaista pošlo po zlu, ili tako što je neko
posumnjao u tišinu koja je izgledala kao zdravlje, pa proverio. To je,
u suštini, cela poenta observability-ja — ne sistem koji zna sve unapred,
nego sistem koji, kad dođe pitanje koje niko nije predvideo, ima gde da
potraži odgovor.
