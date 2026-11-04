import base64, math, json, re, sys
# Reuse parameter table, info text and display-frame builders from the v0.2 generator
g_src = open("/home/claude/gen_ui.py").read()
defs = g_src.split("wf, WF = wf_frame(SCW, 164)")[0]
defs = defs.replace("L = 9; ox = 11; oy = 9;", "L = 9; ox = 11; oy = 6;")
defs = defs.replace("cx = w/2; cy = h - 18; R1 = h - 36", "cx = w/2; cy = h - 18; R1 = min(h - 36, w/2 - 14)")
exec(defs)
T['in_dlyside'] = 0
INFO['in_dlyside'] = "L / R — which channel the CH. DELAY is applied to. Delaying one side shifts the image toward the other."
INFO['in_dly'] = "CH. DELAY — delays one channel 0–20 ms (pick L or R below). A quick Haas-style widen on the raw input."
JS = g_src.split('JS = r"""')[1].split('"""')[0]
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/spread-plugin/ui/index.html"
PREVIEW = "--preview" in sys.argv
import os
H = int(os.environ.get("UIH", H))

# ---------------------------------------------------------------- new light palette
ACC = "#f05a1a"      # orange accent (fills, arcs)
ACCT = "#c4420c"     # orange for text on white (4.5:1)
INKD = "#2f3338"; GREY = "#6b737b"; SOFT = "#8c939a"
TRACE, HOT, SIDE, AMBER = INKD, ACC, "#7f8c99", ACC
FW = "'Michroma', sans-serif"; FT = "'Manrope', sans-serif"
MONO = FT

def knobP(R, name, pid, labels=None, kind=None, skirt=False, ndots=13, lit=False, namesize=11, bi=None):
    pad = 30 if labels else 14
    S = 2 * (R + pad); c = S / 2
    g = uid(); p = []
    bip = pid in ("in_bal", "in_trim", "sh_tilt", "gd_thr", "out_mid", "out_side", "out_gain")
    p.append(f'<defs><radialGradient id="{g}d" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#f6f7f9"/><stop offset="1" stop-color="#d8dce1"/></radialGradient>'
             f'<filter id="{g}f" x="-40%" y="-40%" width="180%" height="190%"><feDropShadow dx="0" dy="{max(3, R*0.14):.1f}" stdDeviation="{max(3, R*0.16):.1f}" flood-color="#1c2430" flood-opacity="0.32"/></filter>'
             f'<radialGradient id="{g}p" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="#cfd4da"/><stop offset="1" stop-color="#eef0f3"/></radialGradient></defs>')
    nt = 41 if R >= 34 else 27
    for i in range(nt):
        fr = i / (nt - 1); a = math.radians(-135 + 270 * fr - 90)
        major = i % 5 == 0
        r1 = R + 9; r2 = R + (15 if major else 12)
        p.append(f'<line x1="{f(c + r1*math.cos(a))}" y1="{f(c + r1*math.sin(a))}" x2="{f(c + r2*math.cos(a))}" y2="{f(c + r2*math.sin(a))}" stroke="{"#a9b0b8" if major else "#c9ced4"}" stroke-width="1.2" stroke-linecap="round"/>')
    if labels:
        for fr, t in labels:
            a = math.radians(-135 + 270 * fr - 90); rr = R + 25
            p.append(f'<text x="{f(c + rr*math.cos(a))}" y="{f(c + rr*math.sin(a) + 4)}" fill="{SOFT}" font-family="{FT}" font-size="10.5" font-weight="600" text-anchor="middle">{t}</text>')
    ra = R + 4
    # groove + value arc
    p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(ra)}" fill="none" stroke="#e3e6ea" stroke-width="4"/>')
    p.append(f'<path class="arc" data-r="{f(ra)}" data-bi="{1 if bip else 0}" d="" fill="none" stroke="{ACC}" stroke-width="4" stroke-linecap="round"/>')
    p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R)}" fill="url(#{g}d)" filter="url(#{g}f)" stroke="#b9c0c8" stroke-width="1.2"/>')
    p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R*0.8)}" fill="none" stroke="#ffffff" stroke-width="1.5" opacity="0.9"/>')
    p.append(f'<circle cx="{f(c)}" cy="{f(c)}" r="{f(R*0.8 + 1.2)}" fill="none" stroke="#d2d7dd" stroke-width="1"/>')
    dr = max(2.1, R * 0.08)
    p.append(f'<g class="ptr"><circle class="pdot" cx="{f(c)}" cy="{f(c - R*0.66)}" r="{f(dr)}" fill="#2f3338" stroke="#2f3338" stroke-width="0.8"/></g>')
    svg = f'<svg width="{int(S)}" height="{int(S)}" viewBox="0 0 {int(S)} {int(S)}" aria-hidden="true">' + "".join(p) + '</svg>'
    link = LINKED.get(pid, "")
    lab = f'<div class="kname{"" if labels else " ksm"}">{name}</div>' if name else ""
    return (f'<div class="kwrap"><div class="knob" tabindex="0" role="slider" aria-label="{name or "Master"}" data-info="{esc(INFO.get(pid, ""))}" data-p="{pid}" data-c="{c}" data-link="{link}" style="width:{int(S)}px;height:{int(S)}px">{svg}</div>'
            f'{lab}<div class="kval" data-v="{pid}"></div></div>')

def fader(name, pid, H=200):
    W_ = 64; tx = W_/2; top = 30; bot = H - 30
    bip = pid in ("in_bal", "in_trim", "sh_tilt", "gd_thr", "out_mid", "out_side", "out_gain")
    g = uid(); p = []
    p.append(f'<defs><linearGradient id="{g}c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#eef0f3"/><stop offset="1" stop-color="#dfe3e7"/></linearGradient>'
             f'<filter id="{g}f" x="-60%" y="-60%" width="220%" height="220%"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#1c2430" flood-opacity="0.32"/></filter></defs>')
    # tick marks either side
    for i in range(11):
        y = top + (bot-top)*i/10; major = i % 5 == 0; L = 8 if major else 5
        for sx in (-1, 1):
            x0 = tx + sx*12; x1 = tx + sx*(12+L)
            p.append(f'<line x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}" stroke="{"#a9b0b8" if major else "#c9ced4"}" stroke-width="1.2" stroke-linecap="round"/>')
    # groove
    p.append(f'<rect x="{f(tx-3)}" y="{top}" width="6" height="{bot-top}" rx="3" fill="#e3e6ea"/>')
    p.append(f'<rect class="ffill" data-top="{top}" data-bot="{bot}" data-bi="{1 if bip else 0}" x="{f(tx-3)}" y="{bot}" width="6" height="0" rx="3" fill="#f05a1a"/>')
    # cap
    ridges = "".join(f'<rect x="{f(tx-7)}" y="{y}" width="14" height="1.6" rx="0.8" fill="#c9ced4"/>' for y in (-17, -12, 7, 12))
    p.append(f'<g class="fcap"><rect x="{f(tx-11)}" y="-26" width="22" height="52" rx="5" fill="url(#{g}c)" stroke="#b9c0c8" stroke-width="1.2" filter="url(#{g}f)"/>'
             f'<rect x="{f(tx-9.5)}" y="-24.5" width="19" height="49" rx="4" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.9"/>'
             f'{ridges}<rect class="fline" x="{f(tx-8)}" y="-1.2" width="16" height="2.4" rx="1.2" fill="#2f3338"/></g>')
    svg = f'<svg width="{W_}" height="{H}" viewBox="0 0 {W_} {H}" aria-hidden="true" style="overflow:visible">' + "".join(p) + '</svg>'
    return (f'<div class="kwrap"><div class="knob fader" tabindex="0" role="slider" aria-label="{name}" data-info="{esc(INFO.get(pid, ""))}" data-p="{pid}" data-c="0" data-link="" style="width:{W_}px;height:{H}px">{svg}</div>'
            f'<div class="kname ksm">{name}</div><div class="kval" data-v="{pid}"></div></div>')

def tbtn(text, pid, col="green", small=True):
    return (f'<button type="button" class="tb" data-t="{pid}" data-col="{col}" data-info="{esc(INFO.get(pid, ""))}"><span class="tl">{text}</span></button>')

def bez(btns, cols=2):
    return f'<div class="bgrid" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{"".join(btns)}</div>'

def scr(svg, chips=""):
    ch_ = f'<div class="chips">{chips}</div>' if chips else ""
    return f'<div class="screen">{svg}{ch_}</div>'

def ch(label, cid, color=INKD, init="—"):
    col = ACCT if color in (ACC, HOT, AMBER) else (GREY if color == SIDE else INKD)
    return f'<div class="chip">{label} <span id="{cid}" style="color:{col}">{init}</span></div>'

def svgbox(w, h, inner, sid, aria):
    return f'<svg id="{sid}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{aria}" style="display:block"><rect width="{w}" height="{h}" fill="#0b100f"/>{inner}</svg>'

def meter_frame(w, h, labels, mid):
    n = len(labels); bw = 6; gap = (w - n*bw) / (n + 1); top = 12; bot = h - 22
    s = []
    for i, t in enumerate(labels):
        x = gap + i*(bw+gap)
        s.append(f'<rect x="{f(x)}" y="{top}" width="{bw}" height="{bot-top}" rx="3" fill="#dde1e5"/>')
        s.append(f'<rect class="mbar" data-m="{mid}{i}" data-top="{top}" data-bot="{bot}" x="{f(x)}" y="{bot}" width="{bw}" height="0" rx="3" fill="{INKD}"/>')
        for k in range(0, 7):
            yy = top + (bot-top)*k/6
            s.append(f'<line x1="{f(x+bw+3)}" y1="{f(yy)}" x2="{f(x+bw+6)}" y2="{f(yy)}" stroke="#c4cad0"/>')
        s.append(f'<text x="{f(x+bw/2)}" y="{h-7}" fill="{SOFT}" font-family="{FT}" font-size="10" font-weight="700" text-anchor="middle">{t}</text>')
    return "".join(s)

POWER = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.8v5.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M4.6 3.9a5.2 5.2 0 1 0 6.8 0" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'

LINKI = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M6.6 9.4l2.8-2.8M7 4.6l1.2-1.2a2.8 2.8 0 0 1 4 4L11 8.6M9 11.4l-1.2 1.2a2.8 2.8 0 0 1-4-4L5 7.4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>'
def module(title, body, link=None, power=None):
    pw = f'<button type="button" class="pwr" data-t="{power}" data-info="{esc("POWER — orange = this section is on. Click to bypass it; the audio passes through untouched.")}" aria-label="{title} on/off">{POWER}</button>'
    ib = f'<button type="button" class="ib" aria-label="About {title}" data-info="{esc(MODINFO[title])}" data-always="1">i</button>'
    lk = (f'<button type="button" class="lnk" data-t="{link}" aria-label="Link {title} to master" data-info="{esc(INFO[link])}">{LINKI}</button>') if link else ''
    return (f'<section class="mod" data-mod="{title.lower()}" aria-label="{title}"><div class="mhead">{pw}<h2>{title}</h2><div class="hgrp">{lk}{ib}</div></div>'
            f'{body}</section>')

def row(*items):
    return f'<div class="row">{"".join(items)}</div>'

wf, WF = wf_frame(SCW, 164); wc, WC = wc_frame(SCW, 164); st, ST = st_frame(SCW, 164); chh, CH = ch_frame(SCW, 164)
def big(x): return f'<div class="big">{x}</div>'
def slot2(x): return f'<div class="big2">{x}</div>'
def rowb(x): return f'<div class="row rowb">{x}</div>'
K = 20   # every small knob the same size
mods = [
 module("Input",
   scr(svgbox(SCW, 164, meter_frame(SCW, 164, ["L", "R"], "in"), "inMeters", "Input meters"), ch("SRC", "cSrc", SIDE) + ch("BAL", "cBal"))
   + big(knobP(38, "Balance", "in_bal", labels=[(0, "L"), (0.5, "C"), (1, "R")]))
   + f'<div class="frow">{fader("Trim", "in_trim")}<div class="kwrap">{fader("Ch. delay", "in_dly")}<div class="seg lr" role="group" aria-label="Delay side"><button type="button" class="tb lrb" data-lr="0" data-info="{esc(INFO["in_dlyside"])}"><span class="tl">L</span></button><button type="button" class="tb lrb" data-lr="1" data-info="{esc(INFO["in_dlyside"])}"><span class="tl">R</span></button></div></div></div>'
   + '<div style="flex-grow:1"></div>'
   + bez([tbtn("Ø L", "in_phl", "red"), tbtn("Ø R", "in_phr", "red"), tbtn("Swap", "in_swap"), tbtn("Mono in", "in_mono")]),
   power="in_on"),
 module("Generate",
   scr(svgbox(SCW, 164, wf, "wf", "Decorrelation display"), ch("HAAS", "cHaas") + ch("DET", "cDet", HOT))
   + big(knobP(38, "Amount", "gen_amt", labels=[(0, "0"), (0.5, "50"), (1, "100")]))
   + row(knobP(K, "Time", "gen_time"), knobP(K, "Cents", "gen_cents"))
   + row(knobP(K, "Rate", "gen_rate"), knobP(K, "Size", "gen_size"))
   + bez([tbtn("Haas", "e_haas"), tbtn("Detune", "e_detune"), tbtn("Chorus", "e_chorus"), tbtn("Comb", "e_comb"), tbtn("Allpass", "e_allpass"), tbtn("Room", "e_room")]),
   link="link_gen", power="gen_on"),
 module("Shape",
   scr(svgbox(SCW, 164, wc, "wc", "Width per band"), ch("BANDS", "cBands", INKD, "4") + ch("XO", "cXo", SIDE))
   + big(knobP(38, "Bass mono", "sh_bass", labels=[(0, "OFF"), (0.5, "150"), (1, "300")]))
   + row(knobP(K, "Lo-mid", "sh_lo"), knobP(K, "Hi-mid", "sh_hi"), knobP(K, "High", "sh_top"))
   + row(knobP(K, "Side tilt", "sh_tilt"), knobP(K, "Side drive", "sh_drive"))
   + bez([tbtn("Solo S", "solo_s", "red"), tbtn("Solo M", "solo_m", "red")]),
   link="link_shape", power="sh_on"),
 module("Space",
   scr(svgbox(SCW, 164, st, "st", "Sound stage"), ch("SHUF", "cShuf") + ch("BEYOND", "cBey", AMBER))
   + big(knobP(38, "Shuffle", "sp_shuf", labels=[(0, "0"), (0.5, "+3"), (1, "+6")]))
   + row(knobP(K, "Transient", "sp_tr"), knobP(K, "Sustain", "sp_sus"))
   + row(knobP(K, "Motion", "sp_mot"), knobP(K, "Depth", "sp_dep"))
   + bez([tbtn("Beyond", "sp_beyond"), tbtn("Sync", "sp_sync")]),
   link="link_space", power="sp_on"),
 module("Guard",
   scr(svgbox(SCW, 164, chh, "ch", "Correlation history"), ch("CORR", "cCorr") + ch("PULL", "cPull", AMBER))
   + big(knobP(38, "Threshold", "gd_thr", labels=[(0, "−.5"), (0.5, "0"), (1, "+.5")]))
   + slot2(knobP(38, "Recovery", "gd_rec", labels=[(0, "100"), (0.25, "400"), (0.5, "800"), (0.75, "1.5s"), (1, "AUTO")]))
   + bez([tbtn("Auto", "gd_auto"), tbtn("Listen", "gd_listen", "red")]),
   power="gd_on"),
 module("Output",
   scr(svgbox(SCW, 164, scope_frame(SCW, 164), "scope", "Output vectorscope"), ch("M", "cM") + ch("S", "cS", SIDE))
   + big(scr(svgbox(SCW, 150, meter_frame(SCW, 150, ["L", "R", "M", "S"], "out"), "outMeters", "Output meters")))
   + row(knobP(K, "Mid", "out_mid"), knobP(K, "Side", "out_side"))
   + row(knobP(K, "Mix", "out_mix"), knobP(K, "Output", "out_gain"))
   + bez([tbtn("Mono", "out_mono", "red"), tbtn("Bypass all", "out_bypass", "red")]),
   power="out_on"),
]

master = knobP(42, "", "master", labels=[(0, "0"), (0.5, "100"), (1, "200")])
sizes = "".join(f'<button type="button" class="tb szb" data-s="{s}" aria-label="Window size {lab}"><span class="tl">{lab}</span></button>' for s, lab in ((0.6, "S"), (0.8, "M"), (1.0, "L"), (1.25, "XL"), (1.5, "XXL")))
header = (f'<header class="top">'
          f'<div class="brand"><div class="wm"><span class="sup">SUPER</span>SPREAD</div><div class="tag">STEREO WORKBENCH</div></div>'
          f'<div class="mastergrp">{master}<div class="minfo"><div class="mtitle">MASTER <span id="mPct">100%</span></div>'
          f'<div class="msub">drag up / down · 100% = knobs as set · keeps their balance</div>'
          f'<div class="msub">drives <span id="mCount">3</span> linked sections</div>'
          f'<div id="mChips" class="mchips"></div></div></div>'
          f'<div class="hright"><div class="hctl"><span class="lbl">SIZE</span><div class="seg">{sizes}</div>'
          f'<button type="button" id="infoBtn" class="tb" aria-pressed="true" data-info="INFO — hover any knob or button to see what it does. Click to turn these tips off or on."><span class="tl">Info</span></button></div>'
          f'<div class="ver">VER. 0.3.0 <span id="mode">—</span></div></div></header>')


VARIANT = os.environ.get("VARIANT", "C")
mpct = '<span id="mPct">100%</span>'
seg = f'<div class="seg">{sizes}</div>'
infob = '<button type="button" id="infoBtn" class="tb" aria-pressed="true" data-info="INFO — hover any knob or button to see what it does. Click to turn these tips off or on."><span class="tl">Info</span></button>'
brand = '<div class="brand"><div class="wm"><span class="sup">SUPER</span>SPREAD</div><div class="tag">STEREO WORKBENCH</div></div>'
ver = '<div class="ver">VER. 0.3.0 <span id="mode">—</span></div>'
rack_mods = list(mods)
if VARIANT in ("B", "C"):
    mk = knobP(56, "", "master", labels=[(0, "0"), (0.5, "100"), (1, "200")])
    mcard = (f'<section class="mod mcard" aria-label="Master"><div class="mtop"><h2>MASTER</h2></div>'
             f'<div class="well">{mk}</div><div class="mbig">{mpct}</div>'
             f'<div class="msub c">keeps the balance of<br>every linked section</div>'
             f'<div class="lbl c" style="margin-top:6px">DRIVING <span id="mCount">3</span></div><div id="mChips" class="mchips col"></div>'
             + ('<div style="flex-grow:1"></div>' + f'<div class="cbot"><div class="hctl col"><span class="lbl">THEME</span><div class="swatches" role="group" aria-label="Theme"><button type="button" class="thb sw sw-light" data-th="light" aria-label="Light theme" data-info="THEME — Light"></button><button type="button" class="thb sw sw-dark" data-th="dark" aria-label="Dark theme" data-info="THEME — Dark"></button><button type="button" class="thb sw sw-violet" data-th="violet" aria-label="Violet theme" data-info="THEME — Violet"></button><button type="button" class="thb sw sw-color" data-th="color" aria-label="Tropic theme" data-info="THEME — Tropic, a colour per section"></button></div><span class="lbl">SIZE</span>{seg}{infob}</div>{ver}</div>' if VARIANT == "C" else "")
             + '</section>')
    if VARIANT == "B":
        rack_mods.insert(4, mcard)
        header = f'<header class="top slim">{brand}<div class="hright"><div class="hctl"><span class="lbl">SIZE</span>{seg}{infob}</div>{ver}</div></header>'
    else:
        mcard = mcard.replace('<div class="mtop"><h2>MASTER</h2></div>', f'<div class="cbrand">{brand}</div><div class="mtop"><h2>MASTER</h2></div>')
        rack_mods.insert(0, mcard)
        header = ""
    W = W + 254
elif VARIANT == "A":
    header = header.replace('<header class="top">', '<header class="top bar">')
fonts = ""
for fam, wt, fn in (("Michroma", "400", "Michroma-Regular.ttf"), ("Manrope", "200 800", "Manrope[wght].ttf")):
    b64 = base64.b64encode(open(f"/home/claude/fonts/{fn}", "rb").read()).decode()
    fonts += f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:normal;src:url(data:font/ttf;base64,{b64}) format('truetype');}}\n"

CSS = f"""{fonts}
html,body{{margin:0;height:100%;background:#e4e7ec;overflow:hidden;user-select:none;-webkit-user-select:none}}
#app{{width:{W}px;height:{H}px;transform-origin:0 0;position:absolute;left:0;top:0;box-sizing:border-box;background:#eef0f3;padding:18px 28px 36px;display:flex;flex-direction:column;gap:14px;overflow:hidden;font-family:{FT};color:{INKD}}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:0 10px}}
.brand .wm{{font-family:{FW};font-size:28px;letter-spacing:.16em;color:{INKD}}}
.brand .sup{{color:{ACC}}}\n.brand .wm{{color:#111315}}
.brand .tag{{font-family:{FT};font-weight:700;font-size:11px;letter-spacing:.42em;color:{SOFT};margin-top:6px}}
.mastergrp{{display:flex;align-items:center;gap:18px}}
.mtitle{{font-family:{FW};font-size:16px;letter-spacing:.2em;color:{INKD}}}
.mtitle span{{color:{ACCT}}}
.msub{{font-size:12px;font-weight:500;color:{GREY};margin-top:5px}}
.mchips{{display:flex;gap:5px;min-height:26px;margin-top:6px}}
.hright{{display:flex;flex-direction:column;align-items:flex-end;gap:12px}}
.hctl{{display:flex;align-items:center;gap:10px}}
.lbl{{font-weight:700;font-size:11px;letter-spacing:.2em;color:{SOFT}}}
.seg{{display:flex;background:#e2e5e9;border-radius:20px;padding:3px;gap:2px;box-shadow:inset 0 1px 3px rgba(20,30,40,.12)}}
.seg .tb{{min-height:30px;padding:0 13px;border:none;background:transparent;box-shadow:none;border-radius:16px}}
.seg .tb[aria-pressed="true"]{{background:#ffffff;color:{INKD};border:none;box-shadow:0 1px 4px rgba(20,30,40,.18)}}
.swatches{{display:flex;gap:10px;padding:4px 2px}}
.sw{{-webkit-appearance:none;appearance:none;display:inline-block;line-height:0;width:22px;height:22px;border-radius:50%;border:2px solid rgba(0,0,0,.12);background-clip:border-box;padding:0;margin:0;cursor:pointer;box-shadow:0 2px 5px rgba(var(--sh),.18);transition:transform .15s}}
.sw:hover{{transform:scale(1.12)}}
.sw[aria-pressed="true"]{{box-shadow:0 0 0 2px var(--ceef0f3),0 0 0 4px var(--cf05a1a)}}
.sw-light{{background:#d9dde2}}.sw-dark{{background:#1a1d22}}.sw-violet{{background:#5b4fb5}}.sw-color{{background:linear-gradient(90deg,#2fa84f 0 25%,#0ea5c9 25% 50%,#8b5cf6 50% 75%,#e23d3d 75% 100%)}}
.ver{{font-family:{FW};font-size:10px;letter-spacing:.2em;color:{SOFT}}}
.ver span{{font-family:{FT};font-weight:600;letter-spacing:.06em;margin-left:8px}}
.rack{{display:flex;justify-content:center;gap:12px;flex-grow:1;min-height:0}}
.mod{{width:{MODW}px;box-sizing:border-box;background:linear-gradient(#f9fafb,#f3f4f6);border-radius:22px;box-shadow:0 10px 24px rgba(30,40,55,.10),0 1px 0 #ffffff inset,0 0 0 1px #e3e6ea;padding:12px 11px 16px;display:flex;flex-direction:column;gap:8px;min-height:0;overflow:hidden}}
.mod.off>*:not(.mhead):not(.foot){{opacity:.35;filter:grayscale(1)}}
.mod.off .mhead h2{{color:#a6adb4}}
.mhead{{display:flex;justify-content:space-between;align-items:center;padding:0 2px 4px}}
.mhead h2{{margin:0;font-family:{FW};font-weight:400;font-size:12px;letter-spacing:.18em;color:{INKD};text-transform:uppercase}}
.pwr{{width:34px;height:34px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 40% 30%,#ffffff,#eceef1);box-shadow:0 3px 8px rgba(30,40,55,.16),0 0 0 1px #e1e4e8;color:#a7aeb6;padding:0}}
.pwr[aria-pressed="true"]{{color:{ACC}}}
.hgrp{{display:flex;gap:6px;align-items:center}}
.lnk{{width:30px;height:26px;border-radius:13px;border:1.5px solid #d6dade;background:#ffffff;color:#a7aeb6;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0}}
.lnk[aria-pressed="true"]{{border-color:{ACC};color:{ACC};box-shadow:0 2px 6px rgba(240,90,26,.2)}}
.ib{{width:26px;height:26px;border-radius:50%;border:1.5px solid #d3d8dd;background:transparent;color:{GREY};font-family:Georgia,serif;font-style:italic;font-weight:700;font-size:14px;cursor:help;padding:0}}
.ib:hover{{color:{ACCT};border-color:{ACC}}}
.screen{{background:#eceef1;border-radius:14px;overflow:hidden;box-shadow:inset 0 2px 7px rgba(20,30,40,.13),inset 0 0 0 1px #e0e3e7;display:flex;flex-direction:column;flex-shrink:0;transition:box-shadow .25s}}
:root.color .mod>.mhead+.screen{{box-shadow:inset 0 2px 7px rgba(0,0,0,.25)}}
.chips{{display:flex;gap:4px;flex-wrap:wrap;padding:6px 7px 7px;background:#e6e9ec}}
.chip{{background:#ffffff;padding:4px 9px;border-radius:10px;font-size:12px;font-weight:600;color:{SOFT};white-space:nowrap;box-shadow:0 1px 2px rgba(20,30,40,.08)}}
.bgrid{{display:grid;gap:6px}}
.tb{{display:flex;align-items:center;justify-content:center;min-height:36px;padding:0 10px;background:linear-gradient(#ffffff,#f3f4f6);border:1.5px solid #d6dade;border-radius:18px;box-shadow:0 2px 5px rgba(30,40,55,.07);font-family:{FT};font-weight:700;font-size:12.5px;letter-spacing:.1em;color:{GREY};cursor:pointer;text-transform:uppercase}}
.tb[aria-pressed="true"]{{border-color:{ACC};color:{ACCT};background:#ffffff;box-shadow:0 2px 8px rgba(240,90,26,.18)}}
.tb[data-col="red"][aria-pressed="true"]{{background:{ACC};color:#fffffe;border-color:{ACC}}}
.tb:active{{transform:translateY(1px)}}
.tb:focus-visible,.knob:focus-visible,.pwr:focus-visible,.ib:focus-visible{{outline:2px solid {ACC};outline-offset:3px}}
.foot{{display:flex;justify-content:center;min-height:36px}}
.foot .tb{{padding:0 18px}}
.kwrap{{display:flex;flex-direction:column;align-items:center}}
.knob{{position:relative;cursor:ns-resize;touch-action:none;border-radius:50%}}
.knob svg{{display:block;overflow:visible;flex-shrink:0}}
.kwrap,.bgrid,.frow,.big,.big2{{flex-shrink:0}}
.kname{{margin-top:-10px;font-weight:800;font-size:10.5px;letter-spacing:.14em;color:#4a5057;text-transform:uppercase;text-align:center}}
.kval{{font-weight:600;font-size:11px;color:{SOFT};text-align:center;margin-top:2px;min-height:14px}}
.row{{display:flex;justify-content:space-around;align-items:flex-start;height:100px;flex-shrink:0}}
.frow{{display:flex;justify-content:space-around;align-items:flex-start;padding-top:6px}}
.seg.lr{{margin-top:6px}}
.seg.lr .tb{{min-height:24px;padding:0 10px;font-size:11px}}
.fader{{cursor:ns-resize;border-radius:8px}}
.fader .kname{{margin-top:6px}}
.ksm{{margin-top:0}}
.rowb{{align-items:center}}
.rowb .bgrid{{width:100%}}
.big{{height:158px;flex-shrink:0;display:flex;justify-content:center;align-items:flex-start}}
.big .screen{{width:100%}}
.big2{{height:208px;flex-shrink:0;display:flex;justify-content:center;align-items:center}}
.bar{{background:linear-gradient(#f9fafb,#f3f4f6);border-radius:22px;box-shadow:0 10px 24px rgba(30,40,55,.10),0 0 0 1px #e3e6ea;padding:12px 26px;margin:0 6px}}
.bar .mastergrp{{background:#e9ecef;border-radius:90px;padding:8px 34px 8px 8px;box-shadow:inset 0 2px 8px rgba(20,30,40,.14),inset 0 0 0 1px #e0e3e7}}
.slim{{padding:4px 10px 0}}
.mcard{{background:linear-gradient(#ffffff,#f4f5f7);box-shadow:0 16px 34px rgba(30,40,55,.16),0 0 0 1px #e3e6ea;align-items:center}}
.mtop h2{{margin:4px 0 0;font-family:{FW};font-weight:400;font-size:13px;letter-spacing:.3em;color:{INKD}}}
.well{{margin-top:8px;width:212px;height:212px;border-radius:50%;background:#e9ecef;box-shadow:inset 0 3px 10px rgba(20,30,40,.16),inset 0 0 0 1px #e0e3e7;display:flex;align-items:center;justify-content:center}}
.mbig{{font-family:{FW};font-size:30px;letter-spacing:.06em;color:{ACCT};margin-top:10px}}
.mbig span{{color:inherit}}
.c{{text-align:center}}
.mchips.col{{flex-direction:column;align-items:center;gap:6px}}
.cbrand{{width:100%;padding:6px 4px 14px;border-bottom:1px solid #e3e6ea;margin-bottom:6px}}
.cbrand .wm{{font-size:17px;letter-spacing:.08em}}
.well .kval{{display:none}}
.cbrand .tag{{letter-spacing:.3em;font-size:10px}}
.hctl.col{{flex-direction:column;gap:8px}}
.cbot{{display:flex;flex-direction:column;align-items:center;gap:10px;width:100%}}
.vC .ver{{text-align:center}}
#tip{{position:absolute;z-index:50;max-width:300px;pointer-events:none;background:#ffffff;border-radius:12px;box-shadow:0 10px 28px rgba(20,30,40,.22),0 0 0 1px #e3e6ea;padding:11px 13px;font-family:{FT};font-weight:500;font-size:13px;line-height:1.4;color:{INKD};display:none}}
#tip b{{color:{ACCT};font-weight:800;letter-spacing:.06em}}
"""

# ---------------------------------------------------------------- JS adjustments for the new look
def jrep(a, b):
    global JS
    assert a in JS, a[:70]
    JS = JS.replace(a, b)
jrep("""  el.querySelector('.ptr').setAttribute('transform', `rotate(${(-135 + 270 * n).toFixed(1)} ${c} ${c})`);""",
"""  const ff = el.querySelector('.ffill');
  if (ff) {
    const top = +ff.dataset.top, bot = +ff.dataset.bot, y = bot - (bot - top) * n, mid = (top + bot) / 2;
    const y0 = ff.dataset.bi === '1' ? mid : bot, a = Math.min(y, y0), h = Math.abs(y - y0);
    ff.setAttribute('y', a.toFixed(1)); ff.setAttribute('height', h.toFixed(1));
    const active = ff.dataset.bi === '1' ? Math.abs(n - 0.5) > 0.004 : n > 0.004;
    ff.setAttribute('fill', ACC(el)); ff.style.opacity = active ? 1 : 0;
    el.querySelector('.fcap').setAttribute('transform', `translate(0 ${y.toFixed(1)})`);
    el.querySelector('.fline').setAttribute('fill', active ? ACC(el) : (DARK ? '#6b7682' : '#b4bbc3'));
    const kv2 = document.querySelector(`.kval[data-v="${k}"]`); if (kv2) kv2.textContent = fmt(k); el.setAttribute('aria-valuetext', fmt(k)); return;
  }
  el.querySelector('.ptr').setAttribute('transform', `rotate(${(-135 + 270 * n).toFixed(1)} ${c} ${c})`);
  const arc = el.querySelector('.arc');
  if (arc) {
    const r = +arc.dataset.r, cc = +c, a0 = arc.dataset.bi === '1' ? 0 : -135, a1 = -135 + 270 * n;
    const lo = Math.min(a0, a1), hi = Math.max(a0, a1), pt = a => { const t = (a - 90) * Math.PI / 180; return (cc + r * Math.cos(t)).toFixed(1) + ' ' + (cc + r * Math.sin(t)).toFixed(1); };
    arc.setAttribute('d', hi - lo < 0.5 ? '' : `M ${pt(lo)} A ${r} ${r} 0 ${hi - lo > 180 ? 1 : 0} 1 ${pt(hi)}`);
    arc.setAttribute('stroke', ACC(el));
    const dot = el.querySelector('.pdot');
    if (dot) { const active = arc.dataset.bi === '1' ? Math.abs(n - 0.5) > 0.004 : n > 0.004; const col = active ? ACC(el) : (DARK ? '#6b7682' : '#b4bbc3');
      dot.setAttribute('fill', col); dot.setAttribute('stroke', col); }
  }""")
jrep("""  const on = el.dataset.inv ? !tog(el.dataset.t) : tog(el.dataset.t), col = LEDC[el.dataset.col] || LEDC.green, led = el.querySelector('.led');
  led.style.background = on ? col : (el.dataset.col === 'red' ? '#3b2424' : '#2c3a30');
  led.style.boxShadow = on ? `0 0 8px ${col}` : 'inset 0 1px 2px #000';
  el.setAttribute('aria-pressed', on ? 'true' : 'false');""",
"""  const on = el.dataset.inv ? !tog(el.dataset.t) : tog(el.dataset.t);
  el.setAttribute('aria-pressed', on ? 'true' : 'false');""")
jrep("""function setMeter(id, i, v) { $$(`.seg[data-m="${id}${i}"]`).forEach(r => r.setAttribute('opacity', +r.dataset.f <= v ? 0.95 : 0.12)); }""",
"""function setMeter(id, i, v) { const r = $(`.mbar[data-m="${id}${i}"]`); if (!r) return; const t = +r.dataset.top, b = +r.dataset.bot, h = (b - t) * v;
  r.setAttribute('y', (b - h).toFixed(1)); r.setAttribute('height', h.toFixed(1)); r.setAttribute('fill', v > 0.9 ? '#f05a1a' : '#2f3338'); }""")
jrep("""  const paintInfo = () => { infoBtn.setAttribute('aria-pressed', tipsOn ? 'true' : 'false'); const led = infoBtn.querySelector('.led');
    led.style.background = tipsOn ? '#62e86d' : '#2c3a30'; led.style.boxShadow = tipsOn ? '0 0 8px #62e86d' : 'inset 0 1px 2px #000'; };""",
"""  const paintInfo = () => { infoBtn.setAttribute('aria-pressed', tipsOn ? 'true' : 'false'); };""")
jrep("""$$('.tb[data-t]').forEach(drawToggle)""", """$$('[data-t]').forEach(drawToggle)""")
jrep("""  $$('.tb[data-t]').forEach(el => el.addEventListener('click'""", """  $$('[data-t]').forEach(el => el.addEventListener('click'""")
jrep("""`<div class="chip">${names[k]} <span style="color:#9be36a">""", """`<div class="chip">${names[k]} <span style="color:#c4420c">""")
jrep("""c.setAttribute('fill', Math.abs(ang) < 30 ? '#ffe24d' : '#5cc8ff')""", """c.setAttribute('fill', Math.abs(ang) < 30 ? '#f05a1a' : '#7f8c99')""")
jrep("""$('#cBey').style.color = bey ? '#5cc8ff' : '#ffb23e';""", """$('#cBey').style.color = bey ? '#c4420c' : '#8c939a';""")
jrep("""$('#mode').textContent = mock ? 'PREVIEW (no audio)' : 'LIVE';""", """$('#mode').textContent = mock ? 'PREVIEW · NO AUDIO' : '';""")
jrep(""".forEach(d => d.setAttribute('fill', +d.dataset.f <= n + 1e-6 ? '#9be36a' : '#3a454f'))""", """.forEach(d => d.setAttribute('fill', +d.dataset.f <= n + 1e-6 ? '#f05a1a' : '#d0d5db'))""")
for _a, _b in [("const LEDC = { green: '#62e86d', amber: '#ffb23e', red: '#ff5a4a' };", "const LEDC = { green: '#62e86d', amber: '#ffb23e', red: '#ff5a4a' };\nconst DARKMAP = __DARKMAP__, VIOLETMAP = __VIOLETMAP__, MAPS = { dark: DARKMAP, violet: VIOLETMAP };\nlet DARK = false, THEME = 'light', MAP = null;\nconst MODACC = { generate: ['#2fa84f', '#1f7f3a'], shape: ['#0ea5c9', '#0b7f9c'], space: ['#8b5cf6', '#6a3fd0'], guard: ['#e23d3d', '#b32a2a'] };\n// Tropic: each display becomes a solid block of its module colour; lines go white, grids a lighter tint.\nfunction tropMap(mod) {\n  const base = { generate: '#1f9a44', shape: '#0797ba', space: '#7c4de8', guard: '#d63333', input: '#2b3238', output: '#2b3238' }[mod];\n  if (!base) return null;\n  const lighten = (hex, k) => { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255;\n    const f = v => Math.round(v + (255 - v) * k).toString(16).padStart(2, '0'); return '#' + f(r) + f(g) + f(b); };\n  const grid = lighten(base, 0.22), grid2 = lighten(base, 0.14), text = lighten(base, 0.78);\n  return { '#eceef1': base, '#e6e9ec': lighten(base, -0.0), '#d5d9de': grid, '#e3e6ea': grid2, '#cdd2d8': grid, '#dde1e5': grid, '#cfd4d9': grid2, '#b3bac2': grid,\n           '#9aa1a9': text, '#8c939a': text, '#7f8c99': lighten(base, 0.6), '#c4cad0': grid, '#2f3338': '#ffffff', '#f05a1a': '#ffffff', '#ffffff': '#ffffff', '#c4420c': '#ffffff', _base: base, _chips: lighten(base, -0.0) };\n}\nconst TROP = {};\n['input', 'generate', 'shape', 'space', 'guard', 'output'].forEach(m => TROP[m] = tropMap(m));\nconst modOf = el => { const m = el && el.closest ? el.closest('.mod[data-mod]') : null; return m ? m.dataset.mod : null; };\nconst ACC = el => { if (THEME === 'color') { const m = modOf(el); if (m && MODACC[m]) return MODACC[m][0]; } return TC('#f05a1a'); };\nconst ACCT = el => { if (THEME === 'color') { const m = modOf(el); if (m && MODACC[m]) return MODACC[m][1]; } return TC('#c4420c'); };\nconst TC = c => MAP ? (MAP[c.toLowerCase()] || c) : c;\nconst TD = (c, el) => { if (THEME !== 'color') return TC(c); const m = modOf(el), t = m && TROP[m]; return t ? (t[c.toLowerCase()] || c) : TC(c); };\nfunction applyTheme(name) {\n  THEME = name; MAP = MAPS[name] || null; const dark = !!MAP; DARK = dark;\n  document.documentElement.classList.toggle('dark', name === 'dark'); document.documentElement.classList.toggle('violet', name === 'violet'); document.documentElement.classList.toggle('color', name === 'color');\n  document.querySelectorAll('[fill],[stroke],[stop-color],[flood-color],[style]').forEach(el => {\n    if (el.closest('#mChips') || el.id === 'cBey' || el.classList.contains('mbar') || el.classList.contains('stD') || el.classList.contains('pdot') || el.classList.contains('ffill') || el.classList.contains('fline') || el.classList.contains('arc') || el.classList.contains('xoD') || el.id === 'wfL' || el.id === 'wcLine' || el.id === 'thrL' || el.id === 'thrT' || el.id === 'chPull' || el.classList.contains('sHot') || el.id === 'app') return;\n    for (const a of ['fill', 'stroke', 'stop-color', 'flood-color', 'style']) {\n      if (!el.hasAttribute(a)) continue;\n      const key = 'l' + a.replace('-', '');\n      if (el.dataset[key] === undefined) el.dataset[key] = el.getAttribute(a);\n      const orig = el.dataset[key];\n      el.setAttribute(a, MAP ? orig.replace(/#[0-9a-fA-F]{6}\\b/g, m => MAP[m.toLowerCase()] || m) : orig);\n    }\n    if (el.hasAttribute('flood-opacity')) el.setAttribute('flood-opacity', dark ? '0.7' : '0.32');\n  });\n  // tropic pass: recolour everything inside each module's main display\n  $$('.mod[data-mod]').forEach(mod => {\n    const t = TROP[mod.dataset.mod]; const scr = mod.querySelector('.mhead + .screen'); if (!t || !scr) return;\n    scr.querySelectorAll('[fill],[stroke],[style]').forEach(el => {\n      if (el.closest('.chips') || el.classList.contains('mbar') || el.classList.contains('stD') || el.id === 'wfL' || el.id === 'wfR' || el.id === 'wcLine' || el.id === 'wcFill' || el.classList.contains('xoD') || el.id === 'thrL' || el.id === 'thrT' || el.id === 'chPull' || el.id === 'chLine' || el.classList.contains('sAll') || el.classList.contains('sHot')) return;\n      for (const a of ['fill', 'stroke', 'style']) {\n        if (!el.hasAttribute(a)) continue; const key = 'l' + a; if (el.dataset[key] === undefined) el.dataset[key] = el.getAttribute(a);\n        const orig = el.dataset[key];\n        el.setAttribute(a, name === 'color' ? orig.replace(/#[0-9a-fA-F]{6}\\b/g, m => t[m.toLowerCase()] || m) : (MAP ? orig.replace(/#[0-9a-fA-F]{6}\\b/g, m => MAP[m.toLowerCase()] || m) : orig));\n      }\n    });\n    \n  });\n  $$('.thb').forEach(b => b.setAttribute('aria-pressed', b.dataset.th === name ? 'true' : 'false'));\n  if (S.master) redrawAll();\n}"), ("r.setAttribute('fill', v > 0.9 ? '#f05a1a' : '#2f3338'); }", "r.setAttribute('fill', THEME === 'color' ? (v > 0.9 ? '#ffb4b4' : '#ffffff') : TC(v > 0.9 ? '#f05a1a' : '#2f3338')); }"), ("c.setAttribute('fill', Math.abs(ang) < 30 ? '#f05a1a' : '#7f8c99')", "c.setAttribute('fill', THEME === 'color' ? (Math.abs(ang) < 30 ? '#ffffff' : 'rgba(255,255,255,.55)') : (Math.abs(ang) < 30 ? ACC($('#st')) : TC('#7f8c99')))"), ("$$('[data-t]').forEach(drawToggle)", "$$('[data-t]').forEach(drawToggle); $$('.lrb').forEach(b => b.setAttribute('aria-pressed', (b.dataset.lr === '1') === tog('in_dlyside') ? 'true' : 'false'))"), ("$('#cShuf').textContent", "const TR = THEME === 'color'; $('#wfL').setAttribute('stroke', TR ? '#ffffff' : ACC($('#wf'))); $('#wfR').setAttribute('stroke', TR ? 'rgba(255,255,255,.55)' : TC('#7f8c99')); $$('.wfb').forEach(p => p.setAttribute('stroke', TR ? 'rgba(255,255,255,.7)' : TC('#2f3338'))); $('#wcLine').setAttribute('stroke', TR ? '#ffffff' : ACC($('#wc'))); $('#wcFill').setAttribute('fill', TR ? '#ffffff' : TC('#2f3338')); $$('.xoD').forEach(d => { d.setAttribute('stroke', TR ? '#ffffff' : ACC($('#wc'))); d.setAttribute('fill', TR ? TROP.shape._base : TC('#eceef1')); }); $('#cDet').style.color = ACCT($('#cDet')); $('#cShuf').style.color = ACCT($('#cShuf')); $('#cShuf').textContent"), ("$('#cBey').style.color = bey ? '#c4420c' : '#8c939a';", "$('#cBey').style.color = bey ? ACCT($('#cBey')) : TC('#8c939a');"), ("$('#thrT').textContent = 'GUARD '", "const TRg = THEME === 'color'; $('#thrL').setAttribute('stroke', TRg ? '#ffffff' : ACC($('#ch'))); $('#thrT').setAttribute('fill', TRg ? '#ffffff' : ACCT($('#ch'))); $('#chPull').setAttribute('fill', TRg ? '#ffffff' : ACC($('#ch'))); $('#chLine').setAttribute('stroke', TRg ? '#ffffff' : TC('#2f3338')); $('#cPull').style.color = ACCT($('#cPull')); $('.sAll').setAttribute('stroke', TRg ? 'rgba(255,255,255,.6)' : TC('#2f3338')); $('.sHot').setAttribute('stroke', TRg ? '#ffffff' : TC('#f05a1a')); $('#thrT').textContent = 'GUARD '"), ('`<div class="chip">${names[k]} <span style="color:#c4420c">', '`<div class="chip">${names[k]} <span style="color:${TC(\'#c4420c\')}">'), ("['in_on', 'gen_on', 'sh_on', 'sp_on', 'gd_on', 'out_on'].forEach((k, i) => $$('.mod')[i].classList.toggle('off', !tog(k)));", "['in_on', 'gen_on', 'sh_on', 'sp_on', 'gd_on', 'out_on'].forEach((k, i) => { const m = $$('.mod:not(.mcard)')[i]; m.classList.toggle('off', !tog(k)); m.classList.toggle('on', tog(k)); });"), ('  // window size presets', "  // theme\n  const setTh = (!mock && Juce.getNativeFunction) ? Juce.getNativeFunction('setTheme') : null;\n  if (mock) { let t = 'light'; try { t = localStorage.getItem('ssTheme') || 'light'; } catch (e) {} applyTheme(t); }\n  else if (Juce.getNativeFunction) { applyTheme('light'); Juce.getNativeFunction('getTheme')().then(t => applyTheme(String(t))); }\n  $$('.thb').forEach(b => b.addEventListener('click', () => { const t = b.dataset.th; applyTheme(t);\n    if (setTh) setTh(t); else { try { localStorage.setItem('ssTheme', t); } catch (e) {} } }));\n  // window size presets"), ("  // window size presets", "  $$('.lrb').forEach(b => b.addEventListener('click', () => TG['in_dlyside'].setValue(b.dataset.lr === '1')));\n  // window size presets"), ("function fit() { const s = Math.min(innerWidth / __W__, innerHeight / __H__);", "function fit() { const de = document.documentElement, w = de.clientWidth || innerWidth, h = de.clientHeight || innerHeight; const s = Math.min(w / __W__, h / __H__);")]:
    jrep(_a, _b)
for k, v in (("__P__", json.dumps(P)), ("__T__", json.dumps(T)), ("__LINKED__", json.dumps(LINKED)), ("__WF__", json.dumps(WF)),
             ("__WC__", json.dumps(WC)), ("__ST__", json.dumps(ST)), ("__CH__", json.dumps(CH)), ("__SCW__", str(SCW)), ("__W__", str(W)), ("__H__", str(H))):
    JS = JS.replace(k, v)

DARKMAP = {
 "#c9ced4": "#363d45", "#a9b0b8": "#5a636d", "#f05a1a": "#5ab8ff", "#ffffff": "#434b55", "#2f3338": "#e4e8ec", "#8c939a": "#8f98a2",
 "#c4cad0": "#3b424a", "#e3e6ea": "#2a3037", "#e4e7eb": "#22282e", "#e4e7ec": "#0e1013", "#eef0f3": "#171a1e", "#f6f7f9": "#353c45",
 "#1c2430": "#000000", "#cfd4da": "#13161a", "#e6e9ed": "#515a64", "#c3c9d0": "#1a1e23", "#dde1e5": "#262b31", "#eceef1": "#111316",
 "#c4420c": "#7cc6ff", "#9aa1a9": "#6f7882", "#d5d9de": "#262c32", "#6b737b": "#a1aab3", "#b3bac2": "#4b535c", "#7f8c99": "#93a0ad",
 "#f3f4f6": "#1e2227", "#e0e3e7": "#252a30", "#cdd2d8": "#2a3036", "#f9fafb": "#262b31", "#a7aeb6": "#69727b", "#d6dade": "#3a424b",
 "#e9ecef": "#13161a", "#111315": "#f2f4f6", "#e2e5e9": "#111417", "#a6adb4": "#565e67", "#e1e4e8": "#2d333a", "#d3d8dd": "#3b434c",
 "#e6e9ec": "#1a1e22", "#4a5057": "#c6ccd2", "#f4f5f7": "#21262c", "#cfd4d9": "#2a3036", "#d0d5db": "#3b434c", "#fffffe": "#08131c", "#d8dce1": "#20252b", "#e2e5e9": "#2b3138", "#dfe3e7": "#262c33", "#f3e6dc": "#15202b", "#eedccf": "#131c26", "#b9c0c8": "#6a7480", "#d2d7dd": "#2a3038",
}
import colorsys
def _violet(hexv, light_src):
    r, g, b = [int(hexv[i:i+2], 16) / 255 for i in (1, 3, 5)]
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    l = l * 0.92 + 0.07
    sat = 0.30 if l < 0.5 else 0.42
    h = 0.69   # ~250deg, indigo/violet
    r, g, b = colorsys.hls_to_rgb(h, l, sat)
    return "#%02x%02x%02x" % (round(r*255), round(g*255), round(b*255))
VIOLETMAP = { k: _violet(v, k) for k, v in DARKMAP.items() }
VIOLETMAP["#f05a1a"] = "#cdbcff"   # lavender accent
VIOLETMAP["#c4420c"] = "#d9ccff"
VIOLETMAP["#2f3338"] = "#f1edff"   # primary lines/text
VIOLETMAP["#ffffff"] = "#4a4476"   # knob highlight / chips
VIOLETMAP["#f6f7f9"] = "#3f3a68"
VIOLETMAP["#d8dce1"] = "#2a2648"
VIOLETMAP["#b9c0c8"] = "#8d84c4"   # knob rim
VIOLETMAP["#e6e9ed"] = "#6a62a3"
VIOLETMAP["#eef0f3"] = "#1f1c36"   # panel
VIOLETMAP["#e4e7ec"] = "#15132a"   # page bg
VIOLETMAP["#f9fafb"] = "#302c52"   # card top
VIOLETMAP["#f3f4f6"] = "#2a2648"   # card bottom
VIOLETMAP["#eceef1"] = "#181530"   # display
VIOLETMAP["#e6e9ec"] = "#1f1c38"   # chips strip
JS = JS.replace("__DARKMAP__", json.dumps(DARKMAP)).replace("__VIOLETMAP__", json.dumps(VIOLETMAP))
import re as _re
_used = {}
def _v(m):
    h = m.group(0).lower()
    if h not in DARKMAP: return m.group(0)
    n = "--c" + h[1:]; _used[n] = h; return f"var({n})"
_fontcss, _rest = CSS.split("\n", 1) if False else ("", CSS)
CSS = _re.sub(r"#[0-9a-fA-F]{6}\b", _v, CSS)
CSS = CSS.replace("rgba(240,90,26,", "rgba(var(--glow),").replace("rgba(30,40,55,", "rgba(var(--sh),").replace("rgba(20,30,40,", "rgba(var(--sh),")
CSS = (":root{" + "".join(f"{n}:{h};" for n, h in _used.items()) + "--glow:240,90,26;--sh:30,40,55}\n"
       + ":root.dark{" + "".join(f"{n}:{DARKMAP[h]};" for n, h in _used.items()) + "--glow:90,184,255;--sh:0,0,0}\n"
       + ":root.violet{" + "".join(f"{n}:{VIOLETMAP[h]};" for n, h in _used.items()) + "--glow:205,188,255;--sh:5,3,20}\n" + CSS)
CSS += """
:root.color{--ceef0f3:#e6e8ec;--ce4e7ec:#d9dce1;--cf9fafb:#f3f4f6;--cf3f4f6:#eceef1;--ceceef1:#e3e6ea;--ce6e9ec:#dde0e5;--cffffff:#fbfbfc;--cf6f7f9:#f1f2f4;--cd8dce1:#cfd3d9;--cf3e6dc:#ece1d8;--ceedccf:#e6d6ca}
:root.color .mod[data-mod=generate]{--cf05a1a:#2fa84f;--cc4420c:#1f7f3a;--glow:47,168,79;--cf3e6dc:#dae9dd;--ceedccf:#d0e2d4}
:root.color .mod[data-mod=shape]{--cf05a1a:#0ea5c9;--cc4420c:#0b7f9c;--glow:14,165,201;--cf3e6dc:#d8e8ec;--ceedccf:#cde0e6}
:root.color .mod[data-mod=space]{--cf05a1a:#8b5cf6;--cc4420c:#6a3fd0;--glow:139,92,246;--cf3e6dc:#e3def2;--ceedccf:#dad4ed}
:root.color .mod[data-mod=guard]{--cf05a1a:#e23d3d;--cc4420c:#b32a2a;--glow:226,61,61;--cf3e6dc:#efdcdc;--ceedccf:#e9d1d1}
:root.color .mod[data-mod=input],:root.color .mod[data-mod=output]{--cf3e6dc:#e3e6ea;--ceedccf:#dde0e5}
:root.color .mod[data-mod=generate]{--cf9fafb:#e6f5ea;--cf3f4f6:#d8ecde;--ce6e9ec:#cfe6d6;--cffffff:#f4fbf6;--ce3e6ea:#c6dfcd;--cd6dade:#b9d6c2}
:root.color .mod[data-mod=shape]{--cf9fafb:#e2f3f7;--cf3f4f6:#d2eaf0;--ce6e9ec:#c7e3ea;--cffffff:#f2fafc;--ce3e6ea:#bddbe3;--cd6dade:#aed2dc}
:root.color .mod[data-mod=space]{--cf9fafb:#ece6fb;--cf3f4f6:#e0d8f6;--ce6e9ec:#d6ccf1;--cffffff:#f6f3fd;--ce3e6ea:#cdc2ec;--cd6dade:#c0b3e6}
:root.color .mod[data-mod=guard]{--cf9fafb:#fbe6e6;--cf3f4f6:#f5d8d8;--ce6e9ec:#efcbcb;--cffffff:#fdf3f3;--ce3e6ea:#ebc0c0;--cd6dade:#e3b2b2}
"""
CSS += ":root.dark .mod,:root.dark .bar{box-shadow:0 12px 26px rgba(0,0,0,.5),0 0 0 1px #2a3037,inset 0 1px 0 #2f363e}\n:root.dark .mcard{box-shadow:0 16px 34px rgba(0,0,0,.6),0 0 0 1px #2e343b,inset 0 1px 0 #353c45}\n"
CSS += ":root.violet .mod,:root.violet .bar{box-shadow:0 12px 26px rgba(5,3,20,.55),0 0 0 1px #3b366a,inset 0 1px 0 #443f78}\n:root.violet .mcard{box-shadow:0 16px 34px rgba(5,3,20,.65),0 0 0 1px #3f3a70,inset 0 1px 0 #4a4480}\n:root.violet .sw-violet,:root.dark .sw-dark,:root.color .sw-color{{}}\n"
body = f'<main id="app" class="v{VARIANT}">{header}<div class="rack">{"".join(rack_mods)}</div><div id="tip" role="tooltip"></div></main>'
# recolour the reused dark-screen display frames for the light theme
for a, b in (("#0b100f", "#eceef1"), ("#1f3329", "#d5d9de"), ("#25402f", "#cdd2d8"), ("#1a2a22", "#d5d9de"), ("#1b2a24", "#dde1e5"),
             ("#1d3327", "#d5d9de"), ("#2b3a33", "#cfd4d9"), ("#5f8a6c", "#9aa1a9"), ("#7ea58a", "#8c939a"), ("#3d6b4c", "#b3bac2"),
             ("#2f5a40", "#b3bac2"), ("#1a2420", "#ffffff"), ("#0f1a15", "#e3e6ea"), ("#9be36a", INKD), ("#ffe24d", ACC), ("#5cc8ff", SIDE), ("#ffb23e", ACC)):
    body = body.replace(a, b)
body = body.replace("font-family=\"'Share Tech Mono', monospace\"", f"font-family=\"{FT}\"")
html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SuperSpread — v0.3 preview</title><style>{CSS}</style></head><body>'
        f'{body}<script type="module">{JS}</script></body></html>')
open(OUT, "w").write(html)
print("ok", len(html), OUT)
