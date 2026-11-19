# Pulling parts of a finished stream VOD (Mac VM)

Run these on the owner's Mac VM: the cloud gets YouTube's bot check.

- `yt-dlp --js-runtimes node -J <url> > vod_info.json` saves the format URLs (valid ~6 h, tied to the Mac's IP).
- `dl.py <itag> <out>` downloads a whole format with parallel Range requests (about 15 MB/s). Use 139 (48 kbps audio, ~210 MB for 10 h) to scan loudness.
- `sidx.py <itag> <out.mp4> <start_s> <end_s>` reads the DASH sidx index and fetches only the init segment plus the fragments that cover the window. It prints t0, which equals the output's `start_time` in stream seconds. Use 299 (1080p60) and 140 (audio). ffmpeg can't open URLs through the proxy, so this replaces `--download-sections`.
- Finding moments: the VOD's top comments with timestamps (`--write-comments`, comment_sort=top) work best, plus per-second RMS spikes over a 2-minute median. Then contact sheets in the built-in browser, then sherpa-onnx whisper-turbo (language hi) on the candidate windows. That takes about 8.5 s per window of up to 30 s, on 4 threads.
- Mac → cloud: device_stage_files times out on ~75 MB. `split -b 20m`, stage the pieces, `cat` them back and check the md5.
