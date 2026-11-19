import sys, subprocess, array, os, sherpa_onnx
M = os.environ['HOME'] + '/asr/sherpa-onnx-whisper-turbo/'
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+'turbo-encoder.int8.onnx', decoder=M+'turbo-decoder.int8.onnx', tokens=M+'turbo-tokens.txt', language='hi', task='transcribe', num_threads=4)
T = lambda s: sum(float(x) * 60 ** i for i, x in enumerate(reversed(s.split(':'))))
for w in sys.argv[1:]:
    a, b = [T(p) for p in w.split('-')]
    raw = subprocess.run(['ffmpeg','-v','error','-ss',str(a),'-t',str(b-a),'-i','a139.m4a','-ac','1','-ar','16000','-f','s16le','-'], capture_output=True).stdout
    x = array.array('h'); x.frombytes(raw)
    st = rec.create_stream(); st.accept_waveform(16000, [v/32768 for v in x]); rec.decode_stream(st)
    print(w, '|', st.result.text.strip(), flush=True)
