---
hide:
  - navigation
  - toc
---

<!-- Homepage hero: a raw HTML section with the H1 nested inside it,
     for the full-bleed background image treatment. -->
<!-- markdownlint-disable MD033 MD041 -->

<div class="hero" markdown="1">
<div class="hero-content" markdown="1">

# Observability u praksi

OpenTelemetry i Grafana LGTM stack
{: .hero-tagline }

</div>
</div>

<!-- markdownlint-enable MD033 MD041 -->

Knjiga strukturirana oko stvarne, višemesečne evolucije jednog produkcionog
observability sistema implementiranog na nivou cele firme — portfelja koji
obuhvata desetine backend i frontend aplikacija, mrežnu infrastrukturu,
upravljane i samostalno upravljane baze podataka, distribuirane compute
klastere, autentikacioni sloj i flotu batch/ETL zadataka, sve na AWS-u, plus
jedan nezavisan SaaS servis van te infrastrukture.

Svako poglavlje kombinuje teoriju (zašto ovako) sa konkretnim, anonimizovanim
primerima iz implementacije: pravim PromQL/LogQL upitima, pravim greškama koje
su napravljene i pravim odlukama zašto je nešto odbijeno.

!!! note "Anonimizacija"
    Sva imena firme, ljudi, interni domeni, ID-jevi resursa i drugi
    identifikujući detalji su namerno uklonjeni ili generalizovani — knjiga se
    oslanja na **obrasce i odluke**, ne na to čiji su.

## Kome je namenjena

DevOps/SRE inženjerima, backend programerima koji uvode instrumentaciju u svoj
servis, i tim lidovima koji treba da donesu odluku self-hosted naspram Grafana
Cloud i da opravdaju trošak.

Knjiga pretpostavlja osnovno radno poznavanje DevOps/SRE prakse (Linux,
kontejneri, CI/CD, cloud infrastruktura) i uvodno poznavanje observability
pojmova (metrike, logovi, trejsovi). Prethodno iskustvo sa OpenTelemetry-jem
nije neophodno — objašnjava se od Poglavlja 2.

## Struktura

| Deo | Tema |
| --- | --- |
| [Uvod](uvod.md) | Zašto ova knjiga, i po čemu se razlikuje |
| [Deo I](poglavlje-01-sta-je-observability.md) | Osnove — šta je observability, OpenTelemetry, izbor platforme |
| [Deo II](deo-2-uvod.md) | Arhitektura prikupljanja telemetrije — gateway, instrumentacija, sidecar |
| [Deo III](poglavlje-10-anatomija-pipeline.md) | Obrada, kardinalnost i troškovi |
| [Deo IV](poglavlje-13-arhitektura-alarmiranja.md) | Alarmiranje, SLO i odgovor na incidente |
| [Deo V](poglavlje-18-baze-podataka.md) | Observability po domenima — baze, klasteri, mreža, batch/ETL, Snowflake |
| [Deo VI](poglavlje-25-privatnost-telemetriji.md) | Upravljanje, usklađenost i zrelost |
| [Deo VII](poglavlje-29-fazni-rollout.md) | Sazrevanje programa |
| [Dodaci](dodatak-a-promql-logql-recepti.md) | PromQL/LogQL recepti, rečnik pojmova, checklist, šabloni |

Svako standardno poglavlje prati isti oblik: uvodna analogija iz stvarnog
života, praktičan deo (kako je urađeno, sa dijagramom arhitekture i gde je
relevantno ilustrativan dashboard mockup), analitički deo (poređenje sa
industrijskim standardom, kontrafaktički scenario), skupljena pravila, i
vežba za čitaoca.

Krenite od [Uvoda](uvod.md), ili direktno na [Poglavlje 1](poglavlje-01-sta-je-observability.md).
