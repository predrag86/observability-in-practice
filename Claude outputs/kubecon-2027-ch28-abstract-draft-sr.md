# KubeCon + CloudNativeCon EU 2027 — CFP nacrt (srpska verzija)
## Izvor: Poglavlje 28, "AI-asistirana observability: agent koji čita telemetriju"

> ⚠️ **Napomena:** ovo je verzija na srpskom za tvoju internu upotrebu (razumevanje, vežbanje,
> eventualni lokalni talk). Sama CFP prijava na Sessionize mora biti na engleskom — to je
> engleska verzija u prethodnom fajlu (`kubecon-2027-ch28-abstract-draft.md`).

Portal za prijavu: https://sessionize.com/cncf-hosted-co-located-events-europe-2027/
Rok: **18. oktobar 2026, 23:59 CET**. Obaveštenja: 14. decembar 2026. Event: 15. mart 2027, Barselona.

Ciljani track(ovi): **Observability Day** (primarno) i/ili **Agentics Day: MCP + Agents**
(sadržaj se uklapa u oba — izaberi jedan kao primarni ako forma traži jedan izbor, ili prijavi
na oba ako dozvoljava; ovo se vidi tek na samoj Sessionize formi, koja traži login).

Preporučeni format: **solo prezentacija, 25 min.** Četiri replay-a incidenata plus dva
mehanizma greške ne stanu udobno u lightning talk od 10 minuta.

---

## Naslov (izaberi jedan, ili kombinuj)

1. **"The Agent Said 'Successfully Deleted.' Nothing Was Deleted."**
   *(„Agent je rekao 'uspešno obrisano.' Ništa nije obrisano."*)
   *Lekcije iz testiranja AI agenta na četiri stvarna observability incidenta*
2. **"Replaying Incidents on an AI Agent: Where It's Right, and Where It Confidently Lies"**
   *(„Puštanje incidenata unazad na AI agentu: gde je u pravu, a gde samopouzdano laže"*)
3. **"The Missing Context Layer: What an AI Agent Doesn't Know About Your Telemetry"**
   *(„Sloj konteksta koji nedostaje: šta AI agent ne zna o vašoj telemetriji"*)
4. **"Four Real Incidents, One AI Agent: A Production Test of MCP-Based Observability"**
   *(„Četiri stvarna incidenta, jedan AI agent: produkcijski test observability-ja preko MCP-a"*)

Preporuka: **naslov #1** ostaje na engleskom čak i u prijavi (to je konkretna, citatna kuka koja
zaustavlja recenzenta) — ali ako praviš srpsku verziju talka (npr. za lokalni meetup ili
vežbanje), fraza iz #3 ("sloj konteksta koji nedostaje") je dobar podnaslov.

---

## Abstract / opis sesije (srpski prevod, ~210 reči u originalu)

Svaki veći vendor telemetrijskih platformi danas nudi svoj MCP server, i poruka je svuda ista:
dajte AI agentu pristup za čitanje vaših metrika, logova i trejsova, i on će ubrzati triage
alarma. Mi to nismo uzeli zdravo za gotovo. Umesto toga, pustili smo agenta da nezavisno prođe
kroz četiri stvarna, već rešena incidenta iz naše produkcijske istorije — sa istim MCP alatima
za upit koje ima i čovek na dežurstvu — i uporedili njegovo zaključivanje sa odgovorom koji smo
već znali.

Dva replay-a su prošla dobro — agent je nezavisno rekonstruisao tačan uzrok kroz lanac dokaza
koji bi čovek prepoznao. Jedan replay je taj zbog kog vredi izdvojiti 25 minuta: bez dodatnog
konteksta, agent je pročitao izvedenu metriku "zdravlja" sistema, prihvatio je zdravo za gotovo,
i samopouzdano bi eskalirao lažni pad sistema — jer ništa u generičkom znanju o observability-ju
nije ukazivalo da je baš ta metrika poznato nepouzdana. A testirajući granicu pisanja agenta,
naišli smo na oštriji problem: blokiran upis i uspešan upis vraćaju *identičnu* poruku "uspeh",
pa će agent iskreno prijaviti akciju koja se nikad nije desila.

Ovaj talk pokriva šta smo napravili kao odgovor — mali "sloj konteksta" specifičnih zamki
sistema koji se učitava po potrebi, i sprovođenje read-only pristupa na nivou dozvola samog
tokena umesto verovanja agentovom sopstvenom izveštaju — i šta su nas četiri stvarna incidenta
naučila o tome gde je AI-asistirana observability spremna danas, a gde još nije.

---

## Napomene za recenzente / polje "da li je ovo case study"

Da — ovo je produkcijski case study, ne demo niti prodajna prezentacija. Sva četiri replay-ovana
incidenta su stvarni, već rešeni produkcijski incidenti (detalji anonimizovani: ime kompanije,
interni domeni i ID-jevi resursa su generalizovani — dosledno tome kako izvorni materijal, knjiga
o ovoj produkcijskoj observability implementaciji, već tretira ovo pitanje). Talk uključuje:
metodologiju replay-a, četiri incidenta i šta je svaki od njih otkrio, dva konkretno imenovana
mehanizma greške (lažni uspeh kod blokirane akcije; upit ka strukturno pogrešnom skladištu
podataka, koje vraća uverljivu nulu umesto greške), mitigaciju kroz sloj konteksta, i gde je ovo
nezavisno potvrđeno postojećim MCP/AI-SRE preporukama (citirano u talku) naspram onoga što je
naš nov nalaz. Završava se jasnom, primenljivom preporukom gde danas povući liniju za ljudsko
odobrenje.

## Relevantni CNCF / ekosistem projekti za formu

- OpenTelemetry (telemetrija koju agent upituje)
- Prometheus / upitna površina koju MCP alat izlaže (metrike)
- Model Context Protocol (standard konektora o kome je ceo talk)
- Grafana (Loki/Tempo/Mimir) kao platforma, ako forma dozvoljava kontekst van CNCF-a

## Jednorečenična poenta (za social/preview karticu, ako forma to traži)

Dali smo AI agentu MCP pristup našoj telemetriji i testirali ga na četiri stvarna incidenta —
evo tačno gde je dijagnoza bila ispravna, gde je samopouzdano pogrešio, i koja jedna
arhitektonska odluka je sprečila da "samopouzdano pogrešno" postane "tiho destruktivno."

---

## Bio govornika (nacrt — prilagodi po ukusu)

Predrag Mujković je Senior DevOps/SRE inženjer sa skoro deceniju iskustva u cloud i on-premises
infrastrukturi, trenutno zadužen za observability platforme za analitiku vremenskih podataka na
AWS-u (ECS Fargate, Aurora/RDS, Terraform) sa OpenTelemetry i Grafana LGTM stack-om (Loki,
Grafana, Tempo, Mimir). Autor je knjige koja od početka do kraja dokumentuje implementaciju
observability sistema te platforme, zasnovane na stvarnom produkcijskom sistemu.

---

## Pre nego što pošalješ — na šta obratiti pažnju

1. Proveri stvarni limit karaktera za title/abstract na živoj Sessionize formi (nije objavljen
   na javnoj CFP stranici) i skrati abstract prema tome.
2. Proveri da li forma dozvoljava izbor više od jednog ciljanog co-located eventa, ili traži
   jedan izbor — na osnovu toga odluči Observability Day naspram Agentics Day.
3. CFP eksplicitno traži da naznačiš ako je prijava slična već održanom talku i objasniš razliku
   — nije problem ovde jer ovo nikad nije predstavljeno, ali vredi napomenuti u jednoj rečenici
   ako forma to pita.
4. Panel format traži 3 govornika iz 3 različite organizacije — nije relevantno ovde jer je ovo
   solo prijava, samo napomena ako kasnije poželiš panel verziju.
