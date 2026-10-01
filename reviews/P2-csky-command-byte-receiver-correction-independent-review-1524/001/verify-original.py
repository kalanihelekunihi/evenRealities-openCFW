#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess,re,importlib.util
HERE=Path(__file__).resolve().parent; ROOT=Path(__file__).resolve().parents[7]; CAMP=ROOT/'g2/build/pseudocode-first/20260930T190500Z'; sha=lambda b:hashlib.sha256(b).hexdigest()
p=json.loads((HERE/'input-pins.json').read_text()); img=ROOT/p['image']['path']; raw=img.read_bytes(); assert len(raw)==p['image']['bytes'] and sha(raw)==p['image']['sha256']=='9546164f32680de47fa99ba85ba08a3c538822260957de6c1baee772638da464'
obj=ROOT/p['tool']['path']; assert sha(obj.read_bytes())==p['tool']['sha256']=='7150f7ffc2ac163f3d2d465620e5dac96df4b29411e5d0944419c41657cc2382'
for x in p['instruction_semantics'].values():
 if isinstance(x,dict) and 'manual_path' in x: assert sha((ROOT/x['manual_path']).read_bytes())==x['manual_sha256']
 elif isinstance(x,dict) and 'data_sleigh_path' in x: assert sha((ROOT/x['data_sleigh_path']).read_bytes())==x['data_sleigh_sha256']
 elif isinstance(x,dict) and 'memory_sleigh_path' in x: assert sha((ROOT/x['memory_sleigh_path']).read_bytes())==x['memory_sleigh_sha256']
 elif isinstance(x,dict) and 'branch_sleigh_path' in x: assert sha((ROOT/x['branch_sleigh_path']).read_bytes())==x['branch_sleigh_sha256']
 elif isinstance(x,dict) and 'dsp_sleigh_path' in x: assert sha((ROOT/x['dsp_sleigh_path']).read_bytes())==x['dsp_sleigh_sha256']
for path,h in p['dependencies'].items():
 d=CAMP/path; assert sha(d.read_bytes())==h,path
 for item in json.loads(d.read_text())['artifact_manifest']:
  b=(d.parent/item['path']).read_bytes(); assert len(b)==item['bytes'] and sha(b)==item['sha256'],path+'/'+item['path']
sup=p['supersedes']; assert sha((CAMP/sup['receipt_path']).read_bytes())==sup['receipt_sha256']
body=(HERE/'body.bin').read_bytes(); assert body==raw[0xBD4:0xC34] and len(body)==96 and sha(body)==json.loads((HERE/'geometry.json').read_text())['body_sha256']
common=[str(obj),'-D','-z','-b','binary','-m','csky','-EL']; src=ROOT/p['image']['path']
ctx=subprocess.run(common+['--adjust-vma=0x0fffffe8','--start-address=0x10000ba8','--stop-address=0x10000c30',str(src)],check=True,text=True,stdout=subprocess.PIPE).stdout; assert ctx==(HERE/'disassembly-context.txt').read_text()
iso=subprocess.run(common+['--adjust-vma=0x10000bbc',str(HERE/'body.bin')],check=True,text=True,stdout=subprocess.PIPE).stdout; assert iso==(HERE/'disassembly-body.txt').read_text()
assert (HERE/'poll-condition-evidence.txt').read_text()==''.join(l+'\n' for l in iso.splitlines() if l.strip().startswith(('10000c0a:','10000c0c:','10000c10:')))
assert re.search(r'10000c0c:\s+e4422008\s+andi\s+r2, r2, 8',iso) and re.search(r'10000c10:\s+e902fffd\s+bez\s+r2, 0x10000c0a',iso)
assert len(re.findall(r'bsr\s+0x10000b4c',iso))==2
spec=importlib.util.spec_from_file_location('replay',HERE/'replay.py'); replay=importlib.util.module_from_spec(spec); spec.loader.exec_module(replay)
f=json.loads((HERE/'fixtures.json').read_text()); assert len(f['cases'])==9 and f['body_sha256']==sha(body)
for c in f['cases']:
 q=c['inputs']; ptr=int(q['pointer'],16); actual=replay.run(q['mode'],ptr,q['count'],q['data_words'],q['pre_words'],q['ready_per_byte'],q['completion_words'],q['post_words']); assert actual==c['expected'],q['name']
by={x['name']:x for x in f['cases']}; assert by['bit 1 alone does not satisfy ready predicate bit 3']['expected']['result']=='still polling for ready before byte 0'; assert by['bit 2 alone does not satisfy ready predicate bit 3']['expected']['result']=='still polling for ready before byte 0'
ready=by['bit 3 set transfers low byte of data word']['expected']; assert ready['bytes_stored'][0]['byte']==0xef
rp=HERE/'receipt.json'
if rp.exists():
 for item in json.loads(rp.read_text())['artifact_manifest']:
  b=(HERE/item['path']).read_bytes(); assert len(b)==item['bytes'] and sha(b)==item['sha256'],item['path']
print('PASS: original source/tool/dependency pins; exact C0C mask-8 plus C10 zero branch; 96-byte geometry; 9 replayed counterexample/poll traces')
