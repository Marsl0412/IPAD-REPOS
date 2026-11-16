# Goodnotes-Vorlagen – Middendorf Metallbau OHG

| Blatt | Ordner |
|---|---|
| Aufmaß Geländer | `ausgabe/Aufmass_Gelaender/` |
| Aufmaß Türen | `ausgabe/Aufmass_Tueren/` |
| Aufmaß allgemein (Tor, Vordach, Sonstiges) | `Aufmassblatt_komplett.pdf` (ältere Version) |

- `*_komplett.pdf` → in Goodnotes als Notizbuch importieren, je Baustelle duplizieren
- `*_S1/S2/S3.pdf` → Goodnotes › Einstellungen › Vorlagen › Importieren

## Ändern / neues Blatt anlegen
Alle Felder stehen als Liste oben in `build_vorlagen.py` (`BLAETTER`).
Text ändern oder neuen Eintrag kopieren, dann:

    python3 build_vorlagen.py

Läuft eine Seite über, bricht das Skript mit einer Meldung ab, statt ein kaputtes PDF zu erzeugen.
