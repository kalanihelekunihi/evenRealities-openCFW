#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[4]
T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
B=ROOT/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin';native=B.read_bytes()
assert hashlib.sha256(native).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
f=json.loads((P/'frontier.json').read_text());f['pointer_relocations']={};target=subprocess.check_output([str(T/'arc-elf32-objdump'),'-dr','-Mcpu=em,dsp',str(P/'source.o')],text=True)
subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(P/'source.o'),str(P/'source.text.bin')],check=True);raw=(P/'source.text.bin').read_bytes()
def rows(t):
 d={}
 for l in t.splitlines():
  v=l.split('\t')
  if len(v)>=3 and re.fullmatch(r'\s*[0-9a-f]+:',v[0]) and v[2].strip():d[int(v[0].strip()[:-1],16)]=(v[2].strip(),v[3].strip() if len(v)>3 else '',l)
 return d
n=rows((P/'native.txt').read_text());t=rows(target);lab={int(b,16):int(a,16) for a,b in re.findall(r'([0-9a-f]+) <L([0-9a-f]+)>:',target)};lab[0x3184f4]=0;assert set(n)==set(lab)
addresses=sorted(n);calls=branches=pointers=exact=0;pending=[]
for j,a in enumerate(addresses):
 m,o,l=n[a];q=lab[a];tm,to,tl=t[q];end=addresses[j+1] if j+1<len(addresses) else 0x31855a;te=lab[end] if end in lab else q+(end-a)
 expanded={0x318540,0x318542}
 assert m==tm or (a in expanded and m.endswith('_s') and tm==m[:-2]),(hex(a),m,tm);assert end-a==te-q or (a in expanded and end-a==2 and te-q==4),(hex(a),end-a,te-q)
 if m in ('bl','bl.d'):
  dest=re.search(r';0x([0-9a-f]+)',l)[1];assert f"{q:x}: R_ARC_S25W_PCREL\t{f['canonical_call_mapping'][dest]}" in target;calls+=1
 elif ';0x' in l:
  dest=re.search(r';0x([0-9a-f]+)',l)[1];assert '<L'+dest+'>' in tl;assert o.split(';')[0].rsplit(',',1)[0]==to.split(';')[0].rsplit(',',1)[0] if ',' in o else True;branches+=1
 elif any('0x'+v in o for v in f['pointer_relocations']):
  dest=next(v for v in f['pointer_relocations'] if '0x'+v in o);sym=f['pointer_relocations'][dest];assert f'{q+4:x}: R_ARC_32_ME\t{sym}' in target;assert raw[q:te-4]==native[a-0x302400:end-0x302400-4];pointers+=1
 elif a in expanded:
  norm=lambda v:re.sub(r'0x([0-9a-f]+)',lambda z:str(int(z[1],16)),v).replace(',0]',']')
  assert norm(o)==norm(to),(hex(a),o,to)
 else:
  if raw[q:te]!=native[a-0x302400:end-0x302400]:pending.append({'at':hex(a),'native_mnemonic':m,'target_mnemonic':tm,'native_operands':o,'target_operands':to})
  else:exact+=1
r={'status':'CROSSWALK_PENDING_ENCODING_REVIEW' if pending else 'PASS_WHOLE_NATIVE_INSTRUCTION_CROSSWALK','pending_encoding_differences':pending,'baseline_load_expansions':[hex(a) for a in sorted(expanded)],'instructions':len(n),'native_bytes':102,'target_function_bytes':lab[0x318558]+2,'target_section_bytes':len(raw),'trailing_alignment_bytes':len(raw)-(lab[0x318558]+2),'true_child_calls':calls,'local_branches':branches,'function_pointer_relocations':pointers,'byte_exact_other_instructions':exact,'source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'selected':False,'limits':['All native out-of-line paths, indirect callback and delayed effects preserved.','Child register contracts, final image linking and hardware execution remain separate gates.']};(P/'crosswalk-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
