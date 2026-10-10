"""Private provider identification: only declared relocations and LRW pool layout vary."""
from pathlib import Path
import struct, subprocess, hashlib, json, re, collections
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PRE=OUT.parent/'shortcut-provider-archive-20261009-agent1'
TOOLS=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
ARCHIVE=ROOT/'third-party/upstream/nationalchip-lvp-kws/lib/libdriver_release_v1.0.6.a'
IP=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
 p=subprocess.run([str(a) for a in args],cwd=OUT,capture_output=True,text=True);assert p.returncode==0,p.stderr
 return p.stdout
def elf(path):
 b=path.read_bytes();assert b[:6]==b'\x7fELF\x01\x01'
 off=struct.unpack_from('<I',b,32)[0];sz,n,strings=struct.unpack_from('<HHH',b,46)
 ss=[struct.unpack_from('<10I',b,off+i*sz) for i in range(n)]
 names=b[ss[strings][4]:ss[strings][4]+ss[strings][5]]
 def string(data,i):return data[i:data.index(0,i)].decode(errors='replace')
 ns=[string(names,s[0]) for s in ss];syms=[];rs=collections.defaultdict(list)
 for s in ss:
  if s[1]!=2:continue
  st=ss[s[6]];strs=b[st[4]:st[4]+st[5]]
  for j in range(s[5]//s[9]):
   name,val,size,info,other,ix=struct.unpack_from('<IIIBBH',b,s[4]+j*s[9])
   syms.append(dict(name=string(strs,name) or (ns[ix] if ix<len(ns) else ''),offset=val,size=size,info=info,section=ix))
 for s in ss:
  if s[1] not in (4,9):continue
  for j in range(s[5]//s[9]):
   at,info=struct.unpack_from('<II',b,s[4]+j*s[9]);sym=syms[info>>8]
   addend=struct.unpack_from('<i',b,s[4]+j*s[9]+8)[0] if s[1]==4 else struct.unpack_from('<I',b,ss[s[7]][4]+at)[0]
   rs[s[7]].append(dict(offset=at,type=info&255,symbol=sym['name'],addend=addend))
 return b,ss,ns,syms,rs
def listing(text):
 sections=collections.defaultdict(dict);sec='binary'
 for line in text.splitlines():
  if line.startswith('Disassembly of section '):sec=line.split('section ')[1].rstrip(':')
  m=re.match(r'^\s*([0-9a-f]+):\s+([0-9a-f]{4,8})\s+([^\s]+)\s*(.*)$',line)
  if not m:continue
  a,h,mn,args=m.groups();args,_,comment=args.partition('//')
  sections[sec][int(a,16)]=dict(size=len(h)//2,mn=mn,args=args.strip(),comment=comment.strip())
 return sections
images={}
for name,base in [('xip',0x10203004),('sram',0x10023400)]:
 p=IP/('binh_a_stage2_'+name+'.bin');data=p.read_bytes()
 native=(PRE/(name+'-native.txt')).read_text()
 images[name]=dict(data=data,base=base,ins=listing(native)['.data'],sha256=sha(p))
assert images['xip']['sha256']=='49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584'
# Learn only section-linked ADDR32 bases retained by the previous receipt.
bases=collections.defaultdict(set)
for row in json.loads((PRE/'archive-inventory.json').read_text())['sections']:
 _,ss,ns,_,rs=elf(PRE/row['object']);relmap={r['offset']:r for r in rs[ns.index(row['section'])]}
 for c in row['stock_candidates']:
  for f in c['addr32_facts']:
   r=relmap[f['offset']];bases[row['object']+':'+r['symbol']].add((f['linked_word']-r['addend'])&0xffffffff)
members=run([TOOLS/'csky-elfabiv2-ar','t',ARCHIVE]).splitlines()
run([TOOLS/'csky-elfabiv2-ar','x',ARCHIVE])
funcs=[];unsupported=[]
for member in members:
 b,ss,ns,syms,rs=elf(OUT/member)
 native=run([TOOLS/'csky-elfabiv2-objdump','-dr',OUT/member]);(OUT/(member+'.native.txt')).write_text(native)
 ins=listing(native)
 for sym in syms:
  ix=sym['section'];start=sym['offset'];size=sym['size']
  if sym['info']&15!=2 or not size or ix>=len(ss) or not ss[ix][2]&4:continue
  s=ss[ix];raw=b[s[4]+start:s[4]+start+size];rel=[r for r in rs[ix] if start<=r['offset']<start+size]
  if any(r['type'] not in (1,19) for r in rel):unsupported.append([member,sym['name'],rel]);continue
  mask=set();lrws=[]
  for r in rel:mask.update(range(r['offset']-start,min(size,r['offset']-start+4)))
  for at,v in ins[ns[ix]].items():
   if start<=at<start+size and v['mn']=='lrw':
    m=re.match(r'([0-9a-f]+)',v['comment']);assert m,(member,at,v)
    pool=int(m[1],16);assert pool+4<=s[5]
    value=struct.unpack_from('<I',b,s[4]+pool)[0]
    pr=[r for r in rs[ix] if r['offset']==pool]
    lrws.append(dict(offset=at-start,size=v['size'],register=v['args'].split(',')[0],pool_offset=pool,unlinked_word=value,relocation=pr[0] if pr else None))
    mask.update(range(at-start,at-start+v['size']))
  spans=[];a=None
  for j in range(size+1):
   if j<size and j not in mask:
    if a is None:a=j
   elif a is not None:spans.append((a,j));a=None
  anchor=max(spans,key=lambda x:x[1]-x[0],default=(0,0));cs=[]
  # Short register helpers are allowed; all candidates remain ambiguous until graph checks.
  if anchor[1]-anchor[0]>=2:
   for name,im in images.items():
    data=im['data'];needle=raw[anchor[0]:anchor[1]];p=data.find(needle)
    while p!=-1:
     off=p-anchor[0];p=data.find(needle,p+1)
     if off<0 or off%2 or off+size>len(data) or not all(data[off+a:off+z]==raw[a:z] for a,z in spans):continue
     addr=im['base']+off;facts=[];bad=False
     for lr in lrws:
      v=im['ins'].get(addr+lr['offset']);m=re.match(r'0x([0-9a-f]+)',v['comment']) if v else None
      if not v or v['mn']!='lrw' or v['size']!=lr['size'] or v['args'].split(',')[0]!=lr['register'] or not m:bad=True;break
      pa=int(m[1],16);po=pa-im['base']
      if not 0<=po<=len(data)-4:bad=True;break
      value=struct.unpack_from('<I',data,po)[0];r=lr['relocation'];expected=sorted(bases.get(member+':'+r['symbol'],set())) if r else []
      base=(value-r['addend'])&0xffffffff if r else None
      if (not r and value!=lr['unlinked_word']) or (r and expected and base not in expected):bad=True;break
      facts.append(dict(**lr,linked_pool=pa,linked_word=value,inferred_base=base if r else None,status='base_seed_confirmed' if expected else 'unresolved_base' if r else 'exact_constant'))
     if bad:continue
     cs.append(dict(image=name,address=addr,offset=off,exact=data[off:off+size]==raw,literal_checks=facts))
  funcs.append(dict(object=member,symbol=sym['name'],section=ns[ix],section_offset=start,size=size,stable_anchor_size=anchor[1]-anchor[0],relocations=[dict(r,offset=r['offset']-start) for r in rel],lrw_sites=lrws,candidates=cs))
# Iterative graph pruning: a target with no provider candidates stays open; known
# provider candidates constrain calls, but no caller may validate its own target.
for iteration in range(20):
 known=collections.defaultdict(set)
 for f in funcs:
  for c in f['candidates']:
   if not c.get('rejected'):known[f['symbol']].add(c['address'])
 changed=False
 for f in funcs:
  for c in f['candidates']:
   if c.get('rejected'):continue
   checks=[];im=images[c['image']]
   for r in f['relocations']:
    if r['type']!=19:continue
    v=im['ins'].get(c['address']+r['offset']);m=re.match(r'0x([0-9a-f]+)',v['args']) if v and v['mn']=='bsr' else None
    target=int(m[1],16) if m else None
    if r['symbol'].startswith('.'):
     expect=sorted({p['address'] for x in funcs if x['object']==f['object'] and x['section']==r['symbol'] and x['section_offset']==r['addend'] for p in x['candidates'] if not p.get('rejected')})
    else:expect=sorted((v+r['addend'])&0xffffffff for v in known[r['symbol']])
    status='contradiction' if target is None or expect and target not in expect else 'target_consistent' if expect else 'unresolved_target'
    checks.append(dict(offset=r['offset'],symbol=r['symbol'],target=target,expected=expect,status=status))
   c['branch_checks']=checks
   if any(x['status']=='contradiction' for x in checks):c['rejected']=True;changed=True
 if not changed:break
previous=json.loads((PRE/'function-inventory.json').read_text())['functions'];closure=[]
for f in previous:
 for c in f['candidates']:
  if c['branch_relocation_contradiction']:continue
  for r in c['branch_relocation_checks']:
   if r['status']!='unresolved_target':continue
   options=[dict(object=x['object'],symbol=x['symbol'],address=p['address'],size=x['size'],exact=p['exact'],literal_checks=p['literal_checks'],branch_checks=p.get('branch_checks',[])) for x in funcs if x['symbol']==r['symbol'] for p in x['candidates'] if not p.get('rejected') and p['address']==r['linked_target']]
   closure.append(dict(caller=f['symbol'],caller_address=c['runtime_conditional'],relocation_offset=r['relocation_offset'],symbol=r['symbol'],target=r['linked_target'],providers=options,status='provider_correlated' if options else 'unresolved'))
boundaries=[];callbacks=[]
for f in funcs:
 for c in f['candidates']:
  if not c.get('rejected'):
   boundaries.append(dict(symbol=f['symbol'],object=f['object'],section=f['section'],start=c['address'],end=c['address']+f['size'],size=f['size'],stable_anchor_size=f['stable_anchor_size'],exact=c['exact'],unresolved_literals=sum(x['status']=='unresolved_base' for x in c['literal_checks'])))
   for lit in c['literal_checks']:
    rel=lit['relocation']
    if not rel or not rel['symbol'].startswith('.'):continue
    targets=[dict(symbol=t['symbol'],address=p['address'],size=t['size']) for t in funcs if t['object']==f['object'] and t['section']==rel['symbol'] and t['section_offset']==rel['addend'] for p in t['candidates'] if not p.get('rejected') and p['address']==lit['linked_word']]
    if targets:callbacks.append(dict(owner=f['symbol'],owner_address=c['address'],lrw_offset=lit['offset'],linked_pointer=lit['linked_word'],providers=targets))
assert not any(c['address']==0x1020566c and not c.get('rejected') for f in funcs if f['symbol']=='npu_dis_interrupt' for c in f['candidates'])
assert any(c['address']==0x10205e28 and not c.get('rejected') for f in funcs if f['symbol']=='gx_snpu_get_state' for c in f['candidates'])
result=dict(archive_sha256=sha(ARCHIVE),images={n:{k:v for k,v in x.items() if k in ('base','sha256')} for n,x in images.items()},members=members,unsupported=unsupported,learned_bases={k:sorted(v) for k,v in bases.items()},functions=funcs,prior_unresolved=closure,boundaries=boundaries,callback_pointers=callbacks,pruning_iterations=iteration+1)
(OUT/'closure.json').write_text(json.dumps(result,indent=2)+'\n')
receipt=dict(archive_members=len(members),function_count=len(funcs),nonrejected_symbols=sum(any(not c.get('rejected') for c in f['candidates']) for f in funcs),candidate_count=len(boundaries),prior_unresolved_sites=len(closure),provider_correlated_sites=sum(bool(x['providers']) for x in closure),remaining_sites=sum(not x['providers'] for x in closure),unsupported_relocations=unsupported,output_sha256=sha(OUT/'closure.json'))
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
