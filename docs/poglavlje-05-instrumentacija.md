# Poglavlje 5 — Instrumentacija aplikacije: dve strategije

Odelo kupljeno u prodavnici je skrojeno za prosečnu figuru — ramena, struk,
dužina rukava, sve je podešeno da odgovara najvećem broju kupaca dovoljno
dobro. Za devedeset posto prilika, to je sasvim dovoljno: obučeš ga i izgleda
uredno. Ali za jednu konkretnu priliku — svadbu, važan nastup — krojač uzima
baš to odelo i menja samo ono što je specifično za tebe: dužinu rukava, širinu
u ramenima, mesto gde dugme zaista treba da stoji. Krojač ne pravi novo odelo
od nule. Uzima ono što fabrika već dobro radi, i dodaje samo onaj jedan detalj
koji fabrika ne može da zna unapred, jer je specifičan za tebe.

Instrumentacija aplikacije radi po istoj logici. Auto-instrumentacija je
odelo iz prodavnice — pokriva ono što je zajedničko gotovo svakoj aplikaciji
istog tipa (HTTP pozivi, upiti ka bazi, redovi za poruke) i to radi dobro, bez
ijedne linije koda u samoj aplikaciji. Ono što auto-instrumentacija ne može da
zna je specifično za tebe: ko je pozvao ovaj konkretan zahtev, i preko kog
kanala. To se dodaje ručno, na tačno jednom mestu, kao krojačev jedan ubod
igle — ne kao novo odelo od nule.

## 5.1 Pitanje na koje ovo poglavlje odgovara

Kad se auto-instrumentacija iz Poglavlja 2 postavi i proradi, prirodno pitanje
je: da li je posao gotov? Da li aplikacija sada ima "svu" telemetriju koja joj
treba, ili postoji kategorija podataka koju auto-instrumentacija strukturno ne
može da vidi, bez obzira koliko dobro radi za HTTP pozive i upite ka bazi?

Odgovor određuje gde tim troši preostalo vreme: da li se ono ulaže u širenje
auto-instrumentacije na još biblioteka (marginalna korist, jer većina bitnih
biblioteka je već pokrivena), ili u malen broj ciljanih, ručnih dopuna na
mestima gde auto-instrumentacija po definiciji ne može da pomogne.

## 5.2 Kako je to urađeno — praktičan pregled

Auto-instrumentacija iz Poglavlja 2 (Java agent, Python SDK sa
entrypoint shim-om) hvata ono što je **strukturno vidljivo iz poznatih
biblioteka**: dolazni i odlazni HTTP pozivi, upiti ka bazi, pozivi ka redu za
poruke, standardni resursni atributi postavljeni pri startu. Ovo pokriva
ogromnu većinu onoga što se ikad pogleda na dashboard-u ili u trejsu tokom
istrage — i namerno se ne dira ili duplira ručnom instrumentacijom, jer bi to
bio posao bez koristi.

To je, u praksi, tačno RED metod (Rate, Errors, Duration) pomenut u Poglavlju
1 — auto-instrumentacija ga ne implementira kao posebnu biblioteku ili
dodatnu konfiguraciju, nego ga proizvodi kao nusprodukt: svaki uhvaćen HTTP
poziv već nosi trajanje i status kod, pa su stopa zahteva, stopa grešaka i
trajanje po servisu upit nad tim istim podacima, ne dodatni instrumentacioni
rad. Ovo važi za sinhrone, zahtev/odgovor servise kojima se ovo poglavlje
bavi; za zakazana batch opterećenja bez kontinualnog toka zahteva ista
pretpostavka ne važi — vidi Poglavlje 23.

Postoji tačno jedna kategorija podataka koju tim u implementaciji koju knjiga
prati dosledno dodaje ručno, na svakom servisu: **identitet pozivaoca i kanal
kojim je stigao.** Razlog je strukturan, ne stilski — auto-instrumentacija vidi
da je stigao HTTP zahtev, vidi putanju i metodu, ali ne zna, i ne može da zna,
*ko* stoji iza tog zahteva u poslovnom smislu, jer to zavisi od autorizacione
logike specifične za svaku aplikaciju. U sistemu koji knjiga prati, isti
endpoint može biti pozvan na tri različita načina:

- korisnik ulogovan preko UI-ja, nosi kratkotrajni sesijski token,
- eksterni klijent koji koristi dugotrajan API ključ,
- legacy integracija koja identitet i dalje šalje kao query-parametar (poznat,
  dokumentovan dug tehnički dug, ne slučajni previd).

Za svaki od ova tri puta, mala funkcija u zajedničkom middleware sloju
ekstrahuje identitet — bez obzira odakle je stigao — i postavlja ga kao span
atribut (`enduser.id` po semantičkoj konvenciji, plus interni
`auth.channel` atribut koji beleži *kojim* od tri puta je identitet stigao).
Ovo je **jedina** ručna instrumentaciona tačka u celom sistemu koja se svesno
održava kao takva — sve ostalo ostaje na auto-instrumentaciji. Namerno je
smeštena na jedno mesto (middleware), ne razmazana po svakom endpointu
posebno — tako da promena logike ekstrakcije (npr. dodavanje četvrtog kanala)
zahteva izmenu na jednom mestu, ne pretragu kroz ceo repozitorijum.

Bitna posledica: pošto identitet postaje resursni/span atribut na *svakom*
zahtevu, upit "koji korisnik je pogodio ovaj spor endpoint" ili "koliko grešaka
dolazi od ovog specifičnog API ključa" postaje trivijalan filter u Grafana
Cloud-u — bez toga, taj podatak bi postojao samo u aplikacionim logovima, van
domašaja trejsova i metrika izvedenih iz njih (span metrics, obrađeno u
Poglavlju 6).

![Auto-instrumentacija (Java agent, Python SDK+shim) pokriva sve što je strukturno vidljivo iz poznatih biblioteka; jedina ručna tačka je ekstrakcija identiteta pozivaoca u zajedničkom middleware sloju, bez obzira kojim od tri kanala je identitet stigao.](diagrams/ch5-instrumentation.png){: width="92%" }

### Kad dva odvojena mehanizma za pseudonimizaciju ne "znaju" jedno za drugo

Frontend deo sistema (obrađen detaljno u Poglavlju 8) je namerno projektovan
da nikad ne šalje stvaran identitet korisnika u sopstvenu telemetriju — nosi
samo pseudonimni, tehnički ID sesije, bez imena ili email adrese. Backend
middleware opisan iznad radi suprotno: ekstrahuje **stvaran** identitet
pozivaoca (email adresu), jer je to bilo najjednostavnije i najkorisnije za
debug uživo — "koji korisnik je pogodio ovaj spor endpoint" je odmah čitljiv
upit bez dodatnog koraka.

Oba dizajna su, pojedinačno, razumna. Problem je ono što ih spaja bez da iko
to eksplicitno odluči: propagacija konteksta traga. Kad zahtev pokrenut u
browseru stigne do backend-a, standardni mehanizam za povezivanje raspona
(trace context propagation) automatski spaja frontend raspon i backend raspon
u **isti** trag — i to je poenta cele arhitekture posmatranja, ne greška.
Ali to znači da spojeni trag sad nosi i pseudonimni ID sa frontend strane
*i* stvaran email sa backend strane, na istom, povezanom putu — dva
navodno nezavisna polja privatnosti, spojena kroz mehanizam koji nema
pojma da privatnost uopšte postoji kao briga.

Ovo nije bila teorijska zabrinutost: izmereno je direktno na jednoj stvarnoj
sesiji da je pseudonimni ID korisnika sa frontend strane, praćen kroz spojeni
trag, u velikoj većini povezanih backend raspona razotkrio potpuno konkretnu,
stvarnu email adresu tog istog korisnika — frontend dizajn za privatnost je
radio tačno kako je zamišljeno, ali ga je backend deo istog spojenog traga
tiho poništavao.

Identifikovana popravka (u trenutku pisanja još nije sprovedena) ne menja
frontend uopšte — menja samo *kako* backend middleware postavlja identitet:
umesto sirove email adrese, izvodi stabilan, nereverzibilan pseudonim
(ključem potpisan HMAC nad normalizovanom email adresom, tako da isti
korisnik uvek dobija isti pseudonim, ali se iz pseudonima ne može izvesti
email bez tajnog ključa). Ostatak middleware-a — koji od tri kanala je
identitet doneo, koja uloga i obim su mu dodeljeni — ostaje potpuno
nepromenjen. Za retke slučajeve kad je nekom stvarno potreban obrnut upit
(pseudonim → email), predviđen je zaseban, ograničen endpoint sa sopstvenom
autorizacijom i audit logom — razrešavanje identiteta je samo po sebi
osetljiva radnja, ne nusprodukt čitanja dashboard-a.

Opšta pouka nadilazi ovaj jedan slučaj: kad dva servisa nezavisno odluče kako
će štititi identitet u sopstvenoj telemetriji, mehanizam koji ih automatski
povezuje (propagacija konteksta traga, ali i deljeni dashboard, deljeni
identifikator korisnika u logovima) briše granicu između njih bez upozorenja.
Privatnost telemetrije se mora proveravati na nivou **spojenog** puta kroz
sistem, ne po servisu pojedinačno — jedan servis koji "radi sve kako treba"
ne znači ništa ako sused na drugom kraju istog traga otkriva ono što je prvi
sakrio.

![Trenutno stanje: frontend nosi pseudonimni ID, ali backend middleware iz 5.2 na istom, povezanom tragu stavlja stvaran email — spojen trag je de-anonimizovan. Identifikovana popravka (nije sprovedena) menja samo backend stranu: isti korisnik dobija isti stabilan pseudonim, spojen trag ostaje pseudoniman od kraja do kraja.](diagrams/ch05-pseudonimizacija-preko-granice.png){: width="80%" }

### Kad se dijagnoza pokvari ispod tebe: isti simptom, promenjen uzrok

Lako je pretpostaviti da "auto-instrumentacija je uključena" znači da sva tri
signala (trejsovi, metrike, logovi) automatski rade za taj servis, i da će
tako i ostati. Stvaran slučaj u jednoj od batch flota u implementaciji
pokazuje zašto ni jedna od te dve pretpostavke nije pouzdana: promenljiva
okruženja koja uključuje izvoz logova bila je eksplicitno postavljena,
potvrđena u definiciji zadatka, i ništa u konfiguraciji nije ukazivalo na
problem — a ipak, nijedan log red iz te flote u tom trenutku nije stizao u
platformu za posmatranje.

Uzrok, dijagnostikovan u tom trenutku: biblioteka za automatsku
instrumentaciju tog jezika je, u verziji koja je tada bila u upotrebi, imala
poseban modul za standardni modul za logovanje — ali taj modul je radio samo
jednu stvar, ubacivao je identifikator trenutnog raspona u već formatiran
tekst log linije, tako da se log može kasnije ručno povezati sa trejsom po
tom identifikatoru. Nije dodavao prijemnik koji bi log zapise zaista slao ka
platformi za posmatranje kao posebne, strukturisane zapise. Popravka je
zavedena kao poznat, čekajući zadatak — ručno dodavanje desetak linija koda
koje bi tu vezu uspostavile.

Ono što se dogodilo posle je i sama pouka: ta ručna popravka nikad nije ni
morala da se napiše. Nekoliko meseci kasnije, biblioteka je rutinski
nadograđena iz sasvim drugog razloga, nevezanog za ovaj problem — a nova
verzija je, kao sporednu posledicu, počela sama da prikači prijemnik za
strukturisane zapise na podrazumevani sistem za logovanje, čim je ta ista
promenljiva okruženja prisutna. Većina flote je počela da šalje logove u
platformu za posmatranje bez ijedne izmene koda, bez da je iko to tražio kao
cilj nadogradnje.

Kad je tim, u sledećoj reviziji, ponovo prošao kroz staru listu flota koje
"ne šalju logove," otkrio je da je stara dijagnoza — "biblioteka nema tu
funkcionalnost" — u međuvremenu postala pogrešna za skoro sve flote na listi,
ali **ne za sve**. Šačica preostalih flota je i dalje pokazivala identičan
spoljašnji simptom (nema logova u platformi za posmatranje), ali uzrok više
nije bio isti: te flote su izrazito kratkotrajne, i njihov proces se gasi pre
nego što interni bafer stigne da isprazni ono što je nakupio — mehanizam koji
detaljno objašnjava sledeće poglavlje. Isti simptom, potpuno druga
dijagnoza, samo par meseci kasnije.

Opšta pouka: dijagnostikovan uzrok ima rok trajanja. Biblioteke od kojih
zavisi auto-instrumentacija menjaju verzije, ponekad tiho popravljajući staru
klasu greške kao sporedan efekat izmene koja uopšte nije ciljala taj problem
— dok identičan spoljašnji simptom, "nema podataka," u međuvremenu počne da
ga proizvodi potpuno drugačiji mehanizam. Pre nego što se stara dijagnoza
ponovo iskoristi kao objašnjenje, vredi je proveriti nanovo — ne pretpostaviti
da razlog koji je važio pre par meseci i dalje važi danas.

## 5.3 Analitički deo — kada ručna instrumentacija zaista vredi truda

### Šta auto-instrumentacija strukturno ne može da vidi

Nezavisne analize ovog izbora (uključujući Elastic-ov vodič za dobru praksu
instrumentacije) navode dve kategorije gde auto-instrumentacija ostaje slepa,
bez obzira na to koliko je zrela: **čist aplikativni/poslovni kod koji ne
prolazi kroz nijednu poznatu biblioteku** (auto-instrumentacija se kači na
poznate biblioteke — sopstvena poslovna logika prosto nije njena teritorija),
i **kontekst koji zahteva poslovno znanje** — ko je korisnik, koji je tenant,
koja je poslovna kategorija zahteva — jer ništa u samom HTTP pozivu to
strukturno ne nosi bez logike specifične za aplikaciju. Ista analiza
preporučuje da svaka organizacija ima **dosledan dogovor o resursnim
atributima** (`service.name`, `service.version`, `deployment.environment`, i
po potrebi tenant/organizacioni identifikator) primenjen kroz celu flotu —
tačno princip koji je ovaj sistem već usvojio u Poglavlju 2, samo ovde
proširen na *span* nivo za identitet pozivaoca, ne samo *resource* nivo za
identitet servisa.

### Gde smo svesno stali, i zašto nismo išli dalje

Vredi eksplicitno primetiti šta implementacija **nije** uradila, jer je to
podjednako bitna odluka kao i ono što jeste. Tim nije pokušao da ručno
instrumentira "sve što bi moglo biti korisno" — nema ručnih spanova oko svake
poslovne funkcije, nema ručno dodatih atributa "za svaki slučaj" van
middleware sloja opisanog gore. Razlog je direktna posledica prakse otkrivene
u Poglavlju 1 (cacher incident): bogaćenje konteksta "za svaki slučaj" je
vredno, ali samo kad je jeftino da se održava. Ručni span oko svake poslovne
funkcije nije jeftin — svaki od njih je linija koda koja mora da se piše,
review-uje i održava zauvek, i koja zastari čim se logika promeni a
instrumentacija ne prati. Jedna, dobro plasirana tačka enrichmenta (middleware
sloj za identitet) daje najveći deo koristi po jedinici truda; deseta,
dvadeseta ručno dodata tačka daje sve manje koristi za isti trud.

### Šta bi se desilo suprotnim izborom

Da je tim otišao u drugu krajnost — oslonio se isključivo na
auto-instrumentaciju i nikad ne dodao identitet ručno — svaka istraga o tome
"ko je pogodio ovaj endpoint" bi zahtevala da se trejs ili metrika ukrste sa
aplikativnim logom po vremenskom pečatu i ID-ju zahteva, ako taj log uopšte
postoji i ako nosi identitet u parsibilnom obliku. To je tačno vrsta posla
koji se radi *usred* incidenta, pod pritiskom, umesto da postoji kao gotov
filter unapred — cena koja se, kao i u Poglavlju 1, ne vidi dok ne zatreba, a
onda se vidi u punom obimu.

Obrnuto, da je tim otišao u ekstremnu ručnu instrumentaciju svuda —
efektivno duplirajući ono što auto-instrumentacija već radi, plus ručne
spanove oko svake poslovne funkcije — rezultat bi bio veći obim koda posvećen
observability-ju nego samoj poslovnoj logici, veći rizik da instrumentacija
zastari kad se kod promeni (jer ručni span ne prati refaktorisanje automatski,
za razliku od auto-instrumentacije koja se kači na stabilan interfejs
biblioteke), i, paradoksalno, teže dashboard-e — jer bi svaki tim ručno birao
sopstvena imena atributa umesto da se drži zajedničke konvencije, tačno onaj
problem sa četiri različita imena za isti koncept iz Poglavlja 2.

Vratimo se na krojača s početka poglavlja. On ne prepravlja svaki šav na
odelu — to bi koštalo koliko i novo odelo, i uništilo bi upravo ono što
fabrika radi dobro. Menja tačno onaj jedan detalj koji fabrika ne može da zna
unapred. **Ručna instrumentacija koja pokušava da zameni auto-instrumentaciju
je gubljenje vremena; ručna instrumentacija koja dopunjuje auto-instrumentaciju
na tačno jednom, dobro izabranom mestu je gotovo uvek vredna truda.** Veština
nije u tome koliko ručno instrumentiraš, nego u tome da li si prepoznao *koji*
je to jedan detalj za tvoj sistem.

## 5.4 Skupljena pravila iz ovog poglavlja

- Ne pokušavaj da ručno instrumentiraš ono što auto-instrumentacija već
  pokriva — potraži umesto toga šta auto-instrumentacija strukturno ne može
  da vidi (poslovni identitet, poslovna kategorija zahteva).
- Postavi dogovor o resursnim atributima (naziv, verzija, okruženje) kroz
  celu flotu pre nego što bilo koji tim počne da dodaje sopstvene, ad-hoc
  atribute istog značenja.
- Ako imaš više od jednog kanala kojim identitet ili kontekst stiže (token,
  API ključ, legacy parametar), normalizuj ih na jednom mestu (middleware),
  ne u svakom endpointu posebno.
- Postavi sebi pitanje pre svakog novog ručnog spana: "da li ovo dopunjuje
  auto-instrumentaciju, ili je pokušavam zameniti?" — drugi odgovor je gotovo
  uvek znak da vreme ide na pogrešno mesto.
- Ručna instrumentacija koja nije jeftina za održavanje neće biti održavana —
  planiraj je tako od početka, ne kao naknadnu nadu.
- Kad dva servisa nezavisno štite identitet u sopstvenoj telemetriji (npr.
  frontend šalje pseudonim, backend šalje pravi identitet), proveri privatnost
  na nivou SPOJENOG traga kroz propagaciju konteksta, ne po servisu posebno —
  mehanizam koji ih automatski povezuje ne zna da privatnost postoji kao briga.
- Ne pretpostavljaj da jednom dijagnostikovan uzrok i dalje važi — biblioteke
  od kojih zavisi auto-instrumentacija menjaju verzije, ponekad tiho
  popravljajući staru grešku kao sporedan efekat nepovezane izmene, dok
  identičan spoljašnji simptom ("nema podataka") u međuvremenu počne da ga
  proizvodi sasvim drugi mehanizam; proveri dijagnozu nanovo pre nego što je
  ponovo iskoristiš kao objašnjenje.

## 5.5 Vežba za čitaoca

Pronađi jedan endpoint ili zadatak u svom sistemu gde bi, usred incidenta,
morao ručno da ukrstiš trejs sa aplikativnim logom da bi saznao *ko* je
pokrenuo problematičan zahtev. Ako takav korak postoji, to je tvoj kandidat
za tačno onu vrstu ciljane ručne instrumentacije opisane u ovom poglavlju —
jedna tačka, jedno mesto u kodu, dosledna kroz sve puteve kojima taj identitet
može da stigne.

---

### Izvori korišćeni u analitičkom delu

- [Best practices for instrumenting OpenTelemetry — Elastic Observability Labs](https://www.elastic.co/observability-labs/blog/best-practices-instrumenting-opentelemetry)
- [Manual vs. auto instrumentation OpenTelemetry: Choose what's right — Cribl](https://cribl.io/blog/manual-vs-auto-instrumentation-opentelemetry-choose-whats-right/)
- [How to Compare OpenTelemetry Auto-Instrumentation vs Manual Instrumentation — OneUptime](https://oneuptime.com/blog/post/2026-02-06-compare-opentelemetry-auto-vs-manual-instrumentation/view)
- [OpenTelemetry Instrumentation: Manual vs. Automatic — Lumigo](https://lumigo.io/opentelemetry/opentelemetry-instrumentation-manual-vs-automatic-with-examples/)
- [Semantic Conventions for General Attributes (enduser.*) — OpenTelemetry](https://opentelemetry.io/docs/specs/semconv/registry/attributes/enduser/)
