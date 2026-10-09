from pathlib import Path
import json,struct
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';src=(O/'seven_verify.py').read_text();exec(src[:src.index("names=['")]);P=R/'g2/analysis/touch-newlib14-startup-exit-2026-10-09';r=json.loads((P/'results.json').read_text());l=json.loads((P/'exit-link-results.json').read_text());runs=[]
for u in r['runs']:
 argv=u['argv'];mounts={v.split(':')[1]:Path(v.split(':')[0]) for i,v in enumerate(argv) if i and argv[i-1]=='-v'};label='exit'if u['function']=='exit'else'init';b,ss,ns,sy=elf(P/'outputs'/label/'public.o');idx=ns.index('.text.'+u['function']);x=ss[idx];v=b[x[4]:x[4]+x[5]];a=int(u['address'],16);t=stock(a,len(v));rs=relocs(b,ss,ns,sy,idx);mask={j for off,typ,sym in rs for j in range(off,off+4)};runs.append({'function':u['function'],'input_hashes_verified':all(sha((mounts['/'+n.split('/')[1]]/'/'.join(n.split('/')[2:])).read_bytes())==val for n,val in u['consumed_inputs'].items()),'object_hash_verified':sha(b)==u['object_sha256'],'preprocessing_hash_verified':sha((P/'outputs'/label/'public.i').read_bytes())==u['preprocessed_sha256'],'nonrelocated_mismatches_verified':[j for j in range(len(v)) if j not in mask and v[j]!=t[j]]==u['non_relocated_mismatches'],'mismatch_count':len(u['non_relocated_mismatches'])})
ib,iss,ins,isy=elf(P/'outputs/exit/public.o');ix=iss[ins.index('.text.exit')];raw=ib[ix[4]:ix[4]+ix[5]];b,ss,ns,sy=elf(P/'outputs/exit/linked.elf');idx=ns.index('.text');x=ss[idx];v=b[x[4]:x[4]+x[5]];a=0xa9ac;refs=[]
for off in range(0,32,2):
 h=struct.unpack_from('<H',v,off)[0]
 if h&0xf800==0x4800:refs.append([hex(a+off),hex(((a+off+4)&~3)+(h&255)*4)])
weak=False
for sec in iss:
 if sec[1]==2:
  for off in range(sec[4],sec[4]+sec[5],16):
   no,val,size,info,other,si=struct.unpack_from('<IIIBBH',ib,off)
   st=iss[sec[6]];strings=ib[st[4]:st[4]+st[5]];name=strings[no:strings.index(b'\0',no)].decode()
   if name=='__call_exitprocs':weak=(info>>4)==2 and si==0
out={'sources_hash_verified':all(sha((P/'source'/f['upstream_path']).read_bytes())==f['sha256'] for f in r['source_acquisitions']),'compile_runs':runs,'link_input_hashes_verified':all(sha((R/k).read_bytes())==val for k,val in l['inputs'].items()),'exit_exact':v==stock(a,40),'exit_hash_verified':sha(v)==l['linked_sha256']==l['stock_sha256'],'extent_verified':x[3]==a and len(v)==40,'undefined_weak_exitprocs_verified':weak,'weak_call_linked_bytes':v[12:16].hex(),'only_relocations_changed':all(v[j]==raw[j] for j in range(40) if j not in set(range(12,16))|set(range(28,40))),'exit_call_target_verified':bl(v[28:32],a+28)==0xaa40,'weak_literal_zero':struct.unpack_from('<I',v,32)[0]==0,'stdio_slot_verified':struct.unpack_from('<I',v,36)[0]==0x20000f54,'original_LDR_references':refs,'ends_at_memset_start':a+len(v)==0xa9d4,'new_dependency_bytes':40,'census_increment':0};(O/'EXIT-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
