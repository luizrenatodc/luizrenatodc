# Avatar do perfil em pixel art: o recorte do Luiz (foto de camisa listrada) reduzido a uma grade de quadradinhos,
# paleta pequena, contorno escuro de 1 pixel e fundo com halo azul-bebê em degraus. Saída: assets/avatar-pixel.png/.jpg
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

RAIZ = Path(__file__).parent
FOTO = RAIZ.parent / "luizrenato-dev" / "public" / "fotos" / "professor-v2.webp"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 72  # quadradinhos por lado
CELULA = 960 // N                                   # pixels de cada quadradinho na imagem final
CORES = int(sys.argv[2]) if len(sys.argv) > 2 else 22

# 1) recorte quadrado com o rosto centralizado (cabelo inteiro, ombros embaixo)
foto = Image.open(FOTO).convert("RGBA")
lado, cx, cy = 840, 410, 330
box = (cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2)
quadro = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
quadro.paste(foto.crop((box[0], max(0, box[1]), box[2], box[3])), (0, max(0, -box[1])))
quadro = ImageEnhance.Color(quadro).enhance(1.25)
quadro = ImageEnhance.Contrast(quadro).enhance(1.3)
quadro = ImageEnhance.Sharpness(quadro).enhance(2.2)

# 2) reduz para a grade (média de cor por quadradinho) e fecha o alfa em tudo-ou-nada
RGB = Image.new("RGB", (lado, lado), (0, 0, 0))
RGB.paste(quadro, (0, 0), quadro)
a = quadro.split()[3]
rgb_pequeno = RGB.resize((N, N), Image.BOX)
a_pequeno = a.resize((N, N), Image.BOX).point(lambda v: 255 if v > 110 else 0)

# 3) fundo: ink com halo azul-bebê em degraus (bandas) atrás da cabeça
fundo = Image.new("RGB", (N, N))
fd = fundo.load()
ink, glow = (8, 11, 20), (168, 216, 255)
for y in range(N):
    for x in range(N):
        d = ((x - N * .5) ** 2 + (y - N * .42) ** 2) ** .5 / (N * .56)
        t = max(0.0, 1 - d)
        t = round(t * 5) / 5            # 5 degraus
        k = t * t * .55
        fd[x, y] = tuple(int(ink[i] + (glow[i] - ink[i]) * k) for i in range(3))
# faíscas de pixel
for (x, y) in [(8, 12), (84, 18), (12, 76), (88, 66), (5, 44), (91, 40), (24, 5), (72, 8)]:
    if x < N and y < N:
        fd[x, y] = (168, 216, 255)

# 4) contorno de 1 pixel em volta do personagem
mp = a_pequeno.load()
contorno = (6, 9, 18)
saida = fundo.copy()
so = saida.load()
rp = rgb_pequeno.load()
for y in range(N):
    for x in range(N):
        if mp[x, y]:
            so[x, y] = rp[x, y]
        else:
            viz = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(0 <= u < N and 0 <= v < N and mp[u, v] for u, v in viz):
                so[x, y] = contorno

# 5) paleta curta (visual de pixel art) e amplia sem suavizar
saida = saida.quantize(colors=CORES, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
final = saida.resize((N * CELULA, N * CELULA), Image.NEAREST)
final.save(RAIZ / "assets" / "avatar-pixel.png")
final.save(RAIZ / "assets" / "avatar-pixel.jpg", quality=95)
print("ok", N, "x", N, "quadradinhos,", final.size)
