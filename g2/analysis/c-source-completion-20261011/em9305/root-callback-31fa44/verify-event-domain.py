from pathlib import Path
import re,json,collections,hashlib
P=Path(__file__).resolve().parent;n={}
for l in (P/'native.txt').read_text().splitlines():
 v=l.split('\t')
 if len(v)>=3 and re.fullmatch(r'\s*[0-9a-f]+:',v[0]):n[int(v[0].strip()[:-1],16)]=(v[2].strip(),v[3].strip() if len(v)>3 else '',l)
a=sorted(n);nxt={x:(a[i+1] if i+1<len(a) else None) for i,x in enumerate(a)}
def apply(addr,value):
 m,o,_=n[addr]
 if m.startswith('mov') and o.startswith('r1,'):
  rhs=o.split(',')[1];return int(rhs,0) if re.fullmatch(r'(?:0x[0-9a-f]+|[0-9]+)',rhs) else None
 # This native body has no other R1-producing arithmetic/load operations.
 if o.startswith('r1,') and m.startswith(('ld','add','sub','and','or','ext','sex','mpy')):return None
 return value
seen=set();q=collections.deque([(a[0],None)]);calls={}
while q:
 addr,value=q.popleft()
 if addr is None or (addr,value) in seen:continue
 seen.add((addr,value));m,o,l=n[addr];v=apply(addr,value);target=re.search(r';0x([0-9a-f]+)',l);dest=int(target[1],16) if target else None;after=nxt[addr]
 if '.d' in m:
  assert after is not None;v=apply(after,v);after=nxt[after]
 if m.startswith('leave'):continue
 if m in ('bl','bl.d'):
  if dest==0x31fa10:calls.setdefault(hex(addr),set()).add(v)
  q.append((after,None));continue
 if m=='bih':
  for slot in range(0x31fad6,0x31faf2,2):q.append((slot,v))
 elif dest is not None and m.startswith('b'):
  q.append((dest,v))
  if m not in ('b','b.d','b_s'):q.append((after,v))
 else:q.append((after,v))
assert set(calls)=={'0x31fb4a','0x31fb6e'},calls
assert all(None not in vals and vals<=set(range(7)) for vals in calls.values()),calls
r={'status':'PASS_CONSERVATIVE_DIRECT_CALL_EVENT_DOMAIN','call_values':{k:sorted(v) for k,v in calls.items()},'analysis':'Both conditional outcomes traversed; calls clobber R1; delay writes executed before successors; all14 BIH slots explored.','visited_abstract_states':len(seen),'native_disassembly_sha256':hashlib.sha256((P/'native.txt').read_bytes()).hexdigest(),'limits':['Proves event<7 for these two call sites under native control flow.','State<8, other/indirectcallers and callback mutations remain open.']};(P/'event-domain-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
