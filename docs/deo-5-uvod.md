# Deo V — Domenske studije slučaja

## Pre nego što krenemo: isti slojevi, sad kao predmet, ne kao posmatrač

Uvod u Deo II je mapirao sistem koji ova knjiga posmatra: sloj aplikacija,
sloj autentikacije, dve vrste baza podataka, flota batch/ETL zadataka,
mrežni sloj, i jedan nezavisan SaaS servis van naše mreže. U Delu II taj
dijagram je bio namerno tanak na strani posmatranja — poenta je bila
pokazati **šta** se posmatra, ne **kako**. Deo V je mesto gde se to okreće:
svako poglavlje uzima jedan od tih slojeva i pita ga u punoj dubini —
šta ovde konkretno pokvari signal, i zašto standardni pristup iz Delova
I–IV tu nije dovoljan bez prilagođavanja:

- **Poglavlje 18** — upravljane baze podataka (tipa RDS/Aurora), gde AWS
  drži host i tim nema pristup mašini.
- **Poglavlje 19** — samostalno upravljan distribuiran klaster (tipa
  Dremio), gde tim drži i host i proces, sa svim posledicama koje to nosi.
- **Poglavlje 20** — autentikacija i IAM (tipa Keycloak), sloj koji
  omogućava posmatranje svega ostalog, a retko je i sâm predmet posmatranja.
- **Poglavlje 21** — hostovi i serveri kao mašine, sloj koji leži ispod
  svega gore navedenog.
- **Poglavlje 22** — mreža kao posebna ravan posmatranja, infrastruktura
  koja nosi sve ostale slojeve.
- **Poglavlje 23** — flota batch/ETL zadataka, gde se uspeh ne meri time
  da li je proces radio, nego time šta je proizveo.
- **Poglavlje 24** — servis koji nije naš (tipa Snowflake): posmatranje
  bez ikakve operativne kontrole nad infrastrukturom koja ga nosi.

Ovo je najduži deo knjige, i to nije slučajno: ne uvodi nijedan nov
mehanizam posmatranja, nego pokazuje da isti mehanizam, primenjen na
sedam različitih domena, sedam puta zahteva drugačiju odluku. Deo VI, koji
sledi, pretpostavlja da su svi ovi slojevi tehnički pokriveni, i pita
sasvim drugu vrstu pitanja: da li se sistemu koji smo izgradili može
verovati.
