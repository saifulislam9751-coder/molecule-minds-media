"""Rebuild a Short's audio with clean timestamps and a fixed (linear) gain.
Cuts the same parts from the sources as the render did, concatenates them with the
same 60 ms fades, measures loudness, applies one gain + limiter to reach ~-14 LUFS,
writes PCM WAV, then encodes AAC and muxes it with the Short's existing video (copied).
usage: python3 fix_audio.py <module_with_PARTS> <existing_short.mp4> <out.mp4>"""
import importlib.util, json, re, subprocess, sys

mod_path, video_in, out = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("m", mod_path)
m = importlib.util.module_from_spec(spec)
src = open(mod_path).read().split('if __name__ == "__main__":')[0]
exec(compile(src, mod_path, "exec"), m.__dict__)
PARTS = m.PARTS

cmd = ["ffmpeg", "-v", "error", "-y"]
fc = []
for n, p in enumerate(PARTS):
    d = p["b"] - p["a"]
    cmd += ["-ss", f"{p['a'] - p['t0']:.3f}", "-t", f"{d:.3f}", "-i", p["src"]]
    fc.append(f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=N/SR/TB,"
              f"afade=t=in:d=0.06,afade=t=out:st={d - 0.06:.3f}:d=0.06[a{n}]")
fc.append("".join(f"[a{n}]" for n in range(len(PARTS))) + f"concat=n={len(PARTS)}:v=0:a=1[ac]")
cmd += ["-filter_complex", ";".join(fc), "-map", "[ac]", "-c:a", "pcm_f32le", "raw.wav"]
subprocess.run(cmd, check=True)

# measure integrated loudness and true peak of the raw concat
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", "raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                    "-f", "null", "-"], capture_output=True, text=True).stderr
stats = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r, re.S).group(0))
gain = -14.0 - float(stats["input_i"])
print("input_i", stats["input_i"], "input_tp", stats["input_tp"], "-> gain", round(gain, 2), "dB")

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "raw.wav"],
                           capture_output=True, text=True).stdout)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw.wav", "-af",
                f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=5:release=50:level=disabled,"
                f"afade=t=out:st={dur - 0.3:.3f}:d=0.3",
                "-c:a", "pcm_s16le", "fixed.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video_in, "-i", "fixed.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print("wrote", out, "audio", round(dur, 3), "s")
