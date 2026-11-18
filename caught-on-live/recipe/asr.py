"""Transcribe parts of the stream audio with sherpa-onnx Whisper (Hindi).
usage: python3 asr.py START_SEC END_SEC [out.json]
Uses Silero VAD to cut speech segments, then Whisper on each segment."""
import sys, json, time
import numpy as np
import sherpa_onnx

M = "/home/claude/asr/sherpa-onnx-whisper-small"
SR = 16000
start, end = float(sys.argv[1]), float(sys.argv[2])
out = sys.argv[3] if len(sys.argv) > 3 else None

a = np.fromfile("/home/claude/clip/audio16k.pcm", dtype=np.int16).astype(np.float32) / 32768
seg = a[int(start * SR):int(end * SR)]

rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{M}/small-encoder.int8.onnx", decoder=f"{M}/small-decoder.int8.onnx",
    tokens=f"{M}/small-tokens.txt", language="hi", task="transcribe", num_threads=2)

cfg = sherpa_onnx.VadModelConfig()
cfg.silero_vad.model = "/home/claude/asr/silero_vad.onnx"
cfg.silero_vad.min_silence_duration = 0.25
cfg.silero_vad.min_speech_duration = 0.25
cfg.silero_vad.max_speech_duration = 8
cfg.silero_vad.threshold = 0.5
cfg.sample_rate = SR
vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=600)

win = cfg.silero_vad.window_size
segs = []
for i in range(0, len(seg) - win, win):
    vad.accept_waveform(seg[i:i + win])
    while not vad.empty():
        s = vad.front; segs.append((s.start / SR, np.array(s.samples))); vad.pop()
vad.flush()
while not vad.empty():
    s = vad.front; segs.append((s.start / SR, np.array(s.samples))); vad.pop()

t0 = time.time()
res = []
for st, samples in segs:
    stream = rec.create_stream()
    stream.accept_waveform(SR, samples)
    rec.decode_stream(stream)
    txt = stream.result.text.strip()
    res.append({"t": round(start + st, 2), "d": round(len(samples) / SR, 2), "text": txt})
    print(f"{int((start+st)//60):02d}:{(start+st)%60:05.2f} ({len(samples)/SR:.1f}s) {txt}", flush=True)
print(f"# {len(segs)} segments, {sum(len(s) for _, s in segs)/SR:.0f}s speech, decoded in {time.time()-t0:.0f}s", file=sys.stderr)
if out:
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
