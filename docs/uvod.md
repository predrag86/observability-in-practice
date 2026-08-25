# Uvod

Većina literature o observability-ju objašnjava koncepte — tri stuba (metrike,
logovi, trejsovi), RED/USE metodologije, šta je OpenTelemetry. To je neophodno,
ali nije dovoljno: pravi problemi počinju posle instalacije agenta, kada Mimir
ne promoviše atribute u lejble koje očekuješ, kada kardinalnost pojede budžet
za jedan vikend, kada alarm koji izgleda ispravno ćuti baš onda kada je
najpotrebniji, ili kada moraš da objasniš auditoru zašto email korisnika
završava u trejsu.

Ova knjiga polazi od druge tačke: od stvarnog, višemesečnog uvođenja
observability-ja **na nivou cele firme**, ne jednog demo-servisa u jednom
repozitorijumu. Implementacija koju knjiga prati kao svoju centralnu studiju
slučaja pokriva desetine backend i frontend aplikacija (APM — praćenje
performansi aplikacija), mrežnu infrastrukturu, upravljane baze podataka,
samostalno upravljan distribuirani compute klaster (tipa Dremio), autentikacioni
sloj, i flotu batch/ETL zadataka koja se meri desetinama nezavisnih porodica
poslova — sve na AWS-u.

Poseban deo priče, dovoljno drugačiji da dobije sopstveno poglavlje, jeste
onboardovanje servisa koji **nije** na AWS-u niti je hostovan interno: nezavisnog
SaaS data-warehouse rešenja (tipa Snowflake). Taj servis nema host na koji se
može instalirati agent, nema proces koji se može uputiti da izveze telemetriju,
nema mrežu u koju infrastrukturni tim ima uvid — sve što se o njemu zna dolazi
iz sistemskih pregleda koje sam servis dobrovoljno izlaže, upitanih spolja, na
raspored, sa kašnjenjem koje je strukturno i ne može se ukinuti. Poglavlje 24 tu
priču obrađuje u punoj dubini: kako se prikuplja telemetrija servisa nad kojim
nemaš nikakvu operativnu kontrolu, i šta to menja u odnosu na sve ostalo u
knjizi. Ta razlika — instrumentuješ ono što kontrolišeš, posmatraš spolja ono
što ne kontrolišeš — provlači se kroz celu knjigu kao stalna tema, i vraća se
više puta i pre Poglavlja 24 (kod baza, kod pull-obrazaca, kod sintetičkog
praćenja).

## Odakle dolazi materijal

Svaki tehnički primer u ovoj knjizi — arhitektura, PromQL upit, konfiguracioni
isečak, incident, odluka i njena analiza — potiče iz stvarne implementacije,
dokumentovane onako kako je nastajala: sa greškama, ćorsokacima, revizijama i
"zašto smo ovo prvo probali, pa odbacili" beleškama. Ništa u knjizi nije
laboratorijski primer napravljen da lepo izgleda u knjizi; sve je prošlo kroz
produkciju.

Zbog toga je pre objavljivanja urađen jedan eksplicitan korak: **uklanjanje
svakog identifikujućeg detalja.** Naziv firme, imena ljudi, interni domeni,
ID-jevi AWS resursa, adrese, imena internih repozitorijuma i aplikacija — sve je
ili uklonjeno ili zamenjeno generičkim, fiktivnim nazivima. Ono što ostaje su
**obrasci i odluke**, ne to čiji su. Gde god je bilo moguće, zadržani su realni
brojevi (cene, procenti, vremena) jer bez njih polovina lekcija u knjizi gubi
smisao — ali nikad na način koji bi otkrio o kojoj se firmi radi.

## Kome je ova knjiga namenjena

Pre svega DevOps/SRE inženjerima koji grade ili nasleđuju observability sistem
i žele da vide kako on izgleda kad prestane da bude prototip. Zatim backend i
frontend programerima koji uvode instrumentaciju u sopstveni servis i žele da
znaju šta je zaista potrebno, a šta je kult-teretni ritual. I na kraju tim
liderima koji treba da donesu — i da opravdaju pred budžetom — odluku između
Grafana Cloud-a, konkurentskih SaaS platformi i self-hosted rešenja; to pitanje
je toliko česta prva prepreka da mu je posvećeno celo sledeće poglavlje, pre
nego što knjiga uopšte uđe u tehničke detalje.

Knjiga pretpostavlja da čitalac već radi u DevOps/SRE ili srodnoj
infrastrukturnoj ulozi i da mu pojmovi kao što su kontejneri, CI/CD, cloud
provajder (AWS ili sličan) i osnovni Linux rad nisu strani. Poznavanje
observability terminologije (metrike, logovi, trejsovi, dashboard, alarm) na
uvodnom nivou je poželjno, ali nije preduslov — Poglavlje 1 gradi tu
terminologiju od nule. Ono što knjiga NE uči jeste DevOps ili SRE od početka:
ako su vam pojmovi poput CI/CD pipeline-a, kontejnerizacije ili
infrastrukture kao koda potpuno novi, bolje je prvo krenuti od uvodnog
DevOps/SRE materijala, pa se vratiti ovde.

## Kako je knjiga organizovana

Svako poglavlje sledi isti obrazac, namerno ponovljen kroz celu knjigu da bi
čitanje postalo predvidljivo: otvara se jednom paralelom iz stvarnog života koja
uvodi mehanizam o kome je reč, prelazi na **praktičan deo** — kako je tačno
urađeno u implementaciji koju knjiga prati — pa na **analitički deo**, gde se to
rešenje poredi sa onim što industrija naziva "standardnim", eksplicitno imenujući
gde je implementacija odstupila i zašto, i šta bi se dogodilo da nije. Poglavlje
se zatvara vraćanjem na uvodnu paralelu, kratkom listom pravila i vežbom koju
čitalac može odmah da primeni na sopstveni sistem.

Ovaj format nije stilska odluka radi razonode — on je odgovor na ono što čini
većinu observability literature slabom: opisuje se *šta* je urađeno, retko *zašto
baš tako*, a gotovo nikad *šta bi se pokvarilo da je urađeno drugačije*. Ova
knjiga pokušava da svako poglavlje ostavi baš to poslednje pitanje odgovoreno.

Krenimo.
