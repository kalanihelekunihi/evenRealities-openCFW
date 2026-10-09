from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True)
prior=R/'g2/analysis/touch-pdl14-system-interface-2026-10-09';idir=prior/'outputs/cy_sysint.c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((prior/'results.json').read_text());unit=next(u for u in receipt['units'] if u['source_unit']=='cy_sysint.c')
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True
calls=[]
for a,t in [(0xa2c0,0xa214),(0xa2d8,0xa274)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==t;calls.append({'address':hex(a),'target':hex(t),'bytes':i.bytes.hex()})
refs=[]
for a,t,value in [(0xa278,0xa2a0,0x20000400),(0xa280,0xa2a4,0x3300),(0xa28e,0xa2a0,0x20000400),(0xa2c8,0xa2e8,0x20000400)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+2],a));assert i.mnemonic=='ldr';assert ((a+4)&~3)+i.operands[1].mem.disp==t
 assert int.from_bytes(b[t-0x3300:t-0x3300+4],'little')==value
 refs.append({'instruction':hex(a),'literal_address':hex(t),'literal_value':hex(value),'bytes':i.bytes.hex()})
relocs=[]
with (idir/'public.o').open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s['sh_type']=='SHT_REL' and s.name in ['.rel.text.Cy_SysInt_SetVector','.rel.text.Cy_SysInt_Init']:
   target=e.get_section(s['sh_info'])
   for r in s.iter_relocations():
    sym=e.get_section(s['sh_link']).get_symbol(r['r_info_sym']);offset=r['r_offset']
    if r['r_info_type']==2:assert int.from_bytes(target.data()[offset:offset+4],'little')==0
    relocs.append({'section':target.name,'offset':offset,'type':r['r_info_type'],'symbol':sym.name,'raw_word':target.data()[offset:offset+4].hex()})
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
shutil.copyfile(O/'link.ld',out/'link.ld')
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,a,n,dependency in [('nvic',0xa214,96,True),('vector',0xa274,52,False),('init',0xa2a8,72,False)]:
  data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n]
  rows.append({'section':name,'address':hex(a),'absolute_payload_offset':32+a-0x3300,'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'dependency_outside_selected_denominator':dependency})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'original_literal_references':refs,'relocations':relocs,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'prior_receipt_sha256':sha(prior/'results.json'),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'linker_sha256':sha(tool/'bin/arm-none-eabi-ld'),'new_selected_candidate_functions':2,'new_selected_candidate_bytes':124,'dependency_bytes':96,'denominator':54,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'limits':'Static source comparator; literal binding does not initialize RAM vectors or prove runtime table contents. No board/toolchain uniqueness, campaign admission or whole-image completeness.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
