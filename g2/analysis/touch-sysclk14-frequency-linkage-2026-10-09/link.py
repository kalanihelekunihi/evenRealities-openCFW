from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
idir=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/outputs/cy_sysclk.c';assembly=R/'g2/analysis/touch-syslib14-assembly-2026-10-09/outputs/public.o'
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;calls=[]
for a,t in [(0x9cbe,0x9c44),(0x9cd0,0xa6c0),(0x9cd6,0x4492),(0x9d06,0x4480),(0x9d10,0x449a),(0x9d30,0x4480),(0x9fac,0x9f34),(0x9fbc,0x9c44),(0x9fc8,0x9c38)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==t;calls.append({'instruction':hex(a),'target':hex(t),'bytes':i.bytes.hex()})
shutil.copyfile(assembly,out/'assembly.o');shutil.copyfile(O/'link.ld',out/'link.ld');troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','/out/assembly.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,a,n,dep in [('assembly',0x4480,32,True),('external',0x9c38,12,True),('imo_get',0x9c44,60,True),('imo_set',0x9c80,272,False),('source_get',0x9f34,16,True),('frequency',0x9f9c,56,False)]:
  data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'reused_dependency':dep})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'assembly_object_sha256':sha(assembly),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'new_selected_candidate_functions':2,'new_selected_candidate_bytes':328,'reused_dependency_bytes':120,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'unimplemented_external_binding':{'symbol':'__aeabi_uidiv','stock_target':'0xA6C0','evidence':'original BL at 0x9CD0; no executable body/stub supplied'},'limits':'Static comparator only. Compiler division body unresolved here; not a complete linked executable or runtime/physical clock proof.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
