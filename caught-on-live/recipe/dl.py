import json, sys, os, urllib.request, concurrent.futures as cf
# usage: dl.py <itag> <out> [start end]  -- parallel range download, resumable (chunk files)
itag, out = sys.argv[1], sys.argv[2]
d = json.load(open('../vod_info.json'))
f = [x for x in d['formats'] if x['format_id'] == itag][0]
url, size = f['url'], f['filesize']
start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
end = int(sys.argv[4]) if len(sys.argv) > 4 else size - 1
CH = 4 * 1024 * 1024
os.makedirs(out + '.parts', exist_ok=True)
jobs = [(s, min(s + CH - 1, end)) for s in range(start, end + 1, CH)]
def get(j):
    s, e = j; p = f"{out}.parts/{s:012d}"
    if os.path.exists(p) and os.path.getsize(p) == e - s + 1: return 0
    req = urllib.request.Request(url, headers={'Range': f'bytes={s}-{e}', 'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=60).read()
    open(p + '.tmp', 'wb').write(data); os.replace(p + '.tmp', p); return len(data)
import time; t = time.time(); n = 0; done = 0
with cf.ThreadPoolExecutor(16) as ex:
    for r in ex.map(get, jobs):
        n += r; done += 1
        if time.time() - t > 150: break
missing = [j for j in jobs if not (os.path.exists(f"{out}.parts/{j[0]:012d}") and os.path.getsize(f"{out}.parts/{j[0]:012d}") == j[1]-j[0]+1)]
print('fetched MB', n // 2**20, 'in', int(time.time() - t), 's; missing chunks', len(missing), 'of', len(jobs))
if not missing:
    with open(out, 'wb') as o:
        for s, e in jobs: o.write(open(f"{out}.parts/{s:012d}", 'rb').read())
    print('joined', out, os.path.getsize(out))
