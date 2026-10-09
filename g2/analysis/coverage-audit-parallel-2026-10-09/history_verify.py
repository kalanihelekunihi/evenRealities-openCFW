from pathlib import Path
import json,hashlib,struct
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';P=R/'g2/analysis/touch-pdl14-history-layout-2026-10-09';src=(O/'seven_verify.py').read_text();exec(src[:src.index("names=['")]);r=json.loads((P/'results.json').read_text());runs=[]
for u in r['runs']:
 argv=u['argv'];mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'};runs.append({'label':u['label'],'success':u['exit_code']==0,'device_retained':'-DCY8C4046FNI_T412'in argv,'inputs_verified':all(sha((mounts['/'+n.split('/')[1]]/'/'.join(n.split('/')[2:])).read_bytes())==v for n,v in u['consumed_input_hashes'].items()),'outputs_verified':all(sha((P/'outputs'/u['label']/n).read_bytes())==v for n,v in u['output_hashes'].items()),'data_sections':'-fdata-sections'in argv})
D=R/'g2/analysis/source-discovery-parallel-2026-10-09/pdl-residual-history';prov=[]
for n in ['provenance.json','header-recipe-provenance.json']:
 items=json.loads((D/n).read_text());prov.append({'file':n,'all_content_hashes_verified':all(sha((R/x.get('path',x.get('local'))).read_bytes())==x['sha256'] for x in items)})
linked=json.loads((P/'linked-results.json').read_text());lr=[];ranges=[]
for u in linked['runs']:
 group=u['group'];argv=u['argv'];mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'};ib,iss,ins,isy=elf(mounts['/input']/'public.o');eb,ess,ens,esy=elf(P/'linked'/group/'linked.elf');script=(P/(group+'.ld')).read_text();q={'group':group,'input_hash_verified':sha(ib)==u['input_object_sha256'],'elf_hash_verified':sha(eb)==u['linked_elf_sha256'],'script_hash_verified':sha(script.encode())==u['link_script_sha256'],'sections':[],'evidence':[]}
 for f in u['sections']:
  idx=ens.index('.'+f['section']);x=ess[idx];a=int(f['address'],16);v=eb[x[4]:x[4]+x[5]];maps=sorted((sv-a,sn) for sn,sv,_,k in esy if k==idx and sn.startswith(('$t','$d')));z={'section':f['section'],'exact':v==stock(a,len(v)),'hash_verified':sha(v)==f['sha256']==f['stock_sha256'],'extent_verified':x[3]==a and len(v)==f['expected_bytes'],'mapping_symbols':maps};start=script.index('.'+f['section']+' ');part=script[start:script.index('}',start)];inp=part.split('(')[1].split(')')[0]
  if inp in ins and not any(tag in part for tag in ['uidiv.o','zero.o','assembly.o']):
   ii=ins.index(inp);ix=iss[ii];raw=ib[ix[4]:ix[4]+ix[5]];rs=relocs(ib,iss,ins,isy,ii);mask={j for off,typ,sym in rs for j in range(off,off+4)};z['unchanged_except_relocations']=len(raw)==len(v) and all(raw[j]==v[j] for j in range(len(raw)) if j not in mask);bindings=[]
   for off,typ,sym in rs:
    sn,sv,size,si=sym;target=next((val for n,val,_,_ in esy if n==sn),None) if sn else None
    if not sn:
     si_name=ins[si]
     # Source section assigned by explicit linker selector.
     for line in script.splitlines():
      if '('+si_name+')' in line:
       outsec=line.strip().split()[0];target=ess[ens.index(outsec)][3]
    addend=struct.unpack_from('<I',raw,off)[0] if typ==2 else None;actual=struct.unpack_from('<I',v,off)[0] if typ==2 else bl(v[off:off+4],a+off);ok=target is not None and (actual==((target+addend)&0xffffffff) if typ==2 else actual==target&~1);bindings.append({'offset':off,'symbol':sn or ins[si],'type':typ,'verified':ok})
   z['bindings']=bindings
  if maps and any(n.startswith('$t') for _,n in maps) and any(n.startswith('$d') for _,n in maps):
   pool=next(off for off,n in maps if n.startswith('$d'));refs=set();off=0
   while off<pool:
    h=struct.unpack_from('<H',v,off)[0]
    if h&0xf800==0x4800:refs.add(((a+off+4)&~3)+(h&255)*4)
    off+=4 if h>>11 in (29,30,31) else 2
   z['literal_pool_owned']=set(range(a+pool,a+len(v),4))<=refs
  q['sections'].append(z)
  if not f['dependency']:ranges.append((a,a+len(v),group,f['section']))
 for e in u['original_relocation_evidence']:
  a=int(e['address'],16)
  if e['kind']=='BL':ok=bl(stock(a,4),a)==int(e['target'],16)
  else:
   ok=struct.unpack('<I',stock(a,4))[0]==int(e['value'],16)
   for pc in e['PC_loads']:
    pc=int(pc,16);h=struct.unpack('<H',stock(pc,2))[0];ok=ok and h&0xf800==0x4800 and ((pc+4)&~3)+(h&255)*4==a
  q['evidence'].append({'address':hex(a),'verified':ok})
 lr.append(q)
# Receipt review without repeating original execution.
pm=json.loads((P/'pm-original-results.json').read_text());pc=[]
for x in pm['results']:
 seq=x['sequence'];fail=x['failure_callback'];skip=x['middle_skip_mask'];events=[];last=None
 for i in range(3):
  if i==1 and skip&seq[0]:continue
  events.append([i,seq[0]]);last=i
  if seq[0]==1 and i==fail:break
 for i in (range(last-1,-1,-1) if seq[1]==2 else range(2,-1,-1)):
  if i==1 and skip&seq[1]:continue
  events.append([i,seq[1]])
 expected_failed=hex(0x20001000+32*fail) if seq[0]==1 and fail>=0 and [fail,1]in events else '0x0';pc.append(events==x['events'] and expected_failed==x['failed_callback'])
st=json.loads((P/'status-original-results.json').read_text());errors={1:0x520001,3:0x520004,4:0x520004,5:0x520005,7:0,8:0x500008,9:0x500009,17:0x520021,19:0x520021,20:0x520021};sc=[]
for x in st['results']:
 a=int(x['status_word'],16);expected=0 if a&0xf0000000==0xa0000000 else errors.get(a-0xf0000000,0x5200ff) if a&0xf0000000==0xf0000000 else 0x500023;sc.append(int(x['returned_status'],16)==expected and x['MMIO_reads']==[['0x40100008',4]] and not x['MMIO_writes'])
ranges.sort();out={'compilation_runs':runs,'provenance_files':prov,'linked_reviews':lr,'new_ranges':ranges,'new_selected_bytes':sum(e-a for a,e,_,_ in ranges),'new_selected_functions':len(ranges),'new_nonoverlapping':all(x[1]<=y[0] for x,y in zip(ranges,ranges[1:])),'PM_80_receipts_consistent':len(pc)==80 and all(pc),'SROM_32_receipts_consistent':len(sc)==32 and all(sc),'aggregate_selected_bytes':3948+1004,'aggregate_selected_functions':54};(O/'HISTORY-LAYOUT-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
def scan(v,path=''):
 if isinstance(v,dict):
  for k,x in v.items():
   if x is False:print(path+'.'+k)
   else:scan(x,path+'.'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):scan(x,path+f'[{i}]')
scan(out);print('counts',out['new_selected_functions'],out['new_selected_bytes'])
