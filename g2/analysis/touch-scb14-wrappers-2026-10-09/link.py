from pathlib import Path
import hashlib,json,subprocess,shutil,re
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True)
prior=R/'g2/analysis/touch-scb14-holdouts-2026-10-09';idir=prior/'outputs/14.2.Rel1';rec=json.loads((prior/'results.json').read_text())[0];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(idir/'public.o')==rec['output_hashes']['public.o']
payload=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(payload)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=payload.read_bytes()[32:]
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;calls=[]
for a,t in [(0x9266,0x9218),(0x92ca,0x926e),(0x930a,0x92d6)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==t;calls.append({'address':a,'target':t,'bytes':i.bytes.hex()})
overlaps=[]
for p in (R/'g2/build/pseudocode-first/20260930T190500Z/tasks').glob('*.json'):
 d=json.loads(p.read_text());s=d.get('scope','');s=s if isinstance(s,str) else json.dumps(s)
 for a,z in re.findall(r'\[\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)',s):
  if int(a,16)<0x9316 and int(z,16)>0x9250:overlaps.append(str(p.relative_to(R)))
assert not overlaps
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';e=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/e['gcc']).parents[1];shutil.copyfile(O/'link.ld',out/'link.ld')
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-u','Cy_SCB_WriteArray','-u','Cy_SCB_WriteDefaultArray','-T','/out/link.ld','/input/public.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 elf=ELFFile(f)
 for name,a,n in [('read_helper',0x9218,56),('read',0x9250,30),('write_helper',0x926e,56),('write',0x92a6,48),('default_helper',0x92d6,16),('default',0x92e6,48)]:
  s=elf.get_section_by_name('.'+name);data=s.data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':s.name,'address':a,'absolute_payload_offset':32+a-0x3300,'declared_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'reused_dependency':name.endswith('helper')})
res={'argv':argv,'exit_code':p.returncode,'diagnostics':p.stderr,'sections':rows,'original_calls':calls,'input_object_sha256':sha(idir/'public.o'),'link_script_sha256':sha(O/'link.ld'),'linker_sha256':sha(tool/'bin/arm-none-eabi-ld'),'linked_elf_sha256':sha(out/'linked.elf'),'scope_overlap':overlaps,'new_wrapper_bytes':126,'reused_helper_bytes':128,'original_execution':False,'admitted':False};(O/'results.json').write_text(json.dumps(res,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
