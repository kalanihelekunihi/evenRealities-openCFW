from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'g2/analysis/touch-pdl14-system-interface-2026-10-09';idir=prior/'outputs/cy_syslib.c';assembly=R/'g2/analysis/touch-syslib14-assembly-2026-10-09/outputs/public.o'
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:]
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;calls=[];refs=[]
for a in [0xa2fa,0xa312,0xa32c]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==0x4480;calls.append({'instruction':hex(a),'target':'0x4480','bytes':i.bytes.hex()})
for a,t,v,sym in [(0xa2f6,0xa318,0x2000086c,'cy_delay32kMs'),(0xa30c,0xa320,0x20000874,'cy_delayFreqKhz'),(0xa326,0xa334,0x20000870,'cy_delayFreqMhz')]:
 i=next(md.disasm(b[a-0x3300:a-0x3300+2],a));assert i.mnemonic=='ldr' and ((a+4)&~3)+i.operands[1].mem.disp==t;assert int.from_bytes(b[t-0x3300:t-0x3300+4],'little')==v
 refs.append({'instruction':hex(a),'literal_address':hex(t),'literal_value':hex(v),'source_symbol':sym})
relocs=[]
with (idir/'public.o').open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s['sh_type']=='SHT_REL' and s.name in ['.rel.text.Cy_SysLib_Delay','.rel.text.Cy_SysLib_DelayUs']:
   q=e.get_section(s['sh_info'])
   for r in s.iter_relocations():
    sym=e.get_section(s['sh_link']).get_symbol(r['r_info_sym']);off=r['r_offset']
    if r['r_info_type']==2:assert int.from_bytes(q.data()[off:off+4],'little')==0
    relocs.append({'section':q.name,'offset':off,'type':r['r_info_type'],'symbol':sym.name})
shutil.copyfile(assembly,out/'assembly.o');shutil.copyfile(O/'link.ld',out/'link.ld')
troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','/out/assembly.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True);assert p.returncode==0,p.stderr;rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for name,a,n,dep in [('assembly',0x4480,32,True),('delay',0xa2f0,52,False),('delay_us',0xa324,20,False)]:
  data=e.get_section_by_name('.'+name).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':name,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'reused_dependency':dep})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'original_literal_references':refs,'relocations':relocs,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'assembly_object_sha256':sha(assembly),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'new_selected_candidate_functions':2,'new_selected_candidate_bytes':72,'reused_dependency_bytes':32,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'limits':'Static bytes, not calibrated wall-clock duration. Globals bound from referenced literals, values not supplied or initialized by this comparator.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
