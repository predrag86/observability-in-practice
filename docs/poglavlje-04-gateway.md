# Poglavlje 4 — Gateway obrazac: centralna tačka za telemetriju

Zamisli luku. Brodovi stižu sa svih strana sveta, svaki sa drugačijim tovarom,
drugačijim papirima, drugačijim namerama. Kad bi svaki brod sam odlučivao gde
da istovari robu i sam sebi izdavao dozvolu za ulazak, luka bi bila haos za
par nedelja — ne zato što bi kapetani bili nepošteni, nego zato što dosledna
primena pravila zahteva jedno mesto gde se ta pravila primenjuju, a ne hiljadu
nezavisnih tumačenja. Zato roba prolazi kroz carinski terminal: manji broj
kontrolisanih tačaka, gde se ista provera radi na isti način, bez obzira ko je
pošiljalac i odakle dolazi.

Takav terminal ima cenu — ako stane, staje i sav protok kroz njega. Zato dobre
luke ne rešavaju taj rizik tako što ukidaju terminal, nego tako što ih grade
više od jednog, i svaki tretiraju sa punom ozbiljnošću, ne uzgredno.

Ista logika važi za telemetriju — samo je roba drugačija, i to je pitanje na
koje ovo poglavlje odgovara.

## 4.1 Pitanje na koje ovo poglavlje odgovara

Svaki sistem koji šalje telemetriju u cloud servis (Grafana Cloud, Datadog,
Honeycomb...) mora da odgovori na isti arhitektonski problem kao luka iz
uvoda, pre nego što se napiše ijedna linija instrumentacije: **da li svaki
pošiljalac priča direktno sa cloud-om, ili postoji nešto između?**

To "nešto između" — kolektor koji stoji na putu i radi nešto sa signalom pre
nego što ga pusti dalje — zove se u OpenTelemetry svetu jednostavno *gateway*.
Pitanje zvuči kao detalj infrastrukture. Nije. Od njega zavisi ko drži
kredencijale za cloud, gde se troši budžet za obradu, šta se dešava kada cloud
servis ima kratak prekid, i — kao što ćemo videti — koliko će koštati svaki novi
tip pošiljaoca koji se doda za godinu dana.

## 4.2 Kako je to urađeno — praktičan pregled

U implementaciji koju pratimo kroz knjigu, odluka je bila: **jedan centralni
gateway, u visokoj dostupnosti, kroz koji prolazi skoro sav saobraćaj.**

Konkretno:

- Gateway je **Grafana Alloy** (distribucija OpenTelemetry Collector-a koju
  održava Grafana Labs), pokrenut kao dva nezavisna zadatka na kontejnerskoj
  platformi (AWS ECS/Fargate), iza internog load balansera.
- Svi pošiljaoci — bilo da su to duže-živi servisi (backend aplikacija) ili
  kratkotrajni batch zadaci — gađaju **jedno stabilno DNS ime** koje ostaje isto
  kroz rebuild-ove i samog gateway-a i load balansera. Nijedan pošiljalac ne zna
  niti ga zanima koja od dve instance gateway-a je trenutno primila njegov
  signal.
- Gateway je **jedino mesto koje drži kredencijale za cloud** (basic-auth token
  ka Grafana Cloud-u). Nijedna aplikacija, nijedan batch zadatak, nijedan
  sidecar ne zna taj token — što znači da kompromitovanje bilo kog pojedinačnog
  servisa ne kompromituje pristup posmatračkoj platformi.
- Na gateway-u se dešava sva obrada koja mora biti dosledna kroz ceo sistem:
  odsecanje šuma (health-check pozivi), skidanje osetljivih atributa,
  ograničavanje veličine poruka, agregacija visoko-kardinalnih dimenzija — sve
  ono što je detaljno obrađeno u Poglavlju 10. Ovde je bitno samo da postoji
  **jedno mesto** gde se te odluke primenjuju, umesto da se ista logika
  kopira u svaki servis posebno.

Šematski, to izgleda ovako:

![Telemetrija ide od pošiljalaca ka jednom stabilnom DNS imenu, koje ravnopravno raspoređuje saobraćaj na dve nezavisne gateway instance; samo gateway razgovara sa cloud platformom.](diagrams/diagram.png){: width="100%" }

Ono što ovaj dijagram *ne* pokazuje, a bitno je: postoji mala, **eksplicitno
dokumentovana** lista pošiljalaca koji gateway **zaobilaze** — Lambda funkcija
koja javlja o padu zadataka, i browser-korisnički interfejs. Oba imaju isti
razlog: gateway živi u privatnoj mreži i fizički mu ne mogu pristupiti (Lambda
nije u istoj virtuelnoj mreži; browser korisnika nikad neće imati pristup
internoj infrastrukturi). Umesto da se ta ograničenja zaobilaze veštački, obe
komponente dobijaju sopstveni, uzak put direktno do cloud-a — i to je namerno,
ne previd. Vratićemo se na ovaj princip u Poglavlju 7.

## 4.3 Analitički deo — kako to rade drugi, i zašto smo (delimično) drugačije

### Šta zvanična dokumentacija preporučuje

OpenTelemetry projekat ima zvanično opisana tri (u praksi četiri, ako se ubroji
"nema kolektora uopšte") obrasca raspoređivanja kolektora:

1. **Bez kolektora** — aplikacija šalje direktno u cloud. Najmanje pokretnih
   delova, ali svaki prekid cloud servisa se oseti direktno u aplikaciji, i
   nema mesta za centralizovanu obradu.
2. **Agent obrazac** — kolektor po hostu/podu (npr. kao DaemonSet u Kubernetes-u),
   lokalni "sused" aplikacije koji radi kao privremeni bafer i mesto za
   transformaciju pre slanja dalje.
3. **Agent-to-gateway obrazac** — agenti na svakom čvoru šalju napred ka
   manjem broju centralnih gateway instanci koje rade tešku obradu (tail
   sampling, redakcija, jedinstvena politika) i koje su jedina tačka koja drži
   kredencijale.
4. **Gateway-only obrazac** — pošiljaoci idu direktno na centralni gateway,
   bez lokalnog posrednika.

Zvanična preporuka za veće, produkcione sisteme je **agent-to-gateway**
(obrazac #3) — to je ono što OpenTelemetry dokumentacija, Datadog-ov vodič za
izbor arhitekture i više nezavisnih analiza (SigNoz, OneUptime) navode kao
"industrijski standard" za sisteme koji rastu. Razlog je konkretan: lokalni
agent daje bafer ako centralni gateway zakaže, hvata podatke specifične za host
(metrike operativnog sistema, Kubernetes atribute) koje ništa drugo prirodno ne
vidi, i skalira se nezavisno od gateway sloja — broj agenata prati broj
čvorova, broj gateway instanci prati zapreminu telemetrije, i te dve krive
retko rastu zajedno.

### Gde smo svesno otišli drugačijim putem

Implementacija koju analiziramo **nema opšti agent sloj**. Većina pošiljalaca
ide direktno na gateway — što je, po gornjoj taksonomiji, bliže obrascu #4
(gateway-only), sa jednim značajnim izuzetkom: za kratkotrajne kontejnerske
zadatke koristi se **sidecar po zadatku** (kolektor upregnut uz aplikaciju u
istom zadatku, ali ne trajan agent na čvoru — čvor u serverless kontejnerskom
svetu ni ne postoji na način na koji ga zvanična dokumentacija zamišlja). Treći
komad — pull-bazirani izvori (baze, samostalno upravljani klasteri, SaaS) —
uopšte ne liči ni na jedan od četiri standardna obrasca, jer tamo *gateway
sam* radi posao koji bi agent obično radio, samo u smeru povlačenja umesto
guranja podataka.

Zašto ovo odstupanje, i da li je to greška? Tri razloga, svaki proveriv:

**1. "Čvor" na koji bi se agent instalirao često ne postoji.** Zvanični
agent-obrazac pretpostavlja stabilan host — VM ili Kubernetes node — na kome
DaemonSet živi danima ili nedeljama i prirodno hvata host-nivo metrike. Kod
kratkotrajnih serverless kontejnerskih zadataka (batch posao koji živi par
minuta i onda nestaje) ta pretpostavka ne važi: nema stabilnog čvora, ima samo
efemernog zadatka. Sidecar-po-zadatku nije "siromašnija verzija" agenta — to
je *ispravan* prevod istog principa (lokalni pratilac koji hvata
resurs-specifične podatke i daje prostor za graciozno gašenje) u okruženje gde
klasičan DaemonSet fizički nema na šta da se zakači. Ovo je važna razlika za
čitaoca: kada standardni obrazac ne stane na tvoju infrastrukturu, pravo
pitanje nije "kako da ga na silu primenim" nego "koji je princip iza obrasca, i
kako taj princip izgleda u mom okruženju."

Vredi ovde biti eksplicitan umesto da ostane implicitno u prethodnom pasusu:
sistem koji knjiga prati ne pokreće Kubernetes **nigde** — ni za ovaj
gateway, ni za bilo šta drugo u sistemu (kontejnerska platforma je servisi
bez upravljanih čvorova, uz nekoliko klasičnih virtuelnih mašina, funkcije
bez servera i upravljani batch servis). Ovo nije propust u pokrivenosti
knjige nego prenesena, stvarna arhitektura, i vredi je imati na umu kroz
ostatak knjige: čitava kategorija alata koja pretpostavlja postojanje
Kubernetes klastera — bilo mrežni alati zasnovani na direktnom pristupu
jezgru operativnog sistema, bilo operatorski agenti koji očekuju klaster
kojim upravljaju — jednostavno nije primenjiva na ovakvu infrastrukturu, ne
zbog nedostatka nego zbog strukturne pretpostavke koju sam alat nosi u
sebi. Čitalac čiji sistem **jeste** na Kubernetes-u dobija, iz iste
činjenice, obrnutu prednost: cela ta kategorija alata mu je na raspolaganju
na način na koji ovoj implementaciji nikad neće biti — vredi to imati u
vidu kad god neko poglavlje kasnije kaže da je neki alat razmotren i
odbijen: razlog je često baš ovaj, ne kvalitet samog alata.

**2. Cena lokalnog hop-a nije uvek isplativa.** Zvanična prednost agent sloja —
lokalni bafer koji preživljava kratak prekid gateway-a — ima realnu cenu:
dodatni proces po instanci, dodatna slika za održavanje, dodatna tačka koja
može da otkaže. Za sistem gde je broj dugotrajnih servisa mali (nekoliko app
instanci, ne hiljade), a gateway je već u HA (dve nezavisne instance iza load
balansera sa DNS otpornim na rebuild), granularni rizik koji agent sloj
uklanja je mali, dok je operativna cena — još jedan artefakt da se gradi,
verzioniše i prati za svaki servis — realna i konstantna. Ovo je račun koji se
mora raditi eksplicitno, ne pretpostaviti: "industrijski standard" je dobra
polazna tačka, ne automatska odluka.

**3. Tail sampling — glavni razlog *za* agent-to-gateway šablon u zvaničnoj
dokumentaciji — ovde uopšte nije u igri.** Ovo je najvredniji nalaz ovog
poređenja. Zvanični agent-to-gateway obrazac dobija najviše smisla kada gateway
mora da radi *tail-based sampling* — odluku "da li da zadržim ovaj trejs"
donetu tek pošto se vide svi njegovi delovi. Za tu odluku, load-balancing
exporter mora da hešira po trace ID-u tako da svi delovi jednog trejsa stignu
na **istu** gateway instancu — bez toga tail sampling ne radi ispravno. To je
netrivijalan zahtev koji utiče na to kako se gateway sloj balansira.
Implementacija koju analiziramo je **eksplicitno odbila** tail sampling na
gateway nivou (razrađeno u Poglavlju 12) u korist server-side adaptivnog
uzorkovanja na cloud strani. Rezultat: ograničenje koje bi opravdalo
kompleksniji, trace-svestan load-balancing sloj — prosto ne postoji ovde.
Običan L4 load balanser je dovoljan, jer nijedna odluka na gateway-u ne zavisi
od toga da li su svi delovi jednog trejsa stigli na isto mesto. **Kada
odbaciš jedan zahtev iz udžbeničkog rešenja, prirodno otpada i deo arhitekture
koji je postojao samo da bi taj zahtev zadovoljio** — dobra opšta lekcija za
čitaoca kada poredi svoj sistem sa referentnom arhitekturom.

### Cena izbora: šta bi se desilo da smo išli "po knjizi"

Vredi odigrati i suprotan scenario, jer to je ono što razlikuje inženjersku
odluku od slepog kopiranja preporuke.

Da je uveden pun agent-to-gateway sloj sa DaemonSet-om na svakom kontejnerskom
"čvoru": u serverless Fargate okruženju bi to značilo dodatni pratilac proces
po zadatku (što se u praksi svodi na isto što i sidecar koji već postoji za
batch flotu — samo preimenovan), ali *i* za dugotrajne servise koji danas idu
direktno na gateway. Za tih par dugotrajnih servisa, dodatni lokalni kolektor
bi značio: još jedna slika koja mora da prati verzije OpenTelemetry
Collector-a, još jedan proces koji troši memoriju pored same aplikacije, i —
najskuplje od svega — još jedna komponenta čiji pad treba dijagnostikovati kada
nešto ne štima ("da li je problem u aplikaciji, u lokalnom agentu, u
gateway-u, ili u mreži između njih?"). Realna korist bi bila mala: gateway već
jeste u HA, a jedini scenario u kome bi lokalni bafer stvarno pomogao — potpuni
pad *oba* gateway zadatka istovremeno — već je pokriven drugim, jeftinijim
mehanizmom (sintetičko spoljašnje praćenje iz Poglavlja 9, koje uopšte ne
zavisi od gateway-a).

Obrnuto, da je izabran čist "bez-kolektora" obrazac (svaka aplikacija direktno
u cloud, bez ičega između): svaka aplikacija bi morala da nosi cloud
kredencijale, svaka promena politike obrade (npr. "sakrij ovaj atribut za
celu flotu") zahtevala bi izmenu u svakom repozitorijumu ponaosob, i — što je
posebno bitno za temu troškova iz Poglavlja 11 — ne bi postojalo jedno mesto na
kome se kardinalnost i cena mogu presresti pre nego što stignu do
naplativog dela cevovoda. Gateway sloj se u praksi vrlo brzo plati kroz jednu
jedinu intervenciju te vrste.

### Zašto Grafana Alloy, a ne "čist" OpenTelemetry Collector

Druga odluka vredna analize: gateway nije pokrenut kao vanilla
`opentelemetry-collector-contrib` distribucija, nego kao Grafana Alloy —
Grafana Labs-ova sopstvena distribucija istog kolektorskog jezgra, sa svojom
konfiguracionom sintaksom (River/Alloy jezik umesto standardnog YAML pipeline
opisa) i ugrađenim komponentama za povlačenje metrika (npr. direktno iz
CloudWatch-a ili Postgres-a).

Nezavisne analize ovog izbora (uključujući i kritičke, ne samo promotivne)
navode realan rizik: Alloy uvodi **sopstvenu, ne-standardnu sintaksu** i
podrazumevano gura korisnika ka Grafana-inom ekosistemu (Loki za logove,
Mimir/Prometheus za metrike), što otežava kasniju migraciju na drugog
dobavljača — klasičan oblik blagog vendor lock-in-a, uprkos tome što protokol
kojim se šalje napred (OTLP) ostaje standardan.

U implementaciji koju analiziramo, taj rizik je svesno prihvaćen iz dva
razloga koja imaju smisla samo *u kontekstu* — ovo nije opšte pravilo "Alloy je
bolji", nego primer kako se takva odluka opravdava:

1. **Downstream je već Grafana Cloud.** Cena vendor-vezanosti na nivou
   kolektora je marginalna kada je cela posmatračka platforma iza njega već
   kod istog dobavljača — lock-in na konfiguracionoj sintaksi kolektora ne
   dodaje novi rizik povrh onog koji je već prihvaćen izborom platforme.
2. **Ugrađeni pull-eksporteri menjaju čitavu jednu kategoriju infrastrukture.**
   Da je izabran čist OpenTelemetry Collector, povlačenje CloudWatch i
   Postgres metrika (Poglavlje 7) zahtevalo bi *odvojenu* Prometheus
   infrastrukturu sa `remote_write` ka istom cilju — još jedna komponenta,
   još jedan sloj za rad i praćenje. Alloy to radi u istom procesu, istom
   pipeline-u, istom monitoring sloju kao i sve ostalo.

Poenta za čitaoca nije "izaberi Alloy" — poenta je da svaka odluka o
konkretnom alatu mora biti opravdana kroz *ono što ta odluka menja nizvodno*,
ne kroz reputaciju alata samog po sebi.

Vratimo se na luku s početka poglavlja. Terminal ne rešava rizik od zastoja
tako što se ukine, nego tako što se izgradi više od jednog i svaki tretira sa
punom ozbiljnošću — tačno ono što gateway iz ovog poglavlja radi sa dve
nezavisne instance umesto jedne. **Centralizacija nije suprotnost
pouzdanosti — ona je priznanje da je lakše učiniti pouzdanim jedno
kontrolisano mesto nego hiljadu nekontrolisanih**, uz uslov da se to jedno
mesto zaista tretira sa punom ozbiljnošću. Mera te ozbiljnosti vraćaće se kroz
celu knjigu: da li mesto ima dovoljno redundanse, da li njegov pad ima
nezavisan način da bude primećen, i da li iko van njega može da nastavi da
radi kada ono padne.

## 4.4 Skupljena pravila iz ovog poglavlja

- Standardni obrazac (agent + gateway) je dobra polazna pretpostavka, ali
  proveri da li čvor na koji bi agent išao *uopšte postoji* u tvom okruženju
  pre nego što ga kopiraš.
- Kada odbaciš jedan zahtev iz referentne arhitekture (npr. tail sampling),
  proveri šta je *u toj arhitekturi* postojalo samo zbog tog zahteva — često
  možeš da uprostiš i taj deo.
- Gateway koji drži cloud kredencijale mora biti tretiran kao kritična
  infrastruktura eksplicitno: HA, stabilna adresa, i nezavisan način da neko
  primeti kada je pao (ne samo "alarmi prestanu da stižu" — to je tiho i lako
  se propusti, videćemo u Poglavlju 14 zašto).
- Svaka odluka o alatu ("zašto baš ovaj kolektor/ovaj dobavljač") treba da se
  opravda kroz ono što ta odluka menja *nizvodno* (koje druge komponente
  postaju nepotrebne ili neophodne), ne kroz opštu reputaciju alata.
- Namerno zaobilaženje gateway-a (za komponente koje fizički ne mogu da mu
  pristupe) treba da bude **spisak sa razlogom**, ne slučajno odstupanje koje
  neko otkrije šest meseci kasnije.
- Znaj eksplicitno da li tvoja infrastruktura pretpostavlja Kubernetes ili ne
  — cela kategorija alata (mrežni alati zasnovani na jezgru, operatorski
  agenti) je dostupna ili strukturno neprimenljiva u zavisnosti od tog
  jednog odgovora, nezavisno od kvaliteta samog alata.

## 4.5 Vežba za čitaoca

Nacrtaj dijagram sopstvenog sistema onako kako telemetrija danas putuje —
svaka aplikacija, svaka baza, svaki eksterni servis. Za svaku strelicu ka
cloud servisu postavi tri pitanja: (1) da li ova komponenta drži cloud
kredencijale direktno, (2) šta bi se desilo kada bi cloud servis bio
nedostupan 5 minuta, i (3) ko bi prvi primetio da ova strelica prestane da
radi. Ako je odgovor na (3) "niko, dok neko ne primeti da nešto drugo ne
štima" — to je tvoj prvi kandidat za gateway.

---

### Izvori korišćeni u analitičkom delu

- [Agent-to-gateway deployment pattern — OpenTelemetry](https://opentelemetry.io/docs/collector/deploy/other/agent-to-gateway/)
- [Gateway deployment pattern — OpenTelemetry](https://opentelemetry.io/docs/collector/deploy/gateway/)
- [Agent deployment pattern — OpenTelemetry](https://opentelemetry.io/docs/collector/deploy/agent/)
- [How to select your OpenTelemetry deployment — Datadog](https://www.datadoghq.com/blog/otel-deployments/)
- [OpenTelemetry Deployment Patterns Explained — SigNoz](https://signoz.io/blog/opentelemetry-deployment-patterns/)
- [How to Set Up High-Availability Collector Deployments with Agent-Gateway Pattern — OneUptime](https://oneuptime.com/blog/post/2026-02-06-high-availability-collector-agent-gateway-pattern/view)
- [Grafana Alloy: OpenTelemetry, With Some Abstraction Issues — Coralogix](https://coralogix.com/blog/the-grafana-alloy-dilemma/)
