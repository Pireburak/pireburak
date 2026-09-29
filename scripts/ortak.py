"""Profil SVG'lerinde ortak kullanılan renkler, fontlar ve Türk motifleri."""

import base64
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
FONTLAR = KOK / "assets" / "fonts"

# Palet: gece laciverti, İznik çinisi, tezhip altını, kök boya kırmızısı
GECE = "#0B1426"
GECE2 = "#13233F"
LACIVERT = "#1B2A4A"
CINI = "#2EC4B6"
KOBALT = "#1E5AA8"
ALTIN = "#D4AF37"
ALTIN_ACIK = "#F2D675"
AL = "#E30A17"
KOKBOYA = "#A4161A"
KREM = "#F4E9D8"
SOLUK = "#8A96AD"

_FONT_DOSYA = {
    "Cinzel": [("cinzel-500.woff2", 500), ("cinzel-700.woff2", 700)],
    "Great Vibes": [("greatvibes.woff2", 400)],
    "JetBrains Mono": [("jbm-400.woff2", 400), ("jbm-700.woff2", 700)],
}


def font_css(*aileler: str) -> str:
    """İstenen fontları gömülü @font-face olarak döndürür ("Cinzel" veya "Cinzel:700")."""
    css = []
    for istek in aileler:
        aile, _, sadece = istek.partition(":")
        for dosya, agirlik in _FONT_DOSYA[aile]:
            if sadece and int(sadece) != agirlik:
                continue
            veri = base64.b64encode((FONTLAR / dosya).read_bytes()).decode()
            css.append(
                f"@font-face{{font-family:'{aile}';font-weight:{agirlik};"
                f"src:url(data:font/woff2;base64,{veri}) format('woff2');}}"
            )
    return "\n".join(css)


def esc(metin: str) -> str:
    return (str(metin).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ─────────────────────────────── KİLİM ───────────────────────────────

_KILIM_RENK = {
    "i": LACIVERT, "r": KOKBOYA, "g": ALTIN, "c": KREM, "t": CINI, "o": "#233B6E",
}

# Elibelinde: bereket ve anneliğin sembolü
_ELIBELINDE = [
    ".....c.....",
    "....coc....",
    ".....c.....",
    ".cc.ccc.cc.",
    ".c.ccocc.c.",
    "..cccoccc..",
    "....coc....",
    "..cccoccc..",
    ".c.ccocc.c.",
    ".cc.ccc.cc.",
    ".....c.....",
]

# Koçboynuzu: güç ve kahramanlık
_KOCBOYNUZU = [
    "...........",
    ".gg.....gg.",
    "g..g...g..g",
    "g..g...g..g",
    ".g.g...g.g.",
    "...ggggg...",
    "....gtg....",
    "...ggggg...",
    ".g.g...g.g.",
    "g..g...g..g",
    "g..g...g..g",
]


def _goz() -> list[str]:
    """Nazar/göz motifi: iç içe baklavalar."""
    satirlar = []
    for y in range(11):
        s = ""
        for x in range(11):
            d = abs(x - 5) + abs(y - 5)
            s += {5: "g", 4: ".", 3: "c", 2: "i"}.get(d, "t" if d <= 1 else ".")
        satirlar.append(s)
    return satirlar


def _ayrac() -> list[str]:
    satirlar = []
    for y in range(11):
        s = ""
        for x in range(5):
            d = abs(x - 2) + abs(y - 5)
            s += "g" if d <= 1 else ("c" if d == 2 else ".")
        satirlar.append(s)
    return satirlar


def kilim_izgara(sutun: int) -> list[str]:
    """17 satırlık kilim şeridinin renk ızgarasını üretir."""
    motifler = [_ELIBELINDE, _goz(), _KOCBOYNUZU, _goz()]
    orta = ["" for _ in range(11)]
    i = 0
    while len(orta[0]) < sutun:
        parca = motifler[i % len(motifler)]
        ayr = _ayrac()
        for y in range(11):
            orta[y] += ayr[y] + parca[y]
        i += 1
    orta = [s[:sutun] for s in orta]

    def cizgi(fn):
        return "".join(fn(x) for x in range(sutun))

    izgara = [
        cizgi(lambda x: "i"),
        cizgi(lambda x: "g" if x % 2 == 0 else "i"),
        cizgi(lambda x: "r"),
        *[s.replace(".", "r") for s in orta],
        cizgi(lambda x: "r"),
        cizgi(lambda x: "t" if x % 4 in (0, 1) else "r"),
        cizgi(lambda x: "g" if x % 2 == 1 else "i"),
        cizgi(lambda x: "i"),
    ]
    return izgara


KILIM_DONEM = 64  # motif dizisinin tekrar ettiği sütun sayısı


def kilim_serit(x: float, y: float, genislik: float, hucre: float = 5.0, id_: str = "kilim") -> str:
    """Verilen konuma yatay bir kilim şeridi çizer (yükseklik = 17 * hücre).

    Tek bir motif dönemi <pattern> olarak, her renk tek bir <path> ile çizilir.
    """
    izgara = kilim_izgara(KILIM_DONEM)
    yollar: dict[str, list[str]] = {}
    for r, satir in enumerate(izgara):
        c = 0
        while c < len(satir):
            renk = satir[c]
            bas = c
            while c < len(satir) and satir[c] == renk:
                c += 1
            yollar.setdefault(renk, []).append(f"M{bas} {r}h{c - bas}v1h-{c - bas}z")
    govde = "".join(f'<path fill="{_KILIM_RENK[k]}" d="{"".join(v)}"/>' for k, v in yollar.items())
    dw = KILIM_DONEM * hucre
    return (f'<defs><pattern id="{id_}" width="{dw:g}" height="{KILIM_SATIR * hucre:g}" '
            f'patternUnits="userSpaceOnUse" x="{x:g}" y="{y:g}">'
            f'<g transform="scale({hucre:g})" shape-rendering="crispEdges">{govde}</g></pattern></defs>'
            f'<rect x="{x:g}" y="{y:g}" width="{genislik:g}" height="{KILIM_SATIR * hucre:g}" fill="url(#{id_})"/>')


KILIM_SATIR = 17


# ─────────────────────────────── ÇİNİ & TEZHİP ───────────────────────────────

def yildiz_noktalari(cx, cy, dis, ic, uc=8, donus=0.0) -> str:
    import math
    nokta = []
    for i in range(uc * 2):
        a = math.radians(donus + i * 180 / uc - 90)
        r = dis if i % 2 == 0 else ic
        nokta.append(f"{cx + r * math.cos(a):.2f},{cy + r * math.sin(a):.2f}")
    return " ".join(nokta)


def selcuklu_deseni(id_: str, boyut: int = 60, renk: str = ALTIN, opaklik: float = 0.10) -> str:
    """Selçuklu yıldız-haç çini deseni (<pattern>)."""
    s = boyut
    y1 = yildiz_noktalari(0, 0, s * 0.42, s * 0.30)
    y2 = yildiz_noktalari(s / 2, s / 2, s * 0.42, s * 0.30)
    kose = [yildiz_noktalari(px, py, s * 0.42, s * 0.30) for px, py in ((s, 0), (0, s), (s, s))]
    stil = f'fill="none" stroke="{renk}" stroke-opacity="{opaklik}" stroke-width="1"'
    poli = "".join(f'<polygon points="{p}" {stil}/>' for p in [y1, y2, *kose])
    return (f'<pattern id="{id_}" width="{s}" height="{s}" patternUnits="userSpaceOnUse">'
            f'{poli}<circle cx="{s/2}" cy="{s/2}" r="{s*0.08}" fill="{renk}" fill-opacity="{opaklik}"/>'
            f'</pattern>')


def lale(x, y, olcek=1.0, aci=0, renk=AL, kontur=ALTIN) -> str:
    """Osmanlı lalesi (100x100 kutuda çizilir)."""
    return f'''<g transform="translate({x} {y}) rotate({aci}) scale({olcek}) translate(-50 -50)">
  <path d="M50 70 C50 80 48 90 45 100" fill="none" stroke="{kontur}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M47 90 C38 82 28 84 20 76 C30 92 40 95 47 94Z" fill="{CINI}" stroke="{kontur}" stroke-width="1"/>
  <path d="M49 84 C58 78 66 80 74 72 C66 88 57 90 49 89Z" fill="{CINI}" stroke="{kontur}" stroke-width="1"/>
  <path d="M50 70 C35 68 27 50 31 28 C38 42 45 50 50 58Z" fill="{renk}" stroke="{kontur}" stroke-width="1.2"/>
  <path d="M50 70 C65 68 73 50 69 28 C62 42 55 50 50 58Z" fill="{renk}" stroke="{kontur}" stroke-width="1.2"/>
  <path d="M50 16 C59 32 61 54 50 70 C39 54 41 32 50 16Z" fill="{renk}" stroke="{kontur}" stroke-width="1.2"/>
  <path d="M50 26 C54 38 54 52 50 64" fill="none" stroke="{ALTIN_ACIK}" stroke-opacity=".55" stroke-width="1"/>
</g>'''


def hatayi(x, y, r=14, yaprak=8, renk=ALTIN, ic=AL) -> str:
    """Hatayi/rozet çiçeği."""
    parca = [f'<g transform="translate({x} {y})">']
    for i in range(yaprak):
        parca.append(
            f'<ellipse cx="0" cy="{-r * 0.55:.2f}" rx="{r * 0.26:.2f}" ry="{r * 0.5:.2f}" '
            f'transform="rotate({i * 360 / yaprak:.1f})" fill="{renk}" fill-opacity=".9"/>'
        )
    parca.append(f'<circle r="{r * 0.32:.2f}" fill="{ic}" stroke="{renk}" stroke-width="1.2"/>')
    parca.append(f'<circle r="{r * 0.12:.2f}" fill="{ALTIN_ACIK}"/></g>')
    return "".join(parca)


def tezhip_cerceve(x, y, w, h, renk=ALTIN) -> str:
    """Çift altın çizgili tezhip çerçevesi + köşe rozetleri."""
    p = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="{renk}" stroke-width="2"/>',
        f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="6" fill="none" '
        f'stroke="{renk}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="2 4"/>',
    ]
    for kx, ky in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        p.append(f'<polygon points="{yildiz_noktalari(kx, ky, 13, 6)}" fill="{GECE}" stroke="{renk}" stroke-width="1.5"/>')
        p.append(f'<circle cx="{kx}" cy="{ky}" r="3" fill="{AL}"/>')
    return "".join(p)


def parilti_gradyan(id_: str, sure: str = "6s") -> str:
    """Yüzeyde soldan sağa kayan altın parıltı."""
    return f'''<linearGradient id="{id_}" x1="-1" y1="0" x2="0" y2="0" gradientUnits="objectBoundingBox">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".5" stop-color="{ALTIN_ACIK}" stop-opacity=".35"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  <animate attributeName="x1" values="-1;2" dur="{sure}" repeatCount="indefinite"/>
  <animate attributeName="x2" values="0;3" dur="{sure}" repeatCount="indefinite"/>
</linearGradient>'''


def altin_gradyan(id_: str) -> str:
    return f'''<linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{ALTIN_ACIK}"/>
  <stop offset=".55" stop-color="{ALTIN}"/>
  <stop offset="1" stop-color="#9C7A1E"/>
</linearGradient>'''
