import json, struct, sys, urllib.request
# usage: sidx.py <itag> <out.mp4> <start_s> <end_s>  -> init + fragments covering [start,end]; prints t0
itag, out, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
d = json.load(open('../vod_info.json')); f = [x for x in d['formats'] if x['format_id'] == itag][0]; url = f['url']
def rng(s, e):
    req = urllib.request.Request(url, headers={'Range': f'bytes={s}-{e}', 'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read()
head = rng(0, 1_500_000)
pos = 0; init_end = None; sidx = None
while pos < len(head) - 8:
    size, typ = struct.unpack('>I4s', head[pos:pos+8])
    if size == 1: size = struct.unpack('>Q', head[pos+8:pos+16])[0]
    if typ == b'sidx': sidx = (pos, size)
    if typ in (b'moof', b'mdat'): break
    if typ == b'moov': init_end = pos + size
    pos += size
p, size = sidx; s = head[p:p+size]; ver = s[8]
o = 12 + 4
ts = struct.unpack('>I', s[o:o+4])[0]; o += 4
if ver == 0: ept, foff = struct.unpack('>II', s[o:o+8]); o += 8
else: ept, foff = struct.unpack('>QQ', s[o:o+16]); o += 16
o += 2; n = struct.unpack('>H', s[o:o+2])[0]; o += 2
off = p + size + foff; t = ept / ts; refs = []
for i in range(n):
    rs, dur, _ = struct.unpack('>III', s[o:o+12]); o += 12
    rs &= 0x7fffffff; refs.append((t, t + dur / ts, off, off + rs - 1)); off += rs; t += dur / ts
sel = [r for r in refs if r[1] > a and r[0] < b]
print('timescale', ts, 'refs', n, 'seg ~%.2fs' % (refs[1][0] - refs[0][0]), 'select', len(sel), 't0 %.3f' % sel[0][0], 't1 %.3f' % sel[-1][1], 'bytes', sel[-1][3] - sel[0][2] + 1)
with open(out, 'wb') as w:
    w.write(head[:init_end])
    s0, e0 = sel[0][2], sel[-1][3]; CH = 8 << 20
    import concurrent.futures as cf
    parts = [(x, min(x + CH - 1, e0)) for x in range(s0, e0 + 1, CH)]
    with cf.ThreadPoolExecutor(8) as ex:
        for blob in ex.map(lambda r: rng(*r), parts): w.write(blob)
print('t0', sel[0][0])
