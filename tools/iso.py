"""等轴测插图绘制库（网站配图用）。

坐标：x 向右下、y 向左下、z 向上。p(x, y, z) 把三维点投到屏幕。
所有图元按 depth 从小到大绘制（越靠前 / 越高越晚画）。
"""
import math

BG = "#f5f5f7"
BLUE, RED, YELLOW, GREEN, PURPLE = "#4285F4", "#EA4335", "#FBBC04", "#34A853", "#A142F4"
WHITE = "#ffffff"
GRAY = "#c7c7cc"
INK = "#1d1d1f"
WIN = "#d2e3fc"

C = math.cos(math.radians(30))
S = math.sin(math.radians(30))
R2 = math.sqrt(2)


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tint(c, t):
    """变浅：t=0 原色，t=1 白色"""
    return mix(c, "#ffffff", t)


def shades(color):
    """返回 (顶面, 左面, 右面) 三个明暗"""
    if color == WHITE:
        return "#ffffff", "#e6e8ee", "#d0d4dc"
    return mix(color, "#ffffff", .22), color, mix(color, "#000000", .16)


class Scene:
    def __init__(self):
        self.items = []
        self.shadows = []
        self.overlay = []
        self.pts = []
        self.defs = {}

    # ---------- 基础 ----------
    @staticmethod
    def p(x, y, z=0):
        return ((x - y) * C, (x + y) * S - z)

    def _pts(self, pts3):
        pts = [self.p(*q) for q in pts3]
        self.pts += pts
        return " ".join(f"{a:.3f},{b:.3f}" for a, b in pts)

    def poly(self, pts3, fill, depth, extra=""):
        self.items.append((depth, f'<polygon points="{self._pts(pts3)}" fill="{fill}" {extra}/>'))

    def outline(self, pts3, stroke, width, depth, fill="none", extra=""):
        self.items.append((depth, f'<polygon points="{self._pts(pts3)}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" {extra}/>'))

    def polyline(self, pts3, stroke, width, depth, extra=""):
        self.items.append((depth, f'<polyline points="{self._pts(pts3)}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'))

    def line(self, a3, b3, color=INK, width=.25, depth=1e9, dash=None, opacity=1):
        a, b = self.p(*a3), self.p(*b3)
        self.pts += [a, b]
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append((depth, f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" opacity="{opacity}"{da}/>'))

    def dot(self, x, y, z, r, fill, depth, extra=""):
        cx, cy = self.p(x, y, z)
        self.pts += [(cx - r, cy - r), (cx + r, cy + r)]
        self.items.append((depth, f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{fill}" {extra}/>'))

    def raw(self, svg, depth=1e9, bbox=None):
        if bbox:
            self.pts += bbox
        self.items.append((depth, svg))

    def grad(self, color):
        """圆柱体用的左亮右暗横向渐变"""
        gid = "g" + color.lstrip("#")
        if gid not in self.defs:
            top, left, right = shades(color)
            self.defs[gid] = (f'<linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0">'
                              f'<stop offset="0" stop-color="{mix(left, "#ffffff", .25)}"/>'
                              f'<stop offset=".55" stop-color="{left}"/>'
                              f'<stop offset="1" stop-color="{right}"/></linearGradient>')
        return f"url(#{gid})"

    # ---------- 面上作图 ----------
    def on_top(self, z, pts_xy, fill, depth, extra=""):
        self.poly([(a, b, z) for a, b in pts_xy], fill, depth, extra)

    def on_left(self, y, pts_xz, fill, depth, extra=""):
        """y = 常数 的竖直面（朝左下）"""
        self.poly([(a, y, b) for a, b in pts_xz], fill, depth, extra)

    def on_right(self, x, pts_yz, fill, depth, extra=""):
        """x = 常数 的竖直面（朝右下）"""
        self.poly([(x, a, b) for a, b in pts_yz], fill, depth, extra)

    def rect_top(self, x, y, z, w, d, fill, depth, extra=""):
        self.on_top(z, [(x, y), (x + w, y), (x + w, y + d), (x, y + d)], fill, depth, extra)

    def rect_left(self, x, y, z, w, h, fill, depth, extra=""):
        self.on_left(y, [(x, z), (x + w, z), (x + w, z + h), (x, z + h)], fill, depth, extra)

    def rect_right(self, x, y, z, d, h, fill, depth, extra=""):
        self.on_right(x, [(y, z), (y + d, z), (y + d, z + h), (y, z + h)], fill, depth, extra)

    # ---------- 立体 ----------
    def box(self, x, y, z, w, d, h, color=WHITE, windows=None, depth_bias=0, stroke=True, dep=None, faces=None):
        top, left, right = faces or shades(color)
        dep = (x + y + w / 2 + d / 2 + z * 0.01 + depth_bias) if dep is None else dep
        st = 'stroke="#ffffff" stroke-opacity=".7" stroke-width=".035" stroke-linejoin="round"' if stroke else ""
        self.poly([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], left, dep, st)
        self.poly([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], right, dep, st)
        self.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], top, dep + 0.001, st)
        if windows:
            m = min(w, h) * 0.18
            self.poly([(x + m, y + d, z + h * .38), (x + w - m, y + d, z + h * .38),
                       (x + w - m, y + d, z + h * .72), (x + m, y + d, z + h * .72)], windows, dep + 0.002)
            m2 = min(d, h) * 0.18
            self.poly([(x + w, y + m2, z + h * .38), (x + w, y + d - m2, z + h * .38),
                       (x + w, y + d - m2, z + h * .72), (x + w, y + m2, z + h * .72)], mix(windows, "#000000", .12), dep + 0.002)
        return dep

    def wire_box(self, x, y, z, w, d, h, color, width=.05, depth=1e9, fill_opacity=.1):
        """数字孪生用的线框盒子（半透明面 + 全部棱线）"""
        c = [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z),
             (x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]
        for f in ([3, 2, 6, 7], [1, 2, 6, 5], [4, 5, 6, 7]):
            self.poly([c[i] for i in f], color, depth, f'fill-opacity="{fill_opacity}"')
        for a, b in [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]:
            hidden = a in (0,) or b in (0,)
            self.line(c[a], c[b], color, width, depth + .01, dash=(f"{width * 3:.2f} {width * 3:.2f}" if hidden else None),
                      opacity=.55 if hidden else 1)

    def cyl(self, x, y, z, r, h, color=WHITE, dep=None, top=None):
        """竖直圆柱（x, y 为底面圆心）"""
        dep = (x + y + z * 0.01) if dep is None else dep
        cx, cbot = self.p(x, y, z)
        _, ctop = self.p(x, y, z + h)
        rx, ry = r * R2 * C, r * R2 * S
        self.pts += [(cx - rx, ctop - ry), (cx + rx, cbot + ry)]
        topc = top or shades(color)[0]
        body = (f'<path d="M{cx - rx:.3f},{ctop:.3f} L{cx - rx:.3f},{cbot:.3f} '
                f'A{rx:.3f},{ry:.3f} 0 0 0 {cx + rx:.3f},{cbot:.3f} L{cx + rx:.3f},{ctop:.3f} Z" fill="{self.grad(color)}"/>')
        cap = f'<ellipse cx="{cx:.3f}" cy="{ctop:.3f}" rx="{rx:.3f}" ry="{ry:.3f}" fill="{topc}"/>'
        self.items.append((dep, body + cap))
        return dep

    def disc(self, x, y, z, r, fill, depth, extra=""):
        """水平圆（地面上的圆形）"""
        cx, cy = self.p(x, y, z)
        rx, ry = r * R2 * C, r * R2 * S
        self.pts += [(cx - rx, cy - ry), (cx + rx, cy + ry)]
        self.items.append((depth, f'<ellipse cx="{cx:.3f}" cy="{cy:.3f}" rx="{rx:.3f}" ry="{ry:.3f}" fill="{fill}" {extra}/>'))

    def person(self, x, y, color, z=0, scale=1.0, dep=None):
        dep = (x + y + 0.5) if dep is None else dep
        self.disc(x, y, z, .55 * scale, "#1d1d1f", dep - .05, 'opacity=".10"')
        self.cyl(x, y, z, .36 * scale, 1.05 * scale, color, dep=dep)
        if "head" not in self.defs:
            self.defs["head"] = ('<radialGradient id="head" cx=".38" cy=".35" r=".75">'
                                 '<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#dfe1e6"/></radialGradient>')
        hx_, hy_ = self.p(x, y, z + (1.05 + .5) * scale)
        r = .4 * scale
        self.pts += [(hx_ - r, hy_ - r)]
        self.items.append((dep + .001, f'<circle cx="{hx_:.3f}" cy="{hy_:.3f}" r="{r:.3f}" fill="url(#head)"/>'))

    def plate(self, x, y, w, d, color="#e8e8ed", h=0.18):
        self.box(x, y, -h, w, d, h, color, depth_bias=-100, stroke=False, dep=-1000)

    def shadow(self, x, y, w, d, blur=1.0, opacity=.18, grow=0.35):
        pts = [self.p(x - grow, y - grow, 0), self.p(x + w + grow, y - grow, 0),
               self.p(x + w + grow, y + d + grow, 0), self.p(x - grow, y + d + grow, 0)]
        self.pts += pts
        dd = " ".join(f"{a:.2f},{b:.2f}" for a, b in pts)
        self.shadows.append(f'<polygon points="{dd}" fill="#1d1d1f" opacity="{opacity}" filter="url(#soft)"/>')

    # ---------- 屏幕空间元素（随场景缩放） ----------
    def bubble(self, x, y, z, w, h, depth, lines=3, accent=RED, tail="left"):
        """对话气泡：白色圆角卡片 + 文字行 + 强调色圆点"""
        cx, cy = self.p(x, y, z)
        x0, y0 = cx - w / 2, cy - h
        r = h * .18
        self.pts += [(x0, y0), (x0 + w, y0 + h + h * .2)]
        tx = x0 + w * (.22 if tail == "left" else .78)
        parts = [f'<g filter="url(#lift)"><rect x="{x0:.3f}" y="{y0:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{r:.3f}" fill="#ffffff"/>'
                 f'<path d="M{tx - h * .1:.3f},{y0 + h - .01:.3f} L{tx:.3f},{y0 + h * 1.2:.3f} L{tx + h * .14:.3f},{y0 + h - .01:.3f} Z" fill="#ffffff"/></g>']
        pad = h * .2
        ar = h * .14
        parts.append(f'<circle cx="{x0 + pad + ar:.3f}" cy="{y0 + pad + ar:.3f}" r="{ar:.3f}" fill="{accent}"/>')
        lh = (h - 2 * pad) / max(lines, 1)
        for i in range(lines):
            lw = (w - 3 * pad - 2 * ar) * (1 if i < lines - 1 else .6) if i == 0 else (w - 2 * pad) * (.9 if i < lines - 1 else .55)
            lx = x0 + pad + (2 * ar + pad * .8 if i == 0 else 0)
            ly = y0 + pad + lh * i + lh * .35
            parts.append(f'<rect x="{lx:.3f}" y="{ly:.3f}" width="{lw:.3f}" height="{lh * .3:.3f}" rx="{lh * .15:.3f}" fill="#e3e3e8"/>')
        self.items.append((depth, "".join(parts)))
        self.ensure_lift()

    def ensure_lift(self):
        if "lift" not in self.defs:
            self.defs["lift"] = ('<filter id="lift" x="-30%" y="-30%" width="160%" height="180%">'
                                 '<feDropShadow dx="0" dy=".12" stdDeviation=".18" flood-color="#1d1d1f" flood-opacity=".14"/></filter>')

    def badge(self, x, y, z, r, color, depth, icon="check"):
        """圆形徽章（对勾 / 星）"""
        cx, cy = self.p(x, y, z)
        self.pts += [(cx - r, cy - r), (cx + r, cy + r)]
        self.ensure_lift()
        if icon == "check":
            ic = (f'<path d="M{cx - r * .42:.3f},{cy + r * .02:.3f} L{cx - r * .1:.3f},{cy + r * .34:.3f} L{cx + r * .45:.3f},{cy - r * .3:.3f}" '
                  f'fill="none" stroke="#fff" stroke-width="{r * .2:.3f}" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            ic = star(cx, cy, r * .55)
        self.items.append((depth, f'<g filter="url(#lift)"><circle cx="{cx:.3f}" cy="{cy:.3f}" r="{r:.3f}" fill="{color}"/></g>{ic}'))

    def shield(self, x, y, z, s, color, depth):
        cx, cy = self.p(x, y, z)
        self.pts += [(cx - s, cy - s * 1.2), (cx + s, cy + s * 1.2)]
        self.ensure_lift()
        d = (f"M{cx:.3f},{cy - s * 1.15:.3f} L{cx + s:.3f},{cy - s * .75:.3f} L{cx + s * .92:.3f},{cy + s * .15:.3f} "
             f"Q{cx + s * .7:.3f},{cy + s * .85:.3f} {cx:.3f},{cy + s * 1.2:.3f} Q{cx - s * .7:.3f},{cy + s * .85:.3f} {cx - s * .92:.3f},{cy + s * .15:.3f} "
             f"L{cx - s:.3f},{cy - s * .75:.3f} Z")
        ck = (f'<path d="M{cx - s * .42:.3f},{cy + s * .02:.3f} L{cx - s * .1:.3f},{cy + s * .36:.3f} L{cx + s * .45:.3f},{cy - s * .32:.3f}" '
              f'fill="none" stroke="#fff" stroke-width="{s * .2:.3f}" stroke-linecap="round" stroke-linejoin="round"/>')
        self.items.append((depth, f'<g filter="url(#lift)"><path d="{d}" fill="{color}"/></g>{ck}'))

    def svg(self, W, H, pad=0.12, offset=(0, 0), bg="url(#bgg)"):
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
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.1"/></filter>
  <radialGradient id="bgg" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="#f7f7f9"/><stop offset="1" stop-color="#efeff2"/></radialGradient>
  {"".join(self.defs.values())}
</defs>
<rect width="{W}" height="{H}" fill="{bg}"/>
<g transform="translate({tx:.2f},{ty:.2f}) scale({k:.4f})">{sh}{body}</g>
{"".join(self.overlay)}
</svg>'''


def star(cx, cy, R, fill="#ffffff"):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else R * .45
        pts.append(f"{cx + rr * math.cos(a):.3f},{cy + rr * math.sin(a):.3f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'
