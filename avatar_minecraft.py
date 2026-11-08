# Avatar do perfil no estilo Minecraft: o Luiz como uma "skin" desenhada quadradinho por quadradinho (grade 32x32).
# Cabeça 8x8 do jogo ampliada 2x (16x16 quadradinhos): cabelo curto com volume, óculos redondos, barba cheia, suéter azul-marinho.
# Saída: assets/avatar-minecraft.png/.jpg (960x960)
import random
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).parent
N, CEL = 32, 30
random.seed(5)

SKIN, SKIN2, SKIN3 = "#c8906c", "#b97f5d", "#d9a481"
HAIR, HAIR2 = "#33210f", "#4a331c"
BEARD, BEARD2 = "#2a1a10", "#3a251a"
LIP, WHITE, IRIS = "#8a5545", "#f4f4f4", "#3b2a1c"
FRAME = "#0b0b10"
NAVY, NAVY2, NAVY3 = "#1d2a4a", "#26375f", "#141d36"
INK, GLOW = (8, 11, 20), (168, 216, 255)

g = [[None] * N for _ in range(N)]


def px(x, y, c):
    if 0 <= x < N and 0 <= y < N:
        g[y][x] = c


def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px(x, y, c)


# ---------- fundo: halo azul-bebê em degraus + faíscas ----------
for y in range(N):
    for x in range(N):
        d = ((x - 15.5) ** 2 + (y - 11) ** 2) ** .5 / 17
        t = round(max(0, 1 - d) * 5) / 5
        k = t * t * .6
        px(x, y, "#%02x%02x%02x" % tuple(int(INK[i] + (GLOW[i] - INK[i]) * k) for i in range(3)))
for x, y in [(3, 3), (28, 5), (2, 14), (29, 12), (6, 1), (25, 2), (1, 8), (30, 18)]:
    px(x, y, "#a8d8ff")

# ---------- corpo: suéter azul-marinho (tronco 16 de largura, braços de 8 em cada lado) ----------
for y in range(20, N):
    for x in range(0, N):
        if 8 <= x <= 23:           # tronco
            c = NAVY2 if (y % 2 == 0) else NAVY
            if x in (8, 23):
                c = NAVY3
        else:                       # braços (mangas)
            c = NAVY3 if x in (0, 7, 24, 31) else (NAVY2 if y % 2 == 0 else NAVY)
        px(x, y, c)
# gola redonda com o pescoço aparecendo
rect(12, 20, 19, 20, SKIN2)
rect(13, 21, 18, 21, SKIN2)
rect(14, 22, 17, 22, SKIN2)
for x, y in [(11, 20), (20, 20), (12, 21), (19, 21), (13, 22), (18, 22)]:
    px(x, y, NAVY3)
rect(14, 23, 17, 23, NAVY3)

# ---------- cabeça (hx, hy de 0 a 15) ----------
HX, HY = 8, 4


def h(hx, hy, c):
    px(HX + hx, HY + hy, c)


# pele de base com leve variação (textura do jogo)
for hy in range(16):
    for hx in range(16):
        h(hx, hy, random.choice([SKIN, SKIN, SKIN, SKIN2, SKIN3]))
# cabelo: topo com volume (3 fileiras), franja irregular e laterais curtas
for hy in range(0, 3):
    for hx in range(16):
        h(hx, hy, random.choice([HAIR, HAIR, HAIR2]))
for hx in (0, 1, 2, 3, 4, 11, 12, 13, 14, 15):
    h(hx, 3, random.choice([HAIR, HAIR, HAIR2]))
for hx in (5, 6, 9, 10):
    h(hx, 3, random.choice([HAIR, HAIR2]))
for hx in (0, 1, 14, 15):
    h(hx, 4, random.choice([HAIR, HAIR2]))
for hy in range(5, 11):
    for hx in (0, 15):
        h(hx, hy, random.choice([HAIR, HAIR2]))
# sobrancelhas grossas
for hx in (2, 3, 4, 5, 6, 9, 10, 11, 12, 13):
    h(hx, 5, HAIR)
# óculos redondos de aro preto
for x0 in (2, 9):
    for hx in range(x0, x0 + 5):
        h(hx, 6, FRAME)
        h(hx, 10, FRAME)
    for hy in range(7, 10):
        h(x0, hy, FRAME)
        h(x0 + 4, hy, FRAME)
for hx in (7, 8):
    h(hx, 7, FRAME)
# olhos: branco do lado de fora, íris perto do nariz (como a skin do Steve)
h(3, 8, WHITE); h(4, 8, IRIS)
h(11, 8, IRIS); h(12, 8, WHITE)
# reflexo nas lentes
h(3, 7, "#9fc3e6"); h(10, 7, "#9fc3e6")
# nariz
h(7, 10, SKIN2); h(8, 10, SKIN2)
h(7, 9, SKIN3); h(8, 9, SKIN3)
# barba cheia + bigode + boca
for hy in range(11, 16):
    for hx in range(0 if hy >= 12 else 1, 16 if hy >= 12 else 15):
        h(hx, hy, random.choice([BEARD, BEARD, BEARD2]))
for hx in range(3, 13):
    h(hx, 11, random.choice([BEARD, BEARD2]))
for hx in (6, 7, 8, 9):
    h(hx, 12, LIP)
for hx in (6, 7, 8, 9):
    h(hx, 13, BEARD2)
# bochechas acima da barba aparecem
for hx in (1, 2, 13, 14):
    h(hx, 10, random.choice([SKIN, SKIN2]))

# ---------- saída ----------
img = Image.new("RGB", (N * CEL, N * CEL))
for y in range(N):
    for x in range(N):
        img.paste(g[y][x], (x * CEL, y * CEL, (x + 1) * CEL, (y + 1) * CEL))
img.save(RAIZ / "assets" / "avatar-minecraft.png")
img.save(RAIZ / "assets" / "avatar-minecraft.jpg", quality=95)
print("ok", img.size)
