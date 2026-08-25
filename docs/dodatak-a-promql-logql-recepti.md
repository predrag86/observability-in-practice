# Dodatak A — PromQL/LogQL recepti

Ovo je zbirka konkretnih upita na koje se knjiga oslanja, na jednom mestu.
Svaki recept prati isti oblik: problem koji rešava, upit koji izgleda
ispravno ali laže, upit koji je stvarno ispravan, i jedna rečenica zašto
je razlika bitna. Namenjeno je da se otvori tokom istrage, ne da se čita
od početka do kraja.

## 1. Zdravlje zakazanog (batch) zadatka — nikad trenutna vrednost

Zadaci koji se pokreću po rasporedu (ne servisi koji stalno primaju
saobraćaj) između pokretanja "zastare" — njihove serije prirodno nestaju
iz najnovijeg uzorka. Ovo laže — izgleda kao da su 3 od 8 porodica
zadataka mrtve:

```promql
count by (job) (batch_step_seconds_count)
```

Ispravno meri da li je porodica RADILA u poslednjih 24h, ne da li
postoji baš u ovom trenutku:

```promql
count by (job) (
  increase(batch_step_seconds_count[24h]) > 0
)
```

**Zašto:** trenutna (instant) vrednost ne razlikuje "u pauzi između dva
pokretanja" od "više nije instrumentiran". Za bilo šta zakazano, koristi
`increase([24h])` ili `max_over_time([7d])`, nikad goli trenutni upit.

## 2. Prazna metrika obično znači pogrešno ime, ne odsustvo instrumentacije

Ovo vraća NIŠTA — zaključak "ovo nije instrumentirano" je preuranjen:

```promql
dremio_memory_heap_bytes
```

Stvarno ime metrike, po OTel semantičkoj konvenciji za JVM memoriju:

```promql
jvm_memory_used_bytes{service_name="dremio", area="heap"}
```

**Zašto:** pre nego što se zaključi da nešto nije instrumentirano, pročitaj
izraz iz postojećeg pravila alarmiranja koje navodno prati tu istu stvar
(`/api/v1/provisioning/alert-rules`) i izvrši TAJ izraz. Ako alarm postoji
i radi, metrika po definiciji postoji — samo pod drugim imenom.

## 3. `or` između dva agregata sa istim (praznim) skupom oznaka tiho zadržava samo levu stranu

Oba operanda ovde agregiraju SVE oznake do praznog skupa, pa se desna
strana poklapa sa levom i `or` zadržava samo levu — druga vrednost je
TIHO odbačena, ne sabrana ni prikazana:

```promql
count(count by (id) (target_info))
  or
count(count by (id) (max_over_time(target_info[7d])))
```

Ispravno je selektor koji zadržava `__name__` (i time razlikuje serije),
ili dva odvojena upita:

```promql
{__name__=~"target_info"}
```

**Zašto:** `or` u PromQL-u nije "prikaži oba" — ako se skupovi oznaka
poklope, desna strana se tiho odbacuje. Nikad ne grupiši različita
skalarna merenja preko `or` bez provere da im se skupovi oznaka zaista
razlikuju.

## 4. Kardinalnost po poslu (job) je tačkasta vrednost — batch porodice je lažu za hiljade serija

Ovo laže ako se izvrši u pogrešnom trenutku — batch porodica u pauzi
između pokretanja može pokazati skoro nula "živih" serija:

```promql
count by (job) ({job="neka_batch_porodica"})
```

Ispravno za uporedivu brojku:

```promql
max_over_time(
  count by (job) ({__name__=~".+"})[24h:2h]
)
```

Ispravno za merenje "churn"-a (koliko RAZLIČITIH identiteta zadataka se
smenilo, ne koliko ih postoji odjednom):

```promql
count by (job) (
  count_over_time(target_info[7d])
)
```

**Zašto:** `max_over_time` se ne može direktno primeniti preko selektora
sa više imena metrika — briše `__name__` i baca grešku "vector cannot
contain metrics with the same labelset". Podupit oblik (`[24h:2h]`) je
rešenje.

## 5. Grub korak na promenljivom (bursty) gauge-u vraća sve nule

30-dnevni opseg sa korakom od 6h na promenljivoj metrici vraća nule na
svakoj tački — izgleda kao "ništa se ne dešava":

```promql
grafanacloud_logs_discarded_bytes_per_second
```

Ispravno je uzeti i prosek i maksimum preko finijeg podupita:

```promql
avg_over_time(
  grafanacloud_logs_discarded_bytes_per_second[30d:5m]
)
max_over_time(
  grafanacloud_logs_discarded_bytes_per_second[30d:5m]
)
```

**Zašto:** nikad ne zaključuj "nema odbacivanja" iz uzorkovanog opsega sa
grubim korakom na promenljivom gauge-u — kratak, oštar skok se jednostavno
preskoči između uzoraka.

## 6. Brojač koji se lenjo stvara i nestaje pri restartu

```promql
otelcol_exporter_send_failed_metric_points_total
```

**Zašto:** ovaj tip brojača se stvara TEK pri prvom neuspehu, i nestaje
kad se zadatak/replika restartuje. "Serija je nestala" i "ništa ne
otkazuje" izgledaju identično na dashboard-u. Ne čitaj odsustvo serije
kao dokaz zdravlja — proveri i vreme poslednjeg restarta zadatka.

## 7. `deriv()` preko JVM heap-a meri fazu garbage collector-a, ne curenje

7-dnevni `deriv()` na testerastom (sawtooth) obrascu memorije zavisi
isključivo od toga GDE u ciklusu prozor počinje — ovo laže:

```promql
deriv(jvm_memory_used_bytes{area="heap"}[7d])
```

**Zašto:** heap koji raste pa se čisti garbage collector-om (testerast
obrazac) NIJE curenje samo zato što jedan prozor pokazuje rastući trend.
Prava provera: da li POD (donja tačka, posle svakog GC ciklusa) raste
kroz VIŠE uzastopnih ciklusa — jedan prozor nikad nije dovoljan.

## 8. "Da li išta upituje ovu metriku" zahteva kontrolni upit

Log stream aktivnosti upita (koji beleži KO je pitao, ne ŠTA je pitao) ne
može da odgovori na pitanje "da li se ova metrika koristi" pretragom
teksta upita — jer tekst upita jednostavno nije tu.

**Ispravna procedura:** jedini pouzdan način je obilazak JSON definicija
svih dashboard-a (`panels[].targets[]`, rekurzivno kroz `row` panele) plus
sva pravila alarmiranja (`/api/v1/provisioning/alert-rules`), tražeći
doslovno ime metrike. I uvek izvrši KONTROLNI upit — potraži isti obrazac
za metriku za koju SIGURNO znaš da se koristi. Ako i ona vrati "nula
pogodaka", izvor ne ume da odgovori na ovo pitanje uopšte, i negativan
rezultat ne znači ništa.

## 9. Provera da li signal uopšte prolazi kroz centralni prolaz (gateway)

Da li prolaz uopšte prima OTLP od pošiljaoca X u poslednjih 15 min:

```promql
sum(rate(
  otelcol_receiver_accepted_spans_total{service_name="X"}[15m]
))
```

Da li prolaz USPEŠNO izvozi dalje (ne samo prima):

```promql
sum(rate(otelcol_exporter_sent_spans_total[15m]))
  /
sum(rate(otelcol_receiver_accepted_spans_total[15m]))
```

**Zašto:** "stiglo je do prolaza" i "prolaz je to uspešno prosledio dalje"
su dva različita pitanja. Odnos manji od 1 znači da se nešto gubi unutar
prolaza (uzorkovanje, red za slanje koji je pun, greška izvoza) — proveri
`otelcol_exporter_send_failed_*` pre nego što posumnjaš na pošiljaoca.

## 10. Otkrivanje pravog imena metrike posle OTLP→Prometheus prevoda

OTel metrika sa jedinicom u definiciji dobija CamelCase sufiks kad stigne
u Prometheus/Mimir — jedinica postaje deo IMENA metrike, ne oznaka:

```text
OTel:       container.memory.utilized   (jedinica: MiB)
Prometheus: container_memory_utilized_MiB

OTel:       neka.metrika.bez.jedinice
Prometheus: neka_metrika_bez_jedinice_None
```

**Zašto:** kad upit na "očigledno" ime metrike ne vrati ništa, prvo
proveri da li je originalna OTel definicija imala jedinicu — ona se
tiho pretvara u sufiks (`_MiB`, `_Bytes`, `_None` za nedostajuću
jedinicu), i to je najčešći razlog "prazne metrike" koji nema veze sa
Receptom #2 iznad.

## 11. Kardinalnost po atributu — pre nego što ga dodaš u produkciju

Koliko RAZLIČITIH vrednosti bi ovaj atribut doneo, PRE nego što ga
uključiš — proveri na uzorku/stejdžingu, nikad direktno u produkciji:

```promql
count(count by (predloženi_atribut) (neka_metrika))
```

**Zašto:** ovo je upit koji se izvršava PRE odluke o dodavanju nove
oznake, ne posle — svaka nova vrednost atributa je nova vremenska serija,
i trošak se plaća unapred, po broju jedinstvenih kombinacija, ne po broju
merenja.

## 12. LogQL — da li logovi jedne porodice uopšte stižu, ispravno parsirani

```logql
{service_name="X"}
  | logfmt
  | __error__=""
```

**Zašto:** filter `__error__=""` isključuje redove koje LogQL nije uspeo
da parsira po zadatoj šemi (`logfmt` u ovom primeru) — bez njega, redovi
koji ne prate očekivan format tiho ostaju u rezultatu i mogu izgledati
kao da je sve u redu dok zapravo parsiranje pada na svakom drugom redu.

---

*Sve gore navedene zamke potiču iz stvarnih, dokumentovanih grešaka
napravljenih tokom rada na sistemu koji je osnova ove knjige — svaka je u
nekom trenutku dovela do pogrešnog zaključka pre nego što je uhvaćena i
zapisana kao pravilo.*
