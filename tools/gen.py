import math, random, os

ROOT = "/home/claude/stereo/project"
os.makedirs(ROOT, exist_ok=True)

PANEL = "#26313b"; LABEL = "#e1e6ea"; DIM = "#a6b1bb"
CREAM = "#efe7d0"; INK = "#1b2127"
TRACE = "#9be36a"; HOT = "#ffe24d"; SIDE = "#5cc8ff"; AMBER = "#ffb23e"
FONT = "'Barlow Condensed', sans-serif"; MONO = "'Share Tech Mono', monospace"

_uid = [0]
def uid():
    _uid[0] += 1
    return f"g{_uid[0]}"

def f(v): return f"{v:.1f}"

# ---------------------------------------------------------------- knobs
def knob(R, val, name, labels=None, kind="knurl", skirt=False, ndots=13, aria=None, lit=None, namesize=13):
    pad = 34 if labels else 15
    S = 2 * (R + pad); c = S / 2
    g = uid()
    p = []
    p.append(f'<defs><radialGradient id="{g}c" cx="40%" cy="35%" r="75%"><stop offset="0" style="stop-color:#e4e8eb"/><stop offset="1" style="stop-color:#8f979e"/></radialGradient>'
             f'<linearGradient id="{g}s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" style="stop-color:#f6f8f9"/><stop offset="0.45" style="stop-color:#8b9399"/><stop offset="0.7" style="stop-color:#5d656c"/><stop offset="1" style="stop-color:#d5dade"/></linearGradient>'
             f'<radialGradient id="{g}b" cx="40%" cy="35%" r="75%"><stop offset="0" style="stop-color:#6aa2f5"/><stop offset="1" style="stop-color:#1f55b3"/></radialGradient></defs>')
    # dot scale
    for i in range(ndots):
        fr = i / (ndots - 1)
        a = math.radians(-135 + 270 * fr - 90)
        rr = R + 9
        col = "#e3e8ec"
        if lit is not None and fr <= val + 1e-6:
            col = lit
        p.append(f'<circle cx="{f(c + rr*math.cos(a))}" cy="{f(c + rr*math.sin(a))}" r="2.6" fill="{col}"/>')
    if labels:
        for fr, t in labels:
            a = math.radians(-135 + 270 * fr - 90)
            rr = R + 24
            x = c + rr * math.cos(a); y = c + rr * math.sin(a) + 4
            p.append(f'<text x="{f(x)}" y="{f(y)}" fill="{DIM}" style="font-family:{FONT};font-size:12px;font-weight:600;text-anchor:middle">{t}</text>')
    ang = -135 + 270 * val
    if kind == "chicken" or kind == "blue":
        fill = f"url(#{g}b)" if kind == "blue" else f"url(#{g}c)"
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R*0.92)}" fill="#1c2329" stroke="#0e1216"/>')
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R*0.62)}" fill="{fill}" stroke="#2b3238"/>')
        w = R * 0.42; L = R * 1.0
        p.append(f'<g transform="rotate({f(ang)} {f(c)} {f(c)})">'
                 f'<path d="M {f(c-w/2)} {f(c+L*0.85)} L {f(c-w*0.38)} {f(c-L)} Q {f(c)} {f(c-L-6)} {f(c+w*0.38)} {f(c-L)} L {f(c+w/2)} {f(c+L*0.85)} Q {f(c)} {f(c+L*0.95)} {f(c-w/2)} {f(c+L*0.85)} Z" fill="{fill}" stroke="#0f1418" style="stroke-width:1.2"/>'
                 f'<line x1="{f(c)}" y1="{f(c-L+3)}" x2="{f(c)}" y2="{f(c-L*0.3)}" stroke="#ffffff" style="stroke-width:3;stroke-linecap:round"/></g>')
    else:
        rk = R
        if skirt:
            p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R)}" fill="url(#{g}s)" stroke="#20272d" style="stroke-width:1.5"/>')
            # skirt pointer
            a = math.radians(ang - 90)
            p.append(f'<line x1="{f(c+R*0.74*math.cos(a))}" y1="{f(c+R*0.74*math.sin(a))}" x2="{f(c+R*0.98*math.cos(a))}" y2="{f(c+R*0.98*math.sin(a))}" stroke="#111" style="stroke-width:3"/>')
            rk = R * 0.7
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(rk)}" fill="#7d858c" stroke="#1d2328" style="stroke-width:1.5"/>')
        circ = 2 * math.pi * (rk - 2)
        dash = circ / 96
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(rk-2)}" fill="none" stroke="#d9dee2" style="stroke-width:3.5;stroke-dasharray:{dash:.2f} {dash:.2f}"/>')
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(rk*0.8)}" fill="url(#{g}c)" stroke="#5c646b"/>')
        a = math.radians(ang - 90)
        p.append(f'<line x1="{f(c+rk*0.45*math.cos(a))}" y1="{f(c+rk*0.45*math.sin(a))}" x2="{f(c+rk*0.95*math.cos(a))}" y2="{f(c+rk*0.95*math.sin(a))}" stroke="#ffffff" style="stroke-width:3;stroke-linecap:round"/>')
    aria = aria or name
    svg = f'<svg role="img" aria-label="{aria}" width="{int(S)}" height="{int(S)}" viewBox="0 0 {int(S)} {int(S)}">' + "".join(p) + '</svg>'
    lab = f'<div style="margin-top: -10px; font-family: {FONT}; font-weight: 600; font-size: {namesize}px; letter-spacing: 0.08em; color: {LABEL}; text-transform: uppercase; text-align: center">{name}</div>' if name else ""
    return f'<div style="display: flex; flex-direction: column; align-items: center">{svg}{lab}</div>'

# ---------------------------------------------------------------- buttons
LEDS = {"green": ("#62e86d", True), "amber": (AMBER, True), "red": ("#ff5a4a", True), "off": ("#3b2424", False), "offg": ("#26382a", False)}
def led(state):
    col, glow = LEDS[state]
    sh = f"box-shadow: 0 0 8px {col}" if glow else "box-shadow: inset 0 1px 2px #000"
    return f'<span aria-hidden="true" style="width: 8px; height: 24px; border-radius: 2px; background: {col}; {sh}; flex-shrink: 0"></span>'

def btn(text, state="off", small=False):
    fs = 14 if small else 15
    return (f'<button type="button" style="display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 10px; background: {CREAM}; border: 1px solid #5f5848; border-radius: 3px; box-shadow: inset 0 -3px 0 #cfc5a8, inset 0 1px 0 #fffaf0; font-family: {FONT}; font-weight: 700; font-size: {fs}px; letter-spacing: 0.05em; color: {INK}; cursor: pointer; text-transform: uppercase">'
            f'{led(state)}<span style="flex-grow: 1; text-align: center">{text}</span></button>')

def bezel(buttons, cols=2):
    inner = "".join(buttons)
    return f'<div style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: 4px; padding: 5px; background: #11161b; border-radius: 4px; box-shadow: 0 1px 0 #3b4752">{inner}</div>'

def screw():
    return '<div aria-hidden="true" style="width: 16px; height: 16px; border-radius: 50%; background: radial-gradient(circle at 40% 35%, #56616b, #14181c 70%); box-shadow: 0 0 0 2px #1a2127, inset 0 0 0 4px #1f262c"></div>'

def chip(label, value, color=TRACE):
    return f'<div style="background: #17201e; padding: 5px 8px; border-radius: 2px; font-family: {MONO}; font-size: 13px; color: #c9d6c4; white-space: nowrap">{label} <span style="color: {color}">{value}</span></div>'

def screen(svg, chips=None, h=None):
    ch = ""
    if chips:
        ch = f'<div style="display: flex; gap: 2px; flex-wrap: wrap; background: #0a0e0d; padding: 2px">{"".join(chips)}</div>'
    return (f'<div style="background: #0b100f; border-radius: 6px; border: 1px solid #04070a; box-shadow: inset 0 2px 10px #000000, 0 1px 0 #3b4752; overflow: hidden; display: flex; flex-direction: column">'
            f'{ch}{svg}</div>')

# ---------------------------------------------------------------- graphics
def grid_lines(w, h, nx, ny, col="#1b2a24"):
    s = []
    for i in range(1, nx):
        x = w * i / nx; s.append(f'<line x1="{f(x)}" y1="0" x2="{f(x)}" y2="{h}" stroke="{col}"/>')
    for i in range(1, ny):
        y = h * i / ny; s.append(f'<line x1="0" y1="{f(y)}" x2="{w}" y2="{f(y)}" stroke="{col}"/>')
    return "".join(s)

def vectorscope(w, h, width=1.4, seed=3, aria="Vectorscope"):
    rnd = random.Random(seed)
    cx, cy = w / 2, h / 2; sz = min(w, h) * 0.86
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    # guide lines L / R diagonals + mono vertical + side horizontal
    d = sz / 2
    s.append(f'<line x1="{f(cx-d*0.7)}" y1="{f(cy-d*0.7)}" x2="{f(cx+d*0.7)}" y2="{f(cy+d*0.7)}" stroke="#1f3329"/>')
    s.append(f'<line x1="{f(cx+d*0.7)}" y1="{f(cy-d*0.7)}" x2="{f(cx-d*0.7)}" y2="{f(cy+d*0.7)}" stroke="#1f3329"/>')
    s.append(f'<line x1="{f(cx)}" y1="{f(cy-d)}" x2="{f(cx)}" y2="{f(cy+d)}" stroke="#25402f"/>')
    s.append(f'<line x1="{f(cx-d)}" y1="{f(cy)}" x2="{f(cx+d)}" y2="{f(cy)}" stroke="#1a2a22"/>')
    s.append(f'<path d="M {f(cx-d)} {f(cy)} A {f(d)} {f(d)} 0 0 1 {f(cx+d)} {f(cy)}" fill="none" stroke="#25402f"/>')
    for t, x, y in (("L", cx - d*0.74, cy - d*0.74), ("R", cx + d*0.74, cy - d*0.74), ("M", cx, cy - d - 4), ("+S", cx + d + 2, cy + 4), ("−S", cx - d - 2, cy + 4)):
        anchor = "middle"
        if t == "+S": anchor = "start"
        if t == "−S": anchor = "end"
        s.append(f'<text x="{f(x)}" y="{f(y)}" fill="#5f8a6c" style="font-family:{MONO};font-size:12px;text-anchor:{anchor}">{t}</text>')
    pts = []; nm = 0; ns = 0
    for i in range(2400):
        t = i / 2400 * 70
        nm = nm*0.92 + 0.08*rnd.uniform(-1, 1); ns = ns*0.9 + 0.1*rnd.uniform(-1, 1)
        m = 0.5*math.sin(t*1.3) + 0.24*math.sin(t*3.7+1) + 0.1*math.sin(t*9.1) + 0.5*nm
        sd = (0.17*math.sin(t*2.1+0.5) + 0.11*math.sin(t*5.3) + 0.6*ns) * width
        pts.append((cx + sd*d, cy - m*d))
    path = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
    s.append(f'<path d="{path}" fill="none" stroke="{TRACE}" style="stroke-width:0.7;opacity:0.5"/>')
    path2 = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts[:320])
    s.append(f'<path d="{path2}" fill="none" stroke="{HOT}" style="stroke-width:1.1;opacity:0.85"/>')
    return f'<svg role="img" aria-label="{aria}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

def corr_bar(w, h, val=0.62, label=True):
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    x0 = 18; x1 = w - 18; mid = (x0 + x1) / 2; y = h / 2 + (4 if label else 0)
    s.append(f'<rect x="{x0}" y="{f(y-6)}" width="{x1-x0}" height="12" rx="2" fill="#121b18"/>')
    # negative zone tint
    s.append(f'<rect x="{x0}" y="{f(y-6)}" width="{f(mid-x0)}" height="12" rx="2" fill="#2a1a12"/>')
    vx = mid + (x1 - mid) * val
    s.append(f'<rect x="{f(mid)}" y="{f(y-6)}" width="{f(vx-mid)}" height="12" fill="{TRACE}" style="opacity:0.85"/>')
    s.append(f'<rect x="{f(vx-1.5)}" y="{f(y-10)}" width="3" height="20" fill="{HOT}"/>')
    for v, t in ((-1, "−1"), (-0.5, ""), (0, "0"), (0.5, ""), (1, "+1")):
        tx = mid + (x1 - mid) * v
        s.append(f'<line x1="{f(tx)}" y1="{f(y+8)}" x2="{f(tx)}" y2="{f(y+12)}" stroke="#5f8a6c"/>')
        if t:
            s.append(f'<text x="{f(tx)}" y="{f(y+24)}" fill="#7ea58a" style="font-family:{MONO};font-size:11px;text-anchor:middle">{t}</text>')
    if label:
        s.append(f'<text x="{x0}" y="14" fill="#7ea58a" style="font-family:{MONO};font-size:11px">CORRELATION</text>')
        s.append(f'<text x="{x1}" y="14" fill="{HOT}" style="font-family:{MONO};font-size:12px;text-anchor:end">+{val:.2f}</text>')
    return f'<svg role="img" aria-label="Correlation meter at plus {val:.2f}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

def waterfall(w, h):
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    L = 9; ox_step = 11; oy_step = 9
    base_y = h - 34; x_start = 10; span = w - 20 - (L-1)*ox_step
    # floor
    s.append(f'<path d="M {x_start} {base_y+14} L {x_start+span} {base_y+14} L {x_start+span+(L-1)*ox_step} {base_y+14-(L-1)*oy_step} L {x_start+(L-1)*ox_step} {base_y+14-(L-1)*oy_step} Z" fill="#0f1a15" stroke="#1d3327"/>')
    for k in range(L):
        depth = L - 1 - k
        ox = depth * ox_step; oy = -depth * oy_step
        op = 0.25 + 0.75 * (k / (L-1))
        for ch in (0, 1):
            pts = []
            for i in range(90):
                u = i / 89
                env = math.sin(math.pi * u) ** 0.8
                ph = ch * (0.6 + 0.35*depth) + depth*0.4
                y = math.sin(u*14 + ph) * 0.6 + math.sin(u*31 + ph*1.7) * 0.25
                pts.append((x_start + ox + u*span, base_y + oy - y*env*22))
            d = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
            if k == L - 1:
                col = HOT if ch == 0 else SIDE
                s.append(f'<path d="{d}" fill="none" stroke="{col}" style="stroke-width:1.6"/>')
            else:
                s.append(f'<path d="{d}" fill="none" stroke="{TRACE}" style="stroke-width:1;opacity:{op*0.8:.2f}"/>')
    s.append(f'<text x="10" y="16" fill="{HOT}" style="font-family:{MONO};font-size:11px">L</text>')
    s.append(f'<text x="22" y="16" fill="{SIDE}" style="font-family:{MONO};font-size:11px">R</text>')
    s.append(f'<text x="{w-10}" y="16" fill="#7ea58a" style="font-family:{MONO};font-size:11px;text-anchor:end">DECORRELATION</text>')
    return f'<svg role="img" aria-label="Left and right channels drifting apart over time" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

def width_curve(w, h):
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    top = 18; bot = h - 22; l = 8; r = w - 8
    def fx(freq): return l + (r - l) * (math.log10(freq) - math.log10(20)) / 3
    def wy(wd): return bot - (bot - top) * wd / 200
    s.append(f'<line x1="{l}" y1="{f(wy(100))}" x2="{r}" y2="{f(wy(100))}" stroke="#25402f" style="stroke-dasharray:3 3"/>')
    s.append(f'<text x="{r}" y="{f(wy(100)-4)}" fill="#5f8a6c" style="font-family:{MONO};font-size:10px;text-anchor:end">100%</text>')
    # faint side spectrum
    rnd = random.Random(5); sp = []
    for i in range(120):
        u = i / 119; fr = 20 * 10 ** (3*u)
        e = 0.55 + 0.25*math.sin(u*9) + 0.12*rnd.uniform(-1, 1) - 0.3*u
        sp.append((l + (r-l)*u, bot - max(0.05, e)*(bot-top)*0.6))
    d = f"M {l} {bot} L " + " L ".join(f"{f(x)} {f(y)}" for x, y in sp) + f" L {r} {bot} Z"
    s.append(f'<path d="{d}" fill="{SIDE}" style="opacity:0.12"/>')
    xo = [150, 1200, 6000]; widths = [0, 100, 135, 175]
    def width_at(fr):
        val = widths[0]
        for i, c in enumerate(xo):
            k = 1 / (1 + math.exp(-(math.log10(fr) - math.log10(c)) * 14))
            val += (widths[i+1] - widths[i]) * k
        return val
    pts = []
    for i in range(160):
        u = i / 159; fr = 20 * 10 ** (3*u)
        pts.append((l + (r-l)*u, wy(width_at(fr))))
    line = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
    s.append(f'<path d="{line} L {r} {bot} L {l} {bot} Z" fill="{TRACE}" style="opacity:0.16"/>')
    s.append(f'<path d="{line}" fill="none" stroke="{HOT}" style="stroke-width:2"/>')
    for c, t in zip(xo, ("150", "1.2k", "6k")):
        x = fx(c)
        s.append(f'<line x1="{f(x)}" y1="{top}" x2="{f(x)}" y2="{bot}" stroke="#3d6b4c" style="stroke-dasharray:2 3"/>')
        s.append(f'<circle cx="{f(x)}" cy="{f(wy(width_at(c)))}" r="3.5" fill="#0b100f" stroke="{HOT}" style="stroke-width:1.5"/>')
        s.append(f'<text x="{f(x)}" y="{h-7}" fill="#7ea58a" style="font-family:{MONO};font-size:10px;text-anchor:middle">{t}</text>')
    s.append(f'<text x="{l+2}" y="{f(bot-6)}" fill="{SIDE}" style="font-family:{MONO};font-size:10px">MONO</text>')
    return f'<svg role="img" aria-label="Width per frequency band: mono lows, widening highs" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

def stage(w, h):
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    cx = w / 2; cy = h - 18; R1 = h - 36
    for rr, op in ((R1, 1), (R1*0.66, 0.7), (R1*0.33, 0.5)):
        s.append(f'<path d="M {f(cx-rr)} {f(cy)} A {f(rr)} {f(rr)} 0 0 1 {f(cx+rr)} {f(cy)}" fill="none" stroke="#1f3329" style="opacity:{op}"/>')
    # speaker wedge (+-30deg) vs beyond zone
    for sign in (-1, 1):
        a = math.radians(-90 + sign*30)
        s.append(f'<line x1="{f(cx)}" y1="{f(cy)}" x2="{f(cx+R1*math.cos(a))}" y2="{f(cy+R1*math.sin(a))}" stroke="#2f5a40" style="stroke-dasharray:3 3"/>')
        sx = cx + R1*0.8*math.cos(a); sy = cy + R1*0.8*math.sin(a)
        s.append(f'<rect x="{f(sx-6)}" y="{f(sy-8)}" width="12" height="16" rx="2" fill="#1a2420" stroke="{TRACE}" transform="rotate({sign*30} {f(sx)} {f(sy)})"/>')
    s.append(f'<text x="10" y="16" fill="#7ea58a" style="font-family:{MONO};font-size:10px">BEYOND</text>')
    s.append(f'<text x="{w-10}" y="16" fill="#7ea58a" style="font-family:{MONO};font-size:10px;text-anchor:end">BEYOND</text>')
    rnd = random.Random(8)
    for i in range(26):
        ang = rnd.uniform(-52, 52); rr = rnd.uniform(0.35, 0.95) * R1
        a = math.radians(-90 + ang)
        col = HOT if abs(ang) < 30 else SIDE
        s.append(f'<circle cx="{f(cx+rr*math.cos(a))}" cy="{f(cy+rr*math.sin(a))}" r="{rnd.uniform(1.5,3.5):.1f}" fill="{col}" style="opacity:{rnd.uniform(0.5,1):.2f}"/>')
    s.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5" fill="{TRACE}"/>')
    return f'<svg role="img" aria-label="Top-down sound stage with sources spreading past the speakers" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

def corr_history(w, h):
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    top = 14; bot = h - 40; l = 6; r = w - 6
    def vy(v): return top + (bot - top) * (1 - v) / 2
    s.append(grid_lines(w, bot, 6, 4).replace('y2="'+str(bot)+'"', f'y2="{bot}"'))
    thr = -0.1
    s.append(f'<line x1="{l}" y1="{f(vy(thr))}" x2="{r}" y2="{f(vy(thr))}" stroke="{AMBER}" style="stroke-dasharray:4 3"/>')
    s.append(f'<text x="{r}" y="{f(vy(thr)+12)}" fill="{AMBER}" style="font-family:{MONO};font-size:10px;text-anchor:end">GUARD −0.10</text>')
    s.append(f'<text x="{l+2}" y="{f(vy(1)+10)}" fill="#5f8a6c" style="font-family:{MONO};font-size:10px">+1</text>')
    s.append(f'<text x="{l+2}" y="{f(vy(-1)-3)}" fill="#5f8a6c" style="font-family:{MONO};font-size:10px">−1</text>')
    rnd = random.Random(11); pts = []; raw = []
    for i in range(140):
        u = i / 139
        v = 0.45 + 0.3*math.sin(u*7) + 0.15*math.sin(u*23) + 0.06*rnd.uniform(-1, 1)
        if 0.52 < u < 0.66: v -= 0.95 * math.sin((u-0.52)/0.14*math.pi)
        raw.append(v)
        pts.append((l + (r-l)*u, vy(max(-1, min(1, v)))))
    d = "M " + " L ".join(f"{f(x)} {f(y)}" for x, y in pts)
    s.append(f'<path d="{d}" fill="none" stroke="{TRACE}" style="stroke-width:1.6"/>')
    # GR strip
    gy = h - 28
    s.append(f'<text x="{l}" y="{gy-3}" fill="#7ea58a" style="font-family:{MONO};font-size:10px">WIDTH PULLED</text>')
    for i, v in enumerate(raw):
        if v < thr + 0.15:
            amt = min(1, (thr + 0.15 - v) / 0.7)
            x = l + (r-l)*i/139
            s.append(f'<rect x="{f(x)}" y="{gy}" width="2.2" height="{f(4+amt*16)}" fill="{AMBER}" style="opacity:0.9"/>')
    s.append(f'<line x1="{l}" y1="{gy}" x2="{r}" y2="{gy}" stroke="#2b3a33"/>')
    return f'<svg role="img" aria-label="Correlation over time; Guard pulls width back when it dips below threshold" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

def meters(w, h, vals, labels):
    s = [f'<rect width="{w}" height="{h}" fill="#0b100f"/>']
    n = len(vals); bw = 14; gap = (w - n*bw) / (n + 1)
    segs = 22; top = 8; bot = h - 20; sh = (bot - top) / segs
    for i, (v, t) in enumerate(zip(vals, labels)):
        x = gap + i*(bw+gap)
        for k in range(segs):
            fr = (k + 1) / segs
            on = fr <= v
            col = TRACE if fr < 0.75 else (HOT if fr < 0.92 else "#ff5a4a")
            y = bot - (k+1)*sh
            s.append(f'<rect x="{f(x)}" y="{f(y+1)}" width="{bw}" height="{f(sh-2)}" fill="{col}" style="opacity:{0.95 if on else 0.12}"/>')
        s.append(f'<text x="{f(x+bw/2)}" y="{h-6}" fill="#7ea58a" style="font-family:{MONO};font-size:10px;text-anchor:middle">{t}</text>')
    return f'<svg role="img" aria-label="Level meters" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block">' + "".join(s) + '</svg>'

# ---------------------------------------------------------------- page bits
HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;0,800;1,800&amp;family=Share+Tech+Mono&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#0e1215}}
a{{color:#9be36a}}a:hover{{color:#ffe24d}}
button:focus-visible{{outline:2px solid #ffe24d;outline-offset:2px}}
</style>
</helmet>
'''
TAIL = '''
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

def wordmark():
    return (f'<div style="display: flex; align-items: baseline; gap: 12px">'
            f'<div style="font-family: {FONT}; font-style: italic; font-weight: 800; font-size: 34px; letter-spacing: 0.06em; color: {LABEL}">SPREAD</div>'
            f'<div style="font-family: {FONT}; font-weight: 600; font-size: 13px; letter-spacing: 0.22em; color: {DIM}">STEREO WORKBENCH</div></div>')

def preset_display(wd=300):
    return (f'<div style="width: {wd}px; background: #0b100f; border: 1px solid #04070a; border-radius: 4px; box-shadow: inset 0 2px 8px #000; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; font-family: {MONO}">'
            f'<span style="font-size: 11px; color: #7ea58a">PRESET</span><span style="font-size: 15px; color: {TRACE}">Wide Vocal Air</span><span style="font-size: 11px; color: #7ea58a">A/B</span></div>')

def view_toggle(active):
    return f'<div style="width: 260px">{bezel([btn("Simple", "green" if active=="simple" else "offg"), btn("Advanced", "green" if active=="adv" else "offg")], 2)}</div>'

def panel_open(w, h, pad=24):
    return f'<div style="width: {w}px; height: {h}px; box-sizing: border-box; background: {PANEL}; border: 1px solid #10161b; box-shadow: inset 0 1px 0 #3c4955; position: relative; padding: {pad}px; display: flex; flex-direction: column; gap: 18px">'

def corner_screws():
    pos = [("top: 10px; left: 10px"), ("top: 10px; right: 10px"), ("bottom: 10px; left: 10px"), ("bottom: 10px; right: 10px")]
    return "".join(f'<div style="position: absolute; {p}">{screw()}</div>' for p in pos)

def section_label(t, size=17):
    return f'<div style="font-family: {FONT}; font-weight: 700; font-size: {size}px; letter-spacing: 0.14em; color: {LABEL}; text-align: center; text-transform: uppercase">{t}</div>'

# ================================================================ SIMPLE VIEW
SW, SH = 1080, 720
parts = [HEAD.format(title="Spread — Simple view"), panel_open(SW, SH, 34), corner_screws()]
parts.append(f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 0 12px">{wordmark()}{preset_display()}{view_toggle("simple")}</div>')
parts.append('<div style="display: flex; gap: 28px; flex-grow: 1; padding: 0 12px">')
# left: big scope
scope = vectorscope(500, 420, width=1.5, aria="Vectorscope showing a wide but mono-safe image")
parts.append(f'<div style="width: 500px; display: flex; flex-direction: column; gap: 8px">'
             f'{screen(scope, [chip("WIDTH", "140%"), chip("BASS MONO", "150 Hz", SIDE), chip("GUARD", "ACTIVE", AMBER)])}'
             f'{screen(corr_bar(500, 56))}</div>')
# right: controls
master = knob(92, 0.7, "", labels=[(0, "0"), (0.25, "25"), (0.5, "50"), (0.75, "75"), (1, "100")], skirt=True, ndots=21, lit=TRACE, aria="Master amount 70 percent")
parts.append('<div style="flex-grow: 1; display: flex; flex-direction: column; align-items: center; gap: 14px">')
parts.append(f'<div style="display: flex; flex-direction: column; align-items: center">{master}'
             f'<div style="margin-top: -6px; font-family: {FONT}; font-weight: 800; font-size: 20px; letter-spacing: 0.2em; color: {LABEL}">MASTER</div>'
             f'<div style="font-family: {MONO}; font-size: 12px; color: {DIM}; margin-top: 2px">drives every linked module · 70%</div></div>')
small = "".join([
    knob(30, 0.55, "Bass mono", labels=[(0, "OFF"), (0.33, "80"), (0.66, "150"), (1, "300")], kind="blue", ndots=11, aria="Bass mono 150 hertz"),
    knob(30, 0.5, "Focus", labels=[(0, "WIDE"), (1, "TIGHT")], ndots=11),
    knob(30, 1.0, "Mix", labels=[(0, "DRY"), (1, "WET")], ndots=11),
])
parts.append(f'<div style="display: flex; gap: 6px; justify-content: center">{small}</div>')
parts.append(f'<div style="width: 100%; display: flex; flex-direction: column; gap: 6px"><div style="font-family: {FONT}; font-weight: 600; font-size: 13px; letter-spacing: 0.14em; color: {DIM}">CHARACTER</div>'
             + bezel([btn("Clean", "offg"), btn("Lush", "green"), btn("Wide", "offg"), btn("Huge", "offg")], 4) + '</div>')
parts.append('<div style="width: 100%">' + bezel([btn("Guard", "amber"), btn("Mono", "off"), btn("Bypass", "off")], 3) + '</div>')
parts.append('</div></div></div>')
parts.append(TAIL.format(w=SW, h=SH))
open(f"{ROOT}/Main.dc.html", "w").write("".join(parts))

# ================================================================ ADVANCED VIEW
AW, AH = 1640, 1090
MODW = 252; SCW = MODW - 22
def module(title, scr, body, link_state="green"):
    return (f'<div style="width: {MODW}px; box-sizing: border-box; background: {PANEL}; border-left: 1px solid #3a4651; border-right: 1px solid #141a1f; padding: 12px 11px; display: flex; flex-direction: column; gap: 12px; position: relative">'
            f'<div style="display: flex; justify-content: space-between; align-items: center">{screw()}{section_label(title)}{screw()}</div>'
            f'{scr}{body}'
            f'<div style="flex-grow: 1"></div>'
            f'{bezel([btn("Link", link_state), btn("On", "green")], 2)}'
            f'<div style="display: flex; justify-content: space-between">{screw()}{screw()}</div></div>')

def row(*items, gap=0):
    return f'<div style="display: flex; justify-content: space-around; align-items: flex-start; gap: {gap}px">{"".join(items)}</div>'

mods = []
# 1 INPUT
mods.append(module("Input",
    screen(meters(SCW, 150, [0.68, 0.66], ["L", "R"]), [chip("SRC", "MONO", SIDE), chip("BAL", "C")]),
    knob(40, 0.5, "Balance", labels=[(0, "L"), (0.5, "C"), (1, "R")], ndots=15, skirt=True)
    + row(knob(24, 0.5, "Trim"), knob(24, 0.5, "Ch. delay"))
    + bezel([btn("Ø L", "off", True), btn("Ø R", "off", True), btn("Swap", "off", True), btn("Mono in", "green", True)], 2),
    link_state="offg"))
# 2 GENERATE
mods.append(module("Generate",
    screen(waterfall(SCW, 170), [chip("HAAS", "12.0ms"), chip("DET", "±9ct", HOT)]),
    bezel([btn("Haas", "green", True), btn("Detune", "green", True), btn("Chorus", "off", True), btn("Comb", "off", True), btn("Allpass", "green", True), btn("Room", "off", True)], 2)
    + knob(40, 0.62, "Amount", labels=[(0, "0"), (0.5, "50"), (1, "100")], ndots=15, lit=TRACE)
    + row(knob(22, 0.35, "Time"), knob(22, 0.45, "Cents"))
    + row(knob(22, 0.3, "Rate"), knob(22, 0.25, "Size"))))
# 3 SHAPE
mods.append(module("Shape",
    screen(width_curve(SCW, 170), [chip("BANDS", "4"), chip("XO", "150·1.2k·6k", SIDE)]),
    knob(36, 0.55, "Bass mono", labels=[(0, "OFF"), (0.25, "50"), (0.5, "80"), (0.75, "150"), (1, "300")], kind="blue", ndots=11)
    + row(knob(19, 0.5, "Lo-mid", namesize=12), knob(19, 0.62, "Hi-mid", namesize=12), knob(19, 0.78, "High", namesize=12))
    + row(knob(22, 0.6, "Side tilt"), knob(22, 0.3, "Side drive"))
    + bezel([btn("Solo S", "off", True), btn("Solo M", "off", True)], 2)))
# 4 SPACE
mods.append(module("Space",
    screen(stage(SCW, 170), [chip("SHUF", "+3dB"), chip("BEYOND", "OFF", AMBER)]),
    knob(40, 0.45, "Shuffle", labels=[(0, "0"), (0.5, "+3"), (1, "+6")], ndots=15, skirt=True)
    + row(knob(22, 0.25, "Transient"), knob(22, 0.7, "Sustain"))
    + row(knob(22, 0.2, "Motion"), knob(22, 0.4, "Depth"))
    + bezel([btn("Beyond", "off", True), btn("Sync", "green", True)], 2)))
# 5 GUARD
mods.append(module("Guard",
    screen(corr_history(SCW, 170), [chip("CORR", "+0.62"), chip("PULL", "−18%", AMBER)]),
    knob(36, 0.45, "Threshold", labels=[(0, "−.5"), (0.25, "−.2"), (0.5, "0"), (0.75, "+.2"), (1, "+.5")], kind="chicken", ndots=11)
    + knob(36, 0.5, "Recovery", labels=[(0, "100"), (0.25, "400"), (0.5, "800"), (0.75, "1.5s"), (1, "AUTO")], kind="chicken", ndots=5)
    + bezel([btn("Auto", "amber", True), btn("Listen", "off", True)], 2),
    link_state="offg"))
# 6 OUTPUT
mods.append(module("Output",
    screen(vectorscope(SCW, 150, width=1.5, seed=4, aria="Output vectorscope"), [chip("M", "−1.2"), chip("S", "−6.8", SIDE)]),
    screen(meters(SCW, 96, [0.72, 0.7, 0.74, 0.42], ["L", "R", "M", "S"]))
    + row(knob(24, 0.55, "Mid"), knob(24, 0.6, "Side"))
    + row(knob(24, 1.0, "Mix"), knob(24, 0.5, "Output"))
    + bezel([btn("Mono", "off", True), btn("Bypass", "off", True)], 2),
    link_state="offg"))

parts = [HEAD.format(title="Spread — Advanced view"), panel_open(AW, AH, 26), corner_screws()]
master_small = knob(44, 0.7, "", labels=[(0, "0"), (0.5, "50"), (1, "100")], skirt=True, ndots=15, lit=TRACE, aria="Master amount 70 percent")
parts.append(f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 0 14px">'
             f'{wordmark()}'
             f'<div style="display: flex; align-items: center; gap: 14px">{master_small}'
             f'<div style="display: flex; flex-direction: column; gap: 4px"><div style="font-family: {FONT}; font-weight: 800; font-size: 20px; letter-spacing: 0.2em; color: {LABEL}">MASTER</div>'
             f'<div style="font-family: {MONO}; font-size: 12px; color: {DIM}">70% · drives 3 linked modules</div>'
             f'<div style="display: flex; gap: 4px">{chip("GEN", "70%")}{chip("SHAPE", "70%")}{chip("SPACE", "70%")}</div></div></div>'
             f'{preset_display(280)}{view_toggle("adv")}</div>')
parts.append(f'<div style="display: flex; justify-content: center; gap: 4px; flex-grow: 1; background: #10151a; padding: 4px; border-radius: 4px">{"".join(mods)}</div>')
parts.append('</div>')
parts.append(TAIL.format(w=AW, h=AH))
open(f"{ROOT}/Advanced.dc.html", "w").write("".join(parts))
print("ok")
