"""Isometric illustration generator for the lab website (light, Google/Apple-like)."""
import math

BG = "#f5f5f7"
BLUE, RED, YELLOW, GREEN, PURPLE = "#4285F4", "#EA4335", "#FBBC04", "#34A853", "#A142F4"
WHITE = "#ffffff"
GRAY = "#c7c7cc"
INK = "#1d1d1f"

C = math.cos(math.radians(30))
S = math.sin(math.radians(30))


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shades(color):
    if color == WHITE:
        return "#ffffff", "#e6e8ee", "#d0d4dc"
    return mix(color, "#ffffff", .22), color, mix(color, "#000000", .16)


class Scene:
    def __init__(self):
        self.items = []  # (depth, svg-element-string, points for bbox)
        self.shadows = []
        self.overlay = []
        self.pts = []

    @staticmethod
    def p(x, y, z):
        return ((x - y) * C, (x + y) * S - z)

    def poly(self, pts3, fill, depth, extra=""):
        pts = [self.p(*q) for q in pts3]
        self.pts += pts
        d = " ".join(f"{a:.2f},{b:.2f}" for a, b in pts)
        self.items.append((depth, f'<polygon points="{d}" fill="{fill}" {extra}/>'))

    def box(self, x, y, z, w, d, h, color=WHITE, windows=None, depth_bias=0, stroke=True, dep=None):
        top, left, right = shades(color)
        dep = (x + y + w / 2 + d / 2 + z * 0.01 + depth_bias) if dep is None else dep
        st = 'stroke="#ffffff" stroke-opacity=".7" stroke-width=".035" stroke-linejoin="round"' if stroke else ""
        # left face (y = y+d)
        self.poly([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], left, dep, st)
        # right face (x = x+w)
        self.poly([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], right, dep, st)
        # top
        self.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], top, dep + 0.001, st)
        if windows:
            wc = windows
            # windows on left face: horizontal strip
            m = min(w, h) * 0.18
            self.poly([(x + m, y + d, z + h * .38), (x + w - m, y + d, z + h * .38),
                       (x + w - m, y + d, z + h * .72), (x + m, y + d, z + h * .72)], wc, dep + 0.002)
            m2 = min(d, h) * 0.18
            self.poly([(x + w, y + m2, z + h * .38), (x + w, y + d - m2, z + h * .38),
                       (x + w, y + d - m2, z + h * .72), (x + w, y + m2, z + h * .72)], mix(wc, "#000000", .12), dep + 0.002)

    def plate(self, x, y, w, d, color="#e8e8ed", h=0.18):
        self.box(x, y, -h, w, d, h, color, depth_bias=-100, stroke=False)

    def shadow(self, x, y, w, d, blur=1.0, opacity=.18, grow=0.35):
        pts = [self.p(x - grow, y - grow, 0), self.p(x + w + grow, y - grow, 0),
               self.p(x + w + grow, y + d + grow, 0), self.p(x - grow, y + d + grow, 0)]
        self.pts += pts
        dd = " ".join(f"{a:.2f},{b:.2f}" for a, b in pts)
        self.shadows.append(f'<polygon points="{dd}" fill="#1d1d1f" opacity="{opacity}" filter="url(#soft)"/>')

    def line(self, a3, b3, color=INK, width=.25, depth=1e9, dash=None, opacity=1):
        a, b = self.p(*a3), self.p(*b3)
        self.pts += [a, b]
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append((depth, f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"{da}/>'))

    def raw(self, svg, depth=1e9, bbox=None):
        if bbox:
            self.pts += bbox
        self.items.append((depth, svg))

    def svg(self, W, H, pad=0.12, scale_fit=True, offset=(0, 0)):
        xs = [q[0] for q in self.pts]
        ys = [q[1] for q in self.pts]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        bw, bh = maxx - minx, maxy - miny
        k = min(W * (1 - 2 * pad) / bw, H * (1 - 2 * pad) / bh)
        tx = W / 2 - (minx + bw / 2) * k + offset[0] * W
        ty = H / 2 - (miny + bh / 2) * k + offset[1] * H
        body = "".join(e for _, e in sorted(self.items, key=lambda t: t[0]))
        sh = "".join(self.shadows)
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{1.1:.2f}"/></filter>
  <radialGradient id="bgg" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="#f7f7f9"/><stop offset="1" stop-color="#efeff2"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="url(#bgg)"/>
<g transform="translate({tx:.2f},{ty:.2f}) scale({k:.4f})">{sh}{body}</g>
{"".join(self.overlay)}
</svg>'''
