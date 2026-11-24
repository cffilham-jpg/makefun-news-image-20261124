#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Tuesday 24 November 2026.

Draws a one-day world news broadsheet (1024x1024 PNG) using only the
Python standard library. No network, no fonts on disk: text is rendered
with a built-in 5x7 bitmap font, scaled up so every word stays legible
at a 300px thumbnail.

Stories: the 15 verified stories in the build brief for 24 Nov 2026 only.
Numbers used: 14, $2.5M, 20, 12, 400, $3tn - all verified in the brief.
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (250, 247, 240)
INK = (11, 31, 58)
RED = (200, 16, 46)
GOLD = (176, 141, 45)
GOLD_BG = (246, 232, 196)
NAVY2 = (18, 48, 88)
GREY = (90, 96, 110)
LIGHT = (232, 228, 219)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = on. All copy is upper-cased before drawing.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}
# Middot / bullet drawn as a filled square by the text code.
FONT['\u00b7'] = ("00000", "00000", "01110", "01110", "01110", "00000", "00000")

CHAR_W = 6  # 5 px glyph + 1 px gap, times scale


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            row = bytes(c) * w
            self.px[base:base + 3 * w] = row

    def border(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=2):
        self.rect(x, y, w, t, c)

    def draw_char(self, x, y, ch, scale, c):
        g = FONT.get(ch)
        if g is None:
            return
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + col * scale, y + r * scale, scale, scale, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            self.draw_char(cx, y, ch, scale, c)
            cx += CHAR_W * scale
        return cx

    def text_center(self, x, y, w, s, scale, c):
        tw = text_width(s.upper(), scale)
        self.text(x + (w - tw) // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines, each <= max_w px."""
        words = s.upper().split()
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_w, leading=None):
        if leading is None:
            leading = 7 * scale + 3
        for line in self.wrap(s, scale, max_w):
            self.text(x, y, line, scale, c)
            y += leading
        return y

    def pill(self, x, y, label, scale, fg, bg):
        w = text_width(label, scale) + 10 * scale // 2 + 8
        h = 7 * scale + 8
        self.rect(x, y, w, h, bg)
        self.text(x + 5, y + 4, label, scale, fg)
        return w


def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- layout
MX = 16          # side margin
CW = 320         # column width (3 cols, 12px gutters: 16*2 + 320*3 + 12*2 = 1024)
GUT = 12


def col_x(i):
    return MX + i * (CW + GUT)


def draw_masthead(cv):
    cv.rect(0, 0, W, 10, RED)
    # Title, left.
    cv.text(MX, 22, "THE WORLD IN ONE DAY", 5, INK)
    cv.text(MX, 66, "TUESDAY 24 NOVEMBER 2026", 3, RED)
    # DATE CHECK box, right.
    bx, by, bw, bh = 680, 20, 328, 66
    cv.border(bx, by, bw, bh, INK, 3)
    cv.text(bx + 12, by + 8, "DATE CHECK", 2, RED)
    cv.para(bx + 12, by + 28, "All stories from 24 Nov editions and wires.", 2, INK, bw - 24)
    cv.hline(MX, 96, W - 2 * MX, INK, 3)


def draw_timeline(cv):
    y = 106
    cv.rect(MX, y, W - 2 * MX, 34, INK)
    cv.text_center(MX, y + 10, W - 2 * MX,
                   "04:37 FIRST WIRE  -  06:36 MARKETS SURGE  -  15:00 CET GAME 1  -  19:00 TASHKENT",
                   2, WHITE)


NUMBERS = [
    ("14", "CHESS GAMES"),
    ("$2.5M", "CHESS PRIZE"),
    ("20", "AGE OF BOTH"),
    ("12", "DEM DEBATES"),
    ("400", "RS CRORE PARK"),
    ("$3TN", "STOCKS ADDED"),
]


def draw_numbers(cv):
    y = 148
    cell = (W - 2 * MX) // 6
    for i, (num, label) in enumerate(NUMBERS):
        x = MX + i * cell
        if i % 2 == 0:
            cv.rect(x + 2, y, cell - 4, 76, LIGHT)
        else:
            cv.border(x + 2, y, cell - 4, 76, LIGHT, 2)
        cv.text_center(x, y + 10, cell, num, 4, RED if i != 2 else INK)
        cv.text_center(x, y + 48, cell, label, 2, INK)


def draw_regions(cv):
    y = 232
    cv.rect(MX, y, W - 2 * MX, 26, GOLD)
    cv.text_center(MX, y + 6, W - 2 * MX,
                   "EUROPE 3  -  ASIA 5  -  NORTH AMERICA 3  -  AFRICA 1  -  MIDDLE EAST 1  -  WORLD 2",
                   2, INK)


def chessboard(cv, x, y, sq):
    for r in range(8):
        for c in range(8):
            col = WHITE if (r + c) % 2 == 0 else INK
            cv.rect(x + c * sq, y + r * sq, sq, sq, col)
    cv.border(x, y, sq * 8, sq * 8, GOLD, 3)
    # A few pieces as dots: white king, black queen, pawns.
    for (r, c, col) in [(0, 3, INK), (0, 4, INK), (7, 4, RED), (7, 3, RED),
                        (1, 0, INK), (1, 7, INK), (6, 0, RED), (6, 7, RED)]:
        px, py = x + c * sq + sq // 4, y + r * sq + sq // 4
        cv.rect(px, py, sq // 2, sq // 2, col)


def draw_hero(cv, i, banner, title, body, pill, accent, board=False):
    x = col_x(i)
    y = 266
    h = 218
    cv.border(x, y, CW, h, INK, 3)
    cv.rect(x, y, CW, 30, accent)
    cv.text_center(x, y + 8, CW, banner, 2, WHITE)
    yy = y + 40
    if board:
        chessboard(cv, x + 12, yy, 11)
        tx = x + 112
        yy2 = cv.para(tx, yy + 2, title, 3, INK, CW - 124)
        cv.text(tx, yy2 + 4, "WHITE: SINDAROV", 2, RED)
        yy = yy + 96
        cv.para(x + 12, yy, body, 2, INK, CW - 24)
    else:
        yy = cv.para(x + 12, yy, title, 3, INK, CW - 24)
        yy += 4
        cv.para(x + 12, yy, body, 2, INK, CW - 24)
    cv.pill(x + 12, y + h - 30, pill, 2, WHITE, RED if pill == "CONFIRMED" else NAVY2)


CARDS = [
    ("ASIA", "INDIA-CHINA TALKS IN ARUNACHAL",
     "Military talks held in Arunachal Pradesh.", "CONFIRMED"),
    ("ASIA", "CJI: LEGAL AID MUST BE MANDATORY",
     "Calls for legal aid and AI rules in law courses.", "CONFIRMED"),
    ("ASIA", "CONGRESS-SP OPEN SEAT TALKS",
     "Seat-sharing talks open after 15-minute meeting.", "CONFIRMED"),
    ("N AMERICA", "DEMOCRATS PLAN 12 PRIMARY DEBATES",
     "12 debates from June 2027. No dark money.", "REPORTED"),
    ("AFRICA", "FOUR RSF COMMANDERS DEFECT",
     "UAE-backed commanders join Sudan army.", "REPORTED"),
    ("M EAST", "IRAN WAR FUNDS MAY BE CUT",
     "Thune, Collins open to cut to avoid shutdown.", "REPORTED"),
    ("WORLD", "FOSSIL SHARE OF POWER FALLING",
     "Fossil share of power falls from above 60%.", "REPORTED"),
    ("N AMERICA", "REPLIT CEO MET VP VANCE",
     "Met Friday on US AI leadership and cyber.", "REPORTED"),
    ("EUROPE", "DE BRUYNE: FEELINGS NEVER CHANGE",
     "On Man City: his feelings never change.", "CONFIRMED"),
    ("EUROPE", "WEIR: WORLD CUP, A DECADE OF JOY",
     "2035 Women's World Cup: a decade of joy.", "CONFIRMED"),
    ("WORLD", "SUPERMOON MEETS SEVEN SISTERS",
     "Supermoon meets the Pleiades tonight.", "CONFIRMED"),
]


def draw_card(cv, i, region, title, body, pill):
    row, col = divmod(i, 3)
    x = col_x(col)
    y = 496 + row * 106
    h = 96
    cv.border(x, y, CW, h, INK, 2)
    cv.rect(x, y, CW, 22, RED)
    cv.text(x + 10, y + 4, region, 2, WHITE)
    pw = text_width(pill, 2) + 18
    cv.pill(x + CW - 8 - pw, y, pill, 2, WHITE, INK)
    cv.para(x + 10, y + 28, title, 2, INK, CW - 20, leading=16)
    cv.para(x + 10, y + 62, body, 2, GREY, CW - 20, leading=15)


def draw_datecheck_cell(cv):
    x = col_x(2)
    y = 496 + 3 * 106
    h = 96
    cv.border(x, y, CW, h, INK, 3)
    cv.rect(x, y, CW, 22, INK)
    cv.text(x + 10, y + 4, "ABOUT THIS PAGE", 2, WHITE)
    cv.para(x + 10, y + 30, "15 STORIES. 6 REGIONS. ALL FROM 24 NOVEMBER 2026 EDITIONS AND WIRES.",
            2, INK, CW - 20)


def draw_mapstrip(cv):
    y = 926
    cv.rect(0, y, W, 98, INK)
    cv.text_center(0, y + 10, W, "AROUND THE WORLD TODAY", 3, GOLD_BG)
    dots = [("WASHINGTON", 150, 60), ("LONDON", 400, 78), ("GENEVA", 500, 60),
            ("KHARTOUM", 610, 78), ("DELHI", 720, 60), ("WELLINGTON", 880, 78)]
    for name, dx, ly in dots:
        cv.rect(dx, y + 50, 10, 10, GOLD)
        cv.text(dx - 20, y + ly, name, 2, WHITE)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_timeline(cv)
    draw_numbers(cv)
    draw_regions(cv)
    draw_hero(cv, 0, "GENEVA - GAME 1 TODAY",
              "GUKESH VS SINDAROV",
              "Begins 15:00 CET. 14 games. $2.5M. Both 20.",
              "CONFIRMED", GOLD, board=True)
    draw_hero(cv, 1, "NEW DELHI",
              "SC BAIL IN GODHRA CASE",
              "Supreme Court grants bail to a Godhra convict. Modi opens AI centre and Rs 400 crore park at IIT Patna.",
              "CONFIRMED", RED)
    draw_hero(cv, 2, "WALL STREET",
              "US STOCKS ADD $3 TRILLION",
              "Markets surge as Huang is reinstated after 11 days out. Board acted Monday after Trump pressure.",
              "REPORTED", NAVY2)
    for i, (region, title, body, pill) in enumerate(CARDS):
        draw_card(cv, i, region, title, body, pill)
    draw_datecheck_cell(cv)
    draw_mapstrip(cv)
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    cv = build()
    path = os.path.join(out, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
