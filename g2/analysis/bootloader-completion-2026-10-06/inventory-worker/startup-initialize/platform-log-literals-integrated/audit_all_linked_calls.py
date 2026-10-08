from pathlib import Path
import json,hashlib,collections
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
R=Path.cwd();P=R/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize';N=P/'platform-log-literals-integrated';O=N/'all-linked-direct-calls';O.mkdir(exist_ok=True);c=json.loads((N/'current-candidate.json').read_text());B=R/c['directory'];H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert H(B/'candidate.elf')==c['sha256'];m=json.loads((B/'input-hashes.json').read_text())
with (B/'candidate.elf').open('rb') as f:
 e=ELFFile(f);sy={s.name:dict(address=int(s['st_value'])&~1,size=int(s['st_size']),type=s['st_info']['type'],section=s['st_shndx']) for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(int(s['p_vaddr']),s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
objects=collections.defaultdict(list)
for r in m['inputs']:
 p=B/r['path'];assert H(p)==r['sha256']
 with p.open('rb') as f:
  e=ELFFile(f);tab=e.get_section_by_name('.symtab')
  if tab:
   for s in tab.iter_symbols():
    if s['st_info']['type']=='STT_FUNC' and s['st_shndx']!='SHN_UNDEF':objects[s.name].append(dict(path=str(p),sha256=r['sha256'],origin=r['original']))
func={};aliases=collections.defaultdict(list)
for name,s in sy.items():
 aliases[s['address']].append(name)
 if s['type']=='STT_FUNC' and s['size']>0:func.setdefault(s['address'],dict(**s,names=[]))['names'].append(name)
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=False;edges={};indirect={}
for address,row in func.items():
 data=next((b[address-a:address-a+row['size']] for a,b in segments if a<=address and address+row['size']<=a+len(b)),None)
 if data is None:continue
 calls=[];sites=[]
 for ins in md.disasm(data,address):
  if ins.mnemonic in ['bl','blx','b','b.w']:
   if ins.op_str.startswith('#'):
    target=int(ins.op_str[1:],0)&~1
    if ins.mnemonic.startswith('bl') or not address<=target<address+row['size']:calls.append(dict(site=ins.address,target=target,kind=ins.mnemonic))
   elif ins.mnemonic.startswith('bl'):sites.append(dict(site=ins.address,operand=ins.op_str,kind=ins.mnemonic))
  elif ins.mnemonic=='bx' and ins.op_str!='lr':sites.append(dict(site=ins.address,operand=ins.op_str,kind='indirect_tail'))
 edges[address]=calls;indirect[address]=sites
roots=sorted(name for name,row in sy.items() if row['type']=='STT_FUNC' and row['size']>0);seen=set();todo=[sy[name]['address'] for name in roots];unresolved=[]
while todo:
 a=todo.pop()
 if a in seen:continue
 seen.add(a)
 if a not in func:continue
 for call in edges.get(a,[]):
  target=call['target']
  if target in func:todo.append(target)
  else:unresolved.append(dict(caller_address=a,caller_names=func[a]['names'],**call,aliases=aliases.get(target,[]),category='external_resident_ROM' if target in [0x40,0x48,0x200ff20] else 'synthetic_test_call' if 0x8002000<=target<0x8003000 else 'unbound_original_executable_reference' if 0x410000<=target<0x435000 else 'unattributed_call'))
rows=[]
for a in sorted(seen):
 if a not in func:continue
 row=func[a];rows.append(dict(linked_address=a,linked_bytes=row['size'],names=row['names'],object_provenance=[o for name in row['names'] for o in objects.get(name,[])],direct_calls=edges.get(a,[]),indirect_sites=indirect.get(a,[]),source_status='linked function; original mapping/source attribution separate'))
(O/'direct-call-closure.json').write_text(json.dumps(dict(candidate_sha256=c['sha256'],roots=roots,linked_functions=rows,unresolved_calls=unresolved,limits=['Static direct calls/tails only; indirect sites explicit, runtime data/callback edges require binding/trace evidence.','STT_FUNC and object presence do not prove C origin, exact-match upstream or behavioral completeness.','No original body bytes admitted by this graph.']),indent=2))
(O/'summary.json').write_text(json.dumps(dict(candidate_sha256=c['sha256'],root_symbols=len(roots),direct_reachable_linked_functions=len(rows),indirect_sites=sum(len(r['indirect_sites']) for r in rows),unresolved=unresolved),indent=2));print('functions',len(rows),'indirect',sum(len(r['indirect_sites']) for r in rows));print(json.dumps(unresolved,indent=2))
