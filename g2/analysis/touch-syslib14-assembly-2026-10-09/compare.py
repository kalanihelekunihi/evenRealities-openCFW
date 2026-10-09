from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1];P=troot/'tools/pdl-input'
source=P/'drivers/source/COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S'
targets=[('Cy_SysLib_DelayCycles',0x4480,18),('Cy_SysLib_EnterCriticalSection',0x4492,8),('Cy_SysLib_ExitCriticalSection',0x449a,6)]
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{P}:/pdl:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-gcc','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-DCY8C4046FNI_T412','-ffunction-sections','-c','/pdl/'+str(source.relative_to(P)),'-o','/out/public.o']
p=subprocess.run(argv,capture_output=True,text=True,check=True)
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes();rows=[]
with (out/'public.o').open('rb') as f:
 e=ELFFile(f);sy=e.get_section_by_name('.symtab');s=e.get_section_by_name('.text');assert not [x for x in e.iter_sections() if x['sh_type'] in ('SHT_REL','SHT_RELA')]
 for name,a,n in targets:
  sym=sy.get_symbol_by_name(name)[0];offset=sym['st_value']&~1;data=s.data()[offset:offset+n];stock=b[32+a-0x3300:32+a-0x3300+n]
  rows.append({'function':name,'runtime_address':hex(a),'object_offset':offset,'symbol_declared_size':sym['st_size'],'compared_bytes':n,'object_bytes':data.hex(),'stock_bytes':stock.hex(),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest()})
 text_size=len(s.data())
assert text_size==32
result={'argv':argv,'diagnostics':p.stderr,'source_path':str(source.relative_to(R)),'source_sha256':sha(source),'object_sha256':sha(out/'public.o'),'text_bytes':text_size,'functions':rows,'new_candidate_functions':3,'new_candidate_bytes':32,'independent_review':'pending','denominator':54,'limits':'Authentic assembly, unchanged. Symbols have no size metadata; extents use predeclared historical rows and contiguous source labels. No physical elapsed-time claim, source implementation invention or whole-image completion.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['function'],x['exact']) for x in rows])
