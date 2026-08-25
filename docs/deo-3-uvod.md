# Deo III — Obrada, kardinalnost i troškovi

## Pre nego što krenemo: isti problem, tri različita ugla

Deo II je odgovorio na pitanje kako se telemetrija prikuplja iz svakog
sloja sistema — gateway, instrumentacija, sidecar, pull-obrasci, RUM,
sintetičko praćenje. Ovaj deo počinje tačno tamo gde se Deo II završava:
kolektor već drži signal u ruci, pre nego što bilo šta od toga ode u
cloud i počne da se plaća. Tri poglavlja koja slede nisu tri odvojena
saveta — to je **isti problem** (kontrola troška bez gubitka signala)
posmatran iz tri različita ugla:

- **Poglavlje 10** pita da li redosled obrade unutar pipeline-a uopšte
  ima značaja, ili je samo stilski izbor — i pokazuje zašto pogrešan
  redosled može da poskupi ili osiromaši signal pre nego što iko primeti.
- **Poglavlje 11** uzima opštiji pogled: kako kardinalnost — broj
  jedinstvenih kombinacija lejbli — prirodno raste iznad budžeta, tiho i
  postepeno, dok jednog dana ne stigne račun koji iznenadi svakoga iako
  je rastao mesecima.
- **Poglavlje 12** spušta isto pitanje na jedan konkretan signal —
  trejsove — i poredi dva suprotna mesta gde se odluka o samplovanju
  može doneti: na serveru, gde se vidi ceo trejs pre odluke, ili na
  kolektoru, gde se odlučuje raspolažući samo delom slike.

Zajednička nit kroz sva tri poglavlja: cena telemetrije nije fiksni
trošak koji se prihvati jednom — to je promenljiva koju arhitektura
pipeline-a, obrazac rasta lejbli i strategija samplovanja zajedno drže
pod kontrolom, ili ne drže. Deo IV, koji sledi, pretpostavlja da je ta
kontrola već uspostavljena, i prelazi na ono što se dešava kad
obrađen, jeftin signal treba da probudi čoveka.
