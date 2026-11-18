"""Render a Caught On Live test Short from src.mp4 (stream time 56:38 at t=0).
Layout 1080x1920: face-cam top (1080x651), gameplay bottom (1080x1269),
hook box on the seam, credit chip, word-by-word captions (active word yellow)."""
import subprocess, pathlib

SRC = "src.mp4"
SRC_T0 = 56 * 60 + 38          # stream time of src t=0
CLIP_START = 56 * 60 + 44.0     # stream time
CLIP_END = 56 * 60 + 58.5
DUR = CLIP_END - CLIP_START
ss = CLIP_START - SRC_T0

# face-cam box on the 1920x1080 stream frame (above Carry's own name banner)
FC = dict(x=14, y=372, w=365, h=220)
FACE_H = 651
GAME_H = 1920 - FACE_H
game_w = round(1080 * 1080 / GAME_H / 2) * 2
GAME = dict(x=420, y=0, w=game_w, h=1080)

HOOK = [r"{\c&H0AD6FF&}GTA 6{\c&H000000&} KE GRAPHICS DEKH KE", r"CARRY BHI RUK GAYA"]

# captions: (stream start, stream end, text). Only lines two transcription passes agreed on.
LINES = [
    (56 * 60 + 45.2, 56 * 60 + 49.3, "YEH PHOOL PATTE BHI CHECK KARO BHAI"),
    (56 * 60 + 49.8, 56 * 60 + 52.7, "I LOVE GAMES JO..."),
    (56 * 60 + 53.0, 56 * 60 + 57.1, "JIN LOGON KO BORING LAGTI HONGI..."),
]
CHUNK = 3  # words on screen at once


def ts(t):
    t = max(0, t)
    h, m = int(t // 3600), int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass():
    out = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2",
           "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
           "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
           "Alignment, MarginL, MarginR, MarginV, Encoding",
           # hook: black Anton on a white box
           "Style: Hook,Anton,84,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,1,0,3,16,0,5,60,60,0,1",
           # captions: white Anton, thick black outline
           "Style: Cap,Anton,106,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,2,0,1,7,3,5,70,70,0,1",
           # chips
           "Style: Live,Montserrat,40,&H00FFFFFF,&H00FFFFFF,&H004D2EFF,&H004D2EFF,1,0,0,0,100,100,2,0,3,10,0,7,0,0,0,1",
           "Style: Name,Montserrat,40,&H00FFFFFF,&H00FFFFFF,&H30100A0A,&H30100A0A,1,0,0,0,100,100,1,0,3,10,0,7,0,0,0,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

    # hook across the seam, whole clip, small pop-in
    hook_text = r"{\fad(120,0)\t(0,180,\fscx104\fscy104)\t(180,320,\fscx100\fscy100)}" + r"\N".join(HOOK)
    out.append(f"Dialogue: 2,{ts(0)},{ts(DUR)},Hook,,0,0,0,,{{\\pos(540,{FACE_H})}}{hook_text}")

    # credit chip (top-left of the face-cam area, below the phone's back button)
    out.append(f"Dialogue: 3,{ts(0)},{ts(DUR)},Live,,0,0,0,,{{\\pos(44,150)}}● LIVE")
    out.append(f"Dialogue: 3,{ts(0)},{ts(DUR)},Name,,0,0,0,,{{\\pos(186,150)}}CarryisLive")

    # word-by-word captions, chunks of 3 words, active word yellow + slightly bigger
    for st, en, text in LINES:
        words = text.split()
        weights = [max(len(w), 2) for w in words]
        total = sum(weights)
        t = st
        times = []
        for w, wt in zip(words, weights):
            d = (en - st) * wt / total
            times.append((t, t + d)); t += d
        for c0 in range(0, len(words), CHUNK):
            chunk = list(range(c0, min(c0 + CHUNK, len(words))))
            for i in chunk:
                a, b = times[i]
                parts = []
                for j in chunk:
                    if j == i:
                        parts.append(r"{\c&H0AD6FF&\fscx112\fscy112}" + words[j] + r"{\c&HFFFFFF&\fscx100\fscy100}")
                    else:
                        parts.append(words[j])
                pop = r"{\t(0,90,\fscx106\fscy106)\t(90,160,\fscx100\fscy100)}" if i == chunk[0] else ""
                out.append(f"Dialogue: 1,{ts(a - CLIP_START)},{ts(b - CLIP_START)},Cap,,0,0,0,,"
                           f"{{\\pos(540,1330)}}{pop}{' '.join(parts)}")
    pathlib.Path("short.ass").write_text("\n".join(out) + "\n", encoding="utf-8")


def render():
    fonts = "/usr/share/fonts/truetype/google-fonts/ofl"
    fc = FC; g = GAME
    vf = (f"[0:v]split=2[a][b];"
          f"[a]crop={fc['w']}:{fc['h']}:{fc['x']}:{fc['y']},scale=1080:{FACE_H}:flags=lanczos,"
          f"unsharp=5:5:0.6:5:5:0.0,eq=saturation=1.08[face];"
          f"[b]crop={g['w']}:{g['h']}:{g['x']}:{g['y']},scale=1080:{GAME_H}:flags=lanczos,eq=saturation=1.08:contrast=1.04:brightness=0.03:gamma=1.12[game];"
          f"[face][game]vstack=inputs=2,"
          f"drawbox=x=0:y={FACE_H-3}:w=1080:h=6:color=0xFF2E4D@1:t=fill,"
          f"ass=short.ass:fontsdir={fonts},format=yuv420p[v]")
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{ss:.3f}", "-t", f"{DUR:.3f}", "-i", SRC,
           "-filter_complex", vf, "-map", "[v]", "-map", "0:a",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.15,afade=t=out:st=%.2f:d=0.3" % (DUR - 0.3),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "60", "-profile:v", "high",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "short_v3.mp4"]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build_ass()
    render()
    print("rendered", round(DUR, 2), "s")
