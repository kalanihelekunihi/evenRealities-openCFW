from pathlib import Path
import json,struct,functools
H=Path(__file__).resolve().parent;R=H.parents[3];B=H.parent;raw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:];cat={int(x['entry'],16):x for x in map(json.loads,(R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())};review=json.loads((B/'case-wave055-ram-stack-evidence-review/verification.json').read_text());strings=[(int(x['native_address'],16),int(x['native_address'],16)+x['bytes_including_NUL']) for x in json.loads((B/'case-wave025-ram-callback-provenance/verification.json').read_text())['strings']]
UNKNOWN=None
# Backward register-definition evaluation, separate from wave053 forward states.
# All syntactic CFG predecessors retained; branch flags never invented/pruned.
def analyze(fn,target,reg):
 lo=int(fn['body_start'],16);hi=int(fn['body_end_inclusive'],16)+1;ins={};pc=lo
 while pc+2<=hi:
  if any(a<=pc<b for a,b in strings):pc+=2;continue
  w=struct.unpack_from('<H',raw,pc-0x8000000)[0];n=4 if w>>11 in [29,30,31] else 2
  if pc+n>hi:break
  ins[pc]=(w,n);pc+=n
 pred={p:[] for p in ins}
 for p,(w,n) in ins.items():
  edges=[p+n]
  if w&0xf800==0xe000:
   off=w&2047;off=off-2048 if off&1024 else off;edges=[p+4+off*2]
  elif w&0xf000==0xd000:
   cond=(w>>8)&15
   if cond<14:
    off=w&255;off=off-256 if off&128 else off;edges.append(p+4+off*2)
   else:edges=[]
  elif w&0xff87==0x4700 or w&0xff00==0xbd00 or (w&0xfc00==0x4400 and ((w&7)|((w>>4)&8))==15 and (w>>8)&3 in [0,2]):edges=[]
  for q in edges:
   if q in pred:pred[q].append(p)
 successors={p:[] for p in ins}
 for q,pp in pred.items():
  for p in pp:successors[p].append(q)
 reachable=set();todo=[lo]
 while todo:
  p=todo.pop()
  if p in reachable:continue
  reachable.add(p);todo.extend(successors.get(p,[]))
 assert target in reachable,('No syntactic entry-to-operand path',hex(lo),hex(target))
 active=set();cache={};proof=[]
 def values(pc,r):
  key=(pc,r)
  if key in cache:return cache[key]
  if key in active:return {UNKNOWN}
  active.add(key);out=set()
  for prev in pred.get(pc,[]):out|=after(prev,r)
  if not pred.get(pc):out.add(UNKNOWN)
  active.remove(key)
  if len(out)>32:out={UNKNOWN}
  cache[key]=out;return out
 def op(pc,a,b,fun):
  aa=values(pc,a);bb={b[1]} if b[0]=='imm' else values(pc,b[1]);return {UNKNOWN if x is None or y is None else fun(x,y)&0xffffffff for x in aa for y in bb}
 def after(pc,r):
  w,n=ins[pc];rd=w&7
  if w&0xff87==0x4780:return {UNKNOWN} if r in [0,1,2,3,12,14] else values(pc,r)
  if n==4:
   tail=struct.unpack_from('<H',raw,pc-0x8000000+2)[0]
   if w&0xf800==0xf000 and tail&0xd000==0xd000:return {UNKNOWN} if r in [0,1,2,3,12,14] else values(pc,r)
   # MRS/MSR/barriers: conservatively invalidate destination for MRS.
   if w==0xf3ef and r==(tail>>8)&15:return {UNKNOWN}
   if w&0xfff0==0xf380 or w==0xf3bf:return values(pc,r)
   return {UNKNOWN}
  if w&0xf800==0x4800:
   if r==(w>>8)&7:
    a=((pc+4)&~3)+(w&255)*4;proof.append((pc,a));return {struct.unpack_from('<I',raw,a-0x8000000)[0]}
   return values(pc,r)
  if w&0xf800==0x2000:return {w&255} if r==(w>>8)&7 else values(pc,r)
  if w&0xf800 in [0x3000,0x3800]:
   d=(w>>8)&7
   return op(pc,r,('imm',w&255), (lambda a,b:a+b) if w&0xf800==0x3000 else (lambda a,b:a-b)) if r==d else values(pc,r)
  if w&0xf800==0x1800:
   if r!=rd:return values(pc,r)
   a=(w>>3)&7;b=(w>>6)&7;return op(pc,a,('imm' if w&0x400 else 'reg',b),(lambda a,b:a-b) if w&0x200 else (lambda a,b:a+b))
  if w&0xe000==0 and w&0x1800!=0x1800:
   if r!=rd:return values(pc,r)
   src=(w>>3)&7;sh=(w>>6)&31;kind=(w>>11)&3
   fun=(lambda a,b:a<<b) if kind==0 else ((lambda a,b:a>>(b or 32)) if kind==1 else (lambda a,b:(a if a<0x80000000 else a-0x100000000)>>(b or 32)))
   return op(pc,src,('imm',sh),fun)
  if w&0xfc00==0x4400:
   d=(w&7)|((w>>4)&8);s=(w>>3)&15;kind=(w>>8)&3
   if kind==1:return values(pc,r)
   if r!=d:return values(pc,r)
   if kind==2:return values(pc,s)
   if kind==0:return op(pc,d,('reg',s),lambda a,b:a+b)
   return {UNKNOWN}
  if w&0xfc00==0x4000:
   code=(w>>6)&15;src=(w>>3)&7
   if code in [8,10,11] or r!=rd:return values(pc,r)
   if code==9:return op(pc,src,('imm',0),lambda a,b:-a)
   if code==15:return op(pc,src,('imm',0),lambda a,b:~a)
   funcs={0:lambda a,b:a&b,1:lambda a,b:a^b,2:lambda a,b:a<<(b&255),3:lambda a,b:a>>(b&255),12:lambda a,b:a|b,13:lambda a,b:a*b,14:lambda a,b:a&~b}
   return op(pc,rd,('reg',src),funcs[code]) if code in funcs else {UNKNOWN}
  # Immediate memory operations: only ROM loads can define a constant.
  top=w&0xf800
  if top in [0x6000,0x6800,0x7000,0x7800,0x8000,0x8800]:
   load=top in [0x6800,0x7800,0x8800]
   if not load or r!=rd:return values(pc,r)
   size=4 if top==0x6800 else (1 if top==0x7800 else 2);out=set()
   for base in values(pc,(w>>3)&7):
    a=None if base is None else base+((w>>6)&31)*size
    if a is None or not 0x8000000<=a<=0x8000000+len(raw)-size:out.add(UNKNOWN)
    else:out.add(int.from_bytes(raw[a-0x8000000:a-0x8000000+size],'little'))
   return out
  if w&0xf800==0xa000:return {((pc+4)&~3)+(w&255)*4} if r==(w>>8)&7 else values(pc,r)
  if w&0xf800==0x2800 or w&0xf000==0xd000 or w&0xf800==0xe000 or w&0xff00 in [0xb400,0xb500] or w&0xffe0==0xb660 or w==0x46c0:return values(pc,r)
  if w&0xf800==0x9000:return values(pc,r) # SP-relative store
  if w&0xf800==0x9800:return {UNKNOWN} if r==(w>>8)&7 else values(pc,r)
  if w&0xfe00==0xbc00:return {UNKNOWN} if r<8 and w&(1<<r) else values(pc,r)
  if w&0xff00==0xb000:return values(pc,r)
  # Remaining register-memory loads/sign extension are conservative.
  if w&0xf000==0x5000:return {UNKNOWN} if (w>>9)&7>=3 and r==rd else values(pc,r)
  return {UNKNOWN}
 result=values(target,reg);return result,sorted(set(proof))
# Negative controls guard against constant provenance crossing call clobbers.
saved_raw=raw
controls=[]
for words,target,register,expected,label in [
 ([0x4803,0x4788,0x6801,0x4770,0,0,0,0,0x1234,0x2000],0x8000004,0,{None},'BLX clobbers R0'),
 ([0x4c03,0x4788,0x6821,0x4770,0,0,0,0,0x1234,0x2000],0x8000004,4,{0x20001234},'BLX preserves R4'),
 ([0x4803,0xf000,0xf800,0x6801,0x4770,0,0,0,0x1234,0x2000],0x8000006,0,{None},'BL clobbers R0'),
 ([0x2800,0xd001,0x2001,0xe000,0x2002,0x6801,0x4770],0x800000a,0,{1,2},'Both branch definitions retained')]:
 raw=struct.pack('<'+'H'*len(words),*words);fn={'body_start':'08000000','body_end_inclusive':hex(0x8000000+len(raw)-1)};actual,_=analyze(fn,target,register);assert actual==expected,(label,actual,expected);controls.append(label)
raw=saved_raw
rows=[]
for rec in review['RAM_operand_review']:
 examples=[]
 for hit in rec['examples']:
  pc=int(hit['PC'],16);fn=cat[int(hit['function_entry'],16)];reg=int(hit['decoded_operand']['base_register'][1:]);expected=int(hit['required_base_value'],16)
  values,proof=analyze(fn,pc,reg);ok=values=={expected};examples.append(dict(PC=hit['PC'],expected_base=hex(expected),inferred_values=[None if v is None else hex(v) for v in values],all_syntactic_predecessors_constant=ok,literal_definition_candidates=[dict(PC=hex(p),literal_address=hex(a)) for p,a in proof]))
 rows.append(dict(target=rec['target'],status='CFG_BASE_CONFIRMED' if any(x['all_syntactic_predecessors_constant'] for x in examples) else 'UNRESOLVED_CONSERVATIVE',examples=examples))
confirmed=sum(x['status']=='CFG_BASE_CONFIRMED' for x in rows)
r=dict(status='COMPLETED_CONSERVATIVE_BACKWARD_CFG_REVIEW',targets=len(rows),confirmed=confirmed,negative_controls=controls,unresolved=len(rows)-confirmed,joins=rows,limits=['Backward raw Thumb evaluator retains all syntactic CFG predecessors; entry-to-operand syntactic path asserted, branch feasibility/flags unconstrained','Unsupported writes/loops become unknown; unresolved is not a firmware defect','Producer alternate-method review, not independent reviewer admission','Native function code/data boundaries remain inherited except authenticated strings filtered; object extent/lifetime not proved'])
(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],confirmed,'/',len(rows))
