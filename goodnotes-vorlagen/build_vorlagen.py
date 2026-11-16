"""Aufmaß-Vorlagen-Generator für Goodnotes – Middendorf Metallbau OHG

Jedes Aufmaßblatt ist unten in BLAETTER als reine Daten beschrieben.
Neues Blatt = neuen Eintrag anlegen, Feld ändern = Text ändern, dann:

    python3 build_vorlagen.py

Ausgabe je Blatt in ausgabe/<Datei>/:
    <Datei>_komplett.pdf   – alle Seiten (als Notizbuch importieren)
    <Datei>_S1.pdf ...     – Einzelseiten (als Goodnotes-Vorlage importieren)

Baustein-Typen in einem Abschnitt ("rows"):
    ("felder", [("Beschriftung", Gewicht), ...])     Schreiblinien nebeneinander
    ("kaestchen", "Label", ["A", "B"], "Restfeld")    Ankreuzkästchen, bricht automatisch um;
                                                      Restfeld (optional) füllt die Zeile auf
    ("hinweis", "Text")                               kleiner grauer Hinweis
    ("linien", n)                                     n leere Schreibzeilen
Sonder-Abschnitte:  {"tabelle": {...}}, {"unterschrift": True}
"""
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# Firmendaten
# ----------------------------------------------------------------------
FIRMA = "Middendorf Metallbau OHG"
FIRMA_ZEILEN = ["Ottostraße 4 · 26899 Rhede (Ems) · Tel. 04964 / 91 99 05-0",
                "info@mb-middendorf.de · www.mb-middendorf.de"]

# ----------------------------------------------------------------------
# Kundendaten (auf allen Blättern gleich)
# ----------------------------------------------------------------------
KUNDE = {"titel": "Kunde", "rows": [
    ("felder", [("Name", 1), ("Telefon", 1)]),
    ("felder", [("Straße", 1), ("E-Mail", 1)]),
    ("felder", [("PLZ / Ort", 1), ("Baustelle (falls abw.)", 1)]),
]}

# ----------------------------------------------------------------------
# Die Blätter – "seiten": Liste aus ("abschnitte", [...]) oder ("skizze", "standard" | "tuer")
# ----------------------------------------------------------------------
BLAETTER = [
    {
        "datei": "Aufmass_Gelaender",
        "titel": "AUFMASS GELÄNDER",
        "seiten": [
            ("abschnitte", [
                KUNDE,
                {"titel": "Füllung", "rows": [
                    ("kaestchen", "", ["Stäbe senkrecht", "Querstäbe", "Lochblech", "Glas (VSG)",
                                       "Streckmetall"], "Sonstiges"),
                ]},
                {"titel": "Maße", "tabelle": {"zeilen": 18, "spalten": [
                    ("Pos.", 12), ("Abschnitt / Lage", 62), ("Länge", 26), ("Höhe", 26), ("Bemerkung", 0)]}},
            ]),
            ("skizze", "standard"),
        ],
    },
    {
        "datei": "Aufmass_Tueren",
        "titel": "AUFMASS TÜREN",
        "seiten": [
            ("abschnitte", [
                KUNDE,
                {"titel": "Füllung & Öffnung", "rows": [
                    ("kaestchen", "Füllung", ["Blech glatt", "Glas", "Lochblech", "Stäbe"], "Sonstiges"),
                    ("kaestchen", "Öffnung", ["DIN links", "DIN rechts", "nach innen", "nach außen"], None),
                ]},
                {"titel": "Maße", "tabelle": {"zeilen": 16, "spalten": [
                    ("Pos.", 12), ("Raum / Lage", 56), ("Breite", 26), ("Höhe", 26), ("Wand", 22),
                    ("Bemerkung", 0)]}},
            ]),
            ("skizze", "standard"),
        ],
    },
]

# ======================================================================
# Ab hier Layout-Technik – für neue Blätter muss nichts geändert werden
# ======================================================================
W, H = A4
M = 12 * mm
CW = W - 2 * M
LH = 8 * mm            # Zeilenhöhe zum Schreiben
HINWEIS_H = 4.5 * mm
BAR = 6 * mm
PAD = 2 * mm
GAP = 3.5 * mm
LABEL_W = 25 * mm
BOX = 3.8 * mm
UNTEN = 14 * mm         # unterster nutzbarer Punkt

ACCENT = HexColor("#1F3A5F")
LINE = HexColor("#9AA5B1")
GRID = HexColor("#D5DBE1")
GRID_MAJOR = HexColor("#B4BEC8")
TEXT = HexColor("#1A1A1A")
MUTED = HexColor("#5B6670")
FILL = HexColor("#EEF2F6")


class Seite:
    def __init__(self, c, blatt, nr, gesamt, start=0):
        self.c, self.blatt, self.nr, self.gesamt = c, blatt, nr, gesamt
        self.y = H - M
        self.abschnitt = start

    # ---------------- Primitive ----------------
    def text(self, x, y, s, size=8, bold=False, color=TEXT):
        self.c.setFillColor(color)
        self.c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        self.c.drawString(x, y, s)

    def w(self, s, size=8, bold=False):
        return self.c.stringWidth(s, "Helvetica-Bold" if bold else "Helvetica", size)

    def hline(self, x, y, x2, color=LINE, width=0.5):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x, y, x2, y)

    def feld(self, x, y, breite, label):
        self.text(x, y + 1.2, label, 7.5, color=MUTED)
        self.hline(x + self.w(label, 7.5) + 2 * mm, y, x + breite)

    def kaestchen(self, x, y, label):
        self.c.setStrokeColor(TEXT)
        self.c.setLineWidth(0.6)
        self.c.rect(x, y - 0.6 * mm, BOX, BOX, stroke=1, fill=0)
        self.text(x + BOX + 1.5 * mm, y + 0.3 * mm, label)

    # ---------------- Kopf / Fuß ----------------
    def kopf(self):
        t = self.blatt["titel"]
        rx = W - M - 70 * mm
        if self.nr == 1:
            self.text(M, self.y - 6 * mm, FIRMA, 15, True, ACCENT)
            for i, z in enumerate(FIRMA_ZEILEN):
                self.text(M, self.y - 11 * mm - i * 3.3 * mm, z, 6.8, color=MUTED)
            self.text(rx, self.y - 6 * mm, t, 14, True, ACCENT)
            self.feld(rx, self.y - 12.5 * mm, 34 * mm, "Nr.")
            self.feld(rx + 37 * mm, self.y - 12.5 * mm, 33 * mm, "Seite")
            self.feld(rx, self.y - 18.5 * mm, 70 * mm, "Datum")
            y = self.y - 21.5 * mm
        else:
            self.text(M, self.y - 5 * mm, FIRMA, 10, True, ACCENT)
            self.text(rx, self.y - 5 * mm, t, 10, True, ACCENT)
            self.feld(M, self.y - 11 * mm, 100 * mm, "Kunde / BV")
            self.feld(rx, self.y - 11 * mm, 34 * mm, "Nr.")
            self.feld(rx + 37 * mm, self.y - 11 * mm, 33 * mm, "Seite")
            y = self.y - 14 * mm
        self.hline(M, y, W - M, ACCENT, 1.2)
        self.y = y - GAP

    def fuss(self):
        self.text(M, 7 * mm, "Alle Maße in mm, sofern nicht anders angegeben · Kritische Maße 2× messen", 6.5,
                  color=MUTED)
        s = f"{self.blatt['titel'].title()} · Formular {self.nr}/{self.gesamt}"
        self.text(W - M - self.w(s, 6.5), 7 * mm, s, 6.5, color=MUTED)

    # ---------------- Zeilen ----------------
    def zeile(self, row, y, zeichnen):
        """Zeichnet eine Zeile mit Grundlinie y; gibt die benötigte Höhe zurück."""
        x0, x1 = M + 3 * mm, M + CW - 3 * mm
        art = row[0]
        if art == "felder":
            items = row[1]
            gap = 5 * mm
            total = sum(g for _, g in items)
            frei = (x1 - x0) - gap * (len(items) - 1)
            x = x0
            for label, g in items:
                b = frei * g / total
                if zeichnen:
                    self.feld(x, y, b, label)
                x += b + gap
            return LH
        if art == "linien":
            if zeichnen:
                for i in range(row[1]):
                    self.hline(x0, y - i * LH, x1)
            return row[1] * LH
        if art == "hinweis":
            if zeichnen:
                self.text(x0, y + 1 * mm, row[1], 6.5, color=MUTED)
            return HINWEIS_H
        if art == "kaestchen":
            _, label, items, rest = row
            if zeichnen:
                self.text(x0, y + 0.3 * mm, label, 8, True)
            xs = x0 + LABEL_W if label else x0
            x, yy, h = xs, y, LH
            for it in items:
                bw = BOX + 1.5 * mm + self.w(it)
                if x + bw > x1 and x > xs:
                    x, yy, h = xs, yy - LH, h + LH
                if zeichnen:
                    self.kaestchen(x, yy, it)
                x += bw + 4.5 * mm
            if rest:
                need = self.w(rest, 7.5) + 2 * mm + 18 * mm
                if x + need > x1:
                    x, yy, h = xs, yy - LH, h + LH
                if zeichnen:
                    self.feld(x, yy, x1 - x, rest)
            return h
        raise ValueError(f"Unbekannter Zeilentyp: {art}")

    def platz(self, hoehe):
        if self.y - hoehe < UNTEN:
            raise SystemExit(f"[{self.blatt['datei']}] Seite {self.nr} läuft über – "
                             f"Abschnitt kürzen oder auf Seite 2 verschieben.")

    def balken(self, titel):
        self.abschnitt += 1
        self.c.setFillColor(ACCENT)
        self.c.rect(M, self.y - BAR, CW, BAR, stroke=0, fill=1)
        self.text(M + 2.5 * mm, self.y - BAR + 1.9 * mm, f"{self.abschnitt}  {titel.upper()}", 8.5, True, white)

    def rahmen(self, top, hoehe):
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.6)
        self.c.rect(M, top - hoehe, CW, hoehe, stroke=1, fill=0)

    # ---------------- Abschnitte ----------------
    def abschnitt_zeichnen(self, a):
        if a.get("unterschrift"):
            return self.unterschrift()
        if "tabelle" in a:
            return self.tabelle(a)
        inhalt = PAD + sum(self.zeile(r, 0, False) for r in a["rows"]) + PAD
        self.platz(BAR + inhalt)
        top = self.y
        self.balken(a["titel"])
        y = top - BAR - PAD
        for r in a["rows"]:
            base = y - HINWEIS_H + 0.8 * mm if r[0] == "hinweis" else y - LH + 2.2 * mm
            y -= self.zeile(r, base, True)
        self.rahmen(top, BAR + inhalt)
        self.y = top - BAR - inhalt - GAP

    def tabelle(self, a):
        t = a["tabelle"]
        rh = LH
        hoehe = BAR + rh * (t["zeilen"] + 1)
        self.platz(hoehe)
        top = self.y
        self.balken(a["titel"])
        widths = [b * mm for _, b in t["spalten"]]
        widths[-1] = CW - sum(widths[:-1])
        ty = top - BAR
        self.c.setFillColor(FILL)
        self.c.rect(M, ty - rh, CW, rh, stroke=0, fill=1)
        x = M
        for (name, _), b in zip(t["spalten"], widths):
            self.text(x + 1.5 * mm, ty - rh + 2.8 * mm, name, 7.5, True)
            x += b
        for r in range(t["zeilen"] + 1):
            self.hline(M, ty - rh - r * rh, M + CW)
        self.c.setStrokeColor(LINE)
        x = M
        for b in widths[:-1]:
            x += b
            self.c.line(x, ty, x, ty - rh * (t["zeilen"] + 1))
        self.rahmen(top, hoehe)
        self.y = top - hoehe - GAP

    def unterschrift(self):
        self.platz(22 * mm)
        self.text(M, self.y - 2 * mm, "Die Maße wurden gemeinsam vor Ort aufgenommen. Grundlage für Angebot und "
                                      "Fertigung sind die oben angegebenen Maße und Bezugshöhen.", 7, color=MUTED)
        ys = self.y - 16 * mm
        half = CW / 2 - 4 * mm
        for i, wer in enumerate(["Ort, Datum · Unterschrift Kunde", f"Unterschrift {FIRMA}"]):
            xx = M + i * (half + 8 * mm)
            self.hline(xx, ys, xx + half)
            self.text(xx, ys - 3.5 * mm, wer, 7, color=MUTED)
        self.y = ys - 8 * mm

    # ---------------- Skizze ----------------
    def skizze(self, art):
        y = self.y - 3 * mm
        self.text(M, y + 0.3 * mm, "Skizze", 8, True)
        x = M + 15 * mm
        for it in ["Ansicht", "Draufsicht", "Schnitt", "Detail"]:
            self.kaestchen(x, y, it)
            x += BOX + 1.5 * mm + self.w(it) + 4.5 * mm
        self.feld(x + 2 * mm, y, 30 * mm, "Pos.")
        self.feld(x + 36 * mm, y, M + CW - (x + 36 * mm), "Blickrichtung")
        top = y - 5 * mm
        if art == "tuer":
            top = self.tuer_schema(top) - 4 * mm
        self.raster(top, 16 * mm)

    def raster(self, top, bottom):
        step = 5 * mm
        nx, ny = int(CW // step), int((top - bottom) // step)
        gw, gh = nx * step, ny * step
        gx, gy = M + (CW - gw) / 2, top - gh
        c = self.c
        c.setLineWidth(0.3)
        for i in range(nx + 1):
            c.setStrokeColor(GRID_MAJOR if i % 2 == 0 else GRID)
            c.line(gx + i * step, gy, gx + i * step, top)
        for j in range(ny + 1):
            c.setStrokeColor(GRID_MAJOR if j % 2 == 0 else GRID)
            c.line(gx, gy + j * step, gx + gw, gy + j * step)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.8)
        c.rect(gx, gy, gw, gh, stroke=1, fill=0)
        self.text(gx, gy - 4 * mm, "Raster 5 mm · Bezugspunkte (OKFF, Meterriss, Wandflucht) einzeichnen · "
                                   "Kettenmaße + Gesamtmaß", 6.5, color=MUTED)

    def pfeil_h(self, x1, x2, y, label):
        c = self.c
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.7)
        c.line(x1, y, x2, y)
        for xx, d in ((x1, 1), (x2, -1)):
            c.line(xx, y, xx + d * 1.6 * mm, y + 0.9 * mm)
            c.line(xx, y, xx + d * 1.6 * mm, y - 0.9 * mm)
        lw = self.w(label, 7, True)
        c.setFillColor(white)
        c.rect((x1 + x2) / 2 - lw / 2 - 1, y - 1.2 * mm, lw + 2, 2.6 * mm, stroke=0, fill=1)
        self.text((x1 + x2) / 2 - lw / 2, y - 0.9 * mm, label, 7, True, ACCENT)

    def pfeil_v(self, x, y1, y2, label):
        c = self.c
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.7)
        c.line(x, y1, x, y2)
        for yy, d in ((y1, 1), (y2, -1)):
            c.line(x, yy, x + 0.9 * mm, yy + d * 1.6 * mm)
            c.line(x, yy, x - 0.9 * mm, yy + d * 1.6 * mm)
        lw = self.w(label, 7, True)
        c.setFillColor(white)
        c.rect(x - lw / 2 - 1, (y1 + y2) / 2 - 1.3 * mm, lw + 2, 2.8 * mm, stroke=0, fill=1)
        self.text(x - lw / 2, (y1 + y2) / 2 - 0.9 * mm, label, 7, True, ACCENT)

    def tuer_schema(self, top):
        """Messschema lichte Wandöffnung: 3× Breite, 2× Höhe, Wanddicke, Meterriss."""
        c = self.c
        h = 62 * mm
        c.setFillColor(FILL)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.rect(M, top - h, CW, h, stroke=1, fill=1)
        # Ansicht Wandöffnung
        ox, ow, oh = M + 22 * mm, 38 * mm, 48 * mm
        floor = top - h + 7 * mm
        c.setFillColor(HexColor("#C9D1DA"))
        c.rect(ox - 12 * mm, floor, 12 * mm, oh + 5 * mm, stroke=0, fill=1)
        c.rect(ox + ow, floor, 12 * mm, oh + 5 * mm, stroke=0, fill=1)
        c.rect(ox, floor + oh, ow, 5 * mm, stroke=0, fill=1)
        self.hline(ox - 16 * mm, floor, ox + ow + 16 * mm, TEXT, 1)
        self.text(ox + ow + 13 * mm, floor + 1 * mm, "OKFF", 6.5, True)
        c.setDash(2, 2)
        self.hline(ox - 16 * mm, floor + 20 * mm, ox + ow + 16 * mm, HexColor("#B04A2F"), 0.7)
        c.setDash()
        self.text(ox + ow + 13 * mm, floor + 21 * mm, "Meterriss", 6.5, True, HexColor("#B04A2F"))
        self.pfeil_h(ox, ox + ow, floor + oh - 4 * mm, "B oben")
        self.pfeil_h(ox, ox + ow, floor + oh / 2 + 3 * mm, "B Mitte")
        self.pfeil_h(ox, ox + ow, floor + 6 * mm, "B unten")
        self.pfeil_v(ox + 6 * mm, floor, floor + oh, "H li")
        self.pfeil_v(ox + ow - 6 * mm, floor, floor + oh, "H re")
        # Draufsicht Wanddicke
        dx, dy = M + 92 * mm, top - 20 * mm
        c.setFillColor(HexColor("#C9D1DA"))
        c.rect(dx, dy, 18 * mm, 10 * mm, stroke=0, fill=1)
        c.rect(dx + 36 * mm, dy, 18 * mm, 10 * mm, stroke=0, fill=1)
        self.pfeil_v(dx + 9 * mm, dy, dy + 10 * mm, "W")
        self.text(dx, dy + 12 * mm, "Draufsicht: Wanddicke W (fertig, inkl. Putz)", 6.5, True)
        # Erklärung
        tx = M + 92 * mm
        zeilen = [
            "So messen:",
            "• Breite an 3 Stellen, Höhe links + rechts – das kleinste Maß zählt",
            "• Höhe immer ab OK Fertigfußboden; fehlt der Boden: Meterriss",
            "  suchen / anzeichnen und Höhe von dort abtragen",
            "• Wanddicke im fertigen Zustand (Putz, Fliese) messen",
            "• Diagonalen messen, wenn die Öffnung schief wirkt",
            "• DIN-Richtung: Blick auf Bandseite, Bänder links = DIN links",
        ]
        for i, z in enumerate(zeilen):
            self.text(tx, top - 28 * mm - i * 4.2 * mm, z, 7, i == 0)
        return top - h


def seiten_fuer(blatt):
    return blatt["seiten"]


def zeichne(c, blatt, nr, seite, gesamt):
    # Abschnittsnummern laufen über die Seiten weiter
    start = sum(1 for art, inh in blatt["seiten"][:nr - 1] if art == "abschnitte"
                for a in inh if not a.get("unterschrift"))
    s = Seite(c, blatt, nr, gesamt, start)
    s.kopf()
    art, inhalt = seite
    if art == "abschnitte":
        for a in inhalt:
            s.abschnitt_zeichnen(a)
    else:
        s.skizze(inhalt)
    s.fuss()


def baue(blatt, ziel: Path):
    ziel.mkdir(parents=True, exist_ok=True)
    seiten = seiten_fuer(blatt)
    n = len(seiten)

    def pdf(pfad, nummern):
        c = canvas.Canvas(str(pfad), pagesize=A4)
        c.setTitle(f"{blatt['titel'].title()} – {FIRMA}")
        c.setAuthor(FIRMA)
        for i in nummern:
            zeichne(c, blatt, i + 1, seiten[i], n)
            c.showPage()
        c.save()

    pdf(ziel / f"{blatt['datei']}_komplett.pdf", range(n))
    for i in range(n):
        pdf(ziel / f"{blatt['datei']}_S{i + 1}.pdf", [i])


if __name__ == "__main__":
    base = Path(__file__).parent / "ausgabe"
    for b in BLAETTER:
        baue(b, base / b["datei"])
        print("erstellt:", b["datei"])
