#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""THE WORLD IN ONE PAGE - Sunday 22 November 2026.

A pure Python 3 standard-library program (no Pillow, no numpy, no
network) that draws a complete newspaper front page summing up the
world news of Sunday 22 November 2026 and writes it to entry.png.

The page is drawn on a 2048x2048 canvas (2x supersample) with flat
saturated shapes and a hand-built 5x7 pixel font, then box-downscaled
to 1024x1024 so every edge and letter stays sharp and colours stay
vivid. Output is deterministic: two runs write identical bytes.
"""

import os
import struct
import zlib

SS = 2                 # supersample factor
W = 1024 * SS          # render width
H = 1024 * SS          # render height

# ---------------------------------------------------------------- PNG out

def write_png(path, w, h, rgb):
    """Write an RGB bytearray (w*h*3) as a PNG file, stdlib only."""
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)

# ---------------------------------------------------------------- canvas

class Canvas:
    """A flat RGB framebuffer drawn in final-page coordinates.

    All drawing calls take coordinates in the 1024x1024 page space;
    they are scaled by SS internally so the render is supersampled.
    """

    def __init__(self, bg):
        self.px = bytearray(bg * (W * H))

    def _set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = col

    def rect(self, x, y, w, h, col):
        x0, y0 = int(x * SS), int(y * SS)
        x1, y1 = int((x + w) * SS), int((y + h) * SS)
        row = col * max(0, x1 - x0)
        for yy in range(max(0, y0), min(H, y1)):
            i = (yy * W + max(0, x0)) * 3
            self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, col, t=2):
        self.rect(x, y, w, t, col)
        self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col)
        self.rect(x + w - t, y, t, h, col)

    def line(self, x0, y0, x1, y1, col, t=2):
        x0, y0, x1, y1 = x0 * SS, y0 * SS, x1 * SS, y1 * SS
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        r = max(1, int(t * SS / 2))
        for s in range(steps + 1):
            cx = int(x0 + (x1 - x0) * s / steps)
            cy = int(y0 + (y1 - y0) * s / steps)
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r:
                        self._set(cx + dx, cy + dy, col)

    def circle(self, cx, cy, r, col, fill=True):
        cx, cy, r = cx * SS, cy * SS, r * SS
        x0, x1 = int(cx - r - 1), int(cx + r + 1)
        y0, y1 = int(cy - r - 1), int(cy + r + 1)
        for yy in range(max(0, y0), min(H, y1)):
            for xx in range(max(0, x0), min(W, x1)):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d2 <= r * r:
                    self._set(xx, yy, col)
                elif not fill and (r - SS) ** 2 <= d2 <= r * r:
                    self._set(xx, yy, col)

    def tri(self, pts, col):
        (ax, ay), (bx, by), (cx, cy) = [(p[0] * SS, p[1] * SS) for p in pts]
        x0 = int(min(ax, bx, cx)); x1 = int(max(ax, bx, cx))
        y0 = int(min(ay, by, cy)); y1 = int(max(ay, by, cy))
        def edge(px, py, qx, qy, rx, ry):
            return (px - rx) * (qy - ry) - (qx - rx) * (py - ry)
        for yy in range(max(0, y0), min(H, y1)):
            for xx in range(max(0, x0), min(W, x1)):
                d1 = edge(xx, yy, ax, ay, bx, by)
                d2 = edge(xx, yy, bx, by, cx, cy)
                d3 = edge(xx, yy, cx, cy, ax, ay)
                if (d1 >= 0 and d2 >= 0 and d3 >= 0) or \
                   (d1 <= 0 and d2 <= 0 and d3 <= 0):
                    self._set(xx, yy, col)

    def downscale(self):
        """Box-downscale the SS canvas to 1024x1024 RGB bytes."""
        out = bytearray(1024 * 1024 * 3)
        sw = W * 3
        for y in range(1024):
            for x in range(1024):
                r = g = b = 0
                for dy in range(SS):
                    base = ((y * SS + dy) * W + x * SS) * 3
                    for dx in range(SS):
                        i = base + dx * 3
                        r += self.px[i]; g += self.px[i + 1]; b += self.px[i + 2]
                o = (y * 1024 + x) * 3
                n = SS * SS
                out[o] = r // n; out[o + 1] = g // n; out[o + 2] = b // n
        return out

# ---------------------------------------------------------------- font
# Hand-built 5x7 pixel font. Each glyph is 7 rows; each row is a 5-bit
# integer, bit 4 = leftmost pixel.

FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "%": (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "·": (0, 0, 0, 0x0C, 0x0C, 0, 0),
    "£": (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x1F),
}

def text_w(s, u, adv=6.0):
    """Width in page px of string s at font unit u."""
    return len(s) * adv * u

def draw_text(cv, x, y, s, u, col, adv=6.0):
    """Draw s with its top-left at (x, y); u = px per font pixel."""
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for b in range(5):
                if bits & (1 << (4 - b)):
                    cv.rect(cx + b * u, y + row * u, u, u, col)
        cx += adv * u
    return cx - x

def draw_center(cv, cx, y, s, u, col, adv=6.0):
    w = text_w(s, u, adv)
    draw_text(cv, cx - w / 2, y, s, u, col, adv)
    return w

def wrap(s, u, maxw, adv=6.0):
    """Greedy word wrap to lines of at most maxw page px."""
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, u, adv) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def draw_block(cv, x, y, s, u, col, maxw, pitch=None, adv=6.0, maxlines=99):
    """Draw wrapped text; returns the y just past the last line."""
    pitch = pitch or (9.5 * u)
    lines = wrap(s, u, maxw, adv)[:maxlines]
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * pitch, ln, u, col, adv)
    return y + len(lines) * pitch

# ---------------------------------------------------------------- palette

PAPER = bytes((247, 240, 221))
CARD = bytes((255, 253, 246))
INK = bytes((20, 26, 43))
RED = bytes((206, 32, 40))
BLUE = bytes((26, 74, 196))
SKY = bytes((52, 144, 220))
TEAL = bytes((8, 128, 122))
ORANGE = bytes((244, 118, 0))
YELLOW = bytes((250, 186, 40))
GREEN = bytes((28, 142, 84))
PURPLE = bytes((102, 70, 160))
GREY = bytes((92, 100, 114))
LGREY = bytes((198, 200, 192))
WHITE = bytes((255, 255, 255))
DARK = bytes((26, 30, 42))
BROWN = bytes((146, 92, 44))

# ---------------------------------------------------------------- scenes

def burst(cv, cx, cy, r, col):
    """An 8-point explosion star."""
    import math
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    for i in range(16):
        cv.tri([pts[i], pts[(i + 1) % 16], (cx, cy)], col)

def flame(cv, x, y, w, h):
    """A simple two-tone flame in a box."""
    cv.tri([(x + w / 2, y), (x + w, y + h), (x, y + h)], ORANGE)
    cv.tri([(x + w / 2, y + h * 0.35), (x + w * 0.78, y + h),
            (x + w * 0.22, y + h)], YELLOW)

def ill_kyiv(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((38, 48, 84)))
    bx, bw = x + w * 0.4, w * 0.34
    cv.rect(bx, y + h * 0.2, bw, h * 0.8, bytes((168, 156, 138)))
    for r in range(3):
        for c in range(3):
            lit = (r * 3 + c) % 3 != 2
            cv.rect(bx + 9 + c * (bw - 14) / 3, y + h * 0.28 + r * h * 0.22,
                    (bw - 14) / 3 - 8, h * 0.12,
                    YELLOW if lit else bytes((70, 76, 96)))
    cv.tri([(bx + bw, y + h * 0.2), (bx + bw, y + h * 0.55),
            (bx + bw * 0.6, y + h * 0.42)], bytes((38, 48, 84)))
    burst(cv, bx + bw * 0.82, y + h * 0.3, w * 0.055, ORANGE)
    burst(cv, bx + bw * 0.82, y + h * 0.3, w * 0.03, YELLOW)
    cv.circle(bx + bw * 0.55, y + h * 0.14, 9, GREY)
    cv.circle(bx + bw * 0.68, y + h * 0.08, 12, GREY)
    cv.rect(x + w * 0.1, y + h * 0.3, w * 0.11, h * 0.045, LGREY)
    cv.line(x + w * 0.1, y + h * 0.27, x + w * 0.05, y + h * 0.27, LGREY, 2)
    cv.line(x + w * 0.21, y + h * 0.27, x + w * 0.26, y + h * 0.27, LGREY, 2)
    cv.line(x + w * 0.155, y + h * 0.345, x + w * 0.155, y + h * 0.42, LGREY, 2)
    cv.rect(x, y + h * 0.94, w, h * 0.06, bytes((16, 20, 32)))

def ill_cop(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((16, 84, 120)))
    cx, cy, r = x + w * 0.5, y + h * 0.56, h * 0.27
    cv.circle(cx, cy, r, TEAL)
    cv.circle(cx - r * 0.35, cy - r * 0.2, r * 0.34, GREEN)
    cv.circle(cx + r * 0.3, cy + r * 0.3, r * 0.3, GREEN)
    cv.circle(cx + r * 0.42, cy - r * 0.42, r * 0.2, GREEN)
    for i in range(2):
        cv.circle(cx, cy, r + 5 + i * 5, RED, fill=False)
    cv.rect(x + w * 0.05, y + h * 0.06, w * 0.34, h * 0.13, RED)
    draw_center(cv, x + w * 0.22, y + h * 0.075, "1.5C", 1.6, WHITE)

def ill_chapo(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((120, 30, 34)))
    cv.rect(x + w * 0.3, y + h * 0.14, w * 0.4, h * 0.72, bytes((238, 226, 198)))
    cv.circle(x + w * 0.5, y + h * 0.42, h * 0.13, BROWN)
    cv.rect(x + w * 0.36, y + h * 0.3, w * 0.28, h * 0.05, DARK)
    cv.tri([(x + w * 0.5, y + h * 0.22), (x + w * 0.64, y + h * 0.32),
            (x + w * 0.36, y + h * 0.32)], DARK)
    cv.rect(x + w * 0.38, y + h * 0.58, w * 0.24, h * 0.2, BROWN)
    for sx in (0.1, 0.86):
        cx = x + w * sx
        cy = y + h * 0.2
        for a in range(5):
            import math
            ang = -math.pi / 2 + a * 2 * math.pi / 5
            cv.tri([(cx, cy), (cx + 9 * math.cos(ang), cy + 9 * math.sin(ang)),
                    (cx + 4 * math.cos(ang + 0.6), cy + 4 * math.sin(ang + 0.6))],
                   YELLOW)

def ill_flags(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((20, 60, 130)))
    cv.rect(x + w * 0.06, y + h * 0.16, w * 0.34, h * 0.5, BLUE)
    import math
    for i in range(8):
        ang = 2 * math.pi * i / 8
        cv.circle(x + w * 0.23 + h * 0.16 * math.cos(ang),
                  y + h * 0.41 + h * 0.16 * math.sin(ang), 3, YELLOW)
    cv.rect(x + w * 0.6, y + h * 0.16, w * 0.34, h * 0.25, RED)
    cv.rect(x + w * 0.6, y + h * 0.41, w * 0.34, h * 0.25, WHITE)
    cv.line(x + w * 0.42, y + h * 0.41, x + w * 0.58, y + h * 0.41, YELLOW, 5)
    cv.tri([(x + w * 0.58, y + h * 0.41), (x + w * 0.52, y + h * 0.33),
            (x + w * 0.52, y + h * 0.49)], YELLOW)
    cv.line(x + w * 0.58, y + h * 0.41, x + w * 0.42, y + h * 0.41, YELLOW, 5)
    cv.tri([(x + w * 0.42, y + h * 0.41), (x + w * 0.48, y + h * 0.33),
            (x + w * 0.48, y + h * 0.49)], YELLOW)

def ill_missile(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((30, 40, 66)))
    cv.line(x + w * 0.12, y + h * 0.85, x + w * 0.62, y + h * 0.2, ORANGE, 4)
    cv.tri([(x + w * 0.62, y + h * 0.2), (x + w * 0.52, y + h * 0.22),
            (x + w * 0.6, y + h * 0.32)], LGREY)
    cv.rect(x + w * 0.08, y + h * 0.78, w * 0.1, h * 0.14, ORANGE)
    cv.circle(x + w * 0.8, y + h * 0.62, h * 0.2, TEAL, fill=False)
    cv.line(x + w * 0.8, y + h * 0.62, x + w * 0.68, y + h * 0.82, TEAL, 3)
    cv.rect(x + w * 0.55, y + h * 0.86, w * 0.42, h * 0.1, bytes((90, 60, 40)))
    cv.rect(x + w * 0.62, y + h * 0.78, w * 0.2, h * 0.08, GREY)
    burst(cv, x + w * 0.88, y + h * 0.3, w * 0.06, RED)

def ill_ship(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h * 0.68, w, h * 0.32, BLUE)
    for i in range(4):
        cv.circle(x + w * (0.12 + 0.24 * i), y + h * 0.7, 5, WHITE)
    cv.tri([(x + w * 0.18, y + h * 0.68), (x + w * 0.86, y + h * 0.68),
            (x + w * 0.76, y + h * 0.82)], DARK)
    cv.rect(x + w * 0.3, y + h * 0.52, w * 0.34, h * 0.16, RED)
    cv.rect(x + w * 0.36, y + h * 0.4, w * 0.12, h * 0.12, WHITE)
    flame(cv, x + w * 0.52, y + h * 0.12, w * 0.12, h * 0.4)
    cv.circle(x + w * 0.68, y + h * 0.2, 8, GREY)
    cv.circle(x + w * 0.74, y + h * 0.13, 11, GREY)

def ill_chart(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((18, 24, 40)))
    pts = [(0.06, 0.24), (0.3, 0.36), (0.48, 0.3), (0.66, 0.55), (0.9, 0.78)]
    for i in range(len(pts) - 1):
        cv.line(x + w * pts[i][0], y + h * pts[i][1],
                x + w * pts[i + 1][0], y + h * pts[i + 1][1], RED, 4)
    cv.tri([(x + w * 0.9, y + h * 0.78), (x + w * 0.8, y + h * 0.76),
            (x + w * 0.88, y + h * 0.64)], RED)
    cv.rect(x + w * 0.08, y + h * 0.62, w * 0.2, h * 0.26, TEAL)
    cv.rect(x + w * 0.11, y + h * 0.65, w * 0.14, h * 0.2, bytes((18, 24, 40)))
    draw_text(cv, x + w * 0.58, y + h * 0.07, "-3.7%", 2.2, RED)

def ill_factory(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((70, 60, 66)))
    cv.rect(x + w * 0.08, y + h * 0.52, w * 0.6, h * 0.42, bytes((120, 116, 110)))
    cv.rect(x + w * 0.14, y + h * 0.2, w * 0.09, h * 0.32, GREY)
    cv.rect(x + w * 0.3, y + h * 0.28, w * 0.09, h * 0.24, GREY)
    flame(cv, x + w * 0.1, y + h * 0.02, w * 0.14, h * 0.24)
    flame(cv, x + w * 0.42, y + h * 0.3, w * 0.2, h * 0.3)
    cv.circle(x + w * 0.8, y + h * 0.2, 10, GREY)
    cv.circle(x + w * 0.87, y + h * 0.12, 13, GREY)

def ill_police(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((24, 44, 92)))
    cx, cy = x + w * 0.5, y + h * 0.52
    import math
    for a in range(5):
        ang = -math.pi / 2 + a * 2 * math.pi / 5
        ang2 = ang + math.pi / 5
        cv.tri([(cx, cy), (cx + h * 0.34 * math.cos(ang), cy + h * 0.34 * math.sin(ang)),
                (cx + h * 0.15 * math.cos(ang2), cy + h * 0.15 * math.sin(ang2))], YELLOW)
        cv.tri([(cx, cy), (cx + h * 0.15 * math.cos(ang2), cy + h * 0.15 * math.sin(ang2)),
                (cx + h * 0.34 * math.cos(ang + 2 * math.pi / 5),
                 cy + h * 0.34 * math.sin(ang + 2 * math.pi / 5))], YELLOW)
    cv.circle(cx, cy, h * 0.09, bytes((24, 44, 92)))

def ill_mercury(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((10, 12, 30)))
    for sx, sy in ((0.12, 0.2), (0.85, 0.16), (0.7, 0.8), (0.2, 0.78), (0.92, 0.55)):
        cv.circle(x + w * sx, y + h * sy, 2.2, WHITE)
    cv.circle(x + w * 0.62, y + h * 0.52, h * 0.3, bytes((196, 140, 92)))
    cv.circle(x + w * 0.52, y + h * 0.42, h * 0.07, BROWN)
    cv.circle(x + w * 0.7, y + h * 0.62, h * 0.05, BROWN)
    cv.rect(x + w * 0.14, y + h * 0.3, w * 0.1, h * 0.12, SKY)
    cv.rect(x + w * 0.05, y + h * 0.33, w * 0.07, h * 0.06, BLUE)
    cv.rect(x + w * 0.25, y + h * 0.33, w * 0.07, h * 0.06, BLUE)
    cv.line(x + w * 0.19, y + h * 0.42, x + w * 0.34, y + h * 0.6, LGREY, 2)

def ill_quake(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((104, 164, 96)))
    cv.tri([(x + w * 0.02, y + h), (x + w * 0.36, y + h * 0.2),
            (x + w * 0.66, y + h)], bytes((110, 96, 84)))
    cv.tri([(x + w * 0.4, y + h), (x + w * 0.7, y + h * 0.3),
            (x + w * 0.98, y + h)], bytes((88, 78, 70)))
    cv.tri([(x + w * 0.36, y + h * 0.2), (x + w * 0.29, y + h * 0.36),
            (x + w * 0.43, y + h * 0.36)], WHITE)
    pts = [(0.44, 0.52), (0.5, 0.64), (0.46, 0.74), (0.53, 0.86), (0.5, 1.0)]
    for i in range(len(pts) - 1):
        cv.line(x + w * pts[i][0], y + h * pts[i][1], x + w * pts[i + 1][0],
                y + h * pts[i + 1][1], bytes((30, 24, 20)), 3)

def ill_exam(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((240, 236, 220)))
    cv.rect(x + w * 0.24, y + h * 0.1, w * 0.44, h * 0.8, WHITE)
    cv.frame(x + w * 0.24, y + h * 0.1, w * 0.44, h * 0.8, GREY, 1)
    for i in range(4):
        cv.rect(x + w * 0.3, y + h * (0.24 + 0.15 * i), w * 0.32, h * 0.045, LGREY)
    burst(cv, x + w * 0.76, y + h * 0.3, w * 0.09, PURPLE)
    cv.line(x + w * 0.3, y + h * 0.78, x + w * 0.44, y + h * 0.64, RED, 3)
    cv.line(x + w * 0.3, y + h * 0.64, x + w * 0.44, y + h * 0.78, RED, 3)

def ill_ball(cv, x, y, w, h):
    cv.rect(x, y, w, h, GREEN)
    cv.rect(x, y + h * 0.46, w, h * 0.05, WHITE)
    cv.circle(x + w * 0.34, y + h * 0.48, h * 0.3, WHITE)
    cv.circle(x + w * 0.34, y + h * 0.48, h * 0.12, DARK)
    draw_text(cv, x + w * 0.66, y + h * 0.3, "4-1", 2.6, WHITE)

def ill_tennis(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((178, 84, 44)))
    cv.rect(x, y + h * 0.47, w, h * 0.05, WHITE)
    cv.circle(x + w * 0.34, y + h * 0.34, h * 0.21, WHITE, fill=False)
    cv.circle(x + w * 0.34, y + h * 0.34, h * 0.16, bytes((90, 60, 40)), fill=False)
    cv.line(x + w * 0.42, y + h * 0.48, x + w * 0.56, y + h * 0.78,
            bytes((90, 60, 40)), 4)
    cv.circle(x + w * 0.74, y + h * 0.28, h * 0.1, YELLOW)
    cv.line(x + w * 0.6, y + h * 0.62, x + w * 0.88, y + h * 0.62, WHITE, 3)

def ill_game(cv, x, y, w, h):
    cv.rect(x, y, w, h, PURPLE)
    cv.rect(x + w * 0.2, y + h * 0.3, w * 0.6, h * 0.4, DARK)
    cv.circle(x + w * 0.2, y + h * 0.5, h * 0.2, DARK)
    cv.circle(x + w * 0.8, y + h * 0.5, h * 0.2, DARK)
    cv.rect(x + w * 0.28, y + h * 0.44, w * 0.05, h * 0.12, WHITE)
    cv.rect(x + w * 0.26, y + h * 0.475, w * 0.09, h * 0.05, WHITE)
    cv.circle(x + w * 0.68, y + h * 0.44, 4, RED)
    cv.circle(x + w * 0.74, y + h * 0.52, 4, YELLOW)
    cv.circle(x + w * 0.62, y + h * 0.56, 4, TEAL)
    cv.circle(x + w * 0.56, y + h * 0.64, 4, SKY)

def ill_houses(cv, x, y, w, h):
    cv.rect(x, y, w, h, bytes((96, 74, 60)))
    for i, hx in enumerate((0.08, 0.42, 0.72)):
        cv.rect(x + w * hx, y + h * 0.52, w * 0.22, h * 0.4, bytes((168, 132, 92)))
        cv.tri([(x + w * (hx - 0.02), y + h * 0.52), (x + w * (hx + 0.24), y + h * 0.52),
                (x + w * (hx + 0.11), y + h * 0.3)], bytes((120, 62, 40)))
    flame(cv, x + w * 0.44, y + h * 0.08, w * 0.13, h * 0.3)
    flame(cv, x + w * 0.12, y + h * 0.2, w * 0.1, h * 0.22)

# ---------------------------------------------------------------- content
# Every story below was reported on Sunday 22 November 2026 (see the
# source list in README.md). 16 pictured stories + 27 in brief = 43.

BRIEFS = [
    "HEGSETH MEMO CURBS CANADA TIES",
    "DEPOK FLOOD KILLS COURIER",
    "ESTONIA SHUTS RUSSIAN BORDER",
    "RUSSIAN MISSILES HIT POLAND",
    "DENMARK EXPELS RUSSIAN ATTACHE",
    "ROHINGYA WELCOME UN VERDICT",
    "UAE RUNS OIL PAST IRAN, HORMUZ",
    "HOUTHIS STRIKE SAUDI ARABIA",
    "GAZA AID VEHICLE HIT BY ISRAEL",
    "UK-EU DEALS SIGNED IN LONDON",
    "FBI DATABASE BREACH PROBED",
    "AMAZON NEAR $7.5BN DECART DEAL",
    "IBM'S 520-QUBIT NIGHTHAWK",
    "NIGERIA BOAT CAPSIZE KILLS 24",
    "BOLSONARO IN INTENSIVE CARE",
    "FRANCE PROTESTS: 82,500 MARCH",
    "NEPAL PM BALENDRA VISITS INDIA",
    "INDIA-CHINA TALKS ON ARUNACHAL",
    "INDIA 720/9 V NZ, LEAD BY 352",
    "HARDEN 51 PASSES KOBE BRYANT",
    "ENGLAND THRASH ALL BLACKS",
    "MESSI GOLDEN BOOT; MIAMI LOSE",
    "MARQUEZ CRASHES; BEZZECCHI 1ST",
    "GARUDA U-17 DRAW MYANMAR 2-2",
    "GUNUNG IBU ERUPTS, 400M ASH",
    "PDIP STAYS OUT OF GOVERNMENT",
    "TNI NAVY FOILS 10KG DRUG RUN",
]

GRID = [
    (ill_missile, RED, "IRAN HITS BAHRAIN PLANT; TANKERS STRUCK",
     "US BLOCKADE OF IRAN: DAY 130"),
    (ill_ship, BLUE, "MISSILES HIT KRYVYI RIH; SHIP BURNS",
     "2 DEAD, DOZENS HURT IN UKRAINE"),
    (ill_chart, RED, "AI SELL-OFF SINKS US STOCKS",
     "S&P 500 -3.7% · NIKKEI -5.1%"),
    (ill_factory, ORANGE, "CANDY FACTORY FIRE: 3 DEAD, 36 MISSING",
     "SERANG, BANTEN · RESCUE GOES ON"),
    (ill_police, BLUE, "POLICE CHIEF ROTATES 704 OFFICERS",
     "12 REGIONAL CHIEFS REPLACED"),
    (ill_mercury, PURPLE, "BEPICOLOMBO ENTERS MERCURY ORBIT",
     "AFTER AN 8-YEAR JOURNEY"),
    (ill_quake, GREEN, "MAGNITUDE 6.7 QUAKE SHAKES PERU",
     "ANDES REGION · NO TSUNAMI ALERT"),
    (ill_exam, PURPLE, "KOREA MINISTER QUITS OVER AI CHEATING",
     "EXAM SCANDAL ROCKS SEOUL"),
    (ill_ball, GREEN, "LEEDS STUN CHELSEA 4-1 AT THE BRIDGE",
     "FIRST WIN THERE SINCE 1999"),
    (ill_tennis, ORANGE, "ALCARAZ V ZVEREV IN TURIN FINAL",
     "ATP FINALS · SUNDAY SHOWDOWN"),
    (ill_game, PURPLE, "GTA VI EARNS $3.8BN ON LAUNCH DAY",
     "BIGGEST DEBUT IN GAME HISTORY"),
    (ill_houses, RED, "FIRE GUTS BADUY VILLAGE: 32 HOMES",
     "132 HOMELESS IN LEBAK, BANTEN"),
]

# ---------------------------------------------------------------- layout

def panel_top(cv, x, y, w, h, ill, kcol, headline, brief):
    cv.rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, INK, 1.5)
    ill(cv, x + 2, y + 2, w - 4, 38)
    ty = y + 46
    for ln in wrap(headline, 2.0, w - 14, 5.5)[:2]:
        draw_text(cv, x + 7, ty, ln, 2.0, INK, 5.5)
        ty += 16.5
    for ln in wrap(brief, 2.0, w - 14, 5.5)[:2]:
        draw_text(cv, x + 7, ty + 2, ln, 2.0, kcol, 5.5)
        ty += 16.5

def panel_side(cv, x, y, w, h, ill, kicker, kcol, headline, brief):
    cv.rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, INK, 1.5)
    ill(cv, x + 2, y + 2, 106, h - 4)
    tx = x + 118
    draw_text(cv, tx, y + 8, kicker, 2.0, kcol, 5.5)
    ty = y + 28
    for ln in wrap(headline, 2.4, w - 128, 5.5)[:2]:
        draw_text(cv, tx, ty, ln, 2.4, INK, 5.5)
        ty += 21
    for ln in wrap(brief, 2.0, w - 128, 5.5)[:3]:
        draw_text(cv, tx, ty + 3, ln, 2.0, GREY, 5.5)
        ty += 16.5

def build():
    cv = Canvas(PAPER)
    # ---- masthead
    draw_center(cv, 512, 10, "THE WORLD IN ONE PAGE", 5.2, INK)
    cv.rect(16, 52, 992, 3, INK)
    draw_text(cv, 16, 60, "JAKARTA EDITION", 2.0, GREY, 5.5)
    draw_center(cv, 512, 58, "SUNDAY · 22 NOVEMBER 2026", 3.0, RED)
    r = "43 STORIES · 16 PICTURED"
    draw_text(cv, 1008 - text_w(r, 2.0, 5.5), 60, r, 2.0, GREY, 5.5)
    cv.rect(16, 84, 992, 3, INK)
    # ---- hero + stack
    hx, hy, hw, hh = 16, 94, 592, 262
    cv.rect(hx, hy, hw, hh, CARD)
    cv.frame(hx, hy, hw, hh, INK, 2)
    ill_kyiv(cv, hx + 2, hy + 2, hw - 4, 100)
    draw_text(cv, hx + 12, hy + 108, "KYIV · UKRAINE · WAR", 2.0, RED, 5.5)
    ty = hy + 128
    for ln in wrap("DRONE STRIKE LEVELS KYIV FLATS; 14 MISSING", 3.2, hw - 24, 5.5):
        draw_text(cv, hx + 12, ty, ln, 3.2, INK, 5.5)
        ty += 29
    draw_block(cv, hx + 12, ty + 4,
               "A RUSSIAN DRONE STRIKE PARTLY DESTROYED AN APARTMENT "
               "BUILDING NEAR KYIV. AT LEAST 14 PEOPLE ARE MISSING AND "
               "RESCUERS ARE DIGGING THROUGH THE RUBBLE FOR SURVIVORS.",
               2.0, GREY, hw - 24, pitch=18, adv=5.5)
    panel_side(cv, 620, 94, 388, 127, ill_cop, "CLIMATE · TURKEY", TEAL,
               "COP31 TALKS RUN INTO OVERTIME",
               "FOSSIL-FUEL ROW BLOCKS DEAL; DRAFT DROPS $120BN AID TARGET")
    panel_side(cv, 620, 229, 388, 127, ill_chapo, "MEXICO · JUSTICE", RED,
               "CARTEL BOSS EL CHAPO ISIDRO CAPTURED",
               "FBI MOST-WANTED HELD IN SINALOA; 11 DIE IN RAID AND AFTERMATH")
    # ---- wide panel: EU-Indonesia
    wx, wy, ww, wh = 16, 364, 992, 92
    cv.rect(wx, wy, ww, wh, CARD)
    cv.frame(wx, wy, ww, wh, INK, 2)
    ill_flags(cv, wx + 2, wy + 2, 296, wh - 4)
    tx = wx + 314
    draw_text(cv, tx, wy + 8, "BRUSSELS · TRADE", 2.0, BLUE, 5.5)
    draw_text(cv, tx, wy + 27,
              "EU AND INDONESIA SIGN LANDMARK TRADE DEAL", 2.8, INK, 5.5)
    draw_block(cv, tx, wy + 58,
               "AFTER TEN YEARS OF TALKS, THE IEU-CEPA PACT REMOVES 98.5% "
               "OF TARIFFS BETWEEN THE EU AND INDONESIA.",
               2.0, GREY, ww - 330, pitch=17, adv=5.5)
    # ---- grid
    gy = 464
    for i, (ill, kcol, head, brief) in enumerate(GRID):
        gx = 16 + (i % 4) * 248
        yy = gy + (i // 4) * 122
        panel_top(cv, gx, yy, 240, 114, ill, kcol, head, brief)
    # ---- in brief band
    by = 832
    cv.rect(16, by, 992, 3, INK)
    draw_text(cv, 16, by + 7, "IN BRIEF — THE REST OF SUNDAY", 2.2, RED, 5.5)
    cols = [BRIEFS[0:9], BRIEFS[9:18], BRIEFS[18:27]]
    for ci, col in enumerate(cols):
        cx = 16 + ci * 336
        for ri, item in enumerate(col):
            yy = by + 32 + ri * 15.6
            cv.rect(cx, yy + 4, 5, 5, RED)
            draw_text(cv, cx + 12, yy, item, 2.0, INK, 5.2)
    cv.rect(16, 1006, 992, 2, INK)
    draw_center(cv, 512, 1010,
                "SOURCES: BBC · AL JAZEERA · REUTERS · AP · FRANCE 24 · "
                "UPI · GUARDIAN · CNBC · INDONESIAN WIRES", 1.8, GREY, 5.2)
    return cv

def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError:
        outdir = "."
    cv = build()
    write_png(os.path.join(outdir, "entry.png"), 1024, 1024, cv.downscale())

if __name__ == "__main__":
    main()
