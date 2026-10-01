#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,re,subprocess,importlib.util
HERE=Path(__file__).resolve().parent; ROOT=Path('/Users/kalani/Repo/evenRealities-openCFW'); CAMP=ROOT/'g2/build/pseudocode-first/20260930T190500Z'; sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((HERE/'input-pins.json').read_text()); img=ROOT/p['image']['path']; raw=img.read_bytes(); assert len(raw)==12288 and sha(raw)==p['image']['sha256']=='9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464'
obj=ROOT/p['tool']['path']; assert sha(obj.read_bytes())==p['tool']['sha256']=='7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
for d,h in p['dependencies'].items():
 rp=CAMP/d; assert sha(rp.read_bytes())==h
 for x in json.loads(rp.read_text())['artifact_manifest']:
  b=(rp.parent/x['path']).read_bytes(); assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
for x in p['semantics_sources'].values(): assert sha((ROOT/x['path']).read_bytes())==x['sha256']
body=(HERE/'body.bin').read_bytes(); assert body==raw[0xB10:0xB1A] and len(body)==10 and sha(body)==json.loads((HERE/'geometry.json').read_text())['body_sha256']
lit=(HERE/'adjacent-literal.bin').read_bytes(); assert lit==raw[0xB0C:0xB10]==bytes.fromhex('80120020')
adj=json.loads((HERE/'adjacent-ranges.json').read_text()); assert adj['before_candidate']['runtime_range']==['0x10000AF4','0x10000AF8'] and adj['before_candidate']['raw_hex']==lit.hex() and adj['before_candidate']['little_endian_value']=='0x20001280'; assert adj['after_candidate']['runtime_range']==['0x10000B02','0x10000B04'] and raw[0xB1A:0xB1C].hex()==adj['after_candidate']['raw_hex']=='0000'
common=[str(obj),'-D','-z','-b','binary','-m','csky','-EL']; src=ROOT/p['image']['path']
ctx=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000ae0','--stop-address=0x10000b0a',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout; ctx=ctx.replace(str(src),str(ROOT/p['image']['path'])); assert ctx==(HERE/'disassembly-context.txt').read_text()
iso=subprocess.run(common+['--adjust-vma=0x10000af8',str(HERE/'body.bin')],check=True,text=True,stdout=subprocess.PIPE).stdout; iso=iso.replace(str(HERE),str(ROOT/'g2/build/pseudocode-first/20260930T190500Z/analysis/csky-9cc-zero-arg-wrapper-1525/001')); assert iso==(HERE/'disassembly-body.txt').read_text()
assert [m.group(3) for l in iso.splitlines() if (m:=re.match(r'^([0-9a-f]{8}):\s+((?:[0-9a-f]{4,8})+)\s+([a-z0-9.]+)',l.strip()))]==['push','movi','bsr','pop']
assert '0x100009cc' in iso.lower() and 'movi' in iso.lower() and re.search(r'10000afa:\s+3200\s+movi\s+r2, 0',iso)
assert '10000ae6:' in ctx and '0x10000af4' in ctx and '10000b02:' in ctx and 'bkpt' in ctx
full=subprocess.run(common+['--adjust-vma=0x0fffffe8',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout; calls=[l.strip() for l in full.splitlines() if 'bsr' in l and '0x10000af8' in l]; sites=[0x10000d5e,0x10000ea4,0x10000eb8,0x10000ec0]; assert len(calls)==4 and [int(re.match(r'([0-9a-f]+):',l).group(1),16) for l in calls]==sites and (HERE/'direct-call-sites.txt').read_text().splitlines()==calls
assert subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000d48','--stop-address=0x10000d72',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout==(HERE/'caller-c40-context.txt').read_text()
assert subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000e84','--stop-address=0x10000ef0',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout==(HERE/'caller-e84-context.txt').read_text()
spec=importlib.util.spec_from_file_location('replay',HERE/'replay.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); f=json.loads((HERE/'fixtures.json').read_text()); assert len(f['cases'])==4 and f['body_sha256']==sha(body)
for c in f['cases']:
 q=c['inputs']; assert mod.run(q['R0'],q['R1'],q['R2'],q['LR'],q['callee_state'])==c['expected'],c['name']
rp=HERE/'receipt.json'
if rp.exists():
 for x in json.loads(rp.read_text())['artifact_manifest']:
  candidate_file=HERE/('verify-original.py' if x['path']=='verify.py' else x['path'])
  b=candidate_file.read_bytes(); assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
print('PASS: original source/tool/dependencies; 10-byte wrapper; 4 exact callers; AF4 literal/B02 BKPT boundaries; 4 child-controlled static traces')
