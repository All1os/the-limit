"""THE LIMIT prototipinin TTS save'ini kurar (vault: board-games/the-limit/GDD-prototype.md).

Tek betik: kart yüzleri (yazı, resimsiz, GDD §13.1), arka yüzler, skor paneli, tur çizelgesi,
fişler, kural tahtası ve save JSON'u. Resimler TTS'in Mods/ klasörüne kopyalanır: macOS
TTS'in ~/Desktop'u okumasına izin vermiyor (SHOWDOWN'da 2026-10-05 doğrulandı).
Kart metni GDD'den birebir; GDD değişirse buradaki listeyi güncelleyip yeniden çalıştır.
Çalıştır: python3 kur.py
"""
import json, math, shutil, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT / "tts-dosyalari"
ASSETS = Path.home() / "Library/Tabletop Simulator/Mods/the-limit"
SAVES = Path.home() / "Library/Tabletop Simulator/Saves/prototipler"  # Yavuz save'leri bu klasörde topladı
SAVE_NAME = "THE-LIMIT-prototype"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/Fonts/Supplemental/"
def f(name, size): return ImageFont.truetype(FONT + name, size)

PAPER, INK = (245, 240, 228), (25, 22, 20)
GOLD, FELT = (212, 175, 75), (22, 64, 44)
# GDD §13.3 renkleri; NPC / karakter / hedef için ayrı tonlar.
COL = {"POINT": (40, 140, 70), "NEGATIVE": (225, 120, 30), "CRASH": (190, 30, 30),
       "SPECIAL": (40, 90, 180), "NPC TRIGGER": (115, 50, 155), "NPC": (55, 65, 75),
       "CHARACTER": (165, 125, 35), "OBJECTIVE": (30, 30, 30)}

# ------------------------------------------------------------------ kart listesi (GDD §6–§9)
# (ID, deste, tip satırı, isim, metin, büyük yazı | None, adet)
# deste: 1 = ana, 2 = NPC, 3 = karakter, 4 = hedef. Yedek 6 Trigger ayrı (RESERVE).
CARDS = [
    ("P05", 1, "POINT", "+5", "Gain 5 points.", "+5", 8),
    ("P10", 1, "POINT", "+10", "Gain 10 points.", "+10", 7),
    ("P20", 1, "POINT", "+20", "Gain 20 points.", "+20", 5),
    ("P30", 1, "POINT", "+30", "Gain 30 points.", "+30", 3),
    ("P50", 1, "POINT", "+50", "Gain 50 points.", "+50", 1),
    ("N05", 1, "NEGATIVE", "−5", "Lose 5 points. Your turn ends.", "−5", 3),
    ("N10", 1, "NEGATIVE", "−10", "Lose 10 points. Your turn ends.", "−10", 3),
    ("N20", 1, "NEGATIVE", "−20", "Lose 20 points. Your turn ends.", "−20", 2),
    ("CR", 1, "CRASH", "CRASH", "Your round score becomes 0. Your turn ends. You stay in the round.", "CRASH", 4),
    ("S-DBL", 1, "SPECIAL", "DOUBLE", "Keep this in front of you. Your next Point Card this turn is doubled. Then discard this. (Discard at end of turn if unused.)", None, 2),
    ("S-2ND", 1, "SPECIAL", "SECOND DRAW", "Immediately draw another card and resolve it.", None, 2),
    ("S-SAFE", 1, "SPECIAL", "SAFE PASS", "Keep this in front of you. Once this turn, when you draw a Negative Card or CRASH, you may discard it unresolved and draw a new card. (Discard at end of turn if unused.)", None, 2),
    ("S-STL", 1, "SPECIAL", "STEAL", "Take 10 points from another player (all of them if they have fewer than 10).", None, 1),
    ("S-FRC", 1, "SPECIAL", "FORCED PUSH", "You must draw another card now. You cannot CASH OUT before resolving it.", None, 1),
    ("T-NPC", 1, "NPC TRIGGER", "DRAW AN NPC CARD", "Draw 1 card from the NPC Deck and resolve it. Then continue your turn unless it says otherwise.", None, 6),
    ("NPC01", 2, "NPC", "THE BOOKMAKER", "Choose another player. If their score is higher than yours, gain 15 points.", None, 1),
    ("NPC02", 2, "NPC", "THE COLLECTOR", "Choose another player. They lose 10 points; you gain 5 points.", None, 1),
    ("NPC03", 2, "NPC", "THE DEALER", "Draw 2 Main Deck cards. Resolve one; put the other on the bottom of the Main Deck.", None, 1),
    ("NPC04", 2, "NPC", "THE FIXER", "The next Negative Card you draw this turn has no effect (discard it; your turn continues).", None, 1),
    ("NPC05", 2, "NPC", "THE INFORMANT", "Look at the top 3 Main Deck cards and put them back in any order.", None, 1),
    ("NPC06", 2, "NPC", "THE LOAN SHARK", "Gain 30 points. Take a LOAN DEBT token: you must draw at least 2 more cards before you can CASH OUT.", None, 1),
    ("NPC07", 2, "NPC", "THE SABOTEUR", "Choose another player. They lose 10 points.", None, 1),
    ("NPC08", 2, "NPC", "THE SMUGGLER", "Put the top Main Deck card face down in front of you without looking. On a later turn this round, you may reveal and resolve it instead of drawing a card. If unused, it is shuffled back at round end.", None, 1),
    ("NPC09", 2, "NPC", "THE INSPECTOR", "Look at all face-down cards in front of another player (Smuggled card). If they have none, nothing happens.", None, 1),
    ("NPC10", 2, "NPC", "THE GAMBLER", "Draw 2 Main Deck cards and resolve both, one after the other. You cannot CASH OUT between them.", None, 1),
    ("NPC11", 2, "NPC", "THE BODYGUARD", "Take a BODYGUARD token. The next effect that would take away your points (Negative, CRASH, steal, any loss) is ignored. The token lasts until it is used or the round ends.", None, 1),
    ("NPC12", 2, "NPC", "THE THIEF", "Take 15 points from another player (all of them if they have fewer than 15).", None, 1),
    ("NPC13", 2, "NPC", "THE DEALER'S ASSISTANT", "Draw 1 Main Deck card. If it is a Point Card, gain 10 extra points. Otherwise resolve it normally.", None, 1),
    ("NPC14", 2, "NPC", "THE BROKER", "If you have at least 10 points, you may turn 10 of them into 20 (net +10).", None, 1),
    ("NPC15", 2, "NPC", "THE BOSS", "Choose one: gain 20 points, or make another player draw 1 Main Deck card (out-of-turn draw).", None, 1),
    ("NPC16", 2, "NPC", "THE CLEANER", "Remove one ENFORCED or LOAN DEBT token from yourself. If you have none, gain 5 points.", None, 1),
    ("NPC17", 2, "NPC", "THE GAMBLING ADDICT", "You must draw another card now. If it is a Point Card, gain 10 extra points.", None, 1),
    ("NPC18", 2, "NPC", "THE DRIVER", "Give 10 of your points to another player (all of them if you have fewer than 10).", None, 1),
    ("NPC19", 2, "NPC", "THE ENFORCER", "Choose another player who has not CASHED OUT. They take an ENFORCED token: on their next turn they must draw at least 2 cards before they can CASH OUT.", None, 1),
    ("NPC20", 2, "NPC", "THE INSIDER", "Look at the top Main Deck card. Leave it on top or put it on the bottom.", None, 1),
    ("C1", 3, "CHARACTER", "THE GAMBLER", "DOUBLE DOWN (once per round): after you resolve a Point Card, declare Double Down: your next Point Card this turn is doubled.\n\nMaximum risk", None, 1),
    ("C2", 3, "CHARACTER", "THE FIXER", "SECOND CHANCE (once per game): when you draw CRASH, keep half your score (round down) instead of 0. Your turn still ends.\n\nControl, caution", None, 1),
    ("C3", 3, "CHARACTER", "THE THIEF", "PICKPOCKET (once per round): when a Special or NPC card lets you take points from another player, take 5 more.\n\nInterfering", None, 1),
    ("C4", 3, "CHARACTER", "THE SURVIVOR", "NOT DEAD YET: after you CRASH, gain 5 points at the start of your next turn.\n\nRecovery", None, 1),
    ("C5", 3, "CHARACTER", "THE COLLECTOR", "CONNECTIONS (once per round): the first time you resolve an NPC Trigger, draw 2 NPC cards, resolve one, put the other on the bottom of the NPC Deck.\n\nNPC interaction", None, 1),
    ("O1", 4, "OBJECTIVE", "ONE MORE", "In 3 different turns, choose PUSH 3 or more times in a row in that turn.\n\nOnly voluntary PUSH decisions count, not forced draws. (3 players: 2 turns.)", None, 1),
    ("O2", 4, "OBJECTIVE", "CLEAN EXIT", "CASH OUT with 20 or more points 3 times.\n\nScore at the moment you declare CASH OUT (before Share the Risk). (3 players: 2 times.)", None, 1),
    ("O3", 4, "OBJECTIVE", "TAKE WHAT ISN'T YOURS", "Take a total of 40 points from other players over the game.\n\nSTEAL, THE THIEF, PICKPOCKET bonus, THE COLLECTOR's 5.", None, 1),
    ("O4", 4, "OBJECTIVE", "STILL STANDING", "2 times: suffer a CRASH, then reach 20+ points later in the same round.\n\nA CRASH cancelled by SAFE PASS or BODYGUARD does not count. The Fixer's half-score CRASH counts.", None, 1),
    ("O5", 4, "OBJECTIVE", "COLLECTION", "Resolve 5 different NPC cards yourself over the game.\n\nNPCs you put on the bottom don't count. Keep a private list.", None, 1),
]
RESERVE_N = 6
_n = {k: sum(c[6] for c in CARDS if c[1] == k) for k in (1, 2, 3, 4)}
assert _n == {1: 50, 2: 20, 3: 5, 4: 5}, _n   # GDD §13.8 sayım kontrolü


# ------------------------------------------------------------------ kart yüzleri
# 400x560: 10 sütun x 5 satır = 4000x2800, TTS'in 4096 sınırının altında. Yazı-only kart
# masada okunsun diye isim ve büyük değer iri.
W, H = 400, 560
COLS, ROWS = 10, 5


def wrap(d, text, font, width):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= width: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out


def fit(d, text, name, size, width):
    while size > 18 and d.textlength(text, font=f(name, size)) > width: size -= 2
    return f(name, size)


def face(c):
    cid, _, typ, name, text, big, _ = c
    col = COL[typ]
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=col, width=14)
    d.rectangle((0, 0, W, 64), fill=col)
    d.text((W / 2, 34), typ, font=f("Arial Black.ttf", 28), fill=PAPER, anchor="mm")
    if big:   # Point / Negative / CRASH: isim = büyük değer, iki kez yazma
        d.text((W / 2, 200), big, font=fit(d, big, "Arial Black.ttf", 150, W - 60), fill=col, anchor="mm")
        y = 330
    else:
        d.text((W / 2, 118), name, font=fit(d, name, "Arial Black.ttf", 44, W - 50), fill=INK, anchor="mm")
        y = 165
    size = 34
    while True:
        font = f("Arial.ttf", size)
        lines = wrap(d, text, font, W - 60)
        if y + len(lines) * (size + 6) < H - 50 or size <= 16: break
        size -= 2
    for ln in lines:
        d.text((W / 2, y), ln, font=font, fill=INK, anchor="ma")
        y += size + 6
    d.text((24, H - 40), cid, font=f("Arial Bold.ttf", 20), fill=col)
    return im


sheet = Image.new("RGB", (W * COLS, H * ROWS), PAPER)
INDEX = {}
for i, c in enumerate(CARDS):
    INDEX[c[0]] = i
    sheet.paste(face(c), ((i % COLS) * W, (i // COLS) * H))
sheet.save(OUT / "yuzler.png")


def back(fn, title, col, sub=""):
    im = Image.new("RGB", (W, H), col)
    d = ImageDraw.Draw(im)
    d.rectangle((18, 18, W - 18, H - 18), outline=GOLD, width=6)
    d.text((W / 2, H / 2 - 20), title, font=fit(d, title, "Arial Black.ttf", 60, W - 70), fill=GOLD, anchor="mm")
    if sub:
        d.text((W / 2, H / 2 + 40), sub, font=f("Arial Bold.ttf", 26), fill=PAPER, anchor="mm")
    im.save(OUT / fn)


back("arka-ana.png", "THE LIMIT", (90, 15, 20), "MAIN DECK")
back("arka-npc.png", "NPC", (35, 45, 55), "THE HOUSE")
back("arka-karakter.png", "CHARACTER", (120, 90, 25))
back("arka-hedef.png", "SECRET", (15, 15, 15), "OBJECTIVE")


# ------------------------------------------------------------------ masa parçaları
def panel_img():
    # Skor paneli: rakamı Lua butonu yazar; resim sadece zemin + başlık.
    im = Image.new("RGB", (900, 560), FELT)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, 892, 552), 40, outline=GOLD, width=14)
    d.text((450, 60), "SCORE", font=f("Arial Black.ttf", 52), fill=GOLD, anchor="mm")
    im.save(OUT / "panel.png")


def tracker_img():
    im = Image.new("RGB", (1400, 420), (40, 20, 25))
    d = ImageDraw.Draw(im)
    d.rectangle((6, 6, 1393, 413), outline=GOLD, width=10)
    for k, n in enumerate((6, 8, 10, 12)):
        x = 30 + k * 340
        d.rounded_rectangle((x, 30, x + 320, 390), 24, outline=GOLD, width=6)
        d.text((x + 160, 110), f"ROUND {k + 1}", font=f("Arial Black.ttf", 50), fill=GOLD, anchor="mm")
        d.text((x + 160, 300), f"NPC Triggers: {n}", font=f("Arial Bold.ttf", 34), fill=PAPER, anchor="mm")
    im.save(OUT / "tur.png")


def token_img(fn, text, col):
    im = Image.new("RGB", (400, 400), col)
    d = ImageDraw.Draw(im)
    d.ellipse((14, 14, 386, 386), outline=PAPER, width=12)
    lines = text.split(" ")
    for k, ln in enumerate(lines):
        y = 200 + (k - (len(lines) - 1) / 2) * 70
        d.text((200, y), ln, font=fit(d, ln, "Arial Black.ttf", 64, 300), fill=PAPER, anchor="mm")
    im.save(OUT / fn)


RULES = [
    ("YOUR TURN", True),
    ("Draw a Main Deck card (DRAW).", False),
    ("Point: add it, then PUSH or CASH OUT.", False),
    ("Negative: subtract (min 0). Turn ends.", False),
    ("CRASH: score = 0. Turn ends.", False),
    ("Special / NPC Trigger: follow the text.", False),
    ("Forced draws come before CASH OUT.", False),
    ("", False),
    ("ROUND END", True),
    ("Everyone cashed out, or Main Deck empty.", False),
    ("Lowest score is eliminated.", False),
    ("2 players left: one Final Round.", False),
    ("Win: reach the Final AND finish", False),
    ("your Secret Objective.", False),
]


def rules_img():
    im = Image.new("RGB", (1300, 1000), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1299, 999), outline=(90, 15, 20), width=20)
    y = 50
    for line, head in RULES:
        font = f("Arial Black.ttf", 56) if head else f("Arial Bold.ttf", 44)
        d.text((60, y), line, font=font, fill=(90, 15, 20) if head else INK)
        y += 74 if head else 62
    im.save(OUT / "kural.png")


panel_img(); tracker_img(); rules_img()
TOKENS = {  # isim: (dosya, renk) — GDD §2 durum fişleri + ilk oyuncu + yetenek
    "CASHED OUT": ("fis-cashed.png", (30, 120, 60)),
    "ENFORCED": ("fis-enforced.png", (170, 30, 30)),
    "LOAN DEBT": ("fis-loan.png", (210, 110, 20)),
    "BODYGUARD": ("fis-bodyguard.png", (35, 80, 170)),
    "ABILITY USED": ("fis-ability.png", (80, 80, 80)),
    "FIRST PLAYER": ("fis-first.png", (160, 120, 20)),
    "ROUND": ("fis-round.png", (200, 160, 40)),
}
for name, (fn, col) in TOKENS.items():
    token_img(fn, name, col)

for png in OUT.glob("*.png"):
    shutil.copy(png, ASSETS / png.name)
# Paylaşılabilir save için Steam Cloud adresleri (bulut.json; Yavuz TTS Cloud Manager'dan yükledi,
# adresler önbellekteki dosyalarla piksel eşleştirilerek çıkarıldı, 2026-10-05). Resim o günden
# beri değiştiyse sha1 tutmaz → yerel yol kullanılır; o resmi yeniden yükleyip bulut.json'u güncelle.
import hashlib
_BULUT = json.loads((ROOT / "bulut.json").read_text()) if (ROOT / "bulut.json").exists() else {}


def url(p):
    fn = Path(p).name
    b = _BULUT.get(fn)
    if b and hashlib.sha1((ASSETS / fn).read_bytes()).hexdigest() == b["sha1"]:
        return b["url"]
    print(f"  yerel (bulutta yok/eski): {fn}")
    return str(ASSETS / fn)

# ================================================================== save JSON
guid_n = 0


def guid():
    global guid_n
    guid_n += 1
    return f"{0xb00000 + guid_n:06x}"


def tr(x, z, rot_y=0.0, face_down=False, s=1.0, y=1.5):
    return {"posX": x, "posY": y, "posZ": z, "rotX": 0.0, "rotY": rot_y,
            "rotZ": 180.0 if face_down else 0.0, "scaleX": s, "scaleY": 1.0, "scaleZ": s}


def base(name, transform, nick="", desc="", **kw):
    o = {"GUID": guid(), "Name": name, "Transform": transform, "Nickname": nick,
         "Description": desc, "GMNotes": "", "Locked": False, "Grid": True, "Snap": True,
         "Tooltip": True, "Hands": False, "LuaScript": "", "LuaScriptState": "", "XmlUI": ""}
    o.update(kw)
    return o


BACKS = {1: "arka-ana.png", 2: "arka-npc.png", 3: "arka-karakter.png", 4: "arka-hedef.png"}
# Anahtar 5 = yedek Trigger'lar: ana destenin aynısı (yüz + arka), ayrı anahtar sadece
# betiğin onları RESET'te yedek yığına geri ayırabilmesi için.
CDECK = {k: {"FaceURL": url("yuzler.png"), "BackURL": url(BACKS[1 if k == 5 else k]),
             "NumWidth": COLS, "NumHeight": ROWS, "BackIsHidden": True, "UniqueBack": False, "Type": 0}
         for k in (1, 2, 3, 4, 5)}
BY_ID = {c[0]: c for c in CARDS}
CS = 1.1   # kart ölçeği: ~2.4 x 3.4 masa birimi (1.3 kalabalık görünüyordu)


def card(cid, key=None, tags=()):
    c = BY_ID[cid]
    key = key or c[1]
    return base("Card", tr(0, 0, 180.0, True, CS), c[3], c[4].replace("\n\n", " — "),
                CardID=key * 100 + INDEX[cid], CustomDeck={str(key): CDECK[key]},
                SidewaysCard=False, HideWhenFaceDown=True, Tags=list(tags))


def deck(cards, pos, nick, key):
    return base("Deck", tr(*pos, 180.0, True, CS, y=1.3), nick,
                DeckIDs=[c["CardID"] for c in cards], CustomDeck={str(key): CDECK[key]},
                ContainedObjects=cards, SidewaysCard=False, HideWhenFaceDown=True)


def tile(fn, transform, nick, locked=True, circle=False, thick=0.1, **kw):
    # Stretch=False: karo resmin en/boy oranını korur.
    return base("Custom_Tile", transform, nick, Locked=locked,
                CustomImage={"ImageURL": url(fn), "ImageSecondaryURL": "", "ImageScalar": 1.0,
                             "WidthScale": 0.0,
                             "CustomTile": {"Type": 2 if circle else 0, "Thickness": thick,
                                            "Stackable": False, "Stretch": False}}, **kw)


def token(name, x=0.0, z=0.0, y=1.5):
    return tile(TOKENS[name][0], tr(x, z, 180.0, s=0.55, y=y), name, locked=False, circle=True, thick=0.2)


# ------------------------------------------------------------------ yerleşim
# Table_RPG (SHOWDOWN'da ölçüldü: eller z=±21, x=±31). 5 koltuk: altta 2, sağda 1, üstte 1, solda 1.
# rot: koltuğun bakış açısı (0 = alttan masaya bakıyor). Kartlar oyuncuya dönük: rot + 180.
SEATS = [
    ("White", -11.0, -21.0, 0.0), ("Red", 11.0, -21.0, 0.0), ("Yellow", 31.0, 0.0, 270.0),
    ("Green", 0.0, 21.0, 180.0), ("Blue", -31.0, 0.0, 90.0),
]


def local(seat, u, v):
    """Koltuğa göre koordinat: u = oyuncunun sağı, v = masanın ortasına doğru."""
    _, hx, hz, rot = seat
    a = math.radians(rot)
    fx, fz = math.sin(a), math.cos(a)
    rx, rz = fz, -fx
    return round(hx + u * rx + v * fx, 2), round(hz + u * rz + v * fz, 2)


# Oyuncu alanı (u, v). Alttaki iki koltuk 22 birim aralıklı; alan u=-8.5..6.5 → çakışmıyor.
A_CHAR = (-5.5, 7.5)                          # karakter kartı (açık)
A_PANEL = (-1.2, 7.2)                         # skor paneli
A_KEEP = [(2.6, 7.5), (5.3, 7.5)]             # tutulan kartlar: DOUBLE, SAFE PASS, Smuggled
A_PLAY = [(-4.8 + k * 2.6, 11.0) for k in range(5)]   # DRAW / NPC kartları buraya açılır
A_TOKEN = (-8.2, 7.5)                         # durum fişleri (CASH OUT buraya koyar)
A_ABILITY = (-8.2, 10.2)                      # yetenek kullanıldı fişi
A_OBJ = (-5.5, 4.2)                           # hedef sayacı

# Orta (x, z). Alt/üst koltukların oyun sırası z=±7.2'ye, yan koltuklarınki x=±17.7'ye
# kadar geliyor; orta bunların içinde.
MAIN_POS, DISC_POS, RES_POS = (-9.5, 3.0), (-6.0, 3.0), (-13.0, 3.0)
NPC_POS, NPCD_POS = (6.0, 3.0), (9.5, 3.0)
CHAR_POS, OBJ_POS = (9.5, -2.5), (13.0, -2.5)
TRACK = (0.0, 3.2)
ROUND_STEPS = [(-2.55 + k * 1.7, 3.2) for k in range(4)]
RULES_POS = (0.0, -2.6)
BAGS = {"CASHED OUT": (-13.0, -1.6), "ENFORCED": (-10.6, -1.6), "LOAN DEBT": (-8.2, -1.6),
        "BODYGUARD": (-5.8, -1.6)}
FIRST_POS = (-13.0, -4.6)

objs, snaps = [], []
snap = lambda p, rot=None: snaps.append(
    {"Position": {"x": p[0], "y": 1.0, "z": p[1]},
     **({"Rotation": {"x": 0.0, "y": rot, "z": 0.0}} if rot is not None else {})})

PANEL_LUA = r'''
-- Skor paneli (GDD §13.4): büyük rakam + butonlar, 0'ın altına inmez.
-- Global betik setScore / getScore'u çağırır (NEW ROUND sıfırlar).
score = 0
STEPS = {-20, -10, -5, 5, 10, 20}

function onLoad(state)
  if state and state ~= "" then score = tonumber(state) or 0 end
  draw()
end

function onSave() return tostring(score) end

function setScore(p)
  score = math.max(0, math.floor(tonumber(p.value) or 0))
  draw()
end

function getScore() return score end

function noop() end

function draw()
  self.clearButtons()
  self.createButton({click_function = "noop", function_owner = self, label = tostring(score),
    position = {0, 0.11, -0.12}, width = 0, height = 0, font_size = 520,
    font_color = {0.83, 0.69, 0.29}})
  for i, d in ipairs(STEPS) do
    local name = "step" .. i
    _G[name] = function(obj, color) setScore({value = score + d}) end
    self.createButton({click_function = name, function_owner = self,
      label = (d > 0 and "+" or "") .. d, position = {-0.78 + (i - 1) * 0.31, 0.11, 0.55},
      width = 190, height = 150, font_size = 90,
      color = d > 0 and {0.16, 0.45, 0.27} or {0.6, 0.2, 0.15}, font_color = {1, 1, 1}})
  end
  self.createButton({click_function = "zero", function_owner = self, label = "0",
    position = {0.85, 0.11, -0.55}, width = 170, height = 170,
    font_size = 110, color = {0.1, 0.1, 0.1}, font_color = {1, 1, 1}, tooltip = "CRASH"})
end

function zero() setScore({value = 0}) end
'''

lua_seats = []
for seat in SEATS:
    color, hx, hz, rot = seat
    cr = rot + 180.0
    objs.append(base("HandTrigger", {"posX": hx, "posY": 4.8, "posZ": hz, "rotX": 0.0, "rotY": rot,
                                     "rotZ": 0.0, "scaleX": 11.8, "scaleY": 9.2, "scaleZ": 4.9},
                     FogColor=color, Locked=True))
    px, pz = local(seat, *A_PANEL)
    objs.append(tile("panel.png", tr(px, pz, cr, s=2.2, y=1.05), f"{color} score",
                     LuaScript=PANEL_LUA, LuaScriptState="0", Tags=["score"], GMNotes=color))
    ox, oz = local(seat, *A_OBJ)
    objs.append(base("Counter", tr(ox, oz, cr, y=1.1), f"{color} objective",
                     "Private objective progress", Counter={"value": 0}, Tags=["objective"]))
    objs.append(token("ABILITY USED", *local(seat, *A_ABILITY)))
    snap(local(seat, *A_CHAR), cr)
    for p in A_KEEP:
        snap(local(seat, *p), cr)
    play = [local(seat, *p) for p in A_PLAY]
    for p in play:
        snap(p, cr)
    snap(local(seat, *A_TOKEN))
    lua_seats.append("{color=%r, rot=%.0f, char={%s}, token={%s}, play={%s}, first={%s}}" % (
        color, cr, "%.2f,%.2f" % local(seat, *A_CHAR), "%.2f,%.2f" % local(seat, *A_TOKEN),
        ",".join("{%.2f,%.2f}" % p for p in play), "%.2f,%.2f" % local(seat, -8.2, 4.8)))

# Desteler
main = [card(c[0]) for c in CARDS if c[1] == 1 for _ in range(c[6])]
reserve = [card("T-NPC", key=5, tags=("reserve",)) for _ in range(RESERVE_N)]
objs += [deck(main, MAIN_POS, "Main Deck", 1), deck(reserve, RES_POS, "Reserve NPC Triggers", 5),
         deck([card(c[0]) for c in CARDS if c[1] == 2], NPC_POS, "NPC Deck", 2),
         deck([card(c[0]) for c in CARDS if c[1] == 3], CHAR_POS, "Characters", 3),
         deck([card(c[0]) for c in CARDS if c[1] == 4], OBJ_POS, "Secret Objectives", 4)]
for p in (MAIN_POS, DISC_POS, RES_POS, NPC_POS, NPCD_POS, CHAR_POS, OBJ_POS):
    snap(p, 180.0)

objs.append(tile("tur.png", tr(*TRACK, 180.0, s=3.5, y=1.05), "Round tracker"))
objs.append(token("ROUND", *ROUND_STEPS[0], y=1.3))
objs.append(tile("kural.png", tr(*RULES_POS, 180.0, s=3.3, y=1.05), "Turn flow"))
objs.append(token("FIRST PLAYER", *FIRST_POS))
# Sonsuz torba: elle fiş almak için. Butonlar fişleri torbasız kendisi üretir.
for name, (x, z) in BAGS.items():
    objs.append(base("Infinite_Bag", tr(x, z, 180.0, s=0.8, y=1.3), name, Locked=True,
                     ContainedObjects=[token(name)], ColorDiffuse={"r": 0.25, "g": 0.2, "b": 0.15}))
for name, (x, z) in BAGS.items():
    snaps.append({"Position": {"x": x, "y": 1.0, "z": z}})

TOKEN_DATA = {n: token(n) for n in ("CASHED OUT",)}

LUA = r"""
-- THE LIMIT prototip tuşları (GDD §13.6). Elle oynamak için hiçbiri şart değil.
--   START      karakter (açık) + gizli hedef (ele) dağıtır, desteleri karıştırır, 1. tur.
--   DRAW       basan oyuncunun önüne ana desteden bir kart açar (PUSH da budur).
--   NPC        basanın önüne NPC kartı açar.
--   DISCARD    oyun sıralarındaki açık kartları ıskartalara atar (ana / NPC ayrı).
--   CASH OUT   basanın önüne CASHED OUT fişi koyar, skorunu duyurur.
--   NEW ROUND  her şeyi toplar, 2. turdan itibaren 2 yedek Trigger ekler, karıştırır,
--              skorları ve durum fişlerini sıfırlar (GDD §4.1, A3).
--   RESET      oyunu en başa alır.
SEATS = {__SEATS__}
MAIN_POS, DISC_POS, RES_POS = {__MAIN__}, {__DISC__}, {__RES__}
NPC_POS, NPCD_POS, CHAR_POS, OBJ_POS = {__NPC__}, {__NPCD__}, {__CHAR__}, {__OBJ__}
ROUND_STEPS = {__STEPS__}
FIRST_POS = {__FIRST__}
CASH_TOKEN = JSON.decode([==[__CASH__]==])
STATUS = {["CASHED OUT"] = true, ["ENFORCED"] = true, ["LOAN DEBT"] = true, ["BODYGUARD"] = true}
round = 0

function onSave() return JSON.encode({round = round}) end
function onLoad(s)
  if s and s ~= "" then local d = JSON.decode(s) round = d.round or 0 end
end

local function near(p, q, r) return (p.x - q[1])^2 + (p.z - q[2])^2 < r * r end

-- CustomDeck anahtarı: 1 ana, 2 NPC, 3 karakter, 4 hedef, 5 yedek Trigger.
local function kind(o)
  local d = o.getData()
  local id = d.CardID or (d.DeckIDs and d.DeckIDs[1])
  return id and math.floor(id / 100) or nil
end

local function pileAt(pos)
  for _, o in ipairs(getObjects()) do
    if (o.type == "Deck" or o.type == "Card") and not o.held_by_color and near(o.getPosition(), pos, 1.4) then
      return o
    end
  end
end

local function seatOf(player)
  for _, s in ipairs(SEATS) do if s.color == player.color then return s end end
  broadcastToColor("Sit at a colored seat first.", player.color, {1, 0.5, 0.5})
end

-- Masada oturan renkler; 3'ten azsa (tek başına test) beş koltuğun hepsi.
local function activeSeats()
  local seated, out = {}, {}
  for _, c in ipairs(getSeatedPlayers()) do seated[c] = true end
  for _, s in ipairs(SEATS) do if seated[s.color] then table.insert(out, s) end end
  if #out < 3 then return SEATS end
  return out
end

local function panel(color)
  for _, o in ipairs(getObjectsWithTag("score")) do
    if o.getGMNotes() == color then return o end
  end
end

local function setAllScores(v)
  for _, o in ipairs(getObjectsWithTag("score")) do o.call("setScore", {value = v}) end
end

-- Bir yığına (deste/kart) başka kartları putObject ile anında ekler. Taban yoksa ilk kart taban olur.
local function gather(keys, pos, faceUp, skip)
  local base = pileAt(pos)
  if base and not keys[kind(base)] then base = nil end
  for _, o in ipairs(getObjects()) do
    if (o.type == "Card" or o.type == "Deck") and o ~= base and o ~= skip and keys[kind(o)] then
      if not base then
        base = o
        base.setPosition({pos[1], 1.5, pos[2]})
        base.setRotation({0, 180, faceUp and 0 or 180})
      else
        base = base.putObject(o) or base
      end
    end
  end
  return base
end

local function shuffleAt(pos)
  local d = pileAt(pos)
  if d then d.setRotation({0, 180, 180}) if d.type == "Deck" then d.shuffle() end end
end

local function clearTokens()
  for _, o in ipairs(getObjects()) do
    if STATUS[o.getName()] and o.type ~= "Infinite" and o.type ~= "Bag" then o.destruct() end
  end
end

local function moveRoundMarker()
  for _, o in ipairs(getObjects()) do
    if o.getName() == "ROUND" then
      local p = ROUND_STEPS[math.max(1, math.min(round, 4))]
      o.setPositionSmooth({p[1], 1.4, p[2]}, false, true)
    end
  end
end

-- Oyuncunun oyun sırasında ilk boş yer.
local function freePlaySpot(s)
  for _, q in ipairs(s.play) do
    local busy = false
    for _, o in ipairs(getObjects()) do
      if (o.type == "Card" or o.type == "Deck") and near(o.getPosition(), q, 1.2) then busy = true end
    end
    if not busy then return q end
  end
  return s.play[#s.play]
end

local function reveal(player, pos, discPos, label)
  local s = seatOf(player)
  if not s then return end
  local d = pileAt(pos)
  if not d and discPos then
    -- NPC destesi bitince ıskartası karıştırılıp yeni deste olur (GDD §7).
    d = pileAt(discPos)
    if d then d.setPosition({pos[1], 1.5, pos[2]}) d.setRotation({0, 180, 180}) if d.type == "Deck" then d.shuffle() end end
  end
  if not d then
    broadcastToAll(label .. " is empty." .. (discPos and "" or " The round ends (GDD 4.2)."), {1, 0.5, 0.3})
    return
  end
  local q = freePlaySpot(s)
  local target = {q[1], 2, q[2]}
  if d.type == "Deck" then
    d.takeObject({position = target, rotation = {0, s.rot, 0}, smooth = true})
  else
    d.setPositionSmooth(target, false, true)
    d.setRotationSmooth({0, s.rot, 0}, false, true)
  end
end

function drawMain(player) reveal(player, MAIN_POS, nil, "Main Deck") end
function drawNPC(player) reveal(player, NPC_POS, NPCD_POS, "NPC Deck") end

function discardPlay(player)
  local n = 0
  for _, o in ipairs(getObjects()) do
    -- Sadece ana (1, 5) ve NPC (2) kartları: karakter / hedef kartı sıraya düşse bile atılmaz.
    local k = o.type == "Card" and kind(o)
    if k and (k == 1 or k == 2 or k == 5) and not o.is_face_down then
      for _, s in ipairs(SEATS) do
        for _, q in ipairs(s.play) do
          if o and near(o.getPosition(), q, 1.6) then
            local pos = (k == 2) and NPCD_POS or DISC_POS
            local pile = pileAt(pos)
            if pile then pile.putObject(o) else
              o.setPosition({pos[1], 1.5, pos[2]}) o.setRotation({0, 180, 0})
            end
            n = n + 1
            o = nil
          end
        end
      end
    end
  end
  if n == 0 then broadcastToAll("Nothing face up in the play rows.", {1, 1, 1}) end
end

function cashOut(player)
  local s = seatOf(player)
  if not s then return end
  local data = JSON.decode(JSON.encode(CASH_TOKEN))
  data.Transform.posX, data.Transform.posY, data.Transform.posZ = s.token[1], 2, s.token[2]
  spawnObjectData({data = data})
  local p = panel(s.color)
  local v = p and p.call("getScore") or "?"
  broadcastToAll((player.steam_name or s.color) .. " (" .. s.color .. ") CASHES OUT with " .. tostring(v) .. ".", {0.5, 1, 0.6})
end

-- Bütün ana + yedek kartları ana desteye, NPC'leri NPC destesine toplar (GDD §4.1 adım 2).
local function collectRound()
  gather({[1] = true, [5] = true}, MAIN_POS, false, pileAt(RES_POS))
  gather({[2] = true}, NPC_POS, false)
end

function newRound(player)
  if round == 0 then broadcastToAll("Press START first.", {1, 0.5, 0.5}) return end
  if round >= 4 then broadcastToAll("Round 4 is the last possible round.", {1, 0.5, 0.5}) return end
  round = round + 1
  collectRound()
  -- 2. turdan itibaren her tur 2 yedek Trigger (6 / 8 / 10 / 12).
  local res = pileAt(RES_POS)
  Wait.time(function()
    local m = pileAt(MAIN_POS)
    for i = 1, 2 do
      res = pileAt(RES_POS)
      if res and m then
        if res.type == "Deck" then m.putObject(res.takeObject({position = {MAIN_POS[1], 3, MAIN_POS[2]}, smooth = false}))
        else m.putObject(res) end
      end
    end
    Wait.time(function() shuffleAt(MAIN_POS) shuffleAt(NPC_POS) end, 0.5)
  end, 0.5)
  setAllScores(0)
  clearTokens()
  moveRoundMarker()
  broadcastToAll("ROUND " .. round .. ": scores reset, " .. (4 + round * 2) .. " NPC Triggers in the Main Deck.", {1, 0.85, 0.3})
end

function resetGame(player)
  gather({[1] = true, [5] = true}, MAIN_POS, false)
  gather({[2] = true}, NPC_POS, false)
  gather({[3] = true}, CHAR_POS, false)
  gather({[4] = true}, OBJ_POS, false)
  -- Yedek Trigger'ları (anahtar 5) ana desteden geri ayır.
  Wait.time(function()
    local m = pileAt(MAIN_POS)
    if m and m.type == "Deck" then
      local n = 0
      for _, c in ipairs(m.getObjects()) do
        for _, t in ipairs(c.tags or {}) do
          if t == "reserve" then
            n = n + 1
            m.takeObject({guid = c.guid, position = {RES_POS[1], 1.5 + n * 0.3, RES_POS[2]},
                          rotation = {0, 180, 180}, smooth = false})
          end
        end
      end
    end
    for _, p in ipairs({MAIN_POS, NPC_POS, CHAR_POS, OBJ_POS}) do shuffleAt(p) end
  end, 0.5)
  setAllScores(0)
  for _, o in ipairs(getObjectsWithTag("objective")) do o.Counter.setValue(0) end
  clearTokens()
  for _, o in ipairs(getObjects()) do
    if o.getName() == "FIRST PLAYER" then o.setPositionSmooth({FIRST_POS[1], 1.4, FIRST_POS[2]}, false, true) end
  end
  round = 0
  moveRoundMarker()
  broadcastToAll("Game reset. Press START.", {1, 1, 1})
end

function startGame(player)
  if round > 0 then broadcastToAll("Game already started. RESET first.", {1, 0.5, 0.5}) return end
  local seats = activeSeats()
  for _, p in ipairs({MAIN_POS, NPC_POS, CHAR_POS, OBJ_POS}) do shuffleAt(p) end
  Wait.time(function()
    local ch, ob = pileAt(CHAR_POS), pileAt(OBJ_POS)
    for _, s in ipairs(seats) do
      if ch and ch.type == "Deck" then
        ch.takeObject({position = {s.char[1], 2, s.char[2]}, rotation = {0, s.rot, 0}, smooth = true})
      end
      ob = pileAt(OBJ_POS)
      if ob and ob.type == "Deck" then ob.deal(1, s.color)
      elseif ob then ob.deal(1, s.color) end
    end
    local first = seats[math.random(#seats)]
    for _, o in ipairs(getObjects()) do
      if o.getName() == "FIRST PLAYER" then o.setPositionSmooth({first.first[1], 1.4, first.first[2]}, false, true) end
    end
    broadcastToAll("THE LIMIT: " .. #seats .. " players. First player: " .. first.color .. ".", {1, 0.85, 0.3})
  end, 0.6)
  setAllScores(0)
  round = 1
  moveRoundMarker()
end
"""
REPL = {
    "__SEATS__": ",\n  ".join(lua_seats),
    "__MAIN__": "%.1f,%.1f" % MAIN_POS, "__DISC__": "%.1f,%.1f" % DISC_POS, "__RES__": "%.1f,%.1f" % RES_POS,
    "__NPC__": "%.1f,%.1f" % NPC_POS, "__NPCD__": "%.1f,%.1f" % NPCD_POS,
    "__CHAR__": "%.1f,%.1f" % CHAR_POS, "__OBJ__": "%.1f,%.1f" % OBJ_POS,
    "__STEPS__": ",".join("{%.2f,%.2f}" % p for p in ROUND_STEPS),
    "__FIRST__": "%.1f,%.1f" % FIRST_POS, "__CASH__": json.dumps(TOKEN_DATA["CASHED OUT"]),
}
for k, v in REPL.items():
    LUA = LUA.replace(k, v)

# Sol üstte küçük (SHOWDOWN'daki yer): TTS'in üst menüsünü kapatmasın.
BTN = '  <Button onClick="{f}" fontSize="14" color="{c}" textColor="#F5ECD7">{t}</Button>'
XML = ('<VerticalLayout height="282" width="130" rectAlignment="UpperLeft" offsetXY="60 -50" spacing="6">\n'
       + "\n".join(BTN.format(f=f_, c=c_, t=t_) for f_, c_, t_ in [
           ("startGame", "#7A6012", "START"), ("drawMain", "#8B1E14", "DRAW"),
           ("drawNPC", "#3A4652", "NPC"), ("discardPlay", "#3C2819", "DISCARD"),
           ("cashOut", "#1E6E3C", "CASH OUT"), ("newRound", "#3C2819", "NEW ROUND"),
           ("resetGame", "#3C2819", "RESET")])
       + "\n</VerticalLayout>")

now = time.localtime()
save = {
    "SaveName": SAVE_NAME, "EpochTime": int(time.time()),
    "Date": time.strftime("%m/%d/%Y %I:%M:%S %p", now), "VersionNumber": "v14.2.2",
    "GameMode": "THE LIMIT prototype", "Tags": [], "Gravity": 0.5, "PlayArea": 0.5,
    "Table": "Table_RPG", "Sky": "Sky_Regal",
    "Note": "THE LIMIT v0.1 prototype. START deals, DRAW = push, CASH OUT locks your score. Score panels: click the buttons.",
    "Hands": {"Enable": True, "DisableUnused": False, "Hiding": 0},
    "LuaScript": LUA, "LuaScriptState": "", "XmlUI": XML, "SnapPoints": snaps, "ObjectStates": objs,
}
(OUT / f"{SAVE_NAME}.json").write_text(json.dumps(save, indent=1, ensure_ascii=False))
shutil.copy(OUT / f"{SAVE_NAME}.json", SAVES / f"{SAVE_NAME}.json")
print(f"{len(objs)} obje, {len(snaps)} snap → {SAVES / (SAVE_NAME + '.json')}")
