# Gera todos os visuais do perfil do GitHub (SVG animado, sem JS e sem fonte externa).
# Identidade igual à do luizrenato.dev: fundo ink, azul bebê, Syne + Inter + JetBrains Mono.
import base64, collections, datetime as dt, io, json, os, random, re, urllib.request
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image

RAIZ = Path(__file__).parent
SITE = RAIZ.parent / "luizrenato-dev" / "public"
OUT = RAIZ / "assets"
OUT.mkdir(exist_ok=True)
random.seed(7)

INK, INK2, LINE, FOG, SNOW = "#06070b", "#0c0f17", "#1c2233", "#8d97ad", "#eef2fa"
BABY, LILAC, AMBER, MINT, PINK = "#a8d8ff", "#c9b8ff", "#ffbe5c", "#4ade80", "#ff7eb6"
EASE = "cubic-bezier(.16,1,.3,1)"


# ---------- texto em curvas ----------
class Fonte:
    def __init__(self, arquivo, **eixos):
        chave = "-".join(f"{k}{v}" for k, v in eixos.items())
        estatica = RAIZ / "fontes" / f"{Path(arquivo).stem}-{chave}.ttf"
        if not estatica.exists():
            f = TTFont(RAIZ / "fontes" / arquivo)
            instancer.instantiateVariableFont(f, eixos, inplace=True)
            f.save(estatica)
        self.tt = TTFont(estatica)
        self.gs = self.tt.getGlyphSet()
        self.ordem = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(str(estatica))))

    def molda(self, s):
        b = hb.Buffer()
        b.add_str(s)
        b.guess_segment_properties()
        hb.shape(self.hb, b, {"kern": True, "liga": False})
        return b.glyph_infos, b.glyph_positions


SYNE = Fonte("Syne.ttf", wght=800)
SYNE7 = Fonte("Syne.ttf", wght=700)
INTER = Fonte("Inter.ttf", wght=400, opsz=14)
INTER6 = Fonte("Inter.ttf", wght=600, opsz=14)
MONO = Fonte("JetBrainsMono.ttf", wght=500)


def largura(s, f, t, ls=0):
    _, pos = f.molda(s)
    return sum(p.x_advance for p in pos) * t / f.upem + ls * len(s)


def curva(s, f, t, x, y, ancora="start", ls=0):
    w = largura(s, f, t, ls)
    x -= {"start": 0, "middle": w / 2, "end": w}[ancora]
    infos, pos = f.molda(s)
    k = t / f.upem
    partes = []
    for i, p in zip(infos, pos):
        pen = SVGPathPen(f.gs, ntos=lambda v: ("%.1f" % v).rstrip("0").rstrip("."))
        f.gs[f.ordem[i.codepoint]].draw(TransformPen(pen, (k, 0, 0, -k, x + p.x_offset * k, y)))
        partes.append(pen.getCommands())
        x += p.x_advance * k + ls
    return "".join(partes)


def T(s, f, t, x, y, fill=SNOW, ancora="start", ls=0, attrs=""):
    return f'<path d="{curva(s, f, t, x, y, ancora, ls)}" fill="{fill}" {attrs}/>'


def quebra(s, f, t, maxw):
    linhas, atual = [], ""
    for p in s.split():
        n = f"{atual} {p}".strip()
        if largura(n, f, t) > maxw and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = n
    return linhas + [atual]


def img64(im, q=72, fmt="WEBP"):
    b = io.BytesIO()
    im.save(b, fmt, quality=q, method=6)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(b.getvalue()).decode()


def svg(nome, w, h, corpo, css="", titulo=""):
    base = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    txt = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{titulo}">'
           f"<title>{titulo}</title><style>{css}{base}</style>{corpo}</svg>")
    (OUT / nome).write_text(txt, encoding="utf-8")
    print(f"{nome:24} {len(txt) / 1024:7.0f} KB")


AURORA_DEFS = "".join(
    f'<radialGradient id="a{i}"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
    for i, (c, o) in enumerate([(BABY, .55), (LILAC, .5), (AMBER, .28), (PINK, .22)]))
AURORA_CSS = """
@keyframes d0{from{transform:translate(-60px,-30px) scale(1)}to{transform:translate(160px,50px) scale(1.25)}}
@keyframes d1{from{transform:translate(80px,40px) scale(1.2)}to{transform:translate(-140px,-40px) scale(.9)}}
@keyframes d2{from{transform:translate(-40px,30px) scale(.9)}to{transform:translate(90px,-50px) scale(1.2)}}
.au{transform-box:fill-box;transform-origin:center;mix-blend-mode:screen}
"""


def aurora(w, h, forca=1.0):
    bl = [(w * .22, h * .3, w * .36, h * .62, 0, "d0", 17), (w * .8, h * .3, w * .34, h * .7, 1, "d1", 21),
          (w * .55, h * .85, w * .3, h * .5, 2, "d2", 15), (w * .1, h * .9, w * .24, h * .45, 3, "d1", 19)]
    return "".join(f'<ellipse class="au" cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="url(#a{g})" opacity="{forca}" style="animation:{k} {d}s ease-in-out infinite alternate"/>'
                   for x, y, rx, ry, g, k, d in bl)


def painel(w, h, rotulo, titulo_linhas, corpo, css="", defs="", alt="", forca=.35):
    """Painel escuro padrão: rótulo mono + título Syne, como as seções do site."""
    y = 92
    t = ""
    for i, ln in enumerate(titulo_linhas):
        t += f'<g class="tt" style="animation-delay:{.1 + i * .08}s">{T(ln, SYNE, 34, 40, y + i * 42)}</g>'
    c = f"""<defs>{AURORA_DEFS}<clipPath id="pc"><rect width="{w}" height="{h}" rx="24"/></clipPath>
    <pattern id="gr" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".03"/></pattern>
    <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{BABY}"/><stop offset=".55" stop-color="{LILAC}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>{defs}</defs>
    <g clip-path="url(#pc)"><rect width="{w}" height="{h}" fill="{INK2}"/>{aurora(w, h, forca)}<rect width="{w}" height="{h}" fill="url(#gr)"/>
    {T(rotulo.upper(), MONO, 12.5, 40, 52, BABY, ls=3.4)}{t}{corpo}</g>
    <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="24" fill="none" stroke="{LINE}"/>
    <rect class="brilho" x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="24" fill="none" stroke="url(#ln)" stroke-width="1.5" pathLength="1000"/>"""
    base = f"""{AURORA_CSS}
    @keyframes sobe{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
    @keyframes volta{{to{{stroke-dashoffset:-1000}}}}
    .tt{{animation:sobe .8s {EASE} both}}
    .brilho{{stroke-dasharray:60 940;animation:volta 9s linear infinite}}
    """
    svg(f"{alt[0]}.svg", w, h, c, base + css, alt[1])


# ---------- 1. capa ----------
def capa():
    W, H = 1000, 560
    foto = Image.open(SITE / "fotos/professor.webp").convert("RGBA")
    fh = 760
    foto = foto.resize((int(foto.width * fh / foto.height), fh), Image.LANCZOS)
    # some embaixo, atrás da faixa (sem corte seco)
    a = foto.getchannel("A")
    fade = Image.new("L", foto.size, 255)
    px = fade.load()
    lat = int(foto.width * .075)
    for y in range(fh):
        vy = 1 if y < fh * .84 else 1 - (y - fh * .84) / (fh * .16)
        for x in range(foto.width):
            vx = min(1, x / lat, (foto.width - 1 - x) / lat)
            px[x, y] = int(255 * vy * (vx * vx * (3 - 2 * vx)))
    from PIL import ImageChops
    foto.putalpha(ImageChops.multiply(a, fade))
    ph = 500
    pw = ph * foto.width / foto.height
    px0, py0 = (W - pw) / 2, 74

    t_luiz = 700 / largura("LUIZ", SYNE, 1)
    t_ren = 948 / largura("RENATO", SYNE, 1)
    d_ren = curva("RENATO", SYNE, t_ren, 500, 302, "middle")

    # papéis com o efeito de embaralhar do site
    papeis = ["Engenheiro de Software", "Analista de Dados", "Especialista em IA", "Desenvolvedor Full Stack", "Automação de Processos"]
    tam = min(25, 288 / max(largura(p, SYNE7, 1) for p in papeis))
    lixo = "abcdefgxyz0123456789*?+=#/"
    Q, PASSO, FICA = 7, .07, 2.1
    ciclo = len(papeis) * (Q * PASSO + FICA)
    frames, t0, css = "", 0.0, ""
    for p in papeis:
        for k in range(Q):
            n = int(len(p) * k / Q)
            s = p[:n] + "".join(c if c == " " else random.choice(lixo) for c in p[n:])
            frames += f'<path class="fr" d="{curva(s, SYNE7, tam, 36, 456)}" fill="{BABY}" style="animation-delay:{t0 - ciclo:.2f}s"/>'
            t0 += PASSO
        frames += f'<path class="fi" d="{curva(p, SYNE7, tam, 36, 456)}" fill="{BABY}" style="animation-delay:{t0 - ciclo:.2f}s"/>'
        t0 += FICA
    pf, pi = PASSO / ciclo * 100, FICA / ciclo * 100

    itens = ["Software", "Dados", "IA", "Automação", "BI", "Full Stack", "Analytics", "Agentes", "Next.js", "Power BI"]
    x, faixa = 0.0, ""
    for it in itens:
        faixa += T(it.upper(), SYNE, 21, x, 30, INK)
        x += largura(it.upper(), SYNE, 21) + 20
        faixa += f'<circle cx="{x:.0f}" cy="23" r="4" fill="{INK}"/>'
        x += 24
    unidade = x

    faiscas = "".join(
        f'<circle class="fa" cx="{random.randint(20, 980)}" cy="{random.randint(90, 500)}" r="{random.choice([1, 1.2, 1.6])}" fill="{random.choice([BABY, LILAC, AMBER, SNOW])}" style="animation-delay:-{random.uniform(0, 7):.1f}s;animation-duration:{random.uniform(5, 9):.1f}s"/>'
        for _ in range(26))

    corpo = f"""<defs>{AURORA_DEFS}
    <clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    <clipPath id="c1"><rect x="0" y="70" width="{W}" height="134"/></clipPath>
    <clipPath id="c2"><rect x="0" y="208" width="{W}" height="102"/></clipPath>
    <pattern id="g" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M50 0H0V50" fill="none" stroke="#fff" stroke-opacity=".05"/></pattern>
    <radialGradient id="gm"><stop offset=".2" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
    <mask id="m"><rect width="{W}" height="{H}" fill="url(#gm)"/></mask>
    <linearGradient id="fim" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}"/></linearGradient>
    </defs>
    <g clip-path="url(#c)">
    <rect width="{W}" height="{H}" fill="{INK}"/>{aurora(W, H, .75)}
    <rect width="{W}" height="{H}" fill="url(#g)" mask="url(#m)"/>{faiscas}
    {T("LUIZRENATO", SYNE, 15, 36, 40, SNOW)}{T(".DEV", MONO, 12, 36 + largura("LUIZRENATO", SYNE, 15) + 3, 40, FOG, ls=1)}
    {T("ENGENHARIA · DADOS · IA", MONO, 11.5, 964, 40, FOG, "end", 3)}
    <g class="ent" style="animation-delay:.1s">{T("DISPONÍVEL PARA NOVOS DESAFIOS", MONO, 10.5, 500, 58, FOG, "middle", 4)}</g>
    <g clip-path="url(#c1)"><g class="rev" style="animation-delay:.15s">{T("LUIZ", SYNE, t_luiz, 500, 198, SNOW, "middle")}</g></g>
    <g clip-path="url(#c2)"><g class="rev" style="animation-delay:.28s">
      <path d="{d_ren}" fill="none" stroke="{SNOW}" stroke-opacity=".38" stroke-width="1.1"/>
      <path class="corre" d="{d_ren}" fill="none" stroke="{BABY}" stroke-width="1.8" pathLength="1000"/>
    </g></g>
    <g class="foto"><g class="flut"><image href="{img64(foto, 80)}" x="{px0:.1f}" y="{py0}" width="{pw:.1f}" height="{ph}"/></g></g>
    <rect y="{H - 170}" width="{W}" height="170" fill="url(#fim)" opacity=".8"/>
    <g class="ent" style="animation-delay:.7s">{T("HOJE EU SOU", MONO, 11, 36, 426, FOG, ls=3.2)}{frames}
    {T("Catanduva, SP · CLT ou PJ · disponível para mudança", INTER, 12.5, 36, 482, "#aab4c8")}</g>
    <g class="ent" style="animation-delay:.85s">
      <rect x="770" y="424" width="194" height="50" rx="25" fill="{INK}" fill-opacity=".6" stroke="#fff" stroke-opacity=".28"/>
      {T("Vamos conversar →", SYNE7, 15.5, 867, 454, SNOW, "middle")}
      <circle cx="790" cy="400" r="4" fill="{MINT}"/><circle class="ping" cx="790" cy="400" r="4" fill="{MINT}"/>
      {T("ABERTO A PROPOSTAS", MONO, 10.5, 804, 404, MINT, ls=2.4)}
    </g>
    <g transform="rotate(-1.5 500 520)">
      <rect x="-30" y="504" width="1060" height="44" fill="{BABY}"/>
      <g transform="translate(0 503)"><g class="corrida">{"".join(f'<g transform="translate({i * unidade:.1f} 0)">{faixa}</g>' for i in range(3))}</g></g>
    </g>
    </g>
    <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="{LINE}"/>"""
    css = f"""{AURORA_CSS}
    @keyframes rev{{from{{transform:translateY(135px)}}to{{transform:none}}}}
    @keyframes ent{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
    @keyframes foto{{from{{opacity:0;transform:translateY(46px)}}to{{opacity:1;transform:none}}}}
    @keyframes flut{{from{{transform:translateY(-3px)}}to{{transform:translateY(5px)}}}}
    @keyframes run{{to{{stroke-dashoffset:-1000}}}}
    @keyframes corrida{{to{{transform:translateX(-{unidade:.1f}px)}}}}
    @keyframes ping{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3.4);opacity:0}}}}
    @keyframes tw{{0%,100%{{opacity:0}}50%{{opacity:.9}}}}
    @keyframes fr{{0%{{opacity:1}}{pf:.3f}%{{opacity:0}}100%{{opacity:0}}}}
    @keyframes fi{{0%{{opacity:1}}{pi:.3f}%{{opacity:0}}100%{{opacity:0}}}}
    .rev{{animation:rev 1.1s {EASE} both}}.ent{{animation:ent .9s {EASE} both}}
    .foto{{animation:foto 1.2s {EASE} .3s both}}.flut{{animation:flut 5s ease-in-out infinite alternate}}
    .corre{{stroke-dasharray:70 930;animation:run 11s linear infinite}}
    .corrida{{animation:corrida 22s linear infinite}}
    .ping{{transform-box:fill-box;transform-origin:center;animation:ping 1.8s ease-out infinite}}
    .fa{{opacity:0;animation:tw 6s ease-in-out infinite}}
    .fr,.fi{{opacity:0;animation-duration:{ciclo:.2f}s;animation-timing-function:step-end;animation-iteration-count:infinite}}
    .fr{{animation-name:fr}}.fi{{animation-name:fi}}
    @media (prefers-reduced-motion:reduce){{.fi{{opacity:1}}.fi~.fi{{opacity:0}}}}
    """
    svg("capa.svg", W, H, corpo, css, "Luiz Renato Carvalho, Engenheiro de Software e IA em Catanduva-SP")


# ---------- 2. sobre ----------
def contador(valor, x, y, t, cor, atraso, uid):
    """Números que rolam até o valor real."""
    s = str(valor)
    corpo, defs = "", ""
    cx = x
    for i, ch in enumerate(s):
        cw = largura(ch, SYNE, t) + 3
        alvo = int(ch) + 10
        tira = "".join(f'<path d="{curva(str(n % 10), SYNE, t, cx + cw / 2, y + n * t * 1.2, "middle")}" fill="{cor}"/>' for n in range(alvo + 1))
        defs += f'<clipPath id="{uid}{i}"><rect x="{cx - 2:.1f}" y="{y - t * 1.02:.1f}" width="{cw + 4:.1f}" height="{t * 1.18:.1f}"/></clipPath>'
        corpo += f'<g clip-path="url(#{uid}{i})"><g class="rola" style="--y:-{alvo * t * 1.2:.1f}px;animation-delay:{atraso + i * .12:.2f}s">{tira}</g></g>'
        cx += cw
    return corpo, defs, cx


def sobre(n_repos, n_commits):
    W, H = 1000, 378
    dados = [(9, "anos", "construindo sistemas de verdade", BABY), (n_repos, "", "repositórios no GitHub", LILAC),
             (n_commits, "", "commits em 2026", AMBER), (16, "", "projetos no portfólio", MINT)]
    corpo, defs = "", ""
    largura_c = (W - 80 - 3 * 16) / 4
    for i, (v, suf, txt, cor) in enumerate(dados):
        x = 40 + i * (largura_c + 16)
        y = 196
        c, d, fim = contador(v, x + 20, y + 66, 46, cor, .4 + i * .15, f"n{i}")
        defs += d
        extra = T(suf, SYNE7, 17, fim + 6, y + 66, cor) if suf else ""
        linhas = "".join(T(l, INTER, 13.5, x + 20, y + 96 + j * 19, "#aab4c8") for j, l in enumerate(quebra(txt, INTER, 13.5, largura_c - 36)))
        corpo += f'<g class="cd" style="animation-delay:{.25 + i * .12}s"><rect x="{x:.1f}" y="{y}" width="{largura_c:.1f}" height="146" rx="18" fill="{INK}" fill-opacity=".62" stroke="{LINE}"/><rect class="traco" x="{x + 20:.1f}" y="{y}" width="46" height="2.5" fill="{cor}"/>{c}{extra}{linhas}</g>'
    css = f"""@keyframes rola{{from{{transform:translateY(0)}}to{{transform:translateY(var(--y))}}}}
    .rola{{animation:rola 2.2s {EASE} both}}.cd{{animation:sobe .9s {EASE} both}}"""
    painel(W, H, "01 · Sobre", ["Da planilha que ninguém aguenta", "mais ao sistema no ar."], corpo, css, defs, ("sobre", f"9 anos construindo sistemas, {n_repos} repositórios, {n_commits} commits em 2026, 16 projetos no portfólio"))


# ---------- 3. trajetória ----------
def trajetoria():
    W, H = 1000, 520
    x0, x1, a0, a1 = 330, 960, 2017, 2027
    pos = lambda ano, mes: x0 + (ano + (mes - 1) / 12 - a0) / (a1 - a0) * (x1 - x0)
    linhas = [("Carvalho Labs", "Fundador · Engenheiro de Software e IA", (2017, 11), (2026, 11), "nov/2017 – atual", BABY, True),
              ("Colombo Agroindústria", "Analista de Dados e Analytics", (2023, 3), (2026, 11), "mar/2023 – atual", MINT, True),
              ("Pixter", "Desenvolvedor Full Stack", (2022, 1), (2023, 2), "jan/2022 – fev/2023", AMBER, False),
              ("Nubank", "Analista de Tecnologia · Software & BI", (2019, 8), (2021, 1), "ago/2019 – jan/2021", LILAC, False)]
    corpo = ""
    for a in range(a0, a1 + 1):
        x = pos(a, 1)
        corpo += f'<line x1="{x:.1f}" x2="{x:.1f}" y1="150" y2="412" stroke="#fff" stroke-opacity=".06"/>'
        if a < a1:
            corpo += T(str(a), MONO, 11, x + 4, 146, FOG)
    for i, (emp, cargo, ini, fim, per, cor, atual) in enumerate(linhas):
        y = 166 + i * 62
        d = .3 + i * .22
        bx, bw = pos(*ini), pos(*fim) - pos(*ini)
        rot = T(per, MONO, 11, bx + 12, y + 28, INK, attrs='class="rot"') if bw > 170 else T(per, MONO, 11, (bx + bw + 10) if bx + bw + 150 < W else bx - 10, y + 28, cor, "start" if bx + bw + 150 < W else "end")
        ponto = f'<circle cx="{bx + bw:.1f}" cy="{y + 24}" r="5" fill="{cor}"/><circle class="ping" cx="{bx + bw:.1f}" cy="{y + 24}" r="5" fill="{cor}"/>' if atual else ""
        corpo += f"""<g class="ln" style="animation-delay:{d}s">{T(emp, SYNE7, 17.5, 40, y + 19, SNOW)}{T(cargo, INTER, 12.2, 40, y + 38, "#aab4c8")}</g>
        <rect class="bar" x="{bx:.1f}" y="{y + 12}" width="{bw:.1f}" height="24" rx="12" fill="{cor}" style="animation-delay:{d + .1}s"/>
        <g class="ln" style="animation-delay:{d + .8}s">{rot}{ponto}</g>"""
    corpo += f'<line x1="40" x2="960" y1="424" y2="424" stroke="{LINE}"/>'
    corpo += T("FORMAÇÃO", MONO, 11, 40, 452, BABY, ls=3)
    x = 40
    for j, txt in enumerate(["Pós-graduação em Ciência de Dados e IA · Uninter", "Ciência da Computação · UNIP"]):
        w = largura(txt, INTER6, 13) + 34
        corpo += f'<g class="ln" style="animation-delay:{1.4 + j * .15}s"><rect x="{x:.1f}" y="466" width="{w:.1f}" height="34" rx="17" fill="{INK}" fill-opacity=".6" stroke="{LINE}"/>{T(txt, INTER6, 13, x + 17, 488, SNOW)}</g>'
        x += w + 12
    css = f"""@keyframes cresce{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
    @keyframes ping{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3.2);opacity:0}}}}
    .bar{{transform-box:fill-box;transform-origin:left;animation:cresce 1.3s {EASE} both}}
    .ln{{animation:sobe .8s {EASE} both}}
    .ping{{transform-box:fill-box;transform-origin:center;animation:ping 1.9s ease-out infinite}}"""
    painel(W, H, "02 · Experiência", ["De onde vem o que eu sei fazer."], corpo, css, "", ("trajetoria", "Carvalho Labs desde 2017, Colombo Agroindústria desde 2023, Pixter de 2022 a 2023 e Nubank de 2019 a 2021"))


# ---------- 4. o que eu faço ----------
def servicos():
    W, H = 1000, 462
    itens = [("Sistemas sob medida", "CRM, RH, chamados, agenda, contratos: o processo da empresa vira sistema, do jeito que o time trabalha.", BABY),
             ("Dados e BI", "Painéis, indicadores e relatórios que se montam sozinhos. Informação espalhada vira decisão.", LILAC),
             ("Agentes de IA", "IA que atende no WhatsApp, responde com os dados da empresa e passa para o humano na hora certa.", MINT),
             ("Automação", "Integrações e fluxos que eliminam retrabalho: planilha, e-mail, ERP e WhatsApp conversando entre si.", AMBER),
             ("Sites e apps", "Sites rápidos, e-commerce com Pix e aplicativos, com SEO e foco em conversão.", PINK),
             ("Ensino", "Cursos, palestras e treinamentos de IA e programação para times e iniciantes.", BABY)]
    cw, ch = (W - 80 - 32) / 3, 152
    corpo = ""
    for i, (t, txt, cor) in enumerate(itens):
        x, y = 40 + (i % 3) * (cw + 16), 128 + (i // 3) * (ch + 14)
        ls = "".join(T(l, INTER, 13.2, x + 20, y + 84 + j * 19.5, "#aab4c8") for j, l in enumerate(quebra(txt, INTER, 13.2, cw - 40)))
        corpo += f"""<g class="cd" style="animation-delay:{.15 + i * .1}s"><rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="18" fill="{INK}" fill-opacity=".62" stroke="{LINE}"/>
        <rect class="luz" x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="18" fill="none" stroke="{cor}" stroke-width="1.4" pathLength="1000" style="animation-delay:{i * 1.1}s"/>
        {T(f"0{i + 1}", MONO, 12, x + 20, y + 32, cor, ls=2)}{T(t, SYNE7, 19, x + 20, y + 60, SNOW)}{ls}</g>"""
    css = f"""@keyframes contorna{{0%{{stroke-dashoffset:1000;opacity:1}}16%{{stroke-dashoffset:0;opacity:1}}24%,100%{{stroke-dashoffset:0;opacity:0}}}}
    .cd{{animation:sobe .9s {EASE} both}}.luz{{stroke-dasharray:1000;opacity:0;animation:contorna 6.6s ease-in-out infinite}}"""
    painel(W, H, "03 · O que eu faço", ["Problema real, resolvido."], corpo, css, "", ("servicos", "Sistemas sob medida, dados e BI, agentes de IA, automação, sites e apps, ensino"))


# ---------- 5. projetos ----------
def projeto(nome, titulo, categoria, texto, telas, cor):
    W, H = 500, 430
    iw, ih = 500, 312.5
    n = len(telas)
    fica = 3.6
    ciclo = n * fica
    pc = 100 / n
    imgs = ""
    for i, t in enumerate(telas):
        im = Image.open(SITE / t).convert("RGB")
        im = im.resize((820, int(820 * im.height / im.width)), Image.LANCZOS)
        # cada tela inteira, sem cortar
        h = iw * im.height / im.width
        imgs += f'<g class="tl" style="animation-delay:{i * fica - ciclo:.1f}s"><image href="{img64(im, 62)}" x="0" y="36" width="{iw}" height="{h:.1f}"/></g>'
    pontos = "".join(f'<rect x="{W - 20 - (n - i) * 30}" y="16" width="24" height="4" rx="2" fill="#fff" fill-opacity=".14"/><rect class="pg" x="{W - 20 - (n - i) * 30}" y="16" width="24" height="4" rx="2" fill="{cor}" style="animation-delay:{i * fica - ciclo:.1f}s"/>' for i in range(n))
    corpo = f"""<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="20"/></clipPath></defs>
    <g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{INK2}"/>
    <rect width="{W}" height="36" fill="{INK}"/>
    <circle cx="20" cy="18" r="5" fill="{PINK}"/><circle cx="37" cy="18" r="5" fill="{AMBER}"/><circle cx="54" cy="18" r="5" fill="{MINT}"/>
    {T(categoria.upper(), MONO, 10.5, 74, 22, FOG, ls=2.4)}{pontos}{imgs}
    <rect y="348.5" width="{W}" height="82" fill="{INK2}"/><rect y="348.5" width="{W}" height="1" fill="{LINE}"/>
    {T(titulo, SYNE7, 20, 20, 378, SNOW)}{T(texto, INTER, 14, 20, 404, "#aab4c8")}</g>
    <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" stroke="{LINE}"/>"""
    k = pc * .9
    css = f"""@keyframes tl{{0%{{opacity:0;transform:translateX(26px)}}3%{{opacity:1;transform:none}}{pc:.1f}%{{opacity:1;transform:none}}{pc + 3:.1f}%{{opacity:0;transform:translateX(-26px)}}100%{{opacity:0}}}}
    @keyframes pg{{0%{{transform:scaleX(0)}}{pc:.1f}%{{transform:scaleX(1);opacity:1}}{pc + .1:.1f}%,100%{{opacity:0}}}}
    .tl{{opacity:0;animation:tl {ciclo}s ease-in-out infinite}}
    .pg{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:pg {ciclo}s linear infinite}}
    @media (prefers-reduced-motion:reduce){{.tl:first-of-type{{opacity:1}}}}"""
    svg(f"{nome}.svg", W, H, corpo, css, f"{titulo}: {texto}")


def titulo_projetos():
    painel(1000, 136, "04 · Projetos", ["Projetos que eu desenhei e construí."], "", "", "", ("projetos", "Projetos que eu desenhei e construí"))


# ---------- 6. stack ----------
def stack():
    W, H = 1000, 480
    ids = "ts,js,react,nextjs,nodejs,php,laravel,vue,tailwind,python,postgres,prisma,vercel,git,github".split(",")
    pasta = RAIZ / "tmp/icones"
    pasta.mkdir(parents=True, exist_ok=True)
    corpo = ""
    tam, gap = 50, (W - 80 - 15 * 50) / 14
    for i, n in enumerate(ids):
        f = pasta / f"{n}.svg"
        if not f.exists():
            req = urllib.request.Request(f"https://skillicons.dev/icons?i={n}&theme=dark", headers={"User-Agent": "gerador-perfil"})
            f.write_bytes(urllib.request.urlopen(req).read())
        d = "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()
        x = 40 + i * (tam + gap)
        corpo += f'<g class="ic" style="animation-delay:{.2 + i * .06:.2f}s"><g class="on" style="animation-delay:{-i * .28:.2f}s"><image href="{d}" x="{x:.1f}" y="130" width="{tam}" height="{tam}"/></g></g>'
    grupos = [("Desenvolvimento", ["TypeScript", "JavaScript", "React", "Next.js", "Node.js", "PHP", "Laravel", "Vue.js", "Tailwind CSS"], BABY, 1),
              ("Dados & BI", ["Power BI", "DAX", "SQL", "Python", "PostgreSQL", "Prisma", "Excel avançado", "VBA", "Analytics"], LILAC, -1),
              ("IA & Automação", ["Agentes de IA", "LLMs (Claude, GPT)", "WhatsApp Business API", "Automação de processos", "Integrações e APIs", "Instagram/Meta API"], MINT, 1),
              ("Low-code & ERP", ["AppSheet", "Power Apps", "TOTVS", "Datasul", "Fluig", "PIMS"], AMBER, -1)]
    css = ""
    for g, (nome, itens, cor, sent) in enumerate(grupos):
        y = 206 + g * 64
        x, tira = 0.0, ""
        for it in itens:
            w = largura(it, INTER6, 14) + 32
            tira += f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="38" rx="19" fill="{INK}" fill-opacity=".7" stroke="{cor}" stroke-opacity=".38"/>{T(it, INTER6, 14, x + 16, 24.5, SNOW)}'
            x += w + 10
        rep = int(760 / x) + 2
        tiras = "".join(f'<g transform="translate({i * x:.1f} 0)">{tira}</g>' for i in range(rep))
        css += f"@keyframes m{g}{{from{{transform:translateX({0 if sent > 0 else -x:.1f}px)}}to{{transform:translateX({-x if sent > 0 else 0:.1f}px)}}}}.m{g}{{animation:m{g} {x / 26:.0f}s linear infinite}}"
        corpo += f'{T(nome.upper(), MONO, 10.5, 40, y + 23, cor, ls=1.6)}<g clip-path="url(#k)" transform="translate(0 {y})"><g transform="translate(190 0)"><g class="m{g}">{tiras}</g></g></g>'
    defs = f'<clipPath id="k"><rect x="190" y="-2" width="770" height="44"/></clipPath>'
    css += f"""@keyframes pop{{from{{opacity:0;transform:scale(.4)}}to{{opacity:1;transform:none}}}}
    @keyframes onda{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
    .ic{{transform-box:fill-box;transform-origin:center;animation:pop .7s {EASE} both}}.on{{animation:onda 4.2s ease-in-out infinite}}"""
    painel(W, H, "05 · Stack", ["Ferramentas do dia a dia."], corpo, css, defs, ("stack", "TypeScript, React, Next.js, Node.js, PHP, Laravel, Vue, Tailwind, Python, PostgreSQL, Prisma, Vercel, Git, Power BI, SQL, agentes de IA e automação"), forca=.25)


# ---------- 7. commits ----------
def commits():
    W, H = 1000, 400
    tz = dt.timedelta(hours=-3)
    datas = []
    for l in (RAIZ / "dados/commits.txt").read_text().split():
        d = (dt.datetime.fromisoformat(l.replace("Z", "+00:00")) + tz).date()
        if d.year == 2026:
            datas.append(d)
    cont = collections.Counter(datas)
    total = len(datas)
    ini = dt.date(2026, 1, 1)
    ini -= dt.timedelta(days=(ini.weekday() + 1) % 7)
    fim = dt.date(2026, 11, 6)
    c, g = 13.4, 3
    x0, y0 = 40, 176
    corpo = ""
    d = ini
    semana = 0
    meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV"]
    visto = set()
    while d <= fim:
        for dia in range(7):
            q = d + dt.timedelta(days=dia)
            if q > fim or q.year != 2026:
                continue
            n = cont.get(q, 0)
            x, y = x0 + semana * (c + g), y0 + dia * (c + g)
            if q.day <= 7 and q.month not in visto and dia == 0:
                visto.add(q.month)
                corpo += T(meses[q.month - 1], MONO, 10.5, x, y0 - 10, FOG, ls=1)
            nivel = 0 if n == 0 else 1 if n <= 2 else 2 if n <= 6 else 3 if n <= 14 else 4
            cor = ["#1a2131", "#2b4a66", "#4f86b3", "#7fb8e6", BABY][nivel]
            atraso = .2 + semana * .035 + dia * .012
            corpo += f'<rect class="q" x="{x:.1f}" y="{y:.1f}" width="{c}" height="{c}" rx="3" fill="{cor}" style="animation-delay:{atraso:.2f}s"/>'
            if nivel >= 3:
                corpo += f'<rect class="b" x="{x:.1f}" y="{y:.1f}" width="{c}" height="{c}" rx="3" fill="#fff" style="animation-delay:{2.5 + semana * .09:.2f}s"/>'
        d += dt.timedelta(days=7)
        semana += 1
    largura_g = semana * (c + g)
    # varredura de luz em cima do calendário
    corpo += f'<rect class="sc" x="{x0}" y="{y0 - 4}" width="44" height="{7 * (c + g) + 6}" fill="url(#sv)"/>'
    # legenda
    corpo += T("menos", INTER, 11.5, x0, y0 + 7 * (c + g) + 26, FOG)
    for i, cor in enumerate(["#1a2131", "#2b4a66", "#4f86b3", "#7fb8e6", BABY]):
        corpo += f'<rect x="{x0 + 44 + i * 17}" y="{y0 + 7 * (c + g) + 15}" width="13" height="13" rx="3" fill="{cor}"/>'
    corpo += T("mais", INTER, 11.5, x0 + 44 + 5 * 17 + 4, y0 + 7 * (c + g) + 26, FOG)
    corpo += T("Commits reais em repositórios privados, de jan a nov/2026.", INTER, 12, x0 + largura_g - 3, y0 + 7 * (c + g) + 26, FOG, "end")
    # números à direita
    dias_ativos = len(cont)
    melhor = max(cont.values())
    mes_top = collections.Counter(q.month for q in datas).most_common(1)[0]
    sx = 800
    stats = [(str(total), "commits em 2026", BABY), (str(dias_ativos), "dias com commit", LILAC), (str(melhor), "commits no melhor dia", AMBER)]
    for i, (v, t, cor) in enumerate(stats):
        y = 150 + i * 72
        corpo += f'<g class="cd" style="animation-delay:{.4 + i * .15}s">{T(v, SYNE, 36, sx, y + 30, cor)}{T(t, INTER, 12.5, sx, y + 50, "#aab4c8")}</g>'
    defs = f'<linearGradient id="sv" x1="0" x2="1"><stop offset="0" stop-color="{BABY}" stop-opacity="0"/><stop offset=".85" stop-color="{BABY}" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity=".6"/></linearGradient>'
    css = f"""@keyframes q{{from{{opacity:0;transform:scale(.2)}}to{{opacity:1;transform:none}}}}
    @keyframes bl{{0%{{opacity:0}}3%{{opacity:.75}}12%,100%{{opacity:0}}}}
    @keyframes sc{{0%{{transform:translateX(-50px);opacity:0}}5%{{opacity:1}}95%{{opacity:1}}100%{{transform:translateX({largura_g:.0f}px);opacity:0}}}}
    .q{{transform-box:fill-box;transform-origin:center;animation:q .5s {EASE} both}}
    .b{{opacity:0;animation:bl 8s linear infinite}}.sc{{opacity:0;animation:sc 8s linear 2.5s infinite}}
    .cd{{animation:sobe .9s {EASE} both}}"""
    painel(W, H, "06 · Ritmo", [f"{total} commits em 2026."], corpo, css, defs, ("commits", f"{total} commits em 2026 em {dias_ativos} dias"), forca=.22)
    print("commits", total, "dias", dias_ativos, "melhor", melhor, "mes", mes_top)
    return total


# ---------- 8. contato ----------
def contato():
    W, H = 1000, 300
    corpo = f"""<g class="tt">{T("Vamos construir", SYNE, 46, 500, 110, SNOW, "middle")}</g>
    <g class="tt" style="animation-delay:.1s"><path d="{curva("algo juntos?", SYNE, 46, 500, 166, "middle")}" fill="none" stroke="{BABY}" stroke-width="1.3"/></g>
    <g class="tt" style="animation-delay:.25s">{T("Busco um time onde eu possa somar com engenharia, dados e IA.", INTER, 16, 500, 214, "#c5cede", "middle")}</g>
    <g class="tt" style="animation-delay:.35s">{T("CLT · PJ · REMOTO · HÍBRIDO · PRESENCIAL", MONO, 12, 500, 252, BABY, "middle", 3)}</g>"""
    c = f"""<defs>{AURORA_DEFS}<clipPath id="pc"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{BABY}"/><stop offset=".55" stop-color="{LILAC}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient></defs>
    <g clip-path="url(#pc)"><rect width="{W}" height="{H}" fill="{INK}"/>{aurora(W, H, .7)}{corpo}</g>
    <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="{LINE}"/>
    <rect class="brilho" x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="url(#ln)" stroke-width="1.5" pathLength="1000"/>"""
    css = f"""{AURORA_CSS}@keyframes sobe{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}@keyframes volta{{to{{stroke-dashoffset:-1000}}}}
    .tt{{animation:sobe .9s {EASE} both}}.brilho{{stroke-dasharray:60 940;animation:volta 9s linear infinite}}"""
    svg("contato.svg", W, H, c, css, "Vamos construir algo juntos? CLT, PJ, remoto, híbrido ou presencial")


def botao(nome, texto, cor, cheio=False):
    t = 15
    w = largura(texto, INTER6, t) + 56
    H = 50
    fundo = cor if cheio else INK2
    txt = INK if cheio else SNOW
    corpo = f"""<defs><clipPath id="c"><rect width="{w:.0f}" height="{H}" rx="25"/></clipPath>
    <linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity="{.5 if cheio else .16}"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
    <g clip-path="url(#c)"><rect width="{w:.0f}" height="{H}" fill="{fundo}"/><rect class="sh" x="-90" y="-10" width="80" height="70" fill="url(#s)"/></g>
    <rect x=".75" y=".75" width="{w - 1.5:.0f}" height="{H - 1.5}" rx="24.25" fill="none" stroke="{cor}" stroke-opacity="{1 if cheio else .55}" stroke-width="1.5"/>
    <circle cx="24" cy="25" r="4" fill="{txt if cheio else cor}"/>{T(texto, INTER6, t, 38, 30.5, txt)}"""
    css = f"@keyframes sh{{0%{{transform:translateX(0) skewX(-18deg)}}35%,100%{{transform:translateX({w + 180:.0f}px) skewX(-18deg)}}}}.sh{{animation:sh 4.5s ease-in-out infinite}}"
    svg(f"btn-{nome}.svg", int(w), H, corpo, css, texto)


if __name__ == "__main__":
    n_repos = sum(1 for l in (RAIZ / "dados/linguagens.jsonl").read_text().splitlines() if l.strip())
    capa()
    total = commits()
    sobre(n_repos, total)
    trajetoria()
    servicos()
    titulo_projetos()
    projeto("proj-agentes", "Agentes de IA", "IA · WhatsApp", "Atendem, fecham pedido, agendam e chamam o humano.", ["galeria-lp/ag-dashboard.webp", "galeria-lp/ag-inbox.webp", "galeria-lp/ag-fluxo.webp"], MINT)
    projeto("proj-sistemas", "Sistemas sob medida", "CRM · Agenda · BI", "O processo da empresa vira sistema, do jeito do time.", ["galeria-lp/ad-dashboard-escuro.webp", "portfolio/crm-desktop.webp", "portfolio/admin-desktop.webp"], BABY)
    projeto("proj-sites", "Sites e e-commerce", "Next.js · SEO", "Rápidos, com identidade própria para cada negócio.", ["galeria-lp/site-restaurante.webp", "galeria-lp/site-barbearia.webp", "galeria-lp/site-odonto.webp"], AMBER)
    projeto("proj-dados", "Automação e dados", "Fluxos · Relatórios", "Retrabalho rodando sozinho e indicador para decidir.", ["portfolio/fluxo-desktop.webp", "galeria-lp/ag-relatorio.webp", "galeria-lp/ad-salao-financeiro.webp"], LILAC)
    stack()
    contato()
    botao("site", "luizrenato.dev", BABY, True)
    botao("linkedin", "LinkedIn", BABY)
    botao("curriculo", "Currículo em PDF", LILAC)
    botao("whatsapp", "WhatsApp", MINT)
    botao("email", "E-mail", AMBER)
    botao("instagram", "Instagram", PINK)
