#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess,re
HERE=Path(__file__).resolve().parent; ROOT=Path(__file__).resolve().parents[7]; CAMP=ROOT/'g2/build/pseudocode-first/20260930T190500Z'; sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((HERE/'input-pins.json').read_text()); img=ROOT/p['image']['path']; raw=img.read_bytes(); assert len(raw)==p['image']['bytes'] and sha(raw)==p['image']['sha256']=='9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464'
obj=ROOT/p['tool']['path']; assert sha(obj.read_bytes())==p['tool']['sha256']=='7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
for x in p['semantics_sources'].values(): assert sha((ROOT/x['path']).read_bytes())==x['sha256']
for dep,h in p['dependency_receipts'].items():
 d=CAMP/dep; assert sha(d.read_bytes())==h
 folder=d.parent
 for x in json.loads(d.read_text())['artifact_manifest']:
  b=(folder/x['path']).read_bytes(); assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
body=(HERE/'body.bin').read_bytes(); g=json.loads((HERE/'geometry.json').read_text()); assert body==raw[0xB64:0xB74] and len(body)==16 and sha(body)==g['body_sha256']
common=[str(obj),'-D','-z','-b','binary','-m','csky','-EL']
ctx=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000b38','--stop-address=0x10000b68',str(img)],check=True,text=True,stdout=subprocess.PIPE).stdout; assert ctx==(HERE/'disassembly-context.txt').read_text()
iso=subprocess.run(common+['--adjust-vma=0x10000b4c',str(HERE/'body.bin')],check=True,text=True,stdout=subprocess.PIPE).stdout; assert iso==(HERE/'disassembly-body.txt').read_text()
full=subprocess.run(common+['--adjust-vma=0x0fffffe8',str(img)],check=True,text=True,stdout=subprocess.PIPE).stdout
allsites=[]
for l in full.splitlines():
 if 'bsr' in l and '0x10000b4c' in l: allsites.append(l.strip())
expected=[0x10000b64,0x10000ba2,0x10000bc4,0x10000c02,0x10000dc4,0x10000e18]
assert len(allsites)==6 and [int(re.match(r'([0-9a-f]+):',x).group(1),16) for x in allsites]==expected
assert (HERE/'direct-call-sites.txt').read_text().splitlines()==allsites
ins=[]
for l in iso.splitlines():
 m=re.match(r'^([0-9a-f]{8}):\s+((?:[0-9a-f]{4,8})+)\s+([a-z0-9.]+)',l.strip())
 if m: ins.append((int(m.group(1),16),len(m.group(2))//2,m.group(3)))
pos=0x10000b4c
for a,n,m in ins: assert a==pos; pos+=n
assert pos==0x10000b5c and [x[2] for x in ins]==['movi','lsli','ld.w','andi','bnez','jmp']
f=json.loads((HERE/'fixtures.json').read_text()); assert len(f['cases'])==5 and f['body_sha256']==sha(body)
for c in f['cases']:
 steps=c['steps']; assert c['reads']==len(steps) and len(steps)==len(c['controlled_words']) and c['writes']==[]
 if c['result']=='returns R0=0': assert steps[-1]['masked_bit0']==0
 else: assert all(x['masked_bit0']==1 for x in steps)
print(f'PASS: source/tool/dependency pins; 16-byte exact body; six contiguous instructions; six full-image callers; five controlled poll traces')
