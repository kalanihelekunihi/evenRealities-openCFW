#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
here=Path(__file__).resolve().parent; repo=Path('/Users/kalani/Repo/evenRealities-openCFW')
def sha(b): return hashlib.sha256(b).hexdigest()
pins=json.loads((here/'evidence-pins.json').read_text())
for key,pin in pins.items():
 f=repo/pin['path']; assert f.is_file() and sha(f.read_bytes())==pin['sha256'], f'pin mismatch: {key}'
record=(repo/pins['record3']['path']).read_bytes(); package=(repo/pins['official_package']['path']).read_bytes()
assert package[1060:1060+len(record)]==record
lo,hi=0x450c,0x4522; body=record[lo:hi]
assert len(body)==22 and sha(body)=='a40f8778cf56af535b68c5ea4cd3ab23c8a4e921ed3717c6ee1095923189377a'
assert (here/'body.bin').read_bytes()==body
assert (here/'boundary-context.bin').read_bytes()==record[0x44c8:0x4530]
# Catalog proposes exact local range; neighboring names/endpoints provide only corroboration.
lines=(repo/pins['symbol_catalog']['path']).read_text().splitlines()
rows=[l.split('\t') for l in lines if l.startswith('0x0030690C\t') or l.startswith('0x00306924\t') or l.startswith('0x003068C8\t')]
assert any(r[:4]==['0x0030690C','0x00306922','22','IRQ_EnableAfterRestore'] for r in rows)
assert any(r[:2]==['0x003068C8','0x0030690C'] for r in rows)
assert any(r[:2]==['0x00306924','0x00306968'] for r in rows)
# Confirm exact caller address, delayed store, and prior value-producing instruction from 1474.
caller=json.loads((repo/pins['caller1474_instructions']['path']).read_text())['instructions']
by={x['address']:x for x in caller}
assert by[0x302cb6]['mnemonic']=='xbfu' and by[0x302cb6]['operands']=='r0,r0,88'
assert by[0x302cc0]['mnemonic']=='bl.d' and by[0x302cc0]['operands']=='15436'
assert by[0x302cc4]['mnemonic']=='st.as' and by[0x302cc4]['operands']=='r0,[r1,72]'
assert by[0x302cba]['mnemonic']=='st.ab' and by[0x302cba]['operands']=='r2,[r1,144]'
edges=json.loads((repo/pins['caller1474_edges']['path']).read_text())
assert any(x.get('site')=='0x00302cc0' and x.get('target')=='0x0030690c' and x.get('delay_slot')=='0x00302cc4: st.as r0,[r1,72]' for x in edges['direct_in_record_calls'])
# Rebuild carrier ELF files with the pinned assembler and restore exact originals.
objdump=repo/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objdump'
for binary,elf,address in [('body.bin','body.elf','0x0030690c'),('boundary-context.bin','boundary-context.elf','0x003068c8')]:
 path=here/elf; original=path.read_bytes()
 try:
  subprocess.run(['python3',str(here/'make_elf.py'),binary,elf,address],cwd=here,check=True,capture_output=True,text=True)
  assert path.read_bytes()==original, f'carrier rebuild mismatch: {elf}'
 finally: path.write_bytes(original)
def decode(elf):
 out=subprocess.run([str(objdump),'-D','-j','.firmware','-M','cpu=em',str(here/elf)],check=True,capture_output=True,text=True).stdout
 # Normalize only the filename header to the candidate's recorded absolute path.
 out=out.replace(str(here/elf), str(repo/'g2/build/pseudocode-first/20260930T190500Z/analysis/arc-direct-callee-30690c-1512/001'/elf), 1)
 return out
assert decode('body.elf')==(here/'body-objdump.txt').read_text()
assert decode('boundary-context.elf')==(here/'boundary-context-objdump.txt').read_text()
def rows(text):
 out=[]
 for line in text.splitlines():
  if not re.match(r'^\s*[0-9a-fA-F]+:',line): continue
  f=re.split(r'\t+',line.strip())
  if len(f)<3: continue
  out.append((int(f[0].rstrip(':'),16),2*len(f[1].split()),f[2].strip(),f[3].strip() if len(f)>3 else ''))
 return out
bodyrows=rows((here/'body-objdump.txt').read_text())
assert len(bodyrows)==7 and sum(r[1] for r in bodyrows)==22 and bodyrows[0][0]==0x30690c and bodyrows[-1][0]+bodyrows[-1][1]==0x306922
assert all(bodyrows[i+1][0]==bodyrows[i][0]+bodyrows[i][1] for i in range(6))
assert bodyrows[0][2]=='mov_s' and bodyrows[-1][2]=='j_s' and bodyrows[-1][3]=='[blink]'
ctx=rows((here/'boundary-context-objdump.txt').read_text())
assert len(ctx)==32 and sum(r[1] for r in ctx)==104 and all(ctx[i+1][0]==ctx[i][0]+ctx[i][1] for i in range(len(ctx)-1))
assert {r[0]:r[2] for r in ctx}[0x30690a]=='j_s' and {r[0]:r[2] for r in ctx}[0x30690c]=='mov_s'
assert {r[0]:r[2] for r in ctx}[0x306920]=='j_s' and {r[0]:r[2] for r in ctx}[0x306922]=='nop_s' and {r[0]:r[2] for r in ctx}[0x306924]=='mov'
ops=(repo/pins['arc_opcode_table']['path']).read_text()
assert '"seti"' in ops and '"bmsk_s"' in ops and '"bset_s"' in ops
receipt=json.loads((here/'receipt.json').read_text())
for name,digest in receipt['outputs'].items():
 candidate_copy=here/(name.replace('.py','-original.py')) if name in ['make_elf.py','verify.py'] else here/name
 assert sha(candidate_copy.read_bytes())==digest, f'output mismatch: {name}'
print('PASS: authenticated 22-byte body, 7 contiguous instructions, catalog seam, caller argument/delay store, carrier rebuild, and output hashes')
