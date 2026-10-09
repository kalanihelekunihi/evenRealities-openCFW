from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09';idir=prior/'outputs/cy_sysclk.c'
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True
calls=[]
for a,t in [(0x9f50,0x9f34),(0x9f6c,0x9c38)]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==t;calls.append({'instruction':hex(a),'target':hex(t),'bytes':i.bytes.hex()})
i=next(md.disasm(b[0x9c38-0x3300:0x9c3a-0x3300],0x9c38));assert i.mnemonic=='ldr' and ((i.address+4)&~3)+i.operands[1].mem.disp==0x9c40
assert int.from_bytes(b[0x9c40-0x3300:0x9c44-0x3300],'little')==0x20000f20
with (idir/'public.o').open('rb') as f:
 e=ELFFile(f);q=e.get_section_by_name('.rel.text.Cy_SysClk_ExtClkGetFrequency');r=list(q.iter_relocations())[0];sym=e.get_section(q['sh_link']).get_symbol(r['r_info_sym']);assert r['r_offset']==8 and r['r_info_type']==2 and e.get_section(sym['st_shndx']).name=='.bss'
 assert e.get_section_by_name('.text.Cy_SysClk_ExtClkGetFrequency').data()[8:12]==bytes(4)
shutil.copyfile(O/'link.ld',out/'link.ld');troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,a,n,historical in [('external',0x9c38,12,'Cy_SysClk_ExtClkGetFrequency'),('get_source',0x9f34,16,'Cy_SysClk_ClkHfGetDivider'),('set_source',0x9f44,88,'Cy_SysClk_ClkHfSetDivider')]:
  data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'historical_attribution':historical})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'original_external_clock_literal':{'instruction':'0x9c38','literal':'0x9c40','value':'0x20000f20'},'sections':rows,'input_object_sha256':sha(idir/'public.o'),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'new_candidate_extents':3,'new_candidate_bytes':116,'independent_review':'pending','historical_name_correction':'9F34/9F44 implement HF source selection, not HF division. Original ledger rows preserved; no symbol-file mutation. Review must account for mislabeled SetSource row at A188 independently.','original_execution':False,'manual_byte_patches':False,'limits':'Unchanged source and stock-address evidence; no runtime clock readiness/frequency/global initialization claim.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
