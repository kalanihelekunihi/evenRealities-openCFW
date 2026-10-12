import hashlib,json,struct,subprocess
from pathlib import Path
p=Path(__file__).resolve().parent
root=next(q for q in p.parents if (q/'.git').exists())
objdump=root/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin/arc-elf32-objdump'
elf=p/'contexts-placement.elf'
out=subprocess.check_output([str(objdump),'-h',str(elf)],text=True)
expected={'.rodata':(0x3357b4,12),'.context_802a60':(0x802a60,704),'.context_8035dc':(0x8035dc,704),'.context_80389c':(0x80389c,704)}
found={}; lines=out.splitlines()
for i,line in enumerate(lines):
 s=line.split()
 if len(s)>5 and s[1] in expected:
  name=s[1]; size=int(s[2],16);addr=int(s[3],16)
  assert (addr,size)==expected[name]
  flags=lines[i+1];assert ('CONTENTS' in flags)==(name=='.rodata')
  found[name]={'address':addr,'bytes':size,'flags':flags.strip()}
  if name=='.rodata':
   data=elf.read_bytes()[int(s[5],16):int(s[5],16)+size]
   assert data==struct.pack('<III',0x8035dc,0x802a60,0x80389c)
assert set(found)==set(expected)
r={'status':'PASS_ISOLATED_FIXED_CONTEXT_PLACEMENT_AND_EXACT_NATIVE_TABLE_BYTES','sections':found,'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'limits':['Isolated layout only; full firmware overlap, startup zeroing and runtime ownership remain open.']}
(p/'contexts-placement-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
