# Junta os quadros gravados em um GIF com moldura de navegador.
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys
W = int(sys.argv[1]) if len(sys.argv) > 1 else 760
fps = 7
qs = sorted(Path("tmp/gif").glob("*.jpg"))[::2]
H = round(W * 720 / 1280)
BAR = 34
base = Image.new("RGB", (W, H + BAR), (6, 7, 11))
d = ImageDraw.Draw(base)
for x, c in [(18, (255, 126, 182)), (36, (255, 190, 92)), (54, (74, 222, 128))]:
    d.ellipse([x - 5, 12, x + 5, 22], fill=c)
d.rounded_rectangle([W // 2 - 130, 7, W // 2 + 130, 27], 10, fill=(18, 22, 33))
f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
d.text((W // 2, 17), "www.luizrenato.dev", font=f, fill=(168, 216, 255), anchor="mm")
quadros = []
for q in qs:
    im = base.copy()
    im.paste(Image.open(q).convert("RGB").resize((W, H), Image.LANCZOS), (0, BAR))
    quadros.append(im)
# uma paleta só para o GIF inteiro
amostra = Image.new("RGB", (W, (H + BAR) * 12))
for i in range(12):
    amostra.paste(quadros[i * len(quadros) // 12], (0, i * (H + BAR)))
pal = amostra.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
saida = [q.quantize(palette=pal, dither=Image.Dither.NONE) for q in quadros]
saida[0].save("assets/site.gif", save_all=True, append_images=saida[1:], duration=1000 // fps, loop=0, optimize=False, disposal=1)
print(Path("assets/site.gif").stat().st_size / 1e6, "MB", len(saida), "quadros")
saida[0].convert("RGB").save("tmp/g0.png")
fol = Image.new("RGB", (4 * 480, 4 * 290), (0, 0, 0))
for i in range(16):
    q = quadros[i * len(quadros) // 16].copy(); q.thumbnail((476, 286))
    fol.paste(q, ((i % 4) * 480, (i // 4) * 290))
fol.save("tmp/folha.jpg", quality=82)
