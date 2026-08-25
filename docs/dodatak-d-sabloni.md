# Dodatak D — Šablon runbook-a i šablon postmortema

Dva šablona, spremna za kopiranje. Razlika između njih je razlika koja
se provlači kroz celu knjigu: runbook gleda UNAPRED ("sledeći put kad
ovo okine, uradi ovo") i piše se PRE incidenta; postmortem gleda UNAZAD
("ovo se dogodilo, evo zašto") i piše se POSLE. Runbook se često
destiluje IZ postmortema, ali su to dva odvojena dokumenta sa dva
odvojena čitaoca u dva odvojena trenutka.

## D.1 — Šablon runbook-a

```markdown
# Runbook — <Klasa kvara, ne jedan događaj>

> **Alarm koji ovo pokreće:** <ime/broj pravila alarmiranja>
> **Kanal:** <gde obaveštenje stiže>
> **Poslednja provera:** <YYYY-MM-DD> · **Vlasnik:** <ime/tim>

## Kad se ovo koristi

<Jedna do dve rečenice — koji tačno alarm/simptom dovodi
ovde, i čime se ovo NE bavi (upućivanje na susedni runbook
ako simptomi liče).>

## Prva provera — pre bilo čega drugog

<Jedno ili dva pitanja koja odmah suze prostor mogućih
uzroka. Primer obrasca: "da li je ovo rutinsko gašenje pri
skaliranju (exit=143) ili stvaran kvar?" — razlikovanje
benignog od stvarnog je uvek prvi korak.>

## Stablo odluke

1. <Pitanje #1> → ako DA, idi na <akcija/link>; ako NE, nastavi.
2. <Pitanje #2> → ...
3. <Pitanje #3> → ...

## Deep-linkovi

- <Direktan link na dashboard/upit pred-podešen na
  relevantan vremenski prozor i filter — ne opis kako do
  njega doći ručno.>

## Poznate zamke

- <Nešto što liči na ovaj kvar, a nije — i kako se razlikuje.>

## Kad eskalirati

<Eksplicitan uslov posle kog se ovaj runbook napušta i
poziva neko drugi — vremenski prag, ili "ako korak 3 ne
pomogne".>

## Vezano

- Postmortem(i) iz kojih je ovaj runbook destilovan: <link(ovi)>
```

## D.2 — Šablon postmortema

```markdown
# <Naslov — šta se pokvarilo, običnim jezikom>

> **Ozbiljnost:** <Niska / Srednja / Visoka / Kritična>
> **Otkriveno:** <YYYY-MM-DD HH:MM>
> **Rešeno:** <YYYY-MM-DD HH:MM>
> **Radijus dejstva:** <ko/šta je pogođeno>
> **Status:** <REŠENO / UBLAŽENO / OTVORENO>
> **Autor:** <ime>

## Rezime

<2-4 rečenice. Šta se dogodilo, simptom vidljiv korisniku,
i uzrok u jednoj rečenici. Neko treba da razume ceo
incident samo iz ovog pasusa.>

## Uticaj

<Konkretno: ko je pogođen, šta nisu mogli da urade ili u
šta su bili dovedeni u zabludu, koliko dugo. Zapiši i šta
NIJE bilo pogođeno — eksplicitno ograniči radijus
dejstva.>

## Vremenska linija

Sva vremena u <vremenska zona>.

| Vreme | Događaj |
| --- | --- |
| <kad je uzrok uveden> | <commit koji je posadio grešku> |
| <kad je otkriveno> | <kako je isplivalo> |
| ... | ... |
| <kad je rešeno> | <popravka uživo + potvrđena> |

## Osnovni uzrok

<Stvaran mehanizam. Budi precizan — citiraj kod,
konfiguraciju, tačnu pogrešnu vrednost. Objasni ZAŠTO je
proizvela baš taj simptom, ne samo šta je bilo pogrešno.>

## Detekcija

<Kako je otkriveno? Ko je primetio, kroz koji signal? Da
li je sistem posmatranja ćutao — i da li je trebalo?>

## Rešenje

<Popravka. Šta je promenjeno, kako je verifikovano, kako
je dostavljeno u produkciju.>

## Zašto nije uhvaćeno ranije

<Iskren deo. Koja provera/test/ograda bi ovo uhvatila, a
nije postojala ili nije bila izvršena.>

## Naučene lekcije

- <Šta sada znamo.>

## Akcione stavke

| # | Akcija | Vlasnik | Status |
| - | --- | --- | --- |
| 1 | <praćenje> | <ko> | <u toku/završeno> |
```

## D.3 — Napomena o disciplini popunjavanja

Oba šablona vrede onoliko koliko se dosledno popunjavaju — prazno polje
"Zašto nije uhvaćeno ranije" je čest znak da je postmortem pisan da bi se
zatvorio, ne da bi se iz njega nešto naučilo. Isto važi za runbook čije
"Poznate zamke" polje ostaje prazno posle prve upotrebe — prva stvarna
primena runbook-a skoro uvek otkrije bar jednu zamku koju original nije
predvideo; vrati se i dopiši je.
