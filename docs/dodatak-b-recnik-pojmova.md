# Dodatak B — Rečnik pojmova

Kratke, praktične definicije termina korišćenih kroz knjigu — onako kako
se zapravo koriste u radu, ne enciklopedijski. Poređano abecedno.

**Absence-class alarm (alarm iz klase odsustva)** — problem koji se ne
manifestuje kao pogrešan signal, nego kao **odsustvo** signala koji bi
trebalo da postoji (npr. drift pokrivenosti alarmiranja). Zahteva
automatizovanu proveru DEKLARISANE konfiguracije, jer opservabilnost
zasnovana na živim signalima ne može da primeti nešto što nikad nije
ni počelo da se emituje.

**Active series / billable series (aktivne / naplative serije)** —
aktivne serije su vremenske serije koje TRENUTNO primaju podatke;
naplative serije su ono za šta pružalac usluge stvarno naplaćuje, i
mehanizam koji povezuje ta dva broja retko je potpuno objavljen. Ne meri
kardinalnost na osnovu razlike ova dva broja bez direktnog merenja.

**Adaptive Traces / adaptivno uzorkovanje na strani platforme** — oblik
uzorkovanja raspona (traces) gde platforma za posmatranje, ne kolektor,
odlučuje šta zadržava, na osnovu politika koje se mogu menjati bez
redeploy-a pošiljaoca. Ključna razlika od uzorkovanja na strani kolektora:
politike se primenjuju REDOSLEDOM, prva koja se poklopi pobeđuje.

**Attribute / Label (atribut / labela)** — par ključ-vrednost zakačen za
metriku, log ili raspon, koji kaže ČIJI je podatak i u kom kontekstu (npr.
`service.name`, `http.response.status_code`). Resource attribute (vidi
dole) je poseban slučaj koji opisuje IZVOR telemetrije, ne pojedinačno
merenje.

**Blast radius (radijus dejstva)** — koliko korisnika/servisa/podataka bi
bilo pogođeno ako nešto pođe po zlu. Koristi se i za redosled faznog
rollout-a (najmanji radijus prvi) i za prioritizaciju rizika (radijus ×
verovatnoća × trošak popravke).

**Burn-rate (stopa sagorevanja budžeta)** — koliko brzo se troši budžet
greške SLO-a, izraženo kao višekratnik normalne stope. Multi-window
multi-burn-rate dizajn (npr. 14.4×/6×/3× pragova) balansira brzo
otkrivanje ozbiljnih kvarova sa otpornošću na kratkotrajne fleksije.

**Cardinality (kardinalnost)** — broj JEDINSTVENIH kombinacija oznaka
(labela) koje jedna metrika proizvodi. Svaka nova jedinstvena kombinacija
je nova vremenska serija — trošak se plaća po kombinaciji, ne po broju
merenja.

**Collector (kolektor)** — proces koji prima telemetriju (obično preko
OTLP), po potrebi je transformiše, i prosleđuje dalje. Može biti bočni
(sidecar, po zadatku) ili centralni (gateway, deljen).

**Dashboard** — grafička tabla sastavljena od panela, gde svaki panel
prikazuje jedan upit nad metrikama, logovima ili trejsovima.

**Dead man's switch (alarm koji ćuti kad treba da radi)** — alarm koji
je dizajniran da se OGLASI kad OTKAŽE mehanizam koji bi inače trebalo da
prijavi problem — logika je obrnuta od uobičajenog alarma: tišina je
loš znak, ne dobar.

**Dedup (deduplikacija)** — grupisanje ponovljenih obaveštenja o istom
kvaru u jedan zapis unutar vremenskog prozora, da bi se izbeglo
zasipanje kanala istom porukom.

**DPM (data points per minute)** — koliko tačaka podataka po minutu
jedna serija proizvodi; jedan od faktora koji određuje naplativu
kardinalnost pored broja jedinstvenih serija.

**Error budget (budžet greške)** — dozvoljena količina "lošeg" ponašanja
pre nego što SLO bude prekršen, izvedena iz cilja pouzdanosti (npr. cilj
99.9% ostavlja 0.1% budžeta). Trošenje budžeta je dozvoljena valuta za
odlučivanje o tempu isporuke promena.

**Exemplar** — pojedinačan uzorak (obično jedan raspon/trace ID) povezan
sa tačkom na histogramu metrike, koji omogućava skok sa agregiranog
grafika direktno na konkretan primer. Retencija exemplar-a je obično
kratka (na primer, nekoliko sati) — koristan je za "šta se sad dešava",
ne za jučerašnji incident.

**Exporter (eksporter)** — deo SDK-a ili kolektora čiji je jedini posao da
uzme već generisanu telemetriju i pošalje je dalje, u OTLP formatu, ka
sledećoj tački u lancu (kolektoru, gateway-u ili direktno cloud platformi).

**Gateway (centralni prolaz)** — deljena komponenta kroz koju prolazi
telemetrija više pošiljalaca pre nego što ode dalje ka skladištu; radi
uzorkovanje, autentikaciju i grupisanje na jednom mestu umesto da svaki
pošiljalac to radi sam.

**Golden signals (zlatni signali)** — kašnjenje, saobraćaj, greške,
zasićenje (latency, traffic, errors, saturation) — osnovni skup od
četiri dimenzije za ocenu zdravlja servisa (Google SRE Book).

**Instrumentation (instrumentacija)** — kod, ili agent koji se kači na
kod, koji generiše metrike, logove i tragove iz rada aplikacije; može biti
AUTOMATSKA (bez izmene koda aplikacije) ili RUČNA (eksplicitna linija
koda koja emituje raspon ili atribut).

**Keyed-HMAC pseudonimizacija** — pretvaranje identifikatora u
pseudonim korišćenjem kriptografske heš funkcije sa TAJNIM ključem, za
razliku od gole heš funkcije bez ključa — ključ sprečava napad grubom
silom (rečnički napad) protiv poznatog skupa mogućih vrednosti (npr.
email adresa).

**Log** — tekstualni zapis JEDNOG konkretnog događaja, u tačno određenom
trenutku; bogatiji je od metrike, ali teži za pretragu ako nije
strukturiran i povezan sa ostatkom sistema.

**MCP (Model Context Protocol)** — otvoren protokol koji AI agentu
omogućava strukturisan pristup alatima i podacima (u ovoj knjizi:
platformi za posmatranje) izvan onoga što je model naučio tokom
treniranja.

**Metric (metrika)** — jedan broj koji se meri tokom vremena (npr. broj
zahteva u sekundi). Jeftin je za čuvanje i brz za grafikon, ali sam po
sebi ne kaže KOJI zahtev ili KOJI korisnik stoji iza tog broja.

**Native histogram** — format histograma gde se raspodela po kantama
(bucket) šalje kompaktnije nego kod klasičnog histograma sa unapred
fiksnim granicama kanti; utiče na naplativu kardinalnost drugačije od
običnih serija (kante se često naplaćuju sa umanjenim koeficijentom).

**Observability (posmatranje sistema)** — sposobnost da se postavi
pitanje koje NIJE bilo predviđeno unapred, o incidentu koji se tek
dogodio, i dobije odgovor iz već prikupljenih podataka — za razliku od
monitoringa, koji odgovara samo na pitanja postavljena unapred.

**OTLP (OpenTelemetry Protocol)** — standardni protokol/format za slanje
metrika, logova i raspona (traces) između pošiljaoca, kolektora i
platforme za posmatranje.

**POA&M (Plan of Action and Milestones)** — formalna kategorija iz NIST
okvira upravljanja rizikom za stavku koja JOŠ NIJE rešena, ali se aktivno
prati ka rešenju — razlikuje se od formalno PRIHVAĆENOG rizika, koji
zatvara pitanje odlukom, ne odlaganjem.

**Postmortem** — dokumentovana analiza posle incidenta: šta se desilo,
zašto, kako je otkriveno, i šta se menja da se ne ponovi. Formalni kanal
kroz koji novo saznanje ulazi u budući plan rada.

**RED metod** — Rate, Errors, Duration (stopa zahteva, greške, trajanje)
— standardni okvir za servise koji stalno primaju saobraćaj. Ne
primenjuje se direktno na zakazane (batch) zadatke — vidi "model
potpunosti".

**Resource attribute** — par ključ-vrednost koji opisuje IZVOR
telemetrije (npr. `service.name`, `service.instance.id`,
`aws.ecs.task.arn`), za razliku od atributa koji opisuje pojedinačan
raspon ili merenje.

**Risk acceptance (formalno prihvatanje rizika)** — dokumentovana
odluka da se rizik SVESNO ne rešava, sa obrazloženjem i datumom — različito
od "još nije urađeno", koje ostaje otvoreno pitanje. Razlika sprečava
da se isto pitanje iznova postavlja svakom novom čitaocu.

**Runbook** — unapred pripremljeno uputstvo (obično stablo odluka) za
konkretnu KLASU kvara, ne za jedan događaj — koristi se dok alarm još
uvek zvoni, za razliku od postmortem-a koji dolazi posle.

**SDK (software development kit)** — biblioteka koju aplikacija uključuje
da bi uopšte mogla da proizvede telemetriju u OpenTelemetry formatu.

**Semantic conventions (semantičke konvencije)** — standardizovana imena
atributa i metrika koje OTel propisuje (npr. `http.status_code`), da bi
telemetrija iz različitih sistema bila uporediva bez ručnog mapiranja.

**Sidecar (bočni kolektor)** — kolektor koji radi UNUTAR istog zadatka/
poda kao aplikacija koju posmatra, hvatajući signale (npr. poslednje
raspone pri gašenju) koje centralni kolektor van zadatka ne bi video.

**SLI / SLO** — Service Level Indicator (merljiv signal, npr. procenat
uspešnih zahteva) i Service Level Objective (ciljna vrednost tog
signala kroz vreme, npr. 99.9%).

**Span (raspon)** — jedan korak unutar traga (trace): jedna operacija ili
poziv jednog servisa, sa trajanjem, ishodom i sopstvenim atributima.

**Span metrics** — metrike IZVEDENE iz raspona (traces) pre bilo kakvog
uzorkovanja — omogućavaju da RED dashboard ostane pun-vernosti (full-
fidelity) čak i kad se sami rasponi agresivno uzorkuju za skladištenje.

**Tail sampling** — odluka o zadržavanju raspona donosi se NAKON što se
ceo raspon završi (npr. "zadrži sve greške, uzorkuj uspešne"), za
razliku od head sampling-a, gde se odluka donosi na samom početku, pre
nego što je ishod poznat.

**Target_info** — standardna OTel/Prometheus metrika koja nosi resource
atribute (identitet izvora) kao oznake, odvojeno od same izmerene
vrednosti — česta tačka za proveru identiteta zadatka/instance.

**Tier (nivo hitnosti)** — klasifikacija alarma po ozbiljnosti (npr.
kritičan/standardan/tih) koja određuje da li se dedup-uje, da li uopšte
šalje obaveštenje, i kojim putem.

**Trace (trag)** — zapis putanje JEDNOG zahteva kroz sve servise kroz
koje je prošao, sastavljen od pojedinačnih raspona (spans).

**USE metod** — Utilization, Saturation, Errors (iskorišćenost,
zasićenost, greške) — okvir za posmatranje RESURSA (host, disk, mreža),
za razliku od RED metoda koji posmatra SERVISE.

**Watcher-outlives-the-watched (posmatrač koji nadživi posmatrano)** —
princip po kom alarm koji prati zdravlje SAME platforme za posmatranje
mora imati put do čoveka koji NE zavisi od te iste platforme — inače,
upravo u trenutku kad je najpotrebniji, i on je nem.
