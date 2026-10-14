#!/usr/bin/env python3
"""Conservative nativeCFG constant-address provenance, not codecoverage promotion."""
from pathlib import Path
import re,json,struct,hashlib,collections
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';blob=F.read_bytes()[32:];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();baseline=json.loads((H.parent/'case-wave025-ram-callback-provenance/verification.json').read_text());targets={int(x['address'],16) for x in baseline['RAM_literals']};catalogue=R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl';functions=list(map(json.loads,catalogue.read_text().splitlines()));ins={}
for line in (H/'native-disassembly.txt').read_text().splitlines():
 m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)',line)
 if m:ins[int(m[1],16)]={'size':len(m[2].split())*2,'op':m[3].split('.')[0],'args':m[4].split('@')[0].strip(),'text':line.strip()}
alias={'sl':'r10','fp':'r11','ip':'r12'}
def reg(s):return alias.get(s.strip(),s.strip())
def imm(s):
 try:return int(s.strip().lstrip('#'),0)
 except ValueError:return None
def value(s,state):
 s=reg(s)
 return state.get(s) if re.fullmatch(r'r\d+|sp|lr|pc',s) else imm(s)
hits=collections.defaultdict(list);unknown_ops=collections.Counter();states_seen=0
for fn in functions:
 start=int(fn['entry'],16);lo=int(fn['body_start'],16);hi=int(fn['body_end_inclusive'],16)+1
 if start not in ins:continue
 incoming={start:{}};work=collections.deque([start]);steps=0
 while work and steps<10000:
  pc=work.popleft();steps+=1;states_seen+=1
  if pc not in ins or not lo<=pc<hi:continue
  i=ins[pc];op=i['op'];args=i['args'];state=dict(incoming[pc]);out=dict(state);next_pc=pc+i['size'];successors=[next_pc]
  def record(address,size,kind):
   if address is None:return
   for t in targets:
    if address<=t<address+size and len(hits[t])<12:hits[t].append({'function_entry':hex(start),'PC':hex(pc),'effective_address':hex(address),'access_bytes':size,'kind':kind,'instruction':i['text']})
  if op in ['b','bx','bl','blx'] or op.startswith('b') and op not in ['bic','bics','bkpt']:
   if op=='b':
    m=re.search(r'0x([0-9a-f]+)',args);successors=[int(m[1],16)] if m else []
   elif op in ['bx','blx']:
    if op=='bx':successors=[]
    else:
     for r in ['r0','r1','r2','r3','r12','lr']:out.pop(r,None)
   elif op=='bl':
    for r in ['r0','r1','r2','r3','r12','lr']:out.pop(r,None)
   else:
    m=re.search(r'0x([0-9a-f]+)',args)
    if m:successors.append(int(m[1],16))
  elif op in ['ldr','ldrb','ldrh','ldrsb','ldrsh','str','strb','strh']:
   m=re.match(r'(\w+),\s*\[(\w+)(?:,\s*([^]]+))?\]',args)
   if m:
    dest,base,offset=m.groups();dest=reg(dest);base=reg(base);offset=0 if offset is None else value(offset,state);bv=((pc+4)&~3) if base=='pc' else state.get(base);address=None if bv is None or offset is None else (bv+offset)&0xffffffff;size=1 if op.endswith('b') else 2 if op.endswith('h') else 4;record(address,size,'read' if op.startswith('ldr') else 'write')
    if op.startswith('ldr'):
     out.pop(dest,None)
     if address is not None and 0x08000000<=address and address+size<=0x08000000+len(blob):out[dest]=int.from_bytes(blob[address-0x08000000:address-0x08000000+size],'little')
    if dest=='pc':successors=[]
  elif op in ['mov','movs','mvn','mvns','add','adds','sub','subs','and','ands','orr','orrs','bic','bics','eor','eors','lsl','lsls','lsr','lsrs','asr','asrs','uxtb','uxth']:
   parts=[reg(x) for x in args.split(',')];dest=parts[0];val=None
   if op in ['mov','movs']:val=value(parts[1],state)
   elif op in ['mvn','mvns']:
    v=value(parts[1],state);val=None if v is None else ~v
   elif op in ['uxtb','uxth']:
    v=value(parts[1],state);val=None if v is None else v&(255 if op=='uxtb' else 65535)
   else:
    left=value(parts[1],state) if len(parts)==3 else state.get(dest);right=value(parts[2],state) if len(parts)==3 else value(parts[1],state)
    if len(parts)==3 and parts[1]=='pc':left=(pc+4)&~3
    if left is not None and right is not None:
     if op.startswith('add'):val=left+right
     elif op.startswith('sub'):val=left-right
     elif op.startswith('and'):val=left&right
     elif op.startswith('orr'):val=left|right
     elif op.startswith('bic'):val=left&~right
     elif op.startswith('eor'):val=left^right
     elif op.startswith('lsl'):val=left<<right if right<32 else 0
     elif op.startswith('lsr'):val=left>>right if right<32 else 0
     elif op.startswith('asr'):val=((left if left<0x80000000 else left-0x100000000)>>right) if right<32 else (-1 if left&0x80000000 else 0)
   out.pop(dest,None)
   if val is not None:out[dest]=val&0xffffffff
   if dest=='pc':successors=[]
  elif op in ['ldmia','stmia','ldm','stm']:
   parts=args.split(',',1);base=reg(parts[0].rstrip('!'));registers=[reg(r) for r in re.findall(r'r\d+|sl|fp|ip|lr|pc',parts[1] if len(parts)>1 else '')];base_value=state.get(base)
   for index,r in enumerate(registers):
    address=None if base_value is None else base_value+4*index;record(address,4,'read' if op.startswith('ldm') else 'write')
    if op.startswith('ldm'):
     out.pop(r,None)
     if address is not None and 0x08000000<=address and address+4<=0x08000000+len(blob):out[r]=int.from_bytes(blob[address-0x08000000:address-0x08000000+4],'little')
   out.pop(base,None)
   if base_value is not None:out[base]=(base_value+4*len(registers))&0xffffffff
   if 'pc' in registers:successors=[]
  elif op in ['svc','bkpt','udf']:successors=[]
  elif op in ['push','pop']:
   if op=='pop':
    for r in re.findall(r'r\d+|lr|pc',args):out.pop(r,None)
    if 'pc' in args:successors=[]
   out.pop('sp',None)
  elif op in ['cmp','cmn','tst','nop','cpsid','cpsie','dsb','isb','dmb']:pass
  else:
   # Unsupported writing instruction: forget its first destination; never infer new constants.
   unknown_ops[op]+=1;first=reg(args.split(',')[0].rstrip('!'))
   if first in out:out.pop(first,None)
   if first=='pc':successors=[]
  for dest in successors:
   if dest not in ins or not lo<=dest<hi:continue
   if dest not in incoming:incoming[dest]=dict(out);work.append(dest)
   else:
    joined={k:v for k,v in incoming[dest].items() if k in out and out[k]==v}
    if joined!=incoming[dest]:incoming[dest]=joined;work.append(dest)
r={'status':'NATIVE_STATIC_RAM_EFFECTIVE_ADDRESS_AUDIT','firmware_sha256':sha(F),'catalogue_sha256':sha(catalogue),'disassembly_sha256':sha(H/'native-disassembly.txt'),'functions':len(functions),'abstract_states':states_seen,'target_count':len(targets),'static_address_join_count':len(hits),'joins':{hex(k):v for k,v in sorted(hits.items())},'targets_without_static_join':[hex(x) for x in sorted(targets-hits.keys())],'unsupported_instruction_counts':dict(unknown_ops),'limits':['Conservative instructionCFG constant propagation; branchconditions unconstrained, not actualruntime path or objectextent proof','Literal values read only from lockedimage; no RAM/factory/peripheral values fabricated','Unknowninstructions and callclobbers drop constants; computedbranch paths mayremainunjoined','No source change or code/data intervalpromotion; independently review joins before formaladdressadmission']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['static_address_join_count'],r['target_count']);print(r['targets_without_static_join'])
