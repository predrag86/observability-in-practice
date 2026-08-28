# Prevodilački rečnik (SR → EN)

Interni fajl, nije deo objavljene knjige (`docs_dir` je `docs/`, ovaj fajl je
van njega, pa ga MkDocs ne obrađuje). Svrha: da svaki naredni deo knjige
prevodimo istim terminima, umesto da svaki prevod bira sopstvenu varijantu.

Dopunjuje se posle svakog prevedenog dela. Kad prevodite novi deo i naiđete
na termin koji nije ovde, dodajte ga pre nego što nastavite — ne birajte
ad-hoc prevod za termin koji će se ponoviti u kasnijim poglavljima.

## Opšti pojmovi

| Srpski | Engleski | Napomena |
| --- | --- | --- |
| observability | observability | ne prevodi se |
| monitoring | monitoring | ne prevodi se |
| incident | incident | |
| trag / trejs | trace | "trag" i "trejs" oba znače trace u originalu |
| dashboard | dashboard | ne prevodi se |
| alarm | alert | "alarm" (SR) → "alert" (EN), ne "alarm" |
| kardinalnost | cardinality | |
| semantičke konvencije | semantic conventions | |
| resursni atributi | resource attributes | |
| gateway | gateway | ne prevodi se |
| self-hosted | self-hosted | ne prevodi se |
| upravljana platforma | managed platform | |
| instrumentacija | instrumentation | |
| rečnik pojmova | glossary | (u Dodacima) |
| known unknown / unknown unknown | known unknown / unknown unknown | ne prevodi se, standardan izraz iz literature |
| zero-code (instrumentacija) | zero-code | ne prevodi se |
| auto-instrumentacioni agent | auto-instrumentation agent | |
| SDK setup | SDK setup | ne prevodi se |
| entrypoint shim | entrypoint shim | ne prevodi se |
| crna kutija | black box | |
| vozni park / flota | fleet | |
| commit cena | commit pricing | |
| FTE | FTE | ne prevodi se (full-time equivalent/employee) |
| obim | scale / volume | zavisi od konteksta — "obim infrastrukture" = scale, "obim podataka" = volume |
| zahtev | request | |
| zapremina | volume | |
| tier | tier | ne prevodi se |
| zadatak / posao | job | u kontekstu batch/scheduled zadataka |
| rezidencija podataka | data residency | |
| pull-obrazac | pull-based pattern | |
| sidecar | sidecar | ne prevodi se |
| sampling | sampling | ne prevodi se |
| SLO / budžet greške | SLO / error budget | |
| runbook | runbook | ne prevodi se |
| postmortem | postmortem | ne prevodi se |
| usklađenost | compliance | |
| zrelost (programa) | maturity | |
| fazni rollout | phased rollout | |
| bela kutija | white box | uparen termin sa "crna kutija" (black box), Poglavlje 18 |
| izvršni čvor / koordinacioni čvor | executor node / coordinator node | standardna Dremio arhitektura, Poglavlje 19 |
| ravan (posmatranja) | plane | u kontekstu "ravan posmatranja" → "observation plane" (Poglavlje 22); ne mešati sa "spoljašnja/unutrašnja ravan" iz Poglavlja 7, gde je "ravan" prevedeno kao "layer" u drugom kontekstu |
| radna jedinica (generički termin za Snowflake warehouse) | compute unit | namerno generičan termin, Poglavlje 24 |
| napad povezivanjem | linkage attack | standardan termin iz privacy-engineering literature, Poglavlje 25 |
| izvedeni pseudonim / ključem-zaštićena heš funkcija | derived pseudonym / keyed hash function | Poglavlje 25, prati NIST/EDPB terminologiju |
| NA MESTU / DELIMIČNO / PRAZNINA (tabela usklađenosti) | IN PLACE / PARTIAL / GAP | Poglavlje 26 |
| časna pomena (backlog kategorija) | honorable mention | Poglavlje 27 |
| bočni kolektor | sidecar collector | Poglavlje 29 |
| estate (celokupan inventar komponenti programa) | estate | ostaje kao engleska pozajmljenica, već tako korišćena u originalu, Poglavlje 30 |
| obrazac (arhitekturni) | pattern | npr. "gateway obrazac" → "gateway pattern", "agent-to-gateway obrazac" → "agent-to-gateway pattern" |
| task definicija / task lifecycle (AWS ECS) | task definition / task lifecycle | ostaje kao standardan AWS ECS termin, ne prevodi se slobodno |
| posmatrač (u smislu watcher procesa) | watcher | dosledno kroz Poglavlje 7 (doctor/pull-pattern analogija) |
| spoljašnja ravan / unutrašnja ravan | external layer / internal layer | u kontekstu pull-obrazaca (Poglavlje 7) |
| RUM za siromašne | poor man's RUM | idiomatski prevod, Poglavlje 9 |
| RUM | RUM | ne prevodi se |
| PII | PII | ne prevodi se |
| Core Web Vitals | Core Web Vitals | ne prevodi se |

## Nazivi delova/poglavlja (za buduće interne linkove)

| Srpski fajl | Engleski fajl |
| --- | --- |
| `index.md` | `index.en.md` |
| `uvod.md` | `uvod.en.md` |
| `deo-1-uvod.md` | `deo-1-uvod.en.md` |
| `poglavlje-01-sta-je-observability.md` | `poglavlje-01-sta-je-observability.en.md` |
| `poglavlje-02-opentelemetry.md` | `poglavlje-02-opentelemetry.en.md` |
| `poglavlje-03-izbor-platforme.md` | `poglavlje-03-izbor-platforme.en.md` |
| `deo-2-uvod.md` | `deo-2-uvod.en.md` |
| `poglavlje-04-gateway.md` | `poglavlje-04-gateway.en.md` |
| `poglavlje-05-instrumentacija.md` | `poglavlje-05-instrumentacija.en.md` |
| `poglavlje-06-sidecar.md` | `poglavlje-06-sidecar.en.md` |
| `poglavlje-07-pull-obrasci.md` | `poglavlje-07-pull-obrasci.en.md` |
| `poglavlje-08-frontend-rum.md` | `poglavlje-08-frontend-rum.en.md` |
| `poglavlje-09-sinteticko-pracenje.md` | `poglavlje-09-sinteticko-pracenje.en.md` |
| `deo-3-uvod.md` | `deo-3-uvod.en.md` |
| `poglavlje-10-anatomija-pipeline.md` | `poglavlje-10-anatomija-pipeline.en.md` |
| `poglavlje-11-kardinalnost-cena.md` | `poglavlje-11-kardinalnost-cena.en.md` |
| `poglavlje-12-sampling-trejsova.md` | `poglavlje-12-sampling-trejsova.en.md` |
| `deo-4-uvod.md` | `deo-4-uvod.en.md` |
| `poglavlje-13-arhitektura-alarmiranja.md` | `poglavlje-13-arhitektura-alarmiranja.en.md` |
| `poglavlje-14-kad-alarm-cuti.md` | `poglavlje-14-kad-alarm-cuti.en.md` |
| `poglavlje-15-slo-budzet-greske.md` | `poglavlje-15-slo-budzet-greske.en.md` |
| `poglavlje-16-runbook-ovi.md` | `poglavlje-16-runbook-ovi.en.md` |
| `poglavlje-17-postmortem-kultura.md` | `poglavlje-17-postmortem-kultura.en.md` |
| `deo-5-uvod.md` | `deo-5-uvod.en.md` |
| `poglavlje-18-baze-podataka.md` | `poglavlje-18-baze-podataka.en.md` |
| `poglavlje-19-samostalni-klaster.md` | `poglavlje-19-samostalni-klaster.en.md` |
| `poglavlje-20-autentikacija-iam.md` | `poglavlje-20-autentikacija-iam.en.md` |
| `poglavlje-21-hostovi-serveri.md` | `poglavlje-21-hostovi-serveri.en.md` |
| `poglavlje-22-mreza-ravan-posmatranja.md` | `poglavlje-22-mreza-ravan-posmatranja.en.md` |
| `poglavlje-23-batch-etl-flota.md` | `poglavlje-23-batch-etl-flota.en.md` |
| `poglavlje-24-snowflake-servis-koji-nije-nas.md` | `poglavlje-24-snowflake-servis-koji-nije-nas.en.md` |
| `deo-6-uvod.md` | `deo-6-uvod.en.md` |
| `poglavlje-25-privatnost-telemetriji.md` | `poglavlje-25-privatnost-telemetriji.en.md` |
| `poglavlje-26-soc2-kontrola.md` | `poglavlje-26-soc2-kontrola.en.md` |
| `poglavlje-27-prioritizacija.md` | `poglavlje-27-prioritizacija.en.md` |
| `poglavlje-28-ai-asistirana-observability.md` | `poglavlje-28-ai-asistirana-observability.en.md` |
| `deo-7-uvod.md` | `deo-7-uvod.en.md` |
| `poglavlje-29-fazni-rollout.md` | `poglavlje-29-fazni-rollout.en.md` |
| `poglavlje-30-merenje-zrelosti.md` | `poglavlje-30-merenje-zrelosti.en.md` |
| `poglavlje-31-zakljucak.md` | `poglavlje-31-zakljucak.en.md` |
| `dodatak-a-promql-logql-recepti.md` | `dodatak-a-promql-logql-recepti.en.md` |
| `dodatak-b-recnik-pojmova.md` | `dodatak-b-recnik-pojmova.en.md` |
| `dodatak-c-checklist-onboarding.md` | `dodatak-c-checklist-onboarding.en.md` |
| `dodatak-d-sabloni.md` | `dodatak-d-sabloni.en.md` |

Ceo tekst knjige (Delovi I–VII i Dodaci A–D) je sada preveden na engleski.

## Stil

- Naslovi delova: "Deo N — X" → "Part N — X". Naslovi poglavlja: "Poglavlje
  N — X" → "Chapter N — X".
- Sekcije unutar poglavlja ("Pitanje na koje ovo poglavlje odgovara",
  "Analitički deo", "Skupljena pravila iz ovog poglavlja", "Vežba za
  čitaoca") prevode se dosledno istim engleskim naslovima kroz celu knjigu:
  "The question this chapter answers", "Analytical section", "Rules
  collected from this chapter", "Exercise for the reader".
- Brojevi: srpski koristi tačku kao razdvajač hiljada (2.000), engleski
  zarez (2,000). Novčani iznosi u skraćenom obliku ($1.1M, $250k) ostaju
  identični u oba jezika (već su u "engleskom" formatu i u originalu).
- Izvori na kraju poglavlja ("Izvori korišćeni u analitičkom delu") se ne
  prevode red-po-red (naslovi izvora ostaju kako su objavljeni), ali naslov
  sekcije se prevodi: "Sources used in the analytical section".

## Dijagrami

Svi dijagrami u `docs/diagrams/` (43 fajla) su rekonstruisani kao
skript-generisani, po jeziku parametrizovani izvori. Svaki dijagram ima:

1. Python skriptu u `scripts/diagrams/<ime>.py` — parametrizovanu po jeziku,
   tako da se srpska i engleska (i buduća) verzija generišu iz istog izvora.
2. Izlazne fajlove u `docs/diagrams/`: `<ime>.png` (sr, podrazumevani jezik,
   bez sufiksa) i `<ime>.en.png` (en).

Ovo je jedini način da se dijagram ponovo generiše ili izmeni bez ručnog
crtanja od nule — vidi `scripts/diagrams/cost_crossover.py` kao prvi
primer (Poglavlje 3, `cost-crossover.png`).

Dve porodice dijagrama, po alatu i paleti:

- **Graphviz (box/flow, 25 dijagrama)** — stabla odluka i arhitekturni
  tokovi, generisani preko Python `graphviz` paketa (`from graphviz import
  Digraph`, oslanja se na sistemski `dot` binarni fajl). Paleta: neutralna
  kutija `#EEEEEE`/`#999999`, ivice `#5B4636`, pozitivan čvor
  `#E6F4EA`/`#2E7D4F`, negativan čvor `#FDE7E7`/`#C0392B`, napomena/tan čvor
  `#F4EFE6`/`#8B7355`, font `DejaVu Serif`.
- **Matplotlib "dashboard-\*" (17 dijagrama)** — grafikoni (linijski/
  bar/area), sopstvena moderna paleta (drugačija od `cost_crossover.py`):
  pozadina `#F4F5F7`, plot `#FFFFFF`, serije `#2A78D6`/`#EB6834`/`#E34948`/
  `#1BAF7A`, isticanje incidenta `#FCECEC`, podrazumevani sans-serif font.

Originalne (pre rekonstrukcije) slike su sačuvane radi poređenja u
`docs/diagrams/_originals/` (nije u git-u, samo lokalna referenca).

### Urađeni dijagrami

| Dijagram | Skripta | Status |
| --- | --- | --- |
| `cost-crossover.png` | `scripts/diagrams/cost_crossover.py` | ✅ sr + en |
| `overview.png` | `scripts/diagrams/overview.py` | ✅ sr + en |
| `diagram.png` | `scripts/diagrams/diagram.py` | ✅ sr + en |
| `ch5-instrumentation.png` | `scripts/diagrams/ch5_instrumentation.py` | ✅ sr + en |
| `ch6-sidecar.png` | `scripts/diagrams/ch6_sidecar.py` | ✅ sr + en |
| `ch7-pull-obrasci.png` | `scripts/diagrams/ch7_pull_obrasci.py` | ✅ sr + en |
| `ch8-rum.png` | `scripts/diagrams/ch8_rum.py` | ✅ sr + en |
| `ch9-synthetic.png` | `scripts/diagrams/ch9_synthetic.py` | ✅ sr + en |
| `ch10-pipeline.png` | `scripts/diagrams/ch10_pipeline.py` | ✅ sr + en |
| `ch12-sampling-policy.png` | `scripts/diagrams/ch12_sampling_policy.py` | ✅ sr + en |
| `ch13-dual-path.png` | `scripts/diagrams/ch13_dual_path.py` | ✅ sr + en |
| `ch16-runbook-flow.png` | `scripts/diagrams/ch16_runbook_flow.py` | ✅ sr + en |
| `ch17-tri-tipa.png` | `scripts/diagrams/ch17_tri_tipa.py` | ✅ sr + en |
| `ch18-dve-ravni.png` | `scripts/diagrams/ch18_dve_ravni.py` | ✅ sr + en |
| `ch19-trostruki-signal.png` | `scripts/diagrams/ch19_trostruki_signal.py` | ✅ sr + en |
| `ch20-asimetrija.png` | `scripts/diagrams/ch20_asimetrija.py` | ✅ sr + en |
| `ch21-cetiri-uzroka.png` | `scripts/diagrams/ch21_cetiri_uzroka.py` | ✅ sr + en |
| `ch22-devet-ravni.png` | `scripts/diagrams/ch22_devet_ravni.py` | ✅ sr + en |
| `ch23-model-potpunosti.png` | `scripts/diagrams/ch23_model_potpunosti.py` | ✅ sr + en |
| `ch24-tri-faze.png` | `scripts/diagrams/ch24_tri_faze.py` | ✅ sr + en |
| `ch25-linkage.png` | `scripts/diagrams/ch25_linkage.py` | ✅ sr + en |
| `ch26-dvosmeran-odnos.png` | `scripts/diagrams/ch26_dvosmeran_odnos.py` | ✅ sr + en |
| `ch27-tri-sloja.png` | `scripts/diagrams/ch27_tri_sloja.py` | ✅ sr + en |
| `ch28-cetiri-replay.png` | `scripts/diagrams/ch28_cetiri_replay.py` | ✅ sr + en |
| `ch29-vremenska-linija.png` | `scripts/diagrams/ch29_vremenska_linija.py` | ✅ sr + en |
| `ch30-ciklus-revizije.png` | `scripts/diagrams/ch30_ciklus_revizije.py` | ✅ sr + en |
| `dashboard-alarm-audit.png` | `scripts/diagrams/dashboard_alarm_audit.py` | ✅ sr + en |
| `dashboard-alert-streak.png` | `scripts/diagrams/dashboard_alert_streak.py` | ✅ sr + en |
| `dashboard-authgap.png` | `scripts/diagrams/dashboard_authgap.py` | ✅ sr + en |
| `dashboard-burnrate.png` | `scripts/diagrams/dashboard_burnrate.py` | ✅ sr + en |
| `dashboard-cardinality.png` | `scripts/diagrams/dashboard_cardinality.py` | ✅ sr + en |
| `dashboard-completeness.png` | `scripts/diagrams/dashboard_completeness.py` | ✅ sr + en |
| `dashboard-connections.png` | `scripts/diagrams/dashboard_connections.py` | ✅ sr + en |
| `dashboard-ebhealth-vs-5xx.png` | `scripts/diagrams/dashboard_ebhealth_vs_5xx.py` | ✅ sr + en |
| `dashboard-natdiff.png` | `scripts/diagrams/dashboard_natdiff.py` | ✅ sr + en |
| `dashboard-pseudonymization.png` | `scripts/diagrams/dashboard_pseudonymization.py` | ✅ sr + en |
| `dashboard-rds.png` | `scripts/diagrams/dashboard_rds.py` | ✅ sr + en |
| `dashboard-rightsizing.png` | `scripts/diagrams/dashboard_rightsizing.py` | ✅ sr + en |
| `dashboard-rum.png` | `scripts/diagrams/dashboard_rum.py` | ✅ sr + en |
| `dashboard-sampling.png` | `scripts/diagrams/dashboard_sampling.py` | ✅ sr + en |
| `dashboard-snowflake.png` | `scripts/diagrams/dashboard_snowflake.py` | ✅ sr + en |
| `dashboard-suppression.png` | `scripts/diagrams/dashboard_suppression.py` | ✅ sr + en |
| `dashboard-synthetic.png` | `scripts/diagrams/dashboard_synthetic.py` | ✅ sr + en |

Svi dijagrami u knjizi su sada rekonstruisani (sr + en) — nema više
statičkih slika bez izvora.
