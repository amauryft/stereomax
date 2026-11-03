import json, math, random, base64
src = open("/home/claude/gen.py").read().split("# ================================================================ SIMPLE VIEW")[0]
exec(src)

W, H = 1640, 1140
MODW = 252; SCW = MODW - 22

# ---------------------------------------------------------------- parameter table (must match PluginProcessor.cpp)
P = {
 'master': (0, 200, 100, '%', 0),
 'in_bal': (-100, 100, 0, '%', 0), 'in_trim': (-12, 12, 0, 'dB', 1), 'in_dly': (0, 20, 0, 'ms', 1),
 'gen_amt': (0, 100, 60, '%', 0), 'gen_time': (1, 40, 12, 'ms', 1), 'gen_cents': (0, 25, 9, 'ct', 0),
 'gen_rate': (0.05, 5, 0.6, 'Hz', 2), 'gen_size': (0, 100, 30, '%', 0),
 'sh_bass': (0, 300, 150, 'Hz', 0), 'sh_lo': (0, 100, 35, '%', 0), 'sh_hi': (0, 100, 50, '%', 0), 'sh_top': (0, 100, 70, '%', 0),
 'sh_tilt': (-100, 100, 0, '%', 0), 'sh_drive': (0, 100, 20, '%', 0),
 'sp_shuf': (0, 6, 2, 'dB', 1), 'sp_tr': (0, 200, 100, '%', 0), 'sp_sus': (0, 200, 100, '%', 0),
 'sp_mot': (0.02, 2, 0.2, 'Hz', 2), 'sp_dep': (0, 100, 0, '%', 0),
 'gd_thr': (-0.5, 0.5, -0.05, '', 2), 'gd_rec': (0, 4, 2, '', 0),
 'out_mid': (-12, 12, 0, 'dB', 1), 'out_side': (-12, 12, 0, 'dB', 1), 'out_mix': (0, 100, 100, '%', 0), 'out_gain': (-12, 12, 0, 'dB', 1),
}
T = {'link_gen': 1, 'link_shape': 1, 'link_space': 1, 'in_on': 1, 'in_phl': 0, 'in_phr': 0, 'in_swap': 0, 'in_mono': 0,
     'gen_on': 1, 'e_haas': 1, 'e_detune': 1, 'e_chorus': 0, 'e_comb': 0, 'e_allpass': 1, 'e_room': 0,
     'sh_on': 1, 'solo_s': 0, 'solo_m': 0, 'sp_on': 1, 'sp_beyond': 0, 'sp_sync': 0,
     'gd_on': 1, 'gd_auto': 1, 'gd_listen': 0, 'out_on': 1, 'out_mono': 0, 'out_bypass': 0}
LINKED = {'gen_amt': 'link_gen', 'gen_cents': 'link_gen', 'gen_size': 'link_gen', 'sh_lo': 'link_shape', 'sh_hi': 'link_shape',
          'sh_top': 'link_shape', 'sh_tilt': 'link_shape', 'sh_drive': 'link_shape', 'sp_shuf': 'link_space', 'sp_dep': 'link_space'}

def knobP(R, name, pid, labels=None, kind="knurl", skirt=False, ndots=13, lit=False, namesize=13):
    pad = 34 if labels else 15
    S = 2 * (R + pad); c = S / 2
    g = uid(); p = []
    p.append(f'<defs><radialGradient id="{g}c" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#e4e8eb"/><stop offset="1" stop-color="#8f979e"/></radialGradient>'
             f'<linearGradient id="{g}s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6f8f9"/><stop offset="0.45" stop-color="#8b9399"/><stop offset="0.7" stop-color="#5d656c"/><stop offset="1" stop-color="#d5dade"/></linearGradient>'
             f'<radialGradient id="{g}b" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#6aa2f5"/><stop offset="1" stop-color="#1f55b3"/></radialGradient></defs>')
    for i in range(ndots):
        fr = i / (ndots - 1); a = math.radians(-135 + 270 * fr - 90); rr = R + 9
        cls = ' class="dot"' if lit else ''
        p.append(f'<circle{cls} data-f="{fr:.4f}" cx="{f(c + rr*math.cos(a))}" cy="{f(c + rr*math.sin(a))}" r="2.6" fill="#e3e8ec"/>')
    if labels:
        for fr, t in labels:
            a = math.radians(-135 + 270 * fr - 90); rr = R + 24
            p.append(f'<text x="{f(c + rr*math.cos(a))}" y="{f(c + rr*math.sin(a) + 4)}" fill="{DIM}" font-family="{FONT}" font-size="12" font-weight="600" text-anchor="middle">{t}</text>')
    if kind in ("chicken", "blue"):
        fill = f"url(#{g}b)" if kind == "blue" else f"url(#{g}c)"
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R*0.92)}" fill="#1c2329" stroke="#0e1216"/>')
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R*0.62)}" fill="{fill}" stroke="#2b3238"/>')
        w = R * 0.42; L = R
        p.append(f'<g class="ptr"><path d="M {f(c-w/2)} {f(c+L*0.85)} L {f(c-w*0.38)} {f(c-L)} Q {f(c)} {f(c-L-6)} {f(c+w*0.38)} {f(c-L)} L {f(c+w/2)} {f(c+L*0.85)} Q {f(c)} {f(c+L*0.95)} {f(c-w/2)} {f(c+L*0.85)} Z" fill="{fill}" stroke="#0f1418" stroke-width="1.2"/>'
                 f'<line x1="{f(c)}" y1="{f(c-L+3)}" x2="{f(c)}" y2="{f(c-L*0.3)}" stroke="#fff" stroke-width="3" stroke-linecap="round"/></g>')
    else:
        rk = R; inner = ""
        if skirt:
            p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R)}" fill="url(#{g}s)" stroke="#20272d" stroke-width="1.5"/>')
            inner += f'<line x1="{f(c)}" y1="{f(c-R*0.74)}" x2="{f(c)}" y2="{f(c-R*0.98)}" stroke="#111" stroke-width="3"/>'
            rk = R * 0.7
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(rk)}" fill="#7d858c" stroke="#1d2328" stroke-width="1.5"/>')
        dash = 2 * math.pi * (rk - 2) / 96
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(rk-2)}" fill="none" stroke="#d9dee2" stroke-width="3.5" stroke-dasharray="{dash:.2f} {dash:.2f}"/>')
        p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(rk*0.8)}" fill="url(#{g}c)" stroke="#5c646b"/>')
        inner += f'<line x1="{f(c)}" y1="{f(c-rk*0.45)}" x2="{f(c)}" y2="{f(c-rk*0.95)}" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
        p.append(f'<g class="ptr">{inner}</g>')
    svg = f'<svg width="{int(S)}" height="{int(S)}" viewBox="0 0 {int(S)} {int(S)}" aria-hidden="true">' + "".join(p) + '</svg>'
    link = LINKED.get(pid, "")
    lab = f'<div class="kname" style="font-size:{namesize}px">{name}</div>' if name else ""
    return (f'<div class="kwrap"><div class="knob" tabindex="0" role="slider" aria-label="{name or "Master"}" data-p="{pid}" data-c="{c}" data-link="{link}" style="width:{int(S)}px;height:{int(S)}px">{svg}</div>'
            f'{lab}<div class="kval" data-v="{pid}"></div></div>')

def tbtn(text, pid, col="green", small=True):
    fs = 14 if small else 15
    return (f'<button type="button" class="tb" data-t="{pid}" data-col="{col}" style="font-size:{fs}px"><span class="led" aria-hidden="true"></span><span class="tl">{text}</span></button>')

def bez(btns, cols=2):
    return f'<div class="bezel" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{"".join(btns)}</div>'

def scr(svg, chips=""):
    ch = f'<div class="chips">{chips}</div>' if chips else ""
    return f'<div class="screen">{ch}{svg}</div>'

def ch(label, cid, color=TRACE, init="—"):
    return f'<div class="chip">{label} <span id="{cid}" style="color:{color}">{init}</span></div>'

def svgbox(w, h, inner, sid, aria):
    return f'<svg id="{sid}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{aria}" style="display:block"><rect width="{w}" height="{h}" fill="#0b100f"/>{inner}</svg>'

def scope_frame(w, h):
    cx, cy = w/2, h/2; d = min(w, h)*0.43
    s = []
    s.append(f'<line x1="{f(cx-d*0.7)}" y1="{f(cy-d*0.7)}" x2="{f(cx+d*0.7)}" y2="{f(cy+d*0.7)}" stroke="#1f3329"/>')
    s.append(f'<line x1="{f(cx+d*0.7)}" y1="{f(cy-d*0.7)}" x2="{f(cx-d*0.7)}" y2="{f(cy+d*0.7)}" stroke="#1f3329"/>')
    s.append(f'<line x1="{f(cx)}" y1="{f(cy-d)}" x2="{f(cx)}" y2="{f(cy+d)}" stroke="#25402f"/>')
    s.append(f'<line x1="{f(cx-d)}" y1="{f(cy)}" x2="{f(cx+d)}" y2="{f(cy)}" stroke="#1a2a22"/>')
    s.append(f'<path d="M {f(cx-d)} {f(cy)} A {f(d)} {f(d)} 0 0 1 {f(cx+d)} {f(cy)}" fill="none" stroke="#25402f"/>')
    for t, x, y, an in (("L", cx-d*0.74, cy-d*0.74, "middle"), ("R", cx+d*0.74, cy-d*0.74, "middle"), ("M", cx, cy-d-4, "middle"), ("+S", cx+d+2, cy+4, "start"), ("−S", cx-d-2, cy+4, "end")):
        s.append(f'<text x="{f(x)}" y="{f(y)}" fill="#5f8a6c" font-family="{MONO}" font-size="12" text-anchor="{an}">{t}</text>')
    s.append(f'<path class="sAll" d="" fill="none" stroke="{TRACE}" stroke-width="0.9" opacity="0.6"/>')
    s.append(f'<path class="sHot" d="" fill="none" stroke="{HOT}" stroke-width="1.3" opacity="0.9"/>')
    return "".join(s)

def meter_frame(w, h, labels, mid):
    n = len(labels); bw = 14; gap = (w - n*bw) / (n + 1); segs = 22; top = 8; bot = h - 20; sh = (bot - top) / segs
    s = []
    for i, t in enumerate(labels):
        x = gap + i*(bw+gap)
        for k in range(segs):
            fr = (k+1)/segs
            col = TRACE if fr < 0.75 else (HOT if fr < 0.92 else "#ff5a4a")
            y = bot - (k+1)*sh
            s.append(f'<rect class="seg" data-m="{mid}{i}" data-f="{fr:.3f}" x="{f(x)}" y="{f(y+1)}" width="{bw}" height="{f(sh-2)}" fill="{col}" opacity="0.12"/>')
        s.append(f'<text x="{f(x+bw/2)}" y="{h-6}" fill="#7ea58a" font-family="{MONO}" font-size="10" text-anchor="middle">{t}</text>')
    return "".join(s)

def wf_frame(w, h):
    L = 9; ox = 11; oy = 9; by = h - 34; xs = 10; span = w - 20 - (L-1)*ox
    s = [f'<path d="M {xs} {by+14} L {xs+span} {by+14} L {xs+span+(L-1)*ox} {by+14-(L-1)*oy} L {xs+(L-1)*ox} {by+14-(L-1)*oy} Z" fill="#0f1a15" stroke="#1d3327"/>']
    for k in range(L-1):
        op = (0.25 + 0.75*k/(L-1))*0.8
        for c in range(2):
            s.append(f'<path class="wfb" d="" fill="none" stroke="{TRACE}" stroke-width="1" opacity="{op:.2f}"/>')
    s.append(f'<path id="wfL" d="" fill="none" stroke="{HOT}" stroke-width="1.6"/><path id="wfR" d="" fill="none" stroke="{SIDE}" stroke-width="1.6"/>')
    s.append(f'<text x="10" y="16" fill="{HOT}" font-family="{MONO}" font-size="11">L</text><text x="22" y="16" fill="{SIDE}" font-family="{MONO}" font-size="11">R</text>')
    s.append(f'<text x="{w-10}" y="16" fill="#7ea58a" font-family="{MONO}" font-size="11" text-anchor="end">DECORRELATION</text>')
    return "".join(s), {"L": L, "ox": ox, "oy": oy, "by": by, "xs": xs, "span": span}

def wc_frame(w, h):
    top = 18; bot = h - 22; l = 8; r = w - 8
    def wy(v): return bot - (bot-top)*v/200
    s = [f'<line x1="{l}" y1="{f(wy(100))}" x2="{r}" y2="{f(wy(100))}" stroke="#25402f" stroke-dasharray="3 3"/>',
         f'<text x="{r}" y="{f(wy(100)-4)}" fill="#5f8a6c" font-family="{MONO}" font-size="10" text-anchor="end">100%</text>']
    s.append(f'<path id="wcFill" d="" fill="{TRACE}" opacity="0.16"/><path id="wcLine" d="" fill="none" stroke="{HOT}" stroke-width="2"/>')
    for i, t in enumerate(("150", "1.2k", "6k")):
        s.append(f'<line class="xoL" x1="0" y1="{top}" x2="0" y2="{bot}" stroke="#3d6b4c" stroke-dasharray="2 3"/>')
        s.append(f'<circle class="xoD" cx="0" cy="0" r="3.5" fill="#0b100f" stroke="{HOT}" stroke-width="1.5"/>')
        s.append(f'<text class="xoT" x="0" y="{h-7}" fill="#7ea58a" font-family="{MONO}" font-size="10" text-anchor="middle">{t}</text>')
    s.append(f'<text id="wcMono" x="{l+2}" y="{f(bot-6)}" fill="{SIDE}" font-family="{MONO}" font-size="10">MONO</text>')
    return "".join(s), {"top": top, "bot": bot, "l": l, "r": r}

def st_frame(w, h):
    cx = w/2; cy = h - 18; R1 = h - 36
    s = []
    for rr, op in ((R1, 1), (R1*0.66, 0.7), (R1*0.33, 0.5)):
        s.append(f'<path d="M {f(cx-rr)} {f(cy)} A {f(rr)} {f(rr)} 0 0 1 {f(cx+rr)} {f(cy)}" fill="none" stroke="#1f3329" opacity="{op}"/>')
    for sign in (-1, 1):
        a = math.radians(-90 + sign*30)
        s.append(f'<line x1="{f(cx)}" y1="{f(cy)}" x2="{f(cx+R1*math.cos(a))}" y2="{f(cy+R1*math.sin(a))}" stroke="#2f5a40" stroke-dasharray="3 3"/>')
        sx = cx + R1*0.8*math.cos(a); sy = cy + R1*0.8*math.sin(a)
        s.append(f'<rect x="{f(sx-6)}" y="{f(sy-8)}" width="12" height="16" rx="2" fill="#1a2420" stroke="{TRACE}" transform="rotate({sign*30} {f(sx)} {f(sy)})"/>')
    s.append(f'<text x="10" y="16" fill="#7ea58a" font-family="{MONO}" font-size="10">BEYOND</text><text x="{w-10}" y="16" fill="#7ea58a" font-family="{MONO}" font-size="10" text-anchor="end">BEYOND</text>')
    rnd = random.Random(8); dots = []
    for i in range(26):
        dots.append([round(rnd.uniform(-1, 1), 3), round(rnd.uniform(0.35, 0.95), 3), round(rnd.uniform(1.5, 3.5), 1), round(rnd.uniform(0.5, 1), 2)])
        s.append(f'<circle class="stD" cx="0" cy="0" r="{dots[-1][2]}" opacity="{dots[-1][3]}" fill="{HOT}"/>')
    s.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5" fill="{TRACE}"/>')
    return "".join(s), {"cx": cx, "cy": cy, "R": R1, "dots": dots}

def ch_frame(w, h):
    top = 14; bot = h - 40; l = 6; r = w - 6
    s = [grid_lines(w, bot, 6, 4)]
    s.append(f'<line id="thrL" x1="{l}" y1="0" x2="{r}" y2="0" stroke="{AMBER}" stroke-dasharray="4 3"/>')
    s.append(f'<text id="thrT" x="{r}" y="0" fill="{AMBER}" font-family="{MONO}" font-size="10" text-anchor="end">GUARD</text>')
    s.append(f'<text x="{l+2}" y="{top+10}" fill="#5f8a6c" font-family="{MONO}" font-size="10">+1</text><text x="{l+2}" y="{bot-3}" fill="#5f8a6c" font-family="{MONO}" font-size="10">−1</text>')
    s.append(f'<path id="chLine" d="" fill="none" stroke="{TRACE}" stroke-width="1.6"/>')
    gy = h - 28
    s.append(f'<text x="{l}" y="{gy-3}" fill="#7ea58a" font-family="{MONO}" font-size="10">WIDTH PULLED</text><line x1="{l}" y1="{gy}" x2="{r}" y2="{gy}" stroke="#2b3a33"/>')
    s.append(f'<path id="chPull" d="" fill="{AMBER}" opacity="0.9"/>')
    return "".join(s), {"top": top, "bot": bot, "l": l, "r": r, "gy": gy}

def row(*items):
    return f'<div class="row">{"".join(items)}</div>'

def module(title, body, link=None, power=None):
    foot = [tbtn("Link", link)] if link else []
    foot.append(tbtn("On", power))
    return (f'<section class="mod" aria-label="{title}"><div class="mhead">{screw()}<h2>{title}</h2>{screw()}</div>'
            f'{body}<div style="flex-grow:1"></div>{bez(foot, len(foot))}<div class="mfoot">{screw()}{screw()}</div></section>')

wf, WF = wf_frame(SCW, 170); wc, WC = wc_frame(SCW, 170); st, ST = st_frame(SCW, 170); chh, CH = ch_frame(SCW, 170)
mods = [
 module("Input",
   scr(svgbox(SCW, 150, meter_frame(SCW, 150, ["L", "R"], "in"), "inMeters", "Input meters"), ch("SRC", "cSrc", SIDE) + ch("BAL", "cBal"))
   + knobP(40, "Balance", "in_bal", labels=[(0, "L"), (0.5, "C"), (1, "R")], ndots=15, skirt=True)
   + row(knobP(24, "Trim", "in_trim"), knobP(24, "Ch. delay", "in_dly"))
   + bez([tbtn("Ø L", "in_phl", "red"), tbtn("Ø R", "in_phr", "red"), tbtn("Swap", "in_swap", "amber"), tbtn("Mono in", "in_mono")]),
   power="in_on"),
 module("Generate",
   scr(svgbox(SCW, 170, wf, "wf", "Decorrelation display"), ch("HAAS", "cHaas") + ch("DET", "cDet", HOT))
   + bez([tbtn("Haas", "e_haas"), tbtn("Detune", "e_detune"), tbtn("Chorus", "e_chorus"), tbtn("Comb", "e_comb"), tbtn("Allpass", "e_allpass"), tbtn("Room", "e_room")])
   + knobP(40, "Amount", "gen_amt", labels=[(0, "0"), (0.5, "50"), (1, "100")], ndots=15, lit=True)
   + row(knobP(22, "Time", "gen_time"), knobP(22, "Cents", "gen_cents"))
   + row(knobP(22, "Rate", "gen_rate"), knobP(22, "Size", "gen_size")),
   link="link_gen", power="gen_on"),
 module("Shape",
   scr(svgbox(SCW, 170, wc, "wc", "Width per band"), ch("BANDS", "cBands", TRACE, "4") + ch("XO", "cXo", SIDE))
   + knobP(36, "Bass mono", "sh_bass", labels=[(0, "OFF"), (0.25, "75"), (0.5, "150"), (0.75, "225"), (1, "300")], kind="blue", ndots=11)
   + row(knobP(19, "Lo-mid", "sh_lo", namesize=12), knobP(19, "Hi-mid", "sh_hi", namesize=12), knobP(19, "High", "sh_top", namesize=12))
   + row(knobP(22, "Side tilt", "sh_tilt"), knobP(22, "Side drive", "sh_drive"))
   + bez([tbtn("Solo S", "solo_s", "red"), tbtn("Solo M", "solo_m", "red")]),
   link="link_shape", power="sh_on"),
 module("Space",
   scr(svgbox(SCW, 170, st, "st", "Sound stage"), ch("SHUF", "cShuf") + ch("BEYOND", "cBey", AMBER))
   + knobP(40, "Shuffle", "sp_shuf", labels=[(0, "0"), (0.5, "+3"), (1, "+6")], ndots=15, skirt=True)
   + row(knobP(22, "Transient", "sp_tr"), knobP(22, "Sustain", "sp_sus"))
   + row(knobP(22, "Motion", "sp_mot"), knobP(22, "Depth", "sp_dep"))
   + bez([tbtn("Beyond", "sp_beyond", "amber"), tbtn("Sync", "sp_sync")]),
   link="link_space", power="sp_on"),
 module("Guard",
   scr(svgbox(SCW, 170, chh, "ch", "Correlation history"), ch("CORR", "cCorr") + ch("PULL", "cPull", AMBER))
   + knobP(36, "Threshold", "gd_thr", labels=[(0, "−.5"), (0.25, "−.25"), (0.5, "0"), (0.75, "+.25"), (1, "+.5")], kind="chicken", ndots=11)
   + knobP(36, "Recovery", "gd_rec", labels=[(0, "100"), (0.25, "400"), (0.5, "800"), (0.75, "1.5s"), (1, "AUTO")], kind="chicken", ndots=5)
   + bez([tbtn("Auto", "gd_auto", "amber"), tbtn("Listen", "gd_listen", "red")]),
   power="gd_on"),
 module("Output",
   scr(svgbox(SCW, 150, scope_frame(SCW, 150), "scope", "Output vectorscope"), ch("M", "cM") + ch("S", "cS", SIDE))
   + scr(svgbox(SCW, 96, meter_frame(SCW, 96, ["L", "R", "M", "S"], "out"), "outMeters", "Output meters"))
   + row(knobP(24, "Mid", "out_mid"), knobP(24, "Side", "out_side"))
   + row(knobP(24, "Mix", "out_mix"), knobP(24, "Output", "out_gain"))
   + bez([tbtn("Mono", "out_mono", "red"), tbtn("Bypass", "out_bypass", "red")]),
   power="out_on"),
]

master = knobP(44, "", "master", labels=[(0, "0"), (0.5, "100"), (1, "200")], skirt=True, ndots=15, lit=True)
header = (f'<header class="top">{wordmark()}'
          f'<div class="mastergrp">{master}<div class="minfo"><div class="mtitle">MASTER <span id="mPct">100%</span></div>'
          f'<div class="msub">drag up/down · 100% = knobs as set · drives <span id="mCount">3</span> linked modules</div>'
          f'<div id="mChips" class="mchips"></div></div></div>'
          f'<div class="ver"><span>SPREAD</span><b>v0.1 TEST BUILD</b><span id="mode">—</span></div></header>')

fonts = ""
for fam, wt, sty, fn in (("Barlow Condensed", 600, "normal", "BarlowCondensed-SemiBold.ttf"), ("Barlow Condensed", 700, "normal", "BarlowCondensed-Bold.ttf"),
                         ("Barlow Condensed", 800, "normal", "BarlowCondensed-ExtraBold.ttf"), ("Barlow Condensed", 800, "italic", "BarlowCondensed-ExtraBoldItalic.ttf"),
                         ("Share Tech Mono", 400, "normal", "ShareTechMono-Regular.ttf")):
    b64 = base64.b64encode(open(f"/home/claude/fonts/{fn}", "rb").read()).decode()
    fonts += f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{sty};src:url(data:font/ttf;base64,{b64}) format('truetype');}}\n"

CSS = f"""{fonts}
html,body{{margin:0;height:100%;background:#0e1215;overflow:hidden;user-select:none;-webkit-user-select:none}}
#app{{width:{W}px;height:{H}px;transform-origin:0 0;position:absolute;left:0;top:0;box-sizing:border-box;background:{PANEL};padding:26px;display:flex;flex-direction:column;gap:18px}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:0 14px}}
.mastergrp{{display:flex;align-items:center;gap:14px}}
.mtitle{{font-family:{FONT};font-weight:800;font-size:20px;letter-spacing:.2em;color:{LABEL}}}
.mtitle span{{font-family:{MONO};font-weight:400;font-size:16px;letter-spacing:0;color:{TRACE}}}
.msub{{font-family:{MONO};font-size:12px;color:{DIM};margin:4px 0}}
.mchips{{display:flex;gap:4px;min-height:26px}}
.ver{{display:flex;flex-direction:column;align-items:flex-end;gap:2px;font-family:{MONO};font-size:11px;color:#7ea58a;background:#0b100f;border:1px solid #04070a;border-radius:4px;box-shadow:inset 0 2px 8px #000;padding:8px 14px;width:240px}}
.ver b{{color:{TRACE};font-weight:400;font-size:15px}}
.rack{{display:flex;justify-content:center;gap:4px;flex-grow:1;background:#10151a;padding:4px;border-radius:4px}}
.mod{{width:{MODW}px;box-sizing:border-box;background:{PANEL};border-left:1px solid #3a4651;border-right:1px solid #141a1f;padding:12px 11px;display:flex;flex-direction:column;gap:10px;transition:opacity .2s}}
.mod.off>*:not(.bezel):not(.mfoot):not(.mhead){{opacity:.35}}
.mhead,.mfoot{{display:flex;justify-content:space-between;align-items:center}}
.mhead h2{{margin:0;font-family:{FONT};font-weight:700;font-size:17px;letter-spacing:.14em;color:{LABEL};text-transform:uppercase}}
.screen{{background:#0b100f;border-radius:6px;border:1px solid #04070a;box-shadow:inset 0 2px 10px #000,0 1px 0 #3b4752;overflow:hidden;display:flex;flex-direction:column}}
.chips{{display:flex;gap:2px;flex-wrap:wrap;background:#0a0e0d;padding:2px}}
.chip{{background:#17201e;padding:5px 8px;border-radius:2px;font-family:{MONO};font-size:13px;color:#c9d6c4;white-space:nowrap}}
.bezel{{display:grid;gap:4px;padding:5px;background:#11161b;border-radius:4px;box-shadow:0 1px 0 #3b4752}}
.tb{{display:flex;align-items:center;gap:8px;min-height:40px;padding:0 10px;background:{CREAM};border:1px solid #5f5848;border-radius:3px;box-shadow:inset 0 -3px 0 #cfc5a8,inset 0 1px 0 #fffaf0;font-family:{FONT};font-weight:700;letter-spacing:.05em;color:{INK};cursor:pointer;text-transform:uppercase}}
.tb:active{{box-shadow:inset 0 2px 3px #b9ae90;transform:translateY(1px)}}
.tb:focus-visible,.knob:focus-visible{{outline:2px solid {HOT};outline-offset:2px}}
.led{{width:8px;height:22px;border-radius:2px;background:#2c3a30;box-shadow:inset 0 1px 2px #000;flex-shrink:0}}
.tl{{flex-grow:1;text-align:center}}
.kwrap{{display:flex;flex-direction:column;align-items:center}}
.knob{{position:relative;cursor:ns-resize;touch-action:none;border-radius:50%}}
.knob svg{{display:block}}
.kname{{margin-top:-10px;font-family:{FONT};font-weight:600;letter-spacing:.08em;color:{LABEL};text-transform:uppercase;text-align:center}}
.kval{{font-family:{MONO};font-size:11px;color:{TRACE};text-align:center;margin-top:1px;min-height:13px}}
.row{{display:flex;justify-content:space-around;align-items:flex-start}}
.corner{{position:absolute}}
"""

JS = r"""
const P = __P__, T = __T__, LINKED = __LINKED__, WF = __WF__, WC = __WC__, ST = __ST__, CH = __CH__, SCW = __SCW__;
const $ = (s, el = document) => el.querySelector(s), $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const f1 = v => (Math.round(v * 10) / 10).toString();
const LEDC = { green: '#62e86d', amber: '#ffb23e', red: '#ff5a4a' };

// ---------- fit to window
function fit() { const s = Math.min(innerWidth / __W__, innerHeight / __H__); $('#app').style.transform = `scale(${s})`; }
addEventListener('resize', fit); fit();

// ---------- backend (JUCE) or browser mock
let Juce, mock = false;
async function boot() {
  if (window.__JUCE__) { Juce = await import('./juce/index.js'); }
  else {
    mock = true;
    const mk = (init, isT) => { const st = { v: init, valueChangedEvent: { ls: [], addListener(f) { this.ls.push(f); }, callListeners() { this.ls.forEach(f => f()); } }, propertiesChangedEvent: { addListener() {} } };
      if (isT) { st.getValue = () => st.v; st.setValue = x => { st.v = x; st.valueChangedEvent.callListeners(); }; }
      else { st.getNormalisedValue = () => st.v; st.setNormalisedValue = x => { st.v = x; st.valueChangedEvent.callListeners(); }; st.sliderDragStarted = () => {}; st.sliderDragEnded = () => {}; }
      return st; };
    const S = {}, TT = {};
    for (const k in P) S[k] = mk((P[k][2] - P[k][0]) / (P[k][1] - P[k][0]), false);
    for (const k in T) TT[k] = mk(!!T[k], true);
    Juce = { getSliderState: k => S[k], getToggleState: k => TT[k] };
  }
  init();
}

const S = {}, TG = {};
const norm = k => S[k].getNormalisedValue();
const tog = k => !!TG[k].getValue();
const master = () => norm('master') * 2;           // 0..2, 1 = as set
function effN(k) {                                   // normalised value after the master macro
  let v = norm(k); const link = LINKED[k];
  if (link && tog(link)) v = k === 'sh_tilt' ? 0.5 + (v - 0.5) * master() : v * master();
  return clamp(v);
}
const scaled = (k, n) => P[k][0] + (P[k][1] - P[k][0]) * n;
const effS = k => scaled(k, effN(k));
const bassHz = () => effS('sh_bass');

function fmt(k) {
  const v = effS(k), u = P[k][3], d = P[k][4];
  if (k === 'sh_bass') return v < 20 ? 'OFF' : Math.round(v) + ' Hz';
  if (k === 'gd_rec') return ['100 ms', '400 ms', '800 ms', '1.5 s', 'AUTO'][Math.round(v)];
  if (k === 'in_bal') return Math.abs(v) < 0.5 ? 'C' : (v < 0 ? 'L' : 'R') + Math.round(Math.abs(v));
  if (k === 'sh_lo' || k === 'sh_hi' || k === 'sh_top') return Math.round(100 + v) + '%';
  if (k === 'master') return Math.round(v) + '%';
  const s = d ? v.toFixed(d) : Math.round(v).toString();
  return ((u === 'dB' || k === 'sh_tilt' || k === 'gd_thr') && v > 0 ? '+' : '') + s + (u ? ' ' + u : '');
}

// ---------- knobs
function drawKnob(el) {
  const k = el.dataset.p, n = effN(k), c = el.dataset.c;
  el.querySelector('.ptr').setAttribute('transform', `rotate(${(-135 + 270 * n).toFixed(1)} ${c} ${c})`);
  $$('.dot', el).forEach(d => d.setAttribute('fill', +d.dataset.f <= n + 1e-6 ? '#9be36a' : '#3a454f'));
  const kv = document.querySelector(`.kval[data-v="${k}"]`); if (kv) kv.textContent = fmt(k);
  el.setAttribute('aria-valuetext', fmt(k));
}
function setN(k, v) {
  v = clamp(v);
  if (k === 'gd_rec') v = Math.round(v * 4) / 4;
  S[k].setNormalisedValue(v);
}
function bindKnob(el) {
  const k = el.dataset.p; let y0 = 0, n0 = 0, drag = false;
  el.addEventListener('pointerdown', e => { el.setPointerCapture(e.pointerId); drag = true; y0 = e.clientY; n0 = norm(k); S[k].sliderDragStarted(); e.preventDefault(); });
  el.addEventListener('pointermove', e => { if (!drag) return; const sens = e.shiftKey ? 1000 : 220; setN(k, n0 + (y0 - e.clientY) / sens); });
  const end = () => { if (drag) { drag = false; S[k].sliderDragEnded(); } };
  el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
  el.addEventListener('dblclick', () => { S[k].sliderDragStarted(); setN(k, (P[k][2] - P[k][0]) / (P[k][1] - P[k][0])); S[k].sliderDragEnded(); });
  el.addEventListener('wheel', e => { e.preventDefault(); setN(k, norm(k) - e.deltaY * (k === 'gd_rec' ? 0.004 : 0.0008)); }, { passive: false });
  el.addEventListener('keydown', e => {
    const step = k === 'gd_rec' ? 0.25 : (e.shiftKey ? 0.002 : 0.01);
    if (e.key === 'ArrowUp' || e.key === 'ArrowRight') { setN(k, norm(k) + step); e.preventDefault(); }
    if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') { setN(k, norm(k) - step); e.preventDefault(); }
  });
}

// ---------- toggles
function drawToggle(el) {
  const on = tog(el.dataset.t), col = LEDC[el.dataset.col] || LEDC.green, led = el.querySelector('.led');
  led.style.background = on ? col : (el.dataset.col === 'red' ? '#3b2424' : '#2c3a30');
  led.style.boxShadow = on ? `0 0 8px ${col}` : 'inset 0 1px 2px #000';
  el.setAttribute('aria-pressed', on ? 'true' : 'false');
}

// ---------- displays driven by parameters
function drawWaterfall() {
  const eng = (tog('e_haas') ? .35 : 0) + (tog('e_detune') ? .3 : 0) + (tog('e_chorus') ? .3 : 0) + (tog('e_comb') ? .25 : 0) + (tog('e_allpass') ? .3 : 0) + (tog('e_room') ? .2 : 0);
  const dec = tog('gen_on') ? effN('gen_amt') * Math.min(1.2, eng / 0.95) : 0;
  const wob = tog('e_chorus') ? effN('gen_rate') : 0, t = performance.now() / 1000;
  const back = $$('.wfb'); let bi = 0;
  for (let k = 0; k < WF.L; k++) {
    const depth = WF.L - 1 - k, ox = depth * WF.ox, oy = -depth * WF.oy;
    for (let ch = 0; ch < 2; ch++) {
      const p = [];
      for (let i = 0; i < 90; i++) {
        const u = i / 89, env = Math.pow(Math.sin(Math.PI * u), 0.8), ph = ch * (0.05 + dec * (0.6 + 0.35 * depth)) + depth * 0.4 + wob * Math.sin(t * 2 + depth) * ch;
        const y = Math.sin(u * 14 + ph) * 0.6 + Math.sin(u * 31 + ph * 1.7) * 0.25;
        p.push(f1(WF.xs + ox + u * WF.span) + ' ' + f1(WF.by + oy - y * env * 22));
      }
      const d = 'M ' + p.join(' L ');
      if (k === WF.L - 1) $(ch ? '#wfR' : '#wfL').setAttribute('d', d); else back[bi++].setAttribute('d', d);
    }
  }
  $('#cHaas').textContent = tog('gen_on') && tog('e_haas') ? effS('gen_time').toFixed(1) + 'ms' : 'OFF';
  $('#cDet').textContent = tog('gen_on') && tog('e_detune') ? '±' + Math.round(effS('gen_cents')) + 'ct' : 'OFF';
}
function drawWidth() {
  const on = tog('sh_on'), hz = bassHz(), bOn = hz >= 20;
  const tilt = (effN('sh_tilt') - 0.5) * 2;
  let g = [0, 100 + effS('sh_lo'), 100 + effS('sh_hi'), 100 + effS('sh_top')];
  for (let i = 1; i < 4; i++) g[i] *= Math.max(0, 1 + tilt * 0.5 * (i - 2));
  g[0] = bOn ? 0 : g[1];
  if (!on) g = [100, 100, 100, 100];
  const xo = [bOn ? hz : 20, 1200, 6000];
  const fx = fr => WC.l + (WC.r - WC.l) * (Math.log10(fr) - Math.log10(20)) / 3;
  const wy = v => WC.bot - (WC.bot - WC.top) * Math.min(200, v) / 200;
  const wat = fr => { let v = g[0]; for (let i = 0; i < 3; i++) { const k = 1 / (1 + Math.exp(-(Math.log10(fr) - Math.log10(xo[i])) * 14)); v += (g[i + 1] - g[i]) * k; } return v; };
  const pts = []; for (let i = 0; i < 160; i++) { const u = i / 159, fr = 20 * Math.pow(10, 3 * u); pts.push(f1(WC.l + (WC.r - WC.l) * u) + ' ' + f1(wy(wat(fr)))); }
  const line = 'M ' + pts.join(' L ');
  $('#wcLine').setAttribute('d', line); $('#wcFill').setAttribute('d', line + ` L ${WC.r} ${WC.bot} L ${WC.l} ${WC.bot} Z`);
  const L = $$('.xoL'), D = $$('.xoD'), TX = $$('.xoT');
  xo.forEach((fr, i) => { const x = f1(fx(fr)); L[i].setAttribute('x1', x); L[i].setAttribute('x2', x); D[i].setAttribute('cx', x); D[i].setAttribute('cy', f1(wy(wat(fr)))); TX[i].setAttribute('x', x); });
  TX[0].textContent = bOn ? Math.round(hz) : 'OFF'; L[0].style.opacity = bOn ? 1 : 0.2;
  $('#wcMono').style.opacity = bOn && on ? 1 : 0;
  $('#cXo').textContent = (bOn ? Math.round(hz) : 'off') + '·1.2k·6k';
}
function drawStage() {
  const on = tog('sp_on'), sh = on ? effN('sp_shuf') : 0, bey = on && tog('sp_beyond');
  const spread = 12 + 40 * sh + (bey ? 22 : 0) + (on ? (effN('sp_sus') - 0.5) * 16 : 0);
  let rate = effS('sp_mot'); const dep = on ? effN('sp_dep') : 0;
  const rot = dep * 25 * Math.sin(performance.now() / 1000 * 2 * Math.PI * rate);
  $$('.stD').forEach((c, i) => { const q = ST.dots[i], ang = q[0] * spread + rot, a = (-90 + ang) * Math.PI / 180, rr = q[1] * ST.R;
    c.setAttribute('cx', f1(ST.cx + rr * Math.cos(a))); c.setAttribute('cy', f1(ST.cy + rr * Math.sin(a))); c.setAttribute('fill', Math.abs(ang) < 30 ? '#ffe24d' : '#5cc8ff'); });
  $('#cShuf').textContent = on ? '+' + effS('sp_shuf').toFixed(1) + 'dB' : 'OFF';
  $('#cBey').textContent = bey ? 'ON' : 'OFF'; $('#cBey').style.color = bey ? '#5cc8ff' : '#ffb23e';
}
function drawThreshold() {
  const v = effS('gd_thr'), y = CH.top + (CH.bot - CH.top) * (1 - v) / 2;
  $('#thrL').setAttribute('y1', f1(y)); $('#thrL').setAttribute('y2', f1(y));
  $('#thrT').setAttribute('y', f1(y + 12)); $('#thrT').textContent = 'GUARD ' + (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2);
}
function drawHeader() {
  $('#mPct').textContent = Math.round(norm('master') * 200) + '%';
  const names = { link_gen: 'GEN', link_shape: 'SHAPE', link_space: 'SPACE' }, on = Object.keys(names).filter(tog);
  $('#mCount').textContent = on.length;
  $('#mChips').innerHTML = on.map(k => `<div class="chip">${names[k]} <span style="color:#9be36a">${Math.round(norm('master') * 200)}%</span></div>`).join('');
  $('#cBal').textContent = fmt('in_bal');
  ['in_on', 'gen_on', 'sh_on', 'sp_on', 'gd_on', 'out_on'].forEach((k, i) => $$('.mod')[i].classList.toggle('off', !tog(k)));
  $('#mode').textContent = mock ? 'PREVIEW (no audio)' : 'LIVE';
}
function redrawAll() { $$('.knob').forEach(drawKnob); $$('.tb').forEach(drawToggle); drawWaterfall(); drawWidth(); drawStage(); drawThreshold(); drawHeader(); }

// ---------- meters & scope from DSP
const corrHist = new Array(140).fill(1), pullHist = new Array(140).fill(0);
let scopePeak = 0.1;
const lvl = x => clamp((20 * Math.log10(Math.max(x, 1e-6)) + 60) / 66);
function setMeter(id, i, v) { $$(`.seg[data-m="${id}${i}"]`).forEach(r => r.setAttribute('opacity', +r.dataset.f <= v ? 0.95 : 0.12)); }
function onMeters(m) {
  setMeter('in', 0, lvl(m.inL)); setMeter('in', 1, lvl(m.inR));
  setMeter('out', 0, lvl(m.outL)); setMeter('out', 1, lvl(m.outR)); setMeter('out', 2, lvl(m.mid * 1.41)); setMeter('out', 3, lvl(m.side * 1.41));
  const live = (m.inL + m.inR) > 1e-4;
  $('#cSrc').textContent = !live ? '—' : (m.inCorr > 0.995 ? 'MONO' : 'STEREO');
  $('#cCorr').textContent = (m.corr >= 0 ? '+' : '−') + Math.abs(m.corr).toFixed(2);
  $('#cPull').textContent = m.pull > 0.005 ? '−' + Math.round(m.pull * 100) + '%' : '0%';
  $('#cM').textContent = (20 * Math.log10(Math.max(m.mid, 1e-5))).toFixed(1);
  $('#cS').textContent = (20 * Math.log10(Math.max(m.side, 1e-5))).toFixed(1);
  corrHist.push(m.corr); corrHist.shift(); pullHist.push(m.pull); pullHist.shift();
  const vy = v => CH.top + (CH.bot - CH.top) * (1 - clamp(v, -1, 1)) / 2;
  $('#chLine').setAttribute('d', 'M ' + corrHist.map((v, i) => f1(CH.l + (CH.r - CH.l) * i / 139) + ' ' + f1(vy(v))).join(' L '));
  $('#chPull').setAttribute('d', pullHist.map((v, i) => v > 0.005 ? `M ${f1(CH.l + (CH.r - CH.l) * i / 139)} ${CH.gy} h 2.2 v ${f1(4 + v * 30)} h -2.2 Z` : '').join(' '));
  // vectorscope (rotated 45°: mono = vertical)
  const pts = m.scope, w = SCW, h = 150, cx = w / 2, cy = h / 2, d = Math.min(w, h) * 0.43;
  let pk = 0; for (let i = 0; i < pts.length; i += 2) { const mm = (pts[i] + pts[i + 1]) / 2, ss = (pts[i] - pts[i + 1]) / 2; pk = Math.max(pk, Math.abs(mm), Math.abs(ss)); }
  scopePeak = Math.max(pk, scopePeak * 0.9, 0.02);
  const g = 0.95 / scopePeak, path = [];
  for (let i = 0; i < pts.length; i += 2) { const mm = (pts[i] + pts[i + 1]) / 2, ss = (pts[i] - pts[i + 1]) / 2; path.push(f1(cx - ss * d * g) + ' ' + f1(cy - mm * d * g)); }
  $('.sAll').setAttribute('d', path.length ? 'M ' + path.join(' L ') : '');
  $('.sHot').setAttribute('d', path.length ? 'M ' + path.slice(-60).join(' L ') : '');
}

// mock meters for browser preview: fake a signal whose width follows the knobs
let mt = 0;
function mockMeters() {
  const eng = (tog('e_detune') || tog('e_allpass') || tog('e_chorus') || tog('e_comb')) ? 1 : 0.4;
  let w = 0.05 + (tog('gen_on') ? effN('gen_amt') * eng : 0) * (tog('sh_on') ? 1 + effN('sh_top') * 0.6 : 1) * (tog('sp_on') ? 1 + effN('sp_shuf') * 0.4 : 1);
  if (tog('out_on')) w *= Math.pow(10, (effS('out_side') - effS('out_mid')) / 20);
  let corr = clamp(0.98 - 0.85 * w, -1, 1), pull = 0;
  if (tog('gd_on') && tog('gd_auto') && corr < effS('gd_thr')) { pull = clamp((effS('gd_thr') - corr) * 1.5, 0, 0.85); w *= 1 - pull; corr = 0.98 - 0.85 * w; }
  if (tog('out_mono')) { w = 0; corr = 1; } if (tog('out_bypass')) { w = 0; corr = 1; pull = 0; }
  const sc = [];
  for (let i = 0; i < 400; i++) { mt += 1; const t = mt / 60; const m = 0.5 * Math.sin(t * 1.3) + 0.24 * Math.sin(t * 3.7 + 1) + 0.1 * Math.sin(t * 9.1);
    const s = (0.4 * Math.sin(t * 2.1 + .5) + 0.25 * Math.sin(t * 5.3)) * w; sc.push(m + s, m - s); }
  const lv = 0.25 * Math.pow(10, effS('in_trim') / 20);
  onMeters({ inL: lv, inR: lv, outL: lv * (1 + w * .2) * Math.pow(10, effS('out_gain') / 20), outR: lv * (1 + w * .2) * Math.pow(10, effS('out_gain') / 20), mid: lv * .7, side: lv * .7 * w, corr, inCorr: 1, pull, scope: sc });
}

function init() {
  for (const k in P) { S[k] = Juce.getSliderState(k); S[k].valueChangedEvent.addListener(redrawAll); }
  for (const k in T) { TG[k] = Juce.getToggleState(k); TG[k].valueChangedEvent.addListener(redrawAll); }
  $$('.knob').forEach(bindKnob);
  $$('.tb').forEach(el => el.addEventListener('click', () => { const k = el.dataset.t; TG[k].setValue(!tog(k)); }));
  if (!mock) window.__JUCE__.backend.addEventListener('meters', onMeters); else setInterval(mockMeters, 33);
  const anim = () => { drawStage(); if (tog('e_chorus')) drawWaterfall(); requestAnimationFrame(anim); }; anim();
  redrawAll();
}
boot();
"""
for k, v in (("__P__", json.dumps(P)), ("__T__", json.dumps(T)), ("__LINKED__", json.dumps(LINKED)), ("__WF__", json.dumps(WF)),
             ("__WC__", json.dumps(WC)), ("__ST__", json.dumps(ST)), ("__CH__", json.dumps(CH)), ("__SCW__", str(SCW)), ("__W__", str(W)), ("__H__", str(H))):
    JS = JS.replace(k, v)

corners = "".join(f'<div class="corner" style="{p}">{screw()}</div>' for p in ("top:10px;left:10px", "top:10px;right:10px", "bottom:10px;left:10px", "bottom:10px;right:10px"))
html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Spread</title><style>{CSS}</style></head><body>'
        f'<main id="app">{corners}{header}<div class="rack">{"".join(mods)}</div></main>'
        f'<script type="module">{JS}</script></body></html>')
open("/home/claude/spread-plugin/ui/index.html", "w").write(html)
print("ui ok", len(html))
