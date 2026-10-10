from pathlib import Path
import struct, subprocess, hashlib, json, re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
TOOLS=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
UP=ROOT/'third-party/upstream/nationalchip-lvp-kws'
IMAGE=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin'
stock=IMAGE.read_bytes()
assert hashlib.sha256(stock).hexdigest()=='49c9aed0126493220a3e48827c267d5e94f64d51d9ede0ccc3e84b8946744584'
def run(args):
 p=subprocess.run([str(x) for x in args],cwd=OUT,capture_output=True,text=True)
 assert p.returncode==0,p.stderr
 return p.stdout
def elf(path):
 b=path.read_bytes(); assert b[:6]==b'\x7fELF\x01\x01'
 off=struct.unpack_from('<I',b,32)[0]; size,n,strings=struct.unpack_from('<HHH',b,46)
 sections=[struct.unpack_from('<10I',b,off+i*size) for i in range(n)]
 names=b[sections[strings][4]:sections[strings][4]+sections[strings][5]]
 def cstr(data,i):return data[i:data.index(0,i)].decode(errors='replace')
 sn=[cstr(names,s[0]) for s in sections]; symbols=[]
 for i,s in enumerate(sections):
  if s[1]!=2:continue
  st=sections[s[6]]; strs=b[st[4]:st[4]+st[5]]
  for j in range(s[5]//s[9]):
   name,val,sz,info,other,idx=struct.unpack_from('<IIIBBH',b,s[4]+j*s[9])
   symbols.append({'name':cstr(strs,name) or (sn[idx] if idx<len(sn) else ''),'offset':val,'size':sz,'info':info,'section':idx})
 rels={}
 for s in sections:
  if s[1] not in (4,9):continue
  for j in range(s[5]//s[9]):
   pos,info=struct.unpack_from('<II',b,s[4]+j*s[9]); sym=symbols[info>>8]
   rels.setdefault(s[7],[]).append({'offset':pos,'type_number':info&255,'symbol':sym['name'],'symbol_section':sym['section'],'symbol_value':sym['offset']})
 return b,sections,sn,symbols,rels
objects=['audio_in.o','audio_out.o','i2s.o','snpu.o','snpu_hw.o','snpu_mcu_ops.o','snpu_regs.o','pmu_ctrl.o','pmu_osc.o','clock.o','device.o']
archive=UP/'lib/libdriver_release_v1.0.6.a'
run([TOOLS/'csky-elfabiv2-ar','x',archive,*objects])
rows=[]; symbolrows=[]
for obj in objects:
 path=OUT/obj;b,sections,names,syms,rels=elf(path)
 (OUT/(obj+'.objdump.txt')).write_text(run([TOOLS/'csky-elfabiv2-objdump','-dr',path]))
 symbolrows.extend([dict(s,object=obj,section_name=names[s['section']] if s['section']<len(names) else 'special') for s in syms])
 for ix,s in enumerate(sections):
  if not(s[2]&4) or s[5]==0:continue
  data=b[s[4]:s[4]+s[5]]; rr=rels.get(ix,[])
  # Only the two verified 32-bit relocation formats may mask bytes. Others remain visible.
  mask=set(); unknown=[]
  for rel in rr:
   if rel['type_number'] in (1,19):mask.update(range(rel['offset'],rel['offset']+4))
   else:unknown.append(rel)
  spans=[];start=None
  for j in range(len(data)+1):
   if j<len(data) and j not in mask:
    if start is None:start=j
   elif start is not None:spans.append((start,j));start=None
  anchor=max(spans,key=lambda p:p[1]-p[0],default=(0,0)); candidates=[]
  if anchor[1]-anchor[0]>=8:
   needle=data[anchor[0]:anchor[1]]; pos=stock.find(needle)
   while pos!=-1:
    at=pos-anchor[0]
    if at>=0 and at+len(data)<=len(stock) and all(stock[at+a:at+z]==data[a:z] for a,z in spans):candidates.append(at)
    pos=stock.find(needle,pos+1)
  rows.append({'object':obj,'section':names[ix],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'symbols':[x for x in syms if x['section']==ix and x['name']],'relocations':rr,'unsupported_relocations':unknown,'comparison_masked_bytes':len(mask),'longest_anchor_bytes':anchor[1]-anchor[0],'stock_candidates':[{'offset':x,'runtime_conditional':0x10203004+x,'exact':stock[x:x+len(data)]==data} for x in candidates]})
functionrows=[]
sram=IMAGE.with_name('binh_a_stage2_sram.bin').read_bytes()
for obj in objects:
 b,sections,names,syms,rels=elf(OUT/obj)
 for sym in syms:
  ix=sym['section']
  if sym['info']&15!=2 or ix>=len(sections) or not sym['size']:continue
  sec=sections[ix];start=sym['offset'];size=sym['size'];data=b[sec[4]+start:sec[4]+start+size]
  rr=[dict(x,offset=x['offset']-start) for x in rels.get(ix,[]) if start<=x['offset']<start+size];mask=set()
  for rel in rr:
   assert rel['type_number'] in (1,19)
   mask.update(range(rel['offset'],min(size,rel['offset']+4)))
  spans=[];a=None
  for j in range(size+1):
   if j<size and j not in mask:
    if a is None:a=j
   elif a is not None:spans.append((a,j));a=None
  anchor=max(spans,key=lambda p:p[1]-p[0],default=(0,0)); candidates=[]
  if anchor[1]-anchor[0]>=8:
   for iname,image,base in [('xip',stock,0x10203004),('sram',sram,0x10023400)]:
    needle=data[anchor[0]:anchor[1]];p=image.find(needle)
    while p!=-1:
     at=p-anchor[0]
     if at>=0 and at+size<=len(image) and all(image[at+a:at+z]==data[a:z] for a,z in spans):candidates.append({'image':iname,'offset':at,'runtime_conditional':base+at,'exact':image[at:at+size]==data})
     p=image.find(needle,p+1)
  functionrows.append({'object':obj,'symbol':sym['name'],'section':names[ix],'section_offset':start,'symbol_size':size,'sha256':hashlib.sha256(data).hexdigest(),'relocations':rr,'comparison_masked_bytes':len(mask),'candidates':candidates})
targetmap={}
for row in functionrows:
 targetmap.setdefault(row['symbol'],set()).update(x['runtime_conditional'] for x in row['candidates'])
calls={}
for iname,image,base in [('xip',IMAGE,0x10203004),('sram',IMAGE.with_name('binh_a_stage2_sram.bin'),0x10023400)]:
 listing=run([TOOLS/'csky-elfabiv2-objdump','-D','-z','-b','binary','-m','csky','--adjust-vma='+hex(base),image])
 (OUT/(iname+'-native.txt')).write_text(listing)
 for addr,dest in re.findall(r'^([0-9a-f]+):.*?\bbsr\s+0x([0-9a-f]+)',listing,re.M):calls[int(addr,16)]=int(dest,16)
for row in functionrows:
 for candidate in row['candidates']:
  checks=[]
  for rel in row['relocations']:
   if rel['type_number']!=19:continue
   at=candidate['runtime_conditional']+rel['offset'];actual=calls.get(at);expected=sorted(targetmap.get(rel['symbol'],set()))
   checks.append({'relocation_offset':rel['offset'],'symbol':rel['symbol'],'linked_target':actual,'known_symbol_candidates':expected,'status':'contradiction' if expected and actual not in expected else 'confirmed_target' if expected else 'unresolved_target'})
  candidate['branch_relocation_checks']=checks
  candidate['branch_relocation_contradiction']=any(x['status']=='contradiction' for x in checks)
for row in rows:
 b,sections,names,syms,rels=elf(OUT/row['object']);ix=names.index(row['section']);sec=sections[ix]
 raw=b[sec[4]:sec[4]+sec[5]]
 for candidate in row['stock_candidates']:
  facts=[]
  for rel in row['relocations']:
   if rel['type_number']!=1:continue
   off=rel['offset'];addend=struct.unpack_from('<I',raw,off)[0];value=struct.unpack_from('<I',stock,candidate['offset']+off)[0]
   facts.append({'offset':off,'symbol':rel['symbol'],'unlinked_word':addend,'linked_word':value,'inferred_symbol_base_mod32':(value-addend)&0xffffffff})
  candidate['addr32_facts']=facts
(OUT/'function-inventory.json').write_text(json.dumps({'sram_sha256':hashlib.sha256(sram).hexdigest(),'functions':functionrows},indent=2)+'\n')
(OUT/'archive-inventory.json').write_text(json.dumps({'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(stock).hexdigest(),'sections':rows,'symbols':symbolrows},indent=2)+'\n')
print(json.dumps({'sections':len(rows),'matched_sections':sum(bool(x['stock_candidates']) for x in rows),'unsupported_types':sorted({y['type_number'] for x in rows for y in x['unsupported_relocations']})}))
