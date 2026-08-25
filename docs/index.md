# Observability u praksi

## OpenTelemetry i Grafana LGTM stack

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

## Struktura

| Deo | Tema |
| --- | --- |
| [Uvod](uvod.md) | Zašto ova knjiga, i po čemu se razlikuje |
| Deo I | Osnove — šta je observability, OpenTelemetry, izbor platforme |
| Deo II | Arhitektura prikupljanja telemetrije — gateway, instrumentacija, sidecar |
| Deo III | Obrada, kardinalnost i troškovi |
| Deo IV | Alarmiranje, SLO i odgovor na incidente |
| Deo V | Observability po domenima — baze, klasteri, mreža, batch/ETL, Snowflake |
| Deo VI | Upravljanje, usklađenost i zrelost |
| Deo VII | Sazrevanje programa |
| Dodaci | PromQL/LogQL recepti, rečnik pojmova, checklist, šabloni |

Svako standardno poglavlje prati isti oblik: uvodna analogija iz stvarnog
života, praktičan deo (kako je urađeno, sa dijagramom arhitekture i gde je
relevantno ilustrativan dashboard mockup), analitički deo (poređenje sa
industrijskim standardom, kontrafaktički scenario), skupljena pravila, i
vežba za čitaoca.

Krenite od [Uvoda](uvod.md), ili direktno na [Poglavlje 1](poglavlje-01-sta-je-observability.md).
