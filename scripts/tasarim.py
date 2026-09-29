"""Profildeki sabit SVG görsellerini üretir (assets/*.svg).

Kullanım:  python scripts/tasarim.py
Fontlar assets/fonts altındaki alt kümelenmiş WOFF2 dosyalarından gömülür.
"""

import math
import random

from ortak import (AL, ALTIN, ALTIN_ACIK, CINI, GECE, GECE2, KILIM_SATIR, KOBALT, KOK,
                   KREM, LACIVERT, SOLUK, altin_gradyan, font_css, hatayi, kilim_serit,
                   lale, parilti_gradyan, selcuklu_deseni, tezhip_cerceve, yildiz_noktalari)

CIKTI = KOK / "assets"


def svg(w, h, baslik, govde, fontlar=(), stil=""):
    css = font_css(*fontlar) if fontlar else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{baslik}">
<title>{baslik}</title>
<style>
{css}
.cz{{font-family:'Cinzel',serif}} .gv{{font-family:'Great Vibes',cursive}} .jb{{font-family:'JetBrains Mono',monospace}}
{stil}
</style>
{govde}
</svg>
'''


# ─────────────────────────────── ORTAK SAHNE PARÇALARI ───────────────────────────────

def yildizli_gok(w, h, adet, tohum, ust_sinir=None):
    rnd = random.Random(tohum)
    ust_sinir = ust_sinir or h
    p = []
    for i in range(adet):
        x, y = rnd.uniform(0, w), rnd.uniform(0, ust_sinir) ** 1.15 / ust_sinir ** 0.15
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        if i % 4 == 0:
            d = rnd.uniform(2, 5)
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{KREM}">'
                     f'<animate attributeName="opacity" values="1;.15;1" dur="{d:.1f}s" '
                     f'begin="{rnd.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>')
        else:
            p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{KREM}" opacity="{rnd.uniform(.3, .9):.2f}"/>')
    return "".join(p)


def hilal(cx, cy, r, id_):
    """Gökyüzünde ay ve yıldız."""
    return f'''<mask id="{id_}"><rect x="{cx - 2*r}" y="{cy - 2*r}" width="{4*r}" height="{4*r}" fill="#fff"/>
<circle cx="{cx + r*0.25}" cy="{cy}" r="{r*0.8}" fill="#000"/></mask>
<radialGradient id="{id_}h"><stop offset="0" stop-color="{KREM}" stop-opacity=".22"/><stop offset="1" stop-color="{KREM}" stop-opacity="0"/></radialGradient>
<circle cx="{cx}" cy="{cy}" r="{r*2.6}" fill="url(#{id_}h)"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="{KREM}" mask="url(#{id_})" opacity=".95"/>
<polygon points="{yildiz_noktalari(cx + r*1.12, cy, r*0.25, r*0.1, 5, -90)}" fill="{KREM}" opacity=".95"/>'''


def cami(x, zemin, s, renk):
    """Klasik Osmanlı camisi silüeti (merkezi kubbe, yarım kubbeler, dört minare)."""
    p = [f'<rect x="{x - 62*s}" y="{zemin - 34*s}" width="{124*s}" height="{34*s}" fill="{renk}"/>',
         f'<rect x="{x - 36*s}" y="{zemin - 46*s}" width="{72*s}" height="{12*s}" fill="{renk}"/>',
         f'<path d="M{x - 34*s} {zemin - 46*s} A{34*s} {30*s} 0 0 1 {x + 34*s} {zemin - 46*s}Z" fill="{renk}"/>',
         f'<rect x="{x - 1*s}" y="{zemin - 86*s}" width="{2*s}" height="{12*s}" fill="{renk}"/>',
         f'<circle cx="{x}" cy="{zemin - 88*s}" r="{2.2*s}" fill="{renk}"/>']
    for yon in (-1, 1):
        p.append(f'<path d="M{x + yon*22*s} {zemin - 34*s} A{24*s} {20*s} 0 0 1 {x + yon*70*s} {zemin - 34*s}Z" '
                 f'transform="translate({-yon*2*s} 0)" fill="{renk}"/>')
        for kx in (46, 58):
            p.append(f'<path d="M{x + yon*kx*s - 7*s} {zemin - 34*s} A{7*s} {7*s} 0 0 1 {x + yon*kx*s + 7*s} {zemin - 34*s}Z" fill="{renk}"/>')
        for mx, mh in ((82, 128), (100, 104)):
            cx = x + yon * mx * s
            ust = zemin - mh * s
            p.append(f'<rect x="{cx - 2.6*s}" y="{ust}" width="{5.2*s}" height="{mh*s}" fill="{renk}"/>')
            for k in (0.28, 0.5, 0.72):
                p.append(f'<rect x="{cx - 4.4*s}" y="{ust + mh*s*k}" width="{8.8*s}" height="{2*s}" fill="{renk}"/>')
            p.append(f'<polygon points="{cx - 3.4*s},{ust} {cx + 3.4*s},{ust} {cx},{ust - 22*s}" fill="{renk}"/>')
    return "".join(p)


def galata(x, zemin, s, renk):
    return (f'<rect x="{x - 12*s}" y="{zemin - 78*s}" width="{24*s}" height="{78*s}" fill="{renk}"/>'
            f'<rect x="{x - 15*s}" y="{zemin - 84*s}" width="{30*s}" height="{6*s}" fill="{renk}"/>'
            f'<rect x="{x - 12*s}" y="{zemin - 94*s}" width="{24*s}" height="{10*s}" fill="{renk}"/>'
            f'<polygon points="{x - 14*s},{zemin - 94*s} {x + 14*s},{zemin - 94*s} {x},{zemin - 128*s}" fill="{renk}"/>')


def kiz_kulesi(x, zemin, s, renk):
    return (f'<rect x="{x - 26*s}" y="{zemin - 12*s}" width="{52*s}" height="{12*s}" fill="{renk}"/>'
            f'<rect x="{x - 9*s}" y="{zemin - 44*s}" width="{18*s}" height="{32*s}" fill="{renk}"/>'
            f'<rect x="{x - 11*s}" y="{zemin - 48*s}" width="{22*s}" height="{4*s}" fill="{renk}"/>'
            f'<polygon points="{x - 7*s},{zemin - 48*s} {x + 7*s},{zemin - 48*s} {x},{zemin - 66*s}" fill="{renk}"/>'
            f'<rect x="{x + 14*s}" y="{zemin - 24*s}" width="{10*s}" height="{12*s}" fill="{renk}"/>')


def istanbul(w, zemin, renk, tohum=7):
    rnd = random.Random(tohum)
    p = []
    x = 0
    pencere = []
    while x < w:
        bw, bh = rnd.uniform(14, 34), rnd.uniform(10, 34)
        p.append(f'<rect x="{x:.1f}" y="{zemin - bh:.1f}" width="{bw + 1:.1f}" height="{bh:.1f}" fill="{renk}"/>')
        if rnd.random() < .55:
            px, py = x + rnd.uniform(3, bw - 5), zemin - rnd.uniform(4, bh - 4)
            pencere.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="2.2" height="3" fill="{ALTIN_ACIK}">'
                           f'<animate attributeName="opacity" values=".9;.25;.9" dur="{rnd.uniform(3, 8):.1f}s" '
                           f'begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></rect>')
        x += bw
    p.append(cami(180, zemin, 0.85, renk))
    p.append(galata(430, zemin, 0.85, renk))
    p.append(cami(700, zemin, 0.98, renk))
    p.append(kiz_kulesi(900, zemin + 14, 0.7, renk))
    return "".join(p) + "".join(pencere)


def iha_mal(renk, kontur=None):
    """Orta irtifa uzun havada kalışlı İHA (üstten görünüş, burun sağa)."""
    k = f'stroke="{kontur}" stroke-width=".8"' if kontur else ""
    return (f'<path d="M-30 0 C-28 -3 18 -3.2 26 -1.6 C30 -.6 30 .6 26 1.6 C18 3.2 -28 3 -30 0Z" fill="{renk}" {k}/>'
            f'<path d="M2 -2 L-2 -46 L4 -46 L9 -2Z M2 2 L-2 46 L4 46 L9 2Z" fill="{renk}" {k}/>'
            f'<path d="M-24 -1.5 L-34 -13 L-30 -13 L-20 -1.5Z M-24 1.5 L-34 13 L-30 13 L-20 1.5Z" fill="{renk}" {k}/>'
            f'<rect x="-33" y="-6" width="1.4" height="12" fill="{renk}" opacity=".7"/>')


def iha_jet(renk, kontur=None):
    """Kanard-delta kanatlı insansız savaş uçağı (üstten görünüş, burun sağa)."""
    k = f'stroke="{kontur}" stroke-width=".8"' if kontur else ""
    return (f'<path d="M34 0 L22 -3.5 L-26 -5 L-30 -3 L-30 3 L-26 5 L22 3.5Z" fill="{renk}" {k}/>'
            f'<path d="M8 -4 L-18 -30 L-26 -30 L-20 -4Z M8 4 L-18 30 L-26 30 L-20 4Z" fill="{renk}" {k}/>'
            f'<path d="M20 -3 L12 -12 L9 -12 L12 -3Z M20 3 L12 12 L9 12 L12 3Z" fill="{renk}" {k}/>'
            f'<path d="M-18 -4 L-28 -12 L-31 -11 L-26 -4Z M-18 4 L-28 12 L-31 11 L-26 4Z" fill="{renk}" {k}/>')


# ─────────────────────────────── 1) BAŞLIK ───────────────────────────────

def baslik():
    W, H = 1000, 480
    zemin = 398
    kilim_h = KILIM_SATIR * 2.4
    govde = f'''<defs>
  <linearGradient id="gok" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#050A16"/><stop offset=".62" stop-color="{GECE2}"/>
    <stop offset=".9" stop-color="#2A3F66"/><stop offset="1" stop-color="#6B4A3A"/>
  </linearGradient>
  <linearGradient id="deniz" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1A2C4E"/><stop offset="1" stop-color="#070D1A"/>
  </linearGradient>
  {selcuklu_deseni("cini", 64, ALTIN, .07)}
  {altin_gradyan("altin")}
  {parilti_gradyan("parilti", "5s")}
  <radialGradient id="hale" cx=".5" cy=".42" r=".5">
    <stop offset="0" stop-color="{ALTIN}" stop-opacity=".18"/><stop offset="1" stop-color="{ALTIN}" stop-opacity="0"/>
  </radialGradient>
  <filter id="parla"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#gok)"/>
<rect width="{W}" height="{zemin}" fill="url(#cini)"/>
{yildizli_gok(W, H, 90, 42, 260)}
{hilal(880, 78, 26, "ay")}
<ellipse cx="500" cy="150" rx="420" ry="140" fill="url(#hale)"/>

<g transform="translate(-80 110)" opacity=".85">
  <g transform="scale(.55)">{iha_mal("#0D1830", "#3A4F78")}</g>
  <circle cx="-16" cy="0" r="1.6" fill="{AL}"><animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></circle>
  <animateTransform attributeName="transform" type="translate" values="-80 110;1080 70" dur="38s" repeatCount="indefinite"/>
</g>

<g text-anchor="middle">
  <line x1="330" y1="72" x2="468" y2="72" stroke="{ALTIN}" stroke-width="1.2"/>
  <line x1="532" y1="72" x2="670" y2="72" stroke="{ALTIN}" stroke-width="1.2"/>
  <circle cx="330" cy="72" r="2.5" fill="{ALTIN}"/><circle cx="670" cy="72" r="2.5" fill="{ALTIN}"/>
  <g transform="rotate(0 500 72)">{hatayi(500, 72, 18)}
    <animateTransform attributeName="transform" type="rotate" values="0 500 72;360 500 72" dur="40s" repeatCount="indefinite"/></g>
  <text x="500" y="168" class="cz" font-weight="700" font-size="82" letter-spacing="10" fill="url(#altin)" filter="url(#parla)">PİREBURAK</text>
  <text x="500" y="168" class="cz" font-weight="700" font-size="82" letter-spacing="10" fill="url(#parilti)">PİREBURAK</text>
  <text x="500" y="206" class="jb" font-size="17" fill="{KREM}" letter-spacing="1">Siber Güvenlik Mühendisi <tspan fill="{ALTIN}">✦</tspan> Python Backend <tspan fill="{ALTIN}">✦</tspan> Keşif Araçları</text>
  <text x="500" y="240" class="gv" font-size="27" fill="{CINI}">If you can't break it, you can't secure it.</text>
</g>

<g opacity=".95">{istanbul(W, zemin, "#060B17")}</g>
<rect y="{zemin}" width="{W}" height="{H - zemin - kilim_h}" fill="url(#deniz)"/>
<g transform="translate(0 {2 * zemin}) scale(1 -1)" opacity=".16">{istanbul(W, zemin, "#2A3F66")}</g>
<g stroke="{ALTIN_ACIK}" stroke-linecap="round" opacity=".5">
  <line x1="820" y1="{zemin + 10}" x2="860" y2="{zemin + 10}"><animate attributeName="opacity" values=".2;.9;.2" dur="3s" repeatCount="indefinite"/></line>
  <line x1="838" y1="{zemin + 20}" x2="890" y2="{zemin + 20}"><animate attributeName="opacity" values=".8;.2;.8" dur="4s" repeatCount="indefinite"/></line>
  <line x1="850" y1="{zemin + 31}" x2="878" y2="{zemin + 31}"><animate attributeName="opacity" values=".3;.8;.3" dur="2.6s" repeatCount="indefinite"/></line>
</g>
{kilim_serit(0, H - kilim_h, W, 2.4)}
'''
    return svg(W, H, "PİREBURAK — Siber Güvenlik Mühendisi", govde, ("Cinzel:700", "Great Vibes", "JetBrains Mono:400"))


# ─────────────────────────────── 2) KİLİM AYRAÇ ───────────────────────────────

def ayrac():
    W = 1000
    h = KILIM_SATIR * 2.2
    govde = f'''<defs>{parilti_gradyan("p", "7s")}</defs>
{kilim_serit(0, 0, W, 2.2)}
<rect width="{W}" height="{h}" fill="url(#p)"/>'''
    return svg(W, round(h, 1), "Kilim şeridi", govde)


# ─────────────────────────────── 3) ATATÜRK & ANITKABİR ───────────────────────────────

_BAYRAK_DALGA = [
    "M0 0 C12 -4 24 4 36 0 C48 -4 56 2 60 0 L60 36 C56 38 48 32 36 36 C24 40 12 32 0 36Z",
    "M0 0 C12 4 24 -4 36 2 C48 6 56 -2 60 2 L60 38 C56 34 48 40 36 38 C24 32 12 40 0 36Z",
]


def anitkabir(x, zemin, s):
    """Anıtkabir Şeref Holü (altın çizgi çizimi) ve dalgalanan bayrak."""
    k = f'stroke="{ALTIN}" stroke-width="1.4" fill="{GECE}"'
    p = []
    for i, (gen, yuk) in enumerate([(300, 8), (270, 8), (240, 8), (220, 10)]):
        p.append(f'<rect x="{x - gen/2*s}" y="{zemin - (i*8 + yuk)*s}" width="{gen*s}" height="{yuk*s}" {k}/>')
    ust = zemin - 34 * s
    p.append(f'<rect x="{x - 96*s}" y="{ust - 78*s}" width="{192*s}" height="{78*s}" fill="#0E1A31"/>')
    for i in range(10):
        cx = x - 100 * s + (i + .5) * 20 * s
        p.append(f'<rect x="{cx - 4.5*s}" y="{ust - 78*s}" width="{9*s}" height="{78*s}" {k}/>')
        p.append(f'<line x1="{cx}" y1="{ust - 74*s}" x2="{cx}" y2="{ust - 4*s}" stroke="{ALTIN}" stroke-opacity=".35"/>')
    p.append(f'<rect x="{x - 108*s}" y="{ust - 92*s}" width="{216*s}" height="{14*s}" {k}/>')
    p.append(f'<rect x="{x - 100*s}" y="{ust - 106*s}" width="{200*s}" height="{14*s}" {k}/>')
    for i in range(12):
        p.append(f'<rect x="{x - 96*s + i*16.5*s}" y="{ust - 102*s}" width="{8*s}" height="{6*s}" fill="{ALTIN}" opacity=".35"/>')
    dx, fy = x + 128 * s, ust - 150 * s
    p.append(f'<line x1="{dx}" y1="{zemin}" x2="{dx}" y2="{fy}" stroke="{ALTIN}" stroke-width="2"/>')
    dalga = ";".join(_BAYRAK_DALGA + _BAYRAK_DALGA[:1])
    p.append(
        f'<g transform="translate({dx} {fy})">'
        f'<path d="{_BAYRAK_DALGA[0]}" fill="{AL}"><animate attributeName="d" dur="3s" repeatCount="indefinite" values="{dalga}"/></path>'
        f'<mask id="ayk"><rect width="60" height="40" fill="#fff"/><circle cx="21.5" cy="18" r="7.2" fill="#000"/></mask>'
        f'<circle cx="20" cy="18" r="9" fill="#fff" mask="url(#ayk)"/>'
        f'<polygon points="{yildiz_noktalari(33, 18, 4.5, 1.8, 5, -90)}" fill="#fff"/></g>'
    )
    return "".join(p)


def ataturk():
    W, H = 1000, 440
    isinlar = "".join(
        f'<line x1="230" y1="250" x2="{230 + 320*math.cos(math.radians(a)):.1f}" '
        f'y2="{250 + 320*math.sin(math.radians(a)):.1f}"/>' for a in range(180, 361, 12))
    govde = f'''<defs>
  <linearGradient id="zemin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GECE}"/><stop offset="1" stop-color="{GECE2}"/></linearGradient>
  <radialGradient id="gunes" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{ALTIN_ACIK}" stop-opacity=".55"/><stop offset=".45" stop-color="{ALTIN}" stop-opacity=".15"/><stop offset="1" stop-color="{ALTIN}" stop-opacity="0"/></radialGradient>
  {selcuklu_deseni("cini", 56, CINI, .06)}
  {altin_gradyan("altin")}
  {parilti_gradyan("parilti", "7s")}
  <clipPath id="kart"><rect x="14" y="14" width="{W-28}" height="{H-28}" rx="10"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="16" fill="url(#zemin)"/>
<rect width="{W}" height="{H}" rx="16" fill="url(#cini)"/>
<g clip-path="url(#kart)">
  <circle cx="230" cy="250" r="190" fill="url(#gunes)"><animate attributeName="r" values="180;205;180" dur="8s" repeatCount="indefinite"/></circle>
  <g stroke="{ALTIN}" stroke-opacity=".12" stroke-width="2">{isinlar}
    <animateTransform attributeName="transform" type="rotate" values="-3 230 250;3 230 250;-3 230 250" dur="20s" repeatCount="indefinite"/></g>
  {anitkabir(230, 356, 1.0)}
  <line x1="40" y1="356" x2="440" y2="356" stroke="{ALTIN}" stroke-opacity=".6"/>
  <text x="230" y="392" text-anchor="middle" class="cz" font-weight="700" font-size="14" letter-spacing="6" fill="{SOLUK}">ANITKABİR · ANKARA</text>
</g>
<g class="cz" font-weight="700">
  <text x="490" y="84" font-size="15" letter-spacing="7" fill="{CINI}">ATAMIZA SAYGIYLA</text>
  <line x1="490" y1="102" x2="700" y2="102" stroke="{ALTIN}" stroke-opacity=".6"/>
  {hatayi(716, 102, 9)}
  <line x1="732" y1="102" x2="940" y2="102" stroke="{ALTIN}" stroke-opacity=".6"/>
  <text x="490" y="160" font-size="36" fill="url(#altin)">“HAYATTA EN HAKİKİ</text>
  <text x="490" y="208" font-size="36" fill="url(#altin)">MÜRŞİT İLİMDİR.”</text>
  <text x="490" y="160" font-size="36" fill="url(#parilti)">“HAYATTA EN HAKİKİ</text>
  <text x="490" y="208" font-size="36" fill="url(#parilti)">MÜRŞİT İLİMDİR.”</text>
</g>
<text x="940" y="258" text-anchor="end" class="gv" font-size="36" fill="{ALTIN}">Mustafa Kemal Atatürk</text>
<g class="jb" font-size="13.5">
  <text x="490" y="310" fill="{SOLUK}">// Gençliğe Hitabe</text>
  <text x="490" y="334" fill="{KREM}">"Ey Türk gençliği! Birinci vazifen, Türk istiklâlini,</text>
  <text x="490" y="355" fill="{KREM}"> Türk Cumhuriyetini, ilelebet muhafaza ve müdafaa etmektir."</text>
  <text x="490" y="392" fill="{ALTIN}">1881 – ∞ <tspan fill="{SOLUK}"> ·  Işığında yürüyoruz.</tspan></text>
</g>
{lale(952, 372, .42, 14)}
{tezhip_cerceve(14, 14, W - 28, H - 28)}
<rect x="14" y="14" width="{W-28}" height="{H-28}" rx="10" fill="none" stroke="url(#parilti)" stroke-width="3"/>
'''
    return svg(W, H, "Atamıza saygıyla — Hayatta en hakiki mürşit ilimdir.", govde,
               ("Cinzel:700", "Great Vibes", "JetBrains Mono:400"))


# ─────────────────────────────── 4) İSTİKBAL GÖKLERDEDİR ───────────────────────────────

def dag(w, taban, tohum, genlik, renk):
    rnd = random.Random(tohum)
    nokta = []
    x, y = 0, taban - genlik * .5
    while x <= w + 80:
        nokta.append(f"{x:.0f},{y:.0f}")
        x += rnd.uniform(30, 80)
        y = min(taban - 8, max(taban - genlik, y + rnd.uniform(-genlik * .45, genlik * .45)))
    return f'<polygon points="{" ".join(nokta)} {w + 80},{taban + 200} 0,{taban + 200}" fill="{renk}"/>'


def gokler():
    W, H = 1000, 440
    hud = CINI
    yon = {0: "K", 90: "D", 180: "G", 270: "B"}
    pusula = []
    for i, d in enumerate(range(0, 360, 15)):
        x = 40 + i * 38
        pusula.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{8 if d % 45 == 0 else 4}" stroke="{hud}"/>')
        if d % 45 == 0:
            pusula.append(f'<text x="{x}" y="22" text-anchor="middle">{yon.get(d, f"{d:03d}")}</text>')
    irtifa = []
    for i in range(16):
        irtifa.append(f'<line x1="0" y1="{i*18}" x2="{12 if i % 5 == 0 else 6}" y2="{i*18}" stroke="{hud}"/>')
        if i % 5 == 0:
            irtifa.append(f'<text x="-8" y="{i*18 + 4}" text-anchor="end">{(30 - i) * 1000:,} ft</text>'.replace(",", "."))
    govde = f'''<defs>
  <linearGradient id="gok" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#040913"/><stop offset=".45" stop-color="{GECE2}"/>
    <stop offset=".75" stop-color="{KOBALT}"/><stop offset=".92" stop-color="#C9784A"/><stop offset="1" stop-color="{ALTIN_ACIK}"/>
  </linearGradient>
  <radialGradient id="safak" cx=".72" cy="1" r=".6"><stop offset="0" stop-color="{ALTIN_ACIK}" stop-opacity=".7"/><stop offset="1" stop-color="{ALTIN_ACIK}" stop-opacity="0"/></radialGradient>
  <linearGradient id="iz" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="tarama" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{hud}" stop-opacity="0"/><stop offset="1" stop-color="{hud}" stop-opacity=".55"/></linearGradient>
  {altin_gradyan("altin")}
  {parilti_gradyan("parilti", "6s")}
  <clipPath id="kart"><rect width="{W}" height="{H}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#kart)">
<rect width="{W}" height="{H}" fill="url(#gok)"/>
<rect width="{W}" height="{H}" fill="url(#safak)"/>
{yildizli_gok(W, H, 60, 9, 200)}
{dag(W, 392, 3, 70, "#16264A")}
{dag(W, 412, 11, 50, "#0D1830")}
{dag(W, 430, 5, 30, "#070D1A")}

<g>
  <rect x="-260" y="-2" width="240" height="4" rx="2" fill="url(#iz)"/>
  <g transform="scale(1.35)">{iha_jet("#E8EDF5", "#6B7A99")}</g>
  <animateTransform attributeName="transform" type="translate" values="-200 300;1250 235" dur="9s" repeatCount="indefinite"/>
</g>

<g>
  <animateMotion dur="24s" repeatCount="indefinite" path="M-120 262 C200 222 420 292 620 240 S980 222 1140 205"/>
  <g transform="scale(1.7)">{iha_mal("#E8EDF5", "#6B7A99")}</g>
  <g fill="none" stroke="{hud}" stroke-width="1.5">
    <path d="M-80 -70 h16 M-80 -70 v16 M80 -70 h-16 M80 -70 v16 M-80 70 h16 M-80 70 v-16 M80 70 h-16 M80 70 v-16"/>
    <circle r="4"/>
  </g>
  <text x="-80" y="-78" class="jb" font-size="11" fill="{hud}">İHA-01 · KİLİTLİ</text>
  <circle cx="-26" cy="0" r="2" fill="{AL}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></circle>
</g>

<g class="jb" font-size="10" fill="{hud}" opacity=".9">
  <g transform="translate(40 28)"><line x1="40" y1="0" x2="{40 + 23*38}" y2="0" stroke="{hud}" stroke-opacity=".5"/>{"".join(pusula)}</g>
  <path d="M537 18 l6 -10 l6 10Z" fill="{ALTIN}"/>
  <g transform="translate(962 110)"><line x1="0" y1="0" x2="0" y2="270" stroke="{hud}" stroke-opacity=".5"/>{"".join(irtifa)}</g>
</g>
<g transform="translate(92 350)">
  <circle r="62" fill="#07101F" fill-opacity=".75" stroke="{hud}" stroke-opacity=".6"/>
  <circle r="42" fill="none" stroke="{hud}" stroke-opacity=".35"/><circle r="21" fill="none" stroke="{hud}" stroke-opacity=".35"/>
  <line x1="-62" y1="0" x2="62" y2="0" stroke="{hud}" stroke-opacity=".3"/><line x1="0" y1="-62" x2="0" y2="62" stroke="{hud}" stroke-opacity=".3"/>
  <g><path d="M0 0 L62 0 A62 62 0 0 0 43.8 -43.8Z" fill="url(#tarama)"/>
    <animateTransform attributeName="transform" type="rotate" values="0;360" dur="4s" repeatCount="indefinite"/></g>
  <circle cx="24" cy="-30" r="3" fill="{ALTIN_ACIK}"><animate attributeName="opacity" values="0;1;0" dur="4s" repeatCount="indefinite"/></circle>
  <circle cx="-34" cy="14" r="2.5" fill="{AL}"><animate attributeName="opacity" values="0;0;1;0" dur="4s" repeatCount="indefinite"/></circle>
</g>
<g transform="translate(610 330)" class="jb" font-size="12.5">
  <rect x="-14" y="-24" width="290" height="104" rx="8" fill="#07101F" fill-opacity=".72" stroke="{hud}" stroke-opacity=".5"/>
  <text y="0" fill="{hud}">▸ GÖREV    <tspan fill="{KREM}">: KEŞİF / GÖZETLEME</tspan></text>
  <text y="20" fill="{hud}">▸ BAĞLANTI <tspan fill="{KREM}">: AES-256 · ŞİFRELİ</tspan></text>
  <text y="40" fill="{hud}">▸ MENŞEİ   <tspan fill="{KREM}">: YERLİ VE MİLLİ</tspan></text>
  <text y="60" fill="{hud}">▸ DURUM    <tspan fill="{ALTIN_ACIK}">: • AKTİF</tspan><animate attributeName="opacity" values="1;.4;1" dur="1.6s" repeatCount="indefinite"/></text>
</g>
<g class="cz" font-weight="700">
  <text x="50" y="98" font-size="44" letter-spacing="3" fill="url(#altin)">İSTİKBAL GÖKLERDEDİR</text>
  <text x="50" y="98" font-size="44" letter-spacing="3" fill="url(#parilti)">İSTİKBAL GÖKLERDEDİR</text>
</g>
<text x="56" y="138" class="gv" font-size="30" fill="{KREM}">— Mustafa Kemal Atatürk</text>
<text x="52" y="168" class="jb" font-size="12" letter-spacing="2" fill="{ALTIN}">TEKNOFEST RUHU · BAYKAR · MİLLİ TEKNOLOJİ HAMLESİ</text>
</g>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="none" stroke="{ALTIN}" stroke-opacity=".7" stroke-width="2"/>
'''
    return svg(W, H, "İstikbal göklerdedir — Milli teknoloji hamlesi", govde,
               ("Cinzel:700", "Great Vibes", "JetBrains Mono:400"))


# ─────────────────────────────── 5) ALT BİLGİ ───────────────────────────────

def altbilgi():
    W, H = 1000, 250
    kh = KILIM_SATIR * 2.2
    govde = f'''<defs>
  {selcuklu_deseni("cini", 56, ALTIN, .08)}
  {altin_gradyan("altin")}
  {parilti_gradyan("parilti", "5s")}
  <radialGradient id="hale" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{AL}" stop-opacity=".25"/><stop offset="1" stop-color="{AL}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="{GECE}"/>
<rect width="{W}" height="{H}" fill="url(#cini)"/>
<ellipse cx="500" cy="{H/2}" rx="380" ry="90" fill="url(#hale)"/>
{kilim_serit(0, 0, W, 2.2, "k1")}
{kilim_serit(0, H - kh, W, 2.2, "k2")}
{lale(90, 128, .9, -8)}{lale(910, 128, .9, 8)}
{lale(160, 140, .55, -24, CINI)}{lale(840, 140, .55, 24, CINI)}
<g text-anchor="middle">
  <text x="500" y="126" class="cz" font-weight="700" font-size="40" letter-spacing="4" fill="url(#altin)">NE MUTLU TÜRKÜM DİYENE!</text>
  <text x="500" y="126" class="cz" font-weight="700" font-size="40" letter-spacing="4" fill="url(#parilti)">NE MUTLU TÜRKÜM DİYENE!</text>
  <text x="500" y="162" class="gv" font-size="28" fill="{KREM}">Mustafa Kemal Atatürk</text>
  <text x="500" y="192" class="jb" font-size="12" letter-spacing="2" fill="{CINI}">stay curious • stay ethical • kapsam yoksa tarama yok</text>
</g>
'''
    return svg(W, H, "Ne mutlu Türküm diyene!", govde, ("Cinzel:700", "Great Vibes", "JetBrains Mono:400"))


# ─────────────────────────────── ÇALIŞTIR ───────────────────────────────

URETICILER = {
    "baslik.svg": baslik,
    "kilim.svg": ayrac,
    "ataturk.svg": ataturk,
    "gokler.svg": gokler,
    "altbilgi.svg": altbilgi,
}


def main():
    for ad, fn in URETICILER.items():
        (CIKTI / ad).write_text(fn(), encoding="utf-8")
        print("yazıldı:", ad)


if __name__ == "__main__":
    main()
