from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'g2/analysis/touch-pdl14-system-interface-2026-10-09';idir=prior/'outputs/cy_systick.c'
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:]
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;calls=[];refs=[]
for a,t in [(0xa676,0xa638),(0xa690,0xa620)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==t;calls.append({'instruction':hex(a),'target':hex(t)})
for a,t,v in [(0xa606,0xa61c,0x20000f40),(0xa662,0xa698,0x20000f40),(0xa670,0xa69c,0x20000400),(0xa672,0xa6a0,0xa5f5),(0xa6ac,0xa6bc,0x20000f40)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+2],a));assert i.mnemonic=='ldr' and ((a+4)&~3)+i.operands[1].mem.disp==t;assert int.from_bytes(b[t-0x3300:t-0x3300+4],'little')==v
 refs.append({'instruction':hex(a),'literal_address':hex(t),'literal_value':hex(v)})
relocs=[]
with (idir/'public.o').open('rb') as f:
 e=ELFFile(f);symbol=e.get_section_by_name('.symtab').get_symbol_by_name('Cy_SysTick_Callbacks')[0];assert symbol['st_size']==20 and symbol['st_value']==0
 for s in e.iter_sections():
  if s['sh_type']=='SHT_REL' and s.name in ['.rel.text.Cy_SysTick_ServiceCallbacks','.rel.text.Cy_SysTick_Init','.rel.text.Cy_SysTick_SetCallback']:
   q=e.get_section(s['sh_info'])
   for r in s.iter_relocations():
    sym=e.get_section(s['sh_link']).get_symbol(r['r_info_sym']);off=r['r_offset']
    if r['r_info_type']==2:assert int.from_bytes(q.data()[off:off+4],'little')==0
    relocs.append({'section':q.name,'offset':off,'type':r['r_info_type'],'symbol':sym.name,'symbol_section':e.get_section(sym['st_shndx']).name if isinstance(sym['st_shndx'],int) else sym['st_shndx']})
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1];shutil.copyfile(O/'link.ld',out/'link.ld')
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 assert e.get_section_by_name('.callbacks')['sh_size']==20
 for name,a,n,dep in [('service',0xa5f4,44,False),('enable',0xa620,24,True),('clock',0xa638,24,True),('init',0xa650,88,False),('set_callback',0xa6a8,24,False)]:
  data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'reused_dependency':dep})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'original_literal_references':refs,'relocations':relocs,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'new_selected_candidate_functions':3,'new_selected_candidate_bytes':156,'reused_dependency_bytes':48,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'limits':'Static bytes; NOLOAD callback table is address/size binding only, no initialized runtime state or timer/exception behavior assumed.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
