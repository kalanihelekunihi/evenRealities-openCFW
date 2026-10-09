from pathlib import Path
import hashlib,json,subprocess,shutil
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
O=Path(__file__).resolve().parent;R=O.parents[2];out=O/'outputs';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
idir=R/'g2/analysis/touch-pdl14-finite-census-2026-10-09/outputs/cy_scb_i2c.c';common=R/'g2/analysis/touch-scb14-holdouts-2026-10-09/outputs/14.2.Rel1/public.o';assembly=R/'g2/analysis/touch-syslib14-assembly-2026-10-09/outputs/public.o'
mapping={'Cy_SCB_ReadArrayNoCheck':0x9218,'Cy_SCB_ReadArray':0x9250,'Cy_SCB_WriteArrayNoCheck':0x926e,'Cy_SCB_WriteArray':0x92a6,'Cy_SCB_WriteDefaultArrayNoCheck':0x92d6,'Cy_SCB_WriteDefaultArray':0x92e6,'Cy_SCB_SetRxFifoLevel':0x9316,'SlaveHandleHsMode':0x9344,'SlaveHandleStop':0x93c4,'SlaveHandleAck':0x9510,'SlaveHandleAddress':0x95b8,'SlaveHandleDataReceive':0x9748,'SlaveHandleDataTransmit':0x97fc,'Cy_SCB_I2C_SlaveInterrupt':0x9b0c,'Cy_SysLib_EnterCriticalSection':0x4492,'Cy_SysLib_ExitCriticalSection':0x449a}
fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';assert sha(fw)=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';b=fw.read_bytes()[32:];md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);md.detail=True;calls=[]
with (idir/'public.o').open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s['sh_type']!='SHT_REL':continue
  parent=e.get_section(s['sh_info']).name.replace('.text.','')
  if parent not in mapping:continue
  for r in s.iter_relocations():
   symbol=e.get_section(s['sh_link']).get_symbol(r['r_info_sym']).name;assert r['r_info_type']==10 and symbol in mapping
   a=mapping[parent]+r['r_offset'];i=next(md.disasm(b[a-0x3300:a-0x3300+4],a));assert i.mnemonic=='bl' and i.operands[0].imm==mapping[symbol]
   calls.append({'caller':parent,'instruction':hex(a),'callee':symbol,'target':hex(mapping[symbol])})
shutil.copyfile(assembly,out/'assembly.o');shutil.copyfile(common,out/'common.o');shutil.copyfile(O/'link.ld',out/'link.ld');troot=R/'g2/analysis/touch-compiler14-successor-2026-10-09';acq=json.loads((troot/'acquisition.json').read_text())[0];tool=(troot/acq['gcc']).parents[1]
argv=['docker','run','--rm','--platform','linux/amd64','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{tool}:/tool:ro','-v',f'{idir}:/input:ro','-v',f'{out}:/out','ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55','/tool/bin/arm-none-eabi-ld','--gc-sections','-T','/out/link.ld','/input/public.o','/out/common.o','/out/assembly.o','-o','/out/linked.elf']
p=subprocess.run(argv,capture_output=True,text=True,check=True);rows=[]
with (out/'linked.elf').open('rb') as f:
 e=ELFFile(f)
 for section,a,n in [('assembly',0x4480,32),('read_helper',0x9218,56),('read',0x9250,30),('write_helper',0x926e,56),('write',0x92a6,48),('default_helper',0x92d6,16),('default',0x92e6,48),('rx_level',0x9316,44),('hs',0x9344,128),('stop',0x93c4,332),('ack',0x9510,168),('address',0x95b8,400),('receive',0x9748,180),('transmit',0x97fc,248),('interrupt',0x9b0c,300)]:
  data=e.get_section_by_name('.'+section).data();stock=b[a-0x3300:a-0x3300+n];rows.append({'section':section,'address':hex(a),'expected_bytes':n,'linked_bytes':len(data),'exact':data==stock,'sha256':hashlib.sha256(data).hexdigest(),'stock_sha256':hashlib.sha256(stock).hexdigest(),'selected_new_candidate':section=='interrupt','new_helper_outside_denominator':section in ['hs','stop','ack','address','receive','transmit']})
result={'argv':argv,'diagnostics':p.stderr,'original_calls':calls,'sections':rows,'input_object_sha256':sha(idir/'public.o'),'common_object_sha256':sha(common),'assembly_object_sha256':sha(assembly),'link_script_sha256':sha(O/'link.ld'),'linked_elf_sha256':sha(out/'linked.elf'),'new_selected_candidate_functions':1,'new_selected_candidate_bytes':300,'new_helpers_outside_denominator_bytes':1456,'new_helpers_outside_denominator_functions':6,'independent_review':'pending','original_execution':False,'manual_byte_patches':False,'limits':'Complete reached direct-call byte linkage, not I2C bus traffic, event ordering, IRQ delivery or concurrent context state.'}
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print([(x['section'],x['exact']) for x in rows])
