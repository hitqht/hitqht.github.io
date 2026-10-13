import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
from iso import *

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
WIN = "#d2e3fc"   # Google blue-50 glass
COLORS5 = [BLUE, RED, YELLOW, GREEN, PURPLE]


def save(name, svg):
    if name.startswith("tile-"):  # 首页入口卡是白底卡片，插图也用白底
        svg = svg.replace('fill="url(#bgg)"', 'fill="#ffffff"')
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)


# ---------- banner: modular building being assembled ----------
def banner():
    s = Scene()
    w, d, h, g = 3.0, 2.4, 1.5, 0.08
    nx, ny, nz = 3, 2, 4
    s.plate(-1.6, -1.2, nx * w + 3.2, ny * d + 3.8)
    s.shadow(0, 0, nx * w, ny * d, opacity=.22)
    missing = (2, 1, 3)
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                if (i, j, k) == missing:
                    continue
                if k == 3 and (i, j) == (0, 0):
                    continue
                s.box(i * w + g, j * d + g, k * h + g, w - 2 * g, d - 2 * g, h - 2 * g, WHITE, windows=WIN, dep=(i + j + k) * 1.0)
    # module being lowered
    lift = 2.6
    mx, my, mz = missing[0] * w + g, missing[1] * d + g, missing[2] * h + g + lift
    s.box(mx, my, mz, w - 2 * g, d - 2 * g, h - 2 * g, BLUE, windows="#aecbfa", dep=50)
    # crane
    cx, cy = -1.0, -0.6
    s.box(cx, cy, 0, .45, .45, 11.5, "#e8eaed", dep=-30)
    s.box(cx - 1.2, cy, 11.5, 10.6, .45, .35, "#e8eaed", dep=40)
    s.box(cx - 1.4, cy - .1, 10.2, 1.2, .65, 1.3, "#dadce0", dep=39)
    hookx = mx + (w - 2 * g) / 2
    hooky = my + (d - 2 * g) / 2
    top = mz + h - 2 * g
    s.line((hookx, cy + .22, 11.5), (hookx, cy + .22, top + 1.4), "#9aa0a6", .06, depth=60)
    for ox, oy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        s.line((hookx, cy + .22, top + 1.4), (hookx + ox * (w / 2 - .3), hooky + oy * (d / 2 - .3), top), "#9aa0a6", .05, depth=60)
    # materials on ground: small colored crates
    for n, (c, (px, py)) in enumerate(zip([RED, YELLOW, GREEN],
                                          [(nx * w + .4, ny * d + 1.2), (nx * w + .4, ny * d + 2.3), (nx * w - 1.0, ny * d + 1.9)])):
        s.shadow(px, py, .9, .9, opacity=.15, grow=.15)
        s.box(px, py, 0, .9, .9, .7, c, dep=20 + n)
    s.box(nx * w + .4, ny * d + 1.2, .7, .9, .9, .7, PURPLE, dep=25)
    return s.svg(2400, 1400, pad=.05)


# ---------- five research directions as blocks ----------
def research(W, H, pad=.14):
    s = Scene()
    s.plate(-0.8, -0.8, 12.6, 4.6)
    heights = [3.2, 4.6, 2.6, 3.8, 2.0]
    for i, (c, hh) in enumerate(zip(COLORS5, heights)):
        x = i * 2.4
        s.shadow(x, 0, 1.8, 3.0, opacity=.16, grow=.25)
        s.box(x, 0, 0, 1.8, 3.0, hh * .62, WHITE, windows=WIN)
        s.box(x, 0, hh * .62, 1.8, 3.0, hh * .38, c)
    return s.svg(W, H, pad=pad)


# ---------- papers stack with a chart ----------
def papers(W, H, pad=.16, lens=False):
    s = Scene()
    pw, pd = 6.0, 7.8
    s.shadow(0, 0, pw, pd, opacity=.18, grow=.4)
    for k in range(6):
        off = (k % 2) * .18 - .09
        s.box(off, -off, k * .16, pw, pd, .14, WHITE, depth_bias=k, stroke=True)
    z0 = 6 * .16 + .002
    # title bar + text lines (flat)
    def flat(x, y, w, d, col, dep):
        s.poly([(x, y, z0), (x + w, y, z0), (x + w, y + d, z0), (x, y + d, z0)], col, 100 + dep)
    flat(.7, .7, 3.4, .45, INK, 1)
    for r in range(4):
        flat(.7, 1.6 + r * .55, 4.6 - (r % 2) * 1.1, .22, "#dadce0", 2)
    # bar chart
    for i, (c, hh) in enumerate(zip([BLUE, RED, YELLOW, GREEN], [1.6, 2.4, 1.1, 2.0])):
        s.box(.9 + i * 1.15, 5.2, z0, .7, 1.6, hh, c, depth_bias=200 + i)
    if lens:
        s.overlay.append('')
    return s.svg(W, H, pad=pad)


# ---------- people (flat, Google-style avatars) ----------
def people(W, H, n=5, scale=1.0):
    cols = [BLUE, RED, YELLOW, GREEN, PURPLE, BLUE, GREEN]
    cx, cy = W / 2, H * .56
    r = min(W, H) * .105 * scale
    gap = r * 2.55
    parts = []
    xs = [cx + (i - (n - 1) / 2) * gap for i in range(n)]
    # connecting arcs
    for i in range(n - 1):
        x1, x2 = xs[i], xs[i + 1]
        parts.append(f'<path d="M{x1:.1f},{cy - r * 1.9:.1f} Q{(x1 + x2) / 2:.1f},{cy - r * 3.1:.1f} {x2:.1f},{cy - r * 1.9:.1f}" fill="none" stroke="#c7c7cc" stroke-width="{r * .06:.1f}" stroke-dasharray="{r * .12:.1f} {r * .14:.1f}" stroke-linecap="round"/>')
    for i, x in enumerate(xs):
        lift = -r * .35 if i % 2 else 0
        c = cols[i % len(cols)]
        y = cy + lift
        parts.append(f'<ellipse cx="{x:.1f}" cy="{cy + r * 1.75:.1f}" rx="{r * 1.05:.1f}" ry="{r * .22:.1f}" fill="#1d1d1f" opacity=".12" filter="url(#soft2)"/>')
        parts.append(f'<path d="M{x - r * .95:.1f},{y + r * 1.55:.1f} C{x - r * .95:.1f},{y + r * .25:.1f} {x + r * .95:.1f},{y + r * .25:.1f} {x + r * .95:.1f},{y + r * 1.55:.1f} Z" fill="{c}"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y - r * .55:.1f}" r="{r * .62:.1f}" fill="#ffffff"/>')
        parts.append(f'<circle cx="{x:.1f}" cy="{y - r * .55:.1f}" r="{r * .62:.1f}" fill="none" stroke="{c}" stroke-width="{r * .1:.1f}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><filter id="soft2" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="{r * .12:.1f}"/></filter>
<radialGradient id="bgg" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="#f7f7f9"/><stop offset="1" stop-color="#efeff2"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="url(#bgg)"/>{"".join(parts)}</svg>'''


# ---------- books ----------
def books(W, H):
    s = Scene()
    specs = [(BLUE, 1.5), (RED, 1.2), (GREEN, 1.7), (YELLOW, 1.1)]
    z = 0
    s.shadow(0, 0, 5.5, 7.5, opacity=.2, grow=.4)
    for k, (c, t) in enumerate(specs):
        off = [0, .5, -.3, .35][k]
        x, y = off, -off * .6
        top, left, right = shades(c)
        dep = k * 10
        bw, bd = 5.2, 7.2
        # pages (white block slightly inset)
        # covers top & bottom
        s.box(x, y, z, bw, bd, .12, c, depth_bias=dep + 1, stroke=False)
        s.box(x + .12, y + .12, z + .12, bw - .12, bd - .24, t - .24, "#fbfbfd", depth_bias=dep + 1.5, stroke=False)
        for ln in range(1, 4):
            zz = z + .12 + (t - .24) * ln / 4
            s.line((x + .12, y + bd - .12, zz), (x + bw, y + bd - .12, zz), "#e0e0e6", .03, depth=x + y + bw / 2 + bd / 2 + dep + 1.6)
        s.box(x, y, z + t - .12, bw, bd, .12, c, depth_bias=dep + 2, stroke=False)
        # spine on the right face side (x = x+bw)
        s.poly([(x + bw, y, z), (x + bw, y + bd, z), (x + bw, y + bd, z + t), (x + bw, y, z + t)], mix(c, "#000000", .12), dep + 3)
        s.poly([(x + bw, y + bd * .3, z + t * .35), (x + bw, y + bd * .7, z + t * .35), (x + bw, y + bd * .7, z + t * .55), (x + bw, y + bd * .3, z + t * .55)], "#ffffff", dep + 4, 'opacity=".55"')
        z += t
    return s.svg(W, H, pad=.16)


# ---------- awards podium ----------
def awards(W, H):
    s = Scene()
    s.plate(-1, -1, 11, 5)
    steps = [(0, 2.2, GREEN), (3, 3.4, YELLOW), (6, 1.5, BLUE)]
    for x, hh, c in steps:
        s.shadow(x, 0, 3, 3, opacity=.14, grow=.2)
        s.box(x, 0, 0, 3, 3, hh, WHITE)
        s.box(x, 0, hh, 3, 3, .22, c)
    svg = s.svg(W, H, pad=.2, offset=(0, .14))
    # medal overlay above centre
    cx, cy, r = W * .5, H * .3, H * .1
    medal = f'''<g>
<path d="M{cx - r * .55:.1f},{cy - r * 2.0:.1f} L{cx - r * .15:.1f},{cy - r * .8:.1f} L{cx + r * .15:.1f},{cy - r * .8:.1f} L{cx - r * .2:.1f},{cy - r * 2.0:.1f} Z" fill="{BLUE}"/>
<path d="M{cx + r * .55:.1f},{cy - r * 2.0:.1f} L{cx + r * .15:.1f},{cy - r * .8:.1f} L{cx - r * .15:.1f},{cy - r * .8:.1f} L{cx + r * .2:.1f},{cy - r * 2.0:.1f} Z" fill="{RED}"/>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{YELLOW}"/>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * .74:.1f}" fill="none" stroke="#ffffff" stroke-opacity=".7" stroke-width="{r * .06:.1f}"/>
{star(cx, cy, r * .42)}
</g>'''
    return svg.replace("</svg>", medal + "</svg>")


def star(cx, cy, R):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else R * .45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="#ffffff"/>'


# ---------- cv: rising steps ----------
def cv(W, H):
    s = Scene()
    n = 6
    cols = [GRAY, GRAY, GRAY, GRAY, GRAY, BLUE]
    s.shadow(0, 0, n * 1.6, 2.6, opacity=.16, grow=.3)
    for i in range(n):
        hh = .7 + i * .75
        s.box(i * 1.6, 0, 0, 1.6, 2.6, hh, WHITE)
        c = [BLUE, RED, YELLOW, GREEN, PURPLE, BLUE][i]
        s.box(i * 1.6 + .4, .7, hh, .8, .8, .7 if i == n - 1 else .4, c, depth_bias=100 + i)
    # flag on last step
    x0 = (n - 1) * 1.6 + .8
    ztop = .7 + (n - 1) * .75 + .7
    s.line((x0, 1.1, ztop), (x0, 1.1, ztop + 3.2), "#9aa0a6", .07, depth=500)
    s.poly([(x0, 1.1, ztop + 3.2), (x0 + 1.6, 1.1, ztop + 2.75), (x0, 1.1, ztop + 2.3)], RED, 501)
    return s.svg(W, H, pad=.16)


save("banner", banner())
save("tile-research", research(1200, 900))
save("tile-papers", papers(1200, 900))
save("tile-people", people(1200, 900, n=4))
save("hero-research", research(1600, 1200, pad=.12))
save("hero-publications", papers(1600, 1200, pad=.14))
save("hero-team", people(1600, 1200, n=5, scale=.95))
save("hero-books", books(1600, 1200))
save("hero-awards", awards(1600, 1200))
save("hero-cv", cv(1600, 1200))
print("ok")
