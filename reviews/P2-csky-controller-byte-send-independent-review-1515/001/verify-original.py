#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess,re,importlib.util
HERE=Path(__file__).resolve().parent; ROOT=Path(__file__).resolve().parents[7]; CAMP=ROOT/'g2/build/pseudocode-first/20260930T190500Z'; sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((HERE/'input-pins.json').read_text()); img=ROOT/p['image']['path']; raw=img.read_bytes(); assert len(raw)==p['image']['bytes'] and sha(raw)==p['image']['sha256']=='9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464'
obj=ROOT/p['tool']['path']; assert sha(obj.read_bytes())==p['tool']['sha256']=='7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
for x in p['isa_semantics_sources'].values():assert sha((ROOT/x['path']).read_bytes())==x['sha256']
for dep,h in p['dependency_receipts'].items():
 d=CAMP/dep; assert sha(d.read_bytes())==h; folder=d.parent
 for x in json.loads(d.read_text())['artifact_manifest']:
  b=(folder/x['path']).read_bytes(); assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
body=(HERE/'body.bin').read_bytes(); g=json.loads((HERE/'geometry.json').read_text()); assert len(body)==96 and body==raw[0xB74:0xBD4] and sha(body)==g['body_sha256']
common=[str(obj),'-D','-z','-b','binary','-m','csky','-EL']
ctx=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000b50','--stop-address=0x10000bc0',str(img)],check=True,text=True,stdout=subprocess.PIPE).stdout; assert ctx==(HERE/'disassembly-context.txt').read_text()
iso=subprocess.run(common+['--adjust-vma=0x10000b5c',str(HERE/'body.bin')],check=True,text=True,stdout=subprocess.PIPE).stdout; assert iso==(HERE/'disassembly-body.txt').read_text()
pathctx=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000c40','--stop-address=0x10000d50',str(img)],check=True,text=True,stdout=subprocess.PIPE).stdout; assert pathctx==(HERE/'caller-path-context.txt').read_text() and re.search(r'andi\s+r8, r3, 2',pathctx) and re.search(r'bnez\s+r8',pathctx)
full=subprocess.run(common+['--adjust-vma=0x0fffffe8',str(img)],check=True,text=True,stdout=subprocess.PIPE).stdout; allc=[l.strip() for l in full.splitlines() if 'bsr' in l and '0x10000b5c' in l]; expected=[0x10000cec,0x10000d38,0x10000d42]; assert len(allc)==3 and [int(re.match(r'([0-9a-f]+):',x).group(1),16) for x in allc]==expected and (HERE/'direct-call-sites.txt').read_text().splitlines()==allc
ins=[]
for l in iso.splitlines():
 m=re.match(r'^([0-9a-f]{8}):\s+((?:[0-9a-f]{4,8})+)\s+([a-z0-9.]+)',l.strip())
 if m:ins.append((int(m.group(1),16),len(m.group(2))//2,m.group(3)))
pos=0x10000b5c
for a,n,m in ins:assert a==pos;pos+=n
assert pos==0x10000bbc and len(ins)>=30 and 'ldbi.b' in iso.lower() and 'bnez' in iso.lower() and 'bez' in iso.lower()
spec=importlib.util.spec_from_file_location('replay',HERE/'replay.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
f=json.loads((HERE/'fixtures.json').read_text()); assert f['body_sha256']==sha(body) and len(f['cases'])==9
for c in f['cases']:
 q=c['inputs']; expected_result=c['expected']; actual=mod.run(q['mode'],q['pointer'],q['count'],q['data'],q['pre'],q['ready'],q['completion'],q['post']); assert actual==expected_result,(q['name'],actual,expected_result)
assert f['cases'][0]['expected']['result']=='returns R0=0' and len(f['cases'][2]['expected']['bytes_loaded'])==3
rp=HERE/'receipt.json'
if rp.exists():
 for x in json.loads(rp.read_text())['artifact_manifest']:
  b=(HERE/x['path']).read_bytes(); assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
print(f'PASS: source/tool/dependency pins; 96-byte body; {len(ins)} contiguous decoded instructions; 3 full-image callers; 9 replayed MMIO/input traces')
