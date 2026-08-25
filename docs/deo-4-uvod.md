# Deo IV — Alarmiranje, SLO i odgovor na incidente

## Pre nego što krenemo: jedan incident, ispričan kroz pet poglavlja

Za razliku od ostalih delova knjige, koji svaki obrađuju jedan sloj ili
jedan mehanizam nezavisno, Deo IV prati **jedan kontinuirani put** —
od trenutka kad nešto krene po zlu do trenutka kad je tim izvukao lekciju
iz toga — kroz pet poglavlja, tim redom kako se taj put stvarno odvija:

- **Poglavlje 13** postavlja arhitekturu: dva potpuno različita puta
  kojima signal o problemu stiže — jedan automatski, jedan ljudski — koji
  se na kraju spajaju u isti odredišni kanal.
- **Poglavlje 14** se bavi suprotnim slučajem: šta se dešava kad alarm
  koji je trebalo da javi ništa ne javi — gating, dedup i "tihi gap" koji
  nastaje baš tamo gde bi ga bilo najteže primetiti.
- **Poglavlje 15** uvodi SLO i alarme zasnovane na budžetu grešaka — način
  da se hitnost reakcije proceni na osnovu toga koliko brzo budžet nestaje,
  a ne samo da li je prag pređen.
- **Poglavlje 16** prelazi na trenutak kad je čovek već pozvan: runbook
  kao most između alarma i konkretnog rešenja, strukturiran tako da radi
  pod pritiskom, ne samo na papiru.
- **Poglavlje 17** zatvara krug: postmortem kultura koja incident pretvara
  u lekciju za sistem, ne u potragu za krivcem.

Ovih pet poglavlja se mogu čitati kao jedna priča, od prvog signala do
poslednjeg zapisa u postmortem dokumentu. Deo V, koji sledi, pretpostavlja
da ovaj put — od signala do rešenja — već postoji i radi, i primenjuje ga
redom na svaki pojedinačan sloj sistema.
