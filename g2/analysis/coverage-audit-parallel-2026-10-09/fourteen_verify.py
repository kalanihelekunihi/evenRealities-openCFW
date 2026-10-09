from pathlib import Path
import json,struct,hashlib
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();src=(O/'finite_verify.py').read_text();exec(src[src.index('def elf('):src.index('checks=[]')]);fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();stock=lambda a,n:fw[32+a-0x3300:32+a-0x3300+n]
def bl(data,a):
 hi,lo=struct.unpack('<HH',data);S=hi>>10&1;j1=lo>>13&1;j2=lo>>11&1;imm=(S<<24)|((1^(j1^S))<<23)|((1^(j2^S))<<22)|((hi&1023)<<12)|((lo&2047)<<1);return a+4+imm-(1<<25 if S else 0)
def relocs(b,ss,ns,syms,idx):
 out=[]
 for t in ss:
  if t[1]==9 and t[7]==idx:
   for off in range(t[4],t[4]+t[5],8):
    pos,info=struct.unpack_from('<II',b,off);sym=syms[info>>8];out.append((pos,info&255,sym))
 return out
names=['sysint14-linkage','syslib14-delay-linkage','systick14-linkage','clkhf14-attribution'];reports=[];newranges=[]
for name in names:
 P=R/'g2/analysis'/('touch-'+name+'-2026-10-09');r=json.loads((P/'results.json').read_text());argv=r['argv'];mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'};obj=mounts['/input']/'public.o';ib,iss,ins,isy=elf(obj);eb,ess,ens,esy=elf(P/'outputs/linked.elf');q={'task':name,'input_hash_verified':sha(obj.read_bytes())==r['input_object_sha256'],'elf_hash_verified':sha(eb)==r['linked_elf_sha256'],'script_hash_verified':sha((P/'link.ld').read_bytes())==r['link_script_sha256'],'script_copy_identical':(P/'link.ld').read_bytes()==(P/'outputs/link.ld').read_bytes(),'sections':[],'calls':[],'literal_references':[]}
 script=(P/'link.ld').read_text()
 for f in r['sections']:
  idx=ens.index('.'+f['section']);x=ess[idx];a=int(f['address'],16);data=eb[x[4]:x[4]+x[5]];z={'section':f['section'],'exact':data==stock(a,len(data)),'hash_verified':sha(data)==f['sha256']==f['stock_sha256'],'address_length_verified':a==x[3] and len(data)==f['expected_bytes']==f['linked_bytes']};maps=sorted((v-a,n) for n,v,_,k in esy if k==idx and n.startswith(('$t','$d')));z['mapping_symbols']=maps
  pattern='*(';start=script.index('.'+f['section']+' ');part=script[start:script.index('}',start)];inp=part.split('(')[1].split(')')[0] if '*(' in part else None
  if inp and inp in ins:
   ii=ins.index(inp);ix=iss[ii];raw=ib[ix[4]:ix[4]+ix[5]];rs=relocs(ib,iss,ins,isy,ii);allowed={j for off,typ,sym in rs for j in range(off,off+4)};z['unchanged_except_relocations']=len(raw)==len(data) and all(raw[j]==data[j] for j in range(len(raw)) if j not in allowed);bindings=[]
   for off,typ,sym in rs:
    sn,sv,size,si=sym;target=None
    if sn:target=next((v for n,v,_,_ in esy if n==sn),None)
    else:
     sec=ins[si];target=next((t[3] for ni,t in zip(ens,ess) if (sec=='.bss' and ni in ('.callbacks','.globals'))),None)
    if typ==2:actual=struct.unpack_from('<I',data,off)[0];addend=struct.unpack_from('<I',raw,off)[0];ok=target is not None and actual==(target+addend)&0xffffffff
    elif typ==10:actual=bl(data[off:off+4],a+off);addend=None;ok=target is not None and actual==target&~1
    else:actual=None;addend=None;ok=False
    bindings.append({'offset':off,'type':typ,'symbol':sn or ins[si],'symbol_address':target,'addend':addend,'bound_value':actual,'verified':ok})
   z['relocation_bindings']=bindings
  q['sections'].append(z)
  if not f.get('reused_dependency') and not f.get('dependency_outside_selected_denominator'):newranges.append((a,a+len(data),name,f.get('historical_attribution')))
 for c in r.get('original_calls',[]):
  a=int(c.get('instruction',c.get('address')),16);q['calls'].append({'instruction':hex(a),'verified':bl(stock(a,4),a)==int(c['target'],16)})
 refs=r.get('original_literal_references',[])+([r['original_external_clock_literal']] if 'original_external_clock_literal'in r else [])
 for c in refs:
  a=int(c['instruction'],16);h=struct.unpack('<H',stock(a,2))[0];dest=((a+4)&~3)+(h&255)*4;want=int(c.get('literal_address',c.get('literal')),16);val=int(c.get('literal_value',c.get('value')),16);q['literal_references'].append({'instruction':hex(a),'verified':h&0xf800==0x4800 and dest==want and struct.unpack('<I',stock(dest,4))[0]==val})
 reports.append(q)
# Assembly extent and exact source-label offsets.
P=R/'g2/analysis/touch-syslib14-assembly-2026-10-09';r=json.loads((P/'results.json').read_text());b,ss,ns,sy=elf(P/'outputs/public.o');x=ss[ns.index('.text')];data=b[x[4]:x[4]+x[5]];aq={'source_hash_verified':sha((R/r['source_path']).read_bytes())==r['source_sha256'],'object_hash_verified':sha(b)==r['object_sha256'],'text_bytes':len(data),'relocation_free':not relocs(b,ss,ns,sy,ns.index('.text')),'functions':[]}
for f in r['functions']:
 a=int(f['runtime_address'],16);off=f['object_offset'];n=f['compared_bytes'];v=data[off:off+n];aq['functions'].append({'function':f['function'],'exact':v==stock(a,n),'hash_verified':sha(v)==f['sha256'],'label_offset_verified':next(v for sn,v,_,_ in sy if sn==f['function'])&~1==off});newranges.append((a,a+n,'assembly',f['function']))
# Inline emission comparisons, including rejected divider alternatives.
P=R/'g2/analysis/touch-pdl14-inline-emission-2026-10-09';r=json.loads((P/'results.json').read_text());b,ss,ns,sy=elf(P/'outputs/public.o');iq={'object_hash_verified':sha(b)==r['object_sha256'],'include_hash_verified':sha((P/'include.c').read_bytes())==r['include_source_sha256'],'header_hashes_verified':all(sha((R/'g2/analysis/touch-compiler14-successor-2026-10-09/tools/pdl-input/drivers/include'/n).read_bytes())==v for n,v in r['header_sha256'].items()),'device_retained':'-DCY8C4046FNI_T412'in r['argv'],'functions':[]}
for f in r['functions']:
 idx=ns.index('.text.'+f['function']);x=ss[idx];v=b[x[4]:x[4]+x[5]];a=int(f['runtime_address'],16);t=stock(a,len(v));iq['functions'].append({'function':f['function'],'exact':v==t,'hashes_verified':sha(v)==f['sha256'] and sha(t)==f['stock_sha256'],'mismatch_positions_verified':[i for i in range(len(v)) if v[i]!=t[i]]==f['mismatch_positions'],'relocation_free':not relocs(b,ss,ns,sy,idx)})
 if f['exact_full_section']:newranges.append((a,a+len(v),'inline',f['function']))
newranges.sort();out={'linked_reviews':reports,'assembly_review':aq,'inline_review':iq,'new_ranges':newranges,'new_extents':len(newranges),'new_bytes':sum(e-a for a,e,_,_ in newranges),'new_nonoverlapping':all(x[1]<=y[0] for x,y in zip(newranges,newranges[1:])),'aggregate_bytes':2368+sum(e-a for a,e,_,_ in newranges),'aggregate_functions':25+len(newranges),'denominator':54};(O/'FOURTEEN-EXTENTS-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print('counts',out['new_extents'],out['new_bytes'],out['new_nonoverlapping']);print('failed booleans')
def scan(v,path=''):
 if isinstance(v,dict):
  for k,x in v.items():
   if x is False:print(path+'.'+k)
   else:scan(x,path+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):scan(x,path+f'[{i}]')
scan(out)
