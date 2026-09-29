"""GitHub verisinden profil kartlarını üretir (dış servis bağımlılığı yok).

Kullanım:
  GITHUB_TOKEN=... python scripts/profil.py --kullanici Pireburak --cikti dist
  python scripts/profil.py --veri ornek.json --cikti /tmp/onizleme   # çevrimdışı önizleme

Üretilen dosyalar: istatistik.svg, diller.svg, katki-kilimi.svg, reconclaw.svg,
rozet-takipci.svg, rozet-yildiz.svg
"""

import argparse
import json
import os
import sys
import textwrap
import urllib.request
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from ortak import (AL, ALTIN, ALTIN_ACIK, CINI, GECE, GECE2, KILIM_SATIR, KOKBOYA, KREM, LACIVERT,
                   SOLUK, altin_gradyan, esc, font_css, hatayi, kilim_serit, lale,
                   parilti_gradyan, selcuklu_deseni, tezhip_cerceve, yildiz_noktalari)

ONE_CIKAN_DEPO = "ReconClaw"

SORGU = """
query($login: String!, $depo: String!) {
  user(login: $login) {
    login
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        name stargazerCount forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
    repository(name: $depo) {
      name description stargazerCount forkCount url
      primaryLanguage { name color }
    }
  }
}
"""


def veri_cek(kullanici: str, token: str) -> dict:
    istek = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": SORGU, "variables": {"login": kullanici, "depo": ONE_CIKAN_DEPO}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "pireburak-profil"},
    )
    with urllib.request.urlopen(istek, timeout=30) as yanit:
        govde = json.load(yanit)
    if govde.get("errors") and not (govde.get("data") or {}).get("user"):
        raise SystemExit(f"GraphQL hatası: {govde['errors']}")
    return govde["data"]["user"]


# ─────────────────────────────── HESAPLAR ───────────────────────────────

def gunler(u):
    return [g for h in u["contributionsCollection"]["contributionCalendar"]["weeks"]
            for g in h["contributionDays"]]


def seriler(gun_listesi):
    sayilar = [g["contributionCount"] for g in gun_listesi]
    en_uzun = simdi = 0
    for s in sayilar:
        simdi = simdi + 1 if s else 0
        en_uzun = max(en_uzun, simdi)
    # bugün henüz katkı yoksa seri dünden sayılır
    i = len(sayilar) - 1
    if i >= 0 and sayilar[i] == 0:
        i -= 1
    guncel = 0
    while i >= 0 and sayilar[i]:
        guncel += 1
        i -= 1
    return guncel, en_uzun


def diller(u, adet=8):
    toplam = Counter()
    renk = {}
    for depo in u["repositories"]["nodes"]:
        for kenar in depo["languages"]["edges"]:
            ad = kenar["node"]["name"]
            toplam[ad] += kenar["size"]
            renk[ad] = kenar["node"]["color"] or SOLUK
    hepsi = sum(toplam.values()) or 1
    return [(ad, boyut / hepsi * 100, renk[ad]) for ad, boyut in toplam.most_common(adet)]


def bicim(n: int) -> str:
    return f"{n:,}".replace(",", ".")


# ─────────────────────────────── SVG ORTAK ───────────────────────────────

def svg(w, h, baslik, govde, fontlar=("Cinzel:700", "JetBrains Mono:400", "JetBrains Mono:700"), stil=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(baslik)}">
<title>{esc(baslik)}</title>
<style>
{font_css(*fontlar)}
.cz{{font-family:'Cinzel',serif;font-weight:700}} .jb{{font-family:'JetBrains Mono',monospace}}
.belir{{animation:belir .6s ease-out both}}
@keyframes belir{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
{stil}
</style>
{govde}
</svg>
'''


def kart_zemini(w, h, baslik, alt_baslik=""):
    return f'''<defs>
  {selcuklu_deseni("cini", 48, ALTIN, .06)}
  {altin_gradyan("altin")}
  {parilti_gradyan("parilti", "8s")}
  <linearGradient id="zemin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GECE}"/><stop offset="1" stop-color="{GECE2}"/></linearGradient>
</defs>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#zemin)"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#cini)"/>
{tezhip_cerceve(10, 10, w - 20, h - 20)}
<rect x="10" y="10" width="{w-20}" height="{h-20}" rx="10" fill="none" stroke="url(#parilti)" stroke-width="2.5"/>
<text x="36" y="50" class="cz" font-size="17" letter-spacing="3" fill="url(#altin)">{esc(baslik)}</text>
<text x="{w - 36}" y="50" text-anchor="end" class="jb" font-size="11" fill="{SOLUK}">{esc(alt_baslik)}</text>
<line x1="36" y1="62" x2="{w - 36}" y2="62" stroke="{ALTIN}" stroke-opacity=".35"/>
'''


# ─────────────────────────────── 1) İSTATİSTİK DEFTERİ ───────────────────────────────

def istatistik_karti(u):
    W, H = 495, 260
    g = gunler(u)
    guncel, en_uzun = seriler(g)
    yildiz = sum(d["stargazerCount"] for d in u["repositories"]["nodes"])
    cc = u["contributionsCollection"]
    satirlar = [
        ("Toplam yıldız", yildiz, ALTIN),
        ("Katkı · son 1 yıl", cc["contributionCalendar"]["totalContributions"], AL),
        ("Commit · son 1 yıl", cc["totalCommitContributions"], CINI),
        ("Pull request", u["pullRequests"]["totalCount"], ALTIN),
        ("Issue", u["issues"]["totalCount"], AL),
        ("Depo", u["repositories"]["totalCount"], CINI),
        ("En uzun seri", f"{en_uzun} gün", ALTIN),
    ]
    govde = [kart_zemini(W, H, "İSTATİSTİK DEFTERİ", f"@{u['login']}")]
    for i, (etiket, deger, renk) in enumerate(satirlar):
        y = 90 + i * 23
        deger = bicim(deger) if isinstance(deger, int) else deger
        govde.append(
            f'<g class="belir" style="animation-delay:{.15 + i * .12:.2f}s">'
            f'<polygon points="{yildiz_noktalari(44, y - 4, 6, 3)}" fill="{renk}"/>'
            f'<text x="58" y="{y}" class="jb" font-size="13" fill="{KREM}">{esc(etiket)}</text>'
            f'<text x="300" y="{y}" text-anchor="end" class="jb" font-weight="700" font-size="13" fill="{ALTIN_ACIK}">{esc(deger)}</text>'
            f'</g>')
    # sağda seri madalyonu
    cx, cy = 395, 150
    govde.append(f'''<g>
  <circle cx="{cx}" cy="{cy}" r="66" fill="{GECE}" stroke="{ALTIN}" stroke-opacity=".4"/>
  <g><polygon points="{yildiz_noktalari(cx, cy, 62, 47)}" fill="none" stroke="{ALTIN}" stroke-width="1.5"/>
    <polygon points="{yildiz_noktalari(cx, cy, 54, 42, 8, 22.5)}" fill="none" stroke="{CINI}" stroke-opacity=".6"/>
    <animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="60s" repeatCount="indefinite"/></g>
  <circle cx="{cx}" cy="{cy}" r="40" fill="{LACIVERT}" stroke="{ALTIN}" stroke-width="1.5"/>
  <text x="{cx}" y="{cy + 10}" text-anchor="middle" class="cz" font-size="32" fill="url(#altin)">{guncel}</text>
  <text x="{cx}" y="{cy + 28}" text-anchor="middle" class="jb" font-size="9" letter-spacing="2" fill="{CINI}">GÜN SERİ</text>
  {hatayi(cx, cy - 66, 8)}
</g>''')
    return svg(W, H, f"{u['login']} — İstatistik Defteri", "".join(govde))


# ─────────────────────────────── 2) DİL DOKUMASI ───────────────────────────────

def diller_karti(u):
    W, H = 495, 260
    liste = diller(u)
    govde = [kart_zemini(W, H, "DİL DOKUMASI", "depo boyutuna göre")]
    govde.append('''<defs><pattern id="dokuma" width="6" height="6" patternUnits="userSpaceOnUse">
  <path d="M0 6 L6 0 M-1 1 L1 -1 M5 7 L7 5" stroke="#fff" stroke-opacity=".22" stroke-width="1.2"/></pattern>
  <clipPath id="serit"><rect x="36" y="82" width="423" height="24" rx="5"/></clipPath></defs>''')
    x = 36.0
    govde.append('<g clip-path="url(#serit)">')
    for i, (ad, yuzde, renk) in enumerate(liste):
        w = 423 * yuzde / 100
        govde.append(f'<rect x="{x:.2f}" y="82" width="{w + .5:.2f}" height="24" fill="{renk}">'
                     f'<animate attributeName="width" from="0" to="{w + .5:.2f}" dur=".8s" begin="{i * .12:.2f}s" fill="freeze"/></rect>')
        x += w
    govde.append('<rect x="36" y="82" width="423" height="24" fill="url(#dokuma)"/></g>')
    govde.append(f'<rect x="36" y="82" width="423" height="24" rx="5" fill="none" stroke="{ALTIN}" stroke-width="1.5"/>')
    for i, (ad, yuzde, renk) in enumerate(liste):
        sutun, satir = divmod(i, 4)
        lx, ly = 44 + sutun * 215, 138 + satir * 24
        govde.append(
            f'<g class="belir" style="animation-delay:{.3 + i * .1:.2f}s">'
            f'<rect x="{lx - 5}" y="{ly - 9}" width="10" height="10" transform="rotate(45 {lx} {ly - 4})" fill="{renk}" stroke="{ALTIN}" stroke-width=".8"/>'
            f'<text x="{lx + 14}" y="{ly}" class="jb" font-size="12.5" fill="{KREM}">{esc(ad)}</text>'
            f'<text x="{lx + 190}" y="{ly}" text-anchor="end" class="jb" font-weight="700" font-size="12.5" fill="{ALTIN_ACIK}">%{yuzde:.1f}</text>'
            f'</g>')
    if not liste:
        govde.append(f'<text x="{W/2}" y="160" text-anchor="middle" class="jb" font-size="13" fill="{SOLUK}">Henüz dil verisi yok</text>')
    return svg(W, H, f"{u['login']} — Dil Dokuması", "".join(govde))


# ─────────────────────────────── 3) KATKI KİLİMİ ───────────────────────────────

SEVIYE_RENK = {
    "NONE": "#16233D",
    "FIRST_QUARTILE": "#6B1D26",
    "SECOND_QUARTILE": "#A4161A",
    "THIRD_QUARTILE": "#E0412F",
    "FOURTH_QUARTILE": "#F2B541",
}
AYLAR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def kilim_karti(u):
    W, H = 1000, 320
    g = gunler(u)
    guncel, en_uzun = seriler(g)
    toplam = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    hucre = 15.6
    x0, y0 = 118, 128
    kh = KILIM_SATIR * 2

    govde = [f'''<defs>
  {selcuklu_deseni("cini", 48, ALTIN, .05)}
  {altin_gradyan("altin")}
  {parilti_gradyan("parilti", "6s")}
</defs>
<rect x="30" y="0" width="{W - 60}" height="{H}" fill="{GECE}"/>
<rect x="30" y="0" width="{W - 60}" height="{H}" fill="url(#cini)"/>
{kilim_serit(30, 0, W - 60, 2, "ku")}
{kilim_serit(30, H - kh, W - 60, 2, "ka")}''']
    # saçaklar
    for kenar in (0, W - 30):
        cizgiler = "".join(
            f'<line x1="{kenar + 2}" y1="{y}" x2="{kenar + 28}" y2="{y + (1.5 if (y // 6) % 2 else -1.5)}"/>'
            for y in range(6, H - 4, 6))
        govde.append(f'<g stroke="{KREM}" stroke-opacity=".55" stroke-width="1.6" stroke-linecap="round">{cizgiler}</g>')
    govde.append(f'''<text x="70" y="80" class="cz" font-size="22" letter-spacing="4" fill="url(#altin)">KATKI KİLİMİ</text>
<text x="70" y="80" class="cz" font-size="22" letter-spacing="4" fill="url(#parilti)">KATKI KİLİMİ</text>
<text x="930" y="80" text-anchor="end" class="jb" font-size="12.5" fill="{KREM}">son 1 yılda <tspan fill="{ALTIN_ACIK}" font-weight="700">{bicim(toplam)}</tspan> katkı  ·  şu anki seri <tspan fill="{ALTIN_ACIK}" font-weight="700">{guncel}</tspan> gün  ·  en uzun <tspan fill="{ALTIN_ACIK}" font-weight="700">{en_uzun}</tspan> gün</text>''')
    for etiket, satir in (("Pzt", 1), ("Çar", 3), ("Cum", 5)):
        govde.append(f'<text x="{x0 - 14}" y="{y0 + satir * hucre + 4}" text-anchor="end" class="jb" font-size="10" fill="{SOLUK}">{etiket}</text>')

    if g:
        ilk = date.fromisoformat(g[0]["date"])
        baslangic = ilk - timedelta(days=(ilk.weekday() + 1) % 7)  # haftanın pazar günü
    son_ay = None
    for gun in g:
        t = date.fromisoformat(gun["date"])
        hafta = (t - baslangic).days // 7
        satir = (t.weekday() + 1) % 7
        cx = x0 + hafta * hucre + hucre / 2
        cy = y0 + satir * hucre
        if t.day <= 7 and satir == 0 and t.month != son_ay:
            son_ay = t.month
            govde.append(f'<text x="{cx - hucre / 2}" y="{y0 - 16}" class="jb" font-size="10" fill="{SOLUK}">{AYLAR[t.month - 1]}</text>')
        r = hucre / 2 + .4
        renk = SEVIYE_RENK.get(gun["contributionLevel"], SEVIYE_RENK["NONE"])
        kenar = f' stroke="{ALTIN}" stroke-opacity=".5" stroke-width=".6"' if gun["contributionLevel"] != "NONE" else ""
        govde.append(
            f'<polygon class="belir" style="animation-delay:{hafta * .035:.3f}s" '
            f'points="{cx:.1f},{cy - r:.1f} {cx + r:.1f},{cy:.1f} {cx:.1f},{cy + r:.1f} {cx - r:.1f},{cy:.1f}" fill="{renk}"{kenar}>'
            f'<title>{t.day} {AYLAR[t.month - 1]} {t.year}: {gun["contributionCount"]} katkı</title></polygon>')
    # açıklama
    lx = 780
    govde.append(f'<text x="{lx - 8}" y="{y0 + 7 * hucre + 26}" text-anchor="end" class="jb" font-size="10" fill="{SOLUK}">az</text>')
    for i, renk in enumerate(SEVIYE_RENK.values()):
        cx, cy = lx + 8 + i * 20, y0 + 7 * hucre + 22
        govde.append(f'<polygon points="{cx},{cy - 8} {cx + 8},{cy} {cx},{cy + 8} {cx - 8},{cy}" fill="{renk}"/>')
    govde.append(f'<text x="{lx + 104}" y="{y0 + 7 * hucre + 26}" class="jb" font-size="10" fill="{SOLUK}">çok</text>')
    govde.append(f'<text x="70" y="{y0 + 7 * hucre + 26}" class="jb" font-size="10" fill="{SOLUK}">Her baklava bir gün; her ilmek bir katkı.</text>')
    return svg(W, H, f"{u['login']} — Katkı Kilimi", "".join(govde))


# ─────────────────────────────── 4) ÖNE ÇIKAN DEPO ───────────────────────────────

def depo_karti(u):
    W, H = 1000, 215
    d = u.get("repository")
    if not d:
        return None
    satirlar = textwrap.wrap(d.get("description") or "Açıklama yok.", 88)[:2]
    dil = d.get("primaryLanguage") or {"name": "—", "color": SOLUK}
    govde = [kart_zemini(W, H, "ÖNE ÇIKAN DEPO", "github.com/" + u["login"] + "/" + d["name"])]
    govde.append(lale(64, 118, .5, 0))
    govde.append(f'<text x="98" y="112" class="cz" font-size="28" fill="url(#altin)">{esc(d["name"])}</text>')
    for i, satir in enumerate(satirlar):
        govde.append(f'<text x="98" y="{136 + i * 18}" class="jb" font-size="13" fill="{KREM}">{esc(satir)}</text>')
    govde.append(f'''<g class="jb" font-size="12.5" transform="translate(98 {136 + len(satirlar) * 18 + 8})">
  <circle cx="5" cy="-4" r="5" fill="{dil["color"] or SOLUK}"/><text x="16" y="0" fill="{KREM}">{esc(dil["name"])}</text>
  <polygon points="{yildiz_noktalari(126, -4, 7, 3, 5)}" fill="{ALTIN}"/><text x="138" y="0" fill="{KREM}">{bicim(d["stargazerCount"])}</text>
  <g fill="none" stroke="{CINI}" stroke-width="1.6"><circle cx="198" cy="-11" r="2.2"/><circle cx="210" cy="-11" r="2.2"/><circle cx="204" cy="3" r="2.2"/>
    <path d="M198 -8.8 v2.8 q0 3 3 3 h6 q3 0 3 -3 v-2.8 M204 -3 v3.8"/></g><text x="220" y="0" fill="{KREM}">{bicim(d["forkCount"])}</text>
</g>''')
    # radar
    cx, cy = 900, 128
    govde.append(f'''<defs><linearGradient id="tarama" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CINI}" stop-opacity="0"/><stop offset="1" stop-color="{CINI}" stop-opacity=".6"/></linearGradient></defs>
<g transform="translate({cx} {cy})">
  <circle r="40" fill="{GECE}" stroke="{CINI}" stroke-opacity=".6"/><circle r="26" fill="none" stroke="{CINI}" stroke-opacity=".3"/><circle r="12" fill="none" stroke="{CINI}" stroke-opacity=".3"/>
  <g><path d="M0 0 L40 0 A40 40 0 0 0 28.3 -28.3Z" fill="url(#tarama)"/><animateTransform attributeName="transform" type="rotate" values="0;360" dur="3s" repeatCount="indefinite"/></g>
  <circle cx="14" cy="-18" r="2.5" fill="{AL}"><animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite"/></circle>
</g>''')
    return svg(W, H, f"{d['name']} — öne çıkan depo", "".join(govde))


# ─────────────────────────────── 5) ROZETLER ───────────────────────────────

def rozet(etiket: str, deger: str) -> str:
    """shields.io 'for-the-badge' ölçülerinde rozet (28px yükseklik)."""
    harf = 11 * .6 + 1.5  # JetBrains Mono 11px + harf aralığı
    sol = round(len(etiket) * harf + 22)
    sag = round(len(deger) * harf + 22)
    w = sol + sag
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="28" viewBox="0 0 {w} 28" role="img" aria-label="{esc(etiket)}: {esc(deger)}">
<title>{esc(etiket)}: {esc(deger)}</title>
<style>{font_css("JetBrains Mono:700")}</style>
<rect width="{sol}" height="28" fill="{KOKBOYA}"/><rect x="{sol}" width="{sag}" height="28" fill="{GECE}"/>
<g font-family="'JetBrains Mono',monospace" font-weight="700" font-size="11" letter-spacing="1.5" text-anchor="middle">
  <text x="{sol / 2 + .75}" y="18" fill="{KREM}">{esc(etiket)}</text>
  <text x="{sol + sag / 2 + .75}" y="18" fill="{ALTIN_ACIK}">{esc(deger)}</text>
</g>
</svg>
'''


def rozetler(u):
    yildiz = sum(d["stargazerCount"] for d in u["repositories"]["nodes"])
    return {
        "rozet-takipci.svg": rozet("TAKİPÇİ", bicim(u["followers"]["totalCount"])),
        "rozet-yildiz.svg": rozet("YILDIZ", bicim(yildiz)),
    }


# ─────────────────────────────── ÇALIŞTIR ───────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kullanici", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "Pireburak"))
    ap.add_argument("--cikti", default="dist")
    ap.add_argument("--veri", help="GraphQL 'user' yanıtını içeren JSON (çevrimdışı önizleme)")
    a = ap.parse_args()

    if a.veri:
        u = json.loads(Path(a.veri).read_text(encoding="utf-8"))
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("GITHUB_TOKEN gerekli.")
        u = veri_cek(a.kullanici, token)

    cikti = Path(a.cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    for ad, fn in (("istatistik.svg", istatistik_karti), ("diller.svg", diller_karti),
                   ("katki-kilimi.svg", kilim_karti), ("reconclaw.svg", depo_karti)):
        icerik = fn(u)
        if icerik:
            (cikti / ad).write_text(icerik, encoding="utf-8")
            print("yazıldı:", cikti / ad)
    for ad, icerik in rozetler(u).items():
        (cikti / ad).write_text(icerik, encoding="utf-8")
        print("yazıldı:", cikti / ad)


if __name__ == "__main__":
    main()
