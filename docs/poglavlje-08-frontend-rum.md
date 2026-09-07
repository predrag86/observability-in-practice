# Poglavlje 8 — Frontend / RUM observability

Ambasada u stranoj zemlji je, tehnički, teritorija matične države — ali ne
funkcioniše kao njena unutrašnja pošta. Pismo poslato iz ambasade ne ide kroz
lokalni poštanski sistem strane zemlje, jer ambasada tom sistemu ni ne
pripada na isti način kao građanska pošta kod kuće; ono ide direktnom,
diplomatskom linijom, jer je to jedini put koji ambasadi uopšte stoji na
raspolaganju. I ambasada nema jedan kanal komunikacije, nego više — redovna
prepiska ide jednim putem, hitni kurirski paketi drugim — a svaki od tih
kanala mora **posebno** da bude proveren pre nego što nešto osetljivo prođe
kroz njega, jer provera na jednom kanalu ne štiti automatski i drugi.

Browser korisnika je, za sistem koji knjiga prati, u sličnoj poziciji.
Fizički živi van interne mreže — ne može, i ne treba, da mu se dozvoli pristup
internom gateway-u iz Poglavlja 4. Mora da ide sopstvenim, direktnim putem. I
baš kao ambasada, ima više od jednog kanala kojim podaci putuju — što znači
da zaštita mora biti primenjena na svakom kanalu posebno, ne jednom, na
jednom mestu, i pretpostavljeno da to pokriva sve.

## 8.1 Pitanje na koje ovo poglavlje odgovara

Sve dosadašnje poglavlje o prikupljanju telemetrije (Poglavlja 4-7)
pretpostavlja da pošiljalac živi unutar mreže koju tim kontroliše — servis,
batch zadatak, baza, čak i klaster. Browser korisnika krši tu pretpostavku na
najosnovniji mogući način: **fizički nikad neće imati pristup internoj
infrastrukturi**, bez obzira koliko dobro ta infrastruktura bude
projektovana. Kako se onda prikuplja telemetrija sa mesta koje po definiciji
ne možeš da uvučeš u sopstvenu mrežu — i šta to menja u odnosu na sve
prethodno u knjizi?

## 8.2 Kako je to urađeno — praktičan pregled

Frontend telemetrija u implementaciji koju knjiga prati ide **direktno** ka
hostovanom RUM kolektoru na strani Grafana Cloud-a — ne kroz interni gateway.
Ovo je jedina kategorija pošiljaoca u celom sistemu koja gateway zaobilazi
namerno, iz razloga eksplicitno pomenutog i u Poglavlju 4: gateway živi u
privatnoj mreži, i browser korisnika joj fizički ne može pristupiti.

Ono što se prikuplja:

- **Core Web Vitals** — standardizovane metrike percepcije performansi
  (vreme do prvog sadržajnog prikaza, stabilnost layout-a, odzivnost na
  interakciju) koje sam browser meri i izlaže.
- **JavaScript greške** — neuhvaćeni izuzeci, odbijeni promisi, sa stack
  trag-om i informacijom o browseru/uređaju.
- **Trejsovi korisničke sesije**, povezani sa backend trejsom preko **istog
  trace ID-ja** — kad korisnik klikne dugme koje pokreće API poziv, RUM SDK
  ubacuje trace-context header u taj poziv, tako da se ceo put (klik u
  browseru → mrežni poziv → backend obrada → odgovor) pojavljuje kao jedan
  kontinuiran trejs, čitljiv u istom Grafana Cloud interfejsu koji već
  koristi backend telemetrija.

Ova poslednja tačka — deljen trace ID kroz ceo put — je razlog zašto frontend
poglavlje uopšte pripada ovoj knjizi, a ne posebnoj, izolovanoj temi: iako
mehanizam transporta strukturno odstupa od svega drugog (direktno umesto kroz
gateway), *semantika* ostaje ista OTel semantika iz Poglavlja 2. Isti trace
ID, ista propagacija konteksta.

**Zašto propagacija radi bez ijedne CORS izmene.** RUM SDK po podrazumevanom
podešavanju ubacuje trace-context header samo u pozive čiji je URL isti
origin kao i sama stranica — cross-origin pozivi ostaju bez njega osim ako
se eksplicitno ne uključe na dozvoljenu listu. U implementaciji koju knjiga
prati ovo se poklapa savršeno sa stvarnim oblikom saobraćaja: backend
aplikacija sama servira frontend (isti origin kao i stranica), a frontend je
poziva na relativnim putanjama (`/api/...`) umesto apsolutnim URL-ovima — pa
je svaki poziv ka backend-u automatski isti origin, bez ijedne CORS izmene i
bez liste dozvoljenih domena koju treba održavati. Kad backend Java agent
primi taj header, njegov server span postaje dete browser span-a — isti
trace ID, jedan kontinuiran trejs, bez ijednog reda koda napisanog samo za
ovu vezu.

Cross-origin pozivi (provajder identiteta, mape, druge treće strane)
namerno ostaju bez trace-context header-a — ne propust, nego eksplicitna
odluka: uključivanje bi značilo curenje trace ID-ja ka servisima van
sopstvene kontrole i stvaranje osirotelih span-ova tamo (span-ova bez para
na drugom kraju, jer taj servis ne šalje ništa nazad u isti Tempo tenant).
Isto tako, dodatni OTel mehanizam za prenošenje proizvoljnih parova
ključ-vrednost uz trejs (baggage) namerno nije uključen uopšte — samo trace
ID prelazi granicu browser→backend, ništa više. Manja površina za curenje je
ovde svesno odabrana nad većom fleksibilnošću.

![Browser ide direktno ka hostovanom RUM kolektoru, zaobilazeći gateway; backend telemetrija i dalje ide kroz gateway. Dve odvojene PII zaštite (native signali naspram trejsova) su namerno naglašene — to je tačka incidenta iz ovog poglavlja.](diagrams/ch8-rum.png){: width="75%" }

**Dve tačke za čišćenje PII, ne jedna.** Ovo je najvrednija praktična lekcija
poglavlja. RUM SDK ima jednu centralnu funkciju koja presreće sve "native"
signale — logove, merenja, greške — i iz njih uklanja poznate osetljive
vrednosti pre slanja (email adrese u porukama grešaka, ID-jevi sesije u
URL-ovima). Ta funkcija radi tačno ono što se od nje očekuje. Problem: **RUM
trejsovi ne prolaze kroz tu istu funkciju.** Trejsovi se generišu i šalju
kroz zaseban deo SDK-a (instrumentacija automatskih fetch/XHR poziva), koji
ima sopstveni, nezavisan put do mreže — i taj put tu istu centralnu funkciju
jednostavno zaobilazi. Otkriveno je da su URL parametri sa identifikatorima
korisnika, koji su uredno uklonjeni iz logova, i dalje završavali u atributima
span-ova, jer je timski mentalni model bio "dodao sam filter za PII" umesto
precizno "dodao sam filter za PII **na ovom konkretnom putu podataka**".
Ispravka je zahtevala eksplicitnu, zasebnu redakciju na nivou span-processora,
ne proširenje postojeće funkcije koja trejsove nikad nije ni videla.

Ovako izgleda Core Web Vitals dashboard u praksi — tri percentila (p50/p75/p95)
umesto jedne linije, jer prosek ili čak medijana lako sakriju baš onaj deo
korisnika koji ima najgore iskustvo:

![LCP praćen po percentilima: p50 i p75 ostaju stabilni, ali p95 pokazuje jasnu regresiju jednog dana — signal koji bi prosek sakrio, jer pogađa samo deo saobraćaja (tipično jedan geografski region ili tip uređaja).](diagrams/dashboard-rum.png){: width="95%" }

### Kad je izgradnja tiha o sopstvenom neuspehu

Prvi pokušaj puštanja frontend telemetrije u probni okvir je, po svakoj
standardnoj proveri, prošao besprekorno: build je prošao, testovi su bili
zeleni, isporučena aplikacija je vraćala HTTP 200 i radila potpuno identično
za korisnika kao i pre. Ni jedna od tih provera nije otkrila da isporučeni
paket **uopšte ne sadrži poziv inicijalizacije SDK-a za telemetriju** — build
je pokrenut iz starije verzije izvornog koda, snimljene pre nego što je kod
za instrumentaciju uopšte ušao u granu iz koje se gradi. Aplikacija je radila
identično jer telemetrija nikad ne utiče na to kako aplikacija izgleda ili
funkcioniše za korisnika — samo na to da li nešto stiže na drugi kraj, van
vidokruga bilo koje provere koja gleda samo isporučenu stranicu.

Otkriveno je tek eksplicitnom, posebno osmišljenom proverom: pretraživanjem
**samog isporučenog, već izgrađenog JavaScript paketa** (ne izvornog koda,
nego artefakta koji je stvarno otišao na server) u potrazi za imenom funkcije
koju SDK poziva pri inicijalizaciji, i nezavisno, proverom da li se naziv tog
frontend servisa uopšte pojavljuje u sistemu za skladištenje telemetrije —
makar sa nula tačaka podataka. Obe provere su rađene **posle** što je svaka
standardna provera već proglasila isporuku uspešnom. Dodatna zamka koja je
uz put otkrivena: postoji i poseban, potpuno odvojen sistem koji takođe
gradi frontend paket radi sopstvene provere ispravnosti koda, ali taj
artefakt niko nikad stvarno ne isporučuje — laka greška bi bila pretpostaviti
da "taj build prolazi" znači "isporučeni build je instrumentisan", kad su to
u stvarnosti dva potpuno nezavisna artefakta.

Opšta pouka: prisustvo SDK-a za telemetriju je nevidljivo za svaku
uobičajenu proveru zdravlja isporuke — build koji prolazi, testove koji su
zeleni, HTTP 200, aplikaciju koja radi. Jedini način da se otkrije njegovo
odsustvo je eksplicitna provera koja gleda baš taj kod u baš tom isporučenom
artefaktu, ili proverava da li se očekivani signal uopšte pojavio nizvodno —
a takva provera se retko radi sama od sebe, mora biti dodata namerno.

![Standardne provere isporuke (build, testovi, HTTP 200) ne gledaju telemetrijski kod — isporučeni paket može biti izgrađen iz stare verzije izvora, bez inicijalizacije SDK-a, a da nijedna od njih to ne primeti. Otkriva se tek eksplicitnom proverom isporučenog artefakta i nizvodne telemetrije.](diagrams/ch08-tiha-praznina.png){: width="80%" }

### Kad procentil laže jer uzorka premalo ima

Interni alat sa relativno malim brojem korisnika generiše, pokazalo se posle
puštanja u produkciju, samo dvanaestak do trinaestak merenja Core Web
Vitals-a **dnevno** — a alarm koji prati regresiju gleda **p75 preko
kliznog prozora od 24 sata**. Na toj količini uzoraka, jedna jedina
neuobičajeno spora sesija — korisnik na slaboj mreži, na starijem uređaju,
u pozadinskom tabu-u — može sama da pomeri p75 cele grupe iz "dobrog" u
"loš" opseg, bez ijedne stvarne promene u aplikaciji koja bi to opravdala.

Zato prvi korak u odgovoru na taj alarm nije istraživanje šta se u
aplikaciji promenilo — nego provera **da li uzorak uopšte ima dovoljno
tačaka da se procentilu veruje**. Alarm eksplicitno zahteva minimalan broj
merenja u prozoru pre nego što uopšte razmotri okidanje, upravo zato što je
poznato da na ovom nivou saobraćaja procentil sam po sebi nije pouzdan
signal ispod tog praga.

Ovo produbljuje princip već pomenut ranije u poglavlju — da RUM ima slepu
tačku kad saobraćaja uopšte nema. Ovde je slepa tačka suptilnija: alarm
**jeste** opalio, procentil **jeste** izračunat, ali sam broj — bez
konteksta koliko je tačaka ušlo u njegov obračun — može da liči na stvarnu
regresiju dok je zapravo statistički artefakt premalog uzorka. Tretiranje
svakog alarma zasnovanog na procentilu kao apsolutne istine, bez pitanja
"na koliko tačaka je ovo izračunato", je greška koja se ne vidi dok se
prvi lažni alarm ne istraži do kraja i ne otkrije da iza njega stoji jedna
jedina sesija.

### Uzorkovanje na nivou sesije — binarno, ne postepeno

RUM SDK uzorkuje na nivou **cele sesije**, ne na nivou pojedinačnog signala:
sesija je ili uzorkovana — i tada šalje baš sve (Core Web Vitals, greške,
trejsove) — ili nije, i tada ne šalje ništa. Pošto se RUM naplaćuje po
sesiji, ovo uzorkovanje je najveći pojedinačni lever za trošak, i za većinu
sistema bi bilo prirodno spustiti ga ispod 100%.

Implementacija koju knjiga prati drži stopu na **1.0** — namerno, ne iz
propusta da se razmotri jeftinija opcija. Dva razloga, oba merljiva: prvo,
na obimu saobraćaja ovog alata (par hiljada sesija dnevno) trošak pune stope
je zanemarljiv. Drugo, i važnije za ovo poglavlje konkretno: stopa ispod 1.0
ne bi samo jeftinije smanjila podatke — tiho bi pokidala baš onu osobinu
zbog koje ovo poglavlje uopšte postoji. Uzorkovanje je binarno na nivou
sesije, što znači da neuzorkovana sesija nikad ne ubacuje trace-context
header u svoj API poziv — "isti trace ID kroz ceo put" iz 8.2 važi samo za
onaj deo saobraćaja koji je uzorkivač zadržao, ne za sav saobraćaj. Spuštanje
stope ne bi bilo pogrešno samo po sebi, ali bi zahtevalo da se ta granica
eksplicitno prizna i komunicira — "trejs povezan kroz ceo put" bi prestalo da
znači "svaki klik", a počelo da znači "svaki klik koji je slučaj hteo da
uzorkivač zadrži".

Ovo se direktno vezuje i za zamku sa procentilima iz prethodnog odeljka:
alarm koji već zahteva minimalan broj tačaka u prozoru pre nego što uopšte
razmotri okidanje računa taj broj na **uzorkovanim** sesijama, ne na
stvarnom saobraćaju. Da stopa ikad padne ispod 1.0, isti minimalni prag bi
odjednom predstavljao mnogo veći procenat stvarnog saobraćaja nego što je
nameravano kad je prag postavljen — dva odvojena podešavanja (stopa
uzorkovanja i minimalni prag alarma) koja moraju ostati usklađena, ne
menjana nezavisno jedno od drugog.

### Sourcemap-ovi: greška je uhvaćena, ali ne i čitljiva

JavaScript greške, opisane u 8.2, stižu redovno i pouzdano — ali stack trag
koji nose je stack trag **minifikovanog, spakovanog** koda koji je stvarno
poslat browseru, ne originalnog izvornog koda. Prevođenje minifikovanog
stack traga nazad u čitljive linije izvornog koda zahteva da build proces
otpremi sopstvene sourcemap fajlove ka RUM kolektoru u trenutku izgradnje —
taj korak, u trenutku pisanja, još nije ožičen.

Praktična posledica: neko ko otvori istragu na osnovu JS greške dobija
stack trag koji upire u jednu jedinu, ogromnu liniju spakovanog koda —
greška **jeste** uhvaćena, tačno kao što je opisano ranije u poglavlju, ali
nije upotrebljiva bez ručne rekonstrukcije lokalno ili ručnog čitanja
minifikovanog izvora, redom, dok se ne pronađe odgovarajuće mesto.

Ovo je ista vrsta iskrenosti prema čitaocu koju je Poglavlje 5 već pokazalo
na drugom mestu: identifikovana popravka koja u trenutku pisanja još nije
sprovedena beleži se kao otvorena praznina, ne prećutkuje se zato što bi
priznanje nedovršenog posla ličilo na manjkavost implementacije. Vrednost
za čitaoca nije u tome da svaki primer u knjizi bude završen — nego da svaki
primer bude tačan onome što stvarno postoji u tom trenutku, uključujući i
ono što se zna da nedostaje.

### Dobavljač je tiho promenio podešavanje koje niko u timu nikad nije postavio

Treći izvor pravno osetljivih podataka u RUM cevovodu ne dolazi iz koda
aplikacije niti iz onoga što browser sam po sebi prikuplja — dolazi iz
podešavanja koje **hostovana platforma za prijem RUM podataka** čuva o svakoj
aplikaciji, van bilo kog fajla koji tim drži pod kontrolom verzija.

Konkretan slučaj: obe frontend aplikacije su imale eksplicitnu, upisanu odluku
— grubo geolociranje isključeno, jer je reč o autentikovanom, internom alatu sa
poznatim korisnicima u EU, i cilj je minimizovati prikupljanje ličnih podataka.
Platforma je tu vrednost tiho prebacila na uključeno, na nivou preciznosti grada
(ne samo kontinenta ili države — mnogo precizniji nivo nego što izraz "grubo
geolociranje" sugeriše), i to na obe aplikacije istovremeno, uz podešavanje
koje se ne pojavljuje ni u jednom fajlu koji tim održava. Istorija verzija
same konfiguracije potvrđuje da to nije bila ljudska izmena — jedini zabeleženi
upis je bio originalni, koji je vrednost postavio na isključeno. Promena je
došla sa strane platforme, van bilo kakve akcije tima. Prozor izloženosti gornja
granica: oko dva meseca — od poslednje primene infrastrukturnog koda do
otkrića, koje se dogodilo tek prvim pokretanjem periodične provere razlike
između željenog i stvarnog stanja. Ništa u runtime monitoringu ne bi ovo
primetilo samo od sebe.

Popravka je nosila sopstvenu zamku: alat za infrastrukturu kao kod je prijavio
uspešnu primenu **dvaput** za redom, a stvarno stanje se nije promenilo nijednom
od ta dva puta. Razlog je drugi, nedokumentovan prekidač na nivou cele platforme
— geolociranje se ne može uključiti kroz podešavanje jedne aplikacije ako je
isključeno na tom višem nivou, ali se *može* isključiti odatle nadole bez
ikakve prepreke. "Primena uspešna" je time dokazivala samo da je komanda
poslata, ne da je podešavanje stvarno promenjeno — jedini pouzdan dokaz je bio
sledeći plan izvršen odmah posle primene, koji upoređuje željeno stanje sa
osvežnim, stvarnim stanjem.

Poslednji obrt: kad je tim krenuo da istraži šta uraditi sa otkrivenom
promenom, ispostavilo se da je sama polazna odluka — "geolociranje isključeno"
— zastarela, upisana bez datuma, i da postoji novija, neformalna odluka da se
geolociranje zapravo **želi**, upravo na nivou preciznosti grada koji je
platforma tiho uključila. Refleksni prvi potez, vratiti podešavanje na staru,
pisanu odluku, bio je pogrešan potez — ne zato što je pogrešno poštovati
pisanu politiku, nego zato što ta politika više nije važila, a ništa u njoj
nije nosilo datum koji bi to otkrio. Konačna popravka nije bila "vrati na
staro" nego "upiši novu odluku eksplicitno, sa razlogom i datumom, tako da
sledeći put kad se nešto promeni — bilo sa strane platforme, bilo sa strane
tima — bude jasno koja je odluka trenutno na snazi." I dalje otvoreno pitanje,
namerno ostavljeno van dometa ovog poglavlja: da li postoji pravni osnov
(pristanak korisnika, na primer) za prikupljanje lokacije na ovom nivou
preciznosti — to je odluka koju ovaj tim ne donosi sam.

## 8.3 Analitički deo — zašto direktna veza nije kompromis nego zahtev, i šta znači kad "jedan filter" nije dovoljan

### Zašto zvanična arhitektura RUM-a skoro uvek ide direktno u cloud

Nezavisni pregledi RUM arhitekture dosledno navode da browser telemetrija
ide direktno ka hostovanom kolektoru, ne kroz internu infrastrukturu — iz
prostog razloga što interna infrastruktura po definiciji nije dostupna sa
javnog interneta na način koji bi browser mogao bezbedno da koristi.
Otvaranje interne mreže ka javnom internetu samo da bi RUM SDK mogao da
pošalje podatke kroz "isti gateway kao sve ostalo" bi značilo probijanje baš
onog perimetra koji je Poglavlje 4 pažljivo zatvorilo — cena veća od koristi
koju bi doslednost transportnog puta donela. Ovo je redak slučaj gde
"industrijski standard" i implementacija koju knjiga prati **nisu u
tenziji** — oba idu istim putem, iz istog razloga.

### Zašto RUM naspram sintetičkog praćenja nisu zamena jedno za drugo

Nezavisna poređenja RUM-a i sintetičkog (black-box) praćenja — tema kojom se
detaljno bavi Poglavlje 9 — ističu da RUM zavisi potpuno od stvarnog
saobraćaja: signal postoji samo ako neko korisnik u tom trenutku koristi
aplikaciju. To znači da RUM ima strukturnu slepu tačku u periodima niskog
saobraćaja (noć, period pre lansiranja) — ako se aplikacija pokvari tačno
tada, RUM to jednostavno neće registrovati na vreme, jer nema koga da
registruje. Ova slepa tačka nije nedostatak RUM implementacije — ona je
strukturno svojstvo pasivnog posmatranja stvarnih korisnika, i rešava se
kombinovanjem sa aktivnim probama, ne popravkom RUM-a samog.

### Lekcija iz PII incidenta: zašto "dodao sam filter" retko znači "sve je pokriveno"

Ovo je poglavlje u kome se najjasnije vidi princip koji se provlači kroz celu
knjigu, prvi put eksplicitno imenovan u Poglavlju 1 na drugom primeru: sistem
može da "radi ispravno" po svakoj proveri koju je neko sproveo, a ipak da
propušta nešto što nijedna od tih provera nije ni gledala. PII filter za
logove je bio testiran, radio je, prošao je code review — sve tačno kako
treba. Ono što nije bilo eksplicitno provereno je pitanje "kroz koje **sve**
puteve podataka ovaj SDK šalje nešto ka mreži" — a odgovor je bio dva puta,
ne jedan, i drugi put niko nije aktivno tražio jer se prvi filter "osećao
kao" kompletno rešenje.

Kontrafaktički: da je tim od početka mapirao **sve** izlazne puteve RUM SDK-a
pre nego što je napisao prvi filter (umesto da filter napiše za put koji je
prvi pao na pamet — logove), ovaj incident se verovatno nikad ne bi ni
dogodio. Cena tog mapiranja unapred je bila mala — par sati čitanja
dokumentacije SDK-a. Cena otkrivanja posle činjenice bila je veća: revizija
istorijskih podataka da se proceni koliko dugo je curenje trajalo, dodatna
runda review-a za sličnu klasu bagova na drugim mestima u sistemu.

Vratimo se na ambasadu s početka poglavlja. Ona nema jedan kanal komunikacije
— ima više, i svaki mora biti proveren posebno, jer provera na jednom
kanalu ne prelazi automatski na drugi. **Kad štitiš osetljive podatke,
pitanje nije "da li sam dodao filter" nego "da li sam nabrojao svaki put
kojim podatak može da izađe, i da li svaki od njih ima sopstvenu,
eksplicitnu proveru."**

## 8.4 Skupljena pravila iz ovog poglavlja

- Browser telemetrija ide direktno ka hostovanom kolektoru — ne pokušavaj da
  je forsiraš kroz internu infrastrukturu radi doslednosti transportnog
  puta; to je pogrešna vrsta doslednosti.
- Zadrži isti trace ID i semantiku konteksta (OTel propagacija) čak i kad se
  transportni mehanizam strukturno razlikuje od ostatka sistema — to je ono
  što povezuje frontend i backend u jedan čitljiv trejs.
- Osloni se na isti-origin propagaciju kad god je moguće (backend servira
  frontend, pozivi na relativnim putanjama) — ona ne traži nijednu CORS
  izmenu. Ne uključuj propagaciju ka cross-origin trećim stranama niti
  baggage bez eksplicitnog razloga — svaki od njih širi površinu curenja
  trace konteksta van sopstvene kontrole.
- Pre nego što napišeš PII filter, mapiraj **sve** izlazne puteve podataka iz
  SDK-a ili biblioteke koju štitiš — logovi, merenja, greške i trejsovi retko
  dele istu funkciju za obradu.
- RUM ne zamenjuje sintetičko praćenje niti obrnuto — RUM zavisi od
  stvarnog saobraćaja i ima slepu tačku u periodima tišine; to nije bag,
  to je razlog da postoji Poglavlje 9.
- Posle svakog "dodao sam filter za X", eksplicitno pitaj: kroz koje sve
  puteve X uopšte može da izađe, i da li ih je filter zaista sve pokrio.
- Nijedna standardna provera isporuke (build, testovi, HTTP status,
  vizuelni rad aplikacije) ne otkriva odsustvo telemetrijskog koda — dodaj
  eksplicitnu proveru koja gleda sam isporučeni artefakt ili potvrđuje da
  se očekivani servis pojavio nizvodno.
- Pre nego što alarmu zasnovanom na procentilu poveruješ kao stvarnom
  signalu, proveri koliko je tačaka ušlo u obračun — na niskom saobraćaju
  jedna sesija može da pomeri p75 iz "dobrog" u "loš" opseg bez ijedne
  stvarne promene u sistemu.

- Uzorkovanje na nivou sesije je binarno, ne postepeno — stopa ispod 1.0 ne
  samo smanjuje trošak, nego tiho ograničava "isti trace ID kroz ceo put" na
  samo onaj deo saobraćaja koji je uzorkivač zadržao. Ako ikad spustiš stopu,
  eksplicitno priznaj tu granicu i ponovo uskladi minimalne pragove alarma
  koji broje uzorkovane, ne stvarne, sesije.
- Hvatanje greške i mogućnost da se ta greška razume nisu ista stvar — provera
  da JS greške stižu ne znači da su stack tragovi čitljivi; bez otpremanja
  sourcemap-a, greška je uhvaćena, ali istraga i dalje počinje od nule.
- Podešavanja koja hostovana platforma čuva o tvojoj aplikaciji (ne kod koji
  ti pišeš) su i dalje deo tvoje površine rizika — proveri ih periodičnom
  proverom razlike, ne samo jednom pri uvođenju.
- "Primena je uspešna" dokazuje da je komanda poslata, ne da se stvarno
  stanje promenilo — kad postoji mogućnost skrivenog, nadređenog prekidača,
  jedini pravi dokaz je sledeći plan izvršen posle primene, protiv osveženog
  stanja.
- Pisana odluka bez datuma ne razlikuje se od trajne istine — kad je vratiš
  na staro jer "tako piše," proveri prvo da li još uvek važi, ne samo da li
  je zapisana.

## 8.5 Vežba za čitaoca

Uzmi bilo koju biblioteku ili SDK u svom sistemu koja šalje podatke ka
spoljnom servisu (RUM, analytics, error tracking) i nabroj **svaki** tip
signala koji ta biblioteka šalje (logovi, metrike, greške, trejsovi, session
replay ako postoji). Za svaki tip, proveri nezavisno da li prolazi kroz isti
filter za osetljive podatke kao i ostali, ili ima sopstveni, poseban put.
Ako ne znaš odgovor sa sigurnošću za bar jedan tip signala — to je rupa koju
ovo poglavlje traži da zatvoriš pre nego što je neko drugi otkrije umesto
tebe.

---

### Izvori korišćeni u analitičkom delu

- [What Is Real User Monitoring (RUM)? — Dash0](https://www.dash0.com/faq/what-is-real-user-monitoring)
- [OpenTelemetry for Web RUM — RUM Architecture, Tooling & Self-Hosting](https://www.rum-core-web-vitals.com/rum-architecture-tooling-self-hosting/opentelemetry-for-web-rum/)
- [RUM vs synthetic monitoring: which do you need? — ClickHouse](https://clickhouse.com/resources/engineering/rum-vs-synthetic-monitoring)
- [Performance Monitoring: RUM vs. Synthetic Monitoring — MDN](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Rum-vs-Synthetic)
- [Real User Monitoring (RUM) — OneUptime](https://oneuptime.com/product/rum)
