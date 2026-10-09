from pathlib import Path
import json,hashlib,subprocess,shutil,io
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1];archive=tool/'lib/gcc/arm-none-eabi/14.2.1/thumb/v6-m/nofp/libgcc.a'
a=archive.read_bytes();assert a[:8]==b'!<arch>\n';offset=8;members={}
while offset<len(a):
 h=a[offset:offset+60];assert h[58:60]==b'`\n';n=int(h[48:58]);name=h[:16].decode().strip();d=a[offset+60:offset+60+n]
 if name in ['_udivsi3.o/','_dvmd_tls.o/']:members[name]=d
 offset+=60+n+(n%2)
assert len(members)==2
(out/'uidiv.o').write_bytes(members['_udivsi3.o/']);(out/'zero.o').write_bytes(members['_dvmd_tls.o/'])
with io.BytesIO(members['_udivsi3.o/']) as f:
 e=ELFFile(f);s=e.get_section_by_name('.text');assert len(s.data())==276
 q=e.get_section_by_name('.rel.text');rel=list(q.iter_relocations());assert len(rel)==1 and rel[0]['r_offset']==260 and rel[0]['r_info_type']==10;assert e.get_section(q['sh_link']).get_symbol(rel[0]['r_info_sym']).name=='__aeabi_idiv0'
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;i=next(md.disasm(b[0xa7c4-0x3300:0xa7c8-0x3300],0xa7c4));assert i.mnemonic=='bl' and i.operands[0].imm==0xa9a8
shutil.copyfile(O/'link.ld',out/'link.ld');argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','-T','/out/link.ld','/out/uidiv.o','/out/zero.o','-o','/out/linked.elf'];p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,addr,n in [('division',0xa6c0,276),('zero',0xa9a8,4)]:
  d=e.get_section_by_name('.'+name).data();stock=b[addr-0x3300:addr-0x3300+n];rows.append({'section':name,'address':hex(addr),'bytes':len(d),'exact':d==stock,'sha256':hashlib.sha256(d).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
result={'argv':argv,'diagnostics':p.stderr,'archive_path':str(archive.relative_to(R)),'archive_sha256':sha(archive),'extracted_member_hashes':{n:hashlib.sha256(d).hexdigest() for n,d in members.items()},'linked_elf_sha256':sha(out/'linked.elf'),'link_script_sha256':sha(O/'link.ld'),'stock_div0_call':{'instruction':'0xA7C4','target':'0xA9A8','bytes':i.bytes.hex()},'sections':rows,'code_extents':{'uidiv':['0xA6C0','0xA7CA'],'alignment':['0xA7CA','0xA7CC'],'uidivmod':['0xA7CC','0xA7D4'],'div0':['0xA9A8','0xA9AA'],'div0_alignment':['0xA9AA','0xA9AC']},'denominator_54_increment':0,'independent_review':'pending','source_rebuild_claim':False,'limits':'Authenticated compiler-runtime binary provider comparator, not rebuilt source. GCC ARM assembly source/revision and runtime exception license need separate provenance before source-complete claim; archive/source producer uniqueness not inferred.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
