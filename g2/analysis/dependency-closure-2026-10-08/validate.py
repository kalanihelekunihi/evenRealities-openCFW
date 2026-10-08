from pathlib import Path
import json,hashlib
R=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').exists());L=R/'g2/analysis/source-replacement-ledger-2026-10-08-readonly';h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();b=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';assert h(b)=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5';blob=b.read_bytes()
for file,total,count in [('mapped-functions.json',9472,38),('mapped-readonly-data.json',1166,37)]:
 rows=json.loads((L/file).read_text());assert len(rows)==count and sum(r['bytes'] for r in rows)==total;spans=[]
 for r in rows:
  for kind in ['source','object']:assert h(R/r[kind+'_path'])==r[kind+'_sha256']
  lo=r.get('original_address_start',r.get('address'));hi=r.get('original_address_end',lo+r['bytes']);assert hi-lo==r['bytes'];assert hashlib.sha256(blob[lo-0x410000:hi-0x410000]).hexdigest()==r['sha256'];spans.append((lo,hi))
 spans.sort();assert all(a[1]<=b[0] for a,b in zip(spans,spans[1:]))
manifest=json.loads((R/'g2/analysis/component-audit-2026-10-07T223956Z/input-manifest.json').read_text())['files'];assert len(manifest)==110 and all(h(R/p)==v for p,v in manifest.items());print('PASS38 mapped bodies9472B,37 readonly ranges1166B, source/object hashes and110 sealed inputs')
