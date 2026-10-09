from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
idir=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/outputs/cy_syspm.c';assembly=R/'g2/analysis/touch-syslib14-assembly-2026-10-09/outputs/public.o'
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;calls=[]
for a,t in [(0xa536,0xa444),(0xa53e,0x4492),(0xa550,0xa444),(0xa554,0xa374),(0xa55a,0x449a),(0xa56a,0xa444),(0xa57a,0xa444),(0xa59a,0xa444),(0xa5a2,0x4492),(0xa5b4,0xa444),(0xa5b8,0xa388),(0xa5be,0x449a),(0xa5d2,0xa444),(0xa5e8,0xa444)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==t;calls.append({'instruction':hex(a),'target':hex(t)})
refs=[]
for a,t in [(0xa3c4,0xa440),(0xa416,0xa440),(0xa420,0xa440)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+2],a));assert i.mnemonic=='ldr' and ((a+4)&~3)+i.operands[1].mem.disp==t;assert int.from_bytes(b[t-0x3300:t-0x3300+4],'little')==0x20000f34;refs.append({'instruction':hex(a),'literal':hex(t),'value':'0x20000F34'})
shutil.copyfile(assembly,out/'assembly.o');shutil.copyfile(O/'link.ld',out/'link.ld');troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','/out/assembly.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,a,n,dep in [('assembly',0x4480,32,True),('sleep_direct',0xa374,20,True),('deep_direct',0xa388,40,True),('register',0xa3b0,148,False),('execute',0xa444,220,True),('sleep',0xa528,100,False),('deep',0xa58c,104,False)]:
  data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'dependency':dep,'mismatch_positions':[i for i in range(min(len(data),len(stock))) if data[i]!=stock[i]]})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'original_callback_literal_references':refs,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'assembly_object_sha256':sha(assembly),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'new_selected_exact_functions':3,'new_selected_exact_bytes':352,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'limits':'ExecuteCallback dependency intentionally retained mismatched. Wrapper exactness is local/static only; no complete sleep composition or physical sleep/IRQ proof. No dependency mismatch concealed.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact'],len(x['mismatch_positions'])) for x in rows])
