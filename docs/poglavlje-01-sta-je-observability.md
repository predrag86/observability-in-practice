# Poglavlje 1 — Šta je observability, a šta je samo monitoring sa novim imenom

Avion ima dva potpuno različita sistema za beleženje sopstvenog stanja. Prvi su
instrumenti u kokpitu: brzinomer, visinomer, indikator goriva, alarm za pad
pritiska u kabini. Svaki od njih meri tačno jednu unapred poznatu stvar i javlja
se onog trenutka kad ta stvar izađe iz granice — piloti su, kad su instrumenti
projektovani, morali unapred da znaju šta može da pođe po zlu da bi uopšte
postavili senzor za to.

Drugi sistem je crna kutija — u stvari dve kutije, flight data recorder i
cockpit voice recorder. One ne javljaju ništa nikome u realnom vremenu. Njihov
posao je samo da upamte apsolutno sve — svaki parametar leta, svaku reč u
kokpitu — tako da posle nesreće, istražitelj koji tog jutra nije imao pojma šta
će tražiti, može da postavi bilo koje pitanje unazad i dobije odgovor. Crna
kutija ne zna unapred šta će pokvariti let. Ona samo garantuje da će, kad se to
dogodi, dokaz postojati.

To je razlika između monitoringa i observability-ja, i ona je operativna, ne
filozofska: monitoring odgovara na pitanja koja si postavio *unapred*.
Observability odgovara na pitanja koja postaviš *posle*, o incidentu koji nisi
mogao da predvidiš dovoljno precizno da za njega napraviš poseban alarm.

## Pre nego što krenemo dalje: nekoliko osnovnih pojmova

Vredi odmah imenovati par termina koje ćemo od ove tačke koristiti bez
čekanja na posebno poglavlje za svaki — tačno onako kako je pilotu iz
primera gore njegov instrument poznat pre nego što bilo šta pođe po zlu.

- **Metrika** — jedan broj koji se meri tokom vremena (broj zahteva u
  sekundi, iskorišćenost CPU-a, dužina reda za obradu). Jeftina je za
  čuvanje i brza za grafikon, ali sama po sebi ne kaže *koji* zahtev ili
  *koji* korisnik stoji iza tog broja.
- **Log** — tekstualni zapis jednog konkretnog događaja, u tačno
  određenom trenutku ("14:32:07 — zahtev X vratio grešku Y"). Bogatiji je
  od metrike, ali teži za pretragu ako nije strukturiran i povezan sa
  ostatkom sistema.
- **Trag (trace)** — zapis putanje *jednog* zahteva kroz sve servise kroz
  koje je prošao, sastavljen od pojedinačnih koraka koji se zovu
  **rasponi (spans)** — jedan raspon po servisu ili operaciji, sa
  trajanjem i ishodom. Trag sa atributom `records_returned=0` iz
  incidenta u § 1.2 ispod je upravo ovakav zapis.
- **Atribut (label)** — par ključ-vrednost zakačen za metriku, log ili
  raspon, koji kaže *čiji* je podatak i u kom kontekstu (`service.name`,
  `http.response.status_code`, `records_returned`). Bez atributa, tri
  stuba ostaju tri gomile brojeva bez konteksta ko je šta uradio.
- **Dashboard** i **alarm** — grafička tabla sa grafikonima, i pravilo
  koje se samo oglašava kad neka vrednost pređe prag; ovi pojmovi već
  postoje u svakodnevnom DevOps/SRE radu, pa im ova knjiga ne posvećuje
  posebnu definiciju, ali se stalno pominju od ovog poglavlja nadalje.

Ovih pet-šest termina se vraćaju u gotovo svakom poglavlju koje sledi.
Dodatak B na kraju knjige drži njihove pune definicije zajedno sa
tridesetak specijalizovanijih pojmova (kardinalnost, tail sampling,
burn-rate...) — svaki od njih uvodimo tek u poglavlju gde prvi put
postane bitan za priču, ne pre.

## 1.1 Pitanje na koje ovo poglavlje odgovara

Zašto uopšte praviti razliku između te dve reči, kad naizgled rade istu stvar —
obe kažu "sistem ima problem"? I zašto je ta razlika dovoljno bitna da bude prvo
poglavlje ove knjige, pre bilo kog konkretnog alata?

Zato što odgovor menja **šta gradiš prvo**. Ako je observability samo
monitoring sa modernijim imenom, onda je dovoljno postaviti dashboard-e sa
metrikama i par alarma, i posao je gotov. Ako observability znači nešto
strukturno drugačije — sposobnost da postaviš pitanje koje juče nisi znao da
ćeš morati da postaviš — onda instrumentacija mora od prvog dana da nosi
kontekst dovoljno bogat da to pitanje bude odgovorljivo, čak i kad ne znaš
unapred koje će to pitanje biti. Ta razlika u pristupu se ne vidi dok sistem
radi normalno. Vidi se tačno jednom, u jednom konkretnom incidentu, kad je
prekasno da se doda.

## 1.2 Kako se ta razlika stvarno oseti — jedan konkretan incident

U implementaciji koju knjiga prati, postoji zadatak koji svi u timu neformalno
zovu "cacher": zakazani posao koji periodično povlači podatke iz jednog
unutrašnjeg servisa i puni njima keš sloj koji čita nekoliko drugih aplikacija.
Zadatak ima potpuno standardan monitoring: alarm koji se javlja ako proces
padne, alarm ako potraje duže od očekivanog, alarm ako izađe sa greškom.

Jednog jutra, taj zadatak je radio potpuno "ispravno" po svakoj metrici koju je
monitoring pratio: pokrenuo se na vreme, završio se na vreme, izašao je sa
kodom 0, nijedan alarm se nije oglasio. A ipak, downstream aplikacije su
počele da vraćaju prazne ili zastarele podatke korisnicima. Uzrok: upstream
servis je te noći vratio prazan, ali validan HTTP 200 odgovor umesto očekivane
liste zapisa — verovatno posledica sopstvenog, kratkog internog problema koji
se sam rešio pre nego što je iko stigao da ga istraži. "Cacher" je taj prazan
odgovor primio, protumačio kao legitiman rezultat, upisao ga u keš, i mirno
prijavio uspeh. Sa stanovišta procesa, ništa nije pošlo po zlu — pukla je samo
pretpostavka da je "izašao bez greške" isto što i "uradio ono što treba".

Ovo je udžbenički primer onoga što se u literaturi zove **known unknown protiv
unknown unknown**. Monitoring alarm za "cacher je pao" je *known unknown* —
tim je unapred znao da proces može da padne, pa je za to postavio senzor,
tačno kao brzinomer u kokpitu. Ali "upstream servis vraća prazan-ali-validan
odgovor umesto greške" nije bilo nešto što je iko unapred zamislio dovoljno
precizno da napravi poseban alarm za to. To je *unknown unknown* — kategorija
kvara koja se ne otkriva boljim alarmima, jer bi za nju trebalo unapred znati
da tačno taj alarm treba postaviti.

Ono što je incident na kraju rešilo nije bio novi alarm — nego trag
(trace) koji je već postojao za taj posao, sa atributom koji je beležio broj
zapisa vraćenih iz upstream poziva. Niko nije gledao taj atribut aktivno tog
jutra; posle prijave korisnika o praznim podacima, neko je otvorio taj isti
trag i za par minuta video: `records_returned=0`, na dan kad je prosek preko
600. Podatak je već postojao. Samo ga niko nije morao unapred da zna da će mu
trebati — instrumentacija ga je snimila "za svaki slučaj", isto kao što crna
kutija snima svaki parametar leta bez obzira da li će se ikad koristiti.

Posle ovog incidenta, tim **nije** dodao novi alarm tipa "javi ako
`records_returned` padne ispod X" — to bi bio prirodan, ali pogrešan refleks,
jer bi rešio baš ovaj specifičan scenario, a sledeći unknown unknown bi opet
prošao neopaženo. Umesto toga, obogaćen je skup atributa koji svaki
sličan pull-zadatak automatski beleži (veličina odgovora, broj zapisa, da li je
odgovor prazan) — ne kao alarm, nego kao *dostupan kontekst* za sledeće pitanje
koje još niko nije postavio. Taj princip — bogatiti podatke pre nego što znaš
pitanje, umesto dodavati alarme posle svakog incidenta — provlači se kroz celu
knjigu i vraća se eksplicitno u Poglavlju 5 (semantika atributa) i Poglavlju 12
(sampling — jer trag mora i da preživi do trenutka kad neko poželi da ga
pogleda).

## 1.3 Analitički deo — odakle dolazi ova razlika, i zašto tri stuba nisu dovoljna

### Known unknowns i unknown unknowns nisu marketinški izraz

Razlikovanje monitoring/observability preko known-unknown vs. unknown-unknown
okvira nije izum dobavljača alata — potiče iz šire literature o upravljanju
rizikom, a u kontekst softverskih sistema ga je najsistematičnije uveo tim iz
Honeycomb-a (Charity Majors i saradnici), koji koriste sličnu ilustraciju:
monitoring vodi računa koliko tanjira poručiti za večeru, dok je observability
ono što obezbeđuje da večera uspe bez obzira šta se te noći dogodi u kuhinji.
Poenta te analogije je ista kao i crne kutije s početka poglavlja: monitoring
je unapred pripremljen odgovor na unapred zamišljeno pitanje, observability je
kapacitet da se odgovori na pitanje koje niko nije unapred zamislio.

Ovo nije čisto teorijska razlika. Ima direktnu, merljivu posledicu: sistem koji
ima odličan monitoring, ali slabu observability, biće brz u otkrivanju
*poznatih* kategorija kvara (spor odgovor, visok CPU, pad procesa), a spor —
ili potpuno slep — na *nove* kategorije kvara, čak i kad su te nove kategorije
često upravo one koje najviše štete rade, jer se prvi put dešavaju bez ijedne
odbrane pripremljene za njih.

### RED, USE i Zlatni signali — odlična polazna tačka, ne kompletan odgovor

Kad se govori o "šta meriti", tri metodologije se stalno pominju:

- **USE** (Utilization, Saturation, Errors) — Brendan Gregg-ov okvir za
  infrastrukturne resurse: za svaki resurs (CPU, disk, mreža) prati se
  iskorišćenost, zasićenost i greške.
- **RED** (Rate, Errors, Duration) — okvir koji je 2015. formulisao Tom Wilkie
  (danas u Grafana Labs), fokusiran na servise, ne resurse: za svaki servis
  prati se stopa zahteva, stopa grešaka i trajanje.
- **Četiri zlatna signala** iz Google-ove SRE knjige — latencija, promet,
  greške, zasićenost — koncepcijski most između prethodna dva, formulisan
  nešto ranije i šire citiran.

Sve tri metodologije rešavaju isti problem: koje **metrike** unapred definisati
tako da najveći broj čestih kvarova bude pokriven sa malim brojem signala. To
ih čini odličnim za **monitoring** sloj — RED metod je, na primer, direktno
primenjiv na svaki servis u sistemu koji ova knjiga prati, i koristi se tačno
tako u Poglavlju 5. Ali sve tri metodologije dele istu strukturnu granicu:
rade sa unapred definisanim, agregiranim brojevima. Nijedna od njih po
definiciji ne ostavlja prostor za pitanje "dobro, `error_rate` je porastao —
ali *za koje* zahteve, sa *kojim* parametrima, od *kog* klijenta?" — to pitanje
zahteva da postoji sirovi, pojedinačni događaj (trag, strukturiran log red) sa
dovoljno atributa da se po njemu filtrira, ne samo agregat koji kaže da je
nešto poraslo.

Zato dobra arhitektura observability-ja ne bira između RED/USE metrika i
observability-ja "umesto" njih — koristi ih zajedno, na dva različita nivoa:
agregirane metrike (RED/USE) kao **jeftin, brz signal da nešto nije u redu**
("error_rate je porastao"), i bogato instrumentirane tragove i logove kao
**mehanizam da se to pitanje odgovori** ("koji tačno zahtevi, i zašto"). Prvi
sloj kaže *da* postoji problem. Drugi sloj kaže *šta* je problem. Sistem koji
ima samo prvi sloj zna da mu gori kuhinja, ali ne zna gde je vatrogasni aparat.

### Zašto "tri stuba" nije definicija, nego popis alata

Uobičajena definicija observability-ja preko "tri stuba" (metrike, logovi,
tragovi) je korisna kao popis *alata*, ali opasna ako se pročita kao
*definicija* — jer sistem može da ima sva tri alata instalirana, a i dalje da
bude čisti monitoring sistem u praksi, ako se ta tri alata koriste samo za
unapred zamišljena pitanja. Instrumentacija koja hvata `records_returned` u
"cacher" primeru gore nije bila deo nijednog unapred definisanog dashboard-a
kad se incident dogodio — postojala je jer je neko ranije odlučio da vredi
snimiti to polje "za svaki slučaj". Ta odluka, ne postojanje trag-alata samog
po sebi, jeste ono što je incident na kraju rešilo za par minuta umesto par
dana pretrage logova.

Vredi dodati i kratku napomenu o obimu ove liste: neki dobavljači —
uključujući Grafana Cloud, platformu koju ova knjiga koristi — u poslednje
vreme dodaju i **continuous profiling** (Grafana Pyroscope) kao svojevrstan
četvrti signal, uz metrike, logove i tragove. Profiling odgovara na pitanje
koje nijedan od tri stuba ne pokriva direktno: *gde tačno u kodu* proces
troši CPU ili memoriju, na nivou funkcije, bez potrebe da se unapred zna koju
funkciju posmatrati. Ova knjiga ga ne obrađuje kao posebnu temu —
implementacija koju prati nije imala profiling kao aktivan deo pipeline-a u
periodu koji knjiga opisuje — ali vredi ga imati na radaru kao prirodno
proširenje istog principa: što više dimenzija sistem beleži unapred, "za
svaki slučaj", to je veća šansa da odgovoriš na pitanje koje juče nisi znao
da ćeš morati da postaviš.

## 1.4 Skupljena pravila iz ovog poglavlja

- Monitoring odgovara na pitanja koja si postavio unapred; observability
  odgovara na pitanja koja postaviš posle. Oba su ti potrebna — ne biraj
  jedno umesto drugog.
- RED/USE/Zlatni signali su odličan recept za *monitoring* sloj (jeftin, brz
  signal da nešto nije u redu). Ne pokušavaj da ih proširiš da rade posao
  observability-ja — za to ti treba sirov, atributima bogat događaj.
- Kad instrumentiraš nešto novo, ne pitaj samo "koji alarm mi ovde treba" —
  pitaj i "koji atribut bih poželeo da imam kad se sledeći put nešto pokvari
  na način koji danas ne mogu da zamislim".
- "Uspešan izlaz" (exit code 0, HTTP 200) nije isto što i "uradio je pravu
  stvar". Za svaki pull/push zadatak, razmisli da li postoji tiha varijanta
  uspeha koja je zapravo kvar.
- Posedovanje sva tri "stuba" (metrike, logovi, tragovi) ne garantuje
  observability samo po sebi — garantuje ga navika da se ti alati koriste i za
  pitanja koja nisi unapred predvideo.

## 1.5 Vežba za čitaoca

Pronađi jedan zakazan zadatak ili batch posao u svom sistemu koji trenutno ima
monitoring samo na nivou "da li je pao / da li je potrajao predugo". Postavi
sebi pitanje: postoji li način da taj zadatak "uspe" po monitoring definiciji,
a da ipak uradi pogrešnu stvar (vrati prazan rezultat, obradi 0 zapisa, upiše
zastarele podatke)? Ako postoji — to je tvoj kandidat za dodavanje atributa
"za svaki slučaj", pre nego što ti zatreba, ne posle.

---

### Izvori korišćeni u analitičkom delu

- [Observability - A 3-Year Retrospective — Honeycomb](https://www.honeycomb.io/blog/observability-a-3-year-retrospective)
- [Monitoring and Observability — Honeycomb blog / docs](https://www.honeycomb.io/blog)
- [The RED Method: How to Instrument Your Services — Grafana Labs](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/)
- [The Four Golden Signals — Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The USE Method — Brendan Gregg](https://www.brendangregg.com/usemethod.html)
