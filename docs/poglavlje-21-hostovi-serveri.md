# Poglavlje 21 — Hostovi i serveri kao mašine

Pozajmljena mapa grada retko odgovara ulicama kroz koje se stvarno vozi.
Neko je nacrtao tu mapu za svoj grad, svoje raskrsnice, svoja jednosmerna
pravila — i kad je poneseš u drugi grad, deo nje se poklapa dovoljno dobro
da zavara, a deo je jednostavno pogrešan: ulica koju mapa označava kao
prolaznu je zatvorena, raskrsnica koju mapa očekuje na jednom mestu je
pomerena za dva bloka. Vozač koji slepo prati takvu mapu ne skreće
pogrešno zato što ne zna da vozi — skreće pogrešno zato što mapa tvrdi
nešto što više nije tačno za ovaj konkretan grad. Rešenje nije odbaciti
svaku mapu i voziti napamet — rešenje je nacrtati sopstvenu, malu, tačnu
mapu za ulice koje stvarno koristiš, čak i ako je mnogo skromnija od one
pozajmljene.

## 21.1 Pitanje na koje ovo poglavlje odgovara

Postoje gotovi, besplatni dashboardi za praćenje servera — preuzmu se sa
nekoliko klikova i obećavaju trenutan uvid. Zašto oni tako često ne rade
čim se stvarno uvezu, i šta znači izgraditi sopstveni, minimalan skup
metrika umesto da se pozajmi tuđi?

## 21.2 Kako je to urađeno — praktičan pregled

### Četiri konkretna razloga zašto pozajmljeni dashboard ne radi

Implementacija je dokumentovala, iz stvarnog iskustva uvoza nekoliko
popularnih zajedničkih dashboarda, četiri odvojena, strukturna razloga
zašto ti dashboardi jednostavno prestaju da rade — ne zbog greške u
podešavanju, nego zbog neusaglašenosti koja postoji čak i kad je sve
"ispravno" instalirano:

- **Pogrešan izvor podataka ugrađen u sam dashboard.** Izvezeni JSON
  dashboarda nosi identifikator izvora podataka iz okruženja osobe koja ga
  je originalno napravila. Uvezen u drugo okruženje, taj identifikator
  jednostavno ne postoji — svaki panel se tiho vraća na "nema podataka,"
  bez greške koja bi to objasnila.
- **Jedan nedostajući kolektor obara sve promenljive šablona.** Dashboard
  pretpostavlja da su svi standardni moduli za prikupljanje uključeni.
  Ako je samo jedan isključen ili drugačije imenovan, upit koji puni
  padajuću listu servera/instanci vraća prazan rezultat — što obara **ceo**
  dashboard u "nema podataka," iako svi ostali podaci u pozadini postoje i
  ispravni su.
- **Šema imenovanja metrika se ne poklapa.** Dashboard napisan za jednu
  konvenciju imenovanja metrika (klasičan format sa prefiksom) ne pronalazi
  ništa kad su stvarne metrike prikupljene drugom, novijom konvencijom
  (OpenTelemetry-stil imenovanja) — različiti nazivi za potpuno iste
  fizičke veličine.
- **Agregacija na strani platforme tiho briše oznake koje dashboard
  očekuje.** Mehanizam koji platforma za metrike koristi da bi smanjila
  trošak — agregiranje redje korišćenih serija — može ukloniti baš onu
  kombinaciju oznaka koju stara promenljiva šablona ili upit očekuje,
  ostavljajući panel prazan bez ijedne poruke o grešci.

Zajednička nit sve četiri: nijedan od ova četiri razloga nije "korisnička
greška" u klasičnom smislu. Svaki je strukturna neusaglašenost između
pretpostavki dashboarda i stvarnog okruženja u koje je uvezen.

### Kako se izgubljena oznaka zaista vraća, korak po korak

Četvrti razlog — agregacija koja tiho briše oznake — zaslužuje dublji uvid,
jer njegov mehanizam krije dve zamke koje čine očigledan popravak
neupotrebljivim.

Prva zamka: ista metrika, ista tražena oznaka, ali različita funkcija
agregacije daje potpuno različit rezultat. Sistem koji automatski smanjuje
broj vremenskih serija ne pamti "ovu oznaku" — pamti tačno **koje**
agregacione funkcije je prethodno izračunao i sačuvao za svaku
kombinaciju. Upit koji koristi baš tu sačuvanu funkciju radi. Upit koji
traži drugu, podjednako razumnu funkciju nad istim podacima vraća — ne
grešku, nego tiho **prazan rezultat**, nerazlučiv od "ovog problema
jednostavno nema." Dva od četiri uobičajena izbora funkcije mogu vratiti
prazno, dok preostala dva rade, na potpuno istoj metrici i istoj oznaci.

Druga zamka je suptilnija i čini najprirodniji popravak nemogućim: ideja
"dodaj alarm ili pravilo koje redovno čita ovu oznaku, pa će sistem sam
zaključiti da je oznaka tražena i prestati da je briše" **ne može sama
sebe pokrenuti**. Dok je oznaka još uvek pod agregacijom, upit koji bi
takav alarm koristio pogađa prvu zamku — tiho prazan rezultat, zauvek —
tako da alarm nikad ne vidi podatak koji bi ga naveo da uopšte postoji.
Popravak zato mora ići u suprotnom redosledu od intuitivnog: prvo se samo
pravilo agregacije ručno ukloni za tačno one metrike i oznake koje
nedostaju, zatim se potvrdi da su oznake stvarno počele da se pune (u
merenom slučaju, u roku od nekoliko minuta), i tek onda se dodaje trajno
pravilo koje čita tu oznaku — da bi je ubuduće držalo van agregacije, ne
da bi je prvi put oslobodilo.

Sam čin uklanjanja pravila nosi treću zamku, operativnu: sistem koji
automatski predlaže i primenjuje agregaciona pravila radi u pozadini, bez
nadzora, i menja isti skup pravila koji se upravo pokušava ručno
izmeniti. Dva čitanja istog skupa pravila, minut-dva razmaknuta, mogu
pokazati različit broj pravila — što znači da naivno "pročitaj, izmeni
lokalno, upiši nazad" rizikuje da tiho obriše tuđu, međuvremenu izmenu.
Ispravan pristup uslovljava upis na tačnu verziju pročitanog stanja, tako
da upis otkaže (umesto da tiho pregazi) ako se stanje u međuvremenu
promenilo, i posle upisa eksplicitno potvrđuje da je promenjeno tačno
onoliko pravila koliko je i nameravano — ni više ni manje.

![Pogrešan redosled popravke izgubljene oznake ne radi — oznaka je i dalje pod agregacijom, upit tiho vraća prazno. Ispravan redosled prvo uklanja pravilo agregacije, potvrđuje da se oznaka zaista vratila, i tek onda dodaje trajno pravilo koje je ubuduće drži otvorenom.](diagrams/ch21-redosled-vracanja.png){: width="75%" }

### Minimalan, namerno biran skup metrika umesto tuđeg kompleta

Umesto da pokuša da popravi svaki od četiri razloga za svaki uvezeni
dashboard, implementacija je krenula suprotnim putem: definisala je
sopstveni, mali skup metrika i alarmi, biran namerno po tome koje
konkretno pitanje svaka metrika odgovara, a ne po tome što je "standardna"
ili dolazi u paketu. Rezultat je manji, ali potpuno razumljiv skup — svaki
panel na dashboardu ima poznat razlog zašto postoji, i niko u timu ne mora
da nagađa da li je "nema podataka" na panelu prava vest ili artefakt jedne
od četiri neusaglašenosti opisane iznad.

### Kalibracija praga: sedmodnevni maksimum, ne trenutna vrednost

Implementacija je usput ispravila metodološku grešku otkrivenu tokom same
analize: prag za alarm nikad se ne postavlja na osnovu vrednosti izmerene
u jednom trenutku — uvek se postavlja na osnovu maksimuma posmatranog kroz
duži prozor, na primer sedam dana. Konkretan slučaj koji je ovo pokazao:
prag postavljen na osnovu trenutne, "tipične" vrednosti bio je za red
veličine pogrešan u odnosu na stvaran, legitiman vrh koji se dešava
redovno, samo ne baš u trenutku kad je neko gledao ekran. Ova greška je
uhvaćena i ispravljena usred same analize, ne posle incidenta izazvanog
lažnim alarmom.

### Utilizacija naspram zasićenja kao dve odvojene klase alarma

Implementacija je razdvojila dva pitanja koja se lako pomešaju kad se
alarmira samo na procenat zauzeća resursa: koliko je resurs **zauzet**
(utilizacija) i koliko posla **čeka** na taj resurs, a ne stiže da bude
opsluženo na vreme (zasićenje). Jedna odluka je prvobitno bila "ne
alarmiraj ovde, biće bučno" — ali poređenje sa poznatim referentnim
alarmnim skupom je pokazalo da je ta odluka pobrkala ova dva pojma: metrika
koja meri zasićenje (dužina reda čekanja, na primer) je mnogo pouzdaniji
rani signal problema od metrike koja meri samo utilizaciju, i retko je
zaista bučna na način na koji je pretpostavka tvrdila.

### "Odbijeno sa razlogom" kao trajno drugačija kategorija od "još nije urađeno"

Implementacija vodi eksplicitnu razliku između dve vrste praznina u
pokrivenosti: stvari koje **nisu urađene jer nisu stigle na red**, i
stvari koje su **svesno odbijene, sa zapisanim razlogom** — na primer,
metrika koja bi bila skupa u pogledu kardinalnosti a odgovara na pitanje
koje se do sada nikad nije stvarno postavilo. Ova razlika sprečava da neko
kasnije, gledajući samo listu "nedostaje," pretpostavi da je svaka
praznina propust — neke su namerne, promišljene odluke, i imaju zapisan
razlog za onog ko ih kasnije preispita.

![Zašto uvezeni zajednički dashboard tipično prestane da radi: pogrešan izvor podataka, nedostajući kolektor koji obara promenljive šablona, neusaglašena šema imenovanja, i agregacija koja tiho briše oznake — četiri odvojena uzroka, isti simptom "nema podataka."](diagrams/ch21-cetiri-uzroka.png){: width="90%" }

## 21.3 Analitički deo — poznat metod, dokumentovan uzrok kvara

### USE metod kao formalni okvir za ono što implementacija radi intuitivno

Formalni metod za dijagnostiku performansi sistemskih resursa poznat kao
USE (Utilizacija, Zasićenje, Greške) definiše tačno tri ose koje treba
proveriti za svaki resurs — koliko je zauzet, koliko posla čeka, i koliko
grešaka nastaje. Ovaj metod eksplicitno naglašava da je zasićenje često
raniji i pouzdaniji signal nadolazećeg zastoja od same utilizacije — što
je tačno ispravka koju je implementacija sama, nezavisno, otkrila
poređenjem sa referentnim alarmnim skupom.

### Zvaničan referentni alarmni skup potvrđuje izbor implementacije

Zvanični, zajednički održavan alarmni skup za standardni sistem
prikupljanja metrika hosta ne fokusira se prvenstveno na proste pragove
procenta CPU-a ili memorije — umesto toga naglašava prediktivne signale
(stopa punjenja diska pre nego što se stvarno napuni, iscrpljivanje broja
i-node-ova, greške na mrežnom interfejsu, degradiran RAID, otkazan
sistemski servis, neusklađenost sistemskog sata). Sam autor tog skupa ga
opisuje kao "rad u toku" i model za dalje prilagođavanje — priznanje da
čak ni zvanični, referentni skup nije konačan ili univerzalno tačan
proizvod, što direktno potkrepljuje odluku implementacije da izgradi
sopstven, manji, ali potpuno razumljiv skup, umesto da preuzme tuđi kao
gotov.

### Neusaglašenost šeme imenovanja je dokumentovan, rastući problem

Razlika u imenima metrika između klasične konvencije i OpenTelemetry-stil
konvencije je potvrđen, dokumentovan problem u samoj zajednici koja
održava standardne kolektore metrika — postoji otvorena diskusija u
projektu koji razvija OpenTelemetry kolektor upravo o ovoj neusaglašenosti,
gde klasičan skup ima znatno više pojedinačnih metrika nego noviji,
kompaktniji OTel skup, pod potpuno drugim imenima i ponekad drugom
granularnošću. Ovo nije hipotetički rizik koji je implementacija
izmislila — to je aktivno priznat jaz u samom ekosistemu alata.

### Agregacija koja briše oznake je dokumentovana platformska karakteristika, ne greška

Zvanična dokumentacija mehanizma platforme koji agregira ređe korišćene
serije radi uštede troška eksplicitno navodi scenarije u kojima postojeći
dashboard prestaje da radi posle uključivanja te agregacije: upit koji
traži tip agregacije koji nije konfigurisan vraća prazan rezultat, upit
koji traži vrednost oznake koja je uklonjena agregacijom vraća prazan
rezultat, a upit koji obuhvata i period pre i period posle prelaska na
agregaciju namerno vraća potpuno prazan odgovor — po dizajnu, da bi se
izbeglo tiho vraćanje pogrešnog broja umesto ničega. Ovo potvrđuje da je
jedan od četiri razloga koje je implementacija identifikovala zapravo
zvanično dokumentovana, očekivana posledica uključivanja ove uštede — ne
nusprodukt lošeg podešavanja.

### Kontrafaktički scenario: šta bi se dogodilo da je dashboard uvožen bez provere

Zamislimo tim koji je jednostavno uvezao popularan zajednički dashboard,
video da nekoliko panela pokazuje podatke, i proglasio zadatak završenim —
bez sistematske provere zašto ostali paneli pokazuju "nema podataka."
Prva stvarna kriza bi otkrila da polovina dashboarda koju su mislili da
imaju zapravo nikad nije radila — ne zato što alarm nije stigao, nego zato
što panel koji je trebalo da pokaže upozoravajući trend nikad nije ni
prikazivao podatke, i niko to nije primetio dok nije bilo prekasno da
pomogne.

Vratimo se na pozajmljenu mapu s početka poglavlja. Mapa nije beskorisna
— samo je nacrtana za drugi grad. Vozač koji shvati tu razliku ne baca
mapu; koristi je kao polaznu tačku, proverava svaku raskrsnicu koju
stvarno koristi, i na kraju ima sopstvenu, manju, ali potpuno tačnu mapu.
Dashboard koji je izgrađen namerno, panel po panel, umesto uvezen ceo
odjednom, radi isto — manji je od onoga što je moglo biti preuzeto, ali
svaki deo njega je proveren i tačan za grad u kom se stvarno vozi.

## 21.4 Skupljena pravila iz ovog poglavlja

- Kad uvoziš tuđi dashboard, proveri sva četiri strukturna razloga zašto
  paneli mogu pokazivati "nema podataka" — pogrešan izvor podataka,
  nedostajući kolektor koji obara promenljive šablona, neusaglašenu šemu
  imenovanja, i agregaciju koja briše oznake — pre nego što pretpostaviš
  da je dashboard jednostavno "spreman za upotrebu."
- Kalibriši svaki prag alarma na osnovu maksimuma kroz duži vremenski
  prozor, nikad na osnovu vrednosti izmerene u jednom trenutku — greška
  reda veličine je lako moguća ako se prag postavi na "tipičnu" vrednost.
- Razdvoji utilizaciju od zasićenja kao dve odvojene klase alarma —
  zasićenje je često pouzdaniji, raniji signal nadolazećeg problema, i
  retko je onoliko bučno koliko se pretpostavlja bez provere.
- Beleži svesno odbijene metrike sa razlogom, odvojeno od stvari koje
  jednostavno još nisu urađene — obe su praznine u pokrivenosti, ali samo
  jedna je propust koji treba popraviti.
- Razmisli da izgradiš manji, namerno biran skup metrika umesto uvoženja
  tuđeg kompleta — svaki panel koji postoji zato što odgovara na poznato
  pitanje je vredniji od deset panela koji postoje zato što su došli u
  paketu.
- Kad vraćaš oznaku koju je automatska agregacija obrisala, ne dodaji
  prvo alarm koji je "drži otvorenom" — dok je oznaka još agregirana, taj
  alarm sam sebe ne može pokrenuti, jer pogađa istu tihu-prazno zamku
  koju pokušava da otkrije. Prvo ukloni pravilo agregacije, potvrdi da se
  oznaka vratila, tek onda dodaj trajno pravilo. I uslovi taj upis na
  tačnu verziju pravila koje menjaš, ako isti skup pravila u pozadini
  menja i neki automatski proces — inače rizikuješ da tiho pregaziš
  promenu koja se desila između tvog čitanja i tvog pisanja.

## 21.5 Vežba za čitaoca

Otvori jedan uvezeni, zajednički dashboard koji tvoj tim koristi za
praćenje servera. Za svaki panel koji trenutno pokazuje "nema podataka"
ili prazan grafik, utvrdi tačan uzrok — da li je izvor podataka pogrešan,
da li nedostaje kolektor, da li se imena metrika ne poklapaju, ili je
agregacija obrisala oznaku koju panel traži. Zapiši uzrok pored svakog
praznog panela pre nego što odlučiš da li ga popraviti ili ukloniti.

---

### Izvori korišćeni u analitičkom delu

- [USE Method: Linux Performance Checklist — Brendan Gregg](https://www.brendangregg.com/USEmethod/use-linux.html)
- [node_exporter mixin — README i alerts.libsonnet](https://github.com/prometheus/node_exporter/blob/master/docs/node-mixin/README.md)
- [Comparing node_exporter and OpenTelemetry Collector host metrics receiver](https://luppeng.wordpress.com/2025/07/26/comparing-the-key-hardware-and-os-metris-exposed-by-prometheus-node-exporter-and-opentelemetry-collectors-host-metrics-receiver/)
- [opentelemetry-collector-contrib issue #22067 — naming differences node_exporter vs OTel](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/22067)
- [Grafana Cloud — Troubleshoot your aggregated metrics query (Adaptive Metrics)](https://grafana.com/docs/grafana-cloud/adaptive-telemetry/adaptive-metrics/troubleshoot-your-aggregated-metrics-query/)
- [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
