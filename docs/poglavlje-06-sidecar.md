# Poglavlje 6 — Kontejnerska/batch radna opterećenja: sidecar obrazac

Na visokoj planini, penjač nikad ne ide sam — ide vezan konopcem za partnera.
Taj partner se ne nalazi u baznom logoru čekajući da se neko vrati sa
problemom; on se penje *sa* tobom, korak po korak, i kad ti siđeš sa planine,
silazi i on, u isto vreme, istim tempom. Bazni logor, s druge strane, ima
lekara koji čeka sve penjače podjednako — koristan, ali fizički ne može da te
prati na liticu, i ne zna tačno gde si u trenutku kad ti zatreba pomoć.

Kad je radno opterećenje kratkotrajno — pokrene se, uradi posao, nestane za
par minuta — ono treba pratioca koji deli tačno njegov životni vek, ne
stalnog čuvara koji čeka u bazi i nada se da će stići na vreme. To je razlika
između sidecar-a i agenta, i to je pitanje na koje ovo poglavlje odgovara.

## 6.1 Pitanje na koje ovo poglavlje odgovara

Poglavlje 4 je uvelo gateway kao centralnu tačku, a Poglavlje 2 auto- i
ručnu instrumentaciju za dugotrajne servise. Ali šta se dešava kad pošiljalac
telemetrije nije dugotrajan servis nego kratkotrajan batch zadatak — proces
koji se rodi, odradi posao, i nestane za par minuta, možda i sekundi? Da li
takav zadatak treba isti tretman kao dugotrajan servis (direktna veza ka
gateway-u), ili mu treba nešto strukturno drugačije?

Odgovor ovog poglavlja je: nešto strukturno drugačije — **sidecar kolektor,
upregnut uz svaki zadatak, koji deli tačno njegov životni vek.** Razlog nije
stilski nego životno-ciklusni, i vidi se najjasnije baš na onome što se
dešava kad zadatak nestane.

## 6.2 Kako je to urađeno — praktičan pregled

Svaki batch/ETL zadatak u sistemu koji knjiga prati pokreće se kao AWS
ECS/Fargate task definicija sa **dva kontejnera**: glavni kontejner koji radi
posao, i sidecar kontejner — lagana OpenTelemetry Collector distribucija
(ADOT — AWS Distro for OpenTelemetry) — koji prima telemetriju od glavnog
kontejnera preko `localhost`, radi minimalnu obradu (batch, dodavanje
resursnih atributa), i prosleđuje je ka centralnom gateway-u iz Poglavlja 4.

Zadatak i njegov sidecar dele **isti task lifecycle**: pokreću se zajedno,
gase se zajedno. Kad glavni kontejner završi posao, ECS task definicija je
podešena da sidecar dobije kratak, ali eksplicitan prozor da isprazni (flush)
sve što još drži u baferu pre nego što se ceo zadatak ugasi — bez tog
prozora, poslednjih par sekundi telemetrije bi jednostavno nestalo zajedno sa
kontejnerom koji ih je proizveo.

![Zadatak i sidecar dele isti ECS/Fargate task — pokreću se i gase zajedno; sidecar dobija kratak flush prozor pre gašenja da isprazni bafer ka centralnom gateway-u.](diagrams/ch6-sidecar.png){: width="85%" }

Ovaj obrazac, uveden u produkciju posle prvobitnog pilot-a na dva zadatka
(razrađeno u Poglavlju 30), otkrio je katalog stvarnih zamki koje nijedna
"quickstart" dokumentacija ne pominje:

- **Sidecar ne postavlja `service.name` sam od sebe.** Za razliku od
  dugotrajnog servisa gde SDK zna sopstveni naziv iz koda, sidecar kolektor
  nema pojma koji je zadatak pokrenut pored njega — mora mu se eksplicitno
  ubrizgati kroz promenljivu okruženja u task definiciji. Bez toga, deseci
  različitih batch zadataka bi u cloud-u izgledali kao jedan neimenovani
  izvor, i dashboard koji filtrira po nazivu zadatka jednostavno ne bi imao
  šta da filtrira.
- **OTLP→Prometheus prevod dodaje sufikse jedinica koji nisu očigledni.**
  Metrika koja u kodu nosi ime `queue_depth` i jedinicu "items" stiže u
  Mimir kao nešto poput `queue_depth_items_total` ili sa sličnim sufiksom u
  zavisnosti od tipa — što znači da "očigledan" naziv metrike, onaj koji bi
  neko intuitivno otkucao u upitu, prosto ne postoji. Svaki novi tim mora
  prvo da otkrije stvarno ime, obično kroz `list_prometheus_metric_names`
  ili sličan alat, pre nego što napiše prvi PromQL upit.
- **Mimir ne promoviše svaki resursni atribut u lejbl.** Podrazumevano se
  promovišu samo eksplicitno navedeni atributi — ako novi resursni atribut
  nije dodat na tu listu, on stiže do Mimir-a, ali ostaje nevidljiv za
  filtriranje po njemu. Praktičan trik za proveru da je signal uopšte prošao
  kroz ceo pipeline (a ne samo da postoji na strani aplikacije): upit protiv
  `target_info` metrike, koju kolektor generiše automatski iz resursnih
  atributa i koja postoji nezavisno od toga da li je aplikacija poslala ijednu
  sopstvenu metriku tog minuta.
- **Neke biblioteke emituju samo spanove, ne i metrike.** Za takve
  komponente, jedini operativni signal na nivou metrike su
  `traces_spanmetrics_*` serije koje Tempo metrics-generator izvodi iz
  samih trejsova (obrađeno detaljnije u Poglavlju 11) — bez razumevanja da
  taj mehanizam postoji, tim bi zaključio da biblioteka "nema metrike", kad u
  stvari ima, samo indirektno.

### Kad novi sidecar izgleda kao uzrok pada — tri činjenice koje su ga oslobodile

Prvi talas kritičnih alarma posle uvođenja sidecar-a na jednu od batch flota
izgledao je kao klasična regresija: zadaci su počeli da se gase sa greškom
odmah po uvođenju nove verzije definicije zadatka, glavni kontejner je
izlazio sa neuspešnim statusom dok je sidecar izlazio čisto. Prvi instinkt —
"nova verzija je nešto pokvarila" — bio je pogrešan, i dokazano pogrešnim, ne
samo pretpostavljeno.

Tri nezavisne činjenice su oslobodile sidecar krivice. Prvo, identična greška
sa identičnim porukama postojala je u logovima tri dana pre nego što je
sidecar uopšte dodat — samo, pre toga, niko je nije mogao videti na jednom
mestu po identifikatoru zadatka, jer platforma za posmatranje još nije imala
uvid u tu flotu. Drugo, isti build, isto pokretanje modela, iste definicije
zadatka — neke varijante posla su tog dana prošle bez greške, dok su druge,
sa identičnim kontejnerskim otiskom, pale. Treće, greška je pogađala samo
jednu uzano definisanu kombinaciju ulaznih parametara, ne flotu uopšte —
oblik kvara vezan za podatke koje taj zadatak obrađuje, ne za infrastrukturu
koja ga pokreće.

Ironija je da je sam čin uvođenja sidecar-a taj problem prvi put učinio
vidljivim kao **obrazac**, ne kao izolovan incident: pošto su logovi grešaka
sad bili upitljivi po identifikatoru zadatka, tim je mogao da potvrdi da se
identična greška ponavljala iz dana u dan, i time dokaže da je uzrok stariji
od bilo koje promene te nedelje. Sidecar nije izazvao problem — otkrio je
problem koji je već postojao, nevidljiv.

Opšta pouka: prva sumnjiva promena posle bilo kakvog rollout-a je gotovo
uvek sama ta promena, jer je najsvežija u sećanju — ali korelacija sa
trenutkom uvođenja nije dokaz uzroka. Pre nego što se nova komponenta
proglasi krivom, vredi proveriti da li isti simptom postoji i van njenog
prisustva: u starijim logovima, na build-u koji je prethodio promeni, na
uporedivim zadacima koji tu promenu još nisu dobili.

### Flush prozor koji sidecar dobija ne pokriva ceo put

Sidecar dobija eksplicitan, kratak prozor pre gašenja da isprazni sve što
drži u sopstvenom baferu — to je opisano iznad, i tačno je, ali opisuje samo
**polovinu** puta koji telemetrija prelazi između glavnog kontejnera i
gateway-a.

Put ima dva odvojena skoka. Prvi: glavni kontejner do sidecar-a, preko
`localhost`. Drugi: sidecar do gateway-a, preko mreže. Prozor za gašenje koji
ECS task definicija garantuje pokriva **samo drugi skok** — vreme koje
sidecar dobija da isprazni ono što već drži pre nego što ga infrastruktura
prekine. Ne garantuje ništa o prvom skoku: ako SDK u glavnom kontejneru
koristi podrazumevani, **asinhroni** mehanizam za baferovanje raspona i
log zapisa (šalje ih u pozadinskim, periodičnim talasima, ne odmah kako
nastanu), i ako se ceo zadatak ugasi pre nego što taj mehanizam stigne do
svog sledećeg periodičnog slanja, ono što je u tom trenutku u baferu
glavnog kontejnera jednostavno nestaje zajedno sa procesom koji ga je
proizveo — nezavisno od toga koliko dug prozor sidecar dobija, jer sidecar
nikad nije ni video te podatke.

Ovo najviše pogađa baš onu klasu zadataka za koju je sidecar obrazac
prvenstveno i uveden: kratkotrajne, koji se gase sekundama posle pokretanja.
Duže-živeći servis ima dovoljno vremena da periodično slanje prirodno
stigne pre gašenja; zadatak koji traje par sekundi možda se ugasi pre nego
što je i jedan ciklus baferovanja završen.

Popravka nije u sidecar-u niti u dužini njegovog prozora za gašenje — mora
ići na strani glavnog kontejnera: eksplicitno, sinhrono pražnjenje bafera pre
izlaska iz procesa (ili prelazak na jednostavniji, sinhroni način slanja koji
ne baferuje u pozadini), tako da ništa ne ostane neposlato u trenutku kad
proces završi. Sidecar-ov prozor za gašenje i dalje ima svrhu — štiti drugi
skok — ali ne može nadoknaditi ono što se izgubilo pre nego što je uopšte
stiglo do njega.

![Flush prozor koji sidecar dobija pre gašenja (stopTimeout) pokriva samo drugi skok — sidecar do gateway-a. Ne pokriva prvi skok — asinhroni bafer u glavnom kontejneru do sidecar-a preko localhost-a — koji se gubi bez traga ako se zadatak ugasi pre sledećeg periodičnog slanja.](diagrams/ch06-flush-prozor.png){: width="75%" }

### Drift kroz reviziju: tri konkretna kvara i kako se sad hvataju

Sve zamke navedene do sada u ovom poglavlju dešavaju se **unutar** jedne
verzije task definicije — kako je konfigurisana, kako se gasi, šta prima.
Postoji i potpuno drugačija klasa kvara, koja nema veze sa sadržajem
nijedne pojedinačne revizije: **ista porodica zadataka može biti
lansirana sa više od jednog mesta, i svako od tih mesta pamti sopstveni
broj revizije.** Registrovanje nove, ispravne revizije sa sidecar-om ne
znači da je iko zaista počeo da je koristi — to je samo upisano u AWS kao
mogućnost, dok svaki launcher i dalje pokreće broj revizije na koji je
poslednji put eksplicitno pokazan.

![Jedna porodica, tri nezavisne tačke lansiranja — svaka pinovana na svoju reviziju; registrovanje nove revizije ne ažurira nijedan pin automatski.](diagrams/ch06-pinovi-driftuju.png){: width="90%" }

Tri stvarna slučaja ovog obrasca, svaki drugačiji:

1. **Par veličina, jedna polovina zaboravljena.** Jedna porodica zadataka
   postoji u dve veličine — standardna i "LARGE" varijanta za posebno
   zahtevan dnevni prozor — registrovane kao susedne revizije istog para.
   Kad je sidecar dodat, nova standardna revizija je registrovana ispravno
   — ali LARGE polovina istog para je registrovana **bez** sidecar-a,
   propuštena jer je par tretiran kao jedna izmena umesto dve. Rezultat:
   LARGE varijanta je nedeljama radila potpuno slepo za observability, a
   Slack alarmi koji su je pokrivali otvarali su linkove ka praznim
   Grafana dashboard-ima — alarm je i dalje radio (jer prati sam ECS, ne
   telemetriju), ali istraga alarma nije imala šta da pokaže.
2. **Porodica koja nikad nije ni ušla u talas onboardovanja.** Jedna
   porodica ima launcher koji hardkoduje **dve** odvojene pinovane
   revizije za dva različita moda rada, ne jednu. Talas onboardovanja koji
   je sistematski prošao kroz sve porodice i dodao sidecar je, po
   pretpostavci "jedna porodica = jedan pin", tu porodicu jednostavno
   preskočio — nije bila greška u primeni, nego u premisi. Nekoliko
   otkaza dnevno ostalo je nevidljivo nedeljama, ne zato što alarm nije
   radio, nego zato što porodica nikad nije ni dobila signal koji bi
   alarm mogao da pročita.
3. **Izmena nevezana za observability koja je ipak obrisala sidecar.**
   Treći slučaj nije ni pokušaj da se nešto doda niti oduzme u vezi sa
   telemetrijom — nova revizija je registrovana samo da bi se udvostručio
   CPU limit porodice, ali je pri tom, kloniranjem sa pogrešne polazne
   revizije, tag image-a tiho vraćen na `:latest` — a `:latest` je
   verzija bez sidecar-a. Ovaj slučaj je ostao samo potencijalna, a ne
   stvarna šteta, jer nijedan launcher još nije pomeren na tu reviziju —
   ali je otkriven kao zamka koja čeka prvog ko odluči da "pređe na
   najnoviju verziju" bez provere da li je ta najnovija verzija zaista i
   dalje instrumentirana.

Zajednička nit sva tri slučaja: **registrovanje revizije i lansiranje
revizije su dva odvojena čina, i drift između njih je nevidljiv dok ga
neko eksplicitno ne proveri.** Otud i pravilo koje sad važi za svaku
izmenu porodice: nova revizija se pravi kloniranjem revizije koja je
**trenutno stvarno pinovana** od strane launcher-a, nikad od najnovije u
konzoli niti od proizvoljne starije — napred, nikad unazad, nikad
ustranu. A pošto jedna porodica ume da ima više od jednog launcher-a
(promenljiva okruženja, hardkodovan broj u kodu, čak i EventBridge
pravilo bez broja revizije koje automatski uzima najnoviju aktivnu), svaki
pin mora biti pronađen i ponovo eksplicitno usmeren — ne pretpostaviti da
je jedan pronađeni pin i jedini koji postoji.

Provera da je nova revizija zaista stigla do prometa, ne samo do AWS
registra, ide istim alatom već pomenutim ranije u poglavlju —
`target_info` — samo raščlanjenim po broju revizije:

```promql
count by (aws_ecs_task_revision) (last_over_time(target_info{service_name="ime-porodice"}[24h]))
```

Ako se očekivani novi broj revizije ne pojavi u rezultatu, nijedan
launcher još nije pomeren — dashboard može izgledati "zeleno" po starim
podacima dok se pinovi ne provere jedan po jedan. Uz ovu proveru na nivou
jedne porodice, sistem danas ima i automatizovanu, nedeljnu proveru na
nivou cele flote koja poredi svaku porodicu sa sopstvenom istorijom
revizija i prijavljuje kad novija revizija ispadne iz keep-liste sidecar-a
ili kad se dve revizije u istom paru veličina razlikuju po tome da li nose
sidecar. Ta provera ima jedno strukturno ograničenje vredno zapamćivanja:
**poredi porodicu samu sa sobom — ne zna koju reviziju launcher zapravo
pokreće.** Prijava da je novija revizija izgubila sidecar može značiti
"bezopasno, launcher je i dalje na staroj dobroj reviziji" ili "aktivan
prekid, launcher je već pomeren" — razlikovanje ta dva zahteva ručnu
proveru pina, alat samo ukazuje gde da se gleda.

## 6.3 Analitički deo — sidecar naspram agenta, i granica gde sidecar prestaje da se isplati

### Zašto sidecar, a ne node-agent, za ovu klasu opterećenja

Nezavisne analize ovog izbora (uključujući Last9-ovo poređenje sidecar vs.
agent obrazaca) navode tačno onaj kriterijum koji je odlučio ovaj slučaj:
sidecar daje **snažnu izolaciju procesa** i garantuje da se "aplikacija i
sidecar gase zajedno" — kritično za batch opterećenje, gde zadatak nestaje
za par minuta i gde bi orphan telemetrijski tok (podaci koji stignu posle
nestanka zadatka koji ih je generisao, ili obrnuto, izgubljeni podaci jer je
zadatak nestao pre nego što ih je sidecar stigao da pošalje) bio gori ishod
od malo veće potrošnje resursa. Node-agent, s druge strane, ima **nezavisan
životni ciklus** — ostaje aktivan i kad se zadaci na njemu menjaju — što je
prednost za stabilne, dugotrajne servise (baš kao u agent-to-gateway obrascu
iz Poglavlja 4, da je tamo bio primenjen), ali stvara neusklađenost tačno na
granici koja ovde najviše boli: kratkotrajni zadaci nestaju, agent ostaje, i
veza između "koji zadatak je proizveo koji podatak" postaje teža da se
garantuje.

Cena ovog izbora je realna i priznata u istoj analizi: sidecar znači veću
potrošnju resursa po zadatku (svaki zadatak nosi sopstvenu kopiju kolektora),
naspram jedne deljene instance agenta po čvoru. Za sistem koji knjiga prati,
ta cena je prihvaćena svesno — broj istovremenih batch zadataka je dovoljno
mali da dodatni CPU/memorija po zadatku ne predstavlja problem, dok bi
alternativa (deljeni agent) uvela tačno onu vrstu orphan-podataka rizika koju
sidecar eliminiše po definiciji.

### Granica gde sidecar prestaje da bude dobar izbor

Vredi eksplicitno pogledati kad ovaj obrazac **prestaje** da se isplati, jer
to je podjednako vredna lekcija kao i sam izbor. AWS-ov sopstveni materijal o
migraciji sa sidecar-a na centralizovani gateway obrazac (za telemetriju koja
prelazi granice više AWS naloga) navodi tri konkretna razloga zašto sidecar
po-zadatku prestaje da skalira: sidecar kolektor je linux-only slika, pa ne
radi kao pratilac uz Windows/.NET Framework zadatke, koji onda ili ostaju
neinstrumentirani ili nose kolektor koji ništa ne prikuplja; troškovi
po-zadatka rastu linearno sa brojem zadataka, dok centralni gateway ima
gotovo konstantnu cenu bez obzira na broj pošiljalaca; i konfiguracija
"drifta" — svaka kopija sidecar-a menja se nezavisno, bez jedne centralne
tačke za politiku prijema, tačno suprotno principu iz Poglavlja 4 ("jedno
mesto gde se ista provera radi na isti način").

Ovo nije kontradikcija sa odlukom u ovom poglavlju — to je granica primene.
Implementacija koju knjiga prati radi na obimu (desetine, ne hiljade
istovremenih batch zadataka, u jednom AWS nalogu) gde prednosti sidecar-a
(izolacija životnog ciklusa) jasno nadmašuju njegove mane (potrošnja
resursa, nedostatak centralne politike). Da je obim narastao za red veličine,
ili da se batch flota proširila na više naloga, ista analiza koja je ovde
opravdala sidecar bi opravdala prelazak na gateway obrazac za tu klasu
opterećenja — što je tačno primer principa iz Poglavlja 4: svaka odluka o
alatu se opravdava kroz kontekst, ne kroz apsolutnu ispravnost samog alata.

Vratimo se na penjača i konopac. Partner koji se penje sa tobom ima smisla
dok ste vas dvoje — dodaj još pedeset penjača na isti konopac, i sistem koji
je savršeno radio za dvoje postaje neuporediv teret. Sidecar je pravi izbor
za obim na kome ovaj sistem danas radi; **prava veština nije u tome da se
zapamti "sidecar je bolji od agenta", nego da se prepozna na kom obimu ta
tvrdnja prestaje da važi.**

## 6.4 Skupljena pravila iz ovog poglavlja

- Za kratkotrajna, efemerna radna opterećenja, prioritizuj obrazac koji deli
  životni ciklus zadatka (sidecar) nad obrascem sa nezavisnim životnim
  ciklusom (agent) — orphan telemetrija je gori ishod od veće potrošnje
  resursa.
- Eksplicitno ubrizgaj `service.name` i druge identifikacione atribute u
  sidecar preko env promenljivih — nikad ne pretpostavljaj da će ih sidecar
  "sam znati".
- Pre nego što napišeš prvi PromQL upit protiv nove metrike, proveri stvarno
  ime posle OTLP→Prometheus prevoda — sufiksi jedinica gotovo nikad nisu
  intuitivni.
- Koristi `target_info` (ili ekvivalent) kao brz test da li signal uopšte
  prolazi kroz ceo pipeline, nezavisno od toga da li aplikacija baš tog
  trenutka šalje sopstvene metrike.
- Sidecar obrazac ima granicu skaliranja (linux-only, troškovi po-zadatku,
  drift konfiguracije) — znaj unapred na kom obimu bi tvoj sistem prešao tu
  granicu, umesto da to otkriješ kad već bude bolno.
- Korelacija sa trenutkom uvođenja neke promene nije dokaz da je ta promena
  uzrok — pre nego što je proglasiš krivom, proveri da li isti simptom
  postoji i van njenog prisustva (stariji logovi, prethodni build, uporedivi
  slučajevi koji promenu još nisu dobili).
- Prozor za gašenje koji infrastruktura garantuje sidecar-u pokriva samo
  skok od sidecar-a nadalje — ne garantuje ništa o asinhronom baferu u
  glavnom kontejneru koji tek treba da stigne do sidecar-a preko localhost-a.
  Za kratkotrajne procese, popravka mora ići na strani aplikacije: eksplicitno
  pražnjenje bafera pre izlaska, ne oslanjanje na tuđi prozor za gašenje.

- Porodica zadataka može biti lansirana sa više od jednog mesta (env
  promenljiva, hardkodovan broj u kodu, EventBridge pravilo) — pre nego
  što proglasiš izmenu završenom, pronađi SVAKI pin, ne samo prvi na koji
  naiđeš.
- Novu reviziju uvek pravi kloniranjem revizije koja je trenutno stvarno
  pinovana od strane launcher-a — nikad od najnovije u konzoli, nikad od
  proizvoljne starije. Napred, nikad unazad, nikad ustranu.
- Posle svake izmene, proveri da je novi broj revizije zaista stigao do
  prometa (`target_info` raščlanjen po `aws_ecs_task_revision`), ne samo
  da je uspešno registrovan u AWS — registrovanje i lansiranje su dva
  odvojena čina.

## 6.5 Vežba za čitaoca

Pronađi jedan kratkotrajan zadatak u svom sistemu (batch posao, cron, Lambda)
koji trenutno šalje telemetriju direktno, bez ikakvog lokalnog pratioca.
Postavi pitanje: šta se dešava sa poslednjih par sekundi telemetrije ako
zadatak bude prekinut (timeout, OOM kill) pre nego što stigne da zatvori
konekciju? Ako je odgovor "verovatno se izgubi" — to je tvoj kandidat za
sidecar obrazac iz ovog poglavlja.

---

### Izvori korišćeni u analitičkom delu

- [Sidecar or Agent for OpenTelemetry: How to Decide — Last9](https://last9.io/blog/opentelemetry-sidecar-vs-agent/)
- [Centralize cross-account Amazon ECS telemetry with an ADOT gateway — AWS](https://aws.amazon.com/blogs/containers/centralize-cross-account-amazon-ecs-telemetry-with-an-adot-gateway/)
- [Setting up AWS Distro for OpenTelemetry Collector in Amazon ECS — AWS](https://aws-otel.github.io/docs/setup/ecs/)
- [Collect Amazon ECS/Fargate OpenTelemetry data — Grafana Alloy docs](https://grafana.com/docs/alloy/latest/collect/ecs-opentelemetry-data/)
- [Monitoring ECS Fargate using OpenTelemetry Collection Agents — SigNoz](https://signoz.io/docs/opentelemetry-collection-agents/ecs/sidecar/user-guides/get-started/)
