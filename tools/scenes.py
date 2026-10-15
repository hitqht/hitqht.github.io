"""网站配图：python3 tools/scenes.py 输出目录  →  生成全部 SVG。

每张图对应网站上的一个位置（见文件末尾 OUTPUTS）。
配色固定为 Google 五色：蓝=装配式建筑、红=垂类大模型、黄=智能设计、绿=智能检测、紫=建造机器人。
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import *

CONCRETE = ("#f3f4f6", "#e1e3e8", "#cdd0d7")
STEEL = BLUE


# ============================================================
# 通用构件
# ============================================================
def facade(s, x, y, z, w, d, h, floors, dep, color=WIN, per=0.95):
    """在盒子的两个可见立面上画逐层窗带"""
    fh = h / floors
    nl = max(1, round(w / per))
    nr = max(1, round(d / per))
    for i in range(floors):
        z0, z1 = z + i * fh + fh * .3, z + i * fh + fh * .78
        for j in range(nl):
            a = x + w * j / nl + w / nl * .16
            b = x + w * (j + 1) / nl - w / nl * .16
            s.on_left(y + d, [(a, z0), (b, z0), (b, z1), (a, z1)], color, dep + .002)
        for j in range(nr):
            a = y + d * j / nr + d / nr * .16
            b = y + d * (j + 1) / nr - d / nr * .16
            s.on_right(x + w, [(a, z0), (b, z0), (b, z1), (a, z1)], mix(color, "#000000", .1), dep + .002)


def building(s, x, y, w, d, h, floors, color=WHITE, roof=None, dep=None):
    s.shadow(x, y, w, d, opacity=.14, grow=.25)
    dep = s.box(x, y, 0, w, d, h, color, dep=dep)
    facade(s, x, y, 0, w, d, h, floors, dep)
    if roof:
        s.box(x + w * .15, y + d * .15, h, w * .7, d * .7, .18, roof, dep=dep + .01)
    return dep


def crane(s, x, y, height, jib, dep=-30, color="#e8eaed"):
    s.box(x, y, 0, .45, .45, height, color, dep=dep)
    for k in range(int(height / 1.2)):
        z = k * 1.2 + .2
        s.line((x + .45, y + .45, z), (x + .45, y + .45, z + 1.0), "#d0d4dc", .04, depth=dep + .5)
    s.box(x - 1.2, y, height, jib, .45, .35, color, dep=dep + 70)
    s.box(x - 1.1, y - .1, height - 1.3, 1.2, .65, 1.3, "#dadce0", dep=dep + 69)


def crane_y(s, x, y, height, jib, dep=-200, color="#e8eaed"):
    """吊臂沿 y 方向（伸向画面左前方）的塔吊"""
    s.box(x, y, 0, .45, .45, height, color, dep=dep)
    for k in range(int(height / 1.2)):
        z = k * 1.2 + .2
        s.line((x + .45, y + .45, z), (x + .45, y + .45, z + 1.0), "#d0d4dc", .04, depth=dep + .5)
    s.box(x, y - 1.6, height, .45, jib, .35, color, dep=dep + 300)
    s.box(x - .1, y - 1.6, height - 1.3, .65, 1.2, 1.3, "#dadce0", dep=dep + 299)


def hook_lines(s, hx_, hy_, ztop, box_xywd, zbox, dep, color="#9aa0a6"):
    x, y, w, d = box_xywd
    knot = (hx_, hy_, zbox + 1.4)
    s.line((hx_, hy_, ztop), knot, color, .06, depth=dep)
    for px, py in [(x + .2, y + .2), (x + w - .2, y + .2), (x + w - .2, y + d - .2), (x + .2, y + d - .2)]:
        s.line(knot, (px, py, zbox), color, .045, depth=dep)


def robot_arm(s, base, joints, color=PURPLE, dep=500, width=.42, platform=True):
    """建造机器人：移动底盘 + 转台 + 多段机械臂。joints 为各关节三维坐标"""
    bx, by = base
    if platform:
        s.shadow(bx - .9, by - .8, 1.8, 1.6, opacity=.16, grow=.2)
        s.box(bx - .9, by - .8, 0, 1.8, 1.6, .45, WHITE, dep=dep - 3)
        s.rect_left(bx - .75, by - .8, .12, 1.5, .2, "#bdc1c6", dep - 2.9)
        s.rect_right(bx + .9, by - .65, .12, 1.3, .2, "#aeb2b9", dep - 2.9)
    s.cyl(bx, by, .45, .5, .35, "#5f6368", dep=dep - 2)
    s.cyl(bx, by, .8, .4, .4, color, dep=dep - 1)
    pts = [(bx, by, 1.15)] + list(joints)
    dark = mix(color, "#000000", .18)
    for a, b in zip(pts, pts[1:]):
        s.line(a, b, dark, width + .08, depth=dep)
        s.line(a, b, color, width, depth=dep + .01)
    for j in pts[:-1]:
        s.dot(*j, width * .62, "#ffffff", dep + .02, f'stroke="{dark}" stroke-width="{width * .18:.3f}"')
    return pts[-1]


def scanner(s, x, y, color=GREEN, dep=None, height=1.9):
    """三维激光扫描仪（三脚架）"""
    dep = (x + y + 1) if dep is None else dep
    head = (x, y, height)
    for lx, ly in [(x - .7, y + .25), (x + .45, y - .6), (x + .3, y + .75)]:
        s.line(head, (lx, ly, 0), "#80868b", .06, depth=dep - .5)
    s.cyl(x, y, height, .34, .55, WHITE, dep=dep)
    s.cyl(x, y, height + .2, .35, .14, color, dep=dep + .01, top=tint(color, .25))
    s.cyl(x, y, height + .55, .22, .12, "#5f6368", dep=dep + .02)
    return (x, y, height + .4)


def turbine(s, x, y, h, dep=None, blade=3.4, angle=12):
    """风机塔筒（变截面）+ 机舱 + 叶片"""
    dep = (x + y) if dep is None else dep
    n = 6
    for i in range(n):
        r = .5 - .26 * i / (n - 1)
        s.cyl(x, y, i * h / n, r, h / n + .01, WHITE, dep=dep + i * .001,
              top=WHITE if i < n - 1 else None)
        if i % 2 == 1:
            s.cyl(x, y, (i + 1) * h / n - .08, r + .01, .08, YELLOW, dep=dep + i * .001 + .0005)
    s.box(x - .35, y - .3, h, .7, 1.3, .55, WHITE, dep=dep + .01)
    hx_, hy_ = s.p(x, y + 1.3, h + .28)
    parts = []
    for k in range(3):
        a = math.radians(angle + k * 120)
        tipx, tipy = hx_ + blade * math.cos(a), hy_ - blade * math.sin(a)
        nx, ny = -math.sin(a) * .22, -math.cos(a) * .22
        parts.append(f'<path d="M{hx_ + nx:.3f},{hy_ + ny:.3f} Q{(hx_ + tipx) / 2 + nx * 1.6:.3f},{(hy_ + tipy) / 2 + ny * 1.6:.3f} {tipx:.3f},{tipy:.3f} '
                     f'L{hx_ - nx * .6:.3f},{hy_ - ny * .6:.3f} Z" fill="#f1f3f4" stroke="#bdc1c6" stroke-width=".05" stroke-linejoin="round"/>')
        s.pts += [(tipx, tipy)]
    parts.append(f'<circle cx="{hx_:.3f}" cy="{hy_:.3f}" r=".26" fill="#ffffff" stroke="#d0d4dc" stroke-width=".05"/>')
    s.raw("".join(parts), depth=dep + .05)


def hardhat(s, x, y, z, size, color=YELLOW, dep=None):
    dep = (x + y + z) if dep is None else dep
    cx, cy = s.p(x, y, z)
    rx, ry = size * 1.15, size * .42
    dark = mix(color, "#000000", .14)
    d = (f'<ellipse cx="{cx:.3f}" cy="{cy:.3f}" rx="{rx:.3f}" ry="{ry:.3f}" fill="{dark}"/>'
         f'<path d="M{cx - size * .78:.3f},{cy - size * .05:.3f} Q{cx - size * .78:.3f},{cy - size * 1.05:.3f} {cx:.3f},{cy - size * 1.05:.3f} '
         f'Q{cx + size * .78:.3f},{cy - size * 1.05:.3f} {cx + size * .78:.3f},{cy - size * .05:.3f} Z" fill="{color}"/>'
         f'<rect x="{cx - size * .09:.3f}" y="{cy - size * 1.08:.3f}" width="{size * .18:.3f}" height="{size * 1.0:.3f}" rx="{size * .09:.3f}" fill="{tint(color, .35)}"/>')
    s.pts += [(cx - rx, cy - size * 1.1), (cx + rx, cy + ry)]
    s.raw(d, depth=dep)


def chart_card(s, x, y, z, w, h, dep, color=YELLOW, kind="pareto"):
    """浮动的小图表卡片：帕累托前沿 / 柱状"""
    cx, cy = s.p(x, y, z)
    x0, y0 = cx - w / 2, cy - h
    s.pts += [(x0, y0), (x0 + w, y0 + h)]
    s.ensure_lift()
    pad = h * .16
    parts = [f'<g filter="url(#lift)"><rect x="{x0:.3f}" y="{y0:.3f}" width="{w:.3f}" height="{h:.3f}" rx="{h * .12:.3f}" fill="#fff"/></g>',
             f'<path d="M{x0 + pad:.3f},{y0 + pad:.3f} L{x0 + pad:.3f},{y0 + h - pad:.3f} L{x0 + w - pad:.3f},{y0 + h - pad:.3f}" fill="none" stroke="#dadce0" stroke-width="{h * .025:.3f}"/>']
    if kind == "pareto":
        rnd = random.Random(3)
        for _ in range(16):
            u, v = rnd.random(), rnd.random()
            px = x0 + pad + (w - 2 * pad) * (.12 + .82 * u)
            py = y0 + pad + (h - 2 * pad) * (.08 + .85 * v)
            parts.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="{h * .03:.3f}" fill="#dadce0"/>')
        front = []
        for i in range(7):
            t = i / 6
            px = x0 + pad + (w - 2 * pad) * (.1 + .85 * t)
            py = y0 + pad + (h - 2 * pad) * (.95 - .85 * (1 - t) ** 2.2) - (h - 2 * pad) * .05
            py = y0 + h - pad - (h - 2 * pad) * (.85 * (1 - t) ** 2 + .08)
            front.append((px, py))
        parts.append('<polyline points="' + " ".join(f"{a:.3f},{b:.3f}" for a, b in front) +
                     f'" fill="none" stroke="{color}" stroke-width="{h * .035:.3f}" stroke-linecap="round" stroke-linejoin="round"/>')
        for a, b in front:
            parts.append(f'<circle cx="{a:.3f}" cy="{b:.3f}" r="{h * .045:.3f}" fill="{color}"/>')
    else:
        vals = [.45, .75, .55, .95]
        cols = [BLUE, RED, YELLOW, GREEN]
        bw = (w - 2 * pad) / (len(vals) * 1.6)
        for i, (v, c) in enumerate(zip(vals, cols)):
            bx = x0 + pad + bw * .5 + i * bw * 1.6
            bh = (h - 2 * pad) * v
            parts.append(f'<rect x="{bx:.3f}" y="{y0 + h - pad - bh:.3f}" width="{bw:.3f}" height="{bh:.3f}" rx="{bw * .15:.3f}" fill="{c}"/>')
    s.raw("".join(parts), depth=dep)


def floor_plan(s, ox, oy, scale=1.0, wall_h=.8, dep_base=0, shear=YELLOW, furniture=True):
    """一套住宅户型：彩色房间 + 墙体（黄色为剪力墙）"""
    S_ = scale
    rooms = [((0, 0, 4.5, 3.5), tint(YELLOW, .78)),
             ((4.5, 0, 3.5, 3.0), tint(BLUE, .82)),
             ((4.5, 3.0, 3.5, 3.0), tint(GREEN, .82)),
             ((0, 3.5, 2.4, 2.5), tint(RED, .84)),
             ((2.4, 3.5, 2.1, 2.5), tint(PURPLE, .85))]
    for (x, y, w, d), c in rooms:
        s.rect_top(ox + x * S_, oy + y * S_, .005, w * S_, d * S_, c, dep_base - 50)
    walls = [((0, 0), (2.6, 0), 1), ((2.6, 0), (8, 0), 0), ((8, 0), (8, 2.2), 1), ((8, 2.2), (8, 6), 0),
             ((0, 6), (8, 6), 0), ((0, 0), (0, 6), 0),
             ((4.5, 0), (4.5, 2.1), 1), ((4.5, 2.9), (4.5, 4.4), 0), ((4.5, 5.2), (4.5, 6), 0),
             ((4.5, 3), (6, 3), 0), ((6.8, 3), (8, 3), 0),
             ((0, 3.5), (1.2, 3.5), 0), ((2.0, 3.5), (3.2, 3.5), 0), ((3.9, 3.5), (4.5, 3.5), 0),
             ((2.4, 3.5), (2.4, 6), 1)]
    t = .2
    for (x0, y0), (x1, y1), sh in walls:
        x0, y0, x1, y1 = ox + x0 * S_, oy + y0 * S_, ox + x1 * S_, oy + y1 * S_
        if y0 == y1:
            bx, by, bw, bd = min(x0, x1) - t * S_ / 2, y0 - t * S_ / 2, abs(x1 - x0) + t * S_, t * S_
        else:
            bx, by, bw, bd = x0 - t * S_ / 2, min(y0, y1) - t * S_ / 2, t * S_, abs(y1 - y0) + t * S_
        s.box(bx, by, 0, bw, bd, wall_h * S_, shear if sh else WHITE, stroke=False, dep=dep_base + bx + by + bw / 2 + bd / 2)
    if furniture:
        f = [(5.0, .5, 1.6, 2.0, .35, WHITE), (5.0, .5, .5, 2.0, .5, tint(BLUE, .4)),      # 床
             (5.0, 3.6, 1.6, 2.0, .35, WHITE), (5.0, 3.6, .5, 2.0, .5, tint(GREEN, .4)),
             (.5, .6, .8, 2.4, .45, tint(YELLOW, .3)), (2.0, 1.2, 1.2, 1.1, .3, WHITE),      # 沙发、茶几
             (.3, 4.0, .6, 1.6, .7, WHITE), (2.8, 4.0, .7, .9, .45, WHITE)]
        for x, y, w, d, h, c in f:
            s.box(ox + x * S_, oy + y * S_, 0, w * S_, d * S_, h * S_, c, stroke=False,
                  dep=dep_base + ox + oy + (x + y + w / 2 + d / 2) * S_ - .3)


# ============================================================
# 研究方向（5 张）
# ============================================================
def dir_prefab():
    """装配式建筑：钢-混凝土混合框架 + 核心筒 + 吊装预制外墙板"""
    s = Scene()
    s.plate(-4.4, -2.0, 14.0, 12.0)
    W, D, fh, n = 6.0, 5.0, 1.6, 5
    xs, ys = [0, 3, 6], [0, 2.5, 5]
    s.shadow(-.2, -.2, W + .4, D + .4, opacity=.2)
    for k in range(n):
        z0 = k * fh
        L = k * 100
        if k >= 1:
            s.box(-.15, -.15, z0 - .14, W + .3, D + .3, .14, WHITE, dep=L - 10, faces=CONCRETE)
        s.box(2.0, 1.4, z0, 2.0, 2.2, fh - .14, WHITE, dep=L + 5.6, faces=CONCRETE)
        s.rect_left(2.6, 1.4, z0, .8, fh * .78, "#cdd0d7", L + 5.61)
        for cx in xs:
            for cy in ys:
                if (cx, cy) == (3, 2.5):
                    continue
                s.box(cx - .13, cy - .13, z0, .26, .26, fh - .14, STEEL, dep=L + cx + cy, stroke=False)
        for (a, b) in zip(xs, xs[1:]):
            for cy in (0, 5):
                s.box(a + .13, cy - .09, z0 + fh - .36, b - a - .26, .18, .22, STEEL, dep=L + a + cy + 1.4, stroke=False)
        for (a, b) in zip(ys, ys[1:]):
            for cx in (0, 6):
                s.box(cx - .09, a + .13, z0 + fh - .36, .18, b - a - .26, .22, STEEL, dep=L + cx + a + 1.4, stroke=False)
        # 低层已完成外墙板
        if k <= 1 or (k == 2):
            for bx in range(2):
                if k == 2 and bx == 1:
                    continue
                x0 = bx * 3 + .18
                s.box(x0, D + .1, z0 + .02, 2.64, .16, fh - .2, WHITE, dep=L + 60 + bx, stroke=True)
                s.rect_left(x0 + .35, D + .26, z0 + .4, 1.94, .7, WIN, L + 60.01 + bx)
            for by in range(2):
                y0 = by * 2.5 + .18
                if k == 2 and by == 1:
                    continue
                s.box(W + .1, y0, z0 + .02, .16, 2.14, fh - .2, WHITE, dep=L + 62 + by, stroke=True)
                s.rect_right(W + .26, y0 + .3, z0 + .4, 1.54, .7, mix(WIN, "#000000", .1), L + 62.01 + by)
    # 塔吊 + 正在吊装的预制外墙板（对准第 3 层左前方空位）
    mx_, my_ = -3.0, -1.2
    crane_y(s, mx_, my_, 10.6, 11.6)
    hx_, hy_ = mx_ + .22, D + 3.6
    px, py, pz = hx_ - 1.32, hy_ - .08, 2 * fh + 3.0
    s.box(px, py, pz, 2.64, .16, fh - .2, tint(BLUE, .55), dep=1000, stroke=False)
    s.rect_left(px + .35, py + .16, pz + .38, 1.94, .7, "#ffffff", 1000.01, 'fill-opacity=".75"')
    s.box(hx_ - .3, hy_ - .22, 10.6 - .16, .6, .45, .16, "#bdc1c6", dep=1001, stroke=False)
    s.line((hx_, hy_, 10.44), (hx_, hy_, pz + fh + .7), "#9aa0a6", .06, depth=1002)
    s.line((hx_, hy_, pz + fh + .7), (px + .3, hy_, pz + fh - .2), "#9aa0a6", .045, depth=1002)
    s.line((hx_, hy_, pz + fh + .7), (px + 2.34, hy_, pz + fh - .2), "#9aa0a6", .045, depth=1002)
    s.box(hx_ - .15, hy_ - .15, pz + fh + .7, .3, .3, .3, YELLOW, dep=1003, stroke=False)
    # 目标空位虚线框 + 引导线
    tx0 = 3.18
    s.outline([(tx0, D + .18, 2 * fh + .02), (tx0 + 2.64, D + .18, 2 * fh + .02), (tx0 + 2.64, D + .18, 3 * fh - .18), (tx0, D + .18, 3 * fh - .18)],
              BLUE, .06, 997, extra='stroke-dasharray=".16 .12"')
    s.polyline([(px + 2.64, py + .08, pz + .4), (tx0 + .1, D + .18, 2 * fh + .9)], BLUE, .06, 998, 'stroke-dasharray=".16 .14" opacity=".7"')
    # 地面构件堆放
    for i in range(3):
        s.box(6.6, 6.0, i * .18, 2.6, 1.0, .16, WHITE, dep=300 + i)
    s.box(4.4, 7.0, 0, .9, .9, .7, YELLOW, dep=300)
    return s


def dir_llm():
    """建造领域垂类大模型：AI 芯片 → 建筑质量与安全监管"""
    s = Scene()
    s.plate(-1.2, -1.2, 12.6, 9.6)
    # 被监管的建筑群
    building(s, 6.0, .2, 2.6, 2.6, 6.4, 8)
    building(s, 9.0, 1.2, 2.0, 2.0, 3.6, 4)
    building(s, 6.4, 3.8, 1.8, 1.6, 2.4, 3)
    # 芯片
    cx, cy = .4, 4.2
    s.shadow(cx, cy, 3.4, 3.4, opacity=.18)
    dep = s.box(cx, cy, 0, 3.4, 3.4, .4, WHITE)
    for i in range(6):
        s.box(cx + .35 + i * .48, cy + 3.4, .1, .22, .3, .12, "#bdc1c6", stroke=False, dep=dep + .1)
        s.box(cx + 3.4, cy + .35 + i * .48, .1, .3, .22, .12, "#aeb2b9", stroke=False, dep=dep + .1)
    s.rect_top(cx + .6, cy + .6, .401, 2.2, 2.2, RED, dep + .01)
    s.rect_top(cx + .8, cy + .8, .402, 1.8, 1.8, tint(RED, .12), dep + .011)
    for i in range(4):
        for j in range(4):
            s.dot(cx + 1.0 + i * .47, cy + 1.0 + j * .47, .403, .07, "#ffffff", dep + .02)
    # 数据走线
    traces = [[(cx + 3.7, cy + .8), (4.8, cy + .8), (4.8, 2.4), (5.9, 2.4)],
              [(cx + 3.7, cy + 1.7), (5.4, cy + 1.7), (5.4, 4.6), (6.3, 4.6)],
              [(cx + 3.7, cy + 2.6), (5.0, cy + 2.6), (5.0, 7.0), (8.6, 7.0), (8.6, 3.4), (9.0, 3.4)]]
    for tr in traces:
        s.polyline([(a, b, .01) for a, b in tr], tint(RED, .35), .07, -40)
        s.dot(tr[-1][0], tr[-1][1], .01, .11, RED, -39)
    # 对话气泡 + 监管通过徽章
    s.bubble(1.4, 5.2, 4.8, 5.4, 2.4, 1500, lines=3, accent=RED)
    s.shield(7.3, 1.5, 8.5, .95, RED, 1600)
    s.badge(10.0, 2.2, 5.0, .45, GREEN, 1601)
    hardhat(s, 3.2, 8.6, 0, .75, YELLOW, dep=300)
    return s


def dir_design():
    """智能设计：户型 / 剪力墙布置 + 风机塔筒 + 多目标优化"""
    s = Scene()
    s.plate(-1.2, -1.2, 14.0, 8.6)
    s.shadow(-.2, -.2, 8.4, 6.4, opacity=.14)
    floor_plan(s, 0, 0)
    turbine(s, 10.8, 2.2, 8.5)
    chart_card(s, 1.0, 1.2, 6.2, 4.6, 3.0, 2000, YELLOW, "pareto")
    return s


def dir_inspect():
    """智能检测：混凝土表面缺陷识别 + 三维激光扫描平整度验收"""
    s = Scene()
    s.plate(-1.2, -1.6, 13.0, 10.0)
    # 背面墙体（被扫描）
    s.box(0, -1.0, 0, 7.4, .5, 3.6, WHITE, dep=-20, faces=CONCRETE)
    rnd = random.Random(7)
    for i in range(26):
        for j in range(10):
            if rnd.random() < .82 and i < 22:
                u = .3 + i * .27 + rnd.uniform(-.05, .05)
                v = .35 + j * .3 + rnd.uniform(-.05, .05)
                s.dot(u, -.5, v, .055, GREEN if rnd.random() < .85 else YELLOW, -19.9, 'opacity=".85"')
    # 楼板（缺陷识别）
    s.shadow(0, 0, 7.4, 6.2, opacity=.16)
    dep = s.box(0, 0, 0, 7.4, 6.2, .5, WHITE, faces=CONCRETE)
    z = .501
    cracks = [[(.9, .9), (1.4, 1.3), (1.6, 2.0), (2.2, 2.3), (2.4, 3.0)],
              [(4.4, .7), (4.9, 1.0), (5.0, 1.5), (5.6, 1.9)],
              [(1.2, 4.3), (1.8, 4.6), (2.1, 5.3)]]
    for c in cracks:
        s.polyline([(a, b, z) for a, b in c], "#80868b", .06, dep + .02)
    boxes = [(.6, .6, 2.1, 2.7, GREEN), (4.1, .45, 1.8, 1.7, GREEN), (.9, 4.0, 1.5, 1.6, YELLOW)]
    for x, y, w, d, c in boxes:
        pts = [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)]
        s.outline(pts, c, .07, dep + .03, fill=c, extra='fill-opacity=".1"')
        s.rect_top(x, y - .0, z, .9, .32, c, dep + .031)
    # 平整度热力图
    rnd = random.Random(4)
    gx, gy, cell = 3.6, 3.2, .45
    for i in range(7):
        for j in range(6):
            v = rnd.random()
            c = tint(GREEN, .25) if v < .62 else (tint(GREEN, .55) if v < .82 else (YELLOW if v < .95 else RED))
            if (i, j) == (5, 1):
                c = RED
            s.rect_top(gx + i * cell + .02, gy + j * cell + .02, z, cell - .04, cell - .04, c, dep + .02, 'fill-opacity=".9"')
    # 扫描仪与扫描光线
    head = scanner(s, 8.9, 5.4, height=2.4)
    for tgt in [(.6, -.5, 3.2), (3.4, -.5, 3.5), (6.4, -.5, .5), (6.6, 4.4, .5), (3.7, 5.8, .5)]:
        s.line(head, tgt, GREEN, .04, depth=2000, dash=".18 .14", opacity=.55)
    s.badge(6.7, 1.4, 2.4, .42, GREEN, 2100)
    return s


def dir_robot():
    """建造机器人：天花面板安装机器人 + 预制构件 3D 打印"""
    s = Scene()
    s.plate(-1.2, -1.2, 13.0, 9.0)
    W, D, H = 6.0, 5.0, 4.0
    for cx, cy in [(0, 0), (W, 0), (0, D), (W, D)]:
        s.box(cx - .14, cy - .14, 0, .28, .28, H, WHITE, dep=cx + cy)
    # 吊顶龙骨网格 + 已装面板（后两排）
    cols, rows = 4, 4
    cw, rh = W / cols, D / rows
    for j in range(rows):
        for i in range(cols):
            if j <= 1 or (j == 2 and i in (0, 3)):
                s.box(i * cw + .04, j * rh + .04, H - .02, cw - .08, rh - .08, .08, "#f1f3f4", dep=800 + i + j, stroke=False,
                      faces=("#f1f3f4", "#dadce0", "#c7c9ce"))
    for j in range(rows + 1):
        s.box(0, j * rh - .04, H, W, .08, .08, "#bdc1c6", stroke=False, dep=810 + j * 2)
    for i in range(cols + 1):
        s.box(i * cw - .04, 0, H, .08, D, .08, "#aeb2b9", stroke=False, dep=811 + i * 2)
    # 机器人托举面板到空位 (i=1, j=2)
    ti, tj = 1, 2
    tx, ty = ti * cw + cw / 2, tj * rh + rh / 2
    tool = robot_arm(s, (4.6, 6.6), [(4.4, 5.8, 2.6), (tx + .25, ty + .5, 2.9), (tx, ty, 3.45)], PURPLE, dep=840)
    s.box(ti * cw + .1, tj * rh + .1, 3.5, cw - .2, rh - .2, .1, tint(PURPLE, .7), dep=845)
    s.line((tx, ty, 3.6), (tx, ty, H - .02), PURPLE, .04, depth=846, dash=".1 .1", opacity=.7)
    # 3D 打印预制构件
    gx, gy = 9.6, 2.6
    for px, py in [(gx - 1.6, gy - 1.4), (gx - 1.6, gy + 1.4)]:
        s.box(px - .12, py - .12, 0, .24, .24, 3.6, "#e8eaed", dep=px + py - 1, stroke=False)
    for px, py in [(gx + 1.6, gy - 1.4), (gx + 1.6, gy + 1.4)]:
        s.box(px - .12, py - .12, 0, .24, .24, 3.6, "#e8eaed", dep=px + py + 2, stroke=False)
    s.box(gx - 1.72, gy - 1.52, 3.6, 3.44, .24, .22, "#dadce0", dep=gx + gy + 2.5, stroke=False)
    s.box(gx - 1.72, gy + 1.28, 3.6, 3.44, .24, .22, "#dadce0", dep=gx + gy + 4.5, stroke=False)
    s.box(gx - .14, gy - 1.52, 3.62, .28, 3.04, .2, "#bdc1c6", dep=gx + gy + 4.6, stroke=False)
    s.box(gx - .3, gy - .3, 3.0, .6, .6, .6, PURPLE, dep=gx + gy + 4.7)
    s.cyl(gx, gy, 2.55, .08, .45, "#5f6368", dep=gx + gy + 4.65)
    layers = 14
    for k in range(layers):
        r = 1.0 + .18 * math.sin(k / layers * math.pi * 1.2)
        s.cyl(gx, gy, k * .16, r, .165, tint(PURPLE, .15 if k % 2 else .35), dep=gx + gy + k * .01,
              top=tint(PURPLE, .7))
    s.disc(gx, gy, layers * .16 + .001, .72, "#f1f3f4", gx + gy + layers * .01 + .001)
    s.shadow(gx - 1.1, gy - 1.1, 2.2, 2.2, opacity=.1)
    return s


# ============================================================
# 页面顶图
# ============================================================
def banner():
    """首页横幅：五个研究方向同框"""
    s = Scene()
    s.plate(-5.4, -1.8, 18.6, 11.2)
    w, d, h, g = 3.0, 2.4, 1.5, 0.08
    nx, ny, nz = 3, 2, 4
    s.shadow(0, 0, nx * w, ny * d, opacity=.22)
    missing = (2, 1, 3)
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                if (i, j, k) == missing or (k == 3 and (i, j) == (0, 0)):
                    continue
                s.box(i * w + g, j * d + g, k * h + g, w - 2 * g, d - 2 * g, h - 2 * g, WHITE, windows=WIN, dep=(i + j + k) * 1.0)
    lift = 1.8
    mx, my, mz = missing[0] * w + g, missing[1] * d + g, missing[2] * h + g + lift
    s.box(mx, my, mz, w - 2 * g, d - 2 * g, h - 2 * g, BLUE, windows="#aecbfa", dep=50)
    cx, cy = -1.0, -0.6
    crane(s, cx, cy, 9.6, 10.6)
    hookx, hooky = mx + (w - 2 * g) / 2, my + (d - 2 * g) / 2
    hook_lines(s, hookx, cy + .22, 9.6, (mx, my, w - 2 * g, d - 2 * g), mz + h - 2 * g, 60)
    # 智能设计：地面上的户型图纸
    s.rect_top(-4.9, 4.6, .01, 5.4, 4.2, "#ffffff", -60, 'stroke="#dadce0" stroke-width=".04"')
    floor_plan(s, -4.5, 4.95, scale=.58, wall_h=.55, dep_base=-55, furniture=False)
    # 建造机器人
    robot_arm(s, (3.6, 7.6), [(3.3, 6.8, 2.2), (2.6, 5.6, 2.7), (2.4, 5.2, 2.2)], PURPLE, dep=200)
    s.box(1.7, 4.8, 1.95, 1.6, .9, .12, WHITE, dep=201)
    # 智能检测
    head = scanner(s, 11.4, 6.6, dep=210, height=2.2)
    for tgt in [(9.0, 2.0, 5.0), (9.0, 4.8, 1.2), (5.0, 4.8, 3.0), (9.0, .6, 3.0)]:
        s.line(head, tgt, GREEN, .045, depth=220, dash=".2 .15", opacity=.55)
    # 垂类大模型
    s.bubble(-2.6, 1.6, 5.4, 4.8, 2.2, 1500, lines=3, accent=RED)
    s.shield(-2.6 + 3.4, 1.6 - 3.4, 5.9, .7, RED, 1501)
    # 物料
    for n, (c, (px, py)) in enumerate(zip([RED, YELLOW, GREEN], [(10.2, 1.0), (10.2, 2.1), (11.3, 1.0)])):
        s.shadow(px, py, .9, .9, opacity=.15, grow=.15)
        s.box(px, py, 0, .9, .9, .7, c, dep=20 + n)
    s.box(10.2, 1.0, .7, .9, .9, .7, PURPLE, dep=25)
    hardhat(s, 6.4, 8.0, 0, .6, YELLOW, dep=230)
    return s


def bridge_twin():
    """研究方向页：桥梁与其数字孪生（感知 → 孪生模型）"""
    s = Scene()
    # 实体桥：地面 + 河道
    s.plate(-1.0, -1.0, 13.0, 4.6)
    s.rect_top(-1.0, .2, .001, 13.0, 1.6, tint(BLUE, .72), -900)
    span = [(0, 3.2), (3.2, 8.8), (8.8, 12.0)]
    for px in (3.2, 8.8):
        s.cyl(px, 1.0, 0, .42, 2.4, WHITE, dep=px + 1)
        s.box(px - .7, .3, 2.2, 1.4, 1.4, .3, WHITE, dep=px + 1.2, faces=CONCRETE)
    s.box(-.6, .2, 0, 1.0, 1.6, 2.5, WHITE, dep=-1, faces=CONCRETE)
    s.box(11.6, .2, 0, 1.0, 1.6, 2.5, WHITE, dep=13, faces=CONCRETE)
    s.box(-.6, .2, 2.5, 13.2, 1.6, .45, WHITE, dep=20)
    for i in range(14):
        s.box(-.5 + i * .95, 1.66, 2.95, .06, .06, .45, "#bdc1c6", dep=21 + i * .01, stroke=False)
    s.box(-.6, 1.68, 3.35, 13.2, .06, .06, "#bdc1c6", dep=21.5, stroke=False)
    for x, y, c in [(2.2, .5, BLUE), (7.4, 1.0, RED), (4.6, .5, WHITE)]:
        s.box(x, y, 2.95, 1.0, .45, .32, c, dep=21.2 + x * .01, stroke=False)
        s.box(x + .2, y + .03, 3.27, .55, .39, .2, tint(c, .5) if c != WHITE else "#e8eaed", dep=21.21 + x * .01, stroke=False)
    sensors = [(1.6, 1.8), (6.0, 1.8), (10.4, 1.8)]
    for x, y in sensors:
        s.dot(x, y, 2.75, .14, RED, 22, 'stroke="#fff" stroke-width=".05"')
    # 孪生模型（右前方）
    oy = 6.0
    s.plate(-1.0, oy - 1.0, 13.0, 4.6, color="#e8f0fe")
    for i in range(14):
        s.line((-1.0 + i, oy - 1.0, .001), (-1.0 + i, oy + 3.6, .001), "#d2e3fc", .03, depth=-800)
    for j in range(5):
        s.line((-1.0, oy - 1.0 + j * 1.15, .001), (12.0, oy - 1.0 + j * 1.15, .001), "#d2e3fc", .03, depth=-800)
    for px in (3.2, 8.8):
        s.wire_box(px - .35, oy + .65, 0, .7, .7, 2.2, BLUE, depth=px + oy)
    s.wire_box(-.6, oy + .2, 0, 1.0, 1.6, 2.5, BLUE, depth=oy - 1)
    s.wire_box(11.6, oy + .2, 0, 1.0, 1.6, 2.5, BLUE, depth=oy + 13)
    s.wire_box(-.6, oy + .2, 2.5, 13.2, 1.6, .45, BLUE, depth=oy + 20, fill_opacity=.16)
    # 应力云图色带
    cols = [GREEN, GREEN, YELLOW, RED, YELLOW, GREEN, GREEN, YELLOW, GREEN]
    seg = 13.2 / len(cols)
    for i, c in enumerate(cols):
        s.on_left(oy + 1.8, [(-.6 + i * seg, 2.5), (-.6 + (i + 1) * seg, 2.5), (-.6 + (i + 1) * seg, 2.95), (-.6 + i * seg, 2.95)],
                  c, oy + 30, 'fill-opacity=".55"')
    # 数据流
    for x, y in sensors:
        s.line((x, y, 2.75), (x, oy + .9, 3.4), RED, .05, depth=1500, dash=".16 .14", opacity=.7)
        s.dot(x, oy + .9, 3.4, .14, RED, 1501, 'stroke="#fff" stroke-width=".05"')
    s.badge(12.4, oy + 1.0, 4.6, .5, BLUE, 1600)
    return s


def papers_scene():
    """论文页：论文与图表（缺陷识别图 + 户型图 + 柱状图）"""
    s = Scene()
    pw, pd = 7.0, 9.0
    s.shadow(0, 0, pw, pd, opacity=.18, grow=.4)
    for k in range(5):
        off = (k % 2) * .2 - .1
        s.box(off, -off, k * .14, pw, pd, .12, WHITE, depth_bias=k)
    z0 = 5 * .14 + .002
    dep = 200
    s.rect_top(.7, .6, z0, 4.2, .5, INK, dep)
    for r in range(3):
        s.rect_top(.7, 1.45 + r * .42, z0, 5.4 - (r % 2) * 1.6, .16, "#dadce0", dep)
    # 图 a：混凝土缺陷识别
    ax, ay = .7, 3.1
    s.rect_top(ax, ay, z0, 2.7, 2.7, "#e8eaed", dep)
    s.on_top(z0, [(ax + .3, ay + .4), (ax + .9, ay + .9), (ax + 1.0, ay + 1.6), (ax + 1.7, ay + 2.0), (ax + 1.9, ay + 2.4),
                  (ax + 1.85, ay + 2.45), (ax + 1.65, ay + 2.05), (ax + .95, ay + 1.65), (ax + .85, ay + .95), (ax + .25, ay + .45)],
             "#80868b", dep + .01)
    s.outline([(ax + .15, ay + .25, z0), (ax + 2.1, ay + .25, z0), (ax + 2.1, ay + 2.6, z0), (ax + .15, ay + 2.6, z0)], GREEN, .07, dep + .02)
    s.rect_top(ax + .15, ay + .25, z0, .8, .25, GREEN, dep + .021)
    # 图 b：户型布局
    bx, by = 3.8, 3.1
    for (x, y, w, d), c in [((0, 0, 1.6, 1.3), tint(YELLOW, .5)), ((1.6, 0, 1.0, 1.3), tint(BLUE, .6)),
                            ((0, 1.3, 1.0, 1.4), tint(RED, .6)), ((1.0, 1.3, 1.6, 1.4), tint(GREEN, .6))]:
        s.rect_top(bx + x, by + y, z0, w - .06, d - .06, c, dep)
    # 图 c：柱状图（立起来）
    for i, (c, hh) in enumerate(zip([BLUE, RED, YELLOW, GREEN], [1.4, 2.3, 1.0, 1.9])):
        s.box(1.0 + i * 1.3, 6.6, z0, .75, 1.6, hh, c, depth_bias=300 + i)
    for r in range(2):
        s.rect_top(.7, 8.35 + r * .32, z0, 5.0 - r * 1.8, .14, "#dadce0", dep)
    # 引用徽标
    s.badge(7.4, -.4, 3.0, .6, BLUE, 2000, icon="star")
    return s


def team_scene():
    """团队页：围着建筑模型讨论的团队 + 屏幕上的户型"""
    s = Scene()
    s.plate(-6.2, -6.2, 10.6, 10.6, color="#ececf0")
    s.disc(0, 0, .001, 3.0, "#e3e3e8", -500)
    # 桌子
    s.cyl(0, 0, 0, .35, 1.0, "#dadce0", dep=0)
    s.cyl(0, 0, 1.0, 2.0, .16, WHITE, dep=.1)
    # 桌上模型
    for i, (x, y, h, c) in enumerate([(-.9, -.7, 1.4, WHITE), (.1, -.8, 2.0, WHITE), (-.6, .3, .9, BLUE), (.3, .2, 1.2, WHITE)]):
        s.box(x, y, 1.16, .7, .7, h, c, windows=WIN if c == WHITE else "#aecbfa", dep=1 + x + y + i * .01)
    # 背后屏幕
    sx, sy = -4.6, -5.4
    s.box(sx, sy, 0, .2, .2, 2.4, "#bdc1c6", dep=-10, stroke=False)
    s.box(sx - 1.6, sy - .05, 2.4, 3.4, .14, 2.2, "#3c4043", dep=-9, stroke=False)
    fx = sx - 1.45
    for (x, z, w, h, c) in [(0, 0, 1.4, 1.0, tint(YELLOW, .3)), (1.4, 0, 1.6, 1.0, tint(BLUE, .4)),
                            (0, 1.0, 1.0, .9, tint(RED, .4)), (1.0, 1.0, 2.0, .9, tint(GREEN, .4))]:
        s.rect_left(fx + x + .04, sy + .09, 2.55 + z + .04, w - .08, h - .08, c, -8.9)
    # 团队
    people = [(2.6, .4, BLUE), (1.6, 2.4, RED), (-.6, 2.8, YELLOW), (-2.7, 1.2, GREEN), (2.3, -1.9, PURPLE), (-2.4, -1.6, BLUE)]
    for x, y, c in people:
        s.person(x, y, c, scale=1.1)
    s.bubble(2.8, -1.2, 4.3, 3.0, 1.35, 3000, lines=2, accent=GREEN, tail="left")
    return s


BOOKS = [  # 与 data/books.yaml 顺序一致
    ("dl", BLUE),     # 深度学习在建筑工程中的应用
    ("epc", RED),     # 装配式建筑 EPC 项目管理
    ("ic", GREEN),    # 建筑智能建造技术初探及其应用
    ("cfd", YELLOW),  # 风荷载的 CFD 数值模拟
]


def cover_icon(kind, cx, cy, sz, color="#ffffff", sw=None):
    """书封面图标（屏幕坐标，白色线描）"""
    sw = sw or sz * .07
    st = f'stroke="{color}" stroke-width="{sw:.3f}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    if kind == "dl":   # 神经网络
        layers = [3, 4, 2]
        pts = []
        for li, n in enumerate(layers):
            x = cx - sz * .55 + li * sz * .55
            col = [(x, cy - sz * .45 * (n - 1) / 3 + j * sz * .9 / 3) for j in range(n)]
            pts.append(col)
        out = []
        for a, b in zip(pts, pts[1:]):
            for p in a:
                for q in b:
                    out.append(f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" {st} opacity=".7"/>')
        for col in pts:
            for p in col:
                out.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{sz * .1:.2f}" fill="{color}"/>')
        return "".join(out)
    if kind == "epc":  # 模块化建筑（等轴测小楼）
        a = sz * .32
        out = []
        for (i, j, k) in [(0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1), (0, 0, 2)]:
            ox = cx + (i - j) * a * C - a * .45
            oy = cy + (i + j) * a * S - k * a + a * .9
            top = f"{ox:.2f},{oy - a:.2f} {ox + a * C:.2f},{oy - a + a * S:.2f} {ox:.2f},{oy - a + 2 * a * S:.2f} {ox - a * C:.2f},{oy - a + a * S:.2f}"
            out.append(f'<polygon points="{top}" {st}/>')
            out.append(f'<path d="M{ox - a * C:.2f},{oy - a + a * S:.2f} v{a:.2f} L{ox:.2f},{oy + 2 * a * S:.2f} L{ox + a * C:.2f},{oy + a * S:.2f} v{-a:.2f} M{ox:.2f},{oy - a + 2 * a * S:.2f} v{a:.2f}" {st}/>')
        return "".join(out)
    if kind == "ic":   # 塔吊
        x0, y0 = cx - sz * .25, cy + sz * .7
        return (f'<path d="M{x0:.2f},{y0:.2f} V{cy - sz * .7:.2f} M{x0 - sz * .35:.2f},{cy - sz * .6:.2f} H{cx + sz * .7:.2f} '
                f'M{x0:.2f},{cy - sz * .7:.2f} L{x0 - sz * .3:.2f},{cy - sz * .6:.2f} M{x0:.2f},{cy - sz * .9:.2f} L{cx + sz * .5:.2f},{cy - sz * .6:.2f} '
                f'M{x0:.2f},{cy - sz * .9:.2f} V{cy - sz * .7:.2f} M{cx + sz * .45:.2f},{cy - sz * .6:.2f} V{cy + sz * .05:.2f} '
                f'M{x0 - sz * .3:.2f},{y0:.2f} H{x0 + sz * .3:.2f}" {st}/>'
                f'<rect x="{cx + sz * .3:.2f}" y="{cy + sz * .05:.2f}" width="{sz * .3:.2f}" height="{sz * .22:.2f}" fill="{color}"/>'
                + "".join(f'<path d="M{x0 - sz * .12:.2f},{y0 - k * sz * .3:.2f} L{x0:.2f},{y0 - (k + 1) * sz * .3:.2f} M{x0 + sz * .12:.2f},{y0 - k * sz * .3:.2f} L{x0:.2f},{y0 - (k + 1) * sz * .3:.2f}" {st} opacity=".6"/>' for k in range(4)))
    if kind == "cfd":  # 建筑绕流流线
        bw, bh = sz * .32, sz * .7
        out = []
        for k, dy in enumerate([-.95, -.72, -.49]):
            y = cy + dy * sz
            bump = (.42 - abs(dy + .1) * .5) * sz
            out.append(f'<path d="M{cx - sz * .9:.2f},{y:.2f} C{cx - sz * .35:.2f},{y:.2f} {cx - sz * .3:.2f},{y - bump:.2f} {cx:.2f},{y - bump:.2f} '
                       f'S{cx + sz * .4:.2f},{y + sz * .02:.2f} {cx + sz * .9:.2f},{y + sz * .05:.2f}" {st} opacity="{.95 - k * .12:.2f}"/>')
        out.append(f'<rect x="{cx - bw / 2:.2f}" y="{cy - sz * .42:.2f}" width="{bw:.2f}" height="{bh:.2f}" fill="{color}"/>')
        return "".join(out)
    return ""


def books_scene():
    """专著页：四本书立在书架上，封面对应各自主题"""
    s = Scene()
    s.plate(-1.0, -1.0, 11.0, 5.0)
    bh, bw = 5.4, 3.6   # 高、封面宽（沿 x）
    xs = [0, 2.35, 4.7, 7.05]
    thick = [.9, .75, 1.0, .65]
    for i, ((kind, c), x) in enumerate(zip(BOOKS, xs)):
        t = thick[i]
        y = 1.2 - t
        lean = 0
        dep = 100 + i * 10
        top, left, right = shades(c)
        s.shadow(x, y, bw * .55, t, opacity=.15, grow=.2)
        # 书：沿 y 的厚度，封面在左面（y = y + t），书脊在右面
        s.box(x, y, 0, 2.0, t, bh, c, dep=dep, faces=(tint("#ffffff", 0), left, right), stroke=False)
        # 纸页（顶面）
        s.rect_top(x + .08, y + .08, bh, 1.84, t - .16, "#ffffff", dep + .01)
        for k in range(1, 4):
            s.line((x + .08, y + .08 + (t - .16) * k / 4, bh + .001), (x + 1.92, y + .08 + (t - .16) * k / 4, bh + .001), "#e3e3e8", .02, depth=dep + .02)
        # 封面图标
        cx, cy = s.p(x + 1.0, y + t, bh * .6)
        s.raw(cover_icon(kind, cx, cy, .82, "#ffffff", .06), depth=dep + .05)
        s.rect_left(x + .3, y + t, bh * .18, 1.4, .1, "#ffffff", dep + .04, 'fill-opacity=".8"')
        s.rect_left(x + .3, y + t, bh * .18 - .25, .9, .08, "#ffffff", dep + .04, 'fill-opacity=".55"')
        # 书脊标签
        s.rect_right(x + 2.0, y + .15, bh * .7, t - .3, .5, "#ffffff", dep + .04, 'fill-opacity=".7"')
    return s


def awards_scene():
    """奖励页：领奖台 + 奖杯 + 示范工程模型 + BIM 奖证书"""
    s = Scene()
    s.plate(-1.2, -1.2, 11.4, 5.6)
    steps = [(0, 2.2, GREEN), (3, 3.4, YELLOW), (6, 1.5, BLUE)]
    for x, hh, c in steps:
        s.shadow(x, 0, 3, 3, opacity=.14, grow=.2)
        s.box(x, 0, 0, 3, 3, hh, WHITE, dep=x)
        s.box(x, 0, hh, 3, 3, .22, c, dep=x + .1)
    # 冠军台：奖杯
    tx, ty, tz = 4.5, 1.5, 3.62
    s.cyl(tx, ty, tz, .55, .3, "#5f6368", dep=10)
    s.cyl(tx, ty, tz + .3, .14, .7, YELLOW, dep=10.1)
    s.cyl(tx, ty, tz + 1.0, .62, 1.0, YELLOW, dep=10.2, top=mix(YELLOW, "#000000", .15))
    cx, cy = s.p(tx, ty, tz + 1.55)
    s.raw(f'<path d="M{cx - .75:.2f},{cy - .4:.2f} C{cx - 1.3:.2f},{cy - .4:.2f} {cx - 1.2:.2f},{cy + .45:.2f} {cx - .62:.2f},{cy + .4:.2f}" fill="none" stroke="{YELLOW}" stroke-width=".14"/>'
          f'<path d="M{cx + .75:.2f},{cy - .4:.2f} C{cx + 1.3:.2f},{cy - .4:.2f} {cx + 1.2:.2f},{cy + .45:.2f} {cx + .62:.2f},{cy + .4:.2f}" fill="none" stroke="{mix(YELLOW, "#000000", .1)}" stroke-width=".14"/>'
          + star(cx, cy + .1, .32), depth=10.3, bbox=[(cx - 1.3, cy - .5)])
    # 亚军台：示范工程楼模型
    for i, (x, y, h) in enumerate([(.5, .5, 1.6), (1.6, .5, 2.4), (.5, 1.6, 1.0), (1.6, 1.6, 1.4)]):
        s.box(x, y, 2.42, .9, .9, h, WHITE if i != 1 else BLUE, windows=WIN if i != 1 else "#aecbfa", dep=5 + x + y)
    # 季军台：证书
    s.box(6.6, 1.2, 1.72, 1.8, .14, 1.6, WHITE, dep=12)
    s.rect_left(6.8, 1.34, 2.95, 1.4, .12, "#dadce0", 12.01)
    s.rect_left(6.8, 1.34, 2.7, 1.0, .1, "#dadce0", 12.01)
    s.rect_left(6.8, 1.34, 2.45, 1.2, .1, "#dadce0", 12.01)
    s.badge(7.95, 1.34, 2.05, .26, RED, 12.02, icon="star")
    s.box(7.6, 1.0, 1.72, .2, .3, .5, "#bdc1c6", dep=11.9, stroke=False)
    return s


def cv_scene():
    """履历页：逐级上升的台阶，每级一段经历"""
    s = Scene()
    s.plate(-1.0, -1.0, 13.0, 5.0)
    # 哈工大设计院 → 万达 → 中科大业 → 华姿建设 → 重庆大学
    n, sw = 5, 2.2
    for i in range(n):
        hh = .6 + i * .6
        s.shadow(i * sw, 0, sw, 3, opacity=.12, grow=.15)
        s.box(i * sw, 0, 0, sw, 3, hh, WHITE, dep=i * 10)
        s.rect_left(i * sw + .25, 3, hh - .32, .5, .14, [BLUE, RED, YELLOW, GREEN, BLUE][i], i * 10 + .01)
    z = lambda i: .6 + i * .6
    d0 = 1000
    # 1 设计院：办公楼
    s.box(.5, .7, z(0), 1.1, 1.1, 1.6, WHITE, windows=WIN, dep=d0 + 1)
    s.box(.5 + .3, .7 + .3, z(0) + 1.6, .5, .5, .2, BLUE, dep=d0 + 1.1)
    # 2 万达：商业综合体
    x = sw
    s.box(x + .2, .5, z(1), 1.8, 1.6, .9, WHITE, windows=WIN, dep=d0 + 2)
    s.box(x + .5, .8, z(1) + .9, .9, .9, 1.0, WHITE, windows=WIN, dep=d0 + 2.1)
    s.box(x + .2, 2.1, z(1) + .7, 1.8, .1, .2, RED, dep=d0 + 2.2, stroke=False)
    # 3 中科大业：预制构件工厂（锯齿屋面）
    x = 2 * sw
    s.box(x + .2, .5, z(2), 1.8, 1.6, .8, WHITE, dep=d0 + 3)
    for k in range(3):
        s.on_left(2.1, [(x + .2 + k * .6, z(2) + .8), (x + .8 + k * .6, z(2) + .8), (x + .8 + k * .6, z(2) + 1.25)], YELLOW, d0 + 3.1)
        s.on_left(2.1 - 1.6, [(x + .2 + k * .6, z(2) + .8), (x + .8 + k * .6, z(2) + .8), (x + .8 + k * .6, z(2) + 1.25)], YELLOW, d0 + 2.9)
        s.poly([(x + .2 + k * .6, .5, z(2) + .8), (x + .8 + k * .6, .5, z(2) + 1.25), (x + .8 + k * .6, 2.1, z(2) + 1.25), (x + .2 + k * .6, 2.1, z(2) + .8)],
               tint(YELLOW, .3), d0 + 3.05)
    s.rect_left(x + .5, 2.1, z(2) + .1, 1.0, .45, WIN, d0 + 3.2)
    # 4 华姿建设：小塔吊 + 在建楼
    x = 3 * sw
    s.box(x + .9, .7, z(3), 1.0, 1.0, 1.1, WHITE, windows=WIN, dep=d0 + 4)
    s.box(x + .35, .5, z(3), .14, .14, 2.3, GREEN, dep=d0 + 3.9, stroke=False)
    s.box(x + .0, .5, z(3) + 2.3, 1.9, .14, .12, GREEN, dep=d0 + 4.2, stroke=False)
    s.line((x + 1.6, .57, z(3) + 2.3), (x + 1.6, .57, z(3) + 1.5), "#9aa0a6", .03, depth=d0 + 4.3)
    s.box(x + 1.45, .45, z(3) + 1.3, .3, .3, .2, YELLOW, dep=d0 + 4.4, stroke=False)
    # 5 重庆大学：学院楼 + 旗
    x = 4 * sw
    s.box(x + .2, .4, z(4), 1.8, 1.4, 1.0, WHITE, dep=d0 + 5)
    for k in range(4):
        s.rect_left(x + .35 + k * .42, 1.8, z(4) + .1, .14, .75, "#d0d4dc", d0 + 5.01)
    s.poly([(x + .2, 1.8, z(4) + 1.0), (x + 2.0, 1.8, z(4) + 1.0), (x + 1.1, 1.8, z(4) + 1.5)], BLUE, d0 + 5.02)
    s.poly([(x + .2, .4, z(4) + 1.0), (x + 1.1, .4, z(4) + 1.5), (x + 1.1, 1.8, z(4) + 1.5), (x + .2, 1.8, z(4) + 1.0)], tint(BLUE, .25), d0 + 5.015)
    s.poly([(x + 1.1, .4, z(4) + 1.5), (x + 2.0, .4, z(4) + 1.0), (x + 2.0, 1.8, z(4) + 1.0), (x + 1.1, 1.8, z(4) + 1.5)], mix(BLUE, "#000000", .1), d0 + 5.016)
    fx, fy = x + 1.9, 2.5
    s.line((fx, fy, z(4)), (fx, fy, z(4) + 2.4), "#9aa0a6", .05, depth=d0 + 6)
    s.on_right(fx, [(fy, z(4) + 2.4), (fy - .9, z(4) + 2.05), (fy, z(4) + 1.7)], RED, d0 + 6.1)
    # 连接虚线（职业路径）
    path = [(1.05, 1.25, z(0) + 1.9), (x - 3 * sw + 1.1, 1.3, z(1) + 2.1), (2 * sw + 1.1, 1.3, z(2) + 1.6), (3 * sw + 1.4, 1.2, z(3) + 1.5), (4 * sw + 1.1, 1.1, z(4) + 1.8)]
    s.polyline([(a, b, c + .5) for a, b, c in path], BLUE, .05, d0 + 10, 'stroke-dasharray=".14 .14" opacity=".6"')
    for p in path:
        s.dot(p[0], p[1], p[2] + .5, .1, BLUE, d0 + 10.1)
    return s


# ============================================================
# 书封面（平面，竖版）
# ============================================================
def book_cover(kind, color, W=360, H=600):
    dark = mix(color, "#000000", .14)
    icon = cover_icon(kind, W * .5, H * .4, W * .28, "#ffffff", W * .018)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{color}"/>
<rect width="{W * .07:.1f}" height="{H}" fill="{dark}"/>
<rect x="{W * .07:.1f}" width="{W * .012:.1f}" height="{H}" fill="#ffffff" opacity=".18"/>
{icon}
</svg>'''


# ============================================================
OUTPUTS = {
    # 名称: (函数, 宽, 高, 留白, 白底?)
    "banner": (banner, 2400, 1400, .04, False),
    "tile-research": (banner, 1200, 900, .06, True),
    "tile-papers": (papers_scene, 1200, 900, .14, True),
    "tile-people": (team_scene, 1200, 900, .1, True),
    "hero-research": (bridge_twin, 1600, 1200, .08, False),
    "hero-publications": (papers_scene, 1600, 1200, .12, False),
    "hero-team": (team_scene, 1600, 1200, .08, False),
    "hero-books": (books_scene, 1600, 1200, .14, False),
    "hero-awards": (awards_scene, 1600, 1200, .12, False),
    "hero-cv": (cv_scene, 1600, 1200, .1, False),
    "dir-1": (dir_prefab, 1200, 900, .07, True),
    "dir-2": (dir_llm, 1200, 900, .07, True),
    "dir-3": (dir_design, 1200, 900, .07, True),
    "dir-4": (dir_inspect, 1200, 900, .07, True),
    "dir-5": (dir_robot, 1200, 900, .07, True),
}

if __name__ == "__main__":
    out = sys.argv[1]
    only = sys.argv[2:]
    os.makedirs(out, exist_ok=True)
    for name, (fn, W, H, pad, white) in OUTPUTS.items():
        if only and name not in only:
            continue
        # 研究方向卡片是浅灰底，配图用同色底；首页入口卡是白底
        bg = "#f5f5f7" if name.startswith("dir-") else ("#ffffff" if white else "url(#bgg)")
        svg = fn().svg(W, H, pad=pad, bg=bg)
        open(os.path.join(out, name + ".svg"), "w").write(svg)
    for i, (kind, color) in enumerate(BOOKS, 1):
        if only and f"book-{i}" not in only:
            continue
        open(os.path.join(out, f"book-{i}.svg"), "w").write(book_cover(kind, color))
    print("ok")
