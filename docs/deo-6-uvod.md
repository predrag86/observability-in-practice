# Deo VI — Upravljanje, usklađenost i zrelost

## Pre nego što krenemo: kad sistem radi, pitanja se menjaju

Svaki prethodni deo knjige je, u osnovi, odgovarao na jedno pitanje: da li
sistem vidi ono što treba da vidi, i da li tim reaguje na vreme kad nešto
pođe po zlu. Deo VI pretpostavlja da je to pitanje već rešeno, i postavlja
pet sasvim drugih:

- **Poglavlje 25** pita da li telemetrija, dok radi svoj posao, curi
  informacije koje ne bi trebalo da nosi — privatnost kao poznat obrazac
  curenja sa preciznim imenom, ne apstraktna briga.
- **Poglavlje 26** pita da li se sistem posmatranja može koristiti kao
  dokaz pred spoljnim revizorom — observability kao kontrola usklađenosti,
  na konkretnom primeru SOC 2.
- **Poglavlje 27** pita kako se, kad su cena, performanse, pouzdanost i
  bezbednost sve podjednako legitimne, uopšte bira šta se radi sledeće.
- **Poglavlje 28** pita šta se menja kad prvi koji čita telemetriju nakon
  incidenta više nije čovek, nego AI agent — i gde je granica onoga što
  taj agent stvarno može da zna.
- **Poglavlje 29** pita šta se dešava kad dve konfiguracije koje bi
  trebalo da budu identične tiho krenu različitim putem — i da li se
  taj incident tiho zakrpi, ili iskoristi kao razlog da se promeni sam
  proces koji ga je proizveo.

Zajednička nit: ovo su organizaciona i poverenja pitanja, ne tehnička
pitanja implementacije koja su nosila prethodne delove. Sistem koji radi
tehnički ispravno, a ne može da odgovori ni na jedno od ovih pet
pitanja, nije zreo sistem — samo je sistem koji još nije bio testiran na
pravi način. Deo VII, koji zatvara knjigu, uzima tačno tu meru zrelosti i
pita kako izgleda kad se primeni na sopstveni, stvaran, višemesečni
rollout.
