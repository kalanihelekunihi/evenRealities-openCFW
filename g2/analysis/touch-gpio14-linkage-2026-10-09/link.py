from pathlib import Path
import json,hashlib,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True)
prior=R/'g2/analysis/touch-gpio14-family-2026-10-09';input_dir=prior/'outputs/14.2.Rel1';receipt=json.loads((prior/'results.json').read_text())[0]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(input_dir/'public.o')==receipt['output_hashes']['public.o']
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';data=fw.read_bytes()[32:]
assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True
calls=[]
for a,t in [(0x8f30,0x8e64),(0x8f3a,0x8e84),(0x8f44,0x8e28),(0x8f4e,0x8ebe)]:
 ins=next(md.disasm(data[a-0x3300:a-0x3300+4],a));assert ins.mnemonic=='bl' and ins.operands[0].imm==t;calls.append({'address':a,'target':t,'bytes':ins.bytes.hex()})
literal=[]
for a,t in [(0x8e38,0x8e5c),(0x8e3e,0x8e60),(0x8f5c,0x8f94),(0x8f76,0x8f98),(0x8f8a,0x8f9c),(0x8f8e,0x8f9c)]:
 ins=next(md.disasm(data[a-0x3300:a-0x3300+2],a));effective=((a+4)&~3)+ins.operands[1].mem.disp;assert effective==t;literal.append({'instruction_address':a,'literal_address':t,'literal_word':int.from_bytes(data[t-0x3300:t-0x3300+4],'little')})
toolroot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';e=json.loads((toolroot/'acquisition.json').read_text())[0];tool=(toolroot/e['gcc']).parents[1]
shutil.copyfile(O/'link.ld',out/'link.ld')
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{input_dir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 elf=ELFFile(f)
 for name,a,n in [('hsiom',0x8e28,60),('write',0x8e64,32),('drive',0x8e84,58),('edge',0x8ebe,36),('init',0x8ee4,188)]:
  s=elf.get_section_by_name('.gpio_'+name);b=s.data();stock=data[a-0x3300:a-0x3300+n];rows.append({'section':s.name,'address':a,'expected_bytes':n,'linked_bytes':len(b),'exact':b==stock,'sha256':hashlib.sha256(b).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest()})
res={'argv':argv,'exit_code':p.returncode,'diagnostics':p.stderr,'original_calls':calls,'original_literal_references':literal,'sections':rows,'input_object_sha256':sha(input_dir/'public.o'),'linker_sha256':sha(tool/'bin/arm-none-eabi-ld'),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'manual_byte_patch':False,'production_or_device_change':False}
(O/'results.json').write_text(json.dumps(res,indent=2)+'\n');print([(x['section'],x['exact'],x['linked_bytes']) for x in rows])
