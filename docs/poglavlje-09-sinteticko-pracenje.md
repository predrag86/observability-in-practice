# Poglavlje 9 — Sintetičko (black-box) praćenje

Čuvar svetionika ne čeka da se pojavi brod da bi proverio da li svetlo radi.
Svake večeri, bez obzira da li se na horizontu vidi iko, pali svetlo i
proverava ga — jer upravo ona noć kad nijedan brod nije u blizini da posvedoči
da svetlo radi jeste noć kad mora najviše da veruje da će raditi, za onaj
jedan brod koji se na kraju ipak pojavi, u mraku, bez upozorenja. Da je čuvar
čekao da vidi brod pre nego što proveri svetlo, otkrio bi kvar tačno u
trenutku kad je najskuplje otkriti ga.

RUM iz prethodnog poglavlja je poput mornara koji gleda svetionik sa broda —
vidi ga samo dok je tu, samo dok postoji saobraćaj koji generiše signal.
Sintetičko praćenje je čuvar koji proverava svetlo svake noći, nezavisno od
toga da li iko gleda. Oba su potrebna; rade različit posao.

## 9.1 Pitanje na koje ovo poglavlje odgovara

RUM iz Poglavlja 8 zavisi od stvarnog korisničkog saobraćaja da bi uopšte
postojao signal. Šta se dešava u periodu kad tog saobraćaja nema — usred
noći, u periodu pred lansiranje, u regionu gde je baza korisnika mala? Da li
sistem tada nema **nikakav** način da zna da li radi, dok se ne pojavi prvi
korisnik da to otkrije umesto monitoring sistema?

Odgovor je sintetičko praćenje — aktivne, zakazane probe koje ne čekaju
stvarnog korisnika, nego same simuliraju jednog, na fiksnom rasporedu,
nezavisno od toga da li iko zaista koristi sistem u tom trenutku.

## 9.2 Kako je to urađeno — praktičan pregled

Implementacija koju knjiga prati koristi spoljašnje HTTP probe koje **ne
prolaze kroz internu infrastrukturu** — ni kroz gateway iz Poglavlja 4, ni
kroz internu mrežu, ni kroz interni DNS. Probe se pokreću iz spoljašnjih
lokacija (upravljanih od strane same Grafana Cloud platforme), gađaju javne
endpoint-e aplikacije baš kao što bi to radio stvarni korisnik izvana, i
prijavljuju rezultat nazad u istu observability platformu na kojoj žive
svi ostali signali iz knjige.

Probe testiraju dve različite stvari, namerno razdvojene:

- **Osnovna dostupnost** — da li javni endpoint uopšte odgovara, i za koliko
  vremena. Ovo je najjednostavniji oblik probe i najjeftiniji za održavanje.
- **Kritični poslovni tok** — višekoracna proba koja simulira stvaran
  korisnički put (prijava, ključni API poziv, provera da odgovor sadrži
  očekivan sadržaj, ne samo status kod 200). Ovo je bitna razlika u odnosu na
  naivnu proveru dostupnosti: endpoint može da odgovori sa 200 i praznim ili
  pogrešnim sadržajem — tačno onaj isti obrazac tihog kvara iz Poglavlja 1
  ("cacher" incident), samo ovde primenjen na spoljašnju proveru umesto na
  interni batch zadatak.

Probe rade sa **više geografskih lokacija istovremeno**, što daje signal koji
ni RUM ni interni health-check ne mogu da daju na isti način: ako proba iz
jednog regiona javlja kvar dok ostale rade normalno, to sužava dijagnozu na
mrežni/DNS problem specifičan za taj region, umesto na problem same
aplikacije.

Najvažnija arhitekturna osobina ovog obrasca, direktno nasleđena iz principa
uvedenog u Poglavlju 7 (**watcher ne sme da zavisi od infrastrukture koju
posmatra**): probe rade potpuno nezavisno od interne mreže, interne DNS zone
i internog gateway-a. To znači da je sintetičko praćenje jedini signal u celom
sistemu koji **preživljava** scenario u kome je cela interna posmatračka
infrastruktura nedostupna — tačno onaj scenario u kome bi svaki drugi izvor u
ovoj knjizi (RUM koji ide direktno ka cloud-u je izuzetak, ali ne testira
poslovnu logiku na isti eksplicitan način) ćutao, ne zato što je aplikacija
pala, nego zato što je put do monitoring sistema pao.

![Probe iz više regiona gađaju javni endpoint direktno preko interneta, zaobilazeći internu mrežu, DNS zonu i gateway — i prijavljuju rezultat nazad u cloud platformu nezavisno od interne infrastrukture.](diagrams/ch9-synthetic.png){: width="92%" }

Multi-region raspored plaća se tačno u ovakvom trenutku — kad jedan region
utihne dok ostala dva i dalje javljaju normalan rad, dijagnoza se sužava sama
od sebe, bez ijednog dodatnog koraka istrage:

![Region B prestaje da javlja latenciju u kratkom prozoru dok Region A i Region C nastavljaju normalno — obrazac koji upućuje na regionalni mrežni problem, ne na pad same aplikacije.](diagrams/dashboard-synthetic.png){: width="95%" }

### Treći sloj: da li se aplikacija zaista renderuje, ne samo da li server odgovara

Osnovna dostupnost-proba i proba poslovnog toka i dalje ostavljaju jednu
rupu: obe testiraju šta server **vrati**, nijedna ne testira šta browser
zaista **prikaže**. Pokvaren JavaScript bundle — loš deploy, izmenjena
putanja do statičkog fajla, greška u build koraku — i dalje vraća HTTP 200 sa
punim HTML dokumentom; sama stranica ostaje prazna, jer se skripta koja bi je
napunila sadržajem nikad ne izvrši. Ni osnovna dostupnost-proba (vidi 200,
prijavljuje "radi") ni proba poslovnog toka usmerena na API pozive ne bi
ovo uhvatile — obe gledaju server, a kvar je isključivo na strani klijenta.

Implementacija koju knjiga prati dodaje treći, poseban tip probe za tačno
ovaj slučaj: proba koja pokreće pravi headless browser (Chromium, upravljan
istim k6 alatom koji stoji iza probe poslovnog toka), učitava frontend
aplikaciju kao pravi korisnik, i proverava da je stranica zaista popunjena
sadržajem posle mrežnog mirovanja — ne samo da je odgovor stigao. Ovo je isti
obrazac tihog kvara iz Poglavlja 1 i iz "kritičnog poslovnog toka" iznad,
primenjen na treći sloj sistema (klijentsko renderovanje) koji prva dva tipa
probe strukturno ne mogu da vide.

Dve stvari vredi eksplicitno reći o ovoj probi. Prva: namerno **ne** emituje
podatke u isti RUM tok kao stvarni korisnici (Poglavlje 8) — bila bi to
sintetička sesija koja bi tiho zagadila baseline p75/p95 izračunat iz
stvarnog saobraćaja, pa se drži potpuno odvojeno, kao nezavisan heartbeat.
Druga: browser proba je najskuplji sloj sintetičkog praćenja — pokretanje
punog Chromium-a po izvršenju nosi mnogo veći trošak (i u novcu i u broju
generisanih serija/logova) od proste HTTP probe — pa se namerno drži na
minimalnom otisku koji i dalje daje signal: jedna lokacija, redak interval,
umesto raskošne multi-regionalne postavke koju osnovna dostupnost-proba sebi
može da priušti. Isti princip — da učestalost i broj lokacija direktno
množe trošak, ne samo preciznost — već je jednom primoran na test kod
osnovnih HTTP probi u ovoj implementaciji, kad je prekomerna multi-regionalna
postavka izazvala neplanirano prekoračenje budžeta i morala biti svedena na
jednu lokaciju sa ređim intervalom.

## 9.3 Analitički deo — zašto sintetičko praćenje nije "RUM za siromašne"

### Sintetičko i RUM rešavaju različite probleme, ne isti problem na dva načina

Nezavisna poređenja RUM-a i sintetičkog praćenja (uključujući ClickHouse-ov i
MDN-ov materijal na ovu temu) dosledno navode da su ovo dva komplementarna, ne
konkurentska pristupa. RUM je bolji za razumevanje **stvarnog** korisničkog
iskustva — stvarni uređaji, stvarne mreže, stvarna geografska raspodela,
long-tail problemi koje nijedan sintetički scenario ne bi pogodio jer ih niko
nije unapred zamislio (isti "unknown unknown" problem iz Poglavlja 1, samo
sada na nivou performansi umesto ispravnosti). Sintetičko praćenje je bolje
za **stabilnu, ponovljivu** proveru dostupnosti i za alarme koji moraju da
rade nezavisno od saobraćaja — SLA verifikacija, alarmiranje van radnog
vremena, regresiono testiranje kritičnih tokova pre nego što se promena
uopšte pusti u produkciju.

Pokušaj da se jedno zameni drugim uvek otkriva istu slepu tačku: sistem
oslonjen samo na RUM ne zna ništa o sopstvenom stanju kad nema saobraćaja;
sistem oslonjen samo na sintetičke probe ne vidi stvarnu distribuciju
korisničkog iskustva (probe testiraju fiksan, mali broj scenarija sa fiksnih
lokacija — ne haos stvarnog sveta).

### Zašto testirati poslovni tok, ne samo dostupnost

Vredi eksplicitno primetiti zašto je odluka da probe testiraju **kritičan
poslovni tok**, ne samo "da li endpoint odgovara sa 200", direktna posledica
lekcije iz Poglavlja 1. Da su probe u implementaciji koju knjiga prati
proveravale samo osnovnu dostupnost, sistem bi mogao da "prođe" svaku probu
danima dok je u pozadini vraćao netačne ili prazne odgovore — isti obrazac
tihog kvara, samo sad neopažen od strane alata koji je specifično dizajniran
da hvata kvarove. Dodatni trošak višekoracne probe (održavanje test naloga,
osvežavanje test podataka, sporija proba) je prihvaćen upravo zato što
jednostavna dostupnost-proba daje lažan osećaj sigurnosti — izgleda kao da
nešto štiti, a zapravo ne hvata baš onu klasu kvara koja najviše boli.

### Šta bi se izgubilo bez ovog sloja

Kontrafaktički scenario je direktan: bez sintetičkog praćenja, jedini signal
o dostupnosti sistema van perioda saobraćaja bio bi tišina — a tišina se, kao
što je Poglavlje 1 pokazalo za "cacher" zadatak i Poglavlje 7 za bazu koja
odbija konekcije, ne razlikuje lako od "sve je u redu". Prvi znak problema bi
bio prvi korisnik koji se požali, umesto alarm koji je stigao pre nego što je
ijedan stvaran korisnik i pokušao da pristupi sistemu. Za sistem koji ima
poslovne korisnike u različitim vremenskim zonama i tihe periode saobraćaja,
ova razlika nije kozmetička — to je razlika između otkrivanja kvara za dva
minuta i otkrivanja kvara za dva sata.

Vratimo se na čuvara svetionika. On ne pali svetlo zato što očekuje brod te
konkretne noći — pali ga zato što ne zna unapred koje će noći brod stvarno
doći, i jedini način da bude spreman za tu noć je da svetlo bude testirano
svaku noć, ne samo one kad je neko tamo da to primeti. **Vrednost sintetičkog
praćenja se ne meri time koliko često pronađe problem — meri se time da,
kada problem postoji baš u trenutku kad niko ne gleda, neko ipak zna.**

## 9.4 Skupljena pravila iz ovog poglavlja

- Sintetičko praćenje mora raditi potpuno nezavisno od interne mreže,
  DNS zone i gateway-a — to je jedini način da ostane koristan tačno onda
  kada ta infrastruktura otkaže.
- Ne zaustavljaj se na proveri osnovne dostupnosti (status kod) — testiraj
  bar jedan kritičan poslovni tok do kraja, sa proverom da je sadržaj
  odgovora zaista ispravan, ne samo da odgovor postoji.
- Koristi probe sa više geografskih lokacija kad god je moguće — razlika u
  tome koja lokacija javlja kvar je sama po sebi dijagnostička informacija.
- Ne tretiraj sintetičko praćenje kao zamenu za RUM niti obrnuto — jedno vidi
  stvarno iskustvo, drugo vidi dostupnost nezavisno od saobraćaja; sistem
  bez oba ima slepu tačku koju ne zna da ima.
- Proveri da li tvoje probe rade tačno u periodima kad je saobraćaj
  najmanji (noć, vikend) — to je period u kome njihova vrednost dolazi do
  izražaja, i period u kome se najlakše zaboravi da se testira.
- Dodaj sloj koji zaista renderuje klijenta (headless browser), ne samo
  proverava HTTP status — pokvaren JS bundle i dalje vraća 200 dok je
  stranica prazna, i nijedna server-side proba to ne vidi. Drži tu probu
  odvojenu od stvarnog RUM toka i na minimalnom otisku (jedna lokacija, redak
  interval) — ona je najskuplji sloj sintetičkog praćenja.

## 9.5 Vežba za čitaoca

Zamisli da tvoj sistem prestane da radi u tri ujutru u vremenskoj zoni gde
trenutno nemaš korisnika. Prođi kroz svaki sloj monitoringa koji imaš i
postavi pitanje: da li bi ovaj sloj primetio kvar u tom trenutku, ili zavisi
od toga da neko konkretan (korisnik, sistem koji zavisi od tvog) aktivno
koristi sistem baš tada? Ako većina tvojih slojeva zavisi od aktivnog
saobraćaja, to je znak da ti nedostaje sloj opisan u ovom poglavlju.

---

### Izvori korišćeni u analitičkom delu

- [RUM vs synthetic monitoring: which do you need? — ClickHouse](https://clickhouse.com/resources/engineering/rum-vs-synthetic-monitoring)
- [Synthetic and Real User Monitoring Explained — Catchpoint](https://www.catchpoint.com/guide-to-synthetic-monitoring/rum-vs-synthetic-monitoring)
- [Performance Monitoring: RUM vs. Synthetic Monitoring — MDN](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Rum-vs-Synthetic)
- [Synthetic Monitoring vs. Real User Monitoring (RUM) — Kentik](https://www.kentik.com/kentipedia/synthetic-monitoring-vs-real-user-monitoring/)
- [Synthetic Monitoring vs. Real User Monitoring (RUM): A Comparison — DebugBear](https://www.debugbear.com/blog/synthetic-vs-rum)
