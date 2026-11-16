# Goodnotes-Vorlagen – Middendorf Metallbau OHG

| Blatt | Ordner |
|---|---|
| Aufmaß Geländer | `ausgabe/Aufmass_Gelaender/` |
| Aufmaß Türen | `ausgabe/Aufmass_Tueren/` |

- `*_komplett.pdf` → in Goodnotes als Notizbuch importieren, je Baustelle duplizieren
- `*_S1.pdf` (Kunde, Füllung, Maße) / `*_S2.pdf` (Skizze) → Goodnotes › Einstellungen › Vorlagen › Importieren

## Ändern / neues Blatt anlegen
Alle Felder stehen als Liste oben in `build_vorlagen.py` (`BLAETTER`).
Text ändern oder neuen Eintrag kopieren, dann:

    python3 build_vorlagen.py

Läuft eine Seite über, bricht das Skript mit einer Meldung ab, statt ein kaputtes PDF zu erzeugen.
