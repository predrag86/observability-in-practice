*[alarm iz klase odsustva]: Problem koji se ne javlja kao pogrešan signal, nego kao odsustvo signala koji bi trebalo da postoji.
*[aktivne serije]: Vremenske serije koje trenutno primaju podatke.
*[naplative serije]: Serije za koje pružalac usluge stvarno naplaćuje — retko je isto što i aktivne serije.
*[Adaptive Traces]: Uzorkovanje raspona gde platforma za posmatranje, ne kolektor, odlučuje šta zadržava, po redosledu politika.
*[radijus dejstva]: Koliko korisnika, servisa ili podataka bi bilo pogođeno ako nešto pođe po zlu.
*[burn-rate]: Koliko brzo se troši budžet greške SLO-a, izraženo kao višekratnik normalne stope.
*[Dead man's switch]: Alarm koji se oglašava kad OTKAŽE mehanizam koji bi inače prijavio problem — tišina je loš znak.
*[dedup]: Grupisanje ponovljenih obaveštenja o istom kvaru u jedan zapis unutar vremenskog prozora.
*[DPM]: Data points per minute — koliko tačaka podataka po minutu jedna serija proizvodi.
*[budžet greške]: Dozvoljena količina "lošeg" ponašanja pre nego što SLO bude prekršen.
*[Exemplar]: Pojedinačan uzorak (obično jedan raspon/trace ID) povezan sa tačkom na histogramu metrike.
*[zlatni signali]: Kašnjenje, saobraćaj, greške, zasićenje — osnovna četiri dimenzije za ocenu zdravlja servisa.
*[Keyed-HMAC pseudonimizacija]: Pretvaranje identifikatora u pseudonim heš funkcijom sa tajnim ključem, protiv brute-force napada.
*[MCP]: Model Context Protocol — otvoren protokol koji AI agentu daje strukturisan pristup alatima i podacima.
*[native histogram]: Format histograma gde se raspodela po kantama šalje kompaktnije nego kod klasičnog histograma.
*[POA&M]: Plan of Action and Milestones — stavka koja još nije rešena, ali se aktivno prati ka rešenju.
*[RED metod]: Rate, Errors, Duration — standardni okvir za servise koji stalno primaju saobraćaj.
*[resource attribute]: Par ključ-vrednost koji opisuje IZVOR telemetrije, npr. service.name.
*[formalno prihvatanje rizika]: Dokumentovana odluka da se rizik svesno ne rešava, sa obrazloženjem i datumom.
*[semantičke konvencije]: Standardizovana imena atributa i metrika koje OTel propisuje, npr. http.status_code.
*[SLI]: Service Level Indicator — merljiv signal, npr. procenat uspešnih zahteva.
*[SLO]: Service Level Objective — ciljna vrednost signala kroz vreme, npr. 99.9%.
*[span metrics]: Metrike izvedene iz raspona (traces) pre bilo kakvog uzorkovanja.
*[tail sampling]: Odluka o zadržavanju raspona donosi se nakon što se ceo raspon završi.
*[target_info]: Standardna OTel/Prometheus metrika koja nosi resursne atribute kao oznake.
*[nivo hitnosti]: Klasifikacija alarma po ozbiljnosti koja određuje dedup i put obaveštenja.
*[USE metod]: Utilization, Saturation, Errors — okvir za posmatranje resursa (host, disk, mreža).
*[posmatrač koji nadživi posmatrano]: Alarm koji prati zdravlje platforme za posmatranje mora imati put do čoveka nezavisan od te platforme.
