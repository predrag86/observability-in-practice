# Poglavlje 24 — Posmatranje servisa koji nije naš (tipa Snowflake)

Kad restoran unajmi spoljnog dobavljača hrane za veliki događaj, šef kuhinje
tog restorana ne može da uđe u dobavljačevu kuhinju, ne može da proveri
temperaturu njihove rerne, ne može da stoji pored njihovog kuvara i gleda
kako se priprema jelo. Sve što šef kuhinje ima je ono što dobavljač sam
odluči da mu pokaže: račun na kraju, isporučena količina, i, ako je
dobavljač uredan, izveštaj o tome šta je poslato i kada. Ništa od toga nije
uživo — račun stiže sutradan, izveštaj kasni sat ili dva. A ako dobavljač
prestane da šalje izveštaje, to ne znači nužno da je hrana prestala da
stiže — možda je samo administrativna osoba koja piše izveštaje otišla na
odmor. Šef kuhinje koji to ne razlikuje bi mogao da pomisli da je čitav
događaj propao, dok je hrana, u stvari, stizala savršeno na vreme — samo
izveštaj o njoj nije.

## 24.1 Pitanje na koje ovo poglavlje odgovara

Poslednja domenska studija slučaja u ovom delu knjige razlikuje se od svih
prethodnih na jedan fundamentalan način: nema hosta na koji se agent
instalira, nema procesa kom se pristupa, nema mreže koja se posmatra iz
sopstvene infrastrukture. Servis je potpuno tuđ — u oblaku dobavljača,
upravljan isključivo od strane tog dobavljača. Šta uopšte znači "posmatrati"
nešto kad nemamo nijedan od uobičajenih alata za to?

## 24.2 Kako je to urađeno — praktičan pregled

### Nula posmatranja kao polazna tačka

Pre nego što je ovaj rad počeo, spoljni servis za analitičko skladištenje
podataka koji implementacija koristi nije imao apsolutno nijedan oblik
posmatranja — nijednu metriku, nijedan log, nijedan alarm. Sve što je
postojalo bio je mesečni račun i, povremeno, subjektivan utisak korisnika
da su pojedini upiti "spori." Ovo je vredna polazna tačka za poglavlje —
razlikuje ga od svih prethodnih studija slučaja, gde je neka forma
posmatranja već postojala i unapređivana.

### Zašto zakazano prikupljanje, a ne direktna konekcija

Pre nego što je bilo šta od gore opisanog izgrađeno, razmotrene su tri
različite putanje ka istom cilju — dashboard u platformi za posmatranje
koji pokazuje šta se dešava unutar spoljnog servisa.

Prva ideja je bila da se na platformu za posmatranje instalira gotov
konektor za direktnu, interaktivnu konekciju ka spoljnom servisu, potpisan
i učitan van zvaničnog kataloga. Ovo se pokazalo tehnički neizvodljivim na
korišćenoj varijanti platforme (upravljanoj, u oblaku, a ne
samostalno-hostovanoj): upravljana varijanta instalira isključivo
konektore iz zvaničnog kataloga, a mehanizam za privatno potpisivanje i
učitavanje sopstvenog konektora postoji samo za samostalno-hostovanu
varijantu platforme. Ćorsokak, otkriven tek pošto je pokušan.

Druga ideja je bila da se plati zvanični, proizvođački konektor za
direktnu konekciju — tehnički bi radio na upravljanoj varijanti platforme
bez ikakvih prepreka. Odbačen je zato što predstavlja stalnu, ponavljanu
stavku troška, a ne jednokratni trošak izgradnje — budžet za to nije
postojao.

Treća, izabrana i izgrađena putanja ne koristi nikakav direktan konektor
uopšte: umesto interaktivnog pristupa gde bi neko mogao da napiše
proizvoljan upit i odmah dobije odgovor, zakazano, kratkotrajno
pokretanje periodično povlači najsporije upite iz sopstvene, ugrađene
istorije upotrebe koju servis već vodi, i gura ih kao sanitizovane
zapise direktno u platformu za posmatranje. Dashboard nad tim zapisima
zamenjuje interaktivni pregled. Prihvaćen kompromis je eksplicitan: nema
slobodnog, proizvoljnog upitivanja kakvo bi dao pravi konektor — dobija
se periodično osvežavana tabela najgorih upita, ne alat za istraživanje.

### Tri faze, jedna zajednička sesija

Rešenje je izgrađeno u tri odvojene faze, svaka pokrivajući drugačiji cilj,
ali sve tri **dele istu sesiju** prema spoljnom servisu — svaka faza se
izvršava unutar istog zakazanog, kratkotrajnog pokretanja, umesto da svaka
otvara sopstvenu, novu sesiju:

- **Prva faza** — pregled najsporijih upita, isporučen kao pretraživi
  log-zapisi, sa poveznicom nazad na alat za dijagnostiku samog servisa za
  svaki upit.
- **Druga faza** — metrike na nivou naloga: potrošeni krediti, opterećenje
  po logičkoj radnoj jedinici, prostor za skladištenje, uspešnost prijava.
- **Treća faza** — svežina podataka (koliko je star poslednji učitan red u
  svakoj ključnoj tabeli) i agregirani pokazatelji performansi upita po
  radnoj jedinici.

Deljenje jedne sesije između sve tri faze nije samo tehnička pogodnost —
to je bila direktna odluka o trošku: pošto spoljni servis naplaćuje po
minimalnom vremenu aktivacije radne jedinice, svaka dodatna, odvojena
sesija bi značila dodatnu naplatu tog minimuma. Spajanjem sve tri faze u
jedno pokretanje, druga i treća faza koštaju praktično **nula dodatnih
kredita** iznad onoga što bi prva faza sama koštala.

### Kako mehanizam zaista radi, korak po korak

Sve tri faze iz prethodnog odeljka izvršava isti mehanizam, i taj
mehanizam vredi opisati na nivou "kako", ne samo "šta":

- **Okidač.** Zakazano pravilo pokreće kratkotrajno izvršavanje na svaka
  tri sata. Vredna zamka: ovakav "svaka N sati" raspored se u praksi
  računa od trenutka kada je *samo pravilo napravljeno*, ne od ponoći po
  časovniku — ako se pravilo ikad iznova napravi (a ne samo izmeni),
  tačno vreme pokretanja se pomera. Ko god prvi put podesi ovakav
  raspored i očekuje da će pogađati okrugle časove, iznenadiće se.
- **Beleška o mestu gde je stalo.** Pre svakog upita ka spoljnom servisu,
  mehanizam čita trajno sačuvanu belešku — do kog reda je poslednji put
  uspešno stigao. Upit traži samo redove novije od te beleške, sa gornjom
  granicom broja redova po pokretanju, uvek najstarije prvo. Beleška se
  pomera tek pošto su redovi uspešno isporučeni platformi za
  posmatranje — ne ranije — tako da neuspešno pokretanje ne gubi redove
  niti ih duplira.
- **Identitet sa minimalnim ovlašćenjima.** Upit se ne izvršava pod istim
  identitetom koji koriste stvarne aplikacije, već pod posebno napravljenim,
  isključivo-za-čitanje identitetom, ograničenim samo na potreban pogled
  na istoriju upotrebe. Autentikacija ide preko para ključeva, ne
  lozinke — kredencijal koji curi ovde ne otvara ništa osim ovog uskog
  pogleda. Sam upit se izvršava nad najmanjom mogućom radnom jedinicom
  servisa, iz istog razloga pomenutog ranije: minimalno vreme naplate po
  buđenju.
- **Sanitizacija pre nego što podatak napusti servis.** Tekst svakog
  upita se pre slanja čisti od stvarnih vrednosti (konkretni literali se
  zamenjuju placeholder znakom), svodi na jednu liniju i seče na razumnu
  dužinu — ono što stigne u platformu za posmatranje je oblik upita, ne
  podaci nad kojima je upit izvršen.
- **Isporuka.** Sanitizovani redovi se šalju kao logovi, istim opštim
  protokolom kojim ova implementacija svuda šalje logove, direktno u
  platformu za posmatranje — bez posrednog servera, bez privremenog
  fajla.

Celo pokretanje, sve tri faze zajedno, traje reda veličine desetak
sekundi do minut — dovoljno kratko da paket koda ne mora ni da se pakuje
kao kontejnerska slika. Pokretanje koje ne pronađe nijedan nov red je
sasvim uobičajeno i tiho se završava bez ičega za slanje — najveći deo
dana, jedno ranije pokretanje istog dana već je pokupilo sve što se tog
dana desilo.

![Konkretan tok podataka kroz zakazano prikupljanje: od stvarnog upita nad spoljnim servisom, preko okidača i beleške o mestu gde je stalo, do sanitizovanih zapisa u platformi za posmatranje.](diagrams/ch24-mehanizam-prikupljanja.png){: width="90%" }

### Strukturno kašnjenje, ne greška u dizajnu

Implementacija eksplicitno dokumentuje da ništa u ovom sistemu nije, niti
je ikad bilo namenjeno da bude, u realnom vremenu. Podaci koje spoljni
servis izlaže o sopstvenoj upotrebi kasne od četrdesetak minuta do
nekoliko sati, u zavisnosti od toga koji tip podatka se posmatra — ovo
kašnjenje je objavljeno svojstvo samog servisa, ne posledica ičega u
implementaciji. Praktična posledica: prag za "podatak nije stigao na
vreme" mora biti postavljen sa svesnom rezervom iznad ovog objavljenog
kašnjenja, jer bi prag postavljen preblizu stvarnom kašnjenju stalno lažno
alarmirao na potpuno zdravom sistemu.

### Alarm koji zavisi od zdravlja sopstvenog kolektora

Najvažnija lekcija ove implementacije, otkrivena i ispravljena tek posle
prvobitnog puštanja u rad: alarm koji prati svežinu podataka mora biti
eksplicitno uslovljen time da je sam mehanizam prikupljanja živ, ne samo
time da li je posmatrana vrednost postala stara. Prvobitna verzija ovog
alarma je posmatrala samo starost same metrike svežine — a kada je
mehanizam prikupljanja jednom prestao da radi (bez ijedne greške u
samom pozivu, samo tiho nije stigao do kraja), metrika svežine je
zamrzla na poslednjoj vrednosti dok je vreme nastavilo da prolazi, što je
prag za starost neizbežno prekoračilo i pokrenulo lažan, kritičan alarm o
navodnom **potpunom prekidu dotoka podataka** — na sistemu koji je u
stvarnosti bio potpuno zdrav. Popravka je bila da se alarm o svežini
podataka eksplicitno uslovi zasebnom metrikom "da li je kolektor uopšte
živ": bez tog uslova, mrtav kolektor izgleda identično kao katastrofalan
prekid dotoka podataka sa spoljnog servisa — dva potpuno različita
problema, ista lažna slika.

### Otkriveno tek pošto je neko prvi put pogledao

Sam čin uvođenja posmatranja otkrio je probleme koji su postojali
mesecima, potpuno nevidljivi dok niko nije imao razlog da ih traži:
nekoliko privremenih, "prelaznih" tabela — ostatak rutinskih mesečnih i
godišnjih obnova podataka — nikad nije obrisano posle završetka posla za
koji su napravljene, ukupno nekoliko terabajta neaktivnog prostora koji se
i dalje naplaćuje svakog meseca. Odvojeno, otkriveno je da tri različita
radna okruženja — razvojno, testno i produkciono — dele **isti** identitet
i istu lozinku za pristup spoljnom servisu, upisanu direktno kao obična,
nešifrovana promenljiva okruženja. Praktična posledica ovog drugog nalaza
je ozbiljna: curenje kredencijala iz najmanje osetljivog, gotovo
neaktivnog razvojnog okruženja bi u tom trenutku bilo identično curenju
produkcionog kredencijala — jer su, tehnički, isti. Oba nalaza su
prijavljena vlasnicima podataka na dalju odluku; posmatranje ih je samo
učinilo vidljivim, ne i rešilo.

![Tri faze prikupljanja nad spoljnim SaaS servisom, sve tri unutar jedne zajedničke, kratkotrajne sesije — alarm o svežini podataka eksplicitno uslovljen zasebnom metrikom zdravlja kolektora, da mrtav kolektor nikad ne bude pročitan kao prekid dotoka podataka.](diagrams/ch24-tri-faze.png){: width="90%" }

![Kad kolektor umre, gauge svežine se smrzava dok vreme nastavlja da prolazi — bez uslovljavanja zasebnom metrikom zdravlja kolektora, ovo izgleda identično stvarnoj katastrofi na potpuno zdravom sistemu.](diagrams/dashboard-snowflake.png){: width="95%" }

### Popravka atribucije nije popravka identiteta — i to je bila svesna odluka

Nalaz o deljenom identitetu iz prethodnog odeljka otvara očigledno pitanje:
zašto nije odmah rešen? Odgovor je da prava popravka — razdvajanje jednog
zajedničkog naloga u po jedan poseban identitet za svako radno okruženje —
nije nešto što se menja s ove strane, van vlasnika tog naloga, i nije nešto
što se radi preko noći. Dok se ta popravka čeka, ostaje pitanje bez odgovora:
kako uopšte razlikovati promet jednog okruženja od drugog u međuvremenu, kad
sva tri pišu identične upite pod istim korisničkim imenom?

Odgovor koji je primenjen ne dira identitet uopšte. Konekcioni string kojim
se aplikacija povezuje na spoljni servis sadrži i parametre koje sam servis
ne prepoznaje — a pokazalo se da upravljački drajver takav nepoznat parametar
tiho pretvara u parametar sesije, umesto da odbije konekciju. To znači da je
dovoljno dodati jedan takav parametar sa vrednošću koja identifikuje okruženje
("ovo je test", "ovo je produkcija") da bi svaki upit koji ta sesija izvrši
odsad nosio taj pečat u istoriji upotrebe servisa — bez ijedne linije koda,
bez novog paketa za isporuku, samo izmena promenljive okruženja i restart.

Ista osobina drajvera koja je ovo učinila bezbednim da se proba ima i naličje,
i oba su podjednako važna:

- **Bezbedno:** pogrešno ime parametra ne može da obori konekciju pri
  pokretanju — probni pokušaj ne nosi rizik da zaustavi aplikaciju.
- **Opasno:** pogrešno ime parametra **tiho ne radi ništa uopšte**. Konekcija
  uspeva, aplikacija radi dalje, sve izgleda potpuno normalno — a nijedan
  upit ne nosi novi pečat, i ništa u tom trenutku to ne prijavljuje.

Posledica je disciplina koja se provlači kroz celu ovu knjigu u različitim
oblicima: da je konekcija uspela, ili da je okruženje posle restarta ponovo
prijavilo zdravo stanje, ne dokazuje ništa o tome da je izmena zaista
proradila. Jedini pouzdan dokaz je pogledati **efekat** — u ovom slučaju,
upit direktno nad istorijom upotrebe servisa koji broji koliko upita zaista
nosi pečat svakog okruženja u poslednjih nekoliko sati. Uvođenje ovog
parametra je zaista bilo rađeno postepeno, okruženje po okruženje, i baš na
jednom od međukoraka desio se koristan skoro-incident: to okruženje je za
nekoliko minuta prijavilo ozbiljno narušeno zdravlje tokom same izmene.
Ispostavilo se da uzrok nije bio parametar servisa nego sasvim običan,
očekivan artefakt platforme na kojoj aplikacija radi — stare instance koje
se gase tokom uobičajene rotacije pri restartu, dok su preostale i dalje
uredno opsluživale saobraćaj bez ijedne greške. Da je provera stala na boji
statusa, umesto da pogleda stvaran saobraćaj, skoro-incident bi lako bio
pogrešno protumačen kao da je bezazlena izmena parametra nešto pokvarila.

Produkcijsko okruženje namerno nije dirano ovom brzom, ručnom izmenom uopšte
— pečat je tamo pušten u rad isključivo kroz redovan put isporuke koda, uz
odobrenje vlasnika sistema. Razlog nije opreznost radi opreznosti: potpunija
zamena istog mehanizma — pečat po pojedinačnom zahtevu, ne samo po okruženju
— već je bila u pripremi kroz taj isti put isporuke, i ručna izmena
produkcije bi bila posao koji sledeće redovno objavljivanje koda odmah
prepiše. Brza, ručna popravka ima smisla tamo gde ništa bolje nije već na
putu; kad bolje već dolazi istim kanalom, ručna prečica postaje posao koji
će neko drugi obrisati.

### Kad je prag podešen za tuđi posao, sopstveni saobraćaj postaje nevidljiv

Pečat po okruženju rešava pitanje "čiji je ovo upit". Ne rešava drugo,
odvojeno pitanje: da li se taj upit uopšte pojavljuje na dashboard-u koji
prikazuje najsporije upite iz prethodnog odeljka ovog poglavlja. Ovde se
otkrio nalaz koji zaslužuje sopstveni pasus, jer izgleda kao pokvaren pečat
dok je u stvari nešto sasvim drugo.

Dashboard najsporijih upita bira upite koji traju najmanje šezdeset sekundi
— prag koji je imao smisla za posao koji periodično učitava velike količine
podataka, i koji taj prag redovno prelazi. Glavna aplikacija, koja ovaj isti
spoljni servis koristi za sasvim drugu svrhu — brzo opsluživanje pojedinačnih
zahteva korisnika — izvršava na desetine hiljada upita dnevno nad tim istim
servisom, i **nijedan jedini od njih** ne prelazi taj prag od šezdeset
sekundi. Posledica: svaki red koji je taj dashboard ikad prikazao potiče od
posla za učitavanje podataka, ne od glavne aplikacije — dashboard koji po
imenu treba da pokriva ceo servis je, u praksi, dashboard samo jednog njegovog
korisnika.

Kad je pečat po okruženju pušten u rad, prirodno se očekivalo da će nova
kolona na tom istom dashboard-u odmah pokazati saobraćaj glavne aplikacije po
okruženjima. Ta kolona je ostala prazna — i to je trenutak gde je razlika
između dva različita objašnjenja presudna. Prazna kolona *izgleda* kao dokaz
da pečat ne radi, isti onaj neuspeh opisan u prethodnom odeljku. Nije: pečat
radi ispravno i upisuje se na svaki upit; upiti na koje se upisuje samo nikad
ne prelaze prag koji bi ih uveo na ovaj konkretan dashboard. Ovo je varijanta
istog obrasca viđenog ranije u knjizi (Poglavlje 20, prijave koje se broje
kao nula ne zato što ih nema, nego zato što selektor gleda pogrešan tip
događaja) — merenje koje izgleda kao "nema ničega" dok stvaran uzrok leži u
tome gde je granica povučena, ne u tome da li se nešto zaista dešava. Jedini
način da se razlikuju ova dva objašnjenja je proveriti direktno nad istorijom
upotrebe servisa, mimo dashboard-a i mimo praga, da li pečat zaista postoji
na upitima glavne aplikacije — a on jeste. Ispravna popravka nije "proveri da
li je pečat pokvaren", nego zaseban, niži prag za upite ovog konkretnog
korisnika servisa — priznata, još neizvedena stavka na listi poboljšanja, ne
nešto što bi bilo koja izmena samog pečata mogla da reši.

## 24.3 Analitički deo — posmatranje bez pristupa infrastrukturi kao poseban problem

### Servis sam razlikuje dva različita oblika sopstvene posmatranosti

Zvanična dokumentacija spoljnog servisa pravi jasnu razliku između dva
potpuno odvojena problema: instrumentacija **koda koji se izvršava unutar**
servisa (uskladištene procedure, korisnički definisane funkcije) naspram
posmatranja **kako se sam servis kao celina koristi** (potrošnja, upiti,
opterećenje, prijave). Prvi problem servis rešava sopstvenim mehanizmom
tragova i događaja, ugrađenim u platformu. Drugi problem — onaj kojim se
ovo poglavlje bavi — servis rešava isključivo kroz sopstvene, upitljive
poglede na istoriju upotrebe. Implementacija je ispravno prepoznala da je
njen slučaj isključivo ovaj drugi: servis se koristi kao skladište, ne kao
platforma na kojoj se izvršava sopstveni kod, pa prvi mehanizam
jednostavno nema šta da posmatra u ovom slučaju.

### Objavljeno kašnjenje je zvanično dokumentovano, po pogledu, ne pretpostavka

Zvanična dokumentacija svakog pojedinačnog upitljivog pogleda koji
implementacija koristi navodi eksplicitnu, brojčanu vrednost očekivanog
kašnjenja — od četrdesetak minuta do nekoliko sati, u zavisnosti od
konkretnog pogleda — sa napomenom da su ove vrednosti "približne" i da
stvarno kašnjenje ponekad može biti manje. Ovo je direktna potvrda da
implementacija nije proizvoljno pretpostavila kašnjenje, nego ga je
preuzela iz objavljene specifikacije samog servisa — princip koji bi
trebalo primeniti na svaki spoljni servis čije unutrašnje stanje se
posmatra samo kroz njegov sopstveni izloženi API, ne kroz direktan
pristup.

### Obrazac "mrtav kolektor izgleda kao katastrofa" je poznat, imenovan problem u praćenju crne kutije

Šira literatura o posmatranju sistema bez direktnog pristupa hostu — kroz
periodično ispitivanje tuđeg izloženog API-ja, uobičajen obrazac za bilo
koji spoljni, upravljan servis — tretira nejasnoću "nema novih podataka"
kao dobro poznat, ponavljajući problem: takav alarm po definiciji izgleda
identično bilo da je uzvodni servis stvarno utihnuo, bilo da je sam
mehanizam prikupljanja prestao da radi. Standardna, preporučena popravka
je tačno ona koju je implementacija primenila tek posle prvog lažnog
alarma — učiniti alarm o zastarelosti uslovljenim nezavisno proverenim
zdravljem samog kolektora, a ne tretirati "stara metrika" i "tih uzvodni
servis" kao isti signal.

### Podešavanje minimalnog vremena aktivacije nema univerzalnu vrednost

I zvanična dokumentacija spoljnog servisa i nezavisni komentari o
kontroli troška u oblaku odbacuju postojanje jedne univerzalne "ispravne"
vrednosti za minimalno vreme aktivacije radne jedinice — umesto toga, oba
izvora ga tretiraju kao kompromis specifičan za radno opterećenje, između
brzine gašenja (manje traćenje kredita dok je jedinica neaktivna) i
očuvane toplote keša (brže sledeće izvršavanje ako jedinica ostane
aktivna malo duže). Zvanična preporuka ide dalje i eksplicitno upozorava
na neusklađenu vrednost — predugo zadržavanje aktivnosti za jedinicu koja
se koristi retko troši kredite bez ijedne koristi od keša. Ovo potvrđuje
da izbor implementacije da zadrži agresivno kratko vreme aktivacije za
zakazan, periodičan posao — gde nema koristi od toplog keša između
pokretanja koja su satima razdvojena — nije proizvoljan, nego usklađen sa
sopstvenom logikom radnog opterećenja.

### Ista promena, dva magacina, suprotan predznak — merenje odlučuje, ne pravilo

Konkretno merenje na dva različita Snowflake magacina u istom sistemu ide
korak dalje od opšteg principa iznad: pokazuje da identična izmena — skraćeno
minimalno vreme aktivacije — nije samo pitanje "koliko kratko," nego pitanje
sa **suprotnim** predznakom u zavisnosti od magacina.

Na magacinu posvećenom periodičnom, zakazanom poslu, skraćivanje minimalnog
vremena aktivacije je bilo najbolja pojedinačna popravka troška u celom
sistemu — merenje je pokazalo da je većina pauza između upita duža od
postojećeg minimuma, pa se kraći minimum direktno prevodi u uštedu bez ijedne
izgubljene prednosti toplog keša (kojeg tu i tako nema). Na drugom, susednom
magacinu koji opslužuje interaktivan, česti saobraćaj, potpuno ista izmena bi
učinila trošak **gorim**, ne boljim — merenje je pokazalo suprotnu
raspodelu: većina pauza između upita je kraća od postojećeg minimuma, pa bi
skraćivanje samo umnožilo broj puta kad se magacin ponovo pokreće i plaća
sopstveni minimum naplate po pokretanju, umesto da tu pauzu prosto sačeka.

Presudni podatak nije tip posla niti intuicija o tome "ovaj magacin izgleda
opterećenije" — presudan je stvaran raspored dužine pauza između upita, po
magacinu, nevidljiv bez atribucije troška na nivo pojedinačnog upita.
Pravilo koje sledi: promena minimalnog vremena aktivacije se nikad ne
prepisuje sa jednog magacina na drugi kao "dobra praksa" — svaki magacin
nosi sopstvenu raspodelu pauza, i ta raspodela, izmerena, jeste odgovor.

### Kontrafaktički scenario: šta bi ostalo nevidljivo bez ovog rada

Zamislimo da je odluka bila "nemamo pristup infrastrukturi, pa nema šta da
se posmatra" — validan, ali pogrešan zaključak. Nekoliko terabajta
neiskorišćenih, zaboravljenih tabela bi nastavilo da se naplaćuje
neograničeno, jer niko ne bi imao razlog da ih traži bez sistematskog
pregleda upotrebe po tabeli. Deljen, nešifrovan kredencijal između tri
okruženja bi ostao neotkriven sve dok, u najgorem slučaju, curenje iz
najmanje čuvanog okruženja ne postane stvaran bezbednosni incident u
produkciji. Oba nalaza su postojala pre ovog rada, potpuno nevidljiva —
posmatranje ih nije stvorilo, samo je prvi put omogućilo da budu viđeni.

Vratimo se restoranu i njegovom spoljnom dobavljaču s početka poglavlja.
Šef kuhinje nikad neće moći da uđe u tuđu kuhinju — ali može tražiti
bolji izveštaj, upoređivati ga iz nedelje u nedelju, i primetiti kad nešto
u tom izveštaju ne štima, čak i preko one uobičajene, prihvaćene
kašnjenja od jednog dana. Posmatranje servisa koji nije naš nikad neće
biti isto kao posmatranje sopstvene infrastrukture — ali odsustvo pristupa
hostu nije isto što i odsustvo mogućnosti da se nešto sazna. Vraćamo se
i na pitanje postavljeno mnogo ranije u ovoj knjizi: šta uopšte znači
"posmatrati" nešto — i odgovor, potvrđen ovde na najtežem mogućem
primeru, ostaje isti. Posmatranje nikad nije bilo o direktnom pristupu.
Uvek je bilo o tome da se postavi pravo pitanje i pronađe **bilo koji**
pouzdan put do odgovora, čak i kad taj put vodi kroz tuđ, zakasneli
izveštaj.

## 24.4 Skupljena pravila iz ovog poglavlja

- Kad servis nema host ni proces kom se može pristupiti, potraži
  sopstvene, upitljive poglede na istoriju upotrebe koje servis sam
  izlaže — to je jedini dostupan izvor istine, i skoro svaki ozbiljan
  spoljni servis ga ima u nekom obliku.
- Preuzmi objavljeno kašnjenje direktno iz zvanične specifikacije servisa,
  po svakom pojedinačnom izvoru podataka — ne pretpostavljaj jedinstvenu
  vrednost kašnjenja za ceo servis odjednom.
- Uslovi svaki alarm o zastarelosti podataka nezavisnom proverom da je
  sam mehanizam prikupljanja živ — bez tog uslova, mrtav kolektor i
  stvaran prekid dotoka izgledaju identično, i lažno će pokrenuti
  najozbiljniju moguću uzbunu.
- Kad naplata zavisi od minimalnog vremena aktivacije, spoji sve faze
  prikupljanja u jednu zajedničku sesiju umesto da svaka otvara
  sopstvenu — razlika u trošku može biti ogromna za posao koji inače
  ne bi ni primetio da deli infrastrukturu.
- Očekuj da će sam čin uvođenja posmatranja otkriti probleme koji nemaju
  nikakve veze sa observability-jem — zaboravljene resurse, deljene
  kredencijale — jer niko pre toga nije imao razlog, ni alat, da ih
  potraži.
- Kad direktna, interaktivna konekcija ka spoljnom servisu nije
  dostupna besplatno (a plaćena varijanta nije u budžetu), proveri da li
  spoljni servis već vodi sopstvenu istoriju upotrebe koju možeš
  periodično povlačiti i gurati kao logove — periodično osvežavana
  tabela najgorih slučajeva je često dovoljna zamena za slobodno
  upitivanje.
- Kad se identitet ne može odmah popraviti, potraži lakšu, obratnu
  popravku za atribuciju — ali proveri da li mehanizam koji to
  omogućava (npr. nepoznat parametar konekcije koji drajver tiho
  prihvata) ima i naličje: ista osobina koja čini probu bezbednom čini
  i grešku u kucanju potpuno nevidljivom. Uvek proveri efekat, nikad
  samo da je konekcija ili okruženje ostalo zdravo.
- Prazna kolona ili nulta vrednost posle uvedene izmene nije
  automatski dokaz da izmena ne radi — proveri da li prag ili filter
  strukturno isključuje baš taj saobraćaj, pre nego što zaključiš da je
  sama izmena pokvarena.
- Ne prepisuj podešavanje minimalnog vremena aktivacije sa jednog magacina
  na drugi kao "dobru praksu" — ista izmena može uštedeti na jednom i
  poskupeti drugi, u zavisnosti od raspodele pauza između upita specifične
  za taj magacin. Izmeri po magacinu, nikad ne generalizuj iz jednog
  slučaja.

## 24.5 Vežba za čitaoca

Nabroj spoljne, upravljane servise koje tvoj sistem koristi, a nad kojima
nemaš nikakav pristup hostu ili procesu — servis za plaćanje, servis za
slanje email-a, spoljni skladišni sloj podataka, bilo šta u tuđem oblaku.
Za jedan od njih, pronađi da li taj servis izlaže sopstveni pogled na
istoriju upotrebe koji bi mogao da se redovno ispituje. Ako postoji, a
niko ga trenutno ne koristi — to je praznina koju ovo poglavlje traži da
zatvoriš.

---

### Izvori korišćeni u analitičkom delu

- [Account Usage — Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage)
- [QUERY_HISTORY view — Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [WAREHOUSE_METERING_HISTORY view — Snowflake Documentation](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [Optimizing the warehouse cache — Snowflake Documentation](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-cache)
- [Observability in Snowflake: A New Era with Snowflake Trail — Snowflake Blog](https://www.snowflake.com/en/blog/observability-new-era-with-snowflake-trail/)
- [How to setup a Prometheus dead man's switch](https://jakubstransky.com/2019/01/26/who-monitors-prometheus/)
