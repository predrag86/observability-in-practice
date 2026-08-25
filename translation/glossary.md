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

## Nazivi delova/poglavlja (za buduće interne linkove)

| Srpski fajl | Engleski fajl |
| --- | --- |
| `index.md` | `index.en.md` |
| `uvod.md` | `uvod.en.md` |
| `deo-1-uvod.md` | `deo-1-uvod.en.md` |
| `poglavlje-01-sta-je-observability.md` | `poglavlje-01-sta-je-observability.en.md` |
| `poglavlje-02-opentelemetry.md` | `poglavlje-02-opentelemetry.en.md` |
| `poglavlje-03-izbor-platforme.md` | `poglavlje-03-izbor-platforme.en.md` |

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

Dijagrami bez izvora (svi u `docs/diagrams/`, ~40 fajlova) rekonstruišu se
po potrebi, jedan po jedan, dok prevodimo deo knjige koji ih koristi.
Svaki rekonstruisan dijagram dobija:

1. Python skriptu u `scripts/diagrams/<ime>.py` — parametrizovanu po jeziku,
   tako da se srpska i engleska (i buduća) verzija generišu iz istog izvora.
2. Izlazne fajlove u `docs/diagrams/`: `<ime>.png` (sr, podrazumevani jezik,
   bez sufiksa) i `<ime>.en.png` (en).

Ovo je jedini način da se dijagram ponovo generiše ili izmeni bez ručnog
crtanja od nule — vidi `scripts/diagrams/cost_crossover.py` kao prvi
primer (Poglavlje 3, `cost-crossover.png`).

### Urađeni dijagrami

| Dijagram | Skripta | Status |
| --- | --- | --- |
| `cost-crossover.png` | `scripts/diagrams/cost_crossover.py` | ✅ sr + en |
