# Avatar do perfil: recorte do Luiz (suéter azul, headset) sobre fundo ink com aurora azul-bebê. Saída < 1 MB.
import random
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw

RAIZ = Path(__file__).parent
FOTO = RAIZ.parent / "luizrenato-dev" / "public" / "fotos" / "capa-pose-1.webp"
S = 1024
random.seed(3)

fundo = Image.new("RGB", (S, S), (6, 7, 11))


def mancha(cx, cy, r, cor, forca):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=int(255 * forca))
    m = m.filter(ImageFilter.GaussianBlur(r * .55))
    fundo.paste(Image.new("RGB", (S, S), cor), (0, 0), m)


mancha(S * .5, S * .42, 430, (168, 216, 255), .55)   # halo azul-bebê atrás da cabeça
mancha(S * .15, S * .85, 330, (201, 184, 255), .30)  # lilás embaixo à esquerda
mancha(S * .88, S * .25, 300, (255, 190, 92), .16)   # âmbar discreto no canto
# grade fina como nas seções do site
g = ImageDraw.Draw(fundo, "RGBA")
for i in range(0, S, 64):
    g.line((i, 0, i, S), fill=(255, 255, 255, 9))
    g.line((0, i, S, i), fill=(255, 255, 255, 9))
# anel fino de brilho
anel = Image.new("L", (S, S), 0)
ImageDraw.Draw(anel).ellipse((S * .5 - 400, S * .46 - 400, S * .5 + 400, S * .46 + 400), outline=140, width=3)
anel = anel.filter(ImageFilter.GaussianBlur(1.2))
fundo.paste(Image.new("RGB", (S, S), (168, 216, 255)), (0, 0), anel)

p = Image.open(FOTO).convert("RGBA")
# enquadra rosto + ombros: corta a parte de cima e escala para preencher a largura
box_h = int(p.width * 1.0 * 1.0)
esc = 0.98 * S / p.width
p = p.resize((int(p.width * esc), int(p.height * esc)), Image.LANCZOS)
x = (S - p.width) // 2
y = 120
# sombra suave sob o recorte
sombra = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sombra.paste((0, 0, 0, 120), (x, y), p.getchannel("A"))
sombra = sombra.filter(ImageFilter.GaussianBlur(18))
fundo.paste(sombra, (0, 0), sombra)
# luz de contorno azul
alfa = p.getchannel("A")
borda = alfa.filter(ImageFilter.GaussianBlur(5))
luz = Image.new("RGBA", (S, S), (0, 0, 0, 0))
luz.paste((168, 216, 255, 110), (x, y), borda)
fundo.paste(luz, (0, 0), luz)
fundo.paste(p, (x, y), p)

out = RAIZ / "assets" / "avatar-luiz.jpg"
for q in (95, 92, 88, 84, 78):
    fundo.save(out, quality=q, optimize=True, subsampling=0 if q > 85 else 2)
    if out.stat().st_size < 900_000:
        break
print(out, out.stat().st_size // 1024, "KB", q)
