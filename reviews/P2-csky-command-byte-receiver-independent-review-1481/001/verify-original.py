#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,struct
HERE=Path(__file__).resolve().parent; ROOT=Path(__file__).resolve().parents[7]; BASE=ROOT/'g2/build/pseudocode-first/20260930T190500Z'; sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((HERE/'input-pins.json').read_text()); raw=(ROOT/p['image']['path']).read_bytes(); assert len(raw)==12288 and sha(raw)==p['image']['sha256']=='9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464'
obj=ROOT/p['tool']['path']; assert sha(obj.read_bytes())==p['tool']['sha256']=='7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
for key in ('manual','data_sleigh','memory_sleigh','branch_sleigh','dsp_sleigh'): assert sha((ROOT/p['instruction_semantics'][key+'_path']).read_bytes())==p['instruction_semantics'][key+'_sha256']
for path,h in p['dependencies'].items():
 d=BASE/path.removesuffix('/receipt.json'); rp=d/'receipt.json'; assert sha(rp.read_bytes())==h,path
 for item in json.loads(rp.read_text())['artifact_manifest']:
  b=(d/item['path']).read_bytes(); assert len(b)==item['bytes'] and sha(b)==item['sha256'],path+'/'+item['path']
g=json.loads((HERE/'geometry.json').read_text()); assert g['runtime_range']==['0x10000BBC','0x10000C1C'] and g['child_file_range']==['0xBD4','0xC34']
body=(HERE/'body.bin').read_bytes(); assert len(body)==96 and body==raw[0xBD4:0xC34] and sha(body)==g['body_sha256']
common=[str(obj),'-D','-z','-b','binary','-m','csky','-EL']; src=ROOT/p['image']['path']
full=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000ba8','--stop-address=0x10000c30',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout; assert full==(HERE/'disassembly-context.txt').read_text()
iso=subprocess.run(common+['--adjust-vma=0x10000bbc',str(HERE/'body.bin')],check=True,text=True,stdout=subprocess.PIPE).stdout; assert iso==(HERE/'disassembly-body.txt').read_text()
ins=[]
for line in iso.splitlines():
 m=re.match(r'^([0-9a-f]{8}):\s+((?:[0-9a-f]{4,8})+)\s+([a-z0-9.]+)',line.strip())
 if m: ins.append((int(m.group(1),16),len(m.group(2))//2,m.group(3),line.lower()))
pos=0x10000bbc
for a,n,m,l in ins: assert a==pos,(hex(a),hex(pos)); pos+=n
assert pos==0x10000c1c and len(ins)>=20 and 'stbi.b' in iso.lower()
nested=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000c1c','--stop-address=0x10000c40',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout; assert nested==(HERE/'nested-caller-disassembly.txt').read_text() and '10000c28:' in nested and '0x10000bbc' in nested
# Authenticate every listed observed caller as an exact BSR and preserve the args recorded from instructions.
ce=(HERE/'caller-callsite-evidence.txt').read_text().lower()
for a in ('10000c28','10000c8e','10000cc6','10000d06','10000d12'):
 l=next((x for x in ce.splitlines() if x.strip().startswith(a+':')),None); assert l and 'bsr' in l and '0x10000bbc' in l
f=json.loads((HERE/'fixtures.json').read_text()); assert f['body_sha256']==sha(body) and len(f['cases'])==5
by={x['name']:x for x in f['cases']}; one=by['mode 3 receives exactly three bytes']['expected']; assert len(one['bytes_stored'])==3 and one['return']=='0x00000000' and one['final_R1']=='0x20000007'
zero=by['zero count still initializes then completes without byte poll']['expected']; assert zero['bytes_stored']==[] and any('0xffffffff' in x for x in zero['events']) and zero['return']=='0x00000000'
ready=by['ready bit remains clear']['expected']; assert ready['bytes_stored']==[] and ready['return']=='does not return'
done=by['completion word remains nonzero after receiving final byte']['expected']; assert len(done['bytes_stored'])==1 and done['return']=='does not return'
wrap=by['three bytes across 32-bit pointer wrap']['expected']; assert [x.split('=')[0] for x in wrap['bytes_stored']]==['u8[0xfffffffe]','u8[0xffffffff]','u8[0x00000000]'] and wrap['final_R1']=='0x00000001'
assert any('R18' in x for x in p['inherited_open_findings']) and any('BKPT' in x for x in p['inherited_open_findings'])
rp=HERE/'receipt.json'
if rp.exists():
 for item in json.loads(rp.read_text())['artifact_manifest']:
  b=(HERE/item['path']).read_bytes(); assert len(b)==item['bytes'] and sha(b)==item['sha256'],item['path']
print(f'PASS: exact source/tool/semantics/dependencies; 96-byte body and mapping; {len(ins)} contiguous instructions; five caller/control/data fixtures; inherited findings and packet manifest')
