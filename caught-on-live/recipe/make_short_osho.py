"""Caught On Live: "Carry ka Jason ban gaya OSHO" — GTA VI meditation minigame (CarryisLive irNhWMG560k, 9:23-9:26).
Video and audio come from separate DASH downloads (med_v.mp4 = itag 299, med_a.m4a = itag 140); t0 = each file's
start_time = stream seconds. Audio is built separately (no loudnorm in the encode: gain + limiter via WAV), then muxed.
Layout 1080x1920: face-cam 1080x652 top, gameplay 1080x1268 bottom, red seam, hook box on the seam, part chip, credit chip.
No speech captions (owner's preference)."""
import json, re, shlex, subprocess, pathlib

def T(h, m, s): return h * 3600 + m * 60 + s

V_SRC, V_T0 = "med/med_v.mp4", 33788.633333
A_SRC, A_T0 = "med/med_a.m4a", 33787.820408

# a/b in stream seconds; flash = white flash at the start of this part
PARTS = [
    dict(a=T(9, 23, 24.8), b=T(9, 23, 52.5), gx=r"if(lt(t\,3.4)\,405+115*(3*pow(t/3.4\,2)-2*pow(t/3.4\,3))\,520)", flash=False),   # "Empty head, easy." + Michael ki tarah + Osho
    dict(a=T(9, 25, 11.0), b=T(9, 25, 31.5), gx=520, flash=True),    # isko literal nasha ho raha hai
    dict(a=T(9, 25, 53.5), b=T(9, 26, 9.5), gx=520, flash=True),     # mujhe nahi karna, par karna pad raha hai
    dict(a=T(9, 26, 22.5), b=T(9, 26, 44.0), gx=520, flash=True),    # ye sab kya khul gaya / zindagi sort ho gayi
]
CHIPS = [
    (PARTS[0]["a"], PARTS[0]["b"], "PART 1 · OSHO MODE ON"),
    (PARTS[1]["a"], PARTS[1]["b"], "PART 2 · NASHA YA DHYAAN?"),
    (PARTS[2]["a"], PARTS[2]["b"], "PART 3 · MAJBOORI KA DHYAAN"),
    (PARTS[3]["a"], PARTS[3]["b"], "PART 4 · ZINDAGI SORTED"),
]
# the game's own "Meditations 1/18 / Focus buffed" HUD sits outside the gameplay crop, so repeat it
END_BADGE = (T(9, 26, 40.0), T(9, 26, 44.0), "MEDITATIONS 1/18 · FOCUS BUFFED")

FC_X, FC_Y, FC_W, FC_H = 70, 440, 328, 198   # inside Carry's cam box (x 12-402, y 408-665 from ~9:00:00)
FACE_H = 652
GAME_H = 1920 - FACE_H
GAME_W = round(1080 * 1080 / GAME_H / 2) * 2
HOOK = [r"CARRY KA JASON", r"BAN GAYA {\c&H4D2EFF&}OSHO{\c&H000000&}"]
FONTS = "/usr/share/fonts/truetype/google-fonts/ofl"
OUT = "short_osho_v1.mp4"

starts, acc = [], 0.0
for p in PARTS:
    starts.append(acc); acc += p["b"] - p["a"]
DUR = acc


def to_out(t):
    for p, s in zip(PARTS, starts):
        if p["a"] - 1e-6 <= t <= p["b"] + 1e-6:
            return s + (t - p["a"])
    raise SystemExit(f"time {t} not inside a part")


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
           "Style: Part,Montserrat,46,&H00000000,&H00000000,&H000AD6FF,&H000AD6FF,1,0,0,0,100,100,1,0,3,10,0,5,0,0,0,1",
           "Style: Badge,Montserrat,44,&H00FFFFFF,&H00FFFFFF,&H004D2EFF,&H004D2EFF,1,0,0,0,100,100,1,0,3,12,0,5,0,0,0,1",
           "Style: Live,Montserrat,40,&H00FFFFFF,&H00FFFFFF,&H004D2EFF,&H004D2EFF,1,0,0,0,100,100,2,0,3,10,0,7,0,0,0,1",
           "Style: Name,Montserrat,40,&H00FFFFFF,&H00FFFFFF,&H30100A0A,&H30100A0A,1,0,0,0,100,100,1,0,3,10,0,7,0,0,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    hook = r"{\fad(120,0)\t(0,180,\fscx104\fscy104)\t(180,320,\fscx100\fscy100)}" + r"\N".join(HOOK)
    out.append(f"Dialogue: 2,{ts(0)},{ts(DUR)},Hook,,0,0,0,,{{\\pos(540,{FACE_H})}}{hook}")
    out.append(f"Dialogue: 3,{ts(0)},{ts(DUR)},Live,,0,0,0,,{{\\pos(44,150)}}● LIVE")
    out.append(f"Dialogue: 3,{ts(0)},{ts(DUR)},Name,,0,0,0,,{{\\pos(186,150)}}CarryisLive")
    for a_st, b_st, label in CHIPS:
        a, b = to_out(a_st), to_out(b_st)
        out.append(f"Dialogue: 2,{ts(a)},{ts(b)},Part,,0,0,0,,"
                   f"{{\\pos(540,{FACE_H + 150})\\fad(150,0)\\t(0,160,\\fscx108\\fscy108)\\t(160,300,\\fscx100\\fscy100)}}{label}")
    a, b = to_out(END_BADGE[0]), to_out(END_BADGE[1])
    out.append(f"Dialogue: 2,{ts(a)},{ts(b)},Badge,,0,0,0,,"
               f"{{\\pos(540,1560)\\fad(150,0)\\t(0,160,\\fscx110\\fscy110)\\t(160,300,\\fscx100\\fscy100)}}{END_BADGE[2]}")
    pathlib.Path("short_osho.ass").write_text("\n".join(out) + "\n", encoding="utf-8")


def render_video():
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for p in PARTS:
        cmd += ["-ss", f"{p['a'] - V_T0:.3f}", "-t", f"{p['b'] - p['a']:.3f}", "-i", V_SRC]
    fc = []
    for n, p in enumerate(PARTS):
        fc.append(f"[{n}:v]split=2[f{n}][g{n}];"
                  f"[f{n}]crop={FC_W}:{FC_H}:{FC_X}:{FC_Y},scale=1080:{FACE_H}:flags=lanczos,"
                  f"unsharp=5:5:0.6:5:5:0.0,eq=saturation=1.08[ff{n}];"
                  f"[g{n}]crop={GAME_W}:1080:{p['gx']}:0,scale=1080:{GAME_H}:flags=lanczos,"
                  f"eq=saturation=1.08:contrast=1.04:brightness=0.03:gamma=1.12[gg{n}];"
                  f"[ff{n}][gg{n}]vstack=inputs=2,fps=fps=60:start_time=0,trim=duration={p["b"] - p["a"]:.4f}[v{n}]")
    ins = "".join(f"[v{n}]" for n in range(len(PARTS)))
    flashes = [f"drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='between(t,{s:.3f},{s + 0.08:.3f})'"
               for s, p in zip(starts, PARTS) if p["flash"]]
    chain = ",".join([f"drawbox=x=0:y={FACE_H - 3}:w=1080:h=6:color=0xFF2E4D@1:t=fill"] + flashes +
                     [f"ass=short_osho.ass:fontsdir={FONTS}", "format=yuv420p"])
    fc.append(f"{ins}concat=n={len(PARTS)}:v=1:a=0[vc];[vc]{chain}[v]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "60", "-profile:v", "high",
            "-movflags", "+faststart", "osho_video.mp4"]
    subprocess.run(cmd, check=True)


def render_audio():
    """same method as fix_audio.py: cut + join as float WAV, measure once, plain gain + limiter, s16 WAV."""
    cmd = ["ffmpeg", "-v", "error", "-y"]; fc = []
    for n, p in enumerate(PARTS):
        d = p["b"] - p["a"]
        cmd += ["-ss", f"{p['a'] - A_T0:.3f}", "-t", f"{d:.3f}", "-i", A_SRC]
        fc.append(f"[{n}:a]aresample=48000,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=N/SR/TB,"
                  f"afade=t=in:d=0.06,afade=t=out:st={d - 0.06:.3f}:d=0.06[a{n}]")
    fc.append("".join(f"[a{n}]" for n in range(len(PARTS))) + f"concat=n={len(PARTS)}:v=0:a=1[ac]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[ac]", "-c:a", "pcm_f32le", "osho_cut.wav"]
    subprocess.run(cmd, check=True)
    # gentle compression so the calm game parts don't sound dead next to Carry's voice (still WAV -> WAV)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "osho_cut.wav", "-af",
                    "acompressor=threshold=-28dB:ratio=3:attack=15:release=250:knee=6", "-c:a", "pcm_f32le",
                    "osho_raw.wav"], check=True)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", "osho_raw.wav", "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    stats = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r, re.S).group(0))
    gain = -14.0 - float(stats["input_i"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "osho_raw.wav", "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled,"
                    f"afade=t=out:st={DUR - 0.3:.3f}:d=0.3", "-c:a", "pcm_s16le", "osho_fixed.wav"], check=True)
    return gain, float(stats["input_i"])


def mux():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "osho_video.mp4", "-i", "osho_fixed.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", OUT], check=True)


if __name__ == "__main__":
    import sys
    build_ass()
    print("duration", round(DUR, 2), "part starts", [round(s, 2) for s in starts])
    if "ass" in sys.argv: raise SystemExit
    render_video()
    print("audio gain/input LUFS", render_audio())
    mux()
    print("wrote", OUT)
