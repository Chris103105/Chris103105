"""
Generador del perfil futurista / hacker para GitHub.

Crea 3 SVG animados que GitHub sí puede mostrar (no ejecuta React ni JS):
  header.svg   -> fondo de letras glitch + tu nombre estilo "TechText"
                  (un marco salta letra por letra y la vuelve contorno)
                  + subtítulo tipo pantalla de aeropuerto (split-flap)
  profile.svg  -> terminal neofetch con tu foto convertida en mosaico glitch
  logos.svg    -> carrusel infinito de logos de tus tecnologías

Requisitos (el workflow los instala solo):
  pip install pillow fonttools brotli
  npm i simple-icons @fontsource/space-grotesk

Edita solo la sección CONFIG.
"""

import datetime as dt
import json
import os
import random
import urllib.request
from io import BytesIO
from xml.sax.saxutils import escape

# ============================ CONFIG ============================
USUARIO = "Chris103105"
NOMBRE = "CHRISTOPHER JOVEL"
ROLES = ["BIENVENIDO", "CHRIS103105", "HOLA MUNDO"]

INFO = [
    ("Nombre", "Christopher Steven Jovel Beltran"),
    ("GitHub", "github.com/Chris103105"),
]

CONTACTO = [
    ("Email", "christopherjovel7@gmail.com"),
    ("LinkedIn", "christopher-jovel-307213364"),
]

# Logos del carrusel (slug de simpleicons.org, texto)
TECNOLOGIAS = [
    ("git", "Git"), ("github", "GitHub"), ("gmail", "Gmail"),
    ("markdown", "Markdown"), ("gnubash", "Terminal"),
]
# ================================================================

FUENTE_NOMBRE = "node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2"
ICONOS = "node_modules/simple-icons/icons"

# Paleta azul suave
BG = "#0B1A30"
BAR = "#10233F"
BORDE = "#1E3A5F"
SOFT = "#93C5FD"
KEY = "#7DD3FC"
VAL = "#BAE6FD"
DOTS = "#2E4A70"
TITULO = "#E0F2FE"
ACENTO = "#38BDF8"
GLITCH = ["#E0F2FE", "#38BDF8", "#7DD3FC", "#60A5FA"]
MONO = "Consolas, 'DejaVu Sans Mono', 'Courier New', monospace"
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$&*()-_+=/[]{};:<>.,"

rnd = random.Random(USUARIO)


# ----------------------------------------------------------------- utilidades
def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def kt(xs):
    """keyTimes válidos (no decrecientes, entre 0 y 1)."""
    out, prev = [], 0.0
    for x in xs:
        x = min(1.0, max(prev, x))
        out.append(x)
        prev = x
    return ";".join(f"{x:.4f}" for x in out)


def anim_ventana(a, b, dur, on="1", off="0", attr="opacity", fade=0.012):
    """Valor `on` durante [a, b] del ciclo, `off` el resto."""
    a, b = max(0.0, a), min(1.0, b)
    if a <= 0:
        vals, keys = [on, on, off, off], [0, b - fade, b, 1]
    elif b >= 1:
        vals, keys = [off, off, on, on], [0, a, a + fade, 1]
    else:
        vals, keys = [off, off, on, on, off, off], [0, a, a + fade, b - fade, b, 1]
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" keyTimes="{kt(keys)}" '
            f'dur="{f(dur)}s" repeatCount="indefinite"/>')


def anim_discreto(s, e, dur):
    """Visible solo entre s y e (fracciones del ciclo), sin transición."""
    if s <= 0 and e >= 1:
        return ""
    if s <= 0:
        return f'<animate attributeName="opacity" calcMode="discrete" values="1;0" keyTimes="0;{e:.4f}" dur="{f(dur)}s" repeatCount="indefinite"/>'
    if e >= 1:
        return f'<animate attributeName="opacity" calcMode="discrete" values="0;1" keyTimes="0;{s:.4f}" dur="{f(dur)}s" repeatCount="indefinite"/>'
    return f'<animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{s:.4f};{e:.4f}" dur="{f(dur)}s" repeatCount="indefinite"/>'


def chispa(x, y, size=12, colors=GLITCH):
    """Un carácter que parpadea de color (efecto LetterGlitch)."""
    dur = rnd.uniform(2.5, 7)
    t = rnd.uniform(0.05, 0.85)
    h = rnd.uniform(0.04, 0.12)
    c = rnd.choice(colors)
    chars = "".join(rnd.choice(CHARSET) for _ in range(4))
    vals = ";".join(escape(ch) for ch in chars)
    return (f'<text x="{f(x)}" y="{f(y)}" fill="{c}" font-size="{size}" opacity="0">{escape(chars[0])}'
            f'<animate attributeName="opacity" values="0;0;1;.9;0;0" keyTimes="{kt([0, t, t + .01, t + h, t + h + .08, 1])}" dur="{f(dur)}s" repeatCount="indefinite"/>'
            f'</text>')


# ----------------------------------------------------------------- datos de GitHub
def gh_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "perfil-glitch"})
    token = os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def obtener_stats():
    s = {"repos": "—", "stars": "—", "commits": "—", "followers": "—"}
    try:
        u = gh_get(f"https://api.github.com/users/{USUARIO}")
        s["repos"], s["followers"] = u["public_repos"], u["followers"]
        stars, page = 0, 1
        while True:
            repos = gh_get(f"https://api.github.com/users/{USUARIO}/repos?per_page=100&page={page}")
            if not repos:
                break
            stars += sum(r.get("stargazers_count", 0) for r in repos)
            page += 1
        s["stars"] = stars
        c = gh_get(f"https://api.github.com/search/commits?q=author:{USUARIO}")
        s["commits"] = f"{c['total_count']:,}"
    except Exception as e:
        print("Aviso: no se pudieron leer estadísticas ->", e)
    return s


# ----------------------------------------------------------------- foto
def silueta():
    from PIL import Image, ImageDraw, ImageFilter
    im = Image.new("L", (400, 440), 0)
    d = ImageDraw.Draw(im)
    d.ellipse((10, 300, 390, 640), fill=150)
    d.polygon([(200, 250), (150, 330), (250, 330)], fill=40)
    d.ellipse((85, 30, 315, 330), fill=200)
    d.ellipse((120, 85, 280, 300), fill=25)
    d.ellipse((140, 105, 260, 275), fill=120)
    d.rounded_rectangle((136, 160, 196, 198), 10, fill=250)
    d.rounded_rectangle((204, 160, 264, 198), 10, fill=250)
    d.rectangle((194, 172, 206, 178), fill=250)
    d.line((178, 235, 222, 235), fill=60, width=5)
    d.rectangle((160, 370, 240, 420), fill=70)
    return im.filter(ImageFilter.GaussianBlur(1.5))


def cargar_foto():
    from PIL import Image
    for nombre in ("foto.png", "foto.jpg", "foto.jpeg"):
        if os.path.exists(nombre):
            return Image.open(nombre)
    try:
        req = urllib.request.Request(f"https://github.com/{USUARIO}.png?size=460",
                                     headers={"User-Agent": "perfil-glitch"})
        return Image.open(BytesIO(urllib.request.urlopen(req, timeout=20).read()))
    except Exception as e:
        print("Sin foto ni avatar, uso la silueta de respaldo ->", e)
        return silueta()


def brillo_foto(cols, rows, cw, ch):
    from PIL import ImageEnhance, ImageOps
    img = ImageOps.exif_transpose(cargar_foto()).convert("L")
    objetivo = (cols * cw) / (rows * ch)
    w, h = img.size
    if w / h > objetivo:
        nw = int(h * objetivo)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / objetivo)
        img = img.crop((0, 0, w, nh))          # recorte desde arriba: prioriza la cara
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageEnhance.Contrast(img).enhance(1.35).resize((cols, rows))
    px = img.load()
    return [[px[x, y] / 255 for x in range(cols)] for y in range(rows)]


# ----------------------------------------------------------------- fuente → paths
def letras_como_paths(texto, size, ancho_max):
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    font = TTFont(FUENTE_NOMBRE)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    os2 = font["OS/2"]
    hmtx = font["hmtx"]
    tracking = -0.02 * upm

    def total(sz):
        w = 0
        for c in texto:
            g = cmap.get(ord(c))
            w += (hmtx[g][0] if g else upm * 0.3) + tracking
        return (w - tracking) * sz / upm

    while total(size) > ancho_max and size > 30:
        size -= 2
    s = size / upm
    x = 0.0
    letras = []
    for c in texto:
        g = cmap.get(ord(c))
        if not g:
            x += upm * 0.3 * s
            continue
        if c.strip():
            pen = SVGPathPen(gs)
            gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
            bp = BoundsPen(gs)
            gs[g].draw(bp)
            if bp.bounds:
                x1, y1, x2, y2 = bp.bounds
                letras.append({"c": c, "d": pen.getCommands(),
                               "box": (x + x1 * s, -y2 * s, x + x2 * s, -y1 * s)})
        x += (hmtx[g][0] + tracking) * s
    return letras, x - tracking * s, {
        "cap": os2.sCapHeight * s, "xh": os2.sxHeight * s,
        "desc": abs(os2.sTypoDescender) * s,
    }


# ----------------------------------------------------------------- fondo glitch
def capa_glitch(w, h, cw, ch, fs):
    cols, rows = int(w / cw) + 1, int(h / ch) + 1
    filas = []
    for r in range(rows):
        linea = "".join(rnd.choice(CHARSET) if rnd.random() < 0.9 else " " for _ in range(cols))
        filas.append(f'<text x="0" y="{f(r * ch + ch * 0.8)}" textLength="{f(cols * cw)}" '
                     f'lengthAdjust="spacing" xml:space="preserve">{escape(linea)}</text>')
    filas = "\n".join(filas)
    chispas = "\n".join(chispa(rnd.randrange(cols) * cw, rnd.randrange(rows) * ch + ch * 0.8, fs)
                        for _ in range(int(cols * rows * 0.035)))
    return filas, chispas


# ================================================================= HEADER
def construir_header():
    W, H = 1000, 320
    cw, ch, fs = 9.0, 17.0, 13
    filas, chispas = capa_glitch(W, H, cw, ch, fs)

    letras, ancho, met = letras_como_paths(NOMBRE.upper(), 104, 740)
    ox = (W - ancho) / 2
    base = 158
    N = len(letras)
    out = []

    # --- fondo, letras glitch y oleadas de luz
    out.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    out.append(f'<g font-family="{MONO}" font-size="{fs}" fill="{VAL}" opacity=".10">{filas}</g>')
    out.append(f'<g font-family="{MONO}" font-size="{fs}" fill="{KEY}" opacity=".55" mask="url(#flow)">{filas}</g>')
    out.append(f'<g font-family="{MONO}">{chispas}</g>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#centro)"/>')

    # --- guías tipográficas (baseline, x-height, cap height)
    gx1, gx2 = ox - 40, ox + ancho + 40
    guias = [(base, "baseline"), (base - met["xh"], "x-height"), (base - met["cap"], "cap height")]
    for y, lab in guias:
        out.append(f'<line x1="{f(gx1)}" x2="{f(gx2)}" y1="{f(y)}" y2="{f(y)}" stroke="{KEY}" stroke-opacity=".18" stroke-dasharray="2 4"/>')
        out.append(f'<rect x="{f(gx1 - 1.5)}" y="{f(y - 1.5)}" width="3" height="3" fill="{KEY}" opacity=".5"/>')
        out.append(f'<text x="{f(gx2 + 8)}" y="{f(y + 3)}" font-family="{MONO}" font-size="10" fill="{KEY}" opacity=".45">{lab}</text>')

    # --- nombre (TechText): cada letra relleno + contorno punteado
    dur = max(6.0, N * 1.15)
    g = 0.22 / dur  # tiempo de deslizamiento del marco
    out.append(f'<g transform="translate({f(ox)} {base})">')
    for i, L in enumerate(letras):
        a, b = i / N, (i + 1) / N
        kick = (f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 0;0 0;0 -14;0 3;0 -1;0 0;0 0" '
                f'keyTimes="{kt([0, a + .002, a + .03 / N * 6, a + .06 / N * 6, a + .09 / N * 6, a + .12 / N * 6, 1])}" '
                f'dur="{f(dur)}s" repeatCount="indefinite"/>')
        out.append(f'<g>{kick}'
                   f'<path d="{L["d"]}" fill="url(#tinta)">{anim_ventana(a + .01, b - g, dur, on="0", off="1")}</path>'
                   f'<path d="{L["d"]}" fill="none" stroke="{KEY}" stroke-width="1.6" stroke-dasharray="4 2" opacity="0">'
                   f'{anim_ventana(a + .01, b - g, dur)}</path></g>')
    out.append('</g>')

    # --- marco de selección que salta de letra en letra
    def caja(L):
        x1, y1, x2, y2 = L["box"]
        return (ox + x1 - 7, base + y1 - 7, ox + x2 + 7, base + y2 + 7)

    cajas = [caja(L) for L in letras]
    tiempos, seq = [0], [cajas[0]]
    for i in range(N):
        b = (i + 1) / N
        tiempos.append(b - g)
        seq.append(cajas[i])
        tiempos.append(b)
        seq.append(cajas[(i + 1) % N])
    keys = kt(tiempos)

    def animar(attr, fn):
        vals = ";".join(f(fn(c)) for c in seq)
        return (f'<animate attributeName="{attr}" values="{vals}" keyTimes="{keys}" '
                f'dur="{f(dur)}s" repeatCount="indefinite" calcMode="spline" '
                f'keySplines="{";".join(["0.3 0 0.2 1"] * (len(seq) - 1))}"/>')

    c0 = cajas[0]
    out.append(f'<rect x="{f(c0[0])}" y="{f(c0[1])}" width="{f(c0[2] - c0[0])}" height="{f(c0[3] - c0[1])}" '
               f'fill="{KEY}" fill-opacity=".05" stroke="{KEY}" stroke-opacity=".6">'
               + animar("x", lambda c: c[0]) + animar("y", lambda c: c[1])
               + animar("width", lambda c: c[2] - c[0]) + animar("height", lambda c: c[3] - c[1]) + '</rect>')
    for fx, fy in ((0, 1), (2, 1), (2, 3), (0, 3)):
        out.append(f'<rect width="6" height="6" fill="{KEY}" x="{f(c0[fx] - 3)}" y="{f(c0[fy] - 3)}">'
                   + animar("x", lambda c, fx=fx: c[fx] - 3) + animar("y", lambda c, fy=fy: c[fy] - 3) + '</rect>')

    # etiquetas y chispitas por letra
    for i, (L, c) in enumerate(zip(letras, cajas)):
        a, b = i / N + .01, (i + 1) / N - g
        w_, h_ = L["box"][2] - L["box"][0], L["box"][3] - L["box"][1]
        piezas = [f'<text x="{f(c[0])}" y="{f(c[1] - 8)}" font-family="{MONO}" font-size="10" fill="{KEY}" opacity=".7">'
                  f'{escape(L["c"])}  {round(w_)} × {round(h_)}</text>']
        for _ in range(9):
            lado = rnd.randrange(4)
            t = rnd.random()
            sep = rnd.choice([6, 9, 12, 16])
            if lado == 0:
                px, py = c[0] + t * (c[2] - c[0]), c[1] - sep
            elif lado == 1:
                px, py = c[2] + sep, c[1] + t * (c[3] - c[1])
            elif lado == 2:
                px, py = c[0] + t * (c[2] - c[0]), c[3] + sep
            else:
                px, py = c[0] - sep, c[1] + t * (c[3] - c[1])
            sz = rnd.choice([2, 2, 3, 3, 5, 8])
            bd = rnd.uniform(.5, 1.3)
            estilo = (f'fill="none" stroke="{KEY}"' if sz >= 5 and rnd.random() < .7 else f'fill="{KEY}"')
            piezas.append(f'<rect x="{f(px - sz / 2)}" y="{f(py - sz / 2)}" width="{sz}" height="{sz}" {estilo} opacity=".7">'
                          f'<animate attributeName="opacity" values=".8;.2;.8;0;.8" dur="{f(bd)}s" repeatCount="indefinite"/></rect>')
        out.append(f'<g opacity="0">{anim_ventana(a, b, dur)}{"".join(piezas)}</g>')

    # --- subtítulo split-flap
    out.append(split_flap(W / 2, 226))

    # --- HUD
    out.append(f'<g font-family="{MONO}" font-size="11" fill="{KEY}">'
               f'<text x="24" y="30" opacity=".6">SYS://{escape(USUARIO.upper())}</text>'
               f'<text x="{W - 24}" y="30" text-anchor="end" opacity=".6">v2.0 · {dt.date.today():%Y}</text>'
               f'<circle cx="28" cy="{H - 27}" r="3.5" fill="#34D399"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>'
               f'<text x="40" y="{H - 23}" opacity=".7">ONLINE</text>'
               f'<text x="{W - 24}" y="{H - 23}" text-anchor="end" opacity=".45">GITHUB.COM/{escape(USUARIO.upper())}</text></g>')
    for x, y, dx, dy in ((12, 12, 1, 1), (W - 12, 12, -1, 1), (12, H - 12, 1, -1), (W - 12, H - 12, -1, -1)):
        out.append(f'<path d="M{x} {y + 18 * dy}V{y}H{x + 18 * dx}" fill="none" stroke="{KEY}" stroke-opacity=".5" stroke-width="1.5"/>')

    defs = f"""<defs>
<linearGradient id="tinta" x1="0" y1="-1" x2="0" y2="0.1" gradientUnits="objectBoundingBox">
  <stop offset="0" stop-color="{TITULO}"/><stop offset="1" stop-color="{SOFT}"/></linearGradient>
<radialGradient id="centro" cx=".5" cy=".5" r=".55">
  <stop offset="0" stop-color="{BG}" stop-opacity=".93"/><stop offset=".6" stop-color="{BG}" stop-opacity=".6"/>
  <stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<radialGradient id="blob"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="flow"><rect width="{W}" height="{H}" fill="#000"/>
  <ellipse cx="0" cy="0" rx="260" ry="150" fill="url(#blob)">
    <animateMotion dur="14s" repeatCount="indefinite" path="M-100 60 C 300 -40, 700 360, 1100 160 C 700 380, 300 0, -100 60Z"/></ellipse>
  <ellipse cx="0" cy="0" rx="200" ry="120" fill="url(#blob)">
    <animateMotion dur="19s" repeatCount="indefinite" path="M1100 260 C 700 120, 400 380, -100 220 C 300 40, 700 -20, 1100 260Z"/></ellipse>
</mask>
<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{defs}<g clip-path="url(#win)">{"".join(out)}</g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{BORDE}"/></svg>')


def split_flap(cx, y, ancho=16, tw=30, th=40, gap=5):
    palabras = [r.upper()[:ancho].center(ancho) for r in ROLES]
    hold, flip, stagger, flips = 3.2, 0.07, 0.035, 6
    dur = hold * len(palabras)
    x0 = cx - (ancho * tw + (ancho - 1) * gap) / 2
    out = [f'<g font-family="{MONO}" font-size="23" font-weight="bold" text-anchor="middle">']
    for j in range(ancho):
        x = x0 + j * (tw + gap)
        out.append(f'<rect x="{f(x)}" y="{y}" width="{tw}" height="{th}" rx="5" fill="url(#tile)" stroke="{BORDE}"/>')
        segs = []  # (inicio, fin, char) en segundos
        t_prev = None
        for k, palabra in enumerate(palabras):
            previa = palabras[k - 1][j]
            objetivo = palabra[j]
            s = k * hold + stagger * j
            eventos = []
            if previa != objetivo:
                for m in range(flips):
                    eventos.append((s + m * flip, rnd.choice(CHARSET[:36])))
                eventos.append((s + flips * flip, objetivo))
            else:
                eventos.append((s, objetivo))
            segs.append(eventos)
        # aplanar en segmentos continuos
        lista = [e for ev in segs for e in ev]
        lista.append((lista[0][0] + dur, lista[0][1]))
        piezas = []
        for (t1, c1), (t2, _) in zip(lista, lista[1:]):
            piezas.append((t1, t2, c1))
        # el último segmento cruza el final del ciclo
        finales = []
        for t1, t2, c1 in piezas:
            if t2 <= dur:
                finales.append((t1, t2, c1))
            else:
                finales.append((t1, dur, c1))
                finales.append((0, t2 - dur, c1))
        for t1, t2, c1 in finales:
            if not c1.strip():
                continue
            an = anim_discreto(t1 / dur, t2 / dur, dur)
            op = "" if an == "" else ' opacity="0"' if t1 > 0 else ""
            out.append(f'<text x="{f(x + tw / 2)}" y="{f(y + th / 2 + 8)}" fill="{TITULO}"{op}>{escape(c1)}{an}</text>')
        out.append(f'<line x1="{f(x)}" x2="{f(x + tw)}" y1="{y + th / 2}" y2="{y + th / 2}" stroke="#050d1a" stroke-width="1.5"/>')
    out.append('</g>')
    tile = (f'<defs><linearGradient id="tile" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#16304F"/><stop offset=".5" stop-color="{BAR}"/>'
            f'<stop offset=".5" stop-color="#0D1D35"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>')
    return tile + "".join(out)


# ================================================================= TARJETA NEOFETCH
def linea_dato(clave, valor, ancho=56):
    izq, der = f". {clave}:", f" {valor}"
    puntos = max(2, ancho - len(izq) - len(der))
    return [(".", KEY), (f" {clave}", KEY), (":", KEY), ("." * puntos, DOTS), (der, VAL)]


def linea_seccion(texto, ancho=56):
    t = f"- {texto} "
    return [(t, TITULO), ("─" * (ancho - len(t)), BORDE)]


def retrato_glitch(x0, y0, cols, rows, cw, ch):
    """Foto convertida en mosaico de caracteres glitch con barrido de luz."""
    br = brillo_foto(cols, rows, cw, ch)
    niveles = [0, .12, .24, .4, .58, .78, 1]
    filas = []
    celdas_brillantes = []
    for r in range(rows):
        partes, actual, buf = [], None, ""
        for c in range(cols):
            v = br[r][c] ** 1.15
            n = min(6, int(v * 7))
            if n >= 4:
                celdas_brillantes.append((c, r))
            ch_ = rnd.choice(CHARSET) if n > 0 else " "
            if n != actual and buf:
                partes.append((actual, buf))
                buf = ""
            actual = n
            buf += ch_
        partes.append((actual, buf))
        spans = "".join(f'<tspan fill-opacity="{niveles[n]}">{escape(t)}</tspan>' if n else escape(t)
                        for n, t in partes)
        filas.append(f'<text x="{f(x0)}" y="{f(y0 + r * ch + ch * .8)}" textLength="{f(cols * cw)}" '
                     f'lengthAdjust="spacing" xml:space="preserve" class="a" style="animation-delay:{r * .025:.2f}s">{spans}</text>')
    filas = "\n".join(filas)
    pw, ph = cols * cw, rows * ch
    out = [f'<g font-family="{MONO}" font-size="11" fill="{SOFT}">{filas}</g>',
           f'<g font-family="{MONO}" font-size="11" fill="{TITULO}" mask="url(#barrido)">{filas}</g>']
    rnd.shuffle(celdas_brillantes)
    out.append(f'<g font-family="{MONO}">' + "".join(
        chispa(x0 + c * cw, y0 + r * ch + ch * .8, 11) for c, r in celdas_brillantes[:45]) + '</g>')

    # marco TechText alrededor de la foto
    x1, y1, x2, y2 = x0 - 8, y0 - 8, x0 + pw + 8, y0 + ph + 8
    out.append(f'<rect x="{f(x1)}" y="{f(y1)}" width="{f(x2 - x1)}" height="{f(y2 - y1)}" fill="none" stroke="{KEY}" stroke-opacity=".35" stroke-dasharray="4 3"/>')
    for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
        out.append(f'<rect x="{f(x - 3)}" y="{f(y - 3)}" width="6" height="6" fill="{KEY}"/>')
    out.append(f'<text x="{f(x1)}" y="{f(y1 - 9)}" font-family="{MONO}" font-size="10" fill="{KEY}" opacity=".7">'
               f'foto.png  {cols * 10} × {rows * 10}</text>')
    for _ in range(14):
        lado, t, sep = rnd.randrange(4), rnd.random(), rnd.choice([6, 10, 14])
        px = [x1 + t * (x2 - x1), x2 + sep, x1 + t * (x2 - x1), x1 - sep][lado]
        py = [y1 - sep, y1 + t * (y2 - y1), y2 + sep, y1 + t * (y2 - y1)][lado]
        sz = rnd.choice([2, 2, 3, 5])
        out.append(f'<rect x="{f(px)}" y="{f(py)}" width="{sz}" height="{sz}" fill="{KEY}">'
                   f'<animate attributeName="opacity" values=".8;0;.6;.1;.8" dur="{f(rnd.uniform(.7, 2))}s" repeatCount="indefinite"/></rect>')
    mask = (f'<mask id="barrido"><rect x="{f(x0)}" y="{f(y0 - 60)}" width="{f(pw)}" height="60" fill="url(#banda)">'
            f'<animate attributeName="y" values="{f(y0 - 60)};{f(y0 + ph)}" dur="5s" repeatCount="indefinite"/></rect></mask>'
            f'<linearGradient id="banda" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/>'
            f'<stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>')
    return "".join(out), mask


def construir_tarjeta():
    st = obtener_stats()
    filas = [[(f"{USUARIO}@github", ACENTO), (" " + "─" * (56 - len(USUARIO) - 8), BORDE)]]
    for item in INFO:
        if item is None:
            filas.append([])
        else:
            k, v = item
            filas.append(linea_dato(k, v))
    filas += [[], linea_seccion("Contacto")] + [linea_dato(k, v) for k, v in CONTACTO]
    filas += [[], linea_seccion("GitHub Stats"),
              linea_dato("Repos", f"{st['repos']}  |  Stars: {st['stars']}"),
              linea_dato("Commits", f"{st['commits']}  |  Followers: {st['followers']}")]

    FS, LH, CW = 15, 20, 9.0
    barra, top = 34, 70
    cols, cw, chh = 44, 7.6, 11.5
    alto_info = (len(filas) + 2) * LH
    rows = max(34, int(alto_info / chh))
    x_ret = 40
    x_info = x_ret + cols * cw + 52
    W = int(x_info + 56 * CW + 36)
    H = int(top + max(alto_info, rows * chh) + 34)

    retrato, mask = retrato_glitch(x_ret, top - 10, cols, rows, cw, chh)

    out = [f'<rect width="{W}" height="{H}" fill="{BG}"/>',
           f'<rect width="{W}" height="{barra}" fill="{BAR}"/>']
    for i, c in enumerate(("#F87171", "#FBBF24", "#34D399")):
        out.append(f'<circle cx="{20 + i * 20}" cy="{barra / 2}" r="6" fill="{c}" opacity=".85"/>')
    out.append(f'<text x="{W / 2}" y="{barra / 2 + 5}" text-anchor="middle" fill="{DOTS}" font-family="{MONO}" font-size="13">'
               f'{escape(USUARIO)}@github: ~ $ neofetch --glitch</text>')
    out.append(retrato)

    out.append(f'<g font-family="{MONO}" font-size="{FS}">')
    base = rows * .025
    for i, partes in enumerate(filas):
        if not partes:
            continue
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in partes)
        out.append(f'<text class="l" style="animation-delay:{base + i * .07:.2f}s" x="{f(x_info)}" y="{top + i * LH}" '
                   f'xml:space="preserve">{spans}</text>')
    y = top + (len(filas) + 1) * LH
    out.append(f'<text class="l" style="animation-delay:{base + len(filas) * .07:.2f}s" x="{f(x_info)}" y="{y}" xml:space="preserve">'
               f'<tspan fill="{ACENTO}">{escape(USUARIO)}@github</tspan><tspan fill="{VAL}">:~$ </tspan></text>')
    out.append(f'<rect class="cur" x="{f(x_info + (len(USUARIO) + 12) * CW)}" y="{y - 14}" width="{CW}" height="18" fill="{KEY}"/>')
    out.append('</g>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#sl)"/>')

    estilos = f"""<style>
@keyframes boot {{ from {{ opacity:0; transform:translateX(-6px); }} to {{ opacity:1; transform:none; }} }}
@keyframes blink {{ 50% {{ opacity:0; }} }}
.l {{ animation: boot .35s ease-out both; }}
.a {{ animation: boot .25s ease-out both; }}
.cur {{ animation: blink 1s step-end infinite; }}
</style>"""
    defs = (f'<defs>{mask}<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">'
            f'<rect width="4" height="1" fill="#fff" opacity=".025"/></pattern>'
            f'<clipPath id="win"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{estilos}{defs}<g clip-path="url(#win)">{"".join(out)}</g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{BORDE}"/></svg>')


# ================================================================= LOGO LOOP
def leer_icono(slug):
    import re
    try:
        with open(os.path.join(ICONOS, f"{slug}.svg"), encoding="utf-8") as fh:
            return re.search(r' d="([^"]+)"', fh.read()).group(1)
    except Exception:
        print("Icono no encontrado:", slug)
        return None


def construir_logos():
    W, H = 1000, 128
    ico, gap = 40, 64
    items = [(leer_icono(s), n) for s, n in TECNOLOGIAS]
    items = [i for i in items if i[0]]
    paso = ico + gap
    periodo = len(items) * paso
    copias = max(2, int(W / periodo) + 2)
    y = 30

    def pista(color, op):
        g = []
        for k in range(copias):
            for i, (d, n) in enumerate(items):
                x = k * periodo + i * paso
                g.append(f'<g transform="translate({x} {y}) scale({ico / 24})"><path d="{d}" fill="{color}"/></g>'
                         f'<text x="{x + ico / 2}" y="{y + ico + 22}" text-anchor="middle">{escape(n)}</text>')
        return (f'<g class="track" font-family="{MONO}" font-size="11" fill="{color}" opacity="{op}">'
                + "".join(g) + '</g>')

    estilos = f"""<style>
@keyframes slide {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{periodo}px); }} }}
.track {{ animation: slide {f(periodo / 55)}s linear infinite; }}
</style>"""
    defs = f"""<defs>
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset=".14" stop-color="#fff"/>
<stop offset=".86" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<radialGradient id="lente" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="bordes"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<mask id="foco"><ellipse cx="{W / 2}" cy="{H / 2}" rx="160" ry="90" fill="url(#lente)"/></mask>
<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>"""
    cuerpo = (f'<rect width="{W}" height="{H}" fill="{BG}"/>'
              f'<ellipse cx="{W / 2}" cy="{H / 2}" rx="130" ry="70" fill="{ACENTO}" opacity=".07"/>'
              f'<g mask="url(#bordes)">{pista(SOFT, ".45")}<g mask="url(#foco)">{pista(TITULO, "1")}</g></g>'
              f'<text x="20" y="20" font-family="{MONO}" font-size="10" fill="{KEY}" opacity=".5">$ which --all herramientas</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'{estilos}{defs}<g clip-path="url(#win)">{cuerpo}</g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{BORDE}"/></svg>')


if __name__ == "__main__":
    for nombre, fn in (("header.svg", construir_header), ("profile.svg", construir_tarjeta), ("logos.svg", construir_logos)):
        with open(nombre, "w", encoding="utf-8") as fh:
            fh.write(fn())
        print(f"{nombre} generado ✔")
