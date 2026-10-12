#!/usr/bin/env python3
"""Whole native/target crosswalk for the prepared twelve-slot dispatcher."""
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent
ROOT=P.parents[4]
TOOL=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
B=ROOT/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin'
native=B.read_bytes();assert hashlib.sha256(native).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
target=subprocess.check_output([str(TOOL/'arc-elf32-objdump'),'-dr','-Mcpu=em,dsp',str(P/'source.o')],text=True)
(P/'target.txt').write_text(target)
subprocess.run([str(TOOL/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(P/'source.o'),str(P/'source.text.bin')],check=True)
raw=(P/'source.text.bin').read_bytes()
def rows(text):
 result={}
 for l in text.splitlines():
  a=l.split('\t')
  if len(a)>=3 and re.fullmatch(r'\s*[0-9a-f]+:',a[0]) and a[2].strip():
   result[int(a[0].strip()[:-1],16)]=(a[2].strip(),a[3].strip() if len(a)>3 else '',l)
 return result
n=rows((P/'native.txt').read_text());t=rows(target)
labels={0x32b210:0}
for l in target.splitlines():
 m=re.match(r'([0-9a-f]+) <L([0-9a-f]+)>:',l)
 if m:labels[int(m[2],16)]=int(m[1],16)
assert set(n)==set(labels),(set(n)-set(labels),set(labels)-set(n))
exp={0x32b230,0x32b23c,0x32b248,0x32b254,0x32b260,0x32b26c,0x32b278,0x32b284,0x32b290,0x32b29c,0x32b2aa,0x32b2b8}
children={'323374':'opencfw_em9305_mode_event_323374','31c420':'opencfw_em9305_mode_event_31c420'}
def norm(s):
 s=re.sub(r'0x([0-9a-f]+)',lambda m:str(int(m[1],16)),s)
 return re.sub(r'\s+','',s).replace(',0]',']')
addresses=sorted(n);calls=0;branches=0
for i,a in enumerate(addresses):
 m,o,l=n[a];q=labels[a];tm,to,tl=t[q]
 end=addresses[i+1] if i+1<len(addresses) else 0x32b2d0
 tend=labels[end] if end in labels else q+(end-a)
 if m in ('bl','bl.d'):
  dest=re.search(r';0x([0-9a-f]+)',l)[1];sym=children[dest]
  assert tm==m and f'{q:x}: R_ARC_S25W_PCREL\t{sym}' in target,(hex(a),tm,sym)
  assert end-a==tend-q==4;calls+=1
 elif ';0x' in l:
  dest=int(re.search(r';0x([0-9a-f]+)',l)[1],16)
  assert tm==m or (a==0x32b29a and m=='brne_s' and tm=='brne.nt'),(hex(a),m,tm)
  assert norm(o.rsplit(',',1)[0] if ',' in o else '')==norm(to.rsplit(',',1)[0] if ',' in to else ''),(hex(a),o,to)
  assert re.search(r'<L([0-9a-f]+)>',tl) and int(re.search(r'<L([0-9a-f]+)>',tl)[1],16)==dest,(hex(a),tl)
  assert end-a==tend-q or (a==0x32b29a and end-a==2 and tend-q==4);branches+=1
 elif a in exp:
  assert m=='ld_s' and tm=='ld' and norm(o)==norm(to),(hex(a),m,o,tm,to)
  assert end-a==2 and tend-q==4
 else:
  assert raw[q:tend]==native[a-0x302400:end-0x302400],(hex(a),m,o,tm,to)
assert sum(m=='jl_s.d' for m,o,l in n.values())==12
assert sum(m=='jl_s.d' for m,o,l in t.values())==12
receipt={'status':'PASS_WHOLE_NATIVE_INSTRUCTION_CROSSWALK','selected':False,'instructions':len(n),'native_function_bytes':192,'target_function_bytes':218,'genuine_child_calls':calls,'reviewed_local_branches':branches,'indirect_callback_slots':12,'baseline_ld_expansions':[hex(a) for a in sorted(exp)],'source_sha256':hashlib.sha256((P/'source.c').read_bytes()).hexdigest(),'limits':['Twelve baseline LDs and one full branch expansion prevent whole function byte equality.','Child providers/register contracts and final image remain separate gates.','No hardware execution.']}
(P/'crosswalk-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
