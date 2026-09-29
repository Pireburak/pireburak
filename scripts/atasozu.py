"""README'deki 'Günün Atasözü' bölümünü günceller.

Her gün (İstanbul saatiyle) listeden bir atasözü seçer ve
<!-- ATASOZU:START --> / <!-- ATASOZU:END --> işaretleri arasına yazar.
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- ATASOZU:START -->", "<!-- ATASOZU:END -->"

# (atasözü, siber güvenlik yorumu)
ATASOZLERI = [
    ("Dost acı söyler.", "İyi bir pentest raporu da öyle."),
    ("Damlaya damlaya göl olur.", "Küçük bilgi sızıntıları da büyük bir ihlale dönüşür."),
    ("Sakla samanı, gelir zamanı.", "Logları sakla; olay müdahalesinde hepsi lazım olur."),
    ("Ak akçe kara gün içindir.", "Yedek de kara gün içindir: 3-2-1 kuralını unutma."),
    ("Bin bilsen de bir bilene danış.", "Code review atlanmaz."),
    ("Aceleyle giden ecele gider.", "Test edilmeden prod'a çıkan yama da."),
    ("Ağaç yaşken eğilir.", "Güvenlik tasarım aşamasında başlar: secure by design."),
    ("Bir musibet bin nasihatten iyidir.", "Her olay bir post-mortem, her post-mortem bir ders."),
    ("Ne ekersen onu biçersin.", "Input'u doğrulamazsan SQL injection biçersin."),
    ("Az olsun, öz olsun.", "En az yetki ilkesi: least privilege."),
    ("Söz gümüşse sükût altındır.", "Hata mesajları da az konuşmalı; stack trace sızdırma."),
    ("Bugünün işini yarına bırakma.", "Bugünün yamasını da."),
    ("Tatlı dil yılanı deliğinden çıkarır.", "Sosyal mühendislik de öyle; oltalamaya dikkat."),
    ("Duvarın da kulağı var.", "Şifrelenmemiş trafiğin de: her yerde TLS."),
    ("Yalancının mumu yatsıya kadar yanar.", "Sahte sertifikanın da; imzaları doğrula."),
    ("Her yiğidin bir yoğurt yiyişi vardır.", "Her saldırganın bir TTP'si: MITRE ATT&CK."),
    ("Keskin sirke küpüne zarar.", "Agresif tarama hem hedefi hem seni yakar; rate limit koy."),
    ("Kaz gelecek yerden tavuk esirgenmez.", "Güvenlik yatırımı, ihlalin maliyetinden ucuzdur."),
    ("Güvenme varlığa, düşersin darlığa.", "Güvenme varsayılan ayarlara, düşersin ihlale."),
    ("Üzüm üzüme baka baka kararır.", "Yamanmamış tek sunucu bütün ağı riske atar."),
    ("Kervan yolda düzülür.", "Ama güvenlik yolda sonradan eklenmez."),
    ("Minareyi çalan kılıfını hazırlar.", "Saldırgan da izini siler; logları merkezi tut."),
    ("Sabrın sonu selamettir.", "Sabırlı keşif, gürültülü brute-force'tan iyidir."),
    ("İşleyen demir ışıldar.", "Her gün biraz CTF, her gün biraz daha keskin."),
]


def main() -> None:
    now = datetime.now(ZoneInfo("Europe/Istanbul"))
    gun = now.timetuple().tm_yday
    atasozu, yorum = ATASOZLERI[(now.year * 366 + gun) % len(ATASOZLERI)]

    blok = "\n".join([
        START,
        "```bash",
        f"┌──(pireburak㉿kali)-[~]",
        f"└─$ fortune tr-atasozleri --gun {gun}",
        f'📜  "{atasozu}"',
        f"🛡️  └─> {yorum}",
        "```",
        f"<sub>🕰️ Son güncelleme: {now:%d.%m.%Y} · İstanbul saatiyle her gece otomatik yenilenir.</sub>",
        END,
    ])

    metin = README.read_text(encoding="utf-8")
    bas, son = metin.index(START), metin.index(END) + len(END)
    README.write_text(metin[:bas] + blok + metin[son:], encoding="utf-8")


if __name__ == "__main__":
    main()
