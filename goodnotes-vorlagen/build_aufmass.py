"""Erzeugt das Aufmaßblatt (A4) für Goodnotes.

Aufruf:  python3 build_aufmass.py
Ausgabe: Aufmassblatt_komplett.pdf (3 Seiten) + Einzelseiten für den Vorlagen-Import.
"""
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent

FIRMA = "Middendorf Metallbau OHG"
FIRMA_ZEILE = "Ottostraße 4 · 26899 Rhede (Ems) · Tel. 04964 / 91 99 05-0 · info@mb-middendorf.de · www.mb-middendorf.de"

W, H = A4
M = 12 * mm                      # Seitenrand
CW = W - 2 * M                   # nutzbare Breite

ACCENT = HexColor("#1F3A5F")     # Stahlblau
LINE = HexColor("#9AA5B1")
GRID = HexColor("#D5DBE1")
GRID_MAJOR = HexColor("#B4BEC8")
TEXT = HexColor("#1A1A1A")
MUTED = HexColor("#5B6670")
FILL = HexColor("#EEF2F6")


class Page:
    def __init__(self, c: canvas.Canvas):
        self.c = c
        self.y = H - M

    # ---------- Grundbausteine ----------
    def text(self, x, y, s, size=8, bold=False, color=TEXT):
        self.c.setFillColor(color)
        self.c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        self.c.drawString(x, y, s)

    def field(self, x, y, w, label, size=7.5):
        """Beschriftete Schreiblinie; y = Grundlinie."""
        self.text(x, y + 1.2, label, size, color=MUTED)
        lw = self.c.stringWidth(label, "Helvetica", size) + 2 * mm
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.5)
        self.c.line(x + lw, y, x + w, y)

    def box(self, x, y, label, size=8):
        """Ankreuzkästchen; gibt x-Position hinter dem Text zurück."""
        s = 3.8 * mm
        self.c.setStrokeColor(TEXT)
        self.c.setLineWidth(0.6)
        self.c.rect(x, y - 0.4 * mm, s, s, stroke=1, fill=0)
        self.text(x + s + 1.5 * mm, y + 0.3 * mm, label, size)
        return x + s + 1.5 * mm + self.c.stringWidth(label, "Helvetica", size)

    def box_row(self, x, y, items, gap=5 * mm, size=8):
        for it in items:
            x = self.box(x, y, it, size) + gap
        return x

    def line_after(self, x, y, x2):
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.5)
        self.c.line(x, y, x2, y)

    def section(self, nr, title, height):
        """Abschnittsrahmen mit Titelleiste; gibt Oberkante des Inhalts zurück."""
        bar = 6 * mm
        top = self.y
        self.c.setFillColor(ACCENT)
        self.c.rect(M, top - bar, CW, bar, stroke=0, fill=1)
        self.text(M + 2.5 * mm, top - bar + 1.9 * mm, f"{nr}  {title.upper()}", 8.5, True, white)
        self.c.setStrokeColor(LINE)
        self.c.setLineWidth(0.6)
        self.c.rect(M, top - bar - height, CW, height + bar, stroke=1, fill=0)
        self.y = top - bar - height - 3.5 * mm
        return top - bar

    def label(self, x, y, s):
        self.text(x, y, s, 8, True)

    # ---------- Kopf ----------
    def header(self, small=False):
        c = self.c
        if small:
            self.text(M, self.y - 5 * mm, FIRMA, 10, True, ACCENT)
            self.text(W - M - 62 * mm, self.y - 5 * mm, "AUFMASSBLATT", 10, True, ACCENT)
            self.field(W - M - 62 * mm, self.y - 11 * mm, 30 * mm, "Nr.")
            self.field(W - M - 29 * mm, self.y - 11 * mm, 29 * mm, "Seite")
            self.field(M, self.y - 11 * mm, 95 * mm, "Kunde / BV")
            y = self.y - 14 * mm
        else:
            self.text(M, self.y - 6 * mm, FIRMA, 15, True, ACCENT)
            self.text(M, self.y - 11 * mm, FIRMA_ZEILE, 6.8, color=MUTED)
            self.text(W - M - 62 * mm, self.y - 6 * mm, "AUFMASSBLATT", 15, True, ACCENT)
            self.field(W - M - 62 * mm, self.y - 12.5 * mm, 30 * mm, "Nr.")
            self.field(W - M - 29 * mm, self.y - 12.5 * mm, 29 * mm, "Seite")
            self.field(W - M - 62 * mm, self.y - 18.5 * mm, 62 * mm, "Datum")
            y = self.y - 21.5 * mm
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.2)
        c.line(M, y, W - M, y)
        self.y = y - 3.5 * mm

    def footer(self, n):
        self.text(M, 7 * mm, "Alle Maße in mm, sofern nicht anders angegeben · Kritische Maße 2× messen",
                  6.5, color=MUTED)
        self.text(W - M - 22 * mm, 7 * mm, f"Formular {n}/3", 6.5, color=MUTED)


# ======================================================================
def page1(c):
    p = Page(c)
    p.header()
    x1, x2 = M + 3 * mm, M + CW / 2 + 2 * mm
    cw = CW / 2 - 5 * mm
    lh = 8 * mm

    # 1 Auftraggeber & Baustelle
    top = p.section("1", "Auftraggeber & Baustelle", 5 * lh + 2 * mm)
    left = ["Kunde", "Straße", "PLZ / Ort", "Telefon", "E-Mail"]
    right = ["Baustelle (falls abw.)", "Ansprechpartner vor Ort", "Tel. vor Ort", "Angebot / Auftrag-Nr.",
             "Aufgenommen von"]
    for i, (a, b) in enumerate(zip(left, right)):
        yy = top - (i + 1) * lh
        p.field(x1, yy, cw, a)
        p.field(x2, yy, cw, b)

    # 2 Bauteil
    top = p.section("2", "Bauteil", 2 * lh + 2 * mm)
    p.box_row(x1, top - lh + 1 * mm, ["Geländer / Brüstung", "Treppe", "Balkon", "Vordach", "Tor", "Tür",
                                        "Zaun"])
    xe = p.box_row(x1, top - 2 * lh + 1.5 * mm, ["Carport / Überdachung", "Bühne / Podest", "Gitterrost",
                                                  "Stalleinrichtung", "Sonstiges:"])
    p.line_after(xe - 3 * mm, top - 2 * lh + 1.5 * mm, M + CW - 33 * mm)
    p.field(M + CW - 30 * mm, top - 2 * lh + 1.5 * mm, 27 * mm, "Anzahl")

    # 3 Ausführung
    top = p.section("3", "Ausführung", 4 * lh + 2 * mm)
    rows = [
        ("Material", ["Stahl", "Edelstahl V2A", "Edelstahl V4A", "Aluminium"]),
        ("Oberfläche", ["feuerverzinkt", "verzinkt + pulverbesch.", "pulverbeschichtet", "roh / grundiert"]),
        ("Füllung", ["Stäbe senkrecht", "Querstäbe", "Lochblech", "Glas (VSG)", "Streckmetall", "ohne"]),
        ("Handlauf", ["Rundrohr Ø ____", "Flachstahl", "Edelstahl", "Holz", "ohne"]),
    ]
    for i, (lab, items) in enumerate(rows):
        yy = top - (i + 1) * lh + 1.5 * mm
        p.label(x1, yy + 0.3 * mm, lab)
        xe = p.box_row(x1 + 22 * mm, yy, items, gap=4 * mm)
        if lab == "Oberfläche":
            p.field(xe, yy, M + CW - 3 * mm - xe, "RAL")

    # 4 Einbausituation
    top = p.section("4", "Einbausituation", 5 * lh + 2 * mm)
    yy = top - lh + 1.5 * mm
    p.label(x1, yy + 0.3 * mm, "Untergrund")
    xe = p.box_row(x1 + 22 * mm, yy, ["Beton", "Mauerwerk", "Holz", "Stahl", "Naturstein / Fliese", "WDVS"],
                   gap=4 * mm)
    p.field(xe, yy, M + CW - 3 * mm - xe, "Dämmung cm")
    yy -= lh
    p.label(x1, yy + 0.3 * mm, "Befestigung")
    p.box_row(x1 + 22 * mm, yy, ["aufgesetzt (Draufsicht)", "seitlich / stirnseitig", "Ankerplatte",
                                  "einbetoniert", "angeschweißt"], gap=4 * mm)
    yy -= lh
    p.label(x1, yy + 0.3 * mm, "Bezugshöhe")
    xe = p.box_row(x1 + 22 * mm, yy, ["OK Fertigfußboden", "Rohbau"], gap=4 * mm)
    p.field(xe, yy, x1 + 118 * mm - xe, "fehlender Aufbau cm")
    p.field(x1 + 123 * mm, yy, M + CW - 3 * mm - (x1 + 123 * mm), "Gefälle %")
    yy -= lh
    p.label(x1, yy + 0.3 * mm, "Prüfen")
    p.box_row(x1 + 22 * mm, yy, ["Leitungen im Bohrbereich geklärt", "Abdichtung / Durchdringung beachtet",
                                  "Statik erforderlich"], gap=4 * mm)
    yy -= lh
    p.box_row(x1 + 22 * mm, yy, ["Lot / Waage geprüft (Toleranzen notiert)", "Denkmalschutz / Genehmigung"],
              gap=4 * mm)

    # 5 Absturzsicherung
    top = p.section("5", "Absturzsicherung  (Geländer · Brüstung · Treppe · Bühne)", 3 * lh + 6 * mm)
    yy = top - lh + 1 * mm
    p.field(x1, yy, 52 * mm, "Absturzhöhe m")
    p.field(x1 + 56 * mm, yy, 55 * mm, "Geländerhöhe cm")
    p.label(x1 + 116 * mm, yy + 0.3 * mm, "Kinder zu erwarten")
    p.box_row(x1 + 148 * mm, yy, ["ja", "nein"], gap=4 * mm)
    yy -= lh
    p.label(x1, yy + 0.3 * mm, "Nutzung")
    p.box_row(x1 + 22 * mm, yy, ["privat", "gewerblich / Arbeitsstätte", "öffentlich"], gap=4 * mm)
    yy -= lh
    p.label(x1, yy + 0.3 * mm, "Treppe")
    p.field(x1 + 22 * mm, yy, 40 * mm, "Steigung")
    p.field(x1 + 66 * mm, yy, 40 * mm, "Auftritt")
    p.field(x1 + 110 * mm, yy, M + CW - 3 * mm - (x1 + 110 * mm), "Laufbreite")
    p.text(x1, yy - 5 * mm,
           "Richtwerte, gegen LBO / ASR / DIN 18065 prüfen: Höhe i. d. R. mind. 90 cm, ab 12 m Absturzhöhe "
           "mind. 110 cm · Öffnungen max. 12 cm · kein Leitereffekt bei Kindern.", 6.5, color=MUTED)
    p.footer(1)


def page2(c):
    p = Page(c)
    p.header(small=True)
    x1 = M + 3 * mm
    lh = 7.6 * mm

    # 6 Baustelle & Montage
    top = p.section("6", "Baustelle & Montage", 4 * lh + 2 * mm)
    yy = top - lh + 1.5 * mm
    p.label(x1, yy + 0.3 * mm, "Zufahrt LKW")
    xe = p.box_row(x1 + 26 * mm, yy, ["ja", "nein"], gap=4 * mm)
    p.label(xe + 6 * mm, yy + 0.3 * mm, "Hebezeug")
    p.box_row(xe + 26 * mm, yy, ["Kran", "Hubsteiger", "von Hand", "Gerüst vorhanden"], gap=4 * mm)
    yy -= lh
    p.label(x1, yy + 0.3 * mm, "Strom vor Ort")
    xe = p.box_row(x1 + 26 * mm, yy, ["230 V", "400 V", "nein"], gap=4 * mm)
    p.field(xe + 6 * mm, yy, 40 * mm, "Etage")
    p.field(xe + 50 * mm, yy, M + CW - 3 * mm - (xe + 50 * mm), "engster Durchgang cm")
    yy -= lh
    p.field(x1, yy, 60 * mm, "Fotos gemacht (Anzahl)")
    p.field(x1 + 64 * mm, yy, M + CW - 3 * mm - (x1 + 64 * mm), "Montage gewünscht bis / Zeitfenster")
    yy -= lh
    p.field(x1, yy, CW - 6 * mm, "Zugang / Schlüssel / Hinweise")

    # 7 Maßtabelle
    rows = 14
    rh = 8 * mm
    top = p.section("7", "Maße", rows * rh + rh)
    cols = [("Pos.", 12), ("Bezeichnung / Bauteil", 62), ("Länge", 22), ("Breite", 22), ("Höhe", 22),
            ("Stk.", 12), ("Bemerkung", 0)]
    widths = [w * mm for _, w in cols]
    widths[-1] = CW - sum(widths[:-1])
    c.setFillColor(FILL)
    c.rect(M, top - rh, CW, rh, stroke=0, fill=1)
    x = M
    for (name, _), w in zip(cols, widths):
        p.text(x + 1.5 * mm, top - rh + 2.4 * mm, name, 7.5, True)
        x += w
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for r in range(1, rows + 1):
        c.line(M, top - rh - r * rh, M + CW, top - rh - r * rh)
    c.line(M, top - rh, M + CW, top - rh)
    x = M
    for w in widths[:-1]:
        x += w
        c.line(x, top, x, top - rh - rows * rh)

    # 8 Bemerkungen
    top = p.section("8", "Bemerkungen / Sonderwünsche", 4 * lh)
    for i in range(1, 5):
        p.line_after(x1, top - i * lh + 1 * mm, M + CW - 3 * mm)

    # Bestätigung
    p.text(M, p.y - 2 * mm,
           "Die Maße wurden gemeinsam vor Ort aufgenommen. Grundlage für Angebot und Fertigung sind die oben "
           "angegebenen Maße und die Bezugshöhe.", 7, color=MUTED)
    ys = p.y - 17 * mm
    half = CW / 2 - 4 * mm
    for i, who in enumerate(["Ort, Datum · Unterschrift Kunde", "Unterschrift Middendorf Metallbau OHG"]):
        xx = M + i * (half + 8 * mm)
        p.line_after(xx, ys, xx + half)
        p.text(xx, ys - 3.5 * mm, who, 7, color=MUTED)
    p.footer(2)


def page3(c):
    p = Page(c)
    p.header(small=True)
    x1 = M + 3 * mm
    yy = p.y - 3 * mm
    p.label(M, yy + 0.3 * mm, "Skizze")
    xe = p.box_row(M + 15 * mm, yy, ["Ansicht", "Draufsicht", "Schnitt", "Detail"], gap=4 * mm)
    p.field(xe + 2 * mm, yy, 30 * mm, "Pos.")
    p.field(xe + 36 * mm, yy, M + CW - (xe + 36 * mm), "Blickrichtung")
    # 5-mm-Raster, jede 1 cm-Linie kräftiger
    top = yy - 5 * mm
    bottom = 16 * mm
    step = 5 * mm
    nx = int(CW // step)
    ny = int((top - bottom) // step)
    gw, gh = nx * step, ny * step
    gx = M + (CW - gw) / 2
    gy = top - gh
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
    p.text(gx, gy - 4 * mm,
           "Raster 5 mm · Bezugspunkte (OKFF, Wandflucht) einzeichnen · Kettenmaße + Gesamtmaß · Diagonalen bei "
           "Rahmen/Toren", 6.5, color=MUTED)
    p.footer(3)


PAGES = [page1, page2, page3]
NAMES = ["Aufmass_1_Daten", "Aufmass_2_Masse", "Aufmass_3_Skizze"]


def build(path, funcs):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Aufmaßblatt – Middendorf Metallbau OHG")
    c.setAuthor(FIRMA)
    for f in funcs:
        f(c)
        c.showPage()
    c.save()


if __name__ == "__main__":
    build(OUT / "Aufmassblatt_komplett.pdf", PAGES)
    for f, n in zip(PAGES, NAMES):
        build(OUT / f"{n}.pdf", [f])
    print("fertig")
