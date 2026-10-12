#!/usr/bin/env python3
from pathlib import Path
import subprocess,re,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[4];T=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/arc-binutils-001/prefix/bin'
n=(ROOT/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(n).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
f=json.loads((P/'frontier.json').read_text());result=[]
def rows(s):
 d={}
 for l in s.splitlines():
  v=l.split('\t')
  if len(v)>=3 and re.fullmatch(r'\s*[0-9a-f]+:',v[0]) and v[2].strip():d[int(v[0].strip()[:-1],16)]=(v[2].strip(),v[3].strip() if len(v)>3 else '',l)
 return d
def norm(s):return re.sub(r'0x([0-9a-f]+)',lambda z:str(int(z[1],16)),s).replace(',0]',']')
for name,start,end in [('callback-329574',0x329574,0x32960e),('callback-329560',0x329560,0x329574),('reset-32ae50',0x32ae50,0x32ae70)]:
 target=subprocess.check_output([str(T/'arc-elf32-objdump'),'-dr','-Mcpu=em,dsp',str(P/(name+'.o'))],text=True)
 subprocess.run([str(T/'arc-elf32-objcopy'),'-O','binary','-j','.text',str(P/(name+'.o')),str(P/(name+'.bin'))],check=True);raw=(P/(name+'.bin')).read_bytes()
 nr=rows((P/(name+'.native.txt')).read_text());tr=rows(target);lab={int(b,16):int(a,16) for a,b in re.findall(r'([0-9a-f]+) <L([0-9a-f]+)>:',target)};lab[start]=0;assert set(nr)==set(lab);aa=sorted(nr);expanded={0x3295a4,0x3295a8,0x3295b2};calls=branches=0
 for j,a in enumerate(aa):
  m,o,l=nr[a];q=lab[a];tm,to,tl=tr[q];e=aa[j+1] if j+1<len(aa) else end;te=lab[e] if e in lab else q+(e-a)
  assert m==tm or (a in expanded and m=='ld_s' and tm=='ld'),(hex(a),m,tm)
  assert e-a==te-q or (a in expanded and e-a==2 and te-q==4),(hex(a),e-a,te-q)
  if m in ('bl','bl.d'):
   dest=re.search(r';0x([0-9a-f]+)',l)[1];assert f'{q:x}: R_ARC_S25W_PCREL\t'+f['children'][dest] in target;calls+=1
  elif ';0x' in l:
   dest=re.search(r';0x([0-9a-f]+)',l)[1];assert '<L'+dest+'>' in tl
   if ',' in o:assert norm(o.rsplit(',',1)[0])==norm(to.rsplit(',',1)[0]);branches+=1
  elif a in expanded:assert norm(o)==norm(to)
  else:assert raw[q:te]==n[a-0x302400:e-0x302400],(hex(a),m,o)
 result.append({'body':name,'status':'PASS_WHOLE_NATIVE_INSTRUCTION_CROSSWALK','instructions':len(nr),'native_bytes':end-start,'target_function_bytes':lab[aa[-1]]+(end-aa[-1]),'true_calls':calls,'local_branches':branches,'source_sha256':hashlib.sha256((P/(name+'.c')).read_bytes()).hexdigest(),'selected':False})
(P/'crosswalk-receipt.json').write_text(json.dumps({'bodies':result,'remaining_provider':'329888','limits':['Unknown indirect callbacks and native child register contracts remain gates.','No hardware execution or full image proof.']},indent=2)+'\n');print(result)
