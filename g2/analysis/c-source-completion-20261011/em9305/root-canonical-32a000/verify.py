#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json,hashlib,tempfile
P=Path(__file__).resolve().parent;R=P.parents[4];T=R/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin';c=json.loads((P/'correction.json').read_text());rows=[]
for x in c['callers']:
 name=Path(x['selected_source']).stem;original=R/'g2/build/c-firmware/20261012/em-root-dispatch-round34/ble_em9305'/('controller_lower_'+name+'.o');draft=P/(name+'.o')
 def textbytes(o):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'text';subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(o),str(p)],check=True);return p.read_bytes()
 assert textbytes(original)==textbytes(draft),name
 def relocs(o):
  s=subprocess.check_output([str(T/'arc-elf32-objdump'),'-r',str(o)],text=True)
  return re.findall(r'^([0-9a-f]+)\s+(R_ARC_\w+)\s+(\S+)',s,re.M)
 old=relocs(original);new=relocs(draft);assert [(a,b,v.replace(c['old_symbol'],c['canonical_symbol'])) for a,b,v in old]==new
 changed=[(a,b,v) for a,b,v in new if v==c['canonical_symbol']];assert len(changed)==1
 assert hashlib.sha256((P/(name+'.c')).read_bytes()).hexdigest()==x['draft_sha256']
 rows.append({'caller':name,'text_bytes':len(textbytes(draft)),'canonical_relocation':changed[0]})
r={'status':'PASS_IDENTICAL_TEXT_AND_SINGLE_CANONICAL_RELOCATION_PER_CALLER','callers':rows,'limits':['Compared against audited round34 objects; final coherent linking remains pending.']};(P/'verification-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
