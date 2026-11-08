# Avatar de terror do perfil: o personagem escuro dos vídeos (óculos redondos, barba cheia, cabelo com volume, suéter),
# com olhos vermelhos brilhando, lentes rachadas, sorriso largo com dentes e névoa. Saída: assets/avatar-terror.svg (1024x1024).
import random
from pathlib import Path

RAIZ = Path(__file__).parent
random.seed(13)
S = 1024


def dentes():
    # sorriso largo dentro da barba: curva de cima (y0..) e de baixo; dentes triangulares em zigue-zague
    def topo(x):
        return 270 + 12 * (1 - ((x - 200) / 56) ** 2)

    def base(x):
        return 270 + 40 * (1 - ((x - 200) / 56) ** 2)

    out = ""
    x = 150
    while x < 250:
        w = 8
        out += f'<path d="M{x} {topo(x):.1f} L{x + w / 2} {topo(x + w / 2) + 9:.1f} L{x + w} {topo(x + w):.1f}Z" fill="#e9e1cf"/>'
        out += f'<path d="M{x + 4} {base(x + 4):.1f} L{x + 4 + w / 2} {base(x + 4 + w / 2) - 8:.1f} L{x + 4 + w} {base(x + 4 + w):.1f}Z" fill="#d9cfba"/>'
        x += w
    return out


def brasas():
    out = ""
    for _ in range(46):
        x, y = random.uniform(40, 984), random.uniform(40, 984)
        r = random.choice([1.2, 1.6, 2.2, 3])
        o = random.uniform(.25, .8)
        out += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#ff4a3a" opacity="{o:.2f}"/>'
    return out


def riscos():
    out = ""
    for _ in range(18):
        x, y = random.uniform(0, 1024), random.uniform(0, 1024)
        dx, dy = random.uniform(-90, 90), random.uniform(60, 200)
        out += f'<path d="M{x:.0f} {y:.0f} l{dx / 5:.0f} {dy / 2:.0f} l{dx / 6:.0f} {dy / 2:.0f}" stroke="#ffffff" stroke-opacity="{random.uniform(.03, .08):.2f}" stroke-width="1.2" fill="none"/>'
    return out


PELE, SOMBRA = "#0d0b12", "#08070d"
CAB, CABL = "#040307", "#14101c"

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">
<defs>
  <radialGradient id="halo" cx="50%" cy="42%" r="55%">
    <stop offset="0" stop-color="#b3121f" stop-opacity=".75"/><stop offset=".45" stop-color="#5a0a14" stop-opacity=".45"/><stop offset="1" stop-color="#05030a" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="vinheta" cx="50%" cy="46%" r="75%">
    <stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".92"/>
  </radialGradient>
  <radialGradient id="olho" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="#fff3e8"/><stop offset=".25" stop-color="#ff5a3c"/><stop offset=".7" stop-color="#d4141f"/><stop offset="1" stop-color="#4a0408"/>
  </radialGradient>
  <linearGradient id="nevoa" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8a8fa8" stop-opacity="0"/><stop offset="1" stop-color="#9aa0b8" stop-opacity=".35"/>
  </linearGradient>
  <filter id="rim" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="0" stdDeviation="2.4" flood-color="#ff4a3a" flood-opacity=".9"/>
    <feDropShadow dx="0" dy="0" stdDeviation="14" flood-color="#c1121f" flood-opacity=".55"/>
  </filter>
  <filter id="brilho" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="borra"><feGaussianBlur stdDeviation="28"/></filter>
  <filter id="grao" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="4"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter>
  <filter id="fumaca" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".008 .018" numOctaves="3" seed="9" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="90"/><feGaussianBlur stdDeviation="9"/></filter>
</defs>

<rect width="{S}" height="{S}" fill="#05030a"/>
<rect width="{S}" height="{S}" fill="url(#halo)"/>
<!-- fumaça escura subindo atrás da cabeça -->
<g filter="url(#fumaca)" opacity=".85">
  <path d="M250 760 C170 560 270 380 210 170 C300 300 330 430 300 560Z" fill="#12060a"/>
  <path d="M780 760 C860 560 760 380 820 170 C730 300 700 430 730 560Z" fill="#12060a"/>
  <path d="M470 330 C430 220 520 120 470 20 C560 110 590 230 540 330Z" fill="#0b0408"/>
</g>
{brasas()}

<g transform="translate(102 6) scale(2.05)" filter="url(#rim)">
  <!-- corpo -->
  <path d="M34 566 C34 452 66 398 140 374 C165 366 182 362 200 362 C218 362 235 366 260 374 C334 398 366 452 366 566Z" fill="#07060c"/>
  <path d="M70 430 C90 400 120 386 150 380 C120 400 100 430 92 470Z" fill="#150f1a" opacity=".7"/>
  <path d="M166 318 L234 318 L238 368 C215 382 185 382 162 368Z" fill="{SOMBRA}"/>
  <path d="M148 366 C175 392 225 392 252 366" fill="none" stroke="#04030a" stroke-width="16" stroke-linecap="round"/>
  <!-- orelhas e rosto -->
  <ellipse cx="96" cy="210" rx="17" ry="27" fill="{SOMBRA}"/><ellipse cx="304" cy="210" rx="17" ry="27" fill="{SOMBRA}"/>
  <path d="M96 190 C96 110 140 74 200 74 C260 74 304 110 304 190 C304 262 280 318 200 334 C120 318 96 262 96 190Z" fill="{PELE}"/>
  <path d="M270 120 C295 150 302 190 298 230 C290 210 284 170 270 120Z" fill="#000" opacity=".5"/>
  <!-- olheiras fundas -->
  <ellipse cx="158" cy="206" rx="30" ry="22" fill="#000" opacity=".55"/><ellipse cx="242" cy="206" rx="30" ry="22" fill="#000" opacity=".55"/>
  <!-- cabelo -->
  <path d="M92 190 C84 118 122 66 196 58 C262 52 314 88 312 168 C306 146 296 130 280 120 C262 108 236 104 214 106 C176 108 140 112 118 134 C104 150 98 168 98 196Z" fill="{CAB}"/>
  <path d="M118 128 C136 84 190 62 246 70 C282 76 304 100 310 130 C292 104 262 92 226 94 C186 96 146 106 118 128Z" fill="{CABL}" opacity=".5"/>
  <!-- barba -->
  <path d="M98 212 C100 262 116 302 150 330 C170 348 186 362 200 372 C214 362 230 348 250 330 C284 302 300 262 302 212 C292 236 276 246 262 250 C252 274 232 292 200 292 C168 292 148 274 138 250 C124 246 108 236 98 212Z" fill="{CAB}"/>
  <path d="M120 270 C135 300 160 325 190 340" fill="none" stroke="{CABL}" stroke-width="5" stroke-linecap="round" opacity=".8"/>
  <!-- nariz -->
  <path d="M202 204 C194 226 194 236 200 240 C207 243 214 240 216 235" fill="none" stroke="#1d1623" stroke-width="5" stroke-linecap="round"/>
  <!-- sorriso largo com dentes -->
  <path d="M146 270 Q200 {270 + 80} 254 270 Q200 {270 + 24} 146 270Z" fill="#050104"/>
  <path d="M146 270 Q200 350 254 270" fill="none" stroke="#7a0c14" stroke-width="2" opacity=".8"/>
  {dentes()}
  <!-- bigode -->
  <path d="M134 252 C156 234 188 236 200 246 C212 236 244 234 266 252 C262 262 254 268 246 266 C228 258 214 258 200 260 C186 258 172 258 154 266 C146 268 138 262 134 252Z" fill="{CAB}"/>
  <!-- olhos vermelhos -->
  <g filter="url(#brilho)">
    <ellipse cx="158" cy="196" rx="17" ry="15" fill="url(#olho)"/><ellipse cx="242" cy="196" rx="17" ry="15" fill="url(#olho)"/>
  </g>
  <rect x="156.8" y="182" width="2.8" height="28" rx="1.4" fill="#120204"/><rect x="240.8" y="182" width="2.8" height="28" rx="1.4" fill="#120204"/>
  <!-- sobrancelhas furiosas -->
  <path d="M132 162 Q160 164 188 184" fill="none" stroke="{CAB}" stroke-width="12" stroke-linecap="round"/>
  <path d="M268 162 Q240 164 212 184" fill="none" stroke="{CAB}" stroke-width="12" stroke-linecap="round"/>
  <!-- óculos redondos de aro grosso, lentes rachadas -->
  <circle cx="158" cy="194" r="37" fill="rgba(255,50,50,.10)" stroke="#0a0508" stroke-width="9"/>
  <circle cx="242" cy="194" r="37" fill="rgba(255,50,50,.10)" stroke="#0a0508" stroke-width="9"/>
  <circle cx="158" cy="194" r="41.5" fill="none" stroke="#ff4a3a" stroke-width="1" opacity=".55"/><circle cx="242" cy="194" r="41.5" fill="none" stroke="#ff4a3a" stroke-width="1" opacity=".55"/>
  <path d="M193 186 Q200 178 207 186" fill="none" stroke="#0a0508" stroke-width="8" stroke-linecap="round"/>
  <path d="M121 188 L98 182 M279 188 L302 182" stroke="#0a0508" stroke-width="8" stroke-linecap="round"/>
  <path d="M142 162 L156 190 L146 222 M156 190 L182 182 M156 190 L170 168" fill="none" stroke="#ffd9d0" stroke-width="1.6" opacity=".7"/>
  <path d="M262 164 L246 192 L258 222 M246 192 L222 186 M246 192 L232 232" fill="none" stroke="#ffd9d0" stroke-width="1.6" opacity=".6"/>
  <!-- sangue escorrendo das lentes -->
  <path d="M160 232 C158 252 163 262 160 288" fill="none" stroke="#8b0a12" stroke-width="4.5" stroke-linecap="round"/><circle cx="160" cy="292" r="3.6" fill="#8b0a12"/>
  <path d="M236 232 C238 250 233 270 237 300" fill="none" stroke="#8b0a12" stroke-width="4" stroke-linecap="round"/><circle cx="237" cy="304" r="3.4" fill="#8b0a12"/>
</g>

<!-- névoa na base, vinheta e grão -->
<rect y="640" width="{S}" height="384" fill="url(#nevoa)"/>
<ellipse cx="200" cy="960" rx="360" ry="90" fill="#8a90aa" opacity=".16" filter="url(#borra)"/><ellipse cx="840" cy="990" rx="380" ry="90" fill="#8a90aa" opacity=".16" filter="url(#borra)"/>
{riscos()}
<rect width="{S}" height="{S}" fill="url(#vinheta)"/>
<rect width="{S}" height="{S}" filter="url(#grao)" opacity=".11"/>
</svg>"""

(RAIZ / "assets" / "avatar-terror.svg").write_text(svg, encoding="utf-8")
print("ok", len(svg) // 1024, "KB")
