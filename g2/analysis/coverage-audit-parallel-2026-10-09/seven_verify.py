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
names=['sysclk14-frequency-linkage','syspm14-linkage','i2c14-slave-linkage'];reports=[];newranges=[]
for name in names:
 P=R/'g2/analysis'/('touch-'+name+'-2026-10-09');r=json.loads((P/'results.json').read_text());argv=r['argv'];mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'};obj=mounts['/input']/'public.o';ib,iss,ins,isy=elf(obj);eb,ess,ens,esy=elf(P/'outputs/linked.elf');q={'task':name,'input_hash_verified':sha(obj.read_bytes())==r['input_object_sha256'],'elf_hash_verified':sha(eb)==r['linked_elf_sha256'],'script_hash_verified':sha((P/'link.ld').read_bytes())==r['link_script_sha256'],'script_copy_identical':(P/'link.ld').read_bytes()==(P/'outputs/link.ld').read_bytes(),'sections':[],'calls':[],'literal_references':[]}
 script=(P/'link.ld').read_text()
 for f in r['sections']:
  idx=ens.index('.'+f['section']);x=ess[idx];a=int(f['address'],16);data=eb[x[4]:x[4]+x[5]];z={'section':f['section'],'exact':data==stock(a,len(data)),'hash_verified':sha(data)==f['sha256'] and sha(stock(a,len(data)))==f['stock_sha256'],'reported_exact_verified':(data==stock(a,len(data)))==f['exact'],'address_length_verified':a==x[3] and len(data)==f['expected_bytes']==f['linked_bytes']};maps=sorted((v-a,n) for n,v,_,k in esy if k==idx and n.startswith(('$t','$d')));z['mapping_symbols']=maps
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
  if f['exact'] and (f.get('selected_new_candidate') or ('dependency' in f and not f['dependency']) or ('reused_dependency'in f and not f['reused_dependency'])):newranges.append((a,a+len(data),name,f.get('historical_attribution')))
 for c in r.get('original_calls',[]):
  a=int(c.get('instruction',c.get('address')),16);q['calls'].append({'instruction':hex(a),'verified':bl(stock(a,4),a)==int(c['target'],16)})
 refs=r.get('original_literal_references',r.get('original_callback_literal_references',[]))+([r['original_external_clock_literal']] if 'original_external_clock_literal'in r else [])
 for c in refs:
  a=int(c['instruction'],16);h=struct.unpack('<H',stock(a,2))[0];dest=((a+4)&~3)+(h&255)*4;want=int(c.get('literal_address',c.get('literal')),16);val=int(c.get('literal_value',c.get('value')),16);q['literal_references'].append({'instruction':hex(a),'verified':h&0xf800==0x4800 and dest==want and struct.unpack('<I',stock(dest,4))[0]==val})
 reports.append(q)

(O/'SEVEN-LINKAGE-VERIFICATION.json').write_text(json.dumps({'reviews':reports,'new_ranges':newranges},indent=2)+'\n');print('selected',len(newranges),sum(e-a for a,e,_,_ in newranges))
