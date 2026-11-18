"""Caught On Live channel art: logo (800x800), banner (2560x1440), watermark (150x150).
Writes SVGs and renders PNGs with rsvg-convert."""
import subprocess, pathlib

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

from PIL import ImageFont
ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
MONT = "/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf"


def text_w(text, size, path, spacing=0.0, weight=None):
    f = ImageFont.truetype(path, int(round(size)))
    if weight is not None:
        f.set_variation_by_axes([weight])
    return f.getlength(text) * (size / int(round(size))) + spacing * len(text)


RED = "#FF2E4D"
YELLOW = "#FFD60A"
WHITE = "#FFFFFF"
BG0 = "#07060C"
BG1 = "#1A0B2E"
MAGENTA = "#C026D3"
CYAN = "#06B6D4"


def brackets(x0, y0, x1, y1, arm, stroke, color=WHITE, opacity=1.0):
    """Four viewfinder corner brackets around the box (x0,y0)-(x1,y1)."""
    p = []
    p.append(f"M{x0},{y0+arm} L{x0},{y0} L{x0+arm},{y0}")
    p.append(f"M{x1-arm},{y0} L{x1},{y0} L{x1},{y0+arm}")
    p.append(f"M{x1},{y1-arm} L{x1},{y1} L{x1-arm},{y1}")
    p.append(f"M{x0+arm},{y1} L{x0},{y1} L{x0},{y1-arm}")
    return (f'<path d="{" ".join(p)}" fill="none" stroke="{color}" stroke-width="{stroke}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>')


def live_pill(cx, cy, w, h, font_size, dot_r, glow=True):
    """Red rounded LIVE badge with a white dot, centred on (cx, cy)."""
    x, y = cx - w / 2, cy - h / 2
    tw = text_w("LIVE", font_size, ANTON, font_size * 0.04)
    gap = dot_r * 1.3
    content = 2 * dot_r + gap + tw
    left = cx - content / 2
    dot_cx = left + dot_r
    text_x = left + 2 * dot_r + gap + tw / 2
    g = ""
    if glow:
        g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h*0.28}" fill="{RED}" '
             f'opacity="0.75" filter="url(#glow)"/>')
    return (g +
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h*0.28}" fill="url(#redgrad)"/>'
            f'<circle cx="{dot_cx}" cy="{cy}" r="{dot_r}" fill="{WHITE}"/>'
            f'<text x="{text_x}" y="{cy + font_size*0.36}" font-family="Anton" font-size="{font_size}" '
            f'fill="{WHITE}" text-anchor="middle" letter-spacing="{font_size*0.04}">LIVE</text>')


DEFS = f"""
<defs>
  <radialGradient id="bgglow" cx="50%" cy="45%" r="65%">
    <stop offset="0%" stop-color="{BG1}"/>
    <stop offset="100%" stop-color="{BG0}"/>
  </radialGradient>
  <linearGradient id="redgrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#FF4A64"/>
    <stop offset="100%" stop-color="#E0122F"/>
  </linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="28"/>
  </filter>
  <filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="120"/>
  </filter>
  <pattern id="scan" width="8" height="8" patternUnits="userSpaceOnUse">
    <rect width="8" height="2" fill="#FFFFFF" opacity="0.035"/>
  </pattern>
</defs>
"""


def logo_svg(transparent=False, size=800):
    s = size
    bg = "" if transparent else (
        f'<rect width="{s}" height="{s}" fill="url(#bgglow)"/>'
        f'<circle cx="{s*0.22}" cy="{s*0.2}" r="{s*0.32}" fill="{MAGENTA}" opacity="0.28" filter="url(#softglow)"/>'
        f'<circle cx="{s*0.82}" cy="{s*0.85}" r="{s*0.3}" fill="{CYAN}" opacity="0.22" filter="url(#softglow)"/>'
        f'<rect width="{s}" height="{s}" fill="url(#scan)"/>')
    # brackets sit inside the circle crop: box 190..610
    b0, b1 = s * 0.2375, s * 0.7625
    body = brackets(b0, b0, b1, b1, arm=s * 0.13, stroke=s * 0.042)
    body += live_pill(s / 2, s / 2, w=s * 0.44, h=s * 0.19, font_size=s * 0.125, dot_r=s * 0.03,
                      glow=not transparent)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">'
            f'{DEFS}{bg}{body}</svg>')


def bubble_w(user, msg, scale=1.0):
    fs = 34 * scale
    return text_w(user + ": ", fs, MONT, weight=700) + text_w(msg, fs, MONT, weight=600) + 56 * scale


def chat_bubble(x, y, user, msg, ucolor, opacity, scale=1.0):
    fs = 34 * scale
    w = bubble_w(user, msg, scale)
    h = 70 * scale
    return (f'<g opacity="{opacity}">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="#FFFFFF" opacity="0.08"/>'
            f'<text x="{x + 28*scale}" y="{y + h*0.64}" font-family="Montserrat" font-weight="700" '
            f'font-size="{fs}" fill="{ucolor}">{user}: <tspan fill="#FFFFFF" font-weight="600">{msg}</tspan></text>'
            f'</g>')


def banner_svg():
    W, H = 2560, 1440
    # YouTube safe area (all devices): 1546 x 423, centred
    sx0, sy0 = (W - 1546) / 2, (H - 423) / 2
    sx1, sy1 = sx0 + 1546, sy0 + 423
    cx = W / 2

    bg = (f'<rect width="{W}" height="{H}" fill="url(#bgglow)"/>'
          f'<circle cx="520" cy="420" r="560" fill="{MAGENTA}" opacity="0.30" filter="url(#softglow)"/>'
          f'<circle cx="2080" cy="1050" r="560" fill="{CYAN}" opacity="0.22" filter="url(#softglow)"/>'
          f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')

    # faux live chat on both sides (outside the safe area; seen on desktop/TV)
    chat = ""
    left = [("rahul_07", "BHAI KYA KIYA", YELLOW), ("xenon", "CLIP IT!!", CYAN), ("nikk", "W MOMENT", "#A3E635"),
            ("ayaan", "REPLAY PLS", "#F472B6"), ("dev", "HAHAHA", YELLOW)]
    right = [("meera", "NO WAY", "#F472B6"), ("kabir_op", "LEGEND", YELLOW), ("zoro", "LOL", CYAN),
             ("sam", "CAUGHT LIVE", "#A3E635"), ("ishu", "AGAIN AGAIN", CYAN)]
    for i, (u, m, c) in enumerate(left):
        chat += chat_bubble(70 + (i % 2) * 60, 330 + i * 160, u, m, c, 0.55 - abs(i - 2) * 0.08)
    for i, (u, m, c) in enumerate(right):
        w = bubble_w(u, m)
        chat += chat_bubble(W - 70 - (i % 2) * 60 - w, 330 + i * 160, u, m, c, 0.55 - abs(i - 2) * 0.08)

    # viewfinder brackets just inside the safe area
    pad = 20
    frame = brackets(sx0 + pad, sy0 + pad, sx1 - pad, sy1 - pad, arm=86, stroke=11, opacity=0.9)

    # REC + timecode, top corners of the frame
    hud = (f'<circle cx="{sx0 + 78}" cy="{sy0 + 70}" r="13" fill="{RED}"/>'
           f'<text x="{sx0 + 102}" y="{sy0 + 82}" font-family="Montserrat" font-weight="800" font-size="34" '
           f'fill="{WHITE}" letter-spacing="3">REC</text>'
           f'<text x="{sx1 - 60}" y="{sy0 + 82}" font-family="DejaVu Sans Mono" font-weight="bold" font-size="32" '
           f'fill="{WHITE}" opacity="0.85" text-anchor="end">00:00:42</text>')

    # title: CAUGHT ON  [LIVE]
    tfs = 168
    title_y = sy0 + 268
    caught_w = text_w("CAUGHT ON", tfs, ANTON, 5)
    pill_w, pill_h = 350, 160
    gap = 38
    total = caught_w + gap + pill_w
    tx = cx - total / 2
    title = (f'<text x="{tx}" y="{title_y}" font-family="Anton" font-size="{tfs}" fill="{WHITE}" '
             f'letter-spacing="5">CAUGHT ON</text>')
    title += live_pill(tx + caught_w + gap + pill_w / 2, title_y - tfs * 0.45, w=pill_w, h=pill_h,
                       font_size=118, dot_r=24)

    tag = (f'<text x="{cx}" y="{sy0 + 350}" font-family="Montserrat" font-weight="600" font-size="42" '
           f'fill="#E5E7EB" text-anchor="middle" letter-spacing="1">The wildest live-stream moments '
           f'<tspan fill="{YELLOW}" font-weight="800">· New Shorts daily</tspan></text>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{DEFS}{bg}{chat}{frame}{hud}{title}{tag}</svg>')


def render(name, svg, w, h):
    p = OUT / f"{name}.svg"
    p.write_text(svg)
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", str(OUT / f"{name}.png"), str(p)], check=True)


if __name__ == "__main__":
    render("logo", logo_svg(), 800, 800)
    render("banner", banner_svg(), 2560, 1440)
    render("watermark", logo_svg(transparent=True, size=800), 150, 150)
    print("done")
