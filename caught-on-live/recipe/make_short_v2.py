"""Caught On Live: multi-part Short (mini story) from Carry's GTA VI stream.
Each part: (source file, stream time of source t=0, stream start, stream end, face-cam y, gameplay x, chip).
Layout 1080x1920: face-cam 1080x651 top, gameplay 1080x1269 bottom, red seam, hook box on the seam,
part chip under the hook, credit chip, word-by-word captions (active word yellow)."""
import subprocess, pathlib

def T(m, s): return m * 60 + s

PARTS = [
    dict(src="src.mp4", t0=T(56, 38), a=T(56, 44.0), b=T(56, 58.5), fy=372, gx=420, chip="PART 1 · PHOOL PATTE"),
    dict(src="shop_src.mp4", t0=T(79, 54), a=T(79, 57.0), b=T(80, 44.0), fy=483, gx=520, chip="PART 2 · SHOPPING TIME"),
    dict(src="shop_src.mp4", t0=T(79, 54), a=T(81, 5.5), b=T(81, 21.0), fy=483, gx=520, chip="PART 2 · SHOPPING TIME"),
]
FC_X, FC_W, FC_H = 14, 365, 220
FACE_H = 651
GAME_H = 1920 - FACE_H
GAME_W = round(1080 * 1080 / GAME_H / 2) * 2

HOOK = [r"GTA 6 MEIN CARRY KA", r"{\c&H4D2EFF&}CHILL MODE{\c&H000000&} ON"]

# captions in stream time; only lines the speech passes agreed on
LINES = [
    (T(56, 45.2), T(56, 49.3), "YEH PHOOL PATTE BHI CHECK KARO BHAI"),
    (T(56, 49.8), T(56, 52.7), "I LOVE GAMES JO..."),
    (T(56, 53.0), T(56, 57.1), "JIN LOGON KO BORING LAGTI HONGI..."),
    (T(79, 59.7), T(80, 1.5), "OKAY OKAY OKAY"),
    (T(80, 13.5), T(80, 18.4), "YEH DIKHAO... INMEIN MAZA AAYEGA"),
    (T(80, 21.0), T(80, 25.1), "MATLAB MERI PREFERENCE..."),
    (T(80, 30.3), T(80, 31.5), "YES!"),
    (T(80, 35.0), T(80, 37.2), "EK MINUTE..."),
    (T(80, 37.8), T(80, 40.3), "BOTTOMS KA HAI?"),
    (T(80, 42.8), T(80, 43.7), "HAAN"),
    (T(81, 6.3), T(81, 7.7), "OR SWIM SHORTS"),
    (T(81, 9.3), T(81, 12.9), "NOT OWNED... EK HI HAI KYA?"),
    (T(81, 16.0), T(81, 20.0), "THEEK HAI BHAI, AUR JAGAH DEKHTE HAIN"),
]
CHUNK = 3
OUT = "short_long_v2.mp4"

# timeline: where each part starts in the output
starts, acc = [], 0.0
for p in PARTS:
    starts.append(acc); acc += p["b"] - p["a"]
DUR = acc


def to_out(t):
    """stream time -> output time (None if not inside a part)"""
    for p, s in zip(PARTS, starts):
        if p["a"] <= t <= p["b"]:
            return s + (t - p["a"])
    return None


def ts(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def build_ass():
    out = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2",
           "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
           "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
           "Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Hook,Anton,84,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,1,0,3,16,0,5,60,60,0,1",
           "Style: Cap,Anton,106,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,7,3,5,70,70,0,1",
           "Style: Part,Montserrat,46,&H00000000,&H00000000,&H000AD6FF,&H000AD6FF,1,0,0,0,100,100,1,0,3,10,0,5,0,0,0,1",
           "Style: Live,Montserrat,40,&H00FFFFFF,&H00FFFFFF,&H004D2EFF,&H004D2EFF,1,0,0,0,100,100,2,0,3,10,0,7,0,0,0,1",
           "Style: Name,Montserrat,40,&H00FFFFFF,&H00FFFFFF,&H30100A0A,&H30100A0A,1,0,0,0,100,100,1,0,3,10,0,7,0,0,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    hook = r"{\fad(120,0)\t(0,180,\fscx104\fscy104)\t(180,320,\fscx100\fscy100)}" + r"\N".join(HOOK)
    out.append(f"Dialogue: 2,{ts(0)},{ts(DUR)},Hook,,0,0,0,,{{\\pos(540,{FACE_H})}}{hook}")
    out.append(f"Dialogue: 3,{ts(0)},{ts(DUR)},Live,,0,0,0,,{{\\pos(44,150)}}● LIVE")
    out.append(f"Dialogue: 3,{ts(0)},{ts(DUR)},Name,,0,0,0,,{{\\pos(186,150)}}CarryisLive")

    # part chips (merge consecutive parts with the same label)
    i = 0
    while i < len(PARTS):
        j = i
        while j + 1 < len(PARTS) and PARTS[j + 1]["chip"] == PARTS[i]["chip"]:
            j += 1
        a, b = starts[i], starts[j] + PARTS[j]["b"] - PARTS[j]["a"]
        out.append(f"Dialogue: 2,{ts(a)},{ts(b)},Part,,0,0,0,,"
                   f"{{\\pos(540,{FACE_H + 150})\\fad(150,0)\\t(0,160,\\fscx108\\fscy108)\\t(160,300,\\fscx100\\fscy100)}}{PARTS[i]['chip']}")
        i = j + 1

    for st, en, text in LINES:
        o_st, o_en = to_out(st), to_out(en)
        if o_st is None or o_en is None:
            raise SystemExit(f"caption outside parts: {text}")
        words = text.split()
        weights = [max(len(w), 2) for w in words]
        total = sum(weights)
        t, times = o_st, []
        for wt in weights:
            d = (o_en - o_st) * wt / total
            times.append((t, t + d)); t += d
        for c0 in range(0, len(words), CHUNK):
            chunk = list(range(c0, min(c0 + CHUNK, len(words))))
            for k in chunk:
                a, b = times[k]
                parts = [(r"{\c&H0AD6FF&\fscx112\fscy112}" + words[j] + r"{\c&HFFFFFF&\fscx100\fscy100}")
                         if j == k else words[j] for j in chunk]
                pop = r"{\t(0,90,\fscx106\fscy106)\t(90,160,\fscx100\fscy100)}" if k == chunk[0] else ""
                out.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos(540,1330)}}{pop}{' '.join(parts)}")
    pathlib.Path("short_long.ass").write_text("\n".join(out) + "\n", encoding="utf-8")


def render():
    fonts = "/usr/share/fonts/truetype/google-fonts/ofl"
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for p in PARTS:
        cmd += ["-ss", f"{p['a'] - p['t0']:.3f}", "-t", f"{p['b'] - p['a']:.3f}", "-i", p["src"]]
    fc = []
    for n, p in enumerate(PARTS):
        d = p["b"] - p["a"]
        fc.append(f"[{n}:v]split=2[f{n}][g{n}];"
                  f"[f{n}]crop={FC_W}:{FC_H}:{FC_X}:{p['fy']},scale=1080:{FACE_H}:flags=lanczos,"
                  f"unsharp=5:5:0.6:5:5:0.0,eq=saturation=1.08[ff{n}];"
                  f"[g{n}]crop={GAME_W}:1080:{p['gx']}:0,scale=1080:{GAME_H}:flags=lanczos,"
                  f"eq=saturation=1.08:contrast=1.04:brightness=0.03:gamma=1.12[gg{n}];"
                  f"[ff{n}][gg{n}]vstack=inputs=2,fps=60,setpts=PTS-STARTPTS[v{n}];"
                  f"[{n}:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.06,afade=t=out:st={d - 0.06:.3f}:d=0.06[a{n}]")
    ins = "".join(f"[v{n}][a{n}]" for n in range(len(PARTS)))
    flashes = ",".join(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='between(t,{s:.3f},{s + 0.08:.3f})'"
                       for s in starts[1:])
    fc.append(f"{ins}concat=n={len(PARTS)}:v=1:a=1[vc][ac];"
              f"[vc]drawbox=x=0:y={FACE_H - 3}:w=1080:h=6:color=0xFF2E4D@1:t=fill,{flashes},"
              f"ass=short_long.ass:fontsdir={fonts},format=yuv420p[v];"
              f"[ac]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={DUR - 0.3:.3f}:d=0.3[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "60", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build_ass()
    render()
    print("rendered", round(DUR, 2), "s; part starts", [round(s, 2) for s in starts])
