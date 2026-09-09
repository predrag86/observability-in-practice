# Poglavlje 22 — Mreža kao posebna ravan posmatranja

Ispod svakog grada leži nekoliko potpuno odvojenih mreža koje niko od
stanara ne vidi dok rade — vodovod, struja, gas, telefonske linije, svaka
sa sopstvenim cevima ili kablovima, sopstvenim tačkama kvara, sopstvenom
ekipom koja je održava. Kad nestane struje, to ne znači da je i vodovod
stao — ali može značiti da pumpe koje vodu guraju uzbrdo stanu, pa se
kvar struje pretvori u kvar vode, iako je cev sama po sebi netaknuta. A
najopasniji trenutak je onaj kad telefonske linije, koje bi trebalo da
prenesu poziv "nemamo struju već sat vremena," prolaze kroz isti razvodni
orman koji je upravo izgoreo — pa u trenutku kad je poziv za pomoć
najpotrebniji, telefon ćuti iz istog razloga iz kog je nestalo struje.
Grad koji razume ovih pet mreža kao pet odvojenih sistema zna nešto
suštinsko: kada jedna od njih padne, prva stvar koju treba proveriti nije
"da li rade ostale," nego "da li ijedna od ostalih uopšte može da javi
da nešto ne radi."

## 22.1 Pitanje na koje ovo poglavlje odgovara

Mreža nije jedan sistem koji ili radi ili ne radi — to je skup nezavisnih
slojeva, svaki sa sopstvenim tačkama kvara i sopstvenom telemetrijom. Kako
se ti slojevi drže odvojenim u posmatranju, i šta znači kada baš mreža —
put kojim telemetrija putuje — postane onaj deo sistema koji je pokvaren?

## 22.2 Kako je to urađeno — praktičan pregled

### Devet nezavisnih ravni

Implementacija deli mrežnu infrastrukturu na devet nezavisnih ravni
posmatranja, svaku sa sopstvenim izvorom metrika i sopstvenim rizikom da
padne bez uticaja na ostalih osam: rub sistema i zaštita od zloupotrebe,
uređaji za balansiranje saobraćaja, izlazni prolaz ka internetu, privatne
veze ka spoljnim servisima u istom oblaku, mrežni interfejs svake
pojedinačne instance, i posebno, često zaboravljeno troje: razrešavanje
imena, servis za metapodatke instance, i sinhronizacija sata. Svaka od
ovih ravni ima sopstvenu telemetriju, sopstveni prag alarma, i — što je
najvažnije — sopstvenu, potpuno nezavisnu putanju kvara od ostalih osam.

### Grupisanje po tome koliko ravan "vidi" kad nešto pođe naopako

Implementacija dalje grupiše ovih devet ravni po tome koliko dobro svaka
ravan sama izveštava o sopstvenom kvaru: neke ravni imaju metriku uživo
koja odmah pokazuje problem, neke imaju samo log koji treba naknadno
pretražiti, neke su potpuno slepe — bez direktne telemetrije, vidljive
samo posredno kroz simptome na drugim ravnima — i jedna grupa je posebno
opasna: ravni koje su i slepe **i** čine deo puta kojim ostala telemetrija
putuje. Implementacija tu poslednju grupu eksplicitno označava kao
najgoru kategoriju — jer kvar na toj ravni ne samo da ostaje neviđen sam
po sebi, nego može ugasiti i vidljivost svega što kroz nju prolazi.

### Diferencijalno čitanje: dva nezavisna puta ka istom kvaru

Centralna disciplina implementacije je čitanje povezanih signala **u
paru**, ne pojedinačno. Konkretan primer: izlazni prolaz ka internetu ima
dve povezane, ali nezavisno generisane metrike — koliko bajtova/paketa
uđe u prolaz sa jedne strane, i koliko izađe sa druge. U normalnom radu
ove dve vrednosti prate jedna drugu. Kad se razdvoje — ulaz raste, izlaz
ne — to samo po sebi je dijagnostičko: pokazuje da se negde između uzima
ili gubi saobraćaj, čak i bez ijednog eksplicitnog alarma za "gubitak."
Implementacija dalje razlikuje dva različita oblika tišine koje ovakav par
metrika može pokazati: jedna ravan koja **stvarno emituje nule** (aktivna,
ali bez saobraćaja) naspram ravni koja **ne emituje ništa** (potpuno tiha,
možda zato što je sam mehanizam prikupljanja pao) — razlika koja izgleda
sitno na papiru, ali potpuno menja dijagnozu: prvo je "nema saobraćaja,"
drugo je "ne znamo da li ima saobraćaja."

### Zašto se mreža mora čitati kao par, ne kao pojedinačan signal

Razlog za ovu disciplinu je strukturan: mreža koja je pokvarena je tačno
onaj deo sistema koji nosi i sopstvenu telemetriju i telemetriju svih
ostalih komponenti koje kroz nju komuniciraju sa spoljnim svetom. Kad
padne, ne pada samo saobraćaj korisnika — može pasti i signal koji bi
trebalo da javi da je saobraćaj korisnika pao. Zato jedan usamljen alarm
koji je prestao da stiže ne znači nužno "sve je u redu" — može značiti
"put kojim je taj alarm trebalo da stigne je upravo pokvaren." Čitanje dva
nezavisna puta ka istom domenu kvara zajedno — jedan i dalje javlja, drugi
ćuti — je jedini način da se razdvoji "stvarno nema problema" od
"problem postoji, ali njegov glasnik je nem."

### Primena principa na sam alarm: ruta koja preživljava pad sopstvenog kolektora

Isti princip diferencijalnog čitanja implementacija je primenila i na
samu isporuku alarma, ne samo na merenje. Većina pravila za mrežne alarme
evaluira nad istim deljenim kolektorom i istim cevovodom koji nosi
ostatak telemetrije flote — što znači da, ako baš taj cevovod padne,
pravilo ne javlja grešku, nego jednostavno **prestaje da evaluira** i
utihne. Tišina pravila je, spolja gledano, neraspoznatljiva od "sve je u
redu" — tačno onaj problem koji je ovo poglavlje već opisalo za obične
metrike, sada primenjen na sam mehanizam koji bi trebalo da upozori na
kvar. Rešenje je bilo namerno razdvojiti mali broj najkritičnijih pravila
u posebnu grupu koja čita direktno iz nezavisnog izvora podataka, mimo
deljenog kolektora — tako da, kad kolektor ili njegov cevovod padnu, ta
druga grupa pravila i dalje evaluira, i dalje može da javi. Obe grupe
šalju na isti kanal za obaveštavanje, tako da razlika postoji samo u
putanji do te tačke, ne u tome gde se na kraju pojavljuje.

![Glavna ruta za mrežne alarme evaluira nad istim kolektorom koji nosi ostatak telemetrije, pa kad taj kolektor padne — ruta utihne, neraspoznatljivo od "sve je u redu". Nezavisna ruta čita direktno iz odvojenog izvora, mimo deljenog kolektora, i nastavlja da radi baš u tom trenutku.](diagrams/ch22-nezavisna-ruta.png){: width="85%" }

### Dve vrste provere za dve vrste grešaka

Pre nego što je novoizgrađeni dashboard pušten u upotrebu, implementacija
je propustila svaki upit na svakom panelu uživo, uporedila sa očekivanim
vrednostima, i tražila prazne ili neuspele rezultate — provera koja je
uhvatila nekoliko stvarnih grešaka u samim upitima. Ali ta ista provera
je **prošla** kroz dve odvojene, stvarne greške koje ništa u upitu nisu
imale — panel je vraćao tačne podatke, samo ih je pogrešno **prikazivao**:
naslov odsečen zbog premalog razmaka za tekst, i jedan panel koji je,
zbog kombinovanja agregacije sa podrazumevanom nula-vrednošću na pogrešnom
mestu, prikazao dve vrednosti jednu pored druge tamo gde je trebalo da
postoji samo jedna. Provera zasnovana na upitu ne može da vidi nijednu od
ove dve greške, jer obe vraćaju validne, neprazne podatke — greška
postoji samo u tome kako je prikazan rezultat, ne u samom rezultatu.
Ova dva sloja provere hvataju strogo različite klase grešaka i nijedan ne
zamenjuje drugi: **provera upita dokazuje da panel nije mrtav, ne da je
ispravan** — za to drugo je potreban pogled na sam iscrtani panel, ne
samo na podatke koji ga pune.

Ovde je vredno primetiti i suptilniju zamku iz same provere upita: jedan
panel je imao podatke u trenutku izgradnje, a bio prazan svega četrdesetak
minuta kasnije — ne zbog kvara, nego zato što je stvarna vrednost pala na
nulu i izvor je prestao da je uopšte emituje. Pouka nije "zapamti koje
metrike znaju da nestanu" — to je pokretna meta, tačno koje metrike su
prazne u datom trenutku zavisi samo od toga šta trenutno meri nulu. Pouka
je da se svaki brojač greške ili odbijanja mora tretirati kao da može
nestati, i eksplicitno mu se doda podrazumevana nula-vrednost, umesto da
se ta zaštita doda tek pošto nešto konkretno stvarno nestane.

![Devet ravni mrežne infrastrukture grupisane po tome koliko vidljivo javljaju o sopstvenom kvaru — najgora grupa je slepa i istovremeno predstavlja put kojim prolazi telemetrija svih ostalih ravni.](diagrams/ch22-devet-ravni.png){: width="90%" }

![Ulazni i izlazni tok bajtova kroz izlazni prolaz, čitani u paru: razilaženje između dve linije, ne bilo koja linija pojedinačno, je ono što otkriva gubitak saobraćaja.](diagrams/dashboard-natdiff.png){: width="95%" }

### Isti tip panela, drugačiji način upita, drugačije ime kolone — bez ijedne greške u upitu

Treći primer iste klase greške, sa sasvim drugim uzrokom od prethodna
dva, otkriven je na dashboard-u koji nema nikakve veze sa mrežom, ali
prolazi kroz identičnu proveru: pet tabelarnih panela je posle izgradnje
prikazivalo sirov naziv kolone `Value #A` umesto čitljivog imena poput
"broj neuspelih pokušaja" ili "broj različitih korisnika". Provera upita
uživo bi ovo propustila iz istog razloga kao i prethodna dva slučaja —
upit je vraćao tačne, neprazne podatke, i sam broj u koloni je bio
ispravan. Greška je bila isključivo u tome kako se ta kolona zvala.

Uzrok: transformacija koja preimenuje kolonu ciljala je polje po imenu
`Value` — ime koje ta ista transformacija dobija kad panel koristi
**range** upit. Svih pet panela je, međutim, koristilo **instant** upit u
tabelarnom formatu, a instant upit vraća vrednost pod imenom
sufiksovanim identifikatorom same reference upita — `Value #A`, ne
`Value`. Preimenovanje polja koje ne postoji pod tim imenom nije greška
koja se prijavljuje; ono jednostavno ne pogodi ništa i tiho ne uradi
ništa, ostavljajući sirovo ime da prođe do prikaza nepromenjeno.

Ovo je ista opšta pouka kao odsečen naslov i duplirana vrednost iz
prethodnog primera — provera upita dokazuje da panel nije mrtav, ne da je
ispravno prikazan — ali sa uzrokom koji njihova provera ne bi ni
teoretski mogla da uhvati na drugi način: dva različita režima upita nad
istim izvorom podataka i istim tipom panela ne dele automatski isto ime
izlaznog polja, a transformacija koja pretpostavlja fiksno ime se ne
buni kad ta pretpostavka ne važi, samo prestane da radi. Popravka nije
bila u upitu nego u transformaciji: preimenovanje je pomereno da cilja
stvarno ime polja koje instant upit zaista vraća.

### Alat koji obećava da pokrije više ravni odjednom — i zašto to ovde ne važi

Postoji tehnologija koja obećava tačno ono što ravan mrežnog interfejsa po
instanci traži: podatke o protoku direktno iz kernela, bez ijedne izmene
aplikacije i bez agenta koji treba posebno instalirati na svaki servis.
Zvuči kao prečica koja bi mogla da zameni deo posla opisanog iznad.
Implementacija ju je razmotrila — i odbila, za veliku većinu flote, iz
jednog strukturnog razloga: ovakav alat čita direktno iz Linux kernela
hosta, a najveći deo flote ne izvršava se na hostu kojim implementacija
upravlja, nego na upravljanom, bez-serverskom izračunavanju bez pristupa
kernelu uopšte. Nezavisan istraživački izvor posvećen posmatranju sistema
je ovo potvrdio eksplicitno, van sopstvenog konteksta implementacije: alati
ove porodice "neće raditi sa serverless tehnologijama," i većina rešenja u
toj kategoriji pretpostavlja Kubernetes klaster koji implementacija uopšte
ne vodi.

Ali odluka nije bila jednostavno "da" ili "ne" za ceo alat — jedan
konkretan proizvod iz iste porodice je promovisan iz "odbijeno" u
"odloženo", ne "prihvaćeno", kad se ispostavilo da je tehnički drugačiji
od ostalih: radi kao prvoklasna komponenta unutar kolektora koji flota već
koristi, pa ne zahteva nov agent na hostovima koji kernel pristup stvarno
imaju. Za tu malu manjinu hostova, ovaj alat bi doneo podatke o protoku po
paru izvor-odredište bez oslanjanja na flow-logove. Zašto onda i tu ostaje
odložen, ne uveden: cena bi bila u kardinalnosti — podaci po paru
izvor/odredište eksplodiraju broj serija na način koji Poglavlje 11 već
upozorava da se meri pre uvođenja, ne posle — a pitanje koje bi ovaj alat
prvi rešio (odbacivanje paketa zbog ograničenja broja DNS zahteva po
mrežnom interfejsu) već ima jeftiniji, postojeći odgovor: jedan alat za
očitavanje same mrežne kartice, koji već radi na tim istim hostovima, po
ceni bliskoj nuli.

Pouka nije "ovakvi alati ne valjaju" — pouka je da alat čija najveća
prednost (rad bez agenta, na nivou kernela) tačno onemogućava upotrebu na
većini flote koja radi bez sopstvenog kernela, i da čak i tamo gde uslov
za upotrebu postoji, redosled pitanja mora biti "koji problem ovo rešava,
i da li već imamo jeftiniji odgovor na baš taj problem" — ne "da li je
ovo tehnički moguće ovde."

### Tri naizgled nepovezana kvara, jedan deljeni prag na istom mrežnom interfejsu

Tri manje očigledne ravni iz prethodnog odeljka — razrešavanje imena,
metapodaci instance, sinhronizacija sata — dele nešto što nijedna od njih,
posmatrana pojedinačno, otkriva: sav saobraćaj ka tim uslugama prolazi
kroz isti uskogrudi, deljeni prag paketa u sekundi na mrežnom interfejsu
same instance. Prag nije po usluzi, nego zajednički za sve tri — što znači
da jedan pričljiv potrošač može da izgladni preostale dve, čak i dok,
posmatran sam za sebe, ostaje ispod sopstvene zamišljene granice. Rezultat
u praksi izgleda kao tri potpuno nepovezana kvara: povremeno razrešavanje
imena ne uspeva, obnavljanje pristupnih akreditiva otkazuje sa greškom
autentifikacije, i sat počne da odstupa dovoljno da pokvari validaciju
sertifikata i usklađivanje logova — sve na istoj mašini, u isto vreme, iz
istog uzroka koji nijedan od tri simptoma pojedinačno ne otkriva.

Očigledan alat za dijagnozu ovde ne pomaže. Uključivanje detaljnog
zapisivanja DNS upita zvuči kao prirodan prvi korak — ali ograničavanje se
dešava **na samom mrežnom interfejsu, pre nego što je upit uopšte
zapisan**, pa ograničen upit nikad ne stigne do loga koji bi ga zabeležio.
Detaljnije zapisivanje ne bi pronašlo ništa, koliko god dugo se ostavilo
uključeno.

Postoji tačno jedan brojač koji ovu klasu kvara uopšte otkriva, i on je
gotovo besplatan — ali je ožičen samo na manjini instanci, onima pod
direktnim nadzorom na nivou hosta. Radno opterećenje najsklonije da samo
izazove ovaj kvar — ono koje razrešava ime ili osvežava akreditive po
svakom pojedinačnom zahtevu, bez keširanja — tipično radi na upravljanom
izračunavanju bez pristupa tom nivou nadzora, što znači da je baš tamo
gde je kvar najverovatniji i najmanje vidljiv. Tišina tog jedinog brojača
na ostatku flote ne dokazuje da problema nema — dokazuje samo da ga niko
tamo ne meri.

## 22.3 Analitički deo — princip poznat u dva odvojena zvanična oblika

### Zvanična dokumentacija već koristi diferencijalni obrazac, i to eksplicitno

Zvanična dokumentacija provajdera za metrike izlaznog prolaza već
preporučuje čitanje ulaznog i izlaznog toka bajtova/paketa u paru, i
eksplicitno navodi da razlika između njih ukazuje na mogući gubitak
podataka ili blokiran saobraćaj — ovo je direktna, zvanična potvrda
diferencijalne discipline implementacije, ne pretpostavka koju je
implementacija sama izmislila. Isti obrazac postoji i na sloju za
balansiranje saobraćaja: zvanična dokumentacija razlikuje greške koje
generiše sam uređaj za balansiranje od grešaka koje generiše pozadinski
servis, kao dva odvojena brojača tačno iz istog razloga — ista tačka
kvara posmatrana sa dve nezavisne pozicije, gde razilaženje između njih
lokalizuje uzrok.

### "Ravni" kao formalan koncept postoje, ali ne pod ovim imenom, za ovu kombinaciju

Zvanična dokumentacija o granicama izolacije kvarova formalizuje podelu
između kontrolne ravni (API-jevi, orkestracija) i podatkovne ravni (stvaran
prenos saobraćaja) kao namernu, arhitekturnu odluku — kvar na kontrolnoj
ravni ne sme oboriti saobraćaj koji je već u letu na podatkovnoj ravni.
Ovo potvrđuje opšti princip da se mreža svesno deli na nezavisne slojeve
radi otpornosti, ali konkretna kombinacija od devet ravni koju
implementacija koristi — rub, balansiranje, izlazni prolaz, privatne veze,
mrežni interfejs po instanci, plus DNS/metapodaci/sat — nije formulisana
kao gotov, imenovan spisak u jednom zvaničnom dokumentu; to je sinteza
implementacije, izgrađena na opštijem principu, primenjena na sopstvenu
arhitekturu.

### DNS, metapodaci instance i sat kao dokumentovano zapostavljena telemetrija

Sva tri manje očigledna sloja imaju dokumentovanu potvrdu da su lako
zapostavljeni: zvanična dokumentacija za razrešavanje imena unutar
privatne mreže eksplicitno navodi da su detaljni podaci po upitu opciona,
plaćena funkcija, dok je osnovno zdravstveno stanje besplatno ali grubo
uzorkovano — što znači da granularna vidljivost DNS-a zahteva svestan,
dodatan korak. Servis za metapodatke instance nema prvoklasnu ugrađenu
metriku dostupnosti ili latencije u standardnoj platformi za metrike —
odsustvo je samo po sebi dokumentovan nalaz, ne pretpostavka. A tačnost
sistemskog sata zahteva prilagođenu skriptu i prilagođenu metriku da bi
uopšte postala vidljiva — nema podrazumevanog alarma za odstupanje sata,
uprkos tome što odstupanje sata direktno kvari validaciju sertifikata,
usklađivanje logova, i tačnost distribuiranog praćenja.

### Kontrafaktički scenario: alarm koji ćuti u pogrešnom trenutku

Zamislimo tim koji prati izlazni prolaz kroz samo jedan brojač — recimo,
samo dolazni saobraćaj — bez uparivanja sa izlaznim. U trenutku kad prolaz
počne da gubi deo saobraćaja, taj jedan brojač i dalje pokazuje "saobraćaj
stiže," jer meri samo ulaz, ne razliku. Alarm koji bi trebalo da uhvati
gubitak nikad ne bi okinuo — ne zato što je prag pogrešno postavljen, nego
zato što posmatrana metrika strukturno ne može da vidi razliku između
"sve prolazi" i "polovina se gubi." Tek kad korisnici počnu da se žale na
sporost bi neko ručno otkrio da je gubitak postojao satima, nevidljiv
jedinom brojaču koji je iko gledao.

Vratimo se na grad i njegovih pet mreža s početka poglavlja. Grad koji
razume da su vodovod, struja, gas i telefon odvojeni sistemi ne panici pri
svakom kvaru — zna tačno koju ekipu pozvati, i zna da proveri da li poziv
za pomoć uopšte može stići kroz mrežu koja je možda upravo ta koja je
pokvarena. Mrežni sloj infrastrukture, posmatran kroz devet nezavisnih
ravni umesto kao jedan nejasan "mrežni problem," daje isti taj uvid: zna
se ne samo šta je pokvareno, nego i da li glasnik koji bi to trebalo da
javi uopšte može da progovori.

## 22.4 Skupljena pravila iz ovog poglavlja

- Posmatraj mrežu kao skup nezavisnih ravni, ne kao jedan sistem — svaka
  ravan ima sopstvenu putanju kvara, i kvar jedne ne znači ni pad ni
  zdravlje ostalih.
- Prepoznaj koje ravni su i slepe (bez direktne telemetrije) i istovremeno
  deo puta kojim telemetrija ostalih ravni putuje — ta kombinacija je
  najopasnija, jer njihov kvar može ugasiti vidljivost svega ostalog.
- Čitaj povezane mrežne signale u paru, ne pojedinačno — razilaženje
  između dva nezavisna puta ka istom domenu kvara je samo po sebi
  dijagnostičko, čak i bez eksplicitnog alarma za tačno taj scenario.
- Razlikuj "ravan koja emituje nule" od "ravni koja ne emituje ništa" —
  prva znači "nema saobraćaja," druga znači "ne znamo," i mešanje ove
  dve dijagnoze vodi u pogrešan zaključak.
- Ne zaboravi DNS, servis metapodataka instance, i sinhronizaciju sata —
  sva tri su dokumentovano zapostavljena, bez podrazumevane detaljne
  telemetrije, uprkos direktnom uticaju na TLS, logove i praćenje.
- Ako DNS, metapodaci instance i sat dele isti mrežni interfejs, pretpostavi
  da dele i isti prag propusnosti — jedan pričljiv potrošač može izgladniti
  preostala dva bez da ijedan pojedinačno pređe sopstvenu zamišljenu
  granicu, i uobičajen alat poput detaljnog DNS-logovanja to neće otkriti
  ako se ograničavanje dešava pre nego što je upit uopšte zapisan.
- Razdvoji šačicu najkritičnijih mrežnih alarma u posebnu grupu koja čita
  direktno iz izvora nezavisnog od deljenog kolektora — ako sva pravila
  evaluiraju nad istim cevovodom koji nose, pad tog cevovoda utihne baš
  ona pravila koja bi trebalo da ga prijave, i ta tišina izgleda identično
  zdravlju.
- Ne veruj da je panel ispravan samo zato što je njegov upit prošao
  proveru uživo — provera upita dokazuje da panel nije mrtav, ne da je
  ispravno prikazan; za greške u prikazu (odsečen tekst, dupla vrednost
  na mestu gde treba jedna) potreban je pogled na sam iscrtani panel.
- Ne pretpostavljaj da isti tip panela nad istim izvorom podataka vraća
  isto ime izlaznog polja bez obzira na režim upita — instant i range
  upit istog izvora mogu imenovati vrednost drugačije, a transformacija
  koja cilja pogrešno ime ne prijavljuje grešku, samo tiho ne uradi
  ništa; proveri stvarno ime polja koje upit vraća, ne ono koje
  pretpostavljaš iz dokumentacije ili iz drugog panela.
- Kad razmatraš alat koji obećava da pokrije više ravni odjednom (npr.
  onaj koji čita direktno iz kernela hosta), prvo proveri da li tvoja
  flota uopšte ima kernel kome bi taj alat mogao da priđe — najveća
  prednost ovakvog alata je često tačno ono što ga isključuje iz najvećeg
  dela flote koja radi bez sopstvenog servera.

## 22.5 Vežba za čitaoca

Nabroj mrežne slojeve kroz koje prolazi jedan tipičan zahtev u tvom
sistemu, od korisnika do baze podataka i nazad. Za svaki sloj, postavi
pitanje: da li ovaj sloj ima sopstvenu, nezavisnu telemetriju, ili se
njegovo zdravlje zaključuje samo posredno, kroz simptome na drugim
slojevima? Pronađi barem jedan sloj koji je trenutno potpuno slep.

---

### Izvori korišćeni u analitičkom delu

- [Create CloudWatch alarms to monitor a NAT gateway — AWS VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/creating-alarms-nat-gateway.html)
- [NAT gateway metrics and dimensions — AWS VPC User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/metrics-dimensions-nat-gateway.html)
- [CloudWatch metrics for your Application Load Balancer — AWS ELB User Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-cloudwatch-metrics.html)
- [AWS Fault Isolation Boundaries whitepaper — Control planes and data planes](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/control-planes-and-data-planes.html)
- [Monitoring Route 53 Resolver endpoints with CloudWatch](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/monitoring-resolver-with-cloudwatch.html)
- [Manage Amazon EC2 instance clock accuracy using Amazon Time Sync Service and CloudWatch — AWS Cloud Operations Blog](https://aws.amazon.com/blogs/mt/manage-amazon-ec2-instance-clock-accuracy-using-amazon-time-sync-service-and-amazon-cloudwatch-part-2/)
- [The State of eBPF in Observability — Observability 360](https://observability-360.com/article/viewarticle?id=ebpf-in-observability)
- [Grafana Beyla — eBPF-based auto-instrumentation](https://grafana.com/oss/beyla-ebpf/)
