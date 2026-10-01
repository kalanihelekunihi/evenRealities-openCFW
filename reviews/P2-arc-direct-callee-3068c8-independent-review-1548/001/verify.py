#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
here=Path(__file__).resolve().parent;repo=Path('/Users/kalani/Repo/evenRealities-openCFW')
def sha(b):return hashlib.sha256(b).hexdigest()
pins=json.loads((here/'evidence-pins.json').read_text())
for k,p in pins.items():
 f=repo/p['path'];assert f.is_file() and sha(f.read_bytes())==p['sha256'],f'pin mismatch {k}'
record=(repo/pins['record3']['path']).read_bytes();pkg=(repo/pins['official_package']['path']).read_bytes()
assert pkg[1060:1060+len(record)]==record
body=record[0x44c8:0x450c];assert len(body)==68 and sha(body)=='00e23deb878b09fb920d569158424d10cfdd8655021e2acb4a0630287882230a'
assert (here/'body.bin').read_bytes()==body and (here/'boundary-context.bin').read_bytes()==record[0x44c8:0x4530]
# Caller direct-call edge and decoder text establish ordinary BL with no delay slot.
edges=json.loads((repo/pins['caller1288_edges']['path']).read_text())
assert any(x.get('site')=='0x00302b20' and x.get('target')=='0x003068c8' and 'delay_slot' not in x for x in edges['direct_in_record_calls'])
cor=json.loads((repo/pins['caller1288_instructions']['path']).read_text())['instructions'];c={int(x['address'],16):x for x in cor}
assert c[0x302b20]['mnemonic']=='bl' and c[0x302b24]['mnemonic']=='lr'
assert c[0x302b16]['mnemonic']=='lr' and c[0x302b1a]['mnemonic']=='bset_s' and c[0x302b1c]['mnemonic']=='kflag'
# Catalog range and adjoining symbols, while keeping name/report evidentiary limit.
lines=(repo/pins['symbol_catalog']['path']).read_text().splitlines(); rows=[x.split('\t') for x in lines]
assert any(x[:4]==['0x003068C8','0x0030690C','68','IRQ_Cleaning'] for x in rows)
assert any(x[:2]==['0x0030690C','0x00306922'] for x in rows)
assert any(x[:2]==['0x00306924','0x00306968'] for x in rows)
# Rebuild the ARCv2-EM carrier ELF from original bytes, restoring exact output even on failure.
for b,e,a in [('body.bin','body.elf','0x003068c8'),('boundary-context.bin','boundary-context.elf','0x003068c8')]:
 path=here/e;original=path.read_bytes()
 try:
  subprocess.run(['python3',str(here/'make_elf.py'),b,e,a],cwd=here,check=True,capture_output=True,text=True)
  assert path.read_bytes()==original,f'carrier rebuild mismatch {e}'
 finally:path.write_bytes(original)
objdump=repo/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objdump'
def decode(e):
 out=subprocess.run([str(objdump),'-D','-j','.firmware','-M','cpu=em',str(here/e)],check=True,capture_output=True,text=True).stdout
 return out.replace(str(here/e), str(repo/'g2/build/pseudocode-first/20260930T190500Z/analysis/arc-direct-callee-3068c8-1531/001'/e),1)
assert decode('body.elf')==(here/'body-objdump.txt').read_text();assert decode('boundary-context.elf')==(here/'boundary-context-objdump.txt').read_text()
def rows(t):
 z=[]
 for line in t.splitlines():
  if not re.match(r'^\s*[0-9a-fA-F]+:',line):continue
  f=re.split(r'\t+',line.strip())
  if len(f)>=3:z.append((int(f[0].rstrip(':'),16),2*len(f[1].split()),f[2].strip(),f[3].strip() if len(f)>3 else ''))
 return z
brows=rows((here/'body-objdump.txt').read_text());assert len(brows)==21 and sum(x[1] for x in brows)==68 and brows[0][0]==0x3068c8 and brows[-1][0]+brows[-1][1]==0x30690c
assert all(brows[i+1][0]==brows[i][0]+brows[i][1] for i in range(len(brows)-1))
by={x[0]:x for x in brows};assert by[0x3068d0][2]=='mov' and by[0x3068d0][3]=='lp_count,0x12'
assert by[0x3068e0][2]=='lp' and by[0x3068e4][2]=='breq.d.nt' and by[0x3068e8][2]=='mov_s'
assert by[0x3068f0][2]=='add2' and by[0x30690a][2]=='j_s' and by[0x30690a][3]=='[blink]'
ctx=rows((here/'boundary-context-objdump.txt').read_text());assert len(ctx)==32 and sum(x[1] for x in ctx)==104
assert {x[0]:x[2] for x in ctx}[0x30690c]=='mov_s' and {x[0]:x[2] for x in ctx}[0x306922]=='nop_s' and {x[0]:x[2] for x in ctx}[0x306924]=='mov'
receipt=json.loads((here/'receipt.json').read_text())
for n,d in receipt['outputs'].items():
 f=here/(n.replace('.py','-original.py') if n in ['verify.py','make_elf.py'] else n)
 assert sha(f.read_bytes())==d,f'output hash {n}'
print('PASS: source/package mapping, 68-byte/21-instruction body, no-delay caller edge, loop/delay boundaries, adjacent seam, carrier rebuild, receipt hashes')
