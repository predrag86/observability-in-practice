# Poglavlje 26 — Observability kao kontrola usklađenosti (SOC 2 primer)

Sanitarni inspektor koji dolazi u restoran ne nosi sa sobom jedan
univerzalni recept za bezbednu kuhinju, isti za svaki restoran u gradu.
Umesto toga, dobar sistem inspekcije traži da svaki restoran unapred
napiše **sopstveni** plan bezbednosti hrane — na kojoj temperaturi se čuva
piletina, ko proverava rok trajanja, šta se radi kad frižider otkaže — i
onda inspektor proverava tačno jedno: da li restoran stvarno radi ono što
je taj plan obećao. Restoran koji je napisao ambiciozan plan pa ga ne
prati dobija gore od restorana koji je napisao skromniji, ali potpuno
tačan plan. Poenta inspekcije nije "da li si najbolji restoran u gradu."
Poenta je: da li je ono što pišeš na vratima istina.

## 26.1 Pitanje na koje ovo poglavlje odgovara

Kako se monitoring i alarmiranje uopšte mapiraju na kriterijume poverenja
koje traži bezbednosni standard poput SOC 2 — i, važnije od same mape,
zašto usaglašenost nije o tome da li ispunjavaš spoljni katalog kontrola,
nego da li radiš ono što tvrdiš da radiš?

## 26.2 Kako je to urađeno — praktičan pregled

### Dva pravca odnosa, ne jedan

Implementacija polazi od jasno formulisanog uvida: observability i
usaglašenost stoje u dvosmernom odnosu, ne jednosmernom.

- **Observability je dokaz kontrole.** Sam sistem za alarmiranje —
  detekcija anomalija, eskalacija, odgovor — je operativni dokaz da
  organizacija zaista nadzire svoje komponente i reaguje na incidente,
  tačno ono što kriterijumi poverenja traže od kontrola nadzora sistema.
- **Observability je istovremeno i obaveza kontrole.** Ista ta telemetrija
  nosi lične podatke (identitet korisnika na trejsovima i logovima,
  potencijalno de-anonimizovane sesije iz pregledača) — što znači da sama
  telemetrija postaje poverljiva informacija koju treba štititi, ne samo
  alat kojim se nešto drugo štiti.

### Iskrena tabela stanja, ne uglačana priča za revizora

Centralni artefakt praktičnog dela je interna radna tabela koja mapira
svaku relevantnu oblast kontrole na tri kolone: kriterijum na koji se
oblast odnosi, **stvarno stanje** (obeleženo iskreno sa oznakom NA MESTU,
DELIMIČNO za "delimično ili nedokumentovano", PRAZNINA za "praznina"), i preostali rad
potreban da se praznina zatvori. Ova tabela je namerno pisana za interno
čitanje, ne za revizora — cilj je da svaka tvrdnja koju organizacija
kasnije izgovori revizoru bude već proverena unutar ove tabele, umesto da
se tabela piše da bi izgledala dobro.

Primer oblika (ilustrativan, ne stvaran spisak implementacije): jedna
oblast kontrole može biti potpuno na mestu (šifrovanje u tranzitu preko
TLS-a), druga delimično dokumentovana (ko tačno ima pristup konzoli
platforme za telemetriju, sa kojom ulogom, nije formalno popisano), a
treća potpuna praznina (ne postoji runbook koji bi, na zahtev, izbrisao
nečije lične podatke iz sistema za trejsove i logove). Vrednost tabele
nije u tome da svaka oznaka bude NA MESTU — vrednost je u tome da svaki znak bude tačan.

### Pitanje koje odlučuje šta uopšte ulazi u obim

Standard koji implementacija prati ima jednu obaveznu kategoriju
kriterijuma (bezbednost) i nekoliko opcionih (dostupnost, poverljivost,
integritet obrade, privatnost) koje organizacija bira da uključi ili ne.
Implementacija eksplicitno razmatra ovu odluku kao strateško pitanje, ne
kao formalnost: uključivanje opcione kategorije koju organizacija stvarno
ne ispunjava ne ostaje neprimećeno — naprotiv, proširuje obim revizije na
tu kategoriju, i svaka praznina u njoj postaje **dokumentovani nalaz**
umesto da jednostavno ne bude deo priče. Zaključak implementacije: prva
runda usaglašenosti cilja samo obaveznu kategoriju (uz mogućnost dodavanja
uže kategorije koja se lakše ispunjava), dok se šira, zahtevnija kategorija
svesno odlaže dok konkretne popravke (poput pseudonimizacije iz prethodnog
poglavlja) stvarno ne slegnu.

### Jedna stvar koju revizor zapravo testira

Implementacija imenuje centralnu proveru koju revizor stvarno sprovodi:
**doslednost između onoga što organizacija javno tvrdi i onoga što
stvarno radi.** Standard ne propisuje da telemetrija mora biti
pseudonimizovana — ali ako bilo koji javni dokument (politika privatnosti,
odgovor na bezbednosni upitnik klijenta) tvrdi da se lični podaci
minimizuju ili pseudonimizuju, a stvarna telemetrija i dalje nosi sirov
identitet, to je razlika koju revizor otkriva i beleži kao izuzetak — bez
obzira na to da li je ta oblast uopšte formalno u obimu revizije.

![Kontrola posmatranja kao dvosmeran odnos: sistem alarmiranja je dokaz nadzora, ali telemetrija koju taj sistem nosi je istovremeno i poverljiv podatak koji sam treba zaštitu.](diagrams/ch26-dvosmeran-odnos.png){: width="85%" }

### Automatizovana akcija iz chat-a: token dozvoljava, kanal ograničava

Jedna kontrola u tabeli zaslužuje poseban osvrt jer pokazuje koliko duboko
mora ići analiza kad automatizacija dobije mogućnost da menja stanje sistema,
ne samo da ga posmatra. Alarm u kanalu za otkaze zadataka nosi dugme koje
pokreće **produkcioni** zadatak iznova — pravo pisanje u infrastrukturu,
pokrenuto direktno iz chat poruke. Mehanizam otkriva dva odvojena sloja
ovlašćenja, i implementacija je eksplicitno imenovala oba, umesto da tretira
"dugme radi" kao dovoljnu proveru.

Prvi sloj je tehnički neizbežan kompromis: okidač je **javni** URL bez
potpisivanja zahteva na strani platforme za razmenu poruka, jer ta platforma
nema mehanizam da potpiše zahtev standardnim protokolom za pristup oblaku.
Umesto toga, autentičnost dolazi od **sopstvenog** HMAC potpisa platforme za
razmenu poruka na svakom zahtevu, sa vremenskim prozorom od nekoliko minuta
koji sprečava da neko snimljenu poruku pošalje ponovo kasnije — i mehanizam
namerno **odbija** zahtev ako tajni ključ za proveru potpisa nije podešen,
umesto da propusti zahtev bez provere. Drugi sloj je suptilniji: platforma za
razmenu poruka nema mehanizam za odobrenje na nivou pojedinačnog dugmeta — pa
je **privatnost samog kanala** jedina stvarna kontrola pristupa. Ko god je
član tog kanala može da pritisne dugme; ko nije, ne vidi ga uopšte. Formalna
lista ovlašćenja u sistemu za upravljanje identitetom je najuža moguća (samo
jedna izvršna funkcija sme da pokrene zadatak, sa ulogom ograničenom na tačno
tri uloge kojima sme da je dodeli) — ali ta lista ništa ne znači ako
članstvo u kanalu nije isto tako strogo kontrolisano i redovno pregledano.

Ovo je tačno vrsta uvida koji iskrena interna tabela treba da uhvati: kontrola
"ko sme da pokrene produkcionu akciju" ovde zapravo **nije jedna** kontrola
nego dve — tehnička (potpis, uloga, opseg dozvola) i organizaciona (ko je
član kanala) — i samo prva od te dve je proverljiva kroz kod i infrastrukturu.
Druga zavisi od discipline oko članstva u chat kanalu, što je lakše
zaboraviti da se redovno proveri.

![Dva odvojena sloja ovlašćenja za akciju pokrenutu iz chat-a: tehnički sloj (potpis, uloga, opseg dozvola) je proverljiv kroz kod, dok je organizacioni sloj (članstvo u kanalu) jedina stvarna kontrola pristupa dugmetu.](diagrams/ch26-lanac-ovlascenja.png){: width="82%" }

### Least-privilege za servise nije isto što i least-privilege za ljude

Ista tabela pokazuje obrazac koji se ponavlja kroz više redova: mašinska
strana pristupa je često strogo, proverljivo ograničena, dok je ljudska
strana istog sistema potpuno nedokumentovana. Pristupni tokeni servisa koji
šalju telemetriju žive u trezoru za tajne, dodeljeni sa najužim mogućim
opsegom po nameni — ovo je stanje koje se može proveriti čitanjem
konfiguracije, i implementacija ga otvoreno beleži kao **na mestu**. Ali ko
tačno ima interaktivan pristup samoj konzoli platforme za telemetriju, i sa
kojom ulogom, nije nigde formalno popisano — ovo ostaje **delimično**, ne
zato što je pristup nužno prevelik nego zato što niko ne može da dokaže
suprotno bez popisa.

Poenta koju implementacija imenuje: "kontrola pristupa" kao jedna stavka na
listi kontrola je pogrešno zrnasta jedinica merenja. Ona pokriva najmanje dva
nezavisna pitanja — da li su mašine ograničene na ono što im treba, i da li
su ljudi ograničeni na ono što im treba — i organizacija može imati potpuno
tačan odgovor na jedno pitanje dok nema nikakav odgovor na drugo. Tabela koja
beleži samo jednu, zbirnu ocenu za "pristup" bi sakrila tačno tu razliku;
tabela koja razdvaja mašinski i ljudski red čini prazninu vidljivom umesto da
je zamagli iza dela koji je već u redu.

## 26.3 Analitički deo — usaglašenost kao samo-doslednost, ne spoljni katalog

### Zvanična struktura kriterijuma potvrđuje dvoslojnu podelu

Zvanična struktura kriterijuma poverenja definiše jednu obaveznu kategoriju
(zajednički kriterijumi, organizovani u devet serija) i četiri opcione
kategorije birane po diskrecionom pravu organizacije, samo kada su stvarno
relevantne za usluge koje se pružaju. Konkretno, kriterijumi unutar serije
koja pokriva rad sistema — nadzor komponenti radi otkrivanja anomalija,
procena da li anomalija predstavlja bezbednosni događaj, i odgovor kroz
definisan program — direktno odgovaraju onome što sistem alarmiranja i
eskalacije implementacije radi svakog dana. Ovo potvrđuje da je
implementacija ispravno prepoznala sopstveni sistem alarmiranja kao
**pozitivan dokaz**, ne samo kao operativni alat.

### "Atestacija, ne sertifikacija" je zvanično, precizno formulisana razlika

Zvanična razlika, potvrđena u industrijskoj literaturi o samom standardu,
jeste da ovo nije sertifikacija sa spoljnim, univerzalnim pragom prolaska —
to je atestacija: licenciran revizor testira da li su kontrole, **onako
kako ih je organizacija sama dokumentovala**, stvarno na mestu i, u
zahtevnijem tipu izveštaja, da li dosledno funkcionišu kroz vreme. Ne
postoji jedan tačan odgovor na "da li je organizacija usaglašena" nezavisno
od toga šta je ta organizacija sama tvrdila da radi — što je tačno uvid
koji implementacija formuliše kao "jedina stvar koju revizor zapravo
testira ovde."

### Odluka o opcionim kategorijama je dokumentovano osetljiva tačka

Industrijska smernica o biranju opcionih kategorija eksplicitno upozorava
da uključivanje kategorije koju organizacija nije stvarno spremna da
ispuni — tipičan primer je najzahtevnija kategorija, ona koja pokriva
privatnost ličnih podataka, uključena bez realnog programa pristanka i
prava subjekta podataka — stvara nepotreban rizik izloženosti: pošto je ta
kategorija sada u obimu, revizor je testira, i svaka praznina postaje
zabeležen izuzetak umesto da jednostavno ne bude deo priče. Ovo potvrđuje
tačno logiku kojom se implementacija vodila pri odlaganju šire kategorije.

### Retencija i pravo na brisanje ne znače ono što se često pretpostavlja

Vodeći princip iz iste industrijske smernice jeste da standard ne propisuje
univerzalan rok čuvanja niti obaveznu implementaciju prava na brisanje po
uzoru na druge regulative — princip je da lični ili poverljivi podaci budu
čuvani ne duže nego što je stvarno potrebno za deklarisanu svrhu, i da
revizor testira da li stvarna praksa uništavanja podataka odgovara
**sopstvenoj** deklarisanoj politici organizacije, ne nekom spoljašnjem
kalendaru. Ovo znači da praznina koju implementacija beleži u sopstvenoj
tabeli (nedostatak formalno dokumentovane retencije po tipu signala) nije
propust prema standardu direktno — ali postaje propust onog trenutka kad
organizacija bilo gde javno tvrdi suprotno.

### Kontrafaktički scenario: šta bi "uglačana priča" propustila

Zamislimo tim koji je, umesto iskrene interne tabele, direktno pisao
odgovore za revizora — birajući formulacije koje zvuče sigurno, bez
prethodne interne provere da li je svaka tvrdnja stvarno tačna. Prva
prava revizija bi otkrila razliku između napisanog i stvarnog, u
najgorem mogućem trenutku — pred revizorom, sa reputacionim i ugovornim
posledicama, umesto interno, gde se praznina može zatvoriti pre nego što
iko spolja uopšte postavi pitanje. Iskrena interna tabela sa DELIMIČNO i PRAZNINA
oznakama nije priznanje slabosti prema spoljnom svetu — ona je razlog zašto
spoljni svet nikad ne mora da vidi iznenađenje.

Vratimo se sanitarnom inspektoru s početka poglavlja. Restoran koji je
napisao skroman, ali potpuno tačan plan — "čuvamo piletinu na ovoj
temperaturi, proveravamo je svaki dan u sedam ujutru" — i zaista to radi,
prolazi inspekciju bolje od restorana koji je napisao ambiciozniji plan pa
ga napola prati. Usaglašenost nikad nije bila takmičenje u tome ko ima
najimpresivniji plan. Bila je, od početka, pitanje da li plan i stvarnost
govore istu priču.

## 26.4 Skupljena pravila iz ovog poglavlja

- Vodi internu, iskrenu tabelu stanja kontrola (NA MESTU / DELIMIČNO / PRAZNINA) pre nego što bilo
  šta stigne do revizora — cilj je da svaka tvrdnja bude već proverena
  interno, ne da tabela izgleda dobro.
- Tretiraj sopstveni sistem alarmiranja i eskalacije kao pozitivan dokaz
  za kriterijume nadzora sistema — dokumentuj ga eksplicitno kao takav,
  ne samo kao operativni alat.
- Ne uključuj opcionu kategoriju kriterijuma koju stvarno ne ispunjavaš —
  uključivanje je ono što otvara obim revizije, i svaka praznina u toj
  kategoriji postaje zabeležen izuzetak tek kad je kategorija u obimu.
- Zapamti da revizor testira doslednost između javnih tvrdnji i stvarne
  prakse, ne ispunjenost univerzalnog spoljnog kataloga — svaka javna
  tvrdnja o minimizaciji ili zaštiti podataka mora biti podržana stvarnim
  stanjem, ne samo namerom.
- Uskladi retenciju i praksu brisanja sa onim što stvarno **pišeš** da
  radiš, ne sa onim što bi u idealnom svetu trebalo da radiš — praznina
  postaje nalaz samo kad tvrdnja i stvarnost krenu različitim putem.
- Kad automatizacija iz chat-a sme da menja stanje produkcije, imenuj oba
  sloja ovlašćenja odvojeno — tehnički (potpis, uloga, opseg dozvola) i
  organizacioni (ko je član kanala koji vidi dugme) — jer prvi je proverljiv
  kroz kod, a drugi zavisi od discipline koja se lako zaboravi.
- Ne beleži "kontrolu pristupa" kao jednu zbirnu stavku — razdvoji mašinsku
  stranu (tokeni, opseg dozvola) od ljudske strane (ko ima interaktivan
  pristup, sa kojom ulogom) — organizacija često ima tačan odgovor na jedno
  pitanje dok nema nikakav na drugo, i zbirna ocena tu razliku sakriva.

## 26.5 Vežba za čitaoca

Pronađi jednu javnu tvrdnju tvog tima ili organizacije o tome kako se
podaci štite, čuvaju, ili minimizuju — u politici privatnosti, u
odgovoru na upitnik klijenta, ili čak u internoj dokumentaciji koja se
deli spolja. Proveri, iskreno i konkretno, da li stvarna telemetrija i
stvarna praksa danas zaista rade ono što ta tvrdnja kaže. Ako ne rade,
to je razlika koju vredi zatvoriti pre nego što je neko drugi otkrije.

---

### Izvori korišćeni u analitičkom delu

- [2017 Trust Services Criteria with Revised Points of Focus — AICPA & CIMA](https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022)
- [SOC 2 CC7.2 — Monitoring of System Components for Anomalies](https://www.cyberday.ai/requirement/soc-2-cc7-2-monitoring-of-system-components-for-anomalies)
- [SOC 2 CC7.4 — Responding to Identified Security Incidents](https://www.cyberday.ai/requirement/soc-2-cc7-4-responding-to-identified-security-incidents)
- [Is SOC 2 a Certification or an Attestation? — Vanta](https://www.vanta.com/collection/soc-2/is-soc-2-a-certification-or-attestation)
- [SOC 2 Trust Services Categories: Do You Need Privacy or Just Confidentiality? — Sage Audits](https://sageaudits.com/blog/2026/05/01/soc-2-trust-services-categories-do-you-need-privacy-or-just-confidentiality/)
- [Data Retention Policy and SOC 2 — Linford & Co](https://linfordco.com/blog/data-retention-policy-soc-2/)
