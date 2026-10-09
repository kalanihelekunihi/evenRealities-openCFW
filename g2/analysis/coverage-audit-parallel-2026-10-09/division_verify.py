from pathlib import Path
import struct,json,hashlib
R=Path.cwd();O=R/'g2/analysis/coverage-audit-parallel-2026-10-09';P=R/'g2/analysis/touch-libgcc14-division-2026-10-09';sha=lambda b:hashlib.sha256(b).hexdigest();src=(O/'seven_verify.py').read_text();exec(src[:src.index("names=['")]);r=json.loads((P/'results.json').read_text());archive=(R/r['archive_path']).read_bytes();assert archive[:8]==b'!<arch>\n';off=8;members={}
while off<len(archive):
 h=archive[off:off+60];n=int(h[48:58]);name=h[:16].decode().strip();members[name]=archive[off+60:off+60+n];off+=60+n+(n&1)
checks=[]
for name,file in [('_udivsi3.o/','uidiv.o'),('_dvmd_tls.o/','zero.o')]:
 v=members[name];checks.append({'member':name,'archive_member_hash_verified':sha(v)==r['extracted_member_hashes'][name],'extracted_object_identical':v==(P/'outputs'/file).read_bytes()})
eb,ess,ens,esy=elf(P/'outputs/linked.elf');sections=[]
for f in r['sections']:
 idx=ens.index('.'+f['section']);x=ess[idx];v=eb[x[4]:x[4]+x[5]];a=int(f['address'],16);sections.append({'section':f['section'],'exact':v==stock(a,len(v)),'coordinates_verified':x[3]==a and len(v)==f['bytes'],'hash_verified':sha(v)==f['sha256']==f['stock_sha256']})
ib,iss,ins,isy=elf(P/'outputs/uidiv.o');idx=ins.index('.text');x=iss[idx];raw=ib[x[4]:x[4]+x[5]];rs=relocs(ib,iss,ins,isy,idx);linked=stock(0xa6c0,len(raw));mask={j for off,typ,sym in rs for j in range(off,off+4)};rr=[]
for off,typ,sym in rs:
 n,sv,size,k=sym;dest=next(v for sn,v,_,_ in esy if sn==n);rr.append({'offset':off,'type':typ,'symbol':n,'target':hex(dest),'verified':typ==10 and bl(linked[off:off+4],0xa6c0+off)==dest&~1})
syms=[{'name':n,'value':hex(v),'size':size,'section':ins[k] if k<len(ins) else k} for n,v,size,k in isy if n in ['__aeabi_uidiv','__udivsi3','__aeabi_uidivmod']];zb,zss,zns,zsy=elf(P/'outputs/zero.o');zero_symbols=[{'name':n,'value':hex(v),'size':size} for n,v,size,k in zsy if 'div0'in n];out={'archive_hash_verified':sha(archive)==r['archive_sha256'],'members':checks,'elf_hash_verified':sha(eb)==r['linked_elf_sha256'],'script_hash_verified':sha((P/'link.ld').read_bytes())==r['link_script_sha256'],'script_copy_identical':(P/'link.ld').read_bytes()==(P/'outputs/link.ld').read_bytes(),'sections':sections,'source_object_unchanged_except_relocation':all(raw[j]==linked[j] for j in range(len(raw)) if j not in mask),'relocations':rr,'original_hook_call_verified':bl(stock(0xa7c4,4),0xa7c4)==0xa9a8,'division_symbols':syms,'zero_symbols':zero_symbols,'uidiv_alignment':stock(0xa7ca,2).hex(),'zero_alignment':stock(0xa9aa,2).hex(),'uidivmod_eight_bytes':stock(0xa7cc,8).hex(),'following_signed_body_not_counted':hex(0xa7d4),'dependency_bytes':280,'census_increment':0};(O/'DIVISION-VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
